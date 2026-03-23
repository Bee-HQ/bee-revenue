# P0 Overlay Components — Design Spec

**Date:** 2026-03-22
**Status:** Draft
**Source:** Dr Insanity video audit (`docs/reference/dr-insanity-visual-effects-audit.md`)

---

## Overview

5 new Remotion overlay components to close the biggest gaps identified in the Dr Insanity visual effects audit. These are the most frequently used effects that we don't yet support.

### Components

| # | Component | Type | Directory | Registry |
|---|-----------|------|-----------|----------|
| 1 | PhotoViewerCard | Dual (overlay + visual) | `remotion/cards/` | PHOTO_VIEWER |
| 2 | SourceBadge | Overlay only | `remotion/` | SOURCE_BADGE |
| 3 | BulletList | Dual (overlay + visual) | `remotion/cards/` | BULLET_LIST |
| 4 | InfoCard | Dual (overlay + visual) | `remotion/cards/` | INFO_CARD |
| 5 | Watermark | Project-level | `remotion/` | N/A (composition-level) |

### File Structure

```
web/src/components/remotion/
├── cards/
│   ├── PhotoViewerCard.tsx
│   ├── PhotoViewerCard.test.ts
│   ├── InfoCard.tsx
│   ├── InfoCard.test.ts
│   ├── BulletList.tsx
│   └── BulletList.test.ts
├── SourceBadge.tsx
├── SourceBadge.test.ts
└── Watermark.tsx
```

### Conventions (from codebase analysis)

All components follow the established patterns:

- **Interface:** `OverlayProps` (`content: string`, `metadata?: Record<string, any> | null`, `durationInFrames: number`)
- **Metadata mapping:** In `BeeComposition.tsx`, the entire `OverlayEntry` object is passed as `metadata` (line 136: `metadata={entry}`). So any field on the storyboard overlay entry (e.g., `src`, `animation`, `position`) is available as `metadata.fieldName`.
- **Dual export pattern:** `ComponentOverlay` (transparent bg, for `OVERLAY_COMPONENTS`) and `Component` (solid bg, for `VISUAL_COMPONENTS`). Internal rendering logic lives in a private `*Visual` component.
- **Parser pattern:** Every component exports a pure `parse*Data(content, metadata?)` function that handles both `content` string parsing and `metadata` field fallback. Content uses `—` (em-dash) as delimiter for compound values.
- **Animation:** `useCurrentFrame()` + `interpolate()` with `{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }` always. Exit animation: last 15 frames fade to 0. Spring via `spring()` + `useVideoConfig()` for fps. Use `useQuality()` for spring configs and timing multipliers. All frame windows in animation specs should scale with `timingMultiplier` from `useQuality()`.
- **Stagger pattern:** For vertically-stacked items in flow/flex layouts, use **manual per-item `spring()` stagger** (the KineticText pattern): `delay = i * staggerFrames`, `spring({ frame: Math.max(0, frame - delay), fps, config })`. Do NOT use `StaggerChildren` — it wraps children in `AbsoluteFill` which breaks flow layouts.
- **Style:** Inline React `style` objects only (no Tailwind/CSS). `AbsoluteFill` as root. Dark crime palette: `#dc2626` red accent, `#0d9488` teal, `#d97706` gold. Font: `Arial, Helvetica, sans-serif`. All sizing assumes 1920x1080.
- **Media paths:** Use `mediaUrl()` from `SafeMedia.tsx` for all asset paths (photos, logos). Raw paths will 404 in dev preview.
- **Registration:** Add to `OVERLAY_COMPONENTS` and/or `VISUAL_COMPONENTS` in `BeeComposition.tsx`. Add `DEFAULT_DURATIONS` entry in `overlays.ts`.
- **Tests:** Colocated `.test.ts` files. Test pure parser functions and data transformations. No render tests.

---

## 1. PhotoViewerCard

### Purpose
Display a photo inside a macOS-style window frame with a name/role label. The signature "person identification" graphic used ~10x per Dr Insanity video.

### Storyboard Usage

Single card:
```json
{
  "type": "PHOTO_VIEWER",
  "content": "Craig Thetford — Victim",
  "src": "photos/craig.jpg",
  "animation": "slide-up"
}
```

Multi-card (side by side):
```json
{
  "type": "PHOTO_VIEWER",
  "content": "[{\"name\":\"Bill\",\"role\":\"Ex-husband\",\"src\":\"photos/bill.jpg\"},{\"name\":\"Scott\",\"src\":\"photos/scott.jpg\"}]"
}
```

### Parsed Data

```ts
interface PhotoViewerData {
  cards: Array<{
    name: string;
    role?: string;
    src?: string;
  }>;
  animation: 'slide-up' | 'slide-left' | 'scale';
  windowTitle: string;
}
```

