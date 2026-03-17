"""Video generation — pluggable provider interface.

Providers generate video clips from text prompts and optional reference media.
Ships with a 'stub' provider for testing. Real providers (Runway, Kling, Luma, etc.)
are optional extras.

Usage:
    from bee_video_editor.processors.videogen import generate_clip, GenerationRequest

    req = GenerationRequest(prompt="aerial shot of farm", duration=5.0)
    result = generate_clip(req, Path("output.mp4"), provider="stub")
"""

from __future__ import annotations

import json
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


# ─── Stub provider (always available, for testing) ───────────────────────────

def _generate_stub(request: GenerationRequest, output_path: Path) -> GenerationResult:
    """Generate a placeholder clip — writes metadata JSON instead of real video.

    For testing and development. Real providers replace this with actual
    AI-generated video.
    """
    placeholder = {
        "type": "stub_generated_clip",
        "prompt": request.prompt,
        "duration": request.duration,
        "width": request.width,
        "height": request.height,
        "reference_images": [str(p) for p in request.reference_images],
        "reference_videos": [str(p) for p in request.reference_videos],
        "style": request.style,
    }
    output_path.write_text(json.dumps(placeholder, indent=2))

    return GenerationResult(
        success=True,
        output_path=output_path,
        provider="stub",
        prompt=request.prompt,
        duration=request.duration,
        metadata=placeholder,
    )


def _ensure_providers_loaded():
    """Register built-in and optional providers."""
    if _PROVIDERS:
        return

    _register("stub", "Placeholder — writes metadata JSON (for testing)", _generate_stub)

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
