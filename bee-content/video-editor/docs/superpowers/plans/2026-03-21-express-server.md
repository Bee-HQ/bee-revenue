# Express Server — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Python FastAPI backend with a Node.js Express server for core web editor functionality — project state, media serving, segment editing, Remotion render.

**Architecture:** Extract shared types + parser to `web/shared/`, build Express server in `web/server/` with ProjectStore service, implement core project/media/production routes. Out-of-scope routes (TTS, stock, matcher) return 501.

**Tech Stack:** TypeScript, Express 4, multer, vitest, supertest

**Spec:** `docs/superpowers/specs/2026-03-21-express-server-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `web/shared/types.ts` | Create | All shared TypeScript types (moved from `src/types/index.ts`) |
| `web/shared/storyboard-parser.ts` | Create | Markdown parser + parseTimecode (moved from `src/lib/`) |
| `web/shared/tsconfig.json` | Create | Node-compatible tsconfig for shared code |
| `web/src/types/index.ts` | Rewrite | Re-export from `../../shared/types` |
| `web/src/lib/storyboard-parser.ts` | Rewrite | Re-export from `../../shared/storyboard-parser` |
| `web/server/index.ts` | Create | Express app, CORS, static serving, error handler |
| `web/server/tsconfig.json` | Create | Server tsconfig (Node, no DOM) |
| `web/server/services/project-store.ts` | Create | Read/write .bee-project.json, in-memory cache |
| `web/server/lib/media-utils.ts` | Create | File scanning, path validation, categorization |
| `web/server/routes/projects.ts` | Create | 7 routes: load, current, assign, update, reorder, export, download-entry(501) |
| `web/server/routes/media.ts` | Create | 3 routes + stubs: list, upload, serve file |
| `web/server/routes/production.ts` | Create | Stubs + effects + status + preflight + render-remotion |
| `web/server/__tests__/project-store.test.ts` | Create | ProjectStore unit tests |
| `web/server/__tests__/routes.test.ts` | Create | Route integration tests |
| `web/src/api/client.ts` | Modify | Remove `exportOtio()`, add `exportJson()`, remove `connectProgress()` |
| `web/src/components/ExportMenu.tsx` | Modify | Replace OTIO export with JSON export |
| `web/package.json` | Modify | Add express, multer, cors, tsx, supertest deps |
| `web/tsconfig.json` | Modify | Add shared + server references |
| `web/dev.sh` | Create | New dev script (Express + Vite, no Python) |
| `web/start.sh` | Create | New production script (Express serves built frontend) |

---

### Task 1: Extract shared code to `web/shared/`

**Files:**
- Create: `web/shared/types.ts`
- Create: `web/shared/storyboard-parser.ts`
- Create: `web/shared/tsconfig.json`
- Rewrite: `web/src/types/index.ts`
- Rewrite: `web/src/lib/storyboard-parser.ts`
- Modify: `web/src/adapters/time-utils.ts`
- Modify: `web/tsconfig.json`

- [ ] **Step 1: Create `web/shared/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "./dist",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true
  },
  "include": ["./**/*.ts"]
}
```

- [ ] **Step 2: Move types to `web/shared/types.ts`**

Copy the entire contents of `web/src/types/index.ts` to `web/shared/types.ts`. No changes to the types themselves.

- [ ] **Step 3: Move parser to `web/shared/storyboard-parser.ts`**

Copy `web/src/lib/storyboard-parser.ts` to `web/shared/storyboard-parser.ts`. Change the import of `parseTimecode` — instead of importing from `../adapters/time-utils`, inline the `parseTimecode` function directly in the shared file (it's 5 lines). Also inline the type imports to point to `./types` instead of `../types`.

The shared parser must have zero imports from `web/src/`.

- [ ] **Step 4: Update `web/src/types/index.ts` to re-export**

Replace contents with:
```ts
export * from '../../shared/types';
```

- [ ] **Step 5: Update `web/src/lib/storyboard-parser.ts` to re-export**

Replace contents with:
```ts
export { parseStoryboardMarkdown } from '../../shared/storyboard-parser';
```

- [ ] **Step 6: Add shared reference to `web/tsconfig.json`**

Add `{ "path": "./shared/tsconfig.json" }` to the references array.

- [ ] **Step 7: Run frontend tests to verify nothing broke**

```bash
cd web && npx vitest run 2>&1 | tail -10
```

Expected: 98 tests pass. The re-exports are transparent to all existing imports.

- [ ] **Step 8: Run TypeScript check**

```bash
cd web && npx tsc --noEmit 2>&1 | head -20
```

Expected: clean compile.

- [ ] **Step 9: Commit**

```bash
git add web/shared/ web/src/types/index.ts web/src/lib/storyboard-parser.ts web/tsconfig.json
git commit -m "refactor: extract shared types and parser to web/shared/"
```

---

### Task 2: Express server skeleton + ProjectStore

**Files:**
- Create: `web/server/index.ts`
- Create: `web/server/tsconfig.json`
- Create: `web/server/services/project-store.ts`
- Modify: `web/package.json`

- [ ] **Step 1: Install dependencies**

```bash
cd web && npm install express cors multer tsx && npm install -D @types/express @types/cors @types/multer supertest @types/supertest
```

- [ ] **Step 2: Create `web/server/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true,
    "types": ["node"]
  },
  "include": ["./**/*.ts"],
  "references": [{ "path": "../shared/tsconfig.json" }]
}
```

- [ ] **Step 3: Implement ProjectStore**

Create `web/server/services/project-store.ts`:

The store manages a single `BeeProject` in memory, backed by `.bee-project.json` on disk. Key methods:

- `loadFromMarkdown(mdPath, projectDir)` — read `.md`, parse via `parseStoryboardMarkdown()`, write `.bee-project.json`, cache in memory, write session files
- `loadFromJson(jsonPath)` — read existing `.bee-project.json`, cache
- `get()` — return cached project (throw if not loaded)
- `getProjectDir()` — return project dir (throw if not loaded)
- `save()` — write `.bee-project.json` with updated `updatedAt`
- `updateSegment(segId, updates)` — apply `visual_updates`, `audio_updates`, `transition_in` to segment, save
- `assignMedia(segId, layer, index, path)` — set `src` on entry, save
- `reorderSegments(order)` — reorder segments array, save
- `updateProduction(updates)` — merge into production block, save
- `tryRestoreSession()` — check `~/.bee-video/last-session.json`, load if valid

Import types from `../../shared/types` and parser from `../../shared/storyboard-parser`.

Session persistence writes to:
- `{projectDir}/.bee-video/session.json`
- `~/.bee-video/last-session.json`

- [ ] **Step 4: Implement Express entry point**

Create `web/server/index.ts`:

```ts
import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = parseInt(process.env.PORT || '8420');

