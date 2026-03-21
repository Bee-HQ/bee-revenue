# react-timeline-editor Integration — Outstanding Issues

**Branch:** `bee/react-timeline-editor` (pushed to origin)
**Date:** 2026-03-21
**Spec:** `docs/superpowers/specs/2026-03-21-react-timeline-editor-design.md`
**Plan:** `docs/superpowers/plans/2026-03-21-react-timeline-editor.md`

## What's Done

Replaced DesignCombo SDK (4 packages) with `@xzdarcy/react-timeline-editor`. 11 commits:

| Commit | Change |
|--------|--------|
| `88a0a90` | Swap deps: remove 4 DesignCombo pkgs, add react-timeline-editor |
| `8caf344` | Rewrite adapter: `TimelineRow[]` in seconds, dynamic tracks |
| `234e37c` | Zustand: editorData, undo/redo history, splitAtPlayhead |
| `55bd1c6` | Action renderer: colored bars per track type |
| `1d276eb` | TimelineEditor: full rewrite (415 → 99 lines) |
| `78dda58` | App.tsx: remove dcDispatch, wire Zustand shortcuts |
| `dd072de` | Fix type imports (types come from `@xzdarcy/timeline-engine` not main pkg) |
| `9405254` | Backend: upload route returns type + duration |
| `13eecaf` | Drag-drop + paste + MediaLibrary dataTransfer wiring |
| `94a4f91` | Code review fixes: action IDs, syncingRef guard, toolbar buttons |
| `c4b0512` | Add library CSS import, remove debug logs |

**What works:**
- 30/30 tests pass (12 time-utils, 11 adapter, 7 store)
- Build clean (`tsc -b && vite build` — 683KB bundle, down from 930KB)
- Zero DesignCombo references remain in source
- Storyboard loads, adapter converts to TimelineRow[] correctly (verified via console.log: 5 rows, 55 actions for sample-3min.md)
- Track labels render (V1, A1, A2, A3, OV1)
- Colored clips render on tracks (amber=video, green=narration, teal=audio)
- Toolbar: Auto-Assign, Acquire, Pipeline, Rough Cut, Split, Snap, Zoom, Undo, Redo
- Remotion Player still works independently (play/pause, seek, captions)

## Outstanding Issues

### Issue 1: Track Label Misalignment (Visual)

**Problem:** Track labels (V1, A1, etc.) are rendered in a separate `<div>` column to the left of the `<Timeline>` component. The library renders its own time ruler at the top (32px height + 10px margin), which shifts all track rows down. The label column doesn't perfectly match this offset, causing labels to be misaligned with their track rows.

**Root cause:** The library's internal layout (time ruler + virtualized scroll area with its own margins) doesn't expose a clean way to align external elements. The spacer approach (42px div) is fragile — scroll position, dynamic row heights, and browser rendering differences break the alignment.

**Proposed fix:** Drop the separate label column entirely. Instead, either:
- (A) Render track labels inside the custom `getActionRender` callback (each clip already knows its track via `effectId`)
- (B) Use CSS `::before` pseudo-elements on the library's row elements to show labels
- (C) Use the library's `getScaleRender` or a custom row component if the API supports it

**Files involved:** `web/src/components/TimelineEditor.tsx` (lines 280-287 — the label column div)

### Issue 2: No Cursor/Playhead Sync with Remotion

**Problem:** When Remotion plays, the timeline cursor doesn't move. When you drag the timeline cursor, Remotion doesn't seek. The bidirectional sync is broken.

**Root cause:** The sync code exists but may not be working:
```tsx
// TimelineEditor.tsx — Remotion → Timeline
useEffect(() => {
  if (timelineRef.current) {
    timelineRef.current.setTime(currentTimeMs / 1000);
  }
}, [currentTimeMs]);

// TimelineEditor.tsx — Timeline → Remotion
const handleCursorDrag = useCallback((time: number) => {
  setCurrentTimeMs(time * 1000);
}, []);
```

