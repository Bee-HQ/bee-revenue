# OTIO Project Format — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the new markdown format (with JSON code blocks), Pydantic models, bidirectional markdown ↔ OTIO converters, clean OTIO export, and migration from old format — all backend-only, no UI changes.

**Architecture:** New `formats/` package contains Pydantic models, markdown parser, markdown writer, and OTIO converters. The markdown parser reads `bee-video:project` and `bee-video:segment` JSON blocks. Converters translate between the parsed models and OTIO timelines. Round-trip is lossless under canonical serialization.

**Tech Stack:** Python 3.11+, Pydantic v2, OpenTimelineIO >= 0.17.0, pytest

**Spec:** `docs/superpowers/specs/2026-03-19-otio-project-format-design.md`

---

## File Map

### New Files

| File | Responsibility |
|------|---------------|
| `src/bee_video_editor/formats/__init__.py` | Package init — re-exports key functions |
| `src/bee_video_editor/formats/models.py` | Pydantic models: `ProjectConfig`, `SegmentConfig`, `VisualEntry`, `AudioEntry`, `OverlayEntry`, `CaptionsConfig`, `TransitionConfig` |
| `src/bee_video_editor/formats/timecodes.py` | `parse_header_tc()`, `format_header_tc()`, `parse_precise_tc()`, `format_precise_tc()`, `tc_to_seconds()` |
| `src/bee_video_editor/formats/slugify.py` | `slugify(title)`, `unique_slug(title, seen)` |
| `src/bee_video_editor/formats/parser.py` | `parse_v2(path_or_text) → ParsedStoryboard` — reads new markdown format |
| `src/bee_video_editor/formats/writer.py` | `write_v2(parsed) → str` — canonical markdown serialization |
| `src/bee_video_editor/formats/otio_convert.py` | `to_otio(parsed) → Timeline`, `from_otio(timeline) → ParsedStoryboard`, `clean_otio(timeline) → Timeline` |
| `src/bee_video_editor/formats/migrate.py` | `old_to_new(storyboard: Storyboard) → ParsedStoryboard` |
| `tests/test_format_models.py` | Model validation tests |
| `tests/test_timecodes.py` | Timecode parsing/formatting tests |
| `tests/test_slugify.py` | Slugification tests |
| `tests/test_format_parser.py` | New markdown parser tests |
| `tests/test_format_writer.py` | Canonical writer tests |
| `tests/test_format_roundtrip.py` | markdown → OTIO → markdown round-trip tests |
| `tests/test_otio_convert.py` | OTIO conversion tests |
| `tests/test_otio_clean.py` | Clean OTIO export tests |
| `tests/test_format_migrate.py` | Old → new migration tests |
| `tests/fixtures/storyboard_v2_minimal.md` | Minimal valid storyboard (1 section, 2 segments) |
| `tests/fixtures/storyboard_v2_full.md` | Full-featured storyboard (all visual/audio/overlay types, multi-visual, narration) |

### Modified Files

| File | Change |
|------|--------|
| `pyproject.toml` | Add `pydantic>=2.0.0` and `opentimelineio>=0.17.0` to core `dependencies` |
| `src/bee_video_editor/models_storyboard.py` | Add `GENERATED` to `VisualType` enum, rename `REAL_AUDIO` value from `"REAL AUDIO"` to `"REAL_AUDIO"` |
| `src/bee_video_editor/adapters/cli.py` | Rename existing `export` → `export-legacy`, add new `import-md` and `export` commands |

---

## Task 1: Dependencies

**Files:**
- Modify: `pyproject.toml:10-17` (core dependencies)

- [ ] **Step 1: Add pydantic and opentimelineio to core dependencies**

```toml
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pillow>=10.0.0",
    "edge-tts>=6.1.0",
    "pysubs2>=1.7.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "opentimelineio>=0.17.0",
]
```

Remove the `otio` optional dependency from `[project.optional-dependencies]` since it's now core.

- [ ] **Step 2: Sync lock file**

Run: `cd bee-content/video-editor && uv sync`
Expected: Lock file updated, dependencies installed.

- [ ] **Step 3: Verify imports work**

Run: `cd bee-content/video-editor && uv run python -c "import pydantic; import opentimelineio; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add bee-content/video-editor/pyproject.toml bee-content/video-editor/uv.lock
git commit -m "move pydantic and opentimelineio to core dependencies"
```

---

## Task 1b: Enum Updates

**Files:**
- Modify: `src/bee_video_editor/models_storyboard.py:9-27`

- [ ] **Step 1: Add GENERATED to VisualType and rename REAL_AUDIO value**

In `models_storyboard.py`:

```python
class VisualType(Enum):
    """Type of visual content in a storyboard layer."""
    FOOTAGE = "FOOTAGE"
    STOCK = "STOCK"
    PHOTO = "PHOTO"
    MAP = "MAP"
    GRAPHIC = "GRAPHIC"
    WAVEFORM = "WAVEFORM"
    BLACK = "BLACK"
    GENERATED = "GENERATED"
    UNKNOWN = "UNKNOWN"


class AudioType(Enum):
    """Type of audio content in a storyboard layer."""
    NAR = "NAR"
    REAL_AUDIO = "REAL_AUDIO"
    MUSIC = "MUSIC"
    SFX = "SFX"
    UNKNOWN = "UNKNOWN"
```

- [ ] **Step 2: Find and update all references to the old "REAL AUDIO" string value**

Run: `cd bee-content/video-editor && grep -rn '"REAL AUDIO"' src/ tests/`

Update any hardcoded `"REAL AUDIO"` strings to `"REAL_AUDIO"` in the codebase. Key files to check:
- `src/bee_video_editor/exporters/otio_export.py` (line 98)
- `src/bee_video_editor/parsers/storyboard.py` (if any)
- `src/bee_video_editor/services/production.py` (if any)

- [ ] **Step 3: Run existing tests to verify no regressions**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All PASS (update any tests that hardcode `"REAL AUDIO"`)

- [ ] **Step 4: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/models_storyboard.py
git add -u bee-content/video-editor/  # any files with REAL AUDIO → REAL_AUDIO
git commit -m "add GENERATED visual type, rename REAL_AUDIO enum value"
```

---

## Task 2: Pydantic Models

**Files:**
- Create: `src/bee_video_editor/formats/__init__.py`
- Create: `src/bee_video_editor/formats/models.py`
- Create: `tests/test_format_models.py`

- [ ] **Step 1: Create formats package**

Create `src/bee_video_editor/formats/__init__.py` — empty for now.

- [ ] **Step 2: Write failing tests for model validation**

```python
# tests/test_format_models.py
"""Tests for the new format Pydantic models."""

import pytest
from pydantic import ValidationError


def test_project_config_minimal():
    """Minimal project config — just a title."""
    from bee_video_editor.formats.models import ProjectConfig
    p = ProjectConfig(title="Test")
    assert p.title == "Test"
    assert p.version == 1
    assert p.voice_lock is None
    assert p.color_preset is None


