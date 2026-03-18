"""Logging configuration for bee-video-editor.

Provides:
- JSONFormatter  — one JSON line per log event, suitable for log aggregation
- HumanFormatter — readable console output for development
- setup_logging() — idempotent initializer for the 'bee_video_editor' logger
"""

import json
import logging
import logging.handlers
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Standard LogRecord attributes to exclude from 'extra'
# ---------------------------------------------------------------------------

_STANDARD_ATTRS: frozenset = frozenset(
    logging.LogRecord(
        name="dummy",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="",
        args=(),
        exc_info=None,
    ).__dict__.keys()
) | frozenset(["message", "asctime"])


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


class JSONFormatter(logging.Formatter):
    """Format log records as a single JSON line per event."""

    def format(self, record: logging.LogRecord) -> str:
        data: dict = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="microseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Collect non-standard attributes into 'extra'
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _STANDARD_ATTRS and not k.startswith("_")
        }
        if extra:
            data["extra"] = extra

        # Include exception traceback if present
        if record.exc_info and record.exc_info[0] is not None:
            data["exc"] = "".join(traceback.format_exception(*record.exc_info)).strip()

        return json.dumps(data, default=str)


class HumanFormatter(logging.Formatter):
    """Human-readable log format for console output."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)-5s [%(module)s] %(message)s",
            datefmt="%H:%M:%S",
        )


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------

_LOG_FILE_NAME = "bee-video.log"
_MAX_BYTES = 20 * 1024 * 1024  # 20 MB
_BACKUP_COUNT = 5


def setup_logging(
    log_dir: str | Path | None = None,
    log_level: str = "INFO",
    human_logs: bool = True,
) -> None:
    """Configure the 'bee_video_editor' logger.

    Idempotent — safe to call multiple times; handlers are only attached once.

    Args:
        log_dir:    Directory where the rotating JSON log file is written.
                    Defaults to ./logs if not specified.
        log_level:  Minimum log level as a string (e.g. "DEBUG", "INFO").
        human_logs: If True, also emit human-readable output to stderr.
    """
    logger = logging.getLogger("bee_video_editor")

    # Idempotency guard — if handlers are already attached, do nothing.
    if logger.handlers:
        return

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    logger.propagate = False

    # Rotating JSON file handler
    log_path = Path(log_dir) if log_dir else Path("./logs")
    log_path.mkdir(parents=True, exist_ok=True)
    log_path = log_path / _LOG_FILE_NAME
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_path),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    # Optional human-readable stream handler (stderr)
    if human_logs:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(HumanFormatter())
        stream_handler.setLevel(log_level)
        logger.addHandler(stream_handler)
