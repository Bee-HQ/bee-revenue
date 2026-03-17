"""CLI adapter for bee-video-editor — typer commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="bee-video",
    help="AI-assisted video production from assembly guides.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def parse(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
):
    """Parse an assembly guide and show project summary."""
    from bee_video_editor.parsers.assembly_guide import parse_assembly_guide

    project = parse_assembly_guide(assembly_guide)
    summary = project.summary()

    console.print(f"\n[bold]{project.title}[/bold]")
    console.print(f"Duration: {project.total_duration} | {project.resolution} | {project.format}")
    console.print(f"Total segments: {summary['total_segments']}")
    console.print()

    # Segment type breakdown
    table = Table(title="Segment Types")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Duration", justify="right")

    for seg_type, count in summary["segment_type_counts"].items():
        dur = summary["segment_type_durations_seconds"].get(seg_type, 0)
        mins = dur // 60
        secs = dur % 60
        table.add_row(seg_type, str(count), f"{mins}m {secs}s")

    console.print(table)

    # Sections
    console.print("\n[bold]Sections:[/bold]")
    for section in summary["sections"]:
        seg_count = len(project.segments_in_section(section))
        console.print(f"  {section} ({seg_count} segments)")

    # Pre-production
    pp_done = summary["pre_production_done"]
    pp_total = summary["pre_production_assets"]
    console.print(f"\n[bold]Pre-production:[/bold] {pp_done}/{pp_total} assets ready")

    # Trim notes
    console.print(f"[bold]Trim notes:[/bold] {summary['trim_notes']} source files")

    # Post checklist
    pc_done = summary["post_checklist_done"]
    pc_total = summary["post_checklist_items"]
    console.print(f"[bold]Post-assembly:[/bold] {pc_done}/{pc_total} checklist items done")
    console.print()


@app.command()
def segments(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    section: str | None = typer.Option(None, "--section", "-s", help="Filter by section name"),
    segment_type: str | None = typer.Option(None, "--type", "-t", help="Filter by type (NAR/REAL/GEN/MIX)"),
):
    """List all segments from the assembly guide."""
    from bee_video_editor.models import SegmentType
    from bee_video_editor.parsers.assembly_guide import parse_assembly_guide

    project = parse_assembly_guide(assembly_guide)

    segs = project.segments
    if section:
        segs = [s for s in segs if section.lower() in s.section.lower()]
    if segment_type:
        try:
            st = SegmentType(segment_type.upper())
            segs = [s for s in segs if s.segment_type == st]
        except ValueError:
            console.print(f"[red]Unknown type: {segment_type}[/red]")
            raise typer.Exit(1)

    table = Table(title=f"Segments ({len(segs)} total)")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Time", style="cyan")
    table.add_column("Dur", justify="right")
    table.add_column("Type", style="bold")
    table.add_column("Section")
    table.add_column("Visual", max_width=40, overflow="ellipsis")
    table.add_column("Audio", max_width=40, overflow="ellipsis")

    type_colors = {
        "NAR": "green",
        "REAL": "yellow",
        "GEN": "blue",
        "MIX": "magenta",
        "SFX": "red",
        "SPONSOR": "dim",
    }

    for i, seg in enumerate(segs):
        color = type_colors.get(seg.segment_type.value, "white")
        table.add_row(
            str(i),
            f"{seg.start}-{seg.end}",
            seg.duration_str,
            f"[{color}]{seg.segment_type.value}[/{color}]",
            seg.subsection or seg.section,
            seg.visual[:40],
            seg.audio[:40],
        )

    console.print(table)


@app.command()
def init(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Project root directory"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine (edge/kokoro/openai)"),
):
    """Initialize a production project from an assembly guide."""
    from bee_video_editor.services.production import ProductionConfig, init_project

    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
    )
    project, state = init_project(assembly_guide, config)

    console.print(f"\n[bold green]Project initialized![/bold green]")
    console.print(f"Title: {project.title}")
    console.print(f"Segments: {project.total_segments}")
    console.print(f"Output: {config.output_dir}")
    console.print(f"State: {config.output_dir / 'production_state.json'}")
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print("  bee-video graphics <assembly-guide>  — Generate graphics assets")
    console.print("  bee-video narration <assembly-guide>  — Generate TTS narration")
    console.print("  bee-video trim <assembly-guide>       — Trim source footage")
    console.print("  bee-video assemble <assembly-guide>   — Final assembly")


@app.command()
def graphics(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    animated: bool = typer.Option(False, "--animated", help="Use Lottie animations for lower-thirds (requires lottie + Cairo)"),
):
    """Generate all graphics assets (lower thirds, timelines, etc.)."""
    from bee_video_editor.services.production import ProductionConfig, generate_graphics_for_project

    config = ProductionConfig(project_dir=Path(project_dir))
    project = _load_project(assembly_guide)

    if animated:
        try:
            from bee_video_editor.processors.lottie_overlays import _has_cairo

            console.print("[bold]Generating graphics (animated lower-thirds)...[/bold]")
            if not _has_cairo():
                console.print("[yellow]Cairo not available — animated lower-thirds will require Cairo for full rendering.[/yellow]")
        except ImportError:
            console.print("[yellow]lottie package not installed — falling back to static PNGs.[/yellow]")
            console.print("[dim]Install with: uv sync --extra animation[/dim]")
            animated = False

    if not animated:
        console.print("[bold]Generating graphics...[/bold]")

    result = generate_graphics_for_project(project, config, animated=animated)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    for g in result.succeeded:
        console.print(f"  {g}")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")


@app.command()
def narration(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine (edge/kokoro/openai)"),
    voice: str | None = typer.Option(None, "--voice", "-v", help="Voice ID"),
):
    """Generate TTS narration for all narrator segments."""
    from bee_video_editor.services.production import ProductionConfig, generate_narration_for_project

    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
        tts_voice=voice,
    )
    project = _load_project(assembly_guide)

    console.print(f"[bold]Generating narration ({tts_engine})...[/bold]")
    result = generate_narration_for_project(project, config)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    for g in result.succeeded:
        console.print(f"  {g}")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")


@app.command()
def trim_footage(
    assembly_guide: str = typer.Argument(..., help="Path to assembly guide markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    footage_dir: str | None = typer.Option(None, "--footage", "-f", help="Footage directory"),
):
    """Trim source footage based on assembly guide trim notes."""
    from bee_video_editor.services.production import ProductionConfig, trim_source_footage

    config = ProductionConfig(
        project_dir=Path(project_dir),
        footage_dir=Path(footage_dir) if footage_dir else None,
    )
    project = _load_project(assembly_guide)

    console.print("[bold]Trimming source footage...[/bold]")
    result = trim_source_footage(project, config)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    for g in result.succeeded:
        console.print(f"  {g}")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")


@app.command()
def assemble(
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    transition_name: str | None = typer.Option(None, "--transition", "-t", help="Apply xfade transition between segments"),
    transition_duration: float = typer.Option(1.0, "--transition-duration", help="Transition duration (seconds)"),
):
    """Assemble all segments into the final video."""
    from bee_video_editor.services.production import ProductionConfig, assemble_final

    config = ProductionConfig(project_dir=Path(project_dir))

    console.print("[bold]Assembling final video...[/bold]")
    result = assemble_final(config, transition=transition_name, transition_duration=transition_duration)

    if result:
        console.print(f"[bold green]Done! Final video: {result}[/bold green]")
    else:
        console.print("[red]No segments found to assemble. Run trim/graphics/narration first.[/red]")


@app.command()
def status(
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Show production status."""
    from bee_video_editor.services.production import ProductionState

    state_path = Path(project_dir) / "output" / "production_state.json"
    if not state_path.exists():
        console.print("[red]No project initialized. Run: bee-video init <assembly-guide>[/red]")
        raise typer.Exit(1)

    state = ProductionState.load(state_path)

    table = Table(title="Production Status")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")

    counts = {}
    for seg in state.segment_statuses:
        counts[seg.status] = counts.get(seg.status, 0) + 1

    status_colors = {
        "pending": "dim",
        "processing": "yellow",
        "done": "green",
        "error": "red",
        "skipped": "dim",
    }

    for s, count in counts.items():
        color = status_colors.get(s, "white")
        table.add_row(f"[{color}]{s}[/{color}]", str(count))

    console.print(table)
    console.print(f"\nPhase: [bold]{state.phase}[/bold]")

    # Show output directory contents
    output_dir = Path(project_dir) / "output"
    for subdir in ["graphics", "narration", "segments", "normalized", "composited", "final"]:
        d = output_dir / subdir
        if d.exists():
            files = list(d.glob("*"))
            if files:
                console.print(f"  {subdir}/: {len(files)} files")


