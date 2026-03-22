# Remotion Component Library Expansion

**Date:** 2026-03-22
**Status:** Approved
**Scope:** New general-purpose, genre-agnostic Remotion components for bee-video web editor

## Goals

Expand the Remotion component library beyond the current 14 true-crime-oriented components. New components should be genre-agnostic, suitable for explainers, finance content, tech tutorials, lifestyle, and more. YouTube mid-tier quality (Vox, Wendover, Johnny Harris) as default, with configurable quality tiers.

## Architecture: Component Families with Shared Primitives (Approach B)

New components compose from a shared set of animation primitives. The storyboard format stays unchanged — `type` string maps to React component via the `OVERLAY_COMPONENTS` registry in `BeeComposition.tsx`. Primitives are internal implementation details, not exposed to the storyboard layer.

### Quality Tiers

A project-level `quality` field on `BeeProject` (`standard` | `premium` | `social`), exposed via React context.

| Tier | Characteristics |
|------|----------------|
| `standard` (default) | Full spring animations, moderate detail. YouTube mid-tier. |
| `premium` | Longer eases, motion blur, richer detail, more animation stages. Broadcast-grade. |
| `social` | Snappy springs (high stiffness), bold/large text, faster pacing. TikTok/Reels. |

**Implementation:** `QualityContext` React context provider wraps `BeeComposition`. Components call `useQuality()` to read the tier and adjust spring configs, detail levels, and timing.

### Primitives Layer

Five internal building blocks composed by all new components:

#### `QualityContext`
- React context provider reading `BeeProject.quality`
- `useQuality()` hook returns `{ tier, springConfig, timing }` with tier-appropriate defaults
- Spring config presets: `standard` (damping: 12, stiffness: 150), `premium` (damping: 8, stiffness: 100), `social` (damping: 20, stiffness: 250)

#### `SpringReveal`
- Wraps children with spring-based entrance animation
- Props: `direction` (`left` | `right` | `up` | `down` | `scale` | `none`), `delay` (frames), `style` (additional CSS)
- Quality-aware: `premium` wraps in `<Trail>` from `@remotion/motion-blur`, `social` uses stiffer springs
- Uses Remotion `spring()` instead of `interpolate()` for natural motion

#### `DrawPath`
- Animated SVG path drawing via `stroke-dashoffset` animation
- Props: `d` (SVG path string), `fromFrame`, `toFrame`, `strokeWidth`, `color`
- Uses `@remotion/paths` `getLength()` for accurate dash calculation
- Quality-aware: `premium` adds glow filter behind stroke

#### `FitText`
- Wrapper around `@remotion/layout-utils` `fitText()` / `fitTextOnNLines()`
- Props: `text`, `maxWidth`, `maxLines`, `fontFamily`, `fontWeight`
- Returns auto-sized text element that never overflows container
- Validates font is loaded before measuring

#### `StaggerChildren`
- Renders children with staggered spring entrances
- Props: `interval` (frames between each child), `direction` (`up` | `down` | `left` | `right` | `scale`)
- Each child wrapped in `SpringReveal` with incremental delay
- Quality-aware: `premium` uses longer intervals (more elegant), `social` uses shorter (snappier)

#### `CountUp` (utility)
- Extracted from existing `FinancialCard` logic
- Animates a number from 0 to target over a frame range
- Props: `value` (number), `fromFrame`, `toFrame`, `format` (locale string, currency, percentage)
- Uses `interpolate()` with clamp

## New Components

### Priority 1: Callouts & Annotations

**Type:** `CALLOUT`
**Modes:** Overlay (primary), Visual (full-screen with background)

**Storyboard usage:**
```json
{
  "overlay": [{
    "type": "CALLOUT",
    "content": "This is the key detail",
    "style": "circle",
    "target": [960, 540],
    "animation": "draw"
  }]
}
```

**Styles:**

| Style | Visual | Use case |
|-------|--------|----------|
| `circle` | Animated circle drawn around a region | Highlight area of interest |
| `arrow` | Curved arrow pointing at target | "Look here" |
| `box` | Rounded rectangle highlight | UI element, text block |
| `underline` | Animated underline stroke | Emphasize text/word |
| `zoom` | Zoom-to-detail with magnified inset | Show fine detail in footage |
| `bracket` | Curly brace grouping multiple items | "These belong together" |

