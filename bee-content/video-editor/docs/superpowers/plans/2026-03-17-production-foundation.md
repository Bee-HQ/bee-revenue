# Production Foundation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace silent error swallowing with structured ProductionResult, add automatic segment status tracking, and replace module globals with SessionStore.

**Architecture:** Three changes to the backend — ProductionResult dataclass (new return type for production functions), ProductionState.track() context manager (automatic status updates), SessionStore class (replaces 3 module-level globals via FastAPI Depends).

**Tech Stack:** Python 3.11+, FastAPI, pytest, dataclasses

**Spec:** `docs/superpowers/specs/2026-03-17-production-foundation-design.md`

---

## Chunk 1: ProductionResult and track() in production.py

### Task 1: Add ProductionResult and FailedItem dataclasses + tests

**Files:**
- Modify: `src/bee_video_editor/services/production.py`
- Modify: `tests/test_production.py`

- [ ] **Step 1: Write failing tests for ProductionResult**

Add to `tests/test_production.py`:

```python
from bee_video_editor.services.production import (
    FailedItem,
    ProductionResult,
)


class TestProductionResult:
    def test_empty_result_is_ok(self):
        result = ProductionResult()
        assert result.ok is True
        assert result.succeeded == []
        assert result.failed == []
        assert result.skipped == []

    def test_result_with_failures_is_not_ok(self):
        result = ProductionResult()
        result.failed.append(FailedItem(path="/bad/file.mp4", error="FFmpeg crashed"))
        assert result.ok is False

    def test_result_accumulates(self):
        result = ProductionResult()
        result.succeeded.append(Path("/out/a.mp4"))
        result.succeeded.append(Path("/out/b.mp4"))
        result.failed.append(FailedItem(path="/src/c.mkv", error="codec error"))
        result.skipped.append("d.mp4 already exists")
        assert len(result.succeeded) == 2
        assert len(result.failed) == 1
        assert len(result.skipped) == 1
        assert result.ok is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionResult -v`
Expected: FAIL with ImportError (FailedItem, ProductionResult not defined)

- [ ] **Step 3: Implement ProductionResult and FailedItem**

Add to `src/bee_video_editor/services/production.py` after the existing imports:

```python
@dataclass
class FailedItem:
    """A single failed processing step."""
    path: str
    error: str


@dataclass
class ProductionResult:
    """Structured return from every production function."""
    succeeded: list[Path] = field(default_factory=list)
    failed: list[FailedItem] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionResult -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "feat(video-editor): add ProductionResult and FailedItem dataclasses"
```

### Task 2: Add state_path property to ProductionConfig + tests

**Files:**
- Modify: `src/bee_video_editor/services/production.py`
- Modify: `tests/test_production.py`

- [ ] **Step 1: Write failing test**

Add to `TestProductionConfig` in `tests/test_production.py`:

```python
    def test_state_path(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            assert config.state_path == Path(d) / "output" / "production_state.json"

    def test_state_path_custom_output(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d), output_dir=Path(d) / "custom")
            assert config.state_path == Path(d) / "custom" / "production_state.json"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionConfig::test_state_path -v`
Expected: FAIL with AttributeError

- [ ] **Step 3: Add state_path property to ProductionConfig**

In `ProductionConfig` class in `production.py`, add after `__post_init__`:

```python
    @property
    def state_path(self) -> Path:
        return self.output_dir / "production_state.json"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionConfig -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "feat(video-editor): add state_path property to ProductionConfig"
```

### Task 3: Add track() context manager to ProductionState + tests

**Files:**
- Modify: `src/bee_video_editor/services/production.py`
- Modify: `tests/test_production.py`

- [ ] **Step 1: Write failing tests for track()**

Add to `tests/test_production.py`:

