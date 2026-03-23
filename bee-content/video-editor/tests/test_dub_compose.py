import json
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from bee_video_editor.services.dub.compose import compose_dubbed_video


class TestCompose:
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
        tts_dir = tmp_path / "tts" / "es"
        tts_dir.mkdir(parents=True)
        (tts_dir / "seg_000.mp3").write_bytes(b"audio0")
        (tts_dir / "seg_001.mp3").write_bytes(b"audio1")
        source = tmp_path / "source.mp4"
        source.touch()
        output = tmp_path / "output" / "es.mp4"
        return source, trans_path, tts_dir, output

    def test_compose_calls_ffmpeg(self, tmp_path):
        source, trans_path, tts_dir, output = self._setup(tmp_path)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            compose_dubbed_video(
                source_video=source, translations_path=trans_path,
                tts_dir=tts_dir, output_path=output,
            )
            assert mock_run.called

    def test_skip_if_exists(self, tmp_path):
        source, trans_path, tts_dir, output = self._setup(tmp_path)
        output.parent.mkdir(parents=True)
        output.write_bytes(b"existing")
        with patch("subprocess.run") as mock_run:
            compose_dubbed_video(source, trans_path, tts_dir, output)
            mock_run.assert_not_called()
