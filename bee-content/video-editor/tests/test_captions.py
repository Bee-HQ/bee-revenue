"""Tests for ASS caption generation."""

import re
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


from bee_video_editor.processors.captions import generate_captions_estimated
import pysubs2


class TestGenerateCaptionsEstimated:
    def test_karaoke_generates_ass(self):
        segments = [
            CaptionSegment("Hello world test", 0, 3000, "Narrator"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            result = generate_captions_estimated(segments, out, style="karaoke")
            assert result.exists()
            # Verify it's valid ASS
            subs = pysubs2.load(str(result))
            assert len(subs.events) == 1
            assert r"\kf" in subs.events[0].text

    def test_karaoke_timing_sums_exactly(self):
        segments = [
            CaptionSegment("This is a test sentence with several words", 0, 5000, "Narrator"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="karaoke")
            subs = pysubs2.load(str(out))
            event = subs.events[0]
            # Extract all \kfNN values and sum them
            kf_values = [int(m) for m in re.findall(r'\\kf(\d+)', event.text)]
            total_cs = 500  # 5000ms = 500cs
            assert sum(kf_values) == total_cs

    def test_phrase_mode(self):
        text = "This is a test sentence with many words in it"
        segments = [CaptionSegment(text, 0, 5000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="phrase")
            subs = pysubs2.load(str(out))
            # Phrase mode creates multiple events per segment
            assert len(subs.events) >= 2
            # Each event should have 3-5 words
            for event in subs.events:
                word_count = len(event.text.strip().split())
                assert 1 <= word_count <= 5

    def test_phrase_mode_short_segment(self):
        segments = [CaptionSegment("Two words", 0, 2000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="phrase")
            subs = pysubs2.load(str(out))
            assert len(subs.events) == 1

    def test_multiple_segments(self):
        segments = [
            CaptionSegment("First segment", 0, 3000, "Narrator"),
            CaptionSegment("Second segment", 3000, 6000, "RealAudio"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            subs = pysubs2.load(str(out))
            assert len(subs.events) == 2
            assert subs.events[0].style == "Narrator"
            assert subs.events[1].style == "RealAudio"

    def test_styles_defined(self):
        segments = [CaptionSegment("Test", 0, 1000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            subs = pysubs2.load(str(out))
            assert "Narrator" in subs.styles
            assert "NarratorPhrase" in subs.styles
            assert "RealAudio" in subs.styles

    def test_reparse_is_valid(self):
        segments = [
            CaptionSegment("Hello world", 0, 2000, "Narrator"),
            CaptionSegment("Real audio clip", 2000, 4000, "RealAudio"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            # Should not raise
            subs = pysubs2.load(str(out))
            resaved = Path(d) / "resaved.ass"
            subs.save(str(resaved))
            assert resaved.exists()
