# Node.js Backend — Replace Python for Web Editor

## Goal

Single Node.js/TypeScript backend in `web/server/` that replaces all FastAPI routes used by the web editor. Python remains only for CLI users (`bee-video` commands). The web editor becomes fully self-contained in `web/`.

## Architecture

```
web/
├── src/              # React frontend (existing)
├── shared/           # NEW — code shared between frontend + server
│   ├── types.ts      # BeeProject, BeeSegment, etc. (moved from src/types/)
│   └── storyboard-parser.ts  # Markdown → BeeProject (moved from src/lib/)
├── server/           # NEW — Express backend
│   ├── index.ts      # Entry point, Express app, CORS, static serving
│   ├── routes/
│   │   ├── projects.ts    # Load, save, update project JSON
│   │   ├── media.ts       # List, upload, serve, stock search/download
│   │   └── production.ts  # TTS, Remotion render, pipeline stubs, effects
│   ├── services/
│   │   ├── project-store.ts   # Read/write .bee-project.json
│   │   ├── matcher.ts         # Auto-assign media to segments
│   │   ├── acquisition.ts     # Stock search + batch download
│   │   └── tts.ts             # Edge-tts-node, ElevenLabs SDK, OpenAI SDK
│   └── lib/
│       └── media-utils.ts     # File scanning, path validation, SSRF check
├── render.mjs        # Remotion render script (existing)
└── package.json      # Shared deps
```

### Shared Code Strategy

Extract types and parser into `web/shared/` with its own `tsconfig.json`:
- `web/shared/types.ts` — `BeeProject`, `BeeSegment`, `MediaFile`, `Effects`, etc.
- `web/shared/storyboard-parser.ts` — `parseStoryboardMarkdown()`
- `web/src/types/index.ts` → re-exports from `../shared/types`
- `web/src/lib/storyboard-parser.ts` → re-exports from `../../shared/storyboard-parser`

This avoids the server importing from the frontend's `src/` directory (which has browser-specific tsconfig, JSX, DOM libs).

## Data Flow

```
storyboard.md
    ↓  parseStoryboardMarkdown() — shared TypeScript parser
.bee-project.json (on disk)
    ↓  Express serves via GET /api/projects/current
React frontend (BeeProject types)
    ↓  User edits → PUT /api/projects/update-segment
.bee-project.json (updated)
    ↓  Remotion render reads JSON directly
final.mp4
```

No more `ParsedStoryboard` → `BeeProjectSchema` bridge. The markdown parser outputs `BeeProject` directly, which gets written to disk as JSON. The frontend reads the same JSON. One format, one language.

## Route Audit

Every method in `web/src/api/client.ts` mapped to its fate:

### Keep — Implement in Node.js (25 routes)

#### Projects (9 routes)

| Route | Method | What it does | Complexity |
|---|---|---|---|
| `/api/projects/load` | POST | Parse `.md` → `BeeProject` JSON, write `.bee-project.json` | Low — parser exists |
| `/api/projects/current` | GET | Read `.bee-project.json` from disk | Trivial |
| `/api/projects/assign` | PUT | Update `seg.visual[i].src` in JSON, write | Low |
| `/api/projects/update-segment` | PUT | Update segment fields (transition, color, volume, trim) | Low |
| `/api/projects/reorder` | PUT | Reorder segments array, write | Trivial |
| `/api/projects/auto-assign` | POST | Match media files to segments by keywords | Medium — port matcher |
| `/api/projects/acquire-media` | POST | Search + download stock for all segments | Medium — port acquisition |
| `/api/projects/download-entry` | POST | Download asset from URL/Pexels for a segment entry | Medium — SSRF validation |
| `/api/projects/export` | GET | `?format=md` → markdown export. `?format=json` → raw JSON download | Low |

#### Media (10 routes)

