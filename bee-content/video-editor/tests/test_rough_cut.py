"""Tests for rough cut export — fast 720p structure review."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from bee_video_editor.formats.models import (
    ProjectConfig,
    SegmentConfig,
    VisualEntry,
)
from bee_video_editor.formats.parser import ParsedSegment, ParsedStoryboard
from bee_video_editor.services.production import ProductionConfig, rough_cut_export


def _seg(id: str, visual_src: str | None = None) -> ParsedSegment:
    visual = [VisualEntry(type="FOOTAGE", src=visual_src)] if visual_src else []
    return ParsedSegment(
        id=id, start="0:00", end="0:10", title=id,
        section="X",
        config=SegmentConfig(visual=visual),
        narration="",
    )


def _parsed(segments: list[ParsedSegment]) -> ParsedStoryboard:
    return ParsedStoryboard(
        project=ProjectConfig(title="Test", version=1),
        sections=[],
        segments=segments,
    )


class TestRoughCutExport:
    def test_collects_assigned_media(self):
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d)
            (proj_dir / "footage").mkdir()
            clip_a = proj_dir / "footage" / "a.mp4"
            clip_b = proj_dir / "footage" / "b.mp4"
            clip_a.write_bytes(b"\x00" * 100)
            clip_b.write_bytes(b"\x00" * 100)

            parsed = _parsed([
                _seg("sa", str(clip_a)),
                _seg("sb", str(clip_b)),
            ])
            config = ProductionConfig(project_dir=proj_dir)

            with patch("bee_video_editor.services.production.normalize_format") as mock_norm, \
                 patch("bee_video_editor.services.production.concat_segments") as mock_concat:
                mock_norm.side_effect = lambda i, o, **kw: Path(o)
                mock_concat.return_value = Path("out.mp4")
                result = rough_cut_export(parsed, config)

            assert mock_norm.call_count == 2
            for c in mock_norm.call_args_list:
                assert c.kwargs["width"] == 1280
                assert c.kwargs["height"] == 720
            mock_concat.assert_called_once()
            concat_output = mock_concat.call_args[0][1]
            assert str(concat_output).endswith("rough/rough_cut.mp4")
            assert result is not None

    def test_skips_segments_without_media(self):
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d)
            clip = proj_dir / "a.mp4"
            clip.write_bytes(b"\x00")

            parsed = _parsed([
                _seg("sa", str(clip)),
                _seg("sb"),  # no media
            ])
            config = ProductionConfig(project_dir=proj_dir)

            with patch("bee_video_editor.services.production.normalize_format") as mock_norm, \
                 patch("bee_video_editor.services.production.concat_segments") as mock_concat:
                mock_norm.side_effect = lambda i, o, **kw: Path(o)
                mock_concat.return_value = Path("out.mp4")
                rough_cut_export(parsed, config)

            assert mock_norm.call_count == 1

    def test_skips_deleted_media_files(self):
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d)
            parsed = _parsed([_seg("sa", "/nonexistent/deleted.mp4")])
            config = ProductionConfig(project_dir=proj_dir)
            result = rough_cut_export(parsed, config)
            assert result is None

    def test_returns_none_when_no_media(self):
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d)
            parsed = _parsed([_seg("sa")])
            config = ProductionConfig(project_dir=proj_dir)
            result = rough_cut_export(parsed, config)
            assert result is None
