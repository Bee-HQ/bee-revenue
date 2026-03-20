# NLE Timeline Alpha Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the segment-list editor with a real NLE multi-track timeline (DesignCombo SDK) and composited preview (Remotion Player), keeping sidebars unchanged.

**Architecture:** DesignCombo's canvas-based timeline manages track/clip visualization and editing. Remotion Player renders composited video preview synced to the timeline scrubber. An adapter converts between our frontend `Storyboard` type and DesignCombo's state format. Zustand stays for app state; DesignCombo StateManager handles timeline state.

**Tech Stack:** React 18/19, TypeScript, Vite, Tailwind, @designcombo/state + timeline + types + events, @remotion/player + remotion, Zustand

**Spec:** `docs/superpowers/specs/2026-03-20-nle-timeline-alpha-design.md`

---

## File Map

### New Files

| File | Responsibility |
|------|---------------|
| `web/src/adapters/time-utils.ts` | Timecode ↔ frames ↔ milliseconds conversions |
| `web/src/adapters/time-utils.test.ts` | Unit tests for time conversions |
| `web/src/adapters/timeline-adapter.ts` | `storyboardToDesignCombo()` + `designComboToStoryboard()` |
| `web/src/adapters/timeline-adapter.test.ts` | Adapter round-trip tests |
| `web/src/components/TimelineEditor.tsx` | DesignCombo canvas mount + toolbar |
| `web/src/components/RemotionPreview.tsx` | Remotion Player wrapper + playback controls |
| `web/src/components/BeeComposition.tsx` | Remotion composition — segments as Sequences |
| `web/src/components/ProductionDropdown.tsx` | Dropdown menu for pipeline actions (Graphics, Narration, etc.) |

### Modified Files

