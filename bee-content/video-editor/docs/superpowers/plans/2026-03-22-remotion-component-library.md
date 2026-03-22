# Remotion Component Library — Priority 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the primitives layer, plumbing changes, and Priority 1 components (Callout, KineticText) from the [Remotion Component Library spec](../specs/2026-03-22-remotion-component-library-design.md).

**Architecture:** Shared primitives (`QualityContext`, `SpringReveal`, `DrawPath`, `FitText`, `StaggerChildren`, `CountUp`) composed by new Remotion components. New visual/overlay types register via registries in `BeeComposition.tsx`. Storyboard parser and type maps updated to recognize new types.

**Tech Stack:** Remotion 4.x (`spring`, `interpolate`, `useCurrentFrame`, `Sequence`), `@remotion/paths`, `@remotion/shapes`, `@remotion/layout-utils`, `@remotion/motion-blur`, `@remotion/rounded-text-box`, React 19, TypeScript, vitest

**Spec:** `docs/superpowers/specs/2026-03-22-remotion-component-library-design.md`

---

## File Map

### New Files

| File | Responsibility |
|------|---------------|
| `web/src/components/remotion/primitives/QualityContext.tsx` | React context for quality tier + `useQuality()` hook |
| `web/src/components/remotion/primitives/SpringReveal.tsx` | Spring-based entrance wrapper |
| `web/src/components/remotion/primitives/DrawPath.tsx` | Animated SVG path drawing |
| `web/src/components/remotion/primitives/FitText.tsx` | Auto-sizing text wrapper |
| `web/src/components/remotion/primitives/StaggerChildren.tsx` | Staggered spring entrance for lists |
| `web/src/components/remotion/primitives/CountUp.tsx` | Animated number counter |
| `web/src/components/remotion/primitives/index.ts` | Barrel export for all primitives |
| `web/src/components/remotion/primitives/primitives.test.ts` | Tests for parsers and pure logic in primitives |
| `web/src/components/remotion/Callout.tsx` | Callout/annotation component (circle, arrow, box, underline, bracket). `zoom` style deferred — requires magnified inset logic. |
| `web/src/components/remotion/callout.test.ts` | Tests for Callout path generators and content parsing |
| `web/src/components/remotion/KineticText.tsx` | Kinetic typography (punch, flow, stack, highlight). `scatter` and `typewriter` presets deferred. |
| `web/src/components/remotion/kinetic-text.test.ts` | Tests for KineticText word parser and emphasis extraction |

### Modified Files

| File | Changes |
|------|---------|
| `web/shared/types.ts:77-86` | Add `quality?: 'standard' \| 'premium' \| 'social'` to `BeeProject` |
| `web/shared/storyboard-parser.ts:23-54` | Add new types to `VISUAL_TYPE_MAP` |
| `web/shared/storyboard-parser.ts:132-143` | Destructure `quality` from project config block |
| `web/src/adapters/timeline-adapter.ts:5-36` | Add new types to duplicated `VISUAL_TYPE_MAP` |
| `web/src/components/remotion/overlays.ts:1-22` | Add `DEFAULT_DURATIONS` entries for new types |
| `web/src/components/BeeComposition.tsx` | Add `VISUAL_COMPONENTS` registry, `QualityContext` provider, register new components |
| `web/src/components/remotion/overlays.test.ts` | Add tests for new overlays helpers |
| `web/package.json` | Add `@remotion/paths`, `@remotion/shapes`, `@remotion/layout-utils`, `@remotion/motion-blur`, `@remotion/rounded-text-box` |

---

## Task 1: Install new Remotion packages

**Files:**
- Modify: `web/package.json`

- [ ] **Step 1: Install packages**

```bash
cd bee-content/video-editor/web
npm install @remotion/paths@4.0.438 @remotion/shapes@4.0.438 @remotion/layout-utils@4.0.438 @remotion/motion-blur@4.0.438 @remotion/rounded-text-box@4.0.438
```

All `@remotion/*` packages must match the existing version (`4.0.438`) exactly. Check `package.json` to confirm all versions align.

- [ ] **Step 2: Verify build**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 3: Commit**

```bash
git add web/package.json web/package-lock.json
git commit -m "chore: add @remotion/paths, shapes, layout-utils, motion-blur, rounded-text-box"
```

---

## Task 2: Add `quality` field to types and parser

**Files:**
- Modify: `web/shared/types.ts:77-86`
- Modify: `web/shared/storyboard-parser.ts:132-143`

- [ ] **Step 1: Write failing test**

Create `web/shared/storyboard-parser.test.ts`:

```typescript
import { describe, test, expect } from 'vitest';
import { parseStoryboardMarkdown } from './storyboard-parser';

test('parses quality from project block', () => {
  const md = '```bee-video:project\n{"title":"Test","quality":"premium"}\n```\n';
  const project = parseStoryboardMarkdown(md);
  expect(project.quality).toBe('premium');
});

test('defaults quality to undefined when not set', () => {
  const md = '```bee-video:project\n{"title":"Test"}\n```\n';
  const project = parseStoryboardMarkdown(md);
  expect(project.quality).toBeUndefined();
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd bee-content/video-editor/web && npx vitest run --reporter=verbose 2>&1 | grep -E "quality|FAIL|PASS"
```

Expected: FAIL — `quality` not on `BeeProject` type, not parsed.

- [ ] **Step 3: Add quality to BeeProject type**

In `web/shared/types.ts`, add to the `BeeProject` interface after line 85 (`production: ProductionState;`):

```typescript
  quality?: 'standard' | 'premium' | 'social';
```

- [ ] **Step 4: Parse quality in storyboard parser**

In `web/shared/storyboard-parser.ts`, update the `projectConfig` type (around line 132):

```typescript
  let projectConfig: { title?: string; fps?: number; resolution?: [number, number]; quality?: 'standard' | 'premium' | 'social' } = {};
```

Then after line 143 (`const resolution = ...`), add:

```typescript
  const quality = projectConfig.quality;
```

