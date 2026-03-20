# NLE Timeline Research — March 2026

## Goal

Replace the segment-list editor with a real NLE-style multi-track timeline with AI features (B-roll generation, smart captions, auto-matching).

## Current UI Assessment

The current UI is a **segment-list editor**, not an NLE:
- No horizontal timeline, no time ruler, no scrubber
- No visual representation of clip duration
- No multi-track lane view
- No drag-to-trim on the timeline
- No sequential playback across segments
- No waveforms, no thumbnails

It's functional for the storyboard workflow but feels like a form, not a video editor.

## What Pro Editors Do

### CapCut (2026)
- Timeline at bottom, preview up top, effects on sides
- AI B-Roll: type a prompt → 10s clip generated → drops into timeline
- AI Captions: 100+ templates, active word highlighting, filler removal
- Color grading: full wheels (shadows/midtones/highlights), luminance curves, HDR10+
- Smart suggestions: analyzes past projects, suggests next clip/transition

### OpusClip
- Highlight sentence in transcript → right-click → "Add B-Roll"
- Stock B-Roll (royalty-free) or AI-generated B-Roll
- 97%+ caption accuracy, multiple templates
- Brand templates (font, color, logo, intro/outro)

### DaVinci Resolve / Premiere
- Multi-track lanes (V1, V2, A1, A2, etc.)
- Frame-accurate editing with JKL shuttle
- Clip blocks proportional to duration
- Transitions as overlapping regions
- Waveforms on audio tracks
- Color grading with curves/wheels

## Libraries Evaluated

### Recommended: Twick SDK

| | |
|---|---|
| **Repo** | [github.com/ncounterspecialist/twick](https://github.com/ncounterspecialist/twick) |
| **Stars** | 353 |
| **License** | SUL v1.0 (free for internal/personal use, restrictions on commercial distribution) |
| **Stack** | React + TypeScript + Canvas |
| **Packages** | `@twick/timeline`, `@twick/canvas`, `@twick/live-player`, `@twick/video-editor`, `@twick/studio` |

**Why Twick:**
- Modular — can use `@twick/timeline` without their full editor
- Canvas-based timeline (performant for 100+ clips)
- AI-native — JSON timeline format, AI caption hooks, MCP agent
- Multi-track support with frame-accurate positioning
- Drag-drop, resize, scrub playback
- Serverless MP4 export
- TypeScript throughout
- "Lean engine with no UI — you craft custom controls" = maximum flexibility

**Integration plan:**
- Map our OTIO tracks (V1, A1, A2, A3, OV1) → Twick timeline tracks
- `ParsedStoryboard` → Twick JSON timeline format on load
- On edit: convert back → `to_otio()` → autosave
- Use `@twick/canvas` for clip drag-drop and resize
- Use `@twick/live-player` for preview synced to scrubber

### Alternatives Considered

| Library | License | Why not primary |
|---------|---------|----------------|
| [react-timeline-editor](https://github.com/xzdarcy/react-timeline-editor) | MIT | DOM-based (performance ceiling at ~50 clips), no waveforms |
| [@cloudgpt/timeline-editor](https://www.npmjs.com/package/@cloudgpt/timeline-editor) | Unknown | Themes + snapping, but less documented |
| [DesignCombo](https://github.com/designcombo/react-video-editor) | Apache 2.0 | Full CapCut clone but heavy, Remotion dependency |
| [OpenCut](https://opencut.app) | Open source | Pre-release, Next.js 15, promising but not ready |
| [Remotion](https://www.remotion.dev) | BSL | Code-first rendering, not interactive editing |
| [WebCut](https://github.com/tangshuang/webcut) | Open source | Vue 3 core (can wrap for React but extra friction) |
| [waveform-playlist](https://github.com/naomiaro/waveform-playlist) | MIT | Excellent for audio waveforms, could complement Twick |

### Audio Waveforms

For rendering audio waveforms on timeline tracks, [waveform-playlist](https://github.com/naomiaro/waveform-playlist) is the gold standard:
- Canvas-based waveform visualization
- Multi-track Web Audio editor
- Drag clips, trim boundaries, split at playhead
- 20+ audio effects via Tone.js
- MIT licensed

Can be used alongside Twick for audio track rendering.

## Best Practices

1. **Canvas-based timeline** — DOM hits performance walls at 50+ clips. Canvas renders 1000+ at 60fps.
2. **JSON-serializable state** — enables LLM-driven editing, undo/redo via snapshots, backend sync.
3. **Decouple timeline from rendering** — timeline = editing decisions, rendering = FFmpeg. Preview can be canvas-approximate.
4. **Web Audio API for waveforms** — `AudioContext.decodeAudioData()` for waveform data, render on canvas.
5. **Lazy loading + virtualization** — only render visible clips.
6. **Frame-accurate time model** — use rational time (like OTIO) internally, display as timecodes.

## Architecture

```
┌─────────────────────────────────────────────┐
│ React App                                    │
├─────────────┬─────────────┬─────────────────┤
│ Twick       │ Video       │ AI Panel        │
│ Timeline    │ Preview     │ (B-Roll,        │
│ (@twick/    │ (@twick/    │  Captions,      │
│  timeline)  │  live-      │  Auto-Match)    │
│             │  player)    │                 │
├─────────────┴─────────────┴─────────────────┤
│ Zustand Store                                │
│ ParsedStoryboard ↔ Twick JSON Timeline       │
├──────────────────────────────────────────────┤
│ OTIO Persistence (backend)                   │
└──────────────────────────────────────────────┘
```

## Decision

**Use Twick as the timeline foundation.** SUL license is fine for internal use. Supplement with waveform-playlist for audio visualization if Twick's audio track rendering is insufficient.
