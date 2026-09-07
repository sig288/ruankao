import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, JSON
from app.database import Base

def generate_plan_id():
    return f"plan_{uuid.uuid4().hex[:12]}"

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(String(36), primary_key=True, default=generate_plan_id)
    user_id = Column(String(36), unique=True, index=True, nullable=False)
    exam_date = Column(String(16), nullable=False)  # 'YYYY-MM-DD'
    daily_minutes = Column(Integer, default=60, nullable=False)
    tasks = Column(JSON, nullable=True)  # List of daily missions
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
