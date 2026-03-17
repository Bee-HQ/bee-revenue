# Design: Model Unification + Parser Resilience

**Date:** 2026-03-17
**Scope:** Make Storyboard the canonical model, add assembly guide converter, harden parsers
**Approach:** A — converter bridge (both parsers kept, everything funnels to Storyboard internally)

---

## 1. assembly_guide_to_storyboard() Converter

### Problem

The "Two Parser Problem": CLI uses `Project` (assembly guide, flat strings), Web UI uses `Storyboard` (rich typed layers). Production functions in `services/production.py` work with `Project`, API routes work with `Storyboard`. Captions and preflight only work with `Storyboard`. This forces duplicated logic (e.g., graphics generation exists in both `production.py` and `routes/production.py`).

### Solution

New file `src/bee_video_editor/converters.py` with one function:

```python
def assembly_guide_to_storyboard(project: Project) -> Storyboard:
    """Convert an assembly guide Project to a Storyboard.

    Best-effort parsing of flat string fields into typed LayerEntry objects.
    """
```

#### Field mapping (every StoryboardSegment field)

| StoryboardSegment field | Source from Project.Segment | Notes |
|---|---|---|
| `id` | `f"{start_str}_{end_str}"` with `:` → `_` | e.g., `"0_00-0_15"` |
| `start` | `str(seg.start)` formatted as `"M:SS"` | Must be `"M:SS"` format for `duration_seconds` property |
| `end` | `str(seg.end)` formatted as `"M:SS"` | Same format |
| `title` | `seg.subsection or seg.section or seg.start-seg.end` | Synthesized — storyboard has titles from markdown headers |
| `section` | `seg.section` | Direct copy |
| `section_time` | `""` | Not available in assembly guide — left empty |
| `subsection` | `seg.subsection` | Direct copy |
| `visual` | Parsed from `seg.visual` string | See visual rules below |
| `audio` | Parsed from `seg.audio` string | See audio rules below |
| `overlay` | Extracted from visual if "lower third" detected | Moved from visual to overlay layer |
| `music` | Extracted from `seg.audio` trailing `+ music...` notes | See music extraction below |
| `source` | Parsed from `seg.source_notes` | Each line → LayerEntry |
| `transition` | Empty list | Assembly guides have no transition info |
| `assigned_media` | Empty dict | Not applicable in conversion |

#### Conversion rules

For each `Segment` in the project:

**Visual field** → `list[LayerEntry]` (visual layer):
- Check for bible codes: `[CODE: qualifier] rest` → `LayerEntry(content=qualifier + rest, content_type=CODE)`
- Check for backtick prefix: `` `TYPE:` content `` → `LayerEntry(content=content, content_type=TYPE)`
- Also consult `seg.segment_type`: if `REAL` → set `content_type="BODYCAM"` as default when no other type detected
- Fallback: `LayerEntry(content=raw_text, content_type="UNKNOWN")`

**Audio field** → `list[LayerEntry]` (audio + music layers):
- Split on `NAR:` prefix → `LayerEntry(content=text_with_quotes, content_type="NAR")` in audio layer
- Split on `REAL AUDIO:` or `REAL:` prefix → `LayerEntry(content=text, content_type="REAL AUDIO")` in audio layer
- Also consult `seg.segment_type`: if `NAR` or `MIX` → default `content_type="NAR"` when no prefix found
- Trailing `+ music...` notes → `LayerEntry(content=music_description, content_type="MUSIC")` in music layer
- **Important:** Quotes are NOT stripped during conversion. Quote stripping is the consumer's job (`_clean_text` in captions, regex in production functions). The converter preserves the raw text.

**Source notes** → `list[LayerEntry]` (source layer):
- Each non-empty line becomes a `LayerEntry(content=line, content_type="SOURCE")`

**Segment ID** generation:
- Format: `"{start_formatted}-{end_formatted}"` where times use `_` instead of `:` (e.g., `"0_00-0_15"`)

**Section/subsection** preserved directly from the assembly guide segment.

**Overlay extraction:**
- If visual content contains "lower third" (case-insensitive) → move that LayerEntry to overlay layer with `content_type="LOWER-THIRD"`
- Otherwise visual content stays in visual layer

### _ensure_storyboard() helper

In `services/production.py`, add:

```python
from bee_video_editor.converters import assembly_guide_to_storyboard

def _ensure_storyboard(source: Project | Storyboard) -> Storyboard:
    """Convert Project to Storyboard if needed."""
    if isinstance(source, Storyboard):
        return source
    return assembly_guide_to_storyboard(source)
```

