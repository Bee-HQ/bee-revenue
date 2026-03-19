"""Production routes — generate assets, preview segments, assemble."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from bee_video_editor.api.schemas import (
    BatchGraphicsRequest,
    CaptionRequest,
    GenerateRequest,
    ProductionStatusSchema,
    VoiceLockRequest,
)
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
    parsed, project_dir = session.require_project()
    output_dir = project_dir / "output"

    return ProductionStatusSchema(
        phase="loaded",
        segments_total=len(parsed.segments),
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
    parsed, project_dir = session.require_project()
    output_dir = project_dir / "output"
    graphics_dir = output_dir / "graphics"
    graphics_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors import graphics as gfx

    succeeded = []
    failed = []
    lower_third_idx = 0

    for seg in parsed.segments:
        for entry in seg.config.overlay:
            if entry.type == "LOWER_THIRD":
                name = entry.text or f"Character {lower_third_idx}"
                role = entry.subtext or ""

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


def _count_narration_segments(parsed) -> int:
    """Count how many narration segments exist in the parsed storyboard."""
    return sum(1 for seg in parsed.segments if seg.narration)


def _run_narration_background(parsed, config, workers: int = 1):
    """Generate narration in a background thread using the service layer."""
    global _narration_task
    from bee_video_editor.services.production import generate_narration_for_project

    try:
        result = generate_narration_for_project(parsed, config, workers=workers)
        _narration_task["running"] = False
        _narration_task["status"] = "ok" if result.ok else ("partial" if result.succeeded else "error")
        _narration_task["succeeded"] = [str(p) for p in result.succeeded]
        _narration_task["failed"] = [{"file": f.path, "error": f.error} for f in result.failed]
    except Exception as exc:
        _narration_task["running"] = False
        _narration_task["status"] = "error"
        _narration_task["failed"] = [{"file": "", "error": str(exc)}]


@router.post("/narration")
def generate_narration(req: GenerateRequest, session: SessionStore = Depends(get_session)):
    """Start TTS narration generation in the background.

    Returns immediately with total count. Poll GET /narration/status for progress.
    """
    global _narration_task

    if req.tts_engine not in VALID_TTS_ENGINES:
        raise HTTPException(400, f"Invalid TTS engine '{req.tts_engine}'. Must be one of: {', '.join(sorted(VALID_TTS_ENGINES))}")

    if _narration_task and _narration_task.get("running"):
        raise HTTPException(409, "Narration is already running")

    parsed, project_dir = session.require_project()

    from bee_video_editor.services.production import ProductionConfig
    config = ProductionConfig(
        project_dir=project_dir,
        tts_engine=req.tts_engine,
        tts_voice=req.tts_voice,
    )
    config.apply_voice_lock(parsed.project.voice_lock)
    config.output_dir.joinpath("narration").mkdir(parents=True, exist_ok=True)

    total = _count_narration_segments(parsed)

    _narration_task = {
        "running": True,
        "total": total,
        "project_dir": str(project_dir),
        "status": "running",
        "succeeded": [],
        "failed": [],
    }

    thread = threading.Thread(
        target=_run_narration_background,
        args=(parsed, config),
        kwargs={"workers": 1},
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

    # Ignore stale task state from a different project
    task = _narration_task
    if task and task.get("project_dir") != str(project_dir):
        task = None

    done = _count_files(narration_dir, "*.mp3") if narration_dir.exists() else 0
    total = task["total"] if task else 0
    running = task["running"] if task else False

    result = {
        "running": running,
        "done": done,
        "total": total,
    }

    # Include final results when done
    if task and not task["running"]:
        result["status"] = task["status"]
        result["succeeded"] = task["succeeded"]
        result["failed"] = task["failed"]
        result["count"] = len(task["succeeded"])

    return result


@router.post("/composite")
def composite_segments(session: SessionStore = Depends(get_session)):
    """Composite all segments (visual + color + overlay + audio)."""
    from bee_video_editor.services.compositor import composite_all
    from bee_video_editor.services.production import ProductionConfig

    parsed, project_dir = session.require_project()
    config = ProductionConfig(project_dir=project_dir)

    report = composite_all(parsed, project_dir, config.output_dir)

    return {
        "status": "ok" if report.failed == 0 else "partial",
        "succeeded": report.succeeded,
        "failed": report.failed,
        "skipped": report.skipped,
        "errors": report.errors,
    }


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

    parsed, project_dir = session.require_project()
    report = run_preflight(parsed, project_dir)

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

    parsed, project_dir = session.require_project()
    segments = extract_caption_segments(parsed)

    if not segments:
        return {"status": "ok", "count": 0, "message": "No captionable segments found"}

    out_dir = project_dir / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    generate_captions_estimated(segments, out, style=req.style)

    return {"status": "ok", "count": len(segments), "output": str(out)}


@router.websocket("/ws/progress")
async def ws_progress(websocket: WebSocket):
    """WebSocket for real-time production progress.

    Client sends: {"action": "produce"|"narration", "params": {...}}
    Server pushes: {"step": "...", "status": "...", "done": N, "total": N, "message": "..."}
    Final message: {"step": "complete", "status": "ok"|"failed", "output": "..."}
    """
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        action = data.get("action")
        params = data.get("params", {})

        from bee_video_editor.api.session import get_session
        session = get_session()

        if action == "narration":
            await _ws_narration(websocket, session, params)
        elif action == "produce":
            await _ws_produce(websocket, session, params)
        else:
            await websocket.send_json({"error": f"Unknown action: {action}"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"step": "error", "status": "failed", "message": str(e)[:200]})
        except Exception:
            pass


async def _ws_narration(websocket: WebSocket, session, params: dict):
    """Run narration with WebSocket progress updates."""
    from bee_video_editor.services.production import ProductionConfig, generate_narration_for_project

    parsed, project_dir = session.require_project()
    config = ProductionConfig(
        project_dir=project_dir,
        tts_engine=params.get("tts_engine", "edge"),
        tts_voice=params.get("tts_voice"),
    )
    config.apply_voice_lock(parsed.project.voice_lock)
    workers = params.get("workers", 1)

    narration_dir = config.output_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    total = _count_narration_segments(parsed)

    await websocket.send_json({"step": "narration", "status": "started", "done": 0, "total": total})

    result_holder: dict = {}
    done_count = [0]

    def run():
        result_holder["result"] = generate_narration_for_project(parsed, config, workers=workers)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    while thread.is_alive():
        current = len(list(narration_dir.glob("*.mp3")))
        if current != done_count[0]:
            done_count[0] = current
            await websocket.send_json({"step": "narration", "status": "running", "done": current, "total": total})
        await asyncio.sleep(1)

    thread.join()
    result = result_holder.get("result")

    final_count = len(list(narration_dir.glob("*.mp3")))
    status = "ok" if result and result.ok else "partial"
    await websocket.send_json({
        "step": "complete",
        "status": status,
        "done": final_count,
        "total": total,
        "succeeded": len(result.succeeded) if result else 0,
        "failed": len(result.failed) if result else 0,
    })


async def _ws_produce(websocket: WebSocket, session, params: dict):
    """Run full pipeline with WebSocket progress updates."""
    import queue

    from bee_video_editor.services.production import ProductionConfig, run_full_pipeline

    parsed, project_dir = session.require_project()

    if not session.otio_path:
        await websocket.send_json({"error": "No storyboard path available"})
        return

    config = ProductionConfig(
        project_dir=project_dir,
        tts_engine=params.get("tts_engine", "edge"),
        tts_voice=params.get("tts_voice"),
    )
    config.apply_voice_lock(parsed.project.voice_lock)

    msg_queue: queue.Queue = queue.Queue()
    result_holder: dict = {}

    def on_step(name, status, message):
        msg_queue.put({"step": name, "status": status, "message": message})

    def run():
        result_holder["result"] = run_full_pipeline(
            parsed=parsed,
            config=config,
            skip_graphics=params.get("skip_graphics", False),
            skip_captions=params.get("skip_captions", False),
            skip_narration=params.get("skip_narration", False),
            skip_trim=params.get("skip_trim", False),
            skip_composite=params.get("skip_composite", False),
            caption_style=params.get("caption_style", "karaoke"),
            transition=params.get("transition"),
            transition_duration=params.get("transition_duration", 1.0),
            animated=params.get("animated", False),
            workers=params.get("workers", 1),
            on_step=on_step,
        )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    while thread.is_alive():
        while not msg_queue.empty():
            msg = msg_queue.get_nowait()
            await websocket.send_json(msg)
        await asyncio.sleep(0.5)

    # Drain remaining messages
    while not msg_queue.empty():
        msg = msg_queue.get_nowait()
        await websocket.send_json(msg)

    thread.join()
    result = result_holder.get("result")

    await websocket.send_json({
        "step": "complete",
        "status": "ok" if result and result.ok else "failed",
        "output": str(result.output_path) if result and result.output_path else None,
    })


@router.post("/produce")
def produce_video(
    transition: str | None = None,
    transition_duration: float = 1.0,
    caption_style: str = "karaoke",
    tts_engine: str = "edge",
    tts_voice: str | None = None,
    skip_graphics: bool = False,
    skip_narration: bool = False,
    skip_captions: bool = False,
    skip_trim: bool = False,
    skip_composite: bool = False,
    session: SessionStore = Depends(get_session),
):
    """Run the full production pipeline."""
    from bee_video_editor.services.production import ProductionConfig, run_full_pipeline

    if tts_engine not in VALID_TTS_ENGINES:
        raise HTTPException(400, f"Invalid TTS engine '{tts_engine}'. Must be one of: {', '.join(sorted(VALID_TTS_ENGINES))}")

    parsed, project_dir = session.require_project()

    if not session.otio_path:
        raise HTTPException(400, "No storyboard path available — load project first")

    config = ProductionConfig(
        project_dir=project_dir,
        tts_engine=tts_engine,
        tts_voice=tts_voice,
    )
    config.apply_voice_lock(parsed.project.voice_lock)

    result = run_full_pipeline(
        parsed=parsed,
        config=config,
        skip_graphics=skip_graphics,
        skip_captions=skip_captions,
        skip_narration=skip_narration,
        skip_trim=skip_trim,
        skip_composite=skip_composite,
        caption_style=caption_style,
        transition=transition,
        transition_duration=transition_duration,
    )

    return {
        "status": "ok" if result.ok else "failed",
        "steps": [{"name": s.name, "status": s.status, "message": s.message} for s in result.steps],
        "output": str(result.output_path) if result.output_path else None,
    }


@router.post("/preview/{segment_id}")
def generate_segment_preview(segment_id: str, session: SessionStore = Depends(get_session)):
    """Generate a preview for a single segment."""
    from bee_video_editor.services.production import generate_preview

    parsed, project_dir = session.require_project()

    # Find segment from in-memory session state (not disk)
    seg = next((s for s in parsed.segments if s.id == segment_id), None)
    if not seg:
        raise HTTPException(404, f"Segment not found: {segment_id}")

    media_path_str = seg.config.visual[0].src if seg.config.visual else None
    if not media_path_str:
        raise HTTPException(400, f"No media assigned to segment {segment_id}")

    media_path = Path(media_path_str)
    if not media_path.exists():
        raise HTTPException(404, f"Assigned media not found: {media_path_str}")

    previews_dir = project_dir / "output" / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)
    preview_path = previews_dir / f"{segment_id}.mp4"

    try:
        generate_preview(media_path, preview_path)
        return {"status": "ok", "preview": str(preview_path)}
    except Exception as e:
        raise HTTPException(500, f"Preview generation failed: {e}")


@router.post("/previews")
def generate_all_segment_previews(session: SessionStore = Depends(get_session)):
    """Generate previews for all segments with assigned media."""
    from bee_video_editor.services.production import generate_all_previews

    parsed, project_dir = session.require_project()
    result = generate_all_previews(parsed, project_dir)

    status = "ok" if result.ok else "partial" if result.succeeded else "error"
    return {
        "status": status,
        "succeeded": len(result.succeeded),
        "failed": len(result.failed),
        "skipped": len(result.skipped),
    }


@router.post("/export/otio")
def export_otio_timeline(
    fps: float = 30.0,
    session: SessionStore = Depends(get_session),
):
    """Export storyboard to OTIO format (clean, no bee_video metadata)."""
    from bee_video_editor.formats.otio_convert import clean_otio

    import opentimelineio as otio_lib

    parsed, project_dir = session.require_project()
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "timeline.otio"

    otio_lib.adapters.write_to_file(clean_otio(session.timeline), str(output_path))

    return {"status": "ok", "output": str(output_path), "segments": len(parsed.segments)}


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


@router.post("/graphics-batch")
def batch_graphics(req: BatchGraphicsRequest, session: SessionStore = Depends(get_session)):
    """Generate graphics from a JSON config file."""
    from bee_video_editor.services.batch_graphics import generate_batch, parse_graphics_config

    _, project_dir = session.require_project()
    config_path = Path(req.config_path)
    if not config_path.exists():
        raise HTTPException(404, f"Config file not found: {req.config_path}")

    try:
        specs, output_dir_rel = parse_graphics_config(config_path)
    except ValueError as e:
        raise HTTPException(400, str(e))

    output_dir = project_dir / output_dir_rel
    result = generate_batch(specs, output_dir)

    status = "ok" if result.ok else ("partial" if result.succeeded else "error")
    return {
        "status": status,
        "count": len(result.succeeded),
        "succeeded": [str(p) for p in result.succeeded],
        "failed": [{"file": f.path, "error": f.error} for f in result.failed],
        "skipped": result.skipped,
    }


@router.put("/voice-lock")
def save_voice_lock(req: VoiceLockRequest, session: SessionStore = Depends(get_session)):
    """Save TTS voice config for this project."""
    session.save_voice_config(req.engine, req.voice, req.speed)
    return {"status": "ok", "engine": req.engine, "voice": req.voice, "speed": req.speed}


@router.get("/voice-lock")
def get_voice_lock(session: SessionStore = Depends(get_session)):
    """Get saved TTS voice config for this project."""
    config = session.load_voice_config()
    return config or {}


@router.post("/rough-cut")
def rough_cut(session: SessionStore = Depends(get_session)):
    """Export a fast 720p rough cut for structure review."""
    from bee_video_editor.services.production import ProductionConfig, rough_cut_export

    parsed, project_dir = session.require_project()
    config = ProductionConfig(project_dir=project_dir)
    result = rough_cut_export(parsed, config)

    if result is None:
        raise HTTPException(400, "No assigned media found. Assign media to segments first.")

    return {"status": "ok", "output": str(result)}