def test_project_config_full():
    """Full project config with all fields."""
    from bee_video_editor.formats.models import ProjectConfig
    p = ProjectConfig(**{
        "title": "The Murdaugh Murders",
        "version": 1,
        "voice_lock": {"engine": "elevenlabs", "voice": "Daniel", "model": "eleven_multilingual_v2"},
        "color_preset": "dark_crime",
        "default_transition": {"type": "dissolve", "duration": 1.0},
        "output": {"resolution": "1920x1080", "fps": 30, "codec": "h264", "crf": 18},
    })
    assert p.voice_lock.engine == "elevenlabs"
    assert p.default_transition.duration == 1.0
    assert p.output.fps == 30


def test_project_config_voice_lock_requires_engine_and_voice():
    """voice_lock requires engine and voice, model is optional."""
    from bee_video_editor.formats.models import VoiceLock
    vl = VoiceLock(engine="edge", voice="en-US-GuyNeural")
    assert vl.model is None
    with pytest.raises(ValidationError):
        VoiceLock(engine="edge")  # missing voice


def test_visual_entry_footage():
    """FOOTAGE visual with trim points and effects."""
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{
        "type": "FOOTAGE",
        "src": "footage/clip.mp4",
        "in": "00:02:14.500",
        "out": "00:02:29.500",
        "color": "surveillance",
        "ken_burns": "zoom_in",
    })
    assert v.type == "FOOTAGE"
    assert v.tc_in == "00:02:14.500"
    assert v.src == "footage/clip.mp4"


def test_visual_entry_stock_with_query():
    """STOCK visual with null src and a search query."""
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(type="STOCK", src=None, query="aerial farm dusk")
    assert v.src is None
    assert v.query == "aerial farm dusk"


def test_visual_entry_map():
    """MAP visual with coordinates."""
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{
        "type": "MAP",
        "style": "tactical",
        "center": [32.5916, -80.6754],
        "zoom": 13,
        "markers": [{"label": "Moselle", "lat": 32.5916, "lng": -80.6754}],
    })
    assert v.type == "MAP"
    assert v.center == [32.5916, -80.6754]


def test_audio_entry_types():
    """All audio types instantiate correctly."""
    from bee_video_editor.formats.models import AudioEntry
    real = AudioEntry(type="REAL_AUDIO", src="footage/clip.mp4", volume=0.6)
    music = AudioEntry(type="MUSIC", src="music/bg.mp3", volume=0.2, fade_in=2.0)
    sfx = AudioEntry(type="SFX", src="sfx/bang.wav", volume=0.8)
    nar = AudioEntry(type="NAR", engine="elevenlabs", voice="Daniel")
    assert real.volume == 0.6
    assert music.fade_in == 2.0
    assert sfx.type == "SFX"
    assert nar.engine == "elevenlabs"


def test_overlay_entry_types():
    """All overlay types instantiate correctly."""
    from bee_video_editor.formats.models import OverlayEntry
    lt = OverlayEntry(type="LOWER_THIRD", text="Name", subtext="Role", duration=4.0, position="bottom-left")
    tm = OverlayEntry(type="TIMELINE_MARKER", date="June 7, 2021", description="10:07 PM")
    qc = OverlayEntry(type="QUOTE_CARD", quote="Some quote", author="Author")
    assert lt.position == "bottom-left"
    assert tm.date == "June 7, 2021"
    assert qc.author == "Author"


def test_segment_config_full():
    """Full segment config with all layers."""
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig(**{
        "visual": [{"type": "FOOTAGE", "src": "clip.mp4"}],
        "audio": [{"type": "REAL_AUDIO", "src": "clip.mp4", "volume": 0.6}],
        "overlay": [{"type": "LOWER_THIRD", "text": "Name"}],
        "captions": {"style": "karaoke", "font_size": 42},
        "transition_in": {"type": "dissolve", "duration": 1.0},
    })
    assert len(sc.visual) == 1
    assert sc.captions.style == "karaoke"
    assert sc.transition_in.type == "dissolve"


def test_segment_config_empty():
    """Empty segment config (narration-only segment)."""
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig()
    assert sc.visual == []
    assert sc.audio == []
    assert sc.captions is None


def test_segment_config_preserves_unknown_keys():
    """Unknown keys are preserved for forward-compatibility."""
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig(**{
        "visual": [],
        "future_feature": {"key": "value"},
    })
    extras = sc.model_dump(exclude_none=True)
    assert "future_feature" in extras


def test_visual_entry_serializes_in_as_in():
    """The 'in' field serializes correctly (not 'tc_in')."""
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{"type": "FOOTAGE", "src": "clip.mp4", "in": "00:01:00.000", "out": "00:02:00.000"})
    d = v.model_dump(by_alias=True, exclude_none=True)
    assert "in" in d
    assert "tc_in" not in d
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bee_video_editor.formats'`

- [ ] **Step 4: Implement models**

```python
# src/bee_video_editor/formats/models.py
"""Pydantic models for the bee-video storyboard format v2.

These models define the JSON schema for ```json bee-video:project```
and ```json bee-video:segment``` blocks in the markdown storyboard.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceLock(BaseModel):
    """TTS voice configuration locked for the project."""
    engine: str
    voice: str
    model: str | None = None


class OutputConfig(BaseModel):
    """Video output settings."""
    resolution: str = "1920x1080"
    fps: int = 30
    codec: str = "h264"
    crf: int = 18


class TransitionConfig(BaseModel):
    """Transition between segments."""
    type: str
    duration: float


class ProjectConfig(BaseModel):
    """Project-level configuration from the bee-video:project block."""
    title: str
    version: int = 1
    voice_lock: VoiceLock | None = None
    color_preset: str | None = None
    default_transition: TransitionConfig | None = None
    output: OutputConfig | None = None


class VisualEntry(BaseModel):
    """A visual element in a segment."""
    type: str  # FOOTAGE, STOCK, PHOTO, MAP, GRAPHIC, GENERATED, WAVEFORM, BLACK
    src: str | None = None
    tc_in: str | None = Field(None, alias="in")
    out: str | None = None
    color: str | None = None
    ken_burns: str | None = None
    query: str | None = None
    duration: float | None = None
    style: str | None = None
    center: list[float] | None = None
    zoom: int | None = None
    markers: list[dict] | None = None
    template: str | None = None
    text: str | None = None
    subtext: str | None = None
    prompt: str | None = None
    provider: str | None = None

    model_config = {"populate_by_name": True}


class AudioEntry(BaseModel):
    """An audio element in a segment."""
    type: str  # REAL_AUDIO, MUSIC, SFX, NAR
    src: str | None = None
    volume: float | None = None
    tc_in: str | None = Field(None, alias="in")
    out: str | None = None
    fade_in: float | None = None
    fade_out: float | None = None
    engine: str | None = None
    voice: str | None = None

    model_config = {"populate_by_name": True}


class OverlayEntry(BaseModel):
    """An overlay/graphic element in a segment."""
    type: str  # LOWER_THIRD, TIMELINE_MARKER, QUOTE_CARD, FINANCIAL_CARD, TEXT_OVERLAY
    text: str | None = None
    subtext: str | None = None
    duration: float | None = None
    position: str | None = None
    date: str | None = None
    description: str | None = None
    quote: str | None = None
    author: str | None = None
    amount: str | None = None


class CaptionsConfig(BaseModel):
    """Segment-level caption configuration."""
    style: str = "phrase"
    font_size: int = 42


class SegmentConfig(BaseModel):
    """Production configuration from a bee-video:segment block."""
    visual: list[VisualEntry] = Field(default_factory=list)
    audio: list[AudioEntry] = Field(default_factory=list)
    overlay: list[OverlayEntry] = Field(default_factory=list)
    captions: CaptionsConfig | None = None
    transition_in: TransitionConfig | None = None

    model_config = {"extra": "allow"}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_models.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/ bee-content/video-editor/tests/test_format_models.py
git commit -m "add Pydantic models for storyboard format v2"
```

