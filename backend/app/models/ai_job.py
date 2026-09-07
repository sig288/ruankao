import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database import Base

def generate_ai_job_id():
    return f"ai_{uuid.uuid4().hex[:12]}"

class AiJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(String(36), primary_key=True, default=generate_ai_job_id)
    user_id = Column(String(36), index=True, nullable=False)
    question_id = Column(String(36), index=True, nullable=True)
    action_type = Column(String(32), index=True, nullable=False)  # 'explain', 'mnemonic', 'case_breakdown', 'study_advice'
    status = Column(String(16), default="pending", nullable=False)  # 'pending', 'completed', 'failed'
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
