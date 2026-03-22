# Remotion Animated Overlays & Transitions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace static/missing overlay renderers and add transition rendering in BeeComposition — all storyboard visual elements become animated React components in the Remotion preview and MP4 export.

**Architecture:** Create 5 new Remotion components (QuoteCard, FinancialCard, TextOverlay, TimelineMarker, TransitionRenderer), extract 2 from BeeComposition (PlaceholderFrame, SafeMedia), refactor BeeComposition to use a registry-based overlay dispatch and `calculateSegmentPositions` for transition-aware frame positioning. Add `transitionMode` toggle to store and UI.

**Tech Stack:** Remotion (`interpolate`, `spring`, `useCurrentFrame`, `Sequence`, `AbsoluteFill`), React 19, Zustand, vitest

**Spec:** `docs/superpowers/specs/2026-03-21-remotion-overlays-transitions-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `web/src/components/remotion/PlaceholderFrame.tsx` | Create (extract) | Colored placeholder with type icon |
| `web/src/components/remotion/SafeMedia.tsx` | Create (extract) | SafeVideo + SafeImg with error fallback |
| `web/src/components/remotion/QuoteCard.tsx` | Create | Animated quote with accent bar |
| `web/src/components/remotion/FinancialCard.tsx` | Create | Counting dollar amount |
| `web/src/components/remotion/TextOverlay.tsx` | Create | Typewriter text |
| `web/src/components/remotion/TimelineMarker.tsx` | Create | Animated slide-in date stamp |
| `web/src/components/remotion/TransitionRenderer.tsx` | Create | Overlap + fade transition modes |
| `web/src/components/remotion/overlays.ts` | Create | Overlay registry + OverlayProps interface + helpers |
| `web/src/components/remotion/overlays.test.ts` | Create | Tests for parsing + position calculation |
| `web/src/components/BeeComposition.tsx` | Rewrite | Registry dispatch, transition positioning |
| `web/src/components/RemotionPreview.tsx` | Modify | Read `computedTotalFrames` for Player duration |
| `web/src/stores/project.ts` | Modify | Add `transitionMode` + `computedTotalFrames` |

---

### Task 1: Extract PlaceholderFrame and SafeMedia from BeeComposition

**Files:**
- Create: `web/src/components/remotion/PlaceholderFrame.tsx`
- Create: `web/src/components/remotion/SafeMedia.tsx`
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Create PlaceholderFrame.tsx**

Read BeeComposition.tsx. Extract the `PlaceholderFrame` function (lines 24-38) and `isRealFile` helper (lines 16-22) to a new file:

```tsx
// web/src/components/remotion/PlaceholderFrame.tsx
import { AbsoluteFill } from 'remotion';

const TYPE_COLORS: Record<string, string> = {
  STOCK: '#1e40af', MAP: '#166534', GRAPHIC: '#86198f',
  GENERATED: '#7c2d12', WAVEFORM: '#065f46', PHOTO: '#6b21a8',
};

const TYPE_ICONS: Record<string, string> = {
  STOCK: '📦', MAP: '🗺️', GRAPHIC: '🎨', GENERATED: '🤖',
};

export function PlaceholderFrame({ type, title }: { type: string; title: string }) {
  return (
    <AbsoluteFill style={{ backgroundColor: TYPE_COLORS[type] || '#1a1a1a', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 48 }}>{TYPE_ICONS[type] || '🎬'}</span>
      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 16, fontFamily: 'Arial' }}>{type}</span>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, fontFamily: 'Arial' }}>{title}</span>
    </AbsoluteFill>
  );
}

export function isRealFile(src: string | undefined): boolean {
  if (!src) return false;
  return src.includes('/') || /\.(mp4|mov|mkv|webm|avi|jpg|jpeg|png|webp|gif|mp3|wav|m4a)$/i.test(src);
}
```

- [ ] **Step 2: Create SafeMedia.tsx**

Extract `SafeVideo`, `SafeImg`, `mediaUrl`, `IMAGE_EXTS`, and `COLOR_FILTERS`:

```tsx
// web/src/components/remotion/SafeMedia.tsx
import { useState, useCallback } from 'react';
import { AbsoluteFill, Video, Img } from 'remotion';
import { PlaceholderFrame } from './PlaceholderFrame';

export function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

export const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'webp', 'gif']);

