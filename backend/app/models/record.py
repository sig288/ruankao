import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float, Boolean
from app.database import Base

def generate_rid():
    return f"rec_{uuid.uuid4().hex[:12]}"

class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id = Column(String(36), primary_key=True, default=generate_rid)
    user_id = Column(String(36), index=True, nullable=False)
    question_id = Column(String(36), index=True, nullable=False)
    subject = Column(String(16), default="basic", nullable=False)
    chapter = Column(String(64), index=True, nullable=True)
    knowledge = Column(String(64), index=True, nullable=True)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    score = Column(Float, default=0.0)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=generate_rid)
    user_id = Column(String(36), index=True, nullable=False)
    question_id = Column(String(36), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ExamRecord(Base):
    __tablename__ = "exam_records"

    id = Column(String(36), primary_key=True, default=generate_rid)
    user_id = Column(String(36), index=True, nullable=False)
    subject = Column(String(16), default="basic", nullable=False)  # 'basic' or 'case'
    total_questions = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    total_score = Column(Float, default=75.0, nullable=False)
    time_spent = Column(Integer, default=0)  # seconds
    details = Column(JSON, nullable=True)  # Snapshot of questions & user answers
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