| Route | Method | What it does | Complexity |
|---|---|---|---|
| `/api/media` | GET | Scan project dirs, list files by category | Low — `fs.readdir` |
| `/api/media/upload` | POST | Save uploaded file, probe duration via FFmpeg | Low — `multer` + `child_process` |
| `/api/media/file` | GET | Serve file with path security check | Low — `res.sendFile` |
| `/api/media/stock/search` | POST | HTTP call to Pexels API | Trivial — `fetch` |
| `/api/media/stock/download` | POST | Download URL to stock dir with SSRF check | Low |
| `/api/media/download/scripts` | GET | List `.sh` scripts in project dir | Low — `fs.readdir` |
| `/api/media/download/tools` | GET | Check which tools are available (yt-dlp, ffmpeg, etc.) | Low — `which` check |
| `/api/media/download/run-script` | POST | Run a download script (async with task tracking) | Medium |
| `/api/media/download/yt-dlp` | POST | Download YouTube video via yt-dlp subprocess | Medium |
| `/api/media/download/status` | GET | Get status of running download tasks | Low |

#### Production (6 routes)

| Route | Method | What it does | Complexity |
|---|---|---|---|
| `/api/production/narration` | POST | Generate TTS audio files for all segments | Medium — 3 TTS SDKs |
| `/api/production/narration/status` | GET | Poll narration progress | Low |
| `/api/production/render-remotion` | POST | Call render.mjs directly (no subprocess hop) | Low |
| `/api/production/effects` | GET | Return static lists of presets | Trivial |
| `/api/production/status` | GET | Count files in output dirs by category | Low — `fs.readdir` |
| `/api/production/preflight` | GET | Check which segments have media assigned | Low — scan project JSON |

### Stub — Return success immediately (5 routes)

These are called by `ProductionDropdown.tsx` but the actual work is now handled by Remotion. The routes exist so the UI doesn't break, but they're no-ops.

| Route | Method | Stub response |
|---|---|---|
| `/api/production/init` | POST | `{ status: "ok" }` — dirs created on demand |
| `/api/production/graphics` | POST | `{ status: "ok", count: 0 }` — Remotion renders overlays |
| `/api/production/composite` | POST | `{ status: "ok", succeeded: 0, failed: 0, skipped: 0, errors: [] }` |
| `/api/production/assemble` | POST | `{ status: "ok" }` — use Remotion render instead |
| `/api/production/captions` | POST | `{ status: "ok" }` — CaptionOverlay component |

### Remove from frontend (4 items)

These require frontend changes — remove the UI elements that call them:

| Item | Frontend location | Change |
|---|---|---|
| OTIO export option | `ExportMenu.tsx` | Remove "Export for NLE" option, replace with "Export JSON" |
| `connectProgress` WebSocket | `api/client.ts` | Remove method (narration uses polling, full pipeline not needed) |
| `roughCut()` | `TimelineEditor.tsx` Rough Cut button | Remove button or rewire to Remotion render at 720p |
| `createMediaDirs()` | `MediaLibrary.tsx` | Remove — dirs created on demand by other routes |

### Not used by frontend (kept only in Python CLI)

| Route | Notes |
|---|---|
| `POST /production/produce` | Full pipeline — CLI only |
| `POST /production/preview/*` | Remotion Player handles preview |
| `PUT /production/voice-lock` | Stored in project JSON `production` block |
| `GET /production/voice-lock` | Read from project JSON |
| `POST /media/generate-clip` | Stubbed AI providers — not wired in UI |
| `POST /production/graphics-batch` | CLI only |

## Error Handling

All error responses use `{ detail: "message" }` format to match the existing frontend API client:

```ts
// Express error handler
app.use((err, req, res, next) => {
  const status = err.status || 500;
  res.status(status).json({ detail: err.message || 'Internal server error' });
});
```

The frontend `client.ts` already parses this format at line 27.

## CORS