**Animation modes:**

| Mode | Behavior |
|------|----------|
| `draw` (default) | SVG path draws in progressively via `DrawPath` |
| `pop` | Spring scale from 0 to 1 via `SpringReveal` |
| `fade` | Simple opacity fade-in |

**Implementation:**
- Each style maps to an SVG path generator function (`circlePath()`, `arrowPath()`, `boxPath()`, etc.)
- `@remotion/shapes` for circle/rect base paths, `@remotion/paths` for length calculation
- Label text uses `FitText` inside a background pill from `@remotion/rounded-text-box`
- `target` is `[x, y]` in 1920x1080 composition coordinates
- Quality: `premium` adds glow/shadow + `<Trail>` on draw. `social` uses thicker strokes, bolder text.

**Props:**
- `content` (string) — label text
- `style` — callout shape
- `target` — `[x, y]` position
- `targetSize` — radius/dimensions for circle/box
- `animation` — entrance mode
- `color` — accent color (default `#dc2626`)
- `labelPosition` — `auto` | `top` | `bottom` | `left` | `right`

### Priority 1: Kinetic Typography

**Type:** `KINETIC_TEXT`
**Modes:** Visual (primary), Overlay

**Storyboard usage:**
```json
{
  "visual": [{
    "type": "KINETIC_TEXT",
    "content": "This changes *everything*",
    "preset": "punch",
    "align": "center"
  }]
}
```

**Presets:**

| Preset | Behavior | Best for |
|--------|----------|----------|
| `punch` (default) | Words slam in one at a time, spring scale with overshoot | Emphasis, dramatic statements |
| `flow` | Words slide in sequentially from right, smooth spring | Narration sync, explanations |
| `stack` | Lines stack vertically, each springs up from below | Lists, building an argument |
| `scatter` | Words start at random positions/rotations, spring to final layout | Energy, chaos, attention |
| `highlight` | Text is static, key words get colored background wipe | Calling out specific terms |
| `typewriter` | Character-by-character with cursor | Technical, documentary |

**Inline emphasis via markdown:**
- `*word*` — emphasized (larger scale, accent color, stronger spring)
- `**word**` — heavy emphasis (even larger, possible shake/glow at premium tier)
- Regular words — standard animation

**Implementation:**
- Parses `content` into word tokens preserving emphasis markers
- Each word is a `SpringReveal` with staggered delay via `StaggerChildren`
- `FitText` sizes text block to fill frame
- Preset determines entry direction, spring config, layout mode, emphasis treatment
- Quality: `premium` adds per-word motion blur, subtle drop shadows. `social` uses bigger text, faster stagger, bolder colors.

**Props:**
- `content` (string) — text with optional markdown emphasis
- `preset` — animation preset
- `align` — `left` | `center` | `right`
- `color` — text color (default white)
- `accentColor` — emphasis color (default red)
- `background` — `none` | `dark` | `blur`
- `position` — `center` | `top` | `bottom` | `lower-third`

### Priority 2: Infographic Panels

**Type:** `INFOGRAPHIC`
**Modes:** Visual (primary)

**Storyboard usage:**
```json
{
  "visual": [{
    "type": "INFOGRAPHIC",
    "content": "{\"layout\": \"stats\", \"title\": \"By The Numbers\", \"items\": [{\"label\": \"Victims\", \"value\": \"12\", \"icon\": \"users\"}]}",
    "preset": "stats"
  }]
}
```

**Layouts:**

| Layout | Visual | Use case |
|--------|--------|----------|
| `comparison` | Two columns side by side with animated value reveals | Before/after, vs, pros/cons |
| `process` | Horizontal steps connected by arrows, each step springs in | Timelines, sequences |
| `stats` | Grid of stat cards with counting numbers | Key facts, data summary |
| `list` | Vertical items with icon + label, staggered entrance | Evidence items, features |
| `pyramid` | Stacked horizontal bars, widest at bottom | Hierarchy, ranking |
| `split` | Left text block, right visual/stat block | Explanation + data |

