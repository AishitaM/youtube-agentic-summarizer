"""Small helper functions used by the Streamlit webpage."""

import re
from urllib.parse import parse_qs, urlparse


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def normalize_youtube_url(raw_url: str) -> str | None:
    """Validate common YouTube link formats and return one standard URL."""
    value = raw_url.strip()
    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    parsed = urlparse(value)
    host = parsed.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]

    video_id = None

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
                video_id = parts[1]

    if not video_id or not VIDEO_ID_PATTERN.fullmatch(video_id):
        return None

    return f"https://www.youtube.com/watch?v={video_id}"


def build_summary_prompt(summary_style: str, language: str) -> str:
    """Create clear instructions for the AI model."""
    formats = {
        "Quick summary": "Write a short overview followed by 5 key points.",
        "Detailed summary": (
            "Write a detailed overview with section headings, the main arguments, "
            "important examples, and a concise conclusion."
        ),
        "Study notes": (
            "Create easy-to-study notes with a short overview, clear section headings, "
            "important definitions, key points, examples, and 5 takeaway bullets."
        ),
    }

    format_instruction = formats.get(summary_style, formats["Study notes"])
    return f"""
You are a careful video-summary agent.

Inspect the video's spoken content and important visuals. Identify the central topic,
main claims, supporting details, and conclusion. Do not invent information that is not
present in the video. If something is unclear, say that it is unclear.

Output language: {language}
Required format: {format_instruction}
Use clean Markdown and make the result easy to read.
""".strip()
