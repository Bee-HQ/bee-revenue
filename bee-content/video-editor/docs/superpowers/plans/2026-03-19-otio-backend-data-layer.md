# OTIO Backend Data Layer — Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Swap the backend from old Storyboard model + sidecar JSON files to ParsedStoryboard (Pydantic) + OTIO persistence — session, services, and routes all consume the new model.

**Architecture:** SessionStore loads/saves OTIO files, holds `ParsedStoryboard` as runtime model. Services receive `ParsedStoryboard`. A `parsed_to_schema()` converter keeps the API response shape unchanged for the frontend. Sidecar files (assignments.json, voice.json, segment-order.json) are absorbed on migration and deprecated.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, OpenTimelineIO, pytest

**Spec:** `docs/superpowers/specs/2026-03-19-otio-backend-data-layer-design.md`

---

## File Map

### Modified Files

| File | Change |
|------|--------|
| `src/bee_video_editor/formats/parser.py` | Add `id` field to `ParsedSegment`, populate via `unique_slug` |
| `src/bee_video_editor/formats/otio_convert.py` | `from_otio()` recovers `id` from OTIO metadata |
| `src/bee_video_editor/api/session.py` | Full rewrite — OTIO-based SessionStore |
| `src/bee_video_editor/api/routes/projects.py` | Use `parsed_to_schema()`, new mutation flow |
| `src/bee_video_editor/api/routes/production.py` | Wire to new session, pass `ParsedStoryboard` to services |
| `src/bee_video_editor/services/production.py` | All functions accept `ParsedStoryboard` instead of `Storyboard` |
| `src/bee_video_editor/processors/captions.py` | `extract_caption_segments()` uses new model |
| `src/bee_video_editor/services/preflight.py` | `run_preflight()` uses new model |

### New Files

| File | Responsibility |
|------|---------------|
| `src/bee_video_editor/api/schema_compat.py` | `parsed_to_schema()` converter + helpers |
| `tests/test_schema_compat.py` | Schema conversion tests |
| `tests/test_session_v2.py` | New session tests (OTIO load/save/mutate) |

---

## Task 1: Add `id` Field to ParsedSegment

**Files:**
- Modify: `src/bee_video_editor/formats/parser.py`
- Modify: `src/bee_video_editor/formats/otio_convert.py`
- Modify: `src/bee_video_editor/formats/migrate.py` (also constructs ParsedSegment, needs `id`)
- Modify: `src/bee_video_editor/formats/writer.py` (if needed for round-trip)
- Modify: `tests/test_format_parser.py`

- [ ] **Step 1: Write failing test for segment id**

Add to `tests/test_format_parser.py`:

```python
def test_parse_segments_have_unique_ids():
    """Each parsed segment has a unique slug id."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.segments[0].id == "first-segment"
    assert parsed.segments[1].id == "second-segment"
    ids = [s.id for s in parsed.segments]
    assert len(ids) == len(set(ids))  # all unique
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_parser.py::test_parse_segments_have_unique_ids -v`
Expected: FAIL — `ParsedSegment` has no `id` field

- [ ] **Step 3: Add `id` field to ParsedSegment and populate in parser**

In `src/bee_video_editor/formats/parser.py`:

1. Add `id: str` as the first field of `ParsedSegment` dataclass
2. In `parse_v2()`, after creating each segment, generate `id` via `unique_slug(seg.title, seen_ids)`:

```python
from bee_video_editor.formats.slugify import unique_slug

# In parse_v2, before the parsing loop:
seen_ids: set[str] = set()

# When creating each segment:
seg_id = unique_slug(title, seen_ids)
segment = ParsedSegment(id=seg_id, title=title, start=start, end=end, ...)
```

3. In `from_otio()` in `otio_convert.py`, recover `id` from `clip.metadata["bee_video"]["segment_id"]` and set it on the ParsedSegment.

4. In `old_to_new()` in `migrate.py`, generate `id` via `unique_slug(seg.title, seen_ids)` when constructing each ParsedSegment. Add `seen_ids: set[str] = set()` before the segment loop.

