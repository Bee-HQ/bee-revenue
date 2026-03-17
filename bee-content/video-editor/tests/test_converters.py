"""Tests for assembly guide → storyboard converter."""

import pytest

from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models import Project, Segment, SegmentType, Timecode


def _seg(start_m, start_s, end_m, end_s, seg_type, visual="", audio="", source="", section="TEST", subsection=""):
    return Segment(
        start=Timecode(start_m, start_s),
        end=Timecode(end_m, end_s),
        duration_seconds=(end_m * 60 + end_s) - (start_m * 60 + start_s),
        segment_type=seg_type,
        visual=visual,
        audio=audio,
        source_notes=source,
        section=section,
        subsection=subsection,
    )


def _project(segments):
    return Project(
        title="Test Project",
        total_duration="~10 minutes",
        resolution="1080p",
        format="MP4",
        segments=segments,
    )


class TestConvertBasics:
    def test_empty_project(self):
        sb = assembly_guide_to_storyboard(_project([]))
        assert sb.title == "Test Project"
        assert len(sb.segments) == 0

    def test_segment_id_format(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 15, SegmentType.NAR),
        ]))
        assert sb.segments[0].id == "0_00-0_15"

    def test_start_end_format(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(1, 30, 2, 0, SegmentType.NAR),
        ]))
        assert sb.segments[0].start == "1:30"
        assert sb.segments[0].end == "2:00"

    def test_duration_seconds_works(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 15, SegmentType.NAR),
        ]))
        assert sb.segments[0].duration_seconds == 15

    def test_title_from_subsection(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, subsection="The Hook"),
        ]))
        assert sb.segments[0].title == "The Hook"

    def test_title_fallback_to_section(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, section="COLD OPEN"),
        ]))
        assert sb.segments[0].title == "COLD OPEN"

    def test_title_fallback_to_timecode(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, section="", subsection=""),
        ]))
        assert sb.segments[0].title == "0:00-0:10"

    def test_section_time_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].section_time == ""

    def test_transition_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].transition == []

    def test_assigned_media_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].assigned_media == {}


class TestVisualConversion:
    def test_bible_code_parsed(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="[MAP-FLAT] Lowcountry region"),
        ]))
        assert sb.segments[0].visual[0].content_type == "MAP-FLAT"
        assert "Lowcountry region" in sb.segments[0].visual[0].content

    def test_bible_code_with_qualifier(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="[BROLL-DARK: atmospheric] slow aerial"),
        ]))
        assert sb.segments[0].visual[0].content_type == "BROLL-DARK"
        assert "atmospheric" in sb.segments[0].visual[0].content

    def test_backtick_prefix(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="`STOCK:` Rural estate at dusk"),
        ]))
        assert sb.segments[0].visual[0].content_type == "STOCK"

    def test_real_segment_type_default(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL, visual="Bodycam footage at scene"),
        ]))
        assert sb.segments[0].visual[0].content_type == "BODYCAM"

    def test_unknown_fallback(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="Some generic description"),
        ]))
        assert sb.segments[0].visual[0].content_type == "UNKNOWN"

    def test_lower_third_moves_to_overlay(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN,
                 visual='[LOWER-THIRD: "Alex Murdaugh — 4th Generation"]'),
        ]))
        assert len(sb.segments[0].visual) == 0
        assert len(sb.segments[0].overlay) == 1
        assert sb.segments[0].overlay[0].content_type == "LOWER-THIRD"


class TestAudioConversion:
    def test_nar_prefix_extracted(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='NAR: "This is the narrator"'),
        ]))
        assert sb.segments[0].audio[0].content_type == "NAR"
        # Quotes preserved — consumer's job to strip
        assert '"This is the narrator"' in sb.segments[0].audio[0].content

    def test_real_audio_prefix(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL, audio='REAL AUDIO: Deputy says hello'),
        ]))
        assert sb.segments[0].audio[0].content_type == "REAL AUDIO"

    def test_segment_type_default_nar(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='"Just some text without prefix"'),
        ]))
        assert sb.segments[0].audio[0].content_type == "NAR"

    def test_music_extracted_to_music_layer(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR,
                 audio='NAR: "Text here" + dark ambient music fades in'),
        ]))
        assert len(sb.segments[0].audio) == 1
        assert len(sb.segments[0].music) == 1
        assert sb.segments[0].music[0].content_type == "MUSIC"
        assert "dark ambient music fades in" in sb.segments[0].music[0].content

    def test_quotes_not_stripped(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='NAR: "Hello world"'),
        ]))
        # The converter must NOT strip quotes
        assert '"' in sb.segments[0].audio[0].content


class TestSourceConversion:
    def test_source_notes_split(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL,
                 source="footage/911-calls/clip.mkv\nfootage/bodycam/arrival.mp4"),
        ]))
        assert len(sb.segments[0].source) == 2
        assert sb.segments[0].source[0].content_type == "SOURCE"

    def test_empty_source(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, source=""),
        ]))
        assert len(sb.segments[0].source) == 0