---

## Task 3: Timecode Utilities

**Files:**
- Create: `src/bee_video_editor/formats/timecodes.py`
- Create: `tests/test_timecodes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_timecodes.py
"""Tests for timecode parsing and formatting."""

from bee_video_editor.formats.timecodes import (
    parse_header_tc,
    format_header_tc,
    parse_precise_tc,
    format_precise_tc,
    tc_to_seconds,
)


def test_parse_header_tc_minutes_seconds():
    assert parse_header_tc("2:30") == 150.0


def test_parse_header_tc_hours():
    assert parse_header_tc("1:05:30") == 3930.0


def test_parse_header_tc_zero():
    assert parse_header_tc("0:00") == 0.0


def test_format_header_tc_minutes_seconds():
    assert format_header_tc(150.0) == "2:30"


def test_format_header_tc_hours():
    assert format_header_tc(3930.0) == "1:05:30"


def test_format_header_tc_zero():
    assert format_header_tc(0.0) == "0:00"


def test_parse_precise_tc():
    assert parse_precise_tc("00:02:14.500") == 134.5


def test_parse_precise_tc_hours():
    assert parse_precise_tc("01:05:30.000") == 3930.0


def test_format_precise_tc():
    assert format_precise_tc(134.5) == "00:02:14.500"


def test_format_precise_tc_zero():
    assert format_precise_tc(0.0) == "00:00:00.000"


def test_tc_to_seconds_header_format():
    assert tc_to_seconds("2:30") == 150.0


def test_tc_to_seconds_precise_format():
    assert tc_to_seconds("00:02:14.500") == 134.5


def test_roundtrip_header():
    """header parse → format → parse is identity."""
    for tc in ["0:00", "2:30", "15:00", "1:05:30"]:
        assert format_header_tc(parse_header_tc(tc)) == tc


def test_roundtrip_precise():
    """precise parse → format → parse is identity."""
    for tc in ["00:00:00.000", "00:02:14.500", "01:05:30.000"]:
        assert format_precise_tc(parse_precise_tc(tc)) == tc
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_timecodes.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Implement timecodes module**

```python
# src/bee_video_editor/formats/timecodes.py
"""Timecode parsing and formatting utilities.

Two formats:
- Header shorthand: "M:SS" or "H:MM:SS" (used in markdown segment headers)
- Precise: "HH:MM:SS.mmm" (used in JSON block in/out values)
"""

from __future__ import annotations


def parse_header_tc(tc: str) -> float:
    """Parse header timecode (M:SS or H:MM:SS) to seconds."""
    parts = tc.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    raise ValueError(f"Invalid header timecode: {tc!r}")


def format_header_tc(seconds: float) -> str:
    """Format seconds to header timecode (M:SS or H:MM:SS)."""
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_precise_tc(tc: str) -> float:
    """Parse precise timecode (HH:MM:SS.mmm) to seconds."""
    parts = tc.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid precise timecode: {tc!r}")
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return h * 3600 + m * 60 + s


def format_precise_tc(seconds: float) -> str:
    """Format seconds to precise timecode (HH:MM:SS.mmm)."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def tc_to_seconds(tc: str) -> float:
    """Auto-detect format and parse to seconds."""
    if "." in tc:
        return parse_precise_tc(tc)
    return parse_header_tc(tc)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_timecodes.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/timecodes.py bee-content/video-editor/tests/test_timecodes.py
git commit -m "add timecode parsing and formatting utilities"
```

---

## Task 4: Slug Generation

**Files:**
- Create: `src/bee_video_editor/formats/slugify.py`
- Create: `tests/test_slugify.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_slugify.py
"""Tests for segment ID slug generation."""

from bee_video_editor.formats.slugify import slugify, unique_slug


def test_slugify_simple():
    assert slugify("Cold Open") == "cold-open"


def test_slugify_special_chars():
    assert slugify("The 911 Call — Emergency") == "the-911-call-emergency"


def test_slugify_collapses_hyphens():
    assert slugify("Act 1: The Night Of") == "act-1-the-night-of"


def test_slugify_strips_edges():
    assert slugify("  --Hello World--  ") == "hello-world"


def test_unique_slug_no_collision():
    seen = set()
    assert unique_slug("Cold Open", seen) == "cold-open"
    assert "cold-open" in seen


def test_unique_slug_with_collision():
    seen = {"establishing-shot"}
    s = unique_slug("Establishing Shot", seen)
    assert s == "establishing-shot-2"
    assert "establishing-shot-2" in seen


def test_unique_slug_multiple_collisions():
    seen = {"shot", "shot-2", "shot-3"}
    s = unique_slug("Shot", seen)
    assert s == "shot-4"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_slugify.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Implement slugify module**

```python
# src/bee_video_editor/formats/slugify.py
"""Segment ID slug generation.

