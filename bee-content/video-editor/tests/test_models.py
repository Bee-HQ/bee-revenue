"""Tests for data models."""

import pytest

from bee_video_editor.models import (
    PostChecklistItem,
    PreProductionAsset,
    Project,
    Segment,
    SegmentType,
    Timecode,
)
from bee_video_editor.models_storyboard import ChecklistItem, Storyboard


class TestTimecode:
    def test_parse_basic(self):
        tc = Timecode.parse("2:30")
        assert tc.minutes == 2
        assert tc.seconds == 30

    def test_parse_zero(self):
        tc = Timecode.parse("0:00")
        assert tc.total_seconds == 0

    def test_parse_large(self):
        tc = Timecode.parse("55:00")
        assert tc.total_seconds == 3300

    def test_parse_with_spaces(self):
        tc = Timecode.parse(" 1:15 ")
        assert tc.minutes == 1
        assert tc.seconds == 15

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            Timecode.parse("invalid")

    def test_total_seconds(self):
        tc = Timecode(minutes=2, seconds=30)
        assert tc.total_seconds == 150

    def test_str(self):
        tc = Timecode(minutes=2, seconds=5)
        assert str(tc) == "2:05"


class TestSegmentType:
    def test_all_types(self):
        assert SegmentType("NAR") == SegmentType.NAR
        assert SegmentType("REAL") == SegmentType.REAL
        assert SegmentType("GEN") == SegmentType.GEN
        assert SegmentType("MIX") == SegmentType.MIX
        assert SegmentType("SFX") == SegmentType.SFX
        assert SegmentType("SPONSOR") == SegmentType.SPONSOR

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            SegmentType("INVALID")


class TestProject:
    def _make_segment(self, start_min, start_sec, end_min, end_sec, seg_type, section="TEST"):
        start = Timecode(start_min, start_sec)
        end = Timecode(end_min, end_sec)
        dur = end.total_seconds - start.total_seconds
        return Segment(
            start=start, end=end, duration_seconds=dur,
            segment_type=seg_type, visual="", audio="",
            source_notes="", section=section, subsection="",
        )

    def test_total_segments(self):
        project = Project(title="Test", total_duration="5m", resolution="1080p", format="MP4")
        project.segments = [
            self._make_segment(0, 0, 0, 15, SegmentType.NAR),
            self._make_segment(0, 15, 0, 30, SegmentType.REAL),
        ]
        assert project.total_segments == 2

    def test_sections(self):
        project = Project(title="Test", total_duration="5m", resolution="1080p", format="MP4")
        project.segments = [
            self._make_segment(0, 0, 0, 15, SegmentType.NAR, "COLD OPEN"),
            self._make_segment(0, 15, 0, 30, SegmentType.REAL, "COLD OPEN"),
            self._make_segment(0, 30, 1, 0, SegmentType.MIX, "ACT 1"),
        ]
        assert project.sections == ["COLD OPEN", "ACT 1"]

    def test_segments_by_type(self):
        project = Project(title="Test", total_duration="5m", resolution="1080p", format="MP4")
        project.segments = [
            self._make_segment(0, 0, 0, 15, SegmentType.NAR),
            self._make_segment(0, 15, 0, 30, SegmentType.REAL),
            self._make_segment(0, 30, 0, 45, SegmentType.NAR),
        ]
        nar_segs = project.segments_by_type(SegmentType.NAR)
        assert len(nar_segs) == 2

    def test_summary(self):
        project = Project(title="Test", total_duration="5m", resolution="1080p", format="MP4")
        project.segments = [
            self._make_segment(0, 0, 0, 15, SegmentType.NAR, "INTRO"),
            self._make_segment(0, 15, 0, 30, SegmentType.REAL, "INTRO"),
        ]
        project.pre_production = [
            PreProductionAsset("Audio", "Generate TTS", done=True),
            PreProductionAsset("Graphics", "Lower thirds", done=False),
        ]
        project.post_checklist = [
            PostChecklistItem("Add music", done=False),
        ]

        s = project.summary()
        assert s["total_segments"] == 2
        assert s["segment_type_counts"]["NAR"] == 1
        assert s["segment_type_counts"]["REAL"] == 1
        assert s["pre_production_assets"] == 2
        assert s["pre_production_done"] == 1
        assert s["post_checklist_items"] == 1
        assert s["post_checklist_done"] == 0


class TestChecklistItem:
    def test_checklist_item(self):
        item = ChecklistItem(text="Generate TTS narration", checked=True, category="audio")
        assert item.text == "Generate TTS narration"
        assert item.checked is True
        assert item.category == "audio"

    def test_checklist_item_unchecked(self):
        item = ChecklistItem(text="Export final video", checked=False, category="post")
        assert item.checked is False


class TestStoryboardMetadata:
    def test_storyboard_metadata_defaults(self):
        sb = Storyboard(title="Test")
        assert sb.total_duration is None
        assert sb.resolution is None
        assert sb.format is None
        assert sb.pre_production == []
        assert sb.post_checklist == []

    def test_storyboard_with_metadata(self):
        sb = Storyboard(
            title="Alex Murdaugh",
            total_duration="55:00",
            resolution="1080p",
            format="MP4",
            pre_production=[
                ChecklistItem(text="Generate TTS", checked=True, category="audio"),
                ChecklistItem(text="Create lower thirds", checked=False, category="graphics"),
            ],
            post_checklist=[
                ChecklistItem(text="Color grade", checked=False, category="post"),
            ],
        )
        assert sb.total_duration == "55:00"
        assert sb.resolution == "1080p"
        assert sb.format == "MP4"
        assert len(sb.pre_production) == 2
        assert sb.pre_production[0].text == "Generate TTS"
        assert sb.pre_production[0].checked is True
        assert sb.pre_production[1].category == "graphics"
        assert len(sb.post_checklist) == 1
        assert sb.post_checklist[0].text == "Color grade"
