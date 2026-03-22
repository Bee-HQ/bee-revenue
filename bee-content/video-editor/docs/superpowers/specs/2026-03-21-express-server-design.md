# Express Server — Replace FastAPI (Step 2 of Python Deprecation)

## Goal

Replace the Python FastAPI backend with a Node.js Express server for core web editor functionality: project state management, media file serving, and segment editing. This is the server skeleton that later steps (TTS, stock search, services) build on.

## Scope

**In scope:**
- Express server setup (entry point, CORS, error handling, static serving)
- Shared code extraction (`web/shared/` for types + parser)
- ProjectStore service (read/write `.bee-project.json`)
- Project routes (load, current, assign, update-segment, reorder, export)
- Media routes (list, upload, serve file)
- Production stubs (so ProductionDropdown doesn't break)
- Effects route (static lists)
- Production status route (file counts)
- Preflight route (check media assignments)
- Frontend changes (shared imports, remove OTIO export, fix bugs)
- Dev/production scripts (no Python)

**Out of scope (later steps):**
- TTS narration (Step 3)
- FFmpeg duration probe on upload (Step 4)
- Stock search/download (Step 5)
- Auto-assign matcher, acquisition, download manager (Step 6)

For out-of-scope routes, the Express server returns `501 Not Implemented` with `{ detail: "Not yet migrated — use Python backend" }`. This makes it obvious what's missing without silently breaking.

## Architecture

```
web/
├── shared/                # NEW — code shared between frontend + server
│   ├── types.ts           # BeeProject, BeeSegment, MediaFile, Effects, etc.
│   ├── storyboard-parser.ts   # Markdown → BeeProject parser
│   └── tsconfig.json      # Shared tsconfig (no DOM, no JSX)
├── server/                # NEW — Express backend
│   ├── index.ts           # Entry point: Express app, CORS, static, error handler
│   ├── routes/
│   │   ├── projects.ts    # 7 routes: load, current, assign, update, reorder, export, download-entry(stub)
│   │   ├── media.ts       # 3 routes: list, upload, serve file (stock/download = 501)
│   │   └── production.ts  # stubs + effects + status + preflight
│   ├── services/
│   │   └── project-store.ts   # Read/write .bee-project.json, in-memory cache
│   └── lib/
│       └── media-utils.ts     # File scanning, path validation, categorization
├── src/                   # React frontend (existing, minor changes)
│   ├── types/index.ts     # Re-exports from ../../shared/types
│   └── lib/storyboard-parser.ts  # Re-exports from ../../shared/storyboard-parser
├── render.mjs             # Remotion render script (existing)
└── package.json
```

## Shared Code Extraction

### Problem

The frontend has types (`src/types/index.ts`) and a parser (`src/lib/storyboard-parser.ts`) that the server also needs. Importing directly from `src/` is fragile — the frontend tsconfig has DOM libs, JSX, and browser-specific settings.

### Solution

Move shared code to `web/shared/`:

**`web/shared/tsconfig.json`:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "declaration": true,
    "outDir": "./dist"
  },
  "include": ["./**/*.ts"]
}
```

**`web/shared/types.ts`:** Move all type definitions from `src/types/index.ts` here. Contains `BeeProject`, `BeeSegment`, `VisualEntry`, `AudioEntry`, `OverlayEntry`, `MusicEntry`, `TransitionEntry`, `ProductionState`, `RenderRecord`, `MediaFile`, `MediaListResponse`, `ProductionStatus`, `Effects`, `DownloadScriptInfo`, `DownloadTools`, `DownloadStatus`.

**`web/shared/storyboard-parser.ts`:** Move parser from `src/lib/storyboard-parser.ts` here. Also move the `parseTimecode` utility it depends on from `src/adapters/time-utils.ts` (just the function, not the whole file).

**Frontend re-exports:**
- `web/src/types/index.ts` → `export * from '../../shared/types';`
- `web/src/lib/storyboard-parser.ts` → `export * from '../../shared/storyboard-parser';`

All existing frontend imports continue to work unchanged. The server imports from `../shared/`.

## Express Server

### index.ts

```ts
import express from 'express';
import cors from 'cors';
import path from 'path';
import { projectRoutes } from './routes/projects';
import { mediaRoutes } from './routes/media';
import { productionRoutes } from './routes/production';

const app = express();
const PORT = parseInt(process.env.PORT || '8420');

// CORS — needed for dev mode (Vite on :5173)
const origins = (process.env.CORS_ORIGINS || '*').split(',');
app.use(cors({ origin: origins }));

app.use(express.json());

