"""Niche benchmarking analyzer.

Aggregates metrics across all channels in a niche group to produce benchmark
medians and per-channel deviation from those benchmarks.
"""

from statistics import mean, median
from collections import Counter
from datetime import datetime


def benchmark_niche(videos: list[dict], channels: list[dict] | None = None) -> dict:
    """Calculate niche benchmarks and per-channel deviation.

    Args:
        videos: List of video dicts from all channels in the niche.
        channels: Optional list of channel dicts for subscriber info.

    Returns:
        Dict with 'niche_medians', 'channel_benchmarks', and 'channel_deviations'.
    """
    if not videos:
        return {"niche_medians": {}, "channel_benchmarks": [], "channel_deviations": []}

    # Group videos by channel
    by_channel: dict[str, list[dict]] = {}
    for v in videos:
        ch_id = v.get("channel_id", "unknown")
        by_channel.setdefault(ch_id, []).append(v)

    # Build channel lookup for subscriber counts
    channel_info = {}
    if channels:
        for ch in channels:
            channel_info[ch["id"]] = ch

    # Niche-wide metrics
    all_views = [v.get("view_count", 0) or 0 for v in videos]
    all_likes = [v.get("like_count", 0) or 0 for v in videos]
    all_comments = [v.get("comment_count", 0) or 0 for v in videos]
    all_durations = [v.get("duration", 0) or 0 for v in videos if v.get("duration")]

    niche_medians = {
        "median_views": round(median(all_views)) if all_views else 0,
        "avg_views": round(mean(all_views)) if all_views else 0,
        "median_likes": round(median(all_likes)) if all_likes else 0,
        "median_comments": round(median(all_comments)) if all_comments else 0,
        "avg_duration_seconds": round(mean(all_durations)) if all_durations else 0,
        "total_videos": len(videos),
        "total_channels": len(by_channel),
    }

    # Calculate upload frequency (videos per week) for niche
    upload_frequencies = []
    for ch_id, ch_videos in by_channel.items():
        dates = []
        for v in ch_videos:
            pub = v.get("published_at", "")
            if pub:
                try:
                    dates.append(datetime.fromisoformat(pub))
                except (ValueError, TypeError):
                    pass
        if len(dates) >= 2:
            dates.sort()
            span_days = (dates[-1] - dates[0]).days
            if span_days > 0:
                freq = len(dates) / (span_days / 7)
                upload_frequencies.append(freq)

    if upload_frequencies:
        niche_medians["median_uploads_per_week"] = round(median(upload_frequencies), 2)
        niche_medians["avg_uploads_per_week"] = round(mean(upload_frequencies), 2)
    else:
        niche_medians["median_uploads_per_week"] = 0
        niche_medians["avg_uploads_per_week"] = 0

    # Per-channel benchmarks
    channel_benchmarks = []
    for ch_id, ch_videos in by_channel.items():
        ch_views = [v.get("view_count", 0) or 0 for v in ch_videos]
        ch_likes = [v.get("like_count", 0) or 0 for v in ch_videos]
        ch_comments = [v.get("comment_count", 0) or 0 for v in ch_videos]
        ch_durations = [v.get("duration", 0) or 0 for v in ch_videos if v.get("duration")]

        ch_median_views = median(ch_views) if ch_views else 0
        ch_median_likes = median(ch_likes) if ch_likes else 0
        ch_median_comments = median(ch_comments) if ch_comments else 0

        # Upload frequency for this channel
        dates = []
        for v in ch_videos:
            pub = v.get("published_at", "")
            if pub:
                try:
                    dates.append(datetime.fromisoformat(pub))
                except (ValueError, TypeError):
                    pass

        ch_freq = 0
        if len(dates) >= 2:
            dates.sort()
            span_days = (dates[-1] - dates[0]).days
            if span_days > 0:
                ch_freq = len(dates) / (span_days / 7)

        # Subscriber-to-view ratio
        sub_count = 0
        ch_name = ch_id
        if ch_id in channel_info:
            sub_count = channel_info[ch_id].get("subscriber_count", 0) or 0
            ch_name = channel_info[ch_id].get("name", ch_id)

        sub_view_ratio = ch_median_views / sub_count if sub_count > 0 else 0

        channel_benchmarks.append({
            "channel_id": ch_id,
            "channel_name": ch_name,
            "video_count": len(ch_videos),
            "median_views": round(ch_median_views),
            "avg_views": round(mean(ch_views)) if ch_views else 0,
            "median_likes": round(ch_median_likes),
            "median_comments": round(ch_median_comments),
            "avg_duration_seconds": round(mean(ch_durations)) if ch_durations else 0,
            "uploads_per_week": round(ch_freq, 2),
            "subscriber_count": sub_count,
            "sub_view_ratio": round(sub_view_ratio, 4),
        })

    # Channel deviations from niche medians
    niche_median_views = niche_medians["median_views"]
    channel_deviations = []
    for cb in channel_benchmarks:
        deviation_pct = 0
        if niche_median_views > 0:
            deviation_pct = ((cb["median_views"] - niche_median_views) / niche_median_views) * 100

        channel_deviations.append({
            "channel_id": cb["channel_id"],
            "channel_name": cb["channel_name"],
            "views_deviation_pct": round(deviation_pct, 1),
            "above_or_below": "above" if deviation_pct > 0 else "below",
        })

    channel_benchmarks.sort(key=lambda x: x["median_views"], reverse=True)
    channel_deviations.sort(key=lambda x: x["views_deviation_pct"], reverse=True)

    return {
        "niche_medians": niche_medians,
        "channel_benchmarks": channel_benchmarks,
        "channel_deviations": channel_deviations,
    }
