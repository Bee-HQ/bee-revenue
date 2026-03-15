"""CLI adapter using typer. Thin translation layer that calls service functions."""

from typing import Optional

import typer
from rich.console import Console

from ..storage.db import Database
from ..services import discovery, analysis, groups, reporting
from ..formatters import (
    format_channels_table,
    format_outliers_table,
    format_engagement_table,
    format_benchmarks_table,
    format_titles_table,
    format_seo_table,
    format_timing_table,
    format_regional_table,
    format_compare_table,
    format_content_gaps_table,
    format_full_report,
    to_json,
    to_csv,
)

app = typer.Typer(name="bee-research", help="YouTube competitor analysis tool")
console = Console()

# Subcommands
group_app = typer.Typer(help="Manage niche groups")
analyze_app = typer.Typer(help="Run analysis")
app.add_typer(group_app, name="group")
app.add_typer(analyze_app, name="analyze")


# --- Discovery & Data commands ---

@app.command()
def discover(
    keyword: str = typer.Argument(..., help="Keyword to search or channel URL for snowball"),
    snowball: bool = typer.Option(False, "--snowball", help="Use snowball discovery from a channel"),
    max_results: int = typer.Option(20, "--max-results", help="Maximum channels to find"),
):
    """Discover channels by keyword search or snowball from a channel."""
    db = Database()
    try:
        if snowball:
            channels = discovery.snowball(db, keyword, max_results)
        else:
            channels = discovery.discover(db, keyword, max_results)
        console.print(format_channels_table(channels))
        console.print(f"\n[green]{len(channels)} channels discovered[/green]")
    finally:
        db.close()


@app.command()
def add(
    urls: list[str] = typer.Argument(..., help="Channel URLs or @handles to add"),
):
    """Manually add channels by URL or @handle."""
    db = Database()
    try:
        for url in urls:
            ch = discovery.add_channel(db, url)
            if ch:
                console.print(f"[green]Added:[/green] {ch['name']} ({ch['id']})")
            else:
                console.print(f"[red]Failed:[/red] {url}")
    finally:
        db.close()


@app.command()
def fetch(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    transcripts: bool = typer.Option(False, "--transcripts", help="Also fetch transcripts"),
    max_videos: int = typer.Option(200, "--max-videos", help="Max videos per channel"),
    delay: float = typer.Option(1.5, "--delay", help="Delay between requests (seconds)"),
    force: bool = typer.Option(False, "--force", help="Re-fetch regardless of TTL"),
):
    """Fetch video data for a channel or niche group."""
    from rich.progress import Progress

    db = Database()
    try:
        with Progress() as progress:
            task = progress.add_task("Fetching...", total=None)

            def cb(current, total):
                progress.update(task, completed=current, total=total)

            result = discovery.fetch_data(
                db, target,
                include_transcripts=transcripts,
                max_videos=max_videos,
                delay=delay,
                force=force,
                progress_callback=cb,
            )

        if result.get("error"):
            console.print(f"[red]Error:[/red] {result['error']}")
        else:
            console.print(f"[green]Fetched {result.get('fetched', 0)} videos[/green]")
            if result.get("skipped"):
                console.print(f"[dim]Skipped {result['skipped']} channels (data still fresh)[/dim]")
            if result.get("warnings"):
                for w in result["warnings"]:
                    console.print(f"[yellow]Warning:[/yellow] {w}")
    finally:
        db.close()


@app.command()
def status():
    """Show cached data statistics and data freshness."""
    db = Database()
    try:
        s = db.get_status()
        console.print(f"[bold]Database:[/bold] {s['db_path']}")
        console.print(f"[bold]Channels:[/bold] {s['channels']}")
        console.print(f"[bold]Videos:[/bold] {s['videos']}")
        console.print(f"[bold]Transcripts:[/bold] {s['transcripts']}")
        console.print(f"[bold]Groups:[/bold] {s['groups']}")
        console.print(
            f"[bold]Data range:[/bold] {s['oldest_fetch'] or 'N/A'} -> {s['newest_fetch'] or 'N/A'}"
        )
    finally:
        db.close()


# --- Group commands ---

@group_app.command("create")
def group_create(
    name: str = typer.Argument(..., help="Group name"),
    channel_ids: list[str] = typer.Argument(..., help="Channel IDs to include"),
):
    """Create a new niche group with channels."""
    db = Database()
    try:
        groups.create(db, name, channel_ids)
        console.print(f"[green]Created group '{name}' with {len(channel_ids)} channels[/green]")
    finally:
        db.close()


@group_app.command("list")
def group_list():
    """List all niche groups."""
    db = Database()
    try:
        grps = groups.list_all(db)
        if not grps:
            console.print("[dim]No groups yet. Create one with: bee-research group create <name> <channel_ids>[/dim]")
            return
        for g in grps:
            console.print(f"  [bold]{g['name']}[/bold] ({g['channel_count']} channels)")
    finally:
        db.close()


@group_app.command("show")
def group_show(
    name: str = typer.Argument(..., help="Group name"),
):
    """Show channels in a niche group."""
    db = Database()
    try:
        channels = groups.show(db, name)
        if channels:
            console.print(format_channels_table(channels))
        else:
            console.print(f"[yellow]No channels found in group '{name}'[/yellow]")
    finally:
        db.close()