Top-level import (no circular dependency risk — `converters.py` doesn't import `production.py`). Parameter named `source` to avoid shadowing `input` builtin.

Production functions gain a `Union` type hint but callers don't change — existing `Project` callers still work, `Storyboard` callers work too.

---

## 2. Production Service Updates

The four production functions keep their current signatures but internally convert:

```python
def generate_graphics_for_project(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    sb = _ensure_storyboard(project)
    # ... rest uses sb.segments with LayerEntry access
```

The internal logic shifts from string-matching (`"lower third" in seg.visual.lower()`) to type-checking (`entry.content_type == "LOWER-THIRD"`). This makes the production functions work identically for both input formats.

**What changes in each function:**

`generate_graphics_for_project`:
- Currently: `if "lower third" in seg.visual.lower()` + regex on `seg.visual`
- After: iterate `seg.overlay` for `entry.content_type == "LOWER-THIRD"` (same as API route already does)
- This eliminates the duplicate graphics logic between production.py and routes/production.py

`generate_narration_for_project`:
- Currently: `_extract_narrator_text(seg.audio)` (string regex)
- After: iterate `seg.audio` for `entry.content_type == "NAR"`, use `_clean_text(entry.content)`
- Reuses the same `_clean_text` from `processors/captions.py`

`trim_source_footage`:
- Currently: uses `project.trim_notes` (Project-specific)
- After: if input is `Project`, still uses `project.trim_notes` as before. If input is `Storyboard`, returns an empty `ProductionResult` immediately (storyboard format has no trim notes — trimming from storyboard source layer is out of scope for this spec)

`normalize_all_segments` and `assemble_final`:
- No model dependency — they work on files on disk. No change needed.

---

## 3. Parser Resilience

### Whitespace normalization

Both parsers get a `_normalize_cell(text)` helper, but with different behavior:

**Assembly guide parser** (`assembly_guide.py`):
```python
def _normalize_cell(text: str) -> str:
    """Strip whitespace and stray backticks from table cell content."""
    return text.strip().strip('`').strip()
```
Backtick stripping is safe here — assembly guide doesn't use backticks semantically.

**Storyboard parser** (`storyboard.py`):
```python
def _normalize_cell(text: str) -> str:
    """Strip whitespace from table cell content. Preserves backticks (used for content type markers)."""
    return text.strip()
```
No backtick stripping — the storyboard parser uses `` `TYPE:` `` backtick prefixes for content type detection. Stripping them would break type parsing.

### Graceful handling of missing sections

**Assembly guide parser:**
- Missing `## Pre-Production` → return empty `pre_production` list (currently may crash)
- Missing `## Trim Notes` → return empty `trim_notes` (currently may crash)
- Missing table header row → skip section, don't crash
- Malformed timecodes → skip segment, log warning, continue

**Storyboard parser:**
- Missing `## STOCK FOOTAGE NEEDED` → return empty `stock_footage` (already works)
- Malformed segment header (`#### time | TITLE`) → skip segment, continue
- Table rows with wrong column count → skip row, continue
- Empty layer content → skip entry, don't add empty LayerEntry

### What does NOT change

- The parser is not made "smart" — no fuzzy section matching, no auto-correction
- The storyboard format itself doesn't change
- The assembly guide format doesn't change

---

## Files Changed

| File | Change |
|------|--------|
| `converters.py` | **New.** `assembly_guide_to_storyboard()`, segment conversion logic, visual/audio/source string parsing. |
| `services/production.py` | Add `_ensure_storyboard()`. Update `generate_graphics_for_project` and `generate_narration_for_project` to work with Storyboard model internally. |
| `parsers/assembly_guide.py` | Add `_normalize_cell()`. Wrap section parsing in try/except with empty defaults. |
| `parsers/storyboard.py` | Add `_normalize_cell()`. Handle malformed headers/rows gracefully. |
| `tests/test_converters.py` | **New.** Tests for assembly_guide_to_storyboard conversion. |
| `tests/test_parser.py` | Add resilience tests (malformed markdown, missing sections). |
| `tests/test_storyboard_parser.py` | Add resilience tests. |

## Files NOT Changed

- `models.py`, `models_storyboard.py` — no model changes
- `processors/*` — no processor changes
- `api/*` — no API changes (routes already use Storyboard)
- `adapters/cli.py` — CLI still passes Project, _ensure_storyboard handles it
- `web/*` — no frontend changes

## Testing Strategy

### Converter
- Unit test: convert a Project with NAR/REAL/GEN segments → verify Storyboard has correct LayerEntry types
- Unit test: visual bible codes parsed correctly from flat strings
- Unit test: audio NAR: prefix extraction, quotes preserved (not stripped)
- Unit test: music notes extracted from `+ music...` suffix into music layer
- Unit test: segment_type enum consulted for default content_type
- Unit test: empty project → empty storyboard (no crash)
- Unit test: source notes split into source layer entries
- Unit test: converted Storyboard has correct `title`, `start`/`end` format (`"M:SS"`), `duration_seconds` works
- Unit test: `section_time` is empty string, `transition` is empty list

### Parser resilience
- Unit test: assembly guide with extra whitespace in table cells → parses correctly
- Unit test: assembly guide missing Pre-Production section → returns empty list
- Unit test: assembly guide with malformed timecode → skips segment, others parse
- Unit test: storyboard with malformed segment header → skips segment, others parse
- Unit test: storyboard table row with wrong column count → skips row
- Unit test: storyboard `_normalize_cell` preserves backticks (no stripping)
- Unit test: assembly guide `_normalize_cell` strips backticks

### Production service
- Unit test: `_ensure_storyboard` with Project input → returns Storyboard
- Unit test: `_ensure_storyboard` with Storyboard input → returns same object
- Unit test: `trim_source_footage` with Storyboard input → returns empty ProductionResult (no crash)
- Unit test: `generate_graphics_for_project(project, config)` with mocked Pillow → produces results
- Unit test: `generate_graphics_for_project(storyboard, config)` also works
- Existing production tests still pass (backward compatible)
