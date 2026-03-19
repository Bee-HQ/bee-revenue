"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from bee_video_editor.api.schema_compat import parsed_to_schema
from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    LoadProjectRequest,
    ReorderSegmentsRequest,
    StoryboardSchema,
)
from bee_video_editor.api.session import SessionStore, get_session

router = APIRouter()


@router.post("/load", response_model=StoryboardSchema)
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    """Load a storyboard file and return the parsed project."""
    parsed = session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return parsed_to_schema(parsed)


@router.get("/current", response_model=StoryboardSchema)
def get_current_project(session: SessionStore = Depends(get_session)):
    """Get the currently loaded project."""
    parsed, _ = session.require_project()
    return parsed_to_schema(parsed)


@router.put("/assign")
def assign_media(req: AssignMediaRequest, session: SessionStore = Depends(get_session)):
    """Assign a media file to a segment layer."""
    return session.assign_media(req.segment_id, req.layer, req.layer_index, req.media_path)


@router.put("/reorder")
def reorder_segments(req: ReorderSegmentsRequest, session: SessionStore = Depends(get_session)):
    """Persist a custom segment ordering."""
    session.reorder_segments(req.segment_order)
    return {"status": "ok", "count": len(req.segment_order)}
