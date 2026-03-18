"""Tests for log_config module — JSONFormatter, HumanFormatter, setup_logging."""

import json
import logging
import tempfile
from pathlib import Path

from bee_video_editor.log_config import JSONFormatter, HumanFormatter, setup_logging

LOGGER_NAME = "bee_video_editor"


def _make_record(msg="hello", level=logging.INFO, name="test.module", **extra):
    record = logging.LogRecord(
        name=name,
        level=level,
        pathname="test_log_config.py",
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(record, k, v)
    return record


# ---------------------------------------------------------------------------
# JSONFormatter tests
# ---------------------------------------------------------------------------


class TestJSONFormatter:
    def setup_method(self):
        self.fmt = JSONFormatter()

    def test_json_formatter_basic_output(self):
        record = _make_record("test message")
        output = self.fmt.format(record)
        data = json.loads(output)

        assert "ts" in data
        assert data["level"] == "INFO"
        assert data["logger"] == "test.module"
        assert data["msg"] == "test message"

    def test_json_formatter_with_extra_fields(self):
        record = _make_record("msg with extra", video_id="abc123", frame=42)
        output = self.fmt.format(record)
        data = json.loads(output)

        assert "extra" in data
        assert data["extra"]["video_id"] == "abc123"
        assert data["extra"]["frame"] == 42

    def test_json_formatter_with_exception(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test_log_config.py",
            lineno=1,
            msg="error occurred",
            args=(),
            exc_info=exc_info,
        )
        output = self.fmt.format(record)
        data = json.loads(output)

        assert "exc" in data
        assert "ValueError" in data["exc"]
        assert "boom" in data["exc"]

    def test_json_formatter_ts_has_microseconds(self):
        record = _make_record("timestamp test")
        output = self.fmt.format(record)
        data = json.loads(output)

        assert "." in data["ts"], f"ts field missing microseconds: {data['ts']!r}"

    def test_json_formatter_no_extra_key_when_no_extras(self):
        record = _make_record("clean message")
        output = self.fmt.format(record)
        data = json.loads(output)

        assert "extra" not in data


# ---------------------------------------------------------------------------
# HumanFormatter tests
# ---------------------------------------------------------------------------


class TestHumanFormatter:
    def setup_method(self):
        self.fmt = HumanFormatter()

    def test_human_formatter_output(self):
        # pathname="test_log_config.py" → %(module)s = "test_log_config"
        record = _make_record("readable message", name="log_config")
        output = self.fmt.format(record)

        assert "INFO" in output
        assert "[test_log_config]" in output
        assert "readable message" in output

    def test_human_formatter_level_alignment(self):
        warn_record = _make_record("warn msg", level=logging.WARNING, name="mod")
        output = self.fmt.format(warn_record)
        assert "WARNI" in output  # %(levelname)-5s truncates WARNING to "WARNI"

    def test_human_formatter_time_format(self):
        record = _make_record("timed message")
        output = self.fmt.format(record)
        # HH:MM:SS format — look for the colon pattern
        import re
        assert re.search(r"\d{2}:\d{2}:\d{2}", output)


# ---------------------------------------------------------------------------
# setup_logging tests
# ---------------------------------------------------------------------------


def _cleanup_logger():
    """Remove all handlers from the bee_video_editor logger."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()


class TestSetupLogging:
    def teardown_method(self):
        _cleanup_logger()

    def test_setup_logging_creates_log_file(self):
        """setup_logging creates log directory and file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)

            logger = logging.getLogger("bee_video_editor.test")
            logger.info("test message")

            log_file = log_dir / "bee-video.log"
            assert log_file.exists()

            content = log_file.read_text()
            data = json.loads(content.strip())
            assert data["msg"] == "test message"

        root = logging.getLogger("bee_video_editor")
        root.handlers.clear()

    def test_setup_logging_idempotent(self):
        with tempfile.TemporaryDirectory() as log_dir:
            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)
            handler_count_1 = len(logging.getLogger(LOGGER_NAME).handlers)

            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)
            handler_count_2 = len(logging.getLogger(LOGGER_NAME).handlers)

            assert handler_count_1 == handler_count_2

    def test_setup_logging_with_human_logs(self):
        with tempfile.TemporaryDirectory() as log_dir:
            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=True)
            logger = logging.getLogger(LOGGER_NAME)
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "StreamHandler" in handler_types

    def test_setup_logging_without_human_logs_no_stream(self):
        with tempfile.TemporaryDirectory() as log_dir:
            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)
            logger = logging.getLogger(LOGGER_NAME)
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "StreamHandler" not in handler_types

    def test_setup_logging_rotation_config(self):
        with tempfile.TemporaryDirectory() as log_dir:
            setup_logging(log_dir=log_dir, log_level="DEBUG", human_logs=False)
            logger = logging.getLogger(LOGGER_NAME)
            rotating_handlers = [
                h for h in logger.handlers
                if hasattr(h, "maxBytes")
            ]
            assert len(rotating_handlers) >= 1
            h = rotating_handlers[0]
            assert h.maxBytes == 20 * 1024 * 1024  # 20MB
            assert h.backupCount == 5
