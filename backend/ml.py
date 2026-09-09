def predict_urgency_and_time(defect_type: str, days_overdue: int):
    base_score = 50 + (days_overdue * 5)
    urgency_score = min(max(base_score, 0), 100)
    repair_times = {"Rail crack": 4, "Ballast wear": 6, "Signal fault": 3, "Point failure": 3}
    return {"urgency_score": urgency_score, "est_repair_hours": repair_times.get(defect_type, 2)}
