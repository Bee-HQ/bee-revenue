# Replace DesignCombo with react-timeline-editor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace DesignCombo's canvas-based timeline with `react-timeline-editor`, a DOM-based React timeline component — eliminating Fabric.js crashes and adding drag-drop/paste media input.

**Architecture:** Rewrite `timeline-adapter.ts` to output `TimelineRow[]` (seconds-based) instead of `DCState` (ms-based). Rewrite `TimelineEditor.tsx` as a pure React component using `<Timeline>` from the library. Add unified undo/redo, split, and drag-drop/paste to Zustand store. Keep Remotion Player and all backend code unchanged (except extending the upload route response).

**Tech Stack:** React 19, `@xzdarcy/react-timeline-editor`, Zustand, Remotion, Vite, vitest, Python/FastAPI backend

**Spec:** `docs/superpowers/specs/2026-03-21-react-timeline-editor-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `web/src/adapters/timeline-adapter.ts` | Rewrite | Convert `Storyboard` ↔ `TimelineRow[]` (seconds) |
| `web/src/adapters/timeline-adapter.test.ts` | Rewrite | Tests for new adapter functions |
| `web/src/components/TimelineEditor.tsx` | Rewrite | `<Timeline>` integration, toolbar, track labels |
| `web/src/components/TimelineRuler.tsx` | Delete | Library has built-in ruler |
| `web/src/components/TimelineActionRenderer.tsx` | Create | Custom colored action bars per track type |
| `web/src/stores/project.ts` | Modify | Add `editorData`, timeline undo/redo, `splitAtPlayhead` |
| `web/src/App.tsx` | Modify | Remove `dcDispatch`, wire keyboard shortcuts to Zustand |
| `web/src/components/MediaLibrary.tsx` | Modify | Add `dataTransfer.setData('bee/media', ...)` on drag |
| `web/src/SPIKE-NOTES.md` | Delete | Stale DesignCombo docs |
| `web/package.json` | Modify | Remove 4 DesignCombo deps, add react-timeline-editor |
| `src/bee_video_editor/api/routes/media.py` | Modify | Extend upload response with `type` + `duration` |

---

### Task 1: Install react-timeline-editor, remove DesignCombo

**Files:**
- Modify: `web/package.json`

- [ ] **Step 1: Uninstall DesignCombo packages**

```bash
cd bee-content/video-editor/web
npm uninstall @designcombo/state @designcombo/timeline @designcombo/types @designcombo/events
```

- [ ] **Step 2: Install react-timeline-editor**

```bash
npm install @xzdarcy/react-timeline-editor
```

- [ ] **Step 3: Verify install**

```bash
ls node_modules/@xzdarcy/react-timeline-editor/package.json && echo "OK"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add web/package.json web/package-lock.json
git commit -m "chore: replace DesignCombo deps with react-timeline-editor"
```

---

### Task 2: Rewrite timeline adapter

**Files:**
- Rewrite: `web/src/adapters/timeline-adapter.ts`
- Rewrite: `web/src/adapters/timeline-adapter.test.ts`

- [ ] **Step 1: Write the failing tests**

Replace `web/src/adapters/timeline-adapter.test.ts` with:

```ts
import { describe, test, expect } from 'vitest';
import { storyboardToTimeline, timelineToStoryboard } from './timeline-adapter';
import type { Storyboard, Segment } from '../types';
import type { TimelineRow } from '@xzdarcy/react-timeline-editor';

