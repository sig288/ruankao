from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class RubricItem(BaseModel):
    point: str
    score: float
    keywords: List[str]

class QuestionBase(BaseModel):
    subject: str = Field(default="basic", description="basic 或 case")
    chapter: str
    knowledge: str
    stem: str
    options: Optional[List[str]] = None
    correct_answer: str
    analysis: Optional[str] = None
    rubrics: Optional[List[RubricItem]] = None
    source: str = "ai-generated"
    difficulty: str = "medium"

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestionPracticeItem(BaseModel):
    id: str
    subject: str
    chapter: str
    knowledge: str
    stem: str
    options: Optional[List[str]] = None
    difficulty: str = "medium"
    source: str = "ai-generated"
    # When user is practicing, we can include answers or omit them; including them allows fast client-side offline checking
    correct_answer: Optional[str] = None
    analysis: Optional[str] = None
    rubrics: Optional[List[Any]] = None

    class Config:
        from_attributes = True