@app.command()
def effects(
    input_file: str = typer.Argument(..., help="Input video file"),
    output_file: str = typer.Argument(..., help="Output video file"),
    color: str | None = typer.Option(None, "--color", "-c", help="Color grade preset"),
    speed_factor: float | None = typer.Option(None, "--speed", help="Speed factor (0.25-4.0)"),
    text: str | None = typer.Option(None, "--text", help="Burn text onto video"),
    text_position: str = typer.Option("bottom", "--text-pos", help="Text position (top/center/bottom)"),
    text_start: float | None = typer.Option(None, "--text-start", help="Text start time (seconds)"),
    text_end: float | None = typer.Option(None, "--text-end", help="Text end time (seconds)"),
    fade: bool = typer.Option(False, "--fade", help="Add 1s fade in/out"),
):
    """Apply effects to a video clip (color grade, speed, text, fade)."""
    from bee_video_editor.processors.ffmpeg import (
        COLOR_GRADE_PRESETS,
        add_fade,
        color_grade,
        drawtext,
        speed,
    )

    current_input = input_file
    result = None

    if color:
        if color not in COLOR_GRADE_PRESETS:
            console.print(f"[red]Unknown preset: {color}[/red]")
            console.print(f"[dim]Available: {', '.join(sorted(COLOR_GRADE_PRESETS))}[/dim]")
            raise typer.Exit(1)
        tmp = output_file if not (speed_factor or text or fade) else str(Path(output_file).with_suffix(".color.mp4"))
        result = color_grade(current_input, tmp, preset=color)
        current_input = str(result)
        console.print(f"[green]Applied color grade: {color}[/green]")

    if speed_factor:
        tmp = output_file if not (text or fade) else str(Path(output_file).with_suffix(".speed.mp4"))
        result = speed(current_input, tmp, factor=speed_factor)
        current_input = str(result)
        console.print(f"[green]Applied speed: {speed_factor}x[/green]")

    if text:
        pos_map = {"top": "50", "center": "(h-th)/2", "bottom": "h-th-50"}
        y = pos_map.get(text_position, "h-th-50")
        tmp = output_file if not fade else str(Path(output_file).with_suffix(".text.mp4"))
        result = drawtext(current_input, tmp, text=text, y=y, start=text_start, end=text_end, box=True)
        current_input = str(result)
        console.print(f"[green]Applied text overlay[/green]")

    if fade:
        result = add_fade(current_input, output_file)
        console.print(f"[green]Applied fade in/out[/green]")

    if result:
        # Clean up intermediate files
        for suffix in [".color.mp4", ".speed.mp4", ".text.mp4"]:
            tmp = Path(output_file).with_suffix(suffix)
            if tmp.exists() and str(tmp) != output_file:
                tmp.unlink()
        console.print(f"[bold green]Output: {output_file}[/bold green]")
    else:
        console.print("[yellow]No effects specified. Use --color, --speed, --text, or --fade.[/yellow]")


