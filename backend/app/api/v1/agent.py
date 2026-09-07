from datetime import datetime, timezone
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.wrong_question import WrongQuestion
from app.models.agent_key import AgentApiKey
from app.schemas.agent import (
    AgentWrongQuestionItem,
    AgentWrongQuestionBatchIn,
    AgentWrongQuestionBatchOut,
    AgentExplainCallbackIn
)
from app.api.deps import get_current_agent

router = APIRouter()

def format_wq_for_agent(wq: WrongQuestion) -> dict:
    return {
        "id": wq.id,
        "user_id": wq.user_id,
        "question_id": wq.question_id,
        "subject": wq.subject,
        "knowledge": wq.knowledge,
        "stem": wq.stem,
        "options": wq.options,
        "correct_answer": wq.correct_answer,
        "user_answer": wq.user_answer,
        "analysis": wq.analysis,
        "answered_at": wq.answered_at.isoformat() if wq.answered_at else datetime.now(timezone.utc).isoformat(),
        "source": wq.source or "ai-generated",
        "wrong_count": wq.wrong_count,
        "is_mastered": wq.is_mastered,
        "agent_explanation": wq.agent_explanation
    }

@router.post("/wrong-questions", response_model=AgentWrongQuestionBatchOut)
def batch_report_wrong_questions(
    payload: Union[AgentWrongQuestionBatchIn, List[AgentWrongQuestionItem]] = Body(...),
    agent: AgentApiKey = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    供外部 Agent 批量上报错题（需 Agent API Key Bearer 认证）
    """
    items = payload.items if isinstance(payload, AgentWrongQuestionBatchIn) else payload
    if not items:
        return AgentWrongQuestionBatchOut(success=True, imported_count=0, message="无错题数据传入")

    count = 0
    now = datetime.now(timezone.utc)

    for item in items:
        # Check if exists by id or (user_id, question_id)
        wq = None
        if item.id:
            wq = db.query(WrongQuestion).filter(WrongQuestion.id == item.id).first()
        if not wq:
            wq = db.query(WrongQuestion).filter(
                WrongQuestion.user_id == item.user_id,
                WrongQuestion.question_id == item.question_id
            ).first()

        answered_dt = now
        if item.answered_at:
            if isinstance(item.answered_at, datetime):
                answered_dt = item.answered_at
            elif isinstance(item.answered_at, str):
                try:
                    answered_dt = datetime.fromisoformat(item.answered_at.replace("Z", "+00:00"))
                except Exception:
                    answered_dt = now

        if wq:
            wq.wrong_count += 1
            wq.user_answer = item.user_answer or wq.user_answer
            wq.answered_at = answered_dt
            wq.is_mastered = False
            wq.updated_at = now
            if item.agent_explanation:
                wq.agent_explanation = item.agent_explanation
        else:
            new_wq = WrongQuestion(
                user_id=item.user_id,
                question_id=item.question_id,
                subject=item.subject,
                knowledge=item.knowledge,
                stem=item.stem,
                options=item.options,
                correct_answer=item.correct_answer,
                user_answer=item.user_answer,
                analysis=item.analysis,
                source=item.source or "ai-generated",
                answered_at=answered_dt,
                wrong_count=item.wrong_count or 1,
                is_mastered=item.is_mastered or False,
                agent_explanation=item.agent_explanation
            )
            if item.id:
                new_wq.id = item.id
            db.add(new_wq)
        count += 1

    db.commit()
    return AgentWrongQuestionBatchOut(
        success=True,
        imported_count=count,
        message=f"成功处理 {count} 条错题"
    )

@router.get("/wrong-questions")
def get_wrong_questions_for_agent(
    user_id: Optional[str] = Query(None, description="指定用户ID"),
    since: Optional[str] = Query(None, description="起始时间 ISO8601，例如 2026-09-01T00:00:00Z"),
    limit: int = Query(50, ge=1, le=200, description="拉取数量上限"),
    agent: AgentApiKey = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    供外部 Agent 拉取错题列表（需 Agent API Key Bearer 认证）
    """
    query = db.query(WrongQuestion)
    if user_id:
        query = query.filter(WrongQuestion.user_id == user_id)
    if since:
        try:
            dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            query = query.filter(WrongQuestion.answered_at >= dt)
        except Exception:
            pass

    records = query.order_by(WrongQuestion.answered_at.desc()).limit(limit).all()
    return [format_wq_for_agent(wq) for wq in records]

@router.get("/wrong-questions/{id}")
def get_single_wrong_question_for_agent(
    id: str,
    agent: AgentApiKey = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    供外部 Agent 查询单题详情（含题干、选项、用户答案、正确答案、解析、知识点、时间）
    """
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    return format_wq_for_agent(wq)

@router.post("/explain-callback")
def agent_explain_callback(
    callback_in: AgentExplainCallbackIn,
    agent: AgentApiKey = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    供外部 Agent 写回讲解摘要与复习指导
    """
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == callback_in.wrong_question_id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")

    full_explanation = callback_in.explanation
    if callback_in.study_tips:
        full_explanation += f"\n\n【复习口诀/重点提醒】\n{callback_in.study_tips}"

    wq.agent_explanation = full_explanation
    wq.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "message": "已成功更新错题讲解与要点",
        "wrong_question_id": wq.id
    }