Slugification: lowercase, replace non-alphanumeric with hyphens,
collapse runs, strip leading/trailing hyphens.
"""

from __future__ import annotations

import re


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def unique_slug(text: str, seen: set[str]) -> str:
    """Generate a unique slug, appending -2, -3, etc. on collision."""
    base = slugify(text)
    slug = base
    n = 2
    while slug in seen:
        slug = f"{base}-{n}"
        n += 1
    seen.add(slug)
    return slug
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_slugify.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/slugify.py bee-content/video-editor/tests/test_slugify.py
git commit -m "add segment ID slug generation"
```

---

## Task 5: Test Fixtures

**Files:**
- Create: `tests/fixtures/storyboard_v2_minimal.md`
- Create: `tests/fixtures/storyboard_v2_full.md`

- [ ] **Step 1: Create minimal fixture**

A valid storyboard with 1 section, 2 segments, narration. Uses only basic features.

```markdown
```json bee-video:project
{
  "title": "Test Project",
  "version": 1
}
```

## Section One (0:00 - 0:30)

### 0:00 - 0:15 | First Segment

```json bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": "footage/clip-a.mp4"}],
  "audio": [{"type": "REAL_AUDIO", "src": "footage/clip-a.mp4", "volume": 0.8}]
}
```

> NAR: This is the first narration line.
> It continues on the next line.

### 0:15 - 0:30 | Second Segment

```json bee-video:segment
{
  "visual": [{"type": "STOCK", "src": "stock/aerial.mp4", "in": "00:00:05.000", "out": "00:00:20.000"}],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: Second segment narration.
```

- [ ] **Step 2: Create full-featured fixture**

A storyboard exercising every feature: all visual/audio/overlay types, multi-visual, captions, maps, generated clips, stock queries, voice_lock, output config, multiple sections.

Write this file at `tests/fixtures/storyboard_v2_full.md` with at least:
- Project block with all fields (voice_lock, color_preset, default_transition, output)
- 2 sections with time ranges
- Segment with FOOTAGE + color + ken_burns
- Segment with STOCK + query (null src)
- Segment with MAP visual
- Segment with GENERATED visual
- Segment with multiple visuals (multi-visual)
- Segment with all audio types (REAL_AUDIO, MUSIC, SFX)
- Segment with overlays (LOWER_THIRD, TIMELINE_MARKER, QUOTE_CARD)
- Segment with captions config
- Narration-only segment (no JSON block)
- Multiple narration paragraphs
- Various transition types

- [ ] **Step 3: Commit**

```bash
git add bee-content/video-editor/tests/fixtures/
git commit -m "add test fixtures for storyboard format v2"
```

---

## Task 6: Markdown Parser

**Files:**
- Create: `src/bee_video_editor/formats/parser.py`
- Create: `tests/test_format_parser.py`

The parser reads the new markdown format and returns a `ParsedStoryboard` — a simple container dataclass holding `ProjectConfig`, a list of sections, and a list of segments with their narration text.

- [ ] **Step 1: Define ParsedStoryboard container in parser.py**

```python
# Top of parser.py — the intermediate representation
@dataclass
class ParsedSection:
    """A section (act) from the storyboard."""
    title: str
    start: str  # header shorthand: "0:00"
    end: str    # header shorthand: "2:30"

@dataclass
class ParsedSegment:
    """A segment with its config and narration."""
    title: str
    start: str
    end: str
    section: str  # parent section title
    config: SegmentConfig
    narration: str  # extracted from > NAR: blockquotes, stripped of prefix

@dataclass
class ParsedStoryboard:
    """Complete parsed storyboard."""
    project: ProjectConfig
    sections: list[ParsedSection]
    segments: list[ParsedSegment]
```

- [ ] **Step 2: Write failing tests for the parser**

```python
# tests/test_format_parser.py
"""Tests for the new markdown storyboard parser."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_minimal():
    """Parse the minimal fixture successfully."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.project.title == "Test Project"
    assert parsed.project.version == 1
    assert len(parsed.sections) == 1
    assert parsed.sections[0].title == "Section One"
    assert len(parsed.segments) == 2


def test_parse_segment_timecodes():
    """Segments have correct start/end times."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.segments[0].start == "0:00"
    assert parsed.segments[0].end == "0:15"
    assert parsed.segments[1].start == "0:15"
    assert parsed.segments[1].end == "0:30"


def test_parse_segment_config():
    """Segment JSON blocks are parsed into SegmentConfig."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    seg0 = parsed.segments[0]
    assert len(seg0.config.visual) == 1
    assert seg0.config.visual[0].type == "FOOTAGE"
    assert seg0.config.visual[0].src == "footage/clip-a.mp4"


def test_parse_narration():
    """Narration blockquotes are extracted and stripped of prefix."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert "first narration line" in parsed.segments[0].narration
    assert "continues on the next line" in parsed.segments[0].narration
    assert parsed.segments[0].narration.startswith("This is")  # NAR: prefix stripped


def test_parse_narration_belongs_to_segment():
    """Each narration block belongs to its preceding segment."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert "Second segment" in parsed.segments[1].narration
    assert "Second segment" not in parsed.segments[0].narration


def test_parse_transition():
    """Transition config is parsed."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.segments[1].config.transition_in is not None
    assert parsed.segments[1].config.transition_in.type == "dissolve"


def test_parse_section_association():
    """Segments know their parent section."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    for seg in parsed.segments:
        assert seg.section == "Section One"


def test_parse_no_project_block_uses_defaults():
    """Missing project block uses defaults with warning."""
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2_text("## Sec (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n")
    assert parsed.project.title == "Untitled"
    assert parsed.project.version == 1


def test_parse_duplicate_project_block_errors():
    """Multiple project blocks raise an error."""
    from bee_video_editor.formats.parser import parse_v2, StoryboardParseError
    text = (
        '```json bee-video:project\n{"title": "A"}\n```\n'
        '```json bee-video:project\n{"title": "B"}\n```\n'
    )
    with pytest.raises(StoryboardParseError, match="multiple.*project"):
        parse_v2_text(text)


def test_parse_invalid_json_errors():
    """Invalid JSON in a block raises error with line number."""
    from bee_video_editor.formats.parser import parse_v2, StoryboardParseError
    text = '```json bee-video:project\n{invalid json}\n```\n'
    with pytest.raises(StoryboardParseError, match="line"):
        parse_v2_text(text)


def test_parse_narration_before_segment_errors():
    """> NAR: before any segment is an error."""
    from bee_video_editor.formats.parser import parse_v2, StoryboardParseError
    text = '> NAR: Orphan narration\n\n## Sec (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n'
    with pytest.raises(StoryboardParseError, match="NAR.*before"):
        parse_v2_text(text)


def test_parse_non_nar_blockquote_ignored():
    """Blockquotes without NAR: prefix are ignored."""
    from bee_video_editor.formats.parser import parse_v2
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n\n'
        '> NAR: Real narration.\n\n'
        '> Just a note, not narration.\n'
    )
    parsed = parse_v2_text(text)
    assert "Real narration" in parsed.segments[0].narration
    assert "Just a note" not in parsed.segments[0].narration


def test_parse_segment_without_json_block():
    """Segment header without JSON block creates empty segment."""
    from bee_video_editor.formats.parser import parse_v2
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### 0:00 - 0:10 | Narration Only\n\n'
        '> NAR: Just narration, no config.\n'
    )
    parsed = parse_v2_text(text)
    assert len(parsed.segments) == 1
    assert parsed.segments[0].config.visual == []
    assert "Just narration" in parsed.segments[0].narration


def test_parse_orphaned_json_block_errors():
    """JSON block without a preceding segment header is an error."""
    from bee_video_editor.formats.parser import parse_v2, StoryboardParseError
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n'
        '```json bee-video:segment\n{"visual": []}\n```\n'  # orphaned
        '### 0:00 - 0:10 | Seg\n'
    )
    with pytest.raises(StoryboardParseError, match="orphan"):
        parse_v2_text(text)


def test_parse_malformed_timecodes_errors():
    """Invalid timecodes in segment header produce an error."""
    from bee_video_editor.formats.parser import parse_v2, StoryboardParseError
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### abc - def | Bad Timecodes\n'
    )
    with pytest.raises(StoryboardParseError, match="timecode"):
        parse_v2_text(text)


# Helper to parse from string instead of file
def parse_v2_text(text: str):
    from bee_video_editor.formats.parser import parse_v2
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        f.flush()
        try:
            return parse_v2(f.name)
        finally:
            os.unlink(f.name)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_parser.py -v`
Expected: FAIL — ImportError

- [ ] **Step 4: Implement the parser**

Build `src/bee_video_editor/formats/parser.py` implementing `parse_v2(path_or_text)`. Key logic:

1. Read file, split into lines.
2. Scan for `` ```json bee-video:project `` blocks — extract JSON, validate with `ProjectConfig`.
3. Scan for `## Section (start - end)` headers.
4. Scan for `### start - end | Title` headers.
5. For each segment, find the next `` ```json bee-video:segment `` block (if any) before the next segment header.
6. Collect `> NAR:` blockquotes after the segment, strip prefix, concatenate.
7. Return `ParsedStoryboard`.

Define `StoryboardParseError` exception class for structured errors.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_parser.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/parser.py bee-content/video-editor/tests/test_format_parser.py
git commit -m "add markdown parser for storyboard format v2"
```

---

## Task 7: Canonical Markdown Writer

**Files:**
- Create: `src/bee_video_editor/formats/writer.py`
- Create: `tests/test_format_writer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_format_writer.py
"""Tests for the canonical markdown writer."""

from bee_video_editor.formats.models import (
    ProjectConfig, SegmentConfig, VisualEntry, AudioEntry,
    OverlayEntry, TransitionConfig, CaptionsConfig,
)
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSection, ParsedSegment


def test_write_minimal():
    """Minimal storyboard writes correctly."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="Test"),
        sections=[ParsedSection(title="Sec", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            title="Seg",
            start="0:00", end="0:10",
            section="Sec",
            config=SegmentConfig(visual=[VisualEntry(type="FOOTAGE", src="clip.mp4")]),
            narration="Hello world.",
        )],
    )
    md = write_v2(parsed)
    assert '```json bee-video:project' in md
    assert '"title": "Test"' in md
    assert '## Sec (0:00 - 0:10)' in md
    assert '### 0:00 - 0:10 | Seg' in md
    assert '```json bee-video:segment' in md
    assert '"type": "FOOTAGE"' in md
    assert '> NAR: Hello world.' in md


