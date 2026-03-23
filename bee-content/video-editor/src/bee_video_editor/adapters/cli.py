"""CLI adapter for bee-video-editor — typer commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="bee-video",
    help="AI-assisted video production from storyboards.",
    no_args_is_help=True,
)

from bee_video_editor.adapters.cli_dub import dub_app
app.add_typer(dub_app, name="dub")

console = Console()


def _load_storyboard(path: str):
    """Load storyboard from .md or .otio, auto-detecting format.

    Returns a ParsedStoryboard (formats.parser).
    """
    from bee_video_editor.formats.parser import parse_v2

    p = Path(path)

    # OTIO file — convert to ParsedStoryboard
    if p.suffix == ".otio":
        import opentimelineio as otio
        from bee_video_editor.formats.otio_convert import from_otio
        tl = otio.adapters.read_from_file(str(p))
        return from_otio(tl)

    # Markdown — try v2 first, then fall back to old parser + migrate
    text = p.read_text(encoding="utf-8")
    if "```json bee-video:" in text:
        return parse_v2(path)

    # Old table format — parse with legacy parser, then migrate
    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.formats.migrate import old_to_new
    old = parse_storyboard(path)
    return old_to_new(old)


@app.command()
def parse(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
):
    """Parse a storyboard and show project summary."""
    from bee_video_editor.formats.parser import segment_duration

    parsed = _load_storyboard(storyboard)

    console.print(f"\n[bold]{parsed.project.title}[/bold]")
    total_segments = len(parsed.segments)
    console.print(f"Total segments: {total_segments}")
    console.print()

    # Visual type breakdown
    visual_types: dict[str, int] = {}
    for seg in parsed.segments:
        for v in seg.config.visual:
            vt = v.type
            visual_types[vt] = visual_types.get(vt, 0) + 1

    if visual_types:
        table = Table(title="Visual Types")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right")

        for vtype, count in visual_types.items():
            table.add_row(vtype, str(count))

        console.print(table)

    # Sections
    if parsed.sections:
        console.print("\n[bold]Sections:[/bold]")
        for section in parsed.sections:
            seg_count = len([s for s in parsed.segments if s.section == section.title])
            console.print(f"  {section.title} ({seg_count} segments)")

    # Total duration
    if parsed.segments:
        total_dur = sum(segment_duration(s) for s in parsed.segments)
        mins = int(total_dur) // 60
        secs = int(total_dur) % 60
        console.print(f"\n[bold]Total duration:[/bold] {mins}m {secs}s")
    console.print()


@app.command()
def segments(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    section: str | None = typer.Option(None, "--section", "-s", help="Filter by section name"),
    content_type: str | None = typer.Option(None, "--type", "-t", help="Filter by visual content type (FOOTAGE/STOCK/GRAPHIC/NAR/etc.)"),
):
    """List all segments from the storyboard."""
    from bee_video_editor.formats.parser import segment_duration

    parsed = _load_storyboard(storyboard)

    segs = parsed.segments
    if section:
        segs = [s for s in segs if section.lower() in s.section.lower()]
    if content_type:
        ct = content_type.upper()
        segs = [
            s for s in segs
            if any(e.type == ct for e in (s.config.visual + s.config.audio + s.config.overlay))
        ]

    table = Table(title=f"Segments ({len(segs)} total)")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Time", style="cyan")
    table.add_column("Dur", justify="right")
    table.add_column("Section")
    table.add_column("Title")
    table.add_column("Visual", max_width=40, overflow="ellipsis")
    table.add_column("Audio", max_width=40, overflow="ellipsis")

    for i, seg in enumerate(segs):
        visual_summary = ", ".join(e.type for e in seg.config.visual) or "-"
        audio_types = [e.type for e in seg.config.audio]
        if seg.narration:
            audio_types.insert(0, "NAR")
        audio_summary = ", ".join(audio_types) or "-"
        dur = segment_duration(seg)
        table.add_row(
            str(i),
            f"{seg.start}-{seg.end}",
            f"{int(dur)}s",
            seg.section,
            (seg.title or "")[:30],
            visual_summary[:40],
            audio_summary[:40],
        )

    console.print(table)


@app.command()
def init(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Project root directory"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine (edge/kokoro/openai)"),
):
    """Initialize a production project from a storyboard."""
    from bee_video_editor.services.production import ProductionConfig, init_project

    parsed = _load_storyboard(storyboard)
    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
    )
    state = init_project(parsed, config)

    console.print(f"\n[bold green]Project initialized![/bold green]")
    console.print(f"Title: {parsed.project.title}")
    console.print(f"Segments: {len(parsed.segments)}")
    console.print(f"Output: {config.output_dir}")
    console.print(f"State: {config.output_dir / 'production_state.json'}")
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print("  bee-video graphics <storyboard>  — Generate graphics assets")
    console.print("  bee-video narration <storyboard>  — Generate TTS narration")
    console.print("  bee-video trim <storyboard>       — Trim source footage")
    console.print("  bee-video assemble                — Final assembly")


@app.command()
def graphics(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Generate all graphics assets (lower thirds, timelines, etc.). Note: most graphics are now Remotion components — this generates legacy Pillow PNGs."""
    from bee_video_editor.services.production import ProductionConfig, generate_graphics_for_project

    config = ProductionConfig(project_dir=Path(project_dir))
    project = _load_storyboard(storyboard)

    console.print("[bold]Generating graphics (legacy Pillow)...[/bold]")
    console.print("[dim]Note: overlays are now Remotion components in the web editor.[/dim]")

    result = generate_graphics_for_project(project, config, animated=False)

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
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine (edge/kokoro/openai)"),
    voice: str | None = typer.Option(None, "--voice", "-v", help="Voice ID"),
    workers: int = typer.Option(1, "--workers", "-w", help="Parallel workers for TTS (default: 1)"),
):
    """Generate TTS narration for all narrator segments."""
    from bee_video_editor.services.production import ProductionConfig, generate_narration_for_project

    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
        tts_voice=voice,
    )
    project = _load_storyboard(storyboard)

    console.print(f"[bold]Generating narration ({tts_engine})...[/bold]")
    result = generate_narration_for_project(project, config, workers=workers)

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
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    footage_dir: str | None = typer.Option(None, "--footage", "-f", help="Footage directory"),
):
    """Trim source footage based on storyboard source layers."""
    from bee_video_editor.services.production import ProductionConfig, trim_source_footage

    config = ProductionConfig(
        project_dir=Path(project_dir),
        footage_dir=Path(footage_dir) if footage_dir else None,
    )
    project = _load_storyboard(storyboard)

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
    from bee_video_editor.processors.captions import (
        extract_caption_segments,
        generate_captions_estimated,
    )

    parsed = _load_storyboard(storyboard_path)
    cap_segments = extract_caption_segments(parsed)

    if not cap_segments:
        console.print("[yellow]No captionable segments found.[/yellow]")
        return

    out_dir = Path(project_dir) / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    console.print(f"[bold]Generating captions ({caption_style}, {len(cap_segments)} segments)...[/bold]")

    if precise:
        console.print("[yellow]Precise mode not yet implemented — falling back to estimated.[/yellow]")

    generate_captions_estimated(cap_segments, out, style=caption_style)
    console.print(f"[green]Captions written to {out}[/green]")


