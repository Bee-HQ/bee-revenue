"""Engagement ratio analysis analyzer.

Calculates per-video engagement metrics: like/view %, comment/view %,
like/comment ratio. Ranks by weighted composite engagement score and
identifies "high engagement, low views" hidden gems.
"""

from statistics import mean, median


def analyze_engagement(videos: list[dict]) -> dict:
    """Analyze engagement ratios across videos.

    Args:
        videos: List of video dicts with view_count, like_count, comment_count.

    Returns:
        Dict with 'videos' (scored and sorted), 'summary', and 'hidden_gems'.
    """
    if not videos:
        return {"videos": [], "summary": {}, "hidden_gems": []}

    scored = []
    for v in videos:
        views = v.get("view_count", 0) or 0
        likes = v.get("like_count", 0) or 0
        comments = v.get("comment_count", 0) or 0

        if views == 0:
            continue

        like_rate = likes / views * 100  # percentage
        comment_rate = comments / views * 100  # percentage
        like_comment_ratio = likes / comments if comments > 0 else 0

        # Weighted composite engagement score
        # Like rate contributes most, comments are rarer and thus weighted higher
        composite_score = (like_rate * 0.6) + (comment_rate * 10 * 0.4)

        scored.append({
            "id": v.get("id", ""),
            "channel_id": v.get("channel_id", ""),
            "title": v.get("title", ""),
            "view_count": views,
            "like_count": likes,
            "comment_count": comments,
            "like_rate": round(like_rate, 3),
            "comment_rate": round(comment_rate, 4),
            "like_comment_ratio": round(like_comment_ratio, 1),
            "composite_score": round(composite_score, 3),
            "published_at": v.get("published_at", ""),
        })

    if not scored:
        return {"videos": [], "summary": {}, "hidden_gems": []}

    # Sort by composite score
    scored.sort(key=lambda x: x["composite_score"], reverse=True)

    # Summary statistics
    all_like_rates = [s["like_rate"] for s in scored]
    all_comment_rates = [s["comment_rate"] for s in scored]
    all_composite = [s["composite_score"] for s in scored]
    all_views = [s["view_count"] for s in scored]

    summary = {
        "total_videos": len(scored),
        "avg_like_rate": round(mean(all_like_rates), 3),
        "median_like_rate": round(median(all_like_rates), 3),
        "avg_comment_rate": round(mean(all_comment_rates), 4),
        "median_comment_rate": round(median(all_comment_rates), 4),
        "avg_composite_score": round(mean(all_composite), 3),
        "median_composite_score": round(median(all_composite), 3),
    }

    # Hidden gems: high engagement but below-median views
    median_views = median(all_views)
    median_composite = median(all_composite)

    hidden_gems = [
        s for s in scored
        if s["view_count"] < median_views and s["composite_score"] > median_composite
    ]
    hidden_gems.sort(key=lambda x: x["composite_score"], reverse=True)

    return {
        "videos": scored,
        "summary": summary,
        "hidden_gems": hidden_gems[:20],
    }
