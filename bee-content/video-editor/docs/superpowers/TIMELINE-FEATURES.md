# Timeline Feature Gap Analysis — Validated Against Library API

**Date:** 2026-03-21
**Library:** `@xzdarcy/react-timeline-editor` + `@xzdarcy/timeline-engine`
**Compared against:** DaVinci Resolve, Premiere Pro, Final Cut Pro, CapCut, Descript, Runway

## Library Capability Map

What `react-timeline-editor` gives us for free vs what we build custom:

| Capability | Library Support | Notes |
|------------|:-:|-------|
| Move clips (drag) | Built-in | `onActionMoveStart/Moving/End` callbacks |
| Resize clips (drag edges) | Built-in | `onActionResizeStart/Resizing/End` + `flexible` flag |
| Select clip | Built-in | `selected` field on `TimelineAction` |
| Snap to grid | Built-in | `gridSnap` prop |
| Drag alignment lines | Built-in | `dragLine` prop |
| Cursor/playhead | Built-in | `onCursorDrag/DragEnd`, `setTime()` ref |
| Time ruler | Built-in | `getScaleRender` for custom labels |
| Custom clip rendering | Built-in | `getActionRender` — full React control |
| Click handlers | Built-in | `onClickAction`, `onClickActionOnly`, `onDoubleClickAction` |
| Right-click handlers | Built-in | `onContextMenuAction`, `onContextMenuRow` |
| Row reordering | Built-in | `enableRowDrag`, `onRowDragStart/End` |
| Auto-scroll on drag | Built-in | `autoScroll` prop |
| Per-action disable | Built-in | `disable` field on action |
| Per-action movable toggle | Built-in | `movable` field on action |
| Per-action min/max bounds | Built-in | `minStart`, `maxEnd` fields |
| Per-row custom height | Built-in | `rowHeight` field on row |
| Per-row CSS classes | Built-in | `classNames` field on row |
| Effect lifecycle hooks | Built-in | `source.enter/update/leave/start/stop` on effects |
| Multi-select clips | **Custom** | Manage `selected` state ourselves |
| Copy/paste/duplicate | **Custom** | Clone actions in editorData |
| Delete clip | **Custom** | Remove from actions array |
| Split clip | **Custom** | Already implemented in store |
| Context menu UI | **Custom** | Use `onContextMenuAction` + render menu |
| Waveform display | **Custom** | Render in `getActionRender` via Web Audio API |
| Clip thumbnails | **Custom** | Render in `getActionRender` via canvas/video frame |
| Track lock/mute/hide | **Custom** | Track labels UI + `disable`/filter rows |
| Timeline markers | **Custom** | Separate marker track or overlay |
| Speed control | **Custom** | `playbackRate` field on action data |
| Transition indicators | **Custom** | Render in `getActionRender` |

## Feature Implementation Plan — Prioritized

### Tier 1: Essential (makes it feel like a real editor)

Features ordered by impact and implementation difficulty.

#### 1. Right-click context menu
**Effort:** Small
**How:** `onContextMenuAction` callback → render a `<ContextMenu>` component with absolute positioning. Actions: Delete, Duplicate, Split, Copy, Properties.
**Files:** New `TimelineContextMenu.tsx`, modify `TimelineEditor.tsx`

#### 2. Multi-select clips
**Effort:** Small
**How:** Track `selectedActionIds: Set<string>` in store. `onClickActionOnly` with `e.shiftKey` → toggle selection. Set `selected: true` on matching actions in `editorData` before passing to `<Timeline>`.
**Files:** Modify `stores/project.ts`, `TimelineEditor.tsx`

#### 3. Copy/paste/duplicate clips
**Effort:** Small
**How:** `clipboard: TimelineAction[]` in store. Ctrl+C copies selected. Ctrl+V pastes at cursor. Ctrl+D duplicates in-place (offset by 1s). Generate new IDs on paste.
**Files:** Modify `stores/project.ts`, `App.tsx` (keyboard handlers)

#### 4. Delete clip (with ripple option)
**Effort:** Small
**How:** Delete key → remove selected actions from `editorData`. Ripple: shift subsequent actions left to close gap. Non-ripple: leave gap.
**Files:** Modify `stores/project.ts`, `App.tsx`

#### 5. Track lock/mute/hide toggles
**Effort:** Medium
**How:** `trackState: Record<string, { locked, muted, hidden }>` in store. Locked → set `movable: false, flexible: false` on all actions in row. Hidden → filter row from `editorData`. Muted → visual indicator + skip in export. Render toggles in track label area.
**Files:** Modify `stores/project.ts`, `TimelineEditor.tsx`