Then in the return object (find `return { version: 1, title, fps, resolution, ...`), add `quality` to the returned object. Only include it if defined — use spread: `...(quality ? { quality } : {})`.

- [ ] **Step 5: Run test to verify it passes**

```bash
cd bee-content/video-editor/web && npx vitest run --reporter=verbose 2>&1 | grep -E "quality|FAIL|PASS"
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add web/shared/types.ts web/shared/storyboard-parser.ts web/shared/storyboard-parser.test.ts
git commit -m "feat: add quality tier to BeeProject type and storyboard parser"
```

---

## Task 3: Update VISUAL_TYPE_MAP in parser and timeline adapter

**Files:**
- Modify: `web/shared/storyboard-parser.ts:23-54`
- Modify: `web/src/adapters/timeline-adapter.ts:5-36`

- [ ] **Step 1: Write failing test**

```typescript
test('KINETIC_TEXT passes through visual type map', () => {
  const md = `### seg-01 | Test
\`\`\`bee-video:segment
{"visual":[{"type":"KINETIC_TEXT","src":null}],"audio":[],"overlay":[],"music":[]}
\`\`\``;
  const project = parseStoryboardMarkdown(md);
  expect(project.segments[0].visual[0].type).toBe('KINETIC_TEXT');
});

test('lowercase visual type maps via toUpperCase', () => {
  const md = `### seg-01 | Test
\`\`\`bee-video:segment
{"visual":[{"type":"kinetic_text","src":null}],"audio":[],"overlay":[],"music":[]}
\`\`\``;
  const project = parseStoryboardMarkdown(md);
  expect(project.segments[0].visual[0].type).toBe('KINETIC_TEXT');
});
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — `KINETIC_TEXT` not in map, gets normalized to `GRAPHIC`.

- [ ] **Step 3: Add new entries to both VISUAL_TYPE_MAP copies**

In `web/shared/storyboard-parser.ts`, add before the `// Standard types pass through` comment (around line 51):

```typescript
  // New component types (pass through)
  'KINETIC_TEXT': 'KINETIC_TEXT', 'KINETIC-TEXT': 'KINETIC_TEXT',
  'INFOGRAPHIC': 'INFOGRAPHIC',
  'SCREEN_MOCKUP': 'SCREEN_MOCKUP', 'SCREEN-MOCKUP': 'SCREEN_MOCKUP',
  'DATA_VIZ': 'DATA_VIZ', 'DATA-VIZ': 'DATA_VIZ',
  'TITLE_CARD': 'TITLE_CARD', 'TITLE-CARD': 'TITLE_CARD',
  'THREE_D': 'THREE_D', 'THREE-D': 'THREE_D',
  'LOTTIE': 'LOTTIE',
```

Add the exact same block to `web/src/adapters/timeline-adapter.ts` in its `VISUAL_TYPE_MAP`.

- [ ] **Step 4: Run test to verify it passes**

```bash
cd bee-content/video-editor/web && npx vitest run --reporter=verbose 2>&1 | tail -5
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add web/shared/storyboard-parser.ts web/src/adapters/timeline-adapter.ts
git commit -m "feat: add new component types to VISUAL_TYPE_MAP"
```

---

## Task 4: QualityContext primitive

**Files:**
- Create: `web/src/components/remotion/primitives/QualityContext.tsx`

- [ ] **Step 1: Write failing test**

Add to `web/src/components/remotion/primitives/primitives.test.ts` (create file):

```typescript
import { describe, test, expect } from 'vitest';
import { getSpringConfig, getTimingMultiplier } from './QualityContext';

describe('QualityContext helpers', () => {
  test('standard spring config', () => {
    const cfg = getSpringConfig('standard');
    expect(cfg.damping).toBe(12);
    expect(cfg.stiffness).toBe(150);
  });

  test('premium has lower stiffness for elegance', () => {
    const cfg = getSpringConfig('premium');
    expect(cfg.stiffness).toBeLessThan(getSpringConfig('standard').stiffness);
  });

  test('social has higher stiffness for snappiness', () => {
    const cfg = getSpringConfig('social');
    expect(cfg.stiffness).toBeGreaterThan(getSpringConfig('standard').stiffness);
  });

  test('timing multiplier scales duration', () => {
    expect(getTimingMultiplier('standard')).toBe(1);
    expect(getTimingMultiplier('premium')).toBeGreaterThan(1);
    expect(getTimingMultiplier('social')).toBeLessThan(1);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd bee-content/video-editor/web && npx vitest run primitives.test --reporter=verbose
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement QualityContext**

Create `web/src/components/remotion/primitives/QualityContext.tsx`:

```tsx
import { createContext, useContext } from 'react';

export type QualityTier = 'standard' | 'premium' | 'social';

export interface SpringConfig {
  mass: number;
  damping: number;
  stiffness: number;
  overshootClamping: boolean;
}

const SPRING_CONFIGS: Record<QualityTier, SpringConfig> = {
  standard: { mass: 1, damping: 12, stiffness: 150, overshootClamping: false },
  premium:  { mass: 1, damping: 8,  stiffness: 100, overshootClamping: false },
  social:   { mass: 1, damping: 20, stiffness: 250, overshootClamping: false },
};

const TIMING_MULTIPLIERS: Record<QualityTier, number> = {
  standard: 1.0,
  premium: 1.4,
  social: 0.7,
};

export function getSpringConfig(tier: QualityTier): SpringConfig {
  return SPRING_CONFIGS[tier];
}

export function getTimingMultiplier(tier: QualityTier): number {
  return TIMING_MULTIPLIERS[tier];
}

interface QualityContextValue {
  tier: QualityTier;
  springConfig: SpringConfig;
  timingMultiplier: number;
}

const QualityCtx = createContext<QualityContextValue>({
  tier: 'standard',
  springConfig: SPRING_CONFIGS.standard,
  timingMultiplier: 1.0,
});

