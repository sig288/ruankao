from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionOut, QuestionPracticeItem

router = APIRouter()

@router.get("/chapters")
def get_chapters(
    subject: Optional[str] = Query(None, description="basic 或 case"),
    db: Session = Depends(get_db)
):
    query = db.query(
        Question.chapter,
        Question.subject,
        func.count(Question.id).label("count")
    )
    if subject:
        query = query.filter(Question.subject == subject)
    results = query.group_by(Question.chapter, Question.subject).all()

    chapters = {}
    for chapter, subj, count in results:
        if chapter not in chapters:
            chapters[chapter] = {"chapter": chapter, "basic_count": 0, "case_count": 0, "total": 0}
        if subj == "basic":
            chapters[chapter]["basic_count"] += count
        else:
            chapters[chapter]["case_count"] += count
        chapters[chapter]["total"] += count

    return list(chapters.values())

@router.get("/knowledge-points")
def get_knowledge_points(
    chapter: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        Question.chapter,
        Question.knowledge,
        func.count(Question.id).label("count")
    )
    if chapter:
        query = query.filter(Question.chapter == chapter)
    if subject:
        query = query.filter(Question.subject == subject)
    results = query.group_by(Question.chapter, Question.knowledge).all()
    return [{"chapter": ch, "knowledge": kp, "count": cnt} for ch, kp, cnt in results]

@router.get("/list", response_model=List[QuestionPracticeItem])
def list_questions(
    subject: Optional[str] = Query(None),
    chapter: Optional[str] = Query(None),
    knowledge: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    if subject:
        query = query.filter(Question.subject == subject)
    if chapter:
        query = query.filter(Question.chapter == chapter)
    if knowledge:
        query = query.filter(Question.knowledge == knowledge)
    questions = query.order_by(Question.created_at.desc()).offset(offset).limit(limit).all()
    return questions

@router.get("/{id}", response_model=QuestionOut)
def get_question(id: str, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question