5. Update any tests that construct `ParsedSegment` directly (in `test_format_writer.py`, `test_format_roundtrip.py`, `test_format_migrate.py`) to include the `id` parameter.

- [ ] **Step 4: Run all format tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_*.py tests/test_otio_convert.py tests/test_otio_clean.py -v`
Expected: All PASS

- [ ] **Step 5: Add `segment_duration` helper**

Add to `src/bee_video_editor/formats/parser.py`:

```python
def segment_duration(seg: ParsedSegment) -> float:
    """Calculate segment duration in seconds from start/end timecodes."""
    from bee_video_editor.formats.timecodes import parse_header_tc
    return parse_header_tc(seg.end) - parse_header_tc(seg.start)
```

- [ ] **Step 6: Commit**

```bash
git add -u bee-content/video-editor/src/ bee-content/video-editor/tests/
git commit -m "add id field to ParsedSegment with unique_slug generation"
```

---

## Task 2: Schema Compatibility Converter

**Files:**
- Create: `src/bee_video_editor/api/schema_compat.py`
- Create: `tests/test_schema_compat.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_schema_compat.py
"""Tests for ParsedStoryboard → StoryboardSchema conversion."""

from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_parsed_to_schema_title():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.title == "Test Project"


def test_parsed_to_schema_segment_count():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.total_segments == 2
    assert len(schema.segments) == 2


def test_parsed_to_schema_segment_fields():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert seg.id == "first-segment"
    assert seg.start == "0:00"
    assert seg.end == "0:15"
    assert seg.title == "First Segment"
    assert seg.section == "Section One"
    assert seg.duration_seconds == 15.0


def test_parsed_to_schema_visual_layer():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert len(seg.visual) == 1
    assert seg.visual[0].content_type == "FOOTAGE"
    assert "clip-a.mp4" in seg.visual[0].content


def test_parsed_to_schema_audio_excludes_music():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    # REAL_AUDIO should be in audio, not music
    assert any(a.content_type == "REAL_AUDIO" for a in seg.audio)
    assert not any(a.content_type == "REAL_AUDIO" for a in seg.music)


def test_parsed_to_schema_narration_in_audio():
    """Narration text should appear as a NAR entry in the audio layer."""
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    nar_entries = [a for a in seg.audio if a.content_type == "NAR"]
    assert len(nar_entries) == 1
    assert "first narration line" in nar_entries[0].content


def test_parsed_to_schema_assigned_media():
    """Visual entries with src should appear in assigned_media dict."""
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert seg.assigned_media.get("visual:0") == "footage/clip-a.mp4"


def test_parsed_to_schema_transition():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[1]
    assert len(seg.transition) == 1
    assert "dissolve" in seg.transition[0].content_type.lower()


def test_parsed_to_schema_stock_count():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.stock_footage_needed == 1  # second segment has STOCK visual


def test_parsed_to_schema_sections():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert "Section One" in schema.sections


def _load_minimal():
    from bee_video_editor.formats.parser import parse_v2
    return parse_v2(FIXTURES / "storyboard_v2_minimal.md")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_schema_compat.py -v`
Expected: FAIL — `schema_compat` module not found

- [ ] **Step 3: Implement `parsed_to_schema()`**

Create `src/bee_video_editor/api/schema_compat.py`:

```python
"""Convert ParsedStoryboard → StoryboardSchema for API backward compatibility."""

from __future__ import annotations

from bee_video_editor.api.schemas import (
    LayerEntrySchema,
    SegmentSchema,
    StoryboardSchema,
)
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
from bee_video_editor.formats.timecodes import parse_header_tc


