"""Regional and language analysis analyzer.

Groups videos and channels by detected language and country, calculates
CPM-adjusted revenue estimates, and identifies underserved language/region
opportunities.
"""

from collections import Counter
from statistics import mean, median

# Approximate CPM rates by country (USD per 1000 views, 2025-2026 estimates)
# Source: compiled from various YouTube creator reports
CPM_BY_COUNTRY = {
    "NO": 43.15,  # Norway
    "DE": 38.85,  # Germany
    "AU": 36.21,  # Australia
    "AT": 33.50,  # Austria
    "CH": 33.00,  # Switzerland
    "GB": 30.50,  # United Kingdom
    "CA": 28.50,  # Canada
    "US": 26.00,  # United States
    "NL": 25.80,  # Netherlands
    "SE": 24.50,  # Sweden
    "DK": 24.00,  # Denmark
    "FI": 22.00,  # Finland
    "FR": 20.00,  # France
    "NZ": 19.50,  # New Zealand
    "IE": 18.00,  # Ireland
    "BE": 17.50,  # Belgium
    "JP": 15.00,  # Japan
    "KR": 12.50,  # South Korea
    "IT": 12.00,  # Italy
    "ES": 10.00,  # Spain
    "SG": 9.50,   # Singapore
    "PT": 8.00,   # Portugal
    "PL": 7.00,   # Poland
    "CZ": 6.50,   # Czech Republic
    "RO": 5.50,   # Romania
    "HU": 5.00,   # Hungary
    "MX": 4.50,   # Mexico
    "AR": 4.00,   # Argentina
    "BR": 3.50,   # Brazil
    "TR": 3.00,   # Turkey
    "RU": 2.50,   # Russia
    "TH": 2.00,   # Thailand
    "ID": 1.50,   # Indonesia
    "PH": 1.20,   # Philippines
    "VN": 1.00,   # Vietnam
    "IN": 0.50,   # India
    "PK": 0.50,   # Pakistan
    "BD": 0.40,   # Bangladesh
    "NG": 0.30,   # Nigeria
}

# Language name lookup
_LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "pt": "Portuguese", "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
    "hi": "Hindi", "ar": "Arabic", "ru": "Russian", "it": "Italian",
    "nl": "Dutch", "pl": "Polish", "tr": "Turkish", "sv": "Swedish",
    "da": "Danish", "fi": "Finnish", "no": "Norwegian", "id": "Indonesian",
    "th": "Thai", "vi": "Vietnamese", "ro": "Romanian", "cs": "Czech",
    "hu": "Hungarian", "el": "Greek", "he": "Hebrew", "uk": "Ukrainian",
    "ms": "Malay", "tl": "Filipino", "bn": "Bengali",
}


