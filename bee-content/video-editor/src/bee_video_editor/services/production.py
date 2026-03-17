"""Production pipeline — orchestrates parsing, asset generation, and assembly."""

from __future__ import annotations

import glob as globmod
import json
import re
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models import Project, Segment, SegmentType
from bee_video_editor.models_storyboard import Storyboard
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
class PipelineStep:
    """A single step in the full production pipeline."""
    name: str
    status: str = "pending"  # pending, running, done, skipped, failed
    message: str = ""


@dataclass
class PipelineResult:
    """Result from run_full_pipeline."""
    steps: list[PipelineStep] = field(default_factory=list)
    output_path: Path | None = None

    @property
    def ok(self) -> bool:
        return all(s.status in ("done", "skipped") for s in self.steps)


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

    @contextmanager
    def track(self, index: int, state_path: Path):
        """Track segment processing. Sets status to processing/done/error and saves."""
        if index < 0 or index >= len(self.segment_statuses):
            raise ValueError(
                f"Segment index {index} out of range (0-{len(self.segment_statuses) - 1})"
            )
        seg = self.segment_statuses[index]
        seg.status = "processing"
        seg.error = None
        self.save(state_path)
        try:
            yield seg
            seg.status = "done"
        except Exception as e:
            seg.status = "error"
            seg.error = str(e)[:200]
            raise
        finally:
            self.save(state_path)