def test_write_json_key_order():
    """JSON keys appear in schema-defined order, not alphabetical."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(
                visual=[VisualEntry(type="FOOTAGE", src="a.mp4")],
                audio=[AudioEntry(type="REAL_AUDIO", src="a.mp4", volume=0.5)],
                transition_in=TransitionConfig(type="dissolve", duration=1.0),
            ),
            narration="",
        )],
    )
    md = write_v2(parsed)
    # visual should appear before audio, audio before transition_in
    vis_pos = md.index('"visual"')
    aud_pos = md.index('"audio"')
    trans_pos = md.index('"transition_in"')
    assert vis_pos < aud_pos < trans_pos


def test_write_omits_none_fields():
    """None fields are excluded from JSON output."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(visual=[VisualEntry(type="BLACK")]),
            narration="",
        )],
    )
    md = write_v2(parsed)
    assert '"src"' not in md  # src is None for BLACK, should be omitted


def test_write_multiline_narration():
    """Multi-line narration wraps with > NAR: prefix."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(),
            narration="First paragraph.\n\nSecond paragraph.",
        )],
    )
    md = write_v2(parsed)
    assert "> NAR: First paragraph." in md
    assert "> NAR: Second paragraph." in md


def test_write_no_narration():
    """Segments without narration don't emit > NAR: lines."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(),
            narration="",
        )],
    )
    md = write_v2(parsed)
    assert "> NAR:" not in md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_writer.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Implement the writer**

Build `src/bee_video_editor/formats/writer.py` implementing `write_v2(parsed) → str`. Key rules:

1. Emit `` ```json bee-video:project `` block with 2-space indented JSON, keys in model field order.
2. For each section: emit `## Title (start - end)` with blank line.
3. For each segment: emit `### start - end | Title`, then `` ```json bee-video:segment `` block, then `> NAR:` lines.
4. Use `model_dump(by_alias=True, exclude_none=True)` for JSON serialization.
5. One blank line between segments, one blank line between sections.
6. Narration paragraphs separated by blank `> NAR:` lines become `\n\n` in the narration string.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_writer.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/writer.py bee-content/video-editor/tests/test_format_writer.py
git commit -m "add canonical markdown writer for storyboard format v2"
```

---

## Task 8: Markdown Round-Trip Tests

**Files:**
- Create: `tests/test_format_roundtrip.py`

- [ ] **Step 1: Write round-trip tests**

```python
# tests/test_format_roundtrip.py
"""Round-trip tests: parse → write → parse produces identical structure."""

from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_roundtrip_minimal():
    """minimal fixture: parse → write → parse gives same data."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    md = write_v2(parsed1)
    parsed2 = _parse_from_string(md)
    _assert_parsed_equal(parsed1, parsed2)


def test_roundtrip_full():
    """full fixture: parse → write → parse gives same data."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_full.md")
    md = write_v2(parsed1)
    parsed2 = _parse_from_string(md)
    _assert_parsed_equal(parsed1, parsed2)


def test_canonical_idempotent():
    """write → parse → write produces identical markdown."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    md1 = write_v2(parsed)
    parsed2 = _parse_from_string(md1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def _parse_from_string(text: str):
    from bee_video_editor.formats.parser import parse_v2
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        f.flush()
        try:
            return parse_v2(f.name)
        finally:
            os.unlink(f.name)


def _assert_parsed_equal(a, b):
    """Deep comparison of two ParsedStoryboard instances."""
    assert a.project.model_dump() == b.project.model_dump()
    assert len(a.sections) == len(b.sections)
    for sa, sb in zip(a.sections, b.sections):
        assert sa.title == sb.title
        assert sa.start == sb.start
        assert sa.end == sb.end
    assert len(a.segments) == len(b.segments)
    for sa, sb in zip(a.segments, b.segments):
        assert sa.title == sb.title
        assert sa.start == sb.start
        assert sa.end == sb.end
        assert sa.section == sb.section
        assert sa.narration == sb.narration
        assert sa.config.model_dump() == sb.config.model_dump()
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_roundtrip.py -v`
Expected: All PASS (parser + writer are already implemented)

- [ ] **Step 3: Commit**

```bash
git add bee-content/video-editor/tests/test_format_roundtrip.py
git commit -m "add markdown round-trip tests for format v2"
```

---

## Task 9: Markdown → OTIO Converter

**Files:**
- Create: `src/bee_video_editor/formats/otio_convert.py`
- Create: `tests/test_otio_convert.py`

- [ ] **Step 1: Write failing tests for to_otio**

