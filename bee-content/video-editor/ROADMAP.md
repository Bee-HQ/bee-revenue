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

**P0 — Clip property panel** (restores editing removed in alpha):
- [x] **Click clip → properties panel** — select a clip on the timeline, show its properties in a side panel or popover
- [x] **Color grade picker** — 12 presets (was inline, now in properties panel)
- [x] **Volume slider** — per-clip volume control with fade in/out for music
- [x] **Trim in/out inputs** — timecode fields for precise trim points
- [x] **Transition picker** — type dropdown + duration slider for segment transitions

**P1 — Remotion overlay rendering:**
- [x] **Lower thirds as React components** — replace Pillow PNGs with animated React `<LowerThird>` in BeeComposition
- [x] **Caption overlay component** — `<CaptionOverlay>` with karaoke/phrase modes rendered live in Remotion
- [x] **Color grade as CSS filter** — apply color presets via CSS filters in Remotion preview
- [x] **Ken Burns as CSS animation** — zoom/pan effects on images/video in Remotion (7 presets via interpolate)

**P2 — Remotion-based export:**
- [x] **Render to MP4 via Remotion** — replace FFmpeg pipeline with Remotion render for final export
- [x] **Export progress** — rendering state on button, file size on completion

**Core timeline features (P3):**
- [x] **Time ruler + scrubber** — horizontal ruler with auto-scaling ticks, draggable playhead, click-to-seek
- [x] **Drag to reposition** — move clips within and between tracks (DesignCombo native + backend sync)
- [x] **Drag edges to trim** — drag left/right edge of a clip to adjust in/out points
- [x] **Transitions between clips** — adapter builds transition entries for DesignCombo, shown on V1 track
- [x] **Zoom in/out** — scroll to zoom timeline (frame-level → full project view)
- [x] **Snap-to-grid** — clips snap to other clip edges, playhead position, markers
- [x] **Split at playhead** — split a clip at the current time position (button + 'S' key)

**Playback improvements (P4):**
- [x] **Sequential playback** — Remotion Player plays all segments as Sequence elements (verified working)
- [x] **JKL shuttle** — J=step back, K=pause, L=play forward
- [x] **Playback speed control** — 0.5x, 1x, 1.5x, 2x cycling button
- [x] **Loop range** — I/O keyboard shortcuts, yellow highlight on seek bar, auto-loop playback
- [ ] **Audio waveforms** — render waveform visualization on audio tracks
- [x] **Thumbnail scrubbing** — hover tooltip shows timecode on seek bar (full thumbnails deferred to v1.0)
- [x] **Frame step** — ◀/▶ buttons for single-frame stepping
- [x] **Keyboard shortcuts** — Space=play/pause, Arrow keys=±1s skip

### Phase B: AI Features Panel (P5)

CapCut/OpusClip-style AI tools as a dedicated panel or right-click context menu.

> **Status:** Basic AI panel shell shipped (stock search, caption button, keyword color suggestion). Deep dive needed for real AI features below.

- [x] **AI panel with tabs** — right sidebar with Media / Props / AI tabs, auto-switch on clip selection
- [x] **Basic B-Roll stock search** — search Pexels from narration text, download + assign
- [x] **Basic caption generation** — karaoke/phrase style picker + generate button
- [x] **Basic color grade suggestion** — keyword-to-preset lookup

**B-Roll generation — deep dive (OpusClip-style):**
- [ ] **Smart query extraction** — LLM-powered narration analysis to extract the key visual concept. "On the night of June 7th, a 911 call shattered the silence" → "rural property night emergency lights"
- [ ] **Select narration → "Generate B-Roll"** — highlight a sentence/segment in the transcript, AI generates or finds matching stock footage
- [ ] **Stock B-Roll** — uses `media_search.py` to find Pexels/Pixabay clips matching narration text
- [ ] **AI-generated B-Roll** — uses `ai_video.py` (Kling/Veo) for abstract/custom visuals. Wire real API providers, not just stubs.
- [ ] **B-Roll drops onto V2 track** — auto-placed on a second video track over the narration segment
- [ ] **B-Roll preview** — preview the B-roll clip in a mini player before accepting, with accept/reject/regenerate
- [ ] **Context-aware suggestions** — analyze surrounding segments to avoid repetitive B-roll

