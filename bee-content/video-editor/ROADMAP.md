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

## v0.9.0 — NLE Timeline (next)

Replace the segment-list editor with a real NLE-style timeline. This is the biggest UI overhaul since the project started.

### Phase A: Timeline Component

Build a horizontal multi-track timeline replacing `StoryboardTimeline.tsx`.

**Evaluate open-source bases:**
- [ ] **Evaluate [Twick](https://github.com/ncounterspecialist/twick)** — React video editor SDK with canvas timeline, multi-track, AI captions, MP4 export. Most aligned with our stack.
- [ ] **Evaluate [@cloudgpt/timeline-editor](https://www.npmjs.com/package/@cloudgpt/timeline-editor)** — multi-track with themes, grid snapping, drag handles, waveforms
- [ ] **Evaluate [react-timeline-editor](https://github.com/xzdarcy/react-timeline-editor)** — lightweight timeline with multi-layer support
- [ ] **Pick one and integrate** or build custom if none fit

**Core timeline features:**
- [ ] **Time ruler + scrubber** — horizontal ruler with frame/timecode markings, draggable playhead
- [ ] **Multi-track lanes** — V1 (video), V2 (B-roll), A1 (narration), A2 (real audio), A3 (music), OV1 (overlays). Map directly from OTIO tracks.
- [ ] **Clip blocks** — each clip shown as a colored rectangle proportional to duration. Show thumbnail for video, waveform for audio.
- [ ] **Drag to reposition** — move clips within and between tracks
- [ ] **Drag edges to trim** — drag left/right edge of a clip to adjust in/out points
- [ ] **Transitions between clips** — shown as overlapping regions on V1, click to change type/duration
- [ ] **Scrubber ↔ player sync** — moving scrubber updates video player position and vice versa
- [ ] **Zoom in/out** — scroll to zoom timeline (frame-level → full project view)
- [ ] **Snap-to-grid** — clips snap to other clip edges, playhead position, markers

**Playback improvements:**
- [ ] **Sequential playback** — play through multiple segments in order (not just single segment)
- [ ] **JKL shuttle** — J=reverse, K=pause, L=forward, tap multiple times to increase speed
- [ ] **Playback speed control** — 0.5x, 1x, 1.5x, 2x
- [ ] **Loop range** — set in/out points and loop just that section
- [ ] **Audio waveforms** — render waveform visualization on audio tracks
- [ ] **Thumbnail scrubbing** — hover over timeline to see frame thumbnails

### Phase B: AI Features Panel

CapCut/OpusClip-style AI tools as a dedicated panel or right-click context menu.

**B-Roll generation (OpusClip-style):**
- [ ] **Select narration → "Generate B-Roll"** — highlight a sentence/segment in the transcript, AI generates or finds matching stock footage
- [ ] **Stock B-Roll** — uses `media_search.py` to find Pexels/Pixabay clips matching narration text
- [ ] **AI-generated B-Roll** — uses `ai_video.py` (Kling/Veo) for abstract/custom visuals
- [ ] **B-Roll drops onto V2 track** — auto-placed on a second video track over the narration segment
- [ ] **B-Roll preview** — preview the B-roll clip before accepting

**Caption templates (CapCut-style):**
- [ ] **Caption template picker** — visual grid of caption styles (font, color, position, animation)
- [ ] **Active word highlighting** — words highlight as they're spoken (upgrade from current `\kf` tags)
- [ ] **Live caption preview** — see captions rendered on the video in real-time
- [ ] **Filler word removal** — auto-remove "um", "uh", "like" from transcript
- [ ] **Multi-language captions** — generate captions in multiple languages

**Smart suggestions:**
- [ ] **Auto color grade** — suggest color preset based on segment content (night → "surveillance", courtroom → "cold_blue")
- [ ] **Transition suggestions** — suggest transition type based on segment pair (same scene → dissolve, scene change → fade)
- [ ] **Music matching** — suggest background music mood based on narration tone

### Phase C: Playback & Preview

- [ ] **Real-time preview rendering** — preview composited output (visual + overlay + color) in the player without backend round-trip
- [ ] **Canvas-based preview** — use HTML5 Canvas or WebGL for client-side effect preview
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
