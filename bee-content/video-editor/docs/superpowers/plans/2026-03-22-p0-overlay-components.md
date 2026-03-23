# P0 Overlay Components Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 5 new Remotion overlay components (PhotoViewerCard, SourceBadge, BulletList, InfoCard, Watermark) identified from the Dr Insanity video audit.

**Architecture:** Each component follows the established dual-export pattern (Overlay + Visual variants), with pure parser functions, manual spring stagger animations, and colocated tests. Three card-like components go in a new `remotion/cards/` subdirectory; two lightweight overlays stay at the top level.

**Tech Stack:** React 19, Remotion 4, TypeScript, Vitest

**Spec:** `docs/superpowers/specs/2026-03-22-p0-overlay-components-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `web/src/components/remotion/SourceBadge.tsx` | Overlay component + parser |
| Create | `web/src/components/remotion/SourceBadge.test.ts` | Parser tests |
| Create | `web/src/components/remotion/cards/BulletList.tsx` | Dual-export component + parser |
| Create | `web/src/components/remotion/cards/BulletList.test.ts` | Parser tests |
| Create | `web/src/components/remotion/cards/PhotoViewerCard.tsx` | Dual-export component + parser |
| Create | `web/src/components/remotion/cards/PhotoViewerCard.test.ts` | Parser tests |
| Create | `web/src/components/remotion/cards/InfoCard.tsx` | Dual-export component + parser |
| Create | `web/src/components/remotion/cards/InfoCard.test.ts` | Parser tests |
| Create | `web/src/components/remotion/Watermark.tsx` | Composition-level component |
| Modify | `web/shared/types.ts:77-87` | Add `WatermarkConfig` + `watermark?` to `BeeProject` |
| Modify | `web/src/components/remotion/overlays.ts:9-32` | Add DEFAULT_DURATIONS entries |
| Modify | `web/src/components/BeeComposition.tsx:1-46` | Add imports + registry entries + Watermark render |

---

### Task 1: SourceBadge — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/SourceBadge.tsx` (parser only first)
- Create: `web/src/components/remotion/SourceBadge.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/SourceBadge.test.ts
import { describe, test, expect } from 'vitest';
import { parseSourceBadgeData } from './SourceBadge';

describe('parseSourceBadgeData', () => {
  test('parses content string as label', () => {
    const result = parseSourceBadgeData('REENACTMENT');
    expect(result).toEqual({ label: 'REENACTMENT', position: 'bottom-left' });
  });

  test('falls back to metadata.text when content is empty', () => {
    const result = parseSourceBadgeData('', { text: 'ACTUAL PHOTO' });
    expect(result).toEqual({ label: 'ACTUAL PHOTO', position: 'bottom-left' });
  });

  test('reads position from metadata', () => {
    const result = parseSourceBadgeData('ACTUAL', { position: 'top-right' });
    expect(result).toEqual({ label: 'ACTUAL', position: 'top-right' });
  });

  test('defaults position to bottom-left', () => {
    const result = parseSourceBadgeData('TEST', {});
    expect(result.position).toBe('bottom-left');
  });

  test('handles null metadata', () => {
    const result = parseSourceBadgeData('LABEL', null);
    expect(result).toEqual({ label: 'LABEL', position: 'bottom-left' });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx vitest run src/components/remotion/SourceBadge.test.ts`
Expected: FAIL — `parseSourceBadgeData` not found

- [ ] **Step 3: Write the parser function**

Create `web/src/components/remotion/SourceBadge.tsx` with only the parser and types (no React component yet):

```ts
// web/src/components/remotion/SourceBadge.tsx

export interface SourceBadgeData {
  label: string;
  position: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
}

export function parseSourceBadgeData(
  content: string,
  metadata?: Record<string, any> | null,
): SourceBadgeData {
  return {
    label: content || metadata?.text || '',
    position: (metadata?.position as SourceBadgeData['position']) || 'bottom-left',
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npx vitest run src/components/remotion/SourceBadge.test.ts`
Expected: PASS — all 5 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/SourceBadge.tsx web/src/components/remotion/SourceBadge.test.ts
git commit -m "feat: add SourceBadge parser with tests"
```

---

### Task 2: SourceBadge — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/SourceBadge.tsx` (add React component)
- Modify: `web/src/components/remotion/overlays.ts` (add DEFAULT_DURATIONS)
- Modify: `web/src/components/BeeComposition.tsx` (add to OVERLAY_COMPONENTS)

