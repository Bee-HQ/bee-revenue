# OTIO Project Format Design

## Summary

Replace the markdown storyboard as the working project format with OpenTimelineIO (OTIO), using a rich markdown format (with JSON code blocks) as the human-readable authoring and version-control layer. Bidirectional lossless conversion between markdown and OTIO. Clean OTIO export for NLE interchange (DaVinci Resolve, Premiere).

## Motivation

The current markdown storyboard format cannot represent production details precisely — clip in/out points, audio volume levels, transition parameters, TTS engine config, color grades per clip, and overlay positioning are either absent or loosely described. This forces the production pipeline to interpret intent rather than execute instructions, and scatters state across sidecar files (`assignments.json`, `voice.json`, `segment-order.json`).

OTIO is Pixar's open standard for timeline interchange. It natively represents clips with media references, source ranges, transitions, and multiple tracks. By extending it with a `bee_video` metadata namespace, it becomes a complete project file that the UI and pipeline operate on directly.

## Format Stack

Three layers, each with a clear job:

```
┌─────────────────────────────────┐
│  Markdown + JSON blocks (.md)   │  Author / review / version control
│  Human-readable, git-diffable   │
├─────────────────────────────────┤
│  OTIO project file (.otio)      │  Working format for UI + pipeline
│  Timeline + bee_video metadata  │
├─────────────────────────────────┤
│  Clean OTIO (.otio)             │  Export for DaVinci / Premiere
│  Standard OTIO, no custom data  │
└─────────────────────────────────┘
```

**Source of truth:** Either markdown or OTIO can be the source at any point. Write markdown → import to OTIO → edit in UI (mutates OTIO) → export back to markdown for review/commit. The round-trip is lossless.

## Markdown Format Spec

### Block Types

- `` ```json bee-video:project `` — one per file, at the top. Project-level config. If missing, defaults are used. If more than one appears, the parser errors.
- `` ```json bee-video:segment `` — one per segment. Production config for all layers. If a segment header exists without a corresponding JSON block, an empty segment is created (narration-only segments are valid).
- `## Section Title (start - end)` — act/section header. Timecodes use `M:SS` or `H:MM:SS` shorthand.
- `### start - end | Title` — segment header with timecodes. Timecodes use `M:SS` or `H:MM:SS` shorthand.
- `> NAR:` blockquotes — narration text, extracted for TTS. See Narration Association Rules below.

### Narration Association Rules

Narration blockquotes (`> NAR: ...`) are associated with the nearest preceding segment:

1. A `> NAR:` blockquote belongs to the **most recent `### segment` header above it**.
2. Consecutive `> NAR:` lines (with no blank line between them) are a single narration block.
3. Multiple narration blocks separated by blank lines within the same segment are concatenated with paragraph breaks.
4. A `> NAR:` blockquote appearing before any `### segment` header is a parser error.
5. Any blockquote **not** starting with `> NAR:` is ignored (treated as a markdown comment/note, not extracted for TTS).
6. The `> NAR:` prefix is stripped before storing the narration text.

Example:

````markdown
### 0:00 - 0:15 | Cold Open

```json bee-video:segment
{ "visual": [...] }
```

> NAR: First paragraph of narration for Cold Open.
> Continuation of the same paragraph.

> NAR: Second paragraph, still belongs to Cold Open.

> This is a creative note, NOT narration (no NAR: prefix). Ignored.

### 0:15 - 0:32 | The 911 Call
````

### Timecode Formats

Two timecode contexts with different formats:

| Context | Format | Examples |
|---------|--------|---------|
| Segment headers (`### ...`) | `M:SS` or `H:MM:SS` (shorthand) | `0:00`, `2:30`, `1:05:30` |
| JSON block values (`in`, `out`) | `HH:MM:SS.mmm` (precise) | `00:02:14.500`, `01:05:30.000` |

The converter normalizes between formats: header shorthand → precise OTIO rational time → header shorthand on export.

### Project Block

```json
{
  "title": "The Murdaugh Murders",
  "version": 1,
  "voice_lock": {
    "engine": "elevenlabs",
    "voice": "Daniel",
    "model": "eleven_multilingual_v2"
  },
  "color_preset": "dark_crime",
  "default_transition": { "type": "dissolve", "duration": 1.0 },
  "output": {
    "resolution": "1920x1080",
    "fps": 30,
    "codec": "h264",
    "crf": 18
  }
}
```

