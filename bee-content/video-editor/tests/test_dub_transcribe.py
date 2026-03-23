import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.transcribe import transcribe_audio


class TestTranscribe:
    def test_returns_segments(self, tmp_path):
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "transcript.json"
        with patch("bee_video_editor.services.dub.transcribe._whisper_api") as mock_api:
            mock_api.return_value = [
                {"id": 0, "start_ms": 0, "end_ms": 2500, "text": "Hello there"},
                {"id": 1, "start_ms": 2500, "end_ms": 5000, "text": "How are you"},
            ]
            result = transcribe_audio(audio_path, output_path, engine="whisper")
            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 2
            assert data["segments"][0]["text"] == "Hello there"
            assert data["segments"][0]["start_ms"] == 0
            assert data["segments"][0]["end_ms"] == 2500

    def test_skip_if_exists(self, tmp_path):
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "transcript.json"
        output_path.write_text(json.dumps({"segments": []}))
        with patch("bee_video_editor.services.dub.transcribe._whisper_api") as mock_api:
            transcribe_audio(audio_path, output_path)
            mock_api.assert_not_called()
