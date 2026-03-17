# Model Unification + Parser Resilience Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Storyboard the canonical model by adding an assembly guide converter, update production functions to work with Storyboard internally, and harden both parsers against malformed input.

**Architecture:** New `converters.py` with `assembly_guide_to_storyboard()`. Production functions gain `_ensure_storyboard()` that transparently converts Project → Storyboard. Both parsers get whitespace normalization and graceful error handling.

**Tech Stack:** Python 3.11+, dataclasses, pytest

**Spec:** `docs/superpowers/specs/2026-03-17-model-unification-design.md`

---

## Chunk 1: Converter

### Task 1: Create assembly_guide_to_storyboard converter + tests

**Files:**
- Create: `src/bee_video_editor/converters.py`
- Create: `tests/test_converters.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_converters.py`:

```python
"""Tests for assembly guide → storyboard converter."""

import pytest

from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models import Project, Segment, SegmentType, Timecode


def _seg(start_m, start_s, end_m, end_s, seg_type, visual="", audio="", source="", section="TEST", subsection=""):
    return Segment(
        start=Timecode(start_m, start_s),
        end=Timecode(end_m, end_s),
        duration_seconds=(end_m * 60 + end_s) - (start_m * 60 + start_s),
        segment_type=seg_type,
        visual=visual,
        audio=audio,
        source_notes=source,
        section=section,
        subsection=subsection,
    )


def _project(segments):
    return Project(
        title="Test Project",
        total_duration="~10 minutes",
        resolution="1080p",
        format="MP4",
        segments=segments,
    )


class TestConvertBasics:
    def test_empty_project(self):
        sb = assembly_guide_to_storyboard(_project([]))
        assert sb.title == "Test Project"
        assert len(sb.segments) == 0

    def test_segment_id_format(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 15, SegmentType.NAR),
        ]))
        assert sb.segments[0].id == "0_00-0_15"

    def test_start_end_format(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(1, 30, 2, 0, SegmentType.NAR),
        ]))
        assert sb.segments[0].start == "1:30"
        assert sb.segments[0].end == "2:00"

    def test_duration_seconds_works(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 15, SegmentType.NAR),
        ]))
        assert sb.segments[0].duration_seconds == 15

    def test_title_from_subsection(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, subsection="The Hook"),
        ]))
        assert sb.segments[0].title == "The Hook"

    def test_title_fallback_to_section(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, section="COLD OPEN"),
        ]))
        assert sb.segments[0].title == "COLD OPEN"

    def test_title_fallback_to_timecode(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, section="", subsection=""),
        ]))
        assert sb.segments[0].title == "0:00-0:10"

    def test_section_time_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].section_time == ""

    def test_transition_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].transition == []

    def test_assigned_media_empty(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR),
        ]))
        assert sb.segments[0].assigned_media == {}


class TestVisualConversion:
    def test_bible_code_parsed(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="[MAP-FLAT] Lowcountry region"),
        ]))
        assert sb.segments[0].visual[0].content_type == "MAP-FLAT"
        assert "Lowcountry region" in sb.segments[0].visual[0].content

    def test_bible_code_with_qualifier(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="[BROLL-DARK: atmospheric] slow aerial"),
        ]))
        assert sb.segments[0].visual[0].content_type == "BROLL-DARK"
        assert "atmospheric" in sb.segments[0].visual[0].content

    def test_backtick_prefix(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="`STOCK:` Rural estate at dusk"),
        ]))
        assert sb.segments[0].visual[0].content_type == "STOCK"

    def test_real_segment_type_default(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL, visual="Bodycam footage at scene"),
        ]))
        assert sb.segments[0].visual[0].content_type == "BODYCAM"

    def test_unknown_fallback(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN, visual="Some generic description"),
        ]))
        assert sb.segments[0].visual[0].content_type == "UNKNOWN"

    def test_lower_third_moves_to_overlay(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.GEN,
                 visual='[LOWER-THIRD: "Alex Murdaugh — 4th Generation"]'),
        ]))
        assert len(sb.segments[0].visual) == 0
        assert len(sb.segments[0].overlay) == 1
        assert sb.segments[0].overlay[0].content_type == "LOWER-THIRD"


class TestAudioConversion:
    def test_nar_prefix_extracted(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='NAR: "This is the narrator"'),
        ]))
        assert sb.segments[0].audio[0].content_type == "NAR"
        # Quotes preserved — consumer's job to strip
        assert '"This is the narrator"' in sb.segments[0].audio[0].content

    def test_real_audio_prefix(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL, audio='REAL AUDIO: Deputy says hello'),
        ]))
        assert sb.segments[0].audio[0].content_type == "REAL AUDIO"

    def test_segment_type_default_nar(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='"Just some text without prefix"'),
        ]))
        assert sb.segments[0].audio[0].content_type == "NAR"

    def test_music_extracted_to_music_layer(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR,
                 audio='NAR: "Text here" + dark ambient music fades in'),
        ]))
        assert len(sb.segments[0].audio) == 1
        assert len(sb.segments[0].music) == 1
        assert sb.segments[0].music[0].content_type == "MUSIC"
        assert "dark ambient music fades in" in sb.segments[0].music[0].content

    def test_quotes_not_stripped(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, audio='NAR: "Hello world"'),
        ]))
        # The converter must NOT strip quotes
        assert '"' in sb.segments[0].audio[0].content


class TestSourceConversion:
    def test_source_notes_split(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.REAL,
                 source="footage/911-calls/clip.mkv\nfootage/bodycam/arrival.mp4"),
        ]))
        assert len(sb.segments[0].source) == 2
        assert sb.segments[0].source[0].content_type == "SOURCE"

    def test_empty_source(self):
        sb = assembly_guide_to_storyboard(_project([
            _seg(0, 0, 0, 10, SegmentType.NAR, source=""),
        ]))
        assert len(sb.segments[0].source) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_converters.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement the converter**

Create `src/bee_video_editor/converters.py`:

```python
"""Convert between assembly guide (Project) and storyboard (Storyboard) models."""

