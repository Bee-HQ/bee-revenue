"""CLI adapter using typer. Thin wrapper over source modules."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="bee-auto",
    help="Automated anime/manga/manhwa YouTube content pipeline",
)
console = Console()


def _run(coro):
    """Run an async coroutine from sync CLI context."""
    return asyncio.run(coro)


# --- Search ---

@app.command()
def search(
    query: str = typer.Argument(..., help="Manga/manhwa title to search"),
    source: str = typer.Option("anilist", "--source", "-s", help="Source: anilist, mangadex, mangaupdates"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
):
    """Search for a manga/manhwa series."""
    if source == "anilist":
        from .sources.anilist import search_manga
        results = _run(search_manga(query, limit))
        table = Table(title=f"AniList Search: {query}")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Status")
        table.add_column("Score", justify="right")
        table.add_column("Popularity", justify="right")
        table.add_column("Genres")
        for s in results:
            table.add_row(
                s.id,
                s.display_title,
                s.status,
                f"{s.score:.1f}" if s.score else "-",
                f"{s.popularity:,}",
                ", ".join(s.genres[:3]),
            )
        console.print(table)

    elif source == "mangadex":
        from .sources.mangadex import search_manga
        results = _run(search_manga(query, limit))
        table = Table(title=f"MangaDex Search: {query}")
        table.add_column("ID", style="dim", max_width=12)
        table.add_column("Title", style="bold")
        table.add_column("Status")
        table.add_column("Year", justify="right")
        table.add_column("Tags")
        for r in results:
            table.add_row(
                r["id"][:12] + "...",
                r["title"],
                r["status"],
                str(r.get("year") or "-"),
                ", ".join(r.get("tags", [])[:3]),
            )
        console.print(table)

    elif source == "mangaupdates":
        from .sources.mangaupdates import search_series
        results = _run(search_series(query))
        table = Table(title=f"MangaUpdates Search: {query}")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Type")
        table.add_column("Year", justify="right")
        for r in results:
            table.add_row(
                str(r.get("id", "")),
                r["title"],
                r.get("type", ""),
                str(r.get("year") or "-"),
            )
        console.print(table)

    else:
        console.print(f"[red]Unknown source:[/red] {source}. Use: anilist, mangadex, mangaupdates")
        raise typer.Exit(1)


# --- Trending ---

@app.command()
def trending(
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
):
    """Show currently trending manga/manhwa on AniList."""
    from .sources.anilist import get_trending_manga

    results = _run(get_trending_manga(limit))
    table = Table(title="Trending Manga/Manhwa")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Score", justify="right")
    table.add_column("Popularity", justify="right")
    table.add_column("Genres")
    for i, s in enumerate(results, 1):
        table.add_row(
            str(i),
            s.display_title,
            s.status,
            f"{s.score:.1f}" if s.score else "-",
            f"{s.popularity:,}",
            ", ".join(s.genres[:3]),
        )
    console.print(table)


# --- Chapters ---

@app.command()
def chapters(
    series: str = typer.Argument(..., help="Manga title or MangaDex ID"),
    source: str = typer.Option("mangadex", "--source", "-s", help="Source: mangadex"),
    language: str = typer.Option("en", "--lang", "-l", help="Language code"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max chapters"),
):
    """List available chapters for a series."""
    if source != "mangadex":
        console.print("[red]Only mangadex source supported for chapters[/red]")
        raise typer.Exit(1)

    from .sources.mangadex import search_manga, get_chapters

    async def _fetch():
        # If it looks like a UUID, use directly; otherwise search first
        if len(series) == 36 and "-" in series:
            manga_id = series
        else:
            results = await search_manga(series, limit=1)
            if not results:
                return None, []
            manga_id = results[0]["id"]
        chaps = await get_chapters(manga_id, language=language, limit=limit)
        return manga_id, chaps

    manga_id, chaps = _run(_fetch())

    if manga_id is None:
        console.print(f"[red]No manga found for:[/red] {series}")
        raise typer.Exit(1)

    if not chaps:
        console.print(f"[yellow]No {language} chapters found for {manga_id}[/yellow]")
        return

    table = Table(title=f"Chapters ({len(chaps)} found)")
    table.add_column("Ch.", justify="right")
    table.add_column("Title")
    table.add_column("Pages", justify="right")
    table.add_column("Group")
    table.add_column("Published")
    for ch in chaps:
        table.add_row(
            f"{ch.number:g}",
            ch.title or "-",
            str(ch.pages),
            ch.scanlation_group or "-",
            ch.published_at[:10] if ch.published_at else "-",
        )
    console.print(table)
    console.print(f"\n[dim]MangaDex ID: {manga_id}[/dim]")


# --- Chapter Summary ---

@app.command()
def summary(
    series: str = typer.Argument(..., help="Series name"),
    chapter: float = typer.Argument(..., help="Chapter number"),
):
    """Get chapter summary from wiki sources."""
    from .sources.fandom import search_wiki, get_chapter_summary

    async def _fetch():
        wiki = await search_wiki(series)
        if not wiki:
            return None, None
        summary = await get_chapter_summary(wiki, int(chapter))
        return wiki, summary

    wiki, result = _run(_fetch())

    if not wiki:
        console.print(f"[yellow]No wiki found for:[/yellow] {series}")
        return
    if not result:
        console.print(f"[yellow]No summary found for chapter {chapter} on {wiki}.fandom.com[/yellow]")
        return

    console.print(f"\n[bold]{result.series_title} — Chapter {result.chapter_number:g}[/bold]")
    console.print(f"[dim]Source: {wiki}.fandom.com[/dim]\n")
    console.print(result.synopsis[:2000])

    if result.characters:
        console.print(f"\n[bold]Characters mentioned:[/bold] {', '.join(result.characters[:8])}")
    if result.key_events:
        console.print(f"\n[bold]Key events:[/bold]")
        for event in result.key_events:
            console.print(f"  - {event[:120]}")


# --- Series Info ---

@app.command()
def info(
    series: str = typer.Argument(..., help="Series name or AniList ID"),
):
    """Get full series info from AniList."""
    from .sources.anilist import search_manga, get_series_details, get_characters

    async def _fetch():
        # If numeric, treat as AniList ID
        if series.isdigit():
            s = await get_series_details(int(series))
        else:
            results = await search_manga(series, limit=1)
            if not results:
                return None, []
            s = results[0]
        chars = await get_characters(int(s.id))
        return s, chars

    result, chars = _run(_fetch())

    if not result:
        console.print(f"[red]Series not found:[/red] {series}")
        raise typer.Exit(1)

    console.print(f"\n[bold]{result.display_title}[/bold]")
    if result.title_romaji and result.title_romaji != result.title_english:
        console.print(f"[dim]{result.title_romaji}[/dim]")
    if result.title_native:
        console.print(f"[dim]{result.title_native}[/dim]")

    console.print(f"\n[bold]Status:[/bold] {result.status}")
    console.print(f"[bold]Chapters:[/bold] {result.chapters or 'Ongoing'}")
    console.print(f"[bold]Score:[/bold] {result.score:.1f}/10" if result.score else "[bold]Score:[/bold] -")
    console.print(f"[bold]Popularity:[/bold] {result.popularity:,}")
    console.print(f"[bold]Genres:[/bold] {', '.join(result.genres)}")
    if result.tags:
        console.print(f"[bold]Tags:[/bold] {', '.join(result.tags[:10])}")

    if result.synopsis:
        console.print(f"\n[bold]Synopsis:[/bold]")
        # Strip HTML tags from AniList synopsis
        import re
        clean = re.sub(r"<[^>]+>", "", result.synopsis)
        console.print(clean[:500])

    if chars:
        console.print(f"\n[bold]Characters ({len(chars)}):[/bold]")
        table = Table()
        table.add_column("Name", style="bold")
        table.add_column("Role")
        table.add_column("Description", max_width=50)
        for c in chars[:10]:
            desc = c.get("description", "")[:100]
            import re
            desc = re.sub(r"<[^>]+>", "", desc)  # strip HTML
            desc = re.sub(r"~!.*?!~", "", desc)  # strip spoiler tags
            table.add_row(c["name"], c["role"], desc)
        console.print(table)