def analyze_regional(videos: list[dict], channels: list[dict] | None = None) -> dict:
    """Analyze regional and language distribution with CPM-adjusted estimates.

    Args:
        videos: List of video dicts with language, view_count.
        channels: Optional list of channel dicts with country, language.

    Returns:
        Dict with 'language_distribution', 'country_distribution',
        'revenue_estimates', and 'opportunities'.
    """
    if not videos:
        return {
            "language_distribution": [],
            "country_distribution": [],
            "revenue_estimates": [],
            "opportunities": [],
        }

    # Language distribution from videos
    lang_counter: Counter = Counter()
    lang_views: dict[str, list[int]] = {}

    for v in videos:
        lang = v.get("language", "") or "unknown"
        views = v.get("view_count", 0) or 0
        lang_counter[lang] += 1
        lang_views.setdefault(lang, []).append(views)

    total_videos = len(videos)
    language_distribution = []
    for lang, count in lang_counter.most_common():
        view_list = lang_views.get(lang, [])
        language_distribution.append({
            "language": lang,
            "language_name": _LANGUAGE_NAMES.get(lang, lang),
            "video_count": count,
            "percentage": round(count / total_videos * 100, 1),
            "avg_views": round(mean(view_list)) if view_list else 0,
            "median_views": round(median(view_list)) if view_list else 0,
            "total_views": sum(view_list),
        })

    # Country distribution from channels
    country_counter: Counter = Counter()
    country_views: dict[str, list[int]] = {}
    channel_country_map: dict[str, str] = {}

    if channels:
        for ch in channels:
            country = ch.get("country", "") or "unknown"
            channel_country_map[ch["id"]] = country
            country_counter[country] += 1

        # Map video views to countries via channel
        for v in videos:
            ch_id = v.get("channel_id", "")
            country = channel_country_map.get(ch_id, "unknown")
            views = v.get("view_count", 0) or 0
            country_views.setdefault(country, []).append(views)

    country_distribution = []
    for country, count in country_counter.most_common():
        view_list = country_views.get(country, [])
        cpm = CPM_BY_COUNTRY.get(country, 2.0)  # default CPM
        total_views = sum(view_list)
        estimated_revenue = (total_views / 1000) * cpm

        country_distribution.append({
            "country": country,
            "channel_count": count,
            "video_count": len(view_list),
            "avg_views": round(mean(view_list)) if view_list else 0,
            "total_views": total_views,
            "estimated_cpm": cpm,
            "estimated_revenue": round(estimated_revenue, 2),
        })

    # Revenue estimates per language/region
    revenue_estimates = []
    for ld in language_distribution:
        # Map language to likely country for CPM estimation
        lang_to_country = {
            "en": "US", "de": "DE", "fr": "FR", "es": "ES", "pt": "BR",
            "ja": "JP", "ko": "KR", "zh": "US", "hi": "IN", "ar": "US",
            "ru": "RU", "it": "IT", "nl": "NL", "pl": "PL", "tr": "TR",
            "sv": "SE", "da": "DK", "fi": "FI", "no": "NO", "id": "ID",
            "th": "TH", "vi": "VN",
        }
        likely_country = lang_to_country.get(ld["language"], "US")
        cpm = CPM_BY_COUNTRY.get(likely_country, 2.0)
        total_views = ld["total_views"]
        est_revenue = (total_views / 1000) * cpm

        revenue_estimates.append({
            "language": ld["language"],
            "language_name": ld["language_name"],
            "likely_country": likely_country,
            "estimated_cpm": cpm,
            "total_views": total_views,
            "estimated_revenue": round(est_revenue, 2),
            "rpm_per_1k_views": round(cpm, 2),
        })

    revenue_estimates.sort(key=lambda x: x["estimated_cpm"], reverse=True)

    # Opportunity scoring: underserved language/region combinations
    opportunities = []

    # Languages with high CPM but low video count
    for re_item in revenue_estimates:
        if re_item["language"] == "unknown":
            continue
        # Opportunity score: high CPM * inverse of coverage
        coverage_ratio = len(lang_views.get(re_item["language"], [])) / total_videos
        if coverage_ratio < 0.1:  # less than 10% coverage
            opportunity_score = re_item["estimated_cpm"] * (1 - coverage_ratio)
            opportunities.append({
                "language": re_item["language"],
                "language_name": re_item["language_name"],
                "estimated_cpm": re_item["estimated_cpm"],
                "current_coverage_pct": round(coverage_ratio * 100, 1),
                "opportunity_score": round(opportunity_score, 2),
                "rationale": f"High CPM (${re_item['estimated_cpm']}) with only {round(coverage_ratio * 100, 1)}% coverage",
            })

    # Also check countries with high CPM and no channel presence
    if channels:
        present_countries = set(channel_country_map.values())
        for country, cpm in sorted(CPM_BY_COUNTRY.items(), key=lambda x: x[1], reverse=True):
            if country not in present_countries and cpm >= 15:
                opportunities.append({
                    "country": country,
                    "estimated_cpm": cpm,
                    "current_coverage_pct": 0,
                    "opportunity_score": round(cpm, 2),
                    "rationale": f"No channels from {country} (CPM: ${cpm})",
                })

    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

    return {
        "language_distribution": language_distribution,
        "country_distribution": country_distribution,
        "revenue_estimates": revenue_estimates,
        "opportunities": opportunities[:20],
    }
