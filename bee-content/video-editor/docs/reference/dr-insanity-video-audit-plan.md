# Dr Insanity Video Audit — Comprehensive Plan

## Video
- **URL:** https://www.youtube.com/watch?v=s6CXNbzKlks
- **Title:** "Secret Killer Leads Cops Into Her $3,000,000 Murder Mansion"
- **Channel:** Dr Insanity (4.37M subscribers)
- **Duration:** 49:56
- **Case:** Craig Thetford / Deana Thetford — Otero County, New Mexico
- **Downloaded:** `video-editor/docs/reference/dr-insanity-frames/source.mp4` (720p)

## Goal

Watch the entire video frame-by-frame at transitions/effects, catalog EVERY visual technique used, and produce actionable improvement tickets for our video production pipeline. This feeds into:
1. Remotion overlay/visual components
2. Storyboard generation skills
3. Screenplay formula
4. FFmpeg processor capabilities
5. Graphics generation (Pillow-based)

## What Already Exists

### Prior audit (partial)
- `video-editor/docs/reference/dr-insanity-visual-effects-audit.md` — first-pass audit with timestamps
- `video-editor/docs/reference/dr-insanity-frames/` — 24 reference frames extracted + `COMPARISON.md`
- `video-editor/docs/reference/dr-insanity-frames/source.mp4` — downloaded video

### Built components (from first audit)
These Remotion components are already built and registered:

| Component | Registry Type | Status |
|-----------|--------------|--------|
| PhotoViewerCard | `PHOTO_VIEWER` | Built — macOS chrome (their version is Windows) |
| SourceBadge | `SOURCE_BADGE` | Built |
| BulletList | `BULLET_LIST` | Built — has corner brackets |
| InfoCard | `INFO_CARD` | Built |
| Watermark | project config | Built |
| NotepadWindow | `NOTEPAD` | Built — macOS chrome |
| MapAnnotation | `MAP_ANNOTATION` | Built |
| DramaticQuote | `DRAMATIC_QUOTE` | Built |
| CaptionOverlay | enhanced | Built — stroke mode + {color:keyword} markup |
| AnimatedBG | helper | Built — teal/red/blue presets |
| CornerBrackets | primitive | Built |

### Codebase structure
```
video-editor/web/src/components/remotion/
├── overlays/       — 9 overlay components (LowerThird, QuoteCard, Callout, KineticText, etc.)
├── visuals/        — 6 visual components (TextChat, SocialPost, EvidenceBoard, AnimatedMap, etc.)
├── cards/          — 5 card components (PhotoViewerCard, NotepadWindow, InfoCard, BulletList, AnimatedBG)
├── primitives/     — 7 primitives (SpringReveal, DrawPath, FitText, StaggerChildren, CountUp, CornerBrackets, QualityContext)
├── overlays.ts     — shared types, parsers, DEFAULT_DURATIONS, NAMED_COLORS, resolveColor
├── BeeComposition.tsx — main composition with OVERLAY_COMPONENTS + VISUAL_COMPONENTS registries
└── consistency.test.ts — registry/parser sync tests
```

### Skills (self-contained, no external file deps)
- `/true-crime:generate-screenplay` — visual codes + narration style inlined
- `/true-crime:generate-storyboard` — visual mapping + component specs inlined
- `/true-crime:review-screenplay` — act targets + style rules inlined
- `/true-crime:review-storyboard` — valid types + validation rules inlined

---

## Phase 1: Frame-by-Frame Video Analysis

### Method
1. Download the video (already done at `dr-insanity-frames/source.mp4`)
2. Use ffmpeg to extract frames at key intervals:
   - Every 5 seconds for general scanning
   - Every 1 second during transitions
   - Frame-by-frame (every frame) during fast cuts, glitch effects, and the trailer montage
3. For each distinct visual effect, extract a clean reference frame
4. Use Chrome browser automation to watch sections at 0.25x speed for animation timing

### What to Catalog (per effect)

For every visual technique found, document:

```markdown
### [EFFECT-NAME] at [TIMESTAMP]

**Type:** overlay | visual | transition | color-grade | animation | composition
**Duration:** [seconds or frames]
**Frequency:** how often it appears in the video

**Visual description:**
[What it looks like — colors, positions, fonts, sizes, opacity, shadows]

**Animation:**
[How it enters, holds, and exits — timing in frames, easing, direction]

**Our current support:**
[Which Remotion component handles this, or "NOT SUPPORTED"]

**Gap analysis:**
[What's different between theirs and ours, or what's missing entirely]

**Priority:** P0 (must have) | P1 (should have) | P2 (nice to have)

**Reference frame:** [filename in dr-insanity-frames/]
```

### Sections to Watch Carefully

