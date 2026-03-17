"""Session management — single-process singleton replacing module globals."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException

from bee_video_editor.models_storyboard import Storyboard
from bee_video_editor.parsers.storyboard import parse_storyboard


@dataclass
class SessionStore:
    """Holds the current project state. One instance per process."""

    storyboard: Storyboard | None = None
    project_dir: Path | None = None
    assignments_path: Path | None = None
    storyboard_path: Path | None = None  # remembered for session persistence

    def require_project(self) -> tuple[Storyboard, Path]:
        """Return (storyboard, project_dir) or raise 404."""
        if self.storyboard is None or self.project_dir is None:
            raise HTTPException(404, "No project loaded")
        return self.storyboard, self.project_dir

    def load_project(self, storyboard_path: Path, project_dir: Path) -> Storyboard:
        """Parse storyboard, restore assignments, set as current session."""
        if not storyboard_path.exists():
            raise HTTPException(404, f"Storyboard not found: {storyboard_path}")
        if not project_dir.exists():
            raise HTTPException(400, f"Project directory not found: {project_dir}")

        self.project_dir = project_dir.resolve()
        self.storyboard_path = storyboard_path.resolve()
        self.assignments_path = self.project_dir / ".bee-video" / "assignments.json"
        self.storyboard = parse_storyboard(storyboard_path)

        saved = self._load_assignments()
        for seg in self.storyboard.segments:
            if seg.id in saved:
                seg.assigned_media = saved[seg.id]

        self._save_session()
        return self.storyboard

    def assign_media(
        self, segment_id: str, layer: str, index: int, media_path: str
    ) -> dict:
        """Assign media to segment layer, persist to sidecar JSON."""
        sb, _ = self.require_project()
        seg = next((s for s in sb.segments if s.id == segment_id), None)
        if seg is None:
            raise HTTPException(404, f"Segment not found: {segment_id}")

        key = f"{layer}:{index}"
        seg.assigned_media[key] = media_path

        assignments = self._load_assignments()
        assignments.setdefault(segment_id, {})[key] = media_path
        self._save_assignments(assignments)

        return {
            "status": "ok",
            "segment_id": segment_id,
            "key": key,
            "media_path": media_path,
        }

    def _save_session(self) -> None:
        """Persist session info for auto-reload on restart."""
        if not self.project_dir or not self.storyboard_path:
            return
        data = {
            "storyboard_path": str(self.storyboard_path),
            "project_dir": str(self.project_dir),
        }
        # Project-local copy
        session_file = self.project_dir / ".bee-video" / "session.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text(json.dumps(data, indent=2))
        # Global pointer so the server can find it on restart
        global_session = Path.home() / ".bee-video" / "last-session.json"
        global_session.parent.mkdir(parents=True, exist_ok=True)
        global_session.write_text(json.dumps(data, indent=2))

    def _load_assignments(self) -> dict:
        if self.assignments_path and self.assignments_path.exists():
            with open(self.assignments_path) as f:
                return json.load(f)
        return {}

    def _save_assignments(self, assignments: dict) -> None:
        if self.assignments_path:
            self.assignments_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.assignments_path, "w") as f:
                json.dump(assignments, f, indent=2)


# Module-level singleton + dependency function

def _try_restore() -> SessionStore:
    """Create SessionStore, attempting to restore the last session."""
    store = SessionStore()
    last_session = Path.home() / ".bee-video" / "last-session.json"
    if last_session.exists():
        try:
            data = json.loads(last_session.read_text())
            sb_path = Path(data["storyboard_path"])
            proj_dir = Path(data["project_dir"])
            if sb_path.exists() and proj_dir.exists():
                store.load_project(sb_path, proj_dir)
        except Exception:
            pass  # Failed to restore — start fresh
    return store


_session = _try_restore()


def get_session() -> SessionStore:
    """FastAPI dependency — returns the singleton SessionStore."""
    return _session
