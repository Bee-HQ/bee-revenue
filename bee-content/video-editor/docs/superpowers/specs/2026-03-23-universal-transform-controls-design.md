# Universal Transform Controls — Design Spec

> Universal position, scale, rotation, and opacity controls for all clips (overlays, visuals, footage) in the Bee Video Editor.

## Problem

The editor has 21+ Remotion components with no consistent way to control where they appear on screen. Position is handled ad-hoc per component — TextOverlay uses 5 flexbox presets, SourceBadge uses CSS absolute positioning, LowerThird is hardcoded to bottom-left, and most components have no positioning at all. There's no way to adjust scale, rotation, or opacity from the UI. The Props panel only shows controls for visuals (color grade, Ken Burns, trim) and audio (volume). Overlays have zero UI controls.

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Scope | All clips (overlays, visuals, footage) | Future-proof — one system for everything |
| Transform properties | position, x, y, scale, rotation, opacity | Core set covers 95% of needs without complexity |
| Architecture | TransformWrapper in BeeComposition | Zero changes to existing components, single integration point |
| Transform vs component position | Transform overrides component position when set | Simplest mental model — component position becomes the default |
| Position preset + offset | Additive — preset picks region, offset nudges from there | Matches how users think: "top-left, nudge it right a bit" |
| Data shape | Nested `transform` object on entries | Clean separation from component metadata, trivial reset |
| UI layout | All controls visible, each configurable | Power users see everything, can hide what they don't use |

## Data Model

### TransformConfig

```typescript
interface TransformConfig {
  position?: 'top-left' | 'top' | 'top-right' | 'left' | 'center' | 'right' | 'bottom-left' | 'bottom' | 'bottom-right';
  x?: number;      // offset from preset, % of frame width (-100 to 100)
  y?: number;      // offset from preset, % of frame height (-100 to 100)
  scale?: number;   // 0.1 to 3.0
  rotation?: number; // -180 to 180 degrees
  opacity?: number;  // 0 to 1
}
```

All fields optional. Defaults: `position: 'center'`, `x: 0`, `y: 0`, `scale: 1`, `rotation: 0`, `opacity: 1`.

### Entry changes

Add optional `transform?: TransformConfig` to `OverlayEntry`, `VisualEntry`, and footage rendering path. Example:

```json
{
  "type": "BULLET_LIST",
  "content": "GUILTY",
  "textColor": "red",
  "transform": {
    "position": "top-left",
    "x": 5,
    "y": 3,
    "scale": 1.0,
    "rotation": 0,
    "opacity": 1.0
  }
}
```

## Rendering Pipeline

### TransformWrapper component

New file: `web/src/components/remotion/TransformWrapper.tsx`

A React component that wraps any child with CSS positioning and transforms based on a `TransformConfig`. Uses Remotion's `AbsoluteFill` for full-frame positioning.

