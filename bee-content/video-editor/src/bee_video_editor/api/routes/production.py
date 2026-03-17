"""Production routes — generate assets, preview segments, assemble."""

from __future__ import annotations

import threading
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from bee_video_editor.api.schemas import CaptionRequest, GenerateRequest, ProductionStatusSchema
from bee_video_editor.api.session import SessionStore, get_session

router = APIRouter()

# Background narration task state
_narration_task: dict | None = None


def _count_files(directory: Path, pattern: str = "*") -> int:
    if not directory.exists():
        return 0
    return len([f for f in directory.glob(pattern) if f.is_file()])


@router.get("/status", response_model=ProductionStatusSchema)
def get_production_status(session: SessionStore = Depends(get_session)):
    """Get current production status."""
    storyboard, project_dir = session.require_project()
    output_dir = project_dir / "output"

    return ProductionStatusSchema(
        phase="loaded",
        segments_total=storyboard.total_segments,
        segments_done=_count_files(output_dir / "segments", "*.mp4"),
        narration_files=_count_files(output_dir / "narration"),
        graphics_files=_count_files(output_dir / "graphics"),
        trimmed_files=_count_files(output_dir / "segments"),
    )


@router.post("/init")
def init_project(session: SessionStore = Depends(get_session)):
    """Initialize output directories for the project."""
    _, project_dir = session.require_project()
    output_dir = project_dir / "output"

    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "final"]:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)

    return {"status": "ok", "output_dir": str(output_dir)}


@router.post("/graphics")
def generate_graphics(session: SessionStore = Depends(get_session)):
    """Generate graphics assets from storyboard."""
    storyboard, project_dir = session.require_project()
    output_dir = project_dir / "output"
    graphics_dir = output_dir / "graphics"
    graphics_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors import graphics as gfx

    succeeded = []
    failed = []
    lower_third_idx = 0

    for seg in storyboard.segments:
        for overlay in seg.overlay:
            if overlay.content_type == "GRAPHIC" and "lower third" in overlay.content.lower():
                # Extract name — role from content like: Lower third — "Name — Role"
                import re
                match = re.search(r'"([^"]+)"', overlay.content)
                if match:
                    parts = match.group(1).split(" — ")
                    name = parts[0].strip()
                    role = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = f"Character {lower_third_idx}"
                    role = ""

                slug = name.lower().replace(" ", "-")[:30]
                out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{slug}.png"

                try:
                    if not out.exists():
                        gfx.lower_third(name, role, out)
                    succeeded.append(str(out))
                except Exception as exc:
                    failed.append({"file": str(out), "error": str(exc)})

                lower_third_idx += 1

    if failed and not succeeded:
        status = "error"
    elif failed:
        status = "partial"
    else:
        status = "ok"

    return {
        "status": status,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": [],
        "count": len(succeeded),
    }


VALID_TTS_ENGINES = {"edge", "kokoro", "openai", "elevenlabs"}


def _count_narration_segments(storyboard) -> int:
    """Count how many NAR audio entries exist in the storyboard."""
    import re
    count = 0
    for seg in storyboard.segments:
        for audio_entry in seg.audio:
            if audio_entry.content_type != "NAR":
                continue
            text = audio_entry.content.strip()
            if not text:
                continue
            text = re.sub(r'\s*\+\s*.*$', '', text)
            text = text.strip('"').strip('\u201c').strip('\u201d')
            if text:
                count += 1
    return count


def _run_narration_background(storyboard, narration_dir: Path, engine: str, voice: str | None):
    """Generate narration in a background thread. Updates _narration_task state."""
    global _narration_task
    import re
    from bee_video_editor.processors.tts import generate_narration as tts_generate

    succeeded = []
    failed = []

    for i, seg in enumerate(storyboard.segments):
        for audio_entry in seg.audio:
            if audio_entry.content_type != "NAR":
                continue

            text = audio_entry.content.strip()
            if not text:
                continue

            text = re.sub(r'\s*\+\s*.*$', '', text)
            text = text.strip('"').strip('\u201c').strip('\u201d')

            if not text:
                continue

            slug = re.sub(r'[^\w\s-]', '', seg.title.lower())
            slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:30]
            out = narration_dir / f"nar-{i:03d}-{slug}.mp3"

            try:
                if not out.exists():
                    tts_generate(
                        text=text,
                        output_path=out,
                        engine=engine,
                        voice=voice,
                    )
                succeeded.append(str(out))
            except Exception as exc:
                failed.append({"file": str(out), "error": str(exc)})

    if failed and not succeeded:
        status = "error"
    elif failed:
        status = "partial"
    else:
        status = "ok"

    _narration_task["running"] = False
    _narration_task["status"] = status
    _narration_task["succeeded"] = succeeded
    _narration_task["failed"] = failed


