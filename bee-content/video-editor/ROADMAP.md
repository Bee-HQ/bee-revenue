# Roadmap

Prioritized improvements for bee-video-editor, organized by effort and impact.

> **This is the single source of truth** for what needs to be built.

---

## Completed Milestones

<details>
<summary>v0.3.1 — v0.8.0 (click to expand)</summary>

### v0.3.1 — Quick Wins
- [x] Surface FFmpeg errors, input validation, segment status tracking
- [x] Configurable API base URL, media search, CORS, TTS progress
- [x] Mugshot card, quote card completion

### v0.4.0 — Core Improvements
- [x] Persistent sessions, undo/redo, segment reordering, batch assignment
- [x] Unified data models, parser resilience, bible visual codes
- [x] Preflight, ASS captions, text chat, social post, news montage, evidence board, Lottie overlays

### v0.5.0 — Big Features
- [x] One-command production (`bee-video produce`), preview generation, parallel narration
- [x] WebSocket progress, flow diagram, timeline sequence, OTIO export, map generation

### v0.6.0 — Scale
- [x] Stock footage API (Pexels), AI video generation infra, batch graphics
- [x] Stock library tracker, TTS voice lock, rough cut, project validator

### v0.7.0 — OTIO Project Format
- [x] v2 storyboard format (JSON blocks), Pydantic models, OTIO converters
- [x] SessionStore rewrite, all services on ParsedStoryboard, sidecar files removed
- [x] Export menu, inline segment editing (transition, color, volume, trim)

### v0.8.0 — Compositor + Search + UI Polish
- [x] Multi-layer compositor, auto-assign matcher, batch acquisition
- [x] Scene detection, multi-provider stock search (Pexels + Pixabay)
- [x] AI video stubs (Kling + Veo), satellite maps (Esri)
- [x] Toast notifications, stock search panel, keyboard shortcuts, loading skeletons
- [x] Per-entry download buttons, production bar (Captions, Rough Cut, Preflight, Composite, Auto-Assign, Acquire)
- [x] SSRF validation, YouTube URL check, path sanitization, drawtext escaping

</details>

---

## v0.9.0 — NLE Timeline

Replace the segment-list editor with a real NLE-style timeline using DesignCombo SDK + Remotion Player.

> **Decision:** DesignCombo for timeline canvas + Remotion for preview/export. Research at `docs/research/2026-03-20-nle-timeline-research.md`.

### v0.9.0-alpha — Foundation (complete)

- [x] **Evaluate libraries** — researched Twick, DesignCombo, react-timeline-editor, Remotion, OpenCut, WebCut. Chose DesignCombo + Remotion.
- [x] **Multi-track timeline** — DesignCombo canvas with V1/A1/A2/A3/OV1 tracks, clips as colored blocks
- [x] **Remotion Player** — composited preview replacing HTML5 video player
- [x] **Timeline adapter** — bidirectional Storyboard ↔ DesignCombo state conversion (24 tests)
- [x] **Scrubber sync** — segment click → player seeks to position
- [x] **Production dropdown** — consolidated 13-button bar into toolbar + dropdown
- [x] **Layout restructured** — sidebars kept, center replaced with Remotion + timeline
- [x] **8 old components removed** — StoryboardTimeline, VideoPlayer, ProductionBar, SegmentCard, TransitionPicker, ColorGradePicker, VolumeSlider, TrimControls

### v0.9.0-beta — Editing + Export (next)

**P0 — Clip property panel (complete):**
- [x] Click clip → properties panel with color grade, volume, trim, transitions
- [x] Auto-switch to Properties tab on clip selection

**P1 — Remotion overlay rendering (complete):**
- [x] Lower thirds as animated React components (slide-in, red accent bar)
- [x] Caption overlay with karaoke (word-by-word highlight) and phrase modes
- [x] Color grade as CSS filter (12 presets) applied live in preview
- [x] Timeline markers as red badge overlays
- [ ] **Ken Burns as CSS animation** — zoom/pan effects on images/video in Remotion

**P2 — Remotion-based export (complete):**
- [x] Render to MP4 via Remotion (Node.js render script + Python API endpoint)
- [ ] **Export progress** — show render progress (frame N/total, ETA)
- [ ] **Export presets** — YouTube 1080p, 4K, Reels, TikTok

**P3 — Timeline interactions (complete):**
- [x] Drag/resize clips (DesignCombo native), state syncs back to backend
- [x] Split at playhead (button + 'S' keyboard shortcut)
- [x] Zoom slider wired to DesignCombo scale
- [x] Snap toggle (magnetic on/off)
- [ ] **Time ruler + scrubber** — horizontal ruler with frame/timecode markings, draggable playhead
- [ ] **Transitions on timeline** — shown as overlapping regions on V1, click to change type/duration

**P4 — Playback polish (complete):**
- [x] JKL shuttle (J=step back, K=pause, L=play)
- [x] Playback speed (0.5x/1x/1.5x/2x)
- [x] Frame step buttons (◀/▶)
- [x] Space=play/pause, Arrow keys=±1s skip
- [x] Shortcuts panel updated with all keys
- [ ] **Loop range** — set in/out points and loop just that section
- [ ] **Audio waveforms** — render waveform visualization on audio tracks
- [ ] **Thumbnail scrubbing** — hover over timeline to see frame thumbnails

**P5 — AI features (basic shell complete, deep dive needed):**
- [x] AI panel with tabs (Media / Props / AI) in right sidebar
- [x] Basic B-Roll stock search from narration text
- [x] Basic caption generation (karaoke/phrase style picker + generate button)
- [x] Basic color grade suggestion (keyword lookup)