Possible causes:
1. `timelineRef` may not be populated — the library uses `React.forwardRef` and `useImperativeHandle`. Check if `timelineRef.current` is null.
2. The library's `setTime()` may update internal state but not visually move the cursor without calling `reRender()`.
3. `onCursorDrag` may not be firing — check if the cursor is actually draggable (might need specific CSS or props).
4. `currentTimeMs` updates during Remotion playback go through the polling fallback (RemotionPreview.tsx line 53-66) which sets `setCurrentTimeMs` — but the useEffect in TimelineEditor fires on every `currentTimeMs` change, which could be too frequent (30fps = 30 setTime calls/sec).

**How to debug:**
```tsx
// Add to TimelineEditor after the ref is created:
useEffect(() => {
  console.log('timelineRef.current:', timelineRef.current);
  console.log('has setTime:', typeof timelineRef.current?.setTime);
}, [editorData]); // fires after Timeline renders with data
```

**Files involved:**
- `web/src/components/TimelineEditor.tsx` (cursor sync useEffect + handleCursorDrag)
- `web/src/components/RemotionPreview.tsx` (frame change → setCurrentTimeMs)

### Issue 3: Transitions Render as Full Clips on V1

**Problem:** The adapter creates transition actions on the V1 track (e.g., `effectId: 'transition'`, gray color). These render as full-width clips alongside video clips, making the V1 track look cluttered and confusing. The first visible clip on V1 says "transition" which is misleading.

**Root cause:** `timeline-adapter.ts` creates transition actions with `flexible: false` and puts them on V1 as overlapping actions. But `react-timeline-editor` doesn't support overlapping actions on the same row — they just stack and look wrong.

**Proposed fix:** Remove transition actions from the adapter output for now. Transitions are metadata (type + duration between segments) that don't need visual representation in the timeline. They can be shown as a small icon/badge between clips later.

**Files involved:** `web/src/adapters/timeline-adapter.ts` (transition generation code, around lines 240-270)

### Issue 4: Zoom/Scale Too Tight

