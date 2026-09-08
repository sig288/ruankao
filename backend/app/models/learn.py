import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean, ForeignKey
from app.database import Base

def generate_uid(prefix="id_"):
    return f"{prefix}{uuid.uuid4().hex[:12]}"

class KnowledgeChapter(Base):
    __tablename__ = "knowledge_chapters"

    id = Column(String(16), primary_key=True)  # e.g., "CH01", "CH07"
    code = Column(String(16), nullable=False, unique=True, index=True)
    title = Column(String(64), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(String(64), primary_key=True)  # e.g., "kp_evm_cpi"
    chapter_id = Column(String(16), ForeignKey("knowledge_chapters.id"), nullable=False, index=True)
    title = Column(String(128), nullable=False, index=True)
    frequency = Column(String(16), default="mid", nullable=False)  # 'high', 'mid', 'low'
    est_minutes = Column(Integer, default=10, nullable=False)
    summary_md = Column(Text, nullable=False)
    formula_md = Column(Text, nullable=True)
    domain_tags = Column(JSON, nullable=True)  # List[str] e.g. ["项目成本管理", "挣值分析"]
    glossary_ids = Column(JSON, nullable=True)  # List[str] e.g. ["term_evm", "term_cpi"]
    question_ids = Column(JSON, nullable=True)  # List[str] e.g. ["q_xxx", "q_yyy"]
    sort_order = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserPointStatus(Base):
    __tablename__ = "user_point_statuses"

    id = Column(String(36), primary_key=True, default=lambda: generate_uid("ups_"))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    point_id = Column(String(64), ForeignKey("knowledge_points.id"), nullable=False, index=True)
    status = Column(String(16), default="unlearned", nullable=False)  # 'unlearned', 'learning', 'mastered'
    last_studied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"

    id = Column(String(64), primary_key=True)  # e.g., "term_evm", "term_wbs"
    term_en = Column(String(128), nullable=False, index=True)
    term_zh = Column(String(128), nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # List[str] e.g. ["成本管理", "绩效分析"]
    tip = Column(Text, nullable=True)  # 考点提示/速记例句
    frequency = Column(String(16), default="mid", nullable=False)  # 'high', 'mid', 'low'
    confuse_with = Column(JSON, nullable=True)  # List[str] 易混词
    knowledge_point_ids = Column(JSON, nullable=True)  # List[str] 反向关联知识点
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserGlossaryStatus(Base):
    __tablename__ = "user_glossary_statuses"

    id = Column(String(36), primary_key=True, default=lambda: generate_uid("ugs_"))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    term_id = Column(String(64), ForeignKey("glossary_terms.id"), nullable=False, index=True)
    known = Column(String(16), default="unknown", nullable=False)  # 'unknown', 'know', 'dont_know'
    favorited = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