const origins = (process.env.CORS_ORIGINS || '*').split(',');
app.use(cors({ origin: origins }));
app.use(express.json());

// Routes will be added in later tasks
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

// Error handler — { detail: "..." } format
app.use((err: any, req: any, res: any, _next: any) => {
  const status = err.status || 500;
  res.status(status).json({ detail: err.message || 'Internal server error' });
});

// Static frontend (production mode)
const staticDir = process.env.STATIC_DIR || path.join(__dirname, '../dist');
app.use(express.static(staticDir));
// SPA catch-all — serve index.html for non-API routes
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(staticDir, 'index.html'));
  }
});

app.listen(PORT, () => console.log(`Bee Video Editor — http://localhost:${PORT}`));

export { app };
```

- [ ] **Step 5: Verify server starts**

```bash
cd web && npx tsx server/index.ts &
sleep 2 && curl -s http://localhost:8420/api/health
kill %1
```

Expected: `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git add web/server/index.ts web/server/tsconfig.json web/server/services/project-store.ts web/package.json web/package-lock.json
git commit -m "feat: Express server skeleton with ProjectStore"
```

---

### Task 3: ProjectStore tests

**Files:**
- Create: `web/server/__tests__/project-store.test.ts`

- [ ] **Step 1: Write ProjectStore unit tests**

Test with temp directories and inline markdown strings:

- `loadFromMarkdown` — parses markdown, writes `.bee-project.json`, returns BeeProject
- `get()` throws when no project loaded
- `assignMedia` — updates visual/audio/music src correctly
- `updateSegment` — applies visual_updates (color, kenBurns, trim), audio_updates (volume), transition_in
- `reorderSegments` — reorders segments array
- `save` — updates `updatedAt` timestamp
- `loadFromJson` — reads existing `.bee-project.json`
- Session persistence — writes session.json files

- [ ] **Step 2: Run tests — expect PASS**

```bash
cd web && npx vitest run server/__tests__/project-store.test.ts
```

- [ ] **Step 3: Commit**

```bash
git add web/server/__tests__/project-store.test.ts
git commit -m "test: ProjectStore unit tests"
```

---

### Task 4: Media utilities

**Files:**
- Create: `web/server/lib/media-utils.ts`

- [ ] **Step 1: Implement media-utils**

Functions:
- `listMediaFiles(projectDir)` — scan category directories (`footage/`, `stock/`, `photos/`, `graphics/`, `narration/`, `maps/`, `music/`, `output/segments/`, `generated/`), return `{ files: MediaFile[], categories: Record<string, number> }`
- `validatePath(filePath, projectDir)` — resolve both paths, check filePath starts with projectDir (prevent path traversal)
- `sanitizeFilename(name)` — reject hidden files (`.`), path separators, `..`; return cleaned name
- `categorizeFile(ext)` — map extension to `'video' | 'audio' | 'image'`

Import `MediaFile` from `../../shared/types`.

- [ ] **Step 2: Commit**

```bash
git add web/server/lib/media-utils.ts
git commit -m "feat: media utilities (file scan, path validation, categorize)"
```

---

### Task 5: Project routes

**Files:**
- Create: `web/server/routes/projects.ts`
- Modify: `web/server/index.ts`

- [ ] **Step 1: Implement project routes**

7 routes on an Express Router:

- `POST /load` — body: `{ storyboard_path, project_dir }`. Call `store.loadFromMarkdown()`. Return the BeeProject.
- `GET /current` — call `store.get()`. Return the BeeProject.
- `PUT /assign` — body: `{ segment_id, layer, media_path, layer_index }`. Call `store.assignMedia()`. Return `{ status: "ok" }`.
- `PUT /update-segment` — body: `{ segment_id, updates }`. Call `store.updateSegment()`. Return `{ status: "ok" }`.
- `PUT /reorder` — body: `{ segment_order }`. Call `store.reorderSegments()`. Return `{ status: "ok", count }`.
- `GET /export` — query: `format=md|json`. For `md`: call `exportToMarkdown(store.get())` and return `{ format: "md", content }`. For `json`: return `{ format: "json", content: JSON.stringify(store.get()) }`.
- `POST /download-entry` — return `501` with `{ detail: "Not yet migrated — Step 6" }`.
- `POST /auto-assign` — return `501` with `{ detail: "Not yet migrated — Step 6" }`.
- `POST /acquire-media` — return `501` with `{ detail: "Not yet migrated — Step 6" }`.

Implement `exportToMarkdown()` inline or as a helper — inverse of the parser:
- Output `bee-video:project` block
- Group segments by section, output `## Section` headers
- Output `### id | title` + `bee-video:segment` block for each segment

