import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models.user import User
from app.models.learn import GlossaryTerm, UserGlossaryStatus, KnowledgePoint
from app.schemas.learn import (
    GlossaryItem, GlossaryDetail, GlossaryStatusUpdate, PointBriefItem,
    GlossaryQuizQuestion, GlossaryQuizOption, GlossaryQuizSubmitRequest,
    GlossaryQuizSubmitResult, GlossaryQuizReviewItem
)
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/glossary")
def list_glossary(
    q: Optional[str] = Query(None, description="搜索英文术语或中文释义"),
    tag: Optional[str] = Query(None, description="按领域标签筛选"),
    known: Optional[str] = Query(None, description="按掌握程度筛选：unknown, know, dont_know"),
    favorited: Optional[bool] = Query(None, description="是否只看收藏"),
    frequency: Optional[str] = Query(None, description="按考频筛选：high, mid, low"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检索英语术语词表，支持中英文搜索、领域标签、考频及个人掌握/收藏状态筛选
    """
    query = db.query(GlossaryTerm)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(or_(
            GlossaryTerm.term_en.ilike(search_pattern),
            GlossaryTerm.term_zh.ilike(search_pattern)
        ))

    if frequency:
        query = query.filter(GlossaryTerm.frequency == frequency)

    # Fetch user status mapping
    user_statuses = db.query(UserGlossaryStatus).filter(UserGlossaryStatus.user_id == current_user.id).all()
    status_map = {s.term_id: s for s in user_statuses}

    terms = query.order_by(GlossaryTerm.term_en.asc()).all()

    items = []
    for t in terms:
        # Tag filter check (JSON list)
        if tag:
            tags = t.tags or []
            if tag not in tags:
                continue

        u_stat = status_map.get(t.id)
        u_known = u_stat.known if u_stat else "unknown"
        u_fav = u_stat.favorited if u_stat else False

        if known and u_known != known:
            continue
        if favorited is not None and u_fav != favorited:
            continue

        items.append(GlossaryItem(
            id=t.id,
            term_en=t.term_en,
            term_zh=t.term_zh,
            tags=t.tags or [],
            tip=t.tip,
            frequency=t.frequency,
            confuse_with=t.confuse_with or [],
            known=u_known,
            favorited=u_fav
        ))

    total = len(items)
    start = (page - 1) * page_size
    paged = items[start:start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paged
    }

@router.get("/glossary/{id}", response_model=GlossaryDetail)
def get_glossary_detail(
    id: str = Path(..., description="词条ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个英语词条卡片详情，包含易混词辨析与关联的系统集成知识点
    """
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == id).first()
    if not term:
        raise HTTPException(status_code=404, detail="术语词条不存在")

    u_stat = db.query(UserGlossaryStatus).filter(
        UserGlossaryStatus.user_id == current_user.id,
        UserGlossaryStatus.term_id == term.id
    ).first()
    known = u_stat.known if u_stat else "unknown"
    favorited = u_stat.favorited if u_stat else False

    # Linked knowledge points
    points_data = []
    if term.knowledge_point_ids:
        kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(term.knowledge_point_ids)).all()
        for p in kps:
            points_data.append(PointBriefItem(
                id=p.id,
                title=p.title,
                chapter_id=p.chapter_id,
                frequency=p.frequency
            ))

    return GlossaryDetail(
        id=term.id,
        term_en=term.term_en,
        term_zh=term.term_zh,
        tags=term.tags or [],
        tip=term.tip,
        frequency=term.frequency,
        confuse_with=term.confuse_with or [],
        known=known,
        favorited=favorited,
        knowledge_points=points_data
    )