def parsed_to_schema(parsed: ParsedStoryboard) -> StoryboardSchema:
    """Convert ParsedStoryboard to the old-format StoryboardSchema."""
    segments = [_segment_to_schema(seg) for seg in parsed.segments]

    stock_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "STOCK")
    photo_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "PHOTO")
    map_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "MAP")

    max_end = max((parse_header_tc(s.end) for s in parsed.segments), default=0)

    return StoryboardSchema(
        title=parsed.project.title,
        total_segments=len(segments),
        total_duration_seconds=int(max_end),
        sections=[sec.title for sec in parsed.sections],
        segments=segments,
        stock_footage_needed=stock_count,
        photos_needed=photo_count,
        maps_needed=map_count,
        production_rules=[],
    )


def _segment_to_schema(seg: ParsedSegment) -> SegmentSchema:
    visual = [
        LayerEntrySchema(
            content=v.src or v.query or v.prompt or v.type,
            content_type=v.type,
        )
        for v in seg.config.visual
    ]

    audio = [
        LayerEntrySchema(content=a.src or "", content_type=a.type)
        for a in seg.config.audio if a.type not in ("MUSIC",)
    ]
    # Add narration as a NAR audio entry
    if seg.narration:
        audio.append(LayerEntrySchema(content=seg.narration, content_type="NAR"))

    music = [
        LayerEntrySchema(content=a.src or "", content_type=a.type)
        for a in seg.config.audio if a.type == "MUSIC"
    ]

    overlay = [
        LayerEntrySchema(
            content=o.text or o.quote or o.date or o.amount or "",
            content_type=o.type,
        )
        for o in seg.config.overlay
    ]

    source = [
        LayerEntrySchema(content=v.src or "", content_type=v.type)
        for v in seg.config.visual if v.src
    ]

    transition = []
    if seg.config.transition_in:
        transition.append(LayerEntrySchema(
            content=f"{seg.config.transition_in.duration}s",
            content_type=seg.config.transition_in.type.upper(),
        ))

    assigned_media: dict[str, str] = {}
    for i, v in enumerate(seg.config.visual):
        if v.src:
            assigned_media[f"visual:{i}"] = v.src

    return SegmentSchema(
        id=seg.id,
        start=seg.start,
        end=seg.end,
        title=seg.title,
        section=seg.section,
        section_time="",
        subsection="",
        duration_seconds=segment_duration(seg),
        visual=visual,
        audio=audio,
        overlay=overlay,
        music=music,
        source=source,
        transition=transition,
        assigned_media=assigned_media,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_schema_compat.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/api/schema_compat.py bee-content/video-editor/tests/test_schema_compat.py
git commit -m "add parsed_to_schema converter for API backward compatibility"
```

---

## Task 3: Rewrite SessionStore

**Files:**
- Modify: `src/bee_video_editor/api/session.py`
- Create: `tests/test_session_v2.py`

This is the biggest task — full rewrite of SessionStore to use OTIO.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_session_v2.py
"""Tests for the OTIO-based SessionStore."""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_otio_file(tmp_path):
    """Load an .otio file directly."""
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib

    # Create an OTIO file
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "test.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))

    session = SessionStore()
    session.load_project(otio_path, tmp_path)
    assert session.parsed is not None
    assert session.parsed.project.title == "Test Project"
    assert len(session.parsed.segments) == 2


def test_load_v2_markdown_creates_otio(tmp_path):
    """Loading a v2 .md auto-creates .otio next to it."""
    import shutil
    from bee_video_editor.api.session import SessionStore

    md_copy = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_copy)

    session = SessionStore()
    session.load_project(md_copy, tmp_path)
    assert session.parsed is not None
    assert (tmp_path / "storyboard.otio").exists()


def test_load_old_markdown_auto_migrates(tmp_path):
    """Loading an old table-format .md auto-migrates to OTIO."""
    from bee_video_editor.api.session import SessionStore

    # Create a minimal old-format storyboard
    old_md = tmp_path / "old.md"
    old_md.write_text(
        "# Test\n\n## Section (0:00 - 0:10)\n\n"
        "### 0:00 - 0:10 | Seg Title\n"
        "| Layer | Content |\n|---|---|\n"
        "| Visual | `FOOTAGE:` clip.mp4 |\n"
    )

    session = SessionStore()
    session.load_project(old_md, tmp_path)
    assert session.parsed is not None
    assert (tmp_path / "old.otio").exists()


def test_assign_media_mutates_and_saves(tmp_path):
    """Assigning media updates parsed model and saves OTIO."""
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "test.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))

    session = SessionStore()
    session.load_project(otio_path, tmp_path)

    seg_id = session.parsed.segments[0].id
    session.assign_media(seg_id, "visual", 0, "footage/new-clip.mp4")

    # In-memory update
    assert session.parsed.segments[0].config.visual[0].src == "footage/new-clip.mp4"

    # Persisted to disk
    tl2 = otio_lib.adapters.read_from_file(str(otio_path))
    from bee_video_editor.formats.otio_convert import from_otio
    parsed2 = from_otio(tl2)
    assert parsed2.segments[0].config.visual[0].src == "footage/new-clip.mp4"


def test_reorder_segments(tmp_path):
    """Reordering segments updates parsed model and saves OTIO."""
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "test.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))

    session = SessionStore()
    session.load_project(otio_path, tmp_path)

    ids = [s.id for s in session.parsed.segments]
    session.reorder_segments(list(reversed(ids)))
    assert session.parsed.segments[0].id == ids[-1]


def test_require_project_raises_without_load():
    from bee_video_editor.api.session import SessionStore
    from fastapi import HTTPException
    session = SessionStore()
    with pytest.raises(HTTPException):
        session.require_project()


def test_require_project_returns_parsed(tmp_path):
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2, ParsedStoryboard
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "test.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))

    session = SessionStore()
    session.load_project(otio_path, tmp_path)
    result_parsed, result_dir = session.require_project()
    assert isinstance(result_parsed, ParsedStoryboard)
    assert result_dir == tmp_path


def test_sidecar_absorption_assignments(tmp_path):
    """Sidecar assignments.json is absorbed on old-format load."""
    import shutil
    from bee_video_editor.api.session import SessionStore

    md_copy = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_copy)

    # Create sidecar assignments
    bee_dir = tmp_path / ".bee-video"
    bee_dir.mkdir()
    assignments = {"first-segment": {"visual:0": "footage/assigned.mp4"}}
    (bee_dir / "assignments.json").write_text(json.dumps(assignments))

    session = SessionStore()
    session.load_project(md_copy, tmp_path)

    assert session.parsed.segments[0].config.visual[0].src == "footage/assigned.mp4"


def test_sidecar_absorption_voice_lock(tmp_path):
    """Sidecar voice.json is absorbed into project config."""
    import shutil
    from bee_video_editor.api.session import SessionStore

    md_copy = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_copy)

    bee_dir = tmp_path / ".bee-video"
    bee_dir.mkdir()
    (bee_dir / "voice.json").write_text(json.dumps({"engine": "elevenlabs", "voice": "Daniel"}))

    session = SessionStore()
    session.load_project(md_copy, tmp_path)
    assert session.parsed.project.voice_lock is not None
    assert session.parsed.project.voice_lock.engine == "elevenlabs"


def test_sidecar_absorption_segment_order(tmp_path):
    """Sidecar segment-order.json is absorbed on load."""
    import shutil
    from bee_video_editor.api.session import SessionStore

    md_copy = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_copy)

    bee_dir = tmp_path / ".bee-video"
    bee_dir.mkdir()
    (bee_dir / "segment-order.json").write_text(json.dumps(["second-segment", "first-segment"]))

    session = SessionStore()
    session.load_project(md_copy, tmp_path)
    assert session.parsed.segments[0].id == "second-segment"


def test_assign_media_unassign(tmp_path):
    """Empty media_path clears the assignment."""
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "test.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))

    session = SessionStore()
    session.load_project(otio_path, tmp_path)
    seg_id = session.parsed.segments[0].id
    # Unassign
    session.assign_media(seg_id, "visual", 0, "")
    assert session.parsed.segments[0].config.visual[0].src is None


def test_assign_media_invalid_segment_raises():
    """Assigning to nonexistent segment raises 404."""
    from bee_video_editor.api.session import SessionStore
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    import opentimelineio as otio_lib
    import tempfile
    from fastapi import HTTPException

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
        tl = to_otio(parsed)
        otio_path = tmp_path / "test.otio"
        otio_lib.adapters.write_to_file(tl, str(otio_path))

        session = SessionStore()
        session.load_project(otio_path, tmp_path)
        with pytest.raises(HTTPException):
            session.assign_media("nonexistent-id", "visual", 0, "clip.mp4")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_session_v2.py -v`
Expected: FAIL — SessionStore doesn't have `parsed` attribute

- [ ] **Step 3: Rewrite SessionStore**

Rewrite `src/bee_video_editor/api/session.py`. Key changes:

1. Replace `storyboard: Storyboard | None` with `timeline`, `parsed`, `otio_path`
2. `load_project(path, project_dir)`:
   - Detect file type (.otio vs .md)
   - For .md: detect v2 (has `bee-video:project`) vs old (table format)
   - Convert to OTIO, save .otio, store both timeline and parsed
   - Absorb sidecar files if present
3. `require_project()` returns `tuple[ParsedStoryboard, Path]`
4. `assign_media()` mutates `parsed.segments[].config.visual[].src` and autosaves
5. `reorder_segments()` reorders `parsed.segments` and autosaves
6. `_autosave()` helper: `to_otio(parsed)` → write to `otio_path`
7. `save_voice_config()` → updates `parsed.project.voice_lock` and autosaves
8. `_save_session()` → writes `session.json` with `otio_path` instead of `storyboard_path`

Keep `_try_restore()` and `get_session()` — update to use new field names.

- [ ] **Step 4: Run session tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_session_v2.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/api/session.py bee-content/video-editor/tests/test_session_v2.py
git commit -m "rewrite SessionStore for OTIO-based persistence"
```

---

## Task 4: Wire Project Routes

**Files:**
- Modify: `src/bee_video_editor/api/routes/projects.py`

- [ ] **Step 1: Replace old schema converter with `parsed_to_schema`**

Rewrite `projects.py`:

```python
"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from bee_video_editor.api.schema_compat import parsed_to_schema
from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    LoadProjectRequest,
    ReorderSegmentsRequest,
    StoryboardSchema,
)
from bee_video_editor.api.session import SessionStore, get_session

