from datetime import datetime, timedelta, timezone
from typing import List, Optional
import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session

from database import Base, engine, get_db

# --- SQLAlchemy Models ---

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    track_segment_id = Column(String, nullable=False)
    work_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    username = Column(String, nullable=True)
    endpoint = Column(String, nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# --- App & Security Configuration ---

app = FastAPI(title="Railway Security Gateway - SIH26027")

SECRET_KEY = "railway_secret_key_sih2026"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Initial Seeding ---

@app.on_event("startup")
def seed_data():
    db = next(get_db())
    if not db.query(Department).first():
        d1 = Department(id=1, name="Civil_Track")
        d2 = Department(id=2, name="Signal_Telecom")
        d3 = Department(id=3, name="Electrical_OHE")
        db.add_all([d1, d2, d3])
        db.commit()

        pwd_eng = bcrypt.hashpw(b"track123", bcrypt.gensalt()).decode("utf-8")
        pwd_sig = bcrypt.hashpw(b"signal123", bcrypt.gensalt()).decode("utf-8")
        pwd_ctrl = bcrypt.hashpw(b"control123", bcrypt.gensalt()).decode("utf-8")
        pwd_audit = bcrypt.hashpw(b"audit123", bcrypt.gensalt()).decode("utf-8")

        u1 = User(username="track_eng", hashed_password=pwd_eng, role="Civil_Engineer", department_id=1)
        u2 = User(username="signal_eng", hashed_password=pwd_sig, role="Signal_Engineer", department_id=2)
        u3 = User(username="controller", hashed_password=pwd_ctrl, role="Controller", department_id=None)
        u4 = User(username="safety_officer", hashed_password=pwd_audit, role="Auditor", department_id=None)
        
        db.add_all([u1, u2, u3, u4])
        db.commit()

# --- Auth Dependencies ---

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)):
        if user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{user['role']}' is unauthorized."
            )
        return user

# --- Pydantic Schemas ---

class RequestSchema(BaseModel):
    track_segment_id: str
    work_type: str
    duration_minutes: int

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    username: Optional[str]
    endpoint: str
    action: str
    status: str

    class Config:
        from_attributes = True

# --- API Endpoints ---

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt.checkpw(form_data.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token_data = {
        "sub": user.username,
        "role": user.role,
        "department_id": user.department_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/requests/create")
def create_request(
    data: RequestSchema,
    user: dict = Depends(RequireRole(["Civil_Engineer", "Signal_Engineer"])),
    db: Session = Depends(get_db)
):
    req = MaintenanceRequest(
        department_id=user["department_id"],
        track_segment_id=data.track_segment_id,
        work_type=data.work_type,
        duration_minutes=data.duration_minutes
    )
    db.add(req)
    log = AuditLog(
        username=user["sub"],
        endpoint="/requests/create",
        action=f"Created {data.work_type} block request",
        status="ALLOWED"
    )
    db.add(log)
    db.commit()
    return {"status": "Request logged", "department_id": user["department_id"]}

@app.post("/optimizer/run")
def trigger_optimizer(
    user: dict = Depends(RequireRole(["Controller"])),
    db: Session = Depends(get_db)
):
    log = AuditLog(
        username=user["sub"],
        endpoint="/optimizer/run",
        action="Triggered AI Optimization Engine",
        status="ALLOWED"
    )
    db.add(log)
    db.commit()
    return {"status": "Optimizer engine launched by railway controller"}

@app.get("/audit-logs", response_model=List[AuditLogResponse])
def view_audit_logs(
    user: dict = Depends(RequireRole(["Controller", "Auditor"])), 
    db: Session = Depends(get_db)
):
    return db.query(AuditLog).all()