@router.post("/glossary/{id}/status")
def update_glossary_status(
    id: str,
    payload: GlossaryStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新词条的掌握程度（known/dont_know/unknown）或收藏状态（favorited）
    """
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == id).first()
    if not term:
        raise HTTPException(status_code=404, detail="术语词条不存在")

    u_stat = db.query(UserGlossaryStatus).filter(
        UserGlossaryStatus.user_id == current_user.id,
        UserGlossaryStatus.term_id == id
    ).first()

    now = datetime.now(timezone.utc)
    if not u_stat:
        u_stat = UserGlossaryStatus(
            user_id=current_user.id,
            term_id=id,
            known=payload.known or "unknown",
            favorited=payload.favorited if payload.favorited is not None else False,
            updated_at=now
        )
        db.add(u_stat)
    else:
        if payload.known is not None:
            u_stat.known = payload.known
        if payload.favorited is not None:
            u_stat.favorited = payload.favorited
        u_stat.updated_at = now

    db.commit()
    return {
        "term_id": id,
        "known": u_stat.known,
        "favorited": u_stat.favorited,
        "message": "词条状态已更新"
    }

@router.post("/glossary/quiz", response_model=List[GlossaryQuizQuestion])
def generate_glossary_quiz(
    tag: Optional[str] = Query(None, description="可选按领域抽题"),
    count: int = Query(10, ge=5, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    看英文选中文：抽取 10 道英语术语小测验题目，动态生成混淆选项
    """
    all_terms = db.query(GlossaryTerm).all()
    if len(all_terms) < 4:
        raise HTTPException(status_code=400, detail="词库术语不足以生成测验（需至少4个词）")

    # Filter pool if tag specified
    pool = all_terms
    if tag:
        tagged = [t for t in all_terms if t.tags and tag in t.tags]
        if len(tagged) >= 4:
            pool = tagged

    # Pick target count terms
    sample_size = min(count, len(pool))
    target_terms = random.sample(pool, sample_size)

    questions = []
    option_keys = ["A", "B", "C", "D"]

    for idx, t in enumerate(target_terms, start=1):
        # 3 distractors from all_terms
        distractor_candidates = [other.term_zh for other in all_terms if other.id != t.id and other.term_zh != t.term_zh]
        distractors = random.sample(distractor_candidates, min(3, len(distractor_candidates)))

        all_choices = [t.term_zh] + distractors
        random.shuffle(all_choices)

        options = [
            GlossaryQuizOption(key=option_keys[i], text=all_choices[i])
            for i in range(len(all_choices))
        ]

        questions.append(GlossaryQuizQuestion(
            index=idx,
            term_id=t.id,
            term_en=t.term_en,
            tags=t.tags or [],
            options=options
        ))

    return questions

@router.post("/glossary/quiz/submit", response_model=GlossaryQuizSubmitResult)
def submit_glossary_quiz(
    payload: GlossaryQuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交小测答案，即时判分并输出详细回顾（含考点提示与易混辨析）
    """
    if not payload.answers:
        raise HTTPException(status_code=400, detail="未提交任何作答")

    term_ids = [a.term_id for a in payload.answers]
    terms = {t.id: t for t in db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(term_ids)).all()}

    correct_count = 0
    results: List[GlossaryQuizReviewItem] = []

    for a in payload.answers:
        term = terms.get(a.term_id)
        if not term:
            continue

        # In quiz, user submitted selected_option which may be "A", "B", "C", "D" or the text directly
        # If client passes text or key, compare
        is_match = (a.selected_option.strip() == term.term_zh.strip())
        if is_match:
            correct_count += 1

        results.append(GlossaryQuizReviewItem(
            term_id=term.id,
            term_en=term.term_en,
            term_zh=term.term_zh,
            selected_key=a.selected_option,
            correct_key=term.term_zh,
            is_correct=is_match,
            tip=term.tip,
            confuse_with=term.confuse_with
        ))

    total = len(payload.answers)
    score = int(round((correct_count / total) * 100)) if total > 0 else 0

    return GlossaryQuizSubmitResult(
        total_questions=total,
        correct_count=correct_count,
        score=score,
        results=results
    )
