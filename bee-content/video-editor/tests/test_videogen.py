"""Tests for video generation provider interface and stub."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.processors.videogen import (
    GenerationRequest,
    GenerationResult,
    generate_clip,
    list_providers,
)


class TestGenerationRequest:
    def test_basic_request(self):
        req = GenerationRequest(prompt="aerial shot of farm at dusk", duration=5.0)
        assert req.prompt == "aerial shot of farm at dusk"
        assert req.duration == 5.0
        assert req.reference_images == []
        assert req.reference_videos == []
        assert req.width == 1280
        assert req.height == 720

    def test_request_with_references(self):
        req = GenerationRequest(
            prompt="match this style",
            duration=3.0,
            reference_images=[Path("/img/ref.jpg")],
            reference_videos=[Path("/vid/ref.mp4")],
        )
        assert len(req.reference_images) == 1
        assert len(req.reference_videos) == 1


class TestListProviders:
    def test_stub_always_available(self):
        providers = list_providers()
        assert "stub" in providers

    def test_returns_dict_with_descriptions(self):
        providers = list_providers()
        assert isinstance(providers, dict)
        assert isinstance(providers["stub"], str)


class TestGenerateClip:
    def test_stub_creates_placeholder(self):
        req = GenerationRequest(prompt="test prompt", duration=3.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "generated.mp4"
            result = generate_clip(req, output, provider="stub")
            assert result.provider == "stub"
            assert result.output_path == output
            assert result.success is True
            assert output.exists()

    def test_stub_output_has_content(self):
        req = GenerationRequest(prompt="test", duration=2.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            generate_clip(req, output, provider="stub")
            assert output.stat().st_size > 0

    def test_unknown_provider_raises(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with pytest.raises(ValueError, match="Unknown video generation provider"):
                generate_clip(req, output, provider="nonexistent")

    def test_creates_parent_dirs(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "deep" / "nested" / "out.mp4"
            result = generate_clip(req, output, provider="stub")
            assert result.success
            assert output.exists()

    def test_result_includes_metadata(self):
        req = GenerationRequest(prompt="a beautiful sunset", duration=5.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            result = generate_clip(req, output, provider="stub")
            assert result.prompt == "a beautiful sunset"
            assert result.duration == 5.0