- **Dev mode** (Vite on :5173, Express on :8420): Express enables CORS for `http://localhost:5173`. Vite's proxy config also handles this.
- **Production mode** (Express serves built frontend on :8420): No CORS needed — same origin.
- Configurable via `CORS_ORIGINS` env var (comma-separated), default `*` for dev.

## State Management

### project-store.ts

Thin file-based store with in-memory cache:

```ts
class ProjectStore {
  private project: BeeProject | null = null;
  private projectDir: string | null = null;
  private jsonPath: string | null = null;

  loadFromMarkdown(mdPath: string, projectDir: string): BeeProject
  // Parse .md → BeeProject via parseStoryboardMarkdown(), write .bee-project.json

  loadFromJson(jsonPath: string): BeeProject
  // Read .bee-project.json, cache in memory

  get(): BeeProject
  // Return cached project (throw if not loaded)

  getProjectDir(): string
  // Return project directory path (throw if not loaded)

  save(): void
  // Write current state to .bee-project.json, update updatedAt timestamp

  updateSegment(segId: string, updates: Record<string, unknown>): BeeProject
  // Read, mutate segment, save, return updated project

  assignMedia(segId: string, layer: string, index: number, path: string): BeeProject
  // Set src on visual/audio/music entry, save, return updated project

  reorderSegments(order: string[]): void
  // Reorder segments array to match order, save

  updateProduction(updates: Partial<ProductionState>): void
  // Update production block (narration engine/voice, status), save
}
```

Single instance per server process. File-write on every mutation.

### Session Persistence

On load, save session info to `{projectDir}/.bee-video/session.json`:
```json
{"storyboard_path": "storyboard.md", "project_dir": "/path/to/project"}
```

On server start, restore last session from `~/.bee-video/last-session.json`.

**Backward compatibility:** If `last-session.json` points to an `.otio` file (from previous Python sessions), look for a `.bee-project.json` in the same directory. If found, load it. If not, look for the original `.md` storyboard and re-parse it. Log a warning about the migration.

## TTS Strategy

Three engines, all with Node.js support:

| Engine | Package | Notes |
|---|---|---|
| Edge TTS | `edge-tts-node` or `node-edge-tts` | Free, cloud. Evaluate both packages for stability |
| ElevenLabs | `elevenlabs` | Official Node SDK. Needs `ELEVENLABS_API_KEY` |
| OpenAI | `openai` | Official Node SDK. `gpt-4o-mini-tts` model |

Kokoro dropped (Python-only local model).

### tts.ts Service Interface

```ts
interface TTSEngine {
  generate(text: string, voice: string, outputPath: string): Promise<void>;
}

async function generateNarration(
  segments: BeeSegment[],
  engine: string,
  voice: string,
  outputDir: string,
  onProgress?: (done: number, total: number) => void,
): Promise<{ succeeded: string[]; failed: Array<{ file: string; error: string }> }>
```

Extracts narration text from `seg.audio.find(a => a.type === 'NAR')?.text`, generates TTS for each segment, writes to `outputDir/seg-{id}.mp3`.

### Voice Lock

Stored in `.bee-project.json` `production` block. Updated via `ProjectStore.updateProduction()`. No separate voice.json sidecar. The narration route reads engine/voice from the production block if not specified in the request.

## Media Utilities

### media-utils.ts

```ts
// Scan project directories for media files
function listMediaFiles(projectDir: string): { files: MediaFile[]; categories: Record<string, number> }

// Validate path is within project directory (security boundary)
function validatePath(filePath: string, projectDir: string): boolean

// Determine media category from file extension
function categorizeFile(filename: string): string

// SSRF validation — block private IPs, localhost, non-HTTPS
function validateUrl(url: string): boolean

// Probe media duration via FFmpeg (for upload response)
function probeDuration(filePath: string): Promise<number | null>
```

### Media Categories

Same as Python backend: `footage`, `stock`, `photos`, `graphics`, `narration`, `maps`, `music`, `segments`, `generated`.

## Auto-Assign Matcher