// API routes
app.use('/api/projects', projectRoutes);
app.use('/api/media', mediaRoutes);
app.use('/api/production', productionRoutes);

// Static frontend (production mode)
const staticDir = process.env.STATIC_DIR || path.join(__dirname, '../dist');
app.use(express.static(staticDir));
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(staticDir, 'index.html'));
  }
});

// Error handler — { detail: "..." } format to match frontend
app.use((err: any, req: any, res: any, next: any) => {
  const status = err.status || 500;
  res.status(status).json({ detail: err.message || 'Internal server error' });
});

app.listen(PORT, () => console.log(`Bee Video Editor — http://localhost:${PORT}`));
```

## ProjectStore Service

### project-store.ts

Single instance, in-memory cache with file-write on every mutation.

```ts
class ProjectStore {
  private project: BeeProject | null = null;
  private projectDir: string | null = null;
  private jsonPath: string | null = null;

  // Load from storyboard markdown — parse, write .bee-project.json
  loadFromMarkdown(mdPath: string, projectDir: string): BeeProject

  // Load from existing .bee-project.json
  loadFromJson(jsonPath: string): BeeProject

  // Get cached project (throws 404-like error if not loaded)
  get(): BeeProject

  // Get project directory path
  getProjectDir(): string

  // Write current state to .bee-project.json with updated timestamp
  save(): void

  // Update segment fields (transition, color, volume, trim, visual_updates, audio_updates)
  updateSegment(segId: string, updates: Record<string, unknown>): BeeProject

  // Set src on visual/audio/music entry
  assignMedia(segId: string, layer: string, index: number, path: string): BeeProject

  // Reorder segments array
  reorderSegments(order: string[]): void

  // Update production block (narration engine/voice, status)
  updateProduction(updates: Partial<ProductionState>): void
}
```

### Session Persistence

On load, write session info:
- `{projectDir}/.bee-video/session.json` — `{ storyboard_path, project_dir }`
- `~/.bee-video/last-session.json` — same, for auto-restore on server restart

**Backward compatibility:** If `last-session.json` points to an `.otio` file, look for `.bee-project.json` in the same dir. If not found, look for the original `.md` and re-parse. Log a warning.

### updateSegment Logic

The `updates` object supports the same structure as the Python backend:

```ts
// Visual updates: color, kenBurns, trim
{ visual_updates: [{ index: 0, color: "noir" }] }
{ visual_updates: [{ index: 0, kenBurns: "zoom_in" }] }
{ visual_updates: [{ index: 0, trim: [5.0, 20.0] }] }

// Audio updates: volume
{ audio_updates: [{ index: 0, volume: 0.5 }] }

