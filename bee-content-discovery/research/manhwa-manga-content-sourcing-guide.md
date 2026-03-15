# Manhwa & Manga Content Sourcing Guide

> For building an automated YouTube recap/review content pipeline.
> Research date: March 2026

---

## Table of Contents

1. [Official/Legal Platforms](#1-officiallegal-platforms)
2. [Aggregator & Scan Sites](#2-aggregator--scan-sites)
3. [Raw/Source Material Access](#3-rawsource-material-access)
4. [APIs and Programmatic Access](#4-apis-and-programmatic-access)
5. [Story/Plot Information Sources](#5-storyplot-information-sources)
6. [Image/Visual Asset Sources](#6-imagevisual-asset-sources)
7. [Legal Considerations for YouTube Content](#7-legal-considerations-for-youtube-content)
8. [Automation-Friendly Sources](#8-automation-friendly-sources)
9. [Recommended Pipeline Architecture](#9-recommended-pipeline-architecture)

---

## 1. Official/Legal Platforms

### Korean Webtoon/Manhwa Platforms

#### Naver Webtoon (Korean) — https://comic.naver.com
- **What it is:** The largest manhwa platform globally. Origin of most popular manhwa series
- **Access model:** Coin-based system. Many series have free chapters; latest chapters cost coins
- **Language:** Korean (primary), with English via LINE Webtoon
- **Account barrier:** Korean phone number required for full access. Workarounds exist but are fragile
- **API:** No official public API. Unofficial scrapers exist (see Section 4)
- **For pipeline:** Source of raw Korean chapters before English translation. Hard to access programmatically as a foreigner

#### LINE Webtoon (Global) — https://www.webtoons.com
- **What it is:** Naver's global English-language platform. Largest global webtoon reader
- **Access model:** Most series free to read with ads. "Fast Pass" (coins) for early access to latest chapters. Canvas section is fully free (indie creators)
- **Key series:** Tower of God, Omniscient Reader's Viewpoint, Unordinary, True Beauty, Lore Olympus
- **API:** No official public API. Unofficial RapidAPI endpoint exists at api.tapas.io-style endpoints. Scraping tools available (scrapetoon on GitHub)
- **Terms:** Explicitly prohibits scraping and redistribution of content
- **For pipeline:** Good source of English manhwa panels. High image quality. Anti-bot protections via Cloudflare

#### Kakao Page / Kakao Webtoon — https://page.kakao.com
- **What it is:** Second-largest Korean platform, owned by Kakao Entertainment
- **Access model:** "Wait or Pay" — free after a waiting period, or pay coins for immediate access
- **Language:** Korean primary. Some titles have English versions via Tapas (Kakao's English subsidiary)
- **Account barrier:** Similar Korean phone number requirements
- **Enforcement:** Extremely aggressive anti-piracy. Shut down 11 piracy sites and deleted 160M+ illegal works in H1 2025 alone. First Korean company to get Google TCRP (Trusted Copyright Removal Program) status — handling 30,000 takedown requests/day
- **For pipeline:** High risk to scrape. Very aggressive enforcement

#### Tappytoon — https://www.tappytoon.com
- **What it is:** Premium English manhwa platform focused on romance, BL, GL, fantasy, action
- **Access model:** Monthly subscription ($6.49/mo or $59.99/yr). No free tier beyond previews
- **Content:** Licensed translations from Korean publishers. High-quality official translations
- **API:** None public
- **For pipeline:** Paid access only. Not automation-friendly

#### Lezhin Comics — https://www.lezhin.com
- **What it is:** Premium per-chapter platform. Known for mature/adult content alongside mainstream
- **Access model:** Pay per chapter with coins. No flat subscription. Can get expensive
- **Content:** Mix of Korean, Japanese, and Chinese titles. Strong BL/GL catalog
- **API:** None public
- **For pipeline:** Expensive per-chapter model makes it impractical for bulk access

### Japanese Manga Platforms

#### Manga Plus by Shueisha — https://mangaplus.shueisha.co.jp
- **What it is:** Shueisha's official free manga platform. Simulpub of Weekly Shonen Jump and Jump+ titles
- **Access model:** Free. First 3 + latest 3 chapters available for older series. New chapters free on release day for a limited window. As of late 2025, Weekly Young Jump titles also included
- **Key series:** One Piece, My Hero Academia, Jujutsu Kaisen, Chainsaw Man, Spy x Family
- **API:** No official public API, but unofficial Python client exists (see Section 4). Protobuf-based internal API
- **For pipeline:** Best free source for Shonen Jump manga. Unofficial API wrappers available. Good image quality

#### Viz Media / Viz Manga — https://www.viz.com
- **What it is:** Major English-language manga publisher (Shueisha subsidiary)
- **Access model:** Freemium. Selected chapters free. Digital vault access via Shonen Jump subscription ($2.99/mo) — all-you-can-read for 15,000+ chapters
- **Content:** Official English translations of Shueisha titles
- **API:** None public
- **Enforcement:** Very aggressive — Viz alone accounts for ~5% of all Google URL takedown requests. 205M+ URL takedown requests filed
- **For pipeline:** High-quality official translations but very aggressive on copyright

#### Crunchyroll Manga — https://www.crunchyroll.com
- **What it is:** Launched October 2025. Subscription manga service bundled with Crunchyroll
- **Access model:** Included with Ultimate Fan tier. Standalone subscription available. Offline reading supported
- **Publishers:** VIZ Media, Yen Press, Square Enix, AlphaPolis, COMPASS, MobileBook.JP, J-Novel Club
- **For pipeline:** New platform, growing catalog. Subscription-gated

#### ComicWalker by Kadokawa — https://comic-walker.com
- **What it is:** Kadokawa's free manga reader. ~300 series with rotating free chapters
- **Access model:** Free with ads. Both Japanese and English tabs
- **For pipeline:** Free access. Moderate catalog. Less anti-bot protection than major platforms

### Other Notable Platforms

| Platform | Type | Model | Notes |
|----------|------|-------|-------|
| **Tapas** (tapas.io) | Manhwa/Webcomics | Free chapters + Ink currency (buy or earn via ads) | Kakao Entertainment subsidiary. Large indie catalog |
| **Manta** (manta.net) | Manhwa | Subscription ($4.99/mo) | Korean manhwa focus. High-quality translations |
| **Pocket Comics** | Manhwa | Free with ads | Smaller catalog |
| **Bilibili Comics** | Manhua/Manga | Free with ads + coins | Chinese platform with manga/manhwa licenses |
| **ComiXology/Kindle** | Manga/Manhwa | Per-volume purchase | Amazon-owned. Largest licensed digital catalog |
| **Azuki** (azuki.co) | Manga | Subscription ($4.99/mo) | Simulpub from Kodansha and others |

---

## 2. Aggregator & Scan Sites

### Major Aggregators

#### MangaDex — https://mangadex.org
- **What it is:** Largest not-for-profit manga/manhwa/manhua aggregation site. Hosts scanlation group uploads
- **Content:** Massive catalog. Multiple translation groups per series. Language options. Quality varies by group
- **Recent events:** ~7,000 series removed in May 2025 after coordinated DMCA from Japanese/Korean publishers (Kodansha, Square Enix, Naver). Catalog still very large but reduced
- **API:** Full REST API at api.mangadex.org. Well-documented. Python/JS/Rust wrappers available (see Section 4). Best API of any aggregator
- **Image quality:** Varies by scanlation group. Generally good (1200-2000px wide). Some groups do 4K
- **Legal status:** Gray area. Links to official sources where available. Removed titles on DMCA requests
- **For pipeline:** Best automation-friendly aggregator. Official API. Multiple language support. But shrinking catalog due to DMCA pressure

#### Bato.to — https://bato.to
- **What it is:** Clean aggregator known for high-quality scans
- **Content:** Smaller than MangaDex but curated. Fast uploads of latest chapters
- **API:** None public. Would need scraping
- **Legal status:** Gray area
- **For pipeline:** Good image quality. No API — scraping required

#### MangaSee — https://mangasee123.com
- **What it is:** Aggregator that focuses on official volume release quality
- **Content:** Updated with official volume scans. Consistent quality
- **API:** None public
- **For pipeline:** Good for volume-quality images. Scraping required

#### Other Aggregators

| Site | Notes |
|------|-------|
| **Mangakakalot / Manganato** | Massive catalog. Frequent updates. Lower image quality. Heavy ads |
| **MangaFire** | Clean UI. Good quality. Newer site |
| **AsuraScans** (asuracomic.net) | Manhwa-focused. Very fast translations of popular Korean series (Solo Leveling, etc.) |
| **ReaperScans** | Was a major hub — **shut down May 2025** by Kakao Entertainment enforcement. 10M monthly visits, $500M estimated damages |
| **FlameScans** | Manhwa-focused aggregator. Active community |
| **Luminous Scans** | Manhwa translations. Active |
| **MangaBuddy** | General aggregator |

### Fan Translation / Scanlation Groups

**How scanlation works:**
1. Raw acquisition — members buy/obtain Korean/Japanese chapters
2. Cleaning — editors erase original text, fix imperfections
3. Translation — bilingual volunteers translate, preserving cultural nuance
4. Typesetting — translated text placed back on pages with appropriate fonts
5. Proofreading — final review of all dialogue and sound effects
6. **Timeline:** Typically 5-8 hours per chapter, with popular series done in 24-48 hours from raw release

**Notable groups and communities:**
- Groups typically coordinate via Discord servers
- Many groups follow an informal code: cease work when a title gets officially licensed
- Quality varies wildly — top groups produce translation quality rivaling official releases
- Groups increasingly under legal pressure — multiple shutdowns in 2025

**Quality and timeliness:**
- Hot titles (Solo Leveling, Omniscient Reader, etc.): English within 24-48 hours of Korean release
- Mid-tier titles: 3-7 days
- Niche titles: Weeks to months, or may never get translated
- Official translations often lag by days to months behind Korean release

### Legal Risks of Using Aggregators

- **Increasing enforcement:** Japanese publishers (CODA/IAPO coalition) and Korean publishers (Kakao, Naver/Webtoon) are both escalating anti-piracy efforts
- **DMCA takedown volume:** Shueisha alone has filed 205M+ URL takedown requests with Google. Kakao handles 30,000/day
- **Criminal prosecution:** Korean courts upholding prison sentences for piracy site operators (OKTOON case, January 2026)
- **Cloudflare lawsuit:** Big 4 Japanese publishers won copyright suit against Cloudflare for supporting piracy sites (November 2025)
- **Trend:** Enforcement is getting stronger, not weaker. Sites shut down regularly. Using pirated content for commercial YouTube channels adds additional legal exposure

---

## 3. Raw/Source Material Access

### Where to Find Raw (Untranslated) Chapters

#### Korean Manhwa Raws
- **Naver Webtoon** (comic.naver.com) — Official source. Requires Korean account
- **Kakao Page** (page.kakao.com) — Official source. Requires Korean account
- **Toomics** — Another Korean platform
- **Account workarounds:** VPN + Korean phone number services exist but are unreliable and potentially TOS-violating

#### Japanese Manga Raws
- **Manga Plus** — Free raws on release day for Jump titles
- **ComicWalker** — Free Kadokawa raws with rotation
- **Amazon Japan** (amazon.co.jp) — Digital manga purchases. High quality
- **Rakuten Kobo** — Digital manga store
- **BookWalker** — Kadokawa's digital store
- **Honto** — Japanese digital bookstore

### Translation Timeline: Raw to English

| Tier | Series Examples | Time to English | Source |
|------|----------------|-----------------|--------|
| Tier 1 (Simulpub) | One Piece, MHA, JJK | Same day | Official (Manga Plus, Viz) |
| Tier 2 (Fast fan TL) | Solo Leveling, ORV, TBATE | 24-48 hours | Scanlation groups |
| Tier 3 (Regular fan TL) | Mid-popularity manhwa/manga | 3-7 days | Scanlation groups |
| Tier 4 (Slow/Niche) | Lesser-known series | Weeks to months | Sporadic fan translations |
| Tier 5 (No TL) | Very niche series | Never translated | Only AI translation option |

### Image Quality Considerations

**Resolution standards:**
- Official webtoon platforms: 720-1080px width, optimized for mobile
- Official manga (digital): ~1400-2100px width at 72-150 DPI
- High-quality scanlations: 1200-2000px width
- Volume scans (tankoubon): ~2140 x 3024px at 300 DPI (print quality)
- Low-quality aggregator rips: 600-900px, compressed JPEG artifacts

**Watermarks:**
- Official platforms often add visible or invisible watermarks
- Naver Webtoon: Light watermarks on some series
- Kakao Page: Watermarks present
- Scanlations: Usually no watermarks (cleaned by editors)
- Some aggregators add their own site watermarks

**For YouTube video production:**
- 1080p video needs images at least 1080px wide
- 4K video needs images at least 2160px wide
- AI upscaling tools can enhance lower-res sources (see Section 6)
- Vertical webtoon format needs cropping/panning for horizontal video

---

## 4. APIs and Programmatic Access

### Platforms with Official/Documented APIs

#### AniList GraphQL API (Best for metadata)
- **URL:** https://graphql.anilist.co
- **Docs:** https://docs.anilist.co
- **Auth:** Not required for most queries. OAuth2 for mutations
- **Data:** 500K+ anime/manga entries. Titles, synopses, characters, staff, genres, tags, scores, popularity, release dates, relations
- **Format:** GraphQL (POST requests)
- **Rate limit:** Generous for typical use
- **Best for:** Series metadata, character info, genre tagging, trend tracking, related series discovery
- **Python/JS libraries:** Multiple community wrappers available

#### MangaDex API (Best for chapter access)
- **URL:** https://api.mangadex.org
- **Docs:** https://api.mangadex.org/docs/swagger.html
- **Auth:** Not required for reading. Auth for uploads/follows
- **Data:** Manga metadata, chapter listings, page images, cover art, scanlation group info, tags
- **Format:** REST/JSON
- **Rate limit:** Moderate. Respect their guidelines
- **Best for:** Accessing actual chapter images programmatically. Multi-language support
- **Python wrapper:** `mangadex` on PyPI
- **Caveats:** Reduced catalog post-May 2025 DMCA. No guarantee of availability for specific titles

#### Jikan API (Unofficial MyAnimeList)
- **URL:** https://api.jikan.moe/v4
- **Docs:** https://docs.api.jikan.moe
- **Auth:** Not required
- **Data:** All MAL data — anime, manga, characters, people, reviews, recommendations, statistics
- **Format:** REST/JSON
- **Rate limit:** 3 requests/second, 60/minute (free tier)
- **Best for:** Series popularity data, user scores, review aggregation, recommendations
- **Reliability:** Scrapes MAL, so depends on MAL availability

#### MangaUpdates API
- **URL:** https://api.mangaupdates.com/v1
- **Auth:** Both authenticated and unauthenticated access
- **Data:** Series info, release tracking, scanlation group data, release dates
- **Format:** REST/JSON
- **Python client:** `manga-updates-api-client` on GitHub
- **Best for:** Release tracking, knowing when new chapters drop, scanlation group activity

#### Kitsu API
- **URL:** https://kitsu.io/api/edge
- **Docs:** https://kitsu.docs.apiary.io
- **Auth:** OAuth2 (optional for GET)
- **Data:** Anime/manga entries, characters, reviews, user libraries
- **Format:** JSON:API specification
- **Rate limit:** Paginated (10-20 per page)
- **Best for:** Alternative metadata source, community ratings

### Unofficial API Wrappers & Scrapers

#### Manga Plus (Shueisha)
- **Python client:** `mangaplus` on GitHub (hyugogirubato/mangaplus)
- **Also:** `pymangaplus` on PyPI, `mloader` for downloading
- **Note:** Unofficial. Uses Shueisha's internal protobuf API. Could break without notice
- **Data:** All Manga Plus titles, chapters, page images

#### Webtoon / LINE Webtoon
- **RapidAPI:** Unofficial Webtoon API by APIDojo — listings for Canvas and Original
- **Python:** `webtoon_data` library for title lists and rankings
- **Scraper:** `scrapetoon` on GitHub — stats and episode downloads
- **Non-public API:** `webtoon-api` on GitHub (s0ko1ex) — communicates with internal endpoints
- **Naver Webtoon scraper:** Available on Apify for Korean manhwa data

#### General Manga Scrapers
- **HakuNeko** — Cross-platform manga/anime downloader. 1,200+ sources. GUI + CLI. Open source
- **Mihon / Tachiyomi forks** — Extension-based. Hundreds of source plugins. Android-focused but Suwayomi brings it to desktop
- **Suwayomi-Server** — Desktop/server rewrite of Tachiyomi. Runs Mihon extensions. Can be used as a headless scraping server
- **manga-downloader** (GitHub) — Various Python projects for batch downloading from multiple sites

### Anti-Bot Measures by Platform

| Platform | Protection Level | Measures |
|----------|-----------------|----------|
| Webtoon/LINE Webtoon | High | Cloudflare, rate limiting, behavioral analysis |
| Kakao Page | Very High | Cloudflare, DRM, account verification, aggressive monitoring |
| Manga Plus | Medium | Rate limiting, protobuf API (not standard REST) |
| Viz Media | High | Cloudflare, DRM on premium content |
| MangaDex | Low | Open API, rate limits only |
| Aggregators (general) | Low-Medium | Basic rate limiting, some Cloudflare |

### Cloudflare Bypass Considerations (2026)

- Cloudflare uses browser fingerprinting, JS challenges, behavioral analysis, and ML-based bot detection
- As of July 2025, Cloudflare blocks AI crawlers by default — opt-in model for site owners
- Bypassing Cloudflare for commercial use is legally risky and violates most platforms' TOS
- Services like ScrapingBee offer managed Cloudflare bypass but add cost and latency
- **Recommendation:** Prefer platforms with open APIs (MangaDex, AniList, Jikan) over scraping protected sites

---

## 5. Story/Plot Information Sources

### Wiki & Database Sites

#### Fandom Wikis (Best for chapter-by-chapter detail)
- **URL:** https://www.fandom.com (search "[series name] wiki")
- **Coverage:** Most popular manga/manhwa have dedicated wikis with:
  - Chapter-by-chapter synopses
  - Character profiles with detailed backstories
  - Story arc breakdowns
  - Power system explanations
  - Relationship maps
- **API:** Fandom/MediaWiki API available for programmatic access
- **Quality:** Varies by community size. Popular series (Solo Leveling, Tower of God, One Piece) have extremely detailed wikis. Niche series may be sparse
- **For pipeline:** Primary source for chapter summaries and character info. API-accessible

#### MyAnimeList (MAL) — https://myanimelist.net
- **Data:** 62,000+ manga entries. Synopses, scores, reviews, recommendations, character lists
- **API:** Via Jikan (see Section 4). Free, no auth required
- **For pipeline:** Great for series metadata, popularity metrics, and user reviews to mine for talking points

#### AniList — https://anilist.co
- **Data:** 500K+ entries. Modern UI. Detailed tagging system. User activity feeds
- **API:** Official GraphQL API. Best-documented anime/manga API
- **For pipeline:** Excellent for automated metadata retrieval. GraphQL allows precise queries

#### MangaUpdates (Baka-Updates) — https://www.mangaupdates.com
- **Data:** Release tracking, scanlation group info, detailed series categorization, publication info
- **API:** Official REST API at api.mangaupdates.com/v1
- **For pipeline:** Best for tracking when new chapters release. Trigger automated content creation on new chapter detection

#### Anime-Planet — https://www.anime-planet.com
- **Data:** 50K+ manga entries. Character database with personality tags. Recommendations
- **For pipeline:** Good supplementary data source. Character personality descriptions useful for scripting

#### NamuWiki — https://en.namu.wiki
- **Data:** Korean wiki. Very detailed entries for manhwa. Character info, plot details
- **Language:** Korean primary, some English pages
- **For pipeline:** Best Korean-language wiki for manhwa details not covered on English wikis

### Synopsis & Summary Resources

| Source | What You Get | Access |
|--------|-------------|--------|
| **Fandom Wikis** | Chapter-by-chapter synopses, character bios | Free, API available |
| **TV Tropes** (tvtropes.org) | Trope analysis, story structure breakdowns | Free, scraping possible |
| **ManhwaRecap.com** | Dedicated manhwa chapter summaries | Free website |
| **ManhwaFresh.com** | Daily manhwa recap updates | Free website |
| **Reddit r/manga** (3.5M members) | Chapter discussion threads with user analysis | Reddit API |
| **Reddit r/manhwa** | Manhwa-specific discussions and recs | Reddit API |
| **Reddit r/OmniscientReader** etc. | Series-specific subreddits with deep analysis | Reddit API |

### Character Databases

- **AniList** — Character pages with descriptions, voice actors, media appearances
- **MyAnimeList** — Character listings with basic info
- **Anime Characters Database** (animecharactersdatabase.com) — Physical descriptions, personality traits
- **Anime-Planet** — Character tags (personality, role, appearance traits)
- **Fandom Wikis** — Most detailed per-series character info
- **Zerochan** — Character image gallery (18,000+ manga cover images)

---

## 6. Image/Visual Asset Sources

### High-Quality Cover Art

| Source | Quality | Licensing | Notes |
|--------|---------|-----------|-------|
| **MangaDex API** (covers endpoint) | 256px / 512px thumbnails | Fair use for review | api.mangadex.org/docs/03-manga/covers |
| **AniList API** | Cover images in multiple sizes | Fair use for review | Via GraphQL media query |
| **MAL / Jikan API** | Cover art URLs | Fair use for review | Hotlinking from MAL CDN |
| **Official publisher sites** | High res | Fair use for review | Manual download |
| **Amazon product images** | High res covers | Product listing use | Via product pages |

### Fan Art Communities

| Platform | Content | Licensing |
|----------|---------|-----------|
| **DeviantArt** | Massive fan art community | Artist-specific licenses. Must check each piece |
| **Pixiv** | Japanese/Korean fan art hub | Most prohibit commercial use without permission |
| **ArtStation** | Professional fan art | Individual artist licenses |
| **Twitter/X** | Fan art posts | No commercial reuse rights |

**Key warning:** Fan art is copyrighted by its creator. Using fan art in commercial YouTube content without permission is copyright infringement, even if the underlying characters are from a manga/manhwa.

### AI-Generated Alternatives for Thumbnails

**Recommended tools (by legal safety):**

1. **Adobe Firefly** — Trained exclusively on Adobe Stock + licensed content. Safest for commercial use. Anime style capabilities improving
2. **Komiko AI** — Free, unlimited anime art generator. Generates manga/manhwa style characters
3. **Stable Diffusion** (with anime models like Anything V5, Counterfeit) — Open source. Run locally. No usage fees. But trained on scraped data — legal gray area
4. **NovelAI** — Strong anime generation. Subscription required. Trained partly on Danbooru (scraped fan art) — legal concerns
5. **Midjourney** — High quality but trained on scraped data. Commercial license included with subscription

**Best practices for AI thumbnails:**
- Generate original characters inspired by a series' aesthetic, not specific copyrighted characters
- Use for backgrounds, atmosphere, generic anime scenes
- Avoid generating recognizable characters, logos, or distinctive UI elements
- YouTube allows AI-generated content but requires disclosure for realistic depictions
- "Anime cityscape background" or "dramatic manga-style action pose" = low risk
- "Solo Leveling Sung Jinwoo exact likeness" = high risk

### Upscaling Low-Resolution Images

- **Upsampler** (upsampler.com) — AI manga-specific upscaler. Preserves line work and screen tones
- **Real-ESRGAN** — Open source AI upscaler with anime-specific models
- **Waifu2x** — Classic anime image upscaler. Still effective for manga panels
- **Topaz Gigapixel** — Commercial upscaler with good anime results

---

## 7. Legal Considerations for YouTube Content

### Fair Use Framework (US Law)

Four factors courts evaluate:
1. **Purpose and character** — Transformative use (commentary, criticism, review, education) favored. Commercial use weighs against
2. **Nature of the original** — Creative works (manga/manhwa) get stronger protection
3. **Amount used** — Using less of the original favors fair use. Showing entire chapters = very risky
4. **Market effect** — If your video replaces the need to read the original, strongly against fair use

**Critical point:** Fair use is a legal *defense*, not a right. You can still receive DMCA takedowns and must then prove fair use — which requires legal resources.

### How Existing Manhwa Recap Channels Operate

**Common practices:**
- Include copyright disclaimers (legally meaningless but signal intent)
- Show selected panels, not entire chapters
- Add voiceover narration as commentary/analysis layer
- Use zoom/pan effects on panels (Ken Burns) rather than static display
- Add text overlays, reactions, and original analysis
- Some channels use AI-generated or modified visuals instead of raw panels
- Focus on popular series where publishers haven't been aggressive on YouTube

**Revenue potential:** Top manhwa recap channels earn $2.8K-$8.4K/month in AdSense. Channels like Manhwa Recap Zone and ManhwaCapped operate at significant scale.

**What they DON'T do:**
- Show complete chapters panel by panel
- Upload raw scans without commentary
- Use official translations without modification

### DMCA Risk by Publisher

#### Very Aggressive Enforcement
| Publisher | Region | Notable Actions |
|-----------|--------|-----------------|
| **Kakao Entertainment** | Korea | 240M illegal removals in H2 2024. 30K takedowns/day. Shut down Reaper Scans. Criminal prosecutions. Prison sentences upheld |
| **Webtoon Entertainment** (Naver) | Korea/Global | Cease-and-desist to aggregators (EnryuManga, etc.). Legal action against 170+ piracy sites |
| **Shueisha** | Japan | 205M+ URL takedown requests to Google. DMCA subpoenas against 24+ piracy sites. Even struck their own translator (Lightning/Viz incident) |
| **Viz Media** | US/Japan | #4 globally for Google URL takedowns. Aggressive across all platforms |
| **Kodansha** | Japan | Part of CODA/IAPO coalition. Won Cloudflare lawsuit |
| **Toei Animation** | Japan | Hit YouTuber Totally Not Mark with 150 copyright claims simultaneously. Targets review content, not just piracy |
| **Kadokawa** | Japan | Won Cloudflare lawsuit alongside other Big 4 publishers |

#### Moderate Enforcement
| Publisher | Notes |
|-----------|-------|
| **Yen Press** | Focuses on piracy sites rather than YouTube reviews |
| **Square Enix** | Part of DMCA coalition but less individually aggressive on YouTube |
| **Seven Seas** | Smaller publisher, less enforcement infrastructure |

#### Relatively Lenient (on YouTube reviews specifically)
| Publisher | Notes |
|-----------|-------|
| **Indie/Canvas creators** | Smaller creators often welcome promotion. Some actively encourage recap content |
| **Chinese publishers** | Less infrastructure for international enforcement (varies) |
| **Smaller Korean studios** | Less resources for YouTube policing |

**Important caveat:** "Lenient" can change overnight. Any publisher can decide to start enforcing at any time. YouTube's AI-based Content ID is also getting better at detecting manga panels.

### The Totally Not Mark Precedent

- YouTuber received 150 copyright claims simultaneously from Toei Animation for Dragon Ball/One Piece review videos
- Three years of work removed. Primary income source eliminated
- Eventually won appeals — videos restored but blocked in Japan only
- **Lesson:** Even clearly transformative review content can be hit. Appeals are possible but slow and stressful

### Best Practices for Transformative Use

1. **Always add substantial commentary** — Don't just narrate what happens. Add analysis, comparisons, criticism, predictions
2. **Limit panel usage** — Show 10-20% of a chapter's panels, not all of them. Mix with original visuals
3. **Transform visually** — Use zoom/pan effects, color grading, overlays, split-screen comparisons
4. **Don't replace the source** — A viewer should still want to read the original after watching your video
5. **Use multiple sources** — Don't rely solely on one publisher's content
6. **Build in AI-generated visuals** — Supplement real panels with AI art for backgrounds, transitions, character interpretations
7. **Document your process** — Keep records showing your editorial/transformative process in case of disputes
8. **Consider revenue diversification** — Don't rely 100% on AdSense in case of strikes. Build Patreon, merch, etc.

### YouTube Copyright System (2026)

- YouTube using AI to detect copyrighted manga/anime content (Content ID improvements)
- Three copyright strikes = channel termination
- Copyright claims (not strikes) reduce monetization but don't threaten the channel
- Counter-notifications possible but require personal info disclosure to the claimant
- 2026 rules are getting tougher per YouTube's updated policies

---

## 8. Automation-Friendly Sources

### Tier 1: APIs with Structured Data (Best for Automation)

#### AniList API — Series Discovery & Metadata
```
Endpoint: https://graphql.anilist.co
Use for: Finding trending series, getting synopses, character info, genres, tags
Update frequency: Near real-time
Auth: None for reads
Output: JSON (GraphQL)
```

#### MangaDex API — Chapter Access & Images
```
Endpoint: https://api.mangadex.org
Use for: Getting chapter lists, page images, cover art, scanlation info
Update frequency: Real-time (new uploads)
Auth: None for reads
Output: JSON (REST)
```

#### Jikan API — MAL Data
```
Endpoint: https://api.jikan.moe/v4
Use for: Popularity scores, reviews, recommendations, character data
Update frequency: Cached (varies)
Auth: None
Rate limit: 3/sec, 60/min
Output: JSON (REST)
```

#### MangaUpdates API — Release Tracking
```
Endpoint: https://api.mangaupdates.com/v1
Use for: New chapter release detection, series metadata
Update frequency: Real-time
Auth: Optional (both modes)
Output: JSON (REST)
```

### Tier 2: RSS Feeds & Notifications

#### MangaDex RSS
- RSS feeds available for followed series
- Can be consumed by any RSS reader or automation tool (Feedly, Inoreader, custom parser)
- Trigger automated pipelines when new chapters detected

#### MangaUpdates RSS
- RSS feed for new chapter releases
- Used by Discord bots (MangaUpdates Bot, Mangalerts, Discans) for notifications
- Can trigger webhooks via IFTTT, Zapier, or custom integrations

#### Reddit RSS
- r/manga and r/manhwa chapter discussion threads
- Monitor via Reddit API or RSS for new chapter posts
- Useful for detecting trending series and chapter drops

### Tier 3: Scraping (More Fragile)

| Tool | Sources | Language | Notes |
|------|---------|----------|-------|
| **HakuNeko** | 1,200+ sources | Electron/JS | GUI + CLI. Most comprehensive |
| **Suwayomi-Server** | Mihon extensions | Kotlin/JVM | Headless server. Run as microservice |
| **scrapetoon** | Webtoon | Rust | Stats and episode download |
| **manga-downloader** (various) | Multiple | Python | Batch chapter downloads |
| **webtoon_data** | Webtoon | Python | Title lists and rankings |
| **mangaplus** (unofficial) | Manga Plus | Python | Shueisha titles access |

### Automation Pipeline Triggers

| Trigger | Source | Method |
|---------|--------|--------|
| New chapter released | MangaUpdates RSS / MangaDex API | Poll RSS feed or API endpoint every 30 min |
| Series trending | AniList API (trending query) | Daily check of trending manga |
| New series announced | AniList API / MAL news | Monitor new entries |
| Chapter discussion spike | Reddit API (r/manga) | Monitor post karma/comment volume |
| Official translation released | Manga Plus / Viz release calendar | Scrape release schedules |

### Structured Data Availability

| Data Type | Best Source | Format |
|-----------|-----------|--------|
| Series titles (multi-language) | AniList API | JSON (romaji, English, native) |
| Chapter numbers & titles | MangaDex API | JSON |
| Release dates | MangaUpdates API | JSON |
| Synopses | AniList API + Fandom wikis | JSON / HTML |
| Character names & descriptions | AniList API + Fandom API | JSON |
| Genre/tag classification | AniList API (rich tagging) | JSON |
| Popularity/scores | AniList API + Jikan API | JSON (numeric) |
| Cover images | MangaDex API + AniList API | Image URLs |
| Chapter page images | MangaDex API | Image URLs |

---

## 9. Recommended Pipeline Architecture

### For an Automated Manhwa/Manga Recap YouTube Channel

```
[Discovery Layer]
  AniList API (trending series, metadata)
  MangaUpdates API (new chapter alerts)
  Reddit API (community buzz detection)
       |
       v
[Content Acquisition Layer]
  MangaDex API (chapter images — where available)
  Fandom Wiki API (chapter synopses, character info)
  AniList API (series context, descriptions)
       |
       v
[Script Generation Layer]
  Chapter synopsis from wiki + original analysis
  Character context from databases
  LLM-assisted script writing (commentary + analysis)
       |
       v
[Visual Assembly Layer]
  Selected panels from MangaDex (limited, fair use)
  AI-generated supplementary visuals (backgrounds, characters)
  Ken Burns effects, zoom/pan on panels
  AI upscaling for low-res source images
       |
       v
[Production Layer]
  TTS or voice narration
  Video assembly (FFmpeg / programmatic editing)
  Thumbnail generation (AI-generated + cover art composites)
       |
       v
[Publishing Layer]
  YouTube upload via API
  SEO metadata from AniList tags/genres
  Scheduling based on chapter release timing
```

### Key Risks to Mitigate

1. **Copyright strikes** — Limit panel usage, maximize original commentary, use AI visuals as supplements
2. **API instability** — MangaDex catalog shrinking. Have fallback sources. Cache aggressively
3. **Quality consistency** — Source image quality varies. Build in upscaling pipeline
4. **Content freshness** — Automate new chapter detection to publish recaps quickly after release
5. **Publisher enforcement changes** — Monitor industry news. Be ready to pivot series focus if a publisher starts targeting YouTube
6. **Platform TOS changes** — YouTube's AI copyright detection improving. Stay ahead of policy changes

### Practical First Steps

1. Set up AniList + MangaDex + Jikan API integrations for metadata
2. Build MangaUpdates RSS monitoring for new chapter alerts
3. Start with manhwa series from smaller publishers (lower DMCA risk)
4. Develop AI visual generation pipeline for supplementary images
5. Create script templates that ensure transformative commentary
6. Test with 5-10 videos before scaling automation
7. Track which publishers send claims and adjust series selection accordingly

---

## Sources

### Official Platforms
- [LINE Webtoon](https://www.webtoons.com)
- [Tapas](https://tapas.io/)
- [Manga Plus by Shueisha](https://mangaplus.shueisha.co.jp/updates)
- [Crunchyroll Manga Launch Announcement](https://www.crunchyroll.com/news/announcements/2025/1/7/crunchyroll-new-manga-app-2025)
- [Viz Media Copyrights](https://www.viz.com/copyrights)
- [Kakao Page](https://www.kakaocorp.com/page/service/service/KakaoPage?lang=en)

### APIs & Developer Resources
- [AniList API Docs](https://docs.anilist.co/)
- [MangaDex API Documentation](https://api.mangadex.org/docs/swagger.html)
- [Jikan API (Unofficial MAL)](https://jikan.moe/)
- [Kitsu API Docs](https://kitsu.docs.apiary.io/)
- [MangaUpdates API Client (Python)](https://github.com/FourierMeow/manga-updates-api-client)
- [MangaDex Python Wrapper](https://pypi.org/project/mangadex/)
- [Manga Plus Python Client](https://github.com/hyugogirubato/mangaplus)
- [Webtoon Data Python Library](https://webtoon-data.readthedocs.io/en/latest/)

### Tools & Scrapers
- [HakuNeko — Manga & Anime Downloader](https://hakuneko.download/)
- [HakuNeko GitHub](https://github.com/manga-download/hakuneko)
- [Mihon (Tachiyomi successor)](https://mihon.app/forks/)
- [Suwayomi-Server (Desktop Tachiyomi)](https://github.com/Suwayomi/Suwayomi-Server)
- [scrapetoon (Webtoon scraper)](https://github.com/RoloEdits/scrapetoon)
- [MangaUpdates Discord Bot](https://github.com/jckli/mangaupdates-bot)

### Legal & Copyright Research
- [Kakao Entertainment Anti-Piracy Whitepaper](https://newsroom.kakaoent.com/news/6th-anti-piracy-whitepaper-kakao-entertainment-launches-1st-ever-comprehensive-crackdown-system-for-webtoons-and-web-novels-blocks-240-million-illegal-cases/)
- [Kakao Entertainment Shuts Down 11 Piracy Sites (ANN)](https://www.animenewsnetwork.com/news/2025-08-23/kakao-entertainment-shuts-down-11-piracy-sites-deletes-160-million-illegal-works-in-1st-half-of-2025/.227932)
- [Webtoon Legal Action Against 170+ Piracy Sites](https://fandomwire.com/im-not-paying-for-each-chapter-webtoon-set-to-take-major-legal-action-against-over-170-piracy-sites-after-drastically-declining-sales/)
- [Korean Court Upholds Prison Sentence for OKTOON Operator](https://www.animenewsnetwork.com/news/2026-01-29/korean-court-upholds-prison-sentence-for-operator-behind-major-webtoon-piracy-site-oktoon/.233554)
- [Japanese Publishers Win Cloudflare Lawsuit](https://www.animenewsnetwork.com/news/2025-11-19/shueisha-kodansha-shogakukan-kadokawa-win-copyright-suit-against-cloudflare/.231199)
- [Totally Not Mark vs Toei Animation](https://kotaku.com/youtuber-hit-with-150-copyright-claims-for-reviews-feat-1848178180)
- [DMCA on YouTube in 2026](https://dmcadesk.com/blogs/dmca-on-youtube-copyright-strikes-and-takedowns/)
- [Reaper Scans Shutdown](https://playthrones.com/reaper-scans-shutdown-fans-guide/)
- [MangaDex DMCA Takedown (May 2025)](https://animeinjapan.com/2025/05/mangadex-and-its-dmca-takedown-what-you-need-to-know/)

### Content & Community
- [r/manga Community Guide](https://prizmatem.co.uk/r-manga/)
- [ManhwaRecap.com](https://manhwarecap.com/)
- [Scanlation (Wikipedia)](https://en.wikipedia.org/wiki/Scanlation)
- [Where to Read Manhwa Legally (2025)](https://yeolliestorytime.com/where-to-read-manhwa-legally-in-2025/)
- [20 Best Websites to Read Manhwa Legally (2026)](https://techcult.com/best-websites-to-read-manhwa-legally/)
- [Webcomics Platform Guide (KComicsBeat)](https://kcomicsbeat.com/2024/09/25/guide-to-webtoon-platforms/)

### Visual Assets & AI Art
- [Komiko AI Anime Generator](https://komiko.app/ai-anime-generator)
- [AI Images for YouTube Thumbnails (2026)](https://thumbnailtest.com/guides/ai-youtube-thumbnails/)
- [Using AI Artwork to Avoid Copyright Infringement](https://copyrightlately.com/using-ai-artwork-to-avoid-copyright-infringement/)
- [Zerochan Manga Cover Gallery](https://www.zerochan.net/Manga+Cover)
