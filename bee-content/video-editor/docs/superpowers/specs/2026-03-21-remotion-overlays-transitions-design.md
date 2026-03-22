# Remotion Animated Overlays & Transitions — Phase 1

## Goal

Replace static/missing renderers in BeeComposition with animated React components for all storyboard overlay types and transitions. Everything renders live in the Remotion Player preview and exports to MP4.

Phase 2 (animated SVG maps) is a separate spec.

## Motivation

Current state: BeeComposition handles video/image display, color filters, Ken Burns, lower thirds, timeline markers, and captions. But QUOTE_CARD, FINANCIAL_CARD, TEXT_OVERLAY have no Remotion renderer — they're either Pillow-generated PNGs (backend) or missing entirely. Transitions (DISSOLVE, FADE_FROM_BLACK) are defined in the storyboard but not rendered at all.

After this work: every visual element in the storyboard renders as an animated React component in the browser preview and MP4 export.

## Architecture

### New Components

```
web/src/components/remotion/
├── LowerThird.tsx          (exists — keep, already animated)
├── CaptionOverlay.tsx      (exists — keep)
├── KenBurns.tsx            (exists — keep)
├── PlaceholderFrame.tsx     (extract from BeeComposition)
├── SafeMedia.tsx            (extract SafeVideo + SafeImg from BeeComposition)
├── QuoteCard.tsx            (new)
├── FinancialCard.tsx        (new)
├── TextOverlay.tsx          (new)
├── TimelineMarker.tsx       (new — replaces inline JSX)
└── TransitionRenderer.tsx   (new)
```

### BeeComposition Changes

- Extract `PlaceholderFrame`, `SafeVideo`, `SafeImg` to separate files
- Overlay type dispatch via registry instead of if/else chains
- Add transition rendering (overlap + fade modes)
- Accept `transitionMode` prop from store
- Recalculate segment positions when overlap mode shifts frames

### Store Addition

`transitionMode: 'overlap' | 'fade'` in Zustand (default `'overlap'`). Toggle in RemotionPreview controls bar.

### No Backend Changes

Pillow graphics processors remain for CLI `bee-video assemble` workflow. Web editor preview/render uses only Remotion components.

## Overlay Components

### Uniform Interface

All overlay components receive:
```ts
interface OverlayProps {
  content: string;             // from entry.content
  metadata?: LayerEntryMetadata;  // from entry.metadata
  durationInFrames: number;    // capped to segment duration
}
```

Registry for dispatch:
```ts
const OVERLAY_COMPONENTS: Record<string, React.FC<OverlayProps>> = {
  LOWER_THIRD: LowerThirdOverlay,
  TIMELINE_MARKER: TimelineMarker,
  QUOTE_CARD: QuoteCard,
  FINANCIAL_CARD: FinancialCard,
  TEXT_OVERLAY: TextOverlay,
};
```

### QuoteCard

**Trigger:** `QUOTE_CARD` overlay type
**Content format:** `"quote text" — Author Name` (split on ` — `)
**Animation:**
1. Dark semi-transparent backdrop fades in (frames 0-10)
2. Accent bar slides from left edge (frames 5-20, spring easing)
3. Quote text fades in (frames 15-30)
4. Author name fades in below (frames 25-40)
5. Everything holds until fade-out in final 15 frames

**Accent colors:** Red (default), teal, gold — read from `metadata.color` if present
**Duration:** 4 seconds (120 frames), capped to segment length
**Position:** Center screen

### FinancialCard

**Trigger:** `FINANCIAL_CARD` overlay type
**Content format:** `$1.4 million — Insurance payout` (split on ` — `)
**Dollar parsing logic:**
```ts
function parseDollarAmount(text: string): { displayValue: string; numericValue: number } {
  // Remove $ and commas: "$1,400,000" → "1400000", "$1.4 million" → "1.4 million"
  const cleaned = text.replace(/[$,]/g, '').trim();
  const match = cleaned.match(/^([\d.]+)\s*(million|billion|thousand|k|m|b)?/i);
  if (!match) return { displayValue: text, numericValue: 0 };
  const num = parseFloat(match[1]);
  const multipliers: Record<string, number> = { thousand: 1e3, k: 1e3, million: 1e6, m: 1e6, billion: 1e9, b: 1e9 };
  const mult = match[2] ? (multipliers[match[2].toLowerCase()] || 1) : 1;
  const numericValue = num * mult;
  // Format display: "$1,400,000" or "$1.4M"
  const displayValue = match[2]
    ? `$${num} ${match[2]}`
    : `$${numericValue.toLocaleString()}`;
  return { displayValue, numericValue };
}
```
**Animation:**
1. Red panel slides up from bottom edge (frames 0-20, spring)
2. Dollar amount counts up from $0 to parsed `numericValue`, formatted with `$` and commas (frames 10-60). If parsing fails, display the raw text without count-up animation.
3. Description text fades in (frames 40-55)
4. Holds, then slides down to exit in final 15 frames

**Duration:** 3 seconds (90 frames)
**Position:** Bottom third of screen

### TextOverlay

