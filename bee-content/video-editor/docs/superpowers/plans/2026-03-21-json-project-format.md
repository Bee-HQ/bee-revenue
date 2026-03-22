# JSON Project Format — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace OTIO with a single `.bee-project.json` format — new TypeScript types, markdown parser, and update all components to read the new format.

**Architecture:** Define new types (`BeeProject`, `BeeSegment`, etc.) → build markdown parser → update timeline adapter → update Zustand store → update BeeComposition → update remaining components. Each task produces working, testable code.

**Tech Stack:** TypeScript, vitest, Zustand, Remotion

**Spec:** `docs/superpowers/specs/2026-03-21-json-project-format-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `web/src/types/index.ts` | Rewrite | New BeeProject/BeeSegment types (keep MediaFile, Effects, etc.) |
| `web/src/lib/storyboard-parser.ts` | Create | Markdown → BeeProject JSON conversion |
| `web/src/lib/storyboard-parser.test.ts` | Create | Parser tests |
| `web/src/adapters/timeline-adapter.ts` | Rewrite | Read BeeProject format (seconds, inline src) |
| `web/src/adapters/timeline-adapter.test.ts` | Rewrite | Tests for new adapter |
| `web/src/stores/project.ts` | Modify | `project: BeeProject` replaces `storyboard: Storyboard` |
| `web/src/stores/project-timeline.test.ts` | Modify | Use new types |
| `web/src/components/BeeComposition.tsx` | Modify | Read new field paths |
| `web/src/components/RemotionPreview.tsx` | Modify | Read from `project` |
| `web/src/components/SegmentList.tsx` | Modify | Seconds → display format |
| `web/src/components/ClipProperties.tsx` | Modify | Read new fields |
| `web/src/components/AIPanel.tsx` | Modify | Read new fields |
| `web/src/components/AssetStatusBanner.tsx` | Modify | Check `src` not `assigned_media` |
| `web/src/components/TimelineEditor.tsx` | Modify | Read from `project` |
| `web/src/components/MediaLibrary.tsx` | Minor | No type changes needed |
| `web/src/remotion-entry.tsx` | Modify | New prop types |
| `web/src/App.tsx` | Modify | Read from `project` |
| `web/src/api/client.ts` | Modify | API response type |

---

### Task 1: Define new types

**Files:**
- Rewrite: `web/src/types/index.ts`

- [ ] **Step 1: Replace the old types with new BeeProject types**

Keep `MediaFile`, `MediaListResponse`, `ProductionStatus`, `Effects`, `DownloadScriptInfo`, `DownloadTools`, `DownloadStatus` as-is.

Replace `LayerEntry`, `LayerEntryMetadata`, `Segment`, `Storyboard`, `LayerName` with:

```ts
// --- New BeeProject format ---

export interface VisualEntry {
  type: string;
  src: string | null;
  trim?: [number, number];
  color?: string;
  kenBurns?: string;
  query?: string;
  lat?: number;
  lng?: number;
  [key: string]: any;
}

export interface AudioEntry {
  type: string;
  src: string | null;
  text?: string;
  volume?: number;
}

export interface OverlayEntry {
  type: string;
  content: string;
  startOffset?: number;
  duration?: number;
  platform?: string;
  animation?: string;
  [key: string]: any;
}

export interface MusicEntry {
  type: string;
  src: string | null;
  volume?: number;
}

export interface TransitionEntry {
  type: string;
  duration: number;
}

export interface BeeSegment {
  id: string;
  title: string;
  section: string;
  start: number;
  duration: number;
  visual: VisualEntry[];
  audio: AudioEntry[];
  overlay: OverlayEntry[];
  music: MusicEntry[];
  transition: TransitionEntry | null;
}

