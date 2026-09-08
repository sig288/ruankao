import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from app.database import Base

def generate_qid():
    return f"q_{uuid.uuid4().hex[:12]}"

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_qid)
    subject = Column(String(16), default="basic", index=True, nullable=False)  # 'basic' or 'case'
    chapter = Column(String(64), index=True, nullable=False)  # e.g., '进度管理', '成本管理'
    knowledge = Column(String(64), index=True, nullable=False)  # e.g., '关键路径法', '挣值分析EVM'
    stem = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # List[str] e.g. ["A...", "B...", "C...", "D..."] for basic
    correct_answer = Column(Text, nullable=False)  # e.g. "B" or case reference answer
    analysis = Column(Text, nullable=True)  # Explanation
    rubrics = Column(JSON, nullable=True)  # Scoring rubrics for case questions: [{"point": "关键路径延长", "score": 2, "keywords": ["关键路径", "工期延长"]}]
    knowledge_point_ids = Column(JSON, nullable=True)  # List[str] e.g. ["kp_evm_cpi"] for direct jump
    glossary_ids = Column(JSON, nullable=True)  # List[str] e.g. ["term_evm"] for English term jump
    is_english_term = Column(Boolean, default=False, nullable=False)  # Whether it's an English term question
    source = Column(String(32), default="ai-generated", nullable=False)
    difficulty = Column(String(16), default="medium")  # 'easy', 'medium', 'hard'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

