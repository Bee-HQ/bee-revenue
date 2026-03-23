from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from bee_video_editor.services.dub.pipeline import run_pipeline
from bee_video_editor.services.dub.models import DubConfig


class TestPipeline:
    def test_runs_all_steps(self, tmp_path):
        config = DubConfig(source="source.mp4", languages=["es"])
        config.save(tmp_path / "dub.json")
        (tmp_path / "source.mp4").touch()
        with patch("bee_video_editor.services.dub.pipeline.download_video") as dl, \
             patch("bee_video_editor.services.dub.pipeline.transcribe_audio") as tr, \
             patch("bee_video_editor.services.dub.pipeline.diarize_segments") as di, \
             patch("bee_video_editor.services.dub.pipeline.separate_vocals") as sep, \
             patch("bee_video_editor.services.dub.pipeline.translate_segments") as tl, \
             patch("bee_video_editor.services.dub.pipeline.setup_voices") as vo, \
             patch("bee_video_editor.services.dub.pipeline.generate_dubbed_audio") as tts, \
             patch("bee_video_editor.services.dub.pipeline.compose_dubbed_video") as comp:
            sep.return_value = (tmp_path / "vocals.wav", tmp_path / "accompaniment.wav")
            # Need diarization.json to exist for voices step
            diar_path = tmp_path / "diarization.json"
            diar_path.write_text(json.dumps({"segments": [], "speakers": ["speaker_0"]}))
            run_pipeline(tmp_path)
            tr.assert_called_once()
            di.assert_called_once()
            sep.assert_called_once()
            tl.assert_called_once()
            vo.assert_called_once()
            tts.assert_called_once()
            comp.assert_called_once()
