# Open Source YouTube Content Research & Analytics Tools

> Research date: 2026-03-14

## Executive Summary

This document catalogs open source tools, libraries, and projects for YouTube content research and analytics -- specifically tools that help analyze what type of content works on YouTube, including niche research, competitor analysis, trending topics, SEO, and engagement metrics.

The ecosystem breaks down into several categories:
1. **No-API scraping libraries** (scrapetube, youtube-search-python) for data collection without quotas
2. **YouTube Data API wrappers** (python-youtube, youtube-data-api) for structured API access
3. **Specialized analytics tools** (analytix, youtube-trend-dashboard) for specific analysis tasks
4. **MCP servers** (youtube-mcp-server, youtube-connector-mcp) for AI-assisted research
5. **CLI tools** (yt-dlp, youtool) for command-line data extraction
6. **Transcript tools** (youtube-transcript-api) for content analysis via transcripts
7. **Academic/research projects** (youtube-engagement) for data science approaches

---

## Comparison Table: Top Tools at a Glance

| Tool | Stars | Language | API Key? | Last Active | Best For |
|------|-------|----------|----------|-------------|----------|
| **yt-dlp** | 151,194 | Python | No | Mar 2026 | Metadata extraction via `--dump-json`, bulk data collection |
| **youtube-transcript-api** | 7,054 | Python | No | Mar 2026 | Transcript extraction for content analysis, topic research |
| **youtube/api-samples** | 5,951 | Multi | Yes | Mar 2026 | Official reference for YouTube API integration |
| **youtube-search-python** | 803 | Python | No | ARCHIVED | Search, video/channel/playlist info without API |
| **scrapetube** | 490 | Python | No | Feb 2026 | Scraping channels, playlists, search results |
| **YouTube-operational-API** | 489 | PHP | No | Apr 2024 | Self-hosted YouTube API alternative |
| **youtube-mcp-server** (Zubeid) | 459 | TypeScript | Yes | Mar 2026 | AI-assisted YouTube research via Claude/Cursor |
| **python-youtube** | 353 | Python | Yes | Mar 2026 | Full YouTube Data API v3 wrapper |
| **the-youtube-scraper** | 175 | Python | No | May 2024 | Video descriptions + comments without API |
| **patrickloeber/youtube-analyzer** | 95 | Python | Yes | Jan 2020 | Channel statistics extraction |
| **SMAPPNYU/youtube-data-api** | 84 | Python | Yes | Dec 2020 | Academic research data collection |
| **youtube-connector-mcp** | 74 | Python | Yes | Mar 2026 | MCP server for Claude + YouTube analytics |
| **PythonicCafe/youtool** | 70 | Python | Yes | Oct 2024 | Batch API access + scraping + transcripts |
| **SocialBlade/socialblade-js** | 50 | TypeScript | Yes* | Mar 2026 | Channel growth/stats via SocialBlade API |
| **parafoxia/analytix** | 44 | Python | OAuth | Mar 2026 | YouTube Analytics API (your own channel data) |
| **YoutubeTags** | 44 | Python | No | Jan 2026 | SEO tag extraction without API |
| **youtube-trend-dashboard** | 41 | Python | Yes+OpenAI | Apr 2024 | Trend + sentiment analysis dashboard |
| **youtube-engagement** | 25 | Python | No | Nov 2025 | Academic engagement prediction (ICWSM paper) |
| **leonardogrig/youtube-niche-research-tool** | 20 | TypeScript | No* | Mar 2026 | Competitor dashboard with outlier detection |
| **Youtube-Channel-Analytics-Dashboard** | 11 | Python | Yes | Nov 2025 | Channel analytics + network analysis + forecasting |
| **StaTube** | 4 | Python | No | Mar 2026 | Desktop GUI: transcript + comment NLP analysis |
| **pauling-ai/youtube-mcp-server** | 5 | Python | OAuth | Mar 2026 | Most comprehensive MCP: 40 tools incl. SEO + revenue |

*\* SocialBlade requires their commercial API key. leonardogrig tool uses internal DB, not directly YouTube API.*

---

