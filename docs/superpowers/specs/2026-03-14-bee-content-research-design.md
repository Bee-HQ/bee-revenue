# bee-content-research — Design Spec

**Date:** 2026-03-14
**Status:** Approved
**Author:** Claude + bamboobee

---

## 1. Overview

`bee-content-research` is a Python CLI + MCP server for YouTube competitor analysis. It helps identify what content works in a niche, discover content gaps, detect viral outliers, and benchmark competitors — all without requiring a YouTube API key.

### Goals

- Discover competitor channels via keyword search, manual entry, or snowball (related channels)
- Fetch and cache video metadata, engagement metrics, and transcripts locally
- Run 7 analysis engines: content gaps, outlier detection, title patterns, niche benchmarking, engagement ratios, cross-channel comparison, regional/language analysis
- Expose functionality via CLI (typer) and MCP server, sharing the same core logic
- Design for future extensibility: REST API, web dashboard, Jupyter notebooks

### Non-Goals (v1)

- No web dashboard or UI (future)
- No ML/NLP models — simple statistical analysis only
- No automated content creation or publishing
- No real-time monitoring or scheduled fetches

---

## 2. Architecture

```
┌─────────────────────────────────────────────┐
│           Interface Adapters                │
│   ┌─────────┐  ┌─────────┐  ┌───────────┐  │
│   │   CLI   │  │   MCP   │  │ Future:   │  │
│   │ (typer) │  │ adapter │  │ REST/gRPC │  │
│   └────┬────┘  └────┬────┘  └─────┬─────┘  │
└────────┼────────────┼─────────────┼─────────┘
         │            │             │
         ▼            ▼             ▼
┌─────────────────────────────────────────────┐
│           Service Layer                     │
│   Protocol-agnostic Python functions        │
│   Returns dataclasses/dicts, not JSON       │
│   No knowledge of CLI args or MCP tools     │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌─────────┐ ┌────────┐ ┌──────────┐
    │Fetchers │ │Storage │ │Analyzers │
    └─────────┘ └────────┘ └──────────┘
```

### Key Principle

The service layer is the API boundary. Adapters (CLI, MCP, future REST) are thin translators that call service functions. Swapping MCP for another protocol means writing a new adapter file — nothing else changes.

### Layer Responsibilities

- **Adapters** — translate protocol (CLI args, MCP JSON, REST HTTP) into service function calls. No business logic.
- **Services** — orchestrate workflows by calling fetchers, storage, and analyzers. Protocol-agnostic. Return dataclasses/dicts.
- **Analyzers** — pure analysis logic. Take DataFrames/dicts in, return results out. No I/O.
- **Fetchers** — handle all external HTTP calls to YouTube (yt-dlp, scrapetube, transcript-api). Implement rate limiting.
- **Storage** — SQLite read/write. Schema migrations.

### Rate Limiting & Politeness

All fetchers enforce request pacing to avoid YouTube throttling:
- Default delay: 1-2 seconds between requests
- Configurable via `--delay` flag or `BCR_DELAY` env var
- Exponential backoff on HTTP 429/503 responses (max 3 retries)
- Default `--max-videos 200` per channel (configurable)
- Progress bar shows fetch progress and ETA

### Error Handling & Partial Failures

The tool uses a **skip-and-warn** model:
- If one channel fails to fetch, log a warning and continue with remaining channels
- If a transcript is unavailable, mark `has_transcript=False` and continue
- If yt-dlp returns incomplete metadata, store what is available
- All warnings are collected and displayed at the end of a command
- The `status` command shows data completeness (e.g., "45/50 videos fetched, 3 channels missing transcripts")

### Cache Freshness

- `fetched_at` timestamp on every record
- Default TTL: 7 days — `fetch` skips channels/videos fetched within TTL
- `--force` flag to re-fetch regardless of TTL
- `status` command shows data age per channel

---

## 3. Project Structure

