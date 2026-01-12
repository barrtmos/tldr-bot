import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

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

def summarize(text: str) -> str:
    model = os.getenv("MODEL_NAME", "").strip()
    if not model:
        raise RuntimeError("MODEL_NAME is empty. Set it to an existing model from /models")

    max_chars = int(os.getenv("MAX_INPUT_CHARS", "50000"))
    text = (text or "").strip()[:max_chars]

    prompt = (
        "Сожми текст в 5-7 буллетов.\n"
        "Потом: 1 строка 'Вывод: ...'.\n"
        "Без воды, без повторов.\n\n"
        "Текст:\n"
        f"{text}"
    )

    c = _client()
    resp = c.models.generate_content(model=model, contents=prompt)
    return (getattr(resp, "text", "") or "").strip() or "no_text"





