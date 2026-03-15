"""Snowball discovery: find related channels via collaborations and search expansion."""

import json
import re
import time

from .channel import fetch_channel_metadata, list_channel_video_ids
from .video import fetch_video_metadata
from .search import search_channels


def discover_related_channels(channel_url: str, max_results: int = 10,
                              delay: float = 1.5) -> list[dict]:
    """Discover related channels via featured channels, collaborations, and search expansion.

    Strategies:
    1. Scan video descriptions for @mentions of other channels
    2. Search expansion using channel's top tags/keywords
    """
    discovered = {}

    # Strategy 1: Scan video descriptions for @mentions
    try:
        video_ids = list_channel_video_ids(channel_url, max_videos=20)
    except Exception:
        video_ids = []

    for vid in video_ids[:10]:
        if len(discovered) >= max_results:
            break
        try:
            meta = fetch_video_metadata(vid)
            if meta and meta.get("description"):
                handles = re.findall(r'@([\w.-]+)', meta["description"])
                for handle in handles:
                    if handle not in discovered and len(discovered) < max_results:
                        ch = fetch_channel_metadata(
                            f"@{handle}",
                            discovered_via=f"snowball:{channel_url}",
                        )
                        if ch and ch.get("id"):
                            discovered[ch["id"]] = ch
            time.sleep(delay)
        except Exception:
            continue

    # Strategy 2: Search expansion using channel's top tags/keywords
    if len(discovered) < max_results and video_ids:
        try:
            sample_video = fetch_video_metadata(video_ids[0])
            if sample_video:
                tags = json.loads(sample_video.get("tags", "[]"))
                if tags:
                    keyword = tags[0]
                    if keyword:
                        results = search_channels(keyword, max_results=max_results)
                        for r in results:
                            if r["id"] not in discovered and len(discovered) < max_results:
                                ch = fetch_channel_metadata(
                                    r["id"],
                                    discovered_via=f"snowball:{channel_url}",
                                )
                                if ch:
                                    discovered[ch["id"]] = ch
        except Exception:
            pass

    return list(discovered.values())
