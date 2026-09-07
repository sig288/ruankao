import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean
from app.database import Base

def generate_key_id():
    return f"ak_{uuid.uuid4().hex[:12]}"

class AgentApiKey(Base):
    __tablename__ = "agent_api_keys"

    id = Column(String(36), primary_key=True, default=generate_key_id)
    key = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(64), nullable=False, default="Default Agent")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)
