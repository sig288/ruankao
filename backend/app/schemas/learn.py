from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ----------------- 章节与知识点 -----------------

class ChapterItem(BaseModel):
    id: str
    code: str
    title: str
    sort_order: int
    total_points: int = 0
    mastered_points: int = 0
    completion_rate: float = 0.0

class GlossaryBriefItem(BaseModel):
    id: str
    term_en: str
    term_zh: str
    frequency: str = "mid"
    tip: Optional[str] = None

class PointCardItem(BaseModel):
    id: str
    chapter_id: str
    title: str
    frequency: str = "mid"
    est_minutes: int = 10
    domain_tags: Optional[List[str]] = None
    status: str = "unlearned"  # 'unlearned', 'learning', 'mastered'
    question_count: int = 0
    glossary_count: int = 0
    sort_order: int = 0

class PointDetail(BaseModel):
    id: str
    chapter_id: str
    chapter_title: Optional[str] = None
    title: str
    frequency: str = "mid"
    est_minutes: int = 10
    summary_md: str
    formula_md: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    status: str = "unlearned"
    last_studied_at: Optional[datetime] = None
    glossary_terms: List[GlossaryBriefItem] = []
    practice_count: int = 0
    question_ids: List[str] = []

class PointStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(unlearned|learning|mastered)$")

class LearnProgressResponse(BaseModel):
    total_points: int
    mastered_points: int
    overall_completion_rate: float
    chapters: List[ChapterItem]
    recent_studied: List[PointCardItem]

# ----------------- 英语词表 -----------------

class PointBriefItem(BaseModel):
    id: str
    title: str
    chapter_id: str
    frequency: str = "mid"

class GlossaryItem(BaseModel):
    id: str
    term_en: str
    term_zh: str
    tags: Optional[List[str]] = None
    tip: Optional[str] = None
    frequency: str = "mid"
    confuse_with: Optional[List[str]] = None
    known: str = "unknown"  # 'unknown', 'know', 'dont_know'
    favorited: bool = False

class GlossaryDetail(GlossaryItem):
    knowledge_points: List[PointBriefItem] = []

class GlossaryStatusUpdate(BaseModel):
    known: Optional[str] = Field(None, pattern="^(unknown|know|dont_know)$")
    favorited: Optional[bool] = None

class GlossaryQuizOption(BaseModel):
    key: str  # "A", "B", "C", "D"
    text: str

class GlossaryQuizQuestion(BaseModel):
    index: int
    term_id: str
    term_en: str
    tags: Optional[List[str]] = None
    options: List[GlossaryQuizOption]

class GlossaryQuizAnswer(BaseModel):
    term_id: str
    selected_option: str  # "A", "B", "C", "D"

class GlossaryQuizSubmitRequest(BaseModel):
    answers: List[GlossaryQuizAnswer]

class GlossaryQuizReviewItem(BaseModel):
    term_id: str
    term_en: str
    term_zh: str
    selected_key: str
    correct_key: str
    is_correct: bool
    tip: Optional[str] = None
    confuse_with: Optional[List[str]] = None

class GlossaryQuizSubmitResult(BaseModel):
    total_questions: int
    correct_count: int
    score: int
    results: List[GlossaryQuizReviewItem]

# ----------------- 管理员批量导入 -----------------

class PointImportItem(BaseModel):
    id: str
    chapter_id: str
    title: str
    frequency: str = "mid"
    est_minutes: int = 10
    summary_md: str
    formula_md: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    glossary_ids: Optional[List[str]] = None
    question_ids: Optional[List[str]] = None
    sort_order: int = 0

class GlossaryImportItem(BaseModel):
    id: Optional[str] = None
    term_en: str
    term_zh: str
    tags: Optional[List[str]] = None
    tip: Optional[str] = None
    frequency: str = "mid"
    confuse_with: Optional[List[str]] = None
    knowledge_point_ids: Optional[List[str]] = None