export const COLOR_FILTERS: Record<string, string> = {
  dark_crime: 'brightness(0.85) saturate(0.6) contrast(1.2) sepia(0.1)',
  surveillance: 'brightness(0.8) saturate(0.3) contrast(1.1) hue-rotate(90deg)',
  noir: 'brightness(0.9) saturate(0) contrast(1.3)',
  bodycam: 'brightness(0.85) saturate(0.5) contrast(1.1) sepia(0.15)',
  cold_blue: 'brightness(0.9) saturate(0.7) contrast(1.1) hue-rotate(200deg)',
  warm_victim: 'brightness(0.9) saturate(0.8) sepia(0.2)',
  sepia: 'brightness(0.95) saturate(0.5) sepia(0.6)',
  vintage: 'brightness(0.9) saturate(0.7) sepia(0.3) contrast(1.1)',
  bleach_bypass: 'brightness(1.1) saturate(0.4) contrast(1.4)',
  night_vision: 'brightness(0.7) saturate(0.3) hue-rotate(90deg) contrast(1.3)',
  golden_hour: 'brightness(1.05) saturate(1.2) sepia(0.15)',
  vhs: 'brightness(0.95) saturate(0.8) contrast(0.9)',
};

export function SafeVideo({ src, type, title, style }: { src: string; type: string; title: string; style?: React.CSSProperties }) {
  const [failed, setFailed] = useState(false);
  const handleError = useCallback(() => setFailed(true), []);
  if (failed) return <PlaceholderFrame type={type} title={`${title} (media unavailable)`} />;
  return <Video src={src} style={style} onError={handleError} />;
}

export function SafeImg({ src, type, title, style }: { src: string; type: string; title: string; style?: React.CSSProperties }) {
  const [failed, setFailed] = useState(false);
  const handleError = useCallback(() => setFailed(true), []);
  if (failed) return <PlaceholderFrame type={type} title={`${title} (media unavailable)`} />;
  return <Img src={src} style={style} onError={handleError} />;
}
```

- [ ] **Step 3: Update BeeComposition imports**

Replace inline definitions with imports:
```tsx
import { PlaceholderFrame, isRealFile } from './remotion/PlaceholderFrame';
import { SafeVideo, SafeImg, mediaUrl, IMAGE_EXTS, COLOR_FILTERS } from './remotion/SafeMedia';
```

Remove the extracted functions/constants from BeeComposition.tsx (lines 11-93 become imports).

- [ ] **Step 4: Verify build and tests**

```bash
cd bee-content/video-editor/web && npm run build 2>&1 | tail -5
npx vitest run 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/PlaceholderFrame.tsx web/src/components/remotion/SafeMedia.tsx web/src/components/BeeComposition.tsx
git commit -m "refactor: extract PlaceholderFrame and SafeMedia from BeeComposition"
```

---

### Task 2: Create overlay components (QuoteCard, FinancialCard, TextOverlay, TimelineMarker)

**Files:**
- Create: `web/src/components/remotion/overlays.ts`
- Create: `web/src/components/remotion/overlays.test.ts`
- Create: `web/src/components/remotion/QuoteCard.tsx`
- Create: `web/src/components/remotion/FinancialCard.tsx`
- Create: `web/src/components/remotion/TextOverlay.tsx`
- Create: `web/src/components/remotion/TimelineMarker.tsx`

- [ ] **Step 1: Create overlays.ts with shared types and parsers**

```ts
// web/src/components/remotion/overlays.ts
import type { LayerEntryMetadata } from '../../types';

export interface OverlayProps {
  content: string;
  metadata?: LayerEntryMetadata | null;
  durationInFrames: number;
}

export const DEFAULT_DURATIONS: Record<string, number> = {
  LOWER_THIRD: 4,      // seconds
  TIMELINE_MARKER: 3,
  QUOTE_CARD: 4,
  FINANCIAL_CARD: 3,
  TEXT_OVERLAY: 3,
};

/** Parse "quote text — Author" into parts */
export function parseQuoteContent(content: string): { quote: string; author: string } {
  const parts = content.split(/\s*[—–]\s*/);
  return { quote: parts[0]?.trim() || content, author: parts[1]?.trim() || '' };
}

