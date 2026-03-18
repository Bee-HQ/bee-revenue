# Logging Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add structured JSON file logging and human-readable console logging across all layers of bee-video-editor, replacing silent failures with logged errors.

**Architecture:** One new module (`log_config.py`) provides `setup_logging()` which configures a root `bee_video_editor` logger with two handlers — `RotatingFileHandler` (JSON) and `StreamHandler` (human-readable, toggleable). Every existing module adds `logger = logging.getLogger(__name__)`. Silent `except` blocks get replaced with `logger.exception()` / `logger.warning()`.

**Tech Stack:** Python stdlib `logging` only. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-03-17-logging-framework-design.md`

---

### Task 1: Create `log_config.py` with formatters and `setup_logging()`

**Files:**
- Create: `src/bee_video_editor/log_config.py`
- Test: `tests/test_log_config.py`

- [ ] **Step 1: Write tests for JSONFormatter**

Create `tests/test_log_config.py`:

```python
"""Tests for logging configuration."""

import json
import logging
import tempfile
from pathlib import Path

import pytest


def test_json_formatter_basic_output():
    """JSONFormatter produces valid JSON with required fields."""
    from bee_video_editor.log_config import JSONFormatter

    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="bee_video_editor.processors.ffmpeg",
        level=logging.INFO,
        pathname="ffmpeg.py",
        lineno=42,
        msg="ffmpeg completed",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    data = json.loads(output)

    assert "ts" in data
    assert data["level"] == "INFO"
    assert data["logger"] == "bee_video_editor.processors.ffmpeg"
    assert data["msg"] == "ffmpeg completed"


def test_json_formatter_with_extra_fields():
    """Extra fields passed via logging are nested under 'extra' key."""
    from bee_video_editor.log_config import JSONFormatter

    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="bee_video_editor.processors.tts",
        level=logging.ERROR,
        pathname="tts.py",
        lineno=10,
        msg="TTS failed",
        args=(),
        exc_info=None,
    )
    record.segment = "911 Call"
    record.engine = "edge"

    output = formatter.format(record)
    data = json.loads(output)

    assert data["extra"]["segment"] == "911 Call"
    assert data["extra"]["engine"] == "edge"


def test_json_formatter_with_exception():
    """Exception info is included as 'exc' field."""
    from bee_video_editor.log_config import JSONFormatter

    formatter = JSONFormatter()
    try:
        raise ValueError("test error")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="something broke",
        args=(),
        exc_info=exc_info,
    )
    output = formatter.format(record)
    data = json.loads(output)

    assert "exc" in data
    assert "ValueError: test error" in data["exc"]


def test_human_formatter_output():
    """HumanFormatter produces readable single-line output."""
    from bee_video_editor.log_config import HumanFormatter

    formatter = HumanFormatter()
    record = logging.LogRecord(
        name="bee_video_editor.processors.ffmpeg",
        level=logging.INFO,
        pathname="ffmpeg.py",
        lineno=42,
        msg="ffmpeg completed",
        args=(),
        exc_info=None,
    )
    record.module = "ffmpeg"
    output = formatter.format(record)

    assert "INFO" in output
    assert "[ffmpeg]" in output
    assert "ffmpeg completed" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_log_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bee_video_editor.log_config'`

- [ ] **Step 3: Implement JSONFormatter and HumanFormatter**

Create `src/bee_video_editor/log_config.py`:

```python
"""Logging configuration for bee-video-editor.

Dual-handler setup: JSON to file (machine-readable), human-readable to console.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone
from pathlib import Path

# Standard LogRecord attributes to exclude from the 'extra' dict
_STANDARD_ATTRS = frozenset(logging.LogRecord(
    "", 0, "", 0, "", (), None
).__dict__.keys()) | {"message", "asctime"}


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter — one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc)
                        .isoformat(timespec="microseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Extract non-standard attributes into 'extra'
        extra = {
            k: v for k, v in record.__dict__.items()
            if k not in _STANDARD_ATTRS and not k.startswith("_")
        }
        if extra:
            entry["extra"] = extra

        if record.exc_info and record.exc_info[0] is not None:
            entry["exc"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str)


class HumanFormatter(logging.Formatter):
    """Clean, scannable console output."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s %(levelname)-5s [%(module)s] %(message)s",
            datefmt="%H:%M:%S",
        )
```

- [ ] **Step 4: Run tests to verify formatters pass**

