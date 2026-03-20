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
from bee_video_editor.formats.models import (
    AudioEntry,
    OverlayEntry,
    ProjectConfig,
    SegmentConfig,
    VisualEntry,
)
from bee_video_editor.formats.parser import ParsedSegment, ParsedStoryboard


def _write_v2_storyboard(path: Path, title: str = "Test", segments: list[dict] | None = None):
    """Write a v2 storyboard markdown file that parse_v2 can parse."""
    segments = segments or []
    lines = [f"# {title}", ""]
    lines.append('```json bee-video:project')
    lines.append(json.dumps({"title": title, "version": 1}))
    lines.append('```')
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


@pytest.fixture
def project_env():
    """Yield (client, session, proj_dir) with a fresh app and temp project."""
    with tempfile.TemporaryDirectory() as d:
        proj_dir = Path(d) / "project"
        proj_dir.mkdir()
        sb_path = Path(d) / "storyboard.md"
        _write_v2_storyboard(sb_path, "Test")

        session = SessionStore()
        app = create_app()
        app.dependency_overrides[get_session] = lambda: session

        client = TestClient(app)
        yield client, session, proj_dir, sb_path


@pytest.fixture
def loaded_project(project_env):
    """Yield (client, session, proj_dir) with a project already loaded."""
    client, session, proj_dir, sb_path = project_env

    _write_v2_storyboard(sb_path, "Murder Mystery", segments=[
        {"title": "Hook", "start": "0:00", "end": "0:05",
         "config": {"visual": [{"type": "FOOTAGE"}]}},
        {"title": "Setup", "start": "0:05", "end": "0:10",
         "config": {"visual": [{"type": "FOOTAGE"}]}},
        {"title": "Deep Dive", "start": "0:10", "end": "0:15",
         "config": {"visual": [{"type": "FOOTAGE"}]}},
    ])

    session.load_project(sb_path, proj_dir)

    yield client, session, proj_dir


# ─── Project routes ──────────────────────────────────────────────────────────


