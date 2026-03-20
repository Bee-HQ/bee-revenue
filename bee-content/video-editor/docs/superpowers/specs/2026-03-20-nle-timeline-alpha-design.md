# NLE Timeline Alpha Design (v0.9.0-alpha)

## Summary

Replace the segment-list editor (StoryboardTimeline + VideoPlayer + ProductionBar) with a real NLE-style multi-track timeline (DesignCombo SDK) and composited preview (Remotion Player). Keep sidebars (SegmentList, MediaLibrary) unchanged. This is the foundation for the full v0.9.0 NLE overhaul.

## Why DesignCombo over Twick

The research doc initially recommended Twick. After deeper evaluation, DesignCombo was chosen because:
- DesignCombo's architecture (state/timeline/events as separate packages) is better documented with official docs at designcombo.dev
- DesignCombo uses Remotion natively — the state model is designed for Remotion `<Player>` integration
- Twick's SUL license has commercial restrictions; DesignCombo's GitHub repo is Apache 2.0
- DesignCombo's event system (ADD_VIDEO, EDIT_OBJECT, LAYER_SELECT, etc.) maps cleanly to our editing operations
- DesignCombo has RxJS + Immer state management with built-in undo/redo — more mature than Twick's

Both are viable. DesignCombo was chosen for tighter Remotion integration since we decided Remotion handles both preview and export.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│ React App (Vite + Tailwind)                               │
├────────────┬──────────────────────┬───────────────────────┤
│ SegmentList│ RemotionPreview      │ MediaLibrary          │
│ (kept)     │ (NEW — @remotion/    │ (kept)                │
│            │  player)             │                       │
│            ├──────────────────────┤                       │
│            │ TimelineEditor       │                       │
│            │ (NEW — @designcombo/ │                       │
│            │  timeline canvas)    │                       │
├────────────┴──────────────────────┴───────────────────────┤
│ Zustand Store (app state) ←→ DesignCombo StateManager     │
│                    ↕ adapter                              │
│            Storyboard (frontend type)                     │
├───────────────────────────────────────────────────────────┤
│ OTIO Persistence (FastAPI backend)                        │
└───────────────────────────────────────────────────────────┘
```

## Data Adapter

### Frontend Data Model

The adapter operates on the **frontend** `Storyboard`/`Segment` types (from `types/index.ts`), not the backend `ParsedStoryboard`. The API's `parsed_to_schema()` converter already flattens the backend model into the frontend shape.

Frontend `Segment` has flat layer arrays:
```typescript
interface Segment {
  id: string;
  start: string;        // "0:15"
  end: string;           // "0:32"
  title: string;
  visual: LayerEntry[];  // FOOTAGE, STOCK, etc.
  audio: LayerEntry[];   // REAL_AUDIO, NAR entries
  overlay: LayerEntry[]; // LOWER_THIRD, TIMELINE_MARKER, etc.
  music: LayerEntry[];   // MUSIC entries (separate array)
  assigned_media: Record<string, string>;  // "visual:0" → "footage/clip.mp4"
}
```

### Storyboard → DesignCombo State

Each segment's layer arrays map to track items on named tracks:

| Frontend Segment Field | DesignCombo Track | Item Type | Color |
|---|---|---|---|
| `seg.visual[]` | V1 | `video` or `image` | Yellow (FOOTAGE), Blue (STOCK), Purple (PHOTO) |
| `seg.audio[]` where content_type=NAR | A1 | `audio` | Green |
| `seg.audio[]` where content_type=REAL_AUDIO/SFX | A2 | `audio` | Yellow |
| `seg.music[]` | A3 | `audio` | Indigo |
| `seg.overlay[]` | OV1 | `text` | Purple |

### Positioning

Each item's `left` (start position) and `width` (duration) are computed from segment timecodes:

```
left = timeToUnits(parseTimecode(seg.start), zoom)
width = timeToUnits(parseTimecode(seg.end) - parseTimecode(seg.start), zoom)
```

For entries with `metadata.tc_in`/`metadata.out`, the item gets trim metadata and its visible width reflects the trimmed duration.

### Adapter Functions

```typescript
// adapters/timeline-adapter.ts

