"""Tests for SessionStore."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.api.session import SessionStore


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
            sb_path.write_text("# Test Storyboard\n\nNo segments.\n")
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                result = store.load_project(sb_path, proj_dir)

            assert store.storyboard is not None
            assert store.project_dir == proj_dir.resolve()
            assert store.assignments_path == proj_dir.resolve() / ".bee-video" / "assignments.json"

    def test_assign_media_persists(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()

            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import (
                    ProductionRules,
                    Storyboard,
                    StoryboardSegment,
                )
                seg = StoryboardSegment(
                    id="0_00-0_05", start="0:00", end="0:05", title="HOOK",
                    section="COLD OPEN", section_time="0:00 - 2:30", subsection="",
                    visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
                    assigned_media={},
                )
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[seg], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(sb_path, proj_dir)

            result = store.assign_media("0_00-0_05", "visual", 0, "/media/clip.mp4")
            assert result["status"] == "ok"

            assignments_path = proj_dir.resolve() / ".bee-video" / "assignments.json"
            assert assignments_path.exists()
            data = json.loads(assignments_path.read_text())
            assert data["0_00-0_05"]["visual:0"] == "/media/clip.mp4"

    def test_assign_media_unknown_segment_raises(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            (Path(d) / "sb.md").write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(Path(d) / "sb.md", proj_dir)

            with pytest.raises(Exception) as exc_info:
                store.assign_media("nonexistent", "visual", 0, "/media/clip.mp4")
            assert exc_info.value.status_code == 404


class TestSegmentOrder:
    def _make_store(self, d: str):
        """Helper: create a SessionStore with a loaded project in temp dir d."""
        from unittest.mock import patch
        from bee_video_editor.models_storyboard import ProductionRules, Storyboard, StoryboardSegment

        store = SessionStore()
        proj_dir = Path(d) / "project"
        proj_dir.mkdir()
        sb_path = Path(d) / "sb.md"
        sb_path.write_text("# Test\n")

        seg_a = StoryboardSegment(
            id="seg_a", start="0:00", end="0:05", title="A",
            section="INTRO", section_time="", subsection="",
            visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
            assigned_media={},
        )
        seg_b = StoryboardSegment(
            id="seg_b", start="0:05", end="0:10", title="B",
            section="INTRO", section_time="", subsection="",
            visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
            assigned_media={},
        )

        with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
            mock_parse.return_value = Storyboard(
                title="Test", segments=[seg_a, seg_b], stock_footage=[],
                photos_needed=[], maps_needed=[], production_rules=ProductionRules(),
            )
            store.load_project(sb_path, proj_dir)
        return store, proj_dir

    def test_load_segment_order_returns_none_when_no_file(self):
        with tempfile.TemporaryDirectory() as d:
            store, _ = self._make_store(d)
            assert store.load_segment_order() is None

    def test_save_and_load_segment_order(self):
        with tempfile.TemporaryDirectory() as d:
            store, proj_dir = self._make_store(d)
            store.save_segment_order(["seg_b", "seg_a"])
            loaded = store.load_segment_order()
            assert loaded == ["seg_b", "seg_a"]
            order_file = proj_dir.resolve() / ".bee-video" / "segment-order.json"
            assert order_file.exists()

    def test_load_project_restores_saved_order(self):
        """load_project re-orders segments according to saved segment-order.json."""
        with tempfile.TemporaryDirectory() as d:
            from unittest.mock import patch
            from bee_video_editor.models_storyboard import ProductionRules, Storyboard, StoryboardSegment

            store = SessionStore()
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            # Pre-create segment-order.json with reversed order
            order_path = proj_dir / ".bee-video" / "segment-order.json"
            order_path.parent.mkdir(parents=True, exist_ok=True)
            order_path.write_text(json.dumps(["seg_b", "seg_a"]))

            seg_a = StoryboardSegment(
                id="seg_a", start="0:00", end="0:05", title="A",
                section="INTRO", section_time="", subsection="",
                visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
                assigned_media={},
            )
            seg_b = StoryboardSegment(
                id="seg_b", start="0:05", end="0:10", title="B",
                section="INTRO", section_time="", subsection="",
                visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
                assigned_media={},
            )

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[seg_a, seg_b], stock_footage=[],
                    photos_needed=[], maps_needed=[], production_rules=ProductionRules(),
                )
                sb = store.load_project(sb_path, proj_dir)

            assert [s.id for s in sb.segments] == ["seg_b", "seg_a"]

    def test_save_segment_order_raises_without_project(self):
        store = SessionStore()
        with pytest.raises(Exception) as exc_info:
            store.save_segment_order(["seg_a"])
        assert exc_info.value.status_code == 404

    def test_load_segment_order_returns_none_without_project(self):
        store = SessionStore()
        assert store.load_segment_order() is None


class TestSessionPersistence:
    def test_save_session_creates_files(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            fake_home = Path(d) / "home"
            fake_home.mkdir()
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                with patch("bee_video_editor.api.session.Path") as mock_path_cls:
                    real_path = Path
                    mock_path_cls.side_effect = lambda *a, **kw: real_path(*a, **kw)
                    mock_path_cls.home.return_value = fake_home
                    store.load_project(sb_path, proj_dir)

            # Check project-local session file
            session_file = proj_dir.resolve() / ".bee-video" / "session.json"
            assert session_file.exists()
            data = json.loads(session_file.read_text())
            assert "storyboard_path" in data
            assert "project_dir" in data
            assert Path(data["project_dir"]) == proj_dir.resolve()

    def test_save_session_stores_storyboard_path(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(sb_path, proj_dir)

            session_file = proj_dir.resolve() / ".bee-video" / "session.json"
            data = json.loads(session_file.read_text())
            assert Path(data["storyboard_path"]) == sb_path.resolve()

    def test_save_session_no_crash_when_empty(self):
        store = SessionStore()
        store._save_session()  # Should not crash

    def test_storyboard_path_set_after_load(self):
        store = SessionStore()
        with tempfile.TemporaryDirectory() as d:
            proj_dir = Path(d) / "project"
            proj_dir.mkdir()
            sb_path = Path(d) / "sb.md"
            sb_path.write_text("# Test\n")

            with patch("bee_video_editor.api.session.parse_storyboard") as mock_parse:
                from bee_video_editor.models_storyboard import ProductionRules, Storyboard
                mock_parse.return_value = Storyboard(
                    title="Test", segments=[], stock_footage=[], photos_needed=[],
                    maps_needed=[], production_rules=ProductionRules(),
                )
                store.load_project(sb_path, proj_dir)

            assert store.storyboard_path == sb_path.resolve()

    def test_try_restore_skips_missing_storyboard(self):
        """_try_restore with a session pointing to non-existent files returns empty store."""
        from bee_video_editor.api.session import _try_restore

        with tempfile.TemporaryDirectory() as d:
            fake_session = Path(d) / "last-session.json"
            fake_session.write_text(json.dumps({
                "storyboard_path": "/nonexistent/sb.md",
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
            # storyboard_path is /nonexistent/sb.md which doesn't exist
            # so store should be fresh (storyboard is None)
            assert store.storyboard is None