**`voice_lock` fields:** `engine` (required), `voice` (required), `model` (optional, engine-specific).

**`version`:** Format version. Starts at `1` for this spec. Increment on breaking changes to the JSON schema. The parser reads the version and applies migrations if needed. Files without a `version` field are treated as version `1`.

### Segment Block

```json
{
  "visual": [
    {
      "type": "FOOTAGE",
      "src": "footage/bodycam-arrival.mp4",
      "in": "00:02:14.500",
      "out": "00:02:29.500",
      "color": "surveillance",
      "ken_burns": "zoom_in"
    }
  ],
  "audio": [
    { "type": "REAL_AUDIO", "src": "footage/bodycam-arrival.mp4", "volume": 0.6 },
    { "type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.2, "fade_in": 2.0 }
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "Colleton County, SC",
      "subtext": "June 7, 2021 — 10:07 PM",
      "duration": 4.0,
      "position": "bottom-left"
    }
  ],
  "captions": {
    "style": "karaoke",
    "font_size": 42
  },
  "transition_in": {
    "type": "fade_from_black",
    "duration": 1.5
  }
}
```

### Visual Types

| Type | Fields | Description |
|------|--------|-------------|
| `FOOTAGE` | `src`, `in`, `out`, `color`, `ken_burns` | Source footage with trim points |
| `STOCK` | `src` (or `null` + `query`), `in`, `out`, `color`, `ken_burns` | Stock footage (Pexels) |
| `PHOTO` | `src`, `ken_burns`, `duration` | Still image as video |
| `MAP` | `style`, `center`, `zoom`, `markers` | Generated from coordinates |
| `GRAPHIC` | `template`, `text`, `subtext` | Generated overlay (Pillow) |
| `GENERATED` | `src` (or `null` + `prompt`), `provider` | AI-generated video clip |
| `WAVEFORM` | `src`, `color` | Audio waveform visualization |
| `BLACK` | `duration` | Solid black frame |

**Note:** `GENERATED` is a new visual type not in the current `VisualType` enum. It must be added to `models_storyboard.py` in Phase 1. `WAVEFORM` and `BLACK` already exist in the current enum and are preserved. The legacy `UNKNOWN` type is removed — any unrecognized type in the JSON block is a parser error.

### Audio Types

| Type | Fields | Description |
|------|--------|-------------|
| `REAL_AUDIO` | `src`, `volume`, `in`, `out` | Audio from source footage |
| `MUSIC` | `src`, `volume`, `fade_in`, `fade_out` | Background music |
| `SFX` | `src`, `volume`, `in`, `out` | Sound effects |
| `NAR` | (text from `> NAR:` blockquote), `engine`, `voice` | TTS narration |

**Naming migration:** The current codebase uses `REAL AUDIO` (space) in the `AudioType` enum. The new format uses `REAL_AUDIO` (underscore). The converter handles both on read; on write, always emits underscore form. The enum must be updated in Phase 1.

### Overlay Types

| Type | Fields | Description |
|------|--------|-------------|
| `LOWER_THIRD` | `text`, `subtext`, `duration`, `position` | Name/role bar |
| `TIMELINE_MARKER` | `date`, `description` | Date stamp |
| `QUOTE_CARD` | `quote`, `author` | Quote display |
| `FINANCIAL_CARD` | `amount`, `description` | Dollar amount |
| `TEXT_OVERLAY` | `text`, `position` | Simple text |

### Captions

Captions are a **segment-level config**, not an overlay type. They control burned-in subtitle generation for the entire segment. Defined as a top-level key in the segment JSON block:

```json
{
  "captions": {
    "style": "karaoke",
    "font_size": 42
  }
}
```

This distinction matters: overlays are individual visual elements with their own timing and positioning. Captions are a processing instruction that applies to the segment's narration audio as a whole. In OTIO, captions config is stored as metadata on the V1 clip, not as a separate track clip.

### Special Values

