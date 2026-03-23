from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.separate import separate_vocals


class TestSeparate:
    def test_calls_demucs(self, tmp_path):
        audio = tmp_path / "source.mp4"
        audio.touch()
        out_dir = tmp_path / "separated"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            demucs_out = tmp_path / "separated" / "htdemucs" / "source"
            demucs_out.mkdir(parents=True)
            (demucs_out / "vocals.wav").write_bytes(b"vocals")
            (demucs_out / "no_vocals.wav").write_bytes(b"accompaniment")
            vocals, accompaniment = separate_vocals(audio, out_dir)
            assert vocals.exists()
            assert accompaniment.exists()

    def test_skip_if_exists(self, tmp_path):
        out_dir = tmp_path / "separated"
        out_dir.mkdir()
        (out_dir / "vocals.wav").write_bytes(b"v")
        (out_dir / "accompaniment.wav").write_bytes(b"a")
        with patch("subprocess.run") as mock_run:
            separate_vocals(tmp_path / "source.mp4", out_dir)
            mock_run.assert_not_called()
