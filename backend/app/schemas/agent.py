from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field

class AgentWrongQuestionItem(BaseModel):
    id: Optional[str] = None
    user_id: str
    question_id: str
    subject: str = "basic"
    knowledge: str
    stem: str
    options: Optional[List[str]] = None
    correct_answer: str
    user_answer: Optional[str] = None
    analysis: Optional[str] = None
    answered_at: Optional[Union[datetime, str]] = None
    source: str = "ai-generated"
    wrong_count: Optional[int] = 1
    is_mastered: Optional[bool] = False
    agent_explanation: Optional[str] = None

class AgentWrongQuestionBatchIn(BaseModel):
    items: List[AgentWrongQuestionItem]

class AgentWrongQuestionBatchOut(BaseModel):
    success: bool
    imported_count: int
    message: str

class AgentExplainCallbackIn(BaseModel):
    wrong_question_id: str = Field(..., description="错题ID，例如 wq_xxx")
    explanation: str = Field(..., description="Agent提供的题目深度讲解内容")
    study_tips: Optional[str] = Field(None, description="学习建议或记忆口诀")

class AgentApiKeyCreate(BaseModel):
    name: str = Field(..., description="Agent 名称或用途标识")

class AgentApiKeyOut(BaseModel):
    id: str
    key: str
    name: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
