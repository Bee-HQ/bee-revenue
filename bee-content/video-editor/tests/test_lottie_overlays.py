"""Tests for Lottie animated overlays."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Skip all tests if lottie not installed
lottie = pytest.importorskip("lottie")

from bee_video_editor.processors.lottie_overlays import (
    create_lower_third_animation,
    generate_animated_lower_third,
    render_lottie_overlay,
    overlay_lottie,
    _has_cairo,
)


class TestCreateLowerThirdAnimation:
    def test_returns_animation(self):
        anim = create_lower_third_animation("Alex Murdaugh", "4th Generation")
        assert isinstance(anim, lottie.objects.Animation)
        assert anim.frame_rate == 30
        assert anim.width == 1920
        assert anim.height == 1080

    def test_duration(self):
        anim = create_lower_third_animation("Name", "Role", duration=5.0, fps=30)
        assert anim.out_point == 150  # 5s * 30fps

    def test_has_layers(self):
        anim = create_lower_third_animation("Name", "Role")
        assert len(anim.layers) >= 3  # bar, line, name text at minimum

    def test_custom_duration(self):
        anim = create_lower_third_animation("Name", "Role", duration=3.0)
        assert anim.out_point == 90  # 3s * 30fps


class TestRenderLottieOverlay:
    @patch("subprocess.run")
    def test_calls_ffmpeg(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        anim = create_lower_third_animation("Name", "Role", duration=1.0, fps=10)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "overlay.webm"
            # Mock Cairo export to create frame files
            with patch("bee_video_editor.processors.lottie_overlays._render_frames") as mock_render:
                mock_render.return_value = Path(d) / "frames"
                (Path(d) / "frames").mkdir()
                # Create dummy frame files
                for i in range(10):
                    (Path(d) / "frames" / f"frame_{i:04d}.png").touch()
                render_lottie_overlay(anim, out)
            mock_run.assert_called_once()
            # Verify ffmpeg command includes VP9 + alpha
            cmd = mock_run.call_args[0][0]
            assert "libvpx-vp9" in cmd
            assert "yuva420p" in cmd


class TestOverlayLottie:
    @patch("subprocess.run")
    def test_calls_ffmpeg_overlay(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "video.mp4"
            overlay = Path(d) / "overlay.webm"
            output = Path(d) / "output.mp4"
            video.touch()
            overlay.touch()
            overlay_lottie(video, overlay, output, start_time=2.0)
            # Called twice: once for ffprobe (duration), once for ffmpeg (overlay)
            assert mock_run.call_count == 2
            # Second call is the ffmpeg overlay command
            cmd_str = " ".join(mock_run.call_args_list[1][0][0])
            assert "overlay" in cmd_str


class TestGenerateAnimatedLowerThird:
    @patch("bee_video_editor.processors.lottie_overlays.render_lottie_overlay")
    def test_chains_create_and_render(self, mock_render):
        mock_render.return_value = Path("/fake/output.webm")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "lower-third.webm"
            mock_render.return_value = out
            result = generate_animated_lower_third("Name", "Role", out)
            mock_render.assert_called_once()
            # Verify the animation passed to render has correct properties
            anim = mock_render.call_args[0][0]
            assert isinstance(anim, lottie.objects.Animation)


class TestHasCairo:
    def test_returns_bool(self):
        result = _has_cairo()
        assert isinstance(result, bool)
