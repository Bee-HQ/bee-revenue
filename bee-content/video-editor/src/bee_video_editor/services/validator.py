"""Project structure validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

EXPECTED_MEDIA_DIRS = ["footage", "stock", "photos", "graphics", "narration", "maps", "music"]
EXPECTED_OUTPUT_DIRS = ["segments", "normalized", "composited", "graphics", "narration", "final"]
SIDECAR_JSON_FILES = ["assignments.json", "segment-order.json", "voice.json", "session.json"]
VALID_MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".mp3", ".wav", ".m4a",
                          ".aac", ".ogg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


@dataclass
class ValidationIssue:
    severity: str  # "error", "warning", "info"
    path: str
    message: str


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def total(self) -> int:
        return len(self.issues)

    @property
    def ok(self) -> bool:
        return self.errors == 0


def validate_project(project_dir: Path) -> ValidationReport:
    """Validate project directory structure, sidecar files, and naming conventions."""
    report = ValidationReport()

    # Check expected media directories
    for dirname in EXPECTED_MEDIA_DIRS:
        d = project_dir / dirname
        if not d.exists():
            report.issues.append(ValidationIssue(
                severity="warning",
                path=str(d),
                message=f"Missing expected directory: {dirname}/",
            ))

    # Check output directories
    output = project_dir / "output"
    if output.exists():
        for dirname in EXPECTED_OUTPUT_DIRS:
            d = output / dirname
            if not d.exists():
                report.issues.append(ValidationIssue(
                    severity="info",
                    path=str(d),
                    message=f"Missing output subdirectory: output/{dirname}/",
                ))

    # Check .bee-video sidecar JSON files
    bee_dir = project_dir / ".bee-video"
    if bee_dir.exists():
        for filename in SIDECAR_JSON_FILES:
            f = bee_dir / filename
            if f.exists():
                try:
                    json.loads(f.read_text())
                except (json.JSONDecodeError, ValueError):
                    report.issues.append(ValidationIssue(
                        severity="error",
                        path=str(f),
                        message=f"Invalid JSON in {filename}",
                    ))

    # Check media filenames
    for dirname in EXPECTED_MEDIA_DIRS:
        d = project_dir / dirname
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() not in VALID_MEDIA_EXTENSIONS:
                continue
            _check_filename(f, project_dir, report)

    return report


def _check_filename(file_path: Path, project_dir: Path, report: ValidationReport) -> None:
    """Check a single media filename for convention issues."""
    name = file_path.name

    if " " in name:
        rel = file_path.relative_to(project_dir)
        report.issues.append(ValidationIssue(
            severity="warning",
            path=str(rel),
            message=f"Filename contains spaces: {name}",
        ))

    if name != name.lower():
        rel = file_path.relative_to(project_dir)
        report.issues.append(ValidationIssue(
            severity="warning",
            path=str(rel),
            message=f"Filename not lowercase: {name}",
        ))
