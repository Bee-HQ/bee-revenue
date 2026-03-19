"""Production pipeline — orchestrates parsing, asset generation, and assembly."""

from __future__ import annotations

import glob as globmod
import json
import re
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
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

    def apply_voice_lock(self, voice_lock=None) -> None:
        """Apply voice lock if no explicit engine/voice was set.

        Args:
            voice_lock: A VoiceLock model instance (from ParsedStoryboard.project.voice_lock),
                        or None if no voice lock is configured.
        """
        if voice_lock is None:
            return
        if self.tts_engine == "edge" and self.tts_voice is None:
            self.tts_engine = voice_lock.engine
            if voice_lock.voice:
                self.tts_voice = voice_lock.voice


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
    storyboard_path: str = ""
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
            storyboard_path=data.get("storyboard_path", data.get("assembly_guide_path", "")),
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


def _derive_segment_type(seg: ParsedSegment) -> str:
    """Derive a segment type string from a ParsedSegment's config layers."""
    has_footage = any(v.type == "FOOTAGE" for v in seg.config.visual)
    has_nar = bool(seg.narration)
    has_real_audio = any(a.type == "REAL_AUDIO" for a in seg.config.audio)
    has_gen_visual = any(v.type in ("GRAPHIC", "MAP", "STOCK", "WAVEFORM") for v in seg.config.visual)
    if has_footage and has_nar:
        return "MIX"
    if has_footage or has_real_audio:
        return "REAL"
    if has_nar:
        return "NAR"
    if has_gen_visual:
        return "GEN"
    return "GEN"


def init_project(
    parsed: ParsedStoryboard,
    config: ProductionConfig,
) -> ProductionState:
    """Initialize a production project from a parsed storyboard.

    Returns a new ProductionState.
    """
    from bee_video_editor.formats.timecodes import format_header_tc

    state = ProductionState(
        storyboard_path="",
        phase="parsed",
    )
    state.segment_statuses = [
        SegmentStatus(
            index=i,
            time_range=f"{seg.start}-{seg.end}",
            segment_type=_derive_segment_type(seg),
        )
        for i, seg in enumerate(parsed.segments)
    ]

    # Create output directories
    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "captions", "final", "previews"]:
        (config.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    state.save(config.state_path)

    return state


def generate_graphics_for_project(
    project: ParsedStoryboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
    animated: bool = False,
) -> ProductionResult:
    """Generate all graphics assets."""
    result = ProductionResult()
    graphics_dir = config.output_dir / "graphics"

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
    for seg in project.segments:
        for entry in seg.config.overlay:
            if entry.type == "LOWER_THIRD":
                name = entry.text or f"Character {lower_third_idx}"
                role = entry.subtext or ""

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

    # Timeline markers (now in overlays)
    timeline_idx = 0
    for seg in project.segments:
        for entry in seg.config.overlay:
            if entry.type == "TIMELINE_MARKER":
                text = entry.date or entry.text or ""
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

    # Financial cards (now in overlays)
    fin_idx = 0
    for seg in project.segments:
        for entry in seg.config.overlay:
            if entry.type == "FINANCIAL_CARD":
                amount = entry.amount or ""
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

    # Quote cards (in overlays)
    quote_idx = 0
    for seg in project.segments:
        for entry in seg.config.overlay:
            if entry.type == "QUOTE_CARD":
                quote_text = entry.quote or ""
                author = entry.author or ""
                if quote_text:
                    out = graphics_dir / f"quote-{quote_idx:02d}-{_slugify(quote_text)[:30]}.png"
                    if out.exists():
                        result.skipped.append(str(out))
                    else:
                        try:
                            gfx.quote_card(quote_text, author, out)
                            result.succeeded.append(out)
                        except Exception as e:
                            result.failed.append(FailedItem(path=str(out), error=str(e)))
                    quote_idx += 1

    return result


def generate_narration_for_project(
    project: ParsedStoryboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
    workers: int = 1,
) -> ProductionResult:
    """Generate TTS narration for all NAR segments."""
    result = ProductionResult()
    narration_dir = config.output_dir / "narration"

    if state:
        state.phase = "narration"
        state.save(config.state_path)

    from bee_video_editor.processors.captions import _clean_text

    # Collect all narration tasks
    tasks = []
    for i, seg in enumerate(project.segments):
        if not seg.narration:
            continue
        nar_text = _clean_text(seg.narration)
        if not nar_text:
            continue
        out = narration_dir / f"nar-{i:03d}-{_slugify(seg.section)[:30]}.mp3"
        if out.exists():
            result.skipped.append(f"narration segment {i} already exists")
            continue
        tasks.append((i, nar_text, out))

    if not tasks:
        return result

    def _generate_one(task):
        idx, text, out_path = task
        generate_narration(
            text=text, output_path=out_path,
            engine=config.tts_engine, voice=config.tts_voice,
        )
        return idx, out_path

    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_generate_one, t): t for t in tasks}
            for future in as_completed(futures):
                task = futures[future]
                idx, _, out_path = task
                try:
                    future.result()
                    result.succeeded.append(out_path)
                except Exception as e:
                    result.failed.append(FailedItem(path=f"segment-{idx}", error=str(e)))
    else:
        # Sequential (original behavior)
        for task in tasks:
            idx, text, out_path = task
            try:
                if state:
                    with state.track(idx, config.state_path):
                        _generate_one(task)
                        result.succeeded.append(out_path)
                else:
                    _generate_one(task)
                    result.succeeded.append(out_path)
            except Exception as e:
                result.failed.append(FailedItem(path=f"segment-{idx}", error=str(e)))

    return result