```
bee-content-research/
├── pyproject.toml
├── src/
│   └── bee_content_research/
│       ├── __init__.py
│       ├── services/           # Protocol-agnostic API (thin orchestrators)
│       │   ├── __init__.py
│       │   ├── discovery.py    # discover_channels, snowball, add_channel
│       │   ├── analysis.py     # delegates to analyzers/*.py, no analysis logic here
│       │   ├── groups.py       # niche group management
│       │   └── reporting.py    # full_report, export
│       ├── adapters/           # Protocol-specific thin layers
│       │   ├── __init__.py
│       │   ├── cli.py          # typer CLI, calls services
│       │   └── mcp.py          # MCP server, calls services
│       ├── fetchers/           # Data collection layer
│       │   ├── __init__.py
│       │   ├── channel.py      # Channel discovery & metadata (yt-dlp + scrapetube)
│       │   ├── video.py        # Video metadata (yt-dlp)
│       │   ├── transcript.py   # Transcript extraction (youtube-transcript-api)
│       │   ├── search.py       # Keyword search & YouTube suggest API
│       │   └── snowball.py     # Related channel discovery (featured channels, collaborations)
│       ├── storage/            # SQLite cache layer
│       │   ├── __init__.py
│       │   ├── db.py           # Connection management, migrations
│       │   └── models.py       # Schema definitions
│       ├── analyzers/          # Analysis engine
│       │   ├── __init__.py
│       │   ├── outliers.py     # Outlier/viral detection
│       │   ├── content_gaps.py # Content gap finder
│       │   ├── titles.py       # Title/thumbnail pattern analysis
│       │   ├── engagement.py   # Engagement ratio scoring
│       │   ├── benchmarks.py   # Niche benchmarking
│       │   ├── seo.py          # Tag/keyword analysis
│       │   ├── timing.py       # Upload timing patterns
│       │   └── regional.py     # Country/language/region analysis
│       └── formatters.py       # Rich tables, JSON/CSV export helpers
└── tests/
```

---

## 4. Data Model (SQLite)

### channels

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | YouTube channel ID |
| name | TEXT | Channel name |
| handle | TEXT | @handle |
| subscriber_count | INT | Subscriber count |
| video_count | INT | Total videos |
| view_count | INT | Total channel views |
| country | TEXT | Channel country |
| language | TEXT | Primary language |
| description | TEXT | Channel description |
| thumbnail_url | TEXT | Channel thumbnail |
| fetched_at | TIMESTAMP | When data was fetched |
| discovered_via | TEXT | "manual", "keyword:finance", "snowball:UC..." |

### videos

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | YouTube video ID |
| channel_id | TEXT FK | References channels.id |
| title | TEXT | Video title |
| description | TEXT | Video description |
| tags | TEXT | JSON array of tags |
| category | TEXT | YouTube category |
| duration | INT | Duration in seconds |
| view_count | INT | View count |
| like_count | INT | Like count |
| comment_count | INT | Comment count |
| published_at | TIMESTAMP | Publish date |
| thumbnail_url | TEXT | Thumbnail URL |
| language | TEXT | Detected language |
| fetched_at | TIMESTAMP | When data was fetched |
| has_transcript | BOOL | Whether transcript was fetched |

### transcripts

| Column | Type | Description |
|--------|------|-------------|
| video_id | TEXT PK FK | References videos.id |
| language | TEXT | Transcript language |
| text | TEXT | Full transcript text |
| fetched_at | TIMESTAMP | When fetched |

### niche_groups

| Column | Type | Description |
|--------|------|-------------|
| id | INT PK AUTO | Auto-increment ID |
| name | TEXT UNIQUE | Group name ("personal finance") |
| created_at | TIMESTAMP | When created |

### niche_group_channels (join table)

| Column | Type | Description |
|--------|------|-------------|
| group_id | INT FK | References niche_groups.id |
| channel_id | TEXT FK | References channels.id |
| added_at | TIMESTAMP | When channel was added to group |
| PK | (group_id, channel_id) | Composite primary key |

---

## 5. CLI Commands

### Discovery & Data

```
bee-research discover <keyword>                    # Find channels by keyword
bee-research discover --snowball <channel_url>      # Discover related channels
bee-research add <channel_url> [...]               # Manually add channels
bee-research fetch <channel_id|niche>              # Fetch/refresh video data
bee-research fetch --transcripts                   # Also fetch transcripts
```

### Niche Groups

```
bee-research group create <name> <channel_ids...>  # Create group
bee-research group list                            # List groups
bee-research group show <name>                     # Show group channels
bee-research group add <name> <channel_ids...>     # Add channels to group
bee-research group remove <name> <channel_ids...>  # Remove channels from group
```

