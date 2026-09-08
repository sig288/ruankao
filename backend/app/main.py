import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine, SessionLocal
from app.services.seed_loader import init_seed_data

from app.api.v1 import auth, questions, practice, exam, wrong_book, agent, admin, mastery, ai, materials, study_plan, learn, glossary, app_version

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ruankao")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_seed_data(db)
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="软考中项（系统集成项目管理工程师第3版）移动端刷题助手与外部Agent错题交互API",
    version="3.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# API Routers
api_v1 = settings.API_V1_STR
app.include_router(auth.router, prefix=f"{api_v1}/auth", tags=["用户认证"])
app.include_router(questions.router, prefix=f"{api_v1}/questions", tags=["题库查询"])
app.include_router(practice.router, prefix=f"{api_v1}/practice", tags=["刷题与判分"])
app.include_router(exam.router, prefix=f"{api_v1}/exam", tags=["模拟考试"])
app.include_router(wrong_book.router, prefix=f"{api_v1}/wrong-book", tags=["错题本"])
app.include_router(mastery.router, prefix=f"{api_v1}/mastery", tags=["掌握度与薄弱推题"])
app.include_router(ai.router, prefix=f"{api_v1}/ai", tags=["DeepSeek伴学"])
app.include_router(materials.router, prefix=f"{api_v1}/materials", tags=["自有资料库"])
app.include_router(study_plan.router, prefix=f"{api_v1}/plan", tags=["倒计时学习计划"])
app.include_router(learn.router, prefix=f"{api_v1}/learn", tags=["知识点学习"])
app.include_router(glossary.router, prefix=f"{api_v1}/learn", tags=["英语术语词表"])
app.include_router(app_version.router, prefix=f"{api_v1}/app", tags=["客户端版本与更新"])
app.include_router(agent.router, prefix=f"{api_v1}/agent", tags=["外部Agent开放接口"])
app.include_router(admin.router, prefix=f"{api_v1}/admin", tags=["管理后台"])

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": "1.0.0"}
