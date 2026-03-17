"""Tests for project structure validation."""

import json
import tempfile
from pathlib import Path

import pytest

from bee_video_editor.services.validator import (
    ValidationIssue,
    ValidationReport,
    validate_project,
)


class TestValidateProject:
    def test_empty_project_reports_missing_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            report = validate_project(Path(d))
        missing_dirs = [i for i in report.issues if "missing" in i.message.lower() and i.severity == "warning"]
        assert len(missing_dirs) > 0
        dir_names = " ".join(i.message for i in missing_dirs)
        assert "footage" in dir_names

    def test_valid_project_no_errors(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            for subdir in ["footage", "stock", "photos", "graphics", "narration", "maps", "music"]:
                (proj / subdir).mkdir()
            (proj / "output").mkdir()
            for subdir in ["segments", "normalized", "composited", "graphics", "narration", "final"]:
                (proj / "output" / subdir).mkdir()
            bee_dir = proj / ".bee-video"
            bee_dir.mkdir()
            (bee_dir / "assignments.json").write_text("{}")
            (bee_dir / "voice.json").write_text('{"engine": "edge"}')

            report = validate_project(proj)
        errors = [i for i in report.issues if i.severity == "error"]
        assert len(errors) == 0

    def test_corrupt_json_sidecar_error(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            bee_dir = proj / ".bee-video"
            bee_dir.mkdir()
            (bee_dir / "assignments.json").write_text("not json{{{")

            report = validate_project(proj)
        errors = [i for i in report.issues if i.severity == "error" and "assignments.json" in i.message]
        assert len(errors) == 1

    def test_filename_with_spaces_warning(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            footage = proj / "footage"
            footage.mkdir()
            (footage / "My Video File.mp4").write_bytes(b"\x00")

            report = validate_project(proj)
        warnings = [i for i in report.issues if i.severity == "warning" and "space" in i.message.lower()]
        assert len(warnings) == 1

    def test_uppercase_filename_warning(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            footage = proj / "footage"
            footage.mkdir()
            (footage / "MyClip.MP4").write_bytes(b"\x00")

            report = validate_project(proj)
        warnings = [i for i in report.issues if i.severity == "warning" and "lowercase" in i.message.lower()]
        assert len(warnings) >= 1

    def test_report_summary(self):
        with tempfile.TemporaryDirectory() as d:
            report = validate_project(Path(d))
        assert report.errors >= 0
        assert report.warnings >= 0
        assert report.total == len(report.issues)