```python
# tests/test_otio_convert.py
"""Tests for OTIO conversion (markdown ↔ OTIO)."""

from pathlib import Path
import opentimelineio as otio

FIXTURES = Path(__file__).parent / "fixtures"


def test_to_otio_timeline_name():
    """Timeline name matches project title."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    assert tl.name == "Test Project"


def test_to_otio_project_metadata():
    """Project config stored in timeline metadata."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    meta = tl.metadata.get("bee_video", {}).get("project", {})
    assert meta["title"] == "Test Project"
    assert meta["version"] == 1


def test_to_otio_tracks():
    """Creates V1, A1, A2, A3, OV1 tracks."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    track_names = [t.name for t in tl.tracks]
    assert "V1" in track_names
    assert "A1" in track_names


def test_to_otio_v1_clips():
    """V1 has one clip per visual entry."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clips = [c for c in v1 if isinstance(c, otio.schema.Clip)]
    assert len(clips) == 2


def test_to_otio_media_ref():
    """Clips with src get ExternalReference, without get MissingReference."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clip0 = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert isinstance(clip0.media_reference, otio.schema.ExternalReference)
    assert "clip-a.mp4" in clip0.media_reference.target_url


def test_to_otio_segment_id():
    """Each clip has bee_video.segment_id metadata."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clip0 = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert clip0.metadata["bee_video"]["segment_id"] == "first-segment"


def test_to_otio_narration_track():
    """A1 (narration) track has clips for segments with narration."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    a1 = [t for t in tl.tracks if t.name == "A1"][0]
    nar_clips = [c for c in a1 if isinstance(c, otio.schema.Clip)]
    assert len(nar_clips) >= 1
    meta = nar_clips[0].metadata["bee_video"]["narration"]
    assert "first narration line" in meta["text"]


def test_to_otio_transition():
    """Transitions appear on V1 before clips that have transition_in."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    transitions = [c for c in v1 if isinstance(c, otio.schema.Transition)]
    assert len(transitions) >= 1


def test_to_otio_section_markers():
    """Section headers become markers on the first V1 clip in each section."""
    parsed = _load_minimal()
    from bee_video_editor.formats.otio_convert import to_otio
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    first_clip = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    marker_names = [m.name for m in first_clip.markers]
    assert "Section One" in marker_names


def _load_minimal():
    from bee_video_editor.formats.parser import parse_v2
    return parse_v2(FIXTURES / "storyboard_v2_minimal.md")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_convert.py -v`
Expected: FAIL — ImportError for `otio_convert`

- [ ] **Step 3: Implement to_otio**

Build `to_otio(parsed: ParsedStoryboard, fps: float = 30.0) -> otio.schema.Timeline` in `formats/otio_convert.py`. Key logic:

1. Create Timeline with name from project title.
2. Store project config in `timeline.metadata["bee_video"]["project"]`.
3. Create tracks: V1 (Video), A1 (Audio/narration), A2 (Audio/real+sfx), A3 (Audio/music), OV1 (Video/overlays).
4. For each segment:
   - Generate `segment_id` via `unique_slug(title, seen)`.
   - For each visual entry: create Clip on V1 with ExternalReference (if src) or MissingReference. Set `source_range` from in/out or segment duration. Store visual metadata.
   - For narration: create Clip on A1 with MissingReference, estimate duration at 150 wpm. Store text in metadata.
   - For audio entries: create Clips on A2 (REAL_AUDIO/SFX) or A3 (MUSIC).
   - For overlays: create Clips on OV1 with MissingReference.
   - For transition_in: insert OTIO Transition before V1 clip.
   - Add section marker to first clip in each new section.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_convert.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/otio_convert.py bee-content/video-editor/tests/test_otio_convert.py
git commit -m "add markdown-to-OTIO converter"
```

---

## Task 10: OTIO → Markdown Converter

**Files:**
- Modify: `src/bee_video_editor/formats/otio_convert.py`
- Add tests to: `tests/test_otio_convert.py`

- [ ] **Step 1: Write failing tests for from_otio**

Add to `tests/test_otio_convert.py`:

```python
def test_from_otio_roundtrip():
    """parsed → to_otio → from_otio produces equivalent ParsedStoryboard."""
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert parsed2.project.title == parsed1.project.title
    assert len(parsed2.segments) == len(parsed1.segments)
    for s1, s2 in zip(parsed1.segments, parsed2.segments):
        assert s1.title == s2.title
        assert s1.narration == s2.narration


def test_from_otio_preserves_visual_config():
    """Visual metadata survives OTIO round-trip."""
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert parsed2.segments[0].config.visual[0].type == "FOOTAGE"
    assert parsed2.segments[0].config.visual[0].src == "footage/clip-a.mp4"


def test_from_otio_preserves_audio():
    """Audio entries survive OTIO round-trip."""
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    real_audio = [a for a in parsed2.segments[0].config.audio if a.type == "REAL_AUDIO"]
    assert len(real_audio) == 1
    assert real_audio[0].volume == 0.8


def test_from_otio_preserves_sections():
    """Section markers are reconstructed."""
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert len(parsed2.sections) == 1
    assert parsed2.sections[0].title == "Section One"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_convert.py::test_from_otio_roundtrip -v`
Expected: FAIL — `from_otio` not found

- [ ] **Step 3: Implement from_otio**

Add `from_otio(timeline: otio.schema.Timeline) -> ParsedStoryboard` to `formats/otio_convert.py`. Key logic:

1. Read project config from `timeline.metadata["bee_video"]["project"]`.
2. Walk V1 clips in order. For each clip:
   - Read `segment_id` from metadata.
   - Reconstruct visual entry from clip metadata + media reference.
   - Correlate clips on A1/A2/A3/OV1 by matching `segment_id`.
   - Reconstruct narration from A1 clip metadata.
   - Group consecutive V1 clips with same `segment_id` (multi-visual).
3. Reconstruct sections from markers.
4. Return `ParsedStoryboard`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_convert.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/otio_convert.py bee-content/video-editor/tests/test_otio_convert.py
git commit -m "add OTIO-to-markdown converter (from_otio)"
```

---

## Task 11: Clean OTIO Export

**Files:**
- Modify: `src/bee_video_editor/formats/otio_convert.py`
- Create: `tests/test_otio_clean.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_otio_clean.py
"""Tests for clean OTIO export (strip bee_video metadata)."""

import opentimelineio as otio
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_clean_otio_strips_metadata():
    """Clean OTIO has no bee_video keys anywhere."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio, clean_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    assert "bee_video" not in clean.metadata
    for track in clean.tracks:
        for item in track:
            if hasattr(item, "metadata"):
                assert "bee_video" not in item.metadata


def test_clean_otio_preserves_clips():
    """Clean OTIO keeps all clips and transitions."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio, clean_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    orig_clips = sum(1 for t in tl.tracks for c in t if isinstance(c, otio.schema.Clip))
    clean_clips = sum(1 for t in clean.tracks for c in t if isinstance(c, otio.schema.Clip))
    assert clean_clips == orig_clips


def test_clean_otio_preserves_media_refs():
    """Clean OTIO keeps media references."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio, clean_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    v1 = [t for t in clean.tracks if t.name == "V1"][0]
    clip = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert isinstance(clip.media_reference, otio.schema.ExternalReference)


def test_clean_otio_does_not_mutate_original():
    """clean_otio returns a copy, original unchanged."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio, clean_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    _ = clean_otio(tl)
    assert "bee_video" in tl.metadata  # original untouched
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_clean.py -v`
Expected: FAIL — `clean_otio` not found

- [ ] **Step 3: Implement clean_otio**

Add `clean_otio(timeline) -> Timeline` to `formats/otio_convert.py`:

