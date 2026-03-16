"""Tests for graphics generation (Pillow-based, no FFmpeg needed)."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from bee_video_editor.processors.graphics import (
    black_frame,
    financial_card,
    lower_third,
    quote_card,
    text_overlay,
    timeline_marker,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestLowerThird:
    def test_creates_file(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        assert out.exists()

    def test_correct_dimensions(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        assert img.size == (1920, 1080)

    def test_rgba_mode(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        assert img.mode == "RGBA"

    def test_has_transparency(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        # Top-left corner should be transparent
        pixel = img.getpixel((0, 0))
        assert pixel[3] == 0  # alpha = 0

    def test_bar_area_opaque(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        # Bottom-left should have the bar
        pixel = img.getpixel((30, 950))
        assert pixel[3] > 0  # not fully transparent


class TestTimelineMarker:
    def test_creates_file(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "The Night of the Murders", tmp_dir / "tm.png")
        assert out.exists()

    def test_correct_dimensions(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "Description", tmp_dir / "tm.png")
        img = Image.open(out)
        assert img.size == (1920, 1080)

    def test_rgb_mode(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "Description", tmp_dir / "tm.png")
        img = Image.open(out)
        assert img.mode == "RGB"


class TestQuoteCard:
    def test_creates_file(self, tmp_dir):
        out = quote_card(
            "I did him so bad.",
            "Alex Murdaugh",
            tmp_dir / "quote.png",
        )
        assert out.exists()

    def test_long_quote_wraps(self, tmp_dir):
        long_quote = "This is a very long quote that should wrap across multiple lines " * 3
        out = quote_card(long_quote, "Speaker", tmp_dir / "quote.png")
        assert out.exists()
        img = Image.open(out)
        assert img.size == (1920, 1080)


class TestFinancialCard:
    def test_creates_file(self, tmp_dir):
        out = financial_card("$8,800,000+", "Stolen from clients", tmp_dir / "fin.png")
        assert out.exists()


class TestTextOverlay:
    def test_creates_file(self, tmp_dir):
        out = text_overlay("Test Text", tmp_dir / "text.png")
        assert out.exists()

    def test_transparent_background(self, tmp_dir):
        out = text_overlay("Test", tmp_dir / "text.png")
        img = Image.open(out)
        assert img.mode == "RGBA"

    def test_positions(self, tmp_dir):
        for pos in ["center", "top", "bottom"]:
            out = text_overlay("Test", tmp_dir / f"text_{pos}.png", position=pos)
            assert out.exists()


class TestBlackFrame:
    def test_creates_file(self, tmp_dir):
        out = black_frame(tmp_dir / "black.png")
        assert out.exists()

    def test_is_black(self, tmp_dir):
        out = black_frame(tmp_dir / "black.png")
        img = Image.open(out)
        pixel = img.getpixel((960, 540))
        assert pixel == (0, 0, 0)
