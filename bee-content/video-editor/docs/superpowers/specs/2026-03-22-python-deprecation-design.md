# Python Web Server Deprecation — Design Spec

## Goal

Remove all Python web server code from the video editor. The Node.js Express server in `web/server/` is the sole backend for the web editor. The Python CLI (`bee-video`) continues to work for all non-serve commands.

## Scope

### Remove

| Item | Path | Reason |
|------|------|--------|
| Python API directory | `src/bee_video_editor/api/` | Dead code — replaced by Express |
| `serve` CLI command | `adapters/cli.py` serve() function | No longer needed |
| `web` optional deps | `pyproject.toml` web extras | `fastapi`, `uvicorn`, `python-multipart` unused |
| `--extra web` in CI | `.github/workflows/ci.yml` | No longer needed for tests |
| Python API tests | `tests/test_api.py`, `tests/test_session_v2.py` | Test dead code |
| `schema_compat.py` | `src/bee_video_editor/api/schema_compat.py` | Bridge layer for Python API |
| `schemas.py` | `src/bee_video_editor/api/schemas.py` | Request/response models for Python API |

### Update (docs + scripts)

| File | Change |
|------|--------|
| `dev.sh` (parent) | Replace `uv run bee-video serve` with `cd web && npx tsx watch server/index.ts` |
| `CLAUDE.md` (video-editor) | Remove `bee-video serve` references, update architecture |
| `CLAUDE.md` (root) | Remove any `bee-video serve` references |
| `README.md` | Update web editor section to Node.js only |
| `setup.sh` | Update echo lines from `bee-video serve` to `./start.sh` |
| `.claude/commands/true-crime/generate-storyboard.md` | `bee-video serve` → `./start.sh` |
| `.claude/commands/true-crime/review-storyboard.md` | `bee-video serve` → `./start.sh` |
| `screenplay-storyboard-formula.md` | `bee-video serve` → `./start.sh` |

### Keep (unchanged)

- All Python CLI commands (`import-md`, `narration`, `graphics`, `trim-footage`, `assemble`, etc.)
- Python processors (`ffmpeg.py`, `tts.py`, `graphics.py`, `scene_detect.py`, etc.)
- Python services (`production.py`, `compositor.py`, `matcher.py`, `acquisition.py`)
- Python formats (`parser.py`, `models.py`, `otio_bridge.py`)
- Python tests for CLI features
- `CHANGELOG.md` historical entries

## Verification

1. `uv run bee-video --help` — still lists all CLI commands, no `serve`
2. `uv run --extra dev pytest tests/ -v` — all remaining tests pass
3. `cd web && npm test` — 215 vitest tests pass
4. `cd web && npx --package=@playwright/test playwright test` — 11 E2E tests pass
5. `./start.sh` and `./dev.sh` — web editor starts on Node.js only
6. `npm run build` — frontend builds clean

## Risk

Low. The Python API code is completely unused by the web editor since the Express migration. No runtime code paths reference it. The only risk is breaking a CLI command that accidentally imports from the API module — verified by running the full Python test suite after removal.
