# Logging Framework Design

Comprehensive logging for bee-video-editor: structured JSON to file for machine parsing, human-readable to console for development. Covers all layers from API routes to subprocess calls.

## Problem

The codebase has almost no logging. One `logger` instance exists (in `media.py`). FFmpeg errors are silently swallowed, parser failures are skipped without trace, async downloads store errors in ephemeral memory dicts, and the production pipeline runs completely dark. When something breaks, there's no trail to follow.

## Goals

1. **Debuggability** — when video assembly fails, the log shows exactly which FFmpeg command failed, with stderr output
2. **Audit trail** — what operations ran, when, what succeeded/failed
3. **Zero-config by default** — works out of the box, configurable when needed
4. **Minimal footprint** — stdlib only, one new module, no architectural changes

## Design

### New Module

```
src/bee_video_editor/log_config.py
```

Contains:
- `setup_logging(log_dir, log_level, human_logs)` — configures root `bee_video_editor` logger
- `JSONFormatter` — structured JSON, one line per event
- `HumanFormatter` — clean, scannable terminal output

### Dual Handler Architecture

```
bee_video_editor (root logger)
├── StreamHandler (console)
│   ├── Format: human-readable
│   ├── Level: from config
│   └── Toggle: BEE_VIDEO_HUMAN_LOGS (default: 1)
│
└── RotatingFileHandler (file)
    ├── Format: JSON, one line per event
    ├── Level: from config
    ├── File: <log_dir>/bee-video.log
    ├── Max size: 20MB
    └── Backup count: 5 (100MB total max)
```

### Configuration

| Control | Type | Default | Purpose |
|---------|------|---------|---------|
| `--log-dir` / `BEE_VIDEO_LOG_DIR` | path | `<project_dir>/.bee-video/logs/` | Log file location |
| `--log-level` / `BEE_VIDEO_LOG_LEVEL` | string | `INFO` | Minimum log level |
| `BEE_VIDEO_HUMAN_LOGS` | `0`/`1` | `1` | Enable console human-readable handler |

CLI flags take precedence over env vars. Env vars take precedence over defaults.

When no project is loaded yet (server starting up), log dir falls back to `./logs/` relative to the working directory. Once a project loads, the log dir is resolved relative to the project directory.

### Log Formats

**Console (human-readable):**
```
23:45:12 INFO  [production] Generating narration for 12 segments (engine=edge)
23:45:14 ERROR [tts] Failed segment "911 Call" — edge-tts timeout after 30s
23:45:15 DEBUG [ffmpeg] cmd: ffmpeg -i input.mp4 -c copy output.mp4 (exit=0, 1.2s)
```

Format string: `%(asctime)s %(levelname)-5s [%(module)s] %(message)s` with `%H:%M:%S` time format. Short module name (not full dotted path) for readability.

**File (JSON):**
```json
{"ts":"2026-03-17T23:45:14.123456","level":"ERROR","logger":"bee_video_editor.processors.tts","msg":"Failed segment","extra":{"segment":"911 Call","engine":"edge","error":"timeout after 30s"}}
```

Fields:
- `ts` — ISO 8601 timestamp with microseconds
- `level` — DEBUG/INFO/WARNING/ERROR/CRITICAL
- `logger` — full dotted logger name
- `msg` — log message
- `extra` — any additional key-value pairs passed via `logger.info("msg", extra={...})`. Note: `JSONFormatter` must extract non-standard LogRecord attributes into this field, since stdlib's `extra` merges keys flat into the LogRecord rather than nesting them.
- `exc` — exception traceback string (only present when `logger.exception()` is used)

### Initialization Points

1. **CLI entry** (`adapters/cli.py`) — call `setup_logging()` before any command runs. For `serve` command, pass `--log-dir` and `--log-level` through to the function.
2. **FastAPI app** (`api/server.py`) — `setup_logging()` called in `create_app()` if not already configured (idempotent).

The `setup_logging()` function is idempotent — calling it multiple times is safe (checks if handlers already attached).

### Per-Module Logger Pattern

Every module gets its own logger:

```python
import logging

logger = logging.getLogger(__name__)
```

This is the only change needed per file. The logger name follows the module path (e.g., `bee_video_editor.processors.ffmpeg`), which means the root `bee_video_editor` logger's handlers capture everything.

### What Gets Logged

#### API Routes (`api/routes/`)

