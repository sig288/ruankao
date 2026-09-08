import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from app.database import Base

def generate_mat_id():
    return f"mat_{uuid.uuid4().hex[:12]}"

class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=generate_mat_id)
    user_id = Column(String(36), index=True, nullable=False)
    title = Column(String(128), nullable=False)
    file_type = Column(String(32), nullable=False)  # 'pdf', 'docx', 'image', 'csv', 'json', 'txt', 'xls'
    category = Column(String(32), default="教材", nullable=False)  # '教材', '口诀', '案例', '真题', '笔记', '导图与三色笔记', '速记与背诵口诀', '机考与画图指南', '历年真题与解析', '官方教材与考纲'
    chapter = Column(String(64), index=True, nullable=True)
    domain = Column(String(64), index=True, nullable=True)
    file_path = Column(String(256), nullable=False)
    file_size = Column(Integer, default=0)
    converted_question_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Extended attributes for official / public curated materials
    is_public = Column(Boolean, default=False, index=True)
    is_recommended = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    year = Column(String(32), nullable=True)
    download_url = Column(String(512), nullable=True)

