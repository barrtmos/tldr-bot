import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from services.ai import ping, list_models, summarize
from services.parser import parse
from cachetools import TTLCache
SUMMARY_CACHE = TTLCache(maxsize=256, ttl=30 * 60)

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class SummarizeIn(BaseModel):
    url: HttpUrl

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": os.getenv("MODEL_NAME"),
        "max_input_chars": int(os.getenv("MAX_INPUT_CHARS", "0")),
    }

@app.get("/models")
def models():
    try:
        return {"models": list_models()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-health")
def ai_health():
    try:
        return {"ai": ping()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
def summarize_url(inp: SummarizeIn):
    t0 = time.perf_counter()
    url = str(inp.url)

    try:
        # cache hit: summary
        if url in SUMMARY_CACHE:
            base = SUMMARY_CACHE[url]
            total_ms = int((time.perf_counter() - t0) * 1000)
            return {
                **base,
                "cache_hit": True,
                "timing_ms": {"total": total_ms, "parse": 0, "ai": 0},
            }

        max_chars = int(os.getenv("MAX_INPUT_CHARS", "50000"))

        t_parse0 = time.perf_counter()
        text = parse(url, max_chars=max_chars)
        parse_ms = int((time.perf_counter() - t_parse0) * 1000)

        t_ai0 = time.perf_counter()
        data = summarize(text)
        ai_ms = int((time.perf_counter() - t_ai0) * 1000)

        base = {"source": url, "chars": len(text), "summary": data}
        SUMMARY_CACHE[url] = base

        total_ms = int((time.perf_counter() - t0) * 1000)
        return {
            **base,
            "cache_hit": False,
            "timing_ms": {"total": total_ms, "parse": parse_ms, "ai": ai_ms},
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