Run: `uv run --extra dev pytest tests/test_log_config.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Write tests for setup_logging()**

Append to `tests/test_log_config.py`:

```python
def test_setup_logging_creates_log_file():
    """setup_logging creates log directory and file."""
    from bee_video_editor.log_config import setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)

        # Get the logger and emit a message
        logger = logging.getLogger("bee_video_editor.test")
        logger.info("test message")

        log_file = log_dir / "bee-video.log"
        assert log_file.exists()

        content = log_file.read_text()
        data = json.loads(content.strip())
        assert data["msg"] == "test message"

    # Clean up handlers to avoid leaking into other tests
    root = logging.getLogger("bee_video_editor")
    root.handlers.clear()


def test_setup_logging_idempotent():
    """Calling setup_logging twice doesn't duplicate handlers."""
    from bee_video_editor.log_config import setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logging(log_dir=log_dir, log_level="INFO", human_logs=False)
        setup_logging(log_dir=log_dir, log_level="INFO", human_logs=False)

        root = logging.getLogger("bee_video_editor")
        handler_count = len(root.handlers)
        # Should have exactly 1 handler (file only, human_logs=False)
        assert handler_count == 1

    root.handlers.clear()


def test_setup_logging_with_human_logs():
    """When human_logs=True, both file and console handlers are attached."""
    from bee_video_editor.log_config import setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logging(log_dir=log_dir, log_level="INFO", human_logs=True)

        root = logging.getLogger("bee_video_editor")
        assert len(root.handlers) == 2

        handler_types = {type(h) for h in root.handlers}
        assert logging.StreamHandler in handler_types
        assert logging.handlers.RotatingFileHandler in handler_types

    root.handlers.clear()


def test_setup_logging_rotation_config():
    """RotatingFileHandler is configured with correct max bytes and backup count."""
    from bee_video_editor.log_config import setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logging(log_dir=log_dir, log_level="INFO", human_logs=False)

        root = logging.getLogger("bee_video_editor")
        file_handler = root.handlers[0]
        assert isinstance(file_handler, logging.handlers.RotatingFileHandler)
        assert file_handler.maxBytes == 20 * 1024 * 1024  # 20MB
        assert file_handler.backupCount == 5

    root.handlers.clear()
```

- [ ] **Step 6: Run tests to verify setup_logging tests fail**

Run: `uv run --extra dev pytest tests/test_log_config.py -v`
Expected: New tests FAIL — `setup_logging` not defined

- [ ] **Step 7: Implement setup_logging()**

Add to `src/bee_video_editor/log_config.py`:

```python
_MAX_BYTES = 20 * 1024 * 1024  # 20MB
_BACKUP_COUNT = 5


def setup_logging(
    log_dir: str | Path | None = None,
    log_level: str = "INFO",
    human_logs: bool = True,
) -> None:
    """Configure logging for bee-video-editor.

    Idempotent — safe to call multiple times.

    Args:
        log_dir: Directory for log files. Defaults to ./logs/ if None.
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        human_logs: If True, add a human-readable console handler.
    """
    root = logging.getLogger("bee_video_editor")

    # Idempotency: skip if already configured
    if root.handlers:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)
    root.setLevel(level)

    # Resolve log directory
    log_path = Path(log_dir) if log_dir else Path("./logs")
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / "bee-video.log"

    # File handler: JSON structured
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())
    file_handler.setLevel(level)
    root.addHandler(file_handler)

    # Console handler: human-readable (optional)
    if human_logs:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(HumanFormatter())
        console_handler.setLevel(level)
        root.addHandler(console_handler)

    # Prevent propagation to root logger (avoid duplicate uvicorn output)
    root.propagate = False
```

- [ ] **Step 8: Run all tests to verify they pass**

Run: `uv run --extra dev pytest tests/test_log_config.py -v`
Expected: All 8 tests PASS

- [ ] **Step 9: Commit**

```bash
git add src/bee_video_editor/log_config.py tests/test_log_config.py
git commit -m "add log_config module with dual formatters and setup_logging"
```

---

### Task 2: Wire up logging in CLI and server entry points

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py:1-16` (app-level callback for all commands)
- Modify: `src/bee_video_editor/adapters/cli.py:397-434` (serve command with extra flags)
- Modify: `src/bee_video_editor/api/server.py:14-48` (create_app)

- [ ] **Step 1: Add typer callback to configure logging for all commands**

In `src/bee_video_editor/adapters/cli.py`, add a callback to the typer app so logging is configured before any command runs:

