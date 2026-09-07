import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "软考中项刷题助手"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ruankao-default-secret-key-please-change-in-env")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/ruankao.db")
    INITIAL_ADMIN_USERNAME: str = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    INITIAL_ADMIN_PASSWORD: str = os.getenv("INITIAL_ADMIN_PASSWORD", "")
    DEFAULT_AGENT_KEY: str = os.getenv("DEFAULT_AGENT_KEY", "")

    # DeepSeek AI Configuration (v3 MVP)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    AI_DAILY_QUOTA: int = int(os.getenv("AI_DAILY_QUOTA", "30"))

    # User Study Materials
    MATERIALS_DIR: str = os.getenv("MATERIALS_DIR", "./data/materials")

    class Config:
        case_sensitive = True

settings = Settings()
