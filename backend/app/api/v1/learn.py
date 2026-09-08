from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.learn import KnowledgeChapter, KnowledgePoint, UserPointStatus, GlossaryTerm
from app.schemas.learn import (
    ChapterItem, PointCardItem, PointDetail, PointStatusUpdate,
    LearnProgressResponse, GlossaryBriefItem
)
from app.schemas.question import QuestionPracticeItem
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/chapters", response_model=List[ChapterItem])
def get_chapters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取 17 章大纲列表，包含每章的知识点总数、当前用户已掌握数及完成率
    """
    chapters = db.query(KnowledgeChapter).order_by(KnowledgeChapter.sort_order.asc()).all()
    if not chapters:
        return []

    # Count total points per chapter
    point_counts = dict(
        db.query(KnowledgePoint.chapter_id, func.count(KnowledgePoint.id))
        .group_by(KnowledgePoint.chapter_id)
        .all()
    )

    # Count mastered points per chapter for current user
    mastered_counts = dict(
        db.query(KnowledgePoint.chapter_id, func.count(UserPointStatus.id))
        .join(UserPointStatus, UserPointStatus.point_id == KnowledgePoint.id)
        .filter(UserPointStatus.user_id == current_user.id, UserPointStatus.status == "mastered")
        .group_by(KnowledgePoint.chapter_id)
        .all()
    )

    res = []
    for ch in chapters:
        tot = point_counts.get(ch.id, 0)
        mas = mastered_counts.get(ch.id, 0)
        rate = round(mas / tot, 2) if tot > 0 else 0.0
        res.append(ChapterItem(
            id=ch.id,
            code=ch.code,
            title=ch.title,
            sort_order=ch.sort_order,
            total_points=tot,
            mastered_points=mas,
            completion_rate=rate
        ))
    return res

@router.get("/points")
def list_points(
    chapter_id: Optional[str] = Query(None, description="所属章ID，如 CH07"),
    status: Optional[str] = Query(None, description="状态筛选：unlearned, learning, mastered"),
    frequency: Optional[str] = Query(None, description="考频筛选：high, mid, low"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    知识点卡片列表查询，支持按章、学习状态、考频多维度筛选
    """
    query = db.query(KnowledgePoint)

    if chapter_id:
        query = query.filter(KnowledgePoint.chapter_id == chapter_id)
    if frequency:
        query = query.filter(KnowledgePoint.frequency == frequency)

    # User statuses for current user
    user_status_map = dict(
        db.query(UserPointStatus.point_id, UserPointStatus.status)
        .filter(UserPointStatus.user_id == current_user.id)
        .all()
    )

    points = query.order_by(KnowledgePoint.sort_order.asc(), KnowledgePoint.id.asc()).all()

    items = []
    for p in points:
        u_status = user_status_map.get(p.id, "unlearned")
        if status and u_status != status:
            continue

        q_count = len(p.question_ids) if p.question_ids else 0
        g_count = len(p.glossary_ids) if p.glossary_ids else 0

        items.append(PointCardItem(
            id=p.id,
            chapter_id=p.chapter_id,
            title=p.title,
            frequency=p.frequency,
            est_minutes=p.est_minutes,
            domain_tags=p.domain_tags or [],
            status=u_status,
            question_count=q_count,
            glossary_count=g_count,
            sort_order=p.sort_order
        ))

    total = len(items)
    start = (page - 1) * page_size
    paged_items = items[start:start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paged_items
    }

