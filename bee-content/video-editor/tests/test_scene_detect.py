"""Tests for scene detection processor."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bee_video_editor.processors.scene_detect import (
    Scene, detect_scenes, _timestamps_to_scenes, _get_duration,
)


class TestScene:
    def test_timecodes(self):
        s = Scene(index=0, start_time=65.5, end_time=130.0, duration=64.5)
        assert s.start_timecode == "1:05"
        assert s.end_timecode == "2:10"

    def test_zero_time(self):
        s = Scene(index=0, start_time=0, end_time=5.0, duration=5.0)
        assert s.start_timecode == "0:00"


class TestTimestampsToScenes:
    def test_basic(self):
        scenes = _timestamps_to_scenes([5.0, 10.0], 15.0, 2.0)
        assert len(scenes) == 3
        assert scenes[0].start_time == 0.0
        assert scenes[0].end_time == 5.0
        assert scenes[1].start_time == 5.0
        assert scenes[2].end_time == 15.0

    def test_filters_short_scenes(self):
        scenes = _timestamps_to_scenes([1.0, 2.0, 10.0], 15.0, 3.0)
        # 0-1 (1s, too short), 1-2 (1s, too short), 2-10 (8s, ok), 10-15 (5s, ok)
        assert all(s.duration >= 3.0 for s in scenes)

    def test_empty_timestamps(self):
        scenes = _timestamps_to_scenes([], 10.0, 2.0)
        assert len(scenes) == 1
        assert scenes[0].duration == 10.0

    def test_sequential_indices(self):
        scenes = _timestamps_to_scenes([3.0, 6.0, 9.0], 12.0, 2.0)
        for i, s in enumerate(scenes):
            assert s.index == i


class TestDetectScenes:
    def test_nonexistent_file(self):
        assert detect_scenes("/nonexistent/video.mp4") == []

    @patch("bee_video_editor.processors.scene_detect._get_duration", return_value=30.0)
    @patch("bee_video_editor.processors.scene_detect._detect_with_ffmpeg", return_value=[10.0, 20.0])
    def test_returns_scenes(self, mock_detect, mock_dur, tmp_path):
        video = tmp_path / "test.mp4"
        video.write_bytes(b"fake")
        scenes = detect_scenes(video)
        assert len(scenes) == 3
        assert scenes[0].start_time == 0.0
        assert scenes[1].start_time == 10.0
        assert scenes[2].start_time == 20.0

    @patch("bee_video_editor.processors.scene_detect._get_duration", return_value=0.0)
    def test_zero_duration(self, mock_dur, tmp_path):
        video = tmp_path / "test.mp4"
        video.write_bytes(b"fake")
        assert detect_scenes(video) == []


class TestGetDuration:
    @patch("subprocess.run")
    def test_parses_duration(self, mock_run):
        mock_run.return_value = MagicMock(stdout='{"format": {"duration": "42.5"}}')
        assert _get_duration(Path("test.mp4")) == 42.5

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_ffprobe_missing(self, mock_run):
        assert _get_duration(Path("test.mp4")) == 0.0
