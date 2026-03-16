# bee-content/research

YouTube competitor analysis CLI + MCP server. Zero API keys required.

## Quick Start

```bash
cd bee-content/research
export PATH="$HOME/.local/bin:$PATH"

# All commands use: uv run bee-research <command>
```

## Commands Reference

### Add & Remove Channels

```bash
# Add by @handle, URL, or channel ID
uv run bee-research add @MrBeast
uv run bee-research add https://www.youtube.com/@MrBeast
uv run bee-research add UCX6OQ3DkcsbYNE6H8uQQuVA

# Add multiple at once
uv run bee-research add @MrBeast @MarkRober @Veritasium

# Remove a channel (deletes all its videos, transcripts, group memberships)
uv run bee-research remove UCX6OQ3DkcsbYNE6H8uQQuVA
```

### Discover Channels

```bash
# Search by keyword — finds channels covering that topic
uv run bee-research discover "personal finance"
uv run bee-research discover "horror stories" --max-results 10

# Snowball — discover related channels from a seed channel
uv run bee-research discover @MrBeast --snowball
```

### Fetch Video Data

```bash
# Fetch videos for a channel (default: last 200 videos)
uv run bee-research fetch UCX6OQ3DkcsbYNE6H8uQQuVA

# Fetch with options
uv run bee-research fetch UCX6OQ3DkcsbYNE6H8uQQuVA --max-videos 50
uv run bee-research fetch UCX6OQ3DkcsbYNE6H8uQQuVA --force          # ignore cache TTL
uv run bee-research fetch UCX6OQ3DkcsbYNE6H8uQQuVA --transcripts    # also fetch transcripts (slower)

# Fetch all channels in a niche group
uv run bee-research fetch my_niche_group --force
```

### Niche Groups

```bash
# Create a group of channels for comparison
uv run bee-research group create finance UC1 UC2 UC3

# List all groups
uv run bee-research group list

# Show channels in a group
uv run bee-research group show finance

# Add/remove channels from existing group
uv run bee-research group add finance UC4 UC5
uv run bee-research group remove finance UC3
```

### Analysis (the main feature)

All analyze commands accept either a channel ID or a niche group name as `<target>`.

```bash
# Content gaps — topics with search demand but low competitor coverage
uv run bee-research analyze gaps <niche_group>

# Outlier detection — viral videos that outperform channel average
uv run bee-research analyze outliers <target>
uv run bee-research analyze outliers <target> --threshold 3.0  # 3x median

# Title patterns — what title formats get the most views
uv run bee-research analyze titles <target>

# Engagement — like/view %, comment/view %, hidden gems
uv run bee-research analyze engagement <target>

# Niche benchmarks — median views, upload frequency, duration averages
uv run bee-research analyze benchmark <niche_group>

# SEO — tag frequency, shared vs unique tags, performance correlation
uv run bee-research analyze seo <target>

# Upload timing — best day/hour to upload
uv run bee-research analyze timing <target>

# Cross-channel comparison — side-by-side metrics
uv run bee-research analyze compare UC1 UC2 UC3

# Regional/language — country distribution, CPM estimates, opportunities
uv run bee-research analyze regional <niche_group>
```

### Output Formats

All analyze commands support `--format`:

```bash
uv run bee-research analyze engagement <target> --format table   # default: rich tables
uv run bee-research analyze engagement <target> --format json    # JSON output
uv run bee-research analyze engagement <target> --format csv     # CSV output
```

### Full Report

```bash
# Run ALL analyzers at once
uv run bee-research report <niche_group>
uv run bee-research report <niche_group> --format json
```

### Status

```bash
# Show what's cached
uv run bee-research status
```

## Full Workflow Example