@app.command()
def transition(
    clip_a: str = typer.Argument(..., help="First clip"),
    clip_b: str = typer.Argument(..., help="Second clip"),
    output_file: str = typer.Argument(..., help="Output file"),
    name: str = typer.Option("fade", "--name", "-n", help="Transition name"),
    duration: float = typer.Option(1.0, "--duration", "-d", help="Transition duration (seconds)"),
):
    """Apply a transition between two clips using xfade."""
    from bee_video_editor.processors.ffmpeg import XFADE_TRANSITIONS, xfade

    if name not in XFADE_TRANSITIONS:
        console.print(f"[red]Unknown transition: {name}[/red]")
        console.print(f"[dim]Available: {', '.join(XFADE_TRANSITIONS[:15])}...[/dim]")
        raise typer.Exit(1)

    console.print(f"[bold]Applying {name} transition ({duration}s)...[/bold]")
    result = xfade(clip_a, clip_b, output_file, transition=name, duration=duration)
    console.print(f"[bold green]Output: {result}[/bold green]")


@app.command()
def list_effects():
    """List all available effects, transitions, and color presets."""
    from bee_video_editor.processors.ffmpeg import COLOR_GRADE_PRESETS, XFADE_TRANSITIONS

    console.print("\n[bold]Color Grade Presets[/bold]")
    table = Table()
    table.add_column("Preset", style="cyan")
    table.add_column("Filter", style="dim")
    for name, filt in sorted(COLOR_GRADE_PRESETS.items()):
        table.add_row(name, filt[:60] + ("..." if len(filt) > 60 else ""))
    console.print(table)

    console.print("\n[bold]xfade Transitions[/bold]")
    # Print in columns
    cols = 4
    rows = []
    for i in range(0, len(XFADE_TRANSITIONS), cols):
        chunk = XFADE_TRANSITIONS[i:i + cols]
        rows.append("  ".join(f"{t:<16}" for t in chunk))
    for row in rows:
        console.print(f"  {row}")

    console.print("\n[bold]Ken Burns Effects[/bold]")
    for kb in ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down", "zoom_in_pan_right"]:
        console.print(f"  {kb}")

    console.print()


