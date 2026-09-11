import numpy as np
import pandas as pd


# Make results reproducible
np.random.seed(42)


# --------------------------------------------------
# Defect types
# --------------------------------------------------

defect_types = [
    "Rail crack",
    "Ballast wear",
    "Signal fault",
    "Point failure",
    "Overhead wear"
]


# --------------------------------------------------
# Number of records
# --------------------------------------------------

NUM_RECORDS = 1000


records = []


# --------------------------------------------------
# Generate maintenance records
# --------------------------------------------------

for _ in range(NUM_RECORDS):

    # Random defect type
    defect_type = np.random.choice(defect_types)

    # Number of days the maintenance task is overdue
    days_overdue = np.random.randint(0, 31)

    # Track section load: 0 to 1
    section_load = round(
        np.random.uniform(0.1, 1.0),
        2
    )

    # Historical failure risk: 0 to 1
    failure_risk = round(
        np.random.uniform(0.1, 1.0),
        2
    )


    # --------------------------------------------------
    # Generate urgency score
    # --------------------------------------------------

    urgency = (
        20
        + (days_overdue * 1.8)
        + (section_load * 20)
        + (failure_risk * 35)
    )


    # Different defects have different importance
    defect_bonus = {
        "Rail crack": 15,
        "Point failure": 12,
        "Signal fault": 10,
        "Overhead wear": 8,
        "Ballast wear": 4
    }

    urgency += defect_bonus[defect_type]


    # Add small random variation
    urgency += np.random.normal(0, 4)


    # Keep score between 0 and 100
    urgency = np.clip(
        urgency,
        0,
        100
    )


    # --------------------------------------------------
    # Generate repair time
    # --------------------------------------------------

    base_repair_time = {
        "Rail crack": 4.0,
        "Ballast wear": 6.0,
        "Signal fault": 3.0,
        "Point failure": 3.5,
        "Overhead wear": 4.5
    }

    repair_hours = (
        base_repair_time[defect_type]
        + (days_overdue * 0.03)
        + (failure_risk * 0.8)
        + np.random.normal(0, 0.3)
    )


    # Repair time cannot be below 0.5 hours
    repair_hours = max(
        0.5,
        repair_hours
    )


    records.append({
        "defect_type": defect_type,
        "days_overdue": days_overdue,
        "section_load": section_load,
        "failure_risk": failure_risk,
        "urgency_score": round(urgency, 2),
        "repair_hours": round(repair_hours, 2)
    })


# --------------------------------------------------
# Create DataFrame
# --------------------------------------------------

df = pd.DataFrame(records)


# --------------------------------------------------
# Save CSV
# --------------------------------------------------

output_path = "data/maintenance_data.csv"

df.to_csv(
    output_path,
    index=False
)


# --------------------------------------------------
# Display information
# --------------------------------------------------

print("Dataset created successfully!")
print(f"Number of records: {len(df)}")
print(f"Saved to: {output_path}")

print("\nFirst 5 records:")
print(df.head())

print("\nDataset information:")
print(df.info())

print("\nDefect type distribution:")
print(df["defect_type"].value_counts())