- [ ] **Step 1: Add the React component to SourceBadge.tsx**

Add imports and the component below the parser:

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from './overlays';

// ... (existing parser code stays above) ...

const POSITION_STYLES: Record<SourceBadgeData['position'], React.CSSProperties> = {
  'bottom-left': { bottom: 24, left: 24 },
  'bottom-right': { bottom: 24, right: 24 },
  'top-left': { top: 24, left: 24 },
  'top-right': { top: 24, right: 24 },
};

export const SourceBadge: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { label, position } = parseSourceBadgeData(content, metadata);

  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const opacity = fadeIn * fadeOut;

  return (
    <AbsoluteFill>
      <div style={{
        position: 'absolute',
        ...POSITION_STYLES[position],
        opacity,
        background: 'rgba(0, 0, 0, 0.6)',
        padding: '4px 10px',
        borderRadius: 3,
      }}>
        <span style={{
          color: '#cccccc',
          fontSize: 13,
          fontFamily: "'Courier New', monospace",
          letterSpacing: 0.5,
        }}>
          [{label}]
        </span>
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Add DEFAULT_DURATIONS entry**

In `web/src/components/remotion/overlays.ts`, add to the `DEFAULT_DURATIONS` object:

```ts
SOURCE_BADGE: 30,
```

- [ ] **Step 3: Register in BeeComposition.tsx**

Add import at top of `web/src/components/BeeComposition.tsx`:
```ts
import { SourceBadge } from './remotion/SourceBadge';
```

Add to `OVERLAY_COMPONENTS` record:
```ts
SOURCE_BADGE: SourceBadge,
```

- [ ] **Step 4: Run all tests to verify nothing breaks**

Run: `cd web && npx vitest run`
Expected: All existing tests pass + SourceBadge tests pass

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/SourceBadge.tsx web/src/components/remotion/overlays.ts web/src/components/BeeComposition.tsx
git commit -m "feat: add SourceBadge overlay component with registration"
```

---

### Task 3: BulletList — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/cards/BulletList.tsx` (parser only)
- Create: `web/src/components/remotion/cards/BulletList.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/cards/BulletList.test.ts
import { describe, test, expect } from 'vitest';
import { parseBulletListData } from './BulletList';

describe('parseBulletListData', () => {
  test('parses newline-separated content into items', () => {
    const result = parseBulletListData('Line one\nLine two\nLine three');
    expect(result.items).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('parses JSON array content', () => {
    const result = parseBulletListData('["First", "Second", "Third"]');
    expect(result.items).toEqual(['First', 'Second', 'Third']);
  });

  test('filters empty lines', () => {
    const result = parseBulletListData('Line one\n\nLine two\n  \nLine three');
    expect(result.items).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('defaults accent to red and style to stagger', () => {
    const result = parseBulletListData('Item');
    expect(result.accent).toBe('red');
    expect(result.style).toBe('stagger');
  });

  test('reads accent and style from metadata', () => {
    const result = parseBulletListData('Item', { accent: 'teal', style: 'cascade' });
    expect(result.accent).toBe('teal');
    expect(result.style).toBe('cascade');
  });

  test('malformed JSON falls back to newline split', () => {
    const result = parseBulletListData('[invalid json');
    expect(result.items).toEqual(['[invalid json']);
  });

  test('handles null metadata', () => {
    const result = parseBulletListData('Item', null);
    expect(result.accent).toBe('red');
    expect(result.style).toBe('stagger');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx vitest run src/components/remotion/cards/BulletList.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the parser**

Create `web/src/components/remotion/cards/BulletList.tsx` with parser only:

```ts
// web/src/components/remotion/cards/BulletList.tsx

export interface BulletListData {
  items: string[];
  accent: 'red' | 'teal' | 'gold' | 'white';
  style: 'stagger' | 'cascade' | 'instant';
}

const ACCENT_COLORS: Record<BulletListData['accent'], string> = {
  red: '#dc2626',
  teal: '#0d9488',
  gold: '#d97706',
  white: '#ffffff',
};

export { ACCENT_COLORS };

export function parseBulletListData(
  content: string,
  metadata?: Record<string, any> | null,
): BulletListData {
  let items: string[];

  if (content.trimStart().startsWith('[')) {
    try {
      const parsed = JSON.parse(content);
      items = Array.isArray(parsed) ? parsed.map(String) : [content];
    } catch {
      items = content.split('\n').map(s => s.trim()).filter(Boolean);
    }
  } else {
    items = content.split('\n').map(s => s.trim()).filter(Boolean);
  }

  return {
    items,
    accent: (metadata?.accent as BulletListData['accent']) || 'red',
    style: (metadata?.style as BulletListData['style']) || 'stagger',
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npx vitest run src/components/remotion/cards/BulletList.test.ts`
Expected: PASS — all 7 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/BulletList.tsx web/src/components/remotion/cards/BulletList.test.ts
git commit -m "feat: add BulletList parser with tests"
```

---

### Task 4: BulletList — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/cards/BulletList.tsx` (add React component)
- Modify: `web/src/components/remotion/overlays.ts`
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Add the React component to BulletList.tsx**

Add imports and components below the parser. Key pattern: manual per-item spring stagger (NOT `StaggerChildren`), slide in from -600px.

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../../primitives/QualityContext';
import type { OverlayProps } from '../../overlays';

// ... (existing parser code stays above) ...

function BulletListVisual({
  data, durationInFrames, background,
}: { data: BulletListData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const staggerFrames = Math.round(8 * timingMultiplier);
  const accentColor = ACCENT_COLORS[data.accent] || ACCENT_COLORS.red;
  const fontSize = data.items.length > 6 ? 18 : 22;

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: background, justifyContent: 'center', padding: '0 80px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, opacity: exitOpacity }}>
        {data.items.map((item, i) => {
          const delay = data.style === 'instant' ? 0 : i * staggerFrames;
          const progress = data.style === 'instant' ? 1 : spring({
            frame: Math.max(0, frame - delay), fps, config: springConfig,
          });
          const translateX = interpolate(progress, [0, 1], [-600, 0]);
          const opacity = interpolate(progress, [0, 1], [0, 1]);
          const indent = data.style === 'cascade' ? Math.min(i * 20, 120) : 0;

          return (
            <div key={i} style={{
              transform: `translateX(${translateX}px)`,
              opacity,
              marginLeft: indent,
              background: 'rgba(0, 0, 0, 0.75)',
              padding: '14px 24px',
              borderLeft: `3px solid ${accentColor}`,
              alignSelf: 'flex-start',
            }}>
              <span style={{
                color: '#fff',
                fontSize,
                fontWeight: 800,
                fontFamily: "'Arial Black', Arial, sans-serif",
                letterSpacing: 2,
                textTransform: 'uppercase',
              }}>
                {item}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

export const BulletListOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseBulletListData(props.content, props.metadata);
  return <BulletListVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const BulletList: React.FC<OverlayProps> = (props) => {
  const data = parseBulletListData(props.content, props.metadata);
  return <BulletListVisual data={data} durationInFrames={props.durationInFrames} background="#000" />;
};
```

- [ ] **Step 2: Add DEFAULT_DURATIONS entry**

In `web/src/components/remotion/overlays.ts`, add:
```ts
BULLET_LIST: 6,
```

- [ ] **Step 3: Register in BeeComposition.tsx**

Add import:
```ts
import { BulletListOverlay, BulletList } from './remotion/cards/BulletList';
```

Add to `OVERLAY_COMPONENTS`:
```ts
BULLET_LIST: BulletListOverlay,
```

Add to `VISUAL_COMPONENTS`:
```ts
BULLET_LIST: BulletList,
```

- [ ] **Step 4: Run all tests**

Run: `cd web && npx vitest run`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/BulletList.tsx web/src/components/remotion/overlays.ts web/src/components/BeeComposition.tsx
git commit -m "feat: add BulletList overlay component with stagger animation"
```

---

### Task 5: PhotoViewerCard — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/cards/PhotoViewerCard.tsx` (parser only)
- Create: `web/src/components/remotion/cards/PhotoViewerCard.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/cards/PhotoViewerCard.test.ts
import { describe, test, expect } from 'vitest';
import { parsePhotoViewerData } from './PhotoViewerCard';

describe('parsePhotoViewerData', () => {
  test('parses "Name — Role" content as single card', () => {
    const result = parsePhotoViewerData('Craig Thetford — Victim', { src: 'photo.jpg' });
    expect(result.cards).toEqual([{ name: 'Craig Thetford', role: 'Victim', src: 'photo.jpg' }]);
  });

  test('parses name-only content (no role)', () => {
    const result = parsePhotoViewerData('John Doe');
    expect(result.cards).toEqual([{ name: 'John Doe', role: undefined, src: undefined }]);
  });

  test('parses JSON array content as multiple cards', () => {
    const json = JSON.stringify([
      { name: 'Bill', role: 'Ex-husband', src: 'bill.jpg' },
      { name: 'Scott', src: 'scott.jpg' },
    ]);
    const result = parsePhotoViewerData(json);
    expect(result.cards).toHaveLength(2);
    expect(result.cards[0]).toEqual({ name: 'Bill', role: 'Ex-husband', src: 'bill.jpg' });
    expect(result.cards[1]).toEqual({ name: 'Scott', role: undefined, src: 'scott.jpg' });
  });

  test('defaults animation to slide-up and windowTitle to Photo Viewer', () => {
    const result = parsePhotoViewerData('Name');
    expect(result.animation).toBe('slide-up');
    expect(result.windowTitle).toBe('Photo Viewer');
  });

  test('reads animation and windowTitle from metadata', () => {
    const result = parsePhotoViewerData('Name', { animation: 'scale', windowTitle: 'Evidence' });
    expect(result.animation).toBe('scale');
    expect(result.windowTitle).toBe('Evidence');
  });

  test('malformed JSON falls back to single card with content as name', () => {
    const result = parsePhotoViewerData('[invalid json');
    expect(result.cards).toEqual([{ name: '[invalid json', role: undefined, src: undefined }]);
  });

  test('empty content with metadata fallback', () => {
    const result = parsePhotoViewerData('', { name: 'From Meta', role: 'Suspect', src: 'meta.jpg' });
    expect(result.cards).toEqual([{ name: 'From Meta', role: 'Suspect', src: 'meta.jpg' }]);
  });

  test('handles null metadata', () => {
    const result = parsePhotoViewerData('Name', null);
    expect(result.cards).toEqual([{ name: 'Name', role: undefined, src: undefined }]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx vitest run src/components/remotion/cards/PhotoViewerCard.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the parser**

Create `web/src/components/remotion/cards/PhotoViewerCard.tsx` with parser only:

```ts
// web/src/components/remotion/cards/PhotoViewerCard.tsx

export interface PhotoViewerCardInfo {
  name: string;
  role?: string;
  src?: string;
}

export interface PhotoViewerData {
  cards: PhotoViewerCardInfo[];
  animation: 'slide-up' | 'slide-left' | 'scale';
  windowTitle: string;
}

export function parsePhotoViewerData(
  content: string,
  metadata?: Record<string, any> | null,
): PhotoViewerData {
  let cards: PhotoViewerCardInfo[];

  if (content.trimStart().startsWith('[')) {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        cards = parsed.map((c: any) => ({
          name: c.name || '',
          role: c.role || undefined,
          src: c.src || undefined,
        }));
      } else {
        cards = [{ name: content, role: undefined, src: metadata?.src }];
      }
    } catch {
      cards = [{ name: content, role: undefined, src: metadata?.src }];
    }
  } else if (!content && metadata) {
    cards = [{
      name: metadata.name || metadata.text || '',
      role: metadata.role || metadata.subtext || undefined,
      src: metadata.src || undefined,
    }];
  } else {
    const parts = content.split(/\s*[—–]\s*/);
    cards = [{
      name: parts[0]?.trim() || content,
      role: parts[1]?.trim() || undefined,
      src: metadata?.src || undefined,
    }];
  }

  return {
    cards,
    animation: (metadata?.animation as PhotoViewerData['animation']) || 'slide-up',
    windowTitle: (metadata?.windowTitle as string) || 'Photo Viewer',
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npx vitest run src/components/remotion/cards/PhotoViewerCard.test.ts`
Expected: PASS — all 8 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/PhotoViewerCard.tsx web/src/components/remotion/cards/PhotoViewerCard.test.ts
git commit -m "feat: add PhotoViewerCard parser with tests"
```

---

### Task 6: PhotoViewerCard — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/cards/PhotoViewerCard.tsx` (add React component)
- Modify: `web/src/components/remotion/overlays.ts`
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Add the React component to PhotoViewerCard.tsx**

Add imports and components below the parser. macOS window chrome with traffic lights, menu bar, photo area, name label. Manual spring stagger for multi-card.

```tsx
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../../primitives/QualityContext';
import { mediaUrl } from '../../SafeMedia';
import type { OverlayProps } from '../../overlays';

// ... (existing parser code stays above) ...

function MacWindowChrome({ title, children, nameLabel, roleLabel }: {
  title: string;
  children: React.ReactNode;
  nameLabel: string;
  roleLabel?: string;
}) {
  return (
    <div style={{
      background: '#1e1e1e', borderRadius: 10, overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)', width: '100%',
    }}>
      {/* Title bar */}
      <div style={{
        height: 32, background: '#2d2d2d', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 8,
      }}>
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f57' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#febc2e' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#28c840' }} />
        <span style={{
          flex: 1, textAlign: 'center', color: '#999', fontSize: 12,
          fontFamily: 'system-ui, Arial, sans-serif',
        }}>{title}</span>
      </div>
      {/* Menu bar */}
      <div style={{
        height: 24, background: '#252525', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 16,
      }}>
        {['File', 'Edit', 'Image', 'View', 'Help'].map(m => (
          <span key={m} style={{ color: '#aaa', fontSize: 11, fontFamily: 'system-ui, Arial, sans-serif' }}>{m}</span>
        ))}
      </div>
      {/* Photo area */}
      {children}
      {/* Name label */}
      <div style={{
        background: '#1a1a1a', padding: '10px 16px', borderTop: '1px solid #333',
      }}>
        <div style={{
          color: '#fff', fontSize: 18, fontWeight: 700,
          fontFamily: 'Arial, Helvetica, sans-serif', letterSpacing: 1,
        }}>{nameLabel}</div>
        {roleLabel && (
          <div style={{
            color: '#999', fontSize: 12, fontFamily: 'Arial, Helvetica, sans-serif', marginTop: 2,
          }}>{roleLabel}</div>
        )}
      </div>
    </div>
  );
}

function PhotoArea({ src }: { src?: string }) {
  if (src) {
    return (
      <div style={{ height: 280, background: '#333', overflow: 'hidden' }}>
        <Img src={mediaUrl(src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
    );
  }
  // Placeholder silhouette
  return (
    <div style={{
      height: 280, background: '#333', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
    }}>
      <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="1.5">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    </div>
  );
}

function PhotoViewerCardVisual({
  data, durationInFrames, background,
}: { data: PhotoViewerData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Entrance animation for the whole container
  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterTransform = data.animation === 'slide-up'
    ? `translateY(${interpolate(enterProgress, [0, 1], [200, 0])}px)`
    : data.animation === 'slide-left'
      ? `translateX(${interpolate(enterProgress, [0, 1], [-400, 0])}px)`
      : `scale(${interpolate(enterProgress, [0, 1], [0.5, 1])})`;

  // Photo fade in
  const photoOpacity = interpolate(frame, [10, 25].map(f => Math.round(f * timingMultiplier)), [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Name label slide up
  const nameLabelY = interpolate(frame, [20, 30].map(f => Math.round(f * timingMultiplier)), [20, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const nameLabelOpacity = interpolate(frame, [20, 30].map(f => Math.round(f * timingMultiplier)), [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const cardWidth = data.cards.length === 1 ? 420 : 360;
  const staggerDelay = Math.round(8 * timingMultiplier);

  return (
    <AbsoluteFill style={{
      backgroundColor: background,
      justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        display: 'flex', gap: 24, opacity: exitOpacity,
        transform: enterTransform,
      }}>
        {data.cards.map((card, i) => {
          const cardProgress = i === 0 ? 1 : spring({
            frame: Math.max(0, frame - i * staggerDelay), fps, config: springConfig,
          });
          const cardOpacity = i === 0 ? 1 : interpolate(cardProgress, [0, 1], [0, 1]);

          return (
            <div key={i} style={{ width: cardWidth, opacity: cardOpacity }}>
              <MacWindowChrome title={data.windowTitle} nameLabel={card.name} roleLabel={card.role}>
                <div style={{ opacity: photoOpacity }}>
                  <PhotoArea src={card.src} />
                </div>
              </MacWindowChrome>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

export const PhotoViewerCardOverlay: React.FC<OverlayProps> = (props) => {
  const data = parsePhotoViewerData(props.content, props.metadata);
  return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const PhotoViewerCard: React.FC<OverlayProps> = (props) => {
  const data = parsePhotoViewerData(props.content, props.metadata);
  return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} background="#000" />;
};
```

- [ ] **Step 2: Add DEFAULT_DURATIONS entry**

In `web/src/components/remotion/overlays.ts`, add:
```ts
PHOTO_VIEWER: 5,
```

- [ ] **Step 3: Register in BeeComposition.tsx**

Add import:
```ts
import { PhotoViewerCardOverlay, PhotoViewerCard } from './remotion/cards/PhotoViewerCard';
```

Add to `OVERLAY_COMPONENTS`:
```ts
PHOTO_VIEWER: PhotoViewerCardOverlay,
```

Add to `VISUAL_COMPONENTS`:
```ts
PHOTO_VIEWER: PhotoViewerCard,
```

- [ ] **Step 4: Run all tests**

Run: `cd web && npx vitest run`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/PhotoViewerCard.tsx web/src/components/remotion/overlays.ts web/src/components/BeeComposition.tsx
git commit -m "feat: add PhotoViewerCard with macOS window chrome"
```

---

### Task 7: InfoCard — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/cards/InfoCard.tsx` (parser only)
- Create: `web/src/components/remotion/cards/InfoCard.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/cards/InfoCard.test.ts
import { describe, test, expect } from 'vitest';
import { parseInfoCardData } from './InfoCard';

describe('parseInfoCardData', () => {
  test('parses JSON content with sections array', () => {
    const content = JSON.stringify({
      sections: [
        { header: 'Charges', body: 'First degree murder' },
        { header: 'Sentence', body: 'Life in prison' },
      ],
    });
    const result = parseInfoCardData(content);
    expect(result.sections).toHaveLength(2);
    expect(result.sections[0]).toEqual({ header: 'Charges', body: 'First degree murder', color: undefined });
    expect(result.sections[1]).toEqual({ header: 'Sentence', body: 'Life in prison', color: undefined });
  });

  test('plain text falls back to single section', () => {
    const result = parseInfoCardData('Some plain text', { header: 'Details' });
    expect(result.sections).toEqual([{ header: 'Details', body: 'Some plain text', color: undefined }]);
  });

  test('malformed JSON falls back to plain text', () => {
    const result = parseInfoCardData('{invalid json}', { header: 'Info' });
    expect(result.sections).toEqual([{ header: 'Info', body: '{invalid json}', color: undefined }]);
  });

  test('defaults photoSide to right', () => {
    const result = parseInfoCardData('text');
    expect(result.photoSide).toBe('right');
  });

  test('reads src and photoSide from metadata', () => {
    const result = parseInfoCardData('text', { src: 'photo.jpg', photoSide: 'left' });
    expect(result.src).toBe('photo.jpg');
    expect(result.photoSide).toBe('left');
  });

  test('section color override', () => {
    const content = JSON.stringify({
      sections: [{ header: 'H', body: 'B', color: '#00ff00' }],
    });
    const result = parseInfoCardData(content);
    expect(result.sections[0].color).toBe('#00ff00');
  });

  test('empty sections array', () => {
    const content = JSON.stringify({ sections: [] });
    const result = parseInfoCardData(content);
    expect(result.sections).toEqual([]);
  });

  test('empty content with no header metadata creates section with empty header', () => {
    const result = parseInfoCardData('');
    expect(result.sections).toEqual([{ header: '', body: '', color: undefined }]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx vitest run src/components/remotion/cards/InfoCard.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the parser**

Create `web/src/components/remotion/cards/InfoCard.tsx`:

```ts
// web/src/components/remotion/cards/InfoCard.tsx

export interface InfoCardSection {
  header: string;
  body: string;
  color?: string;
}

export interface InfoCardData {
  sections: InfoCardSection[];
  src?: string;
  photoSide: 'left' | 'right' | 'none';
}

export function parseInfoCardData(
  content: string,
  metadata?: Record<string, any> | null,
): InfoCardData {
  let sections: InfoCardSection[];

  try {
    const parsed = JSON.parse(content);
    if (parsed && Array.isArray(parsed.sections)) {
      sections = parsed.sections.map((s: any) => ({
        header: s.header || '',
        body: s.body || '',
        color: s.color || undefined,
      }));
    } else {
      throw new Error('not a sections object');
    }
  } catch {
    sections = [{
      header: metadata?.header || '',
      body: content,
      color: undefined,
    }];
  }

  return {
    sections,
    src: metadata?.src || undefined,
    photoSide: (metadata?.photoSide as InfoCardData['photoSide']) || 'right',
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npx vitest run src/components/remotion/cards/InfoCard.test.ts`
Expected: PASS — all 8 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/InfoCard.tsx web/src/components/remotion/cards/InfoCard.test.ts
git commit -m "feat: add InfoCard parser with tests"
```

---

### Task 8: InfoCard — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/cards/InfoCard.tsx` (add React component)
- Modify: `web/src/components/remotion/overlays.ts`
- Modify: `web/src/components/BeeComposition.tsx`

- [ ] **Step 1: Add the React component to InfoCard.tsx**

Add imports and components below the parser. Split layout with manual per-section spring stagger.

```tsx
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../../primitives/QualityContext';
import { mediaUrl } from '../../SafeMedia';
import type { OverlayProps } from '../../overlays';

// ... (existing parser code stays above) ...

const DEFAULT_HEADER_COLOR = '#dc2626';

function InfoCardVisual({
  data, durationInFrames, background,
}: { data: InfoCardData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const sectionInterval = Math.round(10 * timingMultiplier);

  // Container fade in
  const containerOpacity = interpolate(frame, [0, Math.round(20 * timingMultiplier)], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Exit fade
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Photo slide in
  const photoProgress = spring({
    frame: Math.max(0, frame - Math.round(10 * timingMultiplier)), fps, config: springConfig,
  });
  const photoTranslateX = data.photoSide === 'left'
    ? interpolate(photoProgress, [0, 1], [-200, 0])
    : interpolate(photoProgress, [0, 1], [200, 0]);

  const showPhoto = data.src && data.photoSide !== 'none';
  const isPhotoLeft = data.photoSide === 'left';

  const sectionsEl = (
    <div style={{
      flex: 1, padding: 40, display: 'flex', flexDirection: 'column',
      justifyContent: 'center', gap: 24,
    }}>
      {data.sections.map((section, i) => {
        const delay = Math.round(5 * timingMultiplier) + i * sectionInterval;
        const progress = spring({
          frame: Math.max(0, frame - delay), fps, config: springConfig,
        });
        const sectionOpacity = interpolate(progress, [0, 1], [0, 1]);
        const translateY = interpolate(progress, [0, 1], [30, 0]);

        return (
          <div key={i} style={{ opacity: sectionOpacity, transform: `translateY(${translateY}px)` }}>
            {section.header && (
              <div style={{
                color: section.color || DEFAULT_HEADER_COLOR,
                fontSize: 24, fontWeight: 800,
                fontFamily: 'Arial, Helvetica, sans-serif',
                marginBottom: 8,
              }}>{section.header}</div>
            )}
            <div style={{
              color: '#e5e5e5', fontSize: 16, lineHeight: 1.5,
              fontFamily: 'Arial, Helvetica, sans-serif',
            }}>{section.body}</div>
          </div>
        );
      })}
    </div>
  );

  const photoEl = showPhoto ? (
    <div style={{
      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
      transform: `translateX(${photoTranslateX}px)`,
      opacity: interpolate(photoProgress, [0, 1], [0, 1]),
    }}>
      <Img src={mediaUrl(data.src!)} style={{
        maxWidth: '90%', maxHeight: '90%', objectFit: 'cover', borderRadius: 4,
      }} />
    </div>
  ) : null;

  return (
    <AbsoluteFill style={{
      backgroundColor: background, justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        width: '85%', height: '75%', display: 'flex',
        opacity: containerOpacity * exitOpacity,
      }}>
        {isPhotoLeft ? <>{photoEl}{sectionsEl}</> : <>{sectionsEl}{photoEl}</>}
      </div>
    </AbsoluteFill>
  );
}

export const InfoCardOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseInfoCardData(props.content, props.metadata);
  return <InfoCardVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const InfoCard: React.FC<OverlayProps> = (props) => {
  const data = parseInfoCardData(props.content, props.metadata);
  return <InfoCardVisual data={data} durationInFrames={props.durationInFrames} background="#0a0a0a" />;
};
```

- [ ] **Step 2: Add DEFAULT_DURATIONS entry**

In `web/src/components/remotion/overlays.ts`, add:
```ts
INFO_CARD: 6,
```

- [ ] **Step 3: Register in BeeComposition.tsx**

Add import:
```ts
import { InfoCardOverlay, InfoCard } from './remotion/cards/InfoCard';
```

Add to `OVERLAY_COMPONENTS`:
```ts
INFO_CARD: InfoCardOverlay,
```

Add to `VISUAL_COMPONENTS`:
```ts
INFO_CARD: InfoCard,
```

- [ ] **Step 4: Run all tests**

Run: `cd web && npx vitest run`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/InfoCard.tsx web/src/components/remotion/overlays.ts web/src/components/BeeComposition.tsx
git commit -m "feat: add InfoCard with split photo layout and stagger sections"
```

---

### Task 9: Watermark — Component + Type + Integration

**Files:**
- Create: `web/src/components/remotion/Watermark.tsx`
- Modify: `web/shared/types.ts:77-87` (add WatermarkConfig + field)
- Modify: `web/src/components/BeeComposition.tsx` (add Watermark render layer)

- [ ] **Step 1: Add WatermarkConfig type to shared/types.ts**

Add before the `BeeProject` interface in `web/shared/types.ts`:

```ts
export interface WatermarkConfig {
  text?: string;
  src?: string;
  position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  opacity: number;
  enabled: boolean;
}
```

Add `watermark?` field to the `BeeProject` interface:
```ts
export interface BeeProject {
  // ... existing fields ...
  quality?: 'standard' | 'premium' | 'social';
  watermark?: WatermarkConfig;
}
```

- [ ] **Step 2: Create the Watermark component**

```tsx
// web/src/components/remotion/Watermark.tsx
import { AbsoluteFill, Img } from 'remotion';
import { mediaUrl } from './SafeMedia';
import type { WatermarkConfig } from '../../types';

export interface WatermarkProps {
  config: WatermarkConfig;
}

const POSITION_STYLES: Record<WatermarkConfig['position'], React.CSSProperties> = {
  'bottom-right': { bottom: 30, right: 30 },
  'bottom-left': { bottom: 30, left: 30 },
  'top-right': { top: 30, right: 30 },
  'top-left': { top: 30, left: 30 },
};

export const Watermark: React.FC<WatermarkProps> = ({ config }) => {
  const posStyle = POSITION_STYLES[config.position] || POSITION_STYLES['bottom-right'];

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <div style={{
        position: 'absolute',
        ...posStyle,
        opacity: config.opacity ?? 0.3,
      }}>
        {config.src ? (
          <Img src={mediaUrl(config.src)} style={{ maxHeight: 40, width: 'auto' }} />
        ) : config.text ? (
          <span style={{
            color: '#fff',
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 2,
            fontFamily: 'Arial, Helvetica, sans-serif',
          }}>
            {config.text}
          </span>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 3: Add Watermark render layer to BeeComposition.tsx**

Add import at top of `web/src/components/BeeComposition.tsx`:
```ts
import { Watermark } from './remotion/Watermark';
```

Add as the **last child** inside the outer `<AbsoluteFill>` in the `BeeComposition` return, after the overlap transitions block and before the closing `</AbsoluteFill></QualityProvider>`:

```tsx
{/* Watermark — project-level, rendered on top of everything */}
{storyboard.watermark?.enabled && (
  <AbsoluteFill style={{ zIndex: 9999 }}>
    <Watermark config={storyboard.watermark} />
  </AbsoluteFill>
)}
```

- [ ] **Step 4: Run all tests**

Run: `cd web && npx vitest run`
Expected: All tests pass (type change is additive, won't break existing tests)

- [ ] **Step 5: Commit**

```bash
git add web/shared/types.ts web/src/components/remotion/Watermark.tsx web/src/components/BeeComposition.tsx
git commit -m "feat: add Watermark component with project-level config"
```

---

### Task 10: Final Verification

- [ ] **Step 1: Run the full test suite**

Run: `cd web && npx vitest run`
Expected: All tests pass, including all new parser tests

- [ ] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No type errors

- [ ] **Step 3: Verify dev server starts**

Run: `cd web && ./dev.sh` (then check http://localhost:5173 loads without errors)
Expected: No console errors, existing project loads normally

- [ ] **Step 4: Update CLAUDE.md component table**

Add the 5 new components to the Remotion Components table in `video-editor/CLAUDE.md`:

```markdown
| PhotoViewerCard | `PHOTO_VIEWER` overlay/visual | macOS-style photo window with name label |
| SourceBadge | `SOURCE_BADGE` overlay | [ACTUAL]/[REENACTMENT] corner label |
| BulletList | `BULLET_LIST` overlay/visual | Staggered reveal text bars for charge sheets |
| InfoCard | `INFO_CARD` overlay/visual | Split photo + structured sections (charges, sentencing) |
| Watermark | project-level config | Persistent semi-transparent channel logo/text |
```

- [ ] **Step 5: Commit docs update**

```bash
git add video-editor/CLAUDE.md
git commit -m "docs: add P0 overlay components to CLAUDE.md"
```