1. Deep copy the timeline via `timeline.deepcopy()`.
2. Remove `"bee_video"` from timeline metadata.
3. Walk all tracks → all items → remove `"bee_video"` from each item's metadata.
4. Return the cleaned copy.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_otio_clean.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/otio_convert.py bee-content/video-editor/tests/test_otio_clean.py
git commit -m "add clean OTIO export (strip bee_video metadata)"
```

---

## Task 12: Full OTIO Round-Trip Tests

**Files:**
- Modify: `tests/test_format_roundtrip.py`

- [ ] **Step 1: Add OTIO round-trip tests**

Add to `tests/test_format_roundtrip.py`:

```python
def test_otio_roundtrip_minimal():
    """md → otio → md → otio: identical markdown output."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    md1 = write_v2(parsed1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def test_otio_roundtrip_full():
    """Full fixture survives md → otio → md."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_full.md")
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    md1 = write_v2(parsed1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def test_otio_file_roundtrip(tmp_path):
    """Write OTIO to disk, read back, convert to md — same result."""
    import opentimelineio as otio
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    from bee_video_editor.formats.otio_convert import to_otio, from_otio
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed1)
    otio_path = tmp_path / "test.otio"
    otio.adapters.write_to_file(tl, str(otio_path))
    tl2 = otio.adapters.read_from_file(str(otio_path))
    parsed2 = from_otio(tl2)
    _assert_parsed_equal(parsed1, parsed2)
```

- [ ] **Step 2: Run all round-trip tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_roundtrip.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add bee-content/video-editor/tests/test_format_roundtrip.py
git commit -m "add full OTIO round-trip tests"
```

---

## Task 13: Migration Converter (Old → New)

**Files:**
- Create: `src/bee_video_editor/formats/migrate.py`
- Create: `tests/test_format_migrate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_format_migrate.py
"""Tests for migrating old Storyboard format to new ParsedStoryboard."""

from bee_video_editor.models_storyboard import (
    Storyboard, StoryboardSegment, LayerEntry,
)


def test_migrate_basic():
    """Old storyboard converts to ParsedStoryboard."""
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(
        title="Test",
        segments=[
            StoryboardSegment(
                id="0_00-0_15", start="0:00", end="0:15",
                title="Seg", section="Sec", section_time="0:00 - 0:15",
                subsection="",
                visual=[LayerEntry(content="clip.mp4", content_type="FOOTAGE")],
                audio=[LayerEntry(content="Narration text here", content_type="NAR")],
            ),
        ],
    )
    parsed = old_to_new(old)
    assert parsed.project.title == "Test"
    assert len(parsed.segments) == 1
    assert parsed.segments[0].config.visual[0].type == "FOOTAGE"


def test_migrate_music_to_audio():
    """Music layer entries move into audio array with type MUSIC."""
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(
        title="Test",
        segments=[
            StoryboardSegment(
                id="0_00-0_15", start="0:00", end="0:15",
                title="Seg", section="Sec", section_time="0:00 - 0:15",
                subsection="",
                music=[LayerEntry(content="bg-track.mp3", content_type="MUSIC")],
            ),
        ],
    )
    parsed = old_to_new(old)
    music = [a for a in parsed.segments[0].config.audio if a.type == "MUSIC"]
    assert len(music) == 1


def test_migrate_source_to_visual_src():
    """Source layer entries merge into visual src field."""
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(
        title="Test",
        segments=[
            StoryboardSegment(
                id="0_00-0_15", start="0:00", end="0:15",
                title="Seg", section="Sec", section_time="0:00 - 0:15",
                subsection="",
                visual=[LayerEntry(content="description", content_type="FOOTAGE")],
                source=[LayerEntry(content="footage/file.mp4 00:01:30-00:02:00", content_type="FOOTAGE")],
            ),
        ],
    )
    parsed = old_to_new(old)
    assert parsed.segments[0].config.visual[0].src is not None


def test_migrate_narration_extracted():
    """NAR audio entries become narration text on the segment."""
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(
        title="Test",
        segments=[
            StoryboardSegment(
                id="0_00-0_15", start="0:00", end="0:15",
                title="Seg", section="Sec", section_time="0:00 - 0:15",
                subsection="",
                audio=[LayerEntry(content="The narrator says this.", content_type="NAR")],
            ),
        ],
    )
    parsed = old_to_new(old)
    assert "narrator says this" in parsed.segments[0].narration


def test_migrate_transition_to_structured():
    """Freeform transition text → structured TransitionConfig."""
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(
        title="Test",
        segments=[
            StoryboardSegment(
                id="0_00-0_15", start="0:00", end="0:15",
                title="Seg", section="Sec", section_time="0:00 - 0:15",
                subsection="",
                transition=[LayerEntry(content="Dissolve to next", content_type="DISSOLVE")],
            ),
        ],
    )
    parsed = old_to_new(old)
    assert parsed.segments[0].config.transition_in is not None
    assert parsed.segments[0].config.transition_in.type == "dissolve"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_migrate.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: Implement migration converter**

Build `src/bee_video_editor/formats/migrate.py` with `old_to_new(storyboard: Storyboard) -> ParsedStoryboard`. Key mappings per spec's Layer Model Migration table:

- `visual` → `visual[]` (map `content_type` to `type`, `content` to description or src)
- `audio` with type NAR → extract as `narration` text on the segment
- `audio` with other types → `audio[]`
- `music` → `audio[]` with type MUSIC
- `source` → merge into `visual[].src` (parse path and trim info from content)
- `overlay` → `overlay[]`
- `transition` → `transition_in` (parse type from content_type, default duration 1.0)
- Sections derived from unique `section` values across segments

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_migrate.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/migrate.py bee-content/video-editor/tests/test_format_migrate.py
git commit -m "add migration converter: old storyboard to format v2"
```

---

## Task 14: CLI Commands (import-md/export)

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`
- Create: `tests/test_cli_import_export.py`

**Note:** The existing `cli.py` already has an `export` command (line 665) that exports old-format storyboards to OTIO. This must be renamed to `export-legacy` before adding the new `export` command.

- [ ] **Step 1: Rename existing export command**

In `src/bee_video_editor/adapters/cli.py`, change line 665 from `@app.command()` to `@app.command(name="export-legacy")` and rename the function to `export_legacy`.

- [ ] **Step 2: Write failing tests**

```python
# tests/test_cli_import_export.py
"""Tests for bee-video import-md and export CLI commands."""

from pathlib import Path
from typer.testing import CliRunner

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_import_md_creates_otio(tmp_path):
    """bee-video import-md storyboard.md creates .otio file."""
    from bee_video_editor.adapters.cli import app
    md_path = FIXTURES / "storyboard_v2_minimal.md"
    otio_path = tmp_path / "storyboard.otio"
    result = runner.invoke(app, ["import-md", str(md_path), "--output", str(otio_path)])
    assert result.exit_code == 0
    assert otio_path.exists()


def test_export_creates_md(tmp_path):
    """bee-video export project.otio --format md creates .md file."""
    from bee_video_editor.adapters.cli import app
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))
    md_path = tmp_path / "exported.md"
    result = runner.invoke(app, ["export", str(otio_path), "--format", "md", "--output", str(md_path)])
    assert result.exit_code == 0
    assert md_path.exists()
    content = md_path.read_text()
    assert "Test Project" in content


