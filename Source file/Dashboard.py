import os
import requests
import streamlit as st
import pandas as pd

API_BASE_URLS = [
    url.strip()
    for url in [
        os.getenv("SEWER_API_URL", "").strip(),
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
    ]
    if url.strip()
]


def request_json(method, path, payload=None, timeout=5):
    last_error = None
    for base_url in API_BASE_URLS:
        try:
            if method == "get":
                response = requests.get(f"{base_url}{path}", timeout=timeout)
            else:
                response = requests.post(
                    f"{base_url}{path}",
                    json=payload,
                    timeout=timeout,
                )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Unable to reach the API: {last_error}")


st.set_page_config(
        page_title="Sewer Detection System",
        page_icon="🚨",
        layout="wide"
        )

st.title("🚨 AI Sewer Hazard Detection System")

st.subheader("Enter Sensor Values")

col1,col2 = st.columns(2)

with col1:
        methane = st.slider("Methane (ppm)",0, 1000, 500)
        air_quality = st.slider("Air Quality (ppm)",0, 500, 100)

with col2:
        temperature = st.slider("Temperature (°C)",-20, 50, 25)
        humidity = st.slider("Humidity (%)",0, 100, 50)

if st.button("Predict Hazard"):
        payload = {
            "methane": methane,
            "air_quality": air_quality,
            "temperature": temperature,
            "humidity": humidity
        }
        try:
            result = request_json("post", "/predict", payload=payload)
        except Exception as exc:
            st.error(f"Prediction API is unavailable: {exc}")
            st.stop()

        st.write(result)
        risk = result["risk"]
        anomaly = result["anomaly"]

        if anomaly == "Normal":
            st.success("✅ Anomaly Status: Normal")
        else:
            st.error("⚠️ Anomaly Detected")
        st.write()
        risk = risk.lower()

        if risk == "safe":
            st.success("🟢 Risk Level: Safe")

        elif risk == "warning":
            st.warning("🟡 Risk Level: Warning")

        elif risk == "high risk":
            st.warning("🟠 Risk Level: High Risk")

        else:
            st.error("🔴 Risk Level: Critical")
        
        st.subheader("Current Sensor Readings")
        st.subheader("🧠 AI Explanation")   

        explanation = result["explanation"]

        exp_df = pd.DataFrame(
        list(explanation.items()),
        columns=["Feature", "Importance"]
        )

        st.bar_chart(exp_df.set_index("Feature"))

        try:
            forecast = request_json("get", "/forecast")
        except Exception as exc:
            st.warning(f"Forecast unavailable: {exc}")
            forecast = {}

        forecast = forecast or {}
        if forecast.get("error"):
            st.warning(forecast["error"])
        else:
            st.subheader("📈 Forecast")

        c1, c2 = st.columns(2)

        with c1:
            methane_forecast = forecast.get("predicted_methane", "N/A")
            air_quality_forecast = forecast.get("predicted_air_quality", "N/A")
            st.metric("Predicted Methane", f"{methane_forecast:.1f}" if isinstance(methane_forecast, (int, float)) else str(methane_forecast))
            st.metric("Predicted Air Quality", f"{air_quality_forecast:.1f}" if isinstance(air_quality_forecast, (int, float)) else str(air_quality_forecast))

        with c2:
            temperature_forecast = forecast.get("predicted_temperature", "N/A")
            humidity_forecast = forecast.get("predicted_humidity", "N/A")
            st.metric("Predicted Temperature", f"{temperature_forecast:.1f} °C" if isinstance(temperature_forecast, (int, float)) else str(temperature_forecast))
            st.metric("Predicted Humidity", f"{humidity_forecast:.1f} %" if isinstance(humidity_forecast, (int, float)) else str(humidity_forecast))

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Methane", f"{methane} ppm")
        c2.metric("Air Quality", f"{air_quality} ppm")
        c3.metric("Temperature", f"{temperature} °C")
        c4.metric("Humidity", f"{humidity}%")

        st.divider()

        st.subheader("📜 Prediction History")

df = pd.DataFrame(
        columns=[
            "ID",
            "Methane",
            "Air Quality",
            "Temperature",
            "Humidity",
            "Risk",
            "Anomaly"
        ]
    )

try:
    history = request_json("get", "/history")

    df = pd.DataFrame(
            history,
            columns=[
            "ID",
            "Methane",
            "Air Quality",
            "Temperature",
            "Humidity",
            "Risk",
            "Anomaly"
            ]
        )

    st.dataframe(df, width="stretch", hide_index=True)

    risk_counts = df["Risk"].value_counts()

    st.bar_chart(risk_counts)

except Exception as e:
    st.warning(f"Waiting for data... ({e})")
    st.subheader("📊 Dashboard Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", len(df))
    col2.metric("Safe", len(df[df["Risk"] == "Safe"]))
    col3.metric("Warning", len(df[df["Risk"] == "Warning"]))
    col4.metric("High Risk + Critical",
        len(df[df["Risk"].isin(["High Risk", "Critical"])]))

    st.subheader("📈 Risk Distribution")

    risk_counts = df["Risk"].value_counts()

    import plotly.express as px

    risk_counts = df["Risk"].value_counts()

    fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            labels={
            "x": "Risk Level",
            "y": "Count"
            },  
            title="Risk Distribution"
        )

    fig.update_layout(
        xaxis_title="Risk Level",
        yaxis_title="Number of Predictions"
        )
    fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                "Safe": "green",
                "Warning": "yellow",
                "High Risk": "orange",
                "Critical": "red"
            }
        )

    st.plotly_chart(
        fig,
        width="stretch"
        )