**Important:** The wrapper uses `display: 'flex', flexDirection: 'column'` (matching Remotion's AbsoluteFill default behavior) so that `justifyContent` controls vertical axis and `alignItems` controls horizontal axis.

**Bounded container approach:** The wrapper does NOT render children inside a full-frame AbsoluteFill. Instead, it uses an AbsoluteFill with flexbox for positioning, containing a **bounded div** that wraps the children. The bounded div has `position: relative` and constrains the child's dimensions (no `width: 100%; height: 100%`). This means children with their own AbsoluteFill (like TextOverlay, SourceBadge) will be bounded by the wrapper's container rather than filling the entire frame. This is how position overriding works — the child renders within a container that the wrapper positions.

**Position preset mapping:**

| Preset | justifyContent | alignItems | Padding |
|--------|---------------|------------|---------|
| top-left | flex-start | flex-start | 80px 60px 0 |
| top | flex-start | center | 80px 60px 0 |
| top-right | flex-start | flex-end | 80px 60px 0 |
| left | center | flex-start | 0 60px |
| center | center | center | 0 |
| right | center | flex-end | 0 60px |
| bottom-left | flex-end | flex-start | 0 60px 80px |
| bottom | flex-end | center | 0 60px 80px |
| bottom-right | flex-end | flex-end | 0 60px 80px |

**Offset:** Applied as `translate(x%, y%)` CSS transform on the content div.

**Scale/Rotation:** Applied as `scale(s) rotate(deg)` combined with the offset translate.

**Opacity:** Applied as CSS `opacity` on the outer wrapper.

**No-op behavior:** If `transform` is undefined or null, the wrapper still renders the wrapper div with identity styles (no visual change). This keeps the DOM structure stable — adding/removing a transform won't cause layout shifts or animation restarts in Remotion.

### BeeComposition integration

Wrap at three points:

**1. SegmentOverlays** — wrap each overlay component:
```tsx
<Sequence from={startFrame} durationInFrames={dur}>
  <TransformWrapper transform={entry.transform}>
    <Component content={entry.content} metadata={entry} durationInFrames={dur} />
  </TransformWrapper>
</Sequence>
```

**2. SegmentVisual** — wrap visual components and the hardcoded type blocks:
```tsx
<TransformWrapper transform={visual?.transform}>
  <VisualComponent content={...} metadata={visual} durationInFrames={...} />
</TransformWrapper>
```

**3. Footage/image rendering** — wrap the SafeImg/SafeVideo fallback path.

**Override behavior:** When `entry.transform` has a `position` set, the TransformWrapper controls positioning. The wrapper uses a bounded container approach — the child renders inside a constrained div, not a full-frame AbsoluteFill. This means components with internal positioning (TextOverlay's flexbox, SourceBadge's absolute offsets) are bounded by the wrapper's positioned container. The wrapper effectively controls where the child's rendering area is placed on screen, overriding the component's internal positioning.

## API Changes

### update-segment endpoint

**New `overlay_updates` path** in `PUT /api/projects/update-segment`. Follows the existing payload shape where updates are nested inside the `updates` object:

```json
{
  "segment_id": "seg-09",
  "updates": {
    "overlay_updates": [
      { "index": 0, "transform": { "position": "top-left", "x": 5, "y": 3 } }
    ]
  }
}
```

Same pattern as existing `visual_updates`:
- `index` identifies which overlay entry to update
- Remaining fields are merged onto `segment.overlay[index]`
- `transform` is deep-merged (setting `position` doesn't clear `scale`)
- Setting `transform: null` resets to defaults (removes the key)

**Extend `visual_updates`** to accept `transform`:
```json
{
  "updates": {
    "visual_updates": [
      { "index": 0, "transform": { "scale": 0.8, "rotation": -5 } }
    ]
  }
}
```

### project-store.ts changes

Add `overlay_updates` handling in `updateSegment()`:

```typescript
if (updates.overlay_updates) {
  for (const upd of updates.overlay_updates) {
    const { index, transform, ...rest } = upd;
    if (seg.overlay[index]) {
      // Deep-merge transform (don't let Object.assign clobber it)
      if (transform !== undefined && transform !== null) {
        seg.overlay[index].transform = {
          ...seg.overlay[index].transform,
          ...transform,
        };
      } else if (transform === null) {
        delete seg.overlay[index].transform;
      }
      // Merge remaining fields (non-transform)
      if (Object.keys(rest).length) {
        Object.assign(seg.overlay[index], rest);
      }
    }
  }
}
```

Same deep-merge pattern for `visual_updates.transform`.

## Props Panel UI

### TransformSection component

New section in `ClipProperties.tsx` that appears for ALL clip types (visual, overlay, audio is excluded).

**Layout:**
- 9-point position grid (3x3 buttons: TL, T, TR, L, C, R, BL, B, BR)
- Offset X slider (-100% to +100%, default 0)
- Offset Y slider (-100% to +100%, default 0)
- Scale slider (0.1 to 3.0, default 1.0)
- Rotation slider (-180° to +180°, default 0°)
- Opacity slider (0% to 100%, default 100%)
- Reset All button
- Configure toggle (⚙) to show/hide individual controls

**Behavior:**
- Clicking a position preset updates `transform.position` via API
- Moving a slider debounces (500ms) then updates via API
- Reset All sets `transform: null` via API
- Configure toggle persists visibility state to localStorage
- Position grid highlights the active preset
- All sliders show current numeric value

### Timeline adapter

Overlay clips on the OV1 track must be clickable and set `activeClipId` with the format `{segmentId}-ov-{index}` so ClipProperties can identify them.

## Storyboard Parser

Pass through `transform` field on overlay and visual entries in `web/shared/storyboard-parser.ts`. The parser already uses `[key: string]: any` on entries, so this should work without explicit handling — but verify and add explicit pass-through if needed.

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `web/shared/types.ts` | Modify | Add `TransformConfig` interface, add `transform?` to OverlayEntry + VisualEntry |
| `web/src/components/remotion/TransformWrapper.tsx` | Create | New wrapper component |
| `web/src/components/remotion/TransformWrapper.test.ts` | Create | Position preset mapping + transform CSS tests |
| `web/src/components/BeeComposition.tsx` | Modify | Wrap overlays, visuals, footage in TransformWrapper |
| `web/src/components/ClipProperties.tsx` | Modify | Add TransformSection |
| `web/server/services/project-store.ts` | Modify | Add overlay_updates + transform merge logic |
| `web/server/routes/projects.ts` | Modify | Accept overlay_updates in update-segment |
| `web/server/__tests__/routes.test.ts` | Modify | Add overlay_updates tests |
| `web/src/api/client.ts` | Modify | Add overlay_updates support to updateSegment method |
| `web/shared/storyboard-parser.ts` | Modify | Verify transform pass-through |
| `web/src/adapters/timeline-adapter.ts` | Modify | Ensure OV clips set activeClipId correctly |

## Out of Scope

- **No changes to existing 21 components** — they stay as-is
- **No deprecation of per-component position props** — they become defaults when no transform is set
- **No keyframe animation** — static transforms only
- **No drag-to-position on preview** — sliders and grid only
- **No enter/exit animation controls** — components keep their own animations
- **No separate X/Y scale** — uniform scale only
- **No anchor point control** — transforms apply from center
- **No z-index control** — overlay stacking follows render order
