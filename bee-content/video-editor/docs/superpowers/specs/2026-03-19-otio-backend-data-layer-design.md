# OTIO Backend Data Layer Design (Phase 2)

## Summary

Swap the backend data layer from markdown-parsed `Storyboard` objects + sidecar JSON files to OTIO Timeline files with `ParsedStoryboard` as the runtime model. Session management, API routes, and production services all consume `ParsedStoryboard` (Pydantic models from Phase 1). OTIO is the persistence format. Sidecar files (`assignments.json`, `voice.json`, `segment-order.json`) are deprecated — their data lives in OTIO metadata.

## Motivation

Phase 1 built the formats layer: Pydantic models, markdown parser/writer, OTIO converters, and round-trip tests. The backend still reads from the old markdown parser and scatters state across sidecar files. Phase 2 wires the new formats layer into the running system so that the OTIO file becomes the single source of truth.

## Architecture

```
Load (.otio or .md)
       │
       ▼
  SessionStore
  ├── timeline: otio.Timeline     (persistence object)
  ├── parsed: ParsedStoryboard    (runtime model)
  └── otio_path: Path             (autosave target)
       │
       ├── API routes read from session.parsed
       │   └── parsed_to_schema() → StoryboardSchema (backward-compat)
       │
       ├── Services receive session.parsed
       │   └── iterate seg.config.visual/audio/overlay + seg.narration
       │
       └── Mutations (assign, reorder)
           ├── mutate session.parsed in memory
           ├── to_otio(parsed) → update session.timeline
           └── write .otio to disk (autosave)
```

**Key principle:** Services never touch OTIO directly. `ParsedStoryboard` is the domain model. OTIO is a persistence detail.

## ParsedSegment Extensions

### Segment ID

`ParsedSegment` needs an `id` field for API compatibility and mutation endpoints. It is:

- **Stored as a field** on `ParsedSegment` (not computed lazily)
- **Generated during parsing:** `parse_v2()` and `from_otio()` both populate `id` using `unique_slug(title, seen)` — guaranteeing uniqueness within a storyboard
- **Persisted in OTIO:** already stored as `clip.metadata["bee_video"]["segment_id"]` — `from_otio()` reads it back directly (no recomputation needed)
- **Round-trip safe:** `to_otio()` stores the `id`, `from_otio()` recovers it

Add to `ParsedSegment` dataclass:

```python
@dataclass
class ParsedSegment:
    id: str           # unique slug, e.g. "cold-open"
    title: str
    start: str
    end: str
    section: str
    config: SegmentConfig
    narration: str
```

### Segment Duration

Add a helper function (not a property, since `ParsedSegment` is a dataclass):

```python
def segment_duration(seg: ParsedSegment) -> float:
    return parse_header_tc(seg.end) - parse_header_tc(seg.start)
```

## Session Management

### Current

```python
class SessionStore:
    storyboard: Storyboard | None      # old model
    storyboard_path: Path              # .md file
    project_dir: Path
    # Reads/writes: assignments.json, segment-order.json, voice.json, session.json
```

### New

```python
class SessionStore:
    timeline: otio.schema.Timeline | None   # persistence format
    parsed: ParsedStoryboard | None         # runtime model
    otio_path: Path | None                  # autosave target
    project_dir: Path | None
    # Reads/writes: .otio file + session.json only
```

### `require_project()` Return Type

Changes from `tuple[Storyboard, Path]` to `tuple[ParsedStoryboard, Path]`. All 14+ call sites across routes destructure into `parsed, project_dir = session.require_project()` and must update their variable names/usage accordingly. This is a mechanical but pervasive change.

### Load Flow

`load_project(path, project_dir)` accepts `.md` or `.otio`:

1. **`.otio` file:** Read directly → `from_otio(timeline)` → store both `timeline` and `parsed`
2. **`.md` file (v2 format):** Detect `bee-video:project` JSON block → `parse_v2()` → `to_otio()` → write `.otio` next to source → store both
3. **`.md` file (old table format):** No JSON blocks → `parse_storyboard()` → `old_to_new()` → `to_otio()` → write `.otio` → store both

Format detection: check if the file content contains `` ```json bee-video:project `` or `` ```json bee-video:segment ``. If yes → v2 markdown. If no → old table format.

### Mutation Flow

All mutations follow the same pattern:

