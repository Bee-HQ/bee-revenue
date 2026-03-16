# YouTube Video Review & Optimization Tools: Comprehensive Research

> Research date: March 2026
> Scope: AI-powered video analysis, script review, thumbnail optimization, retention analysis, open-source tools, paid SaaS, YouTube API capabilities, LLM-based approaches, storytelling frameworks, and anime/manga-specific tooling.

---

## Table of Contents

1. [AI-Powered Video Analysis Tools](#1-ai-powered-video-analysis-tools)
2. [Open Source & Self-Hostable Tools](#2-open-source--self-hostable-tools)
3. [Paid SaaS Tools](#3-paid-saas-tools)
4. [YouTube Analytics API Capabilities](#4-youtube-analytics-api-capabilities)
5. [LLM-Based Review Agent Approaches](#5-llm-based-review-agent-approaches)
6. [Drama & Storytelling Analysis Frameworks](#6-drama--storytelling-analysis-frameworks)
7. [Manga/Manhwa/Anime-Specific Tools](#7-mangamanhwaanime-specific-tools)
8. [Building Our Own: Claude Code Agent for Video Review](#8-building-our-own-claude-code-agent-for-video-review)

---

## 1. AI-Powered Video Analysis Tools

### OutlierKit
- **URL:** https://outlierkit.com
- **What it does:** Analyzes YouTube videos to find outliers (5-20x overperformance). AI evaluates video openings using ML trained on millions of high-performing videos. Breaks down scripts for hook strength, pacing, curiosity loops, and engagement patterns. Identifies optimal segment lengths before needing pattern interrupts and where to place b-roll/graphics.
- **Pricing:** $9-19/month (cheapest in the outlier-finder category)
- **Open source?** No
- **Can it be replicated with an LLM agent?** Partially. The outlier detection requires a large video database, but the script analysis (hook strength, pacing, engagement patterns) could be replicated by feeding transcripts + metadata to Claude with a well-designed scoring rubric.
- **Relevance:** High -- their hook analysis and pacing detection approach is exactly what we'd want to build. Their "pattern interrupt identification" feature maps directly to retention curve optimization.

### Retention Rabbit
- **URL:** https://retentionrabbit.com
- **What it does:** AI-powered pre-publish retention analysis. Analyzes every frame with claimed 97.7% accuracy, showing where viewers would lose interest before publishing. Users identify critical drop-off points 30x faster than manual analysis. Publishes benchmark reports (150M+ minutes analyzed).
- **Key data:** 2025 average YouTube video retains 23.7% of viewers. 55%+ viewer drop-off within first minute. Videos 5-10 mins hold viewers best (31.5%). Strong intros with >65% first-minute retention correlate with 58% higher average view duration.
- **Pricing:** Free trial available; paid plans not publicly listed
- **Open source?** No
- **Can it be replicated?** The pre-publish frame-by-frame analysis would need computer vision. But transcript-based retention prediction (identifying likely drop-off points from script pacing) is buildable with LLMs. Their benchmark data is gold for calibrating our own scoring system.
- **Relevance:** Very high -- their benchmark data validates what we should measure against.

### ScreenApp
- **URL:** https://screenapp.io/features/video-analyzer
- **What it does:** Web-based video analyzer using computer vision for object detection, scene classification, emotion recognition. Speech-to-text with sentiment analysis. OCR for on-screen text. Provides engagement metrics, content quality scores, actionable recommendations.
- **Pricing:** Free tier (3 analyses/month, no signup). Paid plans available.
- **Open source?** No
- **Can it be replicated?** The visual analysis requires CV models (YOLO, BLIP). The transcript analysis + sentiment is straightforward with LLMs.
- **Relevance:** Medium -- their multi-modal approach (visual + audio + text) is the gold standard, but for manhwa recaps, transcript analysis alone covers most of the value.

### Memories.ai
- **URL:** https://memories.ai/tools/youtube-video-analyzer-ai
- **What it does:** Combines computer vision, speech recognition, and OCR in one workflow. Produces unified timeline of scenes, transcript, entities, summaries. Supports 15+ platforms. Provides recommendations for titles, descriptions, content strategy.
- **Pricing:** Free (no login required)
- **Open source?** No
- **Can it be replicated?** Yes, the transcript + metadata analysis parts. Visual analysis requires additional CV infrastructure.
- **Relevance:** Medium -- useful for competitive analysis of existing videos.

### Maekersuite
- **URL:** https://maekersuite.com
- **What it does:** AI-powered video pre-production. Analyzes competitor videos for performance, related videos, watch intensity, and full transcript. Generates complete video scripts in ~15 minutes by analyzing millions of YouTube videos. Auto-generates SEO-friendly descriptions and tags.
- **Pricing:** From $23/month
- **Open source?** No
- **Can it be replicated?** Yes. Competitor analysis is what bee-content-research already does. Script generation and SEO optimization are straightforward LLM tasks.
- **Relevance:** Medium -- confirms our existing tool covers similar ground. Their "watch intensity" analysis is interesting.

---

## 2. Open Source & Self-Hostable Tools

### youtube-transcript-api (Python)
- **URL:** https://github.com/jdepoix/youtube-transcript-api
- **What it does:** Python API to get transcripts/subtitles for any YouTube video. Works with auto-generated subtitles. No API key needed, no headless browser.
- **Pricing:** Free / MIT license
- **Relevance:** Critical infrastructure -- we already use this in bee-content-research. Foundation for any transcript-based analysis.

### video-analyzer (byjlw)
- **URL:** https://github.com/byjlw/video-analyzer
- **What it does:** Combines vision models (Llama 11B vision), Whisper for transcription, and OpenCV for frame selection. Selects interesting/different frames, analyzes each with a vision LLM maintaining chronological context, then reconstructs a comprehensive video description integrating transcript.
- **Tech:** Python 3.11+, FFmpeg, Ollama (local) or OpenRouter/OpenAI (cloud)
- **Requirements:** 16GB RAM min (32GB recommended), GPU with 12GB VRAM or Apple M-series with 32GB
- **Pricing:** Free / open source
- **Can it be adapted?** Very promising as a foundation. Could be extended to analyze manhwa recap videos by adding engagement scoring on top of the description output.
- **Relevance:** High -- the frame analysis + transcript combination is exactly what a comprehensive video reviewer needs. Published on PyPI as `video-analyzer`.

### YouTube Video Analyzer Pro (KazKozDev)
- **URL:** https://github.com/KazKozDev/video-analyser
- **What it does:** AI-powered video analysis using Whisper for transcription and Llama 3.2 for language analysis. Built with FastAPI. Provides channel optimization, content performance analysis, audience retention insights, engagement optimization, competitor research.
- **Tech:** Python 3.9+, FastAPI, Whisper AI, Llama 3.2, YouTube Data API
- **Pricing:** Free / open source
- **Relevance:** High -- closest open-source equivalent to what we want to build. Could serve as a starting point or reference architecture.

### YouTube Video Inspector (emirhansilsupur)
- **URL:** https://github.com/emirhansilsupur/youtube-video-analyzer
- **What it does:** Multi-agent tool using CrewAI that fetches video metadata, analyzes comments, and generates performance reports exportable as PDFs.
- **Tech:** CrewAI multi-agent framework
- **Pricing:** Free / open source
- **Relevance:** Medium -- the multi-agent architecture (separate agents for metadata, comments, reporting) is a good pattern. CrewAI is an interesting orchestration framework to evaluate.

### AI-Powered Video Analyzer (arashsajjadi)
- **URL:** https://github.com/arashsajjadi/ai-powered-video-analyzer
- **What it does:** Fully offline video analysis: YOLO for object detection, BLIP for image captioning, Whisper for transcription, PANNs for audio event detection, Ollama LLMs for summaries. GUI included.
- **Pricing:** Free / open source
- **Relevance:** Medium -- interesting for comprehensive offline analysis, but heavy infrastructure. More useful if we need visual analysis of manhwa panel quality.

### YouTube Engagement Prediction (academic)
- **URL:** https://github.com/avalanchesiqi/youtube-engagement
- **What it does:** Research code from ICWSM '18 paper "Beyond Views: Measuring and Predicting Engagement in Online Videos." Provides engagement scoring function based on 5M YouTube videos. Takes video length and watch percentage, outputs relative engagement score.
- **Pricing:** Free / research code
- **Relevance:** Medium -- the engagement scoring model could calibrate our benchmarks, though it's from 2018 data.

### YoutubeGPTClaude
- **URL:** https://github.com/agniiva/YoutubeGPTClaude
- **What it does:** Streamlit app that summarizes YouTube videos by converting audio to text and generating summaries. Supports both OpenAI and Claude for the summarization step.
- **Pricing:** Free / open source
- **Relevance:** Low -- basic summarization only, but demonstrates Claude integration pattern.

### YouTube Transcript AI Assistant
- **URL:** https://github.com/pawan941394/YouTube-Transcript-AI-Assistant
- **What it does:** Extracts transcripts and lets you chat with video content using LLMs. Built with Streamlit, supports multiple languages and auto-generated captions.
- **Pricing:** Free / open source
- **Relevance:** Low -- chat-with-video is useful but not our primary need.

### Advanced YouTube SEO Generator
- **URL:** https://github.com/Avinashricky211/Advanced-Youtube-Seo-Generator
- **What it does:** Python script that optimizes YouTube video SEO via the YouTube Data API. Generates recommendations for titles, descriptions, tags, hashtags.
- **Pricing:** Free / open source
- **Relevance:** Medium -- SEO optimization is one dimension of our review pipeline.

### youtube-automation-agent (darkzOGx)
- **URL:** https://github.com/darkzOGx/youtube-automation-agent
- **What it does:** Fully automated YouTube channel management. Creates, optimizes, and publishes videos 24/7. Works with free Gemini API or OpenAI. Includes multi-agent architecture: Content Strategy Agent, Script Writer Agent, Thumbnail Designer Agent, SEO Optimizer Agent, Publishing Agent.
- **Tech:** Node.js 18+, YouTube API, Gemini or OpenAI
- **Pricing:** Free with Gemini (60 req/min), $10-50/month with OpenAI
- **Relevance:** Medium-high -- the multi-agent architecture pattern is directly applicable. We could adapt the agent separation for our review pipeline.

---

## 3. Paid SaaS Tools

### vidIQ
- **URL:** https://vidiq.com
- **What it does:** Industry-leading keyword research with search volume, competition scores, predictive trending analysis. AI Coach provides channel-specific growth strategy. AI script writer with SEO-optimized output, structured for retention (scroll-stopping intros, natural transitions). Real-time performance tracking and competitor analysis.
- **Pricing:** Free tier available. Boost plan ~$16.58/month (annual). Coaching + Boost higher.
- **Strengths vs building our own:** Keyword research database is massive and hard to replicate. Trend prediction requires large-scale data collection. Their AI Coach is essentially a fine-tuned LLM prompt -- replicable.
- **Relevance:** Their keyword research data is hard to replicate, but their script analysis is essentially what an LLM does with the right prompt + context.

### TubeBuddy
- **URL:** https://tubebuddy.com
- **What it does:** 50+ tools for YouTube optimization. AI-powered title suggestions with A/B testing. Thumbnail A/B testing. SEO Studio for titles, tags, descriptions. Retention analyzer. Bulk processing tools. Direct YouTube Studio integration (Chrome extension).
- **Pricing:** Free plan available. Pro plan from $6-7.50/month.
- **Strengths vs building our own:** Their thumbnail A/B testing runs real experiments on live videos -- impossible to replicate without actual viewers. Their retention analyzer connects to real YouTube data. SEO tools are replicable.
- **Relevance:** The A/B testing for thumbnails/titles is the one feature we can't easily build ourselves. Worth using alongside our custom analysis.

### Subscribr
- **URL:** https://subscribr.ai
- **What it does:** AI script generation that learns your writing voice from existing videos. Scans thousands of channels to find outlier videos (2x-10x overperformance). Extracts title structure, psychological hooks, and thumbnail concepts from outliers. Generates titles, descriptions, tags in multiple flavors (informative, narrative, SEO-focused). Supports 35+ languages.
- **Pricing:** Ideation Plan $19/month (3-4 scripts, 20 credits). Creator Plan $49/month (10-12 scripts, 60 credits). Higher tiers up to $400/month for 400 credits + unlimited channels.
- **Strengths vs building our own:** Voice profiling is sophisticated -- learns from your existing content. Outlier detection is what bee-content-research already does (and arguably does better with 4,882 videos analyzed).
- **Relevance:** Their voice profiling approach is worth studying. We could implement similar by feeding Claude a few transcript examples as style reference.

### 1of10
- **URL:** https://1of10.com
- **What it does:** Identifies outlier videos across millions of videos. AI Idea Generator, Title Generator, Thumbnail Generator. Competitor tracking.
- **Pricing:** Basic $29/month ($349/year). Pro $69/month ($828/year) -- adds AI generators and 1000 credits.
- **Strengths vs building our own:** Large-scale outlier database. AI thumbnail generation.
- **Relevance:** Medium -- we already have outlier detection. Their thumbnail generation could be useful but is secondary to script/content review.

### ThumbnailTest
- **URL:** https://thumbnailtest.com
- **What it does:** A/B testing for thumbnails on live YouTube videos. Real-time analytics with CTR performance, confidence intervals, and projected impact on total views. Supports both new and existing videos. Unlimited thumbnail variants per test.
- **Pricing:** From $29/month for up to 10 active tests
- **Relevance:** High for operational use -- we can't replicate live A/B testing without real viewer data.

### Thumblytics
- **URL:** https://thumblytics.com
- **What it does:** Pre-publication thumbnail testing using human panels (hundreds of real respondents). AI thumbnail generation from prompts or YouTube links. Eye-tracking heatmap predictions showing where viewers look first. Scores title-thumbnail packaging as a combined unit.
- **Pricing:** Not publicly listed
- **Relevance:** The title-thumbnail packaging score is an interesting concept -- the combination matters more than either alone.

### AI Thumbnail Analyzers (Various)
- **Thumbnail AI** (thumbnail-ai.app) -- Scores emotion, curiosity, contrast, clarity
- **ThumbMagic** (thumbmagic.co) -- Scores contrast/clarity, face detection, text readability, color pop (0-100 each)
- **Pictiny** (pictiny.dev) -- Analyzes subject clarity, mobile legibility, contrast, safe zones, text ratio
- **Thumio** -- CTR prediction with claimed 87.3% accuracy
- **TubeTool AI** (tubetool.ai) -- Free thumbnail quality checker
- **ThumbPeek** (thumbpeek.com) -- Free tester + AI analyzer
- **Can be replicated?** Most of these use standard computer vision (contrast analysis, face detection, text OCR). The scoring rubrics could be implemented with a vision model like Claude's or GPT-4V.

### Prescene (Screenplay Analysis)
- **URL:** https://prescene.ai
- **What it does:** Professional screenplay analysis for film/TV. Coverage in minutes: plot, structure, characters, dialogue, themes, marketability. Sentiment and emotion analysis. Scene-by-scene breakdowns with tagging/filtering. Casting recommendations based on character descriptions.
- **Pricing:** 3 credits for $40, 10 for $100, 25 for $200. Or $29/script one-off, $59/month subscription.
- **Used by:** Paradigm Talent Agency (cut coverage time by 95%)
- **Can be replicated?** Yes -- this is essentially a specialized LLM prompt chain. Their scene-by-scene breakdown approach maps well to YouTube video segment analysis.
- **Relevance:** High as a pattern to follow. Their analysis dimensions (plot, structure, characters, dialogue, themes, marketability) translate to YouTube video dimensions (hook, structure, narration, engagement, SEO, niche fit).

### Greenlight Coverage
- **URL:** https://glcoverage.com
- **What it does:** Instant premium script analysis with security emphasis. Allows follow-up questions on the analysis.
- **Pricing:** Not publicly listed
- **Relevance:** Medium -- the follow-up questions feature is interesting for an interactive review agent.

### RivetAI
- **URL:** https://rivetai.com
- **What it does:** Pre-production tooling: AI script coverage, breakdowns, budgets, shooting schedules.
- **Relevance:** Low for YouTube specifically, but their multi-dimensional analysis approach is worth noting.

### Jasper AI (for YouTube scripts)
- **URL:** https://jasper.ai
- **What it does:** Long-form AI writing including YouTube scripts. Pre-built templates for hooks, intros, CTAs. Tone/style/structure control.
- **Pricing:** Creator plan $49/month
- **Relevance:** Low -- generic AI writing. Claude does this better with proper prompting.

### Writesonic
- **URL:** https://writesonic.com
- **What it does:** AI writing with 80+ templates. Fast bulk output (1000+ words/minute). Free forever tier available.
- **Pricing:** Free tier available. Paid from $20/month.
- **Relevance:** Low -- commodity AI writing.

### TubeLab
- **URL:** https://tubelab.net
- **What it does:** YouTube research platform. Scanned 400M+ public videos. Unique filters: RPM estimations, content quality, faceless potential, 20+ filters. Title formula analysis. Niche finding. API access available.
- **Pricing:** $178.80/year (~$14.90/month annual)
- **Relevance:** Medium -- their API access is interesting for programmatic research. RPM estimation and faceless potential scoring could inform our niche analysis.

### NexLev
- **URL:** https://nexlev.io
- **What it does:** Designed specifically for faceless automation channels. Niche research, channel tracking, educational courses. AI title generation (10 variations per idea), thumbnail generation, script outlines with retention optimization and hook suggestions.
- **Pricing:** ~$540/year (~$45/month)
- **Relevance:** High -- specifically targets faceless channels like our manhwa/anime pipeline. Their "retention optimization in script outlines" feature is directly relevant.

---

## 4. YouTube Analytics API Capabilities

### YouTube Analytics API (Targeted Queries)
- **URL:** https://developers.google.com/youtube/analytics
- **Purpose:** Real-time, targeted queries with custom report generation, filtering, and sorting

**Available Metrics:**
| Metric | Description | Access Level |
|--------|-------------|-------------|
| `views` | Total view count | Public (Data API v3) |
| `likes` / `dislikes` | Rating counts | Public (Data API v3) |
| `comments` | Comment count | Public (Data API v3) |
| `estimatedMinutesWatched` | Total watch time in minutes | Owner only (Analytics API) |
| `averageViewDuration` | Average seconds watched | Owner only (Analytics API) |
| `audienceWatchRatio` | Ratio of portion watched vs total views | Owner only (Analytics API) |
| `relativeRetentionPerformance` | Retention vs similar-length videos | Owner only (Analytics API) |
| `subscribersGained` / `subscribersLost` | Subscriber changes | Owner only (Analytics API) |
| `shares` | Share count | Owner only (Analytics API) |
| `cardClickRate` / `cardImpressions` | Info card metrics | Owner only (Analytics API) |
| `annotationClickThroughRate` | Annotation CTR | Owner only (Analytics API) |

### YouTube Reporting API (Bulk Data)
- **URL:** https://developers.google.com/youtube/reporting
- **Purpose:** Bulk data retrieval with scheduled jobs and async downloads

**Additional Metrics via Reporting API:**
| Metric | Description | Notes |
|--------|-------------|-------|
| Impressions | Thumbnail impression count | Reach reports only |
| Click-through rate | % of impressions that led to views | Reach reports only |
| Revenue metrics | Ad revenue, RPM, CPM | Content owners only |
| Subtitle/CC data | Caption usage stats | Reporting API only |
| Playlist retention | Per-playlist audience retention | Reporting API only |

### Key Limitations

1. **Retention data is owner-only.** You can only get `audienceWatchRatio` and `relativeRetentionPerformance` for your own channel. Cannot analyze competitor retention programmatically.
2. **Impressions/CTR require Reporting API.** Not available through the standard Analytics API query interface. Requires setting up scheduled report jobs with async downloads.
3. **Single video per retention query.** Cannot batch retention data -- must query one video at a time with `maxResults` capped at 200.
4. **No thumbnail image analysis.** API provides metrics about thumbnails (impressions, CTR) but cannot analyze the thumbnail image itself.
5. **Public data is limited.** For non-owned channels, you can only access: video metadata (title, description, tags, category), view/like/comment counts, and channel subscriber count.

### What's in YouTube Studio but NOT in any API
- Real-time views (first 48 hours)
- Traffic source breakdown details (specific external sites, specific search terms)
- Audience tab demographics (age, gender, geography breakdown)
- Revenue per video (only aggregated in API)
- "New vs Returning" viewer breakdown
- Content tab's "How viewers find your videos" flow

### Practical Implications for Our Tool
We can programmatically access enough public data for competitor analysis (via Data API v3 + scraping with yt-dlp/scrapetube, which we already do). For our own channel's videos, we can pull retention curves and CTR data to validate our AI predictions. The gap is that we cannot verify our predictions against competitors' retention data -- we can only benchmark against our own.

---

## 5. LLM-Based Review Agent Approaches

### Claude for YouTube Script Analysis

Claude has specific advantages for script review:
- **1M token context window** (on Pro) -- can analyze entire video transcripts with full context
- **Strong instruction following** -- if you say "dark humor but no sarcasm," it actually follows through
- **Nuanced tone analysis** -- better at understanding and matching voice/style than most models
- **Structured output** -- can produce consistent scoring rubrics and detailed breakdowns

**Effective prompt patterns for script review:**
1. **Role assignment:** "You are a YouTube content strategist who has analyzed 10,000+ videos across [niche]"
2. **Context loading:** Feed the transcript + metadata + target audience description
3. **Multi-dimensional scoring:** Request scores across specific dimensions (hook, pacing, storytelling, SEO, etc.)
4. **Comparative analysis:** "Compare this script against the patterns found in top-performing videos in the [niche] niche"
5. **Specific feedback:** "For each issue found, provide the exact timestamp, what's wrong, and a rewritten version"

### Proven Workflows

**3-Step Formula (from Medium/reviewraccoon):**
1. Upload script to Claude
2. Ask Claude to analyze the psychological flow of attention
3. Get breakdown of how elements build or break viewer attention

**Structured Prompt Approach (from DEV Community):**
- Define content type and tone (tutorial, review, educational)
- Specify target audience for detail level adjustment
- Provide examples of successful scripts in the niche as reference
- Request output in YouTube-specific format: hook, intro, main content sections with B-roll notes, transitions, CTAs

**Multi-Agent Architecture (from various GitHub projects):**
- **Content Strategy Agent:** Analyzes trends, identifies topics
- **Script Writer Agent:** Generates/reviews scripts with engagement optimization
- **SEO Optimizer Agent:** Keyword research, title/description optimization
- **Thumbnail Designer Agent:** Visual concept generation
- **Quality Review Agent:** Final pass on all elements

### n8n Workflow Automation Patterns

n8n offers several pre-built YouTube automation workflows that demonstrate agent patterns:

1. **Competitor Analysis Pipeline:** Scrapes competitor channels, analyzes top-performing titles and thumbnails, identifies niche trends, gathers audience sentiment from comments, produces data-driven content ideas
2. **AI Content Strategy:** Uses Apify for data collection + AI Chat Model for trend analysis and interpretation
3. **YouTube Comment Analysis Agent:** Extracts comments and metrics, provides AI-driven audience insight analysis
4. **Metadata Generation:** Extracts transcripts via Apify, creates SEO-optimized descriptions/tags, schedules publishing

### Academic Research: Virality Prediction

**"Understanding Virality: A Rubric based Vision-Language Model Framework for Short-Form Edutainment Evaluation"** (arXiv 2512.21402, Dec 2025)

This paper introduces a data-driven evaluation framework that:
- Uses VLMs to extract unsupervised audiovisual features
- Clusters features into interpretable factors
- Trains a regression-based evaluator to predict engagement
- Achieves Spearman correlation of 0.71 with actual engagement
- Dataset: 11,000 manually curated YouTube Shorts (edutainment/informational)
- Uses SHAP importance analysis for feature-level insights

Key insight: The paper introduces **quantifiable dimensions for subjective attributes** like virality potential and emotional impact -- exactly the kind of rubric we need.

---

## 6. Drama & Storytelling Analysis Frameworks

### Save the Cat Beat Sheet (Blake Snyder)
15 beats that structure any compelling story:

| Beat | YouTube Adaptation |
|------|-------------------|
| Opening Image | First 3 seconds -- visual hook |
| Theme Stated | "In this video you'll learn..." |
| Set-Up | Context/background (first 30 seconds) |
| Catalyst | The inciting question/problem |
| Debate | "But wait, there's a catch..." |
| Break into Two | Diving into the main content |
| B Story | Secondary thread / human element |
| Midpoint | Major revelation or twist |
| Bad Guys Close In | Complications / challenges |
| All Is Lost | Darkest moment / biggest problem |
| Dark Night of the Soul | Emotional low point |
| Break into Three | The solution emerges |
| Finale | Resolution / main takeaway |
| Final Image | CTA + closing thought |

**For manhwa recaps:** Maps directly to chapter structure. The "Catalyst" is the plot trigger, "Midpoint" is the major twist, "All Is Lost" is the cliffhanger setup. Each beat should align with a retention checkpoint.

### Dan Harmon's Story Circle
8 steps for any story:

1. **You** -- Establish the character's world (opening scene)
2. **Need** -- Something is missing/wrong (the hook)
3. **Go** -- Character enters unfamiliar territory (rising action)
4. **Search** -- Facing challenges (complications)
5. **Find** -- Getting what they wanted (revelation)
6. **Take** -- Paying the price (consequences)
7. **Return** -- Coming back changed (resolution)
8. **Change** -- New status quo (conclusion + cliffhanger)

**For manhwa recaps:** This maps perfectly to episode/chapter recap structure. Each recap video should complete one full circle, with the "Change" beat setting up the next video's "You" beat.

### Story Grid (Shawn Coyne)
Breaks analysis into macro and micro levels:
- **Macro:** Genre conventions, obligatory scenes, global value at stake
- **Micro:** Per-scene analysis of action, value shift, turning point
- Key principle: every scene must have a value shift (something changes)

**For manhwa recaps:** Each scene/segment in a recap should shift a value (tension rises, mystery deepens, character reveals truth). Scenes without value shifts are retention killers.

### Retention Curve Patterns & Benchmarks

**Key benchmarks (from Retention Rabbit, 150M+ minutes analyzed):**
- Average YouTube video retains 23.7% of viewers
- 55% of viewers lost by the 60-second mark
- Viewers decide in 8 seconds (consideration window before major drop-off risk)
- 70%+ retention in first 30 seconds = strong hook
- Videos 5-10 minutes hold viewers best (31.5% average retention)
- Strong intros with >65% first-minute retention = 58% higher average view duration

**Retention curve pattern types:**
| Pattern | What It Means | Action |
|---------|---------------|--------|
| Early sharp drop | Weak hook | Rewrite first 15 seconds |
| Steady decline | Normal behavior | Acceptable if gradual |
| Spikes | Skipping or rewatching | Indicates interesting moments |
| Flat sections | Strong engagement | Replicate these patterns |
| Step drops | Lost interest at specific points | Add pattern interrupt before |

**Pattern interrupt timing:**
- Every 60-90 seconds: change visual or auditory stimulus
- 25-35 second mark: critical interrupt needed (camera angle, music drop, sound effect)
- Strategic breaks at predicted drop-off points create reengagement spikes of 15-22%

### Engagement Scoring Formula

**Standard engagement rate:** (Likes + Comments + Shares + New Subscribers) / Views x 100

| Tier | Rate | Significance |
|------|------|-------------|
| Average | 3.87% | Baseline |
| Strong | 4-6% | Above average performance |
| Exceptional | 6%+ | Algorithmic boost territory (can double organic reach within 48 hours) |

---

## 7. Manga/Manhwa/Anime-Specific Tools

### Recap Script Maker
- **URL:** https://recapscriptmaker.com
- **What it does:** Upload manga images, get a detailed story script using Google Gemini AI. Character identification with names, text descriptions, and reference images. Batch processing with context from previous batches for longer sequences.
- **Pricing:** Not publicly listed
- **Relevance:** Directly applicable -- converts manga panels to narration scripts. Uses Gemini, could be adapted to use Claude for potentially better narrative quality.

### MagaRecap
- **URL:** https://magarecap.com
- **What it does:** Creates manhwa recap videos with smart image merging, automatic panel cutting, effect creation, CapCut export integration. Reduces content creation from 5 hours to < 1 hour.
- **Pricing:** Not publicly listed
- **Relevance:** High for video production workflow, but not for review/analysis. This is a creation tool, not a review tool.

### manga-reader (pashpashpash)
- **URL:** https://github.com/pashpashpash/manga-reader
- **What it does:** Generates video recap of any manga volume PDF using GPT-4 Vision for page analysis and ElevenLabs for narration. GPT Vision identifies the most important panels for each segment of the "movie script." Requires chapter-reference.pdf and profile-reference.pdf for character identification.
- **Tech:** GPT-4 Vision API, ElevenLabs, Python
- **Pricing:** Free / open source (API costs apply)
- **Relevance:** Very high -- closest open-source tool to our manhwa recap pipeline. The panel selection approach (GPT Vision picking important panels) is directly reusable. Could be forked and adapted with Claude's vision capabilities.

### RecapManga
- **URL:** https://recapmanga.com
- **What it does:** AI visual script and storyboard generator for manga recaps.
- **Pricing:** Not publicly listed
- **Relevance:** Medium -- storyboard generation is useful for production planning.

### Anime/Manga YouTube SEO Services (Fiverr)
Multiple freelancers offer specialized SEO for anime/manga/manhwa recap channels, including keyword/hashtag research tailored to the niche. Typical pricing: $10-40 per video.
- **Relevance:** Low as a tool, but confirms market demand and shows what SEO optimization looks like for this specific niche.

---

## 8. Building Our Own: Claude Code Agent for Video Review

### Architecture: Multi-Agent Video Review Pipeline

Based on everything researched above, here's the spec for our video review agent system.

#### Input Modes
1. **YouTube URL** -- fetches transcript, metadata, comments via existing bee-content-research infrastructure
2. **Raw script text** -- for pre-publish review
3. **Script + thumbnail image** -- for combined analysis
4. **Batch mode** -- analyze multiple videos for pattern identification

#### Analysis Dimensions (7 Pillars)

**Pillar 1: Hook Analysis (0-100)**
- First 8 seconds: Does it create immediate curiosity? (viewer decision window)
- First 30 seconds: Hook rate benchmark (target >70% implied retention)
- First 60 seconds: Does it survive the 55% drop-off cliff?
- Techniques detected: open loop, shocking statement, question, pattern interrupt, cold open
- Compare against our dataset's top-performing hooks

**Pillar 2: Pacing & Retention Prediction (0-100)**
- Segment timing analysis (are segments 60-90 seconds before a shift?)
- Pattern interrupt placement (is there one at 25-35 seconds? Every 60-90 seconds after?)
- Predicted drop-off points (where would viewers likely leave?)
- Value shifts per segment (Story Grid principle: every segment must change something)
- Dead spots identification (sections with no tension, no revelation, no stakes)
- Optimal video length assessment (5-10 min sweet spot for retention)

**Pillar 3: Storytelling Structure (0-100)**
- Story Circle completion (Harmon's 8 steps)
- Beat sheet alignment (adapted Save the Cat for YouTube)
- Narrative arc strength (setup -> rising action -> climax -> resolution)
- Cliffhanger/hook-forward quality (sets up next video)
- Emotional range (does the script hit multiple emotional notes?)
- Character development handling (for manhwa recaps: are characters made compelling?)

**Pillar 4: Engagement Triggers (0-100)**
- Open loops count and resolution timing
- Curiosity gaps (information asymmetry between narrator and audience)
- Social proof / relatability moments
- Call-to-action placement and strength
- Comment-bait moments (questions, controversial takes, "what would you do?")
- Community engagement hooks (subscribe prompts, poll references)

**Pillar 5: Narration & Voice Quality (0-100)**
- Sentence variety (length, structure, rhythm)
- Active vs passive voice ratio
- Conversational vs robotic tone
- Vocabulary appropriateness for target audience
- Filler word detection
- Read-aloud flow (would this sound natural spoken?)
- For AI narration: TTS-friendliness scoring

**Pillar 6: SEO & Discoverability (0-100)**
- Title effectiveness (length, keyword placement, curiosity, clarity)
- Description optimization (keyword density, links, timestamps)
- Tag relevance and coverage
- Thumbnail concept strength (if image provided)
- Title-thumbnail packaging synergy (Thumblytics concept)
- Search intent alignment

**Pillar 7: Niche-Specific Scoring (0-100)**
- For manhwa/anime: source material accuracy
- Genre convention adherence (true crime, horror, action, romance -- each has different rules)
- Competitive positioning (how does this compare to top performers in the niche?)
- Trend alignment (is the topic/approach trending up or down?)
- Benchmarked against our 4,882 video dataset

#### Scoring System

**Overall Score:** Weighted average of 7 pillars
- Hook: 20% (most impactful on performance)
- Pacing: 20% (directly predicts retention)
- Storytelling: 15%
- Engagement: 15%
- Narration: 10%
- SEO: 10%
- Niche-Specific: 10%

**Score Tiers:**
| Score | Tier | Recommendation |
|-------|------|---------------|
| 90-100 | Publish | Ship it |
| 75-89 | Strong | Minor revisions recommended |
| 60-74 | Needs Work | Significant revisions needed |
| 40-59 | Weak | Major rewrite recommended |
| 0-39 | Reject | Start over or fundamental rethink |

#### Output Format

```
== VIDEO REVIEW REPORT ==

OVERALL SCORE: 78/100 (Strong -- Minor revisions recommended)

PILLAR SCORES:
  Hook:           85/100
  Pacing:         72/100  <-- attention needed
  Storytelling:   80/100
  Engagement:     75/100
  Narration:      82/100
  SEO:            70/100  <-- attention needed
  Niche Fit:      78/100

TOP 3 STRENGTHS:
1. Strong cold open with immediate tension (hook score driven by...)
2. ...
3. ...

TOP 3 ISSUES (with fixes):
1. [PACING] Dead spot at ~3:20-4:10 -- no value shift for 50 seconds
   FIX: Insert revelation about [character]'s true motive here
   REWRITE: "But what nobody expected was..."

2. [SEO] Title missing primary keyword
   CURRENT: "He Became The Strongest After Being Betrayed"
   SUGGESTED: "Betrayed Hero Becomes the Strongest | [Series Name] Recap"

3. ...

RETENTION PREDICTION:
  Hook rate (30s): ~72% (target: >70%)
  Predicted drop-offs: 1:15 (weak transition), 3:20 (dead spot), 6:40 (predictable beat)
  Predicted avg retention: ~28% (above 23.7% average)

ENGAGEMENT PREDICTION:
  Predicted engagement rate: ~4.2% (Strong tier)
  Comment triggers found: 3
  Open loops: 4 (all resolved)

BENCHMARK COMPARISON:
  vs. top 10% in niche: -12 points (Hook: on par, Pacing: below, SEO: below)
  vs. median in niche: +15 points
  Similar high-performing video: [Title] by [Channel] (pattern match: 87%)
```

#### Implementation Plan

**Phase 1: Core Transcript Analysis (Week 1-2)**
- Build on existing bee-content-research infrastructure
- New `analyzers/video_review.py` module
- Claude API integration for multi-dimensional scoring
- Prompt chain: Hook Analyzer -> Pacing Analyzer -> Story Analyzer -> Engagement Analyzer -> Narration Analyzer -> SEO Analyzer
- Input: YouTube URL or raw script text
- Output: JSON report + formatted display

**Phase 2: Benchmark Integration (Week 2-3)**
- Connect to our 4,882-video SQLite database
- Build niche-specific scoring baselines from real data
- Implement comparative analysis ("this script's hook is similar to [top video] which got X views")
- Calibrate scoring weights based on actual performance data

**Phase 3: Pre-Publish Workflow (Week 3-4)**
- Script-only analysis mode (before recording)
- Title/description/tag suggestions with SEO scoring
- Thumbnail concept evaluation (text description analysis, or image analysis via Claude Vision)
- Iterative improvement loop (review -> fix -> re-review)

**Phase 4: Multi-Modal Analysis (Week 4-6)**
- Integrate video-analyzer (byjlw) for frame analysis
- Thumbnail image scoring with Claude Vision
- Audio quality assessment (if applicable)
- Combined visual + transcript analysis

**Phase 5: Automation & MCP Integration (Week 6-8)**
- Add as MCP tool alongside existing bee-content-research tools
- CLI command: `bee-research review <url-or-file>`
- Batch review mode for channel auditing
- Integration with production pipeline (review before publish)

#### Technology Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Transcript extraction | youtube-transcript-api + yt-dlp (existing) | Already in bee-content-research |
| Metadata fetching | scrapetube + YouTube Data API (existing) | Already in bee-content-research |
| LLM analysis | Claude API (Anthropic) | 1M context for full transcripts |
| Frame analysis | video-analyzer (byjlw) or OpenCV + Claude Vision | Phase 4 |
| Thumbnail scoring | Claude Vision API | Phase 3+ |
| Benchmark data | SQLite (existing bee-content-research DB) | 4,882 videos already collected |
| Orchestration | Python + existing service layer | Extend current architecture |
| Output | Rich tables (existing) + JSON + PDF | Extend formatters.py |

#### Key Design Decisions

1. **Claude over GPT for script analysis:** Claude's instruction following is stronger for nuanced creative analysis. The 1M context window means no chunking needed for even long transcripts.

2. **Multi-pass analysis over single-prompt:** Each pillar gets its own focused prompt with specific rubric, rather than one mega-prompt. This produces more consistent scoring and makes it easy to iterate on individual dimensions.

3. **Benchmark-driven scoring:** Scores mean nothing without baselines. Every score should be relative to actual performance data from our dataset. "85/100 on hook" should mean "better than 85% of hooks in our database."

4. **Actionable over analytical:** Every issue flagged must include a concrete fix with rewritten text. "Weak pacing" is useless feedback. "Dead spot at 3:20 -- insert this line here" is useful.

5. **Iterative review loop:** The agent should support re-review after fixes. Track improvements across iterations. Show delta: "Hook score improved from 65 -> 82 after rewrite."

---

## Summary: What Exists vs. What We Need to Build

### Already exists (use, don't build):
- **Thumbnail A/B testing** -- ThumbnailTest, TubeBuddy (requires real viewers)
- **Keyword research at scale** -- vidIQ, TubeBuddy (massive databases)
- **YouTube Analytics API access** -- use for our own channel's retention data
- **Transcript extraction** -- youtube-transcript-api (we already use this)
- **Outlier detection** -- bee-content-research already does this

### Build ourselves:
- **Script/transcript engagement scoring** -- LLM-based, calibrated to our niche data
- **Pre-publish retention prediction** -- based on pacing analysis + pattern interrupt detection
- **Storytelling structure analysis** -- Story Circle / Beat Sheet alignment scoring
- **Niche-specific benchmarking** -- using our 4,882-video dataset
- **Iterative review agent** -- review -> fix -> re-review workflow
- **Title/description SEO scoring** -- specialized for anime/manhwa niche
- **Thumbnail concept analysis** -- Claude Vision for scoring thumbnail ideas

### Worth paying for:
- **TubeBuddy Pro** ($6/month) -- thumbnail A/B testing, retention analyzer on our own videos
- **vidIQ Boost** ($17/month) -- keyword research, trend alerts
- **ThumbnailTest** ($29/month) -- if we're publishing enough to justify live A/B testing

### Total estimated cost of our pipeline:
- Claude API: ~$10-30/month (depending on volume)
- vidIQ or TubeBuddy: ~$6-17/month
- ThumbnailTest (optional): $29/month
- **Total: $16-76/month** vs. $100-400/month for comparable SaaS tools

---

## Sources

### AI-Powered Video Analysis
- [OutlierKit: Best YouTube Analyzer AI Tools](https://outlierkit.com/blog/best-youtube-analyzer-ai-tools)
- [OutlierKit: Best YouTube Video Analyzer Tools](https://outlierkit.com/blog/best-youtube-video-analyzer-tools)
- [ScreenApp Video Analyzer](https://screenapp.io/features/video-analyzer)
- [Memories.ai YouTube Video Analyzer](https://memories.ai/tools/youtube-video-analyzer-ai)
- [Maekersuite YouTube Watchtime Analysis](https://maekersuite.com/use-cases/youtube-watchtime-analysis)
- [Retention Rabbit](https://www.retentionrabbit.com/)
- [Retention Rabbit 2025 Benchmark Report](https://www.retentionrabbit.com/blog/2025-youtube-audience-retention-benchmark-report)

### Open Source Tools
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [video-analyzer (byjlw)](https://github.com/byjlw/video-analyzer)
- [YouTube Video Analyzer Pro (KazKozDev)](https://github.com/KazKozDev/video-analyser)
- [YouTube Video Inspector (emirhansilsupur)](https://github.com/emirhansilsupur/youtube-video-analyzer)
- [AI-Powered Video Analyzer (arashsajjadi)](https://github.com/arashsajjadi/ai-powered-video-analyzer)
- [YouTube Engagement Prediction (avalanchesiqi)](https://github.com/avalanchesiqi/youtube-engagement)
- [YoutubeGPTClaude](https://github.com/agniiva/YoutubeGPTClaude)
- [YouTube Transcript AI Assistant](https://github.com/pawan941394/YouTube-Transcript-AI-Assistant)
- [youtube-automation-agent (darkzOGx)](https://github.com/darkzOGx/youtube-automation-agent)
- [manga-reader (pashpashpash)](https://github.com/pashpashpash/manga-reader)
- [Advanced YouTube SEO Generator](https://github.com/Avinashricky211/Advanced-Youtube-Seo-Generator)

### Paid SaaS Tools
- [vidIQ](https://vidiq.com) | [vidIQ Review 2026](https://www.red11media.com/blog/vidiq-worth-it-2026)
- [TubeBuddy](https://www.tubebuddy.com) | [TubeBuddy Review 2026](https://www.bluebirdrank.com/2026/02/05/tubebuddy-review-guide/)
- [Subscribr](https://subscribr.ai/) | [Subscribr Review](https://daveswift.com/subscribr/)
- [1of10](https://1of10.com/)
- [ThumbnailTest](https://thumbnailtest.com/)
- [Thumblytics](https://thumblytics.com/)
- [Prescene AI](https://www.prescene.ai/)
- [Greenlight Coverage](https://glcoverage.com/)
- [RivetAI](https://rivetai.com/)
- [TubeLab](https://tubelab.net/)
- [NexLev](https://nexlev.io/)
- [Jasper AI](https://www.jasper.ai/tools/youtube-script-writer)
- [vidIQ vs TubeBuddy 2026](https://linodash.com/vidiq-vs-tubebuddy/)
- [OutlierKit Review](https://outlierkit.com/blog/outlierkit-review)
- [NexLev Alternatives](https://tubelab.net/blog/top-5-best-nexlev-alternatives)

### YouTube API
- [YouTube Analytics API Metrics](https://developers.google.com/youtube/analytics/metrics)
- [YouTube Analytics API Channel Reports](https://developers.google.com/youtube/analytics/channel_reports)
- [YouTube Reporting API](https://developers.google.com/youtube/reporting)
- [YouTube Analytics Sample Requests](https://developers.google.com/youtube/analytics/sample-requests)
- [YouTube Analytics API Impressions Issue](https://issuetracker.google.com/issues/254665034)

### LLM-Based Approaches
- [YouTube Scripts with Claude](https://claude-ai.chat/use-cases/youtube-scripts/)
- [Claude AI Script Review Formula (Medium)](https://medium.com/@reviewraccoon/i-spent-6-months-struggling-with-youtube-scripts-until-claude-ai-showed-me-this-3-step-formula-that-67bea8c488c2)
- [Claude AI for YouTube Scripting vs Other LLMs](https://medium.com/@reviewraccoon/the-exact-reason-why-i-prefer-claude-ai-in-youtube-scripting-to-other-llms-7a0a904fc231)
- [Prompting Claude for Short-Form Video Engagement](https://creativeworkflowlab.substack.com/p/how-im-prompting-claude-ai-to-maximize)
- [Building YouTube Scripts with Structured AI Prompts](https://dev.to/huizhudev/building-better-youtube-scripts-a-structured-prompt-for-ai-writing-assistants-3eb6)
- [Building a YouTube Research Agent with Claude Code](https://sider.ai/blog/ai-tools/step-by-step-building-a-youtube-research-agent-with-claude-code)
- [9 Best AI Script Coverage Tools 2026](https://scriptation.com/blog/best-ai-script-coverage-feedback-analysis/)
- [7 Best AI Script Writing Tools 2026](https://dupple.com/learn/best-ai-for-script-writing)

### Storytelling Frameworks
- [Save the Cat Beat Sheet](https://savethecat.com/beat-sheets)
- [Save the Cat Explained (StudioBinder)](https://www.studiobinder.com/blog/save-the-cat-beat-sheet/)
- [Dan Harmon Story Circle (StudioBinder)](https://www.studiobinder.com/blog/dan-harmon-story-circle/)
- [Dan Harmon Story Circle (Katalist)](https://www.katalist.ai/post/dan-harmon-story-circle)
- [Story Grid + Save the Cat (Set Your Muse on Fire)](https://www.setyourmuseonfire.com/blog/save-the-cat-and-story-grid-structure-in-beats)
- [Mastering YouTube Storytelling](https://redsunstudio.co.uk/blog/mastering-youtube-storytelling/)

### Retention & Engagement
- [YouTube Retention Graphs Explained (OpusClip)](https://www.opus.pro/blog/youtube-retention-graphs-explained)
- [Analyze Retention Graph (Retention Rabbit)](https://www.retentionrabbit.com/blog/analyze-youtube-audience-retention-graph-free-tools)
- [Advanced Retention Editing (AIR Media-Tech)](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)
- [Ultimate Guide to YouTube Audience Retention](https://www.retentionrabbit.com/blog/ultimate-guide-youtube-audience-retention)
- [Engagement Rate Calculator (HypeAuditor)](https://hypeauditor.com/free-tools/youtube-engagement-calculator/)

### Academic Research
- [Understanding Virality: Rubric-based VLM Framework (arXiv 2512.21402)](https://arxiv.org/abs/2512.21402)
- [Beyond Views: Measuring and Predicting Engagement (ICWSM '18)](https://arxiv.org/pdf/1709.02541)

### Manga/Anime-Specific
- [Recap Script Maker](https://recapscriptmaker.com/)
- [MagaRecap](https://magarecap.com/)
- [RecapManga](https://recapmanga.com/)
- [manga-reader (GitHub)](https://github.com/pashpashpash/manga-reader)

### Thumbnail Analysis
- [Thumbnail AI](https://thumbnail-ai.app/blog/thumbnail-rater-how-to-automatically-analyze-your-youtube-ctr-potential)
- [TubeBuddy Thumbnail Analyzer](https://www.tubebuddy.com/tools/thumbnail-analyzer/)
- [AI Thumbnail Tools (Banana Thumbnail)](https://blog.bananathumbnail.com/ai-thumbnail-tools/)

### Automation Workflows
- [n8n YouTube Metadata Generation Workflow](https://n8n.io/workflows/3900-automated-youtube-video-scheduling-and-ai-metadata-generation/)
- [n8n YouTube Trend Explorer](https://n8n.io/workflows/5296-ai-youtube-trend-explorer-n8n-automation-workflow-with-geminichatgpt/)
- [n8n YouTube Comment Analysis Agent](https://n8n.io/workflows/2636-extract-insights-and-analyse-youtube-comments-via-ai-agent-chat/)
- [n8n YouTube Content Strategy Automation](https://n8n.io/workflows/10808-automate-youtube-content-strategy-with-ai-apify-and-google-sheets/)
- [AI Agents for YouTubers (Foximusic)](https://www.foximusic.com/ai-agents-for-youtubers-automate-your-channel/)
