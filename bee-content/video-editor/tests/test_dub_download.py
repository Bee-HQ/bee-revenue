from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.download import download_video


class TestDownload:
    def test_download_calls_ytdlp(self, tmp_path):
        out = tmp_path / "source.mp4"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            download_video("https://youtube.com/watch?v=abc123", out)
            cmd = mock_run.call_args[0][0]
            assert "yt-dlp" in cmd[0]
            assert "https://youtube.com/watch?v=abc123" in cmd

    def test_skip_if_exists(self, tmp_path):
        out = tmp_path / "source.mp4"
        out.write_bytes(b"existing")
        with patch("subprocess.run") as mock_run:
            result = download_video("https://youtube.com/watch?v=abc", out)
            mock_run.assert_not_called()
            assert result == out

    def test_raises_on_failure(self, tmp_path):
        out = tmp_path / "source.mp4"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="error")
            import pytest
            with pytest.raises(RuntimeError):
                download_video("https://youtube.com/watch?v=abc", out)

    def test_error_includes_stderr(self, tmp_path):
        out = tmp_path / "source.mp4"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="video not found")
            import pytest
            with pytest.raises(RuntimeError, match="video not found"):
                download_video("https://youtube.com/watch?v=abc", out)