- `"src": null` — asset not yet acquired. Paired with `"query"` (stock search intent) or `"prompt"` (AI generation intent).
- Narration text lives in `> NAR:` blockquotes below the segment block — readable and canonical. Not duplicated inside the JSON. See Narration Association Rules.
- Unknown JSON keys are passed through on round-trip (forward-compatible).

### Multi-Visual Segments

A segment may have multiple entries in the `visual` array (e.g., a MAP followed by STOCK footage). In OTIO, these become **sequential clips on V1** within the segment's time range. The segment header timecodes define the total duration; individual clip durations are derived from their `in`/`out` values. If `in`/`out` are not specified, the clips divide the segment duration equally.

This matches the current model where multiple visual entries play back-to-back, not composited/stacked.

### Full Example

````markdown
```json bee-video:project
{
  "title": "The Murdaugh Murders",
  "version": 1,
  "voice_lock": { "engine": "elevenlabs", "voice": "Daniel" },
  "color_preset": "dark_crime",
  "default_transition": { "type": "dissolve", "duration": 1.0 },
  "output": { "resolution": "1920x1080", "fps": 30, "codec": "h264", "crf": 18 }
}
```

## Act 1: The Night Of (0:00 - 2:30)

### 0:00 - 0:15 | Cold Open

```json bee-video:segment
{
  "visual": [{
    "type": "FOOTAGE",
    "src": "footage/bodycam-arrival.mp4",
    "in": "00:02:14.500",
    "out": "00:02:29.500",
    "color": "surveillance",
    "ken_burns": "zoom_in"
  }],
  "audio": [
    { "type": "REAL_AUDIO", "src": "footage/bodycam-arrival.mp4", "volume": 0.6 },
    { "type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.2, "fade_in": 2.0 }
  ],
  "overlay": [{
    "type": "LOWER_THIRD",
    "text": "Colleton County, SC",
    "subtext": "June 7, 2021 — 10:07 PM",
    "duration": 4.0,
    "position": "bottom-left"
  }],
  "captions": { "style": "karaoke", "font_size": 42 },
  "transition_in": { "type": "fade_from_black", "duration": 1.5 }
}
```

> NAR: On the night of June 7th, 2021, a 911 call
> shattered the silence of a South Carolina estate.

### 0:15 - 0:32 | The 911 Call

```json bee-video:segment
{
  "visual": [{
    "type": "STOCK",
    "src": "stock/aerial-farm-dusk-001.mp4",
    "in": "00:00:05.000",
    "out": "00:00:22.000",
    "color": "dark_crime"
  }],
  "audio": [
    { "type": "REAL_AUDIO", "src": "audio/911-call-edited.wav", "volume": 1.0 }
  ],
  "overlay": [{
    "type": "TIMELINE_MARKER",
    "date": "June 7, 2021",
    "description": "10:07 PM — 911 call received"
  }],
  "transition_in": { "type": "dissolve", "duration": 1.0 }
}
```

> NAR: What followed would unravel decades of
> power, privilege, and murder.
````

## OTIO Structure

### Metadata Namespace

All custom data lives under `metadata["bee_video"]` (underscore). This matches the existing OTIO exporter at `exporters/otio_export.py` which already uses `bee_video` as the namespace key. Using underscore avoids ambiguity with Python dict access.

### Timeline Mapping

