# AI Summarizer
**Turn long links into clear meaning.**

Mi Summarizer is a lightweight AI-powered demo that takes a URL (article or YouTube video) and returns a clean, structured summary — title, bullet points, key takeaway, and tags — with transparent timing.

*Built as a proof-of-concept core, not a full product.*

---

## What it does
* **Paste a link** → get the essence
* **Extracts** main content from web pages
* **Reads** YouTube subtitles (if available)
* **Summarizes** with Gemini AI
* **Returns** structured JSON, not just text
* **Shows** how long parsing and AI took
* **Uses** in-memory caching for instant повторные запросы

---

## Supported sources
* **Articles & web pages** (news, blogs, posts)
* **YouTube videos** (via captions)

> **Note:** Not guaranteed to work with dynamic/SPAs, paywalls, or heavily scripted sites.

---

## Output example

```json
{
  "title": "Why AI Summaries Matter",
  "bullets": [
    "AI can reduce information overload",
    "Summaries improve decision speed",
    "Structured output is key for UX"
  ],
  "takeaway": "Summarization is becoming a core interface, not a feature.",
  "tags": ["ai", "summary", "productivity"]
}
```

---

## How it works
1. **URL**
2. ↓ **Content extraction** (web / YouTube)
3. ↓ **Text cleanup + limits**
4. ↓ **Gemini AI**
5. ↓ **Structured summary + timing**

---

## Interface
* `/` — minimal dark UI (paste link → result)
* `/summarize` — JSON API
* `/docs` — Swagger (dev/debug only)

*UI is intentionally simple and framework-free.*

---

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add your GEMINI_API_KEY in .env

python3 -m uvicorn main:app --reload
```

**Open:**
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Environment variables

```env
GEMINI_API_KEY=your_key
MODEL_NAME=models/gemini-2.5-flash
MAX_INPUT_CHARS=50000
REQUEST_TIMEOUT_SEC=20
```

---

## Caching & performance
* **In-memory cache (RAM)**
* Caches both extracted text and final summary
* **TTL:** ~30 minutes
* Cache resets on server restart

*This keeps the demo fast and avoids unnecessary AI calls.*

---

## Demo limitations
* Single URL per request
* No auth, no DB, no queue
* Not production-ready
* Meant to showcase the core summarization pipeline

---

## Why this exists
Mi Summarizer is a clean starting point for:
* Building a real summarization product
* Testing AI summarization quality
* Plugging into a frontend, extension, or API client

---

## Roadmap (ideas)
* Source detection & better extraction
* Language auto-detection
* History / saved summaries
* Browser extension
* Production caching (Redis)

---

## License
**MIT** (or choose your own)
