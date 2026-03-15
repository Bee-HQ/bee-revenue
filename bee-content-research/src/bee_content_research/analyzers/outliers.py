"""Outlier/viral video detection analyzer.

For each channel, calculates median views per video, then flags videos
exceeding threshold x median. Also flags engagement ratio outliers.
"""

from statistics import median


def find_outliers(videos: list[dict], threshold: float = 2.0) -> dict:
    """Find viral outlier videos that dramatically outperform a channel's average.

    Args:
        videos: List of video dicts with view_count, like_count, comment_count, etc.
        threshold: Multiplier above median to consider a video an outlier (default 2.0).

    Returns:
        Dict with 'outliers' list and 'channel_medians' dict.
    """
    if not videos:
        return {"outliers": [], "channel_medians": {}}

    # Group by channel
    by_channel: dict[str, list[dict]] = {}
    for v in videos:
        ch = v.get("channel_id", "unknown")
        by_channel.setdefault(ch, []).append(v)

    channel_medians = {}
    outliers = []

    for ch_id, ch_videos in by_channel.items():
        views = [v.get("view_count", 0) or 0 for v in ch_videos]
        if not views:
            continue

        med = median(views)
        channel_medians[ch_id] = med

        if med == 0:
            continue

        for v in ch_videos:
            vc = v.get("view_count", 0) or 0
            multiplier = vc / med if med > 0 else 0
            if multiplier >= threshold:
                # Also compute engagement ratios
                like_rate = (v.get("like_count", 0) or 0) / vc if vc > 0 else 0
                comment_rate = (v.get("comment_count", 0) or 0) / vc if vc > 0 else 0

                outliers.append({
                    "id": v["id"],
                    "channel_id": ch_id,
                    "title": v.get("title", ""),
                    "view_count": vc,
                    "like_count": v.get("like_count", 0) or 0,
                    "comment_count": v.get("comment_count", 0) or 0,
                    "multiplier": round(multiplier, 1),
                    "like_rate": round(like_rate * 100, 2),
                    "comment_rate": round(comment_rate * 100, 4),
                    "published_at": v.get("published_at", ""),
                    "tags": v.get("tags", "[]"),
                })

    outliers.sort(key=lambda x: x["multiplier"], reverse=True)
    return {"outliers": outliers, "channel_medians": channel_medians}