Port of `services/matcher.py`. Core logic:

1. Scan media directories for files
2. For each segment with no visual `src`, extract keywords from title/section
3. Match keywords against filenames (case-insensitive substring)
4. Assign best match, track conflicts (multiple segments match same file)

Returns `{ assigned: number, unmatched: number, conflicts: string[] }`.

## Stock Acquisition

Port of `services/acquisition.py`. Core logic:

1. For each segment where `visual[0].query` exists and `visual[0].src` is null
2. Search Pexels API with query
3. Download best match to `stock/` directory
4. Set `visual[0].src` to downloaded path

Returns `{ queries: number, downloaded: number, failed: number, errors: string[] }`.

## Markdown Export

Inverse of the parser — convert `BeeProject` back to storyboard markdown:

```ts
function exportToMarkdown(project: BeeProject): string
```

Generates:
- `bee-video:project` block with title/fps/resolution
- Section headers from `segment.section`
- `bee-video:segment` blocks with visual/audio/overlay/music/transition arrays

## Download Task Manager

Port of the async download tracking from Python. Manages background tasks (yt-dlp, script execution):

```ts
class DownloadTaskManager {
  runScript(scriptPath: string, projectDir: string): string  // returns taskId
  runYtDlp(url: string, category: string, projectDir: string, filename?: string): string
  getStatus(): DownloadStatus[]  // all tasks with output/returnCode
}
```

Tasks run as `child_process.spawn()` with stdout/stderr capture. Completed tasks pruned to last 20.

## Dev & Production Scripts

### dev.sh
```bash
# Start Express server (:8420) + Vite frontend (:5173) with hot reload
npx tsx watch web/server/index.ts &
cd web && npm run dev
```

### start.sh
```bash
# Build frontend, Express serves built frontend + API on :8420
cd web && npm run build
npx tsx web/server/index.ts
```

No Python process needed for either mode.

**Transition:** During development, both scripts can coexist. The old `dev.sh`/`start.sh` (which call `uv run bee-video serve`) are replaced in-place once the Node.js backend is verified working.

## Dependencies (new)

```json
{
  "dependencies": {
    "express": "^4.21",
    "multer": "^1.4",
    "cors": "^2.8",
    "edge-tts-node": "^1",
    "elevenlabs": "^1",
    "openai": "^4",
    "tsx": "^4"
  }
}
```

Using Express 4 + multer 1 for maximum stability. Express 5 can be evaluated later.

## Frontend Changes Required

| File | Change |
|---|---|
| `src/types/index.ts` | Re-export from `../shared/types` |
| `src/lib/storyboard-parser.ts` | Re-export from `../../shared/storyboard-parser` |
| `src/api/client.ts` | Remove `connectProgress()`, add `exportJson()` |
| `src/components/ExportMenu.tsx` | Replace "Export for NLE — OTIO" with "Export JSON" |
| `src/components/TimelineEditor.tsx` | Remove or rewire Rough Cut button |
| `src/components/AIPanel.tsx` | Fix `updateBeeSegment` → `updateSegment` (pre-existing bug) |

## Migration Notes

- The Node.js server replaces the Python server completely for the web editor
- The Python CLI (`bee-video`) continues to work independently
- The two don't need to interoperate — they share storyboard markdown as common input
- Existing Python tests are unaffected
- New vitest tests cover the Node.js routes and services

## Success Criteria

1. `./dev.sh` starts the web editor with zero Python
2. All 25 kept routes + 5 stub routes work
3. `.bee-project.json` is the sole project state file (no OTIO, no sidecars)
4. TTS works with edge-tts, ElevenLabs, and OpenAI Node SDKs
5. Existing frontend tests still pass (98/98)
6. New backend tests cover routes and services
7. Media upload includes FFmpeg duration probe
8. Download panel (yt-dlp, scripts) works
9. Production dropdown doesn't throw errors (stubs return success)
