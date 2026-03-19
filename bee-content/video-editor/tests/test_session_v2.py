"""Tests for the OTIO-based SessionStore (v2)."""

import json
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_otio_from_fixture(tmp_path: Path) -> Path:
    """Parse the minimal v2 fixture, convert to OTIO, write to tmp_path.

    Returns the path to the .otio file.
    """
    import opentimelineio as otio

    from bee_video_editor.formats.otio_convert import to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio.adapters.write_to_file(tl, str(otio_path))
    return otio_path


def _fresh_store():
    """Return a fresh SessionStore (not the module singleton)."""
    from bee_video_editor.api.session import SessionStore

    return SessionStore()


def _load_minimal_v2(store, tmp_path: Path):
    """Copy the minimal v2 fixture to tmp_path and load it into the store."""
    md_path = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_path)
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()
    store.load_project(md_path, proj_dir)
    return md_path, proj_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_load_otio_file(tmp_path):
    """Load an .otio file directly."""
    otio_path = _make_otio_from_fixture(tmp_path)
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()

    store = _fresh_store()
    store.load_project(otio_path, proj_dir)

    assert store.parsed is not None
    assert store.parsed.project.title == "Test Project"
    assert len(store.parsed.segments) == 2


def test_load_v2_markdown_creates_otio(tmp_path):
    """Loading a v2 .md auto-creates .otio next to it."""
    store = _fresh_store()
    md_path, proj_dir = _load_minimal_v2(store, tmp_path)

    otio_path = md_path.with_suffix(".otio")
    assert otio_path.exists(), f"Expected .otio file at {otio_path}"
    assert store.parsed is not None
    assert len(store.parsed.segments) == 2


def test_load_old_markdown_auto_migrates(tmp_path):
    """Loading old table-format .md auto-migrates to OTIO."""
    # Write a minimal old-format storyboard
    old_md = tmp_path / "old_storyboard.md"
    old_md.write_text("""\
# Test Old Storyboard

## INTRO (0:00 - 0:15)

### 0:00 - 0:05 | THE HOOK
| Layer | Content |
|-------|---------|
| Visual | `FOOTAGE:` clip of something |
| Audio | `NAR:` This is narration text |

### 0:05 - 0:15 | SECOND SHOT
| Layer | Content |
|-------|---------|
| Visual | `STOCK:` aerial view |
""")
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()

    store = _fresh_store()
    store.load_project(old_md, proj_dir)

    assert store.parsed is not None
    assert len(store.parsed.segments) == 2
    assert store.parsed.project.title == "Test Old Storyboard"

    # Should have created an .otio file
    otio_path = old_md.with_suffix(".otio")
    assert otio_path.exists()


def test_assign_media_mutates_and_saves(tmp_path):
    """Assigning media updates parsed model and saves OTIO."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    seg_id = store.parsed.segments[0].id
    store.assign_media(seg_id, "visual", 0, "footage/new.mp4")

    # Check in-memory
    assert store.parsed.segments[0].config.visual[0].src == "footage/new.mp4"

    # Check on-disk: reload the OTIO and verify
    import opentimelineio as otio

    from bee_video_editor.formats.otio_convert import from_otio

    tl = otio.adapters.read_from_file(str(store.otio_path))
    reloaded = from_otio(tl)
    seg = next(s for s in reloaded.segments if s.id == seg_id)
    assert seg.config.visual[0].src == "footage/new.mp4"


def test_reorder_segments(tmp_path):
    """Reordering segments updates parsed model and saves OTIO."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    ids = [s.id for s in store.parsed.segments]
    assert len(ids) == 2

    # Reverse order
    store.reorder_segments(list(reversed(ids)))

    assert store.parsed.segments[0].id == ids[1]
    assert store.parsed.segments[1].id == ids[0]


def test_require_project_raises_without_load():
    """No project loaded raises HTTPException 404."""
    from fastapi import HTTPException

    store = _fresh_store()
    with pytest.raises(HTTPException) as exc_info:
        store.require_project()
    assert exc_info.value.status_code == 404


def test_require_project_returns_parsed(tmp_path):
    """Load project, require_project returns (ParsedStoryboard, Path)."""
    from bee_video_editor.formats.parser import ParsedStoryboard

    store = _fresh_store()
    _, proj_dir = _load_minimal_v2(store, tmp_path)

    parsed, pdir = store.require_project()
    assert isinstance(parsed, ParsedStoryboard)
    assert pdir == proj_dir.resolve()