`parsePhotoViewerData(content, metadata)`:
- If `content` starts with `[`, parse as JSON array of cards
- Otherwise, parse `"Name — Role"` as single card, `src` from `metadata.src`
- `animation` from `metadata.animation`, default `'slide-up'`
- `windowTitle` from `metadata.windowTitle`, default `'Photo Viewer'`

### Visual Design

macOS window chrome:
- **Title bar** (32px): Dark gray `#2d2d2d`, traffic light buttons (red `#ff5f57`, yellow `#febc2e`, green `#28c840`), centered title text in `#999`
- **Menu bar** (24px): Darker `#252525`, menu items (File, Edit, Image, View, Help) in `#aaa`, 11px
- **Photo area**: Dark `#333` background, photo via `mediaUrl(src)` centered with `object-fit: cover`
- **Name label**: Bottom bar `#1a1a1a`, name in white 18px bold, role in `#999` 12px
- **Window shadow**: `0 20px 60px rgba(0,0,0,0.6)`
- **Border radius**: 10px on window container

Multi-card: Cards placed side by side with 24px gap, each scaled to fit within the viewport. Second card delayed by 8 frames using manual spring stagger (same pattern as KineticText).

If `src` is missing or file not found, show a `User` icon from lucide-react (or a simple SVG person silhouette) on dark `#333` background.

### Animation Timeline

All frame windows scale with `timingMultiplier` from `useQuality()`.

| Frames | Effect |
|--------|--------|
| 0–20 | Window slides in via `spring()` (direction per `animation` prop) |
| 10–25 | Photo fades in (`interpolate` opacity 0→1) |
| 20–30 | Name label slides up from below (`interpolate` translateY) |
| last 15 | Standard fade out |

### Exports

- `PhotoViewerCardOverlay: React.FC<OverlayProps>` — transparent background
- `PhotoViewerCard: React.FC<OverlayProps>` — `#000` background
- `parsePhotoViewerData(content: string, metadata?: Record<string, any> | null): PhotoViewerData`

### DEFAULT_DURATIONS

`PHOTO_VIEWER: 5` (seconds)

### Test Cases

- Parse `"Name — Role"` content → `{ cards: [{ name: "Name", role: "Role" }] }`
- Parse JSON array content → multiple cards
- Empty content with metadata fallback
- Default animation and windowTitle
- Malformed JSON falls back to single card with content as name

---

## 2. SourceBadge

### Purpose
Small corner label indicating footage source type: `[ACTUAL]`, `[REENACTMENT]`, `[ACTUAL PHOTO]`, etc. Simple, persistent, unobtrusive.

### Storyboard Usage

```json
{
  "type": "SOURCE_BADGE",
  "content": "REENACTMENT",
  "position": "bottom-left"
}
```

### Parsed Data

```ts
interface SourceBadgeData {
  label: string;
  position: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
}
```

`parseSourceBadgeData(content, metadata)`:
- `label` from `content` or `metadata.text`
- `position` from `metadata.position`, default `'bottom-left'`

### Visual Design

- Background: `rgba(0, 0, 0, 0.6)`, padding `4px 10px`, border-radius `3px`
- Text: `#cccccc`, 13px, `'Courier New', monospace`, `letter-spacing: 0.5px`
- Displayed as `[LABEL]` (brackets added by component)
- Positioned with 24px margin from edge

### Animation Timeline

| Frames | Effect |
|--------|--------|
| 0–10 | Fade in (opacity 0→1) |
| hold | Persistent |
| last 15 | Standard fade out |

### Exports

- `SourceBadge: React.FC<OverlayProps>` — overlay only (no visual-mode variant needed)
- `parseSourceBadgeData(content: string, metadata?: Record<string, any> | null): SourceBadgeData`

### DEFAULT_DURATIONS

`SOURCE_BADGE: 30` (seconds — intentionally high so it fills the entire segment duration, since `SegmentOverlays` clamps to `Math.min(defaultDur, segDuration)`)

### Test Cases

- Parse content string → label
- Parse empty content with metadata.text fallback
- Default position is bottom-left
- Position from metadata

---

## 3. BulletList

### Purpose
Staggered reveal of text bars, each on its own semi-transparent background. Used for charge sheets, case summaries, key findings. The climactic summary graphic.

### Storyboard Usage

Newline-separated:
```json
{
  "type": "BULLET_LIST",
  "content": "INTENTIONALLY SHOT CRAIG\nMOVED AND HID THE BODY\nLIED ABOUT HIS WHEREABOUTS\nLOOTED SHARED ASSETS",
  "accent": "red",
  "style": "stagger"
}
```

