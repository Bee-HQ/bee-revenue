# Stub FFmpeg + Project Validator + Stock Library

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the stub video generator produce real playable MP4s, add project structure validation, and track stock footage usage across videos to avoid repetition.

**Architecture:** Stub upgrade modifies one function in `videogen.py` to call FFmpeg instead of writing JSON. Validator is a new service with a CLI command. Stock library is a SQLite-backed service at `~/.bee-video/` with CLI commands, auto-registered on `fetch-stock`.

**Tech Stack:** Python 3.11+, FFmpeg (stub), SQLite (stock library), typer (CLI)

---

## File Map

```
src/bee_video_editor/
├── processors/
│   └── videogen.py            (MODIFY — stub now calls FFmpeg)
├── services/
│   ├── validator.py           (NEW — project structure validation)
│   └── stock_library.py       (NEW — SQLite stock footage tracker)
├── adapters/
│   └── cli.py                 (MODIFY — add validate, stock-library commands)

tests/
├── test_videogen.py           (MODIFY — update stub tests for real MP4)
├── test_validator.py          (NEW)
├── test_stock_library.py      (NEW)
```

---

## Task 1: Upgrade Stub to FFmpeg

**Files:**
- Modify: `src/bee_video_editor/processors/videogen.py`
- Modify: `tests/test_videogen.py`

The stub currently writes JSON. Change it to produce a real MP4: black frame + white text showing the prompt, for the requested duration.

- [ ] **Step 1: Update tests for real MP4 output**

Replace the `TestGenerateClip` class in `tests/test_videogen.py`:

