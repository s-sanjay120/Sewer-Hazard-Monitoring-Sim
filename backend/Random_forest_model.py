import random
import uuid
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report 
import pandas as pd
import joblib

random.seed(42)

data_dir = Path(__file__).resolve().parent.parent / "data"
df = pd.read_csv(data_dir / "sensor_data.csv")
model_dir = Path(__file__).resolve().parent.parent / "models"
model_dir.mkdir(parents=True, exist_ok=True)

# expected feature columns in the CSV (lowercase)
feature_cols = ["methane", "air_quality", "temperature", "humidity"]
missing = [c for c in feature_cols if c not in df.columns]
if missing:
    raise KeyError(f"Missing feature columns in CSV: {missing}. Available: {list(df.columns)}")

# add a risk label using a more realistic heuristic for sewer-gas hazard monitoring

def compute_risk(row):
    risk_score = 0

    # methane: higher concentrations increase explosion and asphyxiation risk
    if row["methane"] > 2000:
        risk_score += 3
    elif row["methane"] > 1000:
        risk_score += 2
    elif row["methane"] > 500:
        risk_score += 1

    # air quality: elevated pollutant levels indicate poor ventilation / gas contamination
    if row["air_quality"] > 600:
        risk_score += 3
    elif row["air_quality"] > 350:
        risk_score += 2
    elif row["air_quality"] > 200:
        risk_score += 1

    # temperature: higher temperatures can indicate overheating or active hazard conditions
    if row["temperature"] > 45:
        risk_score += 2
    elif row["temperature"] > 35:
        risk_score += 1

    # humidity: extreme humidity can worsen condensation and gas retention
    if row["humidity"] > 95:
        risk_score += 2
    elif row["humidity"] > 80:
        risk_score += 1

    if risk_score <= 1:
        return "Safe"
    elif risk_score <= 3:
        return "Warning"
    elif risk_score <= 5:
        return "High Risk"
    return "Critical"


def create_synthetic_rows(target_label, count):
    synthetic_rows = []

    for _ in range(count):
        while True:
            if target_label == "Safe":
                methane = round(random.uniform(120, 350), 2)
                air_quality = round(random.uniform(100, 250), 2)
                temperature = round(random.uniform(14, 27), 2)
                humidity = round(random.uniform(55, 78), 2)
            elif target_label == "Warning":
                methane = round(random.uniform(450, 900), 2)
                air_quality = round(random.uniform(220, 400), 2)
                temperature = round(random.uniform(24, 34), 2)
                humidity = round(random.uniform(70, 88), 2)
            elif target_label == "High Risk":
                methane = round(random.uniform(900, 1600), 2)
                air_quality = round(random.uniform(400, 650), 2)
                temperature = round(random.uniform(30, 40), 2)
                humidity = round(random.uniform(80, 95), 2)
            else:
                methane = round(random.uniform(1600, 2800), 2)
                air_quality = round(random.uniform(650, 900), 2)
                temperature = round(random.uniform(35, 45), 2)
                humidity = round(random.uniform(88, 99), 2)

            sample = pd.Series({
                "methane": methane,
                "air_quality": air_quality,
                "temperature": temperature,
                "humidity": humidity,
            })
            if compute_risk(sample) == target_label:
                synthetic_rows.append({
                    "source_key": f"synthetic-{uuid.uuid4().hex}",
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "methane": methane,
                    "air_quality": air_quality,
                    "temperature": temperature,
                    "humidity": humidity,
                    "risk": target_label,
                    "is_synthetic": True,
                })
                break

    return pd.DataFrame(synthetic_rows)


if "risk" not in df.columns:
    df["risk"] = df.apply(compute_risk, axis=1)

if "is_synthetic" not in df.columns:
    df["is_synthetic"] = False

# balance the classes by adding synthetic sewer-style samples for underrepresented labels
for label in ["Safe", "Warning", "High Risk", "Critical"]:
    current_count = int((df["risk"] == label).sum())
    if current_count < 40:
        synthetic = create_synthetic_rows(label, 40 - current_count)
        if not synthetic.empty:
            df = pd.concat([df, synthetic], ignore_index=True)

# recompute risk for the full dataset, then save it back to disk
# this keeps the labels consistent for both real and synthetic rows
df["risk"] = df.apply(compute_risk, axis=1)
df.to_csv(data_dir / "sensor_data.csv", index=False)

X = df[feature_cols]
y = df["risk"]

X_train, X_test, y_train, y_test = train_test_split(
   X, y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
        random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))

joblib.dump(model, model_dir / "sewer_rf_model.pkl")

print(classification_report(y_test, pred))

model = joblib.load(model_dir / "sewer_rf_model.pkl")

prediction = model.predict([[700, 500, 40, 90]])

print(prediction)