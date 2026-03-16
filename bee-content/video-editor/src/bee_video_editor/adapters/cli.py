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
):
    """Generate all graphics assets (lower thirds, timelines, etc.)."""
    from bee_video_editor.services.production import ProductionConfig, generate_graphics_for_project

    config = ProductionConfig(project_dir=Path(project_dir))
    project = _load_project(assembly_guide)

    console.print("[bold]Generating graphics...[/bold]")
    generated = generate_graphics_for_project(project, config)

    console.print(f"[green]Generated {len(generated)} graphics[/green]")
    for g in generated:
        console.print(f"  {g}")


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
    generated = generate_narration_for_project(project, config)

    console.print(f"[green]Generated {len(generated)} narration clips[/green]")


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
    trimmed = trim_source_footage(project, config)

    console.print(f"[green]Trimmed {len(trimmed)} clips[/green]")


@app.command()
def assemble(
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Assemble all segments into the final video."""
    from bee_video_editor.services.production import ProductionConfig, assemble_final

    config = ProductionConfig(project_dir=Path(project_dir))

    console.print("[bold]Assembling final video...[/bold]")
    result = assemble_final(config)

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


def _load_project(assembly_guide: str):
    from bee_video_editor.parsers.assembly_guide import parse_assembly_guide
    return parse_assembly_guide(assembly_guide)


if __name__ == "__main__":
    app()