- [ ] **Step 2: Register routes in index.ts**

Add `app.use('/api/projects', projectRoutes)` to `web/server/index.ts`.

- [ ] **Step 3: Commit**

```bash
git add web/server/routes/projects.ts web/server/index.ts
git commit -m "feat: project routes (load, current, assign, update, reorder, export)"
```

---

### Task 6: Media routes

**Files:**
- Create: `web/server/routes/media.ts`
- Modify: `web/server/index.ts`

- [ ] **Step 1: Implement media routes**

3 real routes + stubs on an Express Router:

- `GET /` (list) — call `listMediaFiles(store.getProjectDir())`. Return `{ files, categories }`.
- `POST /upload` — use `multer` for file upload. Query param `category` (default `footage`). Validate category. Sanitize filename. Save to `{projectDir}/{category}/{filename}`. Return `{ status: "ok", path: relative, type: categorizeFile(ext) }`. Note: duration probe is Step 4 (FFmpeg utils) — skip for now, return `duration: null`.
- `GET /file` — query: `path=relative/path`. Validate path is within projectDir. Send file with `res.sendFile()`.
- `POST /stock/search` — return `501`.
- `POST /stock/download` — return `501`.
- `GET /download/scripts` — return `501`.
- `GET /download/tools` — return `501`.
- `POST /download/run-script` — return `501`.
- `POST /download/yt-dlp` — return `501`.
- `GET /download/status` — return `501`.
- `POST /download/create-dirs` — return `501`.
- `POST /generate-clip` — return `501`.

