"""Video generation — pluggable provider interface.

Providers generate video clips from text prompts and optional reference media.
Ships with a 'stub' provider that generates real MP4s via FFmpeg.
Real providers (Runway, Kling, Luma, etc.) are optional extras.

Usage:
    from bee_video_editor.processors.videogen import generate_clip, GenerationRequest

    req = GenerationRequest(prompt="aerial shot of farm", duration=5.0)
    result = generate_clip(req, Path("output.mp4"), provider="stub")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GenerationRequest:
    """Input for video generation."""
    prompt: str
    duration: float = 5.0
    width: int = 1280
    height: int = 720
    reference_images: list[Path] = field(default_factory=list)
    reference_videos: list[Path] = field(default_factory=list)
    style: str | None = None
    negative_prompt: str | None = None


@dataclass
class GenerationResult:
    """Output from video generation."""
    success: bool
    output_path: Path
    provider: str
    prompt: str
    duration: float
    error: str | None = None
    metadata: dict = field(default_factory=dict)


# ─── Provider registry ───────────────────────────────────────────────────────

_PROVIDERS: dict[str, tuple[str, object]] = {}


def _register(name: str, description: str, fn):
    _PROVIDERS[name] = (description, fn)


def list_providers() -> dict[str, str]:
    """Return {name: description} for all available providers."""
    _ensure_providers_loaded()
    return {name: desc for name, (desc, _) in _PROVIDERS.items()}


def generate_clip(
    request: GenerationRequest,
    output_path: Path,
    provider: str = "stub",
) -> GenerationResult:
    """Generate a video clip using the specified provider.

    Args:
        request: What to generate (prompt, duration, references).
        output_path: Where to save the generated clip.
        provider: Provider name ("stub", "runway", "kling", etc.).

    Returns:
        GenerationResult with success status and metadata.
    """
    _ensure_providers_loaded()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if provider not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(
            f"Unknown video generation provider '{provider}'. "
            f"Available: {available}"
        )

    _, fn = _PROVIDERS[provider]
    return fn(request, output_path)


# ─── Stub provider (always available) ────────────────────────────────────────

def _generate_stub(request: GenerationRequest, output_path: Path) -> GenerationResult:
    """Generate a placeholder video — black frame with prompt text burned in.

    Uses FFmpeg to create a real playable MP4 so downstream pipeline
    processing (trim, normalize, concat) works without a real AI provider.
    """
    from bee_video_editor.processors.ffmpeg import FFmpegError, run_ffmpeg

    # Escape for FFmpeg drawtext (same pattern as ffmpeg.py:drawtext)
    escaped = request.prompt.replace("'", "'\\\\\\''").replace(":", "\\:")

    # Truncate long prompts for display
    if len(escaped) > 80:
        escaped = escaped[:77] + "..."

    try:
        args = [
            "-f", "lavfi",
            "-i", f"color=c=black:s={request.width}x{request.height}:d={request.duration}:r=30",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(request.duration),
            "-vf", (
                f"drawtext=text='{escaped}'"
                f":fontcolor=white:fontsize=28"
                f":x=(w-text_w)/2:y=(h-text_h)/2"
            ),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "64k",
            "-shortest",
            str(output_path),
        ]
        run_ffmpeg(args)

        return GenerationResult(
            success=True,
            output_path=output_path,
            provider="stub",
            prompt=request.prompt,
            duration=request.duration,
            metadata={"type": "stub_ffmpeg", "width": request.width, "height": request.height},
        )
    except FFmpegError as e:
        return GenerationResult(
            success=False,
            output_path=output_path,
            provider="stub",
            prompt=request.prompt,
            duration=request.duration,
            error=str(e),
        )


def _ensure_providers_loaded():
    """Register built-in and optional providers."""
    if _PROVIDERS:
        return

    _register("stub", "Placeholder — generates FFmpeg test video with prompt text", _generate_stub)

    # Optional providers — registered only if their dependencies are installed
    try:
        from bee_video_editor.processors._videogen_runway import generate_runway
        _register("runway", "Runway Gen-4 — text/image to video", generate_runway)
    except ImportError:
        pass

    try:
        from bee_video_editor.processors._videogen_kling import generate_kling
        _register("kling", "Kling — text/image to video", generate_kling)
    except ImportError:
        pass

    try:
        from bee_video_editor.processors._videogen_luma import generate_luma
        _register("luma", "Luma Dream Machine — text/image to video", generate_luma)
    except ImportError:
        pass
