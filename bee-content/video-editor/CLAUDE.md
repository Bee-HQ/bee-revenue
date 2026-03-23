# CLAUDE.md — bee-video-editor

## What This Is

AI-assisted video production tool. Takes a v2 storyboard markdown file → generates assets → assembles final video. Built for true crime documentaries but the processors are genre-agnostic.

**Version:** 0.10.0
**Python:** >=3.11, managed with `uv` + `hatchling`
**Entry point:** `bee-video` CLI

## Quick Reference

```bash
cd bee-content/video-editor

# Core workflow
uv run bee-video import-md storyboard.md -p ./proj          # Load storyboard → OTIO
uv run bee-video scenes source.mp4 -p ./proj                # Detect shot boundaries
uv run bee-video graphics storyboard.md -p ./proj           # Generate overlays
uv run bee-video narration storyboard.md -p ./proj --tts edge  # Generate TTS
uv run bee-video trim-footage storyboard.md -p ./proj       # Trim source clips
uv run bee-video assemble -p ./proj --transition dissolve   # Final assembly
uv run bee-video export -p ./proj --format md               # Export as markdown
uv run bee-video export -p ./proj --format otio             # Export clean OTIO for NLE

# Stock + AI media
uv run bee-video fetch-stock "aerial farm dusk" -n 3 -p ./proj  # Pexels stock footage
uv run bee-video generate-clip "sunset over ocean" -p ./proj    # AI video (stub/kling/veo)

# Utilities
uv run bee-video graphics-batch config.json -p ./proj       # Batch graphics from config
uv run bee-video voice-lock elevenlabs --voice Daniel       # Lock TTS voice for project
uv run bee-video rough-cut storyboard.md -p ./proj          # Fast 720p rough cut
uv run bee-video validate -p ./proj                         # Validate project structure
uv run bee-video stock-list                                 # List tracked stock clips
uv run bee-video stock-check "aerial farm"                  # Check for clip reuse

# Web editor (Node.js — no Python needed)
cd web && ./dev.sh     # Dev mode (Express :8420 + Vite :5173 hot reload)
cd web && ./start.sh   # Production (Express serves built frontend :8420)

# Tests
uv run --extra dev pytest tests/ -v          # Python CLI tests (374)
cd web && npm test                           # Frontend + server vitest (215 tests)
cd web && npx playwright test                # E2E tests (11 Playwright tests)
cd web && npx playwright test --ui           # E2E interactive mode
```

## Architecture

```
CLI (Typer)                    Web Editor (React + Express)
    │                              │
Python Services                 web/server/ (Express)
    │                           ├── ProjectStore (.bee-project.json)
┌───┴───┐                      ├── routes/ (projects, media, production)
formats/    Processors          └── web/shared/ (types, parser)
(Pydantic)  ├ ffmpeg.py
            ├ tts.py            web/src/ (React frontend)
            └ ...               ├── Remotion (preview + render)
                                └── Zustand + Timeline
```

**Two backends:** The Python CLI (`bee-video`) uses its own services/processors. The web editor uses a Node.js Express server in `web/server/` that reads/writes `.bee-project.json` directly — no Python bridge needed.

**Shared code:** Types (`BeeProject`, `BeeSegment`) and the markdown parser live in `web/shared/`, imported by both the React frontend and the Express server.

**Python `formats/` package** remains the canonical representation for CLI workflows. `ParsedStoryboard` (Pydantic) powers all CLI services and routes.

**Processors** are stateless functions wrapping external tools (FFmpeg, TTS, Pillow). CLI-only — the web editor uses Remotion for rendering.

## Storyboard Format (v2)

The v2 storyboard format uses markdown with JSON code blocks tagged `bee-video:project` and `bee-video:segment`. It is the single source of truth for all CLI and web UI workflows.

```markdown
# My Video

\`\`\`bee-video:project
{"title": "My Video", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Section Name

### seg-01 | Scene description

\`\`\`bee-video:segment
{
  "visual": [{"type": "footage", "src": "footage/clip.mp4", "trim": [0, 10]}],
  "audio":  [{"type": "narration", "src": "narration/seg-01.mp3"}],
  "overlay": [{"type": "lower_third", "name": "Alex Murdaugh", "role": "Defendant"}]
}
\`\`\`
```

The `formats/` package provides:
- `ParsedStoryboard` — runtime model (Pydantic)
- `to_otio()` / `from_otio()` — OTIO round-trip
- `clean_otio()` — NLE-ready export (strips metadata)
- `old_to_new()` — migrates old table-based storyboards

## Processor Capabilities

