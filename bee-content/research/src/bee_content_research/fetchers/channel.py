"""Channel metadata fetcher using scrapetube and yt-dlp."""

import json
import subprocess
from datetime import datetime


def parse_channel_metadata(raw: dict, discovered_via: str = "manual") -> dict:
    """Parse yt-dlp or scrapetube output into our channel schema."""
    return {
        "id": raw.get("channel_id") or raw.get("id", ""),
        "name": raw.get("channel") or raw.get("uploader", ""),
        "handle": raw.get("uploader_id", ""),
        "subscriber_count": raw.get("channel_follower_count", 0),
        "video_count": raw.get("video_count"),
        "view_count": raw.get("view_count"),
        "country": raw.get("country", ""),
        "language": raw.get("language", ""),
        "description": raw.get("description", ""),
        "thumbnail_url": raw.get("thumbnail", ""),
        "fetched_at": datetime.now().isoformat(),
        "discovered_via": discovered_via,
    }


def fetch_channel_metadata(channel_url: str, discovered_via: str = "manual") -> dict | None:
    """Fetch channel metadata using yt-dlp. Accepts URL, @handle, or channel ID."""
    if channel_url.startswith("@"):
        channel_url = f"https://www.youtube.com/{channel_url}"
    elif not channel_url.startswith("http"):
        channel_url = f"https://www.youtube.com/channel/{channel_url}"

    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", "--playlist-items", "1",
             f"{channel_url}/videos"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        raw = json.loads(result.stdout.split("\n")[0])
        return parse_channel_metadata(raw, discovered_via=discovered_via)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError):
        return None


def list_channel_video_ids(channel_url: str, max_videos: int = 200) -> list[str]:
    """List all video IDs for a channel using scrapetube."""
    import scrapetube

    if channel_url.startswith("@"):
        channel_url = channel_url.lstrip("@")
        videos = scrapetube.get_channel(channel_username=channel_url, limit=max_videos)
    elif channel_url.startswith("UC"):
        videos = scrapetube.get_channel(channel_id=channel_url, limit=max_videos)
    else:
        # Try to extract channel ID from URL
        if "/channel/" in channel_url:
            ch_id = channel_url.split("/channel/")[1].split("/")[0]
            videos = scrapetube.get_channel(channel_id=ch_id, limit=max_videos)
        elif "/@" in channel_url:
            username = channel_url.split("/@")[1].split("/")[0]
            videos = scrapetube.get_channel(channel_username=username, limit=max_videos)
        else:
            return []

    return [v["videoId"] for v in videos]
