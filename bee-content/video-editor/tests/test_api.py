"""API smoke tests — exercise FastAPI routes via TestClient."""

import json
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from bee_video_editor.api.server import create_app
from bee_video_editor.api.session import SessionStore, get_session
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _make_segment(id: str, title: str, section: str = "INTRO", **kwargs) -> StoryboardSegment:
    defaults = dict(
        start="0:00", end="0:05", section_time="0:00 - 2:30", subsection="",
        visual=[], audio=[], overlay=[], music=[], source=[], transition=[],
        assigned_media={},
    )
    defaults.update(kwargs)
    return StoryboardSegment(id=id, title=title, section=section, **defaults)


def _make_storyboard(segments=None, title="Test") -> Storyboard:
    return Storyboard(
        title=title,
        segments=segments or [],
        stock_footage=[],
        photos_needed=[],
        maps_needed=[],
        production_rules=ProductionRules(),
    )


@pytest.fixture
def project_env():
    """Yield (client, session, proj_dir) with a fresh app and temp project."""
    with tempfile.TemporaryDirectory() as d:
        proj_dir = Path(d) / "project"
        proj_dir.mkdir()
        sb_path = Path(d) / "storyboard.md"
        sb_path.write_text("# Test\n")

        session = SessionStore()
        app = create_app()
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app)
        yield client, session, proj_dir, sb_path


@pytest.fixture
def loaded_project(project_env):
    """Yield (client, session, proj_dir) with a project already loaded."""
    client, session, proj_dir, sb_path = project_env

    seg_a = _make_segment("seg_a", "Hook", section="COLD OPEN")
    seg_b = _make_segment("seg_b", "Setup", section="COLD OPEN")
    seg_c = _make_segment("seg_c", "Deep Dive", section="INVESTIGATION")
    sb = _make_storyboard([seg_a, seg_b, seg_c], title="Murder Mystery")

    with patch("bee_video_editor.api.session.parse_storyboard", return_value=sb):
        session.load_project(sb_path, proj_dir)

    yield client, session, proj_dir


# ─── Project routes ──────────────────────────────────────────────────────────


class TestProjectLoad:
    def test_load_returns_storyboard(self, project_env):
        client, _, proj_dir, sb_path = project_env
        sb = _make_storyboard([_make_segment("s1", "Test Seg")], title="Loaded")

        with patch("bee_video_editor.api.session.parse_storyboard", return_value=sb):
            r = client.post("/api/projects/load", json={
                "storyboard_path": str(sb_path),
                "project_dir": str(proj_dir),
            })
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Loaded"
        assert data["total_segments"] == 1
        assert len(data["segments"]) == 1
        assert data["segments"][0]["id"] == "s1"

    def test_load_nonexistent_storyboard_404(self, project_env):
        client, _, proj_dir, _ = project_env
        r = client.post("/api/projects/load", json={
            "storyboard_path": "/nonexistent/sb.md",
            "project_dir": str(proj_dir),
        })
        assert r.status_code == 404

    def test_current_before_load_404(self, project_env):
        client, _, _, _ = project_env
        r = client.get("/api/projects/current")
        assert r.status_code == 404


class TestProjectCurrent:
    def test_current_returns_loaded_project(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/projects/current")
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Murder Mystery"
        assert data["total_segments"] == 3


# ─── Assign / Unassign ──────────────────────────────────────────────────────


class TestAssignMedia:
    def test_assign_and_read_back(self, loaded_project):
        client, session, proj_dir = loaded_project

        r = client.put("/api/projects/assign", json={
            "segment_id": "seg_a",
            "layer": "visual",
            "media_path": "/media/clip.mp4",
            "layer_index": 0,
        })
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # Read back via current project
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == "seg_a")
        assert seg["assigned_media"]["visual:0"] == "/media/clip.mp4"

    def test_unassign_with_empty_string(self, loaded_project):
        client, session, proj_dir = loaded_project

        # Assign first
        client.put("/api/projects/assign", json={
            "segment_id": "seg_a",
            "layer": "visual",
            "media_path": "/media/clip.mp4",
            "layer_index": 0,
        })

        # Unassign
        r = client.put("/api/projects/assign", json={
            "segment_id": "seg_a",
            "layer": "visual",
            "media_path": "",
            "layer_index": 0,
        })
        assert r.status_code == 200

        # Verify removed
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == "seg_a")
        assert "visual:0" not in seg["assigned_media"]

        # Verify removed from assignments.json on disk
        assignments_path = proj_dir.resolve() / ".bee-video" / "assignments.json"
        data = json.loads(assignments_path.read_text())
        assert "seg_a" not in data

    def test_assign_unknown_segment_404(self, loaded_project):
        client, _, _ = loaded_project
        r = client.put("/api/projects/assign", json={
            "segment_id": "nonexistent",
            "layer": "visual",
            "media_path": "/media/clip.mp4",
            "layer_index": 0,
        })
        assert r.status_code == 404


