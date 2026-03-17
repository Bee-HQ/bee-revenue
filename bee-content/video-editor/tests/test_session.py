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