```python
# Update existing tests — stub now produces real video via FFmpeg
from unittest.mock import patch, MagicMock

class TestGenerateClip:
    def test_stub_creates_file(self):
        req = GenerationRequest(prompt="test prompt", duration=3.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "generated.mp4"
            with patch("bee_video_editor.processors.ffmpeg.run_ffmpeg") as mock_ff:
                result = generate_clip(req, output, provider="stub")
            assert result.provider == "stub"
            assert result.output_path == output
            assert result.success is True
            mock_ff.assert_called_once()

    def test_stub_ffmpeg_args_contain_prompt(self):
        req = GenerationRequest(prompt="aerial shot of farm", duration=5.0, width=1280, height=720)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with patch("bee_video_editor.processors.ffmpeg.run_ffmpeg") as mock_ff:
                generate_clip(req, output, provider="stub")
            args = mock_ff.call_args[0][0]
            args_str = " ".join(args)
            assert "aerial shot of farm" in args_str or "aerial" in args_str
            assert "1280" in args_str
            assert "720" in args_str

    def test_stub_duration_in_args(self):
        req = GenerationRequest(prompt="test", duration=7.5)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with patch("bee_video_editor.processors.ffmpeg.run_ffmpeg") as mock_ff:
                generate_clip(req, output, provider="stub")
            args = mock_ff.call_args[0][0]
            assert "7.5" in " ".join(args) or "7.50" in " ".join(args)

    def test_unknown_provider_raises(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with pytest.raises(ValueError, match="Unknown video generation provider"):
                generate_clip(req, output, provider="nonexistent")

    def test_creates_parent_dirs(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "deep" / "nested" / "out.mp4"
            with patch("bee_video_editor.processors.videogen.run_ffmpeg"):
                result = generate_clip(req, output, provider="stub")
            assert result.success
            assert output.parent.exists()

    def test_result_includes_metadata(self):
        req = GenerationRequest(prompt="a beautiful sunset", duration=5.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with patch("bee_video_editor.processors.videogen.run_ffmpeg"):
                result = generate_clip(req, output, provider="stub")
            assert result.prompt == "a beautiful sunset"
            assert result.duration == 5.0

    def test_ffmpeg_failure_returns_error(self):
        from bee_video_editor.processors.ffmpeg import FFmpegError
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with patch("bee_video_editor.processors.ffmpeg.run_ffmpeg", side_effect=FFmpegError("boom")):
                result = generate_clip(req, output, provider="stub")
            assert result.success is False
            assert "boom" in result.error
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_videogen.py -v`
Expected: FAIL (tests reference `run_ffmpeg` which isn't imported in videogen.py yet)

- [ ] **Step 3: Update stub implementation**

Replace `_generate_stub` in `src/bee_video_editor/processors/videogen.py`:

```python
def _generate_stub(request: GenerationRequest, output_path: Path) -> GenerationResult:
    """Generate a placeholder video — black frame with prompt text burned in.

    Uses FFmpeg to create a real playable MP4 so downstream pipeline
    processing (trim, normalize, concat) works without a real AI provider.
    """
    from bee_video_editor.processors.ffmpeg import FFmpegError, run_ffmpeg

    # Escape for FFmpeg drawtext (same pattern as ffmpeg.py:drawtext)
    escaped = request.prompt.replace("'", "'\\\\\\''").replace(":", "\\:")

    # Truncate long prompts for display
    if len(escaped) > 80:
        escaped = escaped[:77] + "..."

    try:
        args = [
            "-f", "lavfi",
            "-i", f"color=c=black:s={request.width}x{request.height}:d={request.duration}:r=30",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(request.duration),
            "-vf", (
                f"drawtext=text='{escaped}'"
                f":fontcolor=white:fontsize=28"
                f":x=(w-text_w)/2:y=(h-text_h)/2"
            ),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "64k",
            "-shortest",
            str(output_path),
        ]
        run_ffmpeg(args)

        return GenerationResult(
            success=True,
            output_path=output_path,
            provider="stub",
            prompt=request.prompt,
            duration=request.duration,
            metadata={"type": "stub_ffmpeg", "width": request.width, "height": request.height},
        )
    except FFmpegError as e:
        return GenerationResult(
            success=False,
            output_path=output_path,
            provider="stub",
            prompt=request.prompt,
            duration=request.duration,
            error=str(e),
        )
```

Also update the stub registration in `_ensure_providers_loaded()`:
```python
_register("stub", "Placeholder — generates FFmpeg test video with prompt text", _generate_stub)
```

And remove the `import json` at the top of videogen.py if it's no longer used.

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_videogen.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/processors/videogen.py tests/test_videogen.py
git commit -m "feat(video-editor): stub provider generates real MP4 via FFmpeg drawtext"
```

---

## Task 2: Project Validator

### 2.1: Validation service

**Files:**
- Create: `src/bee_video_editor/services/validator.py`
- Create: `tests/test_validator.py`

The validator checks:
1. Expected directories exist (footage, stock, photos, graphics, narration, maps, music)
2. Output subdirectories are correct (segments, normalized, composited, graphics, narration, final)
3. `.bee-video/` sidecar files are valid JSON
4. Media filenames follow conventions (no spaces, lowercase, proper extensions)

```
Issues reported as a list of ValidationIssue(severity, path, message).
Severities: "error" (wrong structure), "warning" (naming issues), "info" (suggestions).
```

- [ ] **Step 1: Write failing tests**

```python
# tests/test_validator.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_validator.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement validator**

```python
# src/bee_video_editor/services/validator.py
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
```

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_validator.py -v`
Expected: all 7 pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/validator.py tests/test_validator.py
git commit -m "feat(video-editor): project structure validator with naming checks"
```

### 2.2: CLI command

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`

- [ ] **Step 1: Add validate command**

Add before `_load_project()` in `cli.py`:

```python
@app.command()
def validate(
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Validate project directory structure and naming conventions."""
    from bee_video_editor.services.validator import validate_project

    report = validate_project(Path(project_dir))

    severity_colors = {"error": "red", "warning": "yellow", "info": "dim"}
    severity_icons = {"error": "✗", "warning": "!", "info": "·"}

    for issue in report.issues:
        color = severity_colors[issue.severity]
        icon = severity_icons[issue.severity]
        console.print(f"  [{color}]{icon} {issue.message}[/{color}]")
        if issue.path:
            console.print(f"    [dim]{issue.path}[/dim]")

    console.print()
    if report.ok:
        console.print(f"[green]Validation passed[/green] ({report.warnings} warnings, {report.total} total)")
    else:
        console.print(f"[red]{report.errors} errors[/red], {report.warnings} warnings ({report.total} total)")
```

- [ ] **Step 2: Run full test suite**

Run: `uv run --extra dev pytest tests/ -q`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "feat(video-editor): bee-video validate CLI command"
```

---

## Task 3: Stock Footage Library

### 3.1: SQLite storage

**Files:**
- Create: `src/bee_video_editor/services/stock_library.py`
- Create: `tests/test_stock_library.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_stock_library.py
"""Tests for stock footage library — SQLite tracker for clip reuse."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from bee_video_editor.services.stock_library import StockLibrary


class TestStockLibrary:
    def test_register_clip(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            lib.register_clip(
                pexels_id=123,
                query="aerial farm",
                path="/proj/stock/aerial-farm-00-pexels-123.mp4",
                project="my-project",
            )
            clips = lib.list_clips()
            assert len(clips) == 1
            assert clips[0]["pexels_id"] == 123
            assert clips[0]["query"] == "aerial farm"
            assert clips[0]["usage_count"] == 1

    def test_register_same_clip_twice_increments_usage(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            lib.register_clip(pexels_id=123, query="farm", path="/a.mp4", project="proj1")
            lib.register_clip(pexels_id=123, query="farm", path="/a.mp4", project="proj2")

            clips = lib.list_clips()
            assert len(clips) == 1
            assert clips[0]["usage_count"] == 2

    def test_list_usages(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            lib.register_clip(pexels_id=100, query="sunset", path="/a.mp4", project="proj-a")
            lib.register_clip(pexels_id=100, query="sunset", path="/a.mp4", project="proj-b")

            usages = lib.list_usages(pexels_id=100)
            assert len(usages) == 2
            projects = {u["project"] for u in usages}
            assert projects == {"proj-a", "proj-b"}

    def test_check_query_warns_on_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            lib.register_clip(pexels_id=100, query="aerial farm", path="/a.mp4", project="proj-a")

            matches = lib.check_query("aerial farm")
            assert len(matches) == 1
            assert matches[0]["pexels_id"] == 100

    def test_check_query_partial_match(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            lib.register_clip(pexels_id=100, query="aerial farm dusk", path="/a.mp4", project="p")
            lib.register_clip(pexels_id=200, query="courtroom interior", path="/b.mp4", project="p")

            matches = lib.check_query("farm")
            assert len(matches) == 1
            assert matches[0]["pexels_id"] == 100

    def test_check_query_no_matches(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            matches = lib.check_query("nonexistent")
            assert matches == []

    def test_list_clips_empty(self):
        with tempfile.TemporaryDirectory() as d:
            lib = StockLibrary(db_path=Path(d) / "test.db")
            assert lib.list_clips() == []

    def test_default_db_path(self):
        """StockLibrary with no args uses ~/.bee-video/stock-library.db."""
        lib = StockLibrary.__new__(StockLibrary)
        # Don't actually connect, just check the default path logic
        from bee_video_editor.services.stock_library import DEFAULT_DB_PATH
        assert "stock-library.db" in str(DEFAULT_DB_PATH)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_stock_library.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement stock library**

```python
# src/bee_video_editor/services/stock_library.py
"""Stock footage library — tracks clip usage across projects to avoid repetition."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".bee-video" / "stock-library.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clips (
    pexels_id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    path TEXT NOT NULL,
    first_used_project TEXT NOT NULL,
    first_used_at TEXT NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS usages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pexels_id INTEGER NOT NULL REFERENCES clips(pexels_id),
    project TEXT NOT NULL,
    used_at TEXT NOT NULL
);
"""


class StockLibrary:
    """SQLite-backed stock footage usage tracker."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def register_clip(
        self,
        pexels_id: int,
        query: str,
        path: str,
        project: str,
    ) -> None:
        """Register a downloaded stock clip. Increments usage if already known."""
        now = datetime.now().isoformat()

        existing = self.conn.execute(
            "SELECT pexels_id FROM clips WHERE pexels_id = ?", (pexels_id,)
        ).fetchone()

        if existing:
            self.conn.execute(
                "UPDATE clips SET usage_count = usage_count + 1 WHERE pexels_id = ?",
                (pexels_id,),
            )
        else:
            self.conn.execute(
                "INSERT INTO clips (pexels_id, query, path, first_used_project, first_used_at, usage_count) "
                "VALUES (?, ?, ?, ?, ?, 1)",
                (pexels_id, query, path, project, now),
            )

        self.conn.execute(
            "INSERT INTO usages (pexels_id, project, used_at) VALUES (?, ?, ?)",
            (pexels_id, project, now),
        )
        self.conn.commit()

    def list_clips(self) -> list[dict]:
        """Return all tracked clips, ordered by usage count descending."""
        rows = self.conn.execute(
            "SELECT pexels_id, query, path, first_used_project, first_used_at, usage_count "
            "FROM clips ORDER BY usage_count DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def list_usages(self, pexels_id: int) -> list[dict]:
        """Return all usages for a specific clip."""
        rows = self.conn.execute(
            "SELECT project, used_at FROM usages WHERE pexels_id = ? ORDER BY used_at",
            (pexels_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def check_query(self, query: str) -> list[dict]:
        """Find clips that match (substring) a search query. For reuse warnings."""
        rows = self.conn.execute(
            "SELECT pexels_id, query, path, first_used_project, usage_count "
            "FROM clips WHERE query LIKE ? ORDER BY usage_count DESC",
            (f"%{query}%",),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()
```

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_stock_library.py -v`
Expected: all 9 pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/stock_library.py tests/test_stock_library.py
git commit -m "feat(video-editor): stock footage library with SQLite tracking"
```

### 3.2: CLI commands + auto-register on fetch-stock

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`

- [ ] **Step 1: Add stock-library commands and wire into fetch-stock**

Add CLI commands before `_load_project()`:

```python
@app.command(name="stock-list")
def stock_library_list():
    """List all tracked stock footage clips."""
    from bee_video_editor.services.stock_library import StockLibrary

    lib = StockLibrary()
    clips = lib.list_clips()

    if not clips:
        console.print("[dim]No stock clips tracked yet.[/dim]")
        return

    table = Table(title=f"Stock Library ({len(clips)} clips)")
    table.add_column("Pexels ID", style="cyan")
    table.add_column("Query")
    table.add_column("Uses", justify="right")
    table.add_column("First Project")
    table.add_column("Path", max_width=40)

    for clip in clips:
        table.add_row(
            str(clip["pexels_id"]),
            clip["query"],
            str(clip["usage_count"]),
            clip["first_used_project"],
            clip["path"][-40:],
        )

    console.print(table)
    lib.close()


@app.command(name="stock-check")
def stock_library_check(
    query: str = typer.Argument(..., help="Search query to check for prior usage"),
):
    """Check if stock clips from a query were already used in other projects."""
    from bee_video_editor.services.stock_library import StockLibrary

    lib = StockLibrary()
    matches = lib.check_query(query)

    if not matches:
        console.print(f"[green]No prior usage found for '{query}'.[/green]")
    else:
        console.print(f"[yellow]Found {len(matches)} previously used clip(s) matching '{query}':[/yellow]")
        for m in matches:
            console.print(f"  Pexels {m['pexels_id']} — used {m['usage_count']}x, first in {m['first_used_project']}")
        console.print("[dim]Consider varying your search terms to avoid visual repetition.[/dim]")

    lib.close()
```

Now wire stock library registration into the existing `fetch_stock` command. Add after the download loop (after `download_stock_clip`):

In the `fetch_stock` function, after the `download_stock_clip` call succeeds, add:

```python
        try:
            download_stock_clip(clip.hd_url, out_path)
            console.print(f"  [green]{filename}[/green] ({clip.duration}s, {clip.width}x{clip.height})")
            # Auto-register in stock library
            try:
                from bee_video_editor.services.stock_library import StockLibrary
                lib = StockLibrary()
                lib.register_clip(
                    pexels_id=clip.id,
                    query=query,
                    path=str(out_path),
                    project=Path(project_dir).resolve().name,
                )
                lib.close()
            except Exception:
                pass  # Library tracking is non-critical
```

- [ ] **Step 2: Run full test suite**

Run: `uv run --extra dev pytest tests/ -q`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "feat(video-editor): stock-list, stock-check CLI + auto-register on fetch-stock"
```

---

## Task 4: Update Docs

**Files:**
- Modify: `ROADMAP.md`
- Modify: `CLAUDE.md`
- Modify: `CHANGELOG.md`
- Modify: `README.md`

- [ ] **Step 1: Mark roadmap items done**

Mark `Stub → FFmpeg placeholder`, `Naming convention enforcement`, and `Stock footage library` as `[x]`.

- [ ] **Step 2: Update CLAUDE.md with new commands**

Add to CLI section:
```
uv run bee-video validate -p ./proj                          # Validate project structure
uv run bee-video stock-list                                  # List tracked stock clips
uv run bee-video stock-check "aerial farm"                   # Check for reuse
```

- [ ] **Step 3: Update CHANGELOG.md and README.md**

- [ ] **Step 4: Run full test suite**

Run: `./test.sh`
Expected: all pass

- [ ] **Step 5: Commit and push**

```bash
# From repo root
git add bee-content/video-editor/ROADMAP.md bee-content/video-editor/CLAUDE.md \
        bee-content/video-editor/CHANGELOG.md bee-content/video-editor/README.md
git commit -m "docs(video-editor): stub FFmpeg + validator + stock library"
```