### Analysis

```
bee-research analyze outliers <target>             # Viral/outlier videos
bee-research analyze gaps <niche>                  # Content gaps
bee-research analyze titles <target>               # Title pattern analysis
bee-research analyze engagement <target>           # Engagement ratios
bee-research analyze benchmark <niche>             # Niche averages
bee-research analyze seo <target>                  # Tag/keyword analysis
bee-research analyze timing <target>               # Upload timing
bee-research analyze compare <ch1> <ch2> [...]     # Side-by-side comparison
bee-research analyze regional <niche>              # Country/language breakdown
```

### Reports & Export

```
bee-research report <niche>                        # Full report (all analyzers)
bee-research report <niche> --format json|csv      # Export report as JSON/CSV
bee-research status                                # Cached data stats + data freshness
```

`<target>` accepts either a channel ID or a niche group name.

---

## 6. MCP Server Tools

The MCP adapter exposes the same service layer as the CLI:

### Discovery & Data

- `discover_channels(keyword, max_results=20)` — find channels by keyword search
- `add_channel(url)` — manually add a channel to the database
- `snowball_discover(channel_url, depth=1)` — discover related channels via featured channels and collaborations
- `fetch_channel(channel_id, include_transcripts=False)` — fetch video data for a single channel
- `fetch_niche(niche_name, include_transcripts=False)` — fetch video data for all channels in a niche group

### Groups

- `create_niche_group(name, channel_ids)` — create niche group
- `list_niche_groups()` — list all groups
- `add_to_group(niche_name, channel_ids)` — add channels to existing group
- `remove_from_group(niche_name, channel_ids)` — remove channels from group

### Analysis

- `find_outliers(target, threshold=2.0)` — find viral outlier videos
- `find_content_gaps(niche)` — identify uncovered topics
- `analyze_titles(target)` — title pattern analysis
- `analyze_engagement(target)` — engagement ratio scoring
- `benchmark_niche(niche)` — niche averages and benchmarks
- `analyze_seo(target)` — tag/keyword analysis
- `analyze_timing(target)` — upload timing patterns
- `compare_channels(channel_ids)` — side-by-side comparison
- `analyze_regional(niche)` — country/language breakdown
- `full_report(niche)` — run all analyzers

### Utilities

- `get_status()` — cached data statistics
- `get_channel_info(channel_id)` — channel details
- `get_video_info(video_id)` — video details

All tools return structured JSON. The MCP adapter is a thin translation layer — replacing it with another protocol adapter requires no changes to the service layer or analyzers.

---

## 7. Analyzer Algorithms

### 7.1 Content Gap Finder (Priority 1)

1. Collect all video titles + tags + transcripts across a niche group
2. Build a topic frequency map (keyword extraction via n-gram counting on titles/tags/transcripts)
3. Cross-reference against YouTube search suggestions (via `http://suggestqueries.google.com/complete/search?client=youtube&q=...` — undocumented but stable public endpoint, no API key needed)
4. Gap = high search demand (suggestions) + low coverage (few/no competitor videos)
5. Output: ranked list of uncovered topics with estimated demand

### 7.2 Outlier Detection (Priority 2)

1. For each channel, calculate median views per video (last 50-100 videos)
2. Flag videos exceeding `threshold × median` (default 2x)
3. Also flag by engagement ratio outliers (like/view, comment/view)
4. Output: outlier videos with multiplier, title, tags, published date

### 7.3 Title/Thumbnail Pattern Analysis (Priority 3)

1. Extract patterns: length, question vs statement, number usage ("Top 10"), power words, emoji
2. Cluster titles by format pattern
3. Correlate patterns with view performance
4. Output: pattern → average performance table, best-performing formats

### 7.4 Niche Benchmarking (Priority 4)

1. Aggregate across all channels in niche group:
   - Median views, likes, comments per video
   - Average upload frequency (videos/week)
   - Average video duration
   - Subscriber-to-view ratio
2. Segment by country/language if data available
3. Output: benchmark table + per-channel deviation from benchmarks

### 7.5 Engagement Ratio Analysis (Priority 5)

1. Calculate per video: like/view %, comment/view %, like/comment ratio
2. Rank by weighted composite engagement score
3. Identify "high engagement, low views" hidden gems
4. Output: engagement leaderboard + hidden gems list

