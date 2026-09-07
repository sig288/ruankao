import json
import os
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.agent_key import AgentApiKey
from app.models.question import Question

logger = logging.getLogger(__name__)

def init_seed_data(db: Session):
    # 1. Initialize Admin user if password provided in environment
    if settings.INITIAL_ADMIN_PASSWORD:
        admin_user = db.query(User).filter(User.username == settings.INITIAL_ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=settings.INITIAL_ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Initialized admin user: {settings.INITIAL_ADMIN_USERNAME}")

    # 2. Initialize default Agent API Key if provided in environment
    if settings.DEFAULT_AGENT_KEY:
        default_key = db.query(AgentApiKey).filter(AgentApiKey.key == settings.DEFAULT_AGENT_KEY).first()
        if not default_key:
            default_key = AgentApiKey(
                key=settings.DEFAULT_AGENT_KEY,
                name="Default Server Agent Key",
                is_active=True
            )
            db.add(default_key)
            db.commit()
        logger.info(f"Initialized default agent key: {settings.DEFAULT_AGENT_KEY}")

    # 3. Load seed questions if database is empty
    question_count = db.query(Question).count()
    if question_count == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_questions.json")
        if os.path.exists(seed_path):
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    questions_data = json.load(f)

                for item in questions_data:
                    q = Question(
                        subject=item.get("subject", "basic"),
                        chapter=item.get("chapter", "综合知识"),
                        knowledge=item.get("knowledge", "核心考点"),
                        stem=item.get("stem"),
                        options=item.get("options"),
                        correct_answer=item.get("correct_answer"),
                        analysis=item.get("analysis"),
                        rubrics=item.get("rubrics"),
                        source=item.get("source", "ai-generated"),
                        difficulty=item.get("difficulty", "medium")
                    )
                    db.add(q)
                db.commit()
                logger.info(f"Loaded {len(questions_data)} seed questions into database.")
            except Exception as e:
                logger.error(f"Failed to load seed questions: {e}")
                db.rollback()
