import os
import re
import httpx
from cachetools import TTLCache
from trafilatura import extract
from youtube_transcript_api import YouTubeTranscriptApi

CACHE = TTLCache(maxsize=256, ttl=30 * 60)

def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def _yt_id(url: str) -> str:
    m = re.search(r"(v=|/)([0-9A-Za-z_-]{11})", url)
    if not m:
        raise ValueError("Invalid YouTube URL")
    return m.group(2)

def _fetch_html(url: str, timeout: int) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (tldr-bot demo)"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.text

def parse(url: str, max_chars: int) -> str:
    if url in CACHE:
        return CACHE[url]

    timeout = int(os.getenv("REQUEST_TIMEOUT_SEC", "20"))

    if _is_youtube(url):
        vid = _yt_id(url)
        t = YouTubeTranscriptApi.get_transcript(vid, languages=["ru", "en"])
        text = " ".join(x["text"] for x in t)
    else:
        html = _fetch_html(url, timeout=timeout)
        text = extract(html) or ""

    text = (text or "").strip()
    if not text:
        raise ValueError("Empty text")

    text = text[:max_chars]
    CACHE[url] = text
    return text

