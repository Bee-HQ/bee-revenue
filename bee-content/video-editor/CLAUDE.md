# CLAUDE.md — bee-video-editor

## What This Is

Storyboard-first AI video production tool. Parses markdown storyboards/assembly guides, manages media, generates assets (TTS narration, graphics), and assembles final video — via CLI, web UI, or Python API.

Currently used for true crime content production (Alex Murdaugh case).

## Commands

```bash
# Start web editor (always rebuilds frontend)
./start.sh

# Dev mode (Vite hot-reload + FastAPI)
./dev.sh

# CLI
uv run bee-video parse <storyboard.md>
uv run bee-video segments <storyboard.md>
uv run bee-video init <storyboard.md> --project-dir ./project
uv run bee-video serve --port 8420

# Tests
uv run --extra dev pytest tests/ -v
```

## Architecture

```
Adapters (CLI / Web UI) → API (FastAPI) → Services → Processors (FFmpeg, TTS, Pillow)
                                        → Parsers (assembly_guide, storyboard)
                                        → Models (Project, Storyboard, Segment)
```

### Backend (`src/bee_video_editor/`)

| Module | Role |
|--------|------|
| `adapters/cli.py` | Typer CLI — all `bee-video` commands including `serve` |
| `api/server.py` | FastAPI app factory, static file serving, CORS |
| `api/routes/` | `projects.py`, `media.py`, `production.py` |
| `api/schemas.py` | Pydantic request/response models |
| `parsers/` | `assembly_guide.py` (original), `storyboard.py` (layered format) |
| `models.py` | Project, Segment, Section — assembly guide data |
| `models_storyboard.py` | StoryboardSegment with typed layers (visual, audio, overlay, music) |
| `processors/ffmpeg.py` | Trim, concat, transitions (30+ xfade), Ken Burns, color grades, PiP |
| `processors/graphics.py` | Pillow-based lower thirds, cards, overlays |
| `processors/tts.py` | Edge (free cloud), Kokoro (free local), OpenAI (paid) |
| `services/production.py` | Orchestrates full pipeline: init → graphics → narration → trim → assemble |

### Frontend (`web/src/`)

React + TypeScript + Vite + TailwindCSS + Zustand.

| Component | Role |
|-----------|------|
| `App.tsx` | Routes: `LoadProject` if no storyboard, `Layout` otherwise |
| `LoadProject.tsx` | Storyboard path input (defaults to alex-murdaugh) |
| `Layout.tsx` | App shell: sidebar + main + preview |
| `StoryboardTimeline.tsx` | Vertical segment cards grouped by section |
| `SegmentCard.tsx` | Single segment — layers, media assignment drop zone |
| `MediaLibrary.tsx` | Project file browser, draggable files |
| `PreviewPanel.tsx` | Segment/full preview container |
| `VideoPlayer.tsx` | HTML5 video player |
| `ProductionBar.tsx` | Generate narration/graphics/assemble buttons |
| `stores/project.ts` | Zustand store — project state, API calls |
| `api/client.ts` | Fetch wrapper for backend API |

## Key Design Decisions

- **Storyboard is source of truth** — editor reads it, media assignments stored as sidecar JSON
- **No NLE timeline** — segments are cards, not horizontal tracks. Storyboard order = edit order
- **Preview via FFmpeg** — server-side rendering, streamed back to browser
- **Media assignment = drag & drop** — drag from library onto segment layer

## Known Issues / Fixes

- **Browser cache**: `index.html` is served with `Cache-Control: no-store` (in `server.py`) so the browser always fetches the latest entry point. Vite's hashed assets cache normally. If you see stale UI, the no-store header should prevent it — but `Cmd+Shift+R` as fallback.
- **start.sh always rebuilds**: No conditional build check — every `./start.sh` runs `npm install + npm run build`. This is intentional to avoid stale builds during development.

## Logging

Structured JSON logs to `<project_dir>/.bee-video/logs/bee-video.log` (20MB rotation, 5 backups). Human-readable console output on by default.

```bash
# Override log directory
BEE_VIDEO_LOG_DIR=/tmp/logs ./start.sh

# Disable human-readable console logs (prod)
BEE_VIDEO_HUMAN_LOGS=0

# Set log level
bee-video serve --log-level DEBUG
```

To read logs:
```bash
# Tail structured JSON logs
tail -f .bee-video/logs/bee-video.log | python -m json.tool

# Search for errors
grep '"level":"ERROR"' .bee-video/logs/bee-video.log | python -m json.tool
```

## Related Docs

- [ROADMAP.md](ROADMAP.md) — prioritized improvements (v0.3.1 → v0.5.0)
- [PLAN.md](PLAN.md) — original architecture plan for the web editor
- [CHANGELOG.md](CHANGELOG.md) — version history (v0.1.0 → v0.3.0)
- [README.md](README.md) — usage docs, CLI reference, effects/transitions tables