from __future__ import annotations

import re

from bee_video_editor.models import Project, Segment, SegmentType
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def assembly_guide_to_storyboard(project: Project) -> Storyboard:
    """Convert an assembly guide Project to a Storyboard.

    Best-effort parsing of flat string fields into typed LayerEntry objects.
    Quotes in text are preserved — stripping is the consumer's job.
    """
    segments = []
    for seg in project.segments:
        start_str = str(seg.start)
        end_str = str(seg.end)
        seg_id = f"{start_str.replace(':', '_')}-{end_str.replace(':', '_')}"

        visual, overlay = _parse_visual(seg.visual, seg.segment_type)
        audio, music = _parse_audio(seg.audio, seg.segment_type)
        source = _parse_source(seg.source_notes)

        title = seg.subsection or seg.section or f"{start_str}-{end_str}"

        segments.append(StoryboardSegment(
            id=seg_id,
            start=start_str,
            end=end_str,
            title=title,
            section=seg.section,
            section_time="",
            subsection=seg.subsection,
            visual=visual,
            audio=audio,
            overlay=overlay,
            music=music,
            source=source,
            transition=[],
        ))

    return Storyboard(
        title=project.title,
        segments=segments,
        production_rules=ProductionRules(),
    )


def _parse_visual(visual_str: str, seg_type: SegmentType) -> tuple[list[LayerEntry], list[LayerEntry]]:
    """Parse visual string into visual + overlay layer entries."""
    visual_entries = []
    overlay_entries = []

    if not visual_str.strip():
        return visual_entries, overlay_entries

    # Check for bible code: [CODE: qualifier] rest  or  [CODE] rest
    bible_match = re.match(r'\[([A-Z][A-Z0-9_-]+)(?::\s*([^\]]*))?\]\s*(.*)', visual_str)
    if bible_match:
        code = bible_match.group(1)
        qualifier = bible_match.group(2)
        rest = bible_match.group(3).strip()
        content = f"{qualifier.strip()} {rest}".strip() if qualifier else rest

        entry = LayerEntry(content=content, content_type=code, raw=visual_str)

        # Lower thirds go to overlay layer
        if code == "LOWER-THIRD" or "lower third" in visual_str.lower():
            entry.content_type = "LOWER-THIRD"
            overlay_entries.append(entry)
        else:
            visual_entries.append(entry)
        return visual_entries, overlay_entries

    # Check for backtick prefix: `TYPE:` content
    bt_match = re.match(r'`([A-Z][A-Z\s]*?):`\s*(.*)', visual_str)
    if bt_match:
        content_type = bt_match.group(1).strip()
        content = bt_match.group(2).strip()
        visual_entries.append(LayerEntry(content=content, content_type=content_type, raw=visual_str))
        return visual_entries, overlay_entries

    # Check for lower third in raw text
    if "lower third" in visual_str.lower():
        overlay_entries.append(LayerEntry(content=visual_str, content_type="LOWER-THIRD", raw=visual_str))
        return visual_entries, overlay_entries

    # Default based on segment type
    default_type = "UNKNOWN"
    if seg_type == SegmentType.REAL:
        default_type = "BODYCAM"

    visual_entries.append(LayerEntry(content=visual_str, content_type=default_type, raw=visual_str))
    return visual_entries, overlay_entries


