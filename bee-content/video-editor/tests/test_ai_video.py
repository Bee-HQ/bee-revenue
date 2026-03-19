"""Tests for AI video generation processor."""

from pathlib import Path
from unittest.mock import patch

from bee_video_editor.processors.ai_video import (
    GenerationResult, generate_clip, list_providers,
)


class TestListProviders:
    def test_stub_always_available(self):
        providers = list_providers()
        assert "stub" in providers

    @patch.dict("os.environ", {"KLING_API_KEY": "test"})
    def test_kling_with_key(self):
        providers = list_providers()
        assert "kling" in providers

    @patch.dict("os.environ", {}, clear=True)
    def test_kling_without_key(self):
        providers = list_providers()
        assert "kling" not in providers


class TestGenerateClip:
    @patch("subprocess.run")
    def test_stub_calls_ffmpeg(self, mock_run, tmp_path):
        mock_run.return_value = None
        result = generate_clip("test prompt", tmp_path, provider="stub")
        assert result.provider == "stub"
        assert result.error is None
        mock_run.assert_called_once()

    def test_unknown_provider(self, tmp_path):
        result = generate_clip("test", tmp_path, provider="nonexistent")
        assert result.error is not None
        assert "Unknown provider" in result.error

    @patch.dict("os.environ", {}, clear=True)
    def test_kling_no_key(self, tmp_path):
        result = generate_clip("test", tmp_path, provider="kling")
        assert result.error is not None
        assert "KLING_API_KEY" in result.error

    @patch.dict("os.environ", {}, clear=True)
    def test_veo_no_key(self, tmp_path):
        result = generate_clip("test", tmp_path, provider="veo")
        assert result.error is not None
        assert "VEO_API_KEY" in result.error

    @patch("subprocess.run", side_effect=FileNotFoundError("ffmpeg not found"))
    def test_stub_ffmpeg_missing(self, mock_run, tmp_path):
        result = generate_clip("test", tmp_path, provider="stub")
        assert result.error is not None