## 1. No-API Scraping Libraries (No YouTube API Key Needed)

### scrapetube
- **GitHub:** https://github.com/dermasmid/scrapetube
- **Stars:** 490 | **Language:** Python | **License:** MIT
- **Last Release:** v2.6.0 (Sep 2025) | **Last Updated:** Feb 2026
- **API Key:** Not required
- **Install:** `pip install scrapetube`
- **Docs:** https://scrapetube.readthedocs.io/en/latest/

**What it does:**
- Scrape all videos from any YouTube channel (returns video IDs + metadata)
- Scrape all videos from any playlist
- Search YouTube programmatically
- No Selenium or browser required -- pure HTTP requests

**Content research use cases:**
- Enumerate all videos from competitor channels
- Analyze upload frequency and patterns
- Collect video IDs for further analysis with other tools
- Search for content in specific niches
- Build datasets of videos for trend analysis

**Limitations:** Returns basic metadata (video IDs, titles). For detailed stats (views, likes), you need to combine with another tool or API.

---

### youtube-search-python
- **GitHub:** https://github.com/alexmercerind/youtube-search-python
- **Stars:** 803 | **Language:** Python | **License:** MIT
- **Status:** ARCHIVED (June 2022) -- no longer maintained
- **API Key:** Not required
- **Install:** `pip install youtube-search-python`

**What it does:**
- Search YouTube videos, channels, playlists
- Get video info from links (views, duration, thumbnails)
- Get playlist info from links
- Get search suggestions/autocomplete
- Supports region-specific search
- Both sync and async interfaces

**Content research use cases:**
- Search for content in specific niches without API quotas
- Get search suggestions to discover trending queries
- Analyze video metadata (views, channel info)

**Warning:** Archived since June 2022. May break as YouTube changes its frontend. Consider alternatives like scrapetube or yt-dlp for active projects.

---

### YoutubeTags
- **GitHub:** https://github.com/nuhmanpk/YoutubeTags
- **Stars:** 44 | **Language:** Python | **License:** MIT
- **Last Release:** v1.4 (Aug 2022) | **Last Updated:** Jan 2026
- **API Key:** Not required
- **Install:** `pip install YoutubeTags`

**What it does:**
- Extract video tags/keywords from any YouTube video URL
- Extract channel tags/keywords
- Get video titles and descriptions
- Get channel descriptions

**Content research use cases:**
- Analyze competitors' SEO tag strategies
- Discover keywords used by successful videos
- Compare tag strategies across niches
- Build keyword databases from top-performing content

---

### the-youtube-scraper
- **GitHub:** https://github.com/hridaydutta123/the-youtube-scraper
- **Stars:** 175 | **Language:** Python
- **Last Updated:** May 2024
- **API Key:** Not required

**What it does:**
- Download video descriptions and comments without API
- Supports single video or batch processing with parallel execution
- Outputs data in JSON format
- Extracts: title, duration, upload date, genre, statistics, uploader info, comments (author, text, timestamp)

**Content research use cases:**
- Analyze comment sentiment and engagement patterns
- Study video descriptions for SEO patterns
- Batch process large sets of videos for research

---

### YouTube-operational-API
- **GitHub:** https://github.com/Benjamin-Loison/YouTube-operational-API
- **Stars:** 489 | **Language:** PHP
- **Last Updated:** Apr 2024
- **API Key:** Not required (optional)

**What it does:**
- Self-hosted alternative to YouTube Data API v3
- Endpoints: channels, videos, playlists, playlistItems, search, commentThreads, community posts, live chats
- Reverse-engineers YouTube's operational endpoints
- Docker deployment available

**Content research use cases:**
- Unlimited API-like access without quotas
- Search, channel data, video data, comments -- all without official API
- Useful for large-scale data collection projects

**Note:** Requires self-hosting (Apache/PHP or Docker). More complex setup but avoids all API quota limits.

---

## 2. YouTube Data API Wrappers (API Key Required)

