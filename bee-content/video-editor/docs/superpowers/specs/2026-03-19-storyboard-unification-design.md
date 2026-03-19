# Storyboard Unification Design

Eliminate the assembly guide format. Make the storyboard the single source of truth for all video production — CLI, web editor, and services.

## Problem

Two parallel document formats describe the same video. The codebase has a dual-path architecture:

- **Assembly guide path** (legacy): `parse_assembly_guide()` → `Project` model → used by 6 CLI commands (`parse`, `segments`, `init`, `graphics`, `narration`, `trim-footage`), the Streamlit dashboard, and `init_project()` in services.
- **Storyboard path** (current): `parse_storyboard()` → `Storyboard` model → used by 6 CLI commands (`produce`, `captions`, `preflight`, `previews`, `export`, `rough-cut`), the web editor, and `run_full_pipeline()`.

A conversion bridge exists: `_ensure_storyboard()` in services + `assembly_guide_to_storyboard()` in converters.py. This lets services accept either format, but `init_project()` and `trim_source_footage()` still only work with the assembly guide model.

The storyboard format is richer (typed layers, asset tables, production rules) but lacks three features the assembly guide has: tech specs header, pre/post-production checklists, and trim notes with file paths.

## Goal

One format. One parser. One model. The storyboard absorbs the assembly guide's missing features, the remaining 6 legacy CLI commands switch to the storyboard parser, services drop the `Project | Storyboard` union type and accept only `Storyboard`, and the conversion bridge is removed.

The workflow becomes: storyboard markdown → web editor (human-in-the-loop corrections) → automated production pipeline (CLI or web).

## Current State (v0.6.0)

### What's already done
- Services (`generate_graphics_for_project`, `generate_narration_for_project`, `rough_cut_export`) accept `Project | Storyboard` and normalize via `_ensure_storyboard()`
- These services already iterate typed layers (`segment.overlay`, `segment.audio`) — no regex on freeform text
- Newer CLI commands use storyboard parser
- Web editor is entirely storyboard-based
- `converters.py` provides `assembly_guide_to_storyboard()`

### What still uses assembly guide
- CLI: `parse`, `segments`, `init`, `graphics`, `narration`, `trim-footage` (via `_load_project()` → `parse_assembly_guide()`)
- `init_project()` — hardcoded to assembly guide, creates `SegmentStatus` from `SegmentType` enum
- `trim_source_footage()` — returns empty for storyboards (no trim note data)
- `ProductionState.assembly_guide_path` field name
- `adapters/dashboard.py` — Streamlit UI, uses assembly guide only

## Design

### 1. Format Changes

The storyboard markdown gains three new sections. Everything else stays as-is.

#### Header metadata (after title, before legend)

```markdown
# Shot-by-Shot Storyboard: "Title"

**Total Duration:** ~55 minutes
**Resolution:** 1080p
**Format:** MP4 (H.264 + AAC)

**Legend:**
...
```

#### Pre-production checklist (new section)

```markdown
## PRE-PRODUCTION

### Audio
- [ ] Generate full narrator voiceover from screenplay (TTS)
- [ ] Select/generate dark ambient background music
- [ ] Normalize all audio to -14 LUFS

### Graphics
- [ ] Lower thirds for 15+ characters
- [ ] Timeline markers (date stamps)
- [ ] Financial amount overlays

### Maps
- [ ] Lowcountry SC region with 5 counties highlighted
- [ ] Moselle property aerial zoom-in
```

#### Post-assembly checklist (new section, at end)

```markdown
## POST-ASSEMBLY

- [ ] Color grade consistency pass across all segments
- [ ] Audio levels check (-14 LUFS narrator, -30 LUFS music bed)
- [ ] Transition timing review
- [ ] Thumbnail generation
- [ ] Export at 1080p H.264 + AAC
```

### 2. Model Changes

#### `models_storyboard.py`

Add new dataclass and fields:

```python
@dataclass
class ChecklistItem:
    text: str
    checked: bool
    category: str  # "audio", "graphics", "maps", "post"

@dataclass
class Storyboard:
    title: str
    total_duration: str | None = None          # NEW
    resolution: str | None = None              # NEW
    format: str | None = None                  # NEW
    pre_production: list[ChecklistItem] = field(default_factory=list)  # NEW
    post_checklist: list[ChecklistItem] = field(default_factory=list)  # NEW
    segments: list[StoryboardSegment] = field(default_factory=list)
    stock_footage: list[StockFootageNeeded] = field(default_factory=list)
    photos_needed: list[PhotoNeeded] = field(default_factory=list)
    maps_needed: list[MapNeeded] = field(default_factory=list)
    production_rules: ProductionRules = field(default_factory=ProductionRules)

    # `sections` stays as a @property (computed from segments) — NOT a field
```

New fields default to `None` / `[]` for backward compatibility.

### 3. Parser Changes

#### `parsers/storyboard.py`

Add three extraction functions to `parse_storyboard()`:

- **`_parse_header_metadata(lines)`** — before the first `##`, match `**Key:** value` patterns for Total Duration, Resolution, Format
- **`_parse_pre_production(lines)`** — parse `## PRE-PRODUCTION` subsections, extract `- [ ]` / `- [x]` checkboxes with category from subsection header (`### Audio` → category="audio")
- **`_parse_post_checklist(lines)`** — parse `## POST-ASSEMBLY`, same checkbox extraction, all items get category="post"