```
Timeline: "The Murdaugh Murders"
├── metadata.bee_video.project
│   ├── voice_lock: { engine, voice, model }
│   ├── color_preset: "dark_crime"
│   ├── default_transition: { type, duration }
│   ├── output: { resolution, fps, codec, crf }
│   └── version: 1
│
├── Track: "V1" (video)
│   ├── Clip: "Cold Open"
│   │   ├── media_ref → ExternalReference("footage/bodycam-arrival.mp4")
│   │   ├── source_range: in=02:14.5, duration=15s
│   │   ├── metadata.bee_video.visual: { type, color, ken_burns }
│   │   ├── metadata.bee_video.captions: { style, font_size }
│   │   └── metadata.bee_video.segment_id: "cold-open"
│   ├── Transition: fade_from_black (1.5s)
│   ├── Clip: "The 911 Call"
│   │   └── ...
│
├── Track: "A1" (narration)
│   ├── Clip: "Cold Open NAR"
│   │   ├── media_ref → MissingReference() (not yet generated)
│   │   ├── source_range: in=0, duration=10s (estimated from word count at 150 wpm)
│   │   └── metadata.bee_video.narration: { text, engine, voice }
│
├── Track: "A2" (real audio / SFX)
│   ├── Clip: "Bodycam Audio"
│   │   ├── media_ref → ExternalReference("footage/bodycam-arrival.mp4")
│   │   └── metadata.bee_video.audio: { type: "REAL_AUDIO", volume: 0.6 }
│
├── Track: "A3" (music)
│   ├── Clip: "Dark Ambient"
│   │   ├── media_ref → ExternalReference("music/dark-ambient.mp3")
│   │   └── metadata.bee_video.audio: { type: "MUSIC", volume: 0.2, fade_in: 2.0 }
│
├── Track: "OV1" (overlays)
│   ├── Clip: "Location Lower Third"
│   │   ├── media_ref → MissingReference() (generated by graphics processor)
│   │   ├── source_range: in=0, duration=4.0 (from overlay duration field)
│   │   ├── offset: starts at segment start (default; adjustable in UI)
│   │   └── metadata.bee_video.overlay: { type, text, subtext, duration, position }
│
└── Markers (sections)
    ├── Marker: "Act 1: The Night Of" @ 0:00, duration=2:30
    └── ...
```

### Cross-Track Clip Correlation

The OTIO → markdown converter must reassemble segment data from multiple tracks. The correlation algorithm:

1. **V1 is the master track.** Walk V1 clips in order. Each V1 clip defines a segment.
2. **`segment_id` metadata** links clips across tracks. Every clip on A1/A2/A3/OV1 has `metadata.bee_video.segment_id` matching a V1 clip's `segment_id`. IDs are generated as `slug(title)` with collision suffixes (`-2`, `-3`) for duplicate titles. Slugification: lowercase, replace non-alphanumeric with hyphens, collapse runs, strip leading/trailing hyphens.
3. **Fallback: time-range overlap.** If `segment_id` is missing (e.g., from a clean import), clips on other tracks are matched to the V1 clip whose time range they overlap with (>50% overlap wins).
4. **Music spanning multiple segments.** A music clip on A3 that spans multiple V1 clips is associated with the **first** V1 clip it overlaps. The `in`/`out` times in the exported markdown reflect the music clip's full duration, not the segment's.
5. **Gaps on V1.** Gaps (no clip) on V1 are ignored — they don't produce markdown segments.

### Media References

- **`ExternalReference(target_url="footage/bodycam.mp4")`** — file exists on disk. Path is relative to project directory.
- **`MissingReference()`** — asset not yet acquired or generated. Generation config in `metadata.bee_video.*`. The production pipeline reads this and produces the asset, then updates the reference to `ExternalReference`.

### Narration Timing

Narration clips on A1 need a duration, but TTS hasn't generated the audio yet. Strategy:

1. On import: estimate duration from narration word count at **150 words per minute**.
2. After TTS generation: update the A1 clip's `source_range` with actual audio duration.
3. If actual narration is longer than the segment's visual duration, flag a warning (narration overruns the cut).

### Metadata Key Reference

| Level | Key | Content |
|-------|-----|---------|
| Timeline | `bee_video.project` | voice_lock, color_preset, default_transition, output, version |
| Clip (all tracks) | `bee_video.segment_id` | Segment identifier for cross-track correlation |
| Clip (V1) | `bee_video.visual` | type, color, ken_burns |
| Clip (V1) | `bee_video.captions` | style, font_size (segment-level caption config) |
| Clip (A1) | `bee_video.narration` | text, engine, voice |
| Clip (A2/A3) | `bee_video.audio` | type, volume, fade_in, fade_out |
| Clip (OV1) | `bee_video.overlay` | type, text, subtext, duration, position |
| Marker | `bee_video.section` | section name |

## Conversion Pipeline

### Markdown → OTIO

