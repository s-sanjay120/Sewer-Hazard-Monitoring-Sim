import pandas as pd

df = pd.read_csv("new_synthetic_data.csv")

timestamp = pd.date_range(
    start="2026-06-25 10:00:00",
    periods=len(df),
    freq="5s"
)

df.insert(0, "timestamp", timestamp)

df.to_csv("new_synthetic_data_with_time.csv", index=False)
print(df.head())
print(df.columns) 