def test_export_clean_otio(tmp_path):
    """bee-video export project.otio --format otio creates clean OTIO."""
    from bee_video_editor.adapters.cli import app
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))
    clean_path = tmp_path / "clean.otio"
    result = runner.invoke(app, ["export", str(otio_path), "--format", "otio", "--output", str(clean_path)])
    assert result.exit_code == 0
    clean_tl = otio_lib.adapters.read_from_file(str(clean_path))
    assert "bee_video" not in clean_tl.metadata


def test_import_md_default_output(tmp_path):
    """Without --output, import-md creates .otio next to the .md file."""
    from bee_video_editor.adapters.cli import app
    import shutil
    md_src = FIXTURES / "storyboard_v2_minimal.md"
    md_copy = tmp_path / "storyboard.md"
    shutil.copy(md_src, md_copy)
    result = runner.invoke(app, ["import-md", str(md_copy)])
    assert result.exit_code == 0
    assert (tmp_path / "storyboard.otio").exists()


def test_import_md_lenient(tmp_path):
    """--lenient flag downgrades parse errors to warnings."""
    from bee_video_editor.adapters.cli import app
    # Create a storyboard with an intentional error (orphaned JSON block)
    bad_md = tmp_path / "bad.md"
    bad_md.write_text(
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '```json bee-video:segment\n{"visual": []}\n```\n'  # orphaned — no segment header
        '## S (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n'
    )
    otio_path = tmp_path / "bad.otio"
    result = runner.invoke(app, ["import-md", str(bad_md), "--output", str(otio_path), "--lenient"])
    assert result.exit_code == 0  # lenient mode skips bad segments
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_cli_import_export.py -v`
Expected: FAIL — commands don't exist

- [ ] **Step 4: Add import-md and new export commands to cli.py**

Add to `src/bee_video_editor/adapters/cli.py`:

```python
@app.command(name="import-md")
def import_md(
    storyboard: str = typer.Argument(..., help="Path to storyboard .md file (format v2)"),
    output: str | None = typer.Option(None, help="Output .otio path (default: same name as input)"),
    lenient: bool = typer.Option(False, "--lenient", help="Downgrade parse errors to warnings, skip bad segments"),
):
    """Import a v2 markdown storyboard into an OTIO project file."""
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio

    parsed = parse_v2(storyboard, lenient=lenient)
    tl = to_otio(parsed)

    if output is None:
        output = str(Path(storyboard).with_suffix(".otio"))

    otio_lib.adapters.write_to_file(tl, output)
    console.print(f"[green]Imported to {output}[/green]")
    console.print(f"  {len(parsed.segments)} segments, {len(parsed.sections)} sections")
```

Replace the existing `export` command (now renamed to `export-legacy`) with the new one:

```python
@app.command()
def export(
    project: str = typer.Argument(..., help="Path to .otio project file"),
    format: str = typer.Option("md", help="Export format: md or otio"),
    output: str | None = typer.Option(None, help="Output path"),
):
    """Export an OTIO project to markdown or clean OTIO."""
    import opentimelineio as otio_lib
    from bee_video_editor.formats.otio_convert import from_otio, clean_otio
    from bee_video_editor.formats.writer import write_v2

    tl = otio_lib.adapters.read_from_file(project)

    if format == "md":
        parsed = from_otio(tl)
        md = write_v2(parsed)
        if output is None:
            output = str(Path(project).with_suffix(".md"))
        Path(output).write_text(md, encoding="utf-8")
        console.print(f"[green]Exported markdown to {output}[/green]")
    elif format == "otio":
        clean = clean_otio(tl)
        if output is None:
            output = str(Path(project).stem + "_clean.otio")
        otio_lib.adapters.write_to_file(clean, output)
        console.print(f"[green]Exported clean OTIO to {output}[/green]")
    else:
        console.print(f"[red]Unknown format: {format}. Use 'md' or 'otio'.[/red]")
        raise typer.Exit(1)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_cli_import_export.py -v`
Expected: All PASS

- [ ] **Step 6: Verify CLI works end-to-end**

Run: `cd bee-content/video-editor && uv run bee-video import-md tests/fixtures/storyboard_v2_minimal.md --output /tmp/test.otio && uv run bee-video export /tmp/test.otio --format md --output /tmp/test_exported.md`

Expected: Both commands succeed. The exported markdown should be the canonical form.

- [ ] **Step 7: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/adapters/cli.py bee-content/video-editor/tests/test_cli_import_export.py
git commit -m "add import-md and export CLI commands, rename old export to export-legacy"
```

---

## Task 15: Package Init + Final Integration

**Files:**
- Modify: `src/bee_video_editor/formats/__init__.py`

- [ ] **Step 1: Re-export key functions from __init__.py**

```python
# src/bee_video_editor/formats/__init__.py
"""Storyboard format v2 — markdown with JSON blocks + OTIO conversion."""

from bee_video_editor.formats.parser import parse_v2, ParsedStoryboard, ParsedSegment, ParsedSection
from bee_video_editor.formats.writer import write_v2
from bee_video_editor.formats.otio_convert import to_otio, from_otio, clean_otio
from bee_video_editor.formats.migrate import old_to_new

__all__ = [
    "parse_v2", "write_v2",
    "to_otio", "from_otio", "clean_otio",
    "old_to_new",
    "ParsedStoryboard", "ParsedSegment", "ParsedSection",
]
```

- [ ] **Step 2: Run all tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_format_*.py tests/test_timecodes.py tests/test_slugify.py tests/test_otio_*.py tests/test_cli_import_export.py -v`
Expected: All PASS

- [ ] **Step 3: Run existing test suite to verify no regressions**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v`
Expected: All existing tests still pass. New tests also pass.

- [ ] **Step 4: Commit**

```bash
git add bee-content/video-editor/src/bee_video_editor/formats/__init__.py
git commit -m "finalize formats package with public API re-exports"
```

---

## Summary

| Task | What | Tests |
|------|------|-------|
| 1 | Dependencies (pydantic, OTIO → core) | import check |
| 2 | Pydantic models | 13 model validation tests |
| 3 | Timecode utilities | 14 parse/format/roundtrip tests |
| 4 | Slug generation | 7 slugify tests |
| 5 | Test fixtures | 2 markdown fixture files |
| 6 | Markdown parser | 12+ parser tests |
| 7 | Canonical markdown writer | 5+ writer tests |
| 8 | Markdown round-trip | 3 round-trip tests |
| 9 | Markdown → OTIO converter | 8+ OTIO conversion tests |
| 10 | OTIO → Markdown converter | 4+ reverse conversion tests |
| 11 | Clean OTIO export | 4 clean export tests |
| 12 | Full OTIO round-trip | 3 end-to-end round-trip tests |
| 13 | Migration (old → new) | 5 migration tests |
| 14 | CLI commands (import/export) | 4 CLI integration tests |
| 15 | Package init + final check | Full regression run |
