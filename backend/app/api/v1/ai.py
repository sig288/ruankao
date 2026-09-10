from datetime import datetime, timezone, timedelta
import os
import json
import uuid
import urllib.request
import urllib.error
import ssl
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.wrong_question import WrongQuestion
from app.models.ai_job import AiJob
from app.api.deps import get_current_user

router = APIRouter()

class CreateAiJobIn(BaseModel):
    question_id: Optional[str] = None
    action_type: str  # 'explain' (A1), 'mnemonic' (A2), 'case_breakdown' (A3), 'study_advice' (A4)
    user_prompt: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

class AiJobOut(BaseModel):
    id: str
    action_type: str
    status: str
    response: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    remaining_quota: int

def call_deepseek_api(prompt: str, system_prompt: str) -> Optional[str]:
    """
    Server-side direct call to DeepSeek Chat API.
    Gracefully returns None if DEEPSEEK_API_KEY is not configured or network error occurs.
    """
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        return None

    url = f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[DeepSeek API Call Failed]: {e}")
        return None

def fallback_ai_generation(action_type: str, question: Optional[Question], user_context: Optional[Dict[str, Any]]) -> str:
    """
    High quality offline template generator for 3rd edition syllabus
    when DeepSeek API key is not configured or network request times out.
    """
    if not question:
        return "【AI 备考诊断】建议重点复习软考中项第3版十大项目管理领域（特别是进度关键路径CPM与成本挣值EVM公式）。每天坚持完成 15 道薄弱章节练习，考前 45 分通关稳固！"

    stem = question.stem
    ans = question.correct_answer
    ana = question.analysis or "参考官方教程考点"
    kp = question.knowledge
    ch = question.chapter

    if action_type == "explain":
        return f"""### 💡 AI 学霸白话精讲 · 《{kp}》

**【一句话秒懂核心】**
这道题考查的是 **{ch}** 中的 **{kp}** 核心概念。

**【大白话避坑拆解】**
* **正确选项为 {ans}**：{ana}
* **常见丢分陷阱**：考场上极易混淆概念的相似定义。切记要抓住题干中的关键词（如“规划”、“执行”、“监控”的阶段区别）。

**【考场解题技巧】**
牢记第3版官方教程核心原则，先排除与知识领域生命周期不相符的选项，遇到计算题优先套用标准公式！"""

    elif action_type == "mnemonic":
        return f"""### 🎯 极速通关记忆口诀 · 《{kp}》

**【黄金背诵顺口溜】**
> 📌 **“{ch[:4]}考点明，{kp[:4]}记在心；\n   认准关键抓核心，保过中项四十五！”**

**【考点速记提取】**
* 核心考点：{kp}
* 对应答案：【{ans}】
* 联想助记法：结合项目实际，把输入、输出与工具技术联系起来，理解重于死记硬背！"""

    elif action_type == "case_breakdown":
        return f"""### 📝 案例分析采分点拆解 · 《{kp}》

**【阅卷采分视角】**
1. **关键词命中策略**：软考案例题为踩点给分，阅卷老师主要扫描核心专业术语（如标准步骤、公式代入、计算结果）。
2. **答题规范**：
   - 先亮出结论（如：“项目进度滞后，成本节约”）；
   - 写出推导公式（如：`SV = EV - PV`，`CV = EV - AC`）；
   - 代入数值分步计算，切勿只写一个最终数字。
3. **纠偏万能措施**：进度落后可采用赶工（加班/加人）、快速跟进（串行改并行）、优化工艺流程。"""

    else:
        return f"【AI 备考指导】：{kp} 为第3版教程高频考点，建议翻阅教材对应章节深化理解！"