- [ ] **Step 2: Register routes in index.ts**

Add `app.use('/api/media', mediaRoutes)`.

- [ ] **Step 3: Commit**

```bash
git add web/server/routes/media.ts web/server/index.ts
git commit -m "feat: media routes (list, upload, serve file)"
```

---

### Task 7: Production routes

**Files:**
- Create: `web/server/routes/production.ts`
- Modify: `web/server/index.ts`

- [ ] **Step 1: Implement production routes**

Real routes:
- `GET /effects` — return static JSON: `{ color_presets: [...], transitions: [...], ken_burns: [...] }`. Copy the preset lists from the Python backend's effects endpoint.
- `GET /status` — scan `output/` subdirs in projectDir, count files by category. Return `{ phase: "ready", segments_total, segments_done, narration_files, graphics_files, trimmed_files }`.
- `GET /preflight` — read project JSON, check each segment's `visual[0].src`. Return `{ total, found, missing, needs_check: 0 }`.
- `POST /render-remotion` — write `store.get()` to a temp JSON file. Resolve render script path: `path.resolve(__dirname, '../../render.mjs')`. Run `execFile('node', [renderScript, jsonPath, outputPath])` with 10 min timeout. Return `{ status: "ok", output: outputPath, size_bytes }`.

Stubs (return success):
- `POST /init` — `{ status: "ok" }`
- `POST /graphics` — `{ status: "ok", count: 0 }`
- `POST /composite` — `{ status: "ok", succeeded: 0, failed: 0, skipped: 0, errors: [] }`
- `POST /assemble` — `{ status: "ok" }`
- `POST /captions` — `{ status: "ok" }`
- `POST /rough-cut` — `{ status: "ok" }`

501 stubs:
- `POST /narration` — `501`
- `GET /narration/status` — `501`
- `PUT /voice-lock` — `501`
- `GET /voice-lock` — `501`
- `POST /produce` — `501`
- `POST /preview/:segmentId` — `501`
- `POST /previews` — `501`
- `POST /export/otio` — `501`
- `POST /graphics-batch` — `501`

- [ ] **Step 2: Register routes in index.ts**

Add `app.use('/api/production', productionRoutes)`.

- [ ] **Step 3: Commit**

```bash
git add web/server/routes/production.ts web/server/index.ts
git commit -m "feat: production routes (effects, status, preflight, render, stubs)"
```

---

### Task 8: Route integration tests

**Files:**
- Create: `web/server/__tests__/routes.test.ts`

- [ ] **Step 1: Write route integration tests**

Using vitest + supertest against the Express `app` (imported from `server/index.ts`):

Project routes:
- POST `/api/projects/load` with markdown storyboard → returns BeeProject with segments
- GET `/api/projects/current` → returns loaded project
- PUT `/api/projects/assign` → updates segment src
- PUT `/api/projects/update-segment` → updates color/transition
- PUT `/api/projects/reorder` → reorders segments
- GET `/api/projects/export?format=md` → returns markdown string
- GET `/api/projects/export?format=json` → returns JSON
- POST `/api/projects/download-entry` → returns 501

Media routes:
- GET `/api/media` → returns file list
- POST `/api/media/upload` → uploads file to category dir
- GET `/api/media/file?path=...` → serves file
- GET `/api/media/file?path=../../etc/passwd` → returns 403 (path traversal)
- POST `/api/media/stock/search` → returns 501

Production routes:
- GET `/api/production/effects` → returns preset lists
- POST `/api/production/init` → returns `{ status: "ok" }`
- POST `/api/production/narration` → returns 501

Error handling:
- GET `/api/projects/current` before load → returns 404 with `{ detail: "..." }`

Use temp directories for project state. Write a small markdown storyboard fixture inline.

- [ ] **Step 2: Run tests**

```bash
cd web && npx vitest run server/__tests__/routes.test.ts
```

- [ ] **Step 3: Commit**

```bash
git add web/server/__tests__/routes.test.ts
git commit -m "test: route integration tests for Express backend"
```

---

### Task 9: Frontend changes

