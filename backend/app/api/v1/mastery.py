from datetime import datetime, timezone, timedelta
import random
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.record import PracticeRecord
from app.models.wrong_question import WrongQuestion
from app.schemas.question import QuestionPracticeItem
from app.api.deps import get_current_user

router = APIRouter()

# 10 Management Knowledge Domains Mapping
DOMAIN_CHAPTER_MAP = {
    "项目整合管理": ["第7章 项目整体管理", "项目整合管理", "配置与变更管理"],
    "项目范围管理": ["第8章 项目范围管理", "项目范围管理"],
    "项目进度管理": ["第9章 项目进度管理", "项目进度管理", "项目进度与变更控制"],
    "项目成本管理": ["第10章 项目成本管理", "项目成本管理", "项目成本与进度管理"],
    "项目质量管理": ["第11章 项目质量管理", "项目质量管理"],
    "项目资源管理": ["第12章 项目资源管理", "项目资源管理"],
    "项目沟通管理": ["第13章 项目沟通管理", "项目沟通管理", "项目沟通与干系人管理"],
    "项目风险管理": ["第14章 项目风险管理", "项目风险管理"],
    "项目采购管理": ["第15章 项目采购管理", "项目采购管理"],
    "项目干系人管理": ["第16章 项目干系人管理", "项目干系人管理"]
}

