import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest

data_dir = Path(__file__).resolve().parent.parent / "data"
model_dir = Path(__file__).resolve().parent.parent / "models"
df = pd.read_csv(data_dir / "sensor_data.csv")

x = df[
    [
        "methane",
        "air_quality",
        "temperature",
        "humidity"
    ]
]

iso = IsolationForest(
    contamination=0.05,
    random_state=42
)

iso.fit(x)

# ensure a repo-level models/ directory exists and save the model there
models_dir = Path(__file__).resolve().parent.parent / "models"
models_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(iso, models_dir / "isolation_forest.pkl")
print(df.columns.tolist())