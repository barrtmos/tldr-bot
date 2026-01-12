import re
import requests
from trafilatura import fetch_url, extract
from youtube_transcript_api import YouTubeTranscriptApi

def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def _yt_id(url: str) -> str:
    m = re.search(r"(v=|/)([0-9A-Za-z_-]{11})", url)
    if not m:
        raise ValueError("Invalid YouTube URL")
    return m.group(2)

def parse(url: str, max_chars: int) -> str:
    if _is_youtube(url):
        vid = _yt_id(url)
        t = YouTubeTranscriptApi.get_transcript(vid)
        text = " ".join(x["text"] for x in t)
    else:
        downloaded = fetch_url(url)
        text = extract(downloaded) or ""

    text = text.strip()
    if not text:
        raise ValueError("Empty text")

    return text[:max_chars]

