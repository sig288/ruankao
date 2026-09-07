import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer
from app.database import Base

def generate_mat_id():
    return f"mat_{uuid.uuid4().hex[:12]}"

class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=generate_mat_id)
    user_id = Column(String(36), index=True, nullable=False)
    title = Column(String(128), nullable=False)
    file_type = Column(String(32), nullable=False)  # 'pdf', 'docx', 'image', 'csv', 'json', 'txt'
    category = Column(String(32), default="教材", nullable=False)  # '教材', '口诀', '案例', '真题', '笔记'
    chapter = Column(String(64), index=True, nullable=True)
    domain = Column(String(64), index=True, nullable=True)
    file_path = Column(String(256), nullable=False)
    file_size = Column(Integer, default=0)
    converted_question_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
