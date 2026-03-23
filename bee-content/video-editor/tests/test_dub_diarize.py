import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.diarize import diarize_segments


class TestDiarize:
    def _make_transcript(self, tmp_path):
        transcript = {
            "segments": [
                {"id": 0, "start_ms": 0, "end_ms": 5000, "text": "Welcome to the show"},
                {"id": 1, "start_ms": 5000, "end_ms": 10000, "text": "Thanks for having me"},
                {"id": 2, "start_ms": 10000, "end_ms": 15000, "text": "So tell us what happened"},
            ]
        }
        path = tmp_path / "transcript.json"
        path.write_text(json.dumps(transcript))
        return path

    def test_assigns_speakers(self, tmp_path):
        transcript_path = self._make_transcript(tmp_path)
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "diarization.json"
        voices_dir = tmp_path / "voices"
        with patch("bee_video_editor.services.dub.diarize._diarize_pyannote") as mock:
            mock.return_value = [
                {"start_ms": 0, "end_ms": 5000, "speaker": "speaker_0"},
                {"start_ms": 5000, "end_ms": 10000, "speaker": "speaker_1"},
                {"start_ms": 10000, "end_ms": 15000, "speaker": "speaker_0"},
            ]
            diarize_segments(audio_path, transcript_path, output_path, voices_dir)
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 3
            assert data["segments"][0]["speaker"] == "speaker_0"
            assert data["segments"][1]["speaker"] == "speaker_1"
            assert data["speakers"] == ["speaker_0", "speaker_1"]

    def test_skip_if_exists(self, tmp_path):
        transcript_path = self._make_transcript(tmp_path)
        output_path = tmp_path / "diarization.json"
        output_path.write_text(json.dumps({"segments": [], "speakers": []}))
        with patch("bee_video_editor.services.dub.diarize._diarize_pyannote") as mock:
            diarize_segments(tmp_path / "source.mp4", transcript_path, output_path, tmp_path / "voices")
            mock.assert_not_called()
