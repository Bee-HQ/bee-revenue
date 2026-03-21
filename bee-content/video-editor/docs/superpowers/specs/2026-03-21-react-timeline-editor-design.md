# Replace DesignCombo with react-timeline-editor

## Goal

Replace the DesignCombo SDK (`@designcombo/state`, `@designcombo/timeline`, `@designcombo/types`, `@designcombo/events`) with `@xzdarcy/react-timeline-editor` — a DOM-based React timeline component. Eliminates canvas/Fabric.js crashes, invisible tracks, class registry bugs, and `updateTrackItemCoords` errors.

## Motivation

DesignCombo's canvas-based timeline has caused persistent issues:
- Fabric.js objects not found during coordinate updates (`updateTrackItemCoords` crash)
- Case-sensitive class registry requiring double registration
- Invisible tracks due to default fill matching dark background
- React 19 compatibility issues with addEventListener
- Complex lifecycle management (StateManager, dispose, purge, destroyListeners)

`react-timeline-editor` is DOM-based (no canvas), has a simple data model (rows + actions), and handles drag/resize/snap/cursor natively.

## Architecture

### Data Flow

```
Storyboard (Zustand store)
  -> storyboardToTimeline() adapter
  -> TimelineRow[] + effects map
  -> <Timeline> component (DOM-based tracks)
  -> onChange callback
  -> update Zustand (with undo history)
  -> debounced backend sync (1s)
```

### What Changes

| Component | Action |
|-----------|--------|
| `@designcombo/*` (4 packages) | Remove |
| `@xzdarcy/react-timeline-editor` | Add |
| `TimelineEditor.tsx` | Rewrite (from ~380 lines) |
| `timeline-adapter.ts` | Rewrite (output `TimelineRow[]` instead of `DCState`) |
| `timeline-adapter.test.ts` | Rewrite (tests for new adapter shape) |
| `TimelineRuler.tsx` | Delete (library has built-in ruler) |
| `SPIKE-NOTES.md` | Delete (documents DesignCombo API, now stale) |
| `App.tsx` | Remove `dcDispatch` imports, replace with Zustand/ref calls |
| `stores/project.ts` | Unify undo/redo into single timeline history system |
| Backend `routes/media.py` | Extend `POST /api/media/upload` response to include `type` and `duration` |

### What Stays Untouched

- `RemotionPreview.tsx` — Remotion Player unchanged
- `BeeComposition.tsx` — composition rendering unchanged
- `SegmentList.tsx` — segment list unchanged
- `Layout.tsx` — TimelineEditor slot unchanged
- All other backend code

## Timeline Adapter

### Output Format

```ts
// react-timeline-editor uses seconds (not ms)
// Each row = one track, each action = one clip

interface BeeTimelineAction extends TimelineAction {
  id: string;        // e.g. 'seg-01-v-0'
  start: number;     // seconds
  end: number;       // seconds
  effectId: string;  // 'video' | 'narration' | 'audio' | 'music' | 'overlay'
  data: {
    segmentId: string;
    contentType: string;
    src: string;
    title: string;
    layerIndex: number;
    formulaCode?: string;
  };
}
```

### Time Unit Boundary

The adapter is the **sole conversion point** between milliseconds (used by Zustand `currentTimeMs`, `parseTimecode`, `timeToMs`) and seconds (used by `react-timeline-editor`).

- `storyboardToTimeline()`: converts `timeToMs(parseTimecode(seg.start))` → divide by 1000 → action.start in seconds
- `timelineToStoryboard()`: action.start in seconds → multiply by 1000 → reconstruct timecode via existing `formatTimecode()` utility
- Cursor sync: `onCursorDrag(timeInSeconds)` → `setCurrentTimeMs(timeInSeconds * 1000)`
- Remotion sync: `currentTimeMs / 1000` → `timelineRef.current.setTime(seconds)`

No other code should do ms↔s conversion.

### Track Mapping

| Track | effectId | Content | Color |
|-------|----------|---------|-------|
| V1 | `video` | Visual entries (footage, stock, maps, graphics) | Amber `#a16207` |
| A1 | `narration` | NAR audio entries | Green `#166534` |
| A2 | `audio` | Real audio, SFX | Teal `#0f766e` |
| A3 | `music` | Music entries | Purple `#6b21a8` |
| OV1 | `overlay` | Lower thirds, captions, timeline markers | Pink `#9d174d` |

### Dynamic Tracks

Only rows with content are rendered. V1 (video) always shows. Empty drop-target rows appear at the bottom for adding new track types.

### Transitions

`react-timeline-editor` has no native transition concept. Transitions are represented as **short overlapping actions on the V1 track** with `effectId: 'transition'`. The action's `data` field carries the transition type and duration:

```ts
{
  id: 'trans-seg-03',
  start: 9.5,    // overlap start
  end: 10.5,     // overlap end (1s transition)
  effectId: 'transition',
  data: { type: 'dissolve', duration: 1, fromSegId: 'seg-02', toSegId: 'seg-03' }
}
```

These render as semi-transparent bars via `getActionRender`. They use `flexible: false` on the `TimelineAction` to disable resize while keeping them movable. The reverse adapter maps overlapping transition actions back to the storyboard's `transition` array entries.

### Reverse Adapter

`timelineToStoryboard(rows, original)` maps changed action positions back to storyboard:

1. For each action, convert `start`/`end` seconds → milliseconds → timecode string
2. Update `assigned_media` entries based on action `data.src`
3. Map transition actions back to segment `transition` array entries
4. Return updated storyboard with new timecodes and assignments

## TimelineEditor Component

### Structure

### Zoom Control

Zoom is controlled by changing the `scaleWidth` prop dynamically. A `zoomLevel` state (range 1-10, default 5) maps to `scaleWidth` via `zoomLevel * 40` (range 40px-400px per scale unit). The toolbar's range slider updates `zoomLevel` in local component state.

### Component Layout

```tsx
<div style={{ height: 180 }}>
  <Toolbar />  {/* zoom slider, snap, undo/redo, split */}
  <div className="flex flex-1 min-h-0">
    <TrackLabels rows={rows} />  {/* V1, A1, etc. with mute buttons */}
    <Timeline
      ref={timelineRef}
      editorData={rows}
      effects={effects}
      onChange={handleChange}
      scale={1}
      scaleWidth={zoomLevel * 40}
      rowHeight={28}
      gridSnap={snapEnabled}
      dragLine={true}
      autoScroll={true}
      getActionRender={renderAction}
      onClickAction={handleClickAction}
      onClickActionOnly={handleSelectAction}
      onCursorDrag={handleLiveSeek}
      onCursorDragEnd={handleSeekEnd}
      onActionMoveEnd={handleMoveEnd}
      onActionResizeEnd={handleResizeEnd}
    />
  </div>
</div>
```

**Note on prop names:** The above uses `react-timeline-editor`'s actual API names from `packages/timeline/src/interface/timeline.ts`. Exact signatures per the source:
- `onCursorDrag?: (time: number) => void` — fires continuously during drag (live scrub)
- `onCursorDragEnd?: (time: number) => void` — fires when cursor drag is released
- `onActionMoveEnd?: (params: { action, row, start, end }) => void`
- `onActionResizeEnd?: (params: { action, row, start, end, dir }) => void`
- `onClickActionOnly?: (e, { action, row, time }) => void` — fires only on click (not drag)

**Ref API** (`TimelineState` from the library, accessed via `timelineRef.current`):
- `setTime(time: number)` — set cursor position programmatically
- `getTime()` — get current cursor time
- `play({ toTime?, autoEnd?, runActionIds? })` — start playback
- `pause()` — stop playback
- `setScrollLeft(val)` / `setScrollTop(val)` — scroll control

### Custom Action Rendering

`getActionRender` returns colored bars per `effectId`:
- `video` — amber with clip title/filename
- `narration` — green with "NAR: segment title"
- `audio` — teal with audio type label
- `music` — purple with music name
- `overlay` — pink with overlay type + content
- `transition` — semi-transparent gradient bar with transition type label

### Clip Selection (activeClipId)

`onClickActionOnly` sets `activeClipId` in Zustand store. The action ID format is `{segmentId}-{type}-{index}` (e.g., `seg-01-v-0`, `seg-03-nar-0`), consistent with the current format that `ClipProperties.tsx` and `AIPanel.tsx` parse via regex. Clicking empty space clears `activeClipId` via `onClickRow`.

### Split at Playhead

Custom implementation since `react-timeline-editor` has no built-in split:

1. Find the action under the cursor on the selected track (or V1 if none selected)
2. Create two new actions: `[action.start, cursorTime]` and `[cursorTime, action.end]`
3. Remove original action, add the two halves
4. Both halves inherit the original's `data` (src, segmentId, etc.)
5. Push to undo history

Triggered by the Split button in the toolbar and `S` key shortcut in `App.tsx`.

**Cross-component access:** `TimelineEditor` exposes a `splitAtPlayhead()` function via a Zustand action (`stores/project.ts`). The function receives the current `editorData` (timeline rows) and `currentTimeMs`, performs the split, and updates `editorData` in the store. `App.tsx` calls `useProjectStore.getState().splitAtPlayhead()` — no ref needed.

### Cursor Sync with Remotion

- `onCursorDrag` (live) → `setCurrentTimeMs(seconds * 1000)` in Zustand → RemotionPreview seeks in real-time during scrub
- `onCursorDragEnd` → same, ensures final position is committed
- When Remotion plays, frame updates → `timelineRef.current.setTime(seconds)` to move cursor
- Bidirectional sync, same pattern as current implementation