### python-youtube
- **GitHub:** https://github.com/sns-sdks/python-youtube
- **Stars:** 353 | **Language:** Python
- **Last Release:** v0.9.8 (Aug 2025) | **Last Updated:** Mar 2026
- **API Key:** Required
- **Install:** `pip install python-youtube`

**What it does:**
- Full YouTube Data API v3 wrapper
- Modern `Client` class (recommended) + legacy `Api` class
- All resource methods: channels, videos, playlists, comments, search
- OAuth support for authenticated access
- Returns Python objects or raw JSON

**Content research use cases:**
- Get detailed channel statistics (subscribers, total views, video count)
- Search for videos by keyword with filters (date, duration, type)
- Analyze video statistics (views, likes, comments, tags)
- List all videos from channels/playlists with full metadata
- Comment analysis

**Best YouTube API wrapper currently maintained.**

---

### SMAPPNYU/youtube-data-api
- **GitHub:** https://github.com/SMAPPNYU/youtube-data-api
- **Stars:** 84 | **Language:** Python/Jupyter
- **Last Updated:** Dec 2020 (maintenance only)
- **API Key:** Required
- **Install:** `pip install youtube-data-api`

**What it does:**
- Simplified Python client for YouTube Data API v3
- Designed for academic research (from NYU Social Media Lab)
- Automated data field collection including hidden fields
- Search and data collection focused

**Content research use cases:**
- Academic-style systematic data collection
- Search and aggregate video data
- Built for research workflows

**Note:** Not actively maintained since 2020, but still functional for basic API access.

---

### google-api-python-client
- **PyPI:** https://pypi.org/project/google-api-python-client/
- **Version:** 2.192.0 (Mar 2026) | **Language:** Python
- **API Key:** Required
- **Install:** `pip install google-api-python-client`

**What it does:**
- Official Google API client library
- Supports all Google APIs via discovery mechanism
- The foundation most YouTube API tools are built on

**Content research use cases:**
- Direct access to YouTube Data API v3, YouTube Analytics API, YouTube Reporting API
- Maximum flexibility but requires more boilerplate code
- Use when you need features not covered by wrapper libraries

---

### youtube/api-samples
- **GitHub:** https://github.com/youtube/api-samples
- **Stars:** 5,951 | **Language:** Multi (Java, Python, JavaScript, PHP, Ruby, Go)
- **Last Updated:** Mar 2026
- **API Key:** Required

**What it does:**
- Official code samples from YouTube for Data API, Analytics API, Live Streaming API
- Reference implementations in multiple languages

**Use case:** Starting point for building custom analytics tools. Not a library, but invaluable reference code.

---

## 3. CLI Tools

### yt-dlp
- **GitHub:** https://github.com/yt-dlp/yt-dlp
- **Stars:** 151,194 | **Language:** Python | **License:** Unlicense
- **Last Updated:** Mar 2026 (very actively maintained)
- **API Key:** Not required
- **Install:** `pip install yt-dlp` or `brew install yt-dlp`

**Metadata extraction (analytics-relevant features):**
While primarily a downloader, yt-dlp is extremely powerful for metadata extraction:

```bash
# Dump all video metadata as JSON (no download)
yt-dlp --dump-json --no-download "VIDEO_URL"

# Dump metadata for all videos in a channel
yt-dlp --dump-json --no-download --flat-playlist "CHANNEL_URL"

# Extract specific fields
yt-dlp --print "%(title)s | %(view_count)s | %(like_count)s | %(tags)s" "VIDEO_URL"
```

**Available metadata fields include:**
- `title`, `description`, `tags`, `categories`
- `view_count`, `like_count`, `comment_count`
- `duration`, `upload_date`
- `channel`, `channel_id`, `channel_follower_count`
- `thumbnails`, `thumbnail`
- `average_rating`
- `age_limit`
- `webpage_url`

**Content research use cases:**
- Bulk metadata extraction from channels/playlists without API limits
- Analyze titles, descriptions, tags across hundreds of videos
- Track view counts and engagement metrics
- Extract thumbnail URLs for analysis
- Feed data into analysis pipelines
- Channel subscriber counts

**This is arguably the most powerful free tool for bulk YouTube metadata collection.** No API key, no quotas, actively maintained with 151K+ stars.