@router.get("/me")
def get_user_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes mastery statistics for the authenticated user across:
    1. All syllabus chapters (17 chapters)
    2. The 10 Knowledge Domains
    Metrics: coverage_rate, accuracy_rate (30d), trend_7d, mastery_level ('weak'|'medium'|'strong'|'untested')
    """
    now = datetime.now(timezone.utc)
    d30_ago = now - timedelta(days=30)
    d7_ago = now - timedelta(days=7)
    d14_ago = now - timedelta(days=14)

    # 1. Total questions per chapter in question bank
    chapter_totals = dict(
        db.query(Question.chapter, func.count(Question.id))
        .group_by(Question.chapter)
        .all()
    )

    # 2. User practiced unique questions per chapter
    user_unique_practiced = dict(
        db.query(PracticeRecord.chapter, func.count(distinct(PracticeRecord.question_id)))
        .filter(PracticeRecord.user_id == current_user.id)
        .group_by(PracticeRecord.chapter)
        .all()
    )

    # 3. User recent 30-day stats per chapter: (total_answered, correct_answered)
    rec_30d = (
        db.query(
            PracticeRecord.chapter,
            func.count(PracticeRecord.id).label("total"),
            func.sum(case((PracticeRecord.is_correct == True, 1), else_=0)).label("correct")
        )
        .filter(PracticeRecord.user_id == current_user.id, PracticeRecord.answered_at >= d30_ago)
        .group_by(PracticeRecord.chapter)
        .all()
    )
    stats_30d = {r.chapter: (r.total, r.correct or 0) for r in rec_30d}

    # 4. Recent 7-day stats
    rec_7d = (
        db.query(
            PracticeRecord.chapter,
            func.count(PracticeRecord.id).label("total"),
            func.sum(case((PracticeRecord.is_correct == True, 1), else_=0)).label("correct")
        )
        .filter(PracticeRecord.user_id == current_user.id, PracticeRecord.answered_at >= d7_ago)
        .group_by(PracticeRecord.chapter)
        .all()
    )
    stats_7d = {r.chapter: (r.total, r.correct or 0) for r in rec_7d}

    # 5. Prior 7-day stats (between 14 and 7 days ago)
    rec_prior7d = (
        db.query(
            PracticeRecord.chapter,
            func.count(PracticeRecord.id).label("total"),
            func.sum(case((PracticeRecord.is_correct == True, 1), else_=0)).label("correct")
        )
        .filter(
            PracticeRecord.user_id == current_user.id,
            PracticeRecord.answered_at >= d14_ago,
            PracticeRecord.answered_at < d7_ago
        )
        .group_by(PracticeRecord.chapter)
        .all()
    )
    stats_prior7d = {r.chapter: (r.total, r.correct or 0) for r in rec_prior7d}

    # Build Chapter Mastery
    chapter_results = []
    weak_chapters = []

    for ch, total_q in chapter_totals.items():
        done_q = user_unique_practiced.get(ch, 0)
        cov_rate = round(done_q / total_q, 3) if total_q > 0 else 0.0

        ans_30d, cor_30d = stats_30d.get(ch, (0, 0))
        accuracy = round(cor_30d / ans_30d, 3) if ans_30d > 0 else None

        # Trend calculation
        ans_7, cor_7 = stats_7d.get(ch, (0, 0))
        ans_p7, cor_p7 = stats_prior7d.get(ch, (0, 0))
        rate_7 = (cor_7 / ans_7) if ans_7 > 0 else None
        rate_p7 = (cor_p7 / ans_p7) if ans_p7 > 0 else None

        trend = 0.0
        if rate_7 is not None and rate_p7 is not None:
            trend = round(rate_7 - rate_p7, 3)
        elif rate_7 is not None:
            trend = round(rate_7 - 0.5, 3)

        # Mastery level
        if ans_30d == 0 and done_q == 0:
            level = "untested"
        elif accuracy is None or accuracy < 0.60:
            level = "weak"
            weak_chapters.append(ch)
        elif accuracy < 0.80:
            level = "medium"
        else:
            level = "strong"

        chapter_results.append({
            "name": ch,
            "total_questions": total_q,
            "practiced_questions": done_q,
            "coverage_rate": cov_rate,
            "answered_30d": ans_30d,
            "accuracy_rate": accuracy,
            "trend_7d": trend,
            "level": level
        })

    # Sort chapters in standard order
    chapter_results.sort(key=lambda x: x["name"])

    # Build 10 Knowledge Domains Mastery
    domain_results = []
    weak_domains = []

    for domain, mapped_chapters in DOMAIN_CHAPTER_MAP.items():
        d_total_q = sum(chapter_totals.get(c, 0) for c in mapped_chapters)
        d_done_q = sum(user_unique_practiced.get(c, 0) for c in mapped_chapters)
        d_cov = round(d_done_q / d_total_q, 3) if d_total_q > 0 else 0.0

        d_ans_30d = sum(stats_30d.get(c, (0, 0))[0] for c in mapped_chapters)
        d_cor_30d = sum(stats_30d.get(c, (0, 0))[1] for c in mapped_chapters)
        d_acc = round(d_cor_30d / d_ans_30d, 3) if d_ans_30d > 0 else None

        if d_ans_30d == 0 and d_done_q == 0:
            d_level = "untested"
        elif d_acc is None or d_acc < 0.60:
            d_level = "weak"
            weak_domains.append(domain)
        elif d_acc < 0.80:
            d_level = "medium"
        else:
            d_level = "strong"

        domain_results.append({
            "name": domain,
            "total_questions": d_total_q,
            "practiced_questions": d_done_q,
            "coverage_rate": d_cov,
            "answered_30d": d_ans_30d,
            "accuracy_rate": d_acc,
            "level": d_level
        })

    # Overall user readiness score (0-100)
    total_bank = sum(chapter_totals.values())
    total_practiced = sum(user_unique_practiced.values())
    total_answered_30d = sum(r[0] for r in stats_30d.values())
    total_correct_30d = sum(r[1] for r in stats_30d.values())
    overall_acc = (total_correct_30d / total_answered_30d) if total_answered_30d > 0 else 0.0
    overall_cov = (total_practiced / total_bank) if total_bank > 0 else 0.0
    readiness_score = round((overall_acc * 0.7 + overall_cov * 0.3) * 100, 1)

    return {
        "overall_readiness": readiness_score,
        "total_practiced": total_practiced,
        "total_in_bank": total_bank,
        "weak_chapters": weak_chapters,
        "weak_domains": weak_domains,
        "chapters": chapter_results,
        "domains": domain_results
    }

@router.post("/weak-drill", response_model=List[QuestionPracticeItem])
def generate_weakness_drill(
    count: int = Body(10, embed=True, ge=5, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    P0 Feature: M5 Weakness-driven Practice Drill
    Rules:
    1. Identifies user's weak chapters and domains.
    2. Prioritizes unmastered wrong questions from those chapters.
    3. Fills >=60% of question set with weak-chapter questions.
    4. Balances with adjacent or untested questions.
    5. Returns practice questions (immediate self-check mode).
    """
    # 1. Fetch unmastered wrong questions for current user
    unmastered_wqs = (
        db.query(WrongQuestion)
        .filter(WrongQuestion.user_id == current_user.id, WrongQuestion.is_mastered == False)
        .all()
    )
    wrong_qids = [wq.question_id for wq in unmastered_wqs]

    # 2. Get user's weak chapters (accuracy < 60% in 30 days or wrong questions exist)
    weak_chapters = set()
    for wq in unmastered_wqs:
        # fetch question chapter
        q = db.query(Question).filter(Question.id == wq.question_id).first()
        if q and q.chapter:
            weak_chapters.add(q.chapter)

    # 3. If weak_chapters is empty, check practice records with low accuracy
    if not weak_chapters:
        rec_acc = (
            db.query(
                PracticeRecord.chapter,
                func.sum(case((PracticeRecord.is_correct == True, 1), else_=0)) * 1.0 / func.count(PracticeRecord.id)
            )
            .filter(PracticeRecord.user_id == current_user.id)
            .group_by(PracticeRecord.chapter)
            .having(func.count(PracticeRecord.id) >= 2)
            .all()
        )
        for ch, acc in rec_acc:
            if acc < 0.60:
                weak_chapters.add(ch)

    # Selected questions pool
    selected_questions: List[Question] = []
    selected_ids = set()

    # Step A: Pick from unmastered wrong questions (up to 40% of target count)
    max_wrong = max(2, int(count * 0.4))
    if wrong_qids:
        candidate_wrong = (
            db.query(Question)
            .filter(Question.id.in_(wrong_qids[:max_wrong * 2]))
            .all()
        )
        picked_wrong = random.sample(candidate_wrong, min(len(candidate_wrong), max_wrong))
        for q in picked_wrong:
            if q.id not in selected_ids:
                selected_questions.append(q)
                selected_ids.add(q.id)

    # Step B: Pick weak-chapter questions (target >= 60% total)
    target_weak_count = int(count * 0.7)
    needed_weak = target_weak_count - len(selected_questions)
    
    if weak_chapters and needed_weak > 0:
        weak_candidates = (
            db.query(Question)
            .filter(Question.chapter.in_(list(weak_chapters)), Question.subject == "basic")
            .filter(~Question.id.in_(selected_ids))
            .all()
        )
        if weak_candidates:
            sample_size = min(len(weak_candidates), needed_weak)
            for q in random.sample(weak_candidates, sample_size):
                if q.id not in selected_ids:
                    selected_questions.append(q)
                    selected_ids.add(q.id)

    # Step C: If still not enough, fill with unpracticed questions or random questions
    remaining_needed = count - len(selected_questions)
    if remaining_needed > 0:
        other_candidates = (
            db.query(Question)
            .filter(Question.subject == "basic")
            .filter(~Question.id.in_(selected_ids))
            .all()
        )
        if other_candidates:
            sample_size = min(len(other_candidates), remaining_needed)
            for q in random.sample(other_candidates, sample_size):
                if q.id not in selected_ids:
                    selected_questions.append(q)
                    selected_ids.add(q.id)

    # Shuffle final set
    random.shuffle(selected_questions)

    # Format output items with analysis available for immediate study
    return [
        QuestionPracticeItem(
            id=q.id,
            subject=q.subject,
            chapter=q.chapter,
            knowledge=q.knowledge,
            stem=q.stem,
            options=q.options,
            difficulty=q.difficulty,
            source=f"薄弱点专练 · {q.source}",
            correct_answer=q.correct_answer,
            analysis=q.analysis,
            rubrics=q.rubrics
        )
        for q in selected_questions
    ]
