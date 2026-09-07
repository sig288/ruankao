from datetime import datetime, timezone, timedelta
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.api.deps import get_current_user

router = APIRouter()

class PlanConfigIn(BaseModel):
    exam_date: str  # YYYY-MM-DD
    daily_minutes: int = 60

class PlanOut(BaseModel):
    id: str
    exam_date: str
    days_remaining: int
    daily_minutes: int
    tasks: List[Dict[str, Any]]
    updated_at: datetime

def generate_default_schedule(exam_date_str: str, daily_minutes: int) -> List[Dict[str, Any]]:
    """
    Generates dynamic 14-day study plan:
    - Days 1-5: High-yield core chapters (Scope, Schedule, Cost, Quality, Risk)
    - Days 6-7: Wrong question cleanup + Case calculations
    - Days 8-11: ITTO & Security/Architecture chapters
    - Days 12-14: Full 75-question mock exams & mnemonic review
    """
    now = datetime.now(timezone.utc)
    tasks = []

    plan_templates = [
        {"type": "chapter", "title": "攻坚第8章：项目范围管理（WBS分解与范围基准）", "path": "/practice?chapter=第8章 项目范围管理", "duration": 30},
        {"type": "chapter", "title": "攻坚第9章：项目进度管理（关键路径CPM与总时差）", "path": "/practice?chapter=第9章 项目进度管理", "duration": 35},
        {"type": "chapter", "title": "攻坚第10章：项目成本管理（EVM挣值公式计算）", "path": "/practice?chapter=第10章 项目成本管理", "duration": 35},
        {"type": "case", "title": "案例分析专练：2024机考甘特图与时标网络题", "path": "/case-exam", "duration": 40},
        {"type": "wrong", "title": "错题本专项歼灭：重做未掌握错题", "path": "/wrong-questions", "duration": 25},
        {"type": "chapter", "title": "攻坚第4章：信息安全与网络（WPDRRC模型与安全空间）", "path": "/practice?chapter=第4章 信息安全与网络", "duration": 30},
        {"type": "chapter", "title": "攻坚第5章：软件工程与系统架构（敏捷Scrum与测试）", "path": "/practice?chapter=第5章 软件工程与系统架构", "duration": 30},
        {"type": "exam", "title": "阶段全真模拟考：75题机考仿真自测", "path": "/mock-exam", "duration": 60},
        {"type": "chapter", "title": "攻坚第14章：项目风险管理（风险定性/定量与应对策略）", "path": "/practice?chapter=第14章 项目风险管理", "duration": 30},
        {"type": "chapter", "title": "攻坚第7章：项目整体管理（项目章程与CCB变更控制）", "path": "/practice?chapter=第7章 项目整体管理", "duration": 30},
        {"type": "case", "title": "案例分析进阶：典型与非典型完工预测EAC", "path": "/case-exam", "duration": 40},
        {"type": "wrong", "title": "薄弱点突击：执行薄弱知识点组卷刷题", "path": "/practice?mode=weak", "duration": 30},
        {"type": "exam", "title": "考前全真模考卷：冲刺45分及格线", "path": "/mock-exam", "duration": 60},
        {"type": "review", "title": "全考点通关背诵：十大管理领域口诀与必背考点", "path": "/wrong-questions", "duration": 30},
    ]

    for i, t in enumerate(plan_templates):
        day_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
        tasks.append({
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "date": day_date,
            "day_index": i + 1,
            "type": t["type"],
            "title": t["title"],
            "path": t["path"],
            "duration": min(t["duration"], daily_minutes),
            "is_completed": False
        })

    return tasks

@router.get("/me", response_model=PlanOut)
def get_my_study_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user study plan with countdown calculation"""
    plan = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).first()
    now = datetime.now(timezone.utc)

    if not plan:
        # Default exam date: 60 days from now (or next official exam window in May/November)
        default_exam = (now + timedelta(days=60)).strftime("%Y-%m-%d")
        tasks = generate_default_schedule(default_exam, 60)
        plan = StudyPlan(
            user_id=current_user.id,
            exam_date=default_exam,
            daily_minutes=60,
            tasks=tasks
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

    try:
        exam_dt = datetime.strptime(plan.exam_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_rem = max(0, (exam_dt - now).days)
    except Exception:
        days_rem = 60

    return PlanOut(
        id=plan.id,
        exam_date=plan.exam_date,
        days_remaining=days_rem,
        daily_minutes=plan.daily_minutes,
        tasks=plan.tasks or [],
        updated_at=plan.updated_at or now
    )

@router.post("/config", response_model=PlanOut)
def set_study_plan_config(
    cfg_in: PlanConfigIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update exam date and daily minutes, regenerating tasks"""
    plan = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).first()
    tasks = generate_default_schedule(cfg_in.exam_date, cfg_in.daily_minutes)
    now = datetime.now(timezone.utc)

    if not plan:
        plan = StudyPlan(
            user_id=current_user.id,
            exam_date=cfg_in.exam_date,
            daily_minutes=cfg_in.daily_minutes,
            tasks=tasks
        )
        db.add(plan)
    else:
        plan.exam_date = cfg_in.exam_date
        plan.daily_minutes = cfg_in.daily_minutes
        plan.tasks = tasks

    db.commit()
    db.refresh(plan)

    try:
        exam_dt = datetime.strptime(plan.exam_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_rem = max(0, (exam_dt - now).days)
    except Exception:
        days_rem = 60

    return PlanOut(
        id=plan.id,
        exam_date=plan.exam_date,
        days_remaining=days_rem,
        daily_minutes=plan.daily_minutes,
        tasks=plan.tasks or [],
        updated_at=plan.updated_at or now
    )

@router.post("/tasks/{task_id}/toggle")
def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle completion status of a daily mission task"""
    plan = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).first()
    if not plan or not plan.tasks:
        raise HTTPException(status_code=404, detail="学习计划不存在")

    updated = False
    new_state = False
    task_list = list(plan.tasks)
    for t in task_list:
        if t.get("task_id") == task_id:
            t["is_completed"] = not t.get("is_completed", False)
            new_state = t["is_completed"]
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="指定任务不存在")

    plan.tasks = task_list
    db.commit()
    return {"success": True, "task_id": task_id, "is_completed": new_state}
