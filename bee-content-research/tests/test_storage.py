"""Tests for the storage layer."""

import os
import tempfile
from datetime import datetime

from bee_content_research.storage.db import Database


def test_database_creates_tables():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = {row[0] for row in tables}
        assert "channels" in table_names
        assert "videos" in table_names
        assert "transcripts" in table_names
        assert "niche_groups" in table_names
        assert "niche_group_channels" in table_names
        db.close()


def test_database_default_path():
    db = Database()
    assert db.db_path.endswith("bee_content_research.db")
    db.close()
    os.unlink(db.db_path)


def test_upsert_and_get_channel():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({
            "id": "UC123", "name": "Test", "handle": "@test",
            "subscriber_count": 1000, "video_count": 50,
            "view_count": 100000, "country": "US", "language": "en",
            "description": "A test channel", "thumbnail_url": "",
            "fetched_at": "2026-03-14T00:00:00", "discovered_via": "manual",
        })
        ch = db.get_channel("UC123")
        assert ch is not None
        assert ch["name"] == "Test"
        assert ch["subscriber_count"] == 1000
        db.close()


def test_upsert_channel_updates_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({
            "id": "UC123", "name": "Original", "handle": "@test",
            "subscriber_count": 1000, "fetched_at": "2026-03-14T00:00:00",
            "discovered_via": "manual",
        })
        db.upsert_channel({
            "id": "UC123", "name": "Updated", "handle": "@test2",
            "subscriber_count": 2000, "fetched_at": "2026-03-14T01:00:00",
            "discovered_via": "manual",
        })
        ch = db.get_channel("UC123")
        assert ch["name"] == "Updated"
        assert ch["subscriber_count"] == 2000
        # discovered_via should not be overwritten on conflict
        assert ch["discovered_via"] == "manual"
        db.close()


def test_list_channels():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Bravo", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Alpha", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        channels = db.list_channels()
        assert len(channels) == 2
        # Should be sorted by name
        assert channels[0]["name"] == "Alpha"
        assert channels[1]["name"] == "Bravo"
        db.close()


def test_upsert_and_get_videos():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_video({
            "id": "v1", "channel_id": "UC1", "title": "Video 1",
            "description": "", "tags": "[]", "category": "Education",
            "duration": 600, "view_count": 1000, "like_count": 100,
            "comment_count": 10, "published_at": "2026-01-01",
            "thumbnail_url": "", "language": "en",
            "fetched_at": "2026-03-14T00:00:00", "has_transcript": 0,
        })
        db.commit()
        videos = db.get_videos_for_channel("UC1")
        assert len(videos) == 1
        assert videos[0]["title"] == "Video 1"
        db.close()


def test_upsert_videos_batch():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        videos = [
            {"id": f"v{i}", "channel_id": "UC1", "title": f"Video {i}",
             "view_count": i * 100, "fetched_at": "2026-03-14T00:00:00"}
            for i in range(5)
        ]
        db.upsert_videos(videos)
        result = db.get_videos_for_channel("UC1")
        assert len(result) == 5
        db.close()


def test_create_group_and_resolve():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("test_niche", ["UC1", "UC2"])
        channel_ids = db.resolve_target("test_niche")
        assert set(channel_ids) == {"UC1", "UC2"}
        # Single channel resolve
        assert db.resolve_target("UC1") == ["UC1"]
        # Unknown target
        assert db.resolve_target("nonexistent") == []
        db.close()


def test_add_remove_from_group():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC3", "name": "Ch3", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("grp", ["UC1"])
        db.add_to_group("grp", ["UC2", "UC3"])
        assert len(db.resolve_target("grp")) == 3
        db.remove_from_group("grp", ["UC2"])
        assert set(db.resolve_target("grp")) == {"UC1", "UC3"}
        db.close()


def test_is_stale():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        assert db.is_stale(None) is True
        assert db.is_stale("2020-01-01T00:00:00") is True
        assert db.is_stale(datetime.now().isoformat()) is False
        db.close()


def test_list_groups():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("alpha", ["UC1"])
        db.create_group("beta", ["UC1", "UC2"])
        groups = db.list_groups()
        assert len(groups) == 2
        assert groups[0]["name"] == "alpha"
        assert groups[0]["channel_count"] == 1
        assert groups[1]["name"] == "beta"
        assert groups[1]["channel_count"] == 2
        db.close()


def test_get_group_channels():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("grp", ["UC1", "UC2"])
        channels = db.get_group_channels("grp")
        assert len(channels) == 2
        ids = {c["id"] for c in channels}
        assert ids == {"UC1", "UC2"}
        db.close()


def test_get_videos_for_group():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("grp", ["UC1", "UC2"])
        db.upsert_video({"id": "v1", "channel_id": "UC1", "title": "V1",
                         "view_count": 100, "fetched_at": "2026-03-14T00:00:00"})
        db.upsert_video({"id": "v2", "channel_id": "UC2", "title": "V2",
                         "view_count": 200, "fetched_at": "2026-03-14T00:00:00"})
        db.commit()
        videos = db.get_videos_for_group("grp")
        assert len(videos) == 2
        db.close()


def test_transcript_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_video({"id": "v1", "channel_id": "UC1", "title": "V1",
                         "view_count": 100, "fetched_at": "2026-03-14T00:00:00"})
        db.commit()
        db.upsert_transcript("v1", "en", "Hello world this is a transcript")
        t = db.get_transcript("v1")
        assert t is not None
        assert t["language"] == "en"
        assert "Hello world" in t["text"]
        # Check that video has_transcript was updated
        v = db.get_videos_for_channel("UC1")[0]
        assert v["has_transcript"] == 1
        db.close()


def test_get_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        status = db.get_status()
        assert status["channels"] == 1
        assert status["videos"] == 0
        assert status["transcripts"] == 0
        assert status["groups"] == 0
        assert status["db_path"] == os.path.join(tmpdir, "test.db")
        db.close()