export function QualityProvider({ tier = 'standard', children }: { tier?: QualityTier; children: React.ReactNode }) {
  const value: QualityContextValue = {
    tier,
    springConfig: getSpringConfig(tier),
    timingMultiplier: getTimingMultiplier(tier),
  };
  return <QualityCtx.Provider value={value}>{children}</QualityCtx.Provider>;
}

export function useQuality(): QualityContextValue {
  return useContext(QualityCtx);
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd bee-content/video-editor/web && npx vitest run primitives.test --reporter=verbose
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/primitives/
git commit -m "feat: add QualityContext primitive with tier-aware spring configs"
```

---

## Task 5: SpringReveal primitive

**Files:**
- Create: `web/src/components/remotion/primitives/SpringReveal.tsx`

- [ ] **Step 1: Implement SpringReveal**

This is a visual component that wraps children — unit testing React animation components requires Remotion's `<Composition>` context, so we test via integration in later tasks. Implement directly:

Create `web/src/components/remotion/primitives/SpringReveal.tsx`:

```tsx
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from './QualityContext';

type Direction = 'left' | 'right' | 'up' | 'down' | 'scale' | 'none';

interface Props {
  direction?: Direction;
  delay?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}

const OFFSETS: Record<Direction, { x: number; y: number; scale: number }> = {
  left:  { x: -100, y: 0, scale: 1 },
  right: { x: 100,  y: 0, scale: 1 },
  up:    { x: 0, y: -80,  scale: 1 },
  down:  { x: 0, y: 80,   scale: 1 },
  scale: { x: 0, y: 0,    scale: 0 },
  none:  { x: 0, y: 0,    scale: 1 },
};

export const SpringReveal: React.FC<Props> = ({
  direction = 'up',
  delay = 0,
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig } = useQuality();

  const progress = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: springConfig,
  });

  const offset = OFFSETS[direction];
  const x = offset.x * (1 - progress);
  const y = offset.y * (1 - progress);
  const scale = direction === 'scale'
    ? progress
    : 1;

  return (
    <AbsoluteFill
      style={{
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
        opacity: progress,
        ...style,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```

Expected: No errors related to SpringReveal.

- [ ] **Step 3: Commit**

```bash
git add web/src/components/remotion/primitives/SpringReveal.tsx
git commit -m "feat: add SpringReveal primitive with quality-aware spring physics"
```

---

## Task 6: DrawPath primitive

**Files:**
- Create: `web/src/components/remotion/primitives/DrawPath.tsx`

- [ ] **Step 1: Implement DrawPath**

Create `web/src/components/remotion/primitives/DrawPath.tsx`:

```tsx
import { useId } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { getLength } from '@remotion/paths';
import { useQuality } from './QualityContext';

interface Props {
  d: string;
  fromFrame?: number;
  toFrame?: number;
  strokeWidth?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const DrawPath: React.FC<Props> = ({
  d,
  fromFrame = 0,
  toFrame,
  strokeWidth = 3,
  color = '#dc2626',
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { tier } = useQuality();
  const filterId = useId(); // unique per instance to avoid SVG filter collisions

  const pathLength = getLength(d);
  const endFrame = toFrame ?? Math.round(fps * 0.8); // default: 0.8s draw

  const progress = interpolate(
    frame,
    [fromFrame, endFrame],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const dashOffset = pathLength * (1 - progress);

  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        ...style,
      }}
    >
      {/* Premium glow effect */}
      {tier === 'premium' && (
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth * 3}
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          opacity={0.2}
          filter={`url(#glow-${filterId})`}
        />
      )}
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={pathLength}
        strokeDashoffset={dashOffset}
        strokeLinecap="round"
      />
      {tier === 'premium' && (
        <defs>
          <filter id={`glow-${filterId}`}>
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      )}
    </svg>
  );
};
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: Commit**

```bash
git add web/src/components/remotion/primitives/DrawPath.tsx
git commit -m "feat: add DrawPath primitive with animated SVG stroke"
```

---

## Task 7: FitText, StaggerChildren, CountUp primitives + barrel export

**Files:**
- Create: `web/src/components/remotion/primitives/FitText.tsx`
- Create: `web/src/components/remotion/primitives/StaggerChildren.tsx`
- Create: `web/src/components/remotion/primitives/CountUp.tsx`
- Create: `web/src/components/remotion/primitives/index.ts`

- [ ] **Step 1: Implement FitText**

Create `web/src/components/remotion/primitives/FitText.tsx`:

```tsx
import { useCallback, useState, useEffect } from 'react';
import { continueRender, delayRender } from 'remotion';

interface Props {
  text: string;
  maxWidth: number;
  maxLines?: number;
  fontFamily?: string;
  fontWeight?: number | string;
  style?: React.CSSProperties;
}

export const FitText: React.FC<Props> = ({
  text,
  maxWidth,
  maxLines = 1,
  fontFamily = 'Arial, Helvetica, sans-serif',
  fontWeight = 700,
  style,
}) => {
  const [fontSize, setFontSize] = useState(48);
  const [handle] = useState(() => delayRender('FitText measuring'));

  useEffect(() => {
    // Binary search for the largest font size that fits
    let lo = 8;
    let hi = 200;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;

    while (lo < hi - 1) {
      const mid = Math.floor((lo + hi) / 2);
      ctx.font = `${fontWeight} ${mid}px ${fontFamily}`;
      const measured = ctx.measureText(text);
      const textWidth = measured.width;

      if (maxLines === 1) {
        if (textWidth <= maxWidth) lo = mid;
        else hi = mid;
      } else {
        // Approximate: check if text fits in maxWidth * maxLines worth of space
        const totalSpace = maxWidth * maxLines;
        if (textWidth <= totalSpace) lo = mid;
        else hi = mid;
      }
    }

    setFontSize(lo);
    continueRender(handle);
  }, [text, maxWidth, maxLines, fontFamily, fontWeight, handle]);

  return (
    <span
      style={{
        fontSize,
        fontFamily,
        fontWeight,
        lineHeight: 1.2,
        ...style,
      }}
    >
      {text}
    </span>
  );
};
```

- [ ] **Step 2: Implement StaggerChildren**

Create `web/src/components/remotion/primitives/StaggerChildren.tsx`:

```tsx
import React from 'react';
import { SpringReveal } from './SpringReveal';
import { useQuality } from './QualityContext';

type Direction = 'left' | 'right' | 'up' | 'down' | 'scale';

interface Props {
  interval?: number; // frames between each child
  direction?: Direction;
  children: React.ReactNode;
}

export const StaggerChildren: React.FC<Props> = ({
  interval = 8,
  direction = 'up',
  children,
}) => {
  const { timingMultiplier } = useQuality();
  const adjustedInterval = Math.round(interval * timingMultiplier);
  const childArray = React.Children.toArray(children);

  return (
    <>
      {childArray.map((child, i) => (
        <SpringReveal key={i} direction={direction} delay={i * adjustedInterval}>
          {child}
        </SpringReveal>
      ))}
    </>
  );
};
```

- [ ] **Step 3: Implement CountUp**

Create `web/src/components/remotion/primitives/CountUp.tsx`:

```tsx
import { useCurrentFrame, interpolate } from 'remotion';

interface Props {
  value: number;
  fromFrame?: number;
  toFrame?: number;
  format?: 'number' | 'currency' | 'percent';
  style?: React.CSSProperties;
}

export const CountUp: React.FC<Props> = ({
  value,
  fromFrame = 0,
  toFrame = 60,
  format = 'number',
  style,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(
    frame,
    [fromFrame, toFrame],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const current = Math.round(value * progress);

  let display: string;
  switch (format) {
    case 'currency':
      display = '$' + current.toLocaleString();
      break;
    case 'percent':
      display = current + '%';
      break;
    default:
      display = current.toLocaleString();
  }

  return <span style={style}>{display}</span>;
};
```

- [ ] **Step 4: Create barrel export**

Create `web/src/components/remotion/primitives/index.ts`:

```typescript
export { QualityProvider, useQuality, getSpringConfig, getTimingMultiplier } from './QualityContext';
export type { QualityTier, SpringConfig } from './QualityContext';
export { SpringReveal } from './SpringReveal';
export { DrawPath } from './DrawPath';
export { FitText } from './FitText';
export { StaggerChildren } from './StaggerChildren';
export { CountUp } from './CountUp';
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 6: Run all tests to confirm nothing broke**

```bash
cd bee-content/video-editor/web && npx vitest run --reporter=verbose 2>&1 | tail -10
```

Expected: All existing tests still pass.

- [ ] **Step 7: Commit**

```bash
git add web/src/components/remotion/primitives/
git commit -m "feat: add FitText, StaggerChildren, CountUp primitives + barrel export"
```

---

## Task 8: Update overlays.ts — add VisualProps, DEFAULT_DURATIONS, helper types

**Files:**
- Modify: `web/src/components/remotion/overlays.ts:1-22`
- Modify: `web/src/components/remotion/overlays.test.ts`

- [ ] **Step 1: Write failing test**

Add to `web/src/components/remotion/overlays.test.ts`:

```typescript
import { DEFAULT_DURATIONS } from './overlays';

describe('DEFAULT_DURATIONS for new components', () => {
  test('CALLOUT has a default duration', () => {
    expect(DEFAULT_DURATIONS.CALLOUT).toBe(4);
  });
  test('KINETIC_TEXT has a default duration', () => {
    expect(DEFAULT_DURATIONS.KINETIC_TEXT).toBe(5);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd bee-content/video-editor/web && npx vitest run overlays.test --reporter=verbose 2>&1 | grep -E "CALLOUT|KINETIC|FAIL|PASS"
```

Expected: FAIL

- [ ] **Step 3: Add new entries and VisualProps interface**

In `web/src/components/remotion/overlays.ts`, add to `DEFAULT_DURATIONS`:

```typescript
  CALLOUT: 4,
  KINETIC_TEXT: 5,
  LOTTIE: 4,
  ATMOSPHERE: 10,
  GLITCH: 3,
  INFOGRAPHIC: 8,
  DATA_VIZ: 6,
  TITLE_CARD: 4,
  SCREEN_MOCKUP: 10,
  THREE_D: 8,
```

Note: Both visual and overlay components use the existing `OverlayProps` interface (`content`, `metadata`, `durationInFrames`). No new interface needed — this matches how existing dual-mode components (TextChat, EvidenceBoard) work.

- [ ] **Step 4: Run test to verify it passes**

```bash
cd bee-content/video-editor/web && npx vitest run overlays.test --reporter=verbose 2>&1 | tail -10
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/overlays.ts web/src/components/remotion/overlays.test.ts
git commit -m "feat: add DEFAULT_DURATIONS for new types + VisualProps interface"
```

---

## Task 9: Callout component

**Files:**
- Create: `web/src/components/remotion/Callout.tsx`
- Create: `web/src/components/remotion/callout.test.ts`

- [ ] **Step 1: Write tests for path generators and content parsing**

Create `web/src/components/remotion/callout.test.ts`:

```typescript
import { describe, test, expect } from 'vitest';
import { circlePath, arrowPath, boxPath, underlinePath, bracketPath, parseCalloutData } from './Callout';

describe('Callout path generators', () => {
  test('circlePath generates valid SVG path', () => {
    const d = circlePath(960, 540, 100);
    expect(d).toMatch(/^M/); // starts with moveTo
    expect(d).toContain('A'); // has arc commands
  });

  test('arrowPath generates path from origin to target', () => {
    const d = arrowPath(100, 100, 500, 500);
    expect(d).toMatch(/^M/);
    expect(d).toContain('Q'); // quadratic curve
  });

  test('boxPath generates rect path', () => {
    const d = boxPath(400, 300, 300, 200, 8);
    expect(d).toMatch(/^M/);
  });

  test('underlinePath generates horizontal line', () => {
    const d = underlinePath(400, 600, 300);
    expect(d).toMatch(/^M/);
    expect(d).toContain('L');
  });

  test('bracketPath generates curly brace', () => {
    const d = bracketPath(400, 300, 200);
    expect(d).toMatch(/^M/);
  });
});

describe('parseCalloutData', () => {
  test('reads target from metadata', () => {
    const result = parseCalloutData('Label text', { target: [0.5, 0.5], style: 'circle' });
    expect(result.targetX).toBe(960);  // 0.5 * 1920
    expect(result.targetY).toBe(540);  // 0.5 * 1080
    expect(result.style).toBe('circle');
    expect(result.label).toBe('Label text');
  });

  test('defaults to center and circle', () => {
    const result = parseCalloutData('test', {});
    expect(result.targetX).toBe(960);
    expect(result.targetY).toBe(540);
    expect(result.style).toBe('circle');
  });

  test('reads animation mode', () => {
    const result = parseCalloutData('', { animation: 'pop' });
    expect(result.animation).toBe('pop');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd bee-content/video-editor/web && npx vitest run callout.test --reporter=verbose
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement Callout**

Create `web/src/components/remotion/Callout.tsx`. This is the largest component. Key structure:

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { DrawPath, SpringReveal, FitText, useQuality } from './primitives';
import type { OverlayProps } from './overlays';

// --- Path generators (exported for testing) ---

export function circlePath(cx: number, cy: number, r: number): string {
  return `M ${cx - r},${cy} A ${r},${r} 0 1,1 ${cx + r},${cy} A ${r},${r} 0 1,1 ${cx - r},${cy}`;
}

export function arrowPath(fromX: number, fromY: number, toX: number, toY: number): string {
  // Quadratic bezier with control point offset perpendicular to line
  const mx = (fromX + toX) / 2;
  const my = (fromY + toY) / 2;
  const dx = toX - fromX;
  const dy = toY - fromY;
  const cpX = mx - dy * 0.3;
  const cpY = my + dx * 0.3;
  return `M ${fromX},${fromY} Q ${cpX},${cpY} ${toX},${toY}`;
}

export function boxPath(x: number, y: number, w: number, h: number, r: number = 8): string {
  return `M ${x + r},${y} L ${x + w - r},${y} Q ${x + w},${y} ${x + w},${y + r} L ${x + w},${y + h - r} Q ${x + w},${y + h} ${x + w - r},${y + h} L ${x + r},${y + h} Q ${x},${y + h} ${x},${y + h - r} L ${x},${y + r} Q ${x},${y} ${x + r},${y} Z`;
}

export function underlinePath(x: number, y: number, width: number): string {
  return `M ${x},${y} L ${x + width},${y}`;
}

export function bracketPath(x: number, y: number, height: number): string {
  const midY = y + height / 2;
  const curveSize = 15;
  return `M ${x + curveSize},${y} Q ${x},${y} ${x},${y + curveSize} L ${x},${midY - curveSize} Q ${x},${midY} ${x - curveSize},${midY} Q ${x},${midY} ${x},${midY + curveSize} L ${x},${y + height - curveSize} Q ${x},${y + height} ${x + curveSize},${y + height}`;
}

// --- Parser ---

export interface CalloutData {
  label: string;
  style: string;
  animation: string;
  targetX: number;
  targetY: number;
  targetSize: number;
  color: string;
  labelPosition: string;
}

export function parseCalloutData(content: string, metadata: Record<string, any> | null | undefined): CalloutData {
  const m = metadata || {};
  const target = m.target || [0.5, 0.5];
  return {
    label: content || '',
    style: m.style || 'circle',
    animation: m.animation || 'draw',
    targetX: Math.round(target[0] * 1920),
    targetY: Math.round(target[1] * 1080),
    targetSize: m.targetSize || 80,
    color: m.color || '#dc2626',
    labelPosition: m.labelPosition || 'auto',
  };
}

// --- Generate SVG path for the callout shape ---

function generatePath(data: CalloutData): string {
  const { style, targetX, targetY, targetSize } = data;
  switch (style) {
    case 'circle':
      return circlePath(targetX, targetY, targetSize);
    case 'arrow': {
      // Arrow from 200px left of target to target
      const fromX = Math.max(100, targetX - 200);
      const fromY = Math.max(100, targetY - 150);
      return arrowPath(fromX, fromY, targetX, targetY);
    }
    case 'box':
      return boxPath(targetX - targetSize, targetY - targetSize / 2, targetSize * 2, targetSize, 8);
    case 'underline':
      return underlinePath(targetX - targetSize, targetY + 10, targetSize * 2);
    case 'bracket':
      return bracketPath(targetX - 20, targetY - targetSize, targetSize * 2);
    default:
      return circlePath(targetX, targetY, targetSize);
  }
}

// --- Label positioning ---

function labelPos(data: CalloutData): { x: number; y: number } {
  const { labelPosition, targetX, targetY, targetSize } = data;
  if (labelPosition === 'top') return { x: targetX, y: targetY - targetSize - 40 };
  if (labelPosition === 'bottom') return { x: targetX, y: targetY + targetSize + 20 };
  if (labelPosition === 'left') return { x: targetX - targetSize - 120, y: targetY };
  if (labelPosition === 'right') return { x: targetX + targetSize + 20, y: targetY };
  // auto: prefer bottom, flip to top if too close to bottom edge
  if (targetY > 800) return { x: targetX, y: targetY - targetSize - 40 };
  return { x: targetX, y: targetY + targetSize + 20 };
}

// --- Components ---

const CalloutInner: React.FC<{ content: string; metadata?: Record<string, any> | null; durationInFrames: number }> = ({
  content, metadata, durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const data = parseCalloutData(content, metadata);
  const path = generatePath(data);
  const pos = labelPos(data);

  const exitOpacity = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill style={{ opacity: exitOpacity }}>
      {data.animation === 'draw' && (
        <DrawPath d={path} strokeWidth={3} color={data.color} toFrame={Math.round(durationInFrames * 0.4)} />
      )}
      {data.animation === 'pop' && (
        <SpringReveal direction="scale">
          <svg viewBox="0 0 1920 1080" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
            <path d={path} fill="none" stroke={data.color} strokeWidth={3} strokeLinecap="round" />
          </svg>
        </SpringReveal>
      )}
      {data.animation === 'fade' && (
        <svg viewBox="0 0 1920 1080" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' }) }}>
          <path d={path} fill="none" stroke={data.color} strokeWidth={3} strokeLinecap="round" />
        </svg>
      )}
      {data.label && (
        <SpringReveal direction="up" delay={Math.round(durationInFrames * 0.3)}>
          <div style={{
            position: 'absolute',
            left: pos.x,
            top: pos.y,
            transform: 'translateX(-50%)',
            background: 'rgba(0,0,0,0.8)',
            color: '#fff',
            padding: '6px 16px',
            borderRadius: 6,
            fontSize: 22,
            fontFamily: 'Arial, Helvetica, sans-serif',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            borderLeft: `3px solid ${data.color}`,
          }}>
            {data.label}
          </div>
        </SpringReveal>
      )}
    </AbsoluteFill>
  );
};

// Overlay export (used in OVERLAY_COMPONENTS registry)
export const CalloutOverlay: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => (
  <CalloutInner content={content} metadata={metadata} durationInFrames={durationInFrames} />
);

// Visual export (full-screen with dark background)
export const Callout: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => (
  <AbsoluteFill style={{ backgroundColor: '#000' }}>
    <CalloutInner content={content} metadata={metadata} durationInFrames={durationInFrames} />
  </AbsoluteFill>
);
```

- [ ] **Step 4: Run tests**

```bash
cd bee-content/video-editor/web && npx vitest run callout.test --reporter=verbose
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/Callout.tsx web/src/components/remotion/callout.test.ts
git commit -m "feat: add Callout/Annotation component with 6 styles and 3 animations"
```

---

## Task 10: KineticText component

**Files:**
- Create: `web/src/components/remotion/KineticText.tsx`
- Create: `web/src/components/remotion/kinetic-text.test.ts`

- [ ] **Step 1: Write tests for word parser**

Create `web/src/components/remotion/kinetic-text.test.ts`:

```typescript
import { describe, test, expect } from 'vitest';
import { parseWords, parseKineticData } from './KineticText';

describe('parseWords', () => {
  test('splits plain text into words', () => {
    const words = parseWords('Hello world');
    expect(words).toEqual([
      { text: 'Hello', emphasis: 'none' },
      { text: 'world', emphasis: 'none' },
    ]);
  });

  test('detects *single* emphasis', () => {
    const words = parseWords('This is *important* stuff');
    expect(words[2]).toEqual({ text: 'important', emphasis: 'light' });
  });

  test('detects **double** emphasis', () => {
    const words = parseWords('This is **critical** stuff');
    expect(words[2]).toEqual({ text: 'critical', emphasis: 'heavy' });
  });

  test('handles mixed emphasis', () => {
    const words = parseWords('The *quick* **brown** fox');
    expect(words).toHaveLength(4);
    expect(words[1].emphasis).toBe('light');
    expect(words[2].emphasis).toBe('heavy');
  });

  test('handles empty string', () => {
    const words = parseWords('');
    expect(words).toEqual([{ text: '', emphasis: 'none' }]);
  });
});

describe('parseKineticData', () => {
  test('reads preset from metadata', () => {
    const result = parseKineticData('text', { preset: 'flow' });
    expect(result.preset).toBe('flow');
  });

  test('defaults to punch', () => {
    const result = parseKineticData('text', {});
    expect(result.preset).toBe('punch');
  });

  test('unknown preset falls back to punch at render time', () => {
    const result = parseKineticData('text', { preset: 'scatter' });
    expect(result.preset).toBe('scatter'); // stored as-is, fallback happens in component
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd bee-content/video-editor/web && npx vitest run kinetic-text.test --reporter=verbose
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement KineticText**

Create `web/src/components/remotion/KineticText.tsx`:

```tsx
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { useQuality } from './primitives';
import type { OverlayProps } from './overlays';

// --- Word parser (exported for testing) ---

export interface ParsedWord {
  text: string;
  emphasis: 'none' | 'light' | 'heavy';
}

export function parseWords(content: string): ParsedWord[] {
  const tokens = content.split(/\s+/);
  return tokens.map((token) => {
    if (token.startsWith('**') && token.endsWith('**')) {
      return { text: token.slice(2, -2), emphasis: 'heavy' as const };
    }
    if (token.startsWith('*') && token.endsWith('*')) {
      return { text: token.slice(1, -1), emphasis: 'light' as const };
    }
    return { text: token, emphasis: 'none' as const };
  });
}

export interface KineticData {
  words: ParsedWord[];
  preset: string;
  color: string;
  accentColor: string;
  background: string;
  position: string;
  align: string;
}

export function parseKineticData(content: string, metadata: Record<string, any> | null | undefined): KineticData {
  const m = metadata || {};
  return {
    words: parseWords(content),
    preset: m.preset || 'punch',
    color: m.color || '#ffffff',
    accentColor: m.accentColor || '#dc2626',
    background: m.background || 'none',
    position: m.position || 'center',
    align: m.align || 'center',
  };
}

// --- Position styling ---

function positionStyle(position: string): React.CSSProperties {
  switch (position) {
    case 'top': return { justifyContent: 'flex-start', paddingTop: 120 };
    case 'bottom': return { justifyContent: 'flex-end', paddingBottom: 120 };
    case 'lower-third': return { justifyContent: 'flex-end', paddingBottom: 200 };
    default: return { justifyContent: 'center' };
  }
}

// --- Preset: Punch (words slam in one at a time) ---

const PunchPreset: React.FC<{ data: KineticData; durationInFrames: number }> = ({ data, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const interval = Math.round(6 * timingMultiplier);

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: data.align === 'center' ? 'center' : data.align === 'right' ? 'flex-end' : 'flex-start', gap: '0 18px', padding: '0 120px' }}>
      {data.words.map((word, i) => {
        const delay = i * interval;
        const progress = spring({ frame: Math.max(0, frame - delay), fps, config: springConfig });
        const scale = word.emphasis === 'heavy' ? 1.3 : word.emphasis === 'light' ? 1.15 : 1;
        const wordColor = word.emphasis !== 'none' ? data.accentColor : data.color;

        return (
          <span
            key={i}
            style={{
              fontSize: 72,
              fontWeight: 800,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: wordColor,
              opacity: progress,
              transform: `scale(${progress * scale})`,
              display: 'inline-block',
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// --- Preset: Flow (words slide in from right) ---

const FlowPreset: React.FC<{ data: KineticData; durationInFrames: number }> = ({ data, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const interval = Math.round(4 * timingMultiplier);

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 14px', padding: '0 120px' }}>
      {data.words.map((word, i) => {
        const delay = i * interval;
        const progress = spring({ frame: Math.max(0, frame - delay), fps, config: { ...springConfig, overshootClamping: true } });
        const x = (1 - progress) * 60;
        const wordColor = word.emphasis !== 'none' ? data.accentColor : data.color;

        return (
          <span
            key={i}
            style={{
              fontSize: 64,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: wordColor,
              opacity: progress,
              transform: `translateX(${x}px)`,
              display: 'inline-block',
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// --- Preset: Stack (lines stack vertically) ---

const StackPreset: React.FC<{ data: KineticData; durationInFrames: number }> = ({ data, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  // Split into lines of ~4 words each
  const lines: ParsedWord[][] = [];
  for (let i = 0; i < data.words.length; i += 4) {
    lines.push(data.words.slice(i, i + 4));
  }

  const interval = Math.round(10 * timingMultiplier);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: data.align === 'center' ? 'center' : data.align === 'right' ? 'flex-end' : 'flex-start', gap: 12, padding: '0 120px' }}>
      {lines.map((line, li) => {
        const delay = li * interval;
        const progress = spring({ frame: Math.max(0, frame - delay), fps, config: springConfig });
        const y = (1 - progress) * 40;

        return (
          <div
            key={li}
            style={{
              opacity: progress,
              transform: `translateY(${y}px)`,
              display: 'flex',
              gap: 14,
            }}
          >
            {line.map((word, wi) => (
              <span
                key={wi}
                style={{
                  fontSize: 64,
                  fontWeight: 700,
                  fontFamily: 'Arial, Helvetica, sans-serif',
                  color: word.emphasis !== 'none' ? data.accentColor : data.color,
                }}
              >
                {word.text}
              </span>
            ))}
          </div>
        );
      })}
    </div>
  );
};

// --- Preset: Highlight (static text, background wipe on keywords) ---

const HighlightPreset: React.FC<{ data: KineticData; durationInFrames: number }> = ({ data, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { timingMultiplier } = useQuality();

  const baseOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  let emphasisIndex = 0;

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 14px', padding: '0 120px', opacity: baseOpacity }}>
      {data.words.map((word, i) => {
        const isEmphasis = word.emphasis !== 'none';
        let bgWidth = '0%';

        if (isEmphasis) {
          const highlightStart = 20 + emphasisIndex * Math.round(12 * timingMultiplier);
          const highlightEnd = highlightStart + 10;
          emphasisIndex++;
          const wipeProgress = interpolate(frame, [highlightStart, highlightEnd], [0, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          bgWidth = `${wipeProgress}%`;
        }

        return (
          <span
            key={i}
            style={{
              fontSize: 64,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: data.color,
              position: 'relative',
              display: 'inline-block',
            }}
          >
            {isEmphasis && (
              <span style={{
                position: 'absolute',
                left: -4,
                top: 0,
                bottom: 0,
                width: bgWidth,
                background: data.accentColor,
                opacity: 0.3,
                borderRadius: 4,
                zIndex: -1,
              }} />
            )}
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// --- Preset lookup ---

const PRESETS: Record<string, React.FC<{ data: KineticData; durationInFrames: number }>> = {
  punch: PunchPreset,
  flow: FlowPreset,
  stack: StackPreset,
  highlight: HighlightPreset,
};

// --- Background wrapper ---

function Background({ type, children }: { type: string; children: React.ReactNode }) {
  if (type === 'dark') return <AbsoluteFill style={{ backgroundColor: 'rgba(0,0,0,0.85)' }}>{children}</AbsoluteFill>;
  if (type === 'blur') return <AbsoluteFill style={{ backdropFilter: 'blur(12px)', backgroundColor: 'rgba(0,0,0,0.5)' }}>{children}</AbsoluteFill>;
  return <>{children}</>;
}

// --- Main component ---

const KineticTextInner: React.FC<{ content: string; metadata?: Record<string, any> | null; durationInFrames: number }> = ({
  content, metadata, durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const data = parseKineticData(content, metadata);

  const exitOpacity = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const Preset = PRESETS[data.preset] || PRESETS.punch;

  return (
    <AbsoluteFill style={{ ...positionStyle(data.position), alignItems: 'center', opacity: exitOpacity }}>
      <Background type={data.background}>
        <AbsoluteFill style={{ ...positionStyle(data.position), alignItems: 'center' }}>
          <Preset data={data} durationInFrames={durationInFrames} />
        </AbsoluteFill>
      </Background>
    </AbsoluteFill>
  );
};

// Overlay export
export const KineticTextOverlay: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => (
  <KineticTextInner content={content} metadata={metadata} durationInFrames={durationInFrames} />
);

// Visual export (full-screen with black bg)
export const KineticText: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => (
  <AbsoluteFill style={{ backgroundColor: '#000' }}>
    <KineticTextInner content={content} metadata={metadata} durationInFrames={durationInFrames} />
  </AbsoluteFill>
);
```

Note: `scatter` and `typewriter` presets are omitted from this initial implementation — they can be added as follow-up. The 4 presets above (`punch`, `flow`, `stack`, `highlight`) cover the most common use cases.

- [ ] **Step 4: Run tests**

```bash
cd bee-content/video-editor/web && npx vitest run kinetic-text.test --reporter=verbose
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/KineticText.tsx web/src/components/remotion/kinetic-text.test.ts
git commit -m "feat: add KineticText component with punch/flow/stack/highlight presets"
```

---

## Task 11: Wire everything into BeeComposition

**Files:**
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Add QualityProvider wrapper and new imports**

At the top of `BeeComposition.tsx`, add imports:

```typescript
import { QualityProvider } from './remotion/primitives';
import { CalloutOverlay, Callout } from './remotion/Callout';
import { KineticTextOverlay, KineticText } from './remotion/KineticText';
```

- [ ] **Step 2: Register in OVERLAY_COMPONENTS**

Add to the `OVERLAY_COMPONENTS` record:

```typescript
  CALLOUT: CalloutOverlay,
  KINETIC_TEXT: KineticTextOverlay,
```

- [ ] **Step 3: Add VISUAL_COMPONENTS registry**

After the `OVERLAY_COMPONENTS` declaration, add:

```typescript
const VISUAL_COMPONENTS: Record<string, React.FC<OverlayProps>> = {
  KINETIC_TEXT: KineticText,
  CALLOUT: Callout,
};
```

- [ ] **Step 4: Update SegmentVisual to use registry**

In the `SegmentVisual` function, before the existing `if (contentType === 'TEXT_CHAT')` block, add:

```typescript
  // Check new visual registry first
  const VisualComponent = VISUAL_COMPONENTS[contentType];
  if (VisualComponent) {
    const visual = seg.visual[0];
    return <VisualComponent content={visual?.content || ''} metadata={visual} durationInFrames={Math.round(seg.duration * fps)} />;
  }
```

Note: New visual components use `fps` from `useVideoConfig()`. The `SegmentVisual` function needs `fps` as a prop — add it to the function signature: `function SegmentVisual({ seg, knownFiles, fps }: { seg: BeeSegment; knownFiles: Set<string>; fps: number })` and pass it from the parent where `fps` is already available via `useVideoConfig()`.

- [ ] **Step 5: Wrap BeeComposition return in QualityProvider**

In the `BeeComposition` component, wrap the returned `<AbsoluteFill>` in a `<QualityProvider>`:

```tsx
  return (
    <QualityProvider tier={storyboard.quality}>
      <AbsoluteFill style={{ backgroundColor: '#000' }}>
        {/* ... existing content unchanged ... */}
      </AbsoluteFill>
    </QualityProvider>
  );
```

- [ ] **Step 6: Verify TypeScript compiles**

```bash
cd bee-content/video-editor/web && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 7: Run all tests**

```bash
cd bee-content/video-editor/web && npx vitest run --reporter=verbose 2>&1 | tail -10
```

Expected: All tests PASS (existing + new).

- [ ] **Step 8: Commit**

```bash
git add web/src/components/BeeComposition.tsx
git commit -m "feat: wire Callout + KineticText into BeeComposition with QualityProvider"
```

---

## Task 12: Manual smoke test

- [ ] **Step 1: Create a test storyboard**

Create a test storyboard markdown file with CALLOUT and KINETIC_TEXT segments to verify they render in the web editor. Write to a temp file:

```markdown
# Test New Components

```bee-video:project
{"title": "Component Test", "fps": 30, "resolution": [1920, 1080], "quality": "standard"}
```

## Test Section

### seg-01 | Kinetic Text Test

```bee-video:segment
{
  "visual": [{"type": "KINETIC_TEXT", "src": null, "content": "This is *really* **important**", "preset": "punch"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 5
}
```

### seg-02 | Callout Test

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "CALLOUT", "content": "Key evidence here", "style": "circle", "target": [0.5, 0.4], "animation": "draw"}],
  "music": [],
  "duration": 4
}
```
```

- [ ] **Step 2: Start the dev server and load the storyboard**

```bash
cd bee-content/video-editor/web && ./dev.sh
```

Open browser, load the test storyboard. Verify:
- seg-01 shows kinetic text with words appearing one at a time
- seg-02 shows a callout circle drawn at center with label text
- No console errors

- [ ] **Step 3: Production build**

```bash
cd bee-content/video-editor/web && npm run build
```

Expected: Build succeeds with no errors. This catches import issues that `tsc --noEmit` misses.

- [ ] **Step 4: Test quality tiers**

Change `"quality": "standard"` to `"premium"` and `"social"` in the test storyboard. Reload each time. Verify:
- `premium`: slower, smoother animations
- `social`: snappier, faster animations

---

## Summary

| Task | What | Commit message |
|------|------|---------------|
| 1 | Install packages | `chore: add @remotion/paths, shapes, layout-utils, motion-blur, rounded-text-box` |
| 2 | Quality type + parser | `feat: add quality tier to BeeProject type and storyboard parser` |
| 3 | VISUAL_TYPE_MAP entries | `feat: add new component types to VISUAL_TYPE_MAP` |
| 4 | QualityContext | `feat: add QualityContext primitive with tier-aware spring configs` |
| 5 | SpringReveal | `feat: add SpringReveal primitive with quality-aware spring physics` |
| 6 | DrawPath | `feat: add DrawPath primitive with animated SVG stroke` |
| 7 | FitText + StaggerChildren + CountUp | `feat: add FitText, StaggerChildren, CountUp primitives + barrel export` |
| 8 | overlays.ts updates | `feat: add DEFAULT_DURATIONS for new types + VisualProps interface` |
| 9 | Callout component | `feat: add Callout/Annotation component with 6 styles and 3 animations` |
| 10 | KineticText component | `feat: add KineticText component with punch/flow/stack/highlight presets` |
| 11 | Wire into BeeComposition | `feat: wire Callout + KineticText into BeeComposition with QualityProvider` |
| 12 | Manual smoke test | (no commit — verification only) |