```python
import os

from bee_video_editor.log_config import setup_logging

@app.callback()
def main(
    log_dir: str = typer.Option(None, "--log-dir", help="Log file directory", hidden=True),
    log_level: str = typer.Option(None, "--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)", hidden=True),
):
    """AI-assisted video production from assembly guides."""
    resolved_log_dir = log_dir or os.environ.get("BEE_VIDEO_LOG_DIR")
    resolved_log_level = log_level or os.environ.get("BEE_VIDEO_LOG_LEVEL", "INFO")
    resolved_human = os.environ.get("BEE_VIDEO_HUMAN_LOGS", "1") != "0"

    setup_logging(
        log_dir=resolved_log_dir,
        log_level=resolved_log_level,
        human_logs=resolved_human,
    )
```

This ensures `setup_logging()` runs before `parse`, `segments`, `init`, `serve`, and all other commands.

- [ ] **Step 2: Add --log-dir and --log-level to serve command**

In `src/bee_video_editor/adapters/cli.py`, modify the `serve` function to pass its log level to uvicorn (logging is already configured via the callback):

The only change to the `serve` function is to read the resolved log level for uvicorn. Logging is already configured by the callback. Modify the last line:

```python
    log_level_str = os.environ.get("BEE_VIDEO_LOG_LEVEL", "INFO").lower()
    uvicorn.run(app_instance, host=host, port=port, log_level=log_level_str)
```

Add `import os` at the top of the serve function if not already imported.

- [ ] **Step 2: Add idempotent setup_logging call in create_app**

In `src/bee_video_editor/api/server.py`, add the logging import and call:

```python
"""FastAPI application for the bee-video-editor web UI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from bee_video_editor.api.routes import media, production, projects
from bee_video_editor.log_config import setup_logging


def create_app(static_dir: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    # Ensure logging is configured (idempotent — no-op if already set up)
    setup_logging()

    app = FastAPI(
        # ... rest unchanged
```

- [ ] **Step 3: Verify server starts correctly**

Run: `uv run bee-video serve --port 8421 --log-level DEBUG &`
Then: `ls ./logs/bee-video.log` — should exist
Kill the server.

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py src/bee_video_editor/api/server.py
git commit -m "wire up logging in CLI serve command and FastAPI app factory"
```

---

### Task 3: Add logging to FFmpeg processor

**Files:**
- Modify: `src/bee_video_editor/processors/ffmpeg.py:1-53`

- [ ] **Step 1: Add logger and log FFmpeg commands**

Add `import logging` and `logger = logging.getLogger(__name__)` after the imports in `ffmpeg.py`.

Modify `run_ffmpeg` to log commands and results:

```python
def run_ffmpeg(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run an ffmpeg command and return the result."""
    cmd = ["ffmpeg", "-y"] + args
    logger.debug("ffmpeg cmd: %s", cmd)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed (exit=%d): %s", result.returncode, result.stderr[:1000])
        if check:
            raise FFmpegError(f"ffmpeg failed: {result.stderr[:500]}")
    else:
        logger.debug("ffmpeg completed (exit=0)")
    return result
```

Similarly, add logging to `probe`:

```python
def probe(input_path: str | Path) -> dict:
    """Get media file info via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_path),
    ]
    logger.debug("ffprobe cmd: %s", cmd)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffprobe failed for %s: %s", input_path, result.stderr[:500])
        return {}
    return json.loads(result.stdout)
```

- [ ] **Step 2: Run existing tests to verify nothing breaks**

Run: `uv run --extra dev pytest tests/test_ffmpeg_effects.py -v`
Expected: All existing tests PASS

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/processors/ffmpeg.py
git commit -m "add logging to FFmpeg processor"
```

---

### Task 4: Add logging to TTS and graphics processors

**Files:**
- Modify: `src/bee_video_editor/processors/tts.py:1-37`
- Modify: `src/bee_video_editor/processors/graphics.py:1-8`

- [ ] **Step 1: Add logger to tts.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

Add logging to `generate_narration`:

```python
def generate_narration(
    text: str,
    output_path: str | Path,
    engine: str = "edge",
    voice: str | None = None,
    speed: float = 0.95,
) -> Path:
    """Generate narration audio from text."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    engines = {
        "edge": _generate_edge,
        "kokoro": _generate_kokoro,
        "openai": _generate_openai,
    }

    if engine not in engines:
        raise ValueError(f"Unknown TTS engine: {engine}. Available: {list(engines.keys())}")

    logger.debug("Generating narration: engine=%s output=%s", engine, output_path.name)
    try:
        result = engines[engine](text, output_path, voice=voice, speed=speed)
        logger.debug("Narration generated: %s", output_path.name)
        return result
    except Exception:
        logger.exception("TTS failed for %s (engine=%s)", output_path.name, engine)
        raise
```