/** Parse "$1.4 million — Description" into parts */
export function parseDollarAmount(text: string): { displayValue: string; numericValue: number; description: string } {
  const parts = text.split(/\s*[—–]\s*/);
  const dollarPart = parts[0]?.trim() || text;
  const description = parts[1]?.trim() || '';

  const cleaned = dollarPart.replace(/[$,]/g, '').trim();
  const match = cleaned.match(/^([\d.]+)\s*(million|billion|thousand|k|m|b)?/i);
  if (!match) return { displayValue: dollarPart, numericValue: 0, description };

  const num = parseFloat(match[1]);
  const multipliers: Record<string, number> = { thousand: 1e3, k: 1e3, million: 1e6, m: 1e6, billion: 1e9, b: 1e9 };
  const mult = match[2] ? (multipliers[match[2].toLowerCase()] || 1) : 1;
  const numericValue = num * mult;
  return { displayValue: dollarPart, numericValue, description };
}

/** Parse "Name — Role" for LowerThird adapter */
export function parseLowerThirdContent(content: string): { name: string; role?: string } {
  const parts = content.split(/\s*[—–-]\s*/);
  return { name: parts[0]?.trim() || content, role: parts[1]?.trim() || undefined };
}
```

- [ ] **Step 2: Write tests**

```ts
// web/src/components/remotion/overlays.test.ts
import { describe, test, expect } from 'vitest';
import { parseQuoteContent, parseDollarAmount, parseLowerThirdContent } from './overlays';

describe('parseQuoteContent', () => {
  test('splits on em dash', () => {
    const r = parseQuoteContent('"Justice was served" — Prosecutor');
    expect(r.quote).toBe('"Justice was served"');
    expect(r.author).toBe('Prosecutor');
  });
  test('handles missing author', () => {
    const r = parseQuoteContent('Just a quote');
    expect(r.quote).toBe('Just a quote');
    expect(r.author).toBe('');
  });
});

describe('parseDollarAmount', () => {
  test('parses $1.4 million', () => {
    const r = parseDollarAmount('$1.4 million — Insurance payout');
    expect(r.numericValue).toBe(1400000);
    expect(r.description).toBe('Insurance payout');
  });
  test('parses $14,000', () => {
    const r = parseDollarAmount('$14,000 — Legal fees');
    expect(r.numericValue).toBe(14000);
    expect(r.description).toBe('Legal fees');
  });
  test('parses $500K', () => {
    const r = parseDollarAmount('$500K');
    expect(r.numericValue).toBe(500000);
  });
  test('handles unparseable', () => {
    const r = parseDollarAmount('a lot of money');
    expect(r.numericValue).toBe(0);
    expect(r.displayValue).toBe('a lot of money');
  });
});

describe('parseLowerThirdContent', () => {
  test('splits name and role', () => {
    const r = parseLowerThirdContent('Alex Murdaugh — Defendant');
    expect(r.name).toBe('Alex Murdaugh');
    expect(r.role).toBe('Defendant');
  });
  test('name only', () => {
    const r = parseLowerThirdContent('Moselle Estate');
    expect(r.name).toBe('Moselle Estate');
    expect(r.role).toBeUndefined();
  });
});
```

- [ ] **Step 3: Run tests**

```bash
npx vitest run src/components/remotion/overlays.test.ts
```
Expected: All pass

- [ ] **Step 4: Create QuoteCard.tsx**

```tsx
// web/src/components/remotion/QuoteCard.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';
import { parseQuoteContent } from './overlays';

const ACCENT_COLORS: Record<string, string> = {
  red: '#dc2626', teal: '#0d9488', gold: '#d97706',
};