@group_app.command("add")
def group_add(
    name: str = typer.Argument(..., help="Group name"),
    channel_ids: list[str] = typer.Argument(..., help="Channel IDs to add"),
):
    """Add channels to an existing group."""
    db = Database()
    try:
        groups.add_channels(db, name, channel_ids)
        console.print(f"[green]Added {len(channel_ids)} channels to '{name}'[/green]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        db.close()


@group_app.command("remove")
def group_remove(
    name: str = typer.Argument(..., help="Group name"),
    channel_ids: list[str] = typer.Argument(..., help="Channel IDs to remove"),
):
    """Remove channels from a group."""
    db = Database()
    try:
        groups.remove_channels(db, name, channel_ids)
        console.print(f"[green]Removed {len(channel_ids)} channels from '{name}'[/green]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        db.close()


# --- Analyze commands ---

@analyze_app.command("outliers")
def analyze_outliers(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    threshold: float = typer.Option(2.0, "--threshold", help="Multiplier threshold"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
):
    """Find viral outlier videos."""
    db = Database()
    try:
        result = analysis.outliers(db, target, threshold)
        if format == "json":
            console.print(to_json(result))
        elif format == "csv":
            console.print(to_csv(result.get("outliers", [])))
        else:
            console.print(format_outliers_table(result))
    finally:
        db.close()


@analyze_app.command("gaps")
def analyze_gaps(
    niche: str = typer.Argument(..., help="Niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Find content gaps in a niche."""
    db = Database()
    try:
        result = analysis.content_gaps(db, niche)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_content_gaps_table(result))
    finally:
        db.close()


@analyze_app.command("titles")
def analyze_titles(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Analyze title patterns."""
    db = Database()
    try:
        result = analysis.titles(db, target)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_titles_table(result))
            # Also show format distribution
            dist = result.get("format_distribution", {})
            if dist:
                console.print(f"\n[bold]Format Distribution:[/bold]")
                for k, v in dist.items():
                    console.print(f"  {k}: {v}")
    finally:
        db.close()


@analyze_app.command("engagement")
def analyze_engagement(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
):
    """Analyze engagement ratios."""
    db = Database()
    try:
        result = analysis.engagement(db, target)
        if format == "json":
            console.print(to_json(result))
        elif format == "csv":
            console.print(to_csv(result.get("videos", [])))
        else:
            console.print(format_engagement_table(result))
            summary = result.get("summary", {})
            if summary:
                console.print(f"\n[bold]Summary:[/bold]")
                console.print(f"  Avg Like Rate: {summary.get('avg_like_rate', 0):.2f}%")
                console.print(f"  Avg Comment Rate: {summary.get('avg_comment_rate', 0):.3f}%")
            gems = result.get("hidden_gems", [])
            if gems:
                console.print(f"\n[bold]Hidden Gems ({len(gems)}):[/bold]")
                for g in gems[:5]:
                    console.print(f"  {g['title'][:40]} (views: {g['view_count']:,}, score: {g['composite_score']:.2f})")
    finally:
        db.close()


@analyze_app.command("benchmark")
def analyze_benchmark(
    niche: str = typer.Argument(..., help="Niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Calculate niche benchmarks."""
    db = Database()
    try:
        result = analysis.benchmarks(db, niche)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_benchmarks_table(result))
            medians = result.get("niche_medians", {})
            if medians:
                console.print(f"\n[bold]Niche Medians:[/bold]")
                console.print(f"  Median Views: {medians.get('median_views', 0):,}")
                console.print(f"  Avg Duration: {medians.get('avg_duration_seconds', 0):.0f}s")
                console.print(f"  Uploads/Week: {medians.get('median_uploads_per_week', 0):.1f}")
    finally:
        db.close()


@analyze_app.command("seo")
def analyze_seo(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Analyze tags and keywords."""
    db = Database()
    try:
        result = analysis.seo(db, target)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_seo_table(result))
            recs = result.get("recommendations", [])
            if recs:
                console.print(f"\n[bold]Recommendations:[/bold]")
                for r in recs:
                    console.print(f"  [{r.get('type', '')}] {r.get('message', '')}")
    finally:
        db.close()


@analyze_app.command("timing")
def analyze_timing(
    target: str = typer.Argument(..., help="Channel ID or niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Analyze upload timing patterns."""
    db = Database()
    try:
        result = analysis.timing(db, target)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_timing_table(result))
            best = result.get("best_times", [])
            if best:
                console.print(f"\n[bold]Best Times:[/bold]")
                for b in best:
                    console.print(f"  {b['type']}: {b['value']} (median views: {b['median_views']:,})")
    finally:
        db.close()


@analyze_app.command("compare")
def analyze_compare(
    channel_ids: list[str] = typer.Argument(..., help="Channel IDs to compare (2+)"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Side-by-side channel comparison."""
    db = Database()
    try:
        result = analysis.compare(db, channel_ids)
        if result.get("error"):
            console.print(f"[red]Error:[/red] {result['error']}")
        elif format == "json":
            console.print(to_json(result))
        else:
            console.print(format_compare_table(result))
    finally:
        db.close()


@analyze_app.command("regional")
def analyze_regional(
    niche: str = typer.Argument(..., help="Niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json"),
):
    """Analyze regional and language distribution."""
    db = Database()
    try:
        result = analysis.regional(db, niche)
        if format == "json":
            console.print(to_json(result))
        else:
            console.print(format_regional_table(result))
            opps = result.get("opportunities", [])
            if opps:
                console.print(f"\n[bold]Opportunities:[/bold]")
                for o in opps[:5]:
                    console.print(f"  Score {o.get('opportunity_score', 0):.1f}: {o.get('rationale', '')}")
    finally:
        db.close()


# --- Report command ---

@app.command()
def report(
    niche: str = typer.Argument(..., help="Niche group name"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
):
    """Run all analyzers and produce a full report."""
    db = Database()
    try:
        result = reporting.full_report(db, niche)
        if result.get("error"):
            console.print(f"[red]Error:[/red] {result['error']}")
        elif format == "json":
            console.print(to_json(result))
        else:
            console.print(format_full_report(result))
    finally:
        db.close()
