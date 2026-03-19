"""AI video generation — generate B-roll clips from text prompts.

Providers:
- stub: FFmpeg black frame with text (no API key, always available)
- kling: Kling AI (requires KLING_API_KEY)
- veo: Google Veo (requires VEO_API_KEY)
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GenerationResult:
    provider: str
    prompt: str
    file_path: Path | None = None
    duration: int = 0
    error: str | None = None


def list_providers() -> dict[str, str]:
    """List available AI video providers."""
    providers = {"stub": "FFmpeg black frame with drawtext (always available)"}
    if os.environ.get("KLING_API_KEY"):
        providers["kling"] = "Kling AI video generation"
    if os.environ.get("VEO_API_KEY"):
        providers["veo"] = "Google Veo video generation"
    return providers


def generate_clip(
    prompt: str,
    output_dir: Path,
    *,
    duration: int = 5,
    provider: str = "stub",
    width: int = 1920,
    height: int = 1080,
) -> GenerationResult:
    """Generate a video clip from a text prompt."""
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r'[^\w\s-]', '', prompt.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:40]
    out_path = output_dir / f"gen-{provider}-{slug}.mp4"

    if provider == "stub":
        return _generate_stub(prompt, out_path, duration, width, height)
    elif provider == "kling":
        return _generate_kling(prompt, out_path, duration)
    elif provider == "veo":
        return _generate_veo(prompt, out_path, duration)
    else:
        return GenerationResult(provider=provider, prompt=prompt, error=f"Unknown provider: {provider}")


def _generate_stub(prompt: str, out_path: Path, duration: int, width: int, height: int) -> GenerationResult:
    """Generate a black frame with the prompt as overlay text."""
    # Validate parameters
    duration = max(1, min(duration, 300))
    width = max(64, min(width, 3840))
    height = max(64, min(height, 2160))
    # FFmpeg drawtext escaping: \ first, then special chars
    safe_text = prompt.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:").replace("[", "\\[").replace("]", "\\]").replace(";", "\\;").replace("%", "%%")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={duration}",
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
        "-vf", f"drawtext=text='{safe_text}':fontcolor=white:fontsize=28:x=(w-tw)/2:y=(h-th)/2",
        "-t", str(duration),
        "-c:v", "libx264", "-c:a", "aac",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=60)
        return GenerationResult(provider="stub", prompt=prompt, file_path=out_path, duration=duration)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return GenerationResult(provider="stub", prompt=prompt, error=str(e)[:200])


def _generate_kling(prompt: str, out_path: Path, duration: int) -> GenerationResult:
    """Generate via Kling AI API (requires KLING_API_KEY)."""
    api_key = os.environ.get("KLING_API_KEY")
    if not api_key:
        return GenerationResult(provider="kling", prompt=prompt, error="KLING_API_KEY not set")

    # Kling API integration would go here
    # For now, return a placeholder indicating the API is not yet implemented
    return GenerationResult(
        provider="kling", prompt=prompt,
        error="Kling API integration not yet implemented — set KLING_API_KEY and check docs",
    )


def _generate_veo(prompt: str, out_path: Path, duration: int) -> GenerationResult:
    """Generate via Google Veo API (requires VEO_API_KEY)."""
    api_key = os.environ.get("VEO_API_KEY")
    if not api_key:
        return GenerationResult(provider="veo", prompt=prompt, error="VEO_API_KEY not set")

    return GenerationResult(
        provider="veo", prompt=prompt,
        error="Veo API integration not yet implemented — set VEO_API_KEY and check docs",
    )