---

### youtool
- **GitHub:** https://github.com/PythonicCafe/youtool
- **Stars:** 70 | **Language:** Python | **License:** LGPL-3.0
- **Last Updated:** Oct 2024
- **API Key:** Required
- **Install:** `pip install youtool`

**What it does:**
- Python library + CLI for YouTube Data API batch access
- Automatic API key rotation and quota tracking
- Batch processing (50 items per request)
- Automatic pagination
- Channel ID extraction from URLs (via scraping, no API needed)
- Channel metadata, video search, video statistics
- Comment threads, live chat, superchat data
- Automatic transcriptions
- Audio/video downloads

**Content research use cases:**
- Batch collect channel and video data efficiently
- API key rotation for large-scale research
- Combined API + scraping approach

---

## 4. Transcript & Content Analysis Tools

### youtube-transcript-api
- **GitHub:** https://github.com/jdepoix/youtube-transcript-api
- **Stars:** 7,054 | **Language:** Python
- **Last Updated:** Mar 2026 (actively maintained)
- **API Key:** Not required
- **Install:** `pip install youtube-transcript-api`

**What it does:**
- Extract transcripts/subtitles from any YouTube video
- Works with manually created and auto-generated subtitles
- Multi-language support with translation capability
- Output formats: JSON, WebVTT, SRT, CSV, plain text
- Proxy support for bypassing IP bans
- CLI tool included

**Content research use cases:**
- Analyze what topics successful videos cover (keyword extraction from transcripts)
- Study content patterns in specific niches
- Build topic models from video content
- Compare content strategies via transcript analysis
- Feed transcripts to LLMs for automated analysis
- Identify trending topics by analyzing transcripts of trending videos

**This is the most important tool for content-level analysis** since it lets you understand what videos actually talk about, not just their metadata.

---

### StaTube
- **GitHub:** https://github.com/Sakth1/StaTube
- **Stars:** 4 | **Language:** Python | **License:** MIT
- **Last Updated:** Mar 2026 (358 commits, actively developed)
- **API Key:** Not required

**What it does:**
- Desktop GUI app (PySide6/Qt6) for YouTube analysis
- Fetches channel videos, transcripts, and comments
- Sentiment analysis on comments (NLTK)
- Word cloud generation from transcripts and comments
- Local SQLite database for offline analysis
- Export analysis as images
- Uses yt-dlp + scrapetube + youtube-transcript-api under the hood

**Content research use cases:**
- Visual analysis of comment sentiment per video
- Word clouds to identify common themes/topics
- Desktop tool for non-programmers to analyze channels
- No API key means no quotas

---

## 5. Specialized Analytics & Research Tools

### analytix
- **GitHub:** https://github.com/parafoxia/analytix
- **Stars:** 44 | **Language:** Python
- **Last Release:** v5.5.1 (Mar 2026) | **Actively maintained**
- **API Key:** OAuth 2.0 required (for YOUR OWN channel)
- **Install:** `pip install analytix`

**What it does:**
- SDK for YouTube Analytics API (not Data API)
- Access YOUR channel's analytics: minutes watched, views, likes, comments
- Filter by country, date range, video dimensions
- Export to CSV, TSV, JSON, Excel, Parquet, Feather
- DataFrame support: pandas, Polars, Apache Arrow
- Session persistence, automatic token refresh

**Content research use cases:**
- Analyze YOUR OWN channel's performance data
- Export analytics for data science workflows
- Track performance trends over time

**Important:** This only works for channels you own/manage (requires OAuth). Not for analyzing competitors.

---

### youtube-trend-dashboard
- **GitHub:** https://github.com/madEffort/youtube-trend-dashboard
- **Stars:** 41 | **Language:** Python | **License:** Apache 2.0
- **Last Updated:** Apr 2024
- **API Key:** YouTube API + OpenAI API required

**What it does:**
- Streamlit dashboard for YouTube trend analysis
- Popular video upload patterns (by weekday/time)
- SEO metrics (average tags in popular videos)
- Word cloud of trending topics/keywords
- Comment sentiment analysis
- Child-safety assessment (profanity detection)
- Side-by-side video comparison