### 7.6 Cross-Channel Comparison (Priority 6)

1. Side-by-side metrics for 2+ channels
2. Compare: subscribers, avg views, upload frequency, engagement rates, top tags, topics
3. Highlight where each channel outperforms others
4. Output: comparison table with winner per metric

### 7.7 Regional/Language Analysis (Priority 7)

1. Group videos by detected language
2. Map channels to countries
3. Calculate CPM-adjusted revenue estimates (Norway $43 vs India $0.50)
4. Identify underserved language/region opportunities
5. Output: language distribution, estimated RPM per region, opportunity scores

All analyzers use stdlib (`statistics`, `collections.Counter`) and basic Python for computation. No ML libraries or heavy dependencies in v1. Content gap finder optionally uses transcripts, falls back to titles + tags.

### Snowball Discovery (Implementation Note)

YouTube removed the public "Related Channels" feature. Snowball discovery uses these fallback strategies:
1. **Featured channels** — scrape the "Featured Channels" section from channel pages (many creators list related channels)
2. **Collaboration detection** — scan video descriptions and titles for @mentions of other channels
3. **Search expansion** — take the seed channel's top keywords/tags and search for other channels covering the same topics
4. If none of these yield results, the command warns the user and suggests using keyword discovery instead.

---

## 8. Dependencies

### Required

| Package | Purpose |
|---------|---------|
| python >= 3.11 | Runtime |
| typer | CLI framework |
| rich | Terminal tables, progress bars |
| yt-dlp | Video/channel metadata (no API key) |
| scrapetube | Channel/playlist enumeration (no API key) |
| youtube-transcript-api | Transcript extraction (no API key) |
| mcp | Official MCP Python SDK |

### Built-in (no install)

| Package | Purpose |
|---------|---------|
| sqlite3 | Local database |
| json | JSON handling |
| csv | CSV export |

### Optional (future)

| Package | Purpose |
|---------|---------|
| pandas | Data manipulation (for notebooks/dashboard) |
| python-youtube | YouTube Data API v3 (if user has API key) |
| matplotlib / plotly | Charts (dashboard/notebooks) |
| fastapi | REST API adapter |

### Tooling

- Package manager: `uv`
- No API keys required for v1

---

## 9. Data Flow Examples

### Competitor Analysis Workflow

```
1. bee-research discover "personal finance"
   → Searches YouTube, finds 20 channels
   → Stores in channels table with discovered_via="keyword:personal finance"

2. bee-research discover --snowball @GrahamStephan
   → Finds related channels via YouTube recommendations
   → Stores with discovered_via="snowball:UC..."

3. bee-research group create "finance" UC1 UC2 UC3 UC4 UC5
   → Creates niche group linking 5 channels

4. bee-research fetch finance --transcripts
   → Fetches all videos for 5 channels via yt-dlp
   → Fetches transcripts for each video
   → Stores in videos + transcripts tables

5. bee-research analyze gaps finance
   → Reads all videos/transcripts for finance group
   → Builds topic map, cross-refs with search suggestions
   → Outputs ranked content gaps

6. bee-research report finance
   → Runs all 7 analyzers
   → Outputs comprehensive report
```

### MCP Usage (via Claude)

```
User: "What content gaps exist in the personal finance YouTube niche?"

Claude calls: discover_channels("personal finance")
Claude calls: create_niche_group("finance", [...channel_ids...])
Claude calls: fetch_channel("finance", include_transcripts=True)
Claude calls: find_content_gaps("finance")
Claude: "Based on analyzing 5 channels and 500+ videos, here are the
         top content gaps in personal finance..."
```

---

## 10. Future Extensibility

### Web Dashboard (v2)

- Add `adapters/rest.py` using FastAPI
- Serve analysis results as REST endpoints
- Build frontend (React/Svelte) consuming the API
- Same service layer, new adapter

### Jupyter Notebooks (v2)

- Import `bee_content_research.services` directly
- Use pandas DataFrames from analyzers
- Add matplotlib/plotly visualizations

### Additional Platforms (v3)

- Add new fetchers for TikTok, Instagram, etc.
- Same analyzer patterns, different data sources
- Storage schema extends with platform-specific tables