**Caption templates — deep dive (CapCut-style):**
- [ ] **Caption template picker** — visual grid of 10+ caption styles rendered as previews (fonts, sizes, colors, positions, background shapes, animations)
- [ ] **Active word highlighting** — Remotion component with multiple highlight styles (underline, box, scale, glow), not just color change
- [ ] **Live caption preview** — select a template → see it applied in real-time in the Remotion Player before committing
- [ ] **Custom template editor** — adjust font, size, color, position, background, animation per template
- [ ] **Filler word removal** — detect and auto-strip "um", "uh", "like", "you know" from narration text
- [ ] **Multi-language captions** — generate captions in multiple languages (translation API integration)

**Smart suggestions — deep dive:**
- [ ] **LLM-powered color grading** — analyze narration tone/content with an LLM to suggest color presets, not keyword lookup
- [ ] **Auto color grade** — suggest color preset based on segment content (night → "surveillance", courtroom → "cold_blue")
- [ ] **Transition suggestions** — suggest transition type based on segment pair (same scene → dissolve, scene change → fade)
- [ ] **Music matching** — suggest background music mood based on narration tone (sentiment analysis or LLM)
- [ ] **Pacing analysis** — flag segments that are too long/short for their content type, suggest splits or merges

### Phase C: Playback & Preview (P6)

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

### Backend Migration: Python → Node.js (gradual)

With Remotion handling preview AND export, many Python processors are now redundant (graphics, captions, color grades, compositor, assembly). The architecture should shift the center of gravity from Python to Node.js while keeping Python for what it uniquely provides.

**What Remotion already replaced (Python processors now redundant):**
- Graphics (Pillow PNGs) → React components in Remotion
- Captions (ASS file + FFmpeg burn) → CaptionOverlay React component
- Color grades (FFmpeg filters) → CSS filters in Remotion
- Compositor (multi-layer FFmpeg) → Remotion composition
- Assembly (FFmpeg concat) → Remotion render

**What Python still uniquely provides:**
- TTS generation — `edge-tts` (free, cloud) and `kokoro` (free, local) are Python-only libraries
- Storyboard format — parser, writer, Pydantic models (2000+ lines tested)

**Migration phases:**
- [x] **Phase 0: JSON project format** — replaced OTIO with `BeeProject` JSON format in the web frontend. TypeScript types (`BeeProject`, `BeeSegment`), markdown parser, all components migrated. OTIO no longer needed in the frontend.
- [x] **Phase 1: Express server** — Node.js Express backend in `web/server/` replaces Python FastAPI for the web editor. Shared types/parser in `web/shared/`. ProjectStore manages `.bee-project.json` directly. 25 routes + stubs. Python no longer needed to run the web editor (except TTS/stock/matcher — 501 stubs for now).
- [ ] **Phase 2: Node.js TTS** — replace Python TTS with Node.js SDKs (edge-tts-node, ElevenLabs, OpenAI). Drop kokoro (Python-only).
- [ ] **Phase 3: Node.js stock + services** — port stock search (Pexels API), auto-assign matcher, acquisition service, download manager to Node.js.
- [ ] **Phase 4: Python optional** — all web editor functionality in Node.js. Python remains only for CLI users.

**Target architecture:**
```
Frontend (React)
    ↓
Node.js (Express/Fastify)
├── Remotion (preview + export) — no more subprocess hop
├── Media serving, stock search, auto-assign
├── Timeline state, .bee-project.json
└── Calls Python service for:
    └── TTS (edge-tts, kokoro)
```

---

## v1.0.1 — AI Deep Dive + Platform Features