**Files:**
- Modify: `web/src/api/client.ts`
- Modify: `web/src/components/ExportMenu.tsx`
- Modify: `web/src/components/AIPanel.tsx`

- [ ] **Step 1: Update api client**

In `web/src/api/client.ts`:
- Remove `connectProgress()` method (WebSocket — not needed)
- Remove `exportOtio()` method
- Add `exportJson()`:
  ```ts
  exportJson(): Promise<{ format: string; content: string }> {
    return request('/projects/export?format=json');
  }
  ```

- [ ] **Step 2: Update ExportMenu**

In `web/src/components/ExportMenu.tsx`:
- Replace the OTIO export button with a JSON export button
- Change the handler from `api.exportOtio()` to `api.exportJson()`
- Update label from "Export for NLE / Clean OTIO for DaVinci/Premiere" to "Export Project JSON / Download .bee-project.json"
- Trigger browser download of the JSON content as `.bee-project.json`

- [ ] **Step 3: Fix AIPanel bug**

In `web/src/components/AIPanel.tsx`, find calls to `api.updateBeeSegment()` and replace with `api.updateSegment()`. This is a pre-existing bug — the method doesn't exist on the API client.

- [ ] **Step 4: Run frontend tests**

```bash
cd web && npx vitest run 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add web/src/api/client.ts web/src/components/ExportMenu.tsx web/src/components/AIPanel.tsx
git commit -m "feat: update frontend for Node.js backend (JSON export, remove OTIO/WebSocket, fix AIPanel bug)"
```

---

### Task 10: Dev and production scripts

**Files:**
- Create: `web/dev.sh`
- Create: `web/start.sh`
- Modify: `web/package.json`

- [ ] **Step 1: Create `web/dev.sh`**

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"

BACKEND_PORT=${BACKEND_PORT:-8420}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# Kill previous instances
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true

echo "Starting Express backend on :$BACKEND_PORT..."
PORT=$BACKEND_PORT npx tsx watch server/index.ts &

echo "Starting Vite frontend on :$FRONTEND_PORT..."
VITE_API_PORT=$BACKEND_PORT npm run dev
```

- [ ] **Step 2: Create `web/start.sh`**

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"

PORT=${PORT:-8420}

# Build frontend if needed
if [[ "$BUILD" == "1" ]] || [[ ! -d dist ]]; then
  echo "Building frontend..."
  npm run build
fi

echo "Starting Bee Video Editor on :$PORT..."
STATIC_DIR=dist PORT=$PORT npx tsx server/index.ts
```

- [ ] **Step 3: Make scripts executable**

```bash
chmod +x web/dev.sh web/start.sh
```

- [ ] **Step 4: Add npm scripts**

Add to `web/package.json` scripts:
```json
"server": "tsx server/index.ts",
"server:dev": "tsx watch server/index.ts"
```

- [ ] **Step 5: Test dev startup**

```bash
cd web && PORT=8420 npx tsx server/index.ts &
sleep 2
curl -s http://localhost:8420/api/health
curl -s http://localhost:8420/api/production/effects | head -c 100
kill %1
```

Expected: health check returns ok, effects returns preset lists.

- [ ] **Step 6: Commit**

```bash
git add web/dev.sh web/start.sh web/package.json
git commit -m "feat: dev.sh and start.sh for Node.js backend (no Python)"
```

---

### Task 11: Full integration verification

- [ ] **Step 1: Run all frontend tests**

```bash
cd web && npx vitest run 2>&1 | tail -15
```

Expected: all tests pass (existing 98 + new server tests).

- [ ] **Step 2: Run TypeScript check**

```bash
cd web && npx tsc --noEmit 2>&1 | head -20
```

Expected: clean compile.

- [ ] **Step 3: Manual smoke test**

Start the full stack:
```bash
cd web && ./dev.sh
```

In the browser at http://localhost:5173:
1. Load a storyboard markdown file
2. Click segments, verify timeline renders
3. Assign media to a segment
4. Change color grade in clip properties
5. Check export menu (Markdown + JSON options)
6. Check production dropdown (buttons should not error)
7. Check media library lists files

- [ ] **Step 4: Commit any fixes, then final commit**

```bash
git add -A web/
git commit -m "chore: verify Express backend integration"
```