export const QuoteCard: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { quote, author } = parseQuoteContent(content);
  const accentColor = ACCENT_COLORS[metadata?.color || 'red'] || ACCENT_COLORS.red;

  const backdropOpacity = interpolate(frame, [0, 10], [0, 0.8], { extrapolateRight: 'clamp' });
  const barX = spring({ frame: frame - 5, fps, config: { stiffness: 200, damping: 20 } });
  const quoteOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const authorOpacity = interpolate(frame, [25, 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity: exitOpacity, maxWidth: 800, padding: '0 60px' }}>
        <div style={{ background: `rgba(0,0,0,${backdropOpacity})`, padding: '40px 48px', borderRadius: 4, position: 'relative' }}>
          <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 6, background: accentColor, transform: `scaleY(${barX})`, transformOrigin: 'top' }} />
          <div style={{ opacity: quoteOpacity, color: '#fff', fontSize: 36, fontWeight: 300, fontFamily: 'Georgia, serif', fontStyle: 'italic', lineHeight: 1.4 }}>
            {quote}
          </div>
          {author && (
            <div style={{ opacity: authorOpacity, color: '#d1d5db', fontSize: 20, fontFamily: 'Arial', marginTop: 16 }}>
              — {author}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 5: Create FinancialCard.tsx**

```tsx
// web/src/components/remotion/FinancialCard.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';
import { parseDollarAmount } from './overlays';

export const FinancialCard: React.FC<OverlayProps> = ({ content, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { displayValue, numericValue, description } = parseDollarAmount(content);

  const slideUp = spring({ frame, fps, config: { stiffness: 180, damping: 18 } });
  const translateY = interpolate(slideUp, [0, 1], [100, 0]);

  // Count up animation
  const countProgress = interpolate(frame, [10, 60], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const currentValue = numericValue > 0 ? Math.round(numericValue * countProgress) : 0;
  const formattedValue = numericValue > 0 ? `$${currentValue.toLocaleString()}` : displayValue;

  const descOpacity = interpolate(frame, [40, 55], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exitY = interpolate(frame, [durationInFrames - 15, durationInFrames], [0, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 0 120px' }}>
      <div style={{ transform: `translateY(${translateY + exitY}%)`, background: 'rgba(220, 38, 38, 0.9)', padding: '24px 48px', borderRadius: 4, textAlign: 'center' }}>
        <div style={{ color: '#fff', fontSize: 56, fontWeight: 800, fontFamily: 'Arial', letterSpacing: -1 }}>
          {formattedValue}
        </div>
        {description && (
          <div style={{ opacity: descOpacity, color: 'rgba(255,255,255,0.8)', fontSize: 20, fontFamily: 'Arial', marginTop: 8 }}>
            {description}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 6: Create TextOverlay.tsx**

```tsx
// web/src/components/remotion/TextOverlay.tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from './overlays';

export const TextOverlay: React.FC<OverlayProps> = ({ content, durationInFrames }) => {
  const frame = useCurrentFrame();

  // Typewriter: reveal characters over first 60% of duration
  const typingEnd = Math.floor(durationInFrames * 0.6);
  const charsToShow = Math.floor(interpolate(frame, [0, typingEnd], [0, content.length], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
  const visibleText = content.slice(0, charsToShow);

  // Blinking cursor
  const cursorVisible = frame < typingEnd ? Math.floor(frame / 8) % 2 === 0 : false;

  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', opacity: exitOpacity }}>
      <div style={{ background: 'rgba(0,0,0,0.7)', padding: '20px 40px', borderRadius: 8, maxWidth: '70%' }}>
        <span style={{ color: '#fff', fontSize: 36, fontWeight: 600, fontFamily: 'Arial', lineHeight: 1.4 }}>
          {visibleText}
        </span>
        {cursorVisible && <span style={{ color: '#3b82f6', fontSize: 36, fontWeight: 300 }}>|</span>}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 7: Create TimelineMarker.tsx**

```tsx
// web/src/components/remotion/TimelineMarker.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';

export const TimelineMarker: React.FC<OverlayProps> = ({ content, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({ frame, fps, config: { stiffness: 200, damping: 20 } });
  const translateX = interpolate(slideIn, [0, 1], [100, 0]);

  const textOpacity = interpolate(frame, [10, 20], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const slideOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [0, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'flex-end', padding: '40px 0' }}>
      <div style={{ transform: `translateX(${translateX + slideOut}%)`, background: 'rgba(220, 38, 38, 0.9)', padding: '8px 24px 8px 20px', borderRadius: '4px 0 0 4px' }}>
        <span style={{ opacity: textOpacity, color: '#fff', fontSize: 24, fontWeight: 700, fontFamily: 'Arial' }}>
          {content}
        </span>
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 8: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/components/remotion/overlays.ts web/src/components/remotion/overlays.test.ts web/src/components/remotion/QuoteCard.tsx web/src/components/remotion/FinancialCard.tsx web/src/components/remotion/TextOverlay.tsx web/src/components/remotion/TimelineMarker.tsx
git commit -m "feat: animated overlay components (QuoteCard, FinancialCard, TextOverlay, TimelineMarker)"
```

---

### Task 3: Create TransitionRenderer

**Files:**
- Create: `web/src/components/remotion/TransitionRenderer.tsx`
- Modify: `web/src/components/remotion/overlays.ts` (add position calculator)
- Modify: `web/src/components/remotion/overlays.test.ts` (add transition tests)

- [ ] **Step 1: Add calculateSegmentPositions to overlays.ts**

Append to `web/src/components/remotion/overlays.ts`:

```ts
import type { Segment } from '../../types';
import { parseTimecode } from '../../adapters/time-utils';

export interface TransitionInfo {
  type: string;
  durationInFrames: number;
}

export interface SegmentPosition {
  segId: string;
  from: number;
  duration: number;
  transitionIn?: TransitionInfo;
}

export function getTransitionInfo(seg: Segment, fps: number): TransitionInfo | null {
  const trans = seg.transition[0];
  if (!trans) return null;
  const durationSec = parseFloat(trans.content?.replace('s', '') || '1');
  return { type: trans.content_type, durationInFrames: Math.round(durationSec * fps) };
}

export function calculateSegmentPositions(
  segments: Segment[],
  fps: number,
  mode: 'overlap' | 'fade',
): { positions: SegmentPosition[]; totalFrames: number } {
  const positions: SegmentPosition[] = [];

  if (mode === 'fade') {
    // Absolute positioning from timecodes
    let maxFrame = 0;
    for (const seg of segments) {
      const from = Math.round(parseTimecode(seg.start) * fps);
      const duration = Math.round(seg.duration_seconds * fps);
      if (duration <= 0) continue;
      const transInfo = getTransitionInfo(seg, fps);
      positions.push({ segId: seg.id, from, duration, transitionIn: transInfo || undefined });
      maxFrame = Math.max(maxFrame, from + duration);
    }
    return { positions, totalFrames: Math.max(1, maxFrame) };
  }

  // Overlap mode: sequential, transitions eat into duration
  let currentFrame = 0;
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const duration = Math.round(seg.duration_seconds * fps);
    if (duration <= 0) continue;
    const transInfo = getTransitionInfo(seg, fps);
    // Clamp transition to segment duration
    if (transInfo && transInfo.durationInFrames > duration) {
      transInfo.durationInFrames = duration;
    }
    positions.push({ segId: seg.id, from: currentFrame, duration, transitionIn: transInfo || undefined });
    const overlap = (i < segments.length - 1 && transInfo) ? transInfo.durationInFrames : 0;
    currentFrame += duration - overlap;
  }
  return { positions, totalFrames: Math.max(1, currentFrame) };
}
```

- [ ] **Step 2: Add position calculation tests**

Append to `web/src/components/remotion/overlays.test.ts`:

```ts
import { calculateSegmentPositions, getTransitionInfo } from './overlays';
import type { Segment } from '../../types';

const makeSeg = (id: string, start: string, dur: number, trans?: { type: string; content: string }): Segment => ({
  id, start, end: '', title: id, section: '', section_time: '', subsection: '',
  duration_seconds: dur,
  visual: [], audio: [], overlay: [], music: [], source: [],
  transition: trans ? [{ content: trans.content, content_type: trans.type, time_start: null, time_end: null, raw: '', metadata: null }] : [],
  assigned_media: {},
});

describe('getTransitionInfo', () => {
  test('parses 1.0s dissolve', () => {
    const seg = makeSeg('s1', '0:00', 15, { type: 'DISSOLVE', content: '1.0s' });
    const info = getTransitionInfo(seg, 30);
    expect(info).toEqual({ type: 'DISSOLVE', durationInFrames: 30 });
  });
  test('returns null when no transition', () => {
    const seg = makeSeg('s1', '0:00', 15);
    expect(getTransitionInfo(seg, 30)).toBeNull();
  });
});

describe('calculateSegmentPositions', () => {
  test('fade mode uses absolute timecodes', () => {
    const segs = [makeSeg('s1', '0:00', 15), makeSeg('s2', '0:15', 15)];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(450); // 15s * 30fps
    expect(totalFrames).toBe(900);
  });

  test('overlap mode shrinks total duration', () => {
    const segs = [
      makeSeg('s1', '0:00', 15),
      makeSeg('s2', '0:15', 15, { type: 'DISSOLVE', content: '1.0s' }),
    ];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(420); // 450 - 30 (1s overlap)
    expect(totalFrames).toBe(870); // 900 - 30
  });

  test('skips zero-duration segments', () => {
    const segs = [makeSeg('s1', '0:00', 15), makeSeg('s2', '0:15', 0), makeSeg('s3', '0:15', 10)];
    const { positions } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions).toHaveLength(2);
  });

  test('clamps transition longer than segment', () => {
    const segs = [
      makeSeg('s1', '0:00', 2),
      makeSeg('s2', '0:02', 1, { type: 'DISSOLVE', content: '5.0s' }),
    ];
    const { positions } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[1].transitionIn!.durationInFrames).toBe(30); // clamped to 1s segment
  });
});
```

- [ ] **Step 3: Run tests**

```bash
npx vitest run src/components/remotion/overlays.test.ts
```

- [ ] **Step 4: Create TransitionRenderer.tsx**

```tsx
// web/src/components/remotion/TransitionRenderer.tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { ReactNode } from 'react';

interface OverlapProps {
  type: string;
  durationInFrames: number;
  mode: 'overlap';
  outgoing: ReactNode;
  incoming: ReactNode;
}

interface FadeProps {
  type: string;
  durationInFrames: number;
  mode: 'fade';
  position: 'in' | 'out';
  children: ReactNode;
}

type Props = OverlapProps | FadeProps;

export const TransitionRenderer: React.FC<Props> = (props) => {
  const frame = useCurrentFrame();
  const { type, durationInFrames, mode } = props;

  if (mode === 'overlap') {
    const { outgoing, incoming } = props as OverlapProps;

    if (type === 'FADE_FROM_BLACK') {
      const incomingOpacity = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
      return (
        <AbsoluteFill>
          <AbsoluteFill style={{ backgroundColor: '#000' }} />
          <AbsoluteFill style={{ opacity: incomingOpacity }}>{incoming}</AbsoluteFill>
        </AbsoluteFill>
      );
    }

    // DISSOLVE (default)
    const outgoingOpacity = interpolate(frame, [0, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    const incomingOpacity = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ opacity: outgoingOpacity }}>{outgoing}</AbsoluteFill>
        <AbsoluteFill style={{ opacity: incomingOpacity }}>{incoming}</AbsoluteFill>
      </AbsoluteFill>
    );
  }

  // Fade mode
  const { position, children } = props as FadeProps;
  const fadeFrames = Math.min(15, durationInFrames);

  if (type === 'FADE_FROM_BLACK' && position === 'in') {
    const opacity = interpolate(frame, [0, fadeFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
  }

  if (position === 'out') {
    const segDuration = durationInFrames;
    const opacity = interpolate(frame, [segDuration - fadeFrames, segDuration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
  }

  // Default: fade in
  const opacity = interpolate(frame, [0, fadeFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};
```

- [ ] **Step 5: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/components/remotion/TransitionRenderer.tsx web/src/components/remotion/overlays.ts web/src/components/remotion/overlays.test.ts
git commit -m "feat: TransitionRenderer with overlap/fade modes + position calculator"
```

---

### Task 4: Add transitionMode to store and UI

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/components/RemotionPreview.tsx`

- [ ] **Step 1: Add to store**

In `ProjectState` interface, add:
```ts
transitionMode: 'overlap' | 'fade';
computedTotalFrames: number | null;
setTransitionMode: (mode: 'overlap' | 'fade') => void;
setComputedTotalFrames: (frames: number) => void;
```

Initial values:
```ts
transitionMode: (() => {
  try { return (localStorage.getItem('bee-editor-transition-mode') as 'overlap' | 'fade') || 'overlap'; }
  catch { return 'overlap' as const; }
})(),
computedTotalFrames: null,
```

Implementations:
```ts
setTransitionMode: (mode) => {
  set({ transitionMode: mode });
  try { localStorage.setItem('bee-editor-transition-mode', mode); } catch {}
},
setComputedTotalFrames: (frames) => set({ computedTotalFrames: frames }),
```

- [ ] **Step 2: Update RemotionPreview to use computedTotalFrames**

In RemotionPreview.tsx, read from store:
```ts
const computedTotalFrames = useProjectStore(s => s.computedTotalFrames);
const transitionMode = useProjectStore(s => s.transitionMode);
```

Change `totalFrames` calculation:
```ts
const totalFrames = computedTotalFrames ?? Math.max(1, Math.round(totalDuration * FPS));
```

Pass `transitionMode` to BeeComposition:
```tsx
inputProps={{ storyboard, mediaFiles: mediaFilePaths, showCaptions, transitionMode }}
```

Add transition mode toggle button next to CC button:
```tsx
<button
  onClick={() => {
    const next = transitionMode === 'overlap' ? 'fade' : 'overlap';
    useProjectStore.getState().setTransitionMode(next);
  }}
  className={`text-[10px] px-1.5 py-0.5 rounded border ${
    transitionMode === 'overlap'
      ? 'text-blue-400 border-blue-600/50 bg-blue-600/10'
      : 'text-gray-500 border-editor-border'
  }`}
  title={`Transition mode: ${transitionMode}`}
>
  {transitionMode === 'overlap' ? 'X-Fade' : 'Fade'}
</button>
```

- [ ] **Step 3: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/stores/project.ts web/src/components/RemotionPreview.tsx
git commit -m "feat: transitionMode toggle in store and preview controls"
```

---

### Task 5: Rewrite BeeComposition with overlay registry and transitions

**Files:**
- Rewrite: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Rewrite BeeComposition.tsx**

Complete rewrite using:
- Imports from extracted files (PlaceholderFrame, SafeMedia)
- Imports overlay components + registry
- `calculateSegmentPositions` for frame positions
- `TransitionRenderer` for transition rendering
- `transitionMode` prop
- `useEffect` to set `computedTotalFrames` in store

Key structure:
```tsx
import { useEffect } from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import type { Storyboard, Segment } from '../types';
import { parseTimecode, timeToFrames } from '../adapters/time-utils';
import { useProjectStore } from '../stores/project';
import { PlaceholderFrame, isRealFile } from './remotion/PlaceholderFrame';
import { SafeVideo, SafeImg, mediaUrl, IMAGE_EXTS, COLOR_FILTERS } from './remotion/SafeMedia';
import { KenBurns } from './remotion/KenBurns';
import { LowerThird } from './remotion/LowerThird';
import { CaptionOverlay } from './remotion/CaptionOverlay';
import { QuoteCard } from './remotion/QuoteCard';
import { FinancialCard } from './remotion/FinancialCard';
import { TextOverlay } from './remotion/TextOverlay';
import { TimelineMarker } from './remotion/TimelineMarker';
import { TransitionRenderer } from './remotion/TransitionRenderer';
import { calculateSegmentPositions, parseLowerThirdContent, DEFAULT_DURATIONS } from './remotion/overlays';
import type { OverlayProps } from './remotion/overlays';

const OVERLAY_COMPONENTS: Record<string, React.FC<OverlayProps>> = {
  QUOTE_CARD: QuoteCard,
  FINANCIAL_CARD: FinancialCard,
  TEXT_OVERLAY: TextOverlay,
  TIMELINE_MARKER: TimelineMarker,
};

// Renders the visual layer for a single segment (video/image/placeholder + color grade + Ken Burns)
function SegmentVisual({ seg, knownFiles }: { seg: Segment; knownFiles: Set<string> }) {
  const src = seg.assigned_media['visual:0'];
  const ext = src?.split('.').pop()?.toLowerCase() ?? '';
  const isImage = IMAGE_EXTS.has(ext);
  const contentType = seg.visual[0]?.content_type || 'NONE';
  const colorPreset = seg.visual[0]?.metadata?.color;
  const colorFilter = colorPreset ? COLOR_FILTERS[colorPreset] : undefined;
  const kenBurns = seg.visual[0]?.metadata?.ken_burns;
  const mediaStyle = { width: '100%' as const, height: '100%' as const, objectFit: 'cover' as const };

  if (!isRealFile(src) || !knownFiles.has(src!)) {
    return <PlaceholderFrame type={contentType} title={seg.title} />;
  }

  const visual = isImage
    ? <SafeImg src={mediaUrl(src)} type={contentType} title={seg.title} style={mediaStyle} />
    : <SafeVideo src={mediaUrl(src)} type={contentType} title={seg.title} style={mediaStyle} />;

  const graded = <AbsoluteFill style={{ filter: colorFilter }}>{visual}</AbsoluteFill>;
  return kenBurns ? <KenBurns effect={kenBurns}>{graded}</KenBurns> : graded;
}

// Renders all overlays for a segment using the registry
function SegmentOverlays({ seg, segDuration, fps }: { seg: Segment; segDuration: number; fps: number }) {
  return (
    <>
      {/* LowerThird — special case (different props interface) */}
      {seg.overlay.filter(o => o.content_type === 'LOWER_THIRD').map((lt, i) => {
        const { name, role } = parseLowerThirdContent(lt.content);
        const dur = Math.min(DEFAULT_DURATIONS.LOWER_THIRD * fps, segDuration);
        const offset = lt.time_start ? Math.round(parseTimecode(lt.time_start) * fps) : 0;
        return (
          <Sequence key={`lt-${i}`} from={offset} durationInFrames={Math.min(dur, segDuration - offset)}>
            <LowerThird name={name} role={role} durationInFrames={dur} />
          </Sequence>
        );
      })}

      {/* Registry-based overlays */}
      {seg.overlay.filter(o => o.content_type !== 'LOWER_THIRD').map((entry, i) => {
        const Component = OVERLAY_COMPONENTS[entry.content_type];
        if (!Component) return null;
        const defaultDur = (DEFAULT_DURATIONS[entry.content_type] || 3) * fps;
        const dur = Math.min(defaultDur, segDuration);
        const offset = entry.time_start ? Math.round(parseTimecode(entry.time_start) * fps) : 0;
        return (
          <Sequence key={`ov-${i}`} from={offset} durationInFrames={Math.min(dur, segDuration - offset)}>
            <Component content={entry.content} metadata={entry.metadata} durationInFrames={dur} />
          </Sequence>
        );
      })}
    </>
  );
}

export const BeeComposition: React.FC<{
  storyboard: Storyboard;
  mediaFiles?: string[];
  showCaptions?: boolean;
  transitionMode?: 'overlap' | 'fade';
}> = ({ storyboard, mediaFiles = [], showCaptions = true, transitionMode = 'overlap' }) => {
  const { fps } = useVideoConfig();
  const knownFiles = new Set(mediaFiles);

  const { positions, totalFrames } = calculateSegmentPositions(storyboard.segments, fps, transitionMode);

  // Publish computed total frames so RemotionPreview can set Player duration
  useEffect(() => {
    useProjectStore.getState().setComputedTotalFrames(totalFrames);
  }, [totalFrames]);

  // Build segment lookup for transition rendering
  const segmentMap = new Map(storyboard.segments.map(s => [s.id, s]));

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {positions.map((pos, i) => {
        const seg = segmentMap.get(pos.segId);
        if (!seg) return null;

        const narEntry = seg.audio.find(a => a.content_type === 'NAR');
        const narrationText = narEntry?.content || '';

        // Segment content (visual + overlays + captions)
        const segmentContent = (
          <>
            <SegmentVisual seg={seg} knownFiles={knownFiles} />
            <SegmentOverlays seg={seg} segDuration={pos.duration} fps={fps} />
            {showCaptions && narrationText && <CaptionOverlay text={narrationText} style="karaoke" />}
          </>
        );

        // Apply transition if present
        if (pos.transitionIn && transitionMode === 'fade') {
          return (
            <Sequence key={seg.id} from={pos.from} durationInFrames={pos.duration} name={seg.title}>
              <TransitionRenderer type={pos.transitionIn.type} durationInFrames={pos.duration} mode="fade" position="in">
                {segmentContent}
              </TransitionRenderer>
            </Sequence>
          );
        }

        // Overlap transitions are rendered between segments (handled below)
        return (
          <Sequence key={seg.id} from={pos.from} durationInFrames={pos.duration} name={seg.title}>
            {segmentContent}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
```

Note: Full overlap transition rendering (rendering the TransitionRenderer with both outgoing and incoming segments during the overlap window) is architecturally complex because it requires rendering two segment contents simultaneously in a shared Sequence. For this initial implementation, overlap mode positions segments to overlap but relies on the natural stacking (later segment renders on top). True cross-dissolve with opacity blending can be added as a follow-up enhancement — the `TransitionRenderer` component is ready for it.

- [ ] **Step 2: Update remotion-entry.tsx if needed**

Read `web/src/remotion-entry.tsx` — ensure the `defaultProps` include `transitionMode`:
```tsx
defaultProps: { storyboard: null as unknown as Storyboard, mediaFiles: [] as string[], showCaptions: true, transitionMode: 'overlap' as const }
```

- [ ] **Step 3: Build and run all tests**

```bash
npm run build 2>&1 | tail -5
npx vitest run 2>&1 | tail -10
```

- [ ] **Step 4: Commit**

```bash
git add web/src/components/BeeComposition.tsx web/src/remotion-entry.tsx
git commit -m "feat: rewrite BeeComposition with overlay registry and transition positioning"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run all tests**

```bash
cd bee-content/video-editor/web && npx vitest run
```
Expected: All pass

- [ ] **Step 2: Full build**

```bash
npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Manual smoke test**

Start dev server and verify in browser:
1. Load project → preview shows segments with overlays
2. QUOTE_CARD segments show animated quote with accent bar
3. FINANCIAL_CARD segments show counting dollar amount
4. TEXT_OVERLAY segments show typewriter text
5. TIMELINE_MARKER shows animated slide-in date
6. LOWER_THIRD still works (slide-in animation)
7. Toggle X-Fade / Fade button → transitions change
8. Color grades and Ken Burns still work
9. Captions still work

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: Remotion overlays and transitions Phase 1 complete"
```
