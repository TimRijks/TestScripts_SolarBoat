import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue
import sys
import csv
from datetime import datetime

# --- Config ---
COM_PORT = 'COM6'        # listening on port 6 as requested
BAUD_RATE = 115200
UPDATE_INTERVAL_MS = 50  # animation update interval
READ_TIMEOUT = 1.0
# expected order from the Arduino
EXPECTED_LABELS = ['ax','ay','az','gx','gy','gz','mx','my','mz','heading','pitch','roll']
# ----------------

def open_serial(port, baud):
    try:
        return serial.Serial(port, baud, timeout=READ_TIMEOUT)
    except Exception as e:
        print("Error opening serial port:", e)
        sys.exit(1)

def parse_name_values(parts):
    labels = []
    vals = []
    for p in parts:
        if ':' not in p:
            return None
        k, v = p.split(':', 1)
        try:
            fv = float(v)
        except:
            return None
        labels.append(k.strip())
        vals.append(fv)
    return labels, vals

def reader_thread_fn(ser, q, labels_global, stop_evt):
    """
    Background thread that reads serial lines and puts parsed numeric lists into queue.
    It maps name:value input to the fixed label order (labels_global) if needed.
    """
    # main reading loop
    while not stop_evt.is_set():
        try:
            raw = ser.readline().decode(errors='ignore').strip()
            if not raw:
                continue
            # ignore header lines
            if raw.lower().startswith('labels:'):
                continue
            parts = [p.strip() for p in raw.split(',') if p.strip()]
            nv = parse_name_values(parts)
            if nv:
                n_labels, vals = nv
                # if incoming labels are a subset of expected, map by name
                if set(n_labels) <= set(labels_global):
                    out = [0.0]*len(labels_global)
                    for k, v in zip(n_labels, vals):
                        try:
                            idx = labels_global.index(k)
                            out[idx] = v
                        except ValueError:
                            pass
                    try:
                        q.put(out, block=False)
                    except queue.Full:
                        pass
                else:
                    # try mapping by position if counts match
                    if len(vals) == len(labels_global):
                        try:
                            q.put(vals, block=False)
                        except queue.Full:
                            pass
                continue
            # numeric CSV fallback
            try:
                vals = [float(p) for p in parts]
                if len(vals) == len(labels_global):
                    try:
                        q.put(vals, block=False)
                    except queue.Full:
                        pass
            except ValueError:
                continue
        except Exception:
            continue

def create_single_plot(labels):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', None)
    lines = []
    for i, lbl in enumerate(labels):
        color = colors[i % len(colors)] if colors else None
        ln, = ax.plot([], [], lw=1.5, label=lbl, color=color)
        lines.append(ln)
    ax.grid(True, alpha=0.25)
    ax.set_xlabel('sample')
    ax.set_ylabel('value')
    leg = ax.legend(loc='upper right')
    fig.tight_layout()
    return fig, ax, lines, leg

def main():
    ser = open_serial(COM_PORT, BAUD_RATE)
    print(f"Listening on {COM_PORT} @ {BAUD_RATE} - waiting for data...")

    # Use expected labels order so we always plot the same channels
    labels = EXPECTED_LABELS.copy()
    num_channels = len(labels)

    # Create CSV file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"imu_data_{timestamp}.csv"
    csv_file = open(csv_filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(labels)  # Write header
    csv_file.flush()
    print(f"Saving data to: {csv_filename}")

    q = queue.Queue(maxsize=1000)
    stop_evt = threading.Event()

    rt = threading.Thread(target=reader_thread_fn, args=(ser, q, labels, stop_evt), daemon=True)
    rt.start()

    # prepare buffers (grow without bound to show all received data)
    buffers = [[] for _ in range(num_channels)]

    fig, ax, line_objs, legend = create_single_plot(labels)

    frame_counter = 0

    def update(frame):
        nonlocal frame_counter
        # drain queue
        drained = 0
        while drained < 200 and not q.empty():
            try:
                vals = q.get_nowait()
            except queue.Empty:
                break
            if len(vals) != num_channels:
                continue
            for i, v in enumerate(vals):
                buffers[i].append(v)
            # Write to CSV
            csv_writer.writerow(vals)
            csv_file.flush()
            drained += 1

        if not any(buffers):
            return line_objs

        # x axis range uses longest buffer (show all data)
        max_len = max(len(b) for b in buffers) if buffers else 0
        xs = list(range(max_len))

        # update each line (pad shorter channels by repeating last value so x aligns)
        for i, ln in enumerate(line_objs):
            y = buffers[i]
            if not y:
                ln.set_data([], [])
                continue
            # if length shorter than max_len, extend with last value for display alignment
            if len(y) < max_len:
                y_disp = y + [y[-1]] * (max_len - len(y))
            else:
                y_disp = y
            ln.set_data(xs, y_disp)

        # autoscale y across all channels
        all_vals = [v for buf in buffers for v in buf]
        if all_vals:
            ymin, ymax = min(all_vals), max(all_vals)
            if ymin == ymax:
                ymin -= 0.5; ymax += 0.5
            pad = 0.1 * (ymax - ymin)
            ax.set_xlim(0, max(100, max_len))
            ax.set_ylim(ymin - pad, ymax + pad)

        # update legend text to include last values
        try:
            for txt, ln_buf, lbl in zip(legend.get_texts(), buffers, labels):
                if ln_buf:
                    txt.set_text(f"{lbl}: {ln_buf[-1]:.3f}")
                else:
                    txt.set_text(f"{lbl}: -")
        except Exception:
            pass

        frame_counter += 1
        return line_objs

    ani = FuncAnimation(fig, update, interval=UPDATE_INTERVAL_MS, blit=False, cache_frame_data=False)
    try:
        plt.show()
    finally:
        stop_evt.set()
        rt.join(timeout=0.5)
        try:
            ser.close()
        except Exception:
            pass
        csv_file.close()
        print(f"Closed. Data saved to: {csv_filename}")

if __name__ == "__main__":
    main()