JSON array:
```json
{
  "type": "BULLET_LIST",
  "content": "[\"Line one\", \"Line two\", \"Line three\"]"
}
```

### Parsed Data

```ts
interface BulletListData {
  items: string[];
  accent: 'red' | 'teal' | 'gold' | 'white';
  style: 'stagger' | 'cascade' | 'instant';
}
```

`parseBulletListData(content, metadata)`:
- If `content` starts with `[`, parse as JSON array
- Otherwise split on `\n`, trim, filter empty
- `accent` from `metadata.accent`, default `'red'`
- `style` from `metadata.style`, default `'stagger'`

### Visual Design

- Each item: `rgba(0, 0, 0, 0.75)` background, `14px 24px` padding, `border-left: 3px solid {accentColor}`
- Text: white `#fff`, 22px (scaled by item count — 18px if >6 items), `font-weight: 800`, `letter-spacing: 2px`, uppercase
- Items vertically stacked with 16px gap, left-aligned
- `cascade` style: each successive item offset 20px right, capped at 120px max indent (6 items max for this style to look good)
- `stagger`/`instant`: no indent
- Centered vertically in viewport with `80px` horizontal padding

Accent colors: `red: #dc2626`, `teal: #0d9488`, `gold: #d97706`, `white: #ffffff`

### Animation Timeline

Uses **manual per-item spring stagger** (KineticText pattern — NOT `StaggerChildren`):

```ts
const delay = i * staggerFrames; // ~8 frames, scaled by timingMultiplier
const progress = spring({ frame: Math.max(0, frame - delay), fps, config: springConfig });
const translateX = interpolate(progress, [0, 1], [-600, 0]); // slide in 600px from left
const opacity = interpolate(progress, [0, 1], [0, 1]);
```

**stagger** (default): Items slide in from left (-600px → 0) with ~8 frame interval.

**cascade**: Same slide-in but each item also indents progressively (20px per item, max 120px).

**instant**: All items visible at frame 0, no animation.

All styles: last 15 frames standard fade out.

### Exports

- `BulletListOverlay: React.FC<OverlayProps>` — transparent background
- `BulletList: React.FC<OverlayProps>` — `#000` background
- `parseBulletListData(content: string, metadata?: Record<string, any> | null): BulletListData`

### DEFAULT_DURATIONS

`BULLET_LIST: 6` (seconds)

### Test Cases

- Parse newline-separated content → items array
- Parse JSON array content → items array
- Empty lines filtered out
- Default accent (red) and style (stagger)
- Metadata overrides for accent/style
- Malformed JSON falls back to newline split

---

## 4. InfoCard

### Purpose
Generic structured information card with labeled sections on one side and an optional photo on the other. Covers sentencing cards, charge summaries, victim profiles, case timelines — any "info + optional photo" layout.

### Storyboard Usage

```json
{
  "type": "INFO_CARD",
  "content": "{\"sections\":[{\"header\":\"Charges\",\"body\":\"Possible first or second degree murder charge\"},{\"header\":\"Sentence\",\"body\":\"Life in prison with parole after 30 years\"}]}",
  "src": "photos/suspect.jpg",
  "photoSide": "right"
}
```

### Parsed Data

```ts
interface InfoCardSection {
  header: string;
  body: string;
  color?: string;  // header color override
}

interface InfoCardData {
  sections: InfoCardSection[];
  src?: string;
  photoSide: 'left' | 'right' | 'none';
}
```

`parseInfoCardData(content, metadata)`:
- Parse `content` as JSON object with `sections` array
- Fallback: if JSON parse fails (plain text or malformed), create single section with `header` from `metadata.header` or empty string, `body` from `content`
- `src` from `metadata.src`
- `photoSide` from `metadata.photoSide`, default `'right'`
- Section `color` defaults to `#dc2626` (red) for headers

### Visual Design

Split layout (when photo present):
- **Text side** (50%): Sections stacked vertically with 24px gap. Header in accent color (default `#dc2626`), 24px, `font-weight: 800`. Body in `#e5e5e5`, 16px, `line-height: 1.5`. Padding 40px.
- **Photo side** (50%): Photo via `mediaUrl(src)` centered, `object-fit: cover`, slight border-radius 4px
- Overall: Centered in viewport at 85% width, 75% height

No-photo layout (photoSide: 'none'):
- Sections centered, max-width 800px

### Animation Timeline

Uses **manual per-section spring stagger** (KineticText pattern — NOT `StaggerChildren`):

| Frames | Effect |
|--------|--------|
| 0–20 | Card container fades in (opacity) |
| 5+ | Sections stagger in via manual `spring()`, ~10 frame interval per section |
| 10–25 | Photo slides in from its side via `spring()` (if present) |
| last 15 | Standard fade out |

All frame windows scale with `timingMultiplier`.