router = APIRouter()


@router.post("/load", response_model=StoryboardSchema)
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    """Load a storyboard file and return the parsed project."""
    session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return parsed_to_schema(session.parsed)


@router.get("/current", response_model=StoryboardSchema)
def get_current_project(session: SessionStore = Depends(get_session)):
    """Get the currently loaded project."""
    parsed, _ = session.require_project()
    return parsed_to_schema(parsed)


@router.put("/assign")
def assign_media(req: AssignMediaRequest, session: SessionStore = Depends(get_session)):
    """Assign a media file to a segment layer."""
    return session.assign_media(req.segment_id, req.layer, req.layer_index, req.media_path)


@router.put("/reorder")
def reorder_segments(req: ReorderSegmentsRequest, session: SessionStore = Depends(get_session)):
    """Persist a custom segment ordering."""
    session.reorder_segments(req.segment_order)
    return {"status": "ok", "count": len(req.segment_order)}
```

- [ ] **Step 2: Run existing API tests for project routes**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_api.py -k "project" -v`
Expected: Need to check which pass. Some may need adjustment if they use old storyboard format fixtures.

- [ ] **Step 3: Fix any failing API tests**

Update test fixtures/setup to work with the new session. The key change: tests that call `/load` with an old-format storyboard should still work because SessionStore auto-migrates.

