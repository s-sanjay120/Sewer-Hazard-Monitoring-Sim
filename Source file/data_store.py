import csv
import hashlib
import re
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SENSOR_LOG_PATH = DATA_DIR / "sensor_data.txt"
SENSOR_CSV_PATH = DATA_DIR / "sensor_data.csv"
DATABASE_PATH = DATA_DIR / "sewer_data.db"

CSV_FIELDS = [
    "source_key",
    "timestamp",
    "methane",
    "air_quality",
    "temperature",
    "humidity",
]

READING_PATTERN = re.compile(
    r"(?P<timestamp>[^|\r\n]+)\s*\|\s*MQ-4 \(Methane\):\s*(?P<methane>-?\d+(?:\.\d+)?)\s*\r?\n"
    r"[^|\r\n]+\|\s*MQ-135 \(Air Quality\):\s*(?P<air_quality>-?\d+(?:\.\d+)?)\s*\r?\n"
    r"[^|\r\n]+\|\s*Temperature:\s*(?P<temperature>-?\d+(?:\.\d+)?)\s*°?C\s*\r?\n"
    r"[^|\r\n]+\|\s*Humidity:\s*(?P<humidity>-?\d+(?:\.\d+)?)\s*%",
    re.MULTILINE,
)


def initialize_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_key TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                methane REAL NOT NULL,
                air_quality REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                methane REAL,
                air_quality REAL,
                temperature REAL,
                humidity REAL,
                risk TEXT,
                anomaly TEXT
            )
            """
        )


def parse_sensor_log():
    if not SENSOR_LOG_PATH.exists():
        return []

    text = SENSOR_LOG_PATH.read_text(encoding="utf-8")
    readings = []
    for match in READING_PATTERN.finditer(text):
        values = match.groupdict()
        values["timestamp"] = values["timestamp"].strip()
        source_text = f"{match.start()}|{match.group(0).replace(chr(13) + chr(10), chr(10))}"
        values["source_key"] = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        readings.append(values)
    return readings


def sync_sensor_log():
    readings = parse_sensor_log()
    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        existing_keys = {
            row[0]
            for row in connection.execute("SELECT source_key FROM sensor_readings")
        }
        new_readings = [
            reading for reading in readings if reading["source_key"] not in existing_keys
        ]

        connection.executemany(
            """
            INSERT INTO sensor_readings
            (source_key, timestamp, methane, air_quality, temperature, humidity)
            VALUES (:source_key, :timestamp, :methane, :air_quality, :temperature, :humidity)
            """,
            new_readings,
        )

    if new_readings:
        csv_exists = SENSOR_CSV_PATH.exists() and SENSOR_CSV_PATH.stat().st_size > 0
        with SENSOR_CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
            if not csv_exists:
                writer.writeheader()
            writer.writerows(new_readings)

    return len(new_readings)