**Content research use cases:**
- Identify optimal upload timing patterns
- Analyze trending keywords in your niche
- Compare video performance visually
- Sentiment analysis of audience reactions

---

### youtube-engagement (Academic)
- **GitHub:** https://github.com/avalanchesiqi/youtube-engagement
- **Stars:** 25 | **Language:** Python | **License:** MIT
- **Paper:** "Beyond Views: Measuring and Predicting Engagement in Online Videos" (ICWSM 2018)

**What it does:**
- Large-scale dataset: 5.3M tweeted videos
- EngagementMap tool: outputs relative engagement scores based on video length + watch percentage
- Temporal analysis of viewer engagement patterns
- Prediction models for video engagement
- Quality video collections from Vevo, Billboard, top news channels

**Content research use cases:**
- Understand engagement patterns beyond view counts
- Predict potential engagement for video concepts
- Academic framework for measuring content quality

---

### Youtube-Channel-Analytics-Dashboard
- **GitHub:** https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard
- **Stars:** 11 | **Language:** Python (Streamlit)
- **Last Updated:** Nov 2025
- **API Key:** Required

**What it does:**
- Channel overview with key metrics
- Top videos ranking by views, likes, comments
- 30-day viewership forecasting (Facebook Prophet model)
- Tag word cloud generation
- Like-to-view ratio tracking
- Network graph of commenter relationships
- Community detection in comment networks

**Content research use cases:**
- Forecast viewership trends for channels
- Identify most effective tags via word clouds
- Discover commenter communities and engagement clusters
- Compare engagement ratios across videos

---

### YouTubeRankCalculator
- **GitHub:** https://github.com/inevolin/YouTubeRankCalculator
- **Stars:** 5 | **Language:** C# | **License:** MIT
- **Last Updated:** Oct 2024

**What it does:**
- YouTube keyword competitiveness analysis
- Algorithm to rank keyword difficulty
- Batch keyword processing
- Competitor research capabilities

**Content research use cases:**
- Evaluate keyword competition before creating content
- Find low-competition keywords in your niche

---

### leonardogrig/youtube-niche-research-tool
- **GitHub:** https://github.com/leonardogrig/youtube-niche-research-tool
- **Stars:** 20 | **Language:** TypeScript (Next.js)
- **Last Updated:** Mar 2026

**What it does:**
- Web dashboard showing competitor YouTube videos
- Advanced filtering by channel, view/like/comment counts, publish date
- **Outlier detection**: identifies videos exceeding channel averages by configurable multipliers
- Time period selection (1 week to 2 months)
- Redis caching for performance
- PostgreSQL + Prisma backend

**Content research use cases:**
- Identify viral/outlier videos in competitor channels
- Understand what content types outperform baseline
- Filter and sort competitor content by engagement metrics
- Systematic competitor analysis workflow

---

## 6. MCP Servers (AI-Assisted YouTube Research)

These are Model Context Protocol servers that let AI assistants (Claude, Cursor, etc.) interact with YouTube data directly.

### ZubeidHendricks/youtube-mcp-server
- **GitHub:** https://github.com/ZubeidHendricks/youtube-mcp-server
- **Stars:** 459 | **Language:** TypeScript
- **Last Updated:** Mar 2026
- **API Key:** YouTube Data API v3 required

**Tools provided:**
- Video details, statistics, search
- Transcript extraction (multi-language)
- Channel info and statistics
- Playlist management
- Search within transcripts

**Use case:** Ask Claude to analyze YouTube channels, compare videos, extract trends -- all through natural language.

---

### youtube-connector-mcp
- **GitHub:** https://github.com/ShellyDeng08/youtube-connector-mcp
- **Stars:** 74 | **Language:** Python
- **Last Updated:** Mar 2026
- **API Key:** YouTube Data API v3 required

**7 Tools:** youtube_search, youtube_get_video, youtube_get_channel, youtube_get_transcript, youtube_get_comments, youtube_get_playlist, youtube_list_playlists