- [ ] **Step 4: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/api/routes/projects.py
git commit -m "wire project routes to OTIO-based session and parsed_to_schema"
```

---

## Task 5: Migrate Production Service Functions

**Files:**
- Modify: `src/bee_video_editor/services/production.py`
- Modify: `tests/test_production.py`

This is the largest task — migrating all service functions from `Storyboard` to `ParsedStoryboard`.

- [ ] **Step 1: Update imports and type annotations**

At the top of `production.py`, change:

```python
# Old:
from bee_video_editor.models_storyboard import Storyboard, StoryboardSegment

# New:
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
```

- [ ] **Step 2: Migrate `_derive_segment_type()`**

```python
def _derive_segment_type(seg: ParsedSegment) -> str:
    has_footage = any(v.type == "FOOTAGE" for v in seg.config.visual)
    has_nar = bool(seg.narration)
    has_real_audio = any(a.type == "REAL_AUDIO" for a in seg.config.audio)
    has_gen_visual = any(v.type in ("GRAPHIC", "MAP", "STOCK", "WAVEFORM") for v in seg.config.visual)
    if has_footage and has_nar:
        return "MIX"
    if has_footage or has_real_audio:
        return "REAL"
    if has_nar:
        return "NAR"
    if has_gen_visual:
        return "GEN"
    return "GEN"
