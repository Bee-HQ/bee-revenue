# Social Media Content Research & Analytics Tools (Non-YouTube)

> **Last Updated:** 2026-03-14
> Comprehensive catalog of open source tools, libraries, and APIs for content research, niche analysis, competitor tracking, and trend detection across all major social platforms except YouTube.

---

## Table of Contents

1. [TikTok](#1-tiktok)
2. [Instagram](#2-instagram)
3. [Twitter/X](#3-twitterx)
4. [Reddit](#4-reddit)
5. [Facebook](#5-facebook)
6. [Pinterest](#6-pinterest)
7. [LinkedIn](#7-linkedin)
8. [Twitch](#8-twitch)
9. [Multi-Platform Tools](#9-multi-platform-tools)
10. [Trend Detection (Platform-Agnostic)](#10-trend-detection-platform-agnostic)
11. [Legal & TOS Considerations Summary](#11-legal--tos-considerations-summary)
12. [Recommendations for Content Research Workflows](#12-recommendations-for-content-research-workflows)

---

## 1. TikTok

### Official API: TikTok Research API

TikTok provides an **official Research API** restricted to academic and nonprofit researchers. Key details:

- **Eligibility:** Independent and academic researchers at non-profit institutions only. Must apply and be approved.
- **Data Access:** Public videos (configured to "Everyone"), comments (text, likes, replies), account metadata (bios, followers, following, liked/reposted/pinned videos)
- **Research Areas:** Misinformation, disinformation, violent extremism, social trends, community building
- **Limitations:** Not available for commercial use. No real-time streaming. Academic-only access significantly limits utility for content creators.

### Open Source TikTok Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [TikTok-Api](https://github.com/davidteather/TikTok-Api) | 6.2k | Python | Feb 2026 | Needs `ms_token` cookie | Yes | General TikTok data extraction |
| [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) | 16.6k | Python | Oct 2025 | No | Yes | High-perf async scraping, Douyin+TikTok |
| [tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) | 5k | TypeScript | May 2023 | No | No | Video downloads, user/trend/hashtag feeds |
| [TikTok-Live-Connector](https://github.com/zerodytrash/TikTok-Live-Connector) | 1.9k | TypeScript | Mar 2026 | No | Yes | Live stream event tracking |
| [TikTokLive](https://github.com/isaackogan/TikTokLive) | 1.4k | Python | Mar 2026 | No | Yes | Python live stream events |
| [tiktok-hashtag-analysis](https://github.com/bellingcat/tiktok-hashtag-analysis) | 357 | Python | Jun 2024 | Yes (TikTok config) | Moderate | Hashtag research, co-occurrence analysis |
| [TikTokPy](https://github.com/Russell-Newton/TikTokPy) | 234 | Python | Nov 2023 | No | No | Simple data extraction, no auth needed |
| [TikTokCommentScraper](https://github.com/cubernetes/TikTokCommentScraper) | 191 | Python | Aug 2023 | No | No | Comment scraping |
| [tiktok-hashtag-tracker](https://github.com/marginalhours/tiktok-hashtag-tracker) | 16 | TypeScript | Mar 2026 | No | Yes | GitHub Actions-based hashtag tracking |

### TikTok Research API Wrappers

| Tool | Stars | Language | Last Active | Notes |
|------|-------|----------|-------------|-------|
| [ResearchTikPy](https://github.com/HohnerJulian/ResearchTikPy) | 40 | Python | Jan 2025 | Videos, users, comments, followers, TikTok Shops |
| [tiktok-research-api-wrapper](https://github.com/tiktok/tiktok-research-api-wrapper) (Official) | 31 | R + Python | Nov 2024 | Official TikTok wrapper, 8 endpoints |
| [tiktok-research-client](https://github.com/AndersGiovanni/tiktok-research-client) | 13 | Python | May 2025 | Simple Python client |
| [tiktok-library](https://github.com/CybersecurityForDemocracy/tiktok-library) | 10 | Python | Jul 2025 | Large-scale data acquisition |

### Key TikTok Tools Deep Dive

**TikTok-Api (davidteather)** -- The most popular unofficial Python wrapper.
- **Features:** Trending videos, user data, async/await, Docker support
- **Requires:** Python 3.9+, Playwright browser automation, `ms_token` cookie from TikTok.com
- **Limitations:** Cannot post content. No authenticated routes. Fragile to TikTok changes.
- **Content Research Use:** Discover trending videos in niches, analyze user engagement patterns, track hashtag growth

**Douyin_TikTok_Download_API** -- Highest-starred TikTok tool overall.
- **Features:** High-performance async scraping, supports both TikTok and Chinese Douyin, full API support
- **Content Research Use:** Bulk download competitor content for analysis, extract metadata at scale

**Bellingcat tiktok-hashtag-analysis** -- Purpose-built for content research.
- **Features:** Hashtag-based video download, co-occurring hashtag frequency analysis, visualization/plots, batch processing
- **Content Research Use:** Niche research via hashtag networks, trend identification, relationship mapping between related content categories

---

## 2. Instagram

### Official APIs

**Instagram Graph API (via Meta)**
- Full access to business/creator account data
- Metrics: impressions, reach, engagement, follower demographics
- Content publishing capabilities
- Requires Facebook Business account + app approval
- Rate limits: 200 calls/user/hour

**Instagram Basic Display API** -- **Deprecated as of December 2024.** No longer available for new apps.

### Open Source Instagram Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [instagrapi](https://github.com/subzeroid/instagrapi) | 6.0k | Python | Mar 2026 | Needs IG credentials | Yes | Full Instagram private API access |
| [instagram-private-api](https://github.com/dilame/instagram-private-api) | 6.4k | TypeScript | Mar 2023 | Needs IG credentials | Transitioning to paid | Node.js private API SDK |
| [instaloader](https://github.com/instaloader/instaloader) | 11.9k | Python | Nov 2025 | Optional login | Yes | Profile/hashtag/story downloads |
| [instagram_private_api](https://github.com/ping/instagram_private_api) | 3.2k | Python | Mar 2026 | Needs IG credentials | Moderate | Python private API |
| [instagrapi-rest](https://github.com/subzeroid/instagrapi-rest) | 595 | Python | Mar 2026 | Needs IG credentials | Yes | RESTful API wrapper for instagrapi |
| [aiograpi](https://github.com/subzeroid/aiograpi) | 341 | Python | Mar 2026 | Needs IG credentials | Yes | Async version of instagrapi |
| [instagram4j](https://github.com/instagram4j/instagram4j) | 939 | Java | Feb 2026 | Needs IG credentials | Moderate | Java private API |
| [Swiftagram](https://github.com/sbertix/Swiftagram) | 253 | Swift | Mar 2026 | Needs IG credentials | Yes | Swift/iOS private API |

### Key Instagram Tools Deep Dive

**instagrapi** -- The most powerful and actively maintained Python Instagram library.
- **Features:** Web + Mobile API requests, 2FA support, challenge resolver, media uploads (photos/videos/reels/albums/stories), user/comment/insight/hashtag operations, story builder, direct messaging
- **Auth:** Username/password or session ID required
- **Content Research Use:** Competitor Reels analysis, hashtag research, engagement metrics extraction, follower analysis
- **Warning:** Developers recommend HikerAPI SaaS for production. Library best for testing/research.
- **Last API verification:** May 2025

**instaloader** -- The go-to tool for data downloading (11.9k stars).
- **Features:** Download public/private profiles, hashtags, stories, feeds, saved media. Downloads comments, geotags, captions. Auto-detects profile name changes. Resume interrupted downloads.
- **Auth:** Optional login for private profiles
- **Content Research Use:** Bulk download competitor posts with metadata, hashtag trend analysis, archive content for review
- **Actively maintained:** v4.15 (Nov 2025), 963 commits, 59 contributors

**instagram-private-api (dilame)** -- Mature Node.js/TypeScript SDK (6.4k stars).
- **Features:** Low-level repositories for single API requests, feeds with async pagination, login flow simulation
- **Warning:** v3.x is shifting to a paid model. v2.x remains open source under MIT.
- **Content Research Use:** Build custom analytics dashboards, programmatic competitor monitoring

### Instagram Content Research Capabilities

| Capability | instagrapi | instaloader | instagram-private-api |
|-----------|-----------|-------------|----------------------|
| Reels metrics | Yes | Metadata only | Yes |
| Hashtag research | Yes | Yes | Yes |
| Competitor analysis | Yes | Yes | Yes |
| Story tracking | Yes | Yes | Yes |
| Follower demographics | Limited | No | Limited |
| Engagement rates | Yes | Partial | Yes |
| Bulk downloads | Yes | Yes | Yes |
| No login needed | No | For public data | No |

---

## 3. Twitter/X

### Official API: X API (formerly Twitter API)

**Current State (as of 2026):**
- **Pricing Model:** Pay-per-usage (credits-based), no monthly subscriptions
- **Enterprise Tier:** Dedicated support, complete streams, custom integrations
- **Major Change (2023):** Twitter shut down free API access in February 2023 under Elon Musk. Previously free Academic Research tier was eliminated. All meaningful access now requires payment.
- **Bonus:** Purchasing X API credits earns up to 20% back in xAI API credits
- **Impact:** Most open source tools that relied on free API access broke. Many shifted to scraping/GraphQL approaches.

### Open Source Twitter/X Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [tweepy](https://github.com/tweepy/tweepy) | 11.1k | Python | Jun 2025 | Yes (X API keys) | Yes | Official API v2 wrapper |
| [snscrape](https://github.com/JustAnotherArchivist/snscrape) | 5.3k | Python | Jun 2023 | No | No (dormant) | Multi-platform scraping |
| [twikit](https://github.com/d60/twikit) | 4.1k | Python | Feb 2025 | No (scraping) | Yes | Scraping without API keys |
| [twit](https://github.com/ttezel/twit) | 4.3k | JavaScript | Feb 2026 | Yes (X API keys) | Moderate | Node.js REST & Streaming |
| [twitter-api-client](https://github.com/trevorhobenshield/twitter-api-client) | 1.9k | Python | Mar 2026 | Optional (cookie auth) | Yes | GraphQL + scraping, Spaces |
| [node-twitter-api-v2](https://github.com/plhery/node-twitter-api-v2) | 1.6k | TypeScript | Mar 2026 | Yes (X API keys) | Yes | TypeScript v1+v2 client |
| [nitter](https://github.com/zedeus/nitter) | 12.6k | Nim | Mar 2026 | No | Community forks | Alternative Twitter frontend |
| [XActions](https://github.com/nirholas/XActions) | 116 | HTML | Mar 2026 | Various | Yes | Complete X automation toolkit |

### Key Twitter/X Tools Deep Dive

**tweepy** -- The gold standard Python Twitter wrapper (11.1k stars).
- **Features:** Full Twitter API v2 support, async support, streaming
- **Auth:** Requires X API credentials (now paid)
- **Content Research Use:** Trending topics, engagement analysis, follower analysis, search tweets
- **64.6k dependent projects** -- massive ecosystem

**twikit** -- The best free alternative (4.1k stars).
- **Features:** Tweet search, trending topics, posting, DMs, media upload -- all without official API keys
- **Auth:** Web scraping approach, no API keys needed
- **Content Research Use:** Track trending topics, analyze engagement without paying for API access
- **Companion project:** twikit_grok for Grok AI integration

**twitter-api-client (trevorhobenshield)** -- Most comprehensive scraping tool (1.9k stars).
- **Features:** v1, v2, and GraphQL API implementation. Account automation, data scraping, Twitter Spaces audio/transcript capture
- **Auth:** Email/password, cookies, or guest sessions (limited)
- **Content Research Use:** Deep competitor analysis, trending content discovery, Spaces content analysis
- **Warning:** Cookie-based auth recommended; password login is unstable. Relies on reverse-engineering.

**snscrape** -- Multi-platform but dormant.
- **Supports:** Twitter, Facebook, Instagram, Reddit, Telegram, Mastodon, VK, Weibo
- **Status:** Last commit June 2023. Many scrapers may be broken due to platform changes.
- **Was excellent for:** No-auth multi-platform scraping. Served as the go-to tool before API lockdowns.

---

## 4. Reddit

### Official API

**Reddit API (2023-2024 Changes):**
- **June 2023:** Reddit made API access paid, killing most third-party apps (including Apollo). Caused massive community protests.
- **Current state:** Free tier allows 100 queries/minute for non-commercial use. OAuth required.
- **Commercial use:** Requires paid agreement with Reddit
- **Pushshift (historical data):** Was the primary source for Reddit historical data. Access restricted in 2023 to moderators only. No longer publicly available for research.

### Open Source Reddit Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [PRAW](https://github.com/praw-dev/praw) | 4.0k | Python | Oct 2024 | Yes (Reddit OAuth) | Yes | Official Python wrapper |
| [asyncpraw](https://github.com/praw-dev/asyncpraw) | 144 | Python | Mar 2026 | Yes (Reddit OAuth) | Yes | Async version of PRAW |
| [Reddit-Insight](https://github.com/PatrickJS/Reddit-Insight) | 142 | JavaScript | Mar 2026 | Yes | Moderate | Angular.js analytics dashboard |

### Key Reddit Tools Deep Dive

**PRAW (Python Reddit API Wrapper)** -- The definitive Reddit library (4.0k stars).
- **Features:** OAuth2 authentication, automatic rate-limit compliance, subreddit interactions, submissions, comments, moderator tools
- **Auth:** Reddit OAuth credentials (client_id, client_secret, username, password)
- **Content Research Use:**
  - Subreddit trend analysis (what content gets upvoted)
  - Competitor/niche research (find what topics resonate)
  - Best posting time analysis
  - Comment sentiment analysis
  - Cross-subreddit content overlap detection
- **License:** Simplified BSD
- **26.6k dependent projects** -- extremely mature ecosystem

**Content Research Workflow with PRAW:**
```
1. Identify target subreddits for your niche
2. Fetch top posts by timeframe (day/week/month/year/all)
3. Analyze post titles, flair, engagement metrics
4. Track comment patterns and sentiment
5. Identify content gaps and opportunities
```

### Impact of Reddit API Changes

- **Pushshift shutdown** means historical data analysis is much harder
- **Free tier (100 queries/min)** is sufficient for individual content research
- **PRAW still works** with free-tier Reddit apps
- **Arctic Shift** (community project) preserves some historical Reddit data but access varies

---

## 5. Facebook

### Official API: Meta Graph API

- **Capabilities:** Page data, post insights, ad analytics, comment management
- **Access:** Requires Facebook Business account, app creation, and review process
- **Rate Limits:** 200 calls/user/hour for most endpoints
- **Analytics Data:** Page impressions, post reach, engagement, demographics
- **Limitations:** Personal profile data heavily restricted post-Cambridge Analytica. Group data access very limited.

**CrowdTangle** -- Meta's social analytics tool for researchers. Was discontinued in August 2024. No replacement for public research access.

### Open Source Facebook Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [facebook-scraper](https://github.com/kevinzg/facebook-scraper) | 3.1k | Python | Feb 2023 | No (optional login) | No (dormant) | Public page/group scraping |
| [CooRnet](https://github.com/fabiogiglietto/CooRnet) | 75 | R | Mar 2025 | CrowdTangle (dead) | Limited | Coordinated link sharing detection |

### Key Facebook Tools Deep Dive

**facebook-scraper** -- The most popular Facebook data tool (3.1k stars).
- **Features:** Extract posts from public pages/groups, comments/replies, reactions, profile info, CSV/JSON export, resume capability
- **Auth:** Optional login via credentials or cookies
- **Content Research Use:** Analyze competitor Facebook pages, track engagement patterns, content type analysis
- **Warnings:**
  - Facebook may temporarily ban IPs for excessive scraping
  - 448 open issues suggest many broken features due to Facebook's frequent UI changes
  - Last commit Feb 2023 -- likely many endpoints are broken
- **Status:** Effectively abandoned. Facebook is extremely aggressive about blocking scrapers.

### Facebook Content Research Reality

Facebook is the **hardest platform to research** with open source tools:
- Graph API requires business verification and extensive permissions
- CrowdTangle was shut down (Aug 2024)
- facebook-scraper is largely broken
- Facebook aggressively blocks automated access
- **Best current approach:** Use Meta Business Suite built-in analytics for your own pages, or manual research

---

## 6. Pinterest

### Official API: Pinterest API v5

Pinterest's official API is surprisingly robust for analytics:
- **Pin Management:** Create, retrieve, update, delete pins
- **Analytics Metrics:** Impressions, clicks, saves, repins, engagement rates
- **Video Metrics:** 3-second views, 10-second views, average watch time
- **Conversion Tracking:** Checkout events, app installs, custom conversions
- **Demographics:** Age, gender, location breakdowns
- **Granularity:** Daily, weekly, monthly, hourly
- **Access:** Requires Pinterest Business account and approved app
- **Rate Limits:** Standard API rate limits; some beta endpoints limited to 5 queries/min/advertiser

### Open Source Pinterest Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [pinterest-dl-gui](https://github.com/sean1832/pinterest-dl-gui) | 34 | Python | Feb 2026 | No | Yes | Image downloading with GUI |
| [PinterestScraper](https://github.com/civiliangame/PinterestScraper) | 27 | Python | Dec 2025 | No | Moderate | Image scraping |
| [pinterest_scraper](https://github.com/creeponsky/pinterest_scraper) | 17 | Python | Mar 2026 | No | Yes | General scraping |
| [Pinterest-Scraper (Bes-js)](https://github.com/Bes-js/Pinterest-Scraper) | 16 | TypeScript | Dec 2025 | No | Moderate | Selenium-based data extraction |

### Pinterest Content Research Reality

- **Open source ecosystem is weak.** No major analytics-focused tools exist.
- **Official API is the best path** for Pinterest content research -- it provides comprehensive analytics.
- **Scraping tools** are all focused on image downloading, not analytics or content research.
- **Recommendation:** Apply for Pinterest API access (business account required) and build custom analytics.

---

## 7. LinkedIn

### Official API: LinkedIn API

- **Official Python Client:** [linkedin-api-python-client](https://github.com/linkedin-developers/linkedin-api-python-client) (245 stars) -- beta, by LinkedIn developers
- **Scopes:** Profile (openid, profile), advertising (r_ads), organization data, campaign management
- **Supports:** 2-legged and 3-legged OAuth2
- **Major Limitation:** LinkedIn is extremely restrictive with API access. Marketing/advertising APIs require approved partnerships. Basic member data access requires verified app with LinkedIn review.
- **No public analytics API** for non-partner developers

### Open Source LinkedIn Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [linkedin_scraper](https://github.com/joeyism/linkedin_scraper) | 3.8k | Python | Mar 2026 | No (scraping) | Yes | Profile data extraction |
| [ScrapedIn](https://github.com/dchrastil/ScrapedIn) | 1.2k | Python | Mar 2026 | No (scraping) | Moderate | Reconnaissance scraping |
| [python-linkedin](https://github.com/ozgur/python-linkedin) | 912 | Python | Feb 2021 | Yes (OAuth) | No (dormant) | Official API wrapper (old) |
| [linkedin (Ruby)](https://github.com/hexgnu/linkedin) | 763 | Ruby | Feb 2026 | Yes (OAuth) | Low | Ruby API wrapper |
| [scrapedin](https://github.com/linkedtales/scrapedin) | 613 | JavaScript | Mar 2026 | No (scraping) | Low | JS profile scraping |

### LinkedIn Content Research Reality

- **LinkedIn is the most restrictive platform** for programmatic access
- **Scraping is aggressively blocked** -- LinkedIn sends cease-and-desist letters and has won court cases (hiQ Labs v. LinkedIn was reversed on remand)
- **No public analytics API** exists for content research
- **Best approach:** Use LinkedIn's built-in Creator Analytics (available for Creator Mode profiles) or Sales Navigator for competitive research
- **linkedin_scraper** (3.8k stars) works for basic profile data but is fragile and against LinkedIn TOS

---

## 8. Twitch

### Official API: Twitch Helix API

Twitch has one of the **most developer-friendly APIs:**
- **Free access** with registered application
- **Endpoints:** Streams, users, videos, clips, games, analytics, subscriptions, chat
- **Analytics:** Stream viewer counts, game popularity, clip engagement
- **EventSub:** Real-time event notifications (new followers, subscriptions, etc.)
- **Rate Limits:** 800 points/minute for most endpoints

### Open Source Twitch Tools

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [TwitchIO](https://github.com/PythonistaGuild/TwitchIO) | 877 | Python | Jan 2026 | Yes (Twitch OAuth) | Yes | Full async Python Twitch library |

### Key Twitch Tools Deep Dive

**TwitchIO** -- The premier Python Twitch library (877 stars).
- **Features:** Modern async Python, full type annotations, EventSub (Webhook/WebSocket/Conduit), chat bot extensions, OAuth management, routine tasks, overlay support
- **Auth:** Twitch API credentials + OAuth tokens
- **Content Research Use:**
  - Track popular games/categories over time
  - Monitor stream viewer patterns
  - Analyze chat engagement and sentiment
  - Discover trending clips and content formats
  - Competitor channel analysis
- **v3.2.1** (Jan 2026) -- actively maintained, 2k+ commits

### Twitch Content Research Notes

- Twitch is **well-suited for open source analytics** due to its permissive API
- **Twitch Tracker** (twitchtracker.com) provides free public statistics but has no open source equivalent
- **SullyGnome** (sullygnome.com) is another popular analytics site with no open source clone
- Building custom Twitch analytics is feasible with TwitchIO + the Helix API

---

## 9. Multi-Platform Tools

### Scheduling & Management (with Analytics)

| Tool | Stars | Language | Last Active | Platforms | Analytics? | Best For |
|------|-------|----------|-------------|-----------|------------|----------|
| [Postiz](https://github.com/gitroomhq/postiz-app) | 27.3k | TypeScript | Mar 2026 | Instagram, TikTok, X, LinkedIn, Facebook, Pinterest, Reddit, YouTube, Threads, Bluesky, Mastodon, Discord, Slack, Dribbble | Yes | Full social media scheduling + AI + analytics |
| [Mixpost](https://github.com/inovector/mixpost) | 3.0k | Vue/PHP | Feb 2026 | Multiple platforms | Yes | Self-hosted Buffer alternative |
| [Social Ring](https://github.com/sanjipun/socialring) | 10 | TypeScript | Feb 2026 | Multiple | Limited | Free social media management |

### Multi-Platform Scrapers

| Tool | Stars | Language | Last Active | Platforms | API Keys? | Best For |
|------|-------|----------|-------------|-----------|-----------|----------|
| [snscrape](https://github.com/JustAnotherArchivist/snscrape) | 5.3k | Python | Jun 2023 | Twitter, Facebook, Instagram, Reddit, Telegram, Mastodon, VK, Weibo | No | Multi-platform scraping (dormant) |
| [skraper](https://github.com/sokomishalov/skraper) | 326 | Kotlin | Jan 2025 | 18+ platforms (FB, IG, Twitter, TikTok, Reddit, Pinterest, Twitch, Telegram, etc.) | No | JVM multi-platform scraping |
| [media-scraper](https://github.com/elvisyjlin/media-scraper) | 427 | Python | Aug 2020 | Instagram, Twitter, Reddit, TikTok | No | Media download across platforms |
| [SocialPwned](https://github.com/MrTuxx/SocialPwned) | 1.3k | Python | Mar 2026 | Instagram, LinkedIn, Twitter | No | OSINT/reconnaissance |

### Key Multi-Platform Tools Deep Dive

**Postiz** -- The most impressive open source social media tool (27.3k stars).
- **Features:** AI-powered scheduling, analytics dashboard, team collaboration, API access (N8N/Make.com/Zapier compatible), multi-tenant SaaS support
- **14 platforms supported** including all major social networks
- **Tech Stack:** NextJS + NestJS + Prisma + PostgreSQL + Temporal
- **License:** AGPL-3.0
- **Content Research Use:** Track post performance across platforms, A/B test content, measure engagement trends
- **Agent CLI:** Postiz Agent (64 stars) allows Claude/AI integration for automated scheduling

**skraper** -- Unique JVM-based multi-platform scraper (326 stars).
- **Features:** Scrapes posts/media from 18+ platforms without authentication, CLI + library interfaces, Telegram bot wrapper, multiple output formats
- **Platforms:** Facebook, Instagram, Twitter, YouTube, TikTok, Telegram, Twitch, Reddit, 9GAG, Pinterest, Flickr, Tumblr, Vimeo, IFunny, Coub, VK, Odnoklassniki, Pikabu
- **Warning:** "Each web-site is subject to change without any notice, so the tool may work incorrectly"
- **Content Research Use:** Quick cross-platform content sampling and comparison

**Mixpost** -- Self-hosted Buffer/Hootsuite alternative (3.0k stars).
- **Features:** Calendar scheduling, media library with stock images, post templates, dynamic variables, hashtag organization, per-platform analytics
- **Tech Stack:** Laravel (PHP) + Vue.js
- **Content Research Use:** Track your own cross-platform performance, compare content types

### Social Media API Aggregators

| Tool | Stars | Language | Last Active | Description |
|------|-------|----------|-------------|-------------|
| [ayrshare/social-media-api](https://github.com/ayrshare/social-media-api) | 290 | JavaScript | Dec 2024 | Unified API for posting + analytics across platforms |
| [SocialBlade JS](https://github.com/SocialBlade/socialblade-js) | 50 | TypeScript | Mar 2026 | Official Social Blade API wrapper |

---

## 10. Trend Detection (Platform-Agnostic)

### Google Trends Wrappers

| Tool | Stars | Language | Last Active | API Keys? | Maintained? | Best For |
|------|-------|----------|-------------|-----------|-------------|----------|
| [google-trends-api](https://github.com/pat310/google-trends-api) | 954 | JavaScript | Active | No | Yes (with caveats) | Node.js Google Trends access |
| [pytrends](https://github.com/GeneralMills/pytrends) | 3.6k | Python | Apr 2023 | No | **ARCHIVED** (Apr 2025) | Python Google Trends |
| [unofficial-google-trends-api](https://github.com/suryasev/unofficial-google-trends-api) | 220 | Python | Mar 2026 | No | Moderate | Alternative Python wrapper |
| [g-trends](https://github.com/x-fran/g-trends) | 118 | PHP | Feb 2026 | No | Moderate | PHP Google Trends |
| [gogtrends](https://github.com/groovili/gogtrends) | 88 | Go | Feb 2026 | No | Moderate | Go Google Trends |
| [trends-js](https://github.com/Shaivpidadi/trends-js) | 24 | TypeScript | Mar 2026 | No | Yes | TypeScript Google Trends |

### Key Trend Detection Tools Deep Dive

**pytrends** -- Was the gold standard, now archived (3.6k stars).
- **Features:** Interest over time, regional interest, related topics/queries, trending searches, real-time trends, top charts, search suggestions
- **Status:** **Archived April 2025.** Looking for maintainers. 136 open issues.
- **No API keys needed** -- interfaces directly with Google Trends
- **Content Research Use:** Identify trending topics, compare keyword popularity, seasonal trend analysis, niche validation

**google-trends-api** -- Best active alternative (954 stars, Node.js).
- **Features:** autoComplete, dailyTrends, interestOverTime, interestByRegion, realTimeTrends, relatedQueries, relatedTopics, proxy support
- **Warning:** v3 to v4 had breaking changes due to Google throttling deprecated endpoints
- **Content Research Use:** Same as pytrends but in Node.js ecosystem

### Trend Detection Approach (DIY)

Since no dedicated "Exploding Topics" open source alternative exists, here's how to build trend detection with available tools:

1. **Google Trends** (pytrends/google-trends-api) -- Macro trend identification
2. **Reddit** (PRAW) -- Emerging topic detection via subreddit growth and hot post analysis
3. **Twitter/X** (twikit) -- Real-time trending topics and hashtag velocity
4. **TikTok** (TikTok-Api) -- Trending sounds, effects, and hashtags
5. **Combine with NLP** -- Use sentiment analysis and topic modeling on collected data

---

## 11. Legal & TOS Considerations Summary

| Platform | Official API | Scraping Legality | Risk Level | Notes |
|----------|-------------|-------------------|------------|-------|
| **TikTok** | Research API (academics only) | Gray area | Medium | TikTok has been less aggressive than others about scrapers |
| **Instagram** | Graph API (business accounts) | Against TOS | High | Meta aggressively blocks scrapers. Multiple lawsuits filed. |
| **Twitter/X** | Paid API only | Against TOS | High | X has sued scrapers. Rate limits and IP blocks common. |
| **Reddit** | Free tier available | Against TOS if commercial | Medium | API changes in 2023 killed most third-party access. Free tier usable for research. |
| **Facebook** | Graph API (restricted) | Against TOS | Very High | Most aggressive platform. CrowdTangle shutdown. |
| **Pinterest** | API v5 (business accounts) | Against TOS | Medium | Official API is good enough for most needs |
| **LinkedIn** | Very restricted | Against TOS | Very High | LinkedIn sends C&D letters, has won court cases |
| **Twitch** | Free Helix API | N/A (API sufficient) | Low | Most developer-friendly platform |

### General Legal Guidance

- **Official APIs are always safest.** Use them when available.
- **Scraping public data** is legally complex. The US Computer Fraud and Abuse Act (CFAA) cases are evolving. The hiQ v. LinkedIn case established some protections for scraping public data, but subsequent rulings have been mixed.
- **Rate limiting and respecting robots.txt** reduces legal risk.
- **Never scrape private/authenticated data** without authorization.
- **Commercial use of scraped data** carries significantly higher legal risk than personal research.
- **GDPR/privacy laws** apply to any personal data collected, regardless of how it was obtained.

---

## 12. Recommendations for Content Research Workflows

### Tier 1: Best-Supported Platforms for Open Source Research

| Platform | Recommended Tool | Why |
|----------|-----------------|-----|
| **Reddit** | PRAW | Free API, excellent library, rich content data |
| **Twitch** | TwitchIO | Free API, full-featured library |
| **TikTok** | TikTok-Api + Bellingcat hashtag analysis | Active maintenance, good features |
| **Google Trends** | google-trends-api (JS) or unofficial-google-trends-api (Python) | No auth needed, trend validation |

### Tier 2: Workable but Requires Caution

| Platform | Recommended Tool | Caveats |
|----------|-----------------|---------|
| **Instagram** | instagrapi | Requires credentials, may break, risk of account ban |
| **Twitter/X** | twikit | No API keys but relies on scraping, fragile |
| **Pinterest** | Official Pinterest API v5 | Requires business account approval |

### Tier 3: Difficult / Limited Options

| Platform | Situation |
|----------|-----------|
| **Facebook** | No reliable open source tools. Use Meta Business Suite manually. |
| **LinkedIn** | No safe open source analytics. Use LinkedIn Creator Analytics manually. |

### Cross-Platform Research Stack

For comprehensive social media content research, here is the recommended open source stack:

```
Content Research Pipeline:
1. Trend Discovery
   - Google Trends (google-trends-api)
   - Reddit (PRAW) -- subreddit trending posts
   - Twitter/X (twikit) -- trending topics

2. Niche Validation
   - TikTok (TikTok-Api) -- hashtag analysis
   - Instagram (instagrapi) -- hashtag/Reels research
   - Reddit (PRAW) -- subreddit engagement analysis

3. Competitor Analysis
   - TikTok (TikTok-Api) -- user profile metrics
   - Instagram (instaloader) -- competitor content download
   - Multi-platform (Postiz) -- cross-platform performance

4. Content Scheduling & Analytics
   - Postiz (27.3k stars) -- schedule + track across 14 platforms
   - Mixpost (3.0k stars) -- self-hosted alternative

5. Ongoing Monitoring
   - tiktok-hashtag-tracker -- GitHub Actions automated tracking
   - PRAW -- Reddit monitoring scripts
   - TwitchIO -- live stream trends
```

---

## Quick Reference: All Major Tools by Stars

| Stars | Tool | Platform(s) | Language | Status |
|-------|------|-------------|----------|--------|
| 27.3k | [Postiz](https://github.com/gitroomhq/postiz-app) | 14 platforms | TypeScript | Active |
| 16.6k | [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) | TikTok/Douyin | Python | Active |
| 12.6k | [nitter](https://github.com/zedeus/nitter) | Twitter/X | Nim | Community |
| 11.9k | [instaloader](https://github.com/instaloader/instaloader) | Instagram | Python | Active |
| 11.1k | [tweepy](https://github.com/tweepy/tweepy) | Twitter/X | Python | Active |
| 6.4k | [instagram-private-api](https://github.com/dilame/instagram-private-api) | Instagram | TypeScript | Transitioning |
| 6.2k | [TikTok-Api](https://github.com/davidteather/TikTok-Api) | TikTok | Python | Active |
| 6.0k | [instagrapi](https://github.com/subzeroid/instagrapi) | Instagram | Python | Active |
| 5.3k | [snscrape](https://github.com/JustAnotherArchivist/snscrape) | Multi-platform | Python | Dormant |
| 5.0k | [tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) | TikTok | TypeScript | Dormant |
| 4.3k | [twit](https://github.com/ttezel/twit) | Twitter/X | JavaScript | Moderate |
| 4.1k | [twikit](https://github.com/d60/twikit) | Twitter/X | Python | Active |
| 4.0k | [PRAW](https://github.com/praw-dev/praw) | Reddit | Python | Active |
| 3.8k | [linkedin_scraper](https://github.com/joeyism/linkedin_scraper) | LinkedIn | Python | Active |
| 3.6k | [pytrends](https://github.com/GeneralMills/pytrends) | Google Trends | Python | Archived |
| 3.2k | [instagram_private_api](https://github.com/ping/instagram_private_api) | Instagram | Python | Moderate |
| 3.1k | [facebook-scraper](https://github.com/kevinzg/facebook-scraper) | Facebook | Python | Dormant |
| 3.0k | [Mixpost](https://github.com/inovector/mixpost) | Multi-platform | Vue/PHP | Active |
| 1.9k | [TikTok-Live-Connector](https://github.com/zerodytrash/TikTok-Live-Connector) | TikTok | TypeScript | Active |
| 1.9k | [twitter-api-client](https://github.com/trevorhobenshield/twitter-api-client) | Twitter/X | Python | Active |
| 1.6k | [node-twitter-api-v2](https://github.com/plhery/node-twitter-api-v2) | Twitter/X | TypeScript | Active |
| 1.4k | [TikTokLive](https://github.com/isaackogan/TikTokLive) | TikTok | Python | Active |
| 954 | [google-trends-api](https://github.com/pat310/google-trends-api) | Google Trends | JavaScript | Active |
| 877 | [TwitchIO](https://github.com/PythonistaGuild/TwitchIO) | Twitch | Python | Active |
| 357 | [tiktok-hashtag-analysis](https://github.com/bellingcat/tiktok-hashtag-analysis) | TikTok | Python | Moderate |
| 326 | [skraper](https://github.com/sokomishalov/skraper) | 18+ platforms | Kotlin | Active |
| 245 | [linkedin-api-python-client](https://github.com/linkedin-developers/linkedin-api-python-client) | LinkedIn | Python | Beta |
| 144 | [asyncpraw](https://github.com/praw-dev/asyncpraw) | Reddit | Python | Active |
| 40 | [ResearchTikPy](https://github.com/HohnerJulian/ResearchTikPy) | TikTok | Python | Active |
| 31 | [tiktok-research-api-wrapper](https://github.com/tiktok/tiktok-research-api-wrapper) | TikTok | R/Python | Active |
