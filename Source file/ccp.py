import pandas as pd
import numpy as np
import random

rows = 5000

data = []

for _ in range(rows):

    methane = random.randint(50, 1000)        # ppm
    air_quality = random.randint(50, 600)     # ppm
    temperature = random.randint(20, 45)      # °C
    humidity = random.randint(30, 95)         # %

    # Risk Classification Rules
 
    risk_score = 0

    if methane > 750: 
        risk_score += 3
    elif methane > 500:
        risk_score += 2
    elif methane > 250:
        risk_score += 1

    if air_quality > 500:
        risk_score += 3
    elif air_quality > 350:
        risk_score += 2
    elif air_quality > 200:
        risk_score += 1

    if temperature > 40:
        risk_score += 1

    if humidity > 85:
        risk_score += 1

    if risk_score <= 1:
        risk = "Safe"
    elif risk_score <= 3:
        risk = "Warning"
    elif risk_score <= 5:
        risk = "High Risk"
    else:
        risk = "Critical"

    data.append([
        methane,
        air_quality,
        temperature,
        humidity,
        risk
    ])

df = pd.DataFrame(
    data,
    columns=[
        "methane",
        "air_quality",
        "temperature",
        "humidity",
        "risk"
    ]
)

df.to_csv("new_synthetic_data.csv", index=False)
print("Synthetic data generated successfully!") 