```
Parse markdown
  ├── Extract ```json bee-video:project``` → Timeline metadata
  │     (error if >1 project block; use defaults if missing)
  ├── Extract ## headers → Section markers on timeline
  ├── For each ### segment:
  │     ├── Parse timecodes from header → clip source_range
  │     ├── Extract ```json bee-video:segment``` → layer config
  │     │     (empty segment if no JSON block found)
  │     ├── Extract > NAR: blockquotes → narration text
  │     │     (per Narration Association Rules)
  │     ├── Generate segment_id from slug(title) (append -2, -3 on collision)
  │     └── For each layer:
  │           ├── visual[] → V1 track clips (sequential, ExternalReference or MissingReference)
  │           ├── audio[] → A1 (NAR), A2 (REAL_AUDIO/SFX), A3 (MUSIC) track clips
  │           ├── overlay[] → OV1 track clips (MissingReference with generation config)
  │           ├── captions → metadata on V1 clip
  │           └── transition_in → OTIO Transition before first V1 clip in segment
  └── Write .otio file
```

### OTIO → Markdown

```
Read .otio
  ├── Timeline metadata → ```json bee-video:project``` block
  ├── Section markers → ## headers with time ranges
  └── Walk V1 track clips in order:
        ├── Clip name + source_range → ### timecode | Title
        ├── Correlate clips from A1/A2/A3/OV1 by segment_id (fallback: time overlap)
        ├── Group multi-visual clips (consecutive V1 clips with same segment_id)
        ├── Assemble all layers → ```json bee-video:segment``` block
        ├── Narration text from A1 metadata → > NAR: blockquotes (below JSON block)
        └── Emit segment
```

### OTIO → Clean OTIO

```
Deep copy timeline
  ├── Strip all metadata["bee_video"] keys recursively
  ├── Optionally: convert bee_video metadata to clip markers/comments (for NLE readability)
  ├── Keep clips, transitions, tracks, media references
  ├── MissingReference stays as-is (NLE shows as offline media)
  └── Write clean .otio
```

### Round-Trip Guarantees

- `markdown → OTIO → markdown` produces an identical file under canonical serialization.
- `OTIO → markdown → OTIO` produces an identical timeline structure.
- Section headers, segment titles, narration text preserved exactly.
- Unknown JSON keys passed through (forward-compatible).
- Segment order = document order = timeline order.

**Canonical serialization:** The markdown writer uses a deterministic format — 2-space JSON indentation, keys in schema-defined order, one blank line between segments, narration blockquotes immediately after the JSON block. Round-trip tests compare against this canonical form, not the original authored whitespace.

### Error Handling

The parser is **strict by default, lenient on opt-in:**

| Condition | Behavior |
|-----------|----------|
| Invalid JSON in a `bee-video:*` block | Error with line number |
| Multiple `bee-video:project` blocks | Error |
| Missing `bee-video:project` block | Warning, use defaults |
| Segment header without JSON block | Valid — creates empty segment (narration-only) |
| JSON block without segment header | Error — orphaned block |
| Unknown JSON keys | Preserved (forward-compatible) |
| `> NAR:` before any segment | Error |
| Malformed timecodes | Error with line number and expected format |
| `--lenient` CLI flag | Downgrades errors to warnings, skips bad segments |

## Layer Model Migration

The current `StoryboardSegment` model has six layer lists: `visual`, `audio`, `overlay`, `music`, `source`, `transition`. The new format consolidates these:

| Old Layer | New Location | Migration |
|-----------|-------------|-----------|
| `visual` | `visual[]` | Direct mapping. `WAVEFORM` type preserved. |
| `audio` | `audio[]` (type `REAL_AUDIO` or `NAR`) | Direct mapping. |
| `overlay` | `overlay[]` | Direct mapping. |
| `music` | `audio[]` (type `MUSIC`) | Music entries move into the unified `audio` array. |
| `source` | `visual[].src` + `visual[].in` + `visual[].out` | Source paths and trim info merge into visual entries. |
| `transition` | `transition_in` object | Freeform text → structured `{ type, duration }`. |

The migration converter (`old_storyboard_to_new_markdown()`) handles this mapping in Phase 1.

## File Layout

```
my-project/
├── storyboard.md              ← authored / version-controlled
├── storyboard.otio            ← working project file (UI + pipeline)
├── footage/
├── stock/
├── music/
├── audio/
├── output/
│   ├── segments/
│   ├── narration/
│   ├── graphics/
│   └── final/
└── .bee-video/
    └── session.json           ← UI session state (tracks storyboard.otio as primary)
```

