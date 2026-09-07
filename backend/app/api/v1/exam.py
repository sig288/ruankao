from datetime import datetime, timezone
import random
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.record import ExamRecord, PracticeRecord
from app.models.wrong_question import WrongQuestion
from app.schemas.exam import ExamGenerateIn, ExamSubmitIn, ExamResultOut, ExamQuestionSummary
from app.schemas.question import QuestionPracticeItem
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/generate", response_model=List[QuestionPracticeItem])
def generate_mock_exam(
    exam_in: ExamGenerateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Question).filter(Question.subject == exam_in.subject)
    if exam_in.chapter:
        query = query.filter(Question.chapter == exam_in.chapter)
    
    all_questions = query.all()
    if not all_questions:
        raise HTTPException(status_code=404, detail="题库中暂无匹配题目")

    count = min(exam_in.question_count, len(all_questions))
    selected = random.sample(all_questions, count)

    # For mock exam, strip correct_answer and analysis so student cannot peek in payload
    result = []
    for q in selected:
        item = QuestionPracticeItem(
            id=q.id,
            subject=q.subject,
            chapter=q.chapter,
            knowledge=q.knowledge,
            stem=q.stem,
            options=q.options,
            difficulty=q.difficulty,
            source=q.source,
            correct_answer=None,  # hidden during exam
            analysis=None,
            rubrics=q.rubrics if q.subject == "case" else None
        )
        result.append(item)

    return result

@router.post("/submit", response_model=ExamResultOut)
def submit_mock_exam(
    submit_in: ExamSubmitIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q_ids = list(submit_in.answers.keys())
    if not q_ids:
        raise HTTPException(status_code=400, detail="未提交任何题目答案")

    questions = db.query(Question).filter(Question.id.in_(q_ids)).all()
    q_map = {q.id: q for q in questions}

    total_questions = len(q_ids)
    correct_count = 0
    earned_score = 0.0
    total_score = float(total_questions)
    details: List[ExamQuestionSummary] = []
    now = datetime.now(timezone.utc)

    for qid, u_ans in submit_in.answers.items():
        q = q_map.get(qid)
        if not q:
            continue

        u_ans_clean = (u_ans or "").strip()
        correct_ans = (q.correct_answer or "").strip()
        is_corr = (u_ans_clean.upper() == correct_ans.upper())

        item_score = 1.0 if is_corr else 0.0
        if is_corr:
            correct_count += 1
            earned_score += 1.0
        else:
            # Auto-save to WrongQuestion
            existing_wq = db.query(WrongQuestion).filter(
                WrongQuestion.user_id == current_user.id,
                WrongQuestion.question_id == q.id
            ).first()

            if existing_wq:
                existing_wq.wrong_count += 1
                existing_wq.user_answer = u_ans_clean
                existing_wq.is_mastered = False
                existing_wq.answered_at = now
                existing_wq.updated_at = now
            else:
                new_wq = WrongQuestion(
                    user_id=current_user.id,
                    question_id=q.id,
                    subject=q.subject,
                    knowledge=q.knowledge,
                    stem=q.stem,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    user_answer=u_ans_clean,
                    analysis=q.analysis,
                    source=q.source or "ai-generated",
                    answered_at=now,
                    wrong_count=1,
                    is_mastered=False
                )
                db.add(new_wq)

        # Save practice record
        prec = PracticeRecord(
            user_id=current_user.id,
            question_id=q.id,
            subject=q.subject,
            chapter=q.chapter,
            knowledge=q.knowledge,
            user_answer=u_ans_clean,
            is_correct=is_corr,
            score=item_score,
            answered_at=now
        )
        db.add(prec)

        details.append(ExamQuestionSummary(
            question_id=q.id,
            stem=q.stem,
            options=q.options,
            user_answer=u_ans_clean,
            correct_answer=correct_ans,
            is_correct=is_corr,
            score=item_score,
            analysis=q.analysis
        ))

    exam_record = ExamRecord(
        user_id=current_user.id,
        subject=submit_in.subject,
        total_questions=total_questions,
        correct_count=correct_count,
        score=earned_score,
        total_score=total_score,
        time_spent=submit_in.time_spent,
        details=[d.model_dump() for d in details],
        created_at=now
    )
    db.add(exam_record)
    db.commit()
    db.refresh(exam_record)

    return ExamResultOut(
        id=exam_record.id,
        subject=exam_record.subject,
        total_questions=exam_record.total_questions,
        correct_count=exam_record.correct_count,
        score=exam_record.score,
        total_score=exam_record.total_score,
        time_spent=exam_record.time_spent,
        created_at=exam_record.created_at,
        details=details
    )

@router.get("/history")
def get_exam_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(ExamRecord).filter(
        ExamRecord.user_id == current_user.id
    ).order_by(ExamRecord.created_at.desc()).limit(20).all()
    return records
