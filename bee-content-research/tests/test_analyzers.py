"""Tests for all analyzer modules."""

import json

from bee_content_research.analyzers.outliers import find_outliers
from bee_content_research.analyzers.content_gaps import find_content_gaps
from bee_content_research.analyzers.titles import analyze_titles
from bee_content_research.analyzers.engagement import analyze_engagement
from bee_content_research.analyzers.benchmarks import benchmark_niche
from bee_content_research.analyzers.seo import analyze_seo
from bee_content_research.analyzers.timing import analyze_timing
from bee_content_research.analyzers.regional import analyze_regional


def _make_videos(count=20, channel_id="UC1", base_views=1000):
    """Helper to create synthetic video data."""
    return [
        {
            "id": f"v{channel_id}_{i}",
            "channel_id": channel_id,
            "title": f"How to do thing {i}" if i % 2 == 0 else f"Top {i} tips for success",
            "description": f"Description for video {i}",
            "tags": json.dumps(["tag1", "tag2", f"topic{i % 5}"]),
            "category": "Education",
            "duration": 600 + i * 30,
            "view_count": base_views * (i + 1),
            "like_count": base_views * (i + 1) // 10,
            "comment_count": base_views * (i + 1) // 100,
            "published_at": f"2026-01-{(i + 1):02d}",
            "thumbnail_url": "",
            "language": "en",
            "fetched_at": "2026-03-14T00:00:00",
            "has_transcript": 0,
        }
        for i in range(count)
    ]


# --- Outlier tests ---

def test_find_outliers_basic():
    videos = _make_videos(20)
    # Add one viral outlier
    videos.append({
        "id": "viral", "channel_id": "UC1", "title": "Viral Video",
        "view_count": 500000, "like_count": 50000, "comment_count": 5000,
        "published_at": "2026-02-01", "tags": "[]",
    })
    result = find_outliers(videos, threshold=2.0)
    assert len(result["outliers"]) >= 1
    assert any(o["id"] == "viral" for o in result["outliers"])
    assert "UC1" in result["channel_medians"]


def test_find_outliers_empty():
    result = find_outliers([])
    assert result["outliers"] == []
    assert result["channel_medians"] == {}


def test_find_outliers_multiple_channels():
    videos = _make_videos(10, "UC1", 1000) + _make_videos(10, "UC2", 5000)
    # Add outlier for UC1 only
    videos.append({
        "id": "viral1", "channel_id": "UC1", "title": "Viral",
        "view_count": 100000, "like_count": 10000, "comment_count": 1000,
        "published_at": "2026-02-01", "tags": "[]",
    })
    result = find_outliers(videos, threshold=3.0)
    assert any(o["id"] == "viral1" for o in result["outliers"])


def test_find_outliers_engagement_fields():
    videos = _make_videos(5)
    videos.append({
        "id": "viral", "channel_id": "UC1", "title": "Viral",
        "view_count": 100000, "like_count": 10000, "comment_count": 1000,
        "published_at": "2026-02-01", "tags": "[]",
    })
    result = find_outliers(videos)
    viral = [o for o in result["outliers"] if o["id"] == "viral"][0]
    assert "like_rate" in viral
    assert "comment_rate" in viral
    assert viral["like_rate"] == 10.0  # 10000/100000 * 100


# --- Content gap tests ---

def test_find_content_gaps_basic():
    videos = _make_videos(20)
    result = find_content_gaps(videos)
    assert "gaps" in result
    assert "covered_topics" in result
    assert "topic_counts" in result
    assert isinstance(result["topic_counts"], dict)


def test_find_content_gaps_with_suggestions():
    videos = _make_videos(20)
    suggestions = ["quantum computing tutorial", "blockchain explained", "how to do thing 1"]
    result = find_content_gaps(videos, suggestions=suggestions)
    assert len(result["gaps"]) > 0
    # "quantum computing tutorial" should appear as a gap (not covered)
    gap_topics = [g["topic"] for g in result["gaps"]]
    assert "quantum computing tutorial" in gap_topics


def test_find_content_gaps_empty():
    result = find_content_gaps([])
    assert result["gaps"] == []


def test_find_content_gaps_with_transcripts():
    videos = _make_videos(5)
    transcripts = [
        {"video_id": "v1", "language": "en", "text": "Today we discuss machine learning and AI"},
        {"video_id": "v2", "language": "en", "text": "Deep dive into neural networks"},
    ]
    result = find_content_gaps(videos, transcripts=transcripts)
    assert "topic_counts" in result
    # Transcript words should appear in topic map
    assert "machine" in result["topic_counts"] or "learning" in result["topic_counts"]


# --- Title analysis tests ---

