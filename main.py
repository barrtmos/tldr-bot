import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from services.ai import ping, list_models, summarize
from services.parser import parse

load_dotenv()

app = FastAPI()

class SummarizeIn(BaseModel):
    url: HttpUrl

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
    try:
        max_chars = int(os.getenv("MAX_INPUT_CHARS", "50000"))
        text = parse(str(inp.url), max_chars=max_chars)
        summary = summarize(text)
        return {"source": str(inp.url), "chars": len(text), "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




