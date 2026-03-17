# Design: Lottie Animated Overlays — Lower-Third Proof of Concept

**Date:** 2026-03-17
**Scope:** Lottie animation pipeline for [LOWER-THIRD], proof of concept for future overlay animation
**Dependencies:** lottie (Python), Cairo (system), FFmpeg

---

## Problem

Current overlays (lower-thirds, quote cards, etc.) are static Pillow PNGs. They look amateur compared to animated lower-thirds used by professional channels. The formula's visual storyboard bible specifies animations: "red line draws in, name slides from left, role fades in, fade out."

## Solution

New processor `lottie_overlays.py` that creates Lottie animations programmatically, renders to WebM with alpha via Cairo + FFmpeg, and composites onto video segments.

### Pipeline

```
Python (lottie library) → Animation JSON
    ↓ Cairo exporter
PNG frames (temp dir, transparent bg)
    ↓ FFmpeg
WebM VP9 with alpha (single file)
    ↓ FFmpeg overlay filter
Composited onto video
```

### Animation: Lower-Third

**Timing (5 seconds at 30fps = 150 frames):**

| Frames | Time | What happens |
|--------|------|-------------|
| 0-15 | 0-0.5s | Red accent line (#C81E1E) draws in from left, 3px tall, ~600px wide |
| 5-20 | 0.17-0.67s | Name text slides in from left (translateX -200→0) with opacity 0→1 |
| 15-25 | 0.5-0.83s | Role text fades in below name (opacity 0→1) |
| 25-130 | 0.83-4.33s | Hold — everything static |
| 130-150 | 4.33-5.0s | Everything fades out (opacity 1→0) |

**Visual spec (matching existing static lower-third):**
- Position: bottom-left, ~80px from bottom, ~40px from left
- Background bar: semi-transparent black (rgba 0,0,0,0.7), ~600x80px
- Name: white, bold, ~42pt
- Role: grey (#B4B4B4), ~28pt
- Accent line: red (#C81E1E), 3px height, above the bar

### Functions

```python
# lottie_overlays.py

def create_lower_third_animation(
    name: str,
    role: str,
    duration: float = 5.0,
    fps: int = 30,
) -> lottie.objects.Animation:
    """Create an animated lower-third as a Lottie Animation object.

    Returns the in-memory animation — call render_lottie_overlay() to produce video.
    """

def render_lottie_overlay(
    animation: lottie.objects.Animation,
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """Render Lottie animation to WebM with alpha channel.

    Pipeline: Cairo renders PNG frames to temp dir → FFmpeg assembles VP9 WebM.
    """

def overlay_lottie(
    video_path: Path,
    overlay_path: Path,
    output_path: Path,
    start_time: float = 0.0,
) -> Path:
    """Composite a WebM overlay (with alpha) onto video at specified time.

    Uses FFmpeg overlay filter with enable='between(t,start,end)'.
    """

def generate_animated_lower_third(
    name: str,
    role: str,
    output_path: Path,
    duration: float = 5.0,
) -> Path:
    """High-level: create + render an animated lower-third to WebM.

    Convenience function that chains create + render.
    """
```

### Rendering details

**Cairo → PNG frames:**
```python
from lottie.exporters.cairo import export_png

# Render each frame to a temp directory
for frame_num in range(total_frames):
    export_png(animation, f"{temp_dir}/frame_{frame_num:04d}.png", frame_num)
```

**PNG frames → WebM with alpha:**
```bash
ffmpeg -framerate 30 -i frame_%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 output.webm
```

VP9 + yuva420p gives us video with alpha channel. `-auto-alt-ref 0` is required for alpha support in VP9.

**Overlay onto video:**
```bash
ffmpeg -i video.mp4 -i overlay.webm -filter_complex "[1:v]setpts=PTS+{start}/TB[ovr];[0:v][ovr]overlay=enable='between(t,{start},{end})'" output.mp4
```

### Integration

**`--animated` flag on CLI:**
```python
@app.command()
def graphics(
    assembly_guide: str = ...,
    project_dir: str = ...,
    animated: bool = typer.Option(False, "--animated", help="Use Lottie animations for lower-thirds"),
):
```

When `--animated`, lower-thirds produce WebM files in `output/graphics/` instead of PNGs. The filenames change from `lower-third-00-name.png` to `lower-third-00-name.webm`.

**Fallback:** If the `lottie` package is not installed or Cairo rendering fails, fall back to static Pillow PNG with a warning.

### Dependencies

`lottie` is already installed (we verified it works). Cairo is a system dependency — on macOS it's available via `brew install cairo` or often pre-installed. The `lottie` package's Cairo exporter uses `cairo` Python bindings.

Check if Cairo is available at runtime:
```python
def _has_cairo() -> bool:
    try:
        from lottie.exporters.cairo import export_png
        return True
    except ImportError:
        return False
```

Add `lottie>=0.7.0` to `[project.optional-dependencies]` as `animation = ["lottie>=0.7.0"]`.

---

## Files Changed

| File | Change |
|------|--------|
| `processors/lottie_overlays.py` | **New.** Animation creation, Cairo rendering, FFmpeg assembly, overlay compositing. |
| `adapters/cli.py` | Add `--animated` flag to `graphics` command. |
| `pyproject.toml` | Add `animation = ["lottie>=0.7.0"]` optional dependency. |
| `tests/test_lottie_overlays.py` | **New.** Tests for animation creation, rendering (mocked FFmpeg), compositing. |

## Files NOT Changed

- `processors/graphics.py` — Pillow functions unchanged, still the default
- `services/production.py` — no change (animated overlays are opt-in via CLI flag)
- `api/*` — no API changes in this spec
- `web/*` — no frontend changes

## Testing Strategy

- Unit test: `create_lower_third_animation` returns a valid Lottie Animation with correct frame count, layers, keyframes
- Unit test: Animation has the right layer structure (bar, line, name text, role text)
- Unit test: `render_lottie_overlay` with mocked Cairo export + mocked FFmpeg → produces output path
- Unit test: `overlay_lottie` with mocked FFmpeg → correct filter string
- Unit test: `generate_animated_lower_third` chains create + render
- Unit test: `_has_cairo()` returns bool without crashing
- Integration test (if Cairo available): full render of a short animation → verify WebM file exists and has non-zero size

~8 tests total.

## Known Limitations

- Cairo must be installed as a system dependency — not a pure-Python solution
- VP9 WebM encoding is slower than PNG generation (~2-3s per 5-second overlay)
- Only lower-third is animated in this spec — other overlays remain static PNGs
- The Lottie `python-lottie` package is AGPLv3 — acceptable for internal tooling but worth noting