```bash
# 1. Add competitors
uv run bee-research add @MrBeast @MarkRober @Veritasium @kurzgesagt @3Blue1Brown

# 2. Create a niche group (use channel IDs from add output)
uv run bee-research group create science UCX6OQ3DkcsbYNE6H8uQQuVA UCYO_jab_esuFRV4b17AJtAw UCHnyfMqiRRG1u-2MsSQLbXA UC9-y-6csu5WGm29I7JiwpnA UCUHW94eEFW7hkUMVaZz4eDg

# 3. Fetch all video data
uv run bee-research fetch science --max-videos 50 --force

# 4. Run analysis
uv run bee-research analyze outliers science
uv run bee-research analyze gaps science
uv run bee-research analyze titles science
uv run bee-research analyze engagement science
uv run bee-research analyze benchmark science
uv run bee-research analyze compare UCX6OQ3DkcsbYNE6H8uQQuVA UCYO_jab_esuFRV4b17AJtAw

# 5. Or run everything at once
uv run bee-research report science --format json
```

## Architecture

```
Adapters (CLI / MCP) → Services → Fetchers + Storage + Analyzers
```

- **Adapters:** `src/bee_content_research/adapters/cli.py`, `mcp_adapter.py`
- **Services:** `src/bee_content_research/services/` — protocol-agnostic orchestration
- **Fetchers:** `src/bee_content_research/fetchers/` — yt-dlp, scrapetube, transcript-api
- **Storage:** `src/bee_content_research/storage/` — SQLite at `~/.bee-content-research/bee_content_research.db`
- **Analyzers:** `src/bee_content_research/analyzers/` — pure analysis logic, no I/O

## MCP Server

The MCP server exposes all functionality as tools for Claude/AI assistants.

```bash
# Run MCP server
uv run bee-research-mcp
```

Available tools: `discover_channels`, `add_channel`, `remove_channel`, `snowball_discover`, `fetch_channel`, `fetch_niche`, `create_niche_group`, `list_niche_groups`, `add_to_group`, `remove_from_group`, `find_outliers`, `find_content_gaps`, `analyze_titles`, `analyze_engagement`, `benchmark_niche`, `analyze_seo`, `analyze_timing`, `compare_channels`, `analyze_regional`, `full_report`, `get_status`, `get_channel_info`, `get_video_info`

## Key Details

- **Database:** SQLite at `~/.bee-content-research/bee_content_research.db`
- **Cache TTL:** 7 days (use `--force` to bypass)
- **Rate limiting:** 1.5s delay between YouTube requests (configurable with `--delay`)
- **Max videos:** 200 per channel default (configurable with `--max-videos`)
- **No API keys needed:** Uses yt-dlp, scrapetube, youtube-transcript-api (all scraping-based)

## Tests

```bash
uv run pytest tests/ -v   # 66 tests
```

## Future Work / TODOs

- [ ] **Screenplay Analyzer** — `bee-research analyze screenplay <youtube_url>` command that:
  - Pulls transcript via youtube-transcript-api
  - Breaks down script structure (hook, tension points, cliffhangers, resolution)
  - Maps to screenplay frameworks (Save The Cat beats, Story Grid, Hero's Journey for true crime)
  - Scores retention techniques (open loops, pattern interrupts, curiosity gaps)
  - Identifies section timing (intro %, buildup %, climax %, resolution %)
  - Outputs a production blueprint (title formula, script template, voiceover notes, visual cues)
  - Available via both CLI and MCP server
  - Reference: `research/youtube-screenplay-analysis-ai-scriptwriting.md`

- [ ] **Transcript-powered content gap analysis** — improve `analyze gaps` to use transcripts for deeper topic extraction (currently title/tag only)

- [ ] **Historical tracking** — scheduled re-fetches (cron) to track channel growth over time

- [ ] **Web dashboard** — FastAPI + frontend for visual analysis (adapters/rest.py)

- [ ] **Jupyter notebook support** — import services directly for interactive analysis

- [ ] **Multi-platform support** — add fetchers for TikTok, Instagram (using tools from `research/social-media-content-research-analytics-tools.md`)

## Dependencies

typer, rich, yt-dlp, scrapetube, youtube-transcript-api, mcp (optional)