#### 6. Waveform display on audio clips
**Effort:** Medium
**How:** In `getActionRender` for audio clips, render a `<canvas>` element. On mount, use Web Audio API (`AudioContext.decodeAudioData`) to get waveform data, draw peaks. Cache waveform data in a `Map<src, Float32Array>`.
**Files:** New `WaveformRenderer.tsx`, modify `TimelineActionRenderer.tsx`

#### 7. Clip thumbnails on video clips
**Effort:** Medium
**How:** In `getActionRender` for video clips, render thumbnail frames. Use `<video>` element with `currentTime` seek + `canvas.drawImage()` to extract frames at intervals. Cache as data URLs.
**Files:** New `ThumbnailRenderer.tsx`, modify `TimelineActionRenderer.tsx`

#### 8. Timeline markers
**Effort:** Small
**How:** `markers: { time: number, label: string, color: string }[]` in store. M key adds marker at cursor. Render as vertical lines + labels overlaid on the timeline. Click marker to seek.
**Files:** Modify `stores/project.ts`, `TimelineEditor.tsx`, `App.tsx`

#### 9. Transition indicators
**Effort:** Small
**How:** Already have transition data in adapter. Render small diamond/gradient elements between adjacent V1 clips using `getActionRender` or an overlay layer. Click to edit transition type/duration.
**Files:** Modify `TimelineActionRenderer.tsx`, `timeline-adapter.ts`

#### 10. Constant speed change
**Effort:** Small
**How:** `playbackRate` field on `BeeActionData`. UI in ClipProperties panel (speed dropdown: 0.5x, 1x, 1.5x, 2x, 4x). Affects clip display width on timeline (faster = shorter). Remotion reads `playbackRate` for render.
**Files:** Modify `ClipProperties.tsx`, `BeeComposition.tsx`, adapter

### Tier 2: Professional (competitive with CapCut)

#### 11. Clip duration labels
**Effort:** Tiny — add duration text in `getActionRender`

#### 12. Timecode ruler
**Effort:** Small — use `getScaleRender` to format seconds as `MM:SS`

#### 13. Scroll-to-zoom (Ctrl+scroll)
**Effort:** Small — `onWheel` handler on container, adjust `zoomLevel` state

#### 14. Fit-to-window zoom
**Effort:** Small — calculate `scaleWidth` from `containerWidth / totalDuration`

#### 15. Blade/razor tool
**Effort:** Small — tool mode state, click on clip splits at click position instead of playhead

#### 16. Track height adjustment
**Effort:** Small — use per-row `rowHeight` field, drag handle between tracks

#### 17. Audio fade handles
**Effort:** Medium — custom drag handles in `getActionRender`, adjust fade in/out duration

#### 18. Default transition shortcut
**Effort:** Small — Ctrl+D at edit point inserts default transition (dissolve 1s)

#### 19. Reverse / freeze frame
**Effort:** Small — `playbackRate: -1` for reverse, duplicate frame as image for freeze

#### 20. Ripple trim mode
**Effort:** Medium — `onActionResizeEnd` shifts all subsequent actions

### Tier 3: Advanced (pro NLE territory)

21. Speed ramp curves — keyframe editor for playbackRate
22. Keyframing — per-property animation curves (opacity, position, scale)
23. Volume rubber-banding — visual volume envelope on audio clips
24. Compound clips — nest multiple actions into one
25. Roll/slip/slide trims — advanced trim modes with `onActionResizing` override
26. Link/unlink A/V — paired action IDs that move together
27. Adjustment layers — special track that applies effects to everything below

## Implementation Order Recommendation

Start with the **quick wins** that use existing library callbacks:

**Sprint 1 (1-2 sessions):** Items 1-4 — context menu, multi-select, copy/paste, delete. All are Zustand state + keyboard handlers + one new component. Makes the timeline feel interactive.

**Sprint 2 (1-2 sessions):** Items 5, 8, 9, 10-14 — track controls, markers, transitions, duration labels, timecode ruler, zoom improvements. Mostly UI additions.

**Sprint 3 (2-3 sessions):** Items 6, 7 — waveforms and thumbnails. These need Web Audio API and video frame extraction — more complex but high visual impact.

**Later:** Tier 2 remaining + Tier 3 as needed.

## Current Outstanding Issues (fix first)

Before adding features, fix the 5 issues in `TIMELINE-ISSUES.md`:
1. Track label misalignment
2. Cursor/playhead sync with Remotion
3. Transitions as full clips on V1
4. Zoom/scale too tight
5. Library default 600x600 dimensions

These are blockers — new features won't matter if the basic timeline doesn't render correctly.