```python
class TestProductionStateTrack:
    def _make_state(self):
        state = ProductionState(assembly_guide_path="/test.md", phase="parsed")
        state.segment_statuses = [
            SegmentStatus(index=0, time_range="0:00-0:15", segment_type="NAR"),
            SegmentStatus(index=1, time_range="0:15-0:30", segment_type="REAL"),
        ]
        return state

    def test_track_success(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with state.track(0, state_path):
                assert state.segment_statuses[0].status == "processing"
            assert state.segment_statuses[0].status == "done"
            # Verify saved to disk
            loaded = ProductionState.load(state_path)
            assert loaded.segment_statuses[0].status == "done"

    def test_track_error(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with pytest.raises(RuntimeError):
                with state.track(1, state_path):
                    raise RuntimeError("ffmpeg died")
            assert state.segment_statuses[1].status == "error"
            assert "ffmpeg died" in state.segment_statuses[1].error
            # Verify saved to disk
            loaded = ProductionState.load(state_path)
            assert loaded.segment_statuses[1].status == "error"

    def test_track_bounds_check(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with pytest.raises(ValueError, match="out of range"):
                with state.track(5, state_path):
                    pass

    def test_track_saves_processing_on_enter(self):
        """If process crashes mid-work, state file shows 'processing' not 'done'."""
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            # Simulate: enter context, save happens, but never reach yield completion
            with pytest.raises(RuntimeError):
                with state.track(0, state_path):
                    # Verify intermediate save shows "processing"
                    intermediate = ProductionState.load(state_path)
                    assert intermediate.segment_statuses[0].status == "processing"
                    raise RuntimeError("crash")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionStateTrack -v`
Expected: FAIL with AttributeError (track not defined)

- [ ] **Step 3: Implement track() context manager**

Add to `ProductionState` class in `production.py`. Add `from contextlib import contextmanager` at top of file.

```python
    @contextmanager
    def track(self, index: int, state_path: Path):
        """Track segment processing. Sets status to processing/done/error and saves."""
        if index < 0 or index >= len(self.segment_statuses):
            raise ValueError(
                f"Segment index {index} out of range (0-{len(self.segment_statuses) - 1})"
            )
        seg = self.segment_statuses[index]
        seg.status = "processing"
        seg.error = None
        self.save(state_path)
        try:
            yield seg
            seg.status = "done"
        except Exception as e:
            seg.status = "error"
            seg.error = str(e)[:200]
            raise
        finally:
            self.save(state_path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestProductionStateTrack -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "feat(video-editor): add track() context manager for segment status"
```

### Task 4: Refactor production functions to return ProductionResult

**Files:**
- Modify: `src/bee_video_editor/services/production.py`