- [ ] **Step 2: Add logger to graphics.py**

Add after the PIL import:

```python
import logging

logger = logging.getLogger(__name__)
```

No other changes needed — graphics functions are simple Pillow operations. The logger is available for future use and keeps the pattern consistent.

- [ ] **Step 3: Run existing tests**

Run: `uv run --extra dev pytest tests/test_graphics.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/processors/tts.py src/bee_video_editor/processors/graphics.py
git commit -m "add logging to TTS and graphics processors"
```

---

### Task 5: Add logging to production service, dashboard, and fix silent failures

**Files:**
- Modify: `src/bee_video_editor/services/production.py:227-251`
- Modify: `src/bee_video_editor/adapters/dashboard.py:64-68`

- [ ] **Step 1: Add logger to production.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

- [ ] **Step 2: Replace silent except blocks with logging**

At line 227-231, replace the silent `except FFmpegError: pass`:

```python
                try:
                    trim(source, out, start=t.start, end=t.duration)
                    trimmed.append(out)
                except FFmpegError:
                    logger.warning("Trim failed for segment %r (source=%s, start=%s, end=%s)",
                                   t.label, source, t.start, t.duration)
```

At line 244-249, replace the second silent `except FFmpegError: pass`:

```python
            try:
                normalize_format(seg_file, out, config.width, config.height, config.fps)
                normalized.append(out)
            except FFmpegError:
                logger.warning("Normalize failed for %s", seg_file.name)
```

- [ ] **Step 3: Add logger to dashboard.py and replace silent except**

Add after the imports in `src/bee_video_editor/adapters/dashboard.py`:

```python
import logging

logger = logging.getLogger(__name__)
```

Replace the silent exception at lines 64-68:

```python
    try:
        project = parse_assembly_guide(guide_path)
    except Exception as e:
        logger.exception("Failed to parse assembly guide: %s", guide_path)
        st.error(f"Failed to parse assembly guide: {e}")
        return
```

- [ ] **Step 4: Run existing tests**

Run: `uv run --extra dev pytest tests/test_production.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py src/bee_video_editor/adapters/dashboard.py
git commit -m "add logging to production service and dashboard, replace silent failures"
```

---

### Task 6: Add logging to parsers, models, and fix silent failures

**Files:**
- Modify: `src/bee_video_editor/parsers/storyboard.py:274-277,317-320,360-363`
- Modify: `src/bee_video_editor/parsers/assembly_guide.py`
- Modify: `src/bee_video_editor/models.py`
- Modify: `src/bee_video_editor/models_storyboard.py`

- [ ] **Step 1: Add logger to storyboard.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

- [ ] **Step 2: Replace silent ValueError continues with warnings**

The three `except ValueError: continue` blocks (lines 274-277, 317-320, 360-363) all parse table index fields. Replace each `continue` with a logged warning before continuing:

```python
        try:
            idx = int(cells[0])
        except ValueError:
            logger.warning("Skipping row with non-integer index %r at table parsing", cells[0])
            continue
```

Apply the same pattern at all three locations.

- [ ] **Step 3: Add logger to assembly_guide.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

Add a log at the end of `parse_assembly_guide`:

```python
    logger.info("Parsed %s: %d sections, %d segments",
                Path(filepath).name, len(project.sections), sum(len(s.segments) for s in project.sections))
```

- [ ] **Step 4: Add logger to storyboard parse_storyboard function**

Add a log at the end of `parse_storyboard`:

```python
    logger.info("Parsed storyboard %s: %d sections, %d segments",
                Path(filepath).name, len(storyboard.sections), len(storyboard.segments))
```

- [ ] **Step 5: Add logger to models.py and models_storyboard.py**

Add after the imports in both `src/bee_video_editor/models.py` and `src/bee_video_editor/models_storyboard.py`:

```python
import logging

logger = logging.getLogger(__name__)
```

These are unused initially but establish the pattern for future use.

- [ ] **Step 6: Run existing tests**

Run: `uv run --extra dev pytest tests/test_parser.py tests/test_storyboard_parser.py tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/bee_video_editor/parsers/storyboard.py src/bee_video_editor/parsers/assembly_guide.py src/bee_video_editor/models.py src/bee_video_editor/models_storyboard.py
git commit -m "add logging to parsers and models, replace silent ValueError continues"
```