@router.get("/points/{id}", response_model=PointDetail)
def get_point_detail(
    id: str = Path(..., description="知识点ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个知识点完整详情，含核心 Markdown 要点、公式、用户学习状态及关联英语术语
    """
    point = db.query(KnowledgePoint).filter(KnowledgePoint.id == id).first()
    if not point:
        raise HTTPException(status_code=404, detail="知识点不存在")

    chapter = db.query(KnowledgeChapter).filter(KnowledgeChapter.id == point.chapter_id).first()
    chapter_title = chapter.title if chapter else None

    # User status
    ups = db.query(UserPointStatus).filter(
        UserPointStatus.user_id == current_user.id,
        UserPointStatus.point_id == point.id
    ).first()
    status = ups.status if ups else "unlearned"
    last_studied_at = ups.last_studied_at if ups else None

    # Related glossary terms
    glossary_items = []
    if point.glossary_ids:
        terms = db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(point.glossary_ids)).all()
        for t in terms:
            glossary_items.append(GlossaryBriefItem(
                id=t.id,
                term_en=t.term_en,
                term_zh=t.term_zh,
                frequency=t.frequency,
                tip=t.tip
            ))

    q_ids = point.question_ids or []
    practice_count = len(q_ids)

    return PointDetail(
        id=point.id,
        chapter_id=point.chapter_id,
        chapter_title=chapter_title,
        title=point.title,
        frequency=point.frequency,
        est_minutes=point.est_minutes,
        summary_md=point.summary_md,
        formula_md=point.formula_md,
        domain_tags=point.domain_tags or [],
        status=status,
        last_studied_at=last_studied_at,
        glossary_terms=glossary_items,
        practice_count=practice_count,
        question_ids=q_ids
    )

@router.post("/points/{id}/status")
def update_point_status(
    id: str,
    payload: PointStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换知识点学习状态（unlearned, learning, mastered），即时持久化并记录最近学习时间
    """
    point = db.query(KnowledgePoint).filter(KnowledgePoint.id == id).first()
    if not point:
        raise HTTPException(status_code=404, detail="知识点不存在")

    ups = db.query(UserPointStatus).filter(
        UserPointStatus.user_id == current_user.id,
        UserPointStatus.point_id == id
    ).first()

    now = datetime.now(timezone.utc)
    if not ups:
        ups = UserPointStatus(
            user_id=current_user.id,
            point_id=id,
            status=payload.status,
            last_studied_at=now,
            updated_at=now
        )
        db.add(ups)
    else:
        ups.status = payload.status
        ups.last_studied_at = now
        ups.updated_at = now

    db.commit()
    return {
        "point_id": id,
        "status": ups.status,
        "last_studied_at": ups.last_studied_at,
        "message": "学习状态已更新"
    }

@router.get("/points/{id}/practice")
def get_point_practice_questions(
    id: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取与该知识点关联的真题与练习题（优先精准关联，缺省由知识点标签兜底）
    """
    point = db.query(KnowledgePoint).filter(KnowledgePoint.id == id).first()
    if not point:
        raise HTTPException(status_code=404, detail="知识点不存在")

    questions: List[Question] = []

    # 1. Directly matched question IDs
    if point.question_ids:
        qs = db.query(Question).filter(Question.id.in_(point.question_ids)).all()
        questions.extend(qs)

    # 2. Match by title or knowledge string if not enough
    if len(questions) < limit:
        needed = limit - len(questions)
        exclude_ids = [q.id for q in questions]
        fallback_qs = db.query(Question).filter(
            ~Question.id.in_(exclude_ids) if exclude_ids else True,
            Question.knowledge.ilike(f"%{point.title[:6]}%")
        ).limit(needed).all()
        questions.extend(fallback_qs)

    # 3. Match by chapter if still not enough
    if len(questions) < limit:
        ch = db.query(KnowledgeChapter).filter(KnowledgeChapter.id == point.chapter_id).first()
        if ch:
            needed = limit - len(questions)
            exclude_ids = [q.id for q in questions]
            ch_qs = db.query(Question).filter(
                ~Question.id.in_(exclude_ids) if exclude_ids else True,
                Question.chapter.ilike(f"%{ch.title[4:8]}%")
            ).limit(needed).all()
            questions.extend(ch_qs)

    res = []
    for q in questions[:limit]:
        res.append(QuestionPracticeItem(
            id=q.id,
            subject=q.subject,
            chapter=q.chapter,
            knowledge=q.knowledge,
            stem=q.stem,
            options=q.options,
            source=q.source,
            difficulty=q.difficulty
        ))

    return {
        "point_id": id,
        "point_title": point.title,
        "total": len(res),
        "items": res
    }

@router.get("/progress", response_model=LearnProgressResponse)
def get_learn_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取全局学习进度：章节完成度概览 + 最近学习历史（倒序前 5 条）
    """
    total_points = db.query(KnowledgePoint).count()

    mastered_points = (
        db.query(func.count(UserPointStatus.id))
        .filter(UserPointStatus.user_id == current_user.id, UserPointStatus.status == "mastered")
        .scalar() or 0
    )

    overall_rate = round(mastered_points / total_points, 2) if total_points > 0 else 0.0

    # Chapters breakdown
    chapters_data = get_chapters(current_user=current_user, db=db)

    # Recent studied points
    recent_records = (
        db.query(UserPointStatus, KnowledgePoint)
        .join(KnowledgePoint, KnowledgePoint.id == UserPointStatus.point_id)
        .filter(UserPointStatus.user_id == current_user.id)
        .order_by(desc(UserPointStatus.last_studied_at))
        .limit(5)
        .all()
    )

    recent_items = []
    for ups, kp in recent_records:
        recent_items.append(PointCardItem(
            id=kp.id,
            chapter_id=kp.chapter_id,
            title=kp.title,
            frequency=kp.frequency,
            est_minutes=kp.est_minutes,
            domain_tags=kp.domain_tags or [],
            status=ups.status,
            question_count=len(kp.question_ids) if kp.question_ids else 0,
            glossary_count=len(kp.glossary_ids) if kp.glossary_ids else 0,
            sort_order=kp.sort_order
        ))

    return LearnProgressResponse(
        total_points=total_points,
        mastered_points=mastered_points,
        overall_completion_rate=overall_rate,
        chapters=chapters_data,
        recent_studied=recent_items
    )
