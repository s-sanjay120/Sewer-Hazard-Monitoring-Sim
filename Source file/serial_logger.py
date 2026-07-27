import serial
from serial.tools import list_ports
from datetime import datetime

from data_store import SENSOR_LOG_PATH, sync_sensor_log

PORT = "COM4"      

BAUD_RATE = 9600

LOG_FILE = SENSOR_LOG_PATH

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
except serial.SerialException as exc:
    available_ports = [port.device for port in list_ports.comports()]
    print(f"Could not open {PORT}: {exc}")
    print("Close any Arduino Serial Monitor or other program using this port, then try again.")
    print(f"Detected ports: {', '.join(available_ports) or 'none'}")
    raise SystemExit(1) from exc

print(f"Logging data to {LOG_FILE}...")
print("Press Ctrl+C to stop.\n")

with open(LOG_FILE, "a") as file:
    try:
        while True:
            line = ser.readline().decode("utf-8").strip()

            if not line:
                continue

            # Ignore header from Arduino
            if line.startswith("MQ4"):
                continue

            timestamp = datetime.now().strftime("%H:%M")
            entry = f"{timestamp} | {line}"

            print(entry)
            file.write(entry + "\n")
            file.flush()
            sync_sensor_log()

    except KeyboardInterrupt:
        print("\nLogging stopped.")

ser.close()
