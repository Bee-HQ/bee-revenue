"""Production routes — generate assets, preview segments, assemble."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from bee_video_editor.api.schemas import GenerateRequest, ProductionStatusSchema

router = APIRouter()


def _get_state():
    from bee_video_editor.api.routes.projects import _current_project_dir, _current_storyboard
    if _current_storyboard is None or _current_project_dir is None:
        raise HTTPException(404, "No project loaded")
    return _current_storyboard, _current_project_dir


def _count_files(directory: Path, pattern: str = "*") -> int:
    if not directory.exists():
        return 0
    return len([f for f in directory.glob(pattern) if f.is_file()])


@router.get("/status", response_model=ProductionStatusSchema)
def get_production_status():
    """Get current production status."""
    storyboard, project_dir = _get_state()
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
def init_project():
    """Initialize output directories for the project."""
    _, project_dir = _get_state()
    output_dir = project_dir / "output"

    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "final"]:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)

    return {"status": "ok", "output_dir": str(output_dir)}


@router.post("/graphics")
def generate_graphics():
    """Generate graphics assets from storyboard."""
    storyboard, project_dir = _get_state()
    output_dir = project_dir / "output"
    graphics_dir = output_dir / "graphics"
    graphics_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors import graphics as gfx

    generated = []
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
                if not out.exists():
                    gfx.lower_third(name, role, out)
                    generated.append(str(out))
                lower_third_idx += 1

    return {"status": "ok", "generated": generated, "count": len(generated)}


@router.post("/narration")
def generate_narration(req: GenerateRequest):
    """Generate TTS narration for narrator segments."""
    storyboard, project_dir = _get_state()
    output_dir = project_dir / "output"
    narration_dir = output_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    from bee_video_editor.processors.tts import generate_narration as tts_generate

    generated = []
    import re

    for i, seg in enumerate(storyboard.segments):
        for audio_entry in seg.audio:
            if audio_entry.content_type != "NAR":
                continue

            text = audio_entry.content.strip()
            if not text:
                continue

            # Strip trailing notes like "+ dark ambient..."
            text = re.sub(r'\s*\+\s*.*$', '', text)
            text = text.strip('"').strip('\u201c').strip('\u201d')

            if not text:
                continue

            slug = re.sub(r'[^\w\s-]', '', seg.title.lower())
            slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:30]
            out = narration_dir / f"nar-{i:03d}-{slug}.mp3"

            if not out.exists():
                tts_generate(
                    text=text,
                    output_path=out,
                    engine=req.tts_engine,
                    voice=req.tts_voice,
                )
                generated.append(str(out))

    return {"status": "ok", "generated": generated, "count": len(generated)}


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


@router.post("/assemble")
def assemble_video(
    transition: str | None = None,
    transition_duration: float = 1.0,
):
    """Assemble all segments into final video.

    Query params:
        transition: Optional xfade transition name.
        transition_duration: Transition duration in seconds.
    """
    _, project_dir = _get_state()
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