@app.command()
def preflight(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Check which assets are ready and which are missing."""
    from rich.table import Table

    from bee_video_editor.services.preflight import run_preflight

    parsed = _load_storyboard(storyboard_path)
    proj = Path(project_dir)
    report = run_preflight(parsed, proj)

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
    from bee_video_editor.services.production import generate_all_previews

    parsed = _load_storyboard(storyboard_path)
    proj = Path(project_dir)

    console.print("[bold]Generating previews...[/bold]")
    result = generate_all_previews(parsed, proj)

    console.print(f"[green]Succeeded: {len(result.succeeded)}[/green]")
    if result.failed:
        console.print(f"[red]Failed: {len(result.failed)}[/red]")
        for f in result.failed:
            console.print(f"  [red]{f.path}: {f.error}[/red]")
    if result.skipped:
        console.print(f"[dim]Skipped: {len(result.skipped)}[/dim]")


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
    workers: int = typer.Option(1, "--workers", "-w", help="Parallel TTS workers"),
):
    """Run the full production pipeline: init -> graphics -> captions -> narration -> trim -> assemble."""
    from bee_video_editor.services.production import ProductionConfig, run_full_pipeline

    parsed = _load_storyboard(storyboard_path)
    config = ProductionConfig(
        project_dir=Path(project_dir),
        tts_engine=tts_engine,
        tts_voice=voice,
    )

    step_icons = {"running": "...", "done": "ok", "skipped": "skip", "failed": "FAIL"}
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
        parsed=parsed,
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
        workers=workers,
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


@app.command(name="import-md")
def import_md(
    storyboard: str = typer.Argument(..., help="Path to storyboard .md file (format v2)"),
    output: str | None = typer.Option(None, help="Output .otio path (default: same name as input)"),
    lenient: bool = typer.Option(False, "--lenient", help="Downgrade parse errors to warnings, skip bad segments"),
):
    """Import a v2 markdown storyboard into an OTIO project file."""
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio

    parsed = parse_v2(storyboard, lenient=lenient)
    tl = to_otio(parsed)

    if output is None:
        output = str(Path(storyboard).with_suffix(".otio"))

    otio_lib.adapters.write_to_file(tl, output)
    console.print(f"[green]Imported to {output}[/green]")
    console.print(f"  {len(parsed.segments)} segments, {len(parsed.sections)} sections")


@app.command(name="export")
def export_v2(
    project: str = typer.Argument(..., help="Path to .otio project file"),
    format: str = typer.Option("md", help="Export format: md or otio"),
    output: str | None = typer.Option(None, help="Output path"),
):
    """Export an OTIO project to markdown or clean OTIO."""
    import opentimelineio as otio_lib
    from bee_video_editor.formats.otio_convert import from_otio, clean_otio
    from bee_video_editor.formats.writer import write_v2

    tl = otio_lib.adapters.read_from_file(project)

    if format == "md":
        parsed = from_otio(tl)
        md = write_v2(parsed)
        if output is None:
            output = str(Path(project).with_suffix(".md"))
        Path(output).write_text(md, encoding="utf-8")
        console.print(f"[green]Exported markdown to {output}[/green]")
    elif format == "otio":
        clean = clean_otio(tl)
        if output is None:
            output = str(Path(project).stem + "_clean.otio")
        otio_lib.adapters.write_to_file(clean, output)
        console.print(f"[green]Exported clean OTIO to {output}[/green]")
    else:
        console.print(f"[red]Unknown format: {format}. Use 'md' or 'otio'.[/red]")
        raise typer.Exit(1)


@app.command(name="map")
def generate_map():
    """[Deprecated] Map generation is now handled by Remotion's AnimatedMap component in the web editor."""
    console.print("[yellow]This command is deprecated. Maps are now rendered by Remotion in the web editor.[/yellow]")
    console.print("[dim]Use the web editor or add MAP visual type to your storyboard.[/dim]")
    raise typer.Exit(0)


@app.command()
def voice_lock(
    engine: str = typer.Argument(..., help="TTS engine (edge/kokoro/openai/elevenlabs)"),
    voice: str | None = typer.Option(None, "--voice", "-v", help="Voice ID"),
    speed: float = typer.Option(0.95, "--speed", "-s", help="Speech speed"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Lock TTS voice config for this project. Narration will use these defaults."""
    import json as json_mod

    proj = Path(project_dir).resolve()
    config_path = proj / ".bee-video" / "voice.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"engine": engine, "speed": speed}
    if voice:
        data["voice"] = voice
    config_path.write_text(json_mod.dumps(data, indent=2))
    console.print(f"[green]Voice locked: engine={engine}, voice={voice or '(default)'}, speed={speed}[/green]")
    console.print(f"[dim]Saved to {config_path}[/dim]")


@app.command()
def rough_cut(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Export a fast 720p rough cut — no grading, no transitions. For structure review."""
    from bee_video_editor.services.production import ProductionConfig, rough_cut_export

    parsed = _load_storyboard(storyboard_path)
    config = ProductionConfig(project_dir=Path(project_dir))

    console.print("[bold]Exporting rough cut (720p, no grading)...[/bold]")
    result = rough_cut_export(parsed, config)

    if result:
        console.print(f"[bold green]Rough cut: {result}[/bold green]")
    else:
        console.print("[yellow]No assigned media found. Assign media to segments first.[/yellow]")


@app.command()
def fetch_stock(
    query: str = typer.Argument(..., help="Search query (e.g. 'aerial farm dusk')"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    count: int = typer.Option(3, "--count", "-n", help="Number of clips to download"),
    min_duration: int = typer.Option(5, "--duration", "-d", help="Minimum clip duration (seconds)"),
    orientation: str | None = typer.Option(None, "--orientation", "-o", help="landscape/portrait/square"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="PEXELS_API_KEY"),
):
    """Search and download stock footage from Pexels."""
    from bee_video_editor.processors.stock import (
        download_stock_clip,
        search_pexels,
        slugify_query,
    )

    try:
        results = search_pexels(
            query, api_key=api_key, per_page=count,
            min_duration=min_duration, orientation=orientation,
        )
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"[bold]Found {len(results)} clips. Downloading...[/bold]")
    stock_dir = Path(project_dir) / "stock"
    slug = slugify_query(query)

    for i, clip in enumerate(results[:count]):
        filename = f"{slug}-{i:02d}-pexels-{clip.id}.mp4"
        out_path = stock_dir / filename

        try:
            download_stock_clip(clip.hd_url, out_path)
            console.print(f"  [green]{filename}[/green] ({clip.duration}s, {clip.width}x{clip.height})")
            # Auto-register in stock library
            try:
                from bee_video_editor.services.stock_library import StockLibrary
                with StockLibrary() as lib:
                    lib.register_clip(
                        pexels_id=clip.id,
                        query=query,
                        path=str(out_path),
                        project=Path(project_dir).resolve().name,
                    )
            except Exception:
                pass  # Library tracking is non-critical
        except RuntimeError as e:
            console.print(f"  [red]{filename}: {e}[/red]")

    console.print(f"[bold green]Done — {stock_dir}[/bold green]")


@app.command()
def generate_clip(
    prompt: str = typer.Argument(..., help="Text prompt describing the clip to generate"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    provider: str = typer.Option("stub", "--provider", help="Generation provider (stub/runway/kling/luma)"),
    duration: float = typer.Option(5.0, "--duration", "-d", help="Clip duration (seconds)"),
    reference: list[str] | None = typer.Option(None, "--reference", "-r", help="Reference image/video path"),
    width: int = typer.Option(1280, "--width", "-w"),
    height: int = typer.Option(720, "--height"),
    style: str | None = typer.Option(None, "--style", "-s", help="Provider-specific style hint"),
):
    """Generate a video clip from a text prompt using AI."""
    from bee_video_editor.processors.stock import slugify_query
    from bee_video_editor.processors.videogen import (
        GenerationRequest,
        generate_clip as gen_clip,
        list_providers,
    )

    available = list_providers()
    if provider not in available:
        console.print(f"[red]Unknown provider '{provider}'. Available: {', '.join(sorted(available))}[/red]")
        raise typer.Exit(1)

    ref_images = []
    ref_videos = []
    for ref in (reference or []):
        p = Path(ref)
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
            ref_images.append(p)
        else:
            ref_videos.append(p)

    slug = slugify_query(prompt)
    output_dir = Path(project_dir) / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}-{provider}.mp4"

    req = GenerationRequest(
        prompt=prompt,
        duration=duration,
        width=width,
        height=height,
        reference_images=ref_images,
        reference_videos=ref_videos,
        style=style,
    )

    console.print(f"[bold]Generating clip ({provider})...[/bold]")
    console.print(f"  Prompt: {prompt}")
    if ref_images or ref_videos:
        console.print(f"  References: {len(ref_images)} images, {len(ref_videos)} videos")

    try:
        result = gen_clip(req, output_path, provider=provider)
        if result.success:
            console.print(f"[bold green]Generated: {result.output_path}[/bold green]")
        else:
            console.print(f"[red]Generation failed: {result.error}[/red]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Validate project directory structure and naming conventions."""
    from bee_video_editor.services.validator import validate_project

    report = validate_project(Path(project_dir))

    severity_colors = {"error": "red", "warning": "yellow", "info": "dim"}
    severity_icons = {"error": "x", "warning": "!", "info": "."}

    for issue in report.issues:
        color = severity_colors[issue.severity]
        icon = severity_icons[issue.severity]
        console.print(f"  [{color}]{icon} {issue.message}[/{color}]")
        if issue.path:
            console.print(f"    [dim]{issue.path}[/dim]")

    console.print()
    if report.ok:
        console.print(f"[green]Validation passed[/green] ({report.warnings} warnings, {report.total} total)")
    else:
        console.print(f"[red]{report.errors} errors[/red], {report.warnings} warnings ({report.total} total)")


@app.command(name="stock-list")
def stock_library_list():
    """List all tracked stock footage clips."""
    from bee_video_editor.services.stock_library import StockLibrary

    with StockLibrary() as lib:
        clips = lib.list_clips()

    if not clips:
        console.print("[dim]No stock clips tracked yet.[/dim]")
        return

    table = Table(title=f"Stock Library ({len(clips)} clips)")
    table.add_column("Pexels ID", style="cyan")
    table.add_column("Query")
    table.add_column("Uses", justify="right")
    table.add_column("First Project")
    table.add_column("Path", max_width=40)

    for clip in clips:
        table.add_row(
            str(clip["pexels_id"]),
            clip["query"],
            str(clip["usage_count"]),
            clip["first_used_project"],
            clip["path"][-40:],
        )

    console.print(table)


@app.command(name="stock-check")
def stock_library_check(
    query: str = typer.Argument(..., help="Search query to check for prior usage"),
):
    """Check if stock clips from a query were already used in other projects."""
    from bee_video_editor.services.stock_library import StockLibrary

    with StockLibrary() as lib:
        matches = lib.check_query(query)

    if not matches:
        console.print(f"[green]No prior usage found for '{query}'.[/green]")
    else:
        console.print(f"[yellow]Found {len(matches)} previously used clip(s) matching '{query}':[/yellow]")
        for m in matches:
            console.print(f"  Pexels {m['pexels_id']} — used {m['usage_count']}x, first in {m['first_used_project']}")
        console.print("[dim]Consider varying your search terms to avoid visual repetition.[/dim]")


@app.command()
def scenes(
    video: str = typer.Argument(..., help="Path to video file"),
    threshold: float = typer.Option(0.3, help="Scene change threshold (0.0-1.0)"),
    min_duration: float = typer.Option(2.0, help="Minimum scene duration in seconds"),
):
    """Detect scene boundaries in a video file."""
    import shutil
    if not shutil.which("ffmpeg"):
        console.print("[red]FFmpeg is required for scene detection[/red]")
        raise typer.Exit(1)

    from bee_video_editor.processors.scene_detect import detect_scenes

    scenes_list = detect_scenes(video, threshold=threshold, min_scene_duration=min_duration)

    if not scenes_list:
        console.print("[yellow]No scenes detected[/yellow]")
        return

    table = Table(title=f"Detected {len(scenes_list)} scenes")
    table.add_column("#", justify="right")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Duration", justify="right")

    for s in scenes_list:
        table.add_row(str(s.index + 1), s.start_timecode, s.end_timecode, f"{s.duration:.1f}s")

    console.print(table)


if __name__ == "__main__":
    app()
