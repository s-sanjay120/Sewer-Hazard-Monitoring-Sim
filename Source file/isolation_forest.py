import pandas as pd
import joblib   
df=pd.read_csv("new_synthetic_data.csv")

x = df[
    [
        "methane",
        "air_quality",
        "temperature",
        "humidity"
    ]
]
from sklearn.ensemble import IsolationForest

iso = IsolationForest(
    contamination=0.05,
    random_state=42
)

iso.fit(x)

joblib.dump(iso, "isolation_forest.pkl")
print(df.columns.tolist())