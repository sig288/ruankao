from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class SubmitAnswerIn(BaseModel):
    question_id: str
    user_answer: str

class RubricMatchResult(BaseModel):
    point: str
    max_score: float
    earned_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    is_hit: bool

class SubmitAnswerOut(BaseModel):
    is_correct: bool
    correct_answer: str
    user_answer: str
    analysis: Optional[str] = None
    earned_score: float = 0.0
    total_score: float = 1.0
    rubric_results: Optional[List[RubricMatchResult]] = None
    feedback: Optional[str] = None