**Use case:** Claude-powered YouTube research with search, transcripts, comments, and channel analytics.

---

### pauling-ai/youtube-mcp-server (Most Comprehensive)
- **GitHub:** https://github.com/pauling-ai/youtube-mcp-server
- **Stars:** 5 | **Language:** Python
- **Last Updated:** Mar 2026
- **API Key:** OAuth 2.0 required

**40 Tools spanning 3 YouTube APIs:**
- **Search & SEO:** youtube_search, youtube_search_suggestions, youtube_trending, youtube_get_categories
- **Analytics -- Performance:** overview, top_videos, top_shorts, video_detail
- **Analytics -- Audience:** traffic_sources, demographics, geography
- **Analytics -- Schedule:** daily, day_of_week, content_type_breakdown
- **Analytics -- Revenue:** revenue, revenue_by_video, retention
- **Publishing:** upload, update, set_thumbnail, delete
- **Playlists:** list, create, add_to, remove_from
- **Comments:** list, post, reply
- **Bulk Reporting:** list_types, create_job, list_jobs, list_reports, download
- **Transcripts:** get_transcript, list_captions

**This is the most feature-complete YouTube MCP server** -- includes SEO suggestions with zero API quota cost, revenue analytics, audience demographics, and bulk CSV report exports. Low star count but very comprehensive.

---

### youtube-researcher-mcp
- **GitHub:** https://github.com/larrygmaguire-tech/youtube-researcher-mcp
- **Stars:** 0 | **Language:** JavaScript
- **Last Updated:** Mar 2026
- **API Key:** YouTube Data API v3 required

**Purpose:** Specifically designed for YouTube niche research -- wraps YouTube Data API v3 for video search, metadata, engagement metrics, thumbnails, and aggregate analysis.

---

## 7. YouTube Search Suggestion / Autocomplete Tools

### youtube-suggest (Node.js)
- **GitHub:** https://github.com/goto-bus-stop/youtube-suggest
- **Stars:** 12 | **Language:** JavaScript
- **Last Updated:** Oct 2024
- **API Key:** Not required
- **Install:** `npm install youtube-suggest`

**What it does:**
- Get YouTube search autocomplete suggestions for any query
- Locale/language customization for region-specific results
- Works in Node.js and browser
- Promise-based async API

**Content research use cases:**
- Discover what people are searching for on YouTube
- Find long-tail keyword variations
- Regional keyword research
- Build keyword suggestion tools

---

### SocialBlade/socialblade-js
- **GitHub:** https://github.com/SocialBlade/socialblade-js
- **Stars:** 50 | **Language:** TypeScript
- **Last Updated:** Mar 2026
- **API Key:** SocialBlade commercial API key required

**What it does:**
- Official SocialBlade API client
- Channel growth statistics, rankings
- Historical subscriber/view data

**Content research use cases:**
- Track channel growth trends
- Compare channels in a niche
- Identify fastest-growing channels

**Note:** Requires paid SocialBlade API access.

---

## 8. Data Science / Research Resources

### Kaggle YouTube Trending Datasets
While not GitHub repos, these are essential for YouTube content research:
- **YouTube Trending Video Dataset** -- daily trending videos across multiple countries with title, tags, views, likes, comments, descriptions
- Search Kaggle for "youtube trending" to find regularly updated datasets
- Commonly used for: trend analysis, topic modeling, engagement prediction

### Key Academic Tools
| Tool | Focus | Paper |
|------|-------|-------|
| youtube-engagement | Engagement prediction | ICWSM 2018 |
| SMAPPNYU/youtube-data-api | Academic data collection | NYU Social Media Lab |
| youtube-transcript-scraper | Transcript research | Bernhard Rieder (UvA) |

---

## 9. Recommended Tool Combinations for Content Research

### Stack A: Zero-Cost Research (No API Key)
Best for getting started without any API setup.

```
yt-dlp (metadata extraction)
  + scrapetube (channel/playlist enumeration)
  + youtube-transcript-api (content analysis)
  + YoutubeTags (SEO tag extraction)
```