### FFmpeg (`processors/ffmpeg.py`)

| Category | Functions |
|----------|-----------|
| Probe | `probe()`, `get_duration()` |
| Basic | `trim()`, `normalize_format()`, `concat_segments()`, `concat_with_transitions()` |
| Image | `image_to_video()` (7 Ken Burns effects), `waveform_video()`, `overlay_png()` |
| Effects | `color_grade()` (12 presets), `drawtext()`, `speed()`, `xfade()` (30+ transitions), `add_fade()`, `picture_in_picture()` |
| Audio | `mix_audio()`, `normalize_loudness()` (target: -14 LUFS) |

**Color presets:** dark_crime, warm_victim, bodycam, noir, sepia, cold_blue, vintage, bleach_bypass, night_vision, golden_hour, surveillance, vhs

**Ken Burns:** zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, zoom_in_pan_right

**Transitions:** fade, dissolve, wipeleft/right/up/down, slideleft/right/up/down, smoothleft/right, circlecrop, rectcrop, pixelize, radial, diagtl/tr/bl/br, hlslice/hrslice, distance, zoomin, fadeblack, fadewhite, hblur, vuslice, vdslice

### Scene Detection (`processors/scene_detect.py`)

`detect_scenes(video_path, threshold)` — FFmpeg-based shot boundary detection. Returns list of `{start, end, duration}` dicts. Used by `bee-video scenes` CLI command.

### Media Search (`processors/media_search.py`)

Unified stock search across Pexels + Pixabay. `search_stock(query, providers, n)` returns normalized results with `download_url` / `pexels_url` metadata. Used by Acquire pipeline and the web stock search panel.

### AI Video (`processors/ai_video.py`)

Pluggable provider interface. Providers: `stub` (FFmpeg placeholder MP4), `kling` (stub), `veo` (stub). `generate_clip(prompt, provider, output_path)`.

### Maps (`processors/maps.py`)

| Function | Output |
|----------|--------|
| `map_flat(lat, lng, ...)` | PNG — flat OpenStreetMap style |
| `map_tactical(lat, lng, ...)` | PNG — dark tactical overlay |
| `map_pulse(lat, lng, ...)` | PNG — pulsing location marker |
| `map_route(points, ...)` | PNG — route between coordinates |
| `map_satellite(lat, lng, ...)` | PNG — Esri World Imagery satellite tiles |
| `map_hybrid(lat, lng, ...)` | PNG — satellite + labels overlay |

### Graphics (`processors/graphics.py`)

| Function | Output |
|----------|--------|
| `lower_third(name, role)` | PNG — semi-transparent bar + name/role text |
| `timeline_marker(date, desc)` | PNG — full-frame date stamp |
| `financial_card(amount, desc)` | PNG — red dollar amount display |
| `quote_card(quote, author)` | PNG — quote display (accent: red/teal/gold) |
| `text_overlay(text)` | PNG — simple text |
| `black_frame()` | PNG — solid black |
| `mugshot_card(photo, charges, sentence)` | PNG — photo right, charges left |
| `news_montage(headlines)` | PNG — stacked rotated headline cards |
| `evidence_board(items)` | PNG — red-string corkboard |
| `flow_diagram(nodes)` | PNG — directional arrows, red/teal colors |
| `timeline_sequence(events)` | PNG — horizontal timeline with nodes |
| `text_chat(messages)` | PNG — iMessage/SMS/generic platform |
| `social_post(content)` | PNG — Facebook/Instagram/Twitter/Snapchat |

All output 1920x1080 PNG. Colors follow Dr. Insanity palette (dark bg, red/teal accents).

### TTS (`processors/tts.py`)

| Engine | Cost | Quality | Notes |
|--------|------|---------|-------|
| Edge | Free (cloud) | Good | Default voice: en-US-GuyNeural |
| Kokoro | Free (local) | Good | 24kHz WAV, needs `kokoro>=0.9.4` |
| OpenAI | Paid | Best | gpt-4o-mini-tts, 1200-word chunking |
| ElevenLabs | Free tier / Paid | Best | Default voice: Daniel. Needs `ELEVENLABS_API_KEY` env var. |

`extract_narrator_sections(screenplay_path)` pulls `**NARRATOR:**` lines from screenplay markdown.

## Services

| Service | File | Responsibility |
|---------|------|----------------|
| Production | `services/production.py` | Full pipeline orchestration (init → graphics → narration → trim → composite → assemble) |
| Compositor | `services/compositor.py` | Per-segment multi-layer composition: visual → trim → normalize → color grade → overlay → audio → mux |
| Matcher | `services/matcher.py` | Auto-assign media to segments via keyword + src matching |
| Acquisition | `services/acquisition.py` | Batch stock search + download for all storyboard queries |

