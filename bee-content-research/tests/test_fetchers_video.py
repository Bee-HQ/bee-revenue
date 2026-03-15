"""Tests for the video metadata fetcher."""

import json

from bee_content_research.fetchers.video import parse_video_metadata


def test_parse_video_metadata():
    """Test parsing of yt-dlp JSON output into our schema."""
    raw = {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "description": "The official video...",
        "tags": ["rick astley", "never gonna give you up"],
        "categories": ["Music"],
        "duration": 212,
        "view_count": 1500000000,
        "like_count": 15000000,
        "comment_count": 2500000,
        "upload_date": "20091025",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
        "channel": "Rick Astley",
        "language": "en",
    }
    video = parse_video_metadata(raw)
    assert video["id"] == "dQw4w9WgXcQ"
    assert video["channel_id"] == "UCuAXFkgsw1L7xaCfnd5JJOw"
    assert video["duration"] == 212
    assert video["view_count"] == 1500000000
    assert json.loads(video["tags"]) == ["rick astley", "never gonna give you up"]
    assert video["published_at"] == "2009-10-25"
    assert video["category"] == "Music"
    assert video["has_transcript"] == 0
    assert video["fetched_at"]  # should be set


def test_parse_video_metadata_missing_fields():
    """Test parsing handles missing fields gracefully."""
    raw = {"id": "abc123"}
    video = parse_video_metadata(raw)
    assert video["id"] == "abc123"
    assert video["channel_id"] == ""
    assert video["title"] == ""
    assert video["tags"] == "[]"
    assert video["category"] == ""
    assert video["duration"] == 0
    assert video["view_count"] == 0
    assert video["published_at"] == ""


def test_parse_video_metadata_no_tags():
    """Test parsing with None tags."""
    raw = {"id": "abc123", "tags": None}
    video = parse_video_metadata(raw)
    assert video["tags"] == "[]"


def test_parse_video_metadata_no_categories():
    """Test parsing with None categories."""
    raw = {"id": "abc123", "categories": None}
    video = parse_video_metadata(raw)
    assert video["category"] == ""
