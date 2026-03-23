# Universal Transform Controls — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add universal position, scale, rotation, and opacity controls for all clips (overlays, visuals, footage) via a TransformWrapper component and a Props panel UI.

**Architecture:** A `TransformWrapper` component wraps every rendered element in BeeComposition.tsx, reading a nested `transform` object from each entry's data. The Props panel gets a new `TransformSection` with a 9-point position grid and sliders. The `update-segment` API gets an `overlay_updates` path and `transform` deep-merge support.

**Tech Stack:** React, Remotion, TypeScript, Vitest, Express

---

## File Map

### New files
| File | Purpose |
|------|---------|
| `web/shared/transform.ts` | `TransformConfig` interface + `POSITION_PRESETS` mapping + `resolveTransformStyle()` helper |
| `web/src/components/remotion/TransformWrapper.tsx` | Wrapper component — reads TransformConfig, applies CSS positioning + transforms |
| `web/src/components/remotion/TransformWrapper.test.ts` | Tests for position mapping, transform CSS output, no-op identity |
| `web/src/components/TransformSection.tsx` | Props panel section — position grid + sliders |

### Modified files
| File | Purpose |
|------|---------|
| `web/shared/types.ts` | Add `transform?: TransformConfig` to `OverlayEntry` + `VisualEntry` |
| `web/src/components/BeeComposition.tsx` | Wrap overlays, visuals, footage in TransformWrapper |
| `web/server/services/project-store.ts` | Add `overlay_updates` handler + `transform` deep-merge |
| `web/server/__tests__/routes.test.ts` | Tests for overlay_updates + transform merge |
| `web/src/components/ClipProperties.tsx` | Import + render TransformSection for visual/overlay clips |
| `web/src/api/client.ts` | Verify overlay_updates passthrough (may need no changes) |
| `web/shared/storyboard-parser.ts` | Verify transform passthrough |

---

## Task 1: TransformConfig type + position presets

**Files:**
- Create: `web/shared/transform.ts`
- Modify: `web/shared/types.ts`

- [ ] **Step 1: Create the TransformConfig type and position preset mapping**

Create `web/shared/transform.ts`:

```typescript
export interface TransformConfig {
  position?: 'top-left' | 'top' | 'top-right' | 'left' | 'center' | 'right' | 'bottom-left' | 'bottom' | 'bottom-right';
  x?: number;
  y?: number;
  scale?: number;
  rotation?: number;
  opacity?: number;
}

export type PositionPreset = NonNullable<TransformConfig['position']>;

export const POSITION_PRESETS: Record<PositionPreset, {
  justifyContent: string;
  alignItems: string;
  padding: string;
}> = {
  'top-left':     { justifyContent: 'flex-start', alignItems: 'flex-start', padding: '80px 60px 0' },
  'top':          { justifyContent: 'flex-start', alignItems: 'center',     padding: '80px 60px 0' },
  'top-right':    { justifyContent: 'flex-start', alignItems: 'flex-end',   padding: '80px 60px 0' },
  'left':         { justifyContent: 'center',     alignItems: 'flex-start', padding: '0 60px' },
  'center':       { justifyContent: 'center',     alignItems: 'center',     padding: '0' },
  'right':        { justifyContent: 'center',     alignItems: 'flex-end',   padding: '0 60px' },
  'bottom-left':  { justifyContent: 'flex-end',   alignItems: 'flex-start', padding: '0 60px 80px' },
  'bottom':       { justifyContent: 'flex-end',   alignItems: 'center',     padding: '0 60px 80px' },
  'bottom-right': { justifyContent: 'flex-end',   alignItems: 'flex-end',   padding: '0 60px 80px' },
};

export const TRANSFORM_DEFAULTS: Required<TransformConfig> = {
  position: 'center',
  x: 0,
  y: 0,
  scale: 1,
  rotation: 0,
  opacity: 1,
};
```

- [ ] **Step 2: Add `transform` to OverlayEntry and VisualEntry**

In `web/shared/types.ts`, add the import and field.

Add import at top:
```typescript
import type { TransformConfig } from './transform';
```

Add `transform?: TransformConfig;` to both `OverlayEntry` (after `animation?: string;`) and `VisualEntry` (after `kenBurns?: string;`).

- [ ] **Step 3: Verify storyboard parser passthrough**