No changes to existing segment, layer, stock footage, photo, map, or production rules parsing.

### 4. CLI Changes

Switch 6 legacy commands from `parse_assembly_guide()` to `parse_storyboard()`:

| Command | Change |
|---------|--------|
| `parse` | Use `parse_storyboard()`. Display title, duration, resolution, section/segment counts, pre-production checklist status |
| `segments` | Iterate `Storyboard.segments`. Filter by section still works. Type filter matches on layer `content_type` instead of `SegmentType` enum |
| `init` | Use `parse_storyboard()`, pass to updated `init_project()` |
| `graphics` | Use `parse_storyboard()` directly (services already accept storyboards) |
| `narration` | Use `parse_storyboard()` directly (services already accept storyboards) |
| `trim-footage` | Use `parse_storyboard()`. Source layer content provides file paths + trim info. See "Trim Notes" section below |

Remove `_load_project()` helper (wraps `parse_assembly_guide()`). The argument name changes from `assembly_guide` to `storyboard` in all commands.

### 5. Services Changes

#### Remove `_ensure_storyboard()` bridge

All functions change from `Project | Storyboard` to `Storyboard` only. The `_ensure_storyboard()` function and the `converters.py` import are removed.

#### `init_project(storyboard_path, config)` rewrite

Currently:
- Parses assembly guide internally
- Creates `SegmentStatus` with `seg.segment_type.value` (SegmentType enum)
- Returns `(Project, ProductionState)`

New:
- Accepts a storyboard path, parses with `parse_storyboard()`
- Creates `SegmentStatus` with a derived segment type from layer analysis:
  - Has `source` layer with FOOTAGE → "REAL"
  - Has both FOOTAGE visual + NAR audio → "MIX"
  - Has only NAR audio → "NAR"
  - Has GRAPHIC/MAP/STOCK visual → "GEN"
  - Fallback → "GEN"
- Reads `storyboard.resolution` and `storyboard.format` for ProductionConfig
- Returns `(Storyboard, ProductionState)`

#### `trim_source_footage(storyboard, config)` rewrite

Currently returns empty for storyboards.

New: iterates segments, collects `source` layers that contain file references with trim info:

```
Source | `segments/911-call-full.mp4` trim 0:00-0:05
```

The layer content is parsed by `_parse_trim_from_source(content)` → `(file_path, start, end)`. This is a substring match on the existing source layer format: path first, then optional `trim start-end`.

If no trim info is present in source layers (e.g., storyboard only has `Source | segments/file.mp4`), the full file is used.

### 6. `ProductionState` field rename

`assembly_guide_path: str` → `storyboard_path: str`

The `load()` classmethod handles backward compatibility: reads `assembly_guide_path` from old JSON files and maps it to `storyboard_path`.

### 7. Deprecations

| File | Action |
|------|--------|
| `parsers/assembly_guide.py` | Remove all imports. Keep file for reference. |
| `models.py` | Remove all imports from CLI, services, dashboard. Keep file. |
| `converters.py` | Remove. No longer needed — no Project→Storyboard bridge. |
| `adapters/dashboard.py` | Deprecate. The web editor replaces it. Remove `parse_assembly_guide` import. |
| `_ensure_storyboard()` in services | Remove. Services accept `Storyboard` only. |
| `_load_project()` in CLI | Remove. Replaced by direct `parse_storyboard()` calls. |
| `_extract_narrator_text()` in services | Remove. Dead code from assembly guide era. |

### What This Does NOT Include

- No changes to processors (FFmpeg, TTS, Pillow) — pure functions, model-agnostic
- No changes to web editor frontend — already storyboard-native
- No changes to API routes/schemas — already storyboard-native
- No deletion of deprecated files — just removal of imports
- No extension of storyboard content to cover full video (separate effort)

### Testing

- Unit tests for new parser functions (header metadata, pre-production, post-assembly checkbox extraction)
- Unit test for `ChecklistItem` model
- Unit test for `_parse_trim_from_source()` helper
- Unit test for segment type derivation from layers (for `init_project`)
- Update service tests: replace `Project` fixtures with `Storyboard` fixtures
- Update CLI tests: commands now accept storyboard paths
- Existing storyboard parser tests pass unchanged (new fields are optional/defaulted)
- Integration test: parse storyboard with all sections → init → graphics → narration → verify outputs
- Backward compat: `ProductionState.load()` reads old `assembly_guide_path` field

### Migration Path

1. Update storyboard format (add header, pre-production, post-assembly to `storyboard.md`)
2. Update model + parser (new fields, new extraction functions)
3. Rewrite `init_project()` and `trim_source_footage()` for storyboard
4. Drop `Project | Storyboard` union — services accept `Storyboard` only
5. Switch 6 legacy CLI commands to storyboard parser
6. Remove bridge code (`_ensure_storyboard`, `converters.py`, `_load_project`, `_extract_narrator_text`)
7. Deprecate dashboard, assembly guide parser, old models
8. Rename `ProductionState.assembly_guide_path` → `storyboard_path`
9. Update CLAUDE.md, CHANGELOG.md, README.md
