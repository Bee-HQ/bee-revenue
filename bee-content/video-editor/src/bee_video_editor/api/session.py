"""Session management — single-process singleton replacing module globals."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
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
        self.assignments_path = self.project_dir / ".bee-video" / "assignments.json"
        self.storyboard = parse_storyboard(storyboard_path)

        saved = self._load_assignments()
        for seg in self.storyboard.segments:
            if seg.id in saved:
                seg.assigned_media = saved[seg.id]

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
_session = SessionStore()


def get_session() -> SessionStore:
    """FastAPI dependency — returns the singleton SessionStore."""
    return _session
