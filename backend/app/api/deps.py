from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.database import get_db
from app.models.user import User
from app.models.agent_key import AgentApiKey

security_bearer = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="凭证无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="凭证过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> AgentApiKey:
    """
    Authenticate external agent via Authorization: Bearer <API_KEY>
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Agent API Key，请在 Header 中提供 Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    api_key = credentials.credentials

    # Check in DB
    agent_key_rec = db.query(AgentApiKey).filter(
        AgentApiKey.key == api_key,
        AgentApiKey.is_active == True
    ).first()

    # If it's the default configured agent key, create it if missing
    if not agent_key_rec and api_key == settings.DEFAULT_AGENT_KEY:
        agent_key_rec = AgentApiKey(
            key=settings.DEFAULT_AGENT_KEY,
            name="Default Server Agent Key",
            is_active=True
        )
        db.add(agent_key_rec)
        db.commit()
        db.refresh(agent_key_rec)

    if not agent_key_rec:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已禁用的 Agent API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last used timestamp
    agent_key_rec.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return agent_key_rec