- [ ] **Step 1: Run existing tests to establish baseline**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py -v`
Expected: all pass

- [ ] **Step 2: Refactor generate_graphics_for_project**

Change return type to `ProductionResult`, add optional `state` param:

```python
def generate_graphics_for_project(
    project: Project,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Generate all graphics assets from project pre-production list."""
    result = ProductionResult()
    graphics_dir = config.output_dir / "graphics"

    if state:
        state.phase = "graphics"
        state.save(config.state_path)

    # Generate lower thirds from segments that mention "lower third"
    lower_third_idx = 0
    for seg in project.segments:
        visual_lower = seg.visual.lower()
        if "lower third" in visual_lower:
            match = re.search(r'lower third[^"]*"([^"]+)"', seg.visual, re.IGNORECASE)
            if match:
                parts = match.group(1).split(" — ")
                name = parts[0].strip()
                role = parts[1].strip() if len(parts) > 1 else ""
            else:
                name = f"Character {lower_third_idx}"
                role = ""

            out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{_slugify(name)}.png"
            if out.exists():
                result.skipped.append(f"lower-third {name} already exists")
            else:
                try:
                    gfx.lower_third(name, role, out)
                    result.succeeded.append(out)
                except Exception as e:
                    result.failed.append(FailedItem(path=str(out), error=str(e)))
            lower_third_idx += 1

    # Generate timeline markers
    timeline_idx = 0
    for seg in project.segments:
        if seg.segment_type == SegmentType.GEN and "TEXT-TIMELINE" in seg.visual:
            match = re.search(r'TEXT-TIMELINE[:\s]*"?([^"]+)"?', seg.visual)
            if match:
                text = match.group(1).strip()
                out = graphics_dir / f"timeline-{timeline_idx:02d}-{_slugify(text)[:30]}.png"
                if out.exists():
                    result.skipped.append(f"timeline {text} already exists")
                else:
                    try:
                        gfx.timeline_marker(text, "", out)
                        result.succeeded.append(out)
                    except Exception as e:
                        result.failed.append(FailedItem(path=str(out), error=str(e)))
                timeline_idx += 1

    # Generate financial cards
    fin_idx = 0
    for seg in project.segments:
        if "TEXT-FINANCIAL" in seg.visual:
            match = re.search(r'TEXT-FINANCIAL\s*"?([^"]+)"?', seg.visual)
            if match:
                amount = match.group(1).strip()
                out = graphics_dir / f"financial-{fin_idx:02d}-{_slugify(amount)[:20]}.png"
                if out.exists():
                    result.skipped.append(f"financial {amount} already exists")
                else:
                    try:
                        gfx.financial_card(amount, "", out)
                        result.succeeded.append(out)
                    except Exception as e:
                        result.failed.append(FailedItem(path=str(out), error=str(e)))
                fin_idx += 1

    return result
```

- [ ] **Step 3: Refactor generate_narration_for_project**

```python
def generate_narration_for_project(
    project: Project,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Generate TTS narration for all NAR and MIX segments."""
    result = ProductionResult()
    narration_dir = config.output_dir / "narration"

    if state:
        state.phase = "narration"
        state.save(config.state_path)

    for i, seg in enumerate(project.segments):
        if seg.segment_type not in (SegmentType.NAR, SegmentType.MIX):
            continue

        nar_text = _extract_narrator_text(seg.audio)
        if not nar_text:
            continue

        out = narration_dir / f"nar-{i:03d}-{_slugify(seg.subsection or seg.section)[:30]}.mp3"
        if out.exists():
            result.skipped.append(f"narration segment {i} already exists")
            continue

        try:
            if state:
                with state.track(i, config.state_path):
                    generate_narration(
                        text=nar_text,
                        output_path=out,
                        engine=config.tts_engine,
                        voice=config.tts_voice,
                    )
                    result.succeeded.append(out)
            else:
                generate_narration(
                    text=nar_text,
                    output_path=out,
                    engine=config.tts_engine,
                    voice=config.tts_voice,
                )
                result.succeeded.append(out)
        except Exception as e:
            result.failed.append(FailedItem(path=f"segment-{i}", error=str(e)))

    return result
```

- [ ] **Step 4: Refactor trim_source_footage**

```python
def trim_source_footage(
    project: Project,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Trim source footage based on assembly guide trim notes."""
    result = ProductionResult()
    segments_dir = config.output_dir / "segments"

    if state:
        state.phase = "trimming"
        state.save(config.state_path)

    for note in project.trim_notes:
        pattern = str(config.footage_dir / note.source_file.replace("footage/", ""))
        matches = globmod.glob(pattern)
        if not matches:
            result.failed.append(FailedItem(path=pattern, error="no matching source file found"))
            continue
        source = matches[0]

        for j, t in enumerate(note.trims):
            slug = _slugify(t.label)[:40]
            out = segments_dir / f"trim-{slug}-{j:02d}.mp4"
            if out.exists():
                result.skipped.append(f"trim {t.label} already exists")
                continue
            try:
                trim(source, out, start=t.start, end=t.duration)
                result.succeeded.append(out)
            except Exception as e:
                result.failed.append(FailedItem(path=str(source), error=str(e)))

    return result
```

- [ ] **Step 5: Refactor normalize_all_segments**

```python
def normalize_all_segments(
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Normalize all segments to consistent format."""
    result = ProductionResult()
    segments_dir = config.output_dir / "segments"
    normalized_dir = config.output_dir / "normalized"

    if state:
        state.phase = "normalizing"
        state.save(config.state_path)

    for seg_file in sorted(segments_dir.glob("*.mp4")):
        out = normalized_dir / seg_file.name
        if out.exists():
            result.skipped.append(f"{seg_file.name} already normalized")
            continue
        try:
            normalize_format(seg_file, out, config.width, config.height, config.fps)
            result.succeeded.append(out)
        except Exception as e:
            result.failed.append(FailedItem(path=str(seg_file), error=str(e)))

    return result
```

- [ ] **Step 6: Update init_project to use config.state_path**

Change line `state_path = config.output_dir / "production_state.json"` to `state.save(config.state_path)`.

- [ ] **Step 7: Run all tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All pass. Existing tests that don't call the refactored functions directly should still work. The test_production.py tests exercise state/config but not the production functions themselves (those are mocked in integration tests).

- [ ] **Step 8: Commit**

```bash
git add src/bee_video_editor/services/production.py
git commit -m "refactor(video-editor): production functions return ProductionResult, accept optional state"
```

### Task 5: Update CLI adapter to handle ProductionResult

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`

- [ ] **Step 1: Update graphics command**

In `cli.py`, change the `graphics` function:

```python
@app.command()
def graphics(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Generate all graphics assets (lower thirds, timelines, etc.)."""
    from bee_video_editor.services.production import ProductionConfig, generate_graphics_for_project

    config = ProductionConfig(project_dir=Path(project_dir))
    project = _load_project(assembly_guide)

    console.print("[bold]Generating graphics...[/bold]")
    result = generate_graphics_for_project(project, config)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    for g in result.succeeded:
        console.print(f"  {g}")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")
```

- [ ] **Step 2: Update narration command**

Same pattern — replace `generated = generate_narration_for_project(...)` + `len(generated)` with `result = ...` + `result.succeeded`/`result.failed`.

- [ ] **Step 3: Update trim_footage command**

Same pattern.

- [ ] **Step 4: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "feat(video-editor): CLI shows succeeded/failed/skipped counts from ProductionResult"
```

### Task 6: Update dashboard adapter to handle ProductionResult

**Files:**
- Modify: `src/bee_video_editor/adapters/dashboard.py`

- [ ] **Step 1: Update _render_produce function**

Change the three production buttons in `dashboard.py` `_render_produce()`:

```python
    with col_g:
        if st.button("Generate Graphics", use_container_width=True):
            from bee_video_editor.services.production import generate_graphics_for_project
            with st.spinner("Generating graphics..."):
                result = generate_graphics_for_project(project, config)
            st.success(f"Generated {len(result.succeeded)} graphics")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")

    with col_n:
        if st.button("Generate Narration", use_container_width=True):
            from bee_video_editor.services.production import generate_narration_for_project
            with st.spinner("Generating narration..."):
                result = generate_narration_for_project(project, config)
            st.success(f"Generated {len(result.succeeded)} narration clips")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")

    with col_t:
        if st.button("Trim Footage", use_container_width=True):
            from bee_video_editor.services.production import trim_source_footage
            with st.spinner("Trimming footage..."):
                result = trim_source_footage(project, config)
            st.success(f"Trimmed {len(result.succeeded)} clips")
            if result.failed:
                st.error(f"Failed: {len(result.failed)} — {result.failed[0].error}")
```

- [ ] **Step 2: Commit**

```bash
git add src/bee_video_editor/adapters/dashboard.py
git commit -m "feat(video-editor): dashboard handles ProductionResult return type"
```

## Chunk 2: SessionStore and API route refactor

### Task 7: Create SessionStore class + tests

**Files:**
- Create: `src/bee_video_editor/api/session.py`
- Create: `tests/test_session.py`

- [ ] **Step 1: Write failing tests for SessionStore**

Create `tests/test_session.py`:

```python
"""Tests for SessionStore."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.api.session import SessionStore


class TestSessionStore:
    def test_require_project_raises_when_empty(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.require_project()
        assert exc_info.value.status_code == 404

    def test_load_project_nonexistent_raises(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.load_project(Path("/nonexistent/storyboard.md"), Path("/tmp/proj"))
        assert exc_info.value.status_code == 404

    def test_load_project_sets_state(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            # Create a minimal storyboard file
            sb_path = Path(d) / "storyboard.md"
            sb_path.write_text("# Test Storyboard\n\nNo segments.\n")
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                result = store.load_project(sb_path, proj_dir)

            assert store.storyboard is not None
            assert store.project_dir == proj_dir.resolve()
            assert store.assignments_path == proj_dir.resolve() / ".bee-video" / "assignments.json"

    def test_assign_media_persists(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()

            # Create storyboard file BEFORE load_project (exists check)
            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import (
                    ProductionRules,
                    Storyboard,
                    StoryboardSegment,
                )
                seg = StoryboardSegment(
                    id="0_00-0_05", start="0:00", end="0:05", title="HOOK",
                    section="COLD OPEN", section_time="0:00 - 2:30", subsection="",
                    visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
                    assigned_media={},
                )
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[seg], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(sb_path, proj_dir)

            result = store.assign_media("0_00-0_05", "visual", 0, "/media/clip.mp4")
            assert result["status"] == "ok"

            # Verify persisted to disk
            assignments_path = proj_dir.resolve() / ".bee-video" / "assignments.json"
            assert assignments_path.exists()
            data = json.loads(assignments_path.read_text())
            assert data["0_00-0_05"]["visual:0"] == "/media/clip.mp4"

    def test_assign_media_unknown_segment_raises(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            (Path(d) / "sb.md").write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(Path(d) / "sb.md", proj_dir)

            with pytest.raises(Exception) as exc_info:
                store.assign_media("nonexistent", "visual", 0, "/media/clip.mp4")
            assert exc_info.value.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_session.py -v`
Expected: FAIL with ModuleNotFoundError (session.py doesn't exist)

- [ ] **Step 3: Create session.py**

Create `src/bee_video_editor/api/session.py`:

```python
"""Session management — single-process singleton replacing module globals."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import HTTPException

from bee_video_editor.models_storyboard import Storyboard
from bee_video_editor.parsers.storyboard import parse_storyboard


@dataclass
class SessionStore:
    """Holds the current project state. One instance per process."""

    storyboard: Storyboard | None = None
    project_dir: Path | None = None
    assignments_path: Path | None = None

    def require_project(self) -> tuple[Storyboard, Path]:
        """Return (storyboard, project_dir) or raise 404."""
        if self.storyboard is None or self.project_dir is None:
            raise HTTPException(404, "No project loaded")
        return self.storyboard, self.project_dir

    def load_project(self, storyboard_path: Path, project_dir: Path) -> Storyboard:
        """Parse storyboard, restore assignments, set as current session."""
        if not storyboard_path.exists():
            raise HTTPException(404, f"Storyboard not found: {storyboard_path}")

        self.project_dir = project_dir.resolve()
        self.assignments_path = self.project_dir / ".bee-video" / "assignments.json"
        self.storyboard = parse_storyboard(storyboard_path)

        saved = self._load_assignments()
        for seg in self.storyboard.segments:
            if seg.id in saved:
                seg.assigned_media = saved[seg.id]

        return self.storyboard

    def assign_media(
        self, segment_id: str, layer: str, index: int, media_path: str
    ) -> dict:
        """Assign media to segment layer, persist to sidecar JSON."""
        sb, _ = self.require_project()
        seg = next((s for s in sb.segments if s.id == segment_id), None)
        if seg is None:
            raise HTTPException(404, f"Segment not found: {segment_id}")

        key = f"{layer}:{index}"
        seg.assigned_media[key] = media_path

        assignments = self._load_assignments()
        assignments.setdefault(segment_id, {})[key] = media_path
        self._save_assignments(assignments)

        return {
            "status": "ok",
            "segment_id": segment_id,
            "key": key,
            "media_path": media_path,
        }

    def _load_assignments(self) -> dict:
        if self.assignments_path and self.assignments_path.exists():
            with open(self.assignments_path) as f:
                return json.load(f)
        return {}

    def _save_assignments(self, assignments: dict) -> None:
        if self.assignments_path:
            self.assignments_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.assignments_path, "w") as f:
                json.dump(assignments, f, indent=2)


# Module-level singleton + dependency function
_session = SessionStore()


def get_session() -> SessionStore:
    """FastAPI dependency — returns the singleton SessionStore."""
    return _session
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_session.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/api/session.py tests/test_session.py
git commit -m "feat(video-editor): add SessionStore class with get_session dependency"
```

### Task 8: Refactor API routes to use SessionStore

**Files:**
- Modify: `src/bee_video_editor/api/routes/projects.py`
- Modify: `src/bee_video_editor/api/routes/media.py`
- Modify: `src/bee_video_editor/api/routes/production.py`

- [ ] **Step 1: Refactor projects.py**

Replace the entire file. Remove the 3 module globals, remove `_load_assignments`/`_save_assignments` helpers, use `Depends(get_session)`:

```python
"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    LayerEntrySchema,
    LoadProjectRequest,
    SegmentSchema,
    StoryboardSchema,
)
from bee_video_editor.api.session import SessionStore, get_session
from bee_video_editor.models_storyboard import Storyboard