**Content schema:**
```json
{
  "layout": "stats",
  "title": "Optional Header",
  "items": [
    { "label": "Victims", "value": "12", "icon": "users" },
    { "label": "Duration", "value": "8 years", "icon": "clock" }
  ]
}
```

**Implementation:**
- Each layout is a sub-component receiving parsed items
- Items animate via `StaggerChildren` + `SpringReveal`
- Numeric values use `CountUp` utility
- Connectors use `DrawPath`
- Built-in SVG icon set (20-30 common icons: dollar, clock, users, map-pin, shield, scale, etc.)
- `FitText` on all text labels
- `@remotion/shapes` for card backgrounds, progress bars
- Quality: `premium` adds card shadows, gradient backgrounds, slower stagger. `social` auto-truncates to 3-4 items, larger text, no connectors.

**Props:**
- `content` (JSON string) — layout config + items
- `preset` — layout type
- `title` — optional header
- `color` — accent color scheme
- `columns` — override grid columns for `stats` layout

### Priority 2: Screen Mockups

**Type:** `SCREEN_MOCKUP`
**Modes:** Visual (primary)

**Storyboard usage:**
```json
{
  "visual": [{
    "type": "SCREEN_MOCKUP",
    "content": "footage/website-recording.mp4",
    "frame": "browser",
    "url": "https://example.com/evidence"
  }]
}
```

**Frame types:**

| Frame | Visual | Use case |
|-------|--------|----------|
| `browser` | Chrome-style window, address bar, traffic lights, tab | Websites, web apps |
| `phone` | iPhone-style notch/bezel, status bar | Mobile apps, social media |
| `phone-android` | Android-style punch-hole, nav bar | Android screenshots |
| `tablet` | iPad-style frame, thinner bezels | Documents, PDFs |
| `terminal` | Dark window, colored prompt, monospace | Code, logs, commands |
| `desktop` | macOS-style desktop with dock and menu bar | Full desktop, app windows |
| `none` | No frame, content with drop shadow on dark bg | Raw screenshot/recording |

**Content types:**
- Video path — plays inside frame (screen recording)
- Image path — static screenshot
- Text string (for `terminal`) — rendered as monospace with syntax coloring

**Animations:**

| Behavior | How |
|----------|-----|
| Entrance | `SpringReveal` scale from 0.85 to 1 + slight rotation settle |
| Scroll | Optional auto-scroll content vertically over duration |
| Zoom-to-detail | Smooth zoom into `[x, y, scale]` region after entrance |
| Typing | For `terminal`, character-by-character typewriter |

**Implementation:**
- Each frame type is SVG/CSS shell with correct proportions and chrome
- Content renders in clipped container at frame's inner dimensions
- `@remotion/shapes` for rounded rect frame backgrounds
- `FitText` on address bar text
- Quality: `premium` adds reflections, depth shadow, 3D perspective tilt. `social` skips frame chrome, rounded corners + thick border only.

**Props:**
- `content` — media path or text
- `frame` — frame type
- `url` — browser address bar text
- `title` — tab/window title
- `scroll` — `{ speed, delay }` for auto-scroll
- `zoomTarget` — `[x, y, scale]` normalized 0-1 coordinates
- `theme` — `dark` | `light`

### Priority 3: Lottie Support

**Type:** `LOTTIE`
**Modes:** Visual, Overlay

**Storyboard usage:**
```json
{
  "overlay": [{
    "type": "LOTTIE",
    "content": "assets/checkmark.json",
    "position": "center",
    "size": 300
  }]
}
```

**Implementation:**
- Wraps `@remotion/lottie` `<Lottie>` component
- Syncs playback to Remotion frame clock via `goToAndStop()`
- Overlay positioning: `center` | `top-left` | `top-right` | `bottom-left` | `bottom-right` | custom `[x, y]`
- Entrance/exit via `SpringReveal` wrapper
- Local `.json` paths served through existing media API
- Remote URLs fetched via `delayRender()` / `continueRender()`
- Quality: `premium` full framerate. `social` skips to key poses. `standard` normal playback.

