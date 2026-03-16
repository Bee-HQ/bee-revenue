"""SEO / tag and keyword analysis analyzer.

Counts tag frequencies, identifies shared vs unique tags, and correlates
tag usage with video performance.
"""

import json
from collections import Counter
from statistics import mean, median


def analyze_seo(videos: list[dict]) -> dict:
    """Analyze tags/keywords and their correlation with performance.

    Args:
        videos: List of video dicts with tags (JSON array string) and view_count.

    Returns:
        Dict with 'tag_frequency', 'tag_performance', 'shared_tags',
        'unique_tags_by_channel', 'recommendations'.
    """
    if not videos:
        return {
            "tag_frequency": [],
            "tag_performance": [],
            "shared_tags": [],
            "unique_tags_by_channel": {},
            "recommendations": [],
        }

    # Parse all tags
    tag_counter: Counter = Counter()
    tag_views: dict[str, list[int]] = {}
    channel_tags: dict[str, set] = {}

    for v in videos:
        tags_raw = v.get("tags", "[]")
        try:
            tags = json.loads(tags_raw) if isinstance(tags_raw, str) else (tags_raw or [])
        except (json.JSONDecodeError, TypeError):
            tags = []

        views = v.get("view_count", 0) or 0
        ch_id = v.get("channel_id", "unknown")
        channel_tags.setdefault(ch_id, set())

        for tag in tags:
            tag_lower = tag.lower().strip()
            if not tag_lower:
                continue
            tag_counter[tag_lower] += 1
            tag_views.setdefault(tag_lower, []).append(views)
            channel_tags[ch_id].add(tag_lower)

    # Tag frequency ranking
    tag_frequency = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(50)
    ]

    # Tag performance correlation
    tag_performance = []
    for tag, view_list in sorted(tag_views.items(), key=lambda x: mean(x[1]) if x[1] else 0, reverse=True):
        if len(view_list) >= 3:  # need at least 3 samples for meaningful stats
            tag_performance.append({
                "tag": tag,
                "avg_views": round(mean(view_list)),
                "median_views": round(median(view_list)),
                "usage_count": len(view_list),
            })
    tag_performance = tag_performance[:30]

    # Shared tags (used by multiple channels)
    num_channels = len(channel_tags)
    shared_tags = []
    if num_channels > 1:
        for tag, count in tag_counter.most_common():
            channels_using = sum(1 for ch_tags in channel_tags.values() if tag in ch_tags)
            if channels_using > 1:
                shared_tags.append({
                    "tag": tag,
                    "channels_using": channels_using,
                    "total_channels": num_channels,
                    "usage_ratio": round(channels_using / num_channels, 2),
                })
        shared_tags.sort(key=lambda x: x["channels_using"], reverse=True)
        shared_tags = shared_tags[:20]

    # Unique tags per channel
    unique_tags_by_channel = {}
    if num_channels > 1:
        all_channel_ids = list(channel_tags.keys())
        for ch_id in all_channel_ids:
            other_tags = set()
            for other_ch_id, other_ch_tags in channel_tags.items():
                if other_ch_id != ch_id:
                    other_tags |= other_ch_tags
            unique = channel_tags[ch_id] - other_tags
            unique_tags_by_channel[ch_id] = sorted(list(unique))[:20]

    # Recommendations based on analysis
    recommendations = []
    if tag_performance:
        top_performing_tags = [tp["tag"] for tp in tag_performance[:5]]
        recommendations.append({
            "type": "high_performing_tags",
            "message": "Consider using these high-performing tags",
            "tags": top_performing_tags,
        })

    if shared_tags:
        universal_tags = [st["tag"] for st in shared_tags if st["usage_ratio"] >= 0.5]
        if universal_tags:
            recommendations.append({
                "type": "universal_tags",
                "message": "Tags used by most channels in this niche (table stakes)",
                "tags": universal_tags[:10],
            })

    # Tags with high performance but low usage = opportunity
    for tp in tag_performance:
        if tp["usage_count"] <= 3 and tp["avg_views"] > (
            mean([v.get("view_count", 0) or 0 for v in videos]) if videos else 0
        ):
            recommendations.append({
                "type": "opportunity_tag",
                "message": f"'{tp['tag']}' has high views but low usage - potential differentiator",
                "tag": tp["tag"],
                "avg_views": tp["avg_views"],
            })
            if len(recommendations) > 10:
                break

    return {
        "tag_frequency": tag_frequency,
        "tag_performance": tag_performance,
        "shared_tags": shared_tags,
        "unique_tags_by_channel": unique_tags_by_channel,
        "recommendations": recommendations,
    }
