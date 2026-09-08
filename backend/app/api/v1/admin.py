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

