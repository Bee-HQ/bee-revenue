"""Project routes — load storyboard, get state, manage assignments."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from bee_video_editor.api.schema_compat import parsed_to_schema
from bee_video_editor.api.schemas import (
    AssignMediaRequest,
    BeeProjectSchema,
    DownloadEntryRequest,
    LoadProjectRequest,
    ReorderSegmentsRequest,
    UpdateSegmentRequest,
)
from bee_video_editor.api.session import SessionStore, get_session

router = APIRouter()


@router.post("/load", response_model=BeeProjectSchema)
def load_project(req: LoadProjectRequest, session: SessionStore = Depends(get_session)):
    """Load a storyboard file and return the parsed project."""
    parsed = session.load_project(Path(req.storyboard_path), Path(req.project_dir))
    return parsed_to_schema(parsed)


@router.get("/current", response_model=BeeProjectSchema)
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


@router.put("/update-segment")
def update_segment(req: UpdateSegmentRequest, session: SessionStore = Depends(get_session)):
    """Update segment config (transition, color, volume, trim points)."""
    return session.update_segment_config(req.segment_id, req.updates)


@router.post("/download-entry")
def download_entry(req: DownloadEntryRequest, session: SessionStore = Depends(get_session)):
    """Download asset for a specific segment entry using its download metadata."""
    _, project_dir = session.require_project()
    return session.download_entry(req.segment_id, req.layer, req.index, project_dir)


@router.post("/auto-assign")
def auto_assign(session: SessionStore = Depends(get_session)):
    """Auto-assign media files to segments based on keyword matching."""
    from bee_video_editor.services.matcher import auto_assign_media

    parsed, project_dir = session.require_project()
    media_dirs = [
        project_dir / "footage",
        project_dir / "stock",
        project_dir / "photos",
    ]
    plan = auto_assign_media(parsed, media_dirs)

    # Apply assignments
    applied = 0
    apply_errors: list[str] = []
    for a in plan.assignments:
        try:
            rel_path = str(a.file_path.relative_to(project_dir))
            session.update_segment_config(a.segment_id, {
                "visual_updates": [{"index": a.layer_index, "src": rel_path}]
            })
            applied += 1
        except Exception as e:
            apply_errors.append(f"{a.segment_id}: {e}")

    return {
        "status": "ok",
        "assigned": applied,
        "unmatched": len(plan.unmatched),
        "conflicts": plan.conflicts,
        "apply_errors": apply_errors,
    }


@router.post("/acquire-media")
def acquire_all_media(session: SessionStore = Depends(get_session)):
    """Search and download all stock media needed by the storyboard."""
    from bee_video_editor.services.acquisition import acquire_media

    parsed, project_dir = session.require_project()
    report = acquire_media(parsed, project_dir)

    return {
        "status": "ok",
        "queries": report.queries_total,
        "matched": report.queries_matched,
        "downloaded": report.downloads_succeeded,
        "failed": report.downloads_failed,
        "errors": report.errors,
    }


@router.get("/export")
def export_project(format: str = "md", session: SessionStore = Depends(get_session)):
    """Export the current project in markdown or OTIO format."""
    parsed, project_dir = session.require_project()
    if format == "md":
        from bee_video_editor.formats.writer import write_v2
        return {"format": "md", "content": write_v2(parsed)}
    elif format == "otio":
        from bee_video_editor.formats.otio_convert import clean_otio
        import opentimelineio as otio_lib
        out = project_dir / "output" / "export.otio"
        out.parent.mkdir(parents=True, exist_ok=True)
        otio_lib.adapters.write_to_file(clean_otio(session.timeline), str(out))
        return {"format": "otio", "path": str(out)}
    else:
        from fastapi import HTTPException
        raise HTTPException(400, f"Unsupported format: {format}")