const mockSegment: Segment = {
  id: 'cold-open',
  start: '0:00',
  end: '0:15',
  title: 'Cold Open',
  section: 'Act 1',
  section_time: '',
  subsection: '',
  duration_seconds: 15,
  visual: [
    { content: 'footage/clip.mp4', content_type: 'FOOTAGE', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  audio: [
    { content: 'narration text', content_type: 'NAR', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  overlay: [
    { content: 'Colleton County', content_type: 'LOWER_THIRD', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  music: [
    { content: 'music/bg.mp3', content_type: 'MUSIC', time_start: null, time_end: null, raw: '', metadata: { volume: 0.2 } },
  ],
  source: [],
  transition: [],
  assigned_media: { 'visual:0': 'footage/clip.mp4' },
};

const mockStoryboard: Storyboard = {
  title: 'Test',
  total_segments: 1,
  total_duration_seconds: 15,
  sections: ['Act 1'],
  segments: [mockSegment],
  stock_footage_needed: 0,
  photos_needed: 0,
  maps_needed: 0,
  production_rules: [],
};

describe('storyboardToTimeline', () => {
  test('creates dynamic rows — only tracks with content', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    // V1 (visual), A1 (nar), A3 (music), OV1 (overlay) — no A2 since no real audio
    const ids = rows.map(r => r.id);
    expect(ids).toContain('V1');
    expect(ids).toContain('A1');
    expect(ids).toContain('A3');
    expect(ids).toContain('OV1');
    expect(ids).not.toContain('A2');
  });

  test('V1 always present even with empty storyboard', () => {
    const empty = { ...mockStoryboard, segments: [], total_segments: 0, total_duration_seconds: 0 };
    const { rows } = storyboardToTimeline(empty);
    expect(rows.some(r => r.id === 'V1')).toBe(true);
  });

  test('times are in seconds (not ms)', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    const action = v1.actions[0];
    expect(action.start).toBe(0);
    expect(action.end).toBe(15); // 15 seconds, not 15000ms
  });

  test('actions have correct effectId per track', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions[0].effectId).toBe('video');
    const a1 = rows.find(r => r.id === 'A1')!;
    expect(a1.actions[0].effectId).toBe('narration');
  });

  test('actions carry segment metadata in data field', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    const data = (v1.actions[0] as any).data;
    expect(data.segmentId).toBe('cold-open');
    expect(data.contentType).toBe('FOOTAGE');
    expect(data.src).toBe('footage/clip.mp4');
  });

  test('returns effects map', () => {
    const { effects } = storyboardToTimeline(mockStoryboard);
    expect(effects.video).toBeDefined();
    expect(effects.narration).toBeDefined();
    expect(effects.overlay).toBeDefined();
  });

  test('creates placeholder for segment with no visuals', () => {
    const noVisual = { ...mockSegment, visual: [], assigned_media: {} };
    const sb = { ...mockStoryboard, segments: [noVisual] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions.length).toBe(1);
    expect((v1.actions[0] as any).data.empty).toBe(true);
  });

  test('normalizes formula codes to base types', () => {
    const brollSeg = {
      ...mockSegment,
      visual: [{ content: '', content_type: 'BROLL-DARK', time_start: null, time_end: null, raw: '', metadata: null }],
    };
    const sb = { ...mockStoryboard, segments: [brollSeg] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect((v1.actions[0] as any).data.contentType).toBe('STOCK');
  });
});

describe('timelineToStoryboard', () => {
  test('preserves segment count and metadata', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const result = timelineToStoryboard(rows, mockStoryboard);
    expect(result.segments.length).toBe(1);
    expect(result.title).toBe('Test');
  });

  test('maps changed src back to assigned_media', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    (v1.actions[0] as any).data.src = 'footage/new-clip.mp4';
    const result = timelineToStoryboard(rows, mockStoryboard);
    expect(result.segments[0].assigned_media['visual:0']).toBe('footage/new-clip.mp4');
  });

  test('round-trips timecodes through seconds conversion', () => {
    // A segment at 1:30 to 2:00 should survive the seconds round-trip
    const seg = { ...mockSegment, id: 'mid', start: '1:30', end: '2:00', duration_seconds: 30 };
    const sb = { ...mockStoryboard, segments: [seg] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    // Verify seconds values
    expect(v1.actions[0].start).toBe(90);  // 1:30 = 90s
    expect(v1.actions[0].end).toBe(120);   // 2:00 = 120s
    // Round-trip back
    const result = timelineToStoryboard(rows, sb);
    expect(result.segments[0].start).toBe('1:30');
    expect(result.segments[0].end).toBe('2:00');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd bee-content/video-editor/web && npx vitest run src/adapters/timeline-adapter.test.ts 2>&1 | tail -5
```
Expected: FAIL — `storyboardToTimeline` is not exported

- [ ] **Step 3: Write the adapter implementation**

Replace `web/src/adapters/timeline-adapter.ts` with the new adapter that:
- Exports `storyboardToTimeline(storyboard)` returning `{ rows: TimelineRow[], effects }` with times in seconds
- Exports `timelineToStoryboard(rows, original)` returning updated `Storyboard`
- Keeps `VISUAL_TYPE_MAP`, `normalizeVisualType`, `cleanPath`, `normalizeAudioType` from current file
- Creates dynamic rows (only tracks with content, V1 always present)
- Uses `BeeTimelineAction` interface extending `TimelineAction` with `data` field
- Transition actions use `flexible: false` and `effectId: 'transition'`

Key structure:
```ts
import type { TimelineRow, TimelineAction, TimelineEffect } from '@xzdarcy/react-timeline-editor';
import type { Storyboard, Segment, LayerEntry } from '../types';
import { parseTimecode, timeToMs } from './time-utils';

export interface BeeActionData {
  segmentId: string;
  contentType: string;
  src: string;
  title: string;
  layerIndex: number;
  formulaCode?: string;
  empty?: boolean;
  // transition-specific
  type?: string;
  duration?: number;
  fromSegId?: string;
  toSegId?: string;
}

export interface BeeTimelineAction extends TimelineAction {
  data: BeeActionData;
}

const EFFECTS: Record<string, TimelineEffect> = {
  video:      { id: 'video',      name: 'Video' },
  narration:  { id: 'narration',  name: 'Narration' },
  audio:      { id: 'audio',      name: 'Audio' },
  music:      { id: 'music',      name: 'Music' },
  overlay:    { id: 'overlay',    name: 'Overlay' },
  transition: { id: 'transition', name: 'Transition' },
};

// ... VISUAL_TYPE_MAP, normalizeVisualType, cleanPath, normalizeAudioType (keep from current)

export function storyboardToTimeline(storyboard: Storyboard): { rows: TimelineRow[]; effects: Record<string, TimelineEffect> } {
  // Build track buckets: V1, A1, A2, A3, OV1
  // For each segment, create actions with times in seconds (timeToMs(parseTimecode(seg.start)) / 1000)
  // Only return rows that have actions (except V1 which is always included)
  // Return { rows, effects: EFFECTS }
}

export function timelineToStoryboard(rows: TimelineRow[], original: Storyboard): Storyboard {
  // For each action's data.segmentId + data.src, update original's assigned_media
  // Return updated storyboard copy
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd bee-content/video-editor/web && npx vitest run src/adapters/timeline-adapter.test.ts 2>&1 | tail -10
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/adapters/timeline-adapter.ts web/src/adapters/timeline-adapter.test.ts
git commit -m "feat: rewrite timeline adapter for react-timeline-editor"
```

---

### Task 3: Add timeline state and undo/redo to Zustand store

**Files:**
- Modify: `web/src/stores/project.ts`

- [ ] **Step 1: Add timeline state fields and actions to the store**

Add to `ProjectState` interface (after `assetStatus`):
```ts
editorData: TimelineRow[];
timelineHistory: TimelineRow[][];
timelineHistoryIndex: number;

setEditorData: (data: TimelineRow[]) => void;
pushTimelineHistory: (data: TimelineRow[]) => void;
timelineUndo: () => void;
timelineRedo: () => void;
splitAtPlayhead: () => void;
```

Add to store initial values:
```ts
editorData: [],
timelineHistory: [],
timelineHistoryIndex: -1,
```

Implement `setEditorData`:
```ts
setEditorData: (data) => set({ editorData: data }),
```

Implement `pushTimelineHistory`:
```ts
pushTimelineHistory: (data) => {
  const { timelineHistory, timelineHistoryIndex } = get();
  // Truncate any future history (user made new change after undo)
  const truncated = timelineHistory.slice(0, timelineHistoryIndex + 1);
  const next = [...truncated, structuredClone(data)];
  if (next.length > MAX_HISTORY) next.shift();
  set({ timelineHistory: next, timelineHistoryIndex: next.length - 1 });
},
```

Implement `timelineUndo`:
```ts
timelineUndo: () => {
  const { timelineHistory, timelineHistoryIndex } = get();
  if (timelineHistoryIndex <= 0) return;
  const newIndex = timelineHistoryIndex - 1;
  set({ editorData: structuredClone(timelineHistory[newIndex]), timelineHistoryIndex: newIndex });
},
```

Implement `timelineRedo`:
```ts
timelineRedo: () => {
  const { timelineHistory, timelineHistoryIndex } = get();
  if (timelineHistoryIndex >= timelineHistory.length - 1) return;
  const newIndex = timelineHistoryIndex + 1;
  set({ editorData: structuredClone(timelineHistory[newIndex]), timelineHistoryIndex: newIndex });
},
```

Implement `splitAtPlayhead`:
```ts
splitAtPlayhead: () => {
  const { editorData, currentTimeMs, activeClipId } = get();
  const cursorSec = currentTimeMs / 1000;
  // Find action under cursor — prefer active clip's row, fall back to V1
  let targetRow = editorData.find(r => r.id === 'V1');
  if (activeClipId) {
    for (const row of editorData) {
      if (row.actions.some(a => a.id === activeClipId)) {
        targetRow = row;
        break;
      }
    }
  }
  if (!targetRow) return;
  const actionIdx = targetRow.actions.findIndex(a => a.start < cursorSec && a.end > cursorSec);
  if (actionIdx === -1) return;
  const action = targetRow.actions[actionIdx] as any;
  const left = { ...action, id: action.id + '-L', end: cursorSec, data: { ...action.data } };
  const right = { ...action, id: action.id + '-R', start: cursorSec, data: { ...action.data } };
  const newActions = [...targetRow.actions];
  newActions.splice(actionIdx, 1, left, right);
  const newRows = editorData.map(r => r.id === targetRow!.id ? { ...r, actions: newActions } : r);
  get().setEditorData(newRows);
  get().pushTimelineHistory(newRows);
},
```

**What to remove:** `HistoryEntry` interface, `applyAssignment()` helper, `undoStack` field + initial value, `redoStack` field + initial value, `undo()` method, `redo()` method. In `assignMedia`, remove the undo stack push logic (lines 291-301: `const entry...`, `const newStack...`, `set({ ...undoStack...redoStack... })`) — keep just the API call and storyboard update.

**What to keep (do NOT remove):** `currentTimeMs`, `setCurrentTimeMs`, `activeClipId`, `setActiveClipId`, `loopIn`, `loopOut`, `playerRef`, `assignMedia` (minus undo logic), `assignMediaBatch`, and all other existing fields/methods.

**Update `loadProject`:** Replace the existing `undoStack: [], redoStack: []` reset (lines 133-134) with:
```ts
editorData: [],
timelineHistory: [],
timelineHistoryIndex: -1,
```

- [ ] **Step 2: Add `TimelineRow` import**

At top of file:
```ts
import type { TimelineRow } from '@xzdarcy/react-timeline-editor';
```

- [ ] **Step 3: Write store tests**

Create `web/src/stores/project-timeline.test.ts`:

```ts
import { describe, test, expect, beforeEach } from 'vitest';
import { useProjectStore } from './project';
import type { TimelineRow } from '@xzdarcy/react-timeline-editor';

const makeRows = (id: string): TimelineRow[] => [
  { id: 'V1', actions: [{ id, start: 0, end: 5, effectId: 'video' }] },
];

describe('timeline undo/redo', () => {
  beforeEach(() => {
    useProjectStore.setState({
      editorData: [],
      timelineHistory: [],
      timelineHistoryIndex: -1,
    });
  });

  test('pushTimelineHistory adds snapshot', () => {
    const rows = makeRows('a1');
    useProjectStore.getState().pushTimelineHistory(rows);
    expect(useProjectStore.getState().timelineHistory).toHaveLength(1);
    expect(useProjectStore.getState().timelineHistoryIndex).toBe(0);
  });

  test('undo reverts to previous state', () => {
    const rows1 = makeRows('a1');
    const rows2 = makeRows('a2');
    const store = useProjectStore.getState();
    store.pushTimelineHistory(rows1);
    store.setEditorData(rows1);
    store.pushTimelineHistory(rows2);
    store.setEditorData(rows2);

    useProjectStore.getState().timelineUndo();
    expect(useProjectStore.getState().editorData[0].actions[0].id).toBe('a1');
  });

  test('redo restores undone state', () => {
    const rows1 = makeRows('a1');
    const rows2 = makeRows('a2');
    const store = useProjectStore.getState();
    store.pushTimelineHistory(rows1);
    store.pushTimelineHistory(rows2);
    store.setEditorData(rows2);

    useProjectStore.getState().timelineUndo();
    useProjectStore.getState().timelineRedo();
    expect(useProjectStore.getState().editorData[0].actions[0].id).toBe('a2');
  });

  test('undo at start of history does nothing', () => {
    useProjectStore.getState().timelineUndo();
    expect(useProjectStore.getState().timelineHistoryIndex).toBe(-1);
  });

  test('new change after undo truncates redo history', () => {
    const store = useProjectStore.getState();
    store.pushTimelineHistory(makeRows('a1'));
    store.pushTimelineHistory(makeRows('a2'));
    store.pushTimelineHistory(makeRows('a3'));
    useProjectStore.getState().timelineUndo();
    useProjectStore.getState().timelineUndo();
    // Now at a1, push new
    useProjectStore.getState().pushTimelineHistory(makeRows('a4'));
    expect(useProjectStore.getState().timelineHistory).toHaveLength(2); // a1, a4
  });

  test('max 50 history entries', () => {
    const store = useProjectStore.getState();
    for (let i = 0; i < 55; i++) {
      store.pushTimelineHistory(makeRows(`a${i}`));
    }
    expect(useProjectStore.getState().timelineHistory).toHaveLength(50);
  });
});

describe('splitAtPlayhead', () => {
  test('splits action at cursor into two halves', () => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [{ id: 'clip1', start: 0, end: 10, effectId: 'video', data: { segmentId: 's1', src: 'a.mp4', title: 'A', contentType: 'FOOTAGE', layerIndex: 0 } } as any] },
    ];
    useProjectStore.setState({
      editorData: rows,
      currentTimeMs: 5000, // 5 seconds
      activeClipId: null,
      timelineHistory: [rows],
      timelineHistoryIndex: 0,
    });
    useProjectStore.getState().splitAtPlayhead();
    const result = useProjectStore.getState().editorData;
    const v1 = result.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(2);
    expect(v1.actions[0].end).toBe(5);
    expect(v1.actions[1].start).toBe(5);
  });
});
```

- [ ] **Step 4: Run store tests**

```bash
cd bee-content/video-editor/web && npx vitest run src/stores/project-timeline.test.ts 2>&1 | tail -10
```
Expected: All tests PASS

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```
Expected: No errors (or only errors from files we haven't updated yet like TimelineEditor.tsx, App.tsx)

- [ ] **Step 6: Commit**

```bash
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts
git commit -m "feat: add timeline undo/redo and split to Zustand store"
```

---

### Task 4: Create custom action renderer

**Files:**
- Create: `web/src/components/TimelineActionRenderer.tsx`

- [ ] **Step 1: Create the renderer component**

```tsx
import type { TimelineAction, TimelineRow } from '@xzdarcy/react-timeline-editor';
import type { BeeTimelineAction } from '../adapters/timeline-adapter';

const TRACK_COLORS: Record<string, { bg: string; border: string }> = {
  video:      { bg: '#a16207', border: '#ca8a04' },
  narration:  { bg: '#166534', border: '#22c55e' },
  audio:      { bg: '#0f766e', border: '#14b8a6' },
  music:      { bg: '#6b21a8', border: '#a855f7' },
  overlay:    { bg: '#9d174d', border: '#f472b6' },
  transition: { bg: 'rgba(255,255,255,0.15)', border: 'rgba(255,255,255,0.3)' },
};

export function renderTimelineAction(action: TimelineAction, _row: TimelineRow) {
  const beeAction = action as BeeTimelineAction;
  const effectId = beeAction.effectId || 'video';
  const colors = TRACK_COLORS[effectId] || TRACK_COLORS.video;
  const data = beeAction.data;

  let label = data?.title || '';
  if (effectId === 'narration') label = `NAR: ${data?.title || ''}`;
  else if (effectId === 'transition') label = data?.type || 'transition';
  else if (effectId === 'overlay') label = `${data?.contentType || ''}: ${data?.title || ''}`;
  else if (effectId === 'music') label = data?.src?.split('/').pop() || 'Music';
  else if (effectId === 'audio') label = data?.contentType || 'Audio';
  else if (data?.src) label = data.src.split('/').pop() || data.title;

  return (
    <div
      style={{
        background: colors.bg,
        borderLeft: `2px solid ${colors.border}`,
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        padding: '0 6px',
        overflow: 'hidden',
        borderRadius: 2,
        cursor: 'pointer',
      }}
    >
      <span style={{ fontSize: 10, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {label}
      </span>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -5
```

- [ ] **Step 3: Commit**

```bash
git add web/src/components/TimelineActionRenderer.tsx
git commit -m "feat: add custom timeline action renderer with track colors"
```

---

### Task 5: Rewrite TimelineEditor component

**Files:**
- Rewrite: `web/src/components/TimelineEditor.tsx`
- Delete: `web/src/components/TimelineRuler.tsx`

- [ ] **Step 1: Delete TimelineRuler.tsx**

```bash
rm bee-content/video-editor/web/src/components/TimelineRuler.tsx
```

- [ ] **Step 2: Rewrite TimelineEditor.tsx**

Replace entire file with new implementation that:
- Imports `Timeline` and `TimelineState` from `@xzdarcy/react-timeline-editor`
- Imports `storyboardToTimeline` from adapter
- Imports `renderTimelineAction` from `TimelineActionRenderer`
- Uses `useProjectStore` for `storyboard`, `editorData`, `setEditorData`, `pushTimelineHistory`, `setActiveClipId`, `setCurrentTimeMs`, `currentTimeMs`
- On storyboard change: converts via adapter, calls `setEditorData` and `pushTimelineHistory`
- `onChange` callback: updates `editorData` in store, pushes to history, debounces backend sync
- `onClickActionOnly`: sets `activeClipId`
- `onClickRow`: clears `activeClipId`
- `onCursorDrag`: live seek — `setCurrentTimeMs(time * 1000)`
- `getActionRender`: delegates to `renderTimelineAction`
- Toolbar: zoom slider (controls `scaleWidth` via `zoomLevel * 40`), snap toggle, undo/redo buttons, split button
- Track labels column on the left showing row IDs (V1, A1, etc.)
- `useEffect` to sync Remotion playback → timeline cursor via `timelineRef.current?.setTime(currentTimeMs / 1000)`
- Wrap timeline container with `onDrop`/`onDragOver` handlers for external file drop
- `onPaste` handler on the container div for Cmd+V

Key structure:
```tsx
import { useEffect, useRef, useCallback, useState } from 'react';
import { Timeline } from '@xzdarcy/react-timeline-editor';
import type { TimelineState, TimelineRow, TimelineAction } from '@xzdarcy/react-timeline-editor';
import { useProjectStore } from '../stores/project';
import { storyboardToTimeline, timelineToStoryboard } from '../adapters/timeline-adapter';
import type { BeeTimelineAction } from '../adapters/timeline-adapter';
import { renderTimelineAction } from './TimelineActionRenderer';
import { ProductionDropdown } from './ProductionDropdown';
import { api } from '../api/client';
import { toast } from '../stores/toast';

export function TimelineEditor() {
  const storyboard = useProjectStore(s => s.storyboard);
  const editorData = useProjectStore(s => s.editorData);
  const setEditorData = useProjectStore(s => s.setEditorData);
  const pushTimelineHistory = useProjectStore(s => s.pushTimelineHistory);
  const setActiveClipId = useProjectStore(s => s.setActiveClipId);
  const setCurrentTimeMs = useProjectStore(s => s.setCurrentTimeMs);
  const currentTimeMs = useProjectStore(s => s.currentTimeMs);
  const timelineRef = useRef<TimelineState>(null);
  const [zoomLevel, setZoomLevel] = useState(5);
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [effects, setEffects] = useState<Record<string, any>>({});
  const syncTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Convert storyboard → timeline rows on storyboard change
  useEffect(() => {
    if (!storyboard) return;
    const { rows, effects: eff } = storyboardToTimeline(storyboard);
    setEditorData(rows);
    setEffects(eff);
    pushTimelineHistory(rows);
  }, [storyboard]);

  // Sync Remotion playback → timeline cursor
  useEffect(() => {
    if (timelineRef.current) {
      timelineRef.current.setTime(currentTimeMs / 1000);
    }
  }, [currentTimeMs]);

  const handleChange = useCallback((newData: TimelineRow[]) => {
    setEditorData(newData);
    pushTimelineHistory(newData);
    // Debounced backend sync
    if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    syncTimeoutRef.current = setTimeout(async () => {
      try {
        const sb = useProjectStore.getState().storyboard;
        if (!sb) return;
        const updated = timelineToStoryboard(newData, sb);
        for (const seg of updated.segments) {
          const original = sb.segments.find(s => s.id === seg.id);
          if (!original) continue;
          for (const [key, path] of Object.entries(seg.assigned_media)) {
            if (original.assigned_media[key] !== path) {
              const [layer, indexStr] = key.split(':');
              await api.assignMedia(seg.id, layer, path, parseInt(indexStr));
            }
          }
        }
        const freshSb = await api.getCurrentProject();
        useProjectStore.setState({ storyboard: freshSb });
      } catch (e) {
        console.error('Timeline sync failed:', e);
      }
    }, 1000);
  }, []);

  const handleCursorDrag = useCallback((time: number) => {
    setCurrentTimeMs(time * 1000);
  }, []);

  const handleCursorDragEnd = useCallback((time: number) => {
    setCurrentTimeMs(time * 1000);
  }, []);

  const handleClickAction = useCallback((_e: any, { action }: { action: TimelineAction }) => {
    setActiveClipId(action.id);
  }, []);

  const handleClickRow = useCallback(() => {
    setActiveClipId(null);
  }, []);

  if (!storyboard) return null;

  return (
    <div
      className="border-t border-editor-border bg-editor-bg flex flex-col shrink-0"
      style={{ height: 180 }}
      tabIndex={0}
    >
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-1 border-b border-editor-border bg-editor-surface shrink-0">
        <ProductionDropdown />
        <div className="flex-1" />
        <button className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={() => useProjectStore.getState().splitAtPlayhead()} title="Split at playhead (S)">Split</button>
        <button className={`text-[10px] px-2 py-1 rounded ${snapEnabled ? 'bg-blue-600/20 text-blue-400' : 'bg-editor-hover text-gray-300'}`}
          onClick={() => setSnapEnabled(!snapEnabled)} title="Toggle snap">Snap</button>
        <input type="range" min="1" max="10" value={zoomLevel}
          onChange={(e) => setZoomLevel(parseInt(e.target.value))}
          className="w-16" style={{ accentColor: '#3b82f6' }} title="Zoom" />
        <button onClick={() => useProjectStore.getState().timelineUndo()}
          className="text-[10px] text-gray-400 hover:text-white px-1" title="Undo">Undo</button>
        <button onClick={() => useProjectStore.getState().timelineRedo()}
          className="text-[10px] text-gray-400 hover:text-white px-1" title="Redo">Redo</button>
      </div>
      {/* Track labels + Timeline */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        <div className="w-12 shrink-0 border-r border-editor-border bg-editor-surface flex flex-col">
          {editorData.map(row => (
            <div key={row.id} className="text-[9px] text-gray-500 font-mono px-1 flex items-center" style={{ height: 28 }}>
              {row.id}
            </div>
          ))}
        </div>
        <div className="flex-1 overflow-hidden">
          <Timeline
            ref={timelineRef}
            editorData={editorData}
            effects={effects}
            onChange={handleChange}
            scale={1}
            scaleWidth={zoomLevel * 40}
            rowHeight={28}
            gridSnap={snapEnabled}
            dragLine={true}
            autoScroll={true}
            getActionRender={renderTimelineAction}
            onClickAction={handleClickAction}
            onClickActionOnly={handleClickAction}
            onClickRow={handleClickRow}
            onCursorDrag={handleCursorDrag}
            onCursorDragEnd={handleCursorDragEnd}
          />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```
Expected: No errors from TimelineEditor.tsx (App.tsx may still have dcDispatch errors)

- [ ] **Step 4: Commit**

```bash
git add web/src/components/TimelineEditor.tsx
git rm web/src/components/TimelineRuler.tsx
git commit -m "feat: rewrite TimelineEditor with react-timeline-editor"
```

---

### Task 6: Update App.tsx — remove DesignCombo, wire new shortcuts

**Files:**
- Modify: `web/src/App.tsx`
- Delete: `web/src/SPIKE-NOTES.md`

- [ ] **Step 1: Remove dcDispatch import and all usages**

Remove:
```ts
import { dispatch as dcDispatch } from '@designcombo/events';
```

Replace the undo/redo keyboard handlers:
```ts
// Old:
dcDispatch('history:undo', { payload: {} });
dcDispatch('history:redo', { payload: {} });
// New:
useProjectStore.getState().timelineUndo();
useProjectStore.getState().timelineRedo();
```

Replace split handler:
```ts
// Old:
dcDispatch('active:split', { payload: { time: currentMs } });
// New:
useProjectStore.getState().splitAtPlayhead();
```

- [ ] **Step 2: Delete SPIKE-NOTES.md**

```bash
rm bee-content/video-editor/web/src/SPIKE-NOTES.md
```

- [ ] **Step 3: Verify full TypeScript build**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```
Expected: Clean — no errors

- [ ] **Step 4: Verify Vite build**

```bash
cd bee-content/video-editor/web && npm run build 2>&1 | tail -10
```
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
git add web/src/App.tsx
git rm web/src/SPIKE-NOTES.md
git commit -m "feat: wire keyboard shortcuts to Zustand, remove DesignCombo events"
```

---

### Task 7: Extend backend upload route

**Files:**
- Modify: `src/bee_video_editor/api/routes/media.py`

- [ ] **Step 1: Add type and duration to upload response**

After line 129 (`shutil.copyfileobj(file.file, f)`), add duration probing:

```python
    # Determine media type from extension
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    VIDEO_EXTS = {"mp4", "mov", "webm", "avi", "mkv"}
    AUDIO_EXTS = {"mp3", "wav", "aac", "m4a", "flac", "ogg"}
    IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "bmp"}

    if ext in VIDEO_EXTS:
        media_type = "video"
    elif ext in AUDIO_EXTS:
        media_type = "audio"
    elif ext in IMAGE_EXTS:
        media_type = "image"
    else:
        media_type = "unknown"

    # Probe duration for video/audio
    duration = None
    if media_type in ("video", "audio"):
        try:
            from bee_video_editor.processors.ffmpeg import get_duration
            duration = get_duration(str(target_path))
        except Exception:
            pass
```

Update the return:
```python
    return {
        "status": "ok",
        "path": str(target_path),
        "name": safe_name,
        "category": category,
        "type": media_type,
        "duration": duration,
    }
```

- [ ] **Step 2: Run backend tests to verify nothing breaks**

```bash
cd bee-content/video-editor && uv run --extra dev pytest tests/test_api_media.py -v 2>&1 | tail -10
```
Expected: All existing tests pass

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/api/routes/media.py
git commit -m "feat: extend upload response with media type and duration"
```

---

### Task 8: Add drag-drop and paste handlers

**Files:**
- Modify: `web/src/components/TimelineEditor.tsx`

- [ ] **Step 1: Add drop handler to timeline container**

In `TimelineEditor.tsx`, wrap the timeline `<div>` with drag-drop handlers:

```tsx
const handleDragOver = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'copy';
}, []);

const handleDrop = useCallback(async (e: React.DragEvent) => {
  e.preventDefault();
  const cursorSec = timelineRef.current?.getTime() ?? 0;

  // 1. Internal drag (from Media Library)
  const beeMedia = e.dataTransfer.getData('bee/media');
  if (beeMedia) {
    try {
      const { path, type } = JSON.parse(beeMedia);
      addActionToTimeline(path, type, cursorSec);
    } catch {}
    return;
  }

  // 2. External file drop
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    for (const file of Array.from(files)) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/media/upload', { method: 'POST', body: formData });
        const data = await res.json();
        addActionToTimeline(data.path, data.type, cursorSec, data.duration);
        toast.success(`Uploaded: ${file.name}`);
      } catch (err) {
        toast.error(`Upload failed: ${file.name}`);
      }
    }
  }
}, []);
```

- [ ] **Step 2: Add paste handler**

```tsx
const handlePaste = useCallback(async (e: React.ClipboardEvent) => {
  const cursorSec = timelineRef.current?.getTime() ?? 0;

  // File paste
  if (e.clipboardData.files.length > 0) {
    for (const file of Array.from(e.clipboardData.files)) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await fetch('/api/media/upload', { method: 'POST', body: formData });
        const data = await res.json();
        addActionToTimeline(data.path, data.type, cursorSec, data.duration);
      } catch {}
    }
    return;
  }

  // Text paste (file path)
  const text = e.clipboardData.getData('text').trim();
  if (text && (text.includes('/') || text.includes('\\'))) {
    const ext = text.split('.').pop()?.toLowerCase() || '';
    const type = ['mp4','mov','webm','avi'].includes(ext) ? 'video'
      : ['mp3','wav','aac','m4a'].includes(ext) ? 'audio'
      : ['png','jpg','jpeg','webp'].includes(ext) ? 'image' : 'video';
    addActionToTimeline(text, type, cursorSec);
  }
}, []);
```

- [ ] **Step 3: Add `addActionToTimeline` helper (module-level, outside the component)**

This function is defined at the top of `TimelineEditor.tsx`, outside the component body. It uses `useProjectStore.getState()` directly (Zustand pattern for non-React code), so it doesn't need to be a hook or callback.

```tsx
// Module-level — outside TimelineEditor component
function addActionToTimeline(path: string, type: string, cursorSec: number, duration?: number | null) {
  const { editorData } = useProjectStore.getState();
  const dur = duration ?? 5;
  const effectId = type === 'audio' ? 'audio' : type === 'image' ? 'video' : 'video';
  const targetRowId = type === 'audio' ? 'A2' : type === 'image' ? 'V1' : 'V1';

  let targetRow = editorData.find(r => r.id === targetRowId);
  const newAction: any = {
    id: `drop-${Date.now()}`,
    start: cursorSec,
    end: cursorSec + dur,
    effectId,
    data: { segmentId: '', contentType: type.toUpperCase(), src: path, title: path.split('/').pop() || '', layerIndex: 0 },
  };

  let newRows: TimelineRow[];
  if (targetRow) {
    newRows = editorData.map(r => r.id === targetRowId ? { ...r, actions: [...r.actions, newAction] } : r);
  } else {
    // Create new row
    newRows = [...editorData, { id: targetRowId, actions: [newAction] }];
  }
  useProjectStore.getState().setEditorData(newRows);
  useProjectStore.getState().pushTimelineHistory(newRows);
}
```

- [ ] **Step 4: Wire handlers to the container div**

Add to the outermost `<div>` of the component:
```tsx
<div
  onDragOver={handleDragOver}
  onDrop={handleDrop}
  onPaste={handlePaste}
  tabIndex={0}
  // ... existing className and style