def trim_source_footage(
    project: ParsedStoryboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Trim source footage based on storyboard visual layers with src."""
    result = ProductionResult()
    segments_dir = config.output_dir / "segments"

    if state:
        state.phase = "trimming"
        state.save(config.state_path)

    for i, seg in enumerate(project.segments):
        for v in seg.config.visual:
            if not v.src:
                continue

            file_path = v.src
            start = v.tc_in   # precise format "HH:MM:SS.mmm" or None
            end = v.out        # precise format or None

            # Resolve path relative to footage_dir
            rel_path = file_path.replace("footage/", "")
            pattern = str(config.footage_dir / rel_path)
            matches = globmod.glob(pattern)
            if not matches:
                result.failed.append(FailedItem(path=file_path, error="No matching source file found"))
                continue
            source_file = matches[0]

            slug = _slugify(Path(file_path).stem)[:40]
            out = segments_dir / f"trim-{i:03d}-{slug}.mp4"
            if out.exists():
                result.skipped.append(str(out))
            else:
                try:
                    trim(source_file, out, start=start, end=end)
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
    parsed: ParsedStoryboard,
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
    workers: int = 1,
) -> PipelineResult:
    """Run the full production pipeline: init -> graphics -> captions -> narration -> trim -> assemble.

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
            r = generate_graphics_for_project(parsed, config, animated=animated)
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
            # extract_caption_segments still uses old Storyboard model (Task 6 migrates it).
            # For now, skip if it fails due to type mismatch.
            try:
                segments = extract_caption_segments(parsed)
            except (TypeError, AttributeError):
                return "skipped (pending captions migration)"
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
            r = generate_narration_for_project(parsed, config, workers=workers)
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
            r = trim_source_footage(parsed, config)
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


def generate_preview(
    media_path: Path,
    output_path: Path,
    width: int = 640,
    height: int = 360,
    max_duration: float = 5.0,
) -> Path:
    """Generate a low-res preview clip from a media file.

    For video: first 5 seconds at 360p.
    For images: convert to 5-second 360p video with Ken Burns.
    """
    import subprocess

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = media_path.suffix.lower()

    if suffix in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
        # Image -> video with Ken Burns
        image_to_video(media_path, output_path, duration=max_duration, ken_burns="zoom_in")
        # Scale down
        scaled = output_path.parent / f"_scaled_{output_path.name}"
        normalize_format(output_path, scaled, width, height, 30)
        scaled.rename(output_path)
    else:
        # Video -> first N seconds at low res
        cmd = [
            "ffmpeg", "-y",
            "-i", str(media_path),
            "-t", str(max_duration),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "64k",
            "-y", str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Preview generation failed: {result.stderr[:300]}")

    return output_path


def generate_all_previews(
    storyboard: ParsedStoryboard,
    project_dir: Path,
) -> ProductionResult:
    """Generate preview clips for all segments with assigned media."""
    result = ProductionResult()
    previews_dir = project_dir / "output" / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    for seg in storyboard.segments:
        # Look for primary visual with src assigned
        media_path_str = seg.config.visual[0].src if seg.config.visual else None
        if not media_path_str:
            continue

        media_path = Path(media_path_str)
        if not media_path.exists():
            result.failed.append(FailedItem(path=media_path_str, error="file not found"))
            continue

        preview_path = previews_dir / f"{seg.id}.mp4"
        if preview_path.exists():
            result.skipped.append(f"{seg.id} already has preview")
            continue

        try:
            generate_preview(media_path, preview_path)
            result.succeeded.append(preview_path)
        except Exception as e:
            result.failed.append(FailedItem(path=str(media_path), error=str(e)))

    return result


def rough_cut_export(
    project: ParsedStoryboard,
    config: ProductionConfig,
) -> Path | None:
    """Export a fast 720p rough cut — no grading, no transitions.

    Collects assigned media (visual[0].src) from each segment, normalizes to
    720p/30fps, and concatenates. Returns output path or None if no media.
    """
    rough_dir = config.output_dir / "rough"
    rough_dir.mkdir(parents=True, exist_ok=True)

    # Collect assigned clips in segment order
    clips = []
    for seg in project.segments:
        media_path = seg.config.visual[0].src if seg.config.visual else None
        if not media_path or not Path(media_path).exists():
            continue
        clips.append((seg.id, Path(media_path)))

    if not clips:
        return None

    # Normalize each to 720p
    normalized = []
    norm_dir = rough_dir / "normalized"
    norm_dir.mkdir(parents=True, exist_ok=True)

    for seg_id, clip_path in clips:
        out_path = norm_dir / f"{seg_id}.mp4"
        if not out_path.exists():
            normalize_format(clip_path, out_path, width=1280, height=720, fps=30)
        normalized.append(out_path)

    # Concat
    output_path = rough_dir / "rough_cut.mp4"
    concat_segments(normalized, output_path, reencode=True)
    return output_path


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')