1. Mutate `session.parsed` in memory (e.g., update `seg.config.visual[0].src`)
2. Rebuild timeline: `session.timeline = to_otio(session.parsed)`
3. Write to disk: `otio.adapters.write_to_file(session.timeline, session.otio_path)`

This is the autosave mechanism. Every mutation persists immediately.

**Concurrency note:** The narration route spawns a background thread. If a user triggers a mutation (assign/reorder) while narration is running, both could race on `session.parsed` and the OTIO file. For Phase 2, single-user/single-tab usage is assumed. A threading lock around mutations is a Phase 3 concern if needed.

### Sidecar File Deprecation

| Sidecar File | Replacement | Migration |
|---|---|---|
| `assignments.json` | `visual[].src` in segment config → OTIO clip `ExternalReference` | On load: if `.otio` doesn't exist but `assignments.json` does, apply assignments to parsed model before first OTIO save |
| `segment-order.json` | Segment order in `ParsedStoryboard.segments` list → OTIO track clip order | On load: if `segment-order.json` exists, reorder parsed segments before first OTIO save |
| `voice.json` | `project.voice_lock` in OTIO timeline metadata | On load: if `voice.json` exists, merge into project config before first OTIO save |
| `session.json` | Still exists — tracks `otio_path` and `project_dir` only | Format changes: `storyboard_path` → `otio_path` |

During the transition, the load flow checks for sidecar files and absorbs their data into the OTIO on first save. After that, the sidecar files are ignored (not deleted — user can clean up manually or Phase 4 handles it).

### Voice Lock Migration

`ProductionConfig.apply_voice_lock()` currently reads from `.bee-video/voice.json`. This changes to read from `session.parsed.project.voice_lock` instead. The method signature becomes:

```python
def apply_voice_lock(self, voice_lock: VoiceLock | None) -> None:
```

Called as: `config.apply_voice_lock(session.parsed.project.voice_lock)` in route handlers.

## Service Layer Migration

### Model Mapping

Production service functions change their input type from `Storyboard` to `ParsedStoryboard`.

| Old access | New access |
|---|---|
| `seg.visual` (`list[LayerEntry]`) | `seg.config.visual` (`list[VisualEntry]`) |
| `entry.content_type == "FOOTAGE"` | `entry.type == "FOOTAGE"` |
| `entry.content` (freeform string) | `entry.src`, `entry.tc_in`, `entry.out` (typed fields) |
| `seg.audio` (LayerEntry list) | `seg.config.audio` where `type != "NAR"` |
| `seg.music` (separate list) | `seg.config.audio` where `type == "MUSIC"` |
| `entry.content_type == "NAR"` in audio | `seg.narration` (string field on ParsedSegment) |
| `seg.overlay` | `seg.config.overlay` (`list[OverlayEntry]`) |
| `entry.content_type == "LOWER-THIRD"` | `entry.type == "LOWER_THIRD"` (underscore, not hyphen) |
| Overlay `entry.content` (regex-parsed name/role) | `entry.text` + `entry.subtext` (explicit fields) |
| `seg.source` | Merged into `seg.config.visual[].src` |
| `seg.transition` (freeform) | `seg.config.transition_in` (`TransitionConfig`) |
| `seg.assigned_media["visual:0"]` | `seg.config.visual[0].src` (assignment IS the src) |
| `seg.duration_seconds` | `segment_duration(seg)` helper |
| `seg.id` | `seg.id` (stored field, unique slug) |
| `seg.section` | `seg.section` (same field name) |
| `seg.subsection` | Not present in new model (was rarely used) |

### Assignment Simplification

In the old model, assignments were a separate concept — a dict mapping `"layer:index"` to file paths, stored in a sidecar JSON. In the new model, **the assignment IS the `src` field**. When a user drags a media file onto a segment:

1. `session.parsed.segments[i].config.visual[j].src = media_path`
2. Autosave to OTIO (the `src` becomes an `ExternalReference` in the OTIO clip)

No separate assignment tracking needed.

### Functions to Migrate

All functions in `services/production.py` that accept `Storyboard`:

