from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import sqlite3

app = FastAPI()

model = joblib.load("sewer_rf_model.pkl")
_last_payload = None


class SensorData(BaseModel):
    methane: float
    air_quality: float
    temperature: float
    humidity: float


@app.get("/")
def home():
    return {"message": "Sewer Hazard API Running"}


@app.post("/predict")
def predict(data: SensorData):
    sample = pd.DataFrame(
        {
            "Methane": [data.methane],
            "Air_quality": [data.air_quality],
            "Temperature": [data.temperature],
            "Humidity": [data.humidity],
        }
    )

    prediction = model.predict(sample)
    risk = str(prediction[0])
    anomaly = "Normal" if risk in {"Safe", "Warning"} else "Anomaly"

    conn = sqlite3.connect("sewer_data.db")
    cursor = conn.cursor()

    cursor.execute(
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

    cursor.execute(
        """
        INSERT INTO predictions
        (methane, air_quality, temperature, humidity, risk, anomaly)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.methane,
            data.air_quality,
            data.temperature,
            data.humidity,
            risk,
            anomaly,
        ),
    )
    conn.commit()
    conn.close()

    global _last_payload
    _last_payload = {
        "methane": data.methane,
        "air_quality": data.air_quality,
        "temperature": data.temperature,
        "humidity": data.humidity,
    }

    explanation = {
        "methane": round(float(data.methane) / 10, 2),
        "air_quality": round(float(data.air_quality) / 10, 2),
        "temperature": round(float(data.temperature) / 10, 2),
        "humidity": round(float(data.humidity) / 10, 2),
    }

    return {
        "risk": risk,
        "anomaly": anomaly,
        "explanation": explanation,
    }


@app.get("/forecast")
def forecast():
    global _last_payload
    if _last_payload is None:
        _last_payload = {
            "methane": 500.0,
            "air_quality": 100.0,
            "temperature": 25.0,
            "humidity": 50.0,
        }

    return {
        "predicted_methane": round(_last_payload["methane"] + 15, 1),
        "predicted_air_quality": round(_last_payload["air_quality"] + 10, 1),
        "predicted_temperature": round(_last_payload["temperature"] + 1.5, 1),
        "predicted_humidity": round(_last_payload["humidity"] + 2.0, 1),
    }


@app.get("/history")
def history():
    conn = sqlite3.connect("sewer_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, methane, air_quality, temperature, humidity, risk, anomaly FROM predictions"
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "ID": row[0],
            "Methane": row[1],
            "Air Quality": row[2],
            "Temperature": row[3],
            "Humidity": row[4],
            "Risk": row[5],
            "Anomaly": row[6] or "Normal",
        }
        for row in rows
    ]