**Props:**
- `content` — path to Lottie JSON file or URL
- `position` — placement
- `size` — bounding box pixels
- `loop` — boolean (default false)
- `speed` — playback multiplier (default 1)
- `playSegment` — `[startFrame, endFrame]` partial playback
- `background` — optional backdrop color/blur

### Priority 4: Remaining Components

#### Data Visualization (`DATA_VIZ`)

Presets: `bar` (animated growth), `line` (path draw via `DrawPath`), `pie` (arc sweep via `@remotion/shapes`), `counter` (big number count-up), `progress` (horizontal fill bar). Content as JSON `{chart, data: [{label, value, color?}]}`. Items via `StaggerChildren`. Built on `@remotion/shapes` + `@remotion/paths`.

#### Animated Titles (`TITLE_CARD`)

Presets: `sweep` (left-to-right bar reveal), `drop` (spring bounce from top), `glitch` (digital distortion), `minimal` (fade + drift), `split` (center split). Subtitle via `\n`. `FitText` + `SpringReveal` + `StaggerChildren`.

#### Atmospheric Effects (`ATMOSPHERE`)

Overlay-only. Presets: `dust` (noise-driven floating particles), `bokeh` (soft blurred circles), `light-leak` (warm color wash), `rain` (diagonal streaks), `smoke` (noise-generated clouds). Built on `@remotion/noise`. `intensity` prop controls density/opacity.

#### Glitch/Retro (`GLITCH`)

Overlay-only. Presets: `vhs` (scan lines + tracking + color bleed), `crt` (curved screen + flicker), `datamosh` (block displacement), `static` (TV noise), `digital` (RGB split + slice displacement). CSS filter chains + noise displacement maps. `intensity` prop.

#### 3D Elements (`THREE_D`)

Presets: `text-3d` (extruded text, camera orbit), `globe` (spinning earth + pin), `object` (.glb model turntable). Uses `@remotion/three` + React Three Fiber. `premium` only by default; `standard` falls back to 2D CSS perspective approximation.

## New Dependencies

| Package | Used by |
|---------|---------|
| `@remotion/motion-blur` | `SpringReveal` (premium tier) |
| `@remotion/shapes` | Callout, Infographic, DataViz, ScreenMockup |
| `@remotion/paths` | DrawPath, Callout, Infographic, DataViz |
| `@remotion/noise` | Atmosphere, Glitch |
| `@remotion/layout-utils` | FitText |
| `@remotion/rounded-text-box` | Callout labels |
| `@remotion/lottie` + `lottie-web` | Lottie |
| `@remotion/three` + `@react-three/fiber` + `three` | ThreeD |

## File Structure

```
web/src/components/remotion/
  primitives/
    QualityContext.tsx
    SpringReveal.tsx
    DrawPath.tsx
    FitText.tsx
    StaggerChildren.tsx
    CountUp.tsx
  Callout.tsx
  KineticText.tsx
  Infographic.tsx
  ScreenMockup.tsx
  LottiePlayer.tsx
  DataViz.tsx
  TitleCard.tsx
  Atmosphere.tsx
  Glitch.tsx
  ThreeD.tsx
  (existing components unchanged)
```

## Registration

New components register in `BeeComposition.tsx`:
- `OVERLAY_COMPONENTS` registry for overlay-capable types
- `SegmentVisual` routing for visual-mode types (KINETIC_TEXT, INFOGRAPHIC, SCREEN_MOCKUP, DATA_VIZ, TITLE_CARD, THREE_D, LOTTIE as visual)
- Dual-mode components export both `Component` and `ComponentOverlay` (pattern already used by TextChat, EvidenceBoard, etc.)

## BeeProject Schema Change

Add `quality` field to `BeeProject`:
```typescript
interface BeeProject {
  // ... existing fields
  quality?: 'standard' | 'premium' | 'social'; // default: 'standard'
}
```

Also add to the `bee-video:project` storyboard JSON block:
```json
{"title": "My Video", "fps": 30, "resolution": [1920, 1080], "quality": "standard"}
```