```

- [ ] **Step 3: Migrate `init_project()`**

Change signature to accept `ParsedStoryboard` instead of parsing from path. **Note: return type changes from `tuple[Storyboard, ProductionState]` to just `ProductionState`** — all call sites (in routes and CLI) that destructure the tuple must be updated:

```python
def init_project(
    parsed: ParsedStoryboard,
    config: ProductionConfig,
) -> ProductionState:
```

Use `parsed.segments` instead of parsing from file. Use `segment_duration(seg)` for time ranges. Remove the internal `parse_storyboard()` call.

- [ ] **Step 4: Migrate `generate_graphics_for_project()`**

Change signature: `project: ParsedStoryboard`. Key mappings:
- `seg.overlay` → `seg.config.overlay`
- `entry.content_type == "LOWER-THIRD"` → `entry.type == "LOWER_THIRD"`
- Regex-parsed name/role from `entry.content` → `entry.text` and `entry.subtext`
- `entry.content_type == "TIMELINE-MARKER"` → `entry.type == "TIMELINE_MARKER"` (in overlay, not visual)
- `entry.content_type == "FINANCIAL-CARD"` → `entry.type == "FINANCIAL_CARD"` (in overlay)

- [ ] **Step 5: Migrate `generate_narration_for_project()`**

Change signature: `project: ParsedStoryboard`. Key change:
- Instead of iterating `seg.audio` looking for `content_type == "NAR"`, use `seg.narration` directly
- `seg.subsection or seg.section` → `seg.section` (subsection doesn't exist in new model)

- [ ] **Step 6: Migrate `trim_source_footage()`**

Change signature: `project: ParsedStoryboard`. Key change:
- Instead of iterating `seg.source` and parsing freeform content, iterate `seg.config.visual` entries with `src` + `tc_in` + `out`

- [ ] **Step 7: Migrate `run_full_pipeline()`**

Change signature to accept `ParsedStoryboard` instead of `storyboard_path`:

```python
def run_full_pipeline(
    parsed: ParsedStoryboard,
    config: ProductionConfig,
    ...
) -> PipelineResult:
```

Remove the internal `parse_storyboard()` call. Pass `parsed` to all sub-functions.

- [ ] **Step 8: Migrate `generate_all_previews()` and `rough_cut_export()`**

Both functions read from `seg.assigned_media` in the old model. In the new model, assignments are in `seg.config.visual[].src`:

```python
# Old: seg.assigned_media.get("visual:0")
# New: seg.config.visual[0].src if seg.config.visual else None
```

Update both functions to accept `ParsedStoryboard` and iterate `seg.config.visual` for assigned media paths.

- [ ] **Step 9: Migrate `apply_voice_lock()`**

Change `ProductionConfig.apply_voice_lock()`:

```python
def apply_voice_lock(self, voice_lock: "VoiceLock | None" = None) -> None:
    """Apply voice lock from project config if no explicit engine/voice was set."""
    if voice_lock is None:
        return
    if self.tts_engine == "edge" and self.tts_voice is None:
        self.tts_engine = voice_lock.engine
        self.tts_voice = voice_lock.voice
