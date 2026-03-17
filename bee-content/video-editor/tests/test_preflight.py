"""Tests for asset preflight scanner."""

import json
import tempfile
from pathlib import Path

import pytest

from bee_video_editor.services.preflight import (
    AssetEntry,
    PreflightReport,
    run_preflight,
)
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _seg(id, visual_code, qualifier="", layer="visual"):
    """Create a segment with one visual/audio/overlay entry."""
    entries = [LayerEntry(content=qualifier, content_type=visual_code, raw=f"[{visual_code}] {qualifier}")]
    kwargs = {layer: entries}
    return StoryboardSegment(
        id=id, start="0:00", end="0:10", title="TEST",
        section="TEST", section_time="0:00 - 0:10", subsection="",
        **kwargs,
    )


class TestPreflightReport:
    def test_ok_when_no_missing(self):
        report = PreflightReport(total=3, found=3, missing=0, generated=0, needs_check=0, entries=[])
        assert report.ok is True

    def test_not_ok_when_missing(self):
        report = PreflightReport(total=3, found=1, missing=2, generated=0, needs_check=0, entries=[])
        assert report.ok is False


class TestRunPreflight:
    def test_finds_existing_graphics(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            (proj / "output" / "graphics").mkdir(parents=True)
            (proj / "output" / "graphics" / "lower-third-00-test.png").touch()

            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "test name", layer="overlay"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.found >= 1

    def test_reports_missing_footage(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "COURTROOM", "testimony"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.missing >= 1
            missing = [e for e in report.entries if e.status == "missing"]
            assert any(e.visual_code == "COURTROOM" for e in missing)

    def test_broll_is_needs_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "BROLL-DARK", "atmospheric"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.needs_check >= 1

    def test_unsupported_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "TEXT-CHAT", "messages"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            not_supported = [e for e in report.entries if e.status == "not-supported"]
            assert len(not_supported) >= 1

    def test_unknown_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "TOTALLY-MADE-UP", "whatever"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            unknown = [e for e in report.entries if e.status == "unknown"]
            assert len(unknown) >= 1

    def test_empty_project_all_missing(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
                _seg("s2", "COURTROOM", "testimony"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.missing == 2
            assert report.found == 0

    def test_json_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            # Serialize to JSON
            manifest = {
                "total": report.total,
                "found": report.found,
                "missing": report.missing,
                "entries": [
                    {"segment_id": e.segment_id, "visual_code": e.visual_code, "status": e.status}
                    for e in report.entries
                ],
            }
            data = json.dumps(manifest)
            parsed = json.loads(data)
            assert parsed["total"] == report.total

    def test_narration_audio_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            (proj / "output" / "narration").mkdir(parents=True)
            (proj / "output" / "narration" / "nar-001-test.mp3").touch()

            sb = Storyboard(title="T", segments=[
                _seg("s1", "NAR", "narrator text", layer="audio"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.found >= 1

    def test_persistent_modifiers_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "COLOR-GRADE", "dark_crime"),
                _seg("s2", "TR-FADE", ""),
                _seg("s3", "VIGNETTE", ""),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.total == 0  # All excluded
