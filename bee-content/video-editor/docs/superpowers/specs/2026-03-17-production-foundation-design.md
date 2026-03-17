# Design: Production Foundation — Error Handling, Progress Tracking, Session Management

**Date:** 2026-03-17
**Scope:** Fix the three foundational weaknesses in bee-video-editor's backend
**Approach:** B — Result objects with clean separation

---

## Problem

Three issues in `services/production.py` and `api/routes/` make the tool unreliable for actual video production:

1. **FFmpegError silently swallowed** — `except FFmpegError: pass` in `trim_source_footage` (line 230) and `normalize_all_segments` (line 248). Callers have no idea what failed or why.
2. **Segment statuses never updated** — `SegmentStatus` objects are created during `init_project` but never transition from `"pending"` to `"processing"`/`"done"`/`"error"`. The status endpoint always shows stale data.
3. **Module-level globals for session** — `_current_storyboard`, `_current_project_dir`, `_assignments_path` in `api/routes/projects.py` (lines 23-25). Not thread-safe, not testable, cross-module imports via `from routes.projects import _current_project_dir`.

## Solution

### 1. ProductionResult dataclass

New dataclasses in `services/production.py`:

```python
@dataclass
class FailedItem:
    """A single failed processing step."""
    path: str       # what was being processed (source file, segment ID, etc.)
    error: str      # error message

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

**Functions that change return type from `list[Path]` to `ProductionResult`:**
- `generate_graphics_for_project`
- `generate_narration_for_project`
- `trim_source_footage`
- `normalize_all_segments`

**Pattern for each function:**

```python
def trim_source_footage(project, config, state) -> ProductionResult:
    result = ProductionResult()
    for note in project.trim_notes:
        ...
        try:
            trim(source, out, start=t.start, end=t.duration)
            result.succeeded.append(out)
        except FFmpegError as e:
            result.failed.append(FailedItem(path=str(source), error=str(e)))
    return result
```

No silent `pass`. Every error captured with context.

**`assemble_final` stays as-is** — it already raises on failure and has only one output. No need for ProductionResult there.

### 2. ProductionState.track() context manager

Add to `ProductionState`:

```python
@contextmanager
def track(self, index: int, state_path: Path):
    """Track segment processing. Sets status to processing/done/error and saves."""
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

Add `state_path` as a derived property on `ProductionConfig`:

```python
@property
def state_path(self) -> Path:
    return self.output_dir / "production_state.json"
```

**`track()` bounds check:**

```python
if index < 0 or index >= len(self.segment_statuses):
    raise ValueError(f"Segment index {index} out of range (0-{len(self.segment_statuses)-1})")
```

This prevents `IndexError` from corrupted/stale state files.

**`state` parameter is optional** — production functions accept `state: ProductionState | None = None`. When `None`, status tracking is skipped (no `track()` calls). This is critical because the CLI allows running `bee-video graphics` without first running `bee-video init` — there may be no state file yet.

```python
def generate_narration_for_project(
    project, config, state: ProductionState | None = None
) -> ProductionResult:
    result = ProductionResult()
    if state:
        state.phase = "narration"
        state.save(config.state_path)

    for i, seg in enumerate(project.segments):
        if seg.segment_type not in (SegmentType.NAR, SegmentType.MIX):
            continue
        try:
            if state:
                with state.track(i, config.state_path):
                    # ... generate narration ...
                    result.succeeded.append(out)
            else:
                # ... generate narration (no tracking) ...
                result.succeeded.append(out)
        except Exception as e:
            result.failed.append(FailedItem(path=f"segment-{i}", error=str(e)))
    return result
```

The `try/except` around `track()` catches the re-raised exception from the context manager so it lands in `ProductionResult.failed` without stopping the loop.

**Phase vocabulary** (replaces the old `init, parsing, assets, trimming, compositing, assembly, done`):
- `init_project` → `"parsed"`
- `generate_graphics_for_project` → `"graphics"`
- `generate_narration_for_project` → `"narration"`
- `trim_source_footage` → `"trimming"`
- `normalize_all_segments` → `"normalizing"`
- `assemble_final` → `"assembly"`, then `"done"` on success

### 3. SessionStore class

New file: `src/bee_video_editor/api/session.py`

```python
@dataclass
class SessionStore:
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

    def assign_media(self, segment_id: str, layer: str, index: int, media_path: str) -> dict:
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

        return {"status": "ok", "segment_id": segment_id, "key": key, "media_path": media_path}

    def _load_assignments(self) -> dict:
        if self.assignments_path and self.assignments_path.exists():
            with open(self.assignments_path) as f:
                return json.load(f)
        return {}

    def _save_assignments(self, assignments: dict):
        if self.assignments_path:
            self.assignments_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.assignments_path, "w") as f:
                json.dump(assignments, f, indent=2)
```

**Wiring via FastAPI dependency injection:**

`get_session` lives in `api/session.py` alongside `SessionStore` so routes import from one place:

```python
# api/session.py (bottom of file)
_session = SessionStore()

def get_session() -> SessionStore:
    return _session
```

