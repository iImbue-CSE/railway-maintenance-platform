import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

DATA_PATH = "data/maintenance_data.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print(f"Number of records: {len(df)}")


# --------------------------------------------------
# 2. Define input features
# --------------------------------------------------

features = [
    "defect_type",
    "days_overdue",
    "section_load",
    "failure_risk"
]

X = df[features]


# --------------------------------------------------
# 3. Define targets
# --------------------------------------------------

y_urgency = df["urgency_score"]

y_repair = df["repair_hours"]


# --------------------------------------------------
# 4. Preprocessing
# --------------------------------------------------

categorical_features = ["defect_type"]

numeric_features = [
    "days_overdue",
    "section_load",
    "failure_risk"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# --------------------------------------------------
# 5. Create Urgency Model
# --------------------------------------------------

urgency_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42
            )
        )
    ]
)


# --------------------------------------------------
# 6. Create Repair Time Model
# --------------------------------------------------

repair_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42
            )
        )
    ]
)


# --------------------------------------------------
# 7. Split data for urgency model
# --------------------------------------------------

X_train_u, X_test_u, y_train_u, y_test_u = train_test_split(
    X,
    y_urgency,
    test_size=0.2,
    random_state=42
)


# --------------------------------------------------
# 8. Split data for repair-time model
# --------------------------------------------------

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X,
    y_repair,
    test_size=0.2,
    random_state=42
)


# --------------------------------------------------
# 9. Train urgency model
# --------------------------------------------------

print("\nTraining urgency model...")

urgency_model.fit(
    X_train_u,
    y_train_u
)

print("Urgency model trained successfully!")


# --------------------------------------------------
# 10. Train repair-time model
# --------------------------------------------------

print("\nTraining repair-time model...")

repair_model.fit(
    X_train_r,
    y_train_r
)

print("Repair-time model trained successfully!")


# --------------------------------------------------
# 11. Evaluate urgency model
# --------------------------------------------------

urgency_predictions = urgency_model.predict(X_test_u)

urgency_mae = mean_absolute_error(
    y_test_u,
    urgency_predictions
)

urgency_r2 = r2_score(
    y_test_u,
    urgency_predictions
)


# --------------------------------------------------
# 12. Evaluate repair-time model
# --------------------------------------------------

repair_predictions = repair_model.predict(X_test_r)

repair_mae = mean_absolute_error(
    y_test_r,
    repair_predictions
)

repair_r2 = r2_score(
    y_test_r,
    repair_predictions
)


# --------------------------------------------------
# 13. Display results
# --------------------------------------------------

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("\nUrgency Model:")
print(f"MAE: {urgency_mae:.2f}")
print(f"R2 Score: {urgency_r2:.2f}")

print("\nRepair Time Model:")
print(f"MAE: {repair_mae:.2f} hours")
print(f"R2 Score: {repair_r2:.2f}")


# --------------------------------------------------
# 14. Save trained models
# --------------------------------------------------

joblib.dump(
    urgency_model,
    "models/urgency_model.pkl"
)

joblib.dump(
    repair_model,
    "models/repair_time_model.pkl"
)

print("\n==============================")
print("MODELS SAVED SUCCESSFULLY")
print("==============================")

print("models/urgency_model.pkl")
print("models/repair_time_model.pkl")