router = APIRouter()


def _segment_to_schema(seg) -> SegmentSchema:
    def _layers(entries):
        return [
            LayerEntrySchema(
                content=e.content,
                content_type=e.content_type,
                time_start=e.time_start,
                time_end=e.time_end,
                raw=e.raw,
            )
            for e in entries
        ]

    return SegmentSchema(
        id=seg.id,
        start=seg.start,
        end=seg.end,
        title=seg.title,
        section=seg.section,
        section_time=seg.section_time,
        subsection=seg.subsection,
        duration_seconds=seg.duration_seconds,
        visual=_layers(seg.visual),
        audio=_layers(seg.audio),
        overlay=_layers(seg.overlay),
        music=_layers(seg.music),
        source=_layers(seg.source),
        transition=_layers(seg.transition),
        assigned_media=seg.assigned_media,
    )


def _storyboard_to_schema(sb: Storyboard) -> StoryboardSchema:
    return StoryboardSchema(
        title=sb.title,
        total_segments=sb.total_segments,
        total_duration_seconds=sb.total_duration_seconds,
        sections=sb.sections,
        segments=[_segment_to_schema(s) for s in sb.segments],
        stock_footage_needed=len(sb.stock_footage),
        photos_needed=len(sb.photos_needed),
        maps_needed=len(sb.maps_needed),
        production_rules=[r for r in sb.production_rules.rules],
    )


