# bee-video-editor

AI-assisted video production tool. Takes assembly guide markdown files and helps produce final videos through CLI commands and a Streamlit dashboard.

## Quick Start

```bash
cd bee-video-editor

# Parse and inspect an assembly guide
uv run bee-video parse /path/to/assembly-guide.md

# List all segments
uv run bee-video segments /path/to/assembly-guide.md

# Initialize a production project
uv run bee-video init /path/to/assembly-guide.md

# Generate assets
uv run bee-video graphics /path/to/assembly-guide.md
uv run bee-video narration /path/to/assembly-guide.md --tts edge
uv run bee-video trim-footage /path/to/assembly-guide.md

# Assemble final video
uv run bee-video assemble

# Launch dashboard
uv run streamlit run src/bee_video_editor/adapters/dashboard.py
```

## Architecture

```
Adapters (CLI / Dashboard) → Services → Parsers + Processors
```

- **Parsers**: Assembly guide markdown → structured `Project` model
- **Processors**: FFmpeg (trim/composite/concat), Pillow (graphics), TTS (edge/kokoro/openai)
- **Services**: Production pipeline orchestration with persistent state
- **Adapters**: Typer CLI + Streamlit dashboard