Run: `cd web && npx vitest run shared/storyboard-parser.test.ts`

The parser uses `...rest` spread on entries so `transform` should pass through. If not, add explicit handling.

- [ ] **Step 4: Commit**

```bash
git add web/shared/transform.ts web/shared/types.ts
git commit -m "feat: add TransformConfig type and position presets"
```

---

## Task 2: TransformWrapper component (TDD)

**Files:**
- Create: `web/src/components/remotion/TransformWrapper.test.ts`
- Create: `web/src/components/remotion/TransformWrapper.tsx`

- [ ] **Step 1: Write failing tests**

Create `web/src/components/remotion/TransformWrapper.test.ts`:

```typescript
import { describe, test, expect } from 'vitest';
import { resolveTransformStyle } from './TransformWrapper';

describe('resolveTransformStyle', () => {
  test('returns identity styles for undefined transform', () => {
    const result = resolveTransformStyle(undefined);
    expect(result.outer.justifyContent).toBe('center');
    expect(result.outer.alignItems).toBe('center');
    expect(result.outer.opacity).toBe(1);
    expect(result.inner.transform).toBeUndefined();
  });

  test('returns identity styles for null transform', () => {
    const result = resolveTransformStyle(null);
    expect(result.outer.opacity).toBe(1);
  });

  test('maps position preset to flexbox styles', () => {
    const result = resolveTransformStyle({ position: 'top-left' });
    expect(result.outer.justifyContent).toBe('flex-start');
    expect(result.outer.alignItems).toBe('flex-start');
    expect(result.outer.padding).toBe('80px 60px 0');
  });

  test('maps bottom-right position', () => {
    const result = resolveTransformStyle({ position: 'bottom-right' });
    expect(result.outer.justifyContent).toBe('flex-end');
    expect(result.outer.alignItems).toBe('flex-end');
    expect(result.outer.padding).toBe('0 60px 80px');
  });

  test('applies offset as translate', () => {
    const result = resolveTransformStyle({ x: 10, y: -5 });
    expect(result.inner.transform).toBe('translate(10%, -5%) scale(1) rotate(0deg)');
  });

  test('applies scale and rotation', () => {
    const result = resolveTransformStyle({ scale: 1.5, rotation: 45 });
    expect(result.inner.transform).toBe('translate(0%, 0%) scale(1.5) rotate(45deg)');
  });

  test('applies opacity', () => {
    const result = resolveTransformStyle({ opacity: 0.5 });
    expect(result.outer.opacity).toBe(0.5);
  });

  test('combines all properties', () => {
    const result = resolveTransformStyle({
      position: 'top-right', x: 5, y: 3, scale: 0.8, rotation: -10, opacity: 0.9,
    });
    expect(result.outer.justifyContent).toBe('flex-start');
    expect(result.outer.alignItems).toBe('flex-end');
    expect(result.outer.opacity).toBe(0.9);
    expect(result.inner.transform).toBe('translate(5%, 3%) scale(0.8) rotate(-10deg)');
  });

  test('defaults position to center when not specified', () => {
    const result = resolveTransformStyle({ scale: 2 });
    expect(result.outer.justifyContent).toBe('center');
    expect(result.outer.alignItems).toBe('center');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npx vitest run src/components/remotion/TransformWrapper.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Implement TransformWrapper**

Create `web/src/components/remotion/TransformWrapper.tsx`:

```tsx
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { POSITION_PRESETS, TRANSFORM_DEFAULTS } from '../../../shared/transform';
import type { TransformConfig, PositionPreset } from '../../../shared/transform';

export function resolveTransformStyle(transform: TransformConfig | null | undefined) {
  const t = { ...TRANSFORM_DEFAULTS, ...transform };
  const preset = POSITION_PRESETS[t.position as PositionPreset] || POSITION_PRESETS.center;

  const hasTransform = t.x !== 0 || t.y !== 0 || t.scale !== 1 || t.rotation !== 0;

  return {
    outer: {
      display: 'flex' as const,
      flexDirection: 'column' as const,
      justifyContent: preset.justifyContent,
      alignItems: preset.alignItems,
      padding: preset.padding,
      opacity: t.opacity,
    },
    inner: {
      position: 'relative' as const,
      transform: hasTransform
        ? `translate(${t.x}%, ${t.y}%) scale(${t.scale}) rotate(${t.rotation}deg)`
        : undefined,
    },
  };
}