```
generate_graphics_for_project(parsed: ParsedStoryboard, config, state) -> ProductionResult
    Iterate: seg.config.overlay entries where type matches graphic templates
    Note: overlay.text and overlay.subtext replace regex-parsed entry.content

generate_narration_for_project(parsed: ParsedStoryboard, config, state) -> ProductionResult
    Iterate: seg.narration (string) for each segment with non-empty narration

trim_source_footage(parsed: ParsedStoryboard, config, state) -> ProductionResult
    Iterate: seg.config.visual entries, use src + tc_in + out for trim points

generate_captions_estimated(parsed: ParsedStoryboard, out_dir, style) -> ProductionResult
    Iterate: segments with non-empty narration + seg.config.captions config
    Note: narration text from seg.narration, not from audio layer entries

run_full_pipeline(parsed: ParsedStoryboard, config, ...) -> PipelineResult
    Accepts ParsedStoryboard (consistent with other service functions)
    Sequence: init → graphics → captions → narration → trim → assemble

generate_all_previews(parsed: ParsedStoryboard, config) -> ProductionResult
    Iterate: seg.config.visual entries with non-null src for preview generation

rough_cut_export(parsed: ParsedStoryboard, config) -> ProductionResult
    Iterate: seg.config.visual entries, concat assigned clips at 720p
```

### Functions in `processors/captions.py`:

```
extract_caption_segments(parsed: ParsedStoryboard) -> list[dict]
    Old: iterated seg.audio for NAR/REAL_AUDIO entries, used entry.content as text
    New: use seg.narration for NAR text, seg.config.audio for REAL_AUDIO src paths
```

### Functions in `services/preflight.py`:

```
run_preflight(parsed: ParsedStoryboard, project_dir) -> PreflightResult
    Old: iterated seg.visual/audio/overlay using entry.content_type and entry.content
    New: iterate seg.config.visual (entry.type, entry.src), seg.config.audio, seg.config.overlay
```

### Route Helpers to Migrate

These helper functions in `api/routes/production.py` also need updating:

```
_count_narration_segments(parsed) -> int
    Old: checks seg.audio for content_type == "NAR"
    New: checks bool(seg.narration)

_derive_segment_type(seg) -> str
    Old: checks entry.content_type against visual/audio entries
    New: checks entry.type against seg.config.visual/audio
```

### Helper: Segment Duration

```python
def segment_duration(seg: ParsedSegment) -> float:
    return parse_header_tc(seg.end) - parse_header_tc(seg.start)
```

This replaces `StoryboardSegment.duration_seconds` which was a property on the old model.

## API Routes

### Schema Backward Compatibility

The frontend expects `StoryboardSchema` with six-layer segments. A `parsed_to_schema()` converter maintains this contract:

```python
def parsed_to_schema(parsed: ParsedStoryboard) -> StoryboardSchema:
    segments = []
    for seg in parsed.segments:
        segments.append(SegmentSchema(
            id=seg.id,
            start=seg.start,
            end=seg.end,
            title=seg.title,
            section=seg.section,
            section_time="",
            subsection="",
            duration_seconds=segment_duration(seg),
            visual=_visual_entries_to_layer(seg.config.visual),
            audio=_audio_entries_to_layer(seg.config.audio, exclude_type="MUSIC"),
            overlay=_overlay_entries_to_layer(seg.config.overlay),
            music=_audio_entries_to_layer(seg.config.audio, only_type="MUSIC"),
            source=_visual_to_source_layer(seg.config.visual),
            transition=_transition_to_layer(seg.config.transition_in),
            assigned_media=_build_assigned_media(seg.config),
        ))

    # Derive counts from segment configs
    stock_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "STOCK")
    photo_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "PHOTO")
    map_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "MAP")

    return StoryboardSchema(
        title=parsed.project.title,
        total_segments=len(segments),
        total_duration_seconds=max(
            (parse_header_tc(s.end) for s in parsed.segments), default=0
        ),
        sections=[sec.title for sec in parsed.sections],
        segments=segments,
        stock_footage_needed=stock_count,
        photos_needed=photo_count,
        maps_needed=map_count,
        production_rules=[],  # not present in new model, always empty
    )
```

This is a thin mapping layer in the routes — not a service concern.

### Route Changes

| Route | Change |
|---|---|
| `POST /load` | Calls `session.load_project()` which now handles .md/.otio. Response via `parsed_to_schema()`. |
| `GET /current` | Returns `parsed_to_schema(session.parsed)` |
| `PUT /assign` | Mutates `session.parsed.segments[].config.visual[].src`, autosaves OTIO |
| `PUT /reorder` | Reorders `session.parsed.segments`, autosaves OTIO |
| `POST /production/*` | Passes `session.parsed` to service functions |
| `POST /export/otio` | Uses `clean_otio(session.timeline)`. Deprecates `exporters/otio_export.py`. |
| `GET /preflight` | Passes `session.parsed` to `run_preflight()` |
| WebSocket handlers | Change `session.storyboard_path` → `session.otio_path` in `_ws_produce()` and `_ws_narration()` |

