"""Tests for map generation (processors/maps.py).

Mocks staticmaps.Context.render_pillow to avoid network calls while
still exercising the full post-processing pipeline.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# Skip entire module if py-staticmaps not installed
pytest.importorskip("staticmaps")

from bee_video_editor.processors.maps import (  # noqa: E402
    MapLocation,
    MapRoute,
    _apply_dark_grade,
    _apply_vignette,
    map_flat,
    map_pulse,
    map_route,
    map_tactical,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dummy_rgba(width: int = 1920, height: int = 1080) -> Image.Image:
    """Return a solid grey RGBA image — stand-in for a real tile render."""
    return Image.new("RGBA", (width, height), (100, 100, 100, 255))


# ---------------------------------------------------------------------------
# Post-processing helpers
# ---------------------------------------------------------------------------

class TestApplyDarkGrade:
    def test_darkens_image(self):
        img = Image.new("RGB", (100, 100), (200, 200, 200))
        result = _apply_dark_grade(img)
        avg = sum(result.getpixel((50, 50))) / 3
        assert avg < 100  # significantly darker than the 200-grey input

    def test_returns_rgb_image(self):
        img = Image.new("RGB", (100, 100), (128, 128, 128))
        result = _apply_dark_grade(img)
        assert result.mode == "RGB"

    def test_preserves_size(self):
        img = Image.new("RGB", (1920, 1080), (128, 128, 128))
        result = _apply_dark_grade(img)
        assert result.size == (1920, 1080)


class TestApplyVignette:
    def test_applies_without_crash(self):
        img = Image.new("RGB", (1920, 1080), (128, 128, 128))
        result = _apply_vignette(img)
        assert result.size == (1920, 1080)

    def test_returns_rgb(self):
        img = Image.new("RGB", (200, 200), (200, 200, 200))
        result = _apply_vignette(img)
        assert result.mode == "RGB"

    def test_edges_are_darker_than_center(self):
        img = Image.new("RGB", (400, 400), (200, 200, 200))
        result = _apply_vignette(img)
        # Corner (0,0) should be darker than center
        corner = sum(result.getpixel((0, 0))) / 3
        center = sum(result.getpixel((200, 200))) / 3
        assert corner < center


# ---------------------------------------------------------------------------
# map_flat
# ---------------------------------------------------------------------------

class TestMapFlat:
    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_creates_png(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "flat.png"
        result = map_flat(32.84, -80.78, out, zoom=10)

        assert result == out
        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_output_is_1920x1080(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "flat.png"
        result = map_flat(32.84, -80.78, out, zoom=10)

        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_with_markers(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        markers = [MapLocation(lat=32.84, lng=-80.78, label="Target", pin_color="red")]
        out = tmp_path / "flat_markers.png"
        result = map_flat(32.84, -80.78, out, markers=markers)

        assert result.exists()
        # Verify add_object was called for the marker
        assert mock_ctx.add_object.called

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_creates_parent_dirs(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "deep" / "nested" / "flat.png"
        result = map_flat(32.84, -80.78, out)
        assert result.exists()


# ---------------------------------------------------------------------------
# map_tactical
# ---------------------------------------------------------------------------

class TestMapTactical:
    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_creates_png(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "tactical.png"
        result = map_tactical(32.84, -80.78, out)

        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_output_is_1920x1080(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "tactical.png"
        result = map_tactical(32.84, -80.78, out)
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_label_does_not_crash(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "tactical_label.png"
        result = map_tactical(32.84, -80.78, out, label="Remote Wilderness")
        assert result.exists()


# ---------------------------------------------------------------------------
# map_pulse
# ---------------------------------------------------------------------------

class TestMapPulse:
    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_creates_png(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "pulse.png"
        result = map_pulse(32.84, -80.78, out)

        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_output_is_1920x1080(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "pulse.png"
        result = map_pulse(32.84, -80.78, out)
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_with_label(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "pulse_label.png"
        result = map_pulse(32.84, -80.78, out, label="Moselle Estate")
        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_marker_added(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "pulse.png"
        map_pulse(32.84, -80.78, out)
        assert mock_ctx.add_object.called


# ---------------------------------------------------------------------------
# map_route
# ---------------------------------------------------------------------------

class TestMapRoute:
    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_creates_png(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "route.png"
        points = [(32.84, -80.78), (32.90, -80.70)]
        result = map_route(points, out)

        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_output_is_1920x1080(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "route.png"
        points = [(32.84, -80.78), (32.90, -80.70)]
        result = map_route(points, out)
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_with_label(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "route_label.png"
        points = [(32.84, -80.78), (32.90, -80.70)]
        result = map_route(points, out, label="Escape Route")
        assert result.exists()

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_line_and_markers_added(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "route.png"
        points = [(32.84, -80.78), (32.90, -80.70)]
        map_route(points, out)
        # Line + 2 markers = 3 add_object calls
        assert mock_ctx.add_object.call_count == 3

    def test_empty_points_raises(self, tmp_path):
        out = tmp_path / "route.png"
        with pytest.raises(ValueError, match="at least one point"):
            map_route([], out)

    @patch("bee_video_editor.processors.maps.staticmaps.Context")
    def test_single_point(self, MockContext, tmp_path):
        mock_ctx = MagicMock()
        mock_ctx.render_pillow.return_value = _dummy_rgba()
        MockContext.return_value = mock_ctx

        out = tmp_path / "route_single.png"
        # Single point: no line (needs ≥2), only 1 start marker
        map_route([(32.84, -80.78)], out)
        assert out.exists()
        assert mock_ctx.add_object.call_count == 1


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_map_location_defaults(self):
        loc = MapLocation(lat=32.84, lng=-80.78)
        assert loc.label == ""
        assert loc.pin_color == "red"

    def test_map_route_defaults(self):
        route = MapRoute(points=[(1.0, 2.0)])
        assert route.color == "red"
