import json
from pathlib import Path
from bee_video_editor.services.dub.models import DubConfig, DubSegment, SegmentState


class TestDubConfig:
    def test_default_config(self):
        config = DubConfig()
        assert config.languages == ["es"]
        assert config.transcription.engine == "whisper"
        assert config.translation.engine == "claude"
        assert config.voices.mode == "clone"
        assert config.tts.engine == "elevenlabs"
        assert config.compositor.target_lufs == -14.0

    def test_load_from_json(self, tmp_path):
        data = {
            "source": "source.mp4",
            "languages": ["es", "de"],
            "translation": {"engine": "deepl"},
        }
        config_path = tmp_path / "dub.json"
        config_path.write_text(json.dumps(data))
        config = DubConfig.load(config_path)
        assert config.source == "source.mp4"
        assert config.languages == ["es", "de"]
        assert config.translation.engine == "deepl"
        assert config.voices.mode == "clone"

    def test_save_config(self, tmp_path):
        config = DubConfig(source="test.mp4", languages=["ar"])
        out = tmp_path / "dub.json"
        config.save(out)
        loaded = json.loads(out.read_text())
        assert loaded["source"] == "test.mp4"
        assert loaded["languages"] == ["ar"]


class TestDubSegment:
    def test_segment_defaults(self):
        seg = DubSegment(
            id="seg_001",
            text="Hello world",
            speaker="speaker_0",
            start_ms=0,
            end_ms=5000,
        )
        assert seg.state == SegmentState.PENDING
        assert seg.translated_text is None
        assert seg.target_duration_ms == 5000

    def test_segment_duration(self):
        seg = DubSegment(
            id="seg_001", text="Hi", speaker="speaker_0",
            start_ms=1000, end_ms=3500,
        )
        assert seg.target_duration_ms == 2500