@router.get("/quota")
def get_daily_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check remaining AI quota for today / custom quota"""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    if current_user.ai_quota is not None:
        used_total = (
            db.query(func.count(AiJob.id))
            .filter(AiJob.user_id == current_user.id)
            .scalar()
        ) or 0
        limit = current_user.ai_quota
        remaining = max(0, limit - used_total)
        return {
            "daily_limit": limit,
            "used_today": used_total,
            "remaining": remaining,
            "has_api_key": bool(settings.DEEPSEEK_API_KEY)
        }
    else:
        used_today = (
            db.query(func.count(AiJob.id))
            .filter(AiJob.user_id == current_user.id, AiJob.created_at >= today_start)
            .scalar()
        ) or 0
        remaining = max(0, settings.AI_DAILY_QUOTA - used_today)
        return {
            "daily_limit": settings.AI_DAILY_QUOTA,
            "used_today": used_today,
            "remaining": remaining,
            "has_api_key": bool(settings.DEEPSEEK_API_KEY)
        }

@router.post("/jobs", response_model=AiJobOut)
def create_ai_job(
    job_in: CreateAiJobIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    P0 Feature: DeepSeek AI Study Assistant
    A1: 错题白话讲解 ('explain')
    A2: 考点记忆口诀 ('mnemonic')
    A3: 案例思路拆解 ('case_breakdown')
    A4: 薄弱点学习建议 ('study_advice')
    """
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    # 1. Check quota
    if current_user.ai_quota is not None:
        used = (
            db.query(func.count(AiJob.id))
            .filter(AiJob.user_id == current_user.id)
            .scalar()
        ) or 0
        if used >= current_user.ai_quota:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"您的专属 AI 伴学配额（共 {current_user.ai_quota} 次）已用完！"
            )
        calc_remaining = max(0, current_user.ai_quota - (used + 1))
    else:
        used_today = (
            db.query(func.count(AiJob.id))
            .filter(AiJob.user_id == current_user.id, AiJob.created_at >= today_start)
            .scalar()
        ) or 0
        if used_today >= settings.AI_DAILY_QUOTA:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"今日 AI 伴学配额已用完（每日上限 {settings.AI_DAILY_QUOTA} 次），明日 00:00 自动刷新！"
            )
        calc_remaining = max(0, settings.AI_DAILY_QUOTA - (used_today + 1))

    # 2. Fetch context question if question_id provided
    question = None
    if job_in.question_id:
        question = db.query(Question).filter(Question.id == job_in.question_id).first()

    # 3. Assemble system and user prompts
    system_prompt = (
        "你是一名资深的计算机技术与软件专业技术资格（软考）中级【系统集成项目管理工程师 第3版】金牌辅导专家。"
        "你的语言生动接地气、逻辑严密、善用大白话和形象生动的比喻，擅长拆解命题陷阱并给出提分秒杀口诀。"
        "请始终使用格式优雅的 GitHub Markdown 格式输出。"
    )

    action_names = {
        "explain": "A1-白话深度精讲",
        "mnemonic": "A2-快速通关口诀",
        "case_breakdown": "A3-案例答题思路拆解",
        "study_advice": "A4-薄弱专项备考建议"
    }

    user_query = ""
    if question:
        opts_str = "\n".join(question.options or [])
        user_query = f"""【考纲章节】：{question.chapter}
【核心知识点】：{question.knowledge}
【题目题干】：{question.stem}
【选项】：
{opts_str}
【标准答案】：{question.correct_answer}
【官方解析】：{question.analysis or '依据第3版官方教程'}

请针对上述题目执行任务：{action_names.get(job_in.action_type, '智能辅导')}。
要求：
1. 语言通俗易懂，大白话击碎晦涩概念；
2. 一针见血点出学员最容易踩坑的陷阱；
3. 如果是口诀，务必押韵、好记、朗朗上口。"""
    else:
        user_query = f"请针对学员当前中项备考情况执行：{action_names.get(job_in.action_type, '智能学习建议')}。补充上下文：{json.dumps(job_in.user_context or {}, ensure_ascii=False)}"

    # 4. Invoke DeepSeek API with graceful fallback
    ai_response = call_deepseek_api(user_query, system_prompt)
    if not ai_response:
        ai_response = fallback_ai_generation(job_in.action_type, question, job_in.user_context)

    # 5. Save AiJob record
    job = AiJob(
        user_id=current_user.id,
        question_id=job_in.question_id,
        action_type=job_in.action_type,
        status="completed",
        prompt=user_query,
        response=ai_response,
        created_at=now
    )
    db.add(job)

    # 6. If it's mnemonic or explain and linked to a wrong question, write back to WrongQuestion
    if question and job_in.question_id:
        wq = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.question_id == question.id
        ).first()
        if wq:
            if job_in.action_type == "mnemonic":
                wq.ai_mnemonic = ai_response
            elif job_in.action_type == "explain":
                wq.agent_explanation = ai_response
            db.add(wq)

    db.commit()
    db.refresh(job)

    remaining_quota = calc_remaining

    return AiJobOut(
        id=job.id,
        action_type=job.action_type,
        status=job.status,
        response=job.response,
        parsed_data=job.parsed_data,
        created_at=job.created_at,
        remaining_quota=remaining_quota
    )

@router.get("/jobs/{job_id}", response_model=AiJobOut)
def get_ai_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of an existing AI job"""
    job = db.query(AiJob).filter(AiJob.id == job_id, AiJob.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AI任务不存在")

    if current_user.ai_quota is not None:
        used_total = db.query(func.count(AiJob.id)).filter(AiJob.user_id == current_user.id).scalar() or 0
        rem = max(0, current_user.ai_quota - used_total)
    else:
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        used_today = db.query(func.count(AiJob.id)).filter(AiJob.user_id == current_user.id, AiJob.created_at >= today_start).scalar() or 0
        rem = max(0, settings.AI_DAILY_QUOTA - used_today)

    return AiJobOut(
        id=job.id,
        action_type=job.action_type,
        status=job.status,
        response=job.response,
        parsed_data=job.parsed_data,
        created_at=job.created_at,
        remaining_quota=rem
    )