## Web UI

React 19 + TypeScript + Vite + Tailwind + Zustand + react-timeline-editor + Remotion.

**Layout:** Left sidebar (segment list) + center (Remotion Player above react-timeline-editor NLE timeline) + right tabbed sidebar (Media / Properties / AI).

**Key features:**
- Load `.md` storyboard → react-timeline-editor multi-track timeline (V1/A1/A2/A3/OV1) with clips as colored blocks proportional to duration
- Remotion Player shows composited video preview with 19 animated overlay/visual components (see Remotion Components below)
- Clip property panel (right sidebar Props tab): color grade picker, volume slider, trim inputs, transition picker
- AI panel (right sidebar AI tab): B-Roll stock search from narration, caption generation, auto color grade suggestions
- Timeline interactions: drag/resize clips with backend sync, split at playhead (S key), zoom slider, snap toggle, undo/redo history (50 snapshots)
- Drag-drop media: internal (Media Library → timeline), external (Finder → timeline with upload), paste (Cmd+V file path)
- Playback controls: JKL shuttle, speed (0.5-2x), frame step, Space/Arrow shortcuts
- Production toolbar: Auto-Assign, Acquire, Pipeline dropdown (Graphics, Narration, Assemble, Captions, Rough Cut, Preflight, Composite)
- Stock search panel (Pexels) in Media tab with per-result download buttons
- Toast notifications (success/error/info/warning with auto-dismiss)
- Keyboard shortcuts panel (press `?`)
- Loading skeletons during initial load
- Export menu: markdown or project JSON
- Remotion-based render: `POST /render-remotion` or `node web/render.mjs` for pixel-perfect MP4
- Dark/light theme toggle (Sun/Moon button in header, CSS variables, persisted to localStorage)
- Resizable preview/timeline split (drag handle, height clamped 120px–60vh, persisted to localStorage)
- lucide-react icons throughout (toolbar, sidebar tabs, menus, media library — replaced all emoji)
- Toolbar visual hierarchy: accent-tinted primary actions (Auto-Assign, Acquire), grouped sections with separators
- Styled form controls: custom dark-themed range sliders and select dropdowns
- Playwright e2e tests: 11 tests covering full UI workflows, integrated into GitHub Actions CI

### Remotion Components (`web/src/components/remotion/`)

19 animated React components that render in the Remotion Player preview and MP4 export:

| Component | Trigger | Description |
|-----------|---------|-------------|
| LowerThird | `LOWER_THIRD` overlay | Animated slide-in name/role bar |
| CaptionOverlay | NAR audio | Karaoke/phrase word-by-word captions |
| KenBurns | `ken_burns` metadata | 7 zoom/pan presets on images |
| QuoteCard | `QUOTE_CARD` overlay | Animated quote with accent bar, author fade-in |
| FinancialCard | `FINANCIAL_CARD` overlay | Counting dollar amount, slide-up panel |
| TextOverlay | `TEXT_OVERLAY` overlay | Typewriter effect with blinking cursor |
| TimelineMarker | `TIMELINE_MARKER` overlay | Animated slide-in date stamp |
| TransitionRenderer | `DISSOLVE`, `FADE_FROM_BLACK` | Overlap (cross-dissolve) or fade mode, UI toggle |
| TextChat | `TEXT_CHAT` visual/overlay | iMessage/Android/Generic chat bubbles, typing/instant/scroll |
| EvidenceBoard | `EVIDENCE_BOARD` visual/overlay | Conspiracy wall — pinned cards, red string connections |
| AnimatedMap | `MAP`, `MAP-*` visual/overlay | MapLibre GL satellite/dark/tactical, fly-to/orbit/route/waypoints |
| SocialPost | `SOCIAL_POST` visual/overlay | Facebook/Instagram/Twitter, slide/reveal/phone animations |
| PictureInPicture | `PIP` visual/overlay | Corner PiP, side-by-side, top-bottom with any source combo |
| AudioVisualization | `WAVEFORM`, `AUDIO_VIS` | Animated bars/waveform/pulse for 911 calls with background media |
| PhotoViewerCard | `PHOTO_VIEWER` overlay/visual | macOS-style photo window with name label, multi-card support |
| SourceBadge | `SOURCE_BADGE` overlay | [ACTUAL]/[REENACTMENT] corner label |
| BulletList | `BULLET_LIST` overlay/visual | Staggered reveal text bars for charge sheets |
| InfoCard | `INFO_CARD` overlay/visual | Split photo + structured sections (charges, sentencing) |
| Watermark | project-level config | Persistent semi-transparent channel logo/text |

