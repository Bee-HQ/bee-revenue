"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    LayerEntrySchema,
    LoadProjectRequest,
    SegmentSchema,
    StoryboardSchema,
)
from bee_video_editor.models_storyboard import Storyboard
from bee_video_editor.parsers.storyboard import parse_storyboard

router = APIRouter()

# In-memory state for the current session
_current_storyboard: Storyboard | None = None
_current_project_dir: Path | None = None
_assignments_path: Path | None = None


def _segment_to_schema(seg) -> SegmentSchema:
    def _layers(entries):
        return [
            LayerEntrySchema(
                content=e.content,
                content_type=e.content_type,
                time_start=e.time_start,
                time_end=e.time_end,
                raw=e.raw,
            )
            for e in entries
        ]

    return SegmentSchema(
        id=seg.id,
        start=seg.start,
        end=seg.end,
        title=seg.title,
        section=seg.section,
        section_time=seg.section_time,
        subsection=seg.subsection,
        duration_seconds=seg.duration_seconds,
        visual=_layers(seg.visual),
        audio=_layers(seg.audio),
        overlay=_layers(seg.overlay),
        music=_layers(seg.music),
        source=_layers(seg.source),
        transition=_layers(seg.transition),
        assigned_media=seg.assigned_media,
    )


def _storyboard_to_schema(sb: Storyboard) -> StoryboardSchema:
    return StoryboardSchema(
        title=sb.title,
        total_segments=sb.total_segments,
        total_duration_seconds=sb.total_duration_seconds,
        sections=sb.sections,
        segments=[_segment_to_schema(s) for s in sb.segments],
        stock_footage_needed=len(sb.stock_footage),
        photos_needed=len(sb.photos_needed),
        maps_needed=len(sb.maps_needed),
        production_rules=[r for r in sb.production_rules.rules],
    )


def _load_assignments(path: Path) -> dict[str, dict[str, str]]:
    """Load media assignments from sidecar JSON."""
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_assignments(path: Path, assignments: dict[str, dict[str, str]]) -> None:
    """Save media assignments to sidecar JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(assignments, f, indent=2)


@router.post("/load", response_model=StoryboardSchema)
def load_project(req: LoadProjectRequest):
    """Load a storyboard file and return the parsed project."""
    global _current_storyboard, _current_project_dir, _assignments_path

    sb_path = Path(req.storyboard_path)
    if not sb_path.exists():
        raise HTTPException(404, f"Storyboard not found: {sb_path}")

    _current_project_dir = Path(req.project_dir).resolve()
    _assignments_path = _current_project_dir / ".bee-video" / "assignments.json"

    _current_storyboard = parse_storyboard(sb_path)

    # Apply saved assignments
    saved = _load_assignments(_assignments_path)
    for seg in _current_storyboard.segments:
        if seg.id in saved:
            seg.assigned_media = saved[seg.id]

    return _storyboard_to_schema(_current_storyboard)


@router.get("/current", response_model=StoryboardSchema)
def get_current_project():
    """Get the currently loaded project."""
    if _current_storyboard is None:
        raise HTTPException(404, "No project loaded")
    return _storyboard_to_schema(_current_storyboard)


@router.put("/assign")
def assign_media(req: AssignMediaRequest):
    """Assign a media file to a segment layer."""
    if _current_storyboard is None or _assignments_path is None:
        raise HTTPException(404, "No project loaded")

    # Find segment
    seg = None
    for s in _current_storyboard.segments:
        if s.id == req.segment_id:
            seg = s
            break

    if seg is None:
        raise HTTPException(404, f"Segment not found: {req.segment_id}")

    # Store assignment
    key = f"{req.layer}:{req.layer_index}"
    seg.assigned_media[key] = req.media_path

    # Persist
    assignments = _load_assignments(_assignments_path)
    if seg.id not in assignments:
        assignments[seg.id] = {}
    assignments[seg.id][key] = req.media_path
    _save_assignments(_assignments_path, assignments)

    return {"status": "ok", "segment_id": seg.id, "key": key, "media_path": req.media_path}
