# JSON Project Format — Replace OTIO

## Goal

Replace OTIO (OpenTimelineIO) with a single `.bee-project.json` file as the primary project format. All project state — segments, media assignments, production progress, render history — lives in one JSON file. Markdown storyboards remain as a write-only import source.

## Data Flow

```
storyboard.md (authored by Claude/human)
    ↓ Node.js parser
.bee-project.json (working format)
    ↓ web UI edits
.bee-project.json (updated)
    ↓ Remotion render
final.mp4
```

## JSON Schema

### Full Structure

```json
{
  "version": 1,
  "title": "The Murdaugh Murders",
  "fps": 30,
  "resolution": [1920, 1080],
  "createdAt": "2026-03-21T00:00:00Z",
  "updatedAt": "2026-03-21T12:00:00Z",

  "segments": [
    {
      "id": "911-call-opening",
      "title": "911 Call Opening",
      "section": "Act 1 — The Night",
      "start": 0,
      "duration": 15,

      "visual": [{
        "type": "FOOTAGE",
        "src": "footage/bodycam-arrival.mp4",
        "trim": [5.0, 20.0],
        "color": "surveillance",
        "kenBurns": null
      }],

      "audio": [
        { "type": "NAR", "text": "On the night of June 7th...", "src": "narration/seg-01.mp3" },
        { "type": "REAL_AUDIO", "src": "footage/bodycam-arrival.mp4", "volume": 0.3 }
      ],

      "overlay": [
        { "type": "TIMELINE_MARKER", "content": "June 7, 2021" },
        { "type": "LOWER_THIRD", "content": "Colleton County — South Carolina" }
      ],

      "music": [
        { "type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.2 }
      ],

      "transition": {
        "type": "FADE_FROM_BLACK",
        "duration": 1.5
      }
    }
  ],

  "production": {
    "narrationEngine": "edge",
    "narrationVoice": "en-US-GuyNeural",
    "transitionMode": "overlap",

    "status": {
      "narration": { "completed": 0, "total": 0 },
      "stock": { "completed": 0, "total": 0 },
      "render": null
    },

    "renders": []
  }
}
```

### Key Design Decisions

- **Times in seconds** (not timecode strings) — matches timeline editor and Remotion
- **`start` + `duration`** instead of `start`/`end` timecodes — no parsing needed
- **`transition` is an object or null** — one transition per segment maximum
- **`src` on audio entries** — narration carries both `text` (script) and `src` (generated file path)
- **No `assigned_media` map** — media paths live directly as `src` on visual/audio/music entries
- **`trim` as `[inSeconds, outSeconds]`** — replaces `tc_in`/`out` metadata strings
- **`production` block** — replaces `voice.json`, `production_state.json`, scattered sidecars
- **`version` field** — for future schema migrations

### TypeScript Types

```ts
interface BeeProject {
  version: number;
  title: string;
  fps: number;
  resolution: [number, number];
  createdAt: string;
  updatedAt: string;
  segments: BeeSegment[];
  production: ProductionState;
}

interface BeeSegment {
  id: string;
  title: string;
  section: string;
  start: number;        // seconds
  duration: number;      // seconds
  visual: VisualEntry[];
  audio: AudioEntry[];
  overlay: OverlayEntry[];
  music: MusicEntry[];
  transition: TransitionEntry | null;
}

interface VisualEntry {
  type: string;          // FOOTAGE, STOCK, MAP, GRAPHIC, etc.
  src: string | null;    // file path or null if not assigned
  trim?: [number, number]; // [in, out] seconds
  color?: string;        // color grade preset
  kenBurns?: string;     // ken burns effect name
  query?: string;        // stock search query
  lat?: number;          // map coordinates
  lng?: number;
  // Any additional metadata as needed
  [key: string]: any;
}

interface AudioEntry {
  type: string;          // NAR, REAL_AUDIO, SFX
  src: string | null;    // file path
  text?: string;         // narration script text
  volume?: number;       // 0-1, default 1
}

interface OverlayEntry {
  type: string;          // LOWER_THIRD, TIMELINE_MARKER, QUOTE_CARD, etc.
  content: string;       // text content or JSON string
  startOffset?: number;  // seconds from segment start (default 0)
  duration?: number;     // seconds (default from DEFAULT_DURATIONS)
  // Metadata for configurable components
  platform?: string;     // for TEXT_CHAT, SOCIAL_POST
  animation?: string;    // for TEXT_CHAT, SOCIAL_POST
  [key: string]: any;
}

interface MusicEntry {
  type: string;          // MUSIC
  src: string | null;
  volume?: number;       // default 0.2
}

interface TransitionEntry {
  type: string;          // DISSOLVE, FADE_FROM_BLACK
  duration: number;      // seconds
}

interface ProductionState {
  narrationEngine: string;
  narrationVoice: string;
  transitionMode: 'overlap' | 'fade';
  status: {
    narration: { completed: number; total: number } | null;
    stock: { completed: number; total: number } | null;
    render: { status: string; progress: number } | null;
  };
  renders: RenderRecord[];
}

interface RenderRecord {
  id: string;
  timestamp: string;
  format: string;
  resolution: [number, number];
  output: string;
  duration: number;
}
```