### Inspired by IMG.LY CE.SDK
- [ ] **Model-agnostic AI plugin system** — register AI providers by category (text2video, text2speech, text2image, stock_video). Each provider shows up as a tool in the AI panel. Users pick which to use. Proxy server injects API keys. Pattern: `{ category: "text2video", providers: [{ name: "kling", apiKey: env.KLING_API_KEY }, { name: "veo", ... }] }`
- [ ] **In-browser MP4 export via WebCodecs** — export video entirely in the browser without Node.js render script. Uses WebCodecs API (Chromium-only). Faster than Remotion headless Chrome. Could be offered as "Fast Export" alongside Remotion's "Quality Export"
- [ ] **AI provider proxy server** — lightweight backend that injects API keys for AI providers. Browser → proxy → AI provider. Keeps keys server-side, allows rate limiting and cost tracking per provider

### Inspired by Descript
- [ ] **AI voice cloning (Overdub-style)** — clone the narrator's voice from a sample, then generate any text in that voice. Would use ElevenLabs voice cloning API or similar. Record a 30-second sample → generate unlimited narration in that voice
- [ ] **AI co-editor (Underlord-style)** — LLM-powered assistant that can: rewrite narration, suggest cuts, generate B-roll queries, fix pacing — all from natural language instructions. "Make the opening more dramatic" → LLM rewrites narration + suggests darker color grade + faster cuts

### Inspired by Captions.ai
- [ ] **AI keyword highlighting in captions** — auto-detect important words (names, places, numbers, emotions) and apply scale/color emphasis. LLM analyzes narration and marks keywords. In Remotion, highlighted words get `scale(1.2)` + accent color
- [ ] **Chat-based style editor** — describe the visual style you want ("dark, cinematic, true crime feel") and the AI applies matching color grade, font, caption style, lower third design across all segments
- [ ] **AI Highlight & Enlarge** — important words in captions automatically get larger/bolder/colored. Multiple highlight modes: underline, box, scale, glow, color change

### Inspired by Shotstack / Creatomate
- [ ] **JSON video template system** — define reusable video templates as JSON (intro sequence, outro, lower third animation, transition package). Apply templates to any storyboard. Share templates between projects
- [ ] **Batch video generation** — produce multiple video variants from one storyboard (different narrators, languages, aspect ratios, color schemes). Queue renders with parameter variations
- [ ] **Cloud rendering API** — offload renders to cloud workers (AWS Lambda via Remotion Lambda, or custom). Parallel rendering for faster output. Could complement local Remotion render

### AI Video Generation Providers (2026 landscape)
- [ ] **Seedance 2.0 (ByteDance)** — latest text-to-video, cinematic quality. Add as provider alongside Kling/Veo
- [ ] **Sora 2.0 (OpenAI)** — OpenAI's video generation. Add as provider
- [ ] **Kling 3.0 (Kuaishou)** — upgraded from current Kling stub. Better quality, longer duration support

---

## Polish (any version)

UX refinements to add when touching nearby code.

- [ ] Responsive layout — collapse sidebars to tabs on < 1024px
- [x] Dark/light theme toggle *(v0.9.0+)*
- [ ] Fullscreen mode for player and timeline
- [ ] Right-click context menus on segments/clips
- [ ] Configurable codec/CRF in FFmpeg processor
- [ ] Retry logic for transient FFmpeg failures
- [ ] ARIA accessibility attributes on all interactive elements

### Test Coverage Gaps

**WebSocket progress**
- [x] `ws/progress` narration, produce, unknown action *(5 tests added)*
- [ ] `ws/progress` malformed JSON, disconnect mid-stream

**Production endpoints (partial)**
- [ ] Graphics with overlays, captions with/without NAR, preflight report, export OTIO
- [ ] Concurrent narration, state isolation across projects

**Media edge cases**
- [ ] Nested subdirs, special characters, yt-dlp category validation, download script listing
