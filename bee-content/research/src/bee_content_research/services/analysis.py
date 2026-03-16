"""Analysis service: delegates to analyzer modules.

This is a thin orchestration layer that fetches data from storage and passes
it to the appropriate analyzer functions. No analysis logic lives here.
"""

from ..storage.db import Database
from ..analyzers.outliers import find_outliers
from ..analyzers.content_gaps import find_content_gaps
from ..analyzers.titles import analyze_titles as _analyze_titles
from ..analyzers.engagement import analyze_engagement as _analyze_engagement
from ..analyzers.benchmarks import benchmark_niche as _benchmark_niche
from ..analyzers.seo import analyze_seo as _analyze_seo
from ..analyzers.timing import analyze_timing as _analyze_timing
from ..analyzers.regional import analyze_regional as _analyze_regional
from ..fetchers.search import fetch_youtube_suggestions


def _get_videos(db: Database, target: str) -> list[dict]:
    """Get videos for a target (channel ID or group name)."""
    channel_ids = db.resolve_target(target)
    if not channel_ids:
        return []
    videos = []
    for ch_id in channel_ids:
        videos.extend(db.get_videos_for_channel(ch_id))
    return videos


def _get_channels(db: Database, target: str) -> list[dict]:
    """Get channel info for a target."""
    channel_ids = db.resolve_target(target)
    channels = []
    for ch_id in channel_ids:
        ch = db.get_channel(ch_id)
        if ch:
            channels.append(ch)
    return channels


def outliers(db: Database, target: str, threshold: float = 2.0) -> dict:
    """Find viral outlier videos for a target."""
    videos = _get_videos(db, target)
    return find_outliers(videos, threshold)


def content_gaps(db: Database, target: str) -> dict:
    """Find content gaps in a niche group."""
    videos = _get_videos(db, target)
    transcripts = db.get_transcripts_for_group(target) if videos else []

    # Fetch YouTube suggestions based on top topics
    suggestions = []
    if videos:
        # Use most common tags as seed keywords
        import json
        from collections import Counter
        tag_counter: Counter = Counter()
        for v in videos:
            try:
                tags = json.loads(v.get("tags", "[]")) if isinstance(v.get("tags"), str) else []
            except (json.JSONDecodeError, TypeError):
                tags = []
            for tag in tags:
                tag_counter[tag.lower()] += 1

        top_keywords = [tag for tag, _ in tag_counter.most_common(5)]
        for kw in top_keywords[:3]:
            try:
                suggs = fetch_youtube_suggestions(kw)
                suggestions.extend(suggs)
            except Exception:
                pass

    return find_content_gaps(videos, transcripts=transcripts or None,
                             suggestions=suggestions or None)


def titles(db: Database, target: str) -> dict:
    """Analyze title patterns for a target."""
    videos = _get_videos(db, target)
    return _analyze_titles(videos)


def engagement(db: Database, target: str) -> dict:
    """Analyze engagement ratios for a target."""
    videos = _get_videos(db, target)
    return _analyze_engagement(videos)


def benchmarks(db: Database, target: str) -> dict:
    """Calculate niche benchmarks for a target."""
    videos = _get_videos(db, target)
    channels = _get_channels(db, target)
    return _benchmark_niche(videos, channels)


def seo(db: Database, target: str) -> dict:
    """Analyze tags/keywords for a target."""
    videos = _get_videos(db, target)
    return _analyze_seo(videos)


def timing(db: Database, target: str) -> dict:
    """Analyze upload timing patterns for a target."""
    videos = _get_videos(db, target)
    return _analyze_timing(videos)


def compare(db: Database, channel_ids: list[str]) -> dict:
    """Side-by-side comparison of multiple channels.

    For each channel, computes key metrics and highlights where each
    channel outperforms others.
    """
    if len(channel_ids) < 2:
        return {"error": "Need at least 2 channels to compare", "channels": []}

    from statistics import mean, median

    channel_stats = []
    for ch_id in channel_ids:
        ch = db.get_channel(ch_id)
        videos = db.get_videos_for_channel(ch_id)

        if not videos:
            channel_stats.append({
                "channel_id": ch_id,
                "channel_name": ch.get("name", ch_id) if ch else ch_id,
                "video_count": 0,
                "subscriber_count": ch.get("subscriber_count", 0) if ch else 0,
            })
            continue

        views = [v.get("view_count", 0) or 0 for v in videos]
        likes = [v.get("like_count", 0) or 0 for v in videos]
        comments = [v.get("comment_count", 0) or 0 for v in videos]

        total_views = sum(views)
        avg_views = round(mean(views)) if views else 0
        med_views = round(median(views)) if views else 0
        avg_likes = round(mean(likes)) if likes else 0
        avg_comments = round(mean(comments)) if comments else 0

        # Engagement rates
        like_rate = (sum(likes) / total_views * 100) if total_views > 0 else 0
        comment_rate = (sum(comments) / total_views * 100) if total_views > 0 else 0

        # Top tags
        import json
        from collections import Counter
        tag_counter: Counter = Counter()
        for v in videos:
            try:
                tags = json.loads(v.get("tags", "[]")) if isinstance(v.get("tags"), str) else []
            except (json.JSONDecodeError, TypeError):
                tags = []
            for tag in tags:
                tag_counter[tag.lower()] += 1

        channel_stats.append({
            "channel_id": ch_id,
            "channel_name": ch.get("name", ch_id) if ch else ch_id,
            "subscriber_count": ch.get("subscriber_count", 0) if ch else 0,
            "video_count": len(videos),
            "total_views": total_views,
            "avg_views": avg_views,
            "median_views": med_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "like_rate": round(like_rate, 3),
            "comment_rate": round(comment_rate, 4),
            "top_tags": [tag for tag, _ in tag_counter.most_common(10)],
        })

    # Determine winners per metric
    metrics = ["subscriber_count", "total_views", "avg_views", "median_views",
               "like_rate", "comment_rate", "video_count"]
    winners = {}
    for metric in metrics:
        valid = [s for s in channel_stats if s.get(metric) is not None]
        if valid:
            best = max(valid, key=lambda s: s.get(metric, 0))
            winners[metric] = {
                "channel_id": best["channel_id"],
                "channel_name": best["channel_name"],
                "value": best[metric],
            }

    return {
        "channels": channel_stats,
        "winners": winners,
    }


def regional(db: Database, target: str) -> dict:
    """Analyze regional/language distribution for a target."""
    videos = _get_videos(db, target)
    channels = _get_channels(db, target)
    return _analyze_regional(videos, channels)