```

- [ ] **Step 9: Update production tests**

Update `tests/test_production.py` to construct `ParsedStoryboard` objects instead of `Storyboard`. Use the same assertion patterns.

- [ ] **Step 10: Run all tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All PASS

- [ ] **Step 11: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/services/production.py bee-content/video-editor/tests/test_production.py
git commit -m "migrate production service to ParsedStoryboard"
```

---

## Task 6: Migrate Captions and Preflight

**Files:**
- Modify: `src/bee_video_editor/processors/captions.py`
- Modify: `src/bee_video_editor/services/preflight.py`
- Modify: `tests/test_captions.py`
- Modify: `tests/test_preflight.py`

- [ ] **Step 1: Migrate `extract_caption_segments()`**

In `processors/captions.py`, change `extract_caption_segments()` to accept `ParsedStoryboard`:

Old pattern:
```python
for seg in storyboard.segments:
    for entry in seg.audio:
        if entry.content_type == "NAR":
            text = entry.content
```

New pattern:
```python
for seg in parsed.segments:
    if seg.narration:
        text = seg.narration
```

- [ ] **Step 2: Migrate `run_preflight()`**

In `services/preflight.py`, change to accept `ParsedStoryboard`:

Old: `entry.content_type`, `entry.content`
New: `entry.type`, `entry.src` (for visuals), `seg.narration` (for NAR)

- [ ] **Step 3: Update caption and preflight tests**

Update test data construction to use `ParsedStoryboard`.

- [ ] **Step 4: Run tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_captions.py tests/test_preflight.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/processors/captions.py bee-content/video-editor/src/bee_video_editor/services/preflight.py bee-content/video-editor/tests/test_captions.py bee-content/video-editor/tests/test_preflight.py
git commit -m "migrate captions and preflight to ParsedStoryboard"
```

---

## Task 7: Wire Production Routes

**Files:**
- Modify: `src/bee_video_editor/api/routes/production.py`
- Modify: `tests/test_api.py`

- [ ] **Step 1: Update all `require_project()` call sites**

Every route handler that calls `session.require_project()` currently destructures to `storyboard, project_dir`. Change all to `parsed, project_dir`:

```python
# Old:
storyboard, project_dir = session.require_project()
# New:
parsed, project_dir = session.require_project()
```

- [ ] **Step 2: Update production status route**

```python
@router.get("/status")
def get_production_status(session: SessionStore = Depends(get_session)):
    parsed, project_dir = session.require_project()
    # Use len(parsed.segments) instead of storyboard.total_segments
```

- [ ] **Step 3: Update graphics/narration/assemble routes**

Pass `parsed` (session.parsed) to service functions instead of `storyboard`.

Update `apply_voice_lock()` calls: `config.apply_voice_lock(parsed.project.voice_lock)`.

- [ ] **Step 4: Update `_count_narration_segments` helper**

```python
def _count_narration_segments(parsed: ParsedStoryboard) -> int:
    return sum(1 for seg in parsed.segments if seg.narration)