### AI Features Deep Dive (future — needs dedicated design cycle)

The current P5 AI panel is a thin wrapper over existing endpoints. A proper AI features implementation needs:

**B-Roll generation — real AI:**
- [ ] **Smart query extraction** — LLM-powered analysis of narration text to extract the key visual concept, not just substring. "On the night of June 7th, a 911 call shattered the silence" → "rural property night emergency lights"
- [ ] **AI-generated B-Roll** — wire real Kling/Veo APIs to generate custom video from prompts. Current stub only makes black frames with text.
- [ ] **B-Roll drops onto V2 track** — auto-placed on a second video track layered over the narration segment, not replacing V1
- [ ] **B-Roll preview before accepting** — show the clip in a mini player, accept/reject/regenerate
- [ ] **Context-aware suggestions** — analyze surrounding segments to avoid repetitive B-roll (e.g., don't use "courthouse" for 5 segments in a row)

**Caption templates — visual design system:**
- [ ] **Caption template picker** — visual grid showing 10+ caption styles rendered as previews (different fonts, sizes, colors, positions, background shapes, animations)
- [ ] **Active word highlighting** — Remotion component that highlights the current word with scale/color animation, not just color change. Multiple highlight styles (underline, box, scale, glow)
- [ ] **Live template preview** — select a template → see it applied in real-time in the Remotion Player before committing
- [ ] **Custom template editor** — adjust font, size, color, position, background, animation per template
- [ ] **Filler word removal** — detect and auto-strip "um", "uh", "like", "you know" from narration text before caption generation
- [ ] **Multi-language captions** — generate captions in multiple languages (translation API integration)

**Smart suggestions — beyond keyword lookup:**
- [ ] **LLM-powered color grading** — analyze narration tone/content with an LLM to suggest color presets. "The bodies were found at dusk" → "golden_hour" not "dark_crime"
- [ ] **Transition suggestions** — analyze consecutive segment pairs: same scene → dissolve, time jump → fade to black, location change → wipe
- [ ] **Music mood matching** — analyze narration tone to suggest music mood (tense, somber, neutral, dramatic). Could use sentiment analysis or LLM.
- [ ] **Pacing analysis** — flag segments that are too long/short for their content type. Suggest splits or merges.

### Remaining Polish

- [ ] **Audio waveforms** — render waveform visualization on audio tracks (canvas-based, from Web Audio API)
- [ ] **Thumbnail scrubbing** — hover over timeline to see frame thumbnails
- [ ] **Loop range** — set in/out and loop playback
- [ ] **Time ruler + draggable scrubber** — proper frame-accurate ruler on the timeline
- [ ] **Ken Burns in Remotion** — zoom/pan CSS animations on images
- [ ] **Export progress bar** — frame N/total with ETA
- [ ] **Real-time preview rendering** — preview composited output without backend round-trip (already done via Remotion)
- [ ] **Audio meters** — real-time loudness visualization during playback
- [ ] **Source monitor** — second player for browsing source clips before placing on timeline

---

## v1.0.0 — Production Ready

### Export & Delivery
- [ ] **Export presets** — YouTube 1080p, YouTube 4K, Instagram Reels, TikTok, custom
- [ ] **Selective export** — choose subset of segments to export
- [ ] **Render queue** — queue multiple exports, run in background
- [ ] **Export progress** — detailed progress (segment N/total, ETA)

### Project Management
- [ ] **Recent projects list** — show last 10 projects on load screen
- [ ] **Project templates** — start from a template (true crime, documentary, vlog)
- [ ] **Settings UI** — TTS voice, render quality, default color preset, API keys

### Media Management
- [ ] **Bins/folders** — organize media library into custom folders
- [ ] **Media tagging** — add keywords/tags to clips
- [ ] **Proxy workflow** — generate low-res proxies for smooth playback, link back for final render
- [ ] **Used/unused indicators** — mark which clips are placed on timeline

### Wire Real AI Providers
- [ ] **Kling API** — wire real Kling video generation (stub exists, needs `KLING_API_KEY`)
- [ ] **Google Veo API** — wire real Veo generation (stub exists, needs credentials)
- [ ] **Runway Gen-4** — add as new provider
- [ ] **Whisper-based captions** — precise word-level timing from actual audio (vs current estimation)

### Architecture
- [ ] **LLM screenplay → storyboard** — generate v2 storyboard from case research + formula
- [ ] **FOIA pipeline tracker** — structured FOIA request tracking per case
- [ ] **Auth option** — optional token-based auth for non-local deployments

---

## Polish (any version)

UX refinements to add when touching nearby code.

- [ ] Responsive layout — collapse sidebars to tabs on < 1024px
- [ ] Dark/light theme toggle
- [ ] Fullscreen mode for player and timeline
- [ ] Right-click context menus on segments/clips
- [ ] Configurable codec/CRF in FFmpeg processor
- [ ] Retry logic for transient FFmpeg failures
- [ ] ARIA accessibility attributes on all interactive elements

### Test Coverage Gaps

**WebSocket progress (zero coverage)**
- [ ] `ws/progress` narration, produce, unknown action, malformed JSON

**Production endpoints (partial)**
- [ ] Graphics with overlays, captions with/without NAR, preflight report, export OTIO
- [ ] Concurrent narration, state isolation across projects

**Media edge cases**
- [ ] Nested subdirs, special characters, yt-dlp category validation, download script listing