export const TransformWrapper: React.FC<{
  transform?: TransformConfig | null;
  children: React.ReactNode;
}> = ({ transform, children }) => {
  const styles = resolveTransformStyle(transform);

  return (
    <AbsoluteFill style={styles.outer}>
      <div style={styles.inner}>
        {children}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npx vitest run src/components/remotion/TransformWrapper.test.ts`
Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/TransformWrapper.tsx web/src/components/remotion/TransformWrapper.test.ts
git commit -m "feat: add TransformWrapper component with position presets"
```

---

## Task 3: Integrate TransformWrapper into BeeComposition

**Files:**
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Add import**

At the top of BeeComposition.tsx, after the existing component imports, add:

```typescript
import { TransformWrapper } from './remotion/TransformWrapper';
```

- [ ] **Step 2: Wrap SegmentVisual rendering**

In `SegmentVisual`, wrap each rendering path with `<TransformWrapper transform={visual?.transform}>`:

**Registry components** (around line 91-95): Wrap the `<VisualComponent>` call.

**Hardcoded type blocks** (TEXT_CHAT, WAVEFORM, SOCIAL_POST, MAP, EVIDENCE_BOARD): Wrap each component render.

**Footage/image fallback** (SafeImg/SafeVideo): Wrap the media rendering.

The pattern for each is:
```tsx
// Before:
return <VisualComponent content={...} metadata={visual} durationInFrames={...} />;

// After:
return (
  <TransformWrapper transform={visual?.transform}>
    <VisualComponent content={...} metadata={visual} durationInFrames={...} />
  </TransformWrapper>
);
```

- [ ] **Step 3: Wrap SegmentOverlays rendering**

In `SegmentOverlays`, wrap the overlay component render inside the `<Sequence>` (around line 167):

```tsx
// Before:
<Component content={entry.content} metadata={entry} durationInFrames={clampedDur} />

// After:
<TransformWrapper transform={entry.transform}>
  <Component content={entry.content} metadata={entry} durationInFrames={clampedDur} />
</TransformWrapper>
```

Also wrap the LOWER_THIRD special case (around line 152).

- [ ] **Step 4: Run existing tests to verify no regressions**

Run: `cd web && npx vitest run`
Expected: All existing tests PASS (the wrapper is identity by default)

- [ ] **Step 5: Commit**

```bash
git add web/src/components/BeeComposition.tsx
git commit -m "feat: wrap all visuals and overlays in TransformWrapper"
```

---

## Task 4: Backend — overlay_updates + transform deep-merge

**Files:**
- Modify: `web/server/services/project-store.ts`
- Modify: `web/server/__tests__/routes.test.ts`

- [ ] **Step 1: Write failing tests**

In `web/server/__tests__/routes.test.ts`, add these tests (after the existing visual_updates tests):

```typescript
// overlay_updates
test('PUT /api/projects/update-segment — overlay_updates sets transform', async () => {
  await loadProject(tmpDir, storyboardPath);

  // First verify the fixture has overlays — if not, use a segment that does
  const before = await request(app).get('/api/projects/current');
  const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
  if (!segWithOverlay) return; // skip if fixture has no overlays

  const res = await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: segWithOverlay.id,
      updates: {
        overlay_updates: [{ index: 0, transform: { position: 'top-left', x: 10, y: 5 } }],
      },
    });
  expect(res.status).toBe(200);

  const after = await request(app).get('/api/projects/current');
  const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
  expect(seg.overlay[0].transform).toEqual({ position: 'top-left', x: 10, y: 5 });
});

test('PUT /api/projects/update-segment — overlay transform deep-merges', async () => {
  await loadProject(tmpDir, storyboardPath);

  const before = await request(app).get('/api/projects/current');
  const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
  if (!segWithOverlay) return;

  // Set initial transform
  await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: segWithOverlay.id,
      updates: { overlay_updates: [{ index: 0, transform: { position: 'top-left', scale: 1.5 } }] },
    });

  // Deep-merge: change position, keep scale
  await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: segWithOverlay.id,
      updates: { overlay_updates: [{ index: 0, transform: { position: 'bottom-right' } }] },
    });

  const after = await request(app).get('/api/projects/current');
  const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
  expect(seg.overlay[0].transform.position).toBe('bottom-right');
  expect(seg.overlay[0].transform.scale).toBe(1.5); // preserved from first update
});

test('PUT /api/projects/update-segment — overlay transform null resets', async () => {
  await loadProject(tmpDir, storyboardPath);

  const before = await request(app).get('/api/projects/current');
  const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
  if (!segWithOverlay) return;

  // Set then reset
  await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: segWithOverlay.id,
      updates: { overlay_updates: [{ index: 0, transform: { position: 'top-left' } }] },
    });

  await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: segWithOverlay.id,
      updates: { overlay_updates: [{ index: 0, transform: null }] },
    });

  const after = await request(app).get('/api/projects/current');
  const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
  expect(seg.overlay[0].transform).toBeUndefined();
});

// visual_updates transform
test('PUT /api/projects/update-segment — visual_updates accepts transform', async () => {
  await loadProject(tmpDir, storyboardPath);

  const res = await request(app)
    .put('/api/projects/update-segment')
    .send({
      segment_id: 'seg-01',
      updates: { visual_updates: [{ index: 0, transform: { scale: 0.8, rotation: -5 } }] },
    });
  expect(res.status).toBe(200);

  const after = await request(app).get('/api/projects/current');
  const seg = after.body.segments.find((s: any) => s.id === 'seg-01');
  expect(seg.visual[0].transform).toEqual({ scale: 0.8, rotation: -5 });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npx vitest run server/__tests__/routes.test.ts`
Expected: FAIL — overlay_updates not handled, transform not deep-merged

- [ ] **Step 3: Add overlay_updates handler to project-store.ts**

In `web/server/services/project-store.ts`, inside `updateSegment()`, add after the `audio_updates` block (before `transition_in`):

```typescript
    // overlay_updates: [{index, transform?, ...rest}]
    if (Array.isArray(updates.overlay_updates)) {
      for (const u of updates.overlay_updates as Array<Record<string, any>>) {
        const { index, transform, ...rest } = u;
        if (typeof index === 'number' && seg.overlay[index]) {
          if (transform !== undefined && transform !== null) {
            seg.overlay[index].transform = {
              ...(seg.overlay[index] as any).transform,
              ...transform,
            };
          } else if (transform === null) {
            delete (seg.overlay[index] as any).transform;
          }
          if (Object.keys(rest).length) {
            Object.assign(seg.overlay[index], rest);
          }
        }
      }
    }
```

- [ ] **Step 4: Add transform deep-merge to visual_updates**

In the existing `visual_updates` block, replace the simple `Object.assign` with transform-aware merging:

```typescript
    if (Array.isArray(updates.visual_updates)) {
      for (const u of updates.visual_updates as Array<Record<string, any>>) {
        const { index, transform, ...rest } = u;
        if (typeof index === 'number' && seg.visual[index]) {
          if (transform !== undefined && transform !== null) {
            seg.visual[index].transform = {
              ...(seg.visual[index] as any).transform,
              ...transform,
            };
          } else if (transform === null) {
            delete (seg.visual[index] as any).transform;
          }
          if (Object.keys(rest).length) {
            Object.assign(seg.visual[index], rest);
          }
        }
      }
    }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd web && npx vitest run server/__tests__/routes.test.ts`
Expected: All tests PASS (existing + 4 new)

- [ ] **Step 6: Commit**

```bash
git add web/server/services/project-store.ts web/server/__tests__/routes.test.ts
git commit -m "feat: add overlay_updates and transform deep-merge to update-segment"
```

---

## Task 5: TransformSection UI component

**Files:**
- Create: `web/src/components/TransformSection.tsx`
- Modify: `web/src/components/ClipProperties.tsx`

- [ ] **Step 1: Create TransformSection component**

Create `web/src/components/TransformSection.tsx`:

```tsx
import { useState, useEffect, useRef } from 'react';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import type { TransformConfig, PositionPreset } from '../../shared/transform';
import { TRANSFORM_DEFAULTS } from '../../shared/transform';

const GRID_LABELS: PositionPreset[] = [
  'top-left', 'top', 'top-right',
  'left', 'center', 'right',
  'bottom-left', 'bottom', 'bottom-right',
];

const GRID_SHORT: Record<PositionPreset, string> = {
  'top-left': 'TL', 'top': 'T', 'top-right': 'TR',
  'left': 'L', 'center': 'C', 'right': 'R',
  'bottom-left': 'BL', 'bottom': 'B', 'bottom-right': 'BR',
};

interface Props {
  segmentId: string;
  clipType: 'v' | 'ov';
  layerIndex: number;
  segment: any;
}

export function TransformSection({ segmentId, clipType, layerIndex, segment }: Props) {
  const entry = clipType === 'v' ? segment.visual[layerIndex] : segment.overlay[layerIndex];
  if (!entry) return null;

  const current: TransformConfig = entry.transform || {};
  const pos = current.position || 'center';
  const [x, setX] = useState(current.x ?? 0);
  const [y, setY] = useState(current.y ?? 0);
  const [scale, setScale] = useState(current.scale ?? 1);
  const [rotation, setRotation] = useState(current.rotation ?? 0);
  const [opacity, setOpacity] = useState(current.opacity ?? 1);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync local state when segment data changes
  useEffect(() => {
    const t = entry.transform || {};
    setX(t.x ?? 0);
    setY(t.y ?? 0);
    setScale(t.scale ?? 1);
    setRotation(t.rotation ?? 0);
    setOpacity(t.opacity ?? 1);
  }, [entry.transform]);

  useEffect(() => {
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, []);

  const updateTransform = async (patch: Partial<TransformConfig>) => {
    try {
      const updateKey = clipType === 'v' ? 'visual_updates' : 'overlay_updates';
      await api.updateSegment(segmentId, {
        [updateKey]: [{ index: layerIndex, transform: patch }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const debouncedUpdate = (patch: Partial<TransformConfig>) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => updateTransform(patch), 500);
  };

  const handleReset = async () => {
    try {
      const updateKey = clipType === 'v' ? 'visual_updates' : 'overlay_updates';
      await api.updateSegment(segmentId, {
        [updateKey]: [{ index: layerIndex, transform: null }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
      toast.success('Transform reset');
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const [hiddenControls, setHiddenControls] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem('bee-transform-hidden');
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch { return new Set(); }
  });
  const [configuring, setConfiguring] = useState(false);

  const toggleControl = (key: string) => {
    const next = new Set(hiddenControls);
    if (next.has(key)) next.delete(key); else next.add(key);
    setHiddenControls(next);
    localStorage.setItem('bee-transform-hidden', JSON.stringify([...next]));
  };

  const isVisible = (key: string) => !hiddenControls.has(key);

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <div className="text-[9px] text-gray-500 uppercase tracking-wider">Transform</div>
        <button
          onClick={() => setConfiguring(!configuring)}
          className="text-[8px] text-gray-600 hover:text-gray-400"
        >
          ⚙ Configure
        </button>
      </div>

      {configuring && (
        <div className="mb-2 p-1.5 bg-editor-bg rounded border border-editor-border">
          {['position', 'offsetX', 'offsetY', 'scale', 'rotation', 'opacity'].map(key => (
            <label key={key} className="flex items-center gap-1.5 text-[8px] text-gray-500 cursor-pointer">
              <input
                type="checkbox"
                checked={isVisible(key)}
                onChange={() => toggleControl(key)}
                className="w-3 h-3"
              />
              {key}
            </label>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        {/* Position grid */}
        {isVisible('position') && (
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Position</div>
            <div className="grid grid-cols-3 gap-0.5" style={{ width: 78 }}>
              {GRID_LABELS.map(p => (
                <button
                  key={p}
                  onClick={() => updateTransform({ position: p })}
                  className={`h-5 rounded text-[7px] font-mono ${
                    pos === p
                      ? 'bg-blue-600 border-blue-500 text-white'
                      : 'bg-editor-bg border-editor-border text-gray-600 hover:text-gray-400'
                  } border`}
                >
                  {GRID_SHORT[p]}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Sliders */}
        <div className="flex-1 space-y-1.5">
          {isVisible('offsetX') && (
            <SliderControl
              label="Offset X" value={x} min={-100} max={100} step={1}
              format={v => `${v > 0 ? '+' : ''}${v}%`}
              onChange={v => { setX(v); debouncedUpdate({ x: v }); }}
            />
          )}
          {isVisible('offsetY') && (
            <SliderControl
              label="Offset Y" value={y} min={-100} max={100} step={1}
              format={v => `${v > 0 ? '+' : ''}${v}%`}
              onChange={v => { setY(v); debouncedUpdate({ y: v }); }}
            />
          )}
          {isVisible('scale') && (
            <SliderControl
              label="Scale" value={scale} min={0.1} max={3} step={0.05}
              format={v => `${v.toFixed(2)}x`}
              onChange={v => { setScale(v); debouncedUpdate({ scale: v }); }}
            />
          )}
          {isVisible('rotation') && (
            <SliderControl
              label="Rotation" value={rotation} min={-180} max={180} step={1}
              format={v => `${v}°`}
              onChange={v => { setRotation(v); debouncedUpdate({ rotation: v }); }}
            />
          )}
          {isVisible('opacity') && (
            <SliderControl
              label="Opacity" value={opacity} min={0} max={1} step={0.05}
              format={v => `${Math.round(v * 100)}%`}
              onChange={v => { setOpacity(v); debouncedUpdate({ opacity: v }); }}
            />
          )}
        </div>
      </div>

      <div className="mt-2">
        <button
          onClick={handleReset}
          className="bg-editor-bg border border-editor-border text-gray-600 text-[8px] px-2 py-0.5 rounded hover:text-gray-400"
        >
          Reset All
        </button>
      </div>
    </div>
  );
}

function SliderControl({ label, value, min, max, step, format, onChange }: {
  label: string; value: number; min: number; max: number; step: number;
  format: (v: number) => string; onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="flex justify-between items-center">
        <span className="text-[8px] text-gray-600">{label}</span>
        <span className="text-[9px] text-gray-500 font-mono">{format(value)}</span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full"
      />
    </div>
  );
}
```

- [ ] **Step 2: Wire TransformSection into ClipProperties**

In `web/src/components/ClipProperties.tsx`:

Add import at top:
```typescript
import { TransformSection } from './TransformSection';
```

In the return JSX (around line 75), add the TransformSection for visual and overlay clips. Add it as the first section inside `<div className="p-3 space-y-3">`:

```tsx
{(clipType === 'v' || clipType === 'ov') && layerIndex >= 0 && (
  <TransformSection segmentId={segmentId} clipType={clipType as 'v' | 'ov'} layerIndex={layerIndex} segment={segment} />
)}
```

- [ ] **Step 3: Run full test suite**

Run: `cd web && npx vitest run`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add web/src/components/TransformSection.tsx web/src/components/ClipProperties.tsx
git commit -m "feat: add TransformSection UI with position grid and sliders"
```

---

## Task 6: Verify end-to-end + parser passthrough

**Files:**
- Modify: `web/shared/storyboard-parser.ts` (if needed)
- Modify: `web/src/api/client.ts` (if needed)

- [ ] **Step 1: Verify API client passthrough**

Read `web/src/api/client.ts` — the `updateSegment` method accepts `Record<string, unknown>` and passes it through. No changes needed unless the signature is restrictive.

- [ ] **Step 2: Verify storyboard parser**

Create a test storyboard with a `transform` field on an overlay entry and load it:

```bash
curl -s -X POST http://localhost:8420/api/projects/load \
  -H "Content-Type: application/json" \
  -d '{"storyboard_path": "/path/to/test.md", "project_dir": "/path/to/dir"}'
```

Verify the `transform` object appears in the API response for that segment's overlay.

- [ ] **Step 3: Run full test suite**

Run: `cd web && npx vitest run`
Expected: All tests PASS

- [ ] **Step 4: Commit if any changes were needed**

```bash
git add -A
git commit -m "fix: ensure transform passthrough in parser and API client"
```

---

## Final Verification

- [ ] **Run full test suite**

```bash
cd web && npx vitest run
```

Expected: All tests pass including new TransformWrapper tests + overlay_updates route tests.

- [ ] **Visual test in browser**

1. Load a storyboard with overlays
2. Click an overlay clip on the OV1 timeline track
3. Verify the TransformSection appears in the Props panel
4. Change position preset → verify preview updates
5. Move scale/rotation/opacity sliders → verify preview updates
6. Click Reset All → verify everything returns to default
7. Click a visual clip on V1 → verify TransformSection also appears