@app.command()
def captions(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    precise: bool = typer.Option(False, "--precise", help="Use Whisper for word-level timestamps"),
    caption_style: str = typer.Option("karaoke", "--style", "-s", help="Caption style: karaoke or phrase"),
):
    """Generate ASS captions from storyboard narrator text."""
    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.processors.captions import (
        extract_caption_segments,
        generate_captions_estimated,
    )

    sb = parse_storyboard(storyboard_path)
    segments = extract_caption_segments(sb)

    if not segments:
        console.print("[yellow]No captionable segments found.[/yellow]")
        return

    out_dir = Path(project_dir) / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    console.print(f"[bold]Generating captions ({caption_style}, {len(segments)} segments)...[/bold]")

    if precise:
        console.print("[yellow]Precise mode not yet implemented — falling back to estimated.[/yellow]")

    generate_captions_estimated(segments, out, style=caption_style)
    console.print(f"[green]Captions written to {out}[/green]")


@app.command()
def preflight(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Check which assets are ready and which are missing."""
    from rich.table import Table

    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.services.preflight import run_preflight

    sb = parse_storyboard(storyboard_path)
    proj = Path(project_dir)
    report = run_preflight(sb, proj)

    table = Table(title="Asset Preflight Report")
    table.add_column("Segment", style="dim")
    table.add_column("Layer")
    table.add_column("Code")
    table.add_column("Qualifier", max_width=40)
    table.add_column("Status")
    table.add_column("File", max_width=50)

    status_colors = {
        "found": "green",
        "missing": "red",
        "needs-check": "yellow",
        "not-supported": "dim",
        "unknown": "magenta",
    }

    for entry in report.entries:
        color = status_colors.get(entry.status, "white")
        table.add_row(
            entry.segment_id,
            entry.layer,
            entry.visual_code,
            entry.qualifier[:40],
            f"[{color}]{entry.status}[/{color}]",
            entry.file_path or "",
        )

    console.print(table)
    console.print(
        f"\n[bold]{report.total} assets:[/bold] "
        f"[green]{report.found} found[/green], "
        f"[red]{report.missing} missing[/red], "
        f"[yellow]{report.needs_check} need check[/yellow]"
    )

    # Write JSON manifest
    import json
    from dataclasses import asdict
    manifest_dir = proj / "output"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "asset-manifest.json"
    manifest = {
        "total": report.total,
        "found": report.found,
        "missing": report.missing,
        "generated": report.generated,
        "needs_check": report.needs_check,
        "entries": [asdict(e) for e in report.entries],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    console.print(f"\n[dim]Manifest written to {manifest_path}[/dim]")


@app.command()
def previews(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Generate low-res preview clips for all assigned segments."""
    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.services.production import generate_all_previews

    sb = parse_storyboard(storyboard_path)
    proj = Path(project_dir)

    console.print("[bold]Generating previews...[/bold]")
    result = generate_all_previews(sb, proj)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host"),
    port: int = typer.Option(8420, "--port", "-p", help="Bind port"),
    dev: bool = typer.Option(False, "--dev", help="Dev mode (CORS open, no static)"),
):
    """Start the web-based video editor server."""
    try:
        import uvicorn
    except ImportError:
        console.print("[red]Missing dependency. Install with: uv pip install bee-video-editor[web][/red]")
        raise typer.Exit(1)

    from bee_video_editor.api.server import create_app

    static_dir = None
    if not dev:
        # Look for built frontend
        candidates = [
            Path(__file__).parent.parent.parent.parent / "web" / "dist",
            Path(__file__).parent.parent / "web" / "dist",
        ]
        for c in candidates:
            if c.exists():
                static_dir = c
                break

    app_instance = create_app(static_dir=static_dir)

    console.print(f"[bold]Bee Video Editor[/bold] — http://{host}:{port}")
    if dev:
        console.print("[dim]Dev mode: run 'npm run dev' in web/ for frontend[/dim]")
    elif static_dir:
        console.print(f"[dim]Serving frontend from {static_dir}[/dim]")
    else:
        console.print("[dim]No built frontend found. Run 'npm run build' in web/[/dim]")

    uvicorn.run(app_instance, host=host, port=port, log_level="info")


