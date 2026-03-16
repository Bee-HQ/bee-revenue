"""Tests for production service (state management, project init)."""

import json
import tempfile
from pathlib import Path

import pytest

from bee_video_editor.services.production import (
    ProductionConfig,
    ProductionState,
    SegmentStatus,
    _extract_narrator_text,
    _slugify,
)


class TestProductionState:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                assembly_guide_path="/path/to/guide.md",
                phase="parsed",
            )
            state.segment_statuses = [
                SegmentStatus(index=0, time_range="0:00-0:15", segment_type="REAL"),
                SegmentStatus(index=1, time_range="0:15-0:30", segment_type="MIX", status="done"),
            ]

            path = Path(d) / "state.json"
            state.save(path)

            loaded = ProductionState.load(path)
            assert loaded.assembly_guide_path == "/path/to/guide.md"
            assert loaded.phase == "parsed"
            assert len(loaded.segment_statuses) == 2
            assert loaded.segment_statuses[1].status == "done"

    def test_state_json_format(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                assembly_guide_path="/path/to/guide.md",
                phase="init",
            )
            path = Path(d) / "state.json"
            state.save(path)

            data = json.loads(path.read_text())
            assert "assembly_guide_path" in data
            assert "phase" in data
            assert "segment_statuses" in data


class TestProductionConfig:
    def test_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            assert config.output_dir == Path(d) / "output"
            assert config.footage_dir == Path(d) / "footage"
            assert config.tts_engine == "edge"
            assert config.width == 1920
            assert config.height == 1080

    def test_custom_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(
                project_dir=Path(d),
                output_dir=Path(d) / "custom_output",
                footage_dir=Path(d) / "custom_footage",
            )
            assert config.output_dir == Path(d) / "custom_output"
            assert config.footage_dir == Path(d) / "custom_footage"


class TestExtractNarratorText:
    def test_quoted(self):
        text = _extract_narrator_text('NAR: "This is Alex Murdaugh..." + dark ambient music')
        assert text == "This is Alex Murdaugh..."

    def test_unquoted(self):
        text = _extract_narrator_text('NAR: This is a test line + music')
        assert text == "This is a test line"

    def test_no_narrator(self):
        text = _extract_narrator_text('Alex 911 call: "I need help!"')
        assert text == ""

    def test_empty(self):
        text = _extract_narrator_text('')
        assert text == ""

    def test_nar_only(self):
        text = _extract_narrator_text('NAR: "Welcome to the story"')
        assert text == "Welcome to the story"


class TestSlugify:
    def test_basic(self):
        assert _slugify("Cold Open") == "cold-open"

    def test_special_chars(self):
        assert _slugify('$792,000 — Missing') == "792000-missing"

    def test_multiple_spaces(self):
        assert _slugify("ACT  1:  THE  DYNASTY") == "act-1-the-dynasty"