@router.post("/narration")
def generate_narration(req: GenerateRequest, session: SessionStore = Depends(get_session)):
    """Start TTS narration generation in the background.

    Returns immediately with total count. Poll GET /status for progress.
    """
    global _narration_task

    if req.tts_engine not in VALID_TTS_ENGINES:
        raise HTTPException(400, f"Invalid TTS engine '{req.tts_engine}'. Must be one of: {', '.join(sorted(VALID_TTS_ENGINES))}")

    if _narration_task and _narration_task.get("running"):
        raise HTTPException(409, "Narration is already running")

    storyboard, project_dir = session.require_project()
    output_dir = project_dir / "output"
    narration_dir = output_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    total = _count_narration_segments(storyboard)

    _narration_task = {
        "running": True,
        "total": total,
        "status": "running",
        "succeeded": [],
        "failed": [],
    }

    thread = threading.Thread(
        target=_run_narration_background,
        args=(storyboard, narration_dir, req.tts_engine, req.tts_voice),
        daemon=True,
    )
    thread.start()

    return {"status": "started", "total": total}


@router.get("/narration/status")
def get_narration_status(session: SessionStore = Depends(get_session)):
    """Get narration generation progress."""
    _, project_dir = session.require_project()
    output_dir = project_dir / "output"
    narration_dir = output_dir / "narration"

    done = _count_files(narration_dir, "*.mp3") if narration_dir.exists() else 0
    total = _narration_task["total"] if _narration_task else 0
    running = _narration_task["running"] if _narration_task else False

    result = {
        "running": running,
        "done": done,
        "total": total,
    }

    # Include final results when done
    if _narration_task and not _narration_task["running"]:
        result["status"] = _narration_task["status"]
        result["succeeded"] = _narration_task["succeeded"]
        result["failed"] = _narration_task["failed"]
        result["count"] = len(_narration_task["succeeded"])

    return result


@router.get("/effects")
def list_effects():
    """List available effects, transitions, and color presets."""
    from bee_video_editor.processors.ffmpeg import COLOR_GRADE_PRESETS, XFADE_TRANSITIONS

    return {
        "color_presets": list(COLOR_GRADE_PRESETS.keys()),
        "transitions": XFADE_TRANSITIONS,
        "ken_burns": [
            "zoom_in", "zoom_out", "pan_left", "pan_right",
            "pan_up", "pan_down", "zoom_in_pan_right",
        ],
    }


@router.get("/preflight")
def get_preflight(session: SessionStore = Depends(get_session)):
    """Run asset preflight check against loaded project."""
    from bee_video_editor.services.preflight import run_preflight

    storyboard, project_dir = session.require_project()
    report = run_preflight(storyboard, project_dir)

    return {
        "total": report.total,
        "found": report.found,
        "missing": report.missing,
        "generated": report.generated,
        "needs_check": report.needs_check,
        "entries": [
            {
                "segment_id": e.segment_id,
                "layer": e.layer,
                "visual_code": e.visual_code,
                "qualifier": e.qualifier,
                "status": e.status,
                "file_path": e.file_path,
            }
            for e in report.entries
        ],
    }


@router.post("/captions")
def generate_captions(req: CaptionRequest, session: SessionStore = Depends(get_session)):
    """Generate ASS captions from storyboard."""
    from bee_video_editor.processors.captions import (
        extract_caption_segments,
        generate_captions_estimated,
    )

    storyboard, project_dir = session.require_project()
    segments = extract_caption_segments(storyboard)

    if not segments:
        return {"status": "ok", "count": 0, "message": "No captionable segments found"}

    out_dir = project_dir / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    generate_captions_estimated(segments, out, style=req.style)

    return {"status": "ok", "count": len(segments), "output": str(out)}


@router.post("/assemble")
def assemble_video(
    transition: str | None = None,
    transition_duration: float = 1.0,
    session: SessionStore = Depends(get_session),
):
    """Assemble all segments into final video.

    Query params:
        transition: Optional xfade transition name.
        transition_duration: Transition duration in seconds.
    """
    if transition:
        from bee_video_editor.processors.ffmpeg import XFADE_TRANSITIONS
        if transition not in XFADE_TRANSITIONS:
            raise HTTPException(400, f"Invalid transition '{transition}'. Use GET /api/production/effects for valid options.")
    _, project_dir = session.require_project()
    output_dir = project_dir / "output"

    from bee_video_editor.processors.ffmpeg import (
        FFmpegError,
        concat_segments,
        concat_with_transitions,
    )

    # Collect segments in order
    composited_dir = output_dir / "composited"
    normalized_dir = output_dir / "normalized"
    segments_dir = output_dir / "segments"

    # Try composited first, then normalized, then raw segments
    for d in [composited_dir, normalized_dir, segments_dir]:
        if d.exists():
            files = sorted(d.glob("*.mp4"))
            if files:
                final_dir = output_dir / "final"
                final_dir.mkdir(parents=True, exist_ok=True)
                output_path = final_dir / "final_assembled.mp4"
                try:
                    if transition and len(files) >= 2:
                        concat_with_transitions(
                            files, output_path,
                            transition=transition,
                            transition_duration=transition_duration,
                        )
                    else:
                        concat_segments(files, output_path, reencode=True)
                    return {"status": "ok", "output": str(output_path)}
                except FFmpegError as e:
                    raise HTTPException(500, f"Assembly failed: {e}")

    raise HTTPException(400, "No segments found to assemble. Generate assets first.")
