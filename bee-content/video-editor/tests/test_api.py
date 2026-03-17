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


# ─── Bug-hunting tests ──────────────────────────────────────────────────────
# These test real edge cases and attack vectors, not just happy paths.


class TestUploadCategoryTraversal:
    """BUG: category param flows into project_dir / category unsanitized.
    An attacker passing category=../../evil creates dirs outside the project."""

    def test_upload_traversal_category_blocked(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post(
            "/api/media/upload?category=../../evil",
            files={"file": ("test.mp4", b"\x00" * 50, "video/mp4")},
        )
        assert r.status_code == 400
        # The file must not have been written anywhere
        assert not (proj_dir / "../../evil" / "test.mp4").exists()

    def test_upload_unknown_category_rejected(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post(
            "/api/media/upload?category=custom_stuff",
            files={"file": ("test.mp4", b"\x00" * 50, "video/mp4")},
        )
        assert r.status_code == 400


class TestServeSymlinkTraversal:
    """Symlinks inside the project pointing outside should be blocked."""

    def test_symlink_to_outside_blocked(self, loaded_project):
        client, _, proj_dir = loaded_project
        # Create a symlink inside project pointing to /etc/passwd
        link = proj_dir / "evil_link"
        try:
            link.symlink_to("/etc/passwd")
        except OSError:
            pytest.skip("Cannot create symlinks")

        r = client.get(f"/api/media/file?path={link}")
        assert r.status_code == 403, "Symlink traversal should be blocked"


class TestUnassignPreservesOtherAssignments:
    """Unassigning one layer must not corrupt other layers on the same segment."""

    def test_unassign_visual_preserves_audio(self, loaded_project):
        client, _, proj_dir = loaded_project

        # Assign both visual and audio
        client.put("/api/projects/assign", json={
            "segment_id": "seg_a", "layer": "visual",
            "media_path": "/media/video.mp4", "layer_index": 0,
        })
        client.put("/api/projects/assign", json={
            "segment_id": "seg_a", "layer": "audio",
            "media_path": "/media/narration.mp3", "layer_index": 0,
        })

        # Unassign visual only
        client.put("/api/projects/assign", json={
            "segment_id": "seg_a", "layer": "visual",
            "media_path": "", "layer_index": 0,
        })

        # Audio must survive
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == "seg_a")
        assert "visual:0" not in seg["assigned_media"]
        assert seg["assigned_media"]["audio:0"] == "/media/narration.mp3"

        # Disk must also have audio but not visual
        assignments_path = proj_dir.resolve() / ".bee-video" / "assignments.json"
        disk = json.loads(assignments_path.read_text())
        assert "visual:0" not in disk.get("seg_a", {})
        assert disk["seg_a"]["audio:0"] == "/media/narration.mp3"


class TestDownloadTaskPruning:
    """Verify completed download tasks are actually pruned at the boundary."""

    def test_prune_keeps_max_completed(self):
        from bee_video_editor.api.routes.media import (
            _MAX_COMPLETED_TASKS,
            _download_tasks,
            _prune_download_tasks,
        )

        _download_tasks.clear()

        # Fill with 25 completed tasks
        for i in range(25):
            _download_tasks[f"task-{i}"] = {
                "running": False,
                "finished_at": float(i),  # older tasks have lower timestamps
                "return_code": 0,
                "output_lines": [],
            }
        # Add 2 running tasks (should never be pruned)
        _download_tasks["running-1"] = {"running": True, "output_lines": [], "return_code": None}
        _download_tasks["running-2"] = {"running": True, "output_lines": [], "return_code": None}

        _prune_download_tasks()

        # Should keep 20 completed + 2 running = 22 total
        completed = [t for t in _download_tasks.values() if not t.get("running")]
        running = [t for t in _download_tasks.values() if t.get("running")]
        assert len(completed) == _MAX_COMPLETED_TASKS
        assert len(running) == 2

        # Oldest should be gone (task-0 through task-4)
        assert "task-0" not in _download_tasks
        assert "task-4" not in _download_tasks
        # Newest should survive
        assert "task-24" in _download_tasks

        _download_tasks.clear()


class TestPreviewReadsFromSession:
    """The preview endpoint should use in-memory assignments, not just disk.
    BUG: It reads from assignments.json directly, bypassing session state."""

    def test_preview_sees_in_memory_assignment(self, loaded_project):
        client, session, proj_dir = loaded_project

        # Create a real media file so the preview endpoint won't 404 on the file
        media_file = proj_dir / "footage" / "clip.mp4"
        media_file.parent.mkdir(parents=True, exist_ok=True)
        media_file.write_bytes(b"\x00" * 100)

        # Assign via API (writes to both memory and disk)
        client.put("/api/projects/assign", json={
            "segment_id": "seg_a", "layer": "visual",
            "media_path": str(media_file), "layer_index": 0,
        })

        # Verify in-memory state has it
        seg = next(s for s in session.storyboard.segments if s.id == "seg_a")
        assert seg.assigned_media.get("visual:0") == str(media_file)

        # Now corrupt the disk file to test which source the preview endpoint reads
        assignments_path = proj_dir.resolve() / ".bee-video" / "assignments.json"
        assignments_path.write_text("{}")  # wipe disk

        # Preview should still work because session has the assignment in memory
        # If this fails with 400 "No media assigned", the endpoint reads from disk
        with patch("bee_video_editor.services.production.generate_preview") as mock_gen:
            mock_gen.return_value = proj_dir / "output" / "previews" / "seg_a.mp4"
            r = client.post("/api/production/preview/seg_a")

        # This assertion exposes the bug: endpoint reads disk, not memory
        assert r.status_code != 400, \
            "Preview endpoint reads assignments.json from disk instead of session memory"


class TestUploadFilenameEdgeCases:
    """Edge cases in filename sanitization."""

    def test_upload_dotdot_filename_rejected(self, loaded_project):
        """Filename '..' should be rejected (starts with '.')."""
        client, _, _ = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": ("..", b"data", "application/octet-stream")},
        )
        assert r.status_code == 400

    def test_upload_dot_filename_rejected(self, loaded_project):
        """Filename '.' resolves to empty name, should be rejected."""
        client, _, _ = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": (".", b"data", "application/octet-stream")},
        )
        assert r.status_code == 400

    def test_upload_nested_traversal_sanitized(self, loaded_project):
        """Filename 'foo/../../bar.txt' should be stripped to 'bar.txt'."""
        client, _, proj_dir = loaded_project
        r = client.post(
            "/api/media/upload?category=footage",
            files={"file": ("foo/../../bar.txt", b"data", "text/plain")},
        )
        assert r.status_code == 200
        assert r.json()["name"] == "bar.txt"
        assert (proj_dir / "footage" / "bar.txt").exists()