### Exports

- `InfoCardOverlay: React.FC<OverlayProps>` — transparent background
- `InfoCard: React.FC<OverlayProps>` — `#0a0a0a` background
- `parseInfoCardData(content: string, metadata?: Record<string, any> | null): InfoCardData`

### DEFAULT_DURATIONS

`INFO_CARD: 6` (seconds)

### Test Cases

- Parse JSON content with sections array
- Plain text fallback → single section
- Malformed JSON → plain text fallback
- Default photoSide (right), src from metadata
- Empty sections array
- Section color override

---

## 5. Watermark

### Purpose
Persistent semi-transparent channel logo/text overlay. Applied at the composition level across all segments, not per-segment.

### Configuration

**Project-level** (in `BeeProject`):
```json
{
  "watermark": {
    "text": "DR. INSANITY",
    "src": "assets/logo.png",
    "position": "bottom-right",
    "opacity": 0.3,
    "enabled": true
  }
}
```

If `watermark` is absent or `enabled` is false/undefined, no watermark is rendered. Off by default.

### Type Definition

`WatermarkConfig` must be defined in `shared/types.ts` (not in the component file) to avoid circular dependencies — `shared/types.ts` is consumed by both the Express server and the React frontend.

```ts
// In shared/types.ts
interface WatermarkConfig {
  text?: string;
  src?: string;
  position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  opacity: number;
  enabled: boolean;
}

interface BeeProject {
  // ... existing fields
  watermark?: WatermarkConfig;
}
```

### Visual Design

- **Text mode**: White `#fff`, 16px, `font-weight: 700`, `letter-spacing: 2px`, `font-family: Arial`
- **Image mode**: Logo image via `mediaUrl(src)`, max height 40px, auto width
- **Both provided**: Image takes precedence, text as fallback
- Opacity: configurable, default 0.3
- Position: 30px margin from edges
- No background, no border — just the content at reduced opacity

### Integration

Rendered in `BeeComposition.tsx` as the **last layer** (on top of everything), outside the segment loop:

```tsx
{storyboard.watermark?.enabled && (
  <AbsoluteFill style={{ zIndex: 9999 }}>
    <Watermark config={storyboard.watermark} />
  </AbsoluteFill>
)}
```

**Not registered** in `OVERLAY_COMPONENTS` — this is a composition-level concern, not a segment overlay.

### Props

```ts
interface WatermarkProps {
  config: WatermarkConfig;
}
```

This is the one component that does NOT use `OverlayProps` since it's not driven by storyboard overlay entries.

### Animation

None — static, persistent. No entrance/exit animation.

### Exports

- `Watermark: React.FC<WatermarkProps>`

No colocated test file — the component has no parser function or complex logic. It renders a positioned text/image at a given opacity.

---

## Registration Summary

### overlays.ts — DEFAULT_DURATIONS additions

```ts
PHOTO_VIEWER: 5,
SOURCE_BADGE: 30,
BULLET_LIST: 6,
INFO_CARD: 6,
```

### BeeComposition.tsx — Registry additions

```ts
import { PhotoViewerCardOverlay, PhotoViewerCard } from './remotion/cards/PhotoViewerCard';
import { BulletListOverlay, BulletList } from './remotion/cards/BulletList';
import { InfoCardOverlay, InfoCard } from './remotion/cards/InfoCard';
import { SourceBadge } from './remotion/SourceBadge';
import { Watermark } from './remotion/Watermark';

// Add to OVERLAY_COMPONENTS:
PHOTO_VIEWER: PhotoViewerCardOverlay,
SOURCE_BADGE: SourceBadge,
BULLET_LIST: BulletListOverlay,
INFO_CARD: InfoCardOverlay,

// Add to VISUAL_COMPONENTS:
PHOTO_VIEWER: PhotoViewerCard,
BULLET_LIST: BulletList,
INFO_CARD: InfoCard,
```

Watermark: rendered directly in `BeeComposition` return, not via registry.

---

## Testing Strategy

Each component with a parser function gets a colocated `.test.ts`:

1. **Parser functions** — the primary test target:
   - Parse content string format ("Name — Role")
   - Parse JSON content format
   - Fallback to metadata fields when content is empty
   - Default values for optional fields
   - Edge cases (empty content, malformed JSON → graceful fallback)

2. **Data transformations** — multi-card layout, item count scaling, etc.

No render tests (consistent with existing test patterns in this codebase).

Components without parsers (Watermark) have no test file.

---

## Out of Scope

- Animated backgrounds (teal motion graphics) — deferred to medium priority
- Map annotation overlays — deferred
- Per-word caption color emphasis — deferred
- Notepad window frame — deferred
- Face/content blur — requires ML, out of scope for Remotion