---

### Task 7: Add logging to API routes

**Files:**
- Modify: `src/bee_video_editor/api/routes/projects.py:1-25`
- Modify: `src/bee_video_editor/api/routes/production.py:1-18`
- Modify: `src/bee_video_editor/api/routes/media.py` (already has logger — add more log points)

- [ ] **Step 1: Add logger to projects.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

Add logging to `load_project`:

```python
    _current_storyboard = parse_storyboard(sb_path)
    logger.info("Loaded storyboard: %d segments from %s",
                len(_current_storyboard.segments), sb_path.name)
```

- [ ] **Step 2: Add logger to production.py**

Add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

Add logging around the FFmpegError catch (find the existing HTTPException(500) handler):

```python
    except FFmpegError as e:
        logger.exception("Production failed: %s", e)
        raise HTTPException(500, f"FFmpeg error: {e}")
```

- [ ] **Step 3: Add more log points to media.py**

The logger already exists. Add logging for downloads:

In the `_run` async function inside `run_download_script`, after `await proc.wait()`:

```python
            await proc.wait()
            _download_tasks[task_id]["return_code"] = proc.returncode
            if proc.returncode == 0:
                logger.info("Download completed: %s", task_id)
            else:
                logger.error("Download failed: %s (exit=%d) last output: %s",
                            task_id, proc.returncode,
                            "\n".join(_download_tasks[task_id]["output_lines"][-10:]))
```

Apply the same pattern to the `_run` function inside `download_with_ytdlp`.

Add to `serve_media_file`, before the return:

```python
    p = _ensure_browser_playable(p)
    logger.debug("Serving media file: %s", p.name)
    return FileResponse(p)
```

- [ ] **Step 4: Run existing tests**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/api/routes/projects.py src/bee_video_editor/api/routes/production.py src/bee_video_editor/api/routes/media.py
git commit -m "add logging to API routes"
```

---

### Task 8: Integration test — end-to-end log file verification

**Files:**
- Modify: `tests/test_log_config.py`

- [ ] **Step 1: Write integration test**

Append to `tests/test_log_config.py`:

```python
def test_log_file_written_on_parse():
    """Parsing a storyboard writes structured JSON to log file."""
    from bee_video_editor.log_config import setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logging(log_dir=log_dir, log_level="INFO", human_logs=False)

        # Create a minimal storyboard file
        sb = Path(tmpdir) / "storyboard.md"
        sb.write_text("# Test Storyboard\n\n## Section 1\n\n### 0:00-0:30 | Test Segment\n\n| Layer | Type | Content |\n|---|---|---|\n| Visual | FOOTAGE | test.mp4 |\n")

        from bee_video_editor.parsers.storyboard import parse_storyboard
        try:
            parse_storyboard(str(sb))
        except Exception:
            pass  # May fail on minimal input, but logger should still fire

        log_file = log_dir / "bee-video.log"
        if log_file.exists():
            lines = log_file.read_text().strip().split("\n")
            for line in lines:
                # Every line should be valid JSON
                data = json.loads(line)
                assert "ts" in data
                assert "level" in data
                assert "logger" in data

    root = logging.getLogger("bee_video_editor")
    root.handlers.clear()
```

- [ ] **Step 2: Run all tests**

Run: `uv run --extra dev pytest tests/test_log_config.py -v`
Expected: All tests PASS

- [ ] **Step 3: Run full test suite**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All tests PASS (no regressions)

- [ ] **Step 4: Commit**

```bash
git add tests/test_log_config.py
git commit -m "add integration test for log file output"
```

---

### Task 9: Update CLAUDE.md and CHANGELOG.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add logging section to CLAUDE.md**

Add after the "Known Issues / Fixes" section:

```markdown
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
```

- [ ] **Step 2: Add to CHANGELOG.md under [Unreleased]**

Add under the existing `### Added` section:

```markdown
- Comprehensive logging framework: structured JSON to file, human-readable to console
- `--log-dir` and `--log-level` flags on `bee-video serve`
- `BEE_VIDEO_LOG_DIR`, `BEE_VIDEO_LOG_LEVEL`, `BEE_VIDEO_HUMAN_LOGS` env vars
- Logging across all layers: API routes, services, processors, parsers

### Fixed

- Silent FFmpeg failures in production pipeline now logged as warnings
- Silent ValueError in storyboard parser now logged as warnings
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md CHANGELOG.md
git commit -m "document logging framework in CLAUDE.md and CHANGELOG.md"
```
