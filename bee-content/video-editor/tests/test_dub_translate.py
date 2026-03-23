import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.translate import translate_segments


class TestTranslate:
    def _make_diarization(self, tmp_path):
        data = {
            "segments": [
                {"id": 0, "start_ms": 0, "end_ms": 3000, "text": "Welcome to the show", "speaker": "speaker_0"},
                {"id": 1, "start_ms": 3000, "end_ms": 6000, "text": "Thanks for having me", "speaker": "speaker_1"},
            ],
            "speakers": ["speaker_0", "speaker_1"],
        }
        path = tmp_path / "diarization.json"
        path.write_text(json.dumps(data))
        return path

    def test_translates_all_segments(self, tmp_path):
        diarization_path = self._make_diarization(tmp_path)
        output_path = tmp_path / "translations" / "es.json"
        with patch("bee_video_editor.services.dub.translate._translate_claude") as mock:
            mock.return_value = [
                {"id": 0, "text": "Bienvenidos al show", "target_duration_ms": 3000},
                {"id": 1, "text": "Gracias por invitarme", "target_duration_ms": 3000},
            ]
            translate_segments(diarization_path, output_path, lang="es")
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 2
            assert data["segments"][0]["translated_text"] == "Bienvenidos al show"
            assert data["segments"][0]["target_duration_ms"] == 3000
            assert data["lang"] == "es"

    def test_skip_if_exists(self, tmp_path):
        diarization_path = self._make_diarization(tmp_path)
        output_path = tmp_path / "translations" / "es.json"
        output_path.parent.mkdir(parents=True)
        output_path.write_text(json.dumps({"segments": [], "lang": "es"}))
        with patch("bee_video_editor.services.dub.translate._translate_claude") as mock:
            translate_segments(diarization_path, output_path, lang="es")
            mock.assert_not_called()
