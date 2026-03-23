import json
from pathlib import Path
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.models import SegmentState


class TestStatusTracker:
    def test_init_creates_file(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        assert tracker.path.exists()

    def test_set_and_get(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "transcribe", SegmentState.COMPLETED)
        assert tracker.get("seg_001", "transcribe") == SegmentState.COMPLETED

    def test_get_unknown_returns_pending(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        assert tracker.get("seg_999", "transcribe") == SegmentState.PENDING

    def test_set_failed_with_error(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.FAILED, error="API timeout")
        assert tracker.get("seg_001", "tts") == SegmentState.FAILED
        assert tracker.get_error("seg_001", "tts") == "API timeout"

    def test_persistence(self, tmp_path):
        path = tmp_path / "status.json"
        tracker = StatusTracker(path)
        tracker.set("seg_001", "translate", SegmentState.COMPLETED)
        tracker2 = StatusTracker(path)
        assert tracker2.get("seg_001", "translate") == SegmentState.COMPLETED

    def test_pending_segments(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.COMPLETED)
        tracker.set("seg_002", "tts", SegmentState.PENDING)
        tracker.set("seg_003", "tts", SegmentState.FAILED)
        pending = tracker.incomplete("tts", ["seg_001", "seg_002", "seg_003"])
        assert pending == ["seg_002", "seg_003"]

    def test_retry_failed_resets(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.FAILED, error="timeout")
        tracker.retry_failed("tts")
        assert tracker.get("seg_001", "tts") == SegmentState.PENDING
        assert tracker.get_error("seg_001", "tts") is None
