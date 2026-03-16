"""Video metadata fetcher using yt-dlp."""

import json
import subprocess
import time
from datetime import datetime

DEFAULT_DELAY = 1.5
DEFAULT_MAX_VIDEOS = 200


def parse_video_metadata(raw: dict) -> dict:
    """Parse yt-dlp JSON output into our video schema."""
    tags = raw.get("tags") or []
    upload_date = raw.get("upload_date", "")
    published_at = ""
    if upload_date and len(upload_date) == 8:
        published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

    return {
        "id": raw.get("id", ""),
        "channel_id": raw.get("channel_id", ""),
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "tags": json.dumps(tags),
        "category": (raw.get("categories") or [""])[0],
        "duration": raw.get("duration", 0),
        "view_count": raw.get("view_count", 0),
        "like_count": raw.get("like_count", 0),
        "comment_count": raw.get("comment_count", 0),
        "published_at": published_at,
        "thumbnail_url": raw.get("thumbnail", ""),
        "language": raw.get("language", ""),
        "fetched_at": datetime.now().isoformat(),
        "has_transcript": 0,
    }


def fetch_video_metadata(video_id: str) -> dict | None:
    """Fetch metadata for a single video using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download",
             f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        raw = json.loads(result.stdout)
        return parse_video_metadata(raw)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def fetch_channel_videos(channel_id: str, max_videos: int = DEFAULT_MAX_VIDEOS,
                         delay: float = DEFAULT_DELAY, progress_callback=None) -> list[dict]:
    """Fetch metadata for all videos in a channel using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", "--flat-playlist",
             f"https://www.youtube.com/channel/{channel_id}/videos"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return []

        video_ids = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                vid = data.get("id", "")
                if vid:
                    video_ids.append(vid)
            except json.JSONDecodeError:
                continue

        video_ids = video_ids[:max_videos]
        videos = []
        for i, vid in enumerate(video_ids):
            meta = fetch_video_metadata(vid)
            if meta:
                videos.append(meta)
            if progress_callback:
                progress_callback(i + 1, len(video_ids))
            if i < len(video_ids) - 1:
                time.sleep(delay)
        return videos
    except subprocess.TimeoutExpired:
        return []