## Markdown Import Parser

### Location

`web/src/lib/storyboard-parser.ts` — shared between web UI and future Node.js CLI.

### What It Does

1. Read `bee-video:project` JSON code block → project config (title, fps, resolution)
2. Read `bee-video:segment` JSON code blocks → segment data
3. Convert timecodes (`"1:30"`) → seconds (`90`)
4. Compute `start` from cumulative segment durations if not explicit
5. Map old `assigned_media` entries → inline `src` fields
6. Normalize visual type codes (BROLL-DARK → STOCK, etc.)
7. Slugify titles → segment IDs
8. Initialize empty `production` block

### Input/Output

```ts
function parseStoryboardMarkdown(markdown: string): BeeProject
```

### Existing Utilities to Reuse

- `parseTimecode()` from `adapters/time-utils.ts` — timecode → seconds
- `VISUAL_TYPE_MAP` from `adapters/timeline-adapter.ts` — formula code normalization
- `cleanPath()`, `normalizeAudioType()` — from adapter

## Integration Changes

### API Routes (Express — future, or current FastAPI bridge)

- `POST /api/projects/load` — accepts `.md` file path, parses to JSON, writes `.bee-project.json`, returns project
- `GET /api/projects/current` — returns the JSON project
- `PUT /api/projects/save` — writes current state to `.bee-project.json`
- Segment updates modify the project JSON directly (no more per-field `assignMedia` calls)

### Zustand Store

- `storyboard: Storyboard` → `project: BeeProject`
- Remove `assigned_media` logic — `src` is inline on entries
- `loadProject()` reads `.bee-project.json` or parses `.md`

### Timeline Adapter

- `storyboardToTimeline()` → `projectToTimeline()` — reads `seg.start` (already seconds, no `parseTimecode`), reads `seg.visual[0].src` (no `assigned_media` lookup)
- `timelineToProject()` reverse adapter — writes `src` directly on entries

### BeeComposition

- `seg.assigned_media['visual:0']` → `seg.visual[0].src`
- `seg.visual[0]?.metadata?.color` → `seg.visual[0]?.color`
- `seg.visual[0]?.metadata?.ken_burns` → `seg.visual[0]?.kenBurns`
- `parseTimecode(seg.start)` → `seg.start` (already seconds)
- Overlay entries: `entry.content` stays the same, metadata fields are now top-level

### Components to Update

- `ClipProperties.tsx` — reads segment fields
- `AIPanel.tsx` — reads segment data
- `SegmentList.tsx` — displays timecodes (format seconds → `MM:SS`)
- `TimelineActionRenderer.tsx` — reads `data.src`
- `AssetStatusBanner.tsx` — checks `src` instead of `assigned_media`
- All tests using old `Segment`/`Storyboard` types

### What Stays Unchanged

- All 14 Remotion components (receive content/metadata props, format-agnostic)
- Timeline component (reads from adapter output)
- UI layout (Layout.tsx, sidebar structure)
- WaveformRenderer, drag-drop, keyboard shortcuts

## Files

| File | Action |
|------|--------|
| `web/src/types/index.ts` | Rewrite — new BeeProject/BeeSegment types |
| `web/src/lib/storyboard-parser.ts` | Create — markdown → JSON parser |
| `web/src/lib/storyboard-parser.test.ts` | Create — parser tests |
| `web/src/adapters/timeline-adapter.ts` | Modify — read new format |
| `web/src/adapters/timeline-adapter.test.ts` | Modify — use new types |
| `web/src/stores/project.ts` | Modify — `project: BeeProject` |
| `web/src/components/BeeComposition.tsx` | Modify — read new field paths |
| `web/src/components/SegmentList.tsx` | Modify — seconds → display |
| `web/src/components/ClipProperties.tsx` | Modify — read new fields |
| `web/src/components/AIPanel.tsx` | Modify — read new fields |
| `web/src/components/AssetStatusBanner.tsx` | Modify — check `src` |
| Backend API route (bridge) | Modify — serve JSON format |

## Testing

- Parser: markdown → JSON conversion with real storyboard files
- Round-trip: parse markdown → write JSON → read JSON → verify structure
- Timeline adapter: works with new types
- BeeComposition: renders with new segment structure
- Store: load/save project lifecycle

## Migration Path

1. Build the parser and new types
2. Update the timeline adapter
3. Update BeeComposition and store
4. Update remaining components
5. Backend route returns new format (Python backend converts OTIO → JSON as bridge)
6. Eventually: Node.js backend replaces Python entirely

## Success Criteria

1. `.bee-project.json` is the working format for all web UI operations
2. Storyboard markdown can be imported to JSON via parser
3. All web UI features work with the new format (timeline, preview, overlays, transitions)
4. No OTIO dependency in the web frontend
5. Single file contains all project state