storyboardToDesignCombo(storyboard: Storyboard): DesignComboState
// Runs on project load. Converts segments → tracks + trackItems.
// Creates 5 tracks (V1, A1, A2, A3, OV1).
// Each LayerEntry becomes a trackItem positioned by segment timecodes.
// Assigned media (from assigned_media dict) determines the media reference.

designComboToStoryboard(state: DesignComboState, original: Storyboard): Storyboard
// Runs on edit (debounced 500ms — drags fire at 60fps, don't sync every frame).
// Converts track items back to segments.
// Preserves fields DesignCombo doesn't know about (metadata, content, raw).
// Matches items to original segments by track position → timecode mapping.
```

### Empty/Unassigned Segments

Segments with no visual entries render as gray "placeholder" blocks on V1, showing the segment title. This matches the current behavior where empty segments show "No media assigned."

### Sync Flow

```
Load:    Backend API → Storyboard → adapter → DesignCombo State → Timeline renders
Edit:    Timeline interaction → DesignCombo event → State update →
         adapter (debounced 500ms) → Storyboard → Backend autosave via API
Select:  SegmentList click → adapter.segmentToTime() → Timeline seek + Remotion seek
```

## DesignCombo Integration Details

### Mounting the Canvas in React

`@designcombo/timeline` is a Fabric.js canvas engine, not a React component. The `TimelineEditor` component manages its lifecycle:

```tsx
function TimelineEditor() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const stateManagerRef = useRef<StateManager | null>(null);

  useEffect(() => {
    // Initialize DesignCombo on mount
    const stateManager = new StateManager({
      size: { width: 1920, height: 1080 },
      fps: 30,
    });
    const timeline = new Timeline(canvasRef.current!, {
      scale: { unit: 300, zoom: 1/300, segments: 5, index: 7 },
      duration: totalDurationMs,
      state: stateManager,
    });

    stateManagerRef.current = stateManager;
    timelineRef.current = timeline;

    // Subscribe to DesignCombo state changes via RxJS
    const sub = stateManager.subscribe((state) => {
      // Debounced sync back to Storyboard
      debouncedSyncToStoryboard(state);
    });

    return () => {
      sub.unsubscribe();
      timeline.destroy();
    };
  }, []);

  return <canvas ref={canvasRef} />;
}
```

### RxJS ↔ Zustand Sync

Two-way sync between DesignCombo's RxJS `StateManager` and our Zustand `project.ts` store:

- **Zustand → DesignCombo:** On project load, call `storyboardToDesignCombo()` and load into `StateManager` via `dispatch("design:load", { payload: designComboState })`.
- **DesignCombo → Zustand:** Subscribe to `StateManager` observable. On change (debounced 500ms), call `designComboToStoryboard()` and update Zustand store, which triggers backend autosave.

### Undo/Redo

DesignCombo's `@designcombo/state` has built-in undo/redo via Immer state snapshots, triggered by `HISTORY_UNDO` / `HISTORY_REDO` events. This replaces the current Zustand undo/redo stack (which only tracked media assignments).

The `Ctrl+Z` / `Ctrl+Shift+Z` handlers in `App.tsx` change from calling `useProjectStore.getState().undo()` to dispatching `HISTORY_UNDO` / `HISTORY_REDO` to DesignCombo.

## Remotion Integration

### Player

The Remotion `<Player>` replaces the HTML5 `<video>` element. It renders a composition that reads from the storyboard data.

For alpha, the composition plays assigned video files in sequence:

```tsx
const BeeComposition: React.FC<{ storyboard: Storyboard }> = ({ storyboard }) => {
  return (
    <>
      {storyboard.segments.map(seg => {
        const src = seg.assigned_media['visual:0'];
        if (!src) return <Black key={seg.id} />;
        return (
          <Sequence key={seg.id} from={timeToFrames(seg.start)} durationInFrames={segFrames(seg)}>
            <Video src={mediaUrl(src)} />
          </Sequence>
        );
      })}
    </>
  );
};
```

Overlay rendering (lower thirds, captions, color grades as React components) is deferred to v0.9.0-beta.

### Scrubber Sync

- **Timeline → Player:** Subscribe to DesignCombo's seek events → call `playerRef.seekTo(frame)`
- **Player → Timeline:** Remotion's `onFrameChange` callback → update DesignCombo playhead position via `timeline.setViewportPos()`
- Both use frames as the common unit (fps from project config, default 30)

**Implementation note:** The exact DesignCombo event names for seek/scrub need to be verified by inspecting the package. Step 1 of implementation is a spike to install the packages and verify the event API surface.

### Export

For alpha, export falls back to the existing FFmpeg pipeline (`bee-video produce`). Remotion-based export is a v0.9.0-beta feature.

## Layout Changes

### Removed Components

| Component | Replacement |
|---|---|
| `StoryboardTimeline.tsx` | DesignCombo timeline canvas |
| `VideoPlayer.tsx` | Remotion `<Player>` |
| `ProductionBar.tsx` | Timeline toolbar + Production dropdown |
| `SegmentCard.tsx` | Clip selection on timeline (alpha: no property panel) |
| `TransitionPicker.tsx` | Timeline transitions (beta) |
| `ColorGradePicker.tsx` | Clip properties (beta) |
| `VolumeSlider.tsx` | Clip properties (beta) |
| `TrimControls.tsx` | Drag clip edges on timeline (beta) |

### Kept Components (unchanged)

- `Layout.tsx` — restructured for new center/bottom layout
- `SegmentList.tsx` — click jumps playhead to segment position
- `MediaLibrary.tsx` — drag files onto timeline tracks
- `StockSearch.tsx`, `DownloadButton.tsx` — stay in MediaLibrary
- `LoadProject.tsx`, `ExportMenu.tsx` — stay
- `ToastContainer.tsx`, `ShortcutsPanel.tsx`, `SkeletonCard.tsx` — stay

### New Components

| Component | Responsibility |
|---|---|
| `TimelineEditor.tsx` | Mounts DesignCombo `Timeline` canvas, manages lifecycle, renders toolbar |
| `RemotionPreview.tsx` | Mounts Remotion `<Player>`, playback controls (play/pause, seek, speed, timecode) |
| `BeeComposition.tsx` | Remotion composition — defines how segments render as video |
| `VideoClip.tsx` | Remotion component — renders a single video clip |
| `adapters/timeline-adapter.ts` | `storyboardToDesignCombo()` + `designComboToStoryboard()` |
| `adapters/time-utils.ts` | Timecode ↔ frames ↔ pixel position conversions |

### New Layout Structure

```tsx
<div className="h-screen flex flex-col">
  <Header />                          {/* kept — title, stats, ExportMenu */}
  <div className="flex flex-1">
    <SegmentList />                    {/* kept — left sidebar */}
    <div className="flex-1 flex flex-col">
      <RemotionPreview />              {/* NEW — top center */}
      <TimelineEditor />              {/* NEW — bottom center */}
    </div>
    <MediaLibrary />                   {/* kept — right sidebar */}
  </div>
