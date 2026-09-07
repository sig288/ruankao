from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.record import PracticeRecord
from app.models.wrong_question import WrongQuestion
from app.schemas.practice import SubmitAnswerIn, SubmitAnswerOut
from app.services.grading import grade_case_answer
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/submit", response_model=SubmitAnswerOut)
def submit_answer(
    answer_in: SubmitAnswerIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == answer_in.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    user_ans = (answer_in.user_answer or "").strip()
    correct_ans = (question.correct_answer or "").strip()

    is_correct = False
    earned_score = 0.0
    total_score = 1.0
    rubric_results = None
    feedback = None

    if question.subject == "basic":
        total_score = 1.0
        # Choice question comparison (e.g. "A" vs "A")
        if user_ans.upper() == correct_ans.upper():
            is_correct = True
            earned_score = 1.0
            feedback = "回答正确！"
        else:
            is_correct = False
            earned_score = 0.0
            feedback = f"回答错误。正确答案是 {correct_ans}。"
    else:
        # Case question semi-automatic grading
        earned_score, total_score, rubric_results = grade_case_answer(user_ans, question.rubrics or [])
        is_correct = (earned_score >= total_score * 0.7) if total_score > 0 else False
        feedback = f"案例自测得分：{earned_score}/{total_score} 分。"

    # Save to PracticeRecord
    record = PracticeRecord(
        user_id=current_user.id,
        question_id=question.id,
        subject=question.subject,
        chapter=question.chapter,
        knowledge=question.knowledge,
        user_answer=user_ans,
        is_correct=is_correct,
        score=earned_score,
        answered_at=datetime.now(timezone.utc)
    )
    db.add(record)

    # If incorrect, automatically add/update WrongQuestion table
    if not is_correct:
        existing_wq = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.question_id == question.id
        ).first()

        now = datetime.now(timezone.utc)
        if existing_wq:
            existing_wq.wrong_count += 1
            existing_wq.user_answer = user_ans
            existing_wq.is_mastered = False
            existing_wq.answered_at = now
            existing_wq.updated_at = now
        else:
            new_wq = WrongQuestion(
                user_id=current_user.id,
                question_id=question.id,
                subject=question.subject,
                knowledge=question.knowledge,
                stem=question.stem,
                options=question.options,
                correct_answer=question.correct_answer,
                user_answer=user_ans,
                analysis=question.analysis,
                source=question.source or "ai-generated",
                answered_at=now,
                wrong_count=1,
                is_mastered=False
            )
            db.add(new_wq)

    db.commit()

    return SubmitAnswerOut(
        is_correct=is_correct,
        correct_answer=correct_ans,
        user_answer=user_ans,
        analysis=question.analysis,
        earned_score=earned_score,
        total_score=total_score,
        rubric_results=rubric_results,
        feedback=feedback
    )