```

- [ ] **Step 5: Update WebSocket handlers**

Change `session.storyboard_path` to `session.otio_path` in `_ws_produce()` and `_ws_narration()`.

For `_ws_produce()`, pass `session.parsed` to `run_full_pipeline()` instead of `session.storyboard_path`.

For `_ws_narration()`, update the inline narration counting loop (around line 343-345) that iterates `seg.audio` looking for `content_type == "NAR"`. Replace with: `sum(1 for seg in parsed.segments if seg.narration)`.

- [ ] **Step 6: Update graphics route handler**

The `POST /graphics` route handler (production.py ~line 60-113) has inline logic that accesses `seg.overlay` and checks `overlay.content_type == "GRAPHIC"`. Update to use `seg.config.overlay` and `overlay.type`.

- [ ] **Step 7: Update `POST /export/otio` route**

Change from using old `exporters/otio_export.py` to using `clean_otio(session.timeline)`. Mark `exporters/otio_export.py` as deprecated.

- [ ] **Step 8: Update voice lock routes**

`PUT /voice-lock` and `GET /voice-lock` routes currently call `session.save_voice_config()` and `session.load_voice_config()` which read/write `voice.json`. Update to mutate `session.parsed.project.voice_lock` and autosave.

- [ ] **Step 9: Update `generate_segment_preview` route**

This route accesses `seg.assigned_media.get("visual:0")` on the old model. Change to: `seg.config.visual[0].src if seg.config.visual else None`.

- [ ] **Step 10: Add `GET /api/projects/export` endpoint**

New endpoint that exports the current project to markdown or clean OTIO:

```python
@router.get("/export")
def export_project(format: str = "md", session: SessionStore = Depends(get_session)):
    parsed, project_dir = session.require_project()
    if format == "md":
        from bee_video_editor.formats.writer import write_v2
        md = write_v2(parsed)
        return {"format": "md", "content": md}
    elif format == "otio":
        from bee_video_editor.formats.otio_convert import clean_otio
        import opentimelineio as otio_lib
        clean = clean_otio(session.timeline)
        out_path = project_dir / "output" / "export.otio"
        otio_lib.adapters.write_to_file(clean, str(out_path))
        return {"format": "otio", "path": str(out_path)}
```

- [ ] **Step 6: Update API tests**

Update `tests/test_api.py` — the API response shape is unchanged (thanks to `parsed_to_schema`), but test setup may need to load storyboards differently.

- [ ] **Step 7: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/api/routes/production.py bee-content/video-editor/tests/test_api.py
git commit -m "wire production routes to OTIO-based session"
```

---

## Task 8: Update Formats Package Exports + Final Integration

**Files:**
- Modify: `src/bee_video_editor/formats/__init__.py`

- [ ] **Step 1: Update package exports**

```python
"""Storyboard format v2 — markdown with JSON blocks + OTIO conversion."""

from bee_video_editor.formats.parser import (
    parse_v2, ParsedStoryboard, ParsedSegment, ParsedSection,
    StoryboardParseError, segment_duration,
)
from bee_video_editor.formats.writer import write_v2
from bee_video_editor.formats.otio_convert import to_otio, from_otio, clean_otio
from bee_video_editor.formats.migrate import old_to_new

__all__ = [
    "parse_v2", "write_v2",
    "to_otio", "from_otio", "clean_otio",
    "old_to_new", "segment_duration",
    "ParsedStoryboard", "ParsedSegment", "ParsedSection",
    "StoryboardParseError",
]
```

- [ ] **Step 2: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: ALL tests pass — both new and existing

- [ ] **Step 3: Run CLI smoke test**

```bash
cd bee-content/video-editor
uv run bee-video import-md tests/fixtures/storyboard_v2_minimal.md --output /tmp/test.otio
uv run bee-video export /tmp/test.otio --format md --output /tmp/test.md
```

Expected: Both commands succeed.

- [ ] **Step 4: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/__init__.py
git commit -m "finalize Phase 2: OTIO backend data layer complete"
```

---

## Summary

| Task | What | Key Risk |
|------|------|----------|
| 1 | Add `id` to ParsedSegment + migrate.py | Round-trip must preserve id |
| 2 | Schema compat converter | Must match old API response shape exactly |
| 3 | Rewrite SessionStore | Core refactor — load/save/mutate all change |
| 4 | Wire project routes | 4 endpoints, mechanical |
| 5 | Migrate production services | Largest task — 9+ functions change signatures (including previews, rough cut) |
| 6 | Migrate captions + preflight | 2 functions, moderate |
| 7 | Wire production routes | 14+ call sites + export/voice-lock/preview/graphics routes + WebSocket |
| 8 | Final integration | Smoke test everything |
