"""Title/thumbnail pattern analysis analyzer.

Extracts patterns from video titles: length, question vs statement, number usage,
power words, emoji presence. Clusters titles by format pattern and correlates
patterns with view performance.
"""

import re
from collections import Counter
from statistics import mean, median

# Power words commonly used in high-performing YouTube titles
_POWER_WORDS = frozenset({
    "secret", "secrets", "shocking", "insane", "unbelievable", "incredible",
    "amazing", "ultimate", "best", "worst", "biggest", "top", "hack", "hacks",
    "free", "easy", "simple", "fast", "quick", "never", "always", "must",
    "need", "stop", "truth", "real", "honest", "finally", "exposed", "revealed",
    "warning", "urgent", "breaking", "update", "mistake", "mistakes", "wrong",
    "perfect", "genius", "brilliant", "massive", "tiny", "huge", "epic",
    "impossible", "banned", "illegal", "dangerous", "crazy", "weird", "strange",
})

# Emoji regex pattern
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def _classify_title(title: str) -> dict:
    """Classify a title by its structural patterns."""
    title_lower = title.lower()
    words = title.split()

    return {
        "length": len(title),
        "word_count": len(words),
        "is_question": title.rstrip().endswith("?") or title_lower.startswith(
            ("how", "what", "why", "when", "where", "who", "which", "can", "do", "does", "is", "are", "will")
        ),
        "has_number": bool(re.search(r'\d+', title)),
        "has_list_format": bool(re.match(r'^(top\s+)?\d+\s', title_lower)),
        "has_how_to": title_lower.startswith("how to") or "how to" in title_lower,
        "has_power_word": any(w.lower() in _POWER_WORDS for w in words),
        "power_words_found": [w.lower() for w in words if w.lower() in _POWER_WORDS],
        "has_emoji": bool(_EMOJI_PATTERN.search(title)),
        "has_brackets": bool(re.search(r'[\[\(].*[\]\)]', title)),
        "has_pipe_or_dash": bool(re.search(r'[|—–-]{1,2}', title)),
        "is_all_caps_word_present": any(w.isupper() and len(w) > 2 for w in words),
    }


def _bucket_length(length: int) -> str:
    """Bucket title length into categories."""
    if length <= 30:
        return "short (<=30)"
    elif length <= 50:
        return "medium (31-50)"
    elif length <= 70:
        return "long (51-70)"
    else:
        return "very_long (>70)"


def analyze_titles(videos: list[dict]) -> dict:
    """Analyze title patterns and their correlation with view performance.

    Args:
        videos: List of video dicts with title, view_count, etc.

    Returns:
        Dict with 'pattern_performance' (pattern -> avg views), 'format_distribution',
        'best_patterns', 'title_details'.
    """
    if not videos:
        return {
            "pattern_performance": {},
            "format_distribution": {},
            "best_patterns": [],
            "title_details": [],
        }

    # Classify each title
    details = []
    for v in videos:
        title = v.get("title", "")
        views = v.get("view_count", 0) or 0
        classification = _classify_title(title)
        classification["title"] = title
        classification["view_count"] = views
        classification["video_id"] = v.get("id", "")
        classification["channel_id"] = v.get("channel_id", "")
        details.append(classification)

    # Compute pattern performance
    pattern_views: dict[str, list[int]] = {
        "question": [],
        "statement": [],
        "has_number": [],
        "no_number": [],
        "list_format": [],
        "how_to": [],
        "has_power_word": [],
        "no_power_word": [],
        "has_emoji": [],
        "no_emoji": [],
        "has_brackets": [],
        "no_brackets": [],
        "all_caps_word": [],
    }

    length_bucket_views: dict[str, list[int]] = {}

    for d in details:
        views = d["view_count"]

        if d["is_question"]:
            pattern_views["question"].append(views)
        else:
            pattern_views["statement"].append(views)

        if d["has_number"]:
            pattern_views["has_number"].append(views)
        else:
            pattern_views["no_number"].append(views)

        if d["has_list_format"]:
            pattern_views["list_format"].append(views)

        if d["has_how_to"]:
            pattern_views["how_to"].append(views)

        if d["has_power_word"]:
            pattern_views["has_power_word"].append(views)
        else:
            pattern_views["no_power_word"].append(views)

        if d["has_emoji"]:
            pattern_views["has_emoji"].append(views)
        else:
            pattern_views["no_emoji"].append(views)

        if d["has_brackets"]:
            pattern_views["has_brackets"].append(views)
        else:
            pattern_views["no_brackets"].append(views)

        if d["is_all_caps_word_present"]:
            pattern_views["all_caps_word"].append(views)

        bucket = _bucket_length(d["length"])
        length_bucket_views.setdefault(bucket, []).append(views)

    # Calculate averages per pattern
    pattern_performance = {}
    for pattern, view_list in pattern_views.items():
        if view_list:
            pattern_performance[pattern] = {
                "avg_views": round(mean(view_list)),
                "median_views": round(median(view_list)),
                "count": len(view_list),
            }

    for bucket, view_list in length_bucket_views.items():
        if view_list:
            pattern_performance[f"length_{bucket}"] = {
                "avg_views": round(mean(view_list)),
                "median_views": round(median(view_list)),
                "count": len(view_list),
            }

    # Format distribution
    format_distribution = {
        "questions": sum(1 for d in details if d["is_question"]),
        "statements": sum(1 for d in details if not d["is_question"]),
        "with_numbers": sum(1 for d in details if d["has_number"]),
        "list_format": sum(1 for d in details if d["has_list_format"]),
        "how_to": sum(1 for d in details if d["has_how_to"]),
        "with_power_words": sum(1 for d in details if d["has_power_word"]),
        "with_emoji": sum(1 for d in details if d["has_emoji"]),
        "with_brackets": sum(1 for d in details if d["has_brackets"]),
        "with_all_caps": sum(1 for d in details if d["is_all_caps_word_present"]),
        "total": len(details),
    }

    # Rank power words by frequency and performance
    power_word_stats: dict[str, list[int]] = {}
    for d in details:
        for pw in d["power_words_found"]:
            power_word_stats.setdefault(pw, []).append(d["view_count"])

    top_power_words = [
        {"word": word, "count": len(view_list), "avg_views": round(mean(view_list))}
        for word, view_list in sorted(
            power_word_stats.items(), key=lambda x: mean(x[1]), reverse=True
        )
    ][:15]

    # Best patterns (sorted by median views)
    best_patterns = sorted(
        [
            {"pattern": p, **stats}
            for p, stats in pattern_performance.items()
            if stats["count"] >= 3  # need at least 3 samples
        ],
        key=lambda x: x["median_views"],
        reverse=True,
    )

    return {
        "pattern_performance": pattern_performance,
        "format_distribution": format_distribution,
        "best_patterns": best_patterns[:10],
        "top_power_words": top_power_words,
        "title_details": details,
    }