```python
# routes/projects.py
from bee_video_editor.api.session import SessionStore, get_session
from fastapi import Depends

@router.post("/load")
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    ...
```

`server.py` does NOT need to create the instance — it's a module-level singleton in `session.py`. Server just includes the routers as before.

**Route changes:**

```python
# routes/projects.py — before:
global _current_storyboard, _current_project_dir, _assignments_path

# routes/projects.py — after:
@router.post("/load")
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    sb = session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return _storyboard_to_schema(sb)
```

```python
# routes/media.py — before:
from bee_video_editor.api.routes.projects import _current_project_dir

# routes/media.py — after:
@router.get("")
def list_media(session: SessionStore = Depends(get_session)):
    _, project_dir = session.require_project()
    ...
```

```python
# routes/production.py — before:
from bee_video_editor.api.routes.projects import _current_project_dir, _current_storyboard

# routes/production.py — after:
@router.get("/status")
def get_production_status(session: SessionStore = Depends(get_session)):
    storyboard, project_dir = session.require_project()
    ...
```

All three module globals eliminated. Cross-module imports of private variables eliminated.

## Files Changed

| File | Change |
|------|--------|
| `services/production.py` | Add `ProductionResult`, `FailedItem`. Add `track()` with bounds check to `ProductionState`. Add `state_path` property to `ProductionConfig`. Refactor all 4 production functions to return `ProductionResult` and accept optional `state` param. Update `init_project` line 111 to use `config.state_path`. |
| `api/session.py` | **New file.** `SessionStore` class with `load_project`, `require_project`, `assign_media`, assignment persistence. Module-level `_session` singleton + `get_session()` dependency function. |
| `api/server.py` | No structural changes needed — `session.py` owns the singleton. Routers are included as before. |
| `api/routes/projects.py` | Remove 3 module globals + `_load_assignments`/`_save_assignments` helpers. Use `SessionStore` via `Depends(get_session)`. |
| `api/routes/media.py` | Replace `_get_project_dir()` import with `SessionStore` via `Depends(get_session)`. |
| `api/routes/production.py` | Replace `_get_state()` import with `SessionStore` via `Depends(get_session)`. Update graphics/narration endpoints to return `ProductionResult` info. |
| `adapters/cli.py` | Update calls to production functions to handle `ProductionResult` (show succeeded/failed counts via Rich). |
| `adapters/dashboard.py` | Update calls to production functions to handle `ProductionResult` (uses `result.succeeded` instead of raw list). |
| `tests/test_production.py` | Update assertions for `ProductionResult` return type. Add tests for `track()` context manager (including bounds check, crash-leaves-processing-status). Add test for `SessionStore`. |

## Files NOT Changed

- `processors/ffmpeg.py` — still raises `FFmpegError`, no change
- `processors/graphics.py` — no change
- `processors/tts.py` — no change
- `parsers/*` — no change
- `models.py`, `models_storyboard.py` — no change
- `web/*` — no frontend changes needed now. The `count` field in API responses stays the same. Note: frontend currently shows "generated N files" even on partial failure — a future frontend update should surface `failed` items, but it's not a blocker for this backend change.

## Known Limitations

- **Concurrency:** `SessionStore` is a single-process singleton with the same thread-safety profile as the module globals it replaces. Two concurrent `assign_media` calls could lose a write. Thread-safe writes (e.g., file locking) are deferred to a future iteration.
- **`ProductionResult.skipped`:** Defined but not yet populated by any production function. Forward-looking for when "already exists" segments are tracked explicitly rather than silently skipped.
- **Corrupted state file:** `ProductionState.load()` will raise on malformed JSON. No graceful recovery — caller should catch and re-init. A future improvement could add validation or auto-repair.

## API Response Changes

The `/api/production/graphics` and `/api/production/narration` endpoints currently return:
```json
{"status": "ok", "generated": [...], "count": 3}
```

After this change they return:
```json
{"status": "ok", "succeeded": [...], "failed": [...], "skipped": [...], "count": 3}
```

- `status`: `"ok"` if no failures, `"partial"` if some failed, `"error"` if all failed
- `count`: always `len(succeeded)` — never includes failures
- `succeeded` replaces the old `generated` field
- The frontend reads `count` which stays the same — no frontend break. But "generated N files" will not surface failures until a future frontend update.

## Testing Strategy

- **Unit tests for `ProductionResult`** — verify `ok` property, accumulation of succeeded/failed/skipped
- **Unit tests for `track()` context manager** — verify status transitions (pending→processing→done, pending→processing→error), verify state saved to disk on each transition, verify bounds check raises `ValueError`, verify crash-during-processing leaves status as `"processing"` in state file
- **Unit tests for `SessionStore`** — verify `load_project` parses and restores assignments, `require_project` raises 404 when empty, `assign_media` persists to sidecar JSON
- **Integration test** — mock FFmpeg to fail on specific segments, verify `ProductionResult.failed` contains the right items with error messages, verify `ProductionState` shows correct statuses after run
- **Dashboard adapter test** — verify `dashboard.py` handles `ProductionResult` return type (uses `result.succeeded`)
