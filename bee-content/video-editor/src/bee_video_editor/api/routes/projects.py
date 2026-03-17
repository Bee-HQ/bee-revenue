"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    LayerEntrySchema,
    LoadProjectRequest,
    ReorderSegmentsRequest,
    SegmentSchema,
    StoryboardSchema,
)
from bee_video_editor.api.session import SessionStore, get_session
from bee_video_editor.models_storyboard import Storyboard

router = APIRouter()


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


@router.post("/load", response_model=StoryboardSchema)
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    """Load a storyboard file and return the parsed project."""
    sb = session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return _storyboard_to_schema(sb)


@router.get("/current", response_model=StoryboardSchema)
def get_current_project(session: SessionStore = Depends(get_session)):
    """Get the currently loaded project."""
    sb, _ = session.require_project()
    return _storyboard_to_schema(sb)


@router.put("/assign")
def assign_media(req: AssignMediaRequest, session: SessionStore = Depends(get_session)):
    """Assign a media file to a segment layer."""
    return session.assign_media(req.segment_id, req.layer, req.layer_index, req.media_path)


@router.put("/reorder")
def reorder_segments(req: ReorderSegmentsRequest, session: SessionStore = Depends(get_session)):
    """Persist a custom segment ordering."""
    session.save_segment_order(req.segment_order)
    return {"status": "ok", "count": len(req.segment_order)}
