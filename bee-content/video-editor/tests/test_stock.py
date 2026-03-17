"""Tests for stock footage search and download via Pexels API."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bee_video_editor.processors.stock import (
    PexelsResult,
    download_stock_clip,
    search_pexels,
)


class TestSearchPexels:
    def test_parses_video_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {
                    "id": 123,
                    "url": "https://pexels.com/video/123",
                    "duration": 15,
                    "width": 1920,
                    "height": 1080,
                    "video_files": [
                        {"id": 1, "quality": "hd", "width": 1920, "height": 1080,
                         "link": "https://cdn.pexels.com/123-hd.mp4", "file_type": "video/mp4"},
                        {"id": 2, "quality": "sd", "width": 640, "height": 360,
                         "link": "https://cdn.pexels.com/123-sd.mp4", "file_type": "video/mp4"},
                    ],
                },
            ],
            "total_results": 1,
        }

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("farm aerial", api_key="test-key")

        assert len(results) == 1
        assert results[0].id == 123
        assert results[0].duration == 15
        assert results[0].hd_url == "https://cdn.pexels.com/123-hd.mp4"

    def test_filters_by_min_duration(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {"id": 1, "url": "", "duration": 3, "width": 1920, "height": 1080,
                 "video_files": [{"id": 1, "quality": "hd", "width": 1920, "height": 1080,
                                  "link": "https://cdn/1.mp4", "file_type": "video/mp4"}]},
                {"id": 2, "url": "", "duration": 10, "width": 1920, "height": 1080,
                 "video_files": [{"id": 2, "quality": "hd", "width": 1920, "height": 1080,
                                  "link": "https://cdn/2.mp4", "file_type": "video/mp4"}]},
            ],
            "total_results": 2,
        }

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("test", api_key="key", min_duration=5)

        assert len(results) == 1
        assert results[0].id == 2

    def test_missing_api_key_raises(self):
        with pytest.raises(ValueError, match="PEXELS_API_KEY"):
            search_pexels("test", api_key=None)

    def test_api_error_raises(self):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            with pytest.raises(RuntimeError, match="Pexels API error"):
                search_pexels("test", api_key="bad-key")

    def test_empty_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"videos": [], "total_results": 0}

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("nonexistent", api_key="key")

        assert results == []


class TestDownloadStockClip:
    def _mock_stream(self, mock_httpx, status_code=200, chunks=None):
        """Set up mock for httpx.stream context manager."""
        if chunks is None:
            chunks = [b"\x00" * 100]
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.iter_bytes.return_value = iter(chunks)
        mock_httpx.stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_httpx.stream.return_value.__exit__ = MagicMock(return_value=False)
        return mock_response

    def test_downloads_to_path(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "stock" / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, chunks=[b"\x00" * 100])
                result = download_stock_clip("https://cdn/clip.mp4", output)

            assert result == output
            assert output.exists()
            assert output.read_bytes() == b"\x00" * 100

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "deep" / "nested" / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, chunks=[b"\x00"])
                download_stock_clip("https://cdn/clip.mp4", output)

            assert output.exists()

    def test_skips_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "clip.mp4"
            output.write_bytes(b"existing")

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                result = download_stock_clip("https://cdn/clip.mp4", output)

            mock_httpx.stream.assert_not_called()
            assert result == output

    def test_download_error_raises(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, status_code=404)
                with pytest.raises(RuntimeError, match="Download failed"):
                    download_stock_clip("https://cdn/clip.mp4", output)
