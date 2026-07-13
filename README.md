# CCP 7th Sem - Prototype Sewer Hazard Detection Simulation

This repository is a prototype simulation of the main application that will eventually power a real-time sewer hazard detection system.

The goal of this project is to demonstrate how the final app will work from end to end:

- a user enters environmental sensor values in a dashboard,
- the backend processes the input using a machine learning model,
- the system classifies the risk level,
- the dashboard shows the prediction, anomaly status, and a simple forecast,
- prediction history is stored for review.

## Project Purpose

This is not the final production app yet. It is a working prototype that simulates the core workflow of the intended system so the team can test the UI, API, model interaction, and overall user experience.

## Current Prototype Flow

1. A Streamlit dashboard collects methane, air quality, temperature, and humidity values.
2. The dashboard sends the data to a FastAPI backend.
3. The backend loads a trained model and returns a risk classification.
4. The result is displayed in the dashboard for the user.
5. The output is saved in a local SQLite database for history and basic analytics.

## Main Files

- `Dashboard.py` - Streamlit user interface for the prototype
- `backend.py` - FastAPI backend for prediction and history endpoints
- `ccp.py` - core logic for risk classification rules
- `Random_forest_model.py` - random forest training/classification workflow
- `lstm.py` - LSTM-based time-series forecasting and training logic
- `database.py` - database helper logic
- `data/` - sample datasets used for simulation and testing

## Prototype Notes

This repository is intended to show the structure and behavior of the main application before full deployment and production hardening.

Current characteristics:

- lightweight demo-style implementation
- local database storage for prediction logs
- sample ML models and forecast logic
- simple dashboard-driven simulation of the final app

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Prototype

Start the API:

```bash
python -m uvicorn backend:app --reload
```

Run the dashboard:

```bash
streamlit run Dashboard.py
```

## Expected Outcome

When the prototype is running, the user can input sensor readings through the dashboard and see how the final application will likely function:

- prediction result,
- risk level,
- anomaly detection indicator,
- forecast values,
- prediction history visualization.

## Disclaimer

This repository represents a proof-of-concept simulation for the main application workflow. It is useful for development, demonstration, and testing, but it is not yet a finished production-grade system.
