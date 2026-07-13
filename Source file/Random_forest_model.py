from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report 
import pandas as pd
import joblib

df = pd.read_csv(r"C:\Users\sanja\Desktop\ccp 7th sem\new_synthetic_data.csv")

X = df[[
    "Methane",
    "Air_quality",
    "Temperature",
    "Humidity",
]]

y = df["Risk"]

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

joblib.dump(model, "sewer_rf_model.pkl")

print(classification_report(y_test, pred))

model = joblib.load("sewer_rf_model.pkl")

prediction = model.predict([[700, 500, 40, 90]])

print(prediction)