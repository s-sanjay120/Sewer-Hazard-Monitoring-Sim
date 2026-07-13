import joblib
import pandas as pd
import shap

# Load model
model = joblib.load("sewer_rf_model.pkl")

# Create explainer
explainer = shap.TreeExplainer(model)

# Sample input
sample = pd.DataFrame({
    "methane": [500],
    "air_quality": [120],
    "temperature": [30],
    "humidity": [65]
})

# Get SHAP values
shap_values = explainer(sample)

print(shap_values.values)
print(shap_values.base_values)