export interface ProductionState {
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

export interface RenderRecord {
  id: string;
  timestamp: string;
  format: string;
  resolution: [number, number];
  output: string;
  duration: number;
}

export interface BeeProject {
  version: number;
  title: string;
  fps: number;
  resolution: [number, number];
  createdAt: string;
  updatedAt: string;
  segments: BeeSegment[];
  production: ProductionState;
}

// --- Legacy type alias for gradual migration ---
// Components can import BeeSegment as Segment during migration
export type Segment = BeeSegment;
export type Storyboard = BeeProject;
```

The legacy aliases at the bottom let us migrate component-by-component without breaking everything at once.

- [ ] **Step 2: Verify TypeScript compiles (expect errors from components using old fields)**

```bash
npx tsc --noEmit 2>&1 | head -30
```

- [ ] **Step 3: Commit**

```bash
git add web/src/types/index.ts
git commit -m "feat: define BeeProject JSON format types"
```

---

### Task 2: Build markdown parser

**Files:**
- Create: `web/src/lib/storyboard-parser.ts`
- Create: `web/src/lib/storyboard-parser.test.ts`

- [ ] **Step 1: Write parser tests**

Test with a minimal markdown storyboard string containing `bee-video:project` and `bee-video:segment` code blocks. Verify:
- Project-level fields (title, fps, resolution) parsed
- Segments converted with times in seconds
- Visual entries have `src`, `color`, `kenBurns` as top-level fields
- Audio entries have `type`, `text`, `src`
- Overlay entries have `type`, `content`
- Transition parsed as object or null
- Empty storyboard produces valid BeeProject with empty segments
- Visual type normalization (BROLL-DARK → STOCK)

- [ ] **Step 2: Run tests — expect FAIL**

- [ ] **Step 3: Implement parser**

The parser should:
1. Extract `bee-video:project` JSON block → project config
2. Extract `bee-video:segment` JSON blocks → raw segment data
3. For each segment, read the existing storyboard format (which has `visual: [{type, src, trim}]` already close to our new format)
4. Convert any timecode strings to seconds using `parseTimecode()`
5. Normalize visual type codes using `VISUAL_TYPE_MAP`
6. Build `BeeProject` with default `production` block

Import reusable utilities from `adapters/time-utils.ts` and the `VISUAL_TYPE_MAP` from `adapters/timeline-adapter.ts` (or extract the map to a shared location).

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add web/src/lib/storyboard-parser.ts web/src/lib/storyboard-parser.test.ts
git commit -m "feat: markdown → BeeProject JSON parser"
```

---

### Task 3: Update timeline adapter

**Files:**
- Rewrite: `web/src/adapters/timeline-adapter.ts`
- Rewrite: `web/src/adapters/timeline-adapter.test.ts`

- [ ] **Step 1: Write new tests using BeeProject types**

Replace mock data to use `BeeSegment` (seconds-based `start`/`duration`, inline `src`, object `transition`). Test that:
- `projectToTimeline()` produces correct TimelineRow[] from BeeProject
- Times are passed through (already seconds)
- `timelineToProject()` maps changed `src` back
- Dynamic tracks still work

- [ ] **Step 2: Run tests — expect FAIL**

- [ ] **Step 3: Rewrite adapter**

Key changes:
- `storyboardToTimeline` → `projectToTimeline` — reads `seg.start` directly (no `parseTimecode`), reads `seg.visual[0].src` (no `assigned_media` lookup)
- `timelineToStoryboard` → `timelineToProject` — writes `src` directly on entries
- Remove `parseTimecode` import (no longer needed)
- Keep `VISUAL_TYPE_MAP`, `normalizeVisualType`, `cleanPath` (still useful for display)

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add web/src/adapters/timeline-adapter.ts web/src/adapters/timeline-adapter.test.ts
git commit -m "feat: timeline adapter reads BeeProject format"
```

---

### Task 4: Update Zustand store

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/stores/project-timeline.test.ts`

- [ ] **Step 1: Update store**

- Replace `storyboard: Storyboard | null` with `project: BeeProject | null`
- Update `loadProject()` to use the new parser or accept JSON directly
- Update `assignMedia()` to set `src` directly on visual/audio entries instead of `assigned_media` map
- Update `loadAssetStatus()` to check `seg.visual[0].src` instead of `assigned_media`
- Remove `assigned_media`-specific logic
- Keep all timeline features (undo/redo, split, multi-select, etc.)

- [ ] **Step 2: Update store tests**

Fix test mock data to use `BeeSegment` format.

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

```bash
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts
git commit -m "feat: Zustand store uses BeeProject format"
```

---

### Task 5: Update BeeComposition

**Files:**
- Modify: `web/src/components/BeeComposition.tsx`
- Modify: `web/src/remotion-entry.tsx`

- [ ] **Step 1: Update field reads**

Replace throughout:
- `seg.assigned_media['visual:0']` → `seg.visual[0]?.src`
- `seg.visual[0]?.metadata?.color` → `seg.visual[0]?.color`
- `seg.visual[0]?.metadata?.ken_burns` → `seg.visual[0]?.kenBurns`
- `parseTimecode(seg.start)` → `seg.start`
- `seg.duration_seconds` → `seg.duration`
- `seg.audio.find(a => a.content_type === 'NAR')` → `seg.audio.find(a => a.type === 'NAR')`
- `entry.content_type` → `entry.type` in overlay dispatch
- `entry.metadata` fields → top-level fields on entry
- `storyboard.total_duration_seconds` → compute from segments or `project` prop

Update `remotion-entry.tsx` defaultProps to use `BeeProject` type.

- [ ] **Step 2: Verify build**

- [ ] **Step 3: Commit**

```bash
git add web/src/components/BeeComposition.tsx web/src/remotion-entry.tsx
git commit -m "feat: BeeComposition reads BeeProject format"
```

---

### Task 6: Update remaining components

**Files:**
- Modify: `web/src/components/RemotionPreview.tsx`
- Modify: `web/src/components/SegmentList.tsx`
- Modify: `web/src/components/ClipProperties.tsx`
- Modify: `web/src/components/AIPanel.tsx`
- Modify: `web/src/components/AssetStatusBanner.tsx`
- Modify: `web/src/components/TimelineEditor.tsx`
- Modify: `web/src/components/Layout.tsx`
- Modify: `web/src/App.tsx`
- Modify: `web/src/api/client.ts`

- [ ] **Step 1: Update all components**

Mechanical changes across all files:
- `useProjectStore(s => s.storyboard)` → `useProjectStore(s => s.project)`
- `storyboard.segments` → `project.segments`
- `storyboard.total_segments` → `project.segments.length`
- `storyboard.total_duration_seconds` → sum of `project.segments` durations
- `seg.duration_seconds` → `seg.duration`
- `seg.start` (was timecode string, now number) — format for display: `formatSeconds(seg.start)`
- `seg.end` → `seg.start + seg.duration` (computed)
- `seg.assigned_media` → removed, use `seg.visual[0].src` etc.
- `seg.visual[0].content_type` → `seg.visual[0].type`
- `seg.visual[0].content` → `seg.visual[0].src` or specific field
- `seg.audio[0].content_type` → `seg.audio[0].type`
- `seg.overlay[0].content_type` → `seg.overlay[0].type`

Add helper function in `adapters/time-utils.ts`:
```ts
export function formatSeconds(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

- [ ] **Step 2: Update API client types**

`api.getCurrentProject()` returns `BeeProject` instead of `Storyboard`. Update the `client.ts` type annotations.

- [ ] **Step 3: Build and run all tests**

```bash
npm run build 2>&1 | tail -10
npx vitest run 2>&1 | tail -10
```

- [ ] **Step 4: Commit**

```bash
git add -A web/src/
git commit -m "feat: all components migrated to BeeProject format"
```

---

### Task 7: Backend bridge (Python serves new format)

**Files:**
- Modify: `src/bee_video_editor/api/routes/projects.py`

- [ ] **Step 1: Update `GET /api/projects/current` to return BeeProject JSON**

The Python backend currently returns `ParsedStoryboard` serialized as JSON. Add a conversion function that transforms it to the new `BeeProject` format:
- Timecodes → seconds
- `assigned_media` → inline `src` on entries
- `LayerEntry.content_type` → `type`
- `LayerEntry.metadata.color` → top-level `color`
- Add default `production` block

This is a temporary bridge until the Python backend is fully replaced.

- [ ] **Step 2: Update `POST /api/projects/load` to accept .md and return BeeProject**

The route already parses markdown via Python. Update the response to use the new format.

- [ ] **Step 3: Run backend tests**

```bash
uv run --extra dev pytest tests/test_api.py -v --tb=short
```

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/api/routes/projects.py
git commit -m "feat: backend serves BeeProject JSON format"
```

---

### Task 8: Remove legacy type aliases and verify

- [ ] **Step 1: Remove `Segment` and `Storyboard` aliases from types/index.ts**

If all components are migrated, the aliases are dead code. Remove:
```ts
export type Segment = BeeSegment;
export type Storyboard = BeeProject;
```

- [ ] **Step 2: Full build and test**

```bash
npm run build 2>&1 | tail -10
npx vitest run 2>&1 | tail -10
uv run --extra dev pytest tests/ -x --tb=short -q
```

- [ ] **Step 3: Smoke test**

Start dev server, load a project, verify:
1. Timeline renders clips
2. Preview plays
3. Overlays animate
4. Segment list shows times
5. Clip properties work

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove legacy Storyboard/Segment type aliases"
```
