# P1 Overlay Components Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 4 medium-priority Remotion components (Caption keyword coloring, NotepadWindow, AnimatedBackground, MapAnnotation) to complement the P0 overlay batch.

**Architecture:** One enhancement to CaptionOverlay, two new components (NotepadWindow, MapAnnotation), one shared helper (AnimatedBG) integrated into existing card components. A shared color resolution utility is extracted to overlays.ts.

**Tech Stack:** React 19, Remotion 4, TypeScript, Vitest

**Spec:** `docs/superpowers/specs/2026-03-22-p1-overlay-components-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `web/src/components/remotion/overlays.ts` | Add NAMED_COLORS, resolveColor(), DEFAULT_DURATIONS |
| Modify | `web/src/components/remotion/CaptionOverlay.tsx` | Add parseCaptionWords, use in both renderers |
| Create | `web/src/components/remotion/CaptionOverlay.test.ts` | Parser tests |
| Create | `web/src/components/remotion/cards/NotepadWindow.tsx` | Dual-export component + parser |
| Create | `web/src/components/remotion/cards/NotepadWindow.test.ts` | Parser tests |
| Create | `web/src/components/remotion/cards/AnimatedBG.tsx` | Shared animated background helper |
| Modify | `web/src/components/remotion/cards/PhotoViewerCard.tsx` | Accept animated bg from metadata |
| Create | `web/src/components/remotion/MapAnnotation.tsx` | Overlay component + parser |
| Create | `web/src/components/remotion/MapAnnotation.test.ts` | Parser tests |
| Modify | `web/src/components/BeeComposition.tsx` | Add NotepadWindow + MapAnnotation to registries |

---

### Task 1: Shared Color Utilities

**Files:**
- Modify: `web/src/components/remotion/overlays.ts`

- [ ] **Step 1: Add NAMED_COLORS and resolveColor to overlays.ts**

Add after the existing `DEFAULT_DURATIONS` block in `web/src/components/remotion/overlays.ts`:

```ts
export const NAMED_COLORS: Record<string, string> = {
  red: '#dc2626',
  teal: '#0d9488',
  gold: '#d97706',
  white: '#ffffff',
};

export function resolveColor(color: string): string {
  return NAMED_COLORS[color] || color;
}
```

- [ ] **Step 2: Add DEFAULT_DURATIONS entries**

Add to the `DEFAULT_DURATIONS` object:
```ts
NOTEPAD: 6,
MAP_ANNOTATION: 6,
```

- [ ] **Step 3: Run existing tests to verify nothing breaks**

Run: `cd video-editor/web && npx vitest run src/components/remotion/overlays.test.ts`
Expected: All existing overlay tests pass

- [ ] **Step 4: Commit**

```bash
git add web/src/components/remotion/overlays.ts
git commit -m "feat: add shared NAMED_COLORS map and resolveColor to overlays.ts"
```

---

### Task 2: Caption Keyword Coloring — Parser + Tests

**Files:**
- Modify: `web/src/components/remotion/CaptionOverlay.tsx` (add parser function)
- Create: `web/src/components/remotion/CaptionOverlay.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/CaptionOverlay.test.ts
import { describe, test, expect } from 'vitest';
import { parseCaptionWords } from './CaptionOverlay';

