import csv
import hashlib
import re
import sqlite3
from pathlib import Path

import pandas as pd

from H2S_estimation import calculate_h2s_estimate, predict_risk


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
    "risk",
    "anomaly",
    "estimated_h2s",
]

READING_PATTERN = re.compile(
    r"(?P<timestamp>[^|\r\n]+)\s*\|\s*MQ-4 \(Methane\):\s*(?P<methane>-?\d+(?:\.\d+)?)\s*\r?\n"
    r"[^|\r\n]+\|\s*MQ-135 \(Air Quality\):\s*(?P<air_quality>-?\d+(?:\.\d+)?)\s*\r?\n"
    r"[^|\r\n]+\|\s*Temperature:\s*(?P<temperature>-?\d+(?:\.\d+)?)\s*°?C\s*\r?\n"
    r"[^|\r\n]+\|\s*Humidity:\s*(?P<humidity>-?\d+(?:\.\d+)?)\s*%",
    re.MULTILINE,
)


def _ensure_column(connection, table_name, column_name, definition):
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table_name})")}
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


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
                humidity REAL NOT NULL,
                risk TEXT,
                anomaly TEXT,
                estimated_h2s REAL
            )
            """
        )
        _ensure_column(connection, "sensor_readings", "risk", "TEXT")
        _ensure_column(connection, "sensor_readings", "anomaly", "TEXT")
        _ensure_column(connection, "sensor_readings", "estimated_h2s", "REAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                methane REAL,
                air_quality REAL,
                temperature REAL,
                humidity REAL,
                risk TEXT,
                anomaly TEXT,
                estimated_h2s REAL
            )
            """
        )
        _ensure_column(connection, "predictions", "estimated_h2s", "REAL")


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


def import_sensor_csv():
    if not SENSOR_CSV_PATH.exists():
        return 0

    initialize_database()

    df = pd.read_csv(SENSOR_CSV_PATH)
    if df.empty:
        return 0

    prepared_readings = []
    for row in df.to_dict(orient="records"):
        timestamp = str(row.get("timestamp", "")).strip()
        methane = float(row.get("methane", 0.0))
        air_quality = float(row.get("air_quality", 0.0))
        temperature = float(row.get("temperature", 0.0))
        humidity = float(row.get("humidity", 0.0))
        source_key = str(row.get("source_key") or hashlib.sha256(
            f"{timestamp}|{methane}|{air_quality}|{temperature}|{humidity}".encode("utf-8")
        ).hexdigest())

        risk = str(row.get("risk") or predict_risk(methane, air_quality, temperature, humidity))
        anomaly = "Normal" if risk in {"Safe", "Warning"} else "Anomaly"
        estimated_h2s_value = row.get("estimated_h2s")
        if pd.isna(estimated_h2s_value):
            estimated_h2s_value = calculate_h2s_estimate(
                methane,
                air_quality,
                temperature,
                humidity,
                risk,
            )["estimated_h2s"]

        prepared_readings.append(
            {
                "source_key": source_key,
                "timestamp": timestamp,
                "methane": methane,
                "air_quality": air_quality,
                "temperature": temperature,
                "humidity": humidity,
                "risk": risk,
                "anomaly": anomaly,
                "estimated_h2s": float(estimated_h2s_value),
            }
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        existing_keys = {
            row[0]
            for row in connection.execute("SELECT source_key FROM sensor_readings")
        }
        new_readings = [
            reading for reading in prepared_readings if reading["source_key"] not in existing_keys
        ]

        if new_readings:
            connection.executemany(
                """
                INSERT INTO sensor_readings
                (source_key, timestamp, methane, air_quality, temperature, humidity, risk, anomaly, estimated_h2s)
                VALUES (:source_key, :timestamp, :methane, :air_quality, :temperature, :humidity, :risk, :anomaly, :estimated_h2s)
                """,
                new_readings,
            )
            connection.executemany(
                """
                INSERT INTO predictions
                (methane, air_quality, temperature, humidity, risk, anomaly, estimated_h2s)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        reading["methane"],
                        reading["air_quality"],
                        reading["temperature"],
                        reading["humidity"],
                        reading["risk"],
                        reading["anomaly"],
                        reading["estimated_h2s"],
                    )
                    for reading in new_readings
                ],
            )

    return len(new_readings)


def sync_sensor_log():
    import_sensor_csv()
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

        prepared_readings = []
        for reading in new_readings:
            methane = float(reading["methane"])
            air_quality = float(reading["air_quality"])
            temperature = float(reading["temperature"])
            humidity = float(reading["humidity"])
            risk = predict_risk(methane, air_quality, temperature, humidity)
            anomaly = "Normal" if risk in {"Safe", "Warning"} else "Anomaly"
            h2s_result = calculate_h2s_estimate(
                methane,
                air_quality,
                temperature,
                humidity,
                risk,
            )
            prepared_readings.append(
                {
                    **reading,
                    "methane": methane,
                    "air_quality": air_quality,
                    "temperature": temperature,
                    "humidity": humidity,
                    "risk": risk,
                    "anomaly": anomaly,
                    "estimated_h2s": h2s_result["estimated_h2s"],
                }
            )

        connection.executemany(
            """
            INSERT INTO sensor_readings
            (source_key, timestamp, methane, air_quality, temperature, humidity, risk, anomaly, estimated_h2s)
            VALUES (:source_key, :timestamp, :methane, :air_quality, :temperature, :humidity, :risk, :anomaly, :estimated_h2s)
            """,
            prepared_readings,
        )

        connection.executemany(
            """
            INSERT INTO predictions
            (methane, air_quality, temperature, humidity, risk, anomaly, estimated_h2s)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    reading["methane"],
                    reading["air_quality"],
                    reading["temperature"],
                    reading["humidity"],
                    reading["risk"],
                    reading["anomaly"],
                    reading["estimated_h2s"],
                )
                for reading in prepared_readings
            ],
        )

    if prepared_readings:
        csv_exists = SENSOR_CSV_PATH.exists() and SENSOR_CSV_PATH.stat().st_size > 0
        with SENSOR_CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
            if not csv_exists:
                writer.writeheader()
            writer.writerows(prepared_readings)

    return len(new_readings)
