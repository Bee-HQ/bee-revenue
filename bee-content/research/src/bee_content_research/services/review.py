"""Review service: orchestrates script review from various input sources.

Handles file reading, YouTube transcript fetching, and delegates
to the reviewer module for LLM-based analysis.
"""

import os
import re

from ..storage.db import Database
from ..reviewers.script_reviewer import review_script, ReviewError


def _extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',  # bare video ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def _is_youtube_url(source: str) -> bool:
    """Check if a string looks like a YouTube URL."""
    return bool(re.search(r'(youtube\.com|youtu\.be)', source))


def _is_file_path(source: str) -> bool:
    """Check if a string looks like a file path."""
    return os.path.exists(source) or source.endswith(('.txt', '.md', '.srt'))


def review_from_file(
    file_path: str,
    metadata: dict | None = None,
) -> dict:
    """Review a script from a file.

    Args:
        file_path: Path to the script file (.txt, .md, etc.)
        metadata: Optional metadata dict.

    Returns:
        Review result dict.
    """
    if not os.path.exists(file_path):
        raise ReviewError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    if not script_text.strip():
        raise ReviewError(f"File is empty: {file_path}")

    return review_script(script_text, metadata)


def review_from_text(
    text: str,
    metadata: dict | None = None,
) -> dict:
    """Review a script from raw text.

    Args:
        text: The script text to review.
        metadata: Optional metadata dict.

    Returns:
        Review result dict.
    """
    return review_script(text, metadata)


def review_from_url(
    db: Database,
    youtube_url: str,
) -> dict:
    """Review a script by fetching its transcript from YouTube.

    Args:
        db: Database instance (for caching, if needed in future).
        youtube_url: YouTube video URL.

    Returns:
        Review result dict.
    """
    from ..fetchers.transcript import fetch_transcript
    from ..fetchers.video import fetch_video_metadata

    video_id = _extract_video_id(youtube_url)
    if not video_id:
        raise ReviewError(f"Could not extract video ID from: {youtube_url}")

    # Fetch transcript
    transcript_data = fetch_transcript(video_id)
    if not transcript_data or not transcript_data.get("text"):
        raise ReviewError(
            f"Could not fetch transcript for video {video_id}. "
            "The video may not have captions available."
        )

    script_text = transcript_data["text"]

    # Fetch video metadata for SEO analysis
    metadata = None
    video_meta = fetch_video_metadata(video_id)
    if video_meta:
        import json
        tags = video_meta.get("tags", "[]")
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = []

        metadata = {
            "title": video_meta.get("title", ""),
            "description": video_meta.get("description", ""),
            "tags": tags,
        }

    return review_script(script_text, metadata)


def review_from_source(
    source: str,
    metadata: dict | None = None,
    db: Database | None = None,
) -> dict:
    """Review a script from any source (file, URL, or raw text).

    Automatically detects the source type and routes to the right handler.

    Args:
        source: File path, YouTube URL, or raw script text.
        metadata: Optional metadata dict.
        db: Database instance (needed for URL sources).

    Returns:
        Review result dict.
    """
    if _is_youtube_url(source):
        if db is None:
            db = Database()
        try:
            return review_from_url(db, source)
        finally:
            if db:
                db.close()

    if _is_file_path(source):
        return review_from_file(source, metadata)

    # Treat as raw text
    return review_from_text(source, metadata)