**Trigger:** `TEXT_OVERLAY` overlay type
**Content:** Plain text string from `entry.content`
**Animation:** Typewriter effect — characters appear one by one with a blinking cursor. Semi-transparent dark backdrop behind text.
**Duration:** 3 seconds (90 frames)
**Position:** Center screen, white text

### TimelineMarker

**Trigger:** `TIMELINE_MARKER` overlay type (replaces current inline JSX in BeeComposition)
**Content:** Date or event text from `entry.content`
**Animation:**
1. Red bar slides in from right edge (frames 0-15, spring)
2. Text fades in on the bar (frames 10-20)
3. Holds
4. Slides out to right in final 15 frames

**Duration:** 3 seconds (90 frames)
**Position:** Top-right corner

### LowerThird (existing)

Already implemented as `LowerThird.tsx` with props `{ name, role, durationInFrames }` — different from `OverlayProps`. Create a thin wrapper `LowerThirdOverlay` that parses `OverlayProps` and delegates:

```tsx
function LowerThirdOverlay({ content, durationInFrames }: OverlayProps) {
  const parts = content.split(/\s*[—–-]\s*/);
  const name = parts[0]?.trim() || content;
  const role = parts[1]?.trim() || undefined;
  return <LowerThird name={name} role={role} durationInFrames={durationInFrames} />;
}
```

The registry entry for `LOWER_THIRD` points to `LowerThirdOverlay`, not `LowerThird` directly. The original `LowerThird.tsx` is unchanged.

## Transitions

### Two Modes

**Stored in Zustand:** `transitionMode: 'overlap' | 'fade'`
**UI toggle:** Button in RemotionPreview controls bar (next to CC button)
**Passed to BeeComposition:** `<BeeComposition transitionMode={transitionMode} ... />`

### Overlap Mode (true cross-dissolve)

Adjacent segments overlap by the transition duration:
- Segment N runs from frame A to frame B
- Segment N+1 starts at frame `B - transitionDuration` instead of frame B
- During the overlap window, both segments render
- `<TransitionRenderer>` controls the blend

Total video duration shrinks by the sum of all transition durations.

**Transition data in storyboard:** `seg.transition` is a `LayerEntry[]`. The first entry carries:
- `content_type`: `'DISSOLVE'` | `'FADE_FROM_BLACK'` (the transition type)
- `content`: `'1.0s'` or `'1.5s'` (duration as string with `s` suffix)

Parsing:
```ts
function getTransitionInfo(seg: Segment, fps: number): { type: string; durationInFrames: number } | null {
  const trans = seg.transition[0];
  if (!trans) return null;
  const durationSec = parseFloat(trans.content?.replace('s', '') || '1');
  return { type: trans.content_type, durationInFrames: Math.round(durationSec * fps) };
}
```

Position calculation:
```ts
let currentFrame = 0;
for (const seg of segments) {
  const duration = timeToFrames(seg.duration_seconds, fps);
  const trans = getTransitionInfo(seg, fps);
  const transitionDur = trans?.durationInFrames ?? 0;
  seg._from = currentFrame;
  seg._duration = duration;
  currentFrame += duration - transitionDur; // overlap
}
```

### Fade Mode (per-segment)

No overlap. Each segment occupies its exact timecoded position. Transitions are rendered as:
- `FADE_FROM_BLACK`: first 15 frames fade from black (opacity 0→1)
- `DISSOLVE`: last 15 frames fade to black (opacity 1→0), next segment fades in

### TransitionRenderer Component

Two separate prop sets for the two modes — no ambiguous children:

```tsx
// Overlap mode: renders both segments, controls blend
interface OverlapTransitionProps {
  type: string;           // 'DISSOLVE' | 'FADE_FROM_BLACK'
  durationInFrames: number;
  mode: 'overlap';
  outgoing: ReactNode;
  incoming: ReactNode;
}

// Fade mode: wraps a single segment with fade in/out
interface FadeTransitionProps {
  type: string;
  durationInFrames: number;
  mode: 'fade';
  children: ReactNode;
  position: 'in' | 'out';  // fade-in at start or fade-out at end
}

type TransitionRendererProps = OverlapTransitionProps | FadeTransitionProps;
```

Transition types:
- `DISSOLVE` — cross-fade: outgoing opacity 1→0, incoming opacity 0→1
- `FADE_FROM_BLACK` — black backdrop, incoming opacity 0→1
- Extensible: future types (wipe, zoom, glitch) add cases to the renderer

### Rendering Logic

**Overlap mode:**
```tsx
// For each pair of adjacent segments with a transition:
<Sequence from={overlapStart} durationInFrames={transitionDuration}>
  <TransitionRenderer type={transType} durationInFrames={transitionDuration} mode="overlap">
    <OutgoingSegmentContent />
    <IncomingSegmentContent />
  </TransitionRenderer>
</Sequence>
```

**Fade mode:**
```tsx
// Wrap each segment that has a transition:
<Sequence from={segFrom} durationInFrames={segDuration}>
  <TransitionRenderer type={transType} durationInFrames={fadeFrames} mode="fade">
    <SegmentContent />
  </TransitionRenderer>
</Sequence>
```

