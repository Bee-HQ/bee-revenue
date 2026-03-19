"""Tests for SessionStore (OTIO-based v2)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.api.session import SessionStore


def _write_v2_storyboard(path: Path, title: str = "Test", segments: list[dict] | None = None):
    """Write a v2 storyboard markdown file that parse_v2 can parse."""
    segments = segments or []
    lines = [f"# {title}", ""]
    lines.append("```json bee-video:project")
    lines.append(json.dumps({"title": title, "version": 1}))
    lines.append("```")
    lines.append("")

    if segments:
        lines.append("## Section (0:00 - 10:00)")
        lines.append("")
        for seg in segments:
            start = seg.get("start", "0:00")
            end = seg.get("end", "0:05")
            seg_title = seg.get("title", "Untitled")
            lines.append(f"### {start} - {end} | {seg_title}")
            lines.append("")
            config = seg.get("config", {})
            if config:
                lines.append("```json bee-video:segment")
                lines.append(json.dumps(config))
                lines.append("```")
                lines.append("")
            narration = seg.get("narration", "")
            if narration:
                lines.append(f"> NAR: {narration}")
                lines.append("")

    path.write_text("\n".join(lines))


_DEFAULT_SEGMENTS = [
    {"title": "HOOK", "start": "0:00", "end": "0:05",
     "config": {"visual": [{"type": "FOOTAGE"}]}},
]


class TestSessionStore:
    def test_require_project_raises_when_empty(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.require_project()
        assert exc_info.value.status_code == 404

    def test_load_project_nonexistent_raises(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.load_project(Path("/nonexistent/storyboard.md"), Path("/tmp/proj"))
        assert exc_info.value.status_code == 404

    def test_load_project_sets_state(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            sb_path = Path(d) / "storyboard.md"
            _write_v2_storyboard(sb_path, "Test", _DEFAULT_SEGMENTS)
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()

            result = store.load_project(sb_path, proj_dir)

            assert store.parsed is not None
            assert store.project_dir == proj_dir.resolve()
            assert store.otio_path is not None

    def test_assign_media_persists(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test", _DEFAULT_SEGMENTS)
            store.load_project(sb_path, proj_dir)

            seg_id = store.parsed.segments[0].id
            result = store.assign_media(seg_id, "visual", 0, "/media/clip.mp4")
            assert result["status"] == "ok"

            # Verify in-memory
            seg = next(s for s in store.parsed.segments if s.id == seg_id)
            assert seg.config.visual[0].src == "/media/clip.mp4"

    def test_assign_media_unknown_segment_raises(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test")
            store.load_project(sb_path, proj_dir)

            with pytest.raises(Exception) as exc_info:
                store.assign_media("nonexistent", "visual", 0, "/media/clip.mp4")
            assert exc_info.value.status_code == 404


class TestSegmentOrder:
    def _make_store(self, d: str):
        """Helper: create a SessionStore with a loaded project in temp dir d."""
        store = SessionStore()
        proj_dir = Path(d) / "project"
        proj_dir.mkdir()
        sb_path = Path(d) / "sb.md"
        _write_v2_storyboard(sb_path, "Test", [
            {"title": "A", "start": "0:00", "end": "0:05",
             "config": {"visual": [{"type": "FOOTAGE"}]}},
            {"title": "B", "start": "0:05", "end": "0:10",
             "config": {"visual": [{"type": "FOOTAGE"}]}},
        ])
        store.load_project(sb_path, proj_dir)
        return store, proj_dir

    def test_reorder_segments(self):
        with tempfile.TemporaryDirectory() as d:
            store, _ = self._make_store(d)
            ids = [s.id for s in store.parsed.segments]
            store.reorder_segments(list(reversed(ids)))
            assert [s.id for s in store.parsed.segments] == list(reversed(ids))

    def test_reorder_segments_raises_without_project(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.reorder_segments(["seg_a"])
        assert exc_info.value.status_code == 404

    def test_load_project_restores_saved_order(self):
        """load_project re-orders segments according to saved segment-order.json."""
        with tempfile.TemporaryDirectory() as d:
            store = SessionStore()
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test", [
                {"title": "A", "start": "0:00", "end": "0:05",
                 "config": {"visual": [{"type": "FOOTAGE"}]}},
                {"title": "B", "start": "0:05", "end": "0:10",
                 "config": {"visual": [{"type": "FOOTAGE"}]}},
            ])

            # First load to get segment IDs
            store.load_project(sb_path, proj_dir)
            ids = [s.id for s in store.parsed.segments]

            # Pre-create segment-order.json with reversed order
            order_path = proj_dir.resolve() / ".bee-video" / "segment-order.json"
            order_path.parent.mkdir(parents=True, exist_ok=True)
            order_path.write_text(json.dumps(list(reversed(ids))))

            # Reload — should apply saved order
            store2 = SessionStore()
            parsed = store2.load_project(sb_path, proj_dir)
            assert [s.id for s in parsed.segments] == list(reversed(ids))


class TestSessionPersistence:
    def test_save_session_creates_files(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test")

            store.load_project(sb_path, proj_dir)

            # Check project-local session file
            session_file = proj_dir.resolve() / ".bee-video" / "session.json"
            assert session_file.exists()
            data = json.loads(session_file.read_text())
            assert "otio_path" in data
            assert "project_dir" in data
            assert Path(data["project_dir"]) == proj_dir.resolve()

    def test_save_session_stores_otio_path(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test")

            store.load_project(sb_path, proj_dir)

            session_file = proj_dir.resolve() / ".bee-video" / "session.json"
            data = json.loads(session_file.read_text())
            assert Path(data["otio_path"]).suffix == ".otio"

    def test_save_session_no_crash_when_empty(self):
        store = SessionStore()
        store._save_session()  # Should not crash

    def test_otio_path_set_after_load(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            _write_v2_storyboard(sb_path, "Test")

            store.load_project(sb_path, proj_dir)

            assert store.otio_path is not None
            assert store.otio_path.suffix == ".otio"

    def test_try_restore_skips_missing_storyboard(self):
        """_try_restore with a session pointing to non-existent files returns empty store."""
        from bee_video_editor.api.session import _try_restore

        with tempfile.TemporaryDirectory() as d:
            fake_session = Path(d) / "last-session.json"
            fake_session.write_text(json.dumps({
                "otio_path": "/nonexistent/sb.otio",
                "project_dir": "/nonexistent/proj",
            }))
            with patch("bee_video_editor.api.session.Path") as mock_path_cls:
                # Let real Path work for everything except home()
                real_path = Path
                def path_side_effect(*args, **kwargs):
                    return real_path(*args, **kwargs)
                mock_path_cls.side_effect = path_side_effect
                mock_path_cls.home.return_value = Path(d)
                store = _try_restore()
            # otio_path is /nonexistent/sb.otio which doesn't exist
            # so store should be fresh (parsed is None)
            assert store.parsed is None
