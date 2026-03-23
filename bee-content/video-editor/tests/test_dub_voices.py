import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.voices import setup_voices


class TestVoices:
    def test_clone_mode(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        (voices_dir / "speaker_0.mp3").write_bytes(b"audio")
        (voices_dir / "speaker_1.mp3").write_bytes(b"audio")
        manifest_path = voices_dir / "manifest.json"
        with patch("bee_video_editor.services.dub.voices._clone_voice") as mock_clone:
            mock_clone.return_value = "cloned_voice_123"
            setup_voices(voices_dir, manifest_path, speakers=["speaker_0", "speaker_1"], mode="clone")
            manifest = json.loads(manifest_path.read_text())
            assert manifest["speaker_0"] == "cloned_voice_123"
            assert manifest["speaker_1"] == "cloned_voice_123"

    def test_mapped_mode_with_overrides(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        manifest_path = voices_dir / "manifest.json"
        overrides = {"speaker_0": "voice_abc", "speaker_1": "voice_def"}
        setup_voices(voices_dir, manifest_path, speakers=["speaker_0", "speaker_1"], mode="mapped", overrides=overrides)
        manifest = json.loads(manifest_path.read_text())
        assert manifest["speaker_0"] == "voice_abc"
        assert manifest["speaker_1"] == "voice_def"

    def test_skip_if_manifest_exists(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        manifest_path = voices_dir / "manifest.json"
        manifest_path.write_text(json.dumps({"speaker_0": "existing"}))
        with patch("bee_video_editor.services.dub.voices._clone_voice") as mock:
            setup_voices(voices_dir, manifest_path, speakers=["speaker_0"], mode="clone")
            mock.assert_not_called()