def test_analyze_titles_basic():
    videos = _make_videos(20)
    result = analyze_titles(videos)
    assert "pattern_performance" in result
    assert "format_distribution" in result
    assert "best_patterns" in result
    assert "title_details" in result
    assert result["format_distribution"]["total"] == 20


def test_analyze_titles_question_detection():
    videos = [
        {"id": "v1", "title": "How to cook pasta?", "view_count": 1000},
        {"id": "v2", "title": "Best pasta recipe", "view_count": 2000},
        {"id": "v3", "title": "What is the best pasta?", "view_count": 1500},
    ]
    result = analyze_titles(videos)
    assert result["format_distribution"]["questions"] == 2
    assert result["format_distribution"]["statements"] == 1


def test_analyze_titles_number_detection():
    videos = [
        {"id": "v1", "title": "Top 10 tips", "view_count": 5000},
        {"id": "v2", "title": "5 best practices", "view_count": 3000},
        {"id": "v3", "title": "Simple guide", "view_count": 1000},
    ]
    result = analyze_titles(videos)
    assert result["format_distribution"]["with_numbers"] == 2
    assert result["format_distribution"]["list_format"] == 2


def test_analyze_titles_empty():
    result = analyze_titles([])
    assert result["pattern_performance"] == {}
    assert result["format_distribution"] == {}


def test_analyze_titles_power_words():
    videos = [
        {"id": "v1", "title": "The SECRET to making money", "view_count": 10000},
        {"id": "v2", "title": "INSANE hack revealed", "view_count": 8000},
        {"id": "v3", "title": "Normal video title", "view_count": 500},
    ]
    result = analyze_titles(videos)
    assert result["format_distribution"]["with_power_words"] >= 2


# --- Engagement tests ---

def test_analyze_engagement_basic():
    videos = _make_videos(20)
    result = analyze_engagement(videos)
    assert "videos" in result
    assert "summary" in result
    assert "hidden_gems" in result
    assert len(result["videos"]) == 20
    assert result["summary"]["total_videos"] == 20


def test_analyze_engagement_scoring():
    videos = [
        {"id": "v1", "view_count": 1000, "like_count": 100, "comment_count": 50},
        {"id": "v2", "view_count": 10000, "like_count": 200, "comment_count": 10},
    ]
    result = analyze_engagement(videos)
    # v1 has higher engagement rate (10% like rate vs 2%)
    assert result["videos"][0]["id"] == "v1"


def test_analyze_engagement_hidden_gems():
    videos = [
        # Low views but high engagement = hidden gem
        {"id": "gem", "view_count": 100, "like_count": 50, "comment_count": 20,
         "channel_id": "UC1"},
        # High views, normal engagement
        {"id": "popular", "view_count": 100000, "like_count": 5000, "comment_count": 100,
         "channel_id": "UC1"},
    ]
    # Need more videos so median calculations work
    for i in range(10):
        videos.append({"id": f"v{i}", "view_count": 5000, "like_count": 250,
                       "comment_count": 25, "channel_id": "UC1"})
    result = analyze_engagement(videos)
    gem_ids = [g["id"] for g in result["hidden_gems"]]
    assert "gem" in gem_ids


def test_analyze_engagement_empty():
    result = analyze_engagement([])
    assert result["videos"] == []
    assert result["summary"] == {}


def test_analyze_engagement_zero_views():
    videos = [{"id": "v1", "view_count": 0, "like_count": 0, "comment_count": 0}]
    result = analyze_engagement(videos)
    assert len(result["videos"]) == 0  # filtered out


# --- Benchmark tests ---

def test_benchmark_niche_basic():
    videos = _make_videos(10, "UC1", 1000) + _make_videos(10, "UC2", 5000)
    result = benchmark_niche(videos)
    assert "niche_medians" in result
    assert "channel_benchmarks" in result
    assert "channel_deviations" in result
    assert result["niche_medians"]["total_channels"] == 2
    assert result["niche_medians"]["total_videos"] == 20
    assert len(result["channel_benchmarks"]) == 2


def test_benchmark_niche_with_channels():
    videos = _make_videos(10, "UC1", 1000)
    channels = [{"id": "UC1", "name": "Channel One", "subscriber_count": 50000}]
    result = benchmark_niche(videos, channels)
    assert result["channel_benchmarks"][0]["subscriber_count"] == 50000
    assert result["channel_benchmarks"][0]["sub_view_ratio"] > 0


def test_benchmark_niche_deviation():
    videos = _make_videos(10, "UC1", 1000) + _make_videos(10, "UC2", 10000)
    result = benchmark_niche(videos)
    deviations = result["channel_deviations"]
    # UC2 should be above niche median
    uc2_dev = [d for d in deviations if d["channel_id"] == "UC2"][0]
    assert uc2_dev["above_or_below"] == "above"


