# P1 Overlay Components — Design Spec

**Date:** 2026-03-22
**Status:** Draft
**Source:** Dr Insanity video audit (`docs/reference/dr-insanity-visual-effects-audit.md`)

---

## Overview

4 medium-priority components to complement the P0 batch. These add visual polish: colored caption keywords, a notepad text window, animated backgrounds for card components, and red annotation overlays for aerial footage.

### Components

| # | Component | Type | Directory | Change Type |
|---|-----------|------|-----------|-------------|
| 1 | Caption Keyword Coloring | Enhancement | `remotion/CaptionOverlay.tsx` | Modify existing |
| 2 | NotepadWindow | Dual (overlay + visual) | `remotion/cards/` | New component |
| 3 | AnimatedBackground | Helper function | `remotion/cards/AnimatedBG.tsx` | New helper |
| 4 | MapAnnotation | Overlay only | `remotion/` | New component |

### File Structure

```
web/src/components/remotion/
├── CaptionOverlay.tsx              (MODIFY — add color markup parsing)
├── CaptionOverlay.test.ts          (CREATE — test color parsing)
├── MapAnnotation.tsx               (CREATE)
├── MapAnnotation.test.ts           (CREATE)
├── cards/
│   ├── NotepadWindow.tsx           (CREATE)
│   ├── NotepadWindow.test.ts       (CREATE)
│   ├── AnimatedBG.tsx              (CREATE — shared helper)
│   └── PhotoViewerCard.tsx         (MODIFY — accept animated bg)
```

### Conventions

Same as P0 spec — `OverlayProps` interface, dual export pattern, pure parser functions, manual spring stagger, `useQuality()`, `mediaUrl()`, inline styles, 1920x1080, colocated tests.

### Conventions Addendum — Shared Named Color Map

Extract the 4-color named palette to `overlays.ts` as an exported constant (currently duplicated in BulletList and about to be used by CaptionOverlay and MapAnnotation):

```ts
// overlays.ts
export const NAMED_COLORS: Record<string, string> = {
  red: '#dc2626',
  teal: '#0d9488',
  gold: '#d97706',
  white: '#ffffff',
};

export function resolveColor(color: string): string {
  return NAMED_COLORS[color] || color; // pass-through hex values
}
```

All components that resolve named colors should import `resolveColor` from `overlays.ts`. BulletList's inline `ACCENT_COLORS` map can be refactored to use this, but that's optional cleanup — new components should use `resolveColor`.

---

## 1. Caption Keyword Coloring

### Purpose

Add per-word color emphasis to the existing `CaptionOverlay` component. In the Dr Insanity video, keywords like "blood" are colored red while the rest of the caption is yellow. This is a backward-compatible enhancement.

### Markup Syntax

Color tokens use `{color:text}` syntax within the caption text:

```
Or is that {red:bl**d}?
She was found with {red:multiple injuries} on the {teal:property}
```

Named colors: `red` → `#dc2626`, `teal` → `#0d9488`, `gold` → `#d97706`, `white` → `#ffffff`

Hex colors: `{#ff00ff:custom color}`

Text without any `{...}` markup renders exactly as before (backward compatible).

### Parsed Data

```ts
interface CaptionWord {
  text: string;
  color?: string;  // hex color override, undefined = default highlight color
}
```

`parseCaptionWords(text: string): CaptionWord[]`:

Algorithm: Run regex against the **full text first** (not split-then-match), to correctly handle multi-word spans like `{teal:DNA evidence}`.

```ts
const regex = /\{([^:}]+):([^}]+)\}|(\S+)/g;
```

This regex matches either:
1. `{color:text with spaces}` — captures color group and inner text (may contain spaces)
2. `\S+` — a plain word (no markup)

For each match:
- If groups 1+2 match (color markup): resolve named color → hex, split inner text on whitespace, return each word as `{ text: word, color: hex }`
- If group 3 matches (plain word): return `{ text: word, color: undefined }`
- Partial markup like `{red:bl**d}?` — the regex matches `{red:bl**d}` and then `?` as a separate plain word. To handle trailing punctuation attached to markup, the regex can be adjusted or the trailing chars merged. For simplicity, treat trailing punctuation as a separate token — visually it won't matter at 42px font size.