>
```

- [ ] **Step 5: Wire MediaLibrary drag to set `dataTransfer` data**

In `web/src/components/MediaLibrary.tsx`, the existing `handleDragStart` calls `setDraggedMedia(file)` but does NOT set `dataTransfer`. The timeline's drop handler reads `e.dataTransfer.getData('bee/media')`. Update the `onDragStart` handler on the draggable media item div (around line 469):

Change from:
```tsx
onDragStart={() => handleDragStart(file)}
```
To:
```tsx
onDragStart={(e) => {
  handleDragStart(file);
  const ext = file.path.split('.').pop()?.toLowerCase() || '';
  const type = ['mp4','mov','webm','avi','mkv'].includes(ext) ? 'video'
    : ['mp3','wav','aac','m4a'].includes(ext) ? 'audio' : 'image';
  e.dataTransfer.setData('bee/media', JSON.stringify({ path: file.relative_path || file.path, type }));
  e.dataTransfer.effectAllowed = 'copy';
}}
```

- [ ] **Step 6: Verify build**

```bash
cd bee-content/video-editor/web && npm run build 2>&1 | tail -10
```
Expected: Build succeeds

- [ ] **Step 7: Commit**

```bash
git add web/src/components/TimelineEditor.tsx web/src/components/MediaLibrary.tsx
git commit -m "feat: add drag-drop and paste handlers to timeline"
```

---

### Task 9: Run all tests, verify, clean up

**Files:**
- All modified files

- [ ] **Step 1: Run frontend tests**

```bash
cd bee-content/video-editor/web && npx vitest run 2>&1 | tail -20
```
Expected: All tests pass

- [ ] **Step 2: Run TypeScript strict build**

```bash
cd bee-content/video-editor/web && npm run build 2>&1 | tail -10
```
Expected: `tsc -b && vite build` succeeds

- [ ] **Step 3: Run backend tests**

```bash
cd bee-content/video-editor && uv run --extra dev pytest tests/ -v --tb=short 2>&1 | tail -20
```
Expected: All backend tests pass

- [ ] **Step 4: Manual smoke test**

```bash
cd bee-content/video-editor && ./dev.sh
```

Verify in browser at `http://localhost:5173`:
1. Load a project — timeline shows colored clips on tracks
2. Drag a clip — it moves, snaps
3. Resize a clip — handles on edges work
4. Click a clip — right sidebar shows Properties
5. Click the time ruler — Remotion player seeks
6. Press Space — play/pause works
7. Press S — split works
8. Ctrl+Z — undo works
9. Drag a file from Finder onto timeline — upload + create clip
10. Cmd+V a file path — creates clip on track

- [ ] **Step 5: Verify no DesignCombo references remain**

```bash
grep -r "designcombo\|DesignCombo\|dcDispatch" bee-content/video-editor/web/src/ --include="*.ts" --include="*.tsx" | grep -v node_modules
```
Expected: No matches

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: clean up DesignCombo removal, all tests passing"
```