### New Endpoint

`GET /api/projects/export` — export current project to markdown or clean OTIO. Reuses `write_v2()` and `clean_otio()` from Phase 1.

### Deprecated

`exporters/otio_export.py` — the old OTIO exporter that used `Storyboard` objects. Superseded by `formats/otio_convert.py`. The `export-legacy` CLI command still references it (kept for Phase 4 cleanup).

## Migration Path

### Auto-Migration on Load

When loading an old-format project:

1. Parse old markdown → `old_to_new()` → `ParsedStoryboard`
2. If `assignments.json` exists: apply assignments to `parsed.segments[].config.visual[].src`
3. If `segment-order.json` exists: reorder `parsed.segments`
4. If `voice.json` exists: set `parsed.project.voice_lock`
5. `to_otio(parsed)` → write `.otio` file
6. Log migration message to console

### No Dual-Write

Once loaded, `.otio` is the source of truth. The original `.md` is not modified. Users who want an updated markdown can use `bee-video export --format md`.

## Testing Strategy

### Existing Tests Must Pass

The `parsed_to_schema()` converter ensures API responses match the old format. Existing API tests should pass without modification (the response shape is identical).

### New Tests

| Area | Tests |
|---|---|
| Session | Load `.otio`, load v2 `.md` (auto-converts), load old `.md` (auto-migrates + converts) |
| Session | Assign mutates parsed + writes OTIO, reorder mutates + writes OTIO |
| Session | Sidecar file absorption (assignments.json, voice.json, segment-order.json) |
| Schema compat | `parsed_to_schema()` produces valid `StoryboardSchema` matching old format |
| Schema compat | `stock_footage_needed`, `photos_needed`, `maps_needed` derived from visual types |
| Services | Each production function works with `ParsedStoryboard` input |
| Services | Caption extraction from `seg.narration` instead of audio entries |
| Services | Preflight validation with new model |
| Services | Preview generation and rough cut with new model |
| Integration | Load old project → auto-migrate → run graphics/narration → verify output |

### Service Test Migration

Existing service tests construct `Storyboard` objects with `StoryboardSegment` and `LayerEntry`. These must be updated to construct `ParsedStoryboard` with `ParsedSegment` and `SegmentConfig`/`VisualEntry`/etc. The assertions stay the same — only the test data construction changes.

## Implementation Phases

### Phase 2a: Session + Schema Converter

- Add `id` field to `ParsedSegment`, populate in `parse_v2()` and `from_otio()`
- Add `segment_duration()` helper
- Rewrite `SessionStore` to hold `timeline` + `parsed` + `otio_path`
- Implement `load_project()` with .md/.otio detection and auto-migration
- Implement sidecar file absorption during migration
- Implement mutation flow (assign → mutate parsed → autosave OTIO)
- Build `parsed_to_schema()` converter (including derived counts for stock/photos/maps)
- Change `require_project()` return type to `tuple[ParsedStoryboard, Path]`
- Change `ProductionConfig.apply_voice_lock()` to accept `VoiceLock` instead of reading file
- Tests for all session operations and schema conversion

### Phase 2b: Service Migration

- Migrate `generate_graphics_for_project()` to `ParsedStoryboard`
- Migrate `generate_narration_for_project()` to `ParsedStoryboard`
- Migrate `trim_source_footage()` to `ParsedStoryboard`
- Migrate `run_full_pipeline()` to accept `ParsedStoryboard`
- Migrate `extract_caption_segments()` in `processors/captions.py`
- Migrate `run_preflight()` in `services/preflight.py`
- Migrate `generate_all_previews()` and `rough_cut_export()`
- Migrate route helpers: `_count_narration_segments()`, `_derive_segment_type()`
- Update all service tests

### Phase 2c: Route Wiring

- Wire routes to use new session + `parsed_to_schema()`
- Update all `require_project()` call sites (14+ locations)
- Update assign/reorder endpoints to use new mutation flow
- Wire production routes to pass `session.parsed` to services
- Update WebSocket handlers (`storyboard_path` → `otio_path`)
- Add export endpoint
- Deprecate `exporters/otio_export.py` (mark as deprecated, keep for `export-legacy` CLI)
- Run full API test suite

## Dependencies

No new dependencies. Phase 1 already added `pydantic` and `opentimelineio` to core.