### Undo/Redo

Unified single undo system replacing both the existing `undoStack`/`redoStack` in `stores/project.ts` and the removed DesignCombo `history:undo`/`history:redo` events:

- `timelineHistory: TimelineRow[][]` — array of row snapshots (max 50)
- `timelineHistoryIndex: number` — current position in history
- Every `onChange` pushes a snapshot
- `undo()` / `redo()` methods navigate the stack and update `editorData`
- Ctrl+Z / Ctrl+Shift+Z in `App.tsx` call the unified `undo()` / `redo()`
- Backend sync fires on latest state after 1s debounce

The existing `undoStack`/`redoStack` fields (which tracked per-assignment `HistoryEntry` objects with `segmentId`, `key`, `oldValue`, `newValue` and called `api.assignMedia()` on undo) are removed. The new timeline history captures full `TimelineRow[]` snapshots, which include all assignment state via each action's `data.src`. When the user undoes a timeline change, the entire row state reverts — including any assignments made via the Media Library sidebar.

To make this work, all media assignment paths (Media Library drag-to-segment, right-click assign, etc.) must also update the timeline `editorData` in Zustand, not just the storyboard. This ensures assignments are captured in timeline history snapshots. The debounced backend sync then pushes the final state.

## Drag-and-Drop & Paste

### 1. Internal Drag (Media Library → Timeline)

- Media Library items set `dataTransfer.setData('bee/media', JSON.stringify({path, type}))`
- Timeline container `onDrop` handler:
  - Parse `bee/media` data
  - Determine target row from drop position
  - Create new action at cursor time with 5s default duration
  - Row highlights on dragover

### 2. External File Drop (Finder → Timeline)

- `onDrop` checks `dataTransfer.files`
- File extension determines target track:
  - `.mp4, .mov, .webm, .avi` → video row
  - `.mp3, .wav, .aac, .m4a` → nearest audio row
  - `.png, .jpg, .jpeg, .webp` → video or overlay row
- Upload via `POST /api/media/upload` → returns `{ path, type, duration }`
- Create action with returned metadata

### 3. Paste (Cmd+V)

- Global `paste` listener (when timeline container is focused)
- Priority: `clipboardData.files` first (file paste), then `clipboardData.getData('text')`
- Text paste: if looks like file path or URL, create action on selected track at cursor
- URLs: download via backend first, then assign
- New action defaults to 5s duration at cursor position

### Backend: POST /api/media/upload (extend existing)

The route already exists at `routes/media.py` (lines 113-136). Current response: `{ status, path, name, category }`. Extend to also return:
- `type: string` — `'video' | 'audio' | 'image'` based on file extension
- `duration: number | null` — probed via FFmpeg `get_duration()` for video/audio, null for images

No new route needed — just extend the existing response shape.

## Removed Dependencies

| Package | Version | Reason |
|---------|---------|--------|
| `@designcombo/state` | 5.5.8 | Replaced by Zustand + react-timeline-editor |
| `@designcombo/timeline` | 5.5.8 | Replaced by react-timeline-editor |
| `@designcombo/types` | 5.5.8 | Types inlined or replaced |
| `@designcombo/events` | 1.0.2 | Events replaced by direct ref calls |

## Deleted Files

- `TimelineRuler.tsx` — library has built-in time ruler
- `SPIKE-NOTES.md` — documents DesignCombo API, entirely stale after migration

## Testing

### Existing tests to rewrite
- `timeline-adapter.test.ts` — 12 existing tests for `storyboardToDesignCombo` / `designComboToStoryboard` must be rewritten for new `storyboardToTimeline` / `timelineToStoryboard` functions

### New tests
- Adapter: output shape (correct `TimelineRow[]`), dynamic track filtering, seconds conversion (verify ms→s boundary), transition action generation
- Reverse adapter: action position changes map back to correct segment timecodes (seconds→ms→timecode), assigned_media updates
- Component smoke test: renders without crashing, correct number of rows for sample storyboard
- Undo/redo: push/pop history, boundary conditions (empty stack, max 50 depth, redo cleared on new change)
- Split: action splits into two at cursor time, both halves have correct data
- Drop handlers: file type → track mapping, paste text parsing, internal drag data parsing

## Success Criteria

1. Timeline renders all storyboard segments as colored clips on correct tracks
2. Drag-to-move and resize clips updates storyboard via backend sync
3. Cursor syncs bidirectionally with Remotion Player
4. Drag files from Finder onto timeline uploads and creates clips
5. Cmd+V paste creates clips on selected track
6. Undo/redo works for all timeline edits
7. Split at playhead divides a clip into two
8. Clicking a clip sets activeClipId (ClipProperties + AIPanel work)
9. Transitions render as overlapping bars on V1
10. No canvas errors, no Fabric.js, no class registry issues
11. Everything fits on screen without scrolling
