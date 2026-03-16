# bee-revenue

Exploring and building automated revenue streams — content, trading, and AI-powered services.

## Projects

### [bee-content/research](bee-content/research/)
YouTube competitor analysis CLI + MCP server. Discover niches, find content gaps, detect viral outliers, benchmark competitors — all without API keys.

**Status:** Built and working (v0.1.0)
**Stack:** Python, typer, yt-dlp, scrapetube, youtube-transcript-api, SQLite
**Features:**
- 8 analyzers: content gaps, outlier detection, title patterns, engagement, benchmarks, SEO, timing, regional/language
- Channel discovery via keyword search and snowball
- CLI with rich terminal output + MCP server (23 tools)
- 66 tests passing

### [bee-content/video-editor](bee-content/video-editor/)
AI-assisted video production from markdown assembly guides. Parses structured guides into segments, generates graphics/narration/trimmed footage, and assembles final videos.

**Status:** Built and working (v0.1.0)
**Stack:** Python, typer, FFmpeg, Pillow, Edge TTS/Kokoro/OpenAI, Streamlit dashboard
**Features:**
- Assembly guide parser (markdown → structured segments)
- 14 FFmpeg operations (trim, grade, overlay, concat, normalize)
- 6 graphics types (lower thirds, timelines, quotes, financial cards)
- 3 TTS engines with fallback (Edge, Kokoro, OpenAI)
- 58 tests passing

### [bee-content/discovery](bee-content/discovery/)
Content discovery research — niche analysis, competitor deep dives, content sourcing strategies, market opportunities.

**Status:** Research phase
**Research covers:**
- Dr Insanity channel analysis (50 videos, title formulas, engagement patterns)
- True crime niche competitive analysis (16 channels, 468 videos)
- Non-English true crime landscape (10 languages, CPM-prioritized)
- True crime content sourcing guide (public records, FOIA, databases, bodycam footage)
- Faceless YouTube channel case studies, monetization, regions/languages
- Creative monetization & platform arbitrage strategies

### [bee-content/automation](bee-content/automation/)
Content production pipeline research — from topic selection to video publishing. Research on AI video generators, voiceover/TTS tools, editing tools, cost breakdowns, production workflows, legal landscape.

**Status:** Research phase

### [bee-trading](bee-trading/)
Research on automated trading, prediction markets, and AI/ML-powered market analysis.

**Status:** Research phase
**Research covers:** Stock market fundamentals, automated trading bots, prediction markets, AI/ML market prediction, trading tools ecosystem, Claude-assisted trading workflows

## Structure

```
bee-revenue/
├── bee-content/
│   ├── research/               # YouTube competitor analysis tool (Python CLI + MCP)
│   ├── video-editor/           # AI video production tool (Python CLI + dashboard)
│   ├── discovery/              # Niche research, competitor analysis, content sourcing
│   └── automation/             # Content production pipeline (research phase)
├── bee-trading/                # Trading & prediction markets (research phase)
└── research/                   # Bookmarks & general links
```