def _parse_audio(audio_str: str, seg_type: SegmentType) -> tuple[list[LayerEntry], list[LayerEntry]]:
    """Parse audio string into audio + music layer entries."""
    audio_entries = []
    music_entries = []

    if not audio_str.strip():
        return audio_entries, music_entries

    # Extract music notes from trailing "+ music..."
    music_match = re.search(r'\s*\+\s*(.+)$', audio_str)
    main_audio = audio_str
    if music_match:
        music_text = music_match.group(1).strip()
        music_entries.append(LayerEntry(content=music_text, content_type="MUSIC", raw=music_text))
        main_audio = audio_str[:music_match.start()]

    main_audio = main_audio.strip()
    if not main_audio:
        return audio_entries, music_entries

    # Check for NAR: prefix
    nar_match = re.match(r'NAR:\s*(.*)', main_audio, re.IGNORECASE)
    if nar_match:
        content = nar_match.group(1).strip()
        audio_entries.append(LayerEntry(content=content, content_type="NAR", raw=main_audio))
        return audio_entries, music_entries

    # Check for REAL AUDIO: or REAL: prefix
    real_match = re.match(r'REAL(?:\s+AUDIO)?:\s*(.*)', main_audio, re.IGNORECASE)
    if real_match:
        content = real_match.group(1).strip()
        audio_entries.append(LayerEntry(content=content, content_type="REAL AUDIO", raw=main_audio))
        return audio_entries, music_entries

    # Default based on segment type
    if seg_type in (SegmentType.NAR, SegmentType.MIX):
        audio_entries.append(LayerEntry(content=main_audio, content_type="NAR", raw=main_audio))
    else:
        audio_entries.append(LayerEntry(content=main_audio, content_type="UNKNOWN", raw=main_audio))

    return audio_entries, music_entries


def _parse_source(source_str: str) -> list[LayerEntry]:
    """Parse source notes into source layer entries."""
    if not source_str.strip():
        return []
    return [
        LayerEntry(content=line.strip(), content_type="SOURCE", raw=line.strip())
        for line in source_str.split("\n")
        if line.strip()
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_converters.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add src/bee_video_editor/converters.py tests/test_converters.py
git commit -m "feat(video-editor): add assembly_guide_to_storyboard converter"
```

---

## Chunk 2: Production service updates

### Task 2: Add _ensure_storyboard + refactor production functions

**Files:**
- Modify: `src/bee_video_editor/services/production.py`
- Modify: `tests/test_production.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_production.py`:

```python
from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)
from bee_video_editor.services.production import _ensure_storyboard


