# bee-content-automation

Automated anime/manga/manhwa YouTube content pipeline.

## Quick Start

```bash
cd bee-content-automation

# Search for manga
uv run bee-auto search "Solo Leveling"

# Show trending
uv run bee-auto trending

# List chapters
uv run bee-auto chapters "One Piece"

# Get chapter summary
uv run bee-auto summary "Naruto" 1

# Full series info
uv run bee-auto info "Jujutsu Kaisen"
```

## Sources

- **AniList** — Trending series, metadata, characters, genres/tags
- **MangaDex** — Chapter listings, page images
- **MangaUpdates** — Release tracking, series metadata
- **Fandom Wiki** — Chapter synopses, character info

## Architecture

```
Sources (AniList, MangaDex, MangaUpdates, Fandom)
    → Script Generator (LLM-assisted)
    → Visual Assembly (future)
    → Production (future)
    → Publishing (future)
```
