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
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment
from bee_video_editor.formats.models import (
    AudioEntry,
    OverlayEntry,
    ProjectConfig,
    SegmentConfig,
    VisualEntry,
)


def _make_parsed(segments):
    """Helper to create a ParsedStoryboard from a list of ParsedSegments."""
    return ParsedStoryboard(
        project=ProjectConfig(title="T", version=1),
        sections=[],
        segments=segments,
    )


def _seg(id, visual_code, qualifier="", layer="visual"):
    """Create a segment with one visual/audio/overlay entry."""
    config_kwargs = {}
    if layer == "visual":
        config_kwargs["visual"] = [VisualEntry(type=visual_code, src=qualifier or None)]
    elif layer == "audio":
        config_kwargs["audio"] = [AudioEntry(type=visual_code, src=qualifier or None)]
    elif layer == "overlay":
        config_kwargs["overlay"] = [OverlayEntry(type=visual_code, text=qualifier or None)]

    # For NAR entries in audio layer, use narration field instead
    narration = ""
    if visual_code == "NAR" and layer == "audio":
        narration = qualifier
        config_kwargs = {}  # Don't put NAR in config.audio

    return ParsedSegment(
        id=id, start="0:00", end="0:10", title="TEST",
        section="TEST",
        config=SegmentConfig(**config_kwargs),
        narration=narration,
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

            parsed = _make_parsed([
                _seg("s1", "LOWER-THIRD", "test name", layer="overlay"),
            ])

            report = run_preflight(parsed, proj)
            assert report.found >= 1

    def test_reports_missing_footage(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "COURTROOM", "testimony"),
            ])

            report = run_preflight(parsed, proj)
            assert report.missing >= 1
            missing = [e for e in report.entries if e.status == "missing"]
            assert any(e.visual_code == "COURTROOM" for e in missing)

    def test_broll_is_needs_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "BROLL-DARK", "atmospheric"),
            ])

            report = run_preflight(parsed, proj)
            assert report.needs_check >= 1

    def test_unsupported_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "TEXT-CHAT", "messages"),
            ])

            report = run_preflight(parsed, proj)
            not_supported = [e for e in report.entries if e.status == "not-supported"]
            assert len(not_supported) >= 1

    def test_unknown_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "TOTALLY-MADE-UP", "whatever"),
            ])

            report = run_preflight(parsed, proj)
            unknown = [e for e in report.entries if e.status == "unknown"]
            assert len(unknown) >= 1

    def test_empty_project_all_missing(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
                _seg("s2", "COURTROOM", "testimony"),
            ])

            report = run_preflight(parsed, proj)
            assert report.missing == 2
            assert report.found == 0

    def test_json_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
            ])

            report = run_preflight(parsed, proj)
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
            parsed_json = json.loads(data)
            assert parsed_json["total"] == report.total

    def test_narration_audio_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            (proj / "output" / "narration").mkdir(parents=True)
            (proj / "output" / "narration" / "nar-001-test.mp3").touch()

            parsed = _make_parsed([
                _seg("s1", "NAR", "narrator text", layer="audio"),
            ])

            report = run_preflight(parsed, proj)
            assert report.found >= 1

    def test_persistent_modifiers_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            parsed = _make_parsed([
                _seg("s1", "COLOR-GRADE", "dark_crime"),
                _seg("s2", "TR-FADE", ""),
                _seg("s3", "VIGNETTE", ""),
            ])

            report = run_preflight(parsed, proj)
            assert report.total == 0  # All excluded
