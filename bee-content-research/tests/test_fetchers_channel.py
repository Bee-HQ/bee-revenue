"""Tests for the channel metadata fetcher."""

from bee_content_research.fetchers.channel import parse_channel_metadata


def test_parse_channel_metadata():
    raw = {
        "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "channel": "MrBeast",
        "channel_url": "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",
        "uploader": "MrBeast",
        "uploader_id": "@MrBeast",
        "channel_follower_count": 350000000,
    }
    ch = parse_channel_metadata(raw, discovered_via="manual")
    assert ch["id"] == "UCX6OQ3DkcsbYNE6H8uQQuVA"
    assert ch["name"] == "MrBeast"
    assert ch["handle"] == "@MrBeast"
    assert ch["subscriber_count"] == 350000000
    assert ch["discovered_via"] == "manual"
    assert ch["fetched_at"]  # should be set


def test_parse_channel_metadata_missing_fields():
    raw = {"channel_id": "UC123"}
    ch = parse_channel_metadata(raw, discovered_via="keyword:test")
    assert ch["id"] == "UC123"
    assert ch["name"] == ""
    assert ch["handle"] == ""
    assert ch["subscriber_count"] == 0
    assert ch["discovered_via"] == "keyword:test"


def test_parse_channel_metadata_prefers_id_over_channel_id():
    raw = {"id": "UCAAA", "channel_id": "UCBBB"}
    ch = parse_channel_metadata(raw)
    assert ch["id"] == "UCAAA"


def test_parse_channel_metadata_prefers_channel_over_uploader():
    raw = {"id": "UC1", "channel": "Channel Name", "uploader": "Uploader Name"}
    ch = parse_channel_metadata(raw)
    assert ch["name"] == "Channel Name"
