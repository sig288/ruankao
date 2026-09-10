import secrets
import csv
import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.wrong_question import WrongQuestion
from app.models.agent_key import AgentApiKey
from app.models.learn import KnowledgePoint, GlossaryTerm
from app.schemas.question import QuestionCreate, QuestionOut
from app.schemas.agent import AgentApiKeyCreate, AgentApiKeyOut
from app.schemas.learn import PointImportItem, GlossaryImportItem
from app.api.deps import get_current_admin

router = APIRouter()

@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_questions = db.query(Question).count()
    basic_questions = db.query(Question).filter(Question.subject == "basic").count()
    case_questions = db.query(Question).filter(Question.subject == "case").count()
    total_wrong_records = db.query(WrongQuestion).count()
    total_agent_keys = db.query(AgentApiKey).count()

    return {
        "total_users": total_users,
        "total_questions": total_questions,
        "basic_questions": basic_questions,
        "case_questions": case_questions,
        "total_wrong_records": total_wrong_records,
        "total_agent_keys": total_agent_keys
    }

@router.post("/import-questions")
def import_questions(
    questions: List[QuestionCreate],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    count = 0
    for q_in in questions:
        q = Question(
            subject=q_in.subject,
            chapter=q_in.chapter,
            knowledge=q_in.knowledge,
            stem=q_in.stem,
            options=q_in.options,
            correct_answer=q_in.correct_answer,
            analysis=q_in.analysis,
            rubrics=[r.model_dump() for r in q_in.rubrics] if q_in.rubrics else None,
            source=q_in.source or "ai-generated",
            difficulty=q_in.difficulty
        )
        db.add(q)
        count += 1

    db.commit()
    return {"success": True, "imported_count": count, "message": f"成功导入 {count} 道题目"}

@router.post("/import-csv")
async def import_csv_questions(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    content = await file.read()
    text = content.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    count = 0

    for row in reader:
        # Expected CSV columns: subject, chapter, knowledge, stem, option_a, option_b, option_c, option_d, correct_answer, analysis
        subj = row.get("subject", "basic").strip()
        ch = row.get("chapter", "基础知识").strip()
        kp = row.get("knowledge", "综合知识").strip()
        stem = row.get("stem", "").strip()
        correct_ans = row.get("correct_answer", "").strip()
        analysis = row.get("analysis", "").strip()

        if not stem or not correct_ans:
            continue

        options = None
        if subj == "basic":
            options = [
                f"A. {row.get('option_a', '').strip()}",
                f"B. {row.get('option_b', '').strip()}",
                f"C. {row.get('option_c', '').strip()}",
                f"D. {row.get('option_d', '').strip()}"
            ]

        q = Question(
            subject=subj,
            chapter=ch,
            knowledge=kp,
            stem=stem,
            options=options,
            correct_answer=correct_ans,
            analysis=analysis,
            source="csv-imported"
        )
        db.add(q)
        count += 1

    db.commit()
    return {"success": True, "imported_count": count, "message": f"成功导入 {count} 道题目"}

@router.get("/agent-keys", response_model=List[AgentApiKeyOut])
def list_agent_keys(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    keys = db.query(AgentApiKey).order_by(AgentApiKey.created_at.desc()).all()
    return keys

@router.post("/agent-keys", response_model=AgentApiKeyOut)
def create_agent_key(
    key_in: AgentApiKeyCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_token = f"rk_agent_{secrets.token_urlsafe(24)}"
    ak = AgentApiKey(
        key=new_token,
        name=key_in.name,
        is_active=True
    )
    db.add(ak)
    db.commit()
    db.refresh(ak)
    return ak

@router.post("/agent-keys/{id}/toggle")
def toggle_agent_key(
    id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ak = db.query(AgentApiKey).filter(AgentApiKey.id == id).first()
    if not ak:
        raise HTTPException(status_code=404, detail="Key 不存在")
    ak.is_active = not ak.is_active
    db.commit()
    return {"id": ak.id, "is_active": ak.is_active, "message": "Key 状态已切换"}

@router.delete("/agent-keys/{id}")
def delete_agent_key(
    id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ak = db.query(AgentApiKey).filter(AgentApiKey.id == id).first()
    if not ak:
        raise HTTPException(status_code=404, detail="Key 不存在")
    db.delete(ak)
    db.commit()
    return {"message": "Agent Key 已删除"}

@router.post("/learn/points/import")
def import_knowledge_points(
    points: List[PointImportItem],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员批量导入/更新知识点（支持 upsert 幂等操作）
    """
    inserted = 0
    updated = 0
    errors = []

    for item in points:
        try:
            kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == item.id).first()
            if kp:
                kp.chapter_id = item.chapter_id
                kp.title = item.title
                kp.frequency = item.frequency
                kp.est_minutes = item.est_minutes
                kp.summary_md = item.summary_md
                kp.formula_md = item.formula_md
                kp.domain_tags = item.domain_tags
                kp.glossary_ids = item.glossary_ids
                kp.question_ids = item.question_ids
                kp.sort_order = item.sort_order
                updated += 1
            else:
                kp = KnowledgePoint(
                    id=item.id,
                    chapter_id=item.chapter_id,
                    title=item.title,
                    frequency=item.frequency,
                    est_minutes=item.est_minutes,
                    summary_md=item.summary_md,
                    formula_md=item.formula_md,
                    domain_tags=item.domain_tags,
                    glossary_ids=item.glossary_ids,
                    question_ids=item.question_ids,
                    sort_order=item.sort_order
                )
                db.add(kp)
                inserted += 1
        except Exception as e:
            errors.append({"id": item.id, "error": str(e)})

    db.commit()
    return {
        "message": f"成功处理 {inserted + updated} 个知识点",
        "inserted": inserted,
        "updated": updated,
        "errors": errors
    }

@router.post("/learn/glossary/import")
def import_glossary_terms(
    terms: List[GlossaryImportItem],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员批量导入/更新英语术语词表（支持 upsert 幂等操作）
    """
    inserted = 0
    updated = 0
    errors = []

    for item in terms:
        try:
            term_id = item.id or f"term_{item.term_en.lower().replace(' ', '_').replace('-', '_')[:30]}"
            t = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
            if t:
                t.term_en = item.term_en
                t.term_zh = item.term_zh
                t.tags = item.tags
                t.tip = item.tip
                t.frequency = item.frequency
                t.confuse_with = item.confuse_with
                t.knowledge_point_ids = item.knowledge_point_ids
                updated += 1
            else:
                t = GlossaryTerm(
                    id=term_id,
                    term_en=item.term_en,
                    term_zh=item.term_zh,
                    tags=item.tags,
                    tip=item.tip,
                    frequency=item.frequency,
                    confuse_with=item.confuse_with,
                    knowledge_point_ids=item.knowledge_point_ids
                )
                db.add(t)
                inserted += 1
        except Exception as e:
            errors.append({"term_en": item.term_en, "error": str(e)})

    db.commit()
    return {
        "message": f"成功处理 {inserted + updated} 个词条",
        "inserted": inserted,
        "updated": updated,
        "errors": errors
    }

# ==================== AI Settings & User Management ====================

from datetime import datetime, timezone
from app.services.ai_config import load_ai_settings, save_ai_settings, test_deepseek_connectivity
from app.models.ai_job import AiJob
from app.core.security import get_password_hash

@router.get("/ai/settings")
def get_ai_settings(current_admin: User = Depends(get_current_admin)):
    return load_ai_settings(masked=True)

@router.put("/ai/settings")
def update_ai_settings(
    settings_in: dict = Body(...),
    current_admin: User = Depends(get_current_admin)
):
    return save_ai_settings(settings_in)

@router.post("/ai/test")
def test_ai_connection(current_admin: User = Depends(get_current_admin)):
    return test_deepseek_connectivity()

@router.get("/ai/usage")
def get_ai_usage_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    total_calls = db.query(AiJob).count()
    today_calls = db.query(AiJob).filter(AiJob.created_at >= today_start).count()
    return {
        "total_calls": total_calls,
        "today_calls": today_calls
    }

@router.get("/users")
def list_admin_users(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    ai_enabled: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    q = db.query(User)
    if search:
        q = q.filter(User.username.contains(search))
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    if ai_enabled is not None:
        q = q.filter(User.ai_enabled == ai_enabled)

    users = q.offset(skip).limit(limit).all()
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    result = []
    for u in users:
        today_usage = db.query(AiJob).filter(AiJob.user_id == u.id, AiJob.created_at >= today_start).count()
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "is_active": getattr(u, "is_active", True) is not False,
            "ai_enabled": getattr(u, "ai_enabled", True) is not False,
            "ai_daily_quota": u.ai_quota,
            "ai_quota": u.ai_quota,
            "today_ai_usage": today_usage,
            "created_at": u.created_at
        })
    return result

@router.post("/users")
def create_admin_user(
    data: dict = Body(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    exist = db.query(User).filter(User.username == username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")

    u = User(
        username=username,
        hashed_password=get_password_hash(password),
        role=data.get("role", "user"),
        ai_quota=data.get("ai_daily_quota") or data.get("ai_quota"),
        is_active=bool(data.get("is_active", True)),
        ai_enabled=bool(data.get("ai_enabled", True))
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "username": u.username, "message": "创建用户成功"}

@router.patch("/users/{id}")
def update_admin_user(
    id: str,
    data: dict = Body(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    if "is_active" in data:
        u.is_active = bool(data["is_active"])
    if "role" in data:
        u.role = str(data["role"])
    db.commit()
    return {"message": "更新成功"}

@router.post("/users/{id}/reset-password")
def reset_user_password(
    id: str,
    data: dict = Body(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    new_pwd = data.get("new_password", "").strip()
    if not new_pwd or len(new_pwd) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于 6 位")

    u.hashed_password = get_password_hash(new_pwd)
    db.commit()
    return {"message": "密码重置成功"}

@router.patch("/users/{id}/ai")
def update_user_ai_config(
    id: str,
    data: dict = Body(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    if "ai_enabled" in data:
        u.ai_enabled = bool(data["ai_enabled"])
    if "ai_daily_quota" in data:
        u.ai_quota = data["ai_daily_quota"]
    elif "ai_quota" in data:
        u.ai_quota = data["ai_quota"]

    db.commit()
    return {"message": "AI权限与额度更新成功"}

@router.get("/users/{id}/ai-usage")
def get_user_ai_usage_history(
    id: str,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    jobs = db.query(AiJob).filter(AiJob.user_id == id).order_by(AiJob.created_at.desc()).limit(limit).all()
    return jobs