**Problem:** With `scale=1` (1 second per scale unit), a 180-second video creates a 36,000px-wide timeline at default zoom. Only ~3 seconds are visible at a time. The time ruler shows "0, 1, 2" which is confusing (looks like minutes but it's seconds).

**Proposed fix:** Change `scale` to `10` (10 seconds per unit) and adjust `scaleWidth` accordingly. This way the ruler shows "0, 10, 20, 30..." and more of the timeline is visible. The zoom slider (which controls `scaleWidth`) then provides fine-grained zoom within that range.

**Files involved:** `web/src/components/TimelineEditor.tsx` (the `<Timeline>` props: `scale` and `scaleWidth`)

### Issue 5: Library Default Dimensions (600x600)

**Problem:** The library's CSS sets `.timeline-editor { height: 600px; width: 600px; }` as defaults. We pass `style={{ width: '100%', height: '100%' }}` but this may conflict with the default CSS.

**Proposed fix:** Override in our CSS or ensure the `style` prop takes precedence. May need `!important` or a wrapper class.

**Files involved:**
- `web/src/components/TimelineEditor.tsx` (style prop on `<Timeline>`)
- Potentially `web/src/index.css` (CSS override)

## Key Architecture Context

### Library API (`@xzdarcy/react-timeline-editor`)

**Component:** `<Timeline>` — the main component. Takes `editorData: TimelineRow[]`, `effects: Record<string, TimelineEffect>`, plus many optional props.

**Types come from `@xzdarcy/timeline-engine`** (not the main package):
```ts
import { Timeline } from '@xzdarcy/react-timeline-editor';
import type { TimelineState } from '@xzdarcy/react-timeline-editor';
import type { TimelineRow, TimelineAction, TimelineEffect } from '@xzdarcy/timeline-engine';
```

**CSS must be imported:**
```ts
import '@xzdarcy/react-timeline-editor/dist/react-timeline-editor.css';
```

**Ref API** (`TimelineState`):
- `setTime(seconds)` — move cursor
- `getTime()` — get cursor time
- `play()` / `pause()` — internal engine playback
- `reRender()` — force visual update
- `setScrollLeft(px)` / `setScrollTop(px)` — scroll

**Key props:**
- `scale` — seconds per scale unit (e.g., `10` = each unit = 10 seconds)
- `scaleWidth` — pixels per scale unit
- `scaleSplitCount` — subdivisions per unit (default 10)
- `rowHeight` — pixels per row (we use 28)
- `gridSnap` — boolean, snap to grid
- `dragLine` — boolean, show alignment guides
- `getActionRender` — custom renderer for action bars
- `onChange` — fires after drag/resize with new `TimelineRow[]`
- `onCursorDrag` — fires continuously during cursor drag
- `onCursorDragEnd` — fires when cursor drag ends
- `onClickActionOnly` — fires on click (not drag)
- `onClickRow` — fires on row click

**Library source cloned at:** `/tmp/rte-src` (may be gone — re-clone from `https://github.com/xzdarcy/react-timeline-editor`)

### Our Adapter (`web/src/adapters/timeline-adapter.ts`)

Converts `Storyboard` → `{ rows: TimelineRow[], effects }` and back.

- Times in **seconds** (library convention). Zustand uses ms.
- Track mapping: V1=video, A1=narration, A2=audio, A3=music, OV1=overlay
- Dynamic rows: only tracks with content are included, V1 always present
- Action IDs: `{segmentId}-{type}-{layerIndex}` (e.g., `seg-01-v-0`) — must match this format because `ClipProperties.tsx` and `AIPanel.tsx` parse it with regex
- `BeeTimelineAction` extends `TimelineAction` with `data: BeeActionData` field carrying segment metadata

### Store (`web/src/stores/project.ts`)

Added fields:
- `editorData: TimelineRow[]` — current timeline state
- `timelineHistory: TimelineRow[][]` — undo snapshots (max 50)
- `timelineHistoryIndex: number` — current position
- `setEditorData()`, `pushTimelineHistory()`, `timelineUndo()`, `timelineRedo()`, `splitAtPlayhead()`

Removed: old `undoStack`/`redoStack`/`HistoryEntry` system

### Storyboard for testing

The loaded storyboard (`sample-3min.md`) has 12 segments, 180s total:
```
911-call-opening: 0:00-0:15  visual=1 audio=2 overlay=1 music=0
the-estate:       0:15-0:30  visual=1 audio=1 overlay=1 music=1
the-dynasty:      0:30-0:45  visual=1 audio=1 overlay=1 music=1
bodies-found:     0:45-1:00  visual=1 audio=2 overlay=1 music=0
bodycam-arrival:  1:00-1:15  visual=1 audio=2 overlay=1 music=1
...
```

Adapter output: 5 rows (V1:23 actions, A1:10, A2:6, A3:5, OV1:11) — total 55 actions.

### Remotion (unchanged)

RemotionPreview.tsx and BeeComposition.tsx are untouched by this migration. The Remotion Player handles video preview independently. Cursor sync should bridge the two via `currentTimeMs` in Zustand.

## How to Pick Up

```bash
cd /Users/mk/work/bee-revenue
git checkout bee/react-timeline-editor
cd bee-content/video-editor

# Run tests
cd web && npx vitest run

# Build
npm run build

# Dev server
cd .. && ./dev.sh
# Frontend: http://localhost:5173
# Backend:  http://localhost:8420
```

Fix the 5 issues above in order: Issues 3 and 4 are quickest (adapter change + prop change). Issue 1 needs a layout rethink. Issue 2 needs debugging. Issue 5 may resolve itself once Issue 1 is fixed.
