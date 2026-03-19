"""Tests for OTIO timeline export."""

import tempfile
from pathlib import Path

import pytest

otio = pytest.importorskip("opentimelineio")

from bee_video_editor.exporters.otio_export import storyboard_to_otio, export_otio
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _seg(id, start, end, title, section="TEST", visual=None, audio=None, overlay=None):
    return StoryboardSegment(
        id=id, start=start, end=end, title=title,
        section=section, section_time="", subsection="",
        visual=visual or [],
        audio=audio or [],
        overlay=overlay or [],
    )


class TestStoryboardToOtio:
    def test_empty_storyboard(self):
        sb = Storyboard(title="Empty", production_rules=ProductionRules())
        tl = storyboard_to_otio(sb)
        assert tl.name == "Empty"
        assert len(tl.tracks) == 2

    def test_basic_timeline(self):
        sb = Storyboard(title="Test", segments=[
            _seg("0_00-0_10", "0:00", "0:10", "HOOK", section="COLD OPEN",
                 visual=[LayerEntry(content="test", content_type="BODYCAM", raw="")],
                 audio=[LayerEntry(content="narrator text", content_type="NAR", raw="")]),
            _seg("0_10-0_20", "0:10", "0:20", "INTRO", section="COLD OPEN"),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        video_track = tl.tracks[0]
        assert len(list(video_track)) == 2

        # First clip has metadata
        clip = list(video_track)[0]
        assert "bee_video" in clip.metadata
        assert clip.metadata["bee_video"]["segment_id"] == "0_00-0_10"

    def test_section_markers(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "A", section="ACT 1"),
            _seg("s2", "0:10", "0:20", "B", section="ACT 1"),
            _seg("s3", "0:20", "0:30", "C", section="ACT 2"),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clips = list(tl.tracks[0])
        # First clip of ACT 1 should have marker
        assert len(clips[0].markers) == 1
        assert clips[0].markers[0].name == "ACT 1"
        # Second clip of ACT 1 should NOT have marker
        assert len(clips[1].markers) == 0
        # First clip of ACT 2 should have marker
        assert len(clips[2].markers) == 1

    def test_assigned_media_becomes_reference(self):
        seg = _seg("s1", "0:00", "0:10", "TEST")
        seg.assigned_media = {"visual:0": "/path/to/clip.mp4"}
        sb = Storyboard(title="Test", segments=[seg], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clip = list(tl.tracks[0])[0]
        assert isinstance(clip.media_reference, otio.schema.ExternalReference)
        assert clip.media_reference.target_url == "/path/to/clip.mp4"

    def test_audio_track(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "NAR",
                 audio=[LayerEntry(content="text", content_type="NAR", raw="")]),
            _seg("s2", "0:10", "0:20", "SILENT"),  # no audio
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        audio_items = list(tl.tracks[1])
        assert len(audio_items) == 2
        # First should be clip (has narration)
        assert isinstance(audio_items[0], otio.schema.Clip)
        # Second should be gap (no audio)
        assert isinstance(audio_items[1], otio.schema.Gap)

    def test_zero_duration_segments_skipped(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:00", "ZERO DUR"),  # zero duration
            _seg("s2", "0:00", "0:10", "GOOD"),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clips = list(tl.tracks[0])
        assert len(clips) == 1

    def test_clip_name_includes_id_and_title(self):
        sb = Storyboard(title="Test", segments=[
            _seg("0_00-0_10", "0:00", "0:10", "THE HOOK"),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clip = list(tl.tracks[0])[0]
        assert "0_00-0_10" in clip.name
        assert "THE HOOK" in clip.name

    def test_track_kinds(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        tl = storyboard_to_otio(sb)
        assert tl.tracks[0].kind == otio.schema.TrackKind.Video
        assert tl.tracks[1].kind == otio.schema.TrackKind.Audio

    def test_track_names(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        tl = storyboard_to_otio(sb)
        assert tl.tracks[0].name == "V1"
        assert tl.tracks[1].name == "A1"

    def test_metadata_visual_codes(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "TEST",
                 visual=[
                     LayerEntry(content="qualifier", content_type="BROLL-DARK", raw=""),
                     LayerEntry(content="qualifier2", content_type="FOOTAGE", raw=""),
                 ]),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clip = list(tl.tracks[0])[0]
        vc = clip.metadata["bee_video"]["visual_codes"]
        assert len(vc) == 2
        assert vc[0]["type"] == "BROLL-DARK"
        assert vc[1]["type"] == "FOOTAGE"

    def test_real_audio_also_creates_audio_clip(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "REAL",
                 audio=[LayerEntry(content="ambient", content_type="REAL_AUDIO", raw="")]),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        audio_items = list(tl.tracks[1])
        assert isinstance(audio_items[0], otio.schema.Clip)

    def test_missing_reference_when_no_assigned_media(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "TEST"),
        ], production_rules=ProductionRules())

        tl = storyboard_to_otio(sb)
        clip = list(tl.tracks[0])[0]
        assert isinstance(clip.media_reference, otio.schema.MissingReference)


class TestExportOtio:
    def test_writes_file(self):
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "TEST"),
        ], production_rules=ProductionRules())

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "timeline.otio"
            result = export_otio(sb, out)
            assert result.exists()
            assert result.stat().st_size > 0

            # Verify it can be read back
            loaded = otio.adapters.read_from_file(str(result))
            assert loaded.name == "Test"

    def test_roundtrip_metadata(self):
        sb = Storyboard(title="Roundtrip", segments=[
            _seg("s1", "0:00", "0:10", "TEST",
                 visual=[LayerEntry(content="qualifier", content_type="BROLL-DARK", raw="")]),
        ], production_rules=ProductionRules())

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "timeline.otio"
            export_otio(sb, out)

            loaded = otio.adapters.read_from_file(str(out))
            clip = list(loaded.tracks[0])[0]
            assert clip.metadata["bee_video"]["visual_codes"][0]["type"] == "BROLL-DARK"

    def test_creates_parent_dirs(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "nested" / "deep" / "timeline.otio"
            result = export_otio(sb, out)
            assert result.exists()

    def test_returns_path(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "timeline.otio"
            result = export_otio(sb, out)
            assert isinstance(result, Path)
            assert result == out

    def test_fps_affects_duration(self):
        """Different fps should yield different rational time denominators."""
        sb = Storyboard(title="Test", segments=[
            _seg("s1", "0:00", "0:10", "TEST"),
        ], production_rules=ProductionRules())

        tl_30 = storyboard_to_otio(sb, fps=30.0)
        tl_24 = storyboard_to_otio(sb, fps=24.0)

        clip_30 = list(tl_30.tracks[0])[0]
        clip_24 = list(tl_24.tracks[0])[0]

        # 10 seconds * 30fps = 300 frames; 10 seconds * 24fps = 240 frames
        assert clip_30.source_range.duration.value == pytest.approx(10 * 30.0)
        assert clip_24.source_range.duration.value == pytest.approx(10 * 24.0)