@router.post("/load", response_model=StoryboardSchema)
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    """Load a storyboard file and return the parsed project."""
    sb = session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return _storyboard_to_schema(sb)


@router.get("/current", response_model=StoryboardSchema)
def get_current_project(session: SessionStore = Depends(get_session)):
    """Get the currently loaded project."""
    sb, _ = session.require_project()
    return _storyboard_to_schema(sb)


@router.put("/assign")
def assign_media(req: AssignMediaRequest, session: SessionStore = Depends(get_session)):
    """Assign a media file to a segment layer."""
    return session.assign_media(req.segment_id, req.layer, req.layer_index, req.media_path)
```

- [ ] **Step 2: Refactor media.py**

Replace the `_get_project_dir()` function and its import. Add `Depends(get_session)` to every route that needs the project dir:

Replace `_get_project_dir` definition and all its usages. Every route function gains `session: SessionStore = Depends(get_session)` and calls `_, project_dir = session.require_project()` or just `project_dir = session.require_project()[1]`.

Add imports at top:
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from bee_video_editor.api.session import SessionStore, get_session
```

Remove the old `_get_project_dir` function. Update each route:
- `list_media(session: SessionStore = Depends(get_session))` — `project_dir = session.require_project()[1]`
- `upload_media(file, category, session: SessionStore = Depends(get_session))`
- `serve_media_file(path, session: SessionStore = Depends(get_session))`
- `list_download_scripts(session: SessionStore = Depends(get_session))`
- `run_download_script(req, session: SessionStore = Depends(get_session))`
- `download_with_ytdlp(url, category, filename, session: SessionStore = Depends(get_session))`
- `create_media_dirs(session: SessionStore = Depends(get_session))`

