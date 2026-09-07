import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.database import Base

def generate_uuid():
    return f"u_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(16), default="user", nullable=False)  # 'user' or 'admin'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