def _ensure_storyboard(source: Project | Storyboard) -> Storyboard:
    """Convert Project to Storyboard if needed."""
    if isinstance(source, Storyboard):
        return source
    return assembly_guide_to_storyboard(source)


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
    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "captions", "final"]:
        (config.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    state.save(config.state_path)

    return project, state


def generate_graphics_for_project(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
    animated: bool = False,
) -> ProductionResult:
    """Generate all graphics assets."""
    result = ProductionResult()
    graphics_dir = config.output_dir / "graphics"
    sb = _ensure_storyboard(project)

    if state:
        state.phase = "graphics"
        state.save(config.state_path)

    # Resolve animated lower-third renderer
    _animated_lower_third = None
    if animated:
        try:
            from bee_video_editor.processors.lottie_overlays import generate_animated_lower_third
            _animated_lower_third = generate_animated_lower_third
        except ImportError:
            pass  # fall back to static

    lower_third_idx = 0
    for seg in sb.segments:
        for entry in seg.overlay:
            if entry.content_type == "LOWER-THIRD":
                match = re.search(r'"([^"]+)"', entry.content)
                if match:
                    parts = match.group(1).split(" — ")
                    name = parts[0].strip()
                    role = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = f"Character {lower_third_idx}"
                    role = ""

                if _animated_lower_third is not None:
                    out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{_slugify(name)}.webm"
                else:
                    out = graphics_dir / f"lower-third-{lower_third_idx:02d}-{_slugify(name)}.png"

                if out.exists():
                    result.skipped.append(str(out))
                else:
                    try:
                        if _animated_lower_third is not None:
                            _animated_lower_third(name, role, out)
                        else:
                            gfx.lower_third(name, role, out)
                        result.succeeded.append(out)
                    except Exception as e:
                        result.failed.append(FailedItem(path=str(out), error=str(e)))
                lower_third_idx += 1

    # Timeline markers
    timeline_idx = 0
    for seg in sb.segments:
        for entry in seg.visual:
            if entry.content_type == "TIMELINE-MARKER":
                text = entry.content.strip().strip('"')
                if text:
                    out = graphics_dir / f"timeline-{timeline_idx:02d}-{_slugify(text)[:30]}.png"
                    if out.exists():
                        result.skipped.append(str(out))
                    else:
                        try:
                            gfx.timeline_marker(text, "", out)
                            result.succeeded.append(out)
                        except Exception as e:
                            result.failed.append(FailedItem(path=str(out), error=str(e)))
                    timeline_idx += 1

    # Financial cards
    fin_idx = 0
    for seg in sb.segments:
        for entry in seg.visual:
            if entry.content_type == "FINANCIAL-CARD":
                amount = entry.content.strip().strip('"')
                if amount:
                    out = graphics_dir / f"financial-{fin_idx:02d}-{_slugify(amount)[:20]}.png"
                    if out.exists():
                        result.skipped.append(str(out))
                    else:
                        try:
                            gfx.financial_card(amount, "", out)
                            result.succeeded.append(out)
                        except Exception as e:
                            result.failed.append(FailedItem(path=str(out), error=str(e)))
                    fin_idx += 1

    return result


def generate_narration_for_project(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Generate TTS narration for all NAR segments."""
    result = ProductionResult()
    narration_dir = config.output_dir / "narration"
    sb = _ensure_storyboard(project)

    if state:
        state.phase = "narration"
        state.save(config.state_path)

    from bee_video_editor.processors.captions import _clean_text

    for i, seg in enumerate(sb.segments):
        for entry in seg.audio:
            if entry.content_type != "NAR":
                continue

            nar_text = _clean_text(entry.content)
            if not nar_text:
                continue

            out = narration_dir / f"nar-{i:03d}-{_slugify(seg.subsection or seg.section)[:30]}.mp3"
            if out.exists():
                result.skipped.append(f"narration segment {i} already exists")
                continue

            try:
                if state:
                    with state.track(i, config.state_path):
                        generate_narration(
                            text=nar_text, output_path=out,
                            engine=config.tts_engine, voice=config.tts_voice,
                        )
                        result.succeeded.append(out)
                else:
                    generate_narration(
                        text=nar_text, output_path=out,
                        engine=config.tts_engine, voice=config.tts_voice,
                    )
                    result.succeeded.append(out)
            except Exception as e:
                result.failed.append(FailedItem(path=f"segment-{i}", error=str(e)))

    return result


def trim_source_footage(
    project: Project | Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Trim source footage. Only works with Project (assembly guide) — Storyboard returns empty result."""
    result = ProductionResult()

    # Storyboard has no trim notes — return empty
    if isinstance(project, Storyboard):
        return result

    segments_dir = config.output_dir / "segments"

    if state:
        state.phase = "trimming"
        state.save(config.state_path)

    for note in project.trim_notes:
        # Resolve glob pattern to actual file
        pattern = str(config.footage_dir / note.source_file.replace("footage/", ""))
        matches = globmod.glob(pattern)
        if not matches:
            result.failed.append(FailedItem(path=note.source_file, error="No matching source file found"))
            continue
        source = matches[0]

        for j, t in enumerate(note.trims):
            slug = _slugify(t.label)[:40]
            out = segments_dir / f"trim-{slug}-{j:02d}.mp4"
            if out.exists():
                result.skipped.append(str(out))
            else:
                try:
                    trim(source, out, start=t.start, end=t.duration)
                    result.succeeded.append(out)
                except Exception as e:
                    result.failed.append(FailedItem(path=str(out), error=str(e)))

    return result


def normalize_all_segments(
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Normalize all segments to consistent format."""
    segments_dir = config.output_dir / "segments"
    normalized_dir = config.output_dir / "normalized"
    result = ProductionResult()

    if state:
        state.phase = "normalizing"
        state.save(config.state_path)

    for seg_file in sorted(segments_dir.glob("*.mp4")):
        out = normalized_dir / seg_file.name
        if out.exists():
            result.skipped.append(str(out))
        else:
            try:
                normalize_format(seg_file, out, config.width, config.height, config.fps)
                result.succeeded.append(out)
            except Exception as e:
                result.failed.append(FailedItem(path=str(out), error=str(e)))

    return result


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

    # Burn in captions if ASS file exists
    captions_path = config.output_dir / "captions" / "captions.ass"
    if output and captions_path.exists():
        from bee_video_editor.processors.captions import burn_captions
        captioned = output.parent / "final_with_captions.mp4"
        try:
            burn_captions(output, captions_path, captioned)
            return captioned
        except RuntimeError:
            pass  # Fall through to return uncaptioned video

    return output


def run_full_pipeline(
    storyboard_path: Path,
    config: ProductionConfig,
    skip_graphics: bool = False,
    skip_captions: bool = False,
    skip_narration: bool = False,
    skip_trim: bool = False,
    caption_style: str = "karaoke",
    transition: str | None = None,
    transition_duration: float = 1.0,
    animated: bool = False,
    on_step: callable | None = None,
) -> PipelineResult:
    """Run the full production pipeline: init → graphics → captions → narration → trim → assemble.

    Steps that already have output are skipped automatically (idempotent).
    Stops on the first failure. Completed steps are not re-run on retry.
    """
    result = PipelineResult(steps=[])

    def _step(name, fn):
        step = PipelineStep(name=name, status="running")
        result.steps.append(step)
        if on_step:
            on_step(name, "running", "")
        try:
            msg = fn()
            step.status = "done"
            step.message = msg or ""
            if on_step:
                on_step(name, "done", step.message)
        except Exception as e:
            step.status = "failed"
            step.message = str(e)[:200]
            if on_step:
                on_step(name, "failed", step.message)
            return False
        return True

    # Parse storyboard
    from bee_video_editor.parsers.storyboard import parse_storyboard
    storyboard = parse_storyboard(storyboard_path)

    # Step 1: Init
    def do_init():
        for subdir in ["segments", "normalized", "composited", "graphics", "narration", "captions", "final"]:
            (config.output_dir / subdir).mkdir(parents=True, exist_ok=True)
        return "directories created"

    if not _step("init", do_init):
        return result

    # Step 2: Graphics
    if skip_graphics:
        result.steps.append(PipelineStep(name="graphics", status="skipped", message="--skip-graphics"))
    elif list((config.output_dir / "graphics").glob("*.png")):
        result.steps.append(PipelineStep(name="graphics", status="skipped", message="already exists"))
    else:
        def do_graphics():
            r = generate_graphics_for_project(storyboard, config, animated=animated)
            return f"{len(r.succeeded)} generated, {len(r.failed)} failed"
        if not _step("graphics", do_graphics):
            return result

    # Step 3: Captions
    if skip_captions:
        result.steps.append(PipelineStep(name="captions", status="skipped", message="--skip-captions"))
    elif (config.output_dir / "captions" / "captions.ass").exists():
        result.steps.append(PipelineStep(name="captions", status="skipped", message="already exists"))
    else:
        def do_captions():
            from bee_video_editor.processors.captions import extract_caption_segments, generate_captions_estimated
            segments = extract_caption_segments(storyboard)
            if not segments:
                return "no captionable segments"
            out = config.output_dir / "captions" / "captions.ass"
            generate_captions_estimated(segments, out, style=caption_style)
            return f"{len(segments)} segments"
        if not _step("captions", do_captions):
            return result

    # Step 4: Narration
    if skip_narration:
        result.steps.append(PipelineStep(name="narration", status="skipped", message="--skip-narration"))
    elif list((config.output_dir / "narration").glob("*.mp3")):
        result.steps.append(PipelineStep(name="narration", status="skipped", message="already exists"))
    else:
        def do_narration():
            r = generate_narration_for_project(storyboard, config)
            return f"{len(r.succeeded)} clips, {len(r.failed)} failed"
        if not _step("narration", do_narration):
            return result

    # Step 5: Trim
    if skip_trim:
        result.steps.append(PipelineStep(name="trim", status="skipped", message="--skip-trim"))
    elif list((config.output_dir / "segments").glob("*.mp4")):
        result.steps.append(PipelineStep(name="trim", status="skipped", message="already exists"))
    else:
        def do_trim():
            r = trim_source_footage(storyboard, config)
            return f"{len(r.succeeded)} trimmed"
        if not _step("trim", do_trim):
            return result

    # Step 6: Assemble
    def do_assemble():
        out = assemble_final(config, transition=transition, transition_duration=transition_duration)
        if out:
            result.output_path = out
            return str(out)
        return "no segments to assemble"
    if not _step("assemble", do_assemble):
        return result

    return result


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