`check_download_tools()` and `download_status()` don't need session — leave them as-is.

- [ ] **Step 3: Refactor production.py routes**

Replace `_get_state()` function and its import. Add `Depends(get_session)`:

```python
from fastapi import APIRouter, Depends, HTTPException
from bee_video_editor.api.session import SessionStore, get_session
```

Remove `_get_state()`. Update each route:
- `get_production_status(session: SessionStore = Depends(get_session))`
- `init_project(session: SessionStore = Depends(get_session))`
- `generate_graphics(session: SessionStore = Depends(get_session))`
- `generate_narration(req, session: SessionStore = Depends(get_session))`
- `assemble_video(transition, transition_duration, session: SessionStore = Depends(get_session))`
- `list_effects()` — no session needed, leave as-is

- [ ] **Step 4: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: PASS

- [ ] **Step 5: Manually verify server starts**

Run: `cd bee-content/video-editor && uv run bee-video serve --port 8421 &` then `curl http://localhost:8421/api/production/effects` — should return JSON. Kill with `kill %1`.

- [ ] **Step 6: Commit**

```bash
git add src/bee_video_editor/api/routes/projects.py src/bee_video_editor/api/routes/media.py src/bee_video_editor/api/routes/production.py
git commit -m "refactor(video-editor): replace module globals with SessionStore via Depends"
```