def test_benchmark_niche_empty():
    result = benchmark_niche([])
    assert result["niche_medians"] == {}


# --- SEO tests ---

def test_analyze_seo_basic():
    videos = _make_videos(20)
    result = analyze_seo(videos)
    assert "tag_frequency" in result
    assert "tag_performance" in result
    assert "shared_tags" in result
    assert len(result["tag_frequency"]) > 0


def test_analyze_seo_shared_tags():
    videos = _make_videos(10, "UC1") + _make_videos(10, "UC2")
    result = analyze_seo(videos)
    # "tag1" and "tag2" should be shared across both channels
    shared_tag_names = [s["tag"] for s in result["shared_tags"]]
    assert "tag1" in shared_tag_names
    assert "tag2" in shared_tag_names


def test_analyze_seo_unique_tags():
    v1 = [{"id": "v1", "channel_id": "UC1", "tags": json.dumps(["common", "unique_a"]),
            "view_count": 1000}]
    v2 = [{"id": "v2", "channel_id": "UC2", "tags": json.dumps(["common", "unique_b"]),
            "view_count": 2000}]
    result = analyze_seo(v1 + v2)
    assert "UC1" in result["unique_tags_by_channel"]
    assert "unique_a" in result["unique_tags_by_channel"]["UC1"]


def test_analyze_seo_empty():
    result = analyze_seo([])
    assert result["tag_frequency"] == []


# --- Timing tests ---

def test_analyze_timing_basic():
    videos = _make_videos(20)
    result = analyze_timing(videos)
    assert "day_of_week" in result
    assert "hour_of_day" in result
    assert "monthly_trend" in result
    assert "best_times" in result


def test_analyze_timing_day_analysis():
    # All videos on Wednesdays (2026-01-07 is a Wednesday)
    videos = [
        {"id": f"v{i}", "published_at": f"2026-01-{7 + i * 7:02d}", "view_count": 1000 * (i + 1)}
        for i in range(3)
    ]
    result = analyze_timing(videos)
    assert "Wednesday" in result["day_of_week"]


def test_analyze_timing_monthly():
    videos = [
        {"id": "v1", "published_at": "2026-01-15", "view_count": 1000},
        {"id": "v2", "published_at": "2026-01-20", "view_count": 2000},
        {"id": "v3", "published_at": "2026-02-10", "view_count": 3000},
    ]
    result = analyze_timing(videos)
    assert len(result["monthly_trend"]) == 2  # Jan and Feb


def test_analyze_timing_empty():
    result = analyze_timing([])
    assert result["day_of_week"] == {}


# --- Regional tests ---

def test_analyze_regional_basic():
    videos = _make_videos(20)
    channels = [{"id": "UC1", "country": "US", "language": "en", "name": "Ch1"}]
    result = analyze_regional(videos, channels)
    assert "language_distribution" in result
    assert "country_distribution" in result
    assert "revenue_estimates" in result
    assert "opportunities" in result


def test_analyze_regional_language_distribution():
    videos = [
        {"id": "v1", "language": "en", "view_count": 1000, "channel_id": "UC1"},
        {"id": "v2", "language": "en", "view_count": 2000, "channel_id": "UC1"},
        {"id": "v3", "language": "es", "view_count": 3000, "channel_id": "UC2"},
    ]
    result = analyze_regional(videos)
    langs = {ld["language"]: ld for ld in result["language_distribution"]}
    assert "en" in langs
    assert "es" in langs
    assert langs["en"]["video_count"] == 2
    assert langs["es"]["video_count"] == 1


def test_analyze_regional_cpm_estimates():
    videos = [
        {"id": "v1", "language": "en", "view_count": 100000, "channel_id": "UC1"},
    ]
    channels = [{"id": "UC1", "country": "US", "name": "Ch1"}]
    result = analyze_regional(videos, channels)
    # US CPM is $26
    us_country = [c for c in result["country_distribution"] if c["country"] == "US"]
    if us_country:
        assert us_country[0]["estimated_cpm"] == 26.00


def test_analyze_regional_empty():
    result = analyze_regional([])
    assert result["language_distribution"] == []


def test_analyze_regional_opportunities():
    # All videos in English from US - should suggest other high-CPM markets
    videos = [
        {"id": f"v{i}", "language": "en", "view_count": 1000, "channel_id": "UC1"}
        for i in range(20)
    ]
    channels = [{"id": "UC1", "country": "US", "name": "Ch1"}]
    result = analyze_regional(videos, channels)
    # Should suggest high-CPM countries with no presence
    if result["opportunities"]:
        # At least some opportunities should exist for countries not present
        assert any(
            "country" in opp for opp in result["opportunities"]
        )
