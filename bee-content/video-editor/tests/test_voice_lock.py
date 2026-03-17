"""Tests for TTS voice lock — per-project voice config persistence."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.api.session import SessionStore
from bee_video_editor.models_storyboard import ProductionRules, Storyboard
from bee_video_editor.services.production import ProductionConfig


def _load_session(d: str) -> tuple[SessionStore, Path]:
    store = SessionStore()
    proj_dir = Path(d) / "project"
    proj_dir.mkdir()
    sb_path = Path(d) / "sb.md"
    sb_path.write_text("# Test\n")

    with patch("bee_video_editor.api.session.parse_storyboard") as mock:
        mock.return_value = Storyboard(
            title="Test", segments=[], stock_footage=[],
            photos_needed=[], maps_needed=[], production_rules=ProductionRules(),
        )
        store.load_project(sb_path, proj_dir)
    return store, proj_dir


class TestVoiceConfig:
    def test_save_voice_config(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            store.save_voice_config("elevenlabs", "Daniel", 0.95)

            config_path = proj_dir.resolve() / ".bee-video" / "voice.json"
            assert config_path.exists()
            data = json.loads(config_path.read_text())
            assert data["engine"] == "elevenlabs"
            assert data["voice"] == "Daniel"
            assert data["speed"] == 0.95

    def test_load_voice_config(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            store.save_voice_config("openai", "nova", 1.0)

            config = store.load_voice_config()
            assert config["engine"] == "openai"
            assert config["voice"] == "nova"

    def test_load_voice_config_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            store, _ = _load_session(d)
            assert store.load_voice_config() is None

    def test_load_voice_config_corrupt_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            config_path = proj_dir.resolve() / ".bee-video" / "voice.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("not valid json{{{")

            assert store.load_voice_config() is None

    def test_save_voice_config_without_project_raises(self):
        store = SessionStore()
        with pytest.raises(Exception):
            store.save_voice_config("edge", None, 0.95)


class TestVoiceLockIntegration:
    def test_production_config_reads_voice_lock(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            store.save_voice_config("elevenlabs", "Daniel", 0.9)

            config = ProductionConfig(project_dir=proj_dir.resolve())
            config.apply_voice_lock()

            assert config.tts_engine == "elevenlabs"
            assert config.tts_voice == "Daniel"

    def test_explicit_engine_overrides_voice_lock(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            store.save_voice_config("elevenlabs", "Daniel", 0.9)

            config = ProductionConfig(project_dir=proj_dir.resolve(), tts_engine="openai")
            config.apply_voice_lock()

            # Explicit engine takes priority
            assert config.tts_engine == "openai"

    def test_no_voice_lock_keeps_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)

            config = ProductionConfig(project_dir=proj_dir.resolve())
            config.apply_voice_lock()

            assert config.tts_engine == "edge"
            assert config.tts_voice is None

    def test_voice_none_roundtrip(self):
        """Locking engine without explicit voice uses engine's default voice."""
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = _load_session(d)
            store.save_voice_config("kokoro", None, 1.0)

            config = ProductionConfig(project_dir=proj_dir.resolve())
            config.apply_voice_lock()

            assert config.tts_engine == "kokoro"
            assert config.tts_voice is None  # engine uses its own default
