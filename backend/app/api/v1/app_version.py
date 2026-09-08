import os
import json
import logging
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import FileResponse

logger = logging.getLogger("ruankao")
router = APIRouter()

# Data directory resolution
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent.parent.parent
DATA_APP_DIR = BACKEND_DIR / "data" / "app"
VERSION_INFO_PATH = DATA_APP_DIR / "version_info.json"

DEFAULT_VERSION_INFO = {
    "latest_version": "3.2.1",
    "latest_version_code": 321,
    "min_supported_version_code": 300,
    "is_force_update": False,
    "title": "软考中项助手 v3.2.0 体验升级",
    "release_notes": [
        "【系统返回键】非首页返回上一页，首页再按一次退出；请安装 3.2.1 客户端后生效",
        "【备考文库在线阅读】PDF 用应用内阅读器翻页，不再出现白屏",
        "【墨纸备考界面】顶栏/底栏为通知栏和手势条留出安全区",
        "【题库扩充】资料库真题 + 自编题合计约 590 道"
    ],
    "apk_filename": "ruankao-v3.2.0.apk",
    "apk_size_bytes": 16078350,
    "apk_size_human": "15.3 MB",
    "release_date": "2026-09-08",
    "download_url": "https://122.51.95.218/api/v1/app/download-apk"
}

def _absolute_download_url(url: str) -> str:
    if url.startswith("/"):
        return f"https://122.51.95.218{url}"
    return url


def load_version_info() -> dict:
    data = DEFAULT_VERSION_INFO.copy()
    if VERSION_INFO_PATH.exists():
        try:
            with open(VERSION_INFO_PATH, "r", encoding="utf-8") as f:
                data.update(json.load(f))
        except Exception as e:
            logger.error(f"Error loading version_info.json: {e}")
    data["download_url"] = _absolute_download_url(
        data.get("download_url") or "/api/v1/app/download-apk"
    )
    return data

def find_apk_file() -> Optional[Path]:
    """Find the latest APK file in candidate directories."""
    info = load_version_info()
    target_name = info.get("apk_filename", "ruankao-v3.2.0.apk")
    
    candidates = [
        DATA_APP_DIR / target_name,
        DATA_APP_DIR / "ruankao-v3.2.0.apk",
        DATA_APP_DIR / "ruankao-v3.1.0.apk",
        BACKEND_DIR.parent / "frontend" / "public" / target_name,
        BACKEND_DIR.parent / "frontend" / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk",
        Path("/app/data/app") / target_name,
        Path("/app/data/app/ruankao-v3.2.0.apk"),
        Path("/app/data/app/ruankao-v3.1.0.apk")
    ]
    for p in candidates:
        if p.exists() and p.is_file() and p.stat().st_size > 0:
            return p
            
    # Also check if any .apk exists in DATA_APP_DIR
    if DATA_APP_DIR.exists():
        for p in DATA_APP_DIR.glob("*.apk"):
            if p.is_file() and p.stat().st_size > 0:
                return p
                
    return None

@router.get("/latest-info", summary="获取最新App版本详情")
def get_latest_app_info():
    info = load_version_info()
    apk_path = find_apk_file()
    if apk_path and apk_path.exists():
        size_bytes = apk_path.stat().st_size
        info["apk_size_bytes"] = size_bytes
        info["apk_size_human"] = f"{size_bytes / (1024 * 1024):.1f} MB"
        info["apk_available"] = True
    else:
        info["apk_available"] = False
    return info

@router.get("/check-update", summary="检查App更新")
def check_app_update(
    client_version: Optional[str] = Query(None, description="客户端版本名，如 3.0.0"),
    client_version_code: Optional[int] = Query(0, description="客户端版本号，如 300"),
    platform: Optional[str] = Query("android", description="客户端操作系统平台，如 android")
):
    info = load_version_info()
    apk_path = find_apk_file()
    if apk_path and apk_path.exists():
        size_bytes = apk_path.stat().st_size
        info["apk_size_bytes"] = size_bytes
        info["apk_size_human"] = f"{size_bytes / (1024 * 1024):.1f} MB"
        info["apk_available"] = True
    else:
        info["apk_available"] = False
        
    latest_code = info.get("latest_version_code", 310)
    min_supported_code = info.get("min_supported_version_code", 300)
    
    has_update = (client_version_code < latest_code)
    is_force_update = info.get("is_force_update", False) or (client_version_code < min_supported_code)

    # 3.2.0 及更早的壳把热更新做成「清缓存 + reload 本地包」。
    # 本地包版本号仍是 320，会再次弹窗并刷新，形成死循环。对这些客户端不再下发 has_update。
    if client_version_code and client_version_code <= 320:
        has_update = False
        is_force_update = False

    download_url = info.get("download_url", "/api/v1/app/download-apk")
    if isinstance(download_url, str) and download_url.startswith("/"):
        download_url = f"https://122.51.95.218{download_url}"
    
    return {
        "has_update": has_update,
        "is_force_update": is_force_update,
        "client_version": client_version,
        "client_version_code": client_version_code,
        "latest_version": info.get("latest_version", "3.1.0"),
        "latest_version_code": latest_code,
        "title": info.get("title", f"发现新版本 v{info.get('latest_version')}"),
        "release_notes": info.get("release_notes", []),
        "apk_size_human": info.get("apk_size_human", "15.0 MB"),
        "apk_size_bytes": info.get("apk_size_bytes", 0),
        "release_date": info.get("release_date", "2026-09-07"),
        "download_url": download_url,
        "apk_available": info.get("apk_available", False)
    }

@router.get("/download-apk", summary="下载最新版Android APK")
def download_apk():
    apk_path = find_apk_file()
    if not apk_path or not apk_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="APK文件正在构建或暂未发布，请稍后刷新重试"
        )
        
    info = load_version_info()
    download_filename = info.get("apk_filename", f"ruankao-v{info.get('latest_version', '3.1.0')}.apk")
    
    return FileResponse(
        path=str(apk_path),
        filename=download_filename,
        media_type="application/vnd.android.package-archive"
    )
