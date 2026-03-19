"""Tests for media matching service."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, ParsedSection
from bee_video_editor.formats.models import ProjectConfig, SegmentConfig, VisualEntry
from bee_video_editor.services.matcher import auto_assign_media, _tokenize


def _make_segment(seg_id, visual_src=None, visual_query=None, visual_type="STOCK", narration=""):
    visuals = []
    if visual_src or visual_query or visual_type:
        visuals = [VisualEntry(type=visual_type, src=visual_src, query=visual_query)]
    return ParsedSegment(
        id=seg_id, title=seg_id.replace("-", " ").title(),
        start="0:00", end="0:10", section="Test",
        config=SegmentConfig(visual=visuals),
        narration=narration,
    )


def _make_storyboard(segments):
    return ParsedStoryboard(
        project=ProjectConfig(title="Test"),
        sections=[ParsedSection(title="Test", start="0:00", end="1:00")],
        segments=segments,
    )


class TestTokenize:
    def test_basic(self):
        tokens = _tokenize("police cars at night")
        assert "police" in tokens
        assert "cars" in tokens
        assert "night" in tokens
        assert "at" not in tokens

    def test_filename(self):
        tokens = _tokenize("pexels-123-police-car-night")
        assert "police" in tokens
        assert "car" in tokens
        assert "night" in tokens

    def test_short_words_filtered(self):
        assert len(_tokenize("a on to go")) == 0

    def test_case_insensitive(self):
        tokens = _tokenize("Police CARS Night")
        assert "police" in tokens
        assert "cars" in tokens


class TestAutoAssignMedia:
    def test_keyword_match(self):
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "police-cars-night-4821.mp4").write_bytes(b"x")
            (stock / "courthouse-exterior-1234.mp4").write_bytes(b"x")

            seg1 = _make_segment("police-night", visual_query="Police cars driving at night")
            seg2 = _make_segment("courthouse", visual_query="Courthouse exterior establishing shot")
            sb = _make_storyboard([seg1, seg2])
            plan = auto_assign_media(sb, [stock])

        assert len(plan.assignments) == 2
        assert plan.unmatched == []
        s1 = next(a for a in plan.assignments if a.segment_id == "police-night")
        assert "police" in s1.file_path.name

    def test_src_match(self):
        with tempfile.TemporaryDirectory() as d:
            footage = Path(d) / "footage"
            footage.mkdir()
            (footage / "911-call-clip.mp4").write_bytes(b"x")

            seg = _make_segment("s1", visual_src="footage/911-call-clip.mp4")
            sb = _make_storyboard([seg])
            plan = auto_assign_media(sb, [footage])

        assert len(plan.assignments) == 1
        assert plan.assignments[0].confidence == 0.95

    def test_no_media_dirs(self):
        seg = _make_segment("s1", visual_query="Something")
        sb = _make_storyboard([seg])
        plan = auto_assign_media(sb, [Path("/nonexistent")])
        assert len(plan.unmatched) == 1

    def test_no_match_for_unrelated(self):
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "sunset-beach-ocean.mp4").write_bytes(b"x")

            seg = _make_segment("s1", visual_query="Police interrogation room")
            sb = _make_storyboard([seg])
            plan = auto_assign_media(sb, [stock])

        assert len(plan.unmatched) == 1

    def test_narration_keywords_help_match(self):
        """Narration text contributes to keyword matching."""
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "courtroom-interior-hd.mp4").write_bytes(b"x")

            seg = _make_segment("s1", narration="Inside the courtroom, the judge spoke clearly")
            sb = _make_storyboard([seg])
            plan = auto_assign_media(sb, [stock])

        assert len(plan.assignments) == 1
        assert "courtroom" in plan.assignments[0].file_path.name

    def test_penalizes_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "police-car.mp4").write_bytes(b"x")

            segments = [_make_segment(f"s{i}", visual_query="Police car driving") for i in range(5)]
            sb = _make_storyboard(segments)
            plan = auto_assign_media(sb, [stock])

        confidences = [a.confidence for a in plan.assignments]
        if len(confidences) >= 2:
            assert confidences[-1] <= confidences[0]

    def test_multiple_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "aerial-town.mp4").write_bytes(b"x")
            photos = Path(d) / "photos"
            photos.mkdir()
            (photos / "mugshot-suspect.jpg").write_bytes(b"x")

            seg1 = _make_segment("s1", visual_query="Aerial view of town")
            seg2 = _make_segment("s2", visual_query="Mugshot of the suspect")
            sb = _make_storyboard([seg1, seg2])
            plan = auto_assign_media(sb, [stock, photos])

        assert len(plan.assignments) == 2

    def test_empty_storyboard(self):
        sb = _make_storyboard([])
        plan = auto_assign_media(sb, [Path(".")])
        assert plan.assignments == []
        assert plan.unmatched == []

    def test_over_use_warning(self):
        with tempfile.TemporaryDirectory() as d:
            stock = Path(d) / "stock"
            stock.mkdir()
            (stock / "police-car.mp4").write_bytes(b"x")

            segments = [_make_segment(f"s{i}", visual_query="Police car driving fast") for i in range(5)]
            sb = _make_storyboard(segments)
            plan = auto_assign_media(sb, [stock])

        if len(plan.assignments) > 3:
            assert len(plan.conflicts) > 0