| Event | Level | Example |
|-------|-------|---------|
| Project loaded | INFO | `Loaded storyboard: 24 segments from storyboard.md` |
| Media file served | DEBUG | `Serving /path/to/file.mp4 (remuxed: false)` |
| Download started | INFO | `Download started: ytdlp-1234 url=https://...` |
| Download completed | INFO | `Download completed: ytdlp-1234 (exit=0)` |
| Download failed | ERROR | `Download failed: ytdlp-1234 (exit=1)` + last 10 lines of output |
| Request error | ERROR | `404: File not found: /missing/path` |

#### Services (`services/production.py`)

| Event | Level | Example |
|-------|-------|---------|
| Pipeline step start | INFO | `Starting narration generation for 12 segments (engine=edge)` |
| Pipeline step complete | INFO | `Narration complete: 12/12 segments (34.2s)` |
| Pipeline step failed | ERROR | `Narration failed at segment 7 "911 Call"` + exception |
| Assembly start/complete | INFO | `Assembling 24 segments with transition=fade` |

#### Processors (`processors/`)

| Event | Level | Example |
|-------|-------|---------|
| FFmpeg command | DEBUG | `ffmpeg cmd: ['ffmpeg', '-i', ...] cwd=/path` |
| FFmpeg success | DEBUG | `ffmpeg completed (exit=0, 2.3s)` |
| FFmpeg failure | ERROR | `ffmpeg failed (exit=1): <stderr first 1000 chars>` |
| TTS segment | DEBUG | `Generating narration: segment="911 Call" engine=edge` |
| TTS failure | ERROR | `TTS failed for segment "911 Call": <error>` |
| Graphics generated | DEBUG | `Generated lower_third: output.png (1920x200)` |

#### Parsers (`parsers/`)

| Event | Level | Example |
|-------|-------|---------|
| File parsed | INFO | `Parsed storyboard.md: 4 sections, 24 segments, 12:30 total` |
| Parse warning | WARNING | `Skipping malformed segment at line 45: missing timecode` |
| Parse error | ERROR | `Failed to parse storyboard.md: <error>` |

#### Media (`api/routes/media.py`)

| Event | Level | Example |
|-------|-------|---------|
| Remux triggered | INFO | `Remuxing file.mp4 (mpegts → mp4)` |
| Remux cached | DEBUG | `Serving cached remux: file-abc123.mp4` |
| Remux failed | WARNING | `Remux failed for file.mp4: <stderr>` |

### Silent Failures to Fix

These existing `except` blocks currently swallow errors silently. They will be updated to log:

1. `services/production.py:230,248` — FFmpeg errors in production pipeline → `logger.exception()`
2. `parsers/storyboard.py:276,319,362` — ValueError in segment parsing → `logger.warning()`
3. `adapters/dashboard.py:64-68` — generic Exception → `logger.exception()`

### What This Does NOT Include

- No correlation IDs or request tracing (overkill for a local tool)
- No remote log shipping (Datadog, CloudWatch, etc.)
- No custom log levels
- No per-module log level overrides
- No log aggregation UI
- No middleware-level request/response logging (uvicorn already does this)

### File Layout After Implementation

```
src/bee_video_editor/
├── log_config.py              # NEW: setup_logging(), JSONFormatter, HumanFormatter
├── models.py               # + logger = logging.getLogger(__name__)
├── models_storyboard.py    # + logger
├── adapters/
│   └── cli.py              # + setup_logging() call, --log-dir/--log-level flags
├── api/
│   ├── server.py           # + setup_logging() in create_app()
│   └── routes/
│       ├── media.py         # already has logger, add more log points
│       ├── projects.py      # + logger
│       └── production.py    # + logger
├── parsers/
│   ├── assembly_guide.py   # + logger, replace silent excepts
│   └── storyboard.py       # + logger, replace silent excepts
├── processors/
│   ├── ffmpeg.py           # + logger, log commands and stderr
│   ├── graphics.py         # + logger
│   └── tts.py              # + logger
└── services/
    └── production.py       # + logger, replace silent excepts
```

### Testing

- Unit test `JSONFormatter` output structure
- Unit test `HumanFormatter` output format
- Unit test `setup_logging()` idempotency (calling twice doesn't duplicate handlers)
- Unit test log rotation config (max bytes, backup count)
- Integration test: log file is created and written to when a route is called