## BeeComposition Refactor

### Extracted Files

- `remotion/PlaceholderFrame.tsx` — colored placeholder with type icon and title
- `remotion/SafeMedia.tsx` — `SafeVideo` and `SafeImg` wrappers with error fallback

### Overlay Dispatch

Replace inline if/else with registry lookup. Overlays honor `entry.time_start` if set (offset within segment), otherwise start at frame 0:

```tsx
for (const entry of seg.overlay) {
  const Component = OVERLAY_COMPONENTS[entry.content_type];
  if (!Component) continue;
  const overlayDuration = Math.min(defaultDurations[entry.content_type] || 3 * fps, segDuration);
  // Offset within segment: entry.time_start is a timecode string like "0:03"
  const offsetFrames = entry.time_start ? timeToFrames(parseTimecode(entry.time_start), fps) : 0;
  const clampedDuration = Math.min(overlayDuration, segDuration - offsetFrames);

  <Sequence from={offsetFrames} durationInFrames={clampedDuration}>
    <Component content={entry.content} metadata={entry.metadata} durationInFrames={clampedDuration} />
  </Sequence>
}
```

If `time_start` is null (most cases), the overlay starts at the beginning of the segment.

Default durations per type:
- LOWER_THIRD: 4s
- TIMELINE_MARKER: 3s
- QUOTE_CARD: 4s
- FINANCIAL_CARD: 3s
- TEXT_OVERLAY: 3s

### Transition Position Calculation

New helper function `calculateSegmentPositions(segments, fps, transitionMode)` returns:
```ts
interface SegmentPosition {
  segId: string;
  from: number;          // frame position
  duration: number;      // segment duration in frames
  transitionIn?: { type: string; durationInFrames: number };
}

function calculateSegmentPositions(segments, fps, mode): {
  positions: SegmentPosition[];
  totalFrames: number;   // total video duration (shorter in overlap mode)
}
```

**Critical:** `totalFrames` must be passed to the Remotion `<Player>` as `durationInFrames`. `RemotionPreview.tsx` currently hardcodes `Math.round(totalDuration * FPS)` — this must be replaced with the computed `totalFrames` from `calculateSegmentPositions`. The computed value is stored in Zustand alongside `transitionMode` so RemotionPreview can read it:

```ts
// In store
computedTotalFrames: number | null;  // set by BeeComposition's useEffect, read by RemotionPreview
```

**Edge cases handled by `calculateSegmentPositions`:**
- Zero-duration segments: skip (don't render)
- Transition longer than segment: clamp transition to segment duration
- Last segment with a transition: only render fade-in, no overlap partner
- First segment: no incoming transition (ignore `FADE_FROM_BLACK` as outgoing)

**Positioning modes:**
- **Overlap mode:** abandons absolute timecodes, uses sequential accumulated positioning. Each segment starts at `previousEnd - transitionDuration`.
- **Fade mode:** uses absolute timecodes from `parseTimecode(seg.start)`. Segments maintain their storyboard positions.

## Store Changes

Add to `ProjectState`:
```ts
transitionMode: 'overlap' | 'fade';
setTransitionMode: (mode: 'overlap' | 'fade') => void;
```

Default: `transitionMode: 'overlap'`
Persisted to `localStorage` (key `bee-editor-transition-mode`) like theme and panel height.

## Testing

### Unit Tests (vitest)

**Overlay parsing:**
- QuoteCard: parses `"quote" — Author` content correctly, handles missing author
- FinancialCard: parses `$1.4 million`, `$14,000`, `$500K`, and unparseable strings (falls back to display-only)
- LowerThirdOverlay: parses `Name — Role` and `Name` (no role)
- TextOverlay: renders content text
- TimelineMarker: renders content text

**Transition logic:**
- `getTransitionInfo`: parses `1.0s`, `1.5s`, handles missing transition
- TransitionRenderer overlap mode: outgoing opacity is 1 at frame 0, 0 at final frame; incoming is inverse
- TransitionRenderer fade mode: opacity ramps correctly

**Position calculation (`calculateSegmentPositions`):**
- Overlap mode: reduces total duration by sum of transition durations
- Fade mode: preserves total duration (uses absolute timecodes)
- Zero-duration segment: skipped
- Transition longer than segment: clamped to segment duration
- Last segment with transition: only fade-in, no overlap partner
- Registry dispatch: unknown `content_type` is silently skipped (no crash)

### Visual Verification

- Load sample storyboard → all overlay types animate in preview
- Toggle overlap/fade → transitions visually change
- Export MP4 → overlays and transitions present in output

## Success Criteria

1. QUOTE_CARD, FINANCIAL_CARD, TEXT_OVERLAY, TIMELINE_MARKER render as animated React components in preview
2. DISSOLVE and FADE_FROM_BLACK transitions render in both overlap and fade modes
3. UI toggle switches between overlap and fade modes
4. Existing features (color grades, Ken Burns, lower thirds, captions) continue working
5. MP4 export includes all animations
6. No Pillow dependency for web preview — all rendering is React/Remotion