**Workflow:**
1. Use scrapetube to list all videos from competitor channels
2. Use yt-dlp `--dump-json` to extract full metadata for each video
3. Use youtube-transcript-api to get transcripts of top-performing videos
4. Use YoutubeTags to extract SEO tags
5. Analyze patterns in Python/Jupyter notebooks

### Stack B: API-Powered Research
Best for structured, quota-managed research with official data.

```
python-youtube (API wrapper)
  + youtube-transcript-api (transcripts)
  + analytix (your own channel analytics)
```

**Workflow:**
1. Use python-youtube to search niches and get detailed video/channel stats
2. Extract transcripts for content analysis
3. Use analytix for your own channel performance tracking

### Stack C: AI-Assisted Research
Best for leveraging AI to analyze and synthesize findings.

```
youtube-mcp-server (Claude integration)
  OR youtube-connector-mcp
  + yt-dlp (bulk data backup)
```

**Workflow:**
1. Set up MCP server with Claude Desktop or Cursor
2. Ask Claude to search, analyze, and compare YouTube content
3. Use yt-dlp for bulk data collection that exceeds API quotas

### Stack D: Full Research Platform
Most comprehensive approach combining multiple tools.

```
yt-dlp (bulk metadata, no limits)
  + scrapetube (channel enumeration)
  + python-youtube (structured API queries)
  + youtube-transcript-api (content analysis)
  + YoutubeTags (SEO analysis)
  + youtube-suggest (keyword discovery)
  + pandas/jupyter (analysis)
  + youtube-mcp-server (AI-assisted synthesis)
```

---

## 10. Feature Matrix: What Each Tool Can Do

| Capability | yt-dlp | scrapetube | python-youtube | transcript-api | YoutubeTags | youtube-mcp-server |
|-----------|--------|------------|---------------|---------------|-------------|-------------------|
| Video metadata | Yes | Basic | Yes | No | Partial | Yes |
| View/like counts | Yes | No | Yes | No | No | Yes |
| Channel stats | Yes | No | Yes | No | No | Yes |
| Video search | No | Yes | Yes | No | No | Yes |
| Transcripts | No | No | No | Yes | No | Yes |
| Tags/keywords | Yes | No | Yes | No | Yes | Partial |
| Comments | No | No | Yes | No | No | Yes |
| Thumbnails | URLs | No | Yes | No | No | Yes |
| Playlist data | Yes | Yes | Yes | No | No | Yes |
| Search suggestions | No | No | No | No | No | Partial* |
| Bulk processing | Yes | Yes | Limited | Yes | Yes | Limited |
| Needs API key | No | No | Yes | No | No | Yes |
| Rate limited | Soft | Soft | 10K/day | Soft | Soft | 10K/day |

*pauling-ai MCP server has search suggestions

---

## 11. Key Takeaways

1. **yt-dlp is the Swiss Army knife** -- 151K stars, no API key, extracts nearly all video metadata. Use `--dump-json --no-download` for pure research.

2. **youtube-transcript-api is essential for content analysis** -- 7K stars, no API key, lets you analyze what successful videos actually talk about, which is the deepest form of niche research.

3. **scrapetube fills the enumeration gap** -- easily list all videos from any channel or playlist without API quotas, then feed IDs to yt-dlp or transcript-api.

4. **python-youtube is the best API wrapper** if you want official, structured API access with good Python ergonomics and active maintenance.

5. **MCP servers are the emerging frontier** -- they let AI assistants like Claude do the research for you. The pauling-ai server is the most comprehensive with 40 tools including SEO suggestions at zero quota cost.

6. **The no-API stack (yt-dlp + scrapetube + transcript-api + YoutubeTags) is sufficient for most content research needs** without any API key setup or quota management.

7. **For competitor analysis specifically**, the leonardogrig/youtube-niche-research-tool provides outlier detection (finding videos that dramatically outperform a channel's average), which is the most actionable insight for content strategy.

8. **No single open-source tool matches paid tools like vidIQ or TubeBuddy** in polish and features, but combining 3-4 of these tools provides equivalent or superior data access with more flexibility.
