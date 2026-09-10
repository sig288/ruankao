import os
import json
import time
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.core.config import settings

AI_SETTINGS_FILE = Path(settings.DATA_DIR) / "app" / "ai_settings.json"

DEFAULT_SETTINGS = {
    "api_key": "",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "default_daily_quota": 30,
    "global_enabled": True,
    "updated_at": "2026-09-08T12:00:00Z"
}

def mask_api_key(key: str) -> str:
    """Mask api key safely: sk-eeb***89f"""
    if not key:
        return ""
    key = key.strip()
    if len(key) <= 8:
        return "********"
    return f"{key[:6]}***{key[-3:]}"

def load_ai_settings(masked: bool = True) -> Dict[str, Any]:
    """
    Load active AI settings from file or initialize with defaults.
    """
    current = dict(DEFAULT_SETTINGS)
    if settings.DEEPSEEK_API_KEY:
        current["api_key"] = settings.DEEPSEEK_API_KEY
    if settings.DEEPSEEK_BASE_URL:
        current["base_url"] = settings.DEEPSEEK_BASE_URL.rstrip('/')
    if settings.DEEPSEEK_MODEL:
        current["model"] = settings.DEEPSEEK_MODEL
    if settings.AI_DAILY_QUOTA:
        current["default_daily_quota"] = settings.AI_DAILY_QUOTA

    if AI_SETTINGS_FILE.exists():
        try:
            with open(AI_SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("api_key"):
                    current["api_key"] = saved["api_key"]
                if saved.get("base_url"):
                    current["base_url"] = saved["base_url"].rstrip('/')
                if saved.get("model"):
                    current["model"] = saved["model"]
                if saved.get("default_daily_quota"):
                    current["default_daily_quota"] = int(saved["default_daily_quota"])
                if "global_enabled" in saved:
                    current["global_enabled"] = bool(saved["global_enabled"])
                if saved.get("updated_at"):
                    current["updated_at"] = saved["updated_at"]
        except Exception as e:
            print(f"[load_ai_settings] Error reading {AI_SETTINGS_FILE}: {e}")

    result = dict(current)
    if masked:
        result["api_key_masked"] = mask_api_key(result.get("api_key", ""))
        result["api_key"] = result["api_key_masked"]
    return result

def save_ai_settings(new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update AI settings. If api_key contains '***' or is empty, keeps existing key.
    """
    raw_current = load_ai_settings(masked=False)

    api_key_input = str(new_settings.get("api_key", "")).strip()
    if api_key_input and "***" not in api_key_input:
        raw_current["api_key"] = api_key_input

    if "base_url" in new_settings and new_settings["base_url"]:
        raw_current["base_url"] = str(new_settings["base_url"]).strip().rstrip('/')
    if "model" in new_settings and new_settings["model"]:
        raw_current["model"] = str(new_settings["model"]).strip()
    if "default_daily_quota" in new_settings:
        try:
            raw_current["default_daily_quota"] = max(1, int(new_settings["default_daily_quota"]))
        except (ValueError, TypeError):
            pass
    if "global_enabled" in new_settings:
        raw_current["global_enabled"] = bool(new_settings["global_enabled"])

    raw_current["updated_at"] = datetime.now(timezone.utc).isoformat()

    AI_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = AI_SETTINGS_FILE.with_suffix(".tmp")
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(raw_current, f, ensure_ascii=False, indent=2)
    tmp_file.replace(AI_SETTINGS_FILE)

    return load_ai_settings(masked=True)

def get_active_api_key() -> str:
    raw = load_ai_settings(masked=False)
    return raw.get("api_key", "").strip()

def test_deepseek_connectivity() -> Dict[str, Any]:
    """
    Official DeepSeek API test request.
    Endpoint: {base_url}/chat/completions (OpenAI Compatible)
    """
    raw = load_ai_settings(masked=False)
    api_key = raw.get("api_key", "").strip()
    if not api_key:
        return {
            "success": False,
            "latency_ms": 0,
            "message": "未配置 DeepSeek API Key，请先输入 Key 并保存"
        }

    base_url = raw.get("base_url", "https://api.deepseek.com/v1").rstrip('/')
    url = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url
    model = raw.get("model", "deepseek-chat")

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "ping"}
        ],
        "max_tokens": 5,
        "temperature": 0.1
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    start_time = time.perf_counter()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            res_json = json.loads(resp.read().decode("utf-8"))
            content = res_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "success": True,
                "latency_ms": elapsed_ms,
                "model": model,
                "reply": content.strip() or "OK",
                "message": f"连接成功！延迟 {elapsed_ms}ms，模型回应正常。"
            }
    except urllib.error.HTTPError as he:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        err_body = he.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "latency_ms": elapsed_ms,
            "status_code": he.code,
            "message": f"HTTP {he.code} 错误: {err_body[:200]}"
        }
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "success": False,
            "latency_ms": elapsed_ms,
            "message": f"网络连接失败: {str(e)}"
        }

def call_deepseek_api(prompt: str, system_prompt: str, max_tokens: int = 2048) -> Optional[str]:
    """
    Invokes DeepSeek Chat API using active configuration.
    """
    raw = load_ai_settings(masked=False)
    api_key = raw.get("api_key", "").strip()
    if not api_key:
        return None

    base_url = raw.get("base_url", "https://api.deepseek.com/v1").rstrip('/')
    url = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url
    model = raw.get("model", "deepseek-chat")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
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
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[DeepSeek API Call Failed]: {e}")
        return None
