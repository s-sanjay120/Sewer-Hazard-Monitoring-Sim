# CCP 7th Sem - Sewer Hazard Detection System

A real-time sewer hazard detection system with a modern React frontend and robust backend infrastructure.

## Project Overview

This application provides comprehensive monitoring and prediction of hazardous conditions in sewer systems. The system enables real-time analysis of environmental sensor data and delivers actionable risk assessments.

**Key Features:**

- User-friendly React dashboard for real-time monitoring
- Machine learning-powered risk classification
- Anomaly detection and forecasting
- Comprehensive prediction history and analytics
- RESTful FastAPI backend with optimized data handling
- Persistent data storage with SQLite

## System Architecture

### Frontend
- **React** - Modern, responsive user interface for dashboard and data visualization

### Backend
- **FastAPI** - High-performance API endpoints for predictions and data retrieval
- **Machine Learning Models:**
  - Random Forest - Risk classification based on sensor inputs
  - LSTM - Time-series forecasting for trend analysis
- **SQLite** - Local database for prediction logs and historical data

## Core Workflow

1. Users input environmental sensor readings (methane, air quality, temperature, humidity) through the React dashboard
2. Data is sent to the FastAPI backend for processing
3. Machine learning models classify risk levels and generate forecasts
4. Results are returned to the dashboard with:
   - Risk classification
   - Anomaly detection status
   - Predictive forecasts
   - Historical trend analysis
5. All predictions are persisted for audit trails and analytics

## Project Structure

```
├── frontend/                    # React application
│   └── ...
├── backend.py                  # FastAPI application and routes
├── ccp.py                       # Risk classification logic
├── Random_forest_model.py       # Random forest model training/inference
├── lstm.py                      # LSTM forecasting model
├── database.py                  # Database helper functions
├── requirements.txt             # Python dependencies
└── data/                        # Sample datasets for testing
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+ (for React frontend)

### Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

```bash
python -m uvicorn backend:app --reload
```

The API will be available at `http://localhost:8000`

### Run the Frontend

```bash
cd frontend
npm start
```

The React dashboard will be available at `http://localhost:3000`

## Usage

1. Open the dashboard at `http://localhost:3000`
2. Input sensor readings (methane levels, air quality index, temperature, humidity)
3. The system processes the input and displays:
   - Risk assessment result
   - Anomaly detection indicators
   - Forecast predictions
   - Historical data visualization
4. Review prediction history for trends and patterns

## Features

- **Real-time Monitoring** - Live sensor data processing and analysis
- **Risk Assessment** - ML-based classification of hazard levels
- **Anomaly Detection** - Identification of unusual patterns in sensor data
- **Time-series Forecasting** - LSTM-based predictions of future conditions
- **Data Persistence** - Complete audit trail of all predictions
- **Analytics Dashboard** - Visualization and exploration of historical trends

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React, TypeScript/JavaScript |
| Backend | FastAPI (Python) |
| ML Models | Scikit-learn (Random Forest), TensorFlow/Keras (LSTM) |
| Database | SQLite |
| API | REST |

## Development

This is a fully functional application designed for production deployment. The codebase is structured for scalability and maintainability with clear separation of concerns between frontend and backend components.

## Notes

- Ensure all dependencies in `requirements.txt` are installed before running the backend
- The React frontend requires Node.js and npm to be installed and configured
- SQLite database is created automatically on first run
- Sample datasets are available in the `data/` directory for testing and validation

## Support

For issues or questions regarding the system, please refer to the project documentation or create an issue in the repository.
