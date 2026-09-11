import joblib
import pandas as pd


# Load trained models
urgency_model = joblib.load("models/urgency_model.pkl")
repair_model = joblib.load("models/repair_time_model.pkl")


# Example maintenance task
task = pd.DataFrame([
    {
        "defect_type": "Signal fault",
        "days_overdue": 10,
        "section_load": 0.88,
        "failure_risk": 0.64
    }
])


# Predict urgency
urgency_prediction = urgency_model.predict(task)[0]


# Predict repair time
repair_prediction = repair_model.predict(task)[0]


# Keep urgency between 0 and 100
urgency_prediction = max(
    0,
    min(100, urgency_prediction)
)


# Keep repair time positive
repair_prediction = max(
    0.5,
    repair_prediction
)


print("==============================")
print("ML MODEL TEST")
print("==============================")

print("\nInput:")
print(task)

print("\nPrediction:")
print(f"Urgency Score: {urgency_prediction:.2f}")
print(f"Estimated Repair Hours: {repair_prediction:.2f}")