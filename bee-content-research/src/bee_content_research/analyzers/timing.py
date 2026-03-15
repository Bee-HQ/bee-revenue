"""Upload timing pattern analyzer.

Analyzes day-of-week and hour-of-day upload patterns and their correlation
with view performance.
"""

from collections import Counter
from datetime import datetime
from statistics import mean, median


_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def analyze_timing(videos: list[dict]) -> dict:
    """Analyze upload timing patterns and their performance impact.

    Args:
        videos: List of video dicts with published_at and view_count.

    Returns:
        Dict with 'day_of_week' performance, 'hour_of_day' performance,
        'monthly_trend', and 'best_times'.
    """
    if not videos:
        return {
            "day_of_week": {},
            "hour_of_day": {},
            "monthly_trend": [],
            "best_times": [],
            "upload_frequency": {},
        }

    day_views: dict[str, list[int]] = {d: [] for d in _DAY_NAMES}
    hour_views: dict[int, list[int]] = {h: [] for h in range(24)}
    month_views: dict[str, list[int]] = {}
    day_counts: Counter = Counter()
    hour_counts: Counter = Counter()

    parsed_count = 0

    for v in videos:
        pub = v.get("published_at", "")
        views = v.get("view_count", 0) or 0
        if not pub:
            continue

        try:
            # Handle both full ISO format and date-only format
            if "T" in pub:
                dt = datetime.fromisoformat(pub)
            else:
                dt = datetime.strptime(pub, "%Y-%m-%d")
            parsed_count += 1
        except (ValueError, TypeError):
            continue

        day_name = _DAY_NAMES[dt.weekday()]
        day_views[day_name].append(views)
        day_counts[day_name] += 1

        hour_views[dt.hour].append(views)
        hour_counts[dt.hour] += 1

        month_key = dt.strftime("%Y-%m")
        month_views.setdefault(month_key, []).append(views)

    # Day of week performance
    day_of_week = {}
    for day, view_list in day_views.items():
        if view_list:
            day_of_week[day] = {
                "avg_views": round(mean(view_list)),
                "median_views": round(median(view_list)),
                "upload_count": len(view_list),
            }

    # Hour of day performance
    hour_of_day = {}
    for hour, view_list in hour_views.items():
        if view_list:
            hour_of_day[hour] = {
                "avg_views": round(mean(view_list)),
                "median_views": round(median(view_list)),
                "upload_count": len(view_list),
            }

    # Monthly trend
    monthly_trend = []
    for month in sorted(month_views.keys()):
        view_list = month_views[month]
        monthly_trend.append({
            "month": month,
            "video_count": len(view_list),
            "avg_views": round(mean(view_list)),
            "total_views": sum(view_list),
        })

    # Best times analysis
    best_times = []

    # Best day
    if day_of_week:
        best_day = max(day_of_week.items(), key=lambda x: x[1]["median_views"])
        worst_day = min(day_of_week.items(), key=lambda x: x[1]["median_views"])
        best_times.append({
            "type": "best_day",
            "value": best_day[0],
            "median_views": best_day[1]["median_views"],
            "upload_count": best_day[1]["upload_count"],
        })
        best_times.append({
            "type": "worst_day",
            "value": worst_day[0],
            "median_views": worst_day[1]["median_views"],
            "upload_count": worst_day[1]["upload_count"],
        })

    # Best hour (only if we have time data)
    active_hours = {h: d for h, d in hour_of_day.items() if d["upload_count"] >= 2}
    if active_hours:
        best_hour = max(active_hours.items(), key=lambda x: x[1]["median_views"])
        best_times.append({
            "type": "best_hour",
            "value": f"{best_hour[0]:02d}:00",
            "median_views": best_hour[1]["median_views"],
            "upload_count": best_hour[1]["upload_count"],
        })

    # Upload frequency
    upload_frequency = {
        "total_uploads": parsed_count,
        "by_day": dict(day_counts.most_common()),
        "most_common_day": day_counts.most_common(1)[0][0] if day_counts else None,
    }

    return {
        "day_of_week": day_of_week,
        "hour_of_day": hour_of_day,
        "monthly_trend": monthly_trend,
        "best_times": best_times,
        "upload_frequency": upload_frequency,
    }
