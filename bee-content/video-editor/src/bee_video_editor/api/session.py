"""Session management — OTIO-based singleton (v2).

Holds an OTIO Timeline + ParsedStoryboard instead of the old Storyboard model.
Autosaves to .otio on every mutation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import opentimelineio as otio
from fastapi import HTTPException

from bee_video_editor.formats.models import VoiceLock
from bee_video_editor.formats.otio_convert import from_otio, to_otio
from bee_video_editor.formats.parser import ParsedStoryboard, parse_v2


# Pattern to detect v2 JSON blocks in markdown
_V2_FENCE_RE = re.compile(r"```json\s+bee-video:")


@dataclass
class SessionStore:
    """Holds the current project state. One instance per process."""

    timeline: otio.schema.Timeline | None = None
    parsed: ParsedStoryboard | None = None
    otio_path: Path | None = None
    project_dir: Path | None = None

    # ── queries ──────────────────────────────────────────────────────

    def require_project(self) -> tuple[ParsedStoryboard, Path]:
        """Return (parsed, project_dir) or raise 404."""
        if self.parsed is None or self.project_dir is None:
            raise HTTPException(404, "No project loaded")
        return self.parsed, self.project_dir

    # ── load ─────────────────────────────────────────────────────────

    def load_project(self, path: Path, project_dir: Path) -> ParsedStoryboard:
        """Load a project from .otio or .md (v2 or old table format).

        After loading the primary file, absorbs any sidecar files
        (assignments.json, segment-order.json, voice.json) and autosaves.
        """
        if not path.exists():
            raise HTTPException(404, f"File not found: {path}")
        if not project_dir.exists():
            raise HTTPException(400, f"Project directory not found: {project_dir}")

        self.project_dir = project_dir.resolve()

        if path.suffix == ".otio":
            self._load_otio(path)
        elif path.suffix == ".md":
            self._load_markdown(path)
        else:
            raise HTTPException(400, f"Unsupported file format: {path.suffix}")

        # Absorb sidecars
        absorbed = self._absorb_sidecars()

        # Always autosave after load (ensures .otio exists for .md loads,
        # and incorporates absorbed sidecars)
        self._autosave()
        self._save_session()

        return self.parsed  # type: ignore[return-value]

    def _load_otio(self, path: Path) -> None:
        """Load from an .otio file."""
        self.timeline = otio.adapters.read_from_file(str(path))
        self.parsed = from_otio(self.timeline)
        self.otio_path = path.resolve()

    def _load_markdown(self, path: Path) -> None:
        """Load from a markdown file — v2 or old table format."""
        content = path.read_text(encoding="utf-8")

        if _V2_FENCE_RE.search(content):
            # v2 format
            self.parsed = parse_v2(path)
        else:
            # Old table format → migrate
            from bee_video_editor.formats.migrate import old_to_new
            from bee_video_editor.parsers.storyboard import parse_storyboard

            old_sb = parse_storyboard(path)
            self.parsed = old_to_new(old_sb)

        self.timeline = to_otio(self.parsed)
        self.otio_path = path.with_suffix(".otio").resolve()

    # ── sidecars ─────────────────────────────────────────────────────

    def _absorb_sidecars(self) -> bool:
        """Absorb sidecar files into parsed model. Returns True if any were absorbed."""
        if self.parsed is None or self.project_dir is None:
            return False

        bee_dir = self.project_dir / ".bee-video"
        absorbed = False

        # assignments.json → apply to visual[].src
        assignments_path = bee_dir / "assignments.json"
        if assignments_path.exists():
            try:
                assignments = json.loads(assignments_path.read_text())
                for seg in self.parsed.segments:
                    if seg.id in assignments:
                        for key, media_path in assignments[seg.id].items():
                            layer, idx_str = key.split(":")
                            idx = int(idx_str)
                            if layer == "visual" and idx < len(seg.config.visual):
                                seg.config.visual[idx] = seg.config.visual[idx].model_copy(
                                    update={"src": media_path}
                                )
                absorbed = True
            except Exception:
                pass

        # segment-order.json → reorder segments
        order_path = bee_dir / "segment-order.json"
        if order_path.exists():
            try:
                order = json.loads(order_path.read_text())
                seg_map = {s.id: s for s in self.parsed.segments}
                reordered = [seg_map[sid] for sid in order if sid in seg_map]
                reordered_ids = {s.id for s in reordered}
                extras = [s for s in self.parsed.segments if s.id not in reordered_ids]
                self.parsed.segments = reordered + extras
                absorbed = True
            except Exception:
                pass

        # voice.json → set voice_lock
        voice_path = bee_dir / "voice.json"
        if voice_path.exists():
            try:
                voice_data = json.loads(voice_path.read_text())
                engine = voice_data.get("engine", "")
                voice = voice_data.get("voice", "")
                if engine and voice:
                    self.parsed.project.voice_lock = VoiceLock(
                        engine=engine, voice=voice,
                    )
                    absorbed = True
            except Exception:
                pass

        return absorbed

    # ── mutations ────────────────────────────────────────────────────

    def assign_media(
        self, segment_id: str, layer: str, index: int, media_path: str
    ) -> dict:
        """Assign (or unassign) media on a segment's visual layer."""
        parsed, _ = self.require_project()
        seg = next((s for s in parsed.segments if s.id == segment_id), None)
        if seg is None:
            raise HTTPException(404, f"Segment not found: {segment_id}")

        if index >= len(seg.config.visual):
            raise HTTPException(
                400,
                f"Visual index {index} out of range (segment has {len(seg.config.visual)} visuals)",
            )

        if not media_path:
            # Unassign
            seg.config.visual[index] = seg.config.visual[index].model_copy(
                update={"src": None}
            )
        else:
            seg.config.visual[index] = seg.config.visual[index].model_copy(
                update={"src": media_path}
            )

        self._autosave()
        return {
            "status": "ok",
            "segment_id": segment_id,
            "key": f"{layer}:{index}",
            "media_path": media_path,
        }

    def reorder_segments(self, order: list[str]) -> None:
        """Reorder parsed.segments by matching IDs, then autosave."""
        parsed, _ = self.require_project()
        seg_map = {s.id: s for s in parsed.segments}
        reordered = [seg_map[sid] for sid in order if sid in seg_map]
        reordered_ids = {s.id for s in reordered}
        extras = [s for s in parsed.segments if s.id not in reordered_ids]
        self.parsed.segments = reordered + extras  # type: ignore[union-attr]
        self._autosave()

    def update_segment_config(
        self, segment_id: str, updates: dict
    ) -> dict:
        """Update segment config fields and autosave.

        Updates can include:
        - transition_in: {"type": "dissolve", "duration": 1.0} or None
        - visual_updates: [{"index": 0, "color": "noir", "tc_in": "00:01:00.000", "out": "00:02:00.000"}]
        - audio_updates: [{"index": 0, "volume": 0.5, "fade_in": 2.0}]
        """
        parsed, _ = self.require_project()
        seg = next((s for s in parsed.segments if s.id == segment_id), None)
        if seg is None:
            raise HTTPException(404, f"Segment not found: {segment_id}")

        # Update transition
        if "transition_in" in updates:
            t = updates["transition_in"]
            if t is None:
                seg.config.transition_in = None
            else:
                from bee_video_editor.formats.models import TransitionConfig

                seg.config.transition_in = TransitionConfig(**t)

        # Update visual entries
        for vu in updates.get("visual_updates", []):
            vu = dict(vu)  # copy so pop doesn't mutate caller
            idx = vu.pop("index")
            if 0 <= idx < len(seg.config.visual):
                update_fields: dict = {}
                for field, value in vu.items():
                    if field == "tc_in":
                        update_fields["tc_in"] = value
                    elif hasattr(seg.config.visual[idx], field):
                        update_fields[field] = value
                seg.config.visual[idx] = seg.config.visual[idx].model_copy(
                    update=update_fields
                )

        # Update audio entries
        for au in updates.get("audio_updates", []):
            au = dict(au)  # copy so pop doesn't mutate caller
            idx = au.pop("index")
            if 0 <= idx < len(seg.config.audio):
                update_fields_a: dict = {}
                for field, value in au.items():
                    if hasattr(seg.config.audio[idx], field):
                        update_fields_a[field] = value
                seg.config.audio[idx] = seg.config.audio[idx].model_copy(
                    update=update_fields_a
                )

        self._autosave()
        return {"status": "ok", "segment_id": segment_id}

    def save_voice_config(self, engine: str, voice: str | None, speed: float = 0.95) -> None:
        """Set voice_lock on the parsed project and autosave."""
        self.require_project()
        if voice:
            self.parsed.project.voice_lock = VoiceLock(engine=engine, voice=voice)  # type: ignore[union-attr]
        self._autosave()

    def load_voice_config(self) -> dict | None:
        """Return voice_lock as dict, or None."""
        if self.parsed is None:
            return None
        vl = self.parsed.project.voice_lock
        if vl is None:
            return None
        return vl.model_dump()

    # ── persistence helpers ──────────────────────────────────────────

    def _autosave(self) -> None:
        """Rebuild timeline from parsed model and write to disk."""
        if self.parsed is None or self.otio_path is None:
            return
        self.timeline = to_otio(self.parsed)
        otio.adapters.write_to_file(self.timeline, str(self.otio_path))

    def _save_session(self) -> None:
        """Persist session info for auto-reload on restart."""
        if not self.project_dir or not self.otio_path:
            return
        data = {
            "otio_path": str(self.otio_path),
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


# Module-level singleton + dependency function


def _try_restore() -> SessionStore:
    """Create SessionStore, attempting to restore the last session."""
    store = SessionStore()
    last_session = Path.home() / ".bee-video" / "last-session.json"
    if last_session.exists():
        try:
            data = json.loads(last_session.read_text())
            otio_path = Path(data.get("otio_path", ""))
            proj_dir = Path(data.get("project_dir", ""))
            if otio_path.exists() and proj_dir.exists():
                store.load_project(otio_path, proj_dir)
        except Exception:
            pass  # Failed to restore — start fresh
    return store


_session = _try_restore()


def get_session() -> SessionStore:
    """FastAPI dependency — returns the singleton SessionStore."""
    return _session
