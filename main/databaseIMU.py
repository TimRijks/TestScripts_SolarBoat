import serial
import time
import mysql.connector

# ---------------------------
# CONFIGURATION
# ---------------------------
SERIAL_PORT = "COM6"          # or /dev/ttyUSB0
BAUD_RATE = 115200

TAILSCALE_HOST = "100.75.92.26" # your MySQL server Tailscale IP
MYSQL_USER = "mse"
MYSQL_PASS = "embeddedBit"
MYSQL_DB   = "IMU"

# ---------------------------
# CONNECT TO MYSQL OVER TAILSCALE
# ---------------------------
db = mysql.connector.connect(
    host=TAILSCALE_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB,
    port=3306
)
cursor = db.cursor()

# ---------------------------
# OPEN SERIAL PORT
# ---------------------------
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print("Listening on", SERIAL_PORT)

# ---------------------------
# MAIN LOOP
# ---------------------------
start_time = time.time()
while True:
    line = ser.readline()
    try:
        line = line.decode('utf-8').strip()
    except UnicodeDecodeError:
        print("Skipping undecodable line")
        continue

    if not line:
        continue

    parts = line.split(",")
    if len(parts) != 12:
        print("Skipping invalid line:", line)
        continue

    try:
        # Extract float values from each labeled part
        values = [float(p.split(":")[1]) for p in parts]
    except Exception as e:
        print("Conversion error:", e, "Line:", line)
        continue
    
    timestamp_ms = int((time.time() - start_time) * 1000)

    sql = """
    INSERT INTO IMU_data
    (timestamp_ms, ax, ay, az, gx, gy, gz, mx, my, mz, heading, pitch, roll)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    try:
        cursor.execute(sql, (timestamp_ms, *values))
        db.commit()
        print("Inserted:", *values)
    except Exception as e:
        print("DB error:", e)
        continue