Named color resolution uses a shared `NAMED_COLORS` map (see Conventions addendum below).

This function is **exported from `CaptionOverlay.tsx`** and tested in `CaptionOverlay.test.ts`.

### Integration

The component's external `Props` interface (`{ text: string; style?: 'karaoke' | 'phrase' }`) is **unchanged**. `parseCaptionWords` is called internally, replacing the existing `text.split(/\s+/)` in both renderers.

### Visual Design Changes

In the karaoke renderer:
- Words with a `color` override use that color instead of `#fbbf24` (yellow) when active/past
- Words without `color` use the existing `#fbbf24` highlight
- Inactive words remain white at 0.6 opacity (unchanged)

In the phrase renderer:
- Colored words keep their color in the phrase display
- Non-colored words use white (unchanged)

### Backward Compatibility

- Existing caption text (no `{...}` markup) produces words with `color: undefined`
- `undefined` color → existing behavior (`#fbbf24` for karaoke, `#fff` for phrase)
- Zero visual change for existing storyboards

### Test Cases

- `"plain text"` → all words with `color: undefined`
- `"is that {red:blood}?"` → `[{text:"is"}, {text:"that"}, {text:"blood?", color:"#dc2626"}]`
- `"{teal:DNA evidence}"` → `[{text:"DNA", color:"#0d9488"}, {text:"evidence", color:"#0d9488"}]`
- `"{#ff00ff:custom}"` → `[{text:"custom", color:"#ff00ff"}]`
- `"no {invalid markup"` → all words with `color: undefined` (graceful handling)

---

## 2. NotepadWindow

### Purpose

macOS-style text editor window showing notes, bullet points, or case summaries with typewriter text animation. Used at 44:00 in the Dr Insanity video to show phone call notes typed out line by line.

### Storyboard Usage

```json
{
  "type": "NOTEPAD",
  "content": "Previous Phone Call:\n- said her mom is crazy\n- thinks she might've poisoned Craig\n- Current whereabouts unknown",
  "animation": "typewriter",
  "windowTitle": "Notepad"
}
```

### Parsed Data

```ts
interface NotepadData {
  lines: string[];
  animation: 'typewriter' | 'lines' | 'instant';
  windowTitle: string;
  background: string;  // solid color or animated bg key
}
```

