"""Discovery service: channel discovery, fetching, and data ingestion."""

from ..storage.db import Database
from ..fetchers.channel import fetch_channel_metadata, list_channel_video_ids
from ..fetchers.video import fetch_channel_videos
from ..fetchers.search import search_channels
from ..fetchers.snowball import discover_related_channels


def discover(db: Database, keyword: str, max_results: int = 20) -> list[dict]:
    """Discover channels by keyword search and store them."""
    results = search_channels(keyword, max_results)
    channels = []
    for r in results:
        ch = fetch_channel_metadata(r["id"], discovered_via=f"keyword:{keyword}")
        if ch:
            db.upsert_channel(ch)
            channels.append(ch)
    return channels


def add_channel(db: Database, url: str) -> dict | None:
    """Manually add a channel by URL or @handle."""
    ch = fetch_channel_metadata(url, discovered_via="manual")
    if ch:
        db.upsert_channel(ch)
    return ch


def snowball(db: Database, channel_url: str, max_results: int = 10) -> list[dict]:
    """Discover related channels via snowball method."""
    channels = discover_related_channels(channel_url, max_results)
    for ch in channels:
        db.upsert_channel(ch)
    return channels


def fetch_data(db: Database, target: str, include_transcripts: bool = False,
               max_videos: int = 200, delay: float = 1.5, force: bool = False,
               progress_callback=None) -> dict:
    """Fetch video data for a channel or niche group.

    Uses skip-and-warn model: if one channel fails, continues with remaining.
    Respects TTL unless force=True.
    """
    channel_ids = db.resolve_target(target)
    if not channel_ids:
        return {"error": f"Target '{target}' not found", "fetched": 0, "skipped": 0,
                "warnings": []}

    results = {"fetched": 0, "skipped": 0, "errors": [], "warnings": []}

    for ch_id in channel_ids:
        ch = db.get_channel(ch_id)
        if ch and not force and not db.is_stale(ch.get("fetched_at")):
            results["skipped"] += 1
            continue

        try:
            videos = fetch_channel_videos(ch_id, max_videos=max_videos,
                                          delay=delay, progress_callback=progress_callback)
            if videos:
                db.upsert_videos(videos)
                results["fetched"] += len(videos)
            else:
                results["warnings"].append(f"No videos fetched for {ch_id}")
        except Exception as e:
            results["warnings"].append(f"Error fetching {ch_id}: {e}")

        if include_transcripts:
            from ..fetchers.transcript import fetch_transcript
            existing_videos = db.get_videos_for_channel(ch_id)
            for v in existing_videos:
                if not v.get("has_transcript"):
                    try:
                        t = fetch_transcript(v["id"])
                        if t:
                            db.upsert_transcript(v["id"], t["language"], t["text"])
                        else:
                            results["warnings"].append(f"No transcript for {v['id']}")
                    except Exception as e:
                        results["warnings"].append(f"Transcript error for {v['id']}: {e}")

    return results