class TestReorderWithStaleIds:
    """Reordering with IDs that don't exist in the storyboard.
    The server saves whatever you send — verify reload handles it gracefully."""

    def test_reorder_with_unknown_ids_then_reload(self, project_env):
        client, session, proj_dir, sb_path = project_env

        seg_a = _make_segment("seg_a", "A")
        seg_b = _make_segment("seg_b", "B")
        sb = _make_storyboard([seg_a, seg_b])

        with patch("bee_video_editor.api.session.parse_storyboard", return_value=sb):
            session.load_project(sb_path, proj_dir)

        # Save order with a nonexistent ID
        client.put("/api/projects/reorder", json={
            "segment_order": ["seg_b", "GHOST", "seg_a"],
        })

        # Reload — should not crash, should skip unknown ID
        with patch("bee_video_editor.api.session.parse_storyboard", return_value=sb):
            r = client.post("/api/projects/load", json={
                "storyboard_path": str(sb_path),
                "project_dir": str(proj_dir),
            })
        assert r.status_code == 200
        ids = [s["id"] for s in r.json()["segments"]]
        assert "GHOST" not in ids
        # seg_b should come before seg_a (the valid reorder)
        assert ids.index("seg_b") < ids.index("seg_a")


# ─── v0.6.0 feature tests ───────────────────────────────────────────────────


class TestBatchGraphics:
    def test_batch_graphics_from_config(self, loaded_project):
        client, _, proj_dir = loaded_project
        config = {
            "graphics": [
                {"type": "lower_third", "name": "Test", "role": "Witness"},
                {"type": "black_frame"},
            ]
        }
        config_path = proj_dir / "graphics.json"
        config_path.write_text(json.dumps(config))

        with patch("bee_video_editor.services.batch_graphics.gfx") as mock_gfx:
            mock_gfx.lower_third.return_value = Path("out.png")
            mock_gfx.black_frame.return_value = Path("out.png")
            r = client.post("/api/production/graphics-batch", json={
                "config_path": str(config_path),
            })

        assert r.status_code == 200
        assert r.json()["count"] == 2

    def test_batch_graphics_missing_config_404(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/graphics-batch", json={
            "config_path": "/nonexistent/config.json",
        })
        assert r.status_code == 404

    def test_batch_graphics_invalid_type_400(self, loaded_project):
        client, _, proj_dir = loaded_project
        config = {"graphics": [{"type": "nonexistent"}]}
        config_path = proj_dir / "graphics.json"
        config_path.write_text(json.dumps(config))

        r = client.post("/api/production/graphics-batch", json={
            "config_path": str(config_path),
        })
        assert r.status_code == 400


