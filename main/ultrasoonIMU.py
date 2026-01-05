import serial
import time
import mysql.connector
import math

# ---------------------------
# CONFIGURATION
# ---------------------------
SERIAL_PORT = "COM6"
BAUD_RATE = 115200

MYSQL_HOST = "100.75.92.26"
MYSQL_USER = "mse"
MYSQL_PASS = "embeddedBit"
MYSQL_DB_recieve   = "Ultrasoon"
MYSQL_DB_send   = "IMU"

# Mechanisch model
H_MIN_CM = 0
H_MAX_CM = 10

# ---------------------------
# CONNECT TO MYSQL
# ---------------------------
db_receive = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB_recieve,
    port=3306
)
cursor_receive = db_receive.cursor()

db_send = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB_send,
    port=3306
)
cursor_send = db_send.cursor()

# ---------------------------
# FETCH ULTRASOON DATA RANGE
# ---------------------------
sql = f"""
SELECT counts * 0.0859655832 AS mm FROM Analog_data
ORDER BY ID ASC
"""
cursor_receive.execute(sql)
us_data = [row[0] for row in cursor_receive.fetchall()]
num_points = len(us_data)
print(f"Fetched {num_points} ultrasonic points from database.")

# ---------------------------
# OPEN SERIAL PORT
# ---------------------------
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print("Listening on", SERIAL_PORT)

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def corrected_height(distance_mm, roll_rad, pitch_rad):
    """Correct the ultrasonic distance for IMU roll/pitch"""
    distance_mm = float(distance_mm)
    cz = math.cos(pitch_rad) * math.cos(roll_rad)
    return (distance_mm * cz) / 10.0  # cm

def foil_angle(h_cm):
    """Map height to foil angle (0-10cm -> 0-10deg)"""
    h_cm = h_cm / 9

    if (h_cm <= 0): 
        h_cm = 0
    elif (h_cm >= 68): 
        h_cm = 10
    return h_cm


# ---------------------------
# MAIN LOOP
# ---------------------------
start_time = time.time()
current_index = 0

while current_index < num_points:
    # ---------- READ IMU ----------
    line = ser.readline()
    try:
        line = line.decode('utf-8').strip()
    except UnicodeDecodeError:
        continue

    if not line:
        continue

    parts = line.split(",")
    if len(parts) != 12:
        continue

    try:
        values = [float(p.split(":")[1]) for p in parts]
        ax, ay, az, gx, gy, gz, mx, my, mz, heading, pitch_deg, roll_deg = values
    except Exception:
        continue

    # ---------- USE ULTRASOON DATA ----------
    distance_mm = us_data[current_index]

    # Convert degrees to radians
    roll_rad = math.radians(roll_deg)
    pitch_rad = math.radians(pitch_deg)

    # Correct height for IMU orientation
    h_cm = corrected_height(distance_mm, roll_rad, pitch_rad)

    # Map height to foil angle
    foil_deg = foil_angle(h_cm)

    # ---------- PRINT ----------
    print(f"H: {h_cm:.2f} cm | Foil: {foil_deg:.2f} deg | Pitch: {pitch_deg:.2f} | Roll: {roll_deg:.2f}")

# ---------- WRITE TO IMU DATABASE ----------
    timestamp_ms = int((time.time() - start_time) * 1000)
    sql_insert = """
    INSERT INTO Analog_ultrasoonIMU
    (height, foil, pitch, roll)
    VALUES (%s,%s,%s,%s)
    """
    try:
        cursor_send.execute(sql_insert, (h_cm, foil_deg, pitch_deg, roll_deg))
        db_send.commit()
    except Exception as e:
        print("DB write error:", e)

    # ---------- NEXT DATA POINT ----------
    current_index += 1
    print(f"Processed {current_index}/{num_points} ultrasonic points.")
    time.sleep(0.01)  # 10ms delay to avoid busy-loop

print("All selected ultrasonic data used. Stopping.")