| File | Change |
|------|--------|
| `web/package.json` | Add @designcombo/*, remotion, @remotion/player deps |
| `web/src/App.tsx` | Change undo/redo to dispatch DesignCombo events |
| `web/src/components/Layout.tsx` | Replace center + bottom with RemotionPreview + TimelineEditor |
| `web/src/components/SegmentList.tsx` | Click → seek timeline + player to segment position |
| `web/src/components/MediaLibrary.tsx` | Drag → dispatch DesignCombo ADD_VIDEO/ADD_AUDIO |

### Removed Files

| File | Reason |
|------|--------|
| `web/src/components/StoryboardTimeline.tsx` | Replaced by TimelineEditor |
| `web/src/components/VideoPlayer.tsx` | Replaced by RemotionPreview |
| `web/src/components/ProductionBar.tsx` | Replaced by timeline toolbar + ProductionDropdown |
| `web/src/components/SegmentCard.tsx` | Inline editing moves to timeline (beta) |
| `web/src/components/TransitionPicker.tsx` | Timeline handles transitions (beta) |
| `web/src/components/ColorGradePicker.tsx` | Clip properties (beta) |
| `web/src/components/VolumeSlider.tsx` | Clip properties (beta) |
| `web/src/components/TrimControls.tsx` | Timeline drag-to-trim (beta) |

---

## Task 1: Spike — Install Dependencies + Verify API

**This task is critical.** It verifies that DesignCombo and Remotion work with our React version and explores their actual APIs. If something doesn't work, we adapt the plan before building.

**Files:**
- Modify: `web/package.json`

- [ ] **Step 1: Create a feature branch**

```bash
cd bee-content/video-editor
git checkout -b bee/nle-timeline-alpha
```

- [ ] **Step 2: Install DesignCombo packages**

```bash
cd web
pnpm add @designcombo/state@5.5.8 @designcombo/timeline@5.5.8 @designcombo/types@5.5.8 @designcombo/events@5.5.8
```

If peer dependency errors occur with React 19, try:
```bash
pnpm add @designcombo/state@5.5.8 @designcombo/timeline@5.5.8 @designcombo/types@5.5.8 @designcombo/events@5.5.8 --force
```

If DesignCombo requires React 18, downgrade:
```bash
pnpm add react@^18.2.0 react-dom@^18.2.0 @types/react@^18.2.0 @types/react-dom@^18.2.0
```

- [ ] **Step 3: Install Remotion packages**

```bash
pnpm add remotion @remotion/player @remotion/cli
```

- [ ] **Step 4: Verify imports compile**

Create a temporary test file `web/src/spike-test.tsx`:

```tsx
// Verify all imports work
import StateManager from '@designcombo/state';
import { Timeline } from '@designcombo/timeline';
import { dispatch } from '@designcombo/events';
import { Player } from '@remotion/player';
import { Composition, Sequence, Video, useCurrentFrame } from 'remotion';

console.log('All imports OK', { StateManager, Timeline, dispatch, Player, Composition });
export {};
```

Run: `cd web && npx tsc --noEmit`

If this fails, document which package has the issue and what React version it needs. This determines the rest of the plan.

- [ ] **Step 5: Explore DesignCombo API surface**

Create `web/src/spike-designcombo.tsx` to test the actual API:

```tsx
import StateManager from '@designcombo/state';
import { Timeline } from '@designcombo/timeline';
import { dispatch, subject } from '@designcombo/events';

// Test StateManager initialization
const sm = new StateManager({ size: { width: 1920, height: 1080 }, fps: 30 });

// Check what methods/properties exist
console.log('StateManager methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(sm)));

// Check event names
console.log('dispatch type:', typeof dispatch);
console.log('subject type:', typeof subject);

// Test Timeline constructor signature
// NOTE: Don't actually mount — just check the constructor exists
console.log('Timeline constructor:', Timeline.toString().substring(0, 200));

export {};
```

Run the spike in the browser (vite dev server) and check the console output. Document:
- Exact constructor signatures for StateManager and Timeline
- Available event names (check the @designcombo/events exports)
- How to subscribe to state changes (RxJS observable? callback?)
- How Timeline mounts to a canvas element

- [ ] **Step 6: Document findings and commit**

Create `web/src/SPIKE-NOTES.md` with findings. Delete spike files.

```bash
git add web/package.json web/pnpm-lock.yaml web/src/SPIKE-NOTES.md
git commit -m "spike: install DesignCombo + Remotion, verify API surface"
```

---

## Task 2: Time Utilities

**Files:**
- Create: `web/src/adapters/time-utils.ts`
- Create: `web/src/adapters/time-utils.test.ts`

- [ ] **Step 1: Write tests**

```typescript
// web/src/adapters/time-utils.test.ts
import { describe, test, expect } from 'vitest';
import {
  parseTimecode, formatTimecode,
  timeToFrames, framesToTime,
  timeToMs, msToTime,
} from './time-utils';

describe('parseTimecode', () => {
  test('M:SS format', () => expect(parseTimecode('2:30')).toBe(150));
  test('H:MM:SS format', () => expect(parseTimecode('1:05:30')).toBe(3930));
  test('0:00', () => expect(parseTimecode('0:00')).toBe(0));
});

describe('formatTimecode', () => {
  test('minutes only', () => expect(formatTimecode(150)).toBe('2:30'));
  test('with hours', () => expect(formatTimecode(3930)).toBe('1:05:30'));
  test('zero', () => expect(formatTimecode(0)).toBe('0:00'));
});

describe('timeToFrames', () => {
  test('at 30fps', () => expect(timeToFrames(1, 30)).toBe(30));
  test('fractional seconds', () => expect(timeToFrames(0.5, 30)).toBe(15));
});

describe('framesToTime', () => {
  test('at 30fps', () => expect(framesToTime(30, 30)).toBe(1));
  test('round-trip', () => {
    const seconds = 42.5;
    expect(framesToTime(timeToFrames(seconds, 30), 30)).toBeCloseTo(seconds, 1);
  });
});

describe('timeToMs', () => {
  test('basic', () => expect(timeToMs(1.5)).toBe(1500));
});

describe('msToTime', () => {
  test('basic', () => expect(msToTime(1500)).toBe(1.5));
});
```

- [ ] **Step 2: Install vitest if not present**

```bash
cd web && pnpm add -D vitest
```

Add to `web/package.json` scripts: `"test": "vitest run"`, `"test:watch": "vitest"`

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd web && pnpm test`
Expected: FAIL — module not found

- [ ] **Step 4: Implement time-utils**

```typescript
// web/src/adapters/time-utils.ts

/** Parse "M:SS" or "H:MM:SS" timecode to seconds. */
export function parseTimecode(tc: string): number {
  const parts = tc.trim().split(':').map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return 0;
}

/** Format seconds to "M:SS" or "H:MM:SS". */
export function formatTimecode(seconds: number): string {
  const total = Math.round(seconds);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Convert seconds to frame count. */
export function timeToFrames(seconds: number, fps: number): number {
  return Math.round(seconds * fps);
}

/** Convert frame count to seconds. */
export function framesToTime(frames: number, fps: number): number {
  return frames / fps;
}

/** Seconds to milliseconds. */
export function timeToMs(seconds: number): number {
  return Math.round(seconds * 1000);
}

/** Milliseconds to seconds. */
export function msToTime(ms: number): number {
  return ms / 1000;
}
```

- [ ] **Step 5: Run tests**

Run: `cd web && pnpm test`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add web/src/adapters/
git commit -m "add time-utils: timecode, frames, milliseconds conversions"
```

---

## Task 3: Timeline Adapter

**Files:**
- Create: `web/src/adapters/timeline-adapter.ts`
- Create: `web/src/adapters/timeline-adapter.test.ts`

This is the hardest task — bidirectional conversion between our `Storyboard` and DesignCombo's state. The exact DesignCombo state shape depends on Task 1 spike findings. The plan below uses the documented API; adapt based on spike.

- [ ] **Step 1: Write adapter tests**

```typescript
// web/src/adapters/timeline-adapter.test.ts
import { describe, test, expect } from 'vitest';
import { storyboardToDesignCombo, designComboToStoryboard } from './timeline-adapter';
import type { Storyboard, Segment } from '../types';

const mockSegment: Segment = {
  id: 'cold-open',
  start: '0:00',
  end: '0:15',
  title: 'Cold Open',
  section: 'Act 1',
  section_time: '',
  subsection: '',
  duration_seconds: 15,
  visual: [{ content: 'footage/clip.mp4', content_type: 'FOOTAGE', time_start: null, time_end: null, raw: '', metadata: null }],
  audio: [{ content: 'narration text', content_type: 'NAR', time_start: null, time_end: null, raw: '', metadata: null }],
  overlay: [],
  music: [{ content: 'music/bg.mp3', content_type: 'MUSIC', time_start: null, time_end: null, raw: '', metadata: { volume: 0.2 } }],
  source: [],
  transition: [],
  assigned_media: { 'visual:0': 'footage/clip.mp4' },
};

const mockStoryboard: Storyboard = {
  title: 'Test Project',
  total_segments: 1,
  total_duration_seconds: 15,
  sections: ['Act 1'],
  segments: [mockSegment],
  stock_footage_needed: 0,
  photos_needed: 0,
  maps_needed: 0,
  production_rules: [],
};

describe('storyboardToDesignCombo', () => {
  test('creates 5 tracks', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    expect(state.tracks).toHaveLength(5);
    expect(state.tracks.map(t => t.id)).toEqual(['V1', 'A1', 'A2', 'A3', 'OV1']);
  });

  test('creates V1 item for visual entry', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const v1Items = state.trackItemIds.filter(id => state.trackItemsMap[id].trackId === 'V1');
    expect(v1Items.length).toBe(1);
  });

  test('positions item at correct time', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const v1Items = state.trackItemIds.filter(id => state.trackItemsMap[id].trackId === 'V1');
    const item = state.trackItemsMap[v1Items[0]];
    expect(item.display?.from).toBe(0); // starts at 0:00
    expect(item.display?.to).toBe(15000); // ends at 0:15 = 15000ms
  });

  test('creates A1 item for narration', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const a1Items = state.trackItemIds.filter(id => state.trackItemsMap[id].trackId === 'A1');
    expect(a1Items.length).toBe(1);
  });

  test('creates A3 item for music', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const a3Items = state.trackItemIds.filter(id => state.trackItemsMap[id].trackId === 'A3');
    expect(a3Items.length).toBe(1);
  });

  test('handles empty storyboard', () => {
    const empty: Storyboard = { ...mockStoryboard, segments: [], total_segments: 0 };
    const state = storyboardToDesignCombo(empty);
    expect(state.tracks).toHaveLength(5);
    expect(state.trackItemIds).toHaveLength(0);
  });
});

describe('designComboToStoryboard', () => {
  test('round-trips segment count', () => {
    const dcState = storyboardToDesignCombo(mockStoryboard);
    const result = designComboToStoryboard(dcState, mockStoryboard);
    expect(result.segments.length).toBe(mockStoryboard.segments.length);
  });

  test('preserves metadata fields', () => {
    const dcState = storyboardToDesignCombo(mockStoryboard);
    const result = designComboToStoryboard(dcState, mockStoryboard);
    expect(result.title).toBe(mockStoryboard.title);
    expect(result.sections).toEqual(mockStoryboard.sections);
  });
});
```

**Note:** The exact DesignCombo state shape (`tracks`, `trackItemIds`, `trackItemsMap`, `display.from/to`) is based on the documented API. Adapt after spike.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && pnpm test`

- [ ] **Step 3: Implement the adapter**

Build `web/src/adapters/timeline-adapter.ts`. Key logic:

1. `storyboardToDesignCombo()`:
   - Create 5 tracks: V1, A1, A2, A3, OV1
   - For each segment, iterate layer arrays and create track items
   - Position each item at `parseTimecode(seg.start)` → milliseconds
   - Duration from `seg.duration_seconds * 1000`
   - Store segment ID and layer index in item metadata for reverse mapping

2. `designComboToStoryboard()`:
   - Walk track items, group by segment ID (from metadata)
   - Rebuild segments with updated positions/durations
   - Preserve all fields from `original` storyboard that DesignCombo doesn't modify

The exact implementation depends heavily on Task 1 spike findings. Write the adapter after understanding DesignCombo's actual state shape.

- [ ] **Step 4: Run tests**

Run: `cd web && pnpm test`

- [ ] **Step 5: Commit**

```bash
git add web/src/adapters/
git commit -m "add timeline adapter: storyboard ↔ DesignCombo state conversion"
```

---

## Task 4: Remotion Preview Component

**Files:**
- Create: `web/src/components/RemotionPreview.tsx`
- Create: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Create the Remotion composition**

```tsx
// web/src/components/BeeComposition.tsx
import { AbsoluteFill, Sequence, Video, useVideoConfig } from 'remotion';
import type { Storyboard } from '../types';
import { parseTimecode, timeToFrames } from '../adapters/time-utils';
import { api } from '../api/client';

interface Props {
  storyboard: Storyboard;
}

function BlackFrame() {
  return <AbsoluteFill style={{ backgroundColor: '#0f0f0f' }} />;
}

export const BeeComposition: React.FC<Props> = ({ storyboard }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {storyboard.segments.map((seg) => {
        const src = seg.assigned_media['visual:0'];
        const from = timeToFrames(parseTimecode(seg.start), fps);
        const duration = timeToFrames(seg.duration_seconds, fps);

        if (!src || duration <= 0) return null;

        return (
          <Sequence key={seg.id} from={from} durationInFrames={duration}>
            <Video src={api.mediaFileUrl(src)} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Create the player wrapper**

```tsx
// web/src/components/RemotionPreview.tsx
import { useCallback, useRef, useState } from 'react';
import { Player, PlayerRef } from '@remotion/player';
import { useProjectStore } from '../stores/project';
import { BeeComposition } from './BeeComposition';
import { formatTimecode, framesToTime } from '../adapters/time-utils';

export function RemotionPreview() {
  const storyboard = useProjectStore(s => s.storyboard);
  const playerRef = useRef<PlayerRef>(null);
  const [currentFrame, setCurrentFrame] = useState(0);

  const fps = 30;
  const totalDuration = storyboard?.total_duration_seconds ?? 0;
  const totalFrames = Math.max(1, Math.round(totalDuration * fps));

  const handleFrameChange = useCallback((frame: number) => {
    setCurrentFrame(frame);
    // TODO: sync to DesignCombo timeline playhead
  }, []);

  if (!storyboard) return null;

  return (
    <div className="flex-1 bg-black flex flex-col">
      {/* Player */}
      <div className="flex-1 flex items-center justify-center">
        <Player
          ref={playerRef}
          component={BeeComposition}
          inputProps={{ storyboard }}
          durationInFrames={totalFrames}
          fps={fps}
          compositionWidth={1920}
          compositionHeight={1080}
          style={{ width: '100%', height: '100%' }}
          controls={false}
        />
      </div>

      {/* Playback controls */}
      <div className="bg-editor-surface border-t border-editor-border px-4 py-2 flex items-center gap-3">
        <span className="text-xs font-mono text-gray-500">
          {formatTimecode(framesToTime(currentFrame, fps))}
        </span>
        <button
          className="text-xs text-gray-400 hover:text-white"
          onClick={() => playerRef.current?.toggle()}
        >
          ▶ / ⏸
        </button>
        <div className="flex-1" />
        <span className="text-xs font-mono text-gray-500">
          {formatTimecode(totalDuration)}
        </span>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd web && npx tsc --noEmit`

- [ ] **Step 4: Commit**

```bash
git add web/src/components/RemotionPreview.tsx web/src/components/BeeComposition.tsx
git commit -m "add Remotion preview player with BeeComposition"
```

---

## Task 5: Timeline Editor Component

**Files:**
- Create: `web/src/components/TimelineEditor.tsx`
- Create: `web/src/components/ProductionDropdown.tsx`

This task depends heavily on Task 1 spike findings for DesignCombo's constructor API.

- [ ] **Step 1: Create ProductionDropdown**

```tsx
// web/src/components/ProductionDropdown.tsx
import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import { useProjectStore } from '../stores/project';

export function ProductionDropdown() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const run = async (name: string, action: () => Promise<any>) => {
    setOpen(false);
    toast.info(`${name}: starting...`);
    try {
      const r = await action();
      toast.success(`${name}: done`);
    } catch (e: any) {
      toast.error(`${name} failed: ${e.message}`);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
      >
        Pipeline ▾
      </button>
      {open && (
        <div className="absolute left-0 bottom-full mb-1 bg-editor-surface border border-editor-border rounded-lg shadow-lg py-1 w-44 z-50">
          {[
            ['Init Dirs', () => api.initProject()],
            ['Graphics', () => api.generateGraphics()],
            ['Narration', () => api.generateNarration()],
            ['Captions', () => api.generateCaptions()],
            ['Preflight', () => api.getPreflight()],
            ['Composite', () => api.compositeSegments()],
            ['Produce', () => api.connectProgress('produce', {}, () => {}, () => {}) as any],
            ['Assemble', () => api.assembleVideo()],
          ].map(([name, action]) => (
            <button
              key={name as string}
              onClick={() => run(name as string, action as () => Promise<any>)}
              className="w-full text-left px-3 py-1.5 text-[10px] text-gray-300 hover:bg-editor-hover"
            >
              {name as string}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create TimelineEditor shell**

```tsx
// web/src/components/TimelineEditor.tsx
import { useEffect, useRef } from 'react';
import { useProjectStore } from '../stores/project';
import { storyboardToDesignCombo } from '../adapters/timeline-adapter';
import { ProductionDropdown } from './ProductionDropdown';
import { api } from '../api/client';
import { toast } from '../stores/toast';

// DesignCombo imports — adapt based on spike findings
import StateManager from '@designcombo/state';
import { Timeline } from '@designcombo/timeline';
import { dispatch as dcDispatch } from '@designcombo/events';

export function TimelineEditor() {
  const storyboard = useProjectStore(s => s.storyboard);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const stateManagerRef = useRef<StateManager | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !storyboard) return;

    // Initialize DesignCombo
    const sm = new StateManager({
      size: { width: 1920, height: 1080 },
      fps: 30,
    });

    const totalMs = storyboard.total_duration_seconds * 1000;

    const tl = new Timeline(canvasRef.current, {
      scale: { unit: 300, zoom: 1 / 300, segments: 5, index: 7 },
      duration: totalMs,
      state: sm,
    });

    stateManagerRef.current = sm;
    timelineRef.current = tl;

    // Load storyboard into DesignCombo
    const dcState = storyboardToDesignCombo(storyboard);
    dcDispatch('design:load', { payload: dcState });

    return () => {
      // Cleanup — adapt based on spike (Timeline may have .destroy())
      timelineRef.current = null;
      stateManagerRef.current = null;
    };
  }, [storyboard]);

  return (
    <div className="border-t border-editor-border bg-editor-bg flex flex-col" style={{ height: 220 }}>
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-1.5 border-b border-editor-border bg-editor-surface">
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={async () => {
            try {
              const r = await api.autoAssign();
              toast.success(`Auto-assigned ${r.assigned} segments`);
              const sb = await api.getCurrentProject();
              useProjectStore.setState({ storyboard: sb });
            } catch (e: any) { toast.error(e.message); }
          }}
        >
          Auto-Assign
        </button>
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={async () => {
            try {
              const r = await api.acquireMedia();
              toast.success(`Acquired: ${r.downloaded} downloaded`);
              useProjectStore.getState().loadMedia();
            } catch (e: any) { toast.error(e.message); }
          }}
        >
          Acquire
        </button>
        <ProductionDropdown />
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={async () => {
            try {
              await api.roughCut();
              toast.success('Rough cut exported');
            } catch (e: any) { toast.error(e.message); }
          }}
        >
          Rough Cut
        </button>
        <div className="flex-1" />
        <span className="text-[9px] text-gray-600">Zoom:</span>
        <input type="range" min="1" max="10" defaultValue="4" className="w-16" style={{ accentColor: '#3b82f6' }} />
      </div>

      {/* DesignCombo Timeline Canvas */}
      <div className="flex-1 overflow-hidden">
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
    </div>
  );
}
```

**Note:** The DesignCombo constructor call, event dispatch, and cleanup will need adaptation based on Task 1 spike. This is the best-guess implementation from their docs.

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd web && npx tsc --noEmit`

- [ ] **Step 4: Commit**

```bash
git add web/src/components/TimelineEditor.tsx web/src/components/ProductionDropdown.tsx
git commit -m "add TimelineEditor with DesignCombo canvas and ProductionDropdown"
```

---

## Task 6: Wire Layout + Remove Old Components

**Files:**
- Modify: `web/src/components/Layout.tsx`
- Modify: `web/src/App.tsx`
- Delete: `web/src/components/StoryboardTimeline.tsx`
- Delete: `web/src/components/VideoPlayer.tsx`
- Delete: `web/src/components/ProductionBar.tsx`
- Delete: `web/src/components/SegmentCard.tsx`
- Delete: `web/src/components/TransitionPicker.tsx`
- Delete: `web/src/components/ColorGradePicker.tsx`
- Delete: `web/src/components/VolumeSlider.tsx`
- Delete: `web/src/components/TrimControls.tsx`

- [ ] **Step 1: Update Layout.tsx**

Replace the center and bottom sections:

```tsx
import { useProjectStore } from '../stores/project';
import { RemotionPreview } from './RemotionPreview';
import { TimelineEditor } from './TimelineEditor';
import { MediaLibrary } from './MediaLibrary';
import { SegmentList } from './SegmentList';
import { ExportMenu } from './ExportMenu';

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = storyboard.total_duration_seconds % 60;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-editor-surface border-b border-editor-border px-4 py-1.5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold">Bee Video Editor</h1>
          <span className="text-xs text-gray-500">|</span>
          <span className="text-xs text-gray-400 truncate max-w-md">{storyboard.title}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>{storyboard.total_segments} segments</span>
          <span>{totalMins}m {totalSecs}s</span>
          <span>{storyboard.sections.length} sections</span>
          <ExportMenu />
        </div>
      </header>

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Segment list */}
        <aside className="w-56 border-r border-editor-border flex flex-col shrink-0">
          <SegmentList />
        </aside>

        {/* Center: Preview + Timeline */}
        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          <RemotionPreview />
          <TimelineEditor />
        </main>

        {/* Right: Media library */}
        <aside className="w-56 border-l border-editor-border flex flex-col shrink-0">
          <MediaLibrary />
        </aside>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update App.tsx undo/redo**

Change undo/redo to dispatch DesignCombo events:

```tsx
import { useEffect } from 'react';
import { useProjectStore } from './stores/project';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';
import { ToastContainer } from './components/ToastContainer';
import { ShortcutsPanel } from './components/ShortcutsPanel';
import { dispatch } from '@designcombo/events';

export default function App() {
  const storyboard = useProjectStore(s => s.storyboard);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        dispatch('history:undo', {});
      }
      if (mod && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        dispatch('history:redo', {});
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  if (!storyboard) {
    return (
      <>
        <LoadProject />
        <ToastContainer />
        <ShortcutsPanel />
      </>
    );
  }

  return (
    <>
      <Layout />
      <ToastContainer />
      <ShortcutsPanel />
    </>
  );
}
```

- [ ] **Step 3: Delete old components**

```bash
rm web/src/components/StoryboardTimeline.tsx
rm web/src/components/VideoPlayer.tsx
rm web/src/components/ProductionBar.tsx
rm web/src/components/SegmentCard.tsx
rm web/src/components/TransitionPicker.tsx
rm web/src/components/ColorGradePicker.tsx
rm web/src/components/VolumeSlider.tsx
rm web/src/components/TrimControls.tsx
```

- [ ] **Step 4: Fix any import errors**

Run: `cd web && npx tsc --noEmit`

Fix any remaining imports that reference deleted components. The `SegmentList` may import `SegmentCard` — if so, simplify SegmentList to render segment rows directly without SegmentCard.

- [ ] **Step 5: Commit**

```bash
git add -u web/src/
git commit -m "wire new layout: RemotionPreview + TimelineEditor, remove old components"
```

---

## Task 7: Segment List → Timeline Seek

**Files:**
- Modify: `web/src/components/SegmentList.tsx`

- [ ] **Step 1: Update click handler to seek timeline + player**

When a segment is clicked in the left sidebar, the timeline playhead and Remotion player should jump to that segment's start time.

Read the current `SegmentList.tsx` to understand its structure. Update the click handler:

```typescript
// In the segment click handler:
import { parseTimecode, timeToMs } from '../adapters/time-utils';

const handleSegmentClick = (segId: string) => {
  const seg = storyboard.segments.find(s => s.id === segId);
  if (!seg) return;

  // Select in store
  toggleSegmentSelection(segId, false);

  // Seek timeline (DesignCombo) — adapt event name based on spike
  const ms = timeToMs(parseTimecode(seg.start));
  // dispatch('timeline:seek', { payload: { time: ms } });

  // Seek Remotion player — need a ref or global callback
  // This will be wired in Task 8 (scrubber sync)
};
```

- [ ] **Step 2: Remove drag-to-reorder if it conflicts with new timeline**

The segment list currently supports drag-to-reorder. For alpha, keep it — it still works via the backend. But remove any drag-drop media assignment code from SegmentList since that now happens on the timeline.

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd web && npx tsc --noEmit`

- [ ] **Step 4: Commit**

```bash
git add web/src/components/SegmentList.tsx
git commit -m "update SegmentList: click seeks timeline and player"
```

---

## Task 8: Scrubber Sync

**Files:**
- Modify: `web/src/components/TimelineEditor.tsx`
- Modify: `web/src/components/RemotionPreview.tsx`

Wire bidirectional sync between DesignCombo timeline playhead and Remotion Player position.

- [ ] **Step 1: Create a shared ref/context for player control**

Add to Zustand store or create a simple context:

```typescript
// Add to stores/project.ts:
playerRef: React.RefObject<PlayerRef> | null;
setPlayerRef: (ref: React.RefObject<PlayerRef>) => void;
seekTo: (frameOrMs: number) => void;
```

Or simpler: use a module-level ref that both components access.

- [ ] **Step 2: Wire Remotion → Timeline**

In `RemotionPreview.tsx`, on frame change, update timeline playhead:

```typescript
const handleFrameChange = useCallback((frame: number) => {
  setCurrentFrame(frame);
  // Update DesignCombo timeline playhead position
  // dispatch('timeline:seek', { payload: { time: framesToTime(frame, fps) * 1000 } });
}, [fps]);
```

- [ ] **Step 3: Wire Timeline → Remotion**

In `TimelineEditor.tsx`, subscribe to DesignCombo seek events and update Remotion:

```typescript
// After initializing StateManager, subscribe to seek events
// The exact API depends on spike findings
subject.subscribe((event) => {
  if (event.type === 'TIMELINE_SEEK' && playerRef.current) {
    const frame = timeToFrames(event.time / 1000, 30);
    playerRef.current.seekTo(frame);
  }
});
```

- [ ] **Step 4: Test manually**

Start dev server: `cd web && pnpm dev`
Load a project, scrub the timeline → verify player updates. Play → verify timeline playhead moves.

- [ ] **Step 5: Commit**

```bash
git add web/src/components/ web/src/stores/
git commit -m "wire scrubber sync between DesignCombo timeline and Remotion player"
```

---

## Task 9: End-to-End Verification + Cleanup

- [ ] **Step 1: TypeScript check**

```bash
cd web && npx tsc --noEmit
```

Fix any remaining type errors.

- [ ] **Step 2: Build check**

```bash
cd web && pnpm build
```

Fix any build errors.

- [ ] **Step 3: Manual end-to-end test**

Start backend + frontend:
```bash
cd bee-content/video-editor && ./dev.sh
```

Verify:
1. Load project → timeline shows tracks with clips
2. Remotion player shows video at playhead position
3. Scrub timeline → player updates
4. Play → sequential playback
5. Click segment in sidebar → playhead jumps
6. Export menu still works
7. Pipeline dropdown works (Graphics, Narration, etc.)

- [ ] **Step 4: Delete spike files**

```bash
rm -f web/src/spike-test.tsx web/src/spike-designcombo.tsx web/src/SPIKE-NOTES.md
```

- [ ] **Step 5: Backend tests still pass**

```bash
cd bee-content/video-editor && uv run --extra dev pytest tests/ -q
```

- [ ] **Step 6: Final commit**

```bash
git add -u .
git commit -m "finalize v0.9.0-alpha: NLE timeline with Remotion preview"
```

---

## Summary

| Task | What | Risk |
|------|------|------|
| 1 | **Spike** — install deps, verify API | HIGH — determines everything else |
| 2 | Time utilities | Low — pure functions |
| 3 | Timeline adapter | MEDIUM — depends on spike findings |
| 4 | Remotion preview | MEDIUM — Remotion Player API |
| 5 | Timeline editor | HIGH — DesignCombo canvas integration |
| 6 | Layout rewire + cleanup | Low — mechanical |
| 7 | Segment list seek | Low — click handler update |
| 8 | Scrubber sync | MEDIUM — bidirectional event wiring |
| 9 | E2E verification | Low — testing |

**Critical path:** Task 1 (spike) → Task 3 (adapter) → Task 5 (timeline) → Task 8 (sync)
