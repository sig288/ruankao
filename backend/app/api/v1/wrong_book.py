from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.wrong_question import WrongQuestion
from app.models.record import PracticeRecord, Favorite
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/wrong-questions")
def get_user_wrong_questions(
    knowledge: Optional[str] = Query(None),
    is_mastered: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WrongQuestion).filter(WrongQuestion.user_id == current_user.id)
    if knowledge:
        query = query.filter(WrongQuestion.knowledge == knowledge)
    if is_mastered is not None:
        query = query.filter(WrongQuestion.is_mastered == is_mastered)
    
    total = query.count()
    items = query.order_by(WrongQuestion.answered_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": items}

@router.post("/wrong-questions/{id}/master")
def toggle_master_status(
    id: str,
    mastered: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == id,
        WrongQuestion.user_id == current_user.id
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    wq.is_mastered = mastered
    db.commit()
    return {"message": "已更新掌握状态", "is_mastered": wq.is_mastered}

@router.delete("/wrong-questions/{id}")
def delete_wrong_question(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == id,
        WrongQuestion.user_id == current_user.id
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    db.delete(wq)
    db.commit()
    return {"message": "错题已移除"}

@router.get("/favorites")
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favs = db.query(Favorite, Question).join(
        Question, Favorite.question_id == Question.id
    ).filter(Favorite.user_id == current_user.id).order_by(Favorite.created_at.desc()).all()

    items = []
    for fav, q in favs:
        items.append({
            "favorite_id": fav.id,
            "question_id": q.id,
            "subject": q.subject,
            "chapter": q.chapter,
            "knowledge": q.knowledge,
            "stem": q.stem,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "analysis": q.analysis,
            "created_at": fav.created_at
        })
    return items

@router.post("/favorites/{question_id}")
def toggle_favorite(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.question_id == question_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False, "message": "已取消收藏"}
    else:
        fav = Favorite(user_id=current_user.id, question_id=question_id)
        db.add(fav)
        db.commit()
        return {"favorited": True, "message": "已收藏"}

@router.get("/statistics")
def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total answered records
    total_answered = db.query(PracticeRecord).filter(PracticeRecord.user_id == current_user.id).count()
    correct_answered = db.query(PracticeRecord).filter(
        PracticeRecord.user_id == current_user.id,
        PracticeRecord.is_correct == True
    ).count()

    overall_accuracy = round(correct_answered / total_answered * 100, 1) if total_answered > 0 else 0.0

    # Wrong questions stats
    total_wrong = db.query(WrongQuestion).filter(WrongQuestion.user_id == current_user.id).count()
    unmastered_wrong = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id,
        WrongQuestion.is_mastered == False
    ).count()

    # Chapter breakdown
    chapter_stats = db.query(
        PracticeRecord.chapter,
        func.count(PracticeRecord.id).label("total"),
        func.sum(func.cast(PracticeRecord.is_correct, func.INTEGER if db.bind.dialect.name == 'sqlite' else func.BOOLEAN)).label("correct")
    ).filter(
        PracticeRecord.user_id == current_user.id,
        PracticeRecord.chapter != None
    ).group_by(PracticeRecord.chapter).all()

    breakdown = []
    for ch, tot, cor in chapter_stats:
        c_val = int(cor or 0)
        t_val = int(tot or 0)
        rate = round(c_val / t_val * 100, 1) if t_val > 0 else 0.0
        breakdown.append({
            "chapter": ch,
            "total": t_val,
            "correct": c_val,
            "accuracy": rate
        })

    return {
        "total_answered": total_answered,
        "correct_answered": correct_answered,
        "overall_accuracy": overall_accuracy,
        "total_wrong": total_wrong,
        "unmastered_wrong": unmastered_wrong,
        "chapter_breakdown": breakdown
    }
