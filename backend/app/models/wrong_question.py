import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
from app.database import Base

def generate_wqid():
    return f"wq_{uuid.uuid4().hex[:12]}"

class WrongQuestion(Base):
    __tablename__ = "wrong_questions"

    id = Column(String(36), primary_key=True, default=generate_wqid)
    user_id = Column(String(36), index=True, nullable=False)
    question_id = Column(String(36), index=True, nullable=False)
    subject = Column(String(16), default="basic", nullable=False)
    knowledge = Column(String(64), index=True, nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)
    source = Column(String(32), default="ai-generated", nullable=False)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    wrong_count = Column(Integer, default=1, nullable=False)
    is_mastered = Column(Boolean, default=False, nullable=False)
    agent_explanation = Column(Text, nullable=True)  # Callback explanation summary from Agent
    ai_mnemonic = Column(Text, nullable=True)  # DeepSeek memory formula / mnemonic
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