class TestVoiceLock:
    def test_save_voice_config(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.put("/api/production/voice-lock", json={
            "engine": "elevenlabs",
            "voice": "Daniel",
            "speed": 0.9,
        })
        assert r.status_code == 200
        config_path = proj_dir.resolve() / ".bee-video" / "voice.json"
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["engine"] == "elevenlabs"

    def test_get_voice_config(self, loaded_project):
        client, session, _ = loaded_project
        session.save_voice_config("openai", "nova", 1.0)
        r = client.get("/api/production/voice-lock")
        assert r.status_code == 200
        assert r.json()["engine"] == "openai"

    def test_get_voice_config_empty(self, loaded_project):
        client, _, _ = loaded_project
        r = client.get("/api/production/voice-lock")
        assert r.status_code == 200
        assert r.json() == {}


class TestRoughCut:
    def test_rough_cut_no_media_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/production/rough-cut")
        assert r.status_code == 400

    def test_rough_cut_with_media(self, loaded_project):
        client, session, proj_dir = loaded_project
        clip = proj_dir / "footage" / "clip.mp4"
        clip.parent.mkdir(parents=True, exist_ok=True)
        clip.write_bytes(b"\x00" * 100)
        session.assign_media("seg_a", "visual", 0, str(clip))

        with patch("bee_video_editor.services.production.normalize_format") as mock_norm, \
             patch("bee_video_editor.services.production.concat_segments") as mock_concat:
            mock_norm.side_effect = lambda i, o, **kw: Path(o)
            output = proj_dir / "output" / "rough" / "rough_cut.mp4"
            mock_concat.return_value = output
            r = client.post("/api/production/rough-cut")

        assert r.status_code == 200
        assert "rough_cut" in r.json()["output"]


# ─── Stock footage + video generation tests ──────────────────────────────────


class TestStockSearch:
    def test_search_returns_results(self, loaded_project):
        client, _, _ = loaded_project
        from bee_video_editor.processors.stock import PexelsResult
        mock_result = PexelsResult(
            id=123, url="https://pexels.com/123", duration=10,
            width=1920, height=1080,
            hd_url="https://cdn/123.mp4", sd_url=None,
        )

        with patch("bee_video_editor.processors.stock.search_pexels", return_value=[mock_result]):
            r = client.post("/api/media/stock/search", json={
                "query": "aerial farm",
                "count": 3,
            })

        assert r.status_code == 200
        assert r.json()["count"] == 1
        assert r.json()["results"][0]["id"] == 123

    def test_search_no_api_key_400(self, loaded_project):
        client, _, _ = loaded_project
        with patch("bee_video_editor.processors.stock.search_pexels",
                    side_effect=ValueError("No API key")):
            r = client.post("/api/media/stock/search", json={"query": "test"})

        assert r.status_code == 400


class TestStockDownload:
    def test_download_clip(self, loaded_project):
        client, _, proj_dir = loaded_project
        with patch("bee_video_editor.processors.stock.download_stock_clip") as mock_dl:
            mock_dl.return_value = proj_dir / "stock" / "clip.mp4"
            r = client.post("/api/media/stock/download", json={
                "url": "https://cdn.pexels.com/clip.mp4",
                "filename": "clip.mp4",
            })

        assert r.status_code == 200
        assert r.json()["name"] == "clip.mp4"

    def test_download_traversal_filename_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/media/stock/download", json={
            "url": "https://cdn/clip.mp4",
            "filename": "../../evil.mp4",
        })
        assert r.status_code == 400

    def test_download_http_url_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/media/stock/download", json={
            "url": "http://internal-server/secret.mp4",
            "filename": "clip.mp4",
        })
        assert r.status_code == 400


class TestGenerateClip:
    def test_generate_with_stub(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post("/api/media/generate-clip", json={
            "prompt": "aerial shot of farm",
            "provider": "stub",
            "duration": 3.0,
        })

        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["provider"] == "stub"

    def test_generate_unknown_provider_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/media/generate-clip", json={
            "prompt": "test",
            "provider": "nonexistent",
        })
        assert r.status_code == 400
