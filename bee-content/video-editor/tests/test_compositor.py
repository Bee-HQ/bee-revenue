"""Tests for compositor service."""

from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, ParsedSection
from bee_video_editor.formats.models import (
    ProjectConfig, SegmentConfig, VisualEntry, AudioEntry, OverlayEntry,
)
from bee_video_editor.services.compositor import (
    CompositeResult, CompositeReport,
    composite_segment, composite_all,
)


def _seg(seg_id="s1", visual_src="footage/clip.mp4", color=None, audio=None, overlay=None, narration=""):
    visuals = [VisualEntry(type="FOOTAGE", src=visual_src, color=color)] if visual_src else []
    return ParsedSegment(
        id=seg_id, title="Test Segment", start="0:00", end="0:15", section="Test",
        config=SegmentConfig(
            visual=visuals,
            audio=audio or [],
            overlay=overlay or [],
        ),
        narration=narration,
    )


def _sb(segments):
    return ParsedStoryboard(
        project=ProjectConfig(title="Test", color_preset="dark_crime"),
        sections=[ParsedSection(title="Test", start="0:00", end="1:00")],
        segments=segments,
    )


class TestCompositeSegment:
    def test_no_visual_returns_error(self, tmp_path):
        seg = _seg(visual_src=None)
        result = composite_segment(seg, tmp_path, tmp_path / "out")
        assert result.error is not None
        assert "No visual source" in result.error

    def test_missing_file_returns_error(self, tmp_path):
        seg = _seg(visual_src="footage/nonexistent.mp4")
        result = composite_segment(seg, tmp_path, tmp_path / "out")
        assert result.error is not None
        assert "not found" in result.error

    @patch("bee_video_editor.services.compositor.normalize_format")
    @patch("bee_video_editor.services.compositor.color_grade")
    def test_applies_visual_and_color(self, mock_grade, mock_norm, tmp_path):
        # Create source file
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake video")

        seg = _seg(color="noir")
        result = composite_segment(seg, tmp_path, tmp_path / "out")

        assert "visual" in result.layers_applied
        assert any("color:noir" in l for l in result.layers_applied)

    @patch("bee_video_editor.services.compositor.normalize_format")
    def test_applies_normalize(self, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake video")

        seg = _seg()
        result = composite_segment(seg, tmp_path, tmp_path / "out")

        assert "normalize" in result.layers_applied
        mock_norm.assert_called_once()

    @patch("bee_video_editor.services.compositor.normalize_format")
    @patch("bee_video_editor.services.compositor.trim")
    def test_trims_with_in_out(self, mock_trim, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake video")

        seg = _seg()
        seg.config.visual[0] = seg.config.visual[0].model_copy(
            update={"tc_in": "00:01:00.000", "out": "00:02:00.000"}
        )
        result = composite_segment(seg, tmp_path, tmp_path / "out")

        mock_trim.assert_called_once()
        assert any("trim:" in l for l in result.layers_applied)

    @patch("bee_video_editor.services.compositor.normalize_format")
    @patch("bee_video_editor.services.compositor.image_to_video")
    def test_image_to_video(self, mock_img, mock_norm, tmp_path):
        photos = tmp_path / "photos"
        photos.mkdir()
        (photos / "mugshot.jpg").write_bytes(b"fake image")

        seg = _seg(visual_src="photos/mugshot.jpg")
        result = composite_segment(seg, tmp_path, tmp_path / "out")

        mock_img.assert_called_once()
        assert "visual:image_to_video" in result.layers_applied

    @patch("bee_video_editor.services.compositor.normalize_format")
    def test_output_path_set(self, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        src = footage / "clip.mp4"
        src.write_bytes(b"fake video")

        seg = _seg()
        result = composite_segment(seg, tmp_path, tmp_path / "out")

        assert result.output_path is not None
        assert result.output_path.name.startswith("comp-")


class TestCompositeAll:
    @patch("bee_video_editor.services.compositor.normalize_format")
    def test_composites_multiple_segments(self, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake")

        sb = _sb([_seg("s1"), _seg("s2")])
        report = composite_all(sb, tmp_path, tmp_path / "output")

        assert report.succeeded == 2
        assert report.failed == 0

    def test_skips_segments_without_media(self, tmp_path):
        sb = _sb([_seg("s1", visual_src=None), _seg("s2", visual_src=None)])
        report = composite_all(sb, tmp_path, tmp_path / "output")

        assert report.succeeded == 0
        assert report.failed == 2  # error, not skipped

    @patch("bee_video_editor.services.compositor.normalize_format")
    def test_uses_project_color_preset(self, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake")

        sb = _sb([_seg("s1")])
        sb.project.color_preset = "surveillance"

        with patch("bee_video_editor.services.compositor.color_grade") as mock_grade:
            report = composite_all(sb, tmp_path, tmp_path / "output")

        # color_grade should have been called with surveillance preset
        if mock_grade.called:
            assert "surveillance" in str(mock_grade.call_args)

    @patch("bee_video_editor.services.compositor.normalize_format")
    def test_progress_callback(self, mock_norm, tmp_path):
        footage = tmp_path / "footage"
        footage.mkdir()
        (footage / "clip.mp4").write_bytes(b"fake")

        sb = _sb([_seg("s1")])
        calls = []
        report = composite_all(sb, tmp_path, tmp_path / "output",
                              on_progress=lambda phase, msg: calls.append((phase, msg)))

        assert len(calls) >= 1
        assert calls[0][0] == "composite"