class TestEnsureStoryboard:
    def test_storyboard_passes_through(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        assert _ensure_storyboard(sb) is sb

    def test_project_converts(self):
        from bee_video_editor.models import Project
        proj = Project(title="Test", total_duration="10m", resolution="1080p", format="MP4")
        result = _ensure_storyboard(proj)
        assert isinstance(result, Storyboard)
        assert result.title == "Test"


class TestTrimWithStoryboard:
    def test_trim_storyboard_returns_empty(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            (config.output_dir / "segments").mkdir(parents=True)
            result = trim_source_footage(sb, config)
            assert isinstance(result, ProductionResult)
            assert result.ok
            assert len(result.succeeded) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_production.py::TestEnsureStoryboard -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement _ensure_storyboard and refactor functions**

In `services/production.py`:

1. Add imports at top:
```python
from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models_storyboard import Storyboard
```

2. Add `_ensure_storyboard`:
```python
def _ensure_storyboard(source: Project | Storyboard) -> Storyboard:
    """Convert Project to Storyboard if needed."""
    if isinstance(source, Storyboard):
        return source
    return assembly_guide_to_storyboard(source)
```

3. Refactor `generate_graphics_for_project` — add `sb = _ensure_storyboard(project)` at top, change internal logic to iterate `sb.segments` overlay layer:

Replace the entire function body with:
```python
def generate_graphics_for_project(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Generate all graphics assets."""
    result = ProductionResult()
    graphics_dir = config.output_dir / "graphics"
    sb = _ensure_storyboard(project)

    if state:
        state.phase = "graphics"
        state.save(config.state_path)

    lower_third_idx = 0
    for seg in sb.segments:
        for entry in seg.overlay:
            if entry.content_type == "LOWER-THIRD":
                match = re.search(r'"([^"]+)"', entry.content)
                if match:
                    parts = match.group(1).split(" — ")
                    name = parts[0].strip()
                    role = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = f"Character {lower_third_idx}"
                    role = ""

                out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{_slugify(name)}.png"
                if out.exists():
                    result.skipped.append(str(out))
                else:
                    try:
                        gfx.lower_third(name, role, out)
                        result.succeeded.append(out)
                    except Exception as e:
                        result.failed.append(FailedItem(path=str(out), error=str(e)))
                lower_third_idx += 1

    # Timeline markers
    timeline_idx = 0
    for seg in sb.segments:
        for entry in seg.visual:
            if entry.content_type == "TIMELINE-MARKER":
                text = entry.content.strip().strip('"')
                if text:
                    out = graphics_dir / f"timeline-{timeline_idx:02d}-{_slugify(text)[:30]}.png"
                    if out.exists():
                        result.skipped.append(str(out))
                    else:
                        try:
                            gfx.timeline_marker(text, "", out)
                            result.succeeded.append(out)
                        except Exception as e:
                            result.failed.append(FailedItem(path=str(out), error=str(e)))
                    timeline_idx += 1

    # Financial cards
    fin_idx = 0
    for seg in sb.segments:
        for entry in seg.visual:
            if entry.content_type == "FINANCIAL-CARD":
                amount = entry.content.strip().strip('"')
                if amount:
                    out = graphics_dir / f"financial-{fin_idx:02d}-{_slugify(amount)[:20]}.png"
                    if out.exists():
                        result.skipped.append(str(out))
                    else:
                        try:
                            gfx.financial_card(amount, "", out)
                            result.succeeded.append(out)
                        except Exception as e:
                            result.failed.append(FailedItem(path=str(out), error=str(e)))
                    fin_idx += 1

    return result
```

4. Refactor `generate_narration_for_project` — use `_ensure_storyboard`, iterate audio entries:

```python
def generate_narration_for_project(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Generate TTS narration for all NAR segments."""
    result = ProductionResult()
    narration_dir = config.output_dir / "narration"
    sb = _ensure_storyboard(project)

    if state:
        state.phase = "narration"
        state.save(config.state_path)

    from bee_video_editor.processors.captions import _clean_text

    for i, seg in enumerate(sb.segments):
        for entry in seg.audio:
            if entry.content_type != "NAR":
                continue

            nar_text = _clean_text(entry.content)
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
                            text=nar_text, output_path=out,
                            engine=config.tts_engine, voice=config.tts_voice,
                        )
                        result.succeeded.append(out)
                else:
                    generate_narration(
                        text=nar_text, output_path=out,
                        engine=config.tts_engine, voice=config.tts_voice,
                    )
                    result.succeeded.append(out)
            except Exception as e:
                result.failed.append(FailedItem(path=f"segment-{i}", error=str(e)))

    return result
```

5. Update `trim_source_footage` to handle Storyboard:

```python
def trim_source_footage(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Trim source footage. Only works with Project (assembly guide) — Storyboard returns empty result."""
    result = ProductionResult()

    # Storyboard has no trim notes — return empty
    if isinstance(project, Storyboard):
        return result

    # ... rest of existing Project-based logic unchanged
```

6. Remove `_extract_narrator_text` function (no longer needed — replaced by `_clean_text` from captions.py).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "refactor(video-editor): production functions use Storyboard internally via _ensure_storyboard"
```

---

## Chunk 3: Parser resilience

### Task 3: Harden assembly guide parser

**Files:**
- Modify: `src/bee_video_editor/parsers/assembly_guide.py`
- Modify: `tests/test_parser.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_parser.py`:

```python
class TestParserResilience:
    def test_whitespace_in_cells(self):
        """Table cells with extra whitespace should parse correctly."""
        # Create a markdown string with extra whitespace in table cells
        md = """# Assembly Guide: "Test"

**Total Duration:** ~5 minutes
**Resolution:** 1080p
**Format:** MP4

## Minute-by-Minute Assembly

### COLD OPEN (0:00 - 0:10)

| Time | Dur | Type | Visual | Audio | Source File / Notes |
|------|-----|------|--------|-------|-------------------|
|  0:00-0:10  |  10s  |  NAR  |  Test visual  |  NAR: "Test audio"  |  source.mp4  |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
            project = parse_assembly_guide(f.name)
            assert len(project.segments) == 1
            assert "Test visual" in project.segments[0].visual

    def test_missing_pre_production(self):
        """Assembly guide with no Pre-Production section should not crash."""
        md = """# Assembly Guide: "Test"

**Total Duration:** ~5 minutes
**Resolution:** 1080p
**Format:** MP4

## Minute-by-Minute Assembly

### SECTION (0:00 - 0:10)

| Time | Dur | Type | Visual | Audio | Source File / Notes |
|------|-----|------|--------|-------|-------------------|
| 0:00-0:10 | 10s | NAR | Visual | Audio | Notes |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
            project = parse_assembly_guide(f.name)
            assert project.pre_production == []
```

- [ ] **Step 2: Run tests — verify current behavior**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_parser.py::TestParserResilience -v`

- [ ] **Step 3: Add _normalize_cell to assembly guide parser**

In `parsers/assembly_guide.py`, add helper:

```python
def _normalize_cell(text: str) -> str:
    """Strip whitespace and stray backticks from table cell content."""
    return text.strip().strip('`').strip()
```

Apply it wherever table cells are split:
- In `_parse_segments`, after splitting row on `|`, apply `_normalize_cell` to each cell

Wrap section parsing functions in try/except returning empty defaults.

- [ ] **Step 4: Run tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_parser.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/parsers/assembly_guide.py tests/test_parser.py
git commit -m "fix(video-editor): assembly guide parser resilience — whitespace normalization, missing section handling"
```

### Task 4: Harden storyboard parser

**Files:**
- Modify: `src/bee_video_editor/parsers/storyboard.py`
- Modify: `tests/test_storyboard_parser.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_storyboard_parser.py`:

```python
class TestStoryboardParserResilience:
    def test_malformed_segment_header_skipped(self):
        md = """# Test Storyboard

## SECTION (0:00 - 0:30)

#### this is not a valid header
| Layer | Content |
|-------|---------|
| Visual | `FOOTAGE:` test |

#### 0:10 - 0:20 | VALID
| Layer | Content |
|-------|---------|
| Visual | `FOOTAGE:` real content |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.storyboard import parse_storyboard
            sb = parse_storyboard(f.name)
            # Should parse at least the valid segment
            valid = [s for s in sb.segments if s.title == "VALID"]
            assert len(valid) >= 1

    def test_normalize_cell_preserves_backticks(self):
        from bee_video_editor.parsers.storyboard import _normalize_cell
        assert _normalize_cell("  `FOOTAGE:` test  ") == "`FOOTAGE:` test"

    def test_wrong_column_count_skipped(self):
        md = """# Test Storyboard

## SECTION (0:00 - 0:10)

#### 0:00 - 0:10 | TEST
| Layer | Content |
|-------|---------|
| Visual | content |
| Bad row with no pipe separator
| Audio | audio content |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.storyboard import parse_storyboard
            sb = parse_storyboard(f.name)
            # Should not crash, should parse what it can
            assert len(sb.segments) >= 1
```

- [ ] **Step 2: Run tests**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_storyboard_parser.py::TestStoryboardParserResilience -v`

- [ ] **Step 3: Add _normalize_cell and error handling to storyboard parser**

In `parsers/storyboard.py`:

1. Add at module level:
```python
def _normalize_cell(text: str) -> str:
    """Strip whitespace from table cell content. Preserves backticks."""
    return text.strip()
```

2. In `_parse_layer_entry` or wherever table rows are split, apply `_normalize_cell` to the layer name cell (NOT the content cell — content gets its own parsing).

3. In segment header parsing, wrap the timecode extraction in try/except — skip segments with unparseable headers.

4. When splitting table rows on `|`, skip rows that produce fewer than 2 non-empty cells.

- [ ] **Step 4: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/parsers/storyboard.py tests/test_storyboard_parser.py
git commit -m "fix(video-editor): storyboard parser resilience — whitespace normalization, malformed row handling"
```

### Task 5: Final verification + ROADMAP update

- [ ] **Step 1: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: 165+ tests pass

- [ ] **Step 2: Update ROADMAP**

Mark these items as done in `ROADMAP.md`:
- `[x] Unify data models`
- `[x] Parser resilience`

- [ ] **Step 3: Push**

```bash
git push
```
