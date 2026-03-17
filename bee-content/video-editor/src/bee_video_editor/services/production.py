"""Production pipeline — orchestrates parsing, asset generation, and assembly."""

from __future__ import annotations

import glob as globmod
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bee_video_editor.models import Project, Segment, SegmentType
from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
from bee_video_editor.processors import graphics as gfx
from bee_video_editor.processors.ffmpeg import (
    FFmpegError,
    concat_segments,
    concat_with_transitions,
    image_to_video,
    normalize_format,
    normalize_loudness,
    overlay_png,
    trim,
)
from bee_video_editor.processors.tts import generate_narration


@dataclass
class FailedItem:
    """A single failed processing step."""
    path: str
    error: str


@dataclass
class ProductionResult:
    """Structured return from every production function."""
    succeeded: list[Path] = field(default_factory=list)
    failed: list[FailedItem] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0


@dataclass
class ProductionConfig:
    """Configuration for a production run."""
    project_dir: Path                # Root directory for the project
    footage_dir: Path | None = None  # Where source footage lives
    output_dir: Path | None = None   # Where to write output
    tts_engine: str = "edge"
    tts_voice: str | None = None
    width: int = 1920
    height: int = 1080
    fps: int = 30
    target_lufs: float = -14.0

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = self.project_dir / "output"
        if self.footage_dir is None:
            self.footage_dir = self.project_dir / "footage"

    @property
    def state_path(self) -> Path:
        return self.output_dir / "production_state.json"


@dataclass
class SegmentStatus:
    """Track the production status of a single segment."""
    index: int
    time_range: str
    segment_type: str
    status: str = "pending"  # pending, processing, done, error, skipped
    output_file: str | None = None
    error: str | None = None


@dataclass
class ProductionState:
    """Persistent state for a production run."""
    assembly_guide_path: str = ""
    segment_statuses: list[SegmentStatus] = field(default_factory=list)
    phase: str = "init"  # init, parsing, assets, trimming, compositing, assembly, done

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> ProductionState:
        with open(path) as f:
            data = json.load(f)
        state = cls(
            assembly_guide_path=data["assembly_guide_path"],
            phase=data["phase"],
        )
        state.segment_statuses = [
            SegmentStatus(**s) for s in data.get("segment_statuses", [])
        ]
        return state