@app.command()
def produce(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine"),
    voice: str | None = typer.Option(None, "--voice", "-v"),
    caption_style: str = typer.Option("karaoke", "--style", "-s", help="Caption style: karaoke or phrase"),
    transition_name: str | None = typer.Option(None, "--transition", "-t"),
    transition_duration: float = typer.Option(1.0, "--transition-duration"),
    skip_graphics: bool = typer.Option(False, "--skip-graphics"),
    skip_narration: bool = typer.Option(False, "--skip-narration"),
    skip_captions: bool = typer.Option(False, "--skip-captions"),
    skip_trim: bool = typer.Option(False, "--skip-trim"),
    animated: bool = typer.Option(False, "--animated"),
):
    """Run the full production pipeline: init → graphics → captions → narration → trim → assemble."""
    from bee_video_editor.services.production import ProductionConfig, run_full_pipeline

    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
        tts_voice=voice,
    )

    step_icons = {"running": "⏳", "done": "✓", "skipped": "⏭", "failed": "✗"}
    step_colors = {"running": "yellow", "done": "green", "skipped": "dim", "failed": "red"}
    total_steps = 6
    step_nums = {"init": 1, "graphics": 2, "captions": 3, "narration": 4, "trim": 5, "assemble": 6}

    def on_step(name, status, message):
        icon = step_icons.get(status, "?")
        color = step_colors.get(status, "white")
        step_num = step_nums.get(name, 0)
        msg = f" — {message}" if message else ""
        console.print(f"[{color}][{step_num}/{total_steps}] {name} {icon}{msg}[/{color}]")

    console.print(f"\n[bold]Producing video from {storyboard_path}[/bold]\n")

    result = run_full_pipeline(
        storyboard_path=Path(storyboard_path),
        config=config,
        skip_graphics=skip_graphics,
        skip_captions=skip_captions,
        skip_narration=skip_narration,
        skip_trim=skip_trim,
        caption_style=caption_style,
        transition=transition_name,
        transition_duration=transition_duration,
        animated=animated,
        on_step=on_step,
    )

    if result.ok:
        console.print(f"\n[bold green]Done![/bold green]")
        if result.output_path:
            console.print(f"Output: {result.output_path}")
    else:
        failed = [s for s in result.steps if s.status == "failed"]
        console.print(f"\n[bold red]Pipeline failed at: {failed[0].name}[/bold red]")
        console.print(f"Error: {failed[0].message}")
        console.print("\n[dim]Fix the issue and re-run — completed steps will be skipped.[/dim]")
        raise typer.Exit(1)


def _load_project(assembly_guide: str):
    from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
    return parse_assembly_guide(assembly_guide)


if __name__ == "__main__":
    app()