Components receive content via `OverlayEntry.content` or `VisualEntry` fields. Configuration uses top-level fields on entries (platform, animation, style, coordinates, etc.) — no nested `metadata` objects. All support both visual (full-screen) and overlay modes via the `OVERLAY_COMPONENTS` registry in `BeeComposition.tsx`.

**Key API routes (Express server in `web/server/`):**
- `POST /api/projects/load` — load storyboard `.md` → `.bee-project.json`
- `GET /api/projects/current` — return current project state
- `PUT /api/projects/update-segment` — update segment properties
- `GET /api/media` — list project media by category
- `POST /api/media/upload` — upload media file
- `GET /api/media/file` — serve media file for preview
- `POST /api/production/render-remotion` — Remotion MP4 render
- `GET /api/production/effects` — available presets/transitions

## Known Gaps & Planned Work

> Full tracking in `ROADMAP.md`. Summary of remaining items:

**Planned:**
- Responsive layout — collapse sidebars to tabs on screens < 1024px
- Real AI video providers (Kling, Veo) — infra is built, API wiring pending
- LLM screenplay generation from case research doc + formula
- FOIA pipeline tracker

## Project Directory Structure (after init)

```
my-project/
├── output/
│   ├── segments/       # Trimmed source clips
│   ├── normalized/     # 1080p/30fps standardized
│   ├── composited/     # Per-segment composited outputs (visual + overlay + audio)
│   ├── graphics/       # Generated PNGs
│   ├── narration/      # TTS audio files
│   ├── previews/       # 360p thumbnails per segment
│   ├── rough/          # rough_cut.mp4
│   └── final/          # final_assembled.mp4
├── stock/              # Downloaded stock footage
├── generated/          # AI-generated clips
└── .bee-project.json    # Project state (web editor)
```

All web editor state lives in `.bee-project.json` (`BeeProject` format). Sidecar files are deprecated.

## Test Patterns

- **Parsers/formats:** Inline markdown + OTIO fixtures → assert on `ParsedStoryboard` structure
- **Graphics:** Mock Pillow → verify function calls + output paths
- **FFmpeg:** Mock subprocess.run → verify filter strings (no real video)
- **Services:** Temp directories → integration-style pipeline calls
- **API (Python):** FastAPI TestClient — all route groups, security boundaries, edge cases
- **API (Node.js):** supertest — ProjectStore unit tests, route integration tests, path traversal checks

374 Python CLI tests. 215 frontend + server vitest tests (98 frontend + 24 store + 24 route + 26 TTS + 13 media-utils + 17 acquisition + 13 matcher/download).

## Dependencies

**Core:** typer, rich, pillow, edge-tts, pydantic, opentimelineio, httpx, pysubs2
**Web (backend — Node.js):** express, cors, multer, tsx, node-edge-tts, @elevenlabs/elevenlabs-js, openai
**Web (frontend):** @xzdarcy/react-timeline-editor, @xzdarcy/timeline-engine, remotion, @remotion/player, @remotion/cli, @remotion/bundler, @remotion/renderer, maplibre-gl, lucide-react, vitest
**TTS extras:** kokoro + soundfile (`--extra tts-kokoro`), openai (`--extra tts-openai`), elevenlabs (`--extra tts-elevenlabs`)
**Maps:** py-staticmaps (`--extra maps`)
**Dev:** pytest (`--extra dev`)
**System:** FFmpeg must be installed and on PATH

## Content Production Skills (Claude Code)

Six skills under `.claude/commands/true-crime/` for the full video production pipeline:

```
/true-crime:research-case            → case-research.md
/true-crime:review-case-research     → viability & completeness check

/true-crime:generate-screenplay      → screenplay.md
/true-crime:review-screenplay        → formula compliance check

/true-crime:generate-storyboard      → storyboard.md (JSON blocks)
/true-crime:review-storyboard        → production readiness check

bee-video produce                    → final video
```

Each generation skill reads the formula + visual bible as context. Each review skill checks against formula requirements.

## Related Documents

| Doc | Purpose |
|-----|---------|
| `CHANGELOG.md` | Version history (v0.1.0 → v0.9.0) |
| `ROADMAP.md` | Planned features and known gaps |
| `README.md` | User-facing usage docs |
| `../research/screenplay-storyboard-formula.md` | The production formula this tool serves |
| `../research/visual-storyboard-bible.md` | Visual element specs the graphics processor should implement |