def init_project(
    assembly_guide_path: str | Path,
    config: ProductionConfig,
) -> tuple[Project, ProductionState]:
    """Initialize a production project from an assembly guide.

    Returns the parsed Project and a new ProductionState.
    """
    project = parse_assembly_guide(assembly_guide_path)

    state = ProductionState(
        assembly_guide_path=str(assembly_guide_path),
        phase="parsed",
    )
    state.segment_statuses = [
        SegmentStatus(
            index=i,
            time_range=f"{seg.start}-{seg.end}",
            segment_type=seg.segment_type.value,
        )
        for i, seg in enumerate(project.segments)
    ]

    # Create output directories
    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "final"]:
        (config.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    state_path = config.output_dir / "production_state.json"
    state.save(state_path)

    return project, state


def generate_graphics_for_project(
    project: Project,
    config: ProductionConfig,
) -> list[Path]:
    """Generate all graphics assets from project pre-production list."""
    graphics_dir = config.output_dir / "graphics"
    generated = []

    # Generate lower thirds from segments that mention "lower third"
    lower_third_idx = 0
    for seg in project.segments:
        visual_lower = seg.visual.lower()
        if "lower third" in visual_lower:
            # Extract name and role from visual description
            match = re.search(r'lower third[^"]*"([^"]+)"', seg.visual, re.IGNORECASE)
            if match:
                parts = match.group(1).split(" — ")
                name = parts[0].strip()
                role = parts[1].strip() if len(parts) > 1 else ""
            else:
                # Try to extract from quotes in the visual field
                name = f"Character {lower_third_idx}"
                role = ""

            out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{_slugify(name)}.png"
            if not out.exists():
                gfx.lower_third(name, role, out)
                generated.append(out)
            lower_third_idx += 1

    # Generate timeline markers
    timeline_idx = 0
    for seg in project.segments:
        if seg.segment_type == SegmentType.GEN and "TEXT-TIMELINE" in seg.visual:
            match = re.search(r'TEXT-TIMELINE[:\s]*"?([^"]+)"?', seg.visual)
            if match:
                text = match.group(1).strip()
                out = graphics_dir / f"timeline-{timeline_idx:02d}-{_slugify(text)[:30]}.png"
                if not out.exists():
                    gfx.timeline_marker(text, "", out)
                    generated.append(out)
                timeline_idx += 1

    # Generate financial cards
    fin_idx = 0
    for seg in project.segments:
        if "TEXT-FINANCIAL" in seg.visual:
            match = re.search(r'TEXT-FINANCIAL\s*"?([^"]+)"?', seg.visual)
            if match:
                amount = match.group(1).strip()
                desc = ""
                out = graphics_dir / f"financial-{fin_idx:02d}-{_slugify(amount)[:20]}.png"
                if not out.exists():
                    gfx.financial_card(amount, desc, out)
                    generated.append(out)
                fin_idx += 1

    return generated


def generate_narration_for_project(
    project: Project,
    config: ProductionConfig,
) -> list[Path]:
    """Generate TTS narration for all NAR and MIX segments."""
    narration_dir = config.output_dir / "narration"
    generated = []

    for i, seg in enumerate(project.segments):
        if seg.segment_type not in (SegmentType.NAR, SegmentType.MIX):
            continue

        # Extract narrator text from audio field
        nar_text = _extract_narrator_text(seg.audio)
        if not nar_text:
            continue

        out = narration_dir / f"nar-{i:03d}-{_slugify(seg.subsection or seg.section)[:30]}.mp3"
        if not out.exists():
            generate_narration(
                text=nar_text,
                output_path=out,
                engine=config.tts_engine,
                voice=config.tts_voice,
            )
            generated.append(out)

    return generated


def trim_source_footage(
    project: Project,
    config: ProductionConfig,
) -> list[Path]:
    """Trim source footage based on assembly guide trim notes."""
    segments_dir = config.output_dir / "segments"
    trimmed = []

    for note in project.trim_notes:
        # Resolve glob pattern to actual file
        pattern = str(config.footage_dir / note.source_file.replace("footage/", ""))
        matches = globmod.glob(pattern)
        if not matches:
            continue
        source = matches[0]

        for j, t in enumerate(note.trims):
            slug = _slugify(t.label)[:40]
            out = segments_dir / f"trim-{slug}-{j:02d}.mp4"
            if not out.exists():
                try:
                    trim(source, out, start=t.start, end=t.duration)
                    trimmed.append(out)
                except FFmpegError:
                    pass  # Skip trims that fail (missing footage etc.)

    return trimmed


def normalize_all_segments(config: ProductionConfig) -> list[Path]:
    """Normalize all segments to consistent format."""
    segments_dir = config.output_dir / "segments"
    normalized_dir = config.output_dir / "normalized"
    normalized = []

    for seg_file in sorted(segments_dir.glob("*.mp4")):
        out = normalized_dir / seg_file.name
        if not out.exists():
            try:
                normalize_format(seg_file, out, config.width, config.height, config.fps)
                normalized.append(out)
            except FFmpegError:
                pass

    return normalized


def assemble_final(
    config: ProductionConfig,
    transition: str | None = None,
    transition_duration: float = 1.0,
) -> Path | None:
    """Concatenate all composited/normalized segments into the final video.

    Args:
        transition: Optional xfade transition name (e.g. "fade", "dissolve").
                    If None, uses simple concatenation.
        transition_duration: Duration of each transition in seconds.
    """
    composited_dir = config.output_dir / "composited"
    normalized_dir = config.output_dir / "normalized"
    final_dir = config.output_dir / "final"

    # Prefer composited segments, fall back to normalized
    segments = sorted(composited_dir.glob("*.mp4"))
    if not segments:
        segments = sorted(normalized_dir.glob("*.mp4"))

    if not segments:
        return None

    output = final_dir / "final_assembled.mp4"

    if transition and len(segments) >= 2:
        concat_with_transitions(segments, output, transition=transition, transition_duration=transition_duration)
    else:
        concat_segments(segments, output, reencode=True)

    return output


def _extract_narrator_text(audio_field: str) -> str:
    """Extract narrator text from an assembly guide audio cell.

    Handles formats like:
        'NAR: "This is Alex Murdaugh..." + dark ambient music fades in'
        'NAR: "Something here"'
    """
    # Look for NAR: "text" pattern
    match = re.search(r'NAR:\s*"([^"]*)"', audio_field)
    if match:
        return match.group(1)

    # Look for NAR: text (without quotes)
    match = re.search(r'NAR:\s*(.+?)(?:\s*\+|\s*$)', audio_field)
    if match:
        text = match.group(1).strip()
        text = text.strip('"').strip('"')
        return text

    return ""


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')