describe('parseCaptionWords', () => {
  test('plain text returns words with no color', () => {
    const result = parseCaptionWords('plain text here');
    expect(result).toEqual([
      { text: 'plain', color: undefined },
      { text: 'text', color: undefined },
      { text: 'here', color: undefined },
    ]);
  });

  test('parses named color markup', () => {
    const result = parseCaptionWords('is that {red:blood}');
    expect(result).toEqual([
      { text: 'is', color: undefined },
      { text: 'that', color: undefined },
      { text: 'blood', color: '#dc2626' },
    ]);
  });

  test('handles multi-word color spans', () => {
    const result = parseCaptionWords('{teal:DNA evidence}');
    expect(result).toEqual([
      { text: 'DNA', color: '#0d9488' },
      { text: 'evidence', color: '#0d9488' },
    ]);
  });

  test('handles hex color', () => {
    const result = parseCaptionWords('{#ff00ff:custom}');
    expect(result).toEqual([
      { text: 'custom', color: '#ff00ff' },
    ]);
  });

  test('handles unclosed markup gracefully', () => {
    const result = parseCaptionWords('no {invalid markup');
    expect(result).toEqual([
      { text: 'no', color: undefined },
      { text: '{invalid', color: undefined },
      { text: 'markup', color: undefined },
    ]);
  });

  test('empty string returns empty array', () => {
    const result = parseCaptionWords('');
    expect(result).toEqual([]);
  });

  test('mixed colored and plain words', () => {
    const result = parseCaptionWords('She had {red:multiple injuries} on the {teal:property}');
    expect(result).toEqual([
      { text: 'She', color: undefined },
      { text: 'had', color: undefined },
      { text: 'multiple', color: '#dc2626' },
      { text: 'injuries', color: '#dc2626' },
      { text: 'on', color: undefined },
      { text: 'the', color: undefined },
      { text: 'property', color: '#0d9488' },
    ]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd video-editor/web && npx vitest run src/components/remotion/CaptionOverlay.test.ts`
Expected: FAIL — `parseCaptionWords` not exported

- [ ] **Step 3: Add parseCaptionWords to CaptionOverlay.tsx**

Add at the top of `web/src/components/remotion/CaptionOverlay.tsx`, after the imports, before the `Props` interface:

```ts
import { resolveColor } from './overlays';

export interface CaptionWord {
  text: string;
  color?: string;
}

export function parseCaptionWords(text: string): CaptionWord[] {
  if (!text) return [];
  const result: CaptionWord[] = [];
  const regex = /\{([^:}]+):([^}]+)\}|(\S+)/g;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match[1] !== undefined && match[2] !== undefined) {
      // Color markup: {color:text with spaces}
      const color = resolveColor(match[1]);
      for (const word of match[2].split(/\s+/)) {
        if (word) result.push({ text: word, color });
      }
    } else if (match[3] !== undefined) {
      // Plain word
      result.push({ text: match[3], color: undefined });
    }
  }

  return result;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd video-editor/web && npx vitest run src/components/remotion/CaptionOverlay.test.ts`
Expected: PASS — all 7 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/CaptionOverlay.tsx web/src/components/remotion/CaptionOverlay.test.ts
git commit -m "feat: add parseCaptionWords with color markup support"
```

---

### Task 3: Caption Keyword Coloring — Integrate into Renderers

**Files:**
- Modify: `web/src/components/remotion/CaptionOverlay.tsx`

- [ ] **Step 1: Replace word splitting with parseCaptionWords in both renderers**

In `CaptionOverlay.tsx`, the component currently does:
```ts
const words = text.split(/\s+/).filter(Boolean);
```

Replace the entire component body to use `parseCaptionWords` internally. The `Props` interface stays unchanged.

The key changes:
1. Replace `text.split(/\s+/).filter(Boolean)` with `parseCaptionWords(text)`
2. In karaoke renderer: use `cw.color || '#fbbf24'` for active/past words instead of hardcoded `'#fbbf24'`
3. In phrase renderer: render each word's color individually instead of `currentChunk.join(' ')`

Updated component (full replacement of the CaptionOverlay export):

```tsx
export const CaptionOverlay: React.FC<Props> = ({ text, style = 'karaoke' }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  if (!text) return null;
  const captionWords = parseCaptionWords(text);
  if (captionWords.length === 0) return null;

  if (style === 'phrase') {
    const chunkSize = Math.min(5, Math.max(3, Math.ceil(captionWords.length / Math.ceil(captionWords.length / 4))));
    const chunks: CaptionWord[][] = [];
    for (let i = 0; i < captionWords.length; i += chunkSize) {
      chunks.push(captionWords.slice(i, i + chunkSize));
    }
    const framesPerChunk = Math.floor(durationInFrames / chunks.length);
    const currentChunkIndex = Math.min(Math.floor(frame / framesPerChunk), chunks.length - 1);
    const currentChunk = chunks[currentChunkIndex];

    return (
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 0 120px' }}>
        <div style={{
          background: 'rgba(0, 0, 0, 0.7)',
          padding: '10px 28px',
          borderRadius: 8,
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '0 8px',
        }}>
          {currentChunk.map((cw, i) => (
            <span key={i} style={{
              color: cw.color || '#fff',
              fontSize: 42,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            }}>
              {cw.text}
            </span>
          ))}
        </div>
      </AbsoluteFill>
    );
  }

  // Karaoke: highlight word by word
  const plainText = captionWords.map(w => w.text).join(' ');
  const totalChars = plainText.length;
  let charsSoFar = 0;

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 40px 120px' }}>
      <div style={{
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '10px 28px',
        borderRadius: 8,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '0 8px',
        maxWidth: '80%',
      }}>
        {captionWords.map((cw, i) => {
          if (i > 0) charsSoFar += 1;
          const wordStart = (charsSoFar / totalChars) * durationInFrames;
          const wordEnd = ((charsSoFar + cw.text.length) / totalChars) * durationInFrames;
          charsSoFar += cw.text.length;

          const isActive = frame >= wordStart && frame <= wordEnd;
          const isPast = frame > wordEnd;
          const highlightColor = cw.color || '#fbbf24';

          return (
            <span
              key={i}
              style={{
                color: isPast || isActive ? highlightColor : '#ffffff',
                fontSize: 42,
                fontWeight: 700,
                fontFamily: 'Arial, Helvetica, sans-serif',
                textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                opacity: isPast || isActive ? 1 : 0.6,
                transform: isActive ? 'scale(1.05)' : 'scale(1)',
              }}
            >
              {cw.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Run all tests**

Run: `cd video-editor/web && npx vitest run`
Expected: All tests pass (CaptionOverlay parser tests + existing tests)

- [ ] **Step 3: Commit**

```bash
git add web/src/components/remotion/CaptionOverlay.tsx
git commit -m "feat: integrate caption keyword coloring into karaoke and phrase renderers"
```

---

### Task 4: NotepadWindow — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/cards/NotepadWindow.tsx` (parser only)
- Create: `web/src/components/remotion/cards/NotepadWindow.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/cards/NotepadWindow.test.ts
import { describe, test, expect } from 'vitest';
import { parseNotepadData } from './NotepadWindow';

describe('parseNotepadData', () => {
  test('parses multiline content into lines array', () => {
    const result = parseNotepadData('Line one\nLine two\nLine three');
    expect(result.lines).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('single line content', () => {
    const result = parseNotepadData('Single line');
    expect(result.lines).toEqual(['Single line']);
  });

  test('defaults animation to typewriter, windowTitle to Notepad, background to #000', () => {
    const result = parseNotepadData('text');
    expect(result.animation).toBe('typewriter');
    expect(result.windowTitle).toBe('Notepad');
    expect(result.background).toBe('#000');
  });

  test('reads overrides from metadata', () => {
    const result = parseNotepadData('text', {
      animation: 'lines',
      windowTitle: 'Case Notes',
      background: 'animated-teal',
    });
    expect(result.animation).toBe('lines');
    expect(result.windowTitle).toBe('Case Notes');
    expect(result.background).toBe('animated-teal');
  });

  test('empty content produces single empty line', () => {
    const result = parseNotepadData('');
    expect(result.lines).toEqual(['']);
  });

  test('preserves blank lines', () => {
    const result = parseNotepadData('Line one\n\nLine three');
    expect(result.lines).toEqual(['Line one', '', 'Line three']);
  });

  test('handles null metadata', () => {
    const result = parseNotepadData('text', null);
    expect(result.animation).toBe('typewriter');
    expect(result.windowTitle).toBe('Notepad');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd video-editor/web && npx vitest run src/components/remotion/cards/NotepadWindow.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the parser**

Create `web/src/components/remotion/cards/NotepadWindow.tsx`:

```ts
// web/src/components/remotion/cards/NotepadWindow.tsx

export interface NotepadData {
  lines: string[];
  animation: 'typewriter' | 'lines' | 'instant';
  windowTitle: string;
  background: string;
}

export function parseNotepadData(
  content: string,
  metadata?: Record<string, any> | null,
): NotepadData {
  return {
    lines: content.split('\n'),
    animation: (metadata?.animation as NotepadData['animation']) || 'typewriter',
    windowTitle: (metadata?.windowTitle as string) || 'Notepad',
    background: (metadata?.background as string) || '#000',
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd video-editor/web && npx vitest run src/components/remotion/cards/NotepadWindow.test.ts`
Expected: PASS — all 7 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/NotepadWindow.tsx web/src/components/remotion/cards/NotepadWindow.test.ts
git commit -m "feat: add NotepadWindow parser with tests"
```

---

### Task 5: NotepadWindow — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/cards/NotepadWindow.tsx` (add React component)
- Modify: `web/src/components/BeeComposition.tsx` (add to registries)

- [ ] **Step 1: Add the React component to NotepadWindow.tsx**

Add imports and component below the parser. macOS window chrome with Notepad menu, typewriter/lines/instant animation, blinking cursor.

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import type { OverlayProps } from '../overlays';

// ... (existing parser code stays above) ...

function NotepadChrome({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: '#1e1e1e', borderRadius: 10, overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)', width: '100%', maxWidth: 600,
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
        {['File', 'Edit', 'Search', 'View', 'Help'].map(m => (
          <span key={m} style={{ color: '#aaa', fontSize: 11, fontFamily: 'system-ui, Arial, sans-serif' }}>{m}</span>
        ))}
      </div>
      {/* Text body */}
      {children}
    </div>
  );
}

function NotepadWindowVisual({
  data, durationInFrames, background,
}: { data: NotepadData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Entrance spring
  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterScale = interpolate(enterProgress, [0, 1], [0.9, 1]);
  const enterOpacity = interpolate(enterProgress, [0, 1], [0, 1]);

  // Blinking cursor (toggles every 15 frames)
  const cursorVisible = Math.floor(frame / 15) % 2 === 0;

  const fullText = data.lines.join('\n');
  const totalChars = fullText.length;

  // Determine visible text based on animation mode
  let visibleLines: { text: string; opacity: number }[];

  if (data.animation === 'instant') {
    visibleLines = data.lines.map(line => ({ text: line, opacity: 1 }));
  } else if (data.animation === 'lines') {
    const staggerInterval = Math.round(12 * timingMultiplier);
    visibleLines = data.lines.map((line, i) => {
      const delay = i * staggerInterval;
      const progress = spring({
        frame: Math.max(0, frame - delay), fps, config: springConfig,
      });
      return { text: line, opacity: interpolate(progress, [0, 1], [0, 1]) };
    });
  } else {
    // typewriter: show chars progressively
    const charsToShow = Math.min(Math.floor((frame / (durationInFrames - 15)) * totalChars), totalChars);
    let charsRemaining = charsToShow;
    visibleLines = data.lines.map(line => {
      if (charsRemaining <= 0) return { text: '', opacity: 1 };
      const visible = line.slice(0, charsRemaining);
      charsRemaining -= line.length + 1; // +1 for newline
      return { text: visible, opacity: 1 };
    });
  }

  // Find cursor position (end of last visible non-empty line)
  const lastVisibleIdx = visibleLines.findLastIndex(l => l.text.length > 0);

  const bgStyle = background?.startsWith('animated-') ? undefined : { backgroundColor: background };

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', ...bgStyle }}>
      {background?.startsWith('animated-') && (
        <AbsoluteFill>
          {/* AnimatedBG will be integrated in Task 7 */}
          <div style={{ position: 'absolute', inset: 0, backgroundColor: '#0a1628' }} />
        </AbsoluteFill>
      )}
      <div style={{
        opacity: exitOpacity * enterOpacity,
        transform: `scale(${enterScale})`,
        width: '100%', maxWidth: 600,
      }}>
        <NotepadChrome title={data.windowTitle}>
          <div style={{
            padding: '20px 24px', minHeight: 160,
            fontFamily: "'Courier New', monospace", fontSize: 15,
            color: '#e5e5e5', lineHeight: 1.8,
          }}>
            {visibleLines.map((vl, i) => (
              <div key={i} style={{ opacity: vl.opacity, minHeight: '1.8em' }}>
                {vl.text}
                {i === lastVisibleIdx && cursorVisible && data.animation === 'typewriter' && (
                  <span style={{ borderRight: '2px solid #e5e5e5', marginLeft: 1 }}>{'\u200B'}</span>
                )}
              </div>
            ))}
          </div>
        </NotepadChrome>
      </div>
    </AbsoluteFill>
  );
}

export const NotepadWindowOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseNotepadData(props.content, props.metadata);
  return <NotepadWindowVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const NotepadWindow: React.FC<OverlayProps> = (props) => {
  const data = parseNotepadData(props.content, props.metadata);
  return <NotepadWindowVisual data={data} durationInFrames={props.durationInFrames} background={data.background} />;
};
```

- [ ] **Step 2: Register in BeeComposition.tsx**

Add import:
```ts
import { NotepadWindowOverlay, NotepadWindow } from './remotion/cards/NotepadWindow';
```

Add to `OVERLAY_COMPONENTS`:
```ts
NOTEPAD: NotepadWindowOverlay,
```

Add to `VISUAL_COMPONENTS`:
```ts
NOTEPAD: NotepadWindow,
```

- [ ] **Step 3: Run all tests**

Run: `cd video-editor/web && npx vitest run`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add web/src/components/remotion/cards/NotepadWindow.tsx web/src/components/BeeComposition.tsx
git commit -m "feat: add NotepadWindow with typewriter animation and macOS chrome"
```

---

### Task 6: MapAnnotation — Parser + Tests

**Files:**
- Create: `web/src/components/remotion/MapAnnotation.tsx` (parser only)
- Create: `web/src/components/remotion/MapAnnotation.test.ts`

- [ ] **Step 1: Write the parser test file**

```ts
// web/src/components/remotion/MapAnnotation.test.ts
import { describe, test, expect } from 'vitest';
import { parseMapAnnotationData } from './MapAnnotation';

describe('parseMapAnnotationData', () => {
  test('parses circle shape', () => {
    const content = JSON.stringify([{ type: 'circle', x: 0.5, y: 0.5, r: 0.1 }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'circle', x: 0.5, y: 0.5, r: 0.1 }]);
  });

  test('parses path shape', () => {
    const content = JSON.stringify([{ type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] }]);
  });

  test('parses rect shape', () => {
    const content = JSON.stringify([{ type: 'rect', x: 0.2, y: 0.3, w: 0.4, h: 0.2 }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'rect', x: 0.2, y: 0.3, w: 0.4, h: 0.2 }]);
  });

  test('parses mixed shapes array', () => {
    const content = JSON.stringify([
      { type: 'circle', x: 0.5, y: 0.5, r: 0.1 },
      { type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] },
    ]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toHaveLength(2);
  });

  test('defaults color to red (#dc2626)', () => {
    const result = parseMapAnnotationData('[]');
    expect(result.color).toBe('#dc2626');
  });

  test('resolves named color from metadata', () => {
    const result = parseMapAnnotationData('[]', { color: 'teal' });
    expect(result.color).toBe('#0d9488');
  });

  test('passes through hex color from metadata', () => {
    const result = parseMapAnnotationData('[]', { color: '#ff00ff' });
    expect(result.color).toBe('#ff00ff');
  });

  test('malformed JSON returns empty shapes', () => {
    const result = parseMapAnnotationData('[invalid');
    expect(result.shapes).toEqual([]);
  });

  test('skips invalid shape entries', () => {
    const content = JSON.stringify([
      { type: 'circle', x: 0.5, y: 0.5, r: 0.1 },
      { type: 'unknown' },
      { type: 'circle' }, // missing x, y, r
      { type: 'path', points: [[0.1, 0.2]] },
    ]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toHaveLength(2); // only valid circle and path
  });

  test('handles null metadata', () => {
    const result = parseMapAnnotationData('[]', null);
    expect(result.color).toBe('#dc2626');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd video-editor/web && npx vitest run src/components/remotion/MapAnnotation.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the parser**

Create `web/src/components/remotion/MapAnnotation.tsx`:

```ts
// web/src/components/remotion/MapAnnotation.tsx
import { resolveColor } from './overlays';

export type AnnotationShape =
  | { type: 'circle'; x: number; y: number; r: number }
  | { type: 'path'; points: [number, number][] }
  | { type: 'rect'; x: number; y: number; w: number; h: number };

export interface MapAnnotationData {
  shapes: AnnotationShape[];
  color: string;
}

function isValidShape(s: any): s is AnnotationShape {
  if (!s || typeof s.type !== 'string') return false;
  if (s.type === 'circle') return typeof s.x === 'number' && typeof s.y === 'number' && typeof s.r === 'number';
  if (s.type === 'path') return Array.isArray(s.points) && s.points.length >= 1;
  if (s.type === 'rect') return typeof s.x === 'number' && typeof s.y === 'number' && typeof s.w === 'number' && typeof s.h === 'number';
  return false;
}

export function parseMapAnnotationData(
  content: string,
  metadata?: Record<string, any> | null,
): MapAnnotationData {
  let shapes: AnnotationShape[] = [];

  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) {
      shapes = parsed.filter(isValidShape);
    }
  } catch {
    // malformed JSON → empty shapes
  }

  return {
    shapes,
    color: resolveColor(metadata?.color || 'red'),
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd video-editor/web && npx vitest run src/components/remotion/MapAnnotation.test.ts`
Expected: PASS — all 10 tests

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/MapAnnotation.tsx web/src/components/remotion/MapAnnotation.test.ts
git commit -m "feat: add MapAnnotation parser with shape validation and tests"
```

---

### Task 7: MapAnnotation — React Component + Registration

**Files:**
- Modify: `web/src/components/remotion/MapAnnotation.tsx` (add React component)
- Modify: `web/src/components/BeeComposition.tsx` (add to OVERLAY_COMPONENTS)

- [ ] **Step 1: Add the React component to MapAnnotation.tsx**

Add imports and SVG overlay component. Uses `DrawPath` for path shapes, manual spring stagger per shape, pulsing dot for circles.

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from './primitives/QualityContext';
import { DrawPath } from './primitives/DrawPath';
import type { OverlayProps } from './overlays';

// ... (existing parser code stays above) ...

function circleSvgPath(cx: number, cy: number, r: number): string {
  return `M ${cx - r} ${cy} A ${r} ${r} 0 1 1 ${cx + r} ${cy} A ${r} ${r} 0 1 1 ${cx - r} ${cy}`;
}

function pathSvgD(points: [number, number][]): string {
  if (points.length === 0) return '';
  const [first, ...rest] = points.map(([x, y]) => [Math.round(x * 1920), Math.round(y * 1080)]);
  if (rest.length === 0) return `M ${first[0]} ${first[1]}`;
  // Quadratic bezier through points
  let d = `M ${first[0]} ${first[1]}`;
  for (const [x, y] of rest) {
    d += ` L ${x} ${y}`;
  }
  return d;
}

export const MapAnnotation: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const { shapes, color } = parseMapAnnotationData(content, metadata);
  const staggerInterval = Math.round(10 * timingMultiplier);

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  if (shapes.length === 0) return null;

  return (
    <AbsoluteFill style={{ opacity: exitOpacity }}>
      <svg viewBox="0 0 1920 1080" style={{
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none',
      }}>
        {shapes.map((shape, i) => {
          const delay = i * staggerInterval;
          const progress = spring({
            frame: Math.max(0, frame - delay), fps, config: springConfig,
          });

          if (shape.type === 'circle') {
            const cx = Math.round(shape.x * 1920);
            const cy = Math.round(shape.y * 1080);
            const r = Math.round(shape.r * Math.min(1920, 1080));
            const scale = interpolate(progress, [0, 1], [0, 1]);
            const pulseScale = interpolate(frame % 30, [0, 15, 30], [1, 1.5, 1], {
              extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
            });

            return (
              <g key={i} transform={`translate(${cx}, ${cy}) scale(${scale}) translate(${-cx}, ${-cy})`}>
                {/* Glow ring */}
                <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={20} opacity={0.3} />
                {/* Main ring */}
                <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={3} />
                {/* Pulsing center dot */}
                <circle cx={cx} cy={cy} r={6} fill={color}
                  transform={`translate(${cx}, ${cy}) scale(${pulseScale}) translate(${-cx}, ${-cy})`} />
              </g>
            );
          }

          if (shape.type === 'rect') {
            const x = Math.round(shape.x * 1920);
            const y = Math.round(shape.y * 1080);
            const w = Math.round(shape.w * 1920);
            const h = Math.round(shape.h * 1080);
            const rectOpacity = interpolate(progress, [0, 1], [0, 1]);

            return (
              <rect key={i} x={x} y={y} width={w} height={h}
                stroke={color} strokeWidth={2} fill={color} fillOpacity={0.1}
                opacity={rectOpacity} />
            );
          }

          return null; // paths handled below
        })}
      </svg>

      {/* DrawPath for path shapes (rendered outside SVG since DrawPath has its own SVG) */}
      {shapes.map((shape, i) => {
        if (shape.type !== 'path') return null;
        const delay = i * staggerInterval;
        const d = pathSvgD(shape.points);
        if (!d) return null;

        return (
          <DrawPath
            key={`path-${i}`}
            d={d}
            fromFrame={delay}
            toFrame={delay + 30}
            strokeWidth={4}
            color={color}
          />
        );
      })}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Register in BeeComposition.tsx**

Add import:
```ts
import { MapAnnotation } from './remotion/MapAnnotation';
```

Add to `OVERLAY_COMPONENTS`:
```ts
MAP_ANNOTATION: MapAnnotation,
```

- [ ] **Step 3: Run all tests**

Run: `cd video-editor/web && npx vitest run`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add web/src/components/remotion/MapAnnotation.tsx web/src/components/BeeComposition.tsx
git commit -m "feat: add MapAnnotation SVG overlay with circle, path, rect shapes"
```

---

### Task 8: AnimatedBG + PhotoViewerCard Integration

**Files:**
- Create: `web/src/components/remotion/cards/AnimatedBG.tsx`
- Modify: `web/src/components/remotion/cards/PhotoViewerCard.tsx`
- Modify: `web/src/components/remotion/cards/NotepadWindow.tsx`

- [ ] **Step 1: Create AnimatedBG helper component**

```tsx
// web/src/components/remotion/cards/AnimatedBG.tsx
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

const PRESET_COLORS: Record<string, string> = {
  'animated-teal': '13, 148, 136',
  'animated-red': '220, 38, 38',
  'animated-blue': '59, 130, 246',
};

interface AnimatedBGProps {
  preset: string;
}

export const AnimatedBG: React.FC<AnimatedBGProps> = ({ preset }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const rgb = PRESET_COLORS[preset] || PRESET_COLORS['animated-teal'];

  // Slow orb drift
  const orb1X = interpolate(frame, [0, durationInFrames], [-10, 10], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const orb2X = interpolate(frame, [0, durationInFrames], [10, -5], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const streakY = interpolate(frame, [0, durationInFrames], [0, 50], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      {/* Base gradient */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(135deg, #0a1628 0%, #0d2847 30%, #0a1628 50%, #0f3060 70%, #0a1628 100%)',
      }} />
      {/* Orb 1 */}
      <div style={{
        position: 'absolute', top: '-20%', left: '-10%', width: '60%', height: '140%',
        background: `radial-gradient(ellipse, rgba(${rgb}, 0.15) 0%, transparent 70%)`,
        transform: `translateX(${orb1X}%)`,
      }} />
      {/* Orb 2 */}
      <div style={{
        position: 'absolute', top: '10%', right: '-20%', width: '50%', height: '100%',
        background: `radial-gradient(ellipse, rgba(${rgb}, 0.1) 0%, transparent 60%)`,
        transform: `translateX(${orb2X}%)`,
      }} />
      {/* Light streaks */}
      <div style={{
        position: 'absolute', top: 0, left: '20%', width: 2, height: '200%',
        background: `linear-gradient(180deg, transparent, rgba(${rgb}, 0.3), transparent)`,
        transform: `rotate(-25deg) translateY(${streakY}px)`,
      }} />
      <div style={{
        position: 'absolute', top: 0, left: '60%', width: 1, height: '200%',
        background: `linear-gradient(180deg, transparent, rgba(${rgb}, 0.2), transparent)`,
        transform: `rotate(-20deg) translateY(${streakY * 0.7}px)`,
      }} />
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Integrate AnimatedBG into PhotoViewerCard**

In `web/src/components/remotion/cards/PhotoViewerCard.tsx`:

Add import at top:
```ts
import { AnimatedBG } from './AnimatedBG';
```

In the `PhotoViewerCard` export (the visual-mode one, line ~210), change:
```ts
return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} background="#000" />;
```
to:
```ts
const bg = props.metadata?.background || '#000';
return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} background={bg} />;
```

In `PhotoViewerCardVisual`, update the `AbsoluteFill` to conditionally render AnimatedBG:

Replace:
```tsx
<AbsoluteFill style={{
  backgroundColor: background,
  justifyContent: 'center', alignItems: 'center',
}}>
```
with:
```tsx
<AbsoluteFill style={{
  backgroundColor: background?.startsWith('animated-') ? undefined : background,
  justifyContent: 'center', alignItems: 'center',
}}>
  {background?.startsWith('animated-') && <AnimatedBG preset={background} />}
```

- [ ] **Step 3: Integrate AnimatedBG into NotepadWindow**

In `web/src/components/remotion/cards/NotepadWindow.tsx`:

Add import:
```ts
import { AnimatedBG } from './AnimatedBG';
```

Replace the placeholder AnimatedBG div (the `{/* AnimatedBG will be integrated in Task 7 */}` comment block) with:
```tsx
{background?.startsWith('animated-') && (
  <AbsoluteFill>
    <AnimatedBG preset={background} />
  </AbsoluteFill>
)}
```

- [ ] **Step 4: Run all tests**

Run: `cd video-editor/web && npx vitest run`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add web/src/components/remotion/cards/AnimatedBG.tsx web/src/components/remotion/cards/PhotoViewerCard.tsx web/src/components/remotion/cards/NotepadWindow.tsx
git commit -m "feat: add AnimatedBG helper, integrate into PhotoViewerCard and NotepadWindow"
```

---

### Task 9: Final Verification + Docs

- [ ] **Step 1: Run the full test suite**

Run: `cd video-editor/web && npx vitest run`
Expected: All tests pass

- [ ] **Step 2: Verify TypeScript compilation**

Run: `cd video-editor/web && npx tsc --noEmit`
Expected: No type errors

- [ ] **Step 3: Update CLAUDE.md component table**

Update the count from 19 to 21 and add new components to the Remotion Components table in `video-editor/CLAUDE.md`:

```markdown
| NotepadWindow | `NOTEPAD` overlay/visual | macOS-style text editor with typewriter animation |
| MapAnnotation | `MAP_ANNOTATION` overlay | Red SVG circles, paths, rects on aerial footage |
```

Also add note about CaptionOverlay enhancement:
Update the CaptionOverlay row description to: `Karaoke/phrase word-by-word captions with {color:keyword} markup`

- [ ] **Step 4: Commit docs update**

```bash
git add video-editor/CLAUDE.md
git commit -m "docs: add P1 overlay components to CLAUDE.md"
```