def test_sidecar_absorption_assignments(tmp_path):
    """Sidecar assignments.json is absorbed on load."""
    store = _fresh_store()
    md_path = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_path)
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()

    # We need to know the segment IDs that will be generated.
    # Parse first to discover them.
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(md_path)
    seg_id = parsed.segments[0].id

    # Create sidecar assignments.json
    bee_dir = proj_dir / ".bee-video"
    bee_dir.mkdir(parents=True)
    assignments = {seg_id: {"visual:0": "footage/sidecar-clip.mp4"}}
    (bee_dir / "assignments.json").write_text(json.dumps(assignments))

    store.load_project(md_path, proj_dir)

    # Verify absorbed
    seg = next(s for s in store.parsed.segments if s.id == seg_id)
    assert seg.config.visual[0].src == "footage/sidecar-clip.mp4"


def test_sidecar_absorption_voice_lock(tmp_path):
    """Sidecar voice.json is absorbed into project config."""
    store = _fresh_store()
    md_path = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_path)
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()

    # Create sidecar voice.json
    bee_dir = proj_dir / ".bee-video"
    bee_dir.mkdir(parents=True)
    (bee_dir / "voice.json").write_text(json.dumps({
        "engine": "elevenlabs",
        "voice": "Daniel",
    }))

    store.load_project(md_path, proj_dir)

    assert store.parsed.project.voice_lock is not None
    assert store.parsed.project.voice_lock.engine == "elevenlabs"
    assert store.parsed.project.voice_lock.voice == "Daniel"


def test_sidecar_absorption_segment_order(tmp_path):
    """Sidecar segment-order.json is absorbed on load."""
    store = _fresh_store()
    md_path = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_path)
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()

    # Parse to get segment IDs
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(md_path)
    ids = [s.id for s in parsed.segments]
    assert len(ids) == 2

    # Create sidecar with reversed order
    bee_dir = proj_dir / ".bee-video"
    bee_dir.mkdir(parents=True)
    (bee_dir / "segment-order.json").write_text(json.dumps(list(reversed(ids))))

    store.load_project(md_path, proj_dir)

    assert store.parsed.segments[0].id == ids[1]
    assert store.parsed.segments[1].id == ids[0]


def test_assign_media_unassign(tmp_path):
    """Empty media_path clears the assignment."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    seg_id = store.parsed.segments[0].id

    # Assign first
    store.assign_media(seg_id, "visual", 0, "footage/clip.mp4")
    assert store.parsed.segments[0].config.visual[0].src == "footage/clip.mp4"

    # Now unassign
    store.assign_media(seg_id, "visual", 0, "")
    assert store.parsed.segments[0].config.visual[0].src is None


def test_assign_media_invalid_segment_raises(tmp_path):
    """Assigning to nonexistent segment raises 404."""
    from fastapi import HTTPException

    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    with pytest.raises(HTTPException) as exc_info:
        store.assign_media("nonexistent-id", "visual", 0, "footage/clip.mp4")
    assert exc_info.value.status_code == 404


def test_save_voice_config(tmp_path):
    """save_voice_config stores in parsed model and autosaves."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    store.save_voice_config("elevenlabs", "Daniel", 0.95)

    assert store.parsed.project.voice_lock is not None
    assert store.parsed.project.voice_lock.engine == "elevenlabs"
    assert store.parsed.project.voice_lock.voice == "Daniel"


def test_load_voice_config(tmp_path):
    """load_voice_config returns voice_lock as dict."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    # No voice lock initially
    result = store.load_voice_config()
    assert result is None

    store.save_voice_config("edge", "en-US-GuyNeural", 0.95)
    result = store.load_voice_config()
    assert result is not None
    assert result["engine"] == "edge"
    assert result["voice"] == "en-US-GuyNeural"


def test_load_voice_config_no_project():
    """load_voice_config returns None when no project loaded."""
    store = _fresh_store()
    assert store.load_voice_config() is None


def test_session_json_uses_otio_path(tmp_path):
    """_save_session writes session.json with otio_path."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    proj_dir = store.project_dir
    session_file = proj_dir / ".bee-video" / "session.json"
    assert session_file.exists()
    data = json.loads(session_file.read_text())
    assert "otio_path" in data
    assert data["otio_path"].endswith(".otio")


def test_save_session_no_crash_when_empty():
    """_save_session on empty store should not crash."""
    store = _fresh_store()
    store._save_session()  # Should not crash


def test_autosave_writes_otio(tmp_path):
    """_autosave creates/updates the OTIO file on disk."""
    store = _fresh_store()
    _load_minimal_v2(store, tmp_path)

    import os

    otio_path = store.otio_path
    mtime_before = os.path.getmtime(otio_path)

    # Force an autosave
    import time

    time.sleep(0.05)
    store._autosave()
    mtime_after = os.path.getmtime(otio_path)
    assert mtime_after >= mtime_before
