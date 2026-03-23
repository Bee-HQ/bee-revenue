import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.tts import generate_dubbed_audio
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.models import SegmentState


class TestTTS:
    def _setup(self, tmp_path):
        translations = {
            "lang": "es",
            "segments": [
                {"id": 0, "translated_text": "Hola", "speaker": "speaker_0",
                 "start_ms": 0, "end_ms": 3000, "target_duration_ms": 3000},
                {"id": 1, "translated_text": "Adios", "speaker": "speaker_1",
                 "start_ms": 3000, "end_ms": 6000, "target_duration_ms": 3000},
            ],
        }
        trans_path = tmp_path / "translations" / "es.json"
        trans_path.parent.mkdir(parents=True)
        trans_path.write_text(json.dumps(translations))
        manifest = {"speaker_0": "voice_a", "speaker_1": "voice_b"}
        manifest_path = tmp_path / "voices" / "manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest))
        tts_dir = tmp_path / "tts" / "es"
        status = StatusTracker(tmp_path / "status.json")
        return trans_path, manifest_path, tts_dir, status

    def test_generates_audio_per_segment(self, tmp_path):
        trans_path, manifest_path, tts_dir, status = self._setup(tmp_path)
        with patch("bee_video_editor.services.dub.tts._generate_segment") as mock, \
             patch("elevenlabs.ElevenLabs") as mock_elevenlabs, \
             patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-key"}):
            mock_elevenlabs.return_value = MagicMock()
            mock.return_value = True
            generate_dubbed_audio(trans_path, manifest_path, tts_dir, status)
            assert mock.call_count == 2

    def test_skips_completed_segments(self, tmp_path):
        trans_path, manifest_path, tts_dir, status = self._setup(tmp_path)
        status.set("seg_000", "tts", SegmentState.COMPLETED)
        tts_dir.mkdir(parents=True)
        (tts_dir / "seg_000.mp3").write_bytes(b"audio")
        with patch("bee_video_editor.services.dub.tts._generate_segment") as mock, \
             patch("elevenlabs.ElevenLabs") as mock_elevenlabs, \
             patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-key"}):
            mock_elevenlabs.return_value = MagicMock()
            mock.return_value = True
            generate_dubbed_audio(trans_path, manifest_path, tts_dir, status)
            assert mock.call_count == 1