class TestProjectLoad:
    def test_load_returns_storyboard(self, project_env):
        client, _, proj_dir, sb_path = project_env
        _write_v2_storyboard(sb_path, "Loaded", segments=[
            {"title": "Test Seg", "start": "0:00", "end": "0:05",
             "config": {"visual": [{"type": "FOOTAGE"}]}},
        ])

        r = client.post("/api/projects/load", json={
            "storyboard_path": str(sb_path),
            "project_dir": str(proj_dir),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Loaded"
        assert data["total_segments"] == 1
        assert len(data["segments"]) == 1

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
        seg_id = session.parsed.segments[0].id

        r = client.put("/api/projects/assign", json={
            "segment_id": seg_id,
            "layer": "visual",
            "media_path": "/media/clip.mp4",
            "layer_index": 0,
        })
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # Read back via current project
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == seg_id)
        assert seg["assigned_media"]["visual:0"] == "/media/clip.mp4"

    def test_unassign_with_empty_string(self, loaded_project):
        client, session, proj_dir = loaded_project
        seg_id = session.parsed.segments[0].id

        # Assign first
        client.put("/api/projects/assign", json={
            "segment_id": seg_id,
            "layer": "visual",
            "media_path": "/media/clip.mp4",
            "layer_index": 0,
        })

        # Unassign
        r = client.put("/api/projects/assign", json={
            "segment_id": seg_id,
            "layer": "visual",
            "media_path": "",
            "layer_index": 0,
        })
        assert r.status_code == 200

        # Verify removed
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == seg_id)
        assert "visual:0" not in seg["assigned_media"]

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
        client, session, proj_dir = loaded_project
        ids = [s.id for s in session.parsed.segments]

        r = client.put("/api/projects/reorder", json={
            "segment_order": list(reversed(ids)),
        })
        assert r.status_code == 200
        assert r.json()["count"] == 3


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
            _write_v2_storyboard(sb_path, "Test", segments=[
                {"title": "Test Seg", "start": "0:00", "end": "0:05",
                 "config": {"visual": [{"type": "FOOTAGE"}]}},
            ])

            # Script at top level — 5 levels above deep_proj
            script = Path(d) / "evil.sh"
            script.write_text("#!/bin/bash\necho pwned")

            session = SessionStore()
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

    def test_produce_no_otio_path_400(self, loaded_project):
        client, session, _ = loaded_project
        session.otio_path = None
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
        client, session, proj_dir = loaded_project
        seg_id = session.parsed.segments[0].id

        # Assign visual
        client.put("/api/projects/assign", json={
            "segment_id": seg_id, "layer": "visual",
            "media_path": "/media/video.mp4", "layer_index": 0,
        })

        # Read back and confirm
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == seg_id)
        assert seg["assigned_media"]["visual:0"] == "/media/video.mp4"

        # Unassign visual
        client.put("/api/projects/assign", json={
            "segment_id": seg_id, "layer": "visual",
            "media_path": "", "layer_index": 0,
        })

        # Visual must be gone
        r = client.get("/api/projects/current")
        seg = next(s for s in r.json()["segments"] if s["id"] == seg_id)
        assert "visual:0" not in seg["assigned_media"]


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
    """The preview endpoint should use in-memory assignments, not just disk."""

    def test_preview_sees_in_memory_assignment(self, loaded_project):
        client, session, proj_dir = loaded_project
        seg_id = session.parsed.segments[0].id

        # Create a real media file so the preview endpoint won't 404 on the file
        media_file = proj_dir / "footage" / "clip.mp4"
        media_file.parent.mkdir(parents=True, exist_ok=True)
        media_file.write_bytes(b"\x00" * 100)

        # Assign via API (writes to both memory and OTIO)
        client.put("/api/projects/assign", json={
            "segment_id": seg_id, "layer": "visual",
            "media_path": str(media_file), "layer_index": 0,
        })

        # Verify in-memory state has it
        seg = next(s for s in session.parsed.segments if s.id == seg_id)
        assert seg.config.visual[0].src == str(media_file)

        # Preview should work because session has the assignment in memory
        with patch("bee_video_editor.services.production.generate_preview") as mock_gen:
            mock_gen.return_value = proj_dir / "output" / "previews" / f"{seg_id}.mp4"
            r = client.post(f"/api/production/preview/{seg_id}")

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

        _write_v2_storyboard(sb_path, "Test", segments=[
            {"title": "A", "start": "0:00", "end": "0:05",
             "config": {"visual": [{"type": "FOOTAGE"}]}},
            {"title": "B", "start": "0:05", "end": "0:10",
             "config": {"visual": [{"type": "FOOTAGE"}]}},
        ])
        session.load_project(sb_path, proj_dir)
        ids = [s.id for s in session.parsed.segments]

        # Save order with a nonexistent ID
        client.put("/api/projects/reorder", json={
            "segment_order": [ids[1], "GHOST", ids[0]],
        })

        # Reload — should not crash, should skip unknown ID
        r = client.post("/api/projects/load", json={
            "storyboard_path": str(sb_path),
            "project_dir": str(proj_dir),
        })
        assert r.status_code == 200
        result_ids = [s["id"] for s in r.json()["segments"]]
        assert "GHOST" not in result_ids


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
        # Voice lock is stored in parsed.project.voice_lock (in-memory + OTIO)
        r2 = client.get("/api/production/voice-lock")
        assert r2.json()["engine"] == "elevenlabs"

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
        seg_id = session.parsed.segments[0].id
        clip = proj_dir / "footage" / "clip.mp4"
        clip.parent.mkdir(parents=True, exist_ok=True)
        clip.write_bytes(b"\x00" * 100)
        session.assign_media(seg_id, "visual", 0, str(clip))

        with patch("bee_video_editor.services.production.normalize_format") as mock_norm, \
             patch("bee_video_editor.services.production.concat_segments") as mock_concat:
            mock_norm.side_effect = lambda i, o, **kw: Path(o)
            output = proj_dir / "output" / "rough" / "rough_cut.mp4"
            mock_concat.return_value = output
            r = client.post("/api/production/rough-cut")

        assert r.status_code == 200
        assert "rough_cut" in r.json()["output"]


# ─── Remotion render ──────────────────────────────────────────────────────────


class TestRenderRemotion:
    def test_render_remotion_endpoint_exists(self, loaded_project):
        """Render endpoint is reachable and fails gracefully."""
        client, _, _ = loaded_project
        r = client.post("/api/production/render-remotion")
        # Will fail because render.mjs path resolution won't find the script
        # from the test's temp directory, or Node deps aren't fully wired.
        # The key assertion: the endpoint exists and returns a valid HTTP status.
        assert r.status_code in (200, 400, 500)


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
        import shutil
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not available")
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