# ─── Reorder ─────────────────────────────────────────────────────────────────


class TestReorderSegments:
    def test_reorder_persists(self, loaded_project):
        client, _, proj_dir = loaded_project

        r = client.put("/api/projects/reorder", json={
            "segment_order": ["seg_c", "seg_a", "seg_b"],
        })
        assert r.status_code == 200
        assert r.json()["count"] == 3

        order_file = proj_dir.resolve() / ".bee-video" / "segment-order.json"
        assert order_file.exists()
        assert json.loads(order_file.read_text()) == ["seg_c", "seg_a", "seg_b"]


# ─── Media routes ────────────────────────────────────────────────────────────


class TestMediaList:
    def test_list_empty_project(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/media")
        assert r.status_code == 200
        data = r.json()
        assert data["files"] == []
        assert data["categories"] == {}

    def test_list_with_files(self, loaded_project):
        client, _, proj_dir = loaded_project
        footage_dir = proj_dir / "footage"
        footage_dir.mkdir()
        (footage_dir / "clip.mp4").write_bytes(b"\x00" * 100)

        r = client.get("/api/media")
        data = r.json()
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "clip.mp4"
        assert data["files"][0]["category"] == "footage"
        assert data["categories"]["footage"] == 1


class TestMediaUpload:
    def test_upload_basic(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": ("test.mp4", b"\x00" * 50, "video/mp4")},
        )
        assert r.status_code == 200
        assert r.json()["name"] == "test.mp4"
        assert (proj_dir / "footage" / "test.mp4").exists()

    def test_upload_path_traversal_rejected(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": ("../../etc/passwd", b"malicious", "text/plain")},
        )
        # Should sanitize the filename, not traverse
        assert r.status_code == 200
        assert r.json()["name"] == "passwd"
        # File should be in footage dir, not at ../../etc/
        assert (proj_dir / "footage" / "passwd").exists()
        assert not (proj_dir.parent / "etc" / "passwd").exists()

    def test_upload_dotfile_rejected(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": (".hidden", b"data", "application/octet-stream")},
        )
        assert r.status_code == 400


class TestMediaServe:
    def test_serve_file_in_project(self, loaded_project):
        client, _, proj_dir = loaded_project
        test_file = proj_dir / "footage" / "clip.mp4"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_bytes(b"\x00\x00\x00\x20ftyp")

        r = client.get(f"/api/media/file?path={test_file}")
        assert r.status_code == 200

    def test_serve_file_outside_project_403(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/media/file?path=/etc/passwd")
        assert r.status_code == 403

    def test_serve_missing_file_404(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.get(f"/api/media/file?path={proj_dir}/nonexistent.mp4")
        assert r.status_code == 404


# ─── Script execution security ───────────────────────────────────────────────


class TestScriptExecution:
    def test_script_outside_project_tree_403(self, loaded_project):
        client, _, proj_dir = loaded_project
        # Project is at /tmp/tmpXXX/project. The check allows 3 parent levels,
        # which covers /tmp/tmpXXX, /tmp, and /. To test rejection, nest the
        # project 5 levels deep and put the script at the top.
        with tempfile.TemporaryDirectory() as d:
            deep_proj = Path(d) / "a" / "b" / "c" / "d" / "project"
            deep_proj.mkdir(parents=True)
            sb_path = Path(d) / "a" / "b" / "c" / "d" / "sb.md"
            sb_path.write_text("# Test\n")

            # Script at top level — 5 levels above deep_proj
            script = Path(d) / "evil.sh"
            script.write_text("#!/bin/bash\necho pwned")

            session = SessionStore()
            sb = _make_storyboard([_make_segment("s1", "Test")])
            with patch("bee_video_editor.api.session.parse_storyboard", return_value=sb):
                session.load_project(sb_path, deep_proj)

            app = create_app()
            app.dependency_overrides[get_session] = lambda: session
            deep_client = TestClient(app)

            r = deep_client.post("/api/media/download/run-script", json={
                "script_path": str(script),
            })
            assert r.status_code == 403

    def test_script_in_project_starts(self, loaded_project):
        client, _, proj_dir = loaded_project
        script = proj_dir / "download.sh"
        script.write_text("#!/bin/bash\necho done")
        script.chmod(0o755)

        r = client.post("/api/media/download/run-script", json={
            "script_path": str(script),
        })
        assert r.status_code == 200
        assert r.json()["status"] == "started"

    def test_non_sh_script_rejected(self, loaded_project):
        client, _, proj_dir = loaded_project
        script = proj_dir / "download.py"
        script.write_text("print('hi')")

        r = client.post("/api/media/download/run-script", json={
            "script_path": str(script),
        })
        assert r.status_code == 400


# ─── Production routes ───────────────────────────────────────────────────────


class TestProductionStatus:
    def test_status_returns_counts(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/production/status")
        assert r.status_code == 200
        data = r.json()
        assert data["phase"] == "loaded"
        assert data["segments_total"] == 3
        assert data["segments_done"] == 0

    def test_status_without_project_404(self, project_env):
        client, _, _, _ = project_env
        r = client.get("/api/production/status")
        assert r.status_code == 404


class TestProductionInit:
    def test_init_creates_dirs(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post("/api/production/init")
        assert r.status_code == 200

        output_dir = proj_dir / "output"
        for subdir in ["segments", "normalized", "composited", "graphics", "narration", "final"]:
            assert (output_dir / subdir).is_dir()


class TestProductionEffects:
    def test_list_effects(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/production/effects")
        assert r.status_code == 200
        data = r.json()
        assert "color_presets" in data
        assert "transitions" in data
        assert "ken_burns" in data
        assert "dark_crime" in data["color_presets"]
        assert len(data["transitions"]) > 20


class TestProductionAssemble:
    def test_assemble_no_segments_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/assemble")
        assert r.status_code == 400

    def test_assemble_invalid_transition_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/assemble?transition=nonexistent")
        assert r.status_code == 400


class TestProductionNarration:
    def test_invalid_engine_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/narration", json={
            "tts_engine": "invalid_engine",
        })
        assert r.status_code == 400

    def test_narration_status_no_task(self, loaded_project):
        client, _, _ = loaded_project
        # Reset narration task state
        from bee_video_editor.api.routes import production
        production._narration_task = None

        r = client.get("/api/production/narration/status")
        assert r.status_code == 200
        data = r.json()
        assert data["running"] is False
        assert data["total"] == 0


class TestProductionProduce:
    def test_produce_invalid_engine_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/produce?tts_engine=invalid")
        assert r.status_code == 400

    def test_produce_no_storyboard_path_400(self, loaded_project):
        client, session, _ = loaded_project
        session.storyboard_path = None
        r = client.post("/api/production/produce")
        assert r.status_code == 400


class TestDownloadStatus:
    def test_status_empty(self, loaded_project):
        client, _, _ = loaded_project
        # Clear any existing tasks
        from bee_video_editor.api.routes import media
        media._download_tasks.clear()

        r = client.get("/api/media/download/status")
        assert r.status_code == 200
        assert r.json() == []


class TestDownloadTools:
    def test_tools_returns_dict(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/media/download/tools")
        assert r.status_code == 200
        data = r.json()
        assert "yt_dlp" in data
        assert "ffmpeg" in data


class TestCreateMediaDirs:
    def test_creates_dirs(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post("/api/media/download/create-dirs")
        assert r.status_code == 200
        assert (proj_dir / "footage").is_dir()
        assert (proj_dir / "music").is_dir()
