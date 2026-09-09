from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ml, bundle, graph, solver

app = FastAPI(title="Railway Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/schedule")
def get_schedule():
    raw_defects = [
        {"task_id": "T1", "track_section": "S1", "defect_type": "Rail crack", "days_overdue": 5},
        {"task_id": "T2", "track_section": "S1", "defect_type": "Ballast wear", "days_overdue": 2},
        {"task_id": "T3", "track_section": "S2", "defect_type": "Signal fault", "days_overdue": 8}
    ]

    processed = [dict(d, **ml.predict_urgency_and_time(d["defect_type"], d["days_overdue"])) for d in raw_defects]
    bundled = bundle.bundle_corridor_jobs(processed)
    return solver.solve_schedule(bundled)
