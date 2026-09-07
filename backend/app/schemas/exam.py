from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.question import QuestionPracticeItem

class ExamGenerateIn(BaseModel):
    subject: str = Field(default="basic", description="basic 或 case")
    question_count: int = Field(default=75, description="题目数量，默认75题")
    chapter: Optional[str] = None

class ExamSubmitIn(BaseModel):
    subject: str = "basic"
    time_spent: int = 0  # seconds
    answers: Dict[str, str] = {}  # {question_id: user_answer}

class ExamQuestionSummary(BaseModel):
    question_id: str
    stem: str
    options: Optional[List[str]] = None
    user_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    score: float
    analysis: Optional[str] = None

class ExamResultOut(BaseModel):
    id: str
    subject: str
    total_questions: int
    correct_count: int
    score: float
    total_score: float
    time_spent: int
    created_at: Optional[datetime] = None
    details: Optional[List[ExamQuestionSummary]] = None