| Timecode | What to Look For |
|----------|-----------------|
| 0:00–1:20 | **Trailer montage** — glitch transitions, white flash frames, rapid cuts, audio clip stacking, text overlays |
| 0:15 | Photo card overlay on bodycam — position, size, animation timing |
| 0:30 | Caption with red keyword — exact styling, font size, stroke width |
| 0:55 | [ACTUAL] source badge — exact position, font, opacity |
| 2:00 | [REENACTMENT] badge |
| 2:30 | Red atmospheric glow on dark B-roll — how is the red effect achieved? |
| 3:00 | Face blur — tracking method, blur radius |
| 4:00 | Surveillance camera timestamp overlay |
| 6:00 | Aerial view with red brushstroke trail — texture, opacity, glow |
| 7:00 | Satellite zoom with pulsing blue marker |
| 10:00–11:00 | Ken Burns on photos — zoom speed, direction, duration |
| 11:00 | Dual Photo Viewer windows — exact layout, gap, background |
| 13:00 | Photo card with role label — "Ex-husband / BILL CAISSE" |
| 15:00 | Full-screen Photo Viewer on animated background — the Windows desktop look |
| 17:30 | B&W color grade — how desaturated? What tint? |
| 26:00 | Dual photos side by side with name labels |
| 35:00 | Aerial + photo inset + quote callouts — composite composition |
| 38:00 | "UNLOCKED DOOR" bold text label — corner bracket decoration |
| 44:00 | Notepad + Photo Viewer side by side — layout, typing speed |
| 48:00 | Interrogation with yellow captions |
| 48:55 | "I'm gonna need a lawyer" dramatic red quote |
| 49:10 | Charge sheet — staggered bars on blurred montage |
| 49:30 | Charges/Sentence card — split layout |
| 49:45 | End card / outro |

### Transition Analysis (frame-by-frame)

Extract 3 frames for each transition: last frame of outgoing, transition frame(s), first frame of incoming.

| Transition Type | Where to Find Examples |
|----------------|----------------------|
| Hard cut | Throughout (most common) |
| Dissolve/cross-fade | Between sections |
| Fade to/from black | Act transitions |
| Glitch/RGB shift | Trailer only |
| White flash | Trailer only |
| Zoom transition | Into aerial/map views |
| Smash cut | Calm → intense mood shifts |

---

## Phase 2: Gap Analysis & Prioritization

After cataloging all effects, compare each against our existing components:

### Comparison Categories

1. **Exact match** — our component does exactly this
2. **Close but different** — we have the concept but styling/animation differs
3. **Missing entirely** — we don't support this at all

### Known Gaps from First Audit (to verify/expand)

| Gap | Severity | Notes |
|-----|----------|-------|
| Red brushstroke trail on aerials | Medium | Our MapAnnotation uses clean SVG paths, theirs is painterly |
| Windows vs macOS chrome | Low | Intentional design choice, but note the differences |
| Caption no-box mode | Done | Built as `captionStyle: 'stroke'` |
| Corner bracket decorations | Done | Built as CornerBrackets primitive |
| Dramatic splash quote | Done | Built as DramaticQuote |
| Video Player window (different from Photo Viewer) | Unknown | Seen at ~49:10 — need to verify |
| Glitch transition effect | Not built | Only used in trailer, complex to implement |
| White flash transition | Not built | Simple — just a white frame |
| Phone screen mockup | Not built | Showing text messages on a phone device frame |
| Missing person flyer mockup | Not built | Seen in montage |
| Animated red radar pulse on map | Partial | AnimatedMap has pulse, but verify it matches |

---

## Phase 3: Improvement Tickets

For each gap, create an actionable improvement item:

```markdown
### IMP-[N]: [Title]

**Component:** [which file to modify or create]
**Type:** new-component | enhancement | style-fix | new-primitive
**Effort:** S (hours) | M (day) | L (days)
**Priority:** P0 | P1 | P2

**Current state:** [what we have now]
**Target state:** [what it should look like, referencing the frame]
**Reference frame:** [filename]

**Implementation notes:**
[Specific technical approach]
```

---

## Phase 4: Output Files

After the full audit, produce these deliverables:

1. **`dr-insanity-complete-audit.md`** — every effect cataloged with timestamps, descriptions, and reference frames
2. **`dr-insanity-gaps.md`** — prioritized list of gaps between their style and our capabilities
3. **`dr-insanity-improvement-tickets.md`** — actionable tickets for each gap, ready for implementation
4. **Updated `COMPARISON.md`** — replace the existing partial comparison with the comprehensive version

All files go in `video-editor/docs/reference/dr-insanity-frames/`.

---

## Tools Available

- **Video file:** `video-editor/docs/reference/dr-insanity-frames/source.mp4`
- **Frame extraction:** `ffmpeg -ss [seconds] -i source.mp4 -frames:v 1 -q:v 2 output.jpg`
- **Batch extraction:** `ffmpeg -i source.mp4 -vf fps=1/5 frames/frame-%04d.jpg` (every 5 sec)
- **Frame-by-frame:** `ffmpeg -ss [start] -t [duration] -i source.mp4 -vf fps=30 transition-%04d.jpg`
- **Chrome browser:** YouTube tab already open, can watch at 0.25x speed
- **Existing frames:** 24 reference frames already extracted in the same directory
- **Read tool:** Can view extracted JPG frames directly

## Execution Notes

- Start from 0:00, work through chronologically
- The trailer (0:00–1:20) is the most effects-dense section — needs frame-by-frame
- Most of the video (1:20–48:00) is bodycam footage with occasional overlays — can scan at 5-second intervals
- The ending (48:00–49:56) is effects-dense again — slow down
- Extract reference frames for EVERY distinct effect, even if similar to one already captured
- Name frames descriptively: `[timestamp]-[effect-name].jpg` (e.g., `0015-photo-viewer-overlay.jpg`)
- Total unique effects expected: 30-50
