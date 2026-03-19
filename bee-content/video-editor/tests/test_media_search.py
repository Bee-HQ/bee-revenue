"""Tests for multi-provider stock media search."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bee_video_editor.processors.media_search import (
    SearchResult, SearchQuery, search_stock,
    _clean_search_term, extract_search_queries,
)


class TestCleanSearchTerm:
    def test_strips_establishing_shot(self):
        assert _clean_search_term("Establishing shot of courthouse") == "courthouse"

    def test_strips_close_up(self):
        assert _clean_search_term("Close-up of evidence bag") == "evidence bag"

    def test_strips_aerial(self):
        assert _clean_search_term("Aerial shot of farm property") == "farm property"

    def test_strips_parenthetical(self):
        assert _clean_search_term("Police car (night scene)") == "Police car"

    def test_leaves_plain_text(self):
        assert _clean_search_term("courtroom interior") == "courtroom interior"

    def test_strips_ken_burns(self):
        assert _clean_search_term("Farm property with Ken Burns zoom") == "Farm property"


class TestSearchStock:
    @patch.dict("os.environ", {"PEXELS_API_KEY": "", "PIXABAY_API_KEY": ""})
    def test_no_api_keys_returns_empty(self):
        results = search_stock("test query")
        assert results == []

    @patch("bee_video_editor.processors.media_search.search_pexels_videos")
    @patch.dict("os.environ", {"PEXELS_API_KEY": "test-key"})
    def test_pexels_provider(self, mock_search):
        mock_search.return_value = [
            SearchResult(provider="pexels", media_type="video", id="1", url="", download_url="https://example.com/v.mp4")
        ]
        results = search_stock("police car", providers=["pexels"])
        assert len(results) == 1
        assert results[0].provider == "pexels"

    @patch("bee_video_editor.processors.media_search.search_pixabay_videos")
    @patch.dict("os.environ", {"PIXABAY_API_KEY": "test-key"})
    def test_pixabay_provider(self, mock_search):
        mock_search.return_value = [
            SearchResult(provider="pixabay", media_type="video", id="2", url="", download_url="https://example.com/v.mp4")
        ]
        results = search_stock("courthouse", providers=["pixabay"])
        assert len(results) == 1
        assert results[0].provider == "pixabay"


class TestExtractSearchQueries:
    def test_extracts_stock_queries(self):
        from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, ParsedSection
        from bee_video_editor.formats.models import ProjectConfig, SegmentConfig, VisualEntry

        parsed = ParsedStoryboard(
            project=ProjectConfig(title="Test"),
            sections=[ParsedSection(title="S", start="0:00", end="0:30")],
            segments=[
                ParsedSegment(
                    id="s1", title="Test", start="0:00", end="0:10", section="S",
                    config=SegmentConfig(visual=[VisualEntry(type="STOCK", query="aerial farm dusk")]),
                    narration="",
                ),
                ParsedSegment(
                    id="s2", title="Test2", start="0:10", end="0:20", section="S",
                    config=SegmentConfig(visual=[VisualEntry(type="PHOTO", query="courtroom interior")]),
                    narration="",
                ),
            ],
        )
        queries = extract_search_queries(parsed)
        assert len(queries) == 2
        video_q = next(q for q in queries if q.media_type == "video")
        assert "aerial farm dusk" in video_q.query
        photo_q = next(q for q in queries if q.media_type == "photo")
        assert "courtroom interior" in photo_q.query

    def test_deduplicates_queries(self):
        from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, ParsedSection
        from bee_video_editor.formats.models import ProjectConfig, SegmentConfig, VisualEntry

        parsed = ParsedStoryboard(
            project=ProjectConfig(title="Test"),
            sections=[ParsedSection(title="S", start="0:00", end="0:20")],
            segments=[
                ParsedSegment(id="s1", title="T", start="0:00", end="0:10", section="S",
                    config=SegmentConfig(visual=[VisualEntry(type="STOCK", query="police car")]), narration=""),
                ParsedSegment(id="s2", title="T", start="0:10", end="0:20", section="S",
                    config=SegmentConfig(visual=[VisualEntry(type="STOCK", query="police car")]), narration=""),
            ],
        )
        queries = extract_search_queries(parsed)
        assert len(queries) == 1
        assert len(queries[0].segment_ids) == 2
