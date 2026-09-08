import os
import csv
import io
import json
import uuid
import mimetypes
from urllib.parse import quote
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.material import Material
from app.api.deps import get_current_user

router = APIRouter()

class MaterialOut(BaseModel):
    id: str
    title: str
    file_type: str
    category: str
    chapter: Optional[str] = None
    domain: Optional[str] = None
    file_size: int
    converted_question_count: int
    created_at: Any
    is_public: bool = False
    is_recommended: bool = False
    sort_order: int = 0
    description: Optional[str] = None
    year: Optional[str] = None
    download_url: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[MaterialOut])
def list_materials(
    scope: str = Query("public", description="查询范围：public (官方精选), private (私有资料), all (全部)"),
    category: Optional[str] = Query(None, description="分类筛选"),
    chapter: Optional[str] = Query(None, description="章节筛选"),
    year: Optional[str] = Query(None, description="年份筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取资料清单：
    - scope='public': 平台官方精选备考资料（思维导图、三色笔记、口诀表、机考指南、真题等）
    - scope='private': 当前用户自己上传的私有资料
    - scope='all': 两者合集
    """
    query = db.query(Material)
    if scope == "public":
        query = query.filter(Material.is_public == True)
    elif scope == "private":
        query = query.filter(Material.user_id == current_user.id, Material.is_public == False)
    else:
        query = query.filter(or_(Material.is_public == True, Material.user_id == current_user.id))

    if category:
        query = query.filter(Material.category == category)
    if chapter:
        query = query.filter(Material.chapter == chapter)
    if year:
        query = query.filter(Material.year == year)

    materials = query.order_by(
        Material.is_recommended.desc(),
        Material.sort_order.asc(),
        Material.created_at.desc()
    ).all()
    return materials


@router.post("", response_model=MaterialOut)
async def upload_material(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: str = Form("教材"),  # '教材', '口诀', '案例', '真题', '笔记'
    chapter: Optional[str] = Form(None),
    domain: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    P1 Feature: M1 Upload user's private study material
    Supported formats: PDF, DOCX, PNG, JPG, CSV, JSON, TXT
    Max size: 50MB
    """
    # 1. Determine file extension
    orig_name = file.filename or "upload"
    ext = os.path.splitext(orig_name)[1].lower().lstrip(".")
    allowed_exts = ["pdf", "doc", "docx", "png", "jpg", "jpeg", "csv", "json", "txt", "apkg"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式（支持：{', '.join(allowed_exts)}）"
        )

    # 2. Read content & check size (< 50MB)
    content = await file.read()
    file_size = len(content)
    if file_size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过 50MB 限制"
        )

    # 3. Save to disk in user directory
    user_storage_dir = os.path.join(settings.MATERIALS_DIR, current_user.id)
    os.makedirs(user_storage_dir, exist_ok=True)
    
    file_id = f"mat_{uuid.uuid4().hex[:12]}"
    saved_filename = f"{file_id}.{ext}"
    saved_path = os.path.join(user_storage_dir, saved_filename)

    with open(saved_path, "wb") as f:
        f.write(content)

    mat_title = title.strip() if title else orig_name

    # 4. Save record
    mat = Material(
        id=file_id,
        user_id=current_user.id,
        title=mat_title,
        file_type=ext,
        category=category,
        chapter=chapter,
        domain=domain,
        file_path=saved_path,
        file_size=file_size,
        converted_question_count=0
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)

    return mat

@router.delete("/{id}")
def delete_material(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user study material and its disk file"""
    mat = db.query(Material).filter(Material.id == id, Material.user_id == current_user.id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="资料不存在或无权访问")

    # Remove file from disk
    if os.path.exists(mat.file_path):
        try:
            os.remove(mat.file_path)
        except Exception:
            pass

    db.delete(mat)
    db.commit()
    return {"success": True, "message": "资料已安全删除"}

@router.get("/manifest/stats")
def get_manifest_stats(
    current_user: User = Depends(get_current_user)
):
    """
    获取全量资料库统计与层级导航元数据（涵盖 460+ 文件）
    """
    manifest_candidates = [
        os.path.join(settings.DATA_DIR, "materials", "materials_manifest.json"),
        os.path.join(os.path.dirname(settings.DATA_DIR), "backend", "data", "materials", "materials_manifest.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "materials", "materials_manifest.json"),
        "backend/data/materials/materials_manifest.json"
    ]
    for p in manifest_candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                by_category = {}
                by_year = {}
                total_size = 0
                for item in data:
                    cat = item.get("category", "其他")
                    by_category[cat] = by_category.get(cat, 0) + 1
                    yr = item.get("year", "未知")
                    by_year[yr] = by_year.get(yr, 0) + 1
                    total_size += item.get("file_size", 0)

                return {
                    "total_files": len(data),
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "by_category": by_category,
                    "by_year": by_year,
                    "categories": list(by_category.keys())
                }
            except Exception:
                pass

    return {"total_files": 0, "total_size_mb": 0, "by_category": {}, "by_year": {}}

@router.get("/{id}/file")
def get_material_file(
    id: str,
    inline: bool = Query(False, description="是否在线预览（True为inline，False为attachment下载）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    下载或在线预览资料底层文件（PDF、XLS、图片等）
    """
    mat = db.query(Material).filter(Material.id == id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="资料不存在")

    if not mat.is_public and mat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该私有资料")

    if not os.path.exists(mat.file_path):
        raise HTTPException(status_code=404, detail="底层物理文件不存在")

    content_type, _ = mimetypes.guess_type(mat.file_path)
    if not content_type:
        content_type = "application/octet-stream"

    filename = os.path.basename(mat.file_path)
    encoded_filename = quote(filename)

    headers = {}
    if inline:
        headers["Content-Disposition"] = f"inline; filename*=UTF-8''{encoded_filename}"
    else:
        headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return FileResponse(
        path=mat.file_path,
        media_type=content_type,
        headers=headers
    )


@router.post("/{id}/convert-questions")
def convert_material_to_questions(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    P1 Feature: M2 Material to Practice Bridge
    Converts CSV / JSON material directly into playable practice questions in the bank.
    """
    mat = db.query(Material).filter(Material.id == id, Material.user_id == current_user.id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="资料不存在")

    if not os.path.exists(mat.file_path):
        raise HTTPException(status_code=404, detail="底层文件丢失")

    count = 0
    if mat.file_type == "csv":
        with open(mat.file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stem = row.get("stem") or row.get("题干") or ""
                ans = row.get("correct_answer") or row.get("答案") or ""
                if not stem or not ans:
                    continue
                opts = []
                for k in ["A", "B", "C", "D"]:
                    v = row.get(f"option_{k.lower()}") or row.get(k) or ""
                    if v:
                        opts.append(f"{k}. {v.strip()}")
                
                ch = row.get("chapter") or row.get("章节") or mat.chapter or "第7章 项目整体管理"
                kp = row.get("knowledge") or row.get("考点") or "自有资料考点"

                q = Question(
                    subject="basic",
                    chapter=ch,
                    knowledge=kp,
                    stem=stem.strip(),
                    options=opts if len(opts) >= 2 else None,
                    correct_answer=ans.strip(),
                    analysis=row.get("analysis") or row.get("解析") or f"来自学员私有资料：《{mat.title}》",
                    source=f"私有资料·{mat.title[:12]}"
                )
                db.add(q)
                count += 1

    elif mat.file_type == "json":
        with open(mat.file_path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        stem = item.get("stem")
                        ans = item.get("correct_answer")
                        if not stem or not ans:
                            continue
                        q = Question(
                            subject=item.get("subject", "basic"),
                            chapter=item.get("chapter") or mat.chapter or "第7章 项目整体管理",
                            knowledge=item.get("knowledge", "自有资料考点"),
                            stem=stem,
                            options=item.get("options"),
                            correct_answer=ans,
                            analysis=item.get("analysis") or f"来自学员私有资料：《{mat.title}》",
                            rubrics=item.get("rubrics"),
                            source=f"私有资料·{mat.title[:12]}"
                        )
                        db.add(q)
                        count += 1
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"JSON 解析失败: {e}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前仅支持 CSV/JSON 题库格式一键导入为刷题，PDF/Word 智能切片出题将在下一期上线"
        )

    mat.converted_question_count += count
    db.commit()

    return {
        "success": True,
        "converted_count": count,
        "message": f"成功将《{mat.title}》转化为 {count} 道可刷题目！"
    }