**Naming convention:** The OTIO file shares the markdown file's basename — `storyboard.md` → `storyboard.otio`. Session management tracks the `.otio` path as primary, with a `source_md` field pointing back to the originating markdown file.

`assignments.json`, `voice.json`, and `segment-order.json` are deprecated — their data now lives in the OTIO project file.

## UI Changes

### Current Flow

```
storyboard.md → parser → Zustand store → UI
                                ↓
                     assignments.json (sidecar)
```

### New Flow

```
storyboard.md → import → storyboard.otio → Zustand store → UI
                              ↑                   ↓
                         autosave on every edit
                              ↓
                    export --format md (on demand)
```

### API Response Schema Changes

The API currently returns `StoryboardSchema` (matching the old six-layer model). Phase 3 introduces updated response schemas:

- `SegmentSchema` gains: `captions` (object), `transition_in` (object). Loses: `music` (merged into `audio`), `source` (merged into `visual`), `transition` (replaced by `transition_in`).
- New endpoint: `GET /api/projects/export` — export to markdown or clean OTIO.
- Frontend `types/index.ts` must be updated to match.

### Component Changes

1. **LoadProject** — accepts `.md` (runs import to create `.otio`) or `.otio` (opens directly). New project option.
2. **All edits save to OTIO** — media assignment updates `media_ref`, transition changes update OTIO transitions, volume changes update audio metadata. No sidecar files.
3. **Export menu** — "Export Markdown" (for review/git), "Export for DaVinci/Premiere" (clean OTIO), "Export Final Video" (production pipeline).
4. **Richer segment editing** — trim handles (in/out point adjustment), transition type picker, per-clip color grade selector, volume sliders on audio clips. These are enabled by OTIO having proper clip source ranges.

### What Stays the Same

- 4-column NLE layout
- Drag-drop from media library
- Segment list with sections
- ProductionBar buttons
- Undo/redo (now persisted via OTIO autosave)

## Implementation Phases

### Phase 1: Format + Converters (backend, no UI changes)

- Define Pydantic models for `bee-video:project` and `bee-video:segment` JSON blocks (validation + serialization)
- Update `VisualType` enum: add `GENERATED`
- Update `AudioType` enum: rename `REAL AUDIO` → `REAL_AUDIO`, add `SFX`
- Build new markdown parser (reads JSON blocks, follows narration association rules)
- Build canonical markdown writer (deterministic serialization)
- Build `markdown → OTIO` converter
- Build `OTIO → markdown` converter
- Build `OTIO → clean OTIO` stripper
- Build `old_storyboard_to_new_markdown()` migration converter
- Round-trip property tests (hypothesis-based, not just golden files)
- CLI commands: `bee-video import`, `bee-video export`

### Phase 2: OTIO as Backend Data Layer

- Build OTIO read/write service (replaces storyboard parser in API routes)
- Production pipeline reads from OTIO
- Session management tracks `.otio` as primary, `source_md` as reference
- Deprecate `assignments.json`, `voice.json`, `segment-order.json`
- All existing API tests pass against new data layer

### Phase 3: UI Integration

- LoadProject accepts `.md` or `.otio`
- Update API response schemas and frontend `types/index.ts`
- Zustand store populated from OTIO (via new API endpoints)
- All edits save back to OTIO (autosave)
- Export menu (markdown, clean OTIO, final video)
- Richer segment editing (trim handles, transition picker, volume sliders)

### Phase 4: Deprecation Cleanup

- Remove old storyboard table parser
- Remove assembly guide parser + converter
- Remove sidecar file handling
- Migrate existing alex-murdaugh storyboard to new format

## Dependencies

- `opentimelineio` — currently an optional dependency (`[project.optional-dependencies] otio`). Must move to core `dependencies` in `pyproject.toml` since OTIO becomes the working project format.
- `pydantic` — currently a transitive dependency via FastAPI (which is itself optional under `web` extra). Must be added to core `dependencies` since the Pydantic models for JSON block validation are used in Phase 1 (converters) independently of the web server.
