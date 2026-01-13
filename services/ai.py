import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import json
import re

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

def _get(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Missing env var: {key}")
    return v

def _client():
    return genai.Client(api_key=_get("GEMINI_API_KEY"))

def list_models(limit: int = 30):
    c = _client()
    out = []
    for m in c.models.list():
        out.append(getattr(m, "name", str(m)))
        if len(out) >= limit:
            break
    return out

def ping() -> str:
    model = os.getenv("MODEL_NAME", "").strip()
    if not model:
        raise RuntimeError("MODEL_NAME is empty. Set it to an existing model from /models")
    c = _client()
    resp = c.models.generate_content(model=model, contents="Ответь одним словом: ok")
    return (getattr(resp, "text", "") or "").strip() or "no_text"

def summarize(text: str) -> dict:
    model = os.getenv("MODEL_NAME", "").strip()
    if not model:
        raise RuntimeError("MODEL_NAME is empty. Set it to an existing model from /models")

    max_chars = int(os.getenv("MAX_INPUT_CHARS", "50000"))
    text = (text or "").strip()[:max_chars]

    prompt = f"""
Ты отвечаешь ТОЛЬКО на русском.
Верни ТОЛЬКО валидный JSON. Без markdown, без ```.

Схема:
{{
  "title": "строка",
  "bullets": ["...", "..."],   // 5-7 пунктов
  "takeaway": "строка",        // 1 строка
  "tags": ["...", "..."]       // 3-8 тегов
}}

Текст:
{text}
""".strip()

    c = _client()
    resp = c.models.generate_content(model=model, contents=prompt)
    raw = (getattr(resp, "text", "") or "").strip()

    # 1) пробуем как есть
    for candidate in (raw,):
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 2) вырезаем первый JSON-объект из текста
    m = re.search(r"\{.*\}", raw, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # 3) деградация
    return {
        "title": "",
        "bullets": [raw][:7],
        "takeaway": "",
        "tags": [],
    }