// Transition
{ transition_in: { type: "dissolve", duration: 1.5 } }
{ transition_in: null }  // remove transition
```

## Routes

### Project Routes (7 routes)

| Route | Method | Request | Response |
|---|---|---|---|
| `/load` | POST | `{ storyboard_path, project_dir }` | `BeeProject` |
| `/current` | GET | — | `BeeProject` |
| `/assign` | PUT | `{ segment_id, layer, media_path, layer_index }` | `{ status: "ok" }` |
| `/update-segment` | PUT | `{ segment_id, updates }` | `{ status: "ok" }` |
| `/reorder` | PUT | `{ segment_order: string[] }` | `{ status: "ok", count }` |
| `/export` | GET | `?format=md` or `?format=json` | `{ format, content }` or JSON file |
| `/download-entry` | POST | `{ segment_id, layer, index }` | `501 Not Implemented` (Step 6) |

### Media Routes (3 routes + stubs)

| Route | Method | Request | Response |
|---|---|---|---|
| `/` (list) | GET | — | `{ files: MediaFile[], categories }` |
| `/upload` | POST | multipart file + `?category=footage` | `{ status, path, type }` |
| `/file` | GET | `?path=relative/path.mp4` | File stream (with path security check) |
| `/stock/search` | POST | — | `501 Not Implemented` (Step 5) |
| `/stock/download` | POST | — | `501 Not Implemented` (Step 5) |
| `/download/*` | * | — | `501 Not Implemented` (Step 6) |

### Production Routes (stubs + 3 real)

| Route | Method | Response | Notes |
|---|---|---|---|
| `/effects` | GET | `{ color_presets, transitions, ken_burns }` | Static lists |
| `/status` | GET | `{ phase, segments_total, ... }` | Count files in output dirs |
| `/preflight` | GET | `{ total, found, missing, needs_check }` | Check segment src fields |
| `/render-remotion` | POST | `{ status, output, size_bytes }` | Call render.mjs directly |
| `/init` | POST | `{ status: "ok" }` | Stub — dirs on demand |
| `/graphics` | POST | `{ status: "ok", count: 0 }` | Stub — Remotion handles |
| `/composite` | POST | `{ status: "ok", ... }` | Stub |
| `/assemble` | POST | `{ status: "ok" }` | Stub |
| `/captions` | POST | `{ status: "ok" }` | Stub |
| `/narration` | POST | — | `501 Not Implemented` (Step 3) |
| `/narration/status` | GET | — | `501 Not Implemented` (Step 3) |

## Media Utilities

### media-utils.ts

```ts
// Scan project directories for media files, categorized
function listMediaFiles(projectDir: string): Promise<{ files: MediaFile[]; categories: Record<string, number> }>

// Validate file path is within project directory (prevent path traversal)
function validatePath(filePath: string, projectDir: string): boolean

// Determine media category from file extension
function categorizeFile(filename: string): 'video' | 'audio' | 'image'

// Sanitize uploaded filename (reject dots, path separators, hidden files)
function sanitizeFilename(filename: string): string
```

### Category Directories

Scanned by `listMediaFiles`:
```
footage/    stock/    photos/    graphics/    narration/
maps/       music/    output/segments/    generated/
```

## Markdown Export

Inverse of the parser:

```ts
function exportToMarkdown(project: BeeProject): string
```

Generates:
- `bee-video:project` code block with title/fps/resolution
- `## Section` headers (grouped by `segment.section`)
- `### id | title` segment headers
- `bee-video:segment` code block with visual/audio/overlay/music/transition

## Remotion Render

Call `render.mjs` directly from Node.js (no Python subprocess hop):

```ts
import { execFile } from 'child_process';

// Write project JSON to temp file
// Run: node render.mjs <json_path> <output_path>
// 10 minute timeout
// Return { status, output, size_bytes }
```

## Frontend Changes

| File | Change |
|---|---|
| `src/types/index.ts` | Replace contents with `export * from '../../shared/types'` |
| `src/lib/storyboard-parser.ts` | Replace contents with `export { parseStoryboardMarkdown } from '../../shared/storyboard-parser'` |
| `src/components/ExportMenu.tsx` | Replace "Export for NLE — OTIO" with "Export JSON" |
| `src/api/client.ts` | Remove `connectProgress()` WebSocket method, remove `exportOtio()`, add `exportJson()` |
| `src/components/AIPanel.tsx` | Fix `updateBeeSegment` → `updateSegment` (pre-existing bug) |

## Dev & Production Scripts

### dev.sh (new)
```bash
#!/bin/bash
cd "$(dirname "$0")"
# Kill previous instances
lsof -ti:${BACKEND_PORT:-8420} | xargs kill -9 2>/dev/null
lsof -ti:${FRONTEND_PORT:-5173} | xargs kill -9 2>/dev/null
# Start Express backend
PORT=${BACKEND_PORT:-8420} npx tsx watch server/index.ts &
# Start Vite frontend
npm run dev
```

### start.sh (new)
```bash
#!/bin/bash
cd "$(dirname "$0")"
[[ "$BUILD" == "1" ]] || [[ ! -d dist ]] && npm run build
PORT=${PORT:-8420} STATIC_DIR=dist npx tsx server/index.ts
```

## Dependencies (new additions to web/package.json)

```
express ^4.21
@types/express ^4
multer ^1.4
@types/multer ^1
cors ^2.8
@types/cors ^2
tsx ^4
```

## Testing

New test file: `web/server/__tests__/routes.test.ts`

Using vitest + supertest:
- Project load from markdown
- Project current (returns cached state)
- Assign media (updates segment src)
- Update segment (transition, color, trim)
- Reorder segments
- Export markdown
- Media list (scans directories)
- Media upload
- Media file serving (+ path traversal rejection)
- Effects returns static lists
- Production stubs return success
- 501 for unimplemented routes
- Error handler returns `{ detail }` format

## Success Criteria

1. `./dev.sh` starts web editor with zero Python — Express on :8420, Vite on :5173
2. Can load a `.md` storyboard, edit segments, assign media, reorder — all via Node.js
3. Media library lists files, upload works, preview serves files
4. Production dropdown doesn't error (stubs return success)
5. Remotion render works (direct Node.js call)
6. Export menu works (markdown + JSON, no OTIO)
7. Frontend tests pass (98/98) with shared code extraction
8. New backend tests pass
9. Unimplemented routes return 501 (clear signal for Steps 3-6)