`parseNotepadData(content, metadata)`:
- Split `content` on `\n`, preserve all lines (don't filter empty — blank lines are intentional in notes)
- `animation` from `metadata.animation`, default `'typewriter'`
- `windowTitle` from `metadata.windowTitle`, default `'Notepad'`
- `background` from `metadata.background`, default `'#000'`

### Visual Design

macOS window chrome — **do NOT reuse** `MacWindowChrome` from PhotoViewerCard (different menu items, no name label). Build a new internal `NotepadChrome` component with:
- **Title bar** (32px): `#2d2d2d`, traffic lights, centered title
- **Menu bar** (24px): `#252525`, items: File, Edit, Search, View, Help (different from PhotoViewerCard's Image menu)
- **Text body**: `#1e1e1e` background, padding `20px 24px`, monospace font
  - Font: `'Courier New', monospace`, 15px, `#e5e5e5`, line-height 1.8
  - Blinking cursor: `border-right: 2px solid #e5e5e5`, toggles via `Math.floor(frame / 15) % 2 === 0` (not `interpolate` — `interpolate` does not loop)
- **Window**: `#1e1e1e`, border-radius 10px, shadow, max-width 600px centered

Note: The `background` metadata prop only applies to the `NotepadWindow` visual-mode export, not `NotepadWindowOverlay` (which is always transparent). This matches the dual-export pattern where the overlay variant has no background.

### Animation Timeline

**typewriter** (default): Characters appear one by one across all lines. Total chars distributed evenly across `durationInFrames`. Cursor tracks the typing position.

```ts
const totalChars = lines.join('\n').length;
const charsToShow = Math.floor((frame / durationInFrames) * totalChars);
```

**lines**: Lines appear one at a time via manual spring stagger (~12 frame interval). Each line fades/slides in. No character-by-character typing.

**instant**: All text visible at frame 0.

All styles: last 15 frames standard fade out.

### Exports

- `NotepadWindowOverlay: React.FC<OverlayProps>` — transparent background (no window bg visible)
- `NotepadWindow: React.FC<OverlayProps>` — uses `background` from metadata (default `#000`, supports animated bg keys)
- `parseNotepadData(content: string, metadata?: Record<string, any> | null): NotepadData`

### DEFAULT_DURATIONS

`NOTEPAD: 6` (seconds)

### Test Cases

- Parse multiline content → lines array
- Single line content
- Default animation (typewriter), windowTitle (Notepad), background (#000)
- Metadata overrides for animation/windowTitle/background
- Empty content → single empty line
- Preserves blank lines (doesn't filter)

---

## 3. AnimatedBackground

### Purpose

Flowing motion graphics backdrop for card components (PhotoViewerCard, NotepadWindow). In the Dr Insanity video, teal/cyan light streaks animate behind Photo Viewer windows. Not a standalone component — a shared helper function used by the visual-mode (solid bg) variants of card components.

### Implementation

A shared React component in `remotion/cards/AnimatedBG.tsx` that renders animated radial gradients and light streaks using `interpolate()`.

```ts
interface AnimatedBGProps {
  preset: 'animated-teal' | 'animated-red' | 'animated-blue';
}
```

The component uses `useCurrentFrame()` and `useVideoConfig()` internally to get `frame` and `durationInFrames` for driving the `interpolate()` orb/streak motion. No need to pass these as props — they come from the Remotion `Sequence` context.

### Visual Design

Three presets, each with:
- **Base**: Dark gradient background (`#0a1628` → darker)
- **Orbs**: 2-3 radial gradient ellipses with the accent color at 10-15% opacity, slowly drifting via `interpolate()` on `translateX`/`translateY`
- **Light streaks**: 2-3 thin diagonal lines (1-2px) with accent color at 20-30% opacity, slowly translating

Color map:
- `animated-teal`: `rgba(13, 148, 136, ...)` (`#0d9488`)
- `animated-red`: `rgba(220, 38, 38, ...)` (`#dc2626`)
- `animated-blue`: `rgba(59, 130, 246, ...)` (`#3b82f6`)

Animation: Orbs drift ~100px over the full duration using `interpolate(frame, [0, durationInFrames], [startPos, endPos])`. Streaks drift ~50px. Slow, subtle, ambient motion.

### Integration

**PhotoViewerCard** and **NotepadWindow** visual-mode variants check their `background` prop:
- If it starts with `animated-`, render `<AnimatedBG preset={background} />` as the background layer instead of a solid color
- Otherwise render solid `backgroundColor` as before

Modify `PhotoViewerCardVisual` and `NotepadWindowVisual` to accept and render the animated background.

### No Registration

Not a standalone component. Not registered in any registry. No `DEFAULT_DURATIONS` entry. No `OverlayProps` interface.

### Test Cases

No test file — purely visual, no parser logic. The preset resolution (string → color) could be tested if desired, but it's a simple map lookup.

---

## 4. MapAnnotation

### Purpose

Draw red annotation shapes (circles, paths, rectangles) over aerial/satellite footage. Used at 6:00 and 35:00 in the Dr Insanity video to highlight areas on aerial views with red markings and path trails.

### Storyboard Usage

```json
{
  "type": "MAP_ANNOTATION",
  "content": "[{\"type\":\"circle\",\"x\":0.31,\"y\":0.37,\"r\":0.04},{\"type\":\"path\",\"points\":[[0.31,0.37],[0.47,0.46],[0.52,0.48]]}]",
  "color": "red"
}
```

### Parsed Data

```ts
type AnnotationShape =
  | { type: 'circle'; x: number; y: number; r: number }
  | { type: 'path'; points: [number, number][] }
  | { type: 'rect'; x: number; y: number; w: number; h: number };

interface MapAnnotationData {
  shapes: AnnotationShape[];
  color: string;  // resolved hex
}
```

Coordinates are normalized [0–1] and multiplied by 1920/1080 at render time (same pattern as Callout's target coordinates).

`parseMapAnnotationData(content, metadata)`:
- Parse `content` as JSON array of shapes
- Validate each shape has required fields, skip malformed entries
- `color` from `metadata.color`, resolve named → hex (same color map as BulletList), default `'red'` → `#dc2626`

### Visual Design

SVG overlay at `viewBox="0 0 1920 1080"`, same pattern as Callout component.

**Circle**:
- Glow ring: `stroke={color}` at 0.3 opacity, `strokeWidth: 20`
- Main ring: `stroke={color}`, `strokeWidth: 3`
- Center dot: `fill={color}`, `r: 6`, pulsing scale via `interpolate(frame % 30, [0, 15, 30], [1, 1.5, 1])` (looping every 30 frames using modulo, not raw `interpolate` which doesn't loop)

**Path**:
- Uses a single `DrawPath` primitive call per path — `DrawPath` automatically renders a glow layer (strokeWidth * 3 at opacity 0.2) when quality tier is `'premium'`. Do NOT render a second DrawPath for glow.
- `stroke={color}`, `strokeWidth: 4`, `strokeLinecap: 'round'`

**Rect**:
- `stroke={color}`, `strokeWidth: 2`, `fill={color}` at 0.1 opacity
- Fade in via `interpolate` opacity

### Animation Timeline

All shapes stagger in with ~10 frame interval (manual spring per shape index).

- **Circles**: Scale from 0→1 via `spring()`
- **Paths**: Drawn via `DrawPath` over ~30 frames
- **Rects**: Fade in over ~15 frames

Last 15 frames: standard exit fade on entire SVG.

### Exports

- `MapAnnotation: React.FC<OverlayProps>` — overlay only (no visual-mode variant)
- `parseMapAnnotationData(content: string, metadata?: Record<string, any> | null): MapAnnotationData`

### DEFAULT_DURATIONS

`MAP_ANNOTATION: 6` (seconds)

### Test Cases

- Parse JSON array with circle shape → resolved coordinates
- Parse path shape with multiple points
- Parse rect shape
- Mixed shapes array
- Default color (red → #dc2626)
- Named color from metadata
- Hex color from metadata
- Malformed JSON → empty shapes array
- Invalid shape entries skipped

---

## Registration Summary

### overlays.ts — DEFAULT_DURATIONS additions

```ts
NOTEPAD: 6,
MAP_ANNOTATION: 6,
```

(No entry for AnimatedBG or CaptionOverlay — AnimatedBG is not a registered component, CaptionOverlay already exists and doesn't use the overlay registry)

### BeeComposition.tsx — Registry additions

```ts
import { NotepadWindowOverlay, NotepadWindow } from './remotion/cards/NotepadWindow';
import { MapAnnotation } from './remotion/MapAnnotation';

// Add to OVERLAY_COMPONENTS:
NOTEPAD: NotepadWindowOverlay,
MAP_ANNOTATION: MapAnnotation,

// Add to VISUAL_COMPONENTS:
NOTEPAD: NotepadWindow,
```

---

## Testing Strategy

Same as P0: colocated `.test.ts` files testing pure parser functions. No render tests.

- `CaptionOverlay.test.ts` — new file, tests `parseCaptionWords` function
- `NotepadWindow.test.ts` — tests `parseNotepadData`
- `MapAnnotation.test.ts` — tests `parseMapAnnotationData` with shape validation
- No test file for `AnimatedBG.tsx` (visual-only helper, no parser)

---

## Out of Scope

- Face/content blur — requires ML
- AtmosphericGlow (red mist) — complex particle effects, deferred
