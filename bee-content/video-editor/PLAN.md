# Plan: Storyboard-First Web Video Editor

Replace the Streamlit dashboard with a proper web-based video editor built around the storyboard format.

## Stack

- **Backend**: FastAPI (Python) — reuses existing processors (FFmpeg, TTS, Pillow)
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **State**: Zustand (minimal boilerplate)
- **Video preview**: HTML5 video + ffmpeg-generated previews

## Architecture

```
bee-content/video-editor/
├── src/bee_video_editor/
│   ├── models.py              # extend with StoryboardSegment, Layer models
│   ├── parsers/
│   │   ├── assembly_guide.py  # existing (keep)
│   │   └── storyboard.py     # NEW: parse layered storyboard.md format
│   ├── api/                   # NEW: FastAPI server
│   │   ├── __init__.py
│   │   ├── server.py          # FastAPI app, CORS, static file serving
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── projects.py    # load storyboard, project state
│   │       ├── media.py       # list/upload media files, assign to segments
│   │       └── production.py  # generate assets, preview, export
│   ├── processors/            # existing (keep as-is)
│   └── services/              # existing (keep as-is)
├── web/                       # NEW: React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/client.ts      # fetch wrapper for backend
│       ├── stores/
│       │   └── project.ts     # Zustand store
│       ├── types/
│       │   └── index.ts       # TypeScript types matching backend schemas
│       └── components/
│           ├── Layout.tsx           # App shell: sidebar + main area
│           ├── StoryboardTimeline.tsx  # Main view: vertical segment cards
│           ├── SegmentCard.tsx      # Single segment with layers
│           ├── MediaLibrary.tsx     # File browser + drag source
│           ├── MediaAssignment.tsx  # Drop target on segment layers
│           ├── PreviewPanel.tsx     # Video player for segment/full preview
│           └── ProductionBar.tsx    # Generate narration/graphics/trim/assemble
└── pyproject.toml             # add fastapi, uvicorn, python-multipart deps
```

## Steps

### 1. Storyboard parser + models
- New `StoryboardSegment` model with typed layers: visual, audio, overlay, music, source, transition
- Each layer has a `type` (FOOTAGE, STOCK, PHOTO, MAP, GRAPHIC, WAVEFORM, NAR, REAL_AUDIO, MUSIC) and `content`
- Parser reads the `### time | TITLE` + table format from storyboard.md
- Visual layer can have multiple sub-visuals (time-ranged within the segment)

### 2. FastAPI backend
- `POST /api/projects/load` — accepts storyboard path, returns parsed project
- `GET /api/projects/current` — returns current project state
- `GET /api/media` — list files in project media directories
- `POST /api/media/upload` — upload media file
- `PUT /api/segments/{id}/media` — assign a media file to a segment layer
- `POST /api/segments/{id}/preview` — generate preview for one segment
- `POST /api/production/narration` — generate all narration
- `POST /api/production/graphics` — generate all graphics
- `POST /api/production/assemble` — assemble final video
- `GET /api/production/status` — current production state
- Static file serving for media previews

### 3. React frontend
- **Layout**: Left sidebar (media library + production controls), center (storyboard timeline), right (preview panel)
- **StoryboardTimeline**: Vertical scrolling list of segment cards grouped by section/act
- **SegmentCard**: Shows time range, title, all layers with their content. Each layer has a drop zone for media assignment. Color-coded by segment type.
- **MediaLibrary**: Tree view of project files (footage/, stock/, photos/, graphics/). Files are draggable.
- **PreviewPanel**: HTML5 video player. Click a segment to preview it. Play button for full assembly preview.
- **ProductionBar**: Buttons for generate narration, graphics, trim, assemble. Progress indicators.

### 4. Wire up + dev experience
- `cd web && ./start.sh` to start Express server + serve built frontend
- Vite dev server proxies API calls to Express during development (`./dev.sh`)
- Express server replaces FastAPI — no Python needed for the web editor

## Key design decisions

1. **Storyboard is the source of truth** — the editor reads it, media assignments are stored as a sidecar JSON
2. **No NLE timeline** — segments are cards, not a horizontal track. The storyboard order IS the edit order.
3. **Preview via ffmpeg** — clicking "preview" on a segment renders a short clip server-side, streams it back
4. **Media assignment = drag & drop** — drag a file from the library onto a segment's visual/audio layer
5. **Keep existing processors** — FFmpeg, TTS, Pillow code stays exactly as-is
