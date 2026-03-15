"""Integration tests: exercise the full workflow using pre-seeded data (no network calls)."""

import json
import os
import tempfile

from bee_content_research.storage.db import Database
from bee_content_research.services import analysis, groups, reporting


def _seed_database(db: Database):
    """Seed a database with realistic test data."""
    # Create channels
    for i in range(3):
        db.upsert_channel({
            "id": f"UC{i}",
            "name": f"Channel {i}",
            "handle": f"@ch{i}",
            "subscriber_count": (i + 1) * 10000,
            "video_count": 20,
            "view_count": (i + 1) * 500000,
            "country": ["US", "DE", "JP"][i],
            "language": ["en", "de", "ja"][i],
            "description": f"Test channel {i} about technology",
            "thumbnail_url": "",
            "fetched_at": "2026-03-14T00:00:00",
            "discovered_via": "manual",
        })

    # Create group
    db.create_group("test_niche", ["UC0", "UC1", "UC2"])

    # Seed videos with varied performance
    for ch_idx in range(3):
        for v_idx in range(20):
            views = 1000 * (v_idx + 1)
            if v_idx == 19:  # Make last video an outlier
                views = 100000
            db.upsert_video({
                "id": f"v{ch_idx}_{v_idx}",
                "channel_id": f"UC{ch_idx}",
                "title": f"How to do thing {v_idx}" if v_idx % 2 == 0 else f"Top {v_idx} tips",
                "description": f"Description for video {v_idx}",
                "tags": json.dumps(["tag1", "tag2", f"topic{v_idx % 5}"]),
                "category": "Education",
                "duration": 600 + v_idx * 30,
                "view_count": views,
                "like_count": views // 10,
                "comment_count": views // 100,
                "published_at": f"2026-01-{(v_idx + 1):02d}",
                "thumbnail_url": "",
                "language": ["en", "de", "ja"][ch_idx],
                "fetched_at": "2026-03-14T00:00:00",
                "has_transcript": 0,
            })
    db.commit()


def test_full_workflow_with_mock_data():
    """Test the full workflow using pre-seeded data (no network calls)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        _seed_database(db)

        # Verify data is seeded
        status = db.get_status()
        assert status["channels"] == 3
        assert status["videos"] == 60
        assert status["groups"] == 1

        # Run outlier analysis
        result = analysis.outliers(db, "test_niche")
        assert len(result["outliers"]) > 0
        # The 100k view videos should be outliers
        outlier_ids = {o["id"] for o in result["outliers"]}
        assert "v0_19" in outlier_ids or "v1_19" in outlier_ids or "v2_19" in outlier_ids

        # Run engagement analysis
        result = analysis.engagement(db, "test_niche")
        assert "videos" in result
        assert len(result["videos"]) > 0
        assert "summary" in result
        assert result["summary"]["total_videos"] > 0

        # Run benchmark analysis
        result = analysis.benchmarks(db, "test_niche")
        assert "niche_medians" in result
        assert result["niche_medians"]["total_channels"] == 3
        assert result["niche_medians"]["total_videos"] == 60

        # Run title analysis
        result = analysis.titles(db, "test_niche")
        assert "pattern_performance" in result
        assert result["format_distribution"]["total"] == 60

        # Run SEO analysis
        result = analysis.seo(db, "test_niche")
        assert len(result["tag_frequency"]) > 0
        # "tag1" and "tag2" should be the most common tags
        top_tags = [t["tag"] for t in result["tag_frequency"][:5]]
        assert "tag1" in top_tags
        assert "tag2" in top_tags

        # Run timing analysis
        result = analysis.timing(db, "test_niche")
        assert "day_of_week" in result
        assert "monthly_trend" in result

        # Run regional analysis
        result = analysis.regional(db, "test_niche")
        assert "language_distribution" in result
        langs = {ld["language"] for ld in result["language_distribution"]}
        assert "en" in langs

        # Run channel comparison
        result = analysis.compare(db, ["UC0", "UC1", "UC2"])
        assert len(result["channels"]) == 3
        assert "winners" in result

        db.close()


def test_full_report():
    """Test that full_report runs all analyzers without error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        _seed_database(db)

        result = reporting.full_report(db, "test_niche")
        assert result["target"] == "test_niche"
        assert result["channel_count"] == 3
        assert "outliers" in result
        assert "engagement" in result
        assert "benchmarks" in result
        assert "titles" in result
        assert "seo" in result
        assert "timing" in result
        assert "regional" in result
        assert "content_gaps" in result

        # No analyzer should have errored on valid data
        for key in ["outliers", "engagement", "benchmarks", "titles", "seo", "timing", "regional"]:
            assert "error" not in result[key], f"{key} produced an error: {result[key]}"

        db.close()


def test_group_management():
    """Test group CRUD operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC3", "name": "Ch3", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})

        # Create
        groups.create(db, "test_group", ["UC1", "UC2"])
        grps = groups.list_all(db)
        assert len(grps) == 1
        assert grps[0]["name"] == "test_group"
        assert grps[0]["channel_count"] == 2

        # Show
        channels = groups.show(db, "test_group")
        assert len(channels) == 2

        # Add
        groups.add_channels(db, "test_group", ["UC3"])
        channels = groups.show(db, "test_group")
        assert len(channels) == 3

        # Remove
        groups.remove_channels(db, "test_group", ["UC2"])
        channels = groups.show(db, "test_group")
        assert len(channels) == 2
        ids = {c["id"] for c in channels}
        assert ids == {"UC1", "UC3"}

        db.close()


def test_single_channel_analysis():
    """Test analysis on a single channel (not a group)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({
            "id": "UC_SINGLE", "name": "Solo Channel", "handle": "@solo",
            "subscriber_count": 50000, "country": "US", "language": "en",
            "fetched_at": "2026-03-14T00:00:00", "discovered_via": "manual",
        })
        for i in range(15):
            db.upsert_video({
                "id": f"vs_{i}", "channel_id": "UC_SINGLE",
                "title": f"Solo video {i}", "tags": json.dumps(["solo", "test"]),
                "view_count": 500 * (i + 1), "like_count": 50 * (i + 1),
                "comment_count": 5 * (i + 1),
                "published_at": f"2026-02-{(i + 1):02d}",
                "fetched_at": "2026-03-14T00:00:00",
            })
        db.commit()

        # Should work with channel ID directly
        result = analysis.outliers(db, "UC_SINGLE")
        assert "outliers" in result

        result = analysis.engagement(db, "UC_SINGLE")
        assert len(result["videos"]) == 15

        db.close()


def test_empty_niche_analysis():
    """Test analysis on a niche with no videos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC_EMPTY", "name": "Empty", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("empty_niche", ["UC_EMPTY"])

        # All analyzers should handle empty data gracefully
        result = analysis.outliers(db, "empty_niche")
        assert result["outliers"] == []

        result = analysis.engagement(db, "empty_niche")
        assert result["videos"] == []

        result = analysis.benchmarks(db, "empty_niche")
        assert result["niche_medians"] == {}

        result = analysis.titles(db, "empty_niche")
        assert result["format_distribution"] == {}

        db.close()
