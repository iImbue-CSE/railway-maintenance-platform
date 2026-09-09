def bundle_corridor_jobs(tasks: list):
    for task in tasks:
        task["requires_power_block"] = task.get("defect_type") in ["Signal fault", "Overhead wear"] or task.get("urgency_score", 0) > 85
    return tasks
