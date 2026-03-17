"""Tests for ASS caption generation."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.processors.captions import (
    CaptionSegment,
    extract_caption_segments,
)
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _make_segment(id, start, end, title, audio_entries):
    """Helper to create a StoryboardSegment with audio entries."""
    return StoryboardSegment(
        id=id, start=start, end=end, title=title,
        section="TEST", section_time=f"{start} - {end}", subsection="",
        audio=[
            LayerEntry(content=text, content_type=ctype, time_start=ts, time_end=te, raw=text)
            for text, ctype, ts, te in audio_entries
        ],
    )


class TestCaptionSegment:
    def test_basic(self):
        seg = CaptionSegment(text="Hello world", start_ms=0, end_ms=5000, style_name="Narrator")
        assert seg.text == "Hello world"
        assert seg.start_ms == 0
        assert seg.end_ms == 5000


class TestExtractCaptionSegments:
    def test_extracts_nar_entries(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("This is the narrator speaking.", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].text == "This is the narrator speaking."
        assert result[0].start_ms == 0
        assert result[0].end_ms == 10000
        assert result[0].style_name == "Narrator"

    def test_extracts_real_audio(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_10-0_20", "0:10", "0:20", "911", [
                ("I need help!", "REAL AUDIO", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].style_name == "RealAudio"

    def test_uses_time_range_if_present(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_30-0_40", "0:30", "0:40", "MIX", [
                ("Deputy speaks here", "REAL AUDIO", "0:30", "0:35"),
                ("Narrator bridges", "NAR", "0:35", "0:40"),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 2
        assert result[0].start_ms == 30000
        assert result[0].end_ms == 35000
        assert result[1].start_ms == 35000
        assert result[1].end_ms == 40000

    def test_strips_quotes_and_trailing_notes(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ('"This is quoted text" + dark ambient music', "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert result[0].text == "This is quoted text"

    def test_skips_empty_text(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 0

    def test_skips_non_caption_types(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("Background music", "MUSIC", None, None),
                ("Narrator line", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].text == "Narrator line"