</div>
```

## Dependencies

```json
{
  "@designcombo/state": "5.5.8",
  "@designcombo/timeline": "5.5.8",
  "@designcombo/types": "5.5.8",
  "@designcombo/events": "5.5.8",
  "@remotion/player": "^4.0.0",
  "remotion": "^4.0.0"
}
```

All `@designcombo/*` packages pinned to the same version to avoid peer dependency conflicts.

React 19 compatibility must be verified for both DesignCombo and Remotion. If either requires React 18, pin React to 18.

## Timeline Toolbar

The toolbar above the timeline canvas:

```
[Auto-Assign] [Acquire] | [Render ▾] [Rough Cut] | Zoom: [━━━━] [Snap] | [Undo] [Redo]
```

**Toolbar buttons:**
- **Auto-Assign** — runs matcher service
- **Acquire** — runs batch acquisition
- **Render ▾** — dropdown with: Produce (full pipeline), Assemble, Rough Cut
- **Zoom** — slider controls timeline scale
- **Snap** — toggle snap-to-grid
- **Undo/Redo** — dispatches DesignCombo HISTORY_UNDO/REDO

**Production dropdown (inside Render ▾):**
- Init Dirs
- Generate Graphics
- Generate Narration
- Generate Captions
- Run Preflight
- Composite All
- Produce (full pipeline)
- Assemble

This replaces the 13-button ProductionBar with a cleaner two-level UI.

## Testing Strategy

### Adapter Tests (unit)

```typescript
// adapters/__tests__/timeline-adapter.test.ts

test('storyboardToDesignCombo creates correct tracks', () => { ... });
test('storyboardToDesignCombo positions items by timecode', () => { ... });
test('storyboardToDesignCombo handles empty segments', () => { ... });
test('designComboToStoryboard round-trips correctly', () => { ... });
test('designComboToStoryboard preserves metadata fields', () => { ... });
```

### Time Utils Tests (unit)

```typescript
// adapters/__tests__/time-utils.test.ts

test('parseTimecode handles M:SS format', () => { ... });
test('parseTimecode handles H:MM:SS format', () => { ... });
test('timeToFrames converts correctly at 30fps', () => { ... });
test('framesToTime round-trips correctly', () => { ... });
```

### Integration Tests

Manual verification against the minimal fixture (`storyboard_v2_minimal.md`):
1. Load project → verify 5 tracks appear with clips at correct positions
2. Scrub timeline → verify Remotion player shows correct frame
3. Play → verify sequential playback
4. Click segment in sidebar → verify playhead jumps
5. Drag media from library → verify clip appears on track

## What Alpha Delivers

1. Load project → adapter converts storyboard to DesignCombo state
2. Multi-track timeline with V1/A1/A2/A3/OV tracks, clips as colored blocks
3. Remotion Player shows video at playhead position
4. Scrub timeline ↔ preview syncs
5. Sequential playback through all segments
6. Drag media from MediaLibrary onto timeline tracks
7. Click segment in sidebar → jumps to position
8. Export via existing FFmpeg pipeline
9. Undo/redo via DesignCombo state snapshots

## What Alpha Does NOT Deliver (beta scope)

- Drag clip edges to trim
- Transitions between clips (visual on timeline)
- Waveforms on audio tracks
- Clip property panel (color, volume, effects)
- Remotion-based export
- AI features (B-roll panel, caption templates)
- Overlay rendering in Remotion (lower thirds, graphics)

## Implementation Order

1. **Spike: Install deps, verify API surface** — install all packages, verify React compat, explore DesignCombo's actual event names and Timeline constructor API
2. Build `adapters/time-utils.ts` (timecode ↔ frames ↔ pixels) + tests
3. Build `adapters/timeline-adapter.ts` (storyboard ↔ DesignCombo) + tests
4. Build `TimelineEditor.tsx` (mount DesignCombo canvas, toolbar, lifecycle)
5. Build `RemotionPreview.tsx` + `BeeComposition.tsx` (player + composition)
6. Wire scrubber sync (timeline ↔ player)
7. Wire DesignCombo ↔ Zustand sync (RxJS subscription, debounced)
8. Update `Layout.tsx` (new center/bottom structure)
9. Update `SegmentList.tsx` (click → seek to position via adapter)
10. Update `MediaLibrary.tsx` (drag → dispatch DesignCombo ADD_VIDEO/ADD_AUDIO event)
11. Replace undo/redo (App.tsx keybindings → DesignCombo HISTORY events)
12. Remove old components
13. End-to-end test