### Task 9: Update production.py API routes to surface ProductionResult

**Files:**
- Modify: `src/bee_video_editor/api/routes/production.py`

> **Note: Why the API routes have their own logic instead of delegating to service functions.**
> The API routes work with the Storyboard model (segments have `.overlay`, `.audio` layers) while the service functions in `production.py` work with the assembly guide's Project model (segments have `.visual`, `.audio` strings). This is the "Two Parser Problem" documented in CLAUDE.md — until v0.4.0 unifies the models, both codepaths need the same error-handling pattern applied independently.

- [ ] **Step 1: Update graphics endpoint response**

The `generate_graphics()` route has its own storyboard-based graphics loop. Apply the same error-handling pattern (try/except, collect failures):

```python
@router.post("/graphics")
def generate_graphics(session: SessionStore = Depends(get_session)):
    """Generate graphics assets from storyboard."""
    storyboard, project_dir = session.require_project()
    output_dir = project_dir / "output"
    graphics_dir = output_dir / "graphics"
    graphics_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors import graphics as gfx
    import re

    generated = []
    failed = []
    lower_third_idx = 0

    for seg in storyboard.segments:
        for overlay in seg.overlay:
            if overlay.content_type == "GRAPHIC" and "lower third" in overlay.content.lower():
                match = re.search(r'"([^"]+)"', overlay.content)
                if match:
                    parts = match.group(1).split(" — ")
                    name = parts[0].strip()
                    role = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = f"Character {lower_third_idx}"
                    role = ""

                slug = name.lower().replace(" ", "-")[:30]
                out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{slug}.png"
                if not out.exists():
                    try:
                        gfx.lower_third(name, role, out)
                        generated.append(str(out))
                    except Exception as e:
                        failed.append({"path": str(out), "error": str(e)})
                lower_third_idx += 1

    status = "ok" if not failed else ("error" if not generated else "partial")
    return {"status": status, "succeeded": generated, "failed": failed, "skipped": [], "count": len(generated)}
```

- [ ] **Step 2: Update narration endpoint response**

Same pattern — wrap TTS calls in try/except, collect failures:

```python
@router.post("/narration")
def generate_narration(req: GenerateRequest, session: SessionStore = Depends(get_session)):
    """Generate TTS narration for narrator segments."""
    storyboard, project_dir = session.require_project()
    output_dir = project_dir / "output"
    narration_dir = output_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors.tts import generate_narration as tts_generate
    import re

    generated = []
    failed = []

    for i, seg in enumerate(storyboard.segments):
        for audio_entry in seg.audio:
            if audio_entry.content_type != "NAR":
                continue

            text = audio_entry.content.strip()
            if not text:
                continue

            text = re.sub(r'\s*\+\s*.*$', '', text)
            text = text.strip('"').strip('\u201c').strip('\u201d')

            if not text:
                continue

            slug = re.sub(r'[^\w\s-]', '', seg.title.lower())
            slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:30]
            out = narration_dir / f"nar-{i:03d}-{slug}.mp3"

            if not out.exists():
                try:
                    tts_generate(
                        text=text,
                        output_path=out,
                        engine=req.tts_engine,
                        voice=req.tts_voice,
                    )
                    generated.append(str(out))
                except Exception as e:
                    failed.append({"path": f"segment-{i}", "error": str(e)})

    status = "ok" if not failed else ("error" if not generated else "partial")
    return {"status": status, "succeeded": generated, "failed": failed, "skipped": [], "count": len(generated)}
```

- [ ] **Step 3: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/api/routes/production.py
git commit -m "feat(video-editor): API production endpoints return succeeded/failed/skipped"
```

### Task 10: Final verification

- [ ] **Step 1: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All 125+ tests pass (113 existing + ~12 new from Tasks 1-3, 7)

- [ ] **Step 2: Verify no remaining silent error swallowing**

Run: `cd bee-content/video-editor && grep -rn "except.*FFmpegError" src/`
Expected: No lines with `pass` after the catch — all should have `result.failed.append` or `raise`

- [ ] **Step 3: Verify no remaining module globals**

Run: `cd bee-content/video-editor && grep -rn "_current_storyboard\|_current_project_dir\|_assignments_path" src/`
Expected: No matches in any file

- [ ] **Step 4: Push**

```bash
git push
```
