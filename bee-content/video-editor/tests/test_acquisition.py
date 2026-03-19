"""Tests for media acquisition service."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, ParsedSection
from bee_video_editor.formats.models import ProjectConfig, SegmentConfig, VisualEntry
from bee_video_editor.services.acquisition import acquire_media, AcquisitionReport


def _make_storyboard(visual_queries):
    segments = []
    for i, q in enumerate(visual_queries):
        segments.append(ParsedSegment(
            id=f"s{i}", title=f"Seg {i}", start=f"{i}:00", end=f"{i}:10", section="S",
            config=SegmentConfig(visual=[VisualEntry(type="STOCK", query=q)]),
            narration="",
        ))
    return ParsedStoryboard(
        project=ProjectConfig(title="Test"),
        sections=[ParsedSection(title="S", start="0:00", end="1:00")],
        segments=segments,
    )


def test_empty_storyboard(tmp_path):
    sb = _make_storyboard([])
    report = acquire_media(sb, tmp_path)
    assert report.queries_total == 0
    assert report.downloads_succeeded == 0


@patch("bee_video_editor.services.acquisition.download_media", return_value=Path("/tmp/clip.mp4"))
@patch("bee_video_editor.services.acquisition.search_stock")
def test_searches_and_downloads(mock_search, mock_download, tmp_path):
    from bee_video_editor.processors.media_search import SearchResult
    mock_search.return_value = [
        SearchResult(provider="pexels", media_type="video", id="1", url="", download_url="https://example.com/v.mp4")
    ]
    sb = _make_storyboard(["aerial farm"])
    report = acquire_media(sb, tmp_path)
    assert report.queries_total == 1
    assert report.queries_matched == 1
    assert report.downloads_succeeded == 1


@patch("bee_video_editor.services.acquisition.search_stock", return_value=[])
def test_no_results_reports_error(mock_search, tmp_path):
    sb = _make_storyboard(["extremely specific query"])
    report = acquire_media(sb, tmp_path)
    assert report.queries_matched == 0
    assert len(report.errors) == 1


@patch("bee_video_editor.services.acquisition.download_media", return_value=None)
@patch("bee_video_editor.services.acquisition.search_stock")
def test_download_failure(mock_search, mock_download, tmp_path):
    from bee_video_editor.processors.media_search import SearchResult
    mock_search.return_value = [
        SearchResult(provider="pexels", media_type="video", id="1", url="", download_url="https://example.com/v.mp4")
    ]
    sb = _make_storyboard(["police car"])
    report = acquire_media(sb, tmp_path)
    assert report.downloads_failed == 1
