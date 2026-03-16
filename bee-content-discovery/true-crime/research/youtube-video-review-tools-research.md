# True Crime YouTube Video Review Tools & AI Systems — Comprehensive Research

> **SCOPE NOTICE:** This research is specifically for the **TRUE CRIME documentary narration** genre on YouTube. The tools, frameworks, scoring rubrics, and agent specifications described here are calibrated for crime documentary storytelling — not anime, gaming, commentary, vlogs, or other content genres. Applying these frameworks outside true crime will produce unreliable results.

**Researched:** 2026-03-15
**Context:** This document builds on existing research in the `bee-content-discovery/true-crime/` directory:
- [Competitive Analysis](./true-crime-niche-competitive-analysis.md) — 16 channels, 468 videos
- [Dr Insanity Channel Analysis](./channel-analysis-dr-insanity.md) — 50 videos, title/engagement patterns
- [Screenplay Analysis](./screenplay-analysis-dr-insanity-s6CXNbzKlks.md) — full structural breakdown
- [Narration Style Guide](../channels/dr-insanity/narration-style-guide.md) — 17 transcripts, 721K chars
- [Visual Clip Taxonomy](../channels/dr-insanity/visual-clip-taxonomy.md) — 10 clip categories
- [Content Sourcing Guide](./true-crime-content-sourcing-guide.md) — FOIA, court records, footage sources
- [Non-English Competitors](./non-english-true-crime-competitors-analysis.md) — 70 channels, 5 languages

---

## Table of Contents

1. [AI-Powered Script & Content Analysis Tools](#1-ai-powered-script--content-analysis-tools)
2. [Open Source & Self-Hostable Tools](#2-open-source--self-hostable-tools)
3. [YouTube-Specific Analytics & Optimization Tools](#3-youtube-specific-analytics--optimization-tools)
4. [True Crime Content Generation Platforms](#4-true-crime-content-generation-platforms)
5. [Thumbnail & Title Optimization Tools](#5-thumbnail--title-optimization-tools)
6. [Voice & Audio Analysis Tools](#6-voice--audio-analysis-tools)
7. [True Crime Storytelling Frameworks](#7-true-crime-storytelling-frameworks)
8. [Engagement & Retention Psychology for True Crime](#8-engagement--retention-psychology-for-true-crime)
9. [True Crime Video Review Agent — Full Specification](#9-true-crime-video-review-agent--full-specification)
10. [Tool Comparison Matrix](#10-tool-comparison-matrix)
11. [Recommended Stack](#11-recommended-stack)

---

## 1. AI-Powered Script & Content Analysis Tools

These tools analyze screenplay/script quality across dimensions like pacing, tension, structure, dialogue, and emotional intensity. While built for film/TV, several are directly applicable to true crime YouTube scripts.

### 1.1 Largo.AI — Emotional Intensity & Pacing Analysis

**URL:** https://home.largo.ai
**Type:** SaaS (enterprise-leaning)
**Pricing:** Custom (special rates available for indie filmmakers through From the Heart Productions partnership)

**What it does:**
- Analyzes scripts scene-by-scene for emotional intensity across 8 distinct emotions: joy, trust, surprise, sadness, fear, anger, disgust, and anticipation
- Generates an Emotion Analysis graph showing the shifting dynamics of emotions throughout the story
- Breaks down narrative into essential story sections and assesses rhythm, pacing, and dominant genres
- Provides an Emotional Intensity Score — higher scores correlate with increased viewer engagement
- Offers casting recommendations and financial forecasts with up to 80% accuracy
- Delivers results in ~15 minutes

**True Crime Relevance:** HIGH. The emotion graph is directly useful for mapping tension arcs in true crime scripts. A Dr Insanity-style script should show a specific emotional pattern: fear/surprise peaks at the cold open, sustained tension through investigation, anger/disgust peaks during suspect background reveal, and a sadness/trust resolution. Largo can validate whether a script hits these beats.

**Limitations:** Built for feature films. No YouTube-specific metrics. The casting/financial features are irrelevant to faceless YouTube channels. Pricing is opaque.

---

### 1.2 Prescene — AI Screenplay Coverage

**URL:** https://www.prescene.ai
**Type:** SaaS
**Pricing:** $29 one-time (1 script) | $59/month (3 scripts) | $149/month (10 scripts)

**What it does:**
- Full script coverage in ~5 minutes: story intelligence, character breakdowns, production-ready feedback
- Script chatbot — a conversational agent trained specifically to interact with scripts and answer industry-relevant questions
- Detects brands, trademarks, celebrities, and copyrighted content (useful for legal compliance in true crime)
- Provides cast suggestions and talent recommendations
- Character breakdowns with motivations, arcs, and development tracking

**True Crime Relevance:** MODERATE-HIGH. The script chatbot is interesting — you could upload a true crime screenplay and ask specific questions like "Does the tension drop between minutes 15-20?" or "Is the suspect's introduction ominous enough?" The IP/copyright detection could flag issues with using real names, brands, or copyrighted material in scripts.

**Limitations:** Film/TV-oriented. Doesn't understand YouTube-specific concepts like hooks, retention curves, or mid-roll ad placement.

---

### 1.3 ScriptReader.ai — Scene-by-Scene Breakdown

**URL:** https://scriptreader.ai
**Type:** SaaS
**Pricing:** $9.99 per script (first 3 scenes free)

**What it does:**
- Delivers a 100-page scene-by-scene analysis report
- Grades each scene on dialogue, concept, plot, conflict level
- Identifies pacing issues — flags where transitions feel rushed and suggests where to linger
- AI brainstorm tools: rewrite scenes, explore character psychology, refine dialogue and pacing
- Generates an AI pitch video — a professional video summary of the script
- Compare versions side-by-side (useful for A/B testing script drafts)

**True Crime Relevance:** MODERATE. At $9.99 per script, this is cheap enough to run every true crime screenplay through before production. The scene-by-scene conflict level grading is directly useful — in Dr Insanity's format, conflict should escalate every 60-90 seconds with new information. ScriptReader can flag "dead zones" where the pacing goes flat.

**Limitations:** The 100-page report is probably overkill for a 40-minute YouTube script. No true-crime-specific analysis.

---

### 1.4 Callaia (by Cinelytic) — Premium Script Coverage

**URL:** https://www.callaia.ai
**Type:** SaaS
**Pricing:** $79 (1 script) | $349 (5 scripts) | $699 (10 scripts)

**What it does:**
- Generates coverage reports in under 60 seconds
- Scores: premise, originality, dialogue, structure, logic, tone, conflict, pacing, craft
- Provides loglines, synopses, keywords, runtime estimates, budget estimates
- Recommends release strategies, film comps, and cast suggestions
- Industry-leading script/data protection — no AI training on user scripts

**True Crime Relevance:** MODERATE. The scoring dimensions (conflict, pacing, tone, structure) are relevant. The "logic" score could catch plot holes in the factual narrative. But at $79/script, it's expensive for a YouTube production workflow where you're producing 2-3 scripts per month.

**Limitations:** Film/TV-oriented. Expensive. No YouTube-specific features.

---

### 1.5 Greenlight Coverage — Instant Analysis with Memory

**URL:** https://glcoverage.com
**Type:** SaaS
**Pricing:** $45 first script (free tier available for key insights)

**What it does:**
- Evaluates plot structure, character arcs, dialogue authenticity, pacing
- Creates cast lists and movie comps
- AI Q&A session to ask specific questions about the script
- Rewrite Feature with memory — upload new drafts and the AI remembers previous versions
- Financial forecasting and budget breakdowns
- Processing time: 15-60 minutes depending on tier

**True Crime Relevance:** MODERATE. The rewrite-with-memory feature is genuinely useful for iterating on true crime screenplays. You could upload Draft 1, get feedback, revise, and upload Draft 2 — the AI knows what changed and provides contextual feedback.

---

### 1.6 Script Intelligence — 30-Page Professional Coverage

**URL:** https://www.scriptintelligence.com
**Type:** SaaS
**Pricing:** First 7 pages free, paid plans available

**What it does:**
- 30+ page coverage reports covering synopsis, premise, structure, characters, dialogue, setting, pacing, tone, transitions
- Delivery in 3-4 hours during business hours
- Trained on industry-standard screenplay evaluation criteria
- Scripts not used for AI model training

**True Crime Relevance:** LOW-MODERATE. The 3-4 hour turnaround is slower than competitors. The analysis is thorough but film-industry-focused. The 30-page report length is excessive for YouTube script review.

---

### 1.7 Jumpcut ScriptSense — Claude-Powered Industry Tool

**URL:** https://scriptsense.app
**Type:** Enterprise SaaS (used by 200+ companies)

**What it does:**
- Built on Claude 3 Opus, designed for studios, agencies, and production companies
- Multi-step agentic architecture breaks scripts into core components: plot, character, thematic devices
- Indexes all uploaded scripts into a searchable database
- Can search across thousands of scripts by subgenre, setting, themes, character types, storylines
- Saved 35,000+ hours in script reading across user base
- Acquired by Cinelytic in 2025

**True Crime Relevance:** LOW for individual creators, but the architecture is instructive. The multi-step agentic approach — decomposing a script into plot/character/theme, then analyzing each independently — is exactly the pattern our custom agent should follow. The searchable database concept could be applied to our growing library of true crime screenplays.

---

### 1.8 FilmTailor — Pre-Production AI

**URL:** https://www.filmtailor.ai
**Type:** SaaS

**What it does:**
- Script breakdown in one click
- Generates moodboards for every scene and character
- Detailed costume designs
- Smart scouting for filming locations
- Script writing assistant

**True Crime Relevance:** LOW. The moodboard generation could be interesting for planning B-roll and visual atmosphere, but most true crime visual assembly follows a fixed taxonomy (bodycam, 911 audio vis, maps, photos, B-roll — see our [Visual Clip Taxonomy](../channels/dr-insanity/visual-clip-taxonomy.md)).

---

## 2. Open Source & Self-Hostable Tools

### 2.1 Film_Script_Analysis (Python)

**URL:** https://github.com/AdeboyeML/Film_Script_Analysis
**Language:** Python (Jupyter notebooks)
**License:** Open source

**What it does:**
- Character analysis: dialogue frequency, word count per character
- Scene location analysis
- Emotional and sentiment analysis of the whole film and individual characters
- Character interaction mapping
- Gender distribution analysis

**True Crime Relevance:** MODERATE. The sentiment analysis per character could be adapted to analyze narrator emotional tone across a true crime script. The scene-by-scene emotional tracking is useful for validating tension arcs. Would need modification to handle narrator-driven scripts rather than dialogue-heavy screenplays.

---

### 2.2 Deep Narrative Analysis (DNA)

**URL:** https://github.com/ontoinsights/deep_narrative_analysis
**Language:** Python
**License:** Open source

**What it does:**
- Analyzes narratives in biographical/autobiographical text and news articles
- Detects reporting bias and investigates potential mis/disinformation
- Uses semantic, ontological, and NLP/AI/ML technologies
- Currently focused on news articles

**True Crime Relevance:** MODERATE. The bias detection could be adapted to evaluate whether a true crime script sensationalizes events or misrepresents facts. True crime content walks a fine line between engaging storytelling and ethical representation — this tool could help flag when a script crosses that line.

---

### 2.3 Limbic — Python Emotion Analysis

**URL:** https://github.com/glhuilli/limbic
**Language:** Python
**License:** Open source

**What it does:**
- Lexicon-based emotion model for text analysis
- Detects emotional expressions in text
- Lightweight, pip-installable

**True Crime Relevance:** HIGH for building custom tools. Could be used to generate emotion curves from true crime scripts, mapping emotional intensity paragraph-by-paragraph. Combined with the Dr Insanity narration style guide (which defines specific emotional beats at specific structural points), this could validate whether a script follows the proven emotional pattern.

---

### 2.4 Sentiment Arc Analysis (Python/NLP)

**URL:** Multiple implementations — key paper: https://arxiv.org/html/2511.11857
**Language:** Python (NLTK, VADER, TextBlob, transformers)

**What it does:**
- Three-stage Narrative Analyzer: Plot-Sentiment Breakdown, Structure Learning, Concept Detection
- Generates emotional arcs showing sentiment trajectory through a text
- Classifies stories into six major arc patterns: Rags to Riches, Riches to Rags, Man in a Hole, Icarus, Cinderella, Oedipus
- Smoothing via LOESS or moving average for clean visualization

**True Crime Relevance:** HIGH. A Dr Insanity true crime script should follow a specific arc pattern close to "Man in a Hole" — starts with a normal life (neutral), drops into crime discovery (negative), deepens through investigation (sustained negative), hits bottom at the confrontation/evidence reveal, then rises slightly with arrest/resolution. Building a sentiment arc analyzer calibrated to this expected pattern would flag scripts that deviate from the proven formula.

**Implementation approach:**
```python
# Pseudocode for a true crime sentiment arc validator
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analyze_script_arc(script_text, expected_pattern="man_in_a_hole"):
    # Split into segments (1 segment = ~2 min of narration)
    segments = split_into_segments(script_text, n=20)
    scores = [sia.polarity_scores(seg)['compound'] for seg in segments]
    arc = smooth(scores, method='loess')
    deviation = compare_to_template(arc, expected_pattern)
    return arc, deviation
```

---

### 2.5 ShortGPT — YouTube Automation Framework

**URL:** https://github.com/RayVentura/ShortGPT
**Language:** Python
**License:** Open source

**What it does:**
- Experimental AI framework for YouTube Shorts / TikTok automation
- Automated content generation pipeline
- Text-to-video with AI voiceover
- Designed for short-form content

**True Crime Relevance:** LOW for long-form. The architecture is interesting but designed for short-form, not the 35-50 minute documentaries in our pipeline.

---

### 2.6 YouTube Automation Agent

**URL:** https://github.com/darkzOGx/youtube-automation-agent
**Language:** Node.js
**License:** Open source

**What it does:**
- Fully automated YouTube channel management with specialized AI agents:
  - Content Strategy Agent (trend analysis, content calendar)
  - Script Writer Agent (hooks, storytelling, watch time optimization)
  - Thumbnail Designer Agent (generation, A/B testing, CTR optimization)
  - SEO Optimizer Agent (keywords, titles, descriptions, tags, metadata)
  - Publishing Agent (upload, scheduling, playlist management)
- Works with free Gemini API or OpenAI
- No coding required (npm install and run)

**True Crime Relevance:** MODERATE. The multi-agent architecture is directly relevant to our pipeline. However, the Script Writer Agent is generic — it doesn't understand true crime storytelling conventions (dramatic irony, open loops, progressive revelation). Could serve as a scaffold to build a true-crime-specific agent on top of.

---

### 2.7 Gemini YouTube Automation

**URL:** https://github.com/ChaituRajSagar/gemini-youtube-automation
**Language:** Python
**License:** Open source

**What it does:**
- Autonomous AI pipeline using Gemini LLM
- Content generation, video production, auto-upload to YouTube
- Designed for educational content

**True Crime Relevance:** LOW. Educational content pipeline, but the architecture patterns (LLM → TTS → video assembly → upload) are the same ones needed for true crime.

---

## 3. YouTube-Specific Analytics & Optimization Tools

### 3.1 OutlierKit — Viral Video Analysis

**URL:** https://outlierkit.com
**Type:** SaaS (Chrome extension)
**Pricing:** $9/month

**What it does:**
- Discovers outlier videos (5x-100x above channel average)
- Script analysis: evaluates hook strength, pacing, curiosity loops, and engagement patterns at the sentence level
- Analyzes video openings and generates alternatives optimized for the critical first 15 seconds
- Gives hook strength scores with specific improvement suggestions
- Reveals optimal pacing patterns, ideal segment lengths before pattern interrupts, and B-roll/graphics placement
- Competitor analysis across channels

**True Crime Relevance:** HIGH. This is the most directly useful YouTube tool for true crime. The hook analysis is critical — our data shows Dr Insanity's cold opens follow a strict formula (real audio clip → narrator dramatic irony setup → 3-7 flash-forward clips). OutlierKit can validate whether a competitor's hook outperforms and why. The pacing analysis tells you when viewers expect pattern interrupts, which maps directly to the 60-90 second "new information arrival rate" we documented in the narration style guide.

---

### 3.2 Subscribr — Niche Research & Script Writing

**URL:** https://subscribr.ai
**Type:** SaaS
**Pricing:** Subscription (AppSumo lifetime deal available)

**What it does:**
- Scans thousands of channels to find 2x-10x outlier videos
- Extracts title structure, psychological hook, and thumbnail concept from outliers
- Proprietary Velocity Score reveals rapidly growing channels
- Script writer: turns an idea into a ready-to-film script in under 12 minutes
- Research Assistant: imports from URLs, analyzes YouTube transcripts, converts documents to research notes
- Learns your writing style and produces scripts that sound like you

**True Crime Relevance:** HIGH. The research assistant could ingest our existing Dr Insanity narration style guide and then help generate new scripts in that style. The outlier finder is useful for case discovery — finding which true crime topics are trending. For true crime specifically, Subscribr notes that "the most successful historical crime channels spend 3x more time on research than scripting."

---

### 3.3 vidIQ — Analytics & Trend Detection

**URL:** https://vidiq.com
**Type:** SaaS (free tier available)
**Pricing:** Free | $7.50/month (Pro) | $39/month (Boost)

**What it does:**
- Views Per Hour tracking (real-time performance data)
- Competitor analysis: monitor rival channels' uploads, track title/thumbnail changes, view velocity
- AI trend alerts for emerging topics in your niche
- Content ideas engine based on current trends
- Keyword research and SEO scoring

**True Crime Relevance:** MODERATE. Good for monitoring competitors (the 16 channels in our competitive analysis). The trend alerts could catch breaking cases early — being first to cover a viral case matters in true crime.

---

### 3.4 TubeBuddy — Bulk Optimization & A/B Testing

**URL:** https://www.tubebuddy.com
**Type:** SaaS (Chrome extension)
**Pricing:** Free | $4.50/month (Pro) | $21.50/month (Legend)

**What it does:**
- Keyword research weighted by your specific channel size and niche
- Bulk SEO optimization (update tags/descriptions across multiple videos)
- Retention Analyzer: identifies key moments where viewers drop off
- Thumbnail A/B testing

**True Crime Relevance:** MODERATE. The Retention Analyzer is the most useful feature. It can identify the exact seconds where viewers leave, which tells you whether your open loops are working, whether the sponsor break placement is holding attention, and whether the resolution section is too long.

---

### 3.5 NemoVideo — Agentic Video Analysis

**URL:** https://www.nemovideo.com
**Type:** SaaS
**Pricing:** Subscription tiers available

**What it does:**
- First AI-powered "Pro Video Editing Agent"
- Analyzes viral videos frame-by-frame, second-by-second
- Decomposes moments at the element level: pacing shifts, visual cues, narrative turns, editing decisions
- Translates viral videos into working scripts with pacing, hooks, emotional beats, and conversion moments
- Hunt → Analyze → Recreate workflow: find trends, map the "genome" of viral content, produce blueprints

**True Crime Relevance:** HIGH. The frame-by-frame analysis of viral true crime videos could reverse-engineer exactly what makes Dr Insanity's videos work at the visual editing level — something our narration style guide covers from the script side but doesn't address from the visual rhythm side. The "viral genome" concept aligns with our existing visual clip taxonomy.

---

## 4. True Crime Content Generation Platforms

### 4.1 Revid AI — True Crime Video Generator

**URL:** https://www.revid.ai/tools/ai-true-crime-video-generator
**Type:** SaaS
**Pricing:** From $39/month (2,000 credits)

**What it does:**
- Enter a case description → AI researches facts → generates a suspenseful mini-documentary
- Investigative narrator voice, dark moody visuals
- Automatically adds suspenseful music and sound effects
- Choose between AI-generated video clips or atmospheric moving AI images
- Option to record your own voiceover or upload pre-recorded audio
- Fully editable in Revid's editor
- Most videos generated in a few minutes

**True Crime Relevance:** LOW for our purposes. Revid is designed for short-form true crime content (#CrimeTok, YouTube Shorts). It cannot produce the 35-50 minute documentary-style content that dominates the true crime niche. The output quality isn't comparable to the Dr Insanity standard, and reviews are mixed on quality vs. cost.

---

### 4.2 Faceless.so — True Crime Niche Automation

**URL:** https://faceless.so/niche/true-crime
**Type:** SaaS

**What it does:**
- Automated true crime video creation from script to final render
- Complete video generation in 5-10 minutes
- AI handles all production steps

**True Crime Relevance:** LOW. Same issue as Revid — built for low-effort, short-form content. The quality threshold for competing with Dr Insanity (10M+ views/video) requires real footage, real audio, and carefully crafted narration that these tools can't deliver.

---

### 4.3 Videnly — True Crime AI Video Generator

**URL:** https://videnly.com/examples/true-crime-stories
**Type:** SaaS

**What it does:**
- Beginner-friendly true crime video generation
- Most videos ready in minutes
- Customizable script and visual options

**True Crime Relevance:** LOW. Same limitations as above.

---

**Key Insight on Content Generation Platforms:** None of these tools can produce content at the Dr Insanity quality bar. The 10M+ view standard requires:
1. Real bodycam/911/interrogation footage (45% of visuals, per our clip taxonomy)
2. Carefully researched case narratives with progressive revelation
3. Present-tense narration with dramatic irony (per our style guide)
4. Strategic open loop placement and 60-90 second information arrival rate
5. Professional-quality AI voice with documentary tone

These platforms produce "disposable" content. Our pipeline needs to produce premium content.

---

## 5. Thumbnail & Title Optimization Tools

### 5.1 ThumbnailTest — A/B Testing for YouTube

**URL:** https://thumbnailtest.com
**Type:** SaaS
**Pricing:** $29/month (10 active tests)

**What it does:**
- A/B test up to 10 thumbnails per video (YouTube native only allows 3)
- Real-time CTR analytics with confidence intervals
- Tests on both new and existing videos
- Preview across different devices and YouTube surfaces
- Projected impact on total views

**True Crime Relevance:** HIGH. True crime thumbnails follow specific conventions (dark/moody tones, high-contrast lighting, suspect/victim faces, bold short text). Testing variations of these elements is critical. One user reported going from 15K to 120K views by changing a thumbnail. For true crime specifically, testing variables like:
- Mugshot vs. bodycam still
- Red accent vs. blue accent
- With text overlay vs. without
- Close-up face vs. wide crime scene

---

### 5.2 True Crime Thumbnail Design Principles

Based on research across top-performing true crime channels and design analysis:

**Visual Elements That Work:**
- Moody tones with high contrast
- Bold typography (3-word maximum headline)
- Expressive close-ups of faces (suspect or victim)
- Blood-red accents against dark backgrounds
- Desaturated colors with 80% of the image in shadow
- "Floating elements" that match the story (crime tape, evidence, weapons)

**What Dr Insanity Does:**
- Consistent dark background palette across all thumbnails
- Suspect/victim face as primary visual
- Short, punchy text overlay (often just the key hook phrase from the title)
- No emoji, no borders, no channel branding in the thumbnail
- Creates a "newspaper crime section" aesthetic

**Title Formulas for True Crime** (from our competitive analysis):
1. Discovery Formula: `[Person] [Discovers/Realizes] [Shocking Crime Detail]` — 9.8M+ median
2. Police Investigation: `[Police/Cops] [Find/Discover] [Crime Scene Detail]` — 14.9M+ top
3. Hubris Formula: `[Person] Thinks [They] Can Get Away With [Crime]` — 21M+ top
4. Accidental Formula: `[Person] [Accidentally] [Unintended Crime]` — highest engagement
5. How Police Caught: `How [Police] Captured [Descriptor] [Killer]` — 16.6M average

**Algorithm Context (2026):** YouTube's Gemini AI integration now analyzes videos frame-by-frame. The viral window has compressed to 24-36 hours — strong early signals within the first day are critical. Channel consistency matters more than individual video performance.

---

## 6. Voice & Audio Analysis Tools

### 6.1 ElevenLabs — Documentary Narrator Voices

**URL:** https://elevenlabs.io/voice-library/documentary-narrator-voices
**Type:** SaaS
**Pricing:** Free tier | $5/month (Starter) | $22/month (Creator) | $99/month (Pro)

**What it does:**
- AI voices specifically designed for documentary narration
- Preserves emotional nuance, natural cadence, and clarity
- Granular control: Stability (consistency), Similarity (speaker matching), Style exaggeration (expressiveness)
- "Josh" voice frequently chosen by documentary/motivational YouTube channels
- Long-form narration support with consistent tone

**True Crime Relevance:** CRITICAL. ElevenLabs is the industry standard for faceless true crime channels. The narration style guide specifies: "calm, measured pace — not dramatic," "slight pauses before reveals," "drop pitch slightly for ominous lines," "speed up during investigation montages," "slow down for confrontation scenes." ElevenLabs provides the controls to achieve this. Recommended settings for true crime: Stability 60-75%, Similarity 75-85%, Style 10-30%.

---

### 6.2 Voice Quality Analysis Tools

**ScreenApp Speech Analyzer** (https://screenapp.io/features/speech-analyzer-online)
- Analyzes pace, filler words, clarity
- Free online tool

**JustBuildThings Voice Consistency Checker** (https://justbuildthings.com/ai-audio-analysis/voice-consistency-checker)
- Tracks changes in pitch, volume, pace, energy, clarity, and tone throughout a recording
- Useful for ensuring AI narration maintains consistent quality across a 40-minute video

**Insight7 Voice Quality Metrics** (https://insight7.io)
- Measures pitch, tone, speech rate, clarity in real-time
- Monitors syllable-per-second ratios
- Detects pauses for emphasis

**True Crime Application:** Run the final narration audio through these tools before video assembly to verify:
- Speech rate stays in the 140-160 WPM range (optimal for documentary narration)
- Pitch drops are correctly placed before reveals
- No inconsistent tonal shifts across the 40-minute runtime
- Pauses are properly placed at dramatic moments

---

## 7. True Crime Storytelling Frameworks

### 7.1 The Thriller Arc Framework

Academic framework from genre theory applied to true crime documentaries (source: Tandfonline research paper on cinematic true crime documentary typology, 2024).

**Three-Act Structure for True Crime:**

| Act | % of Runtime | Function | Dr Insanity Application |
|-----|-------------|----------|------------------------|
| **Setup** | 15-25% | Victim intro, inciting incident, first clues | Cold open + first welfare check/911 call |
| **Confrontation** | 50-60% | Investigation deepens, suspect emerges, evidence mounts | Witness interviews, background dig, financial investigation |
| **Resolution** | 15-25% | Confession/arrest, trial, sentencing | Confrontation, body discovery, legal outcome |

---

### 7.2 The Seven-Point Structure (Applied to True Crime)

The 7-Point Story Structure maps emotional turning points within the three acts:

| Beat | Definition | True Crime Application |
|------|-----------|----------------------|
| **Hook** | Opening state that captures attention | Cold open: bodycam audio, dramatic irony, flash-forward montage |
| **Plot Turn 1** | Event that kicks the story into motion | First official report/911 call — the crime enters the system |
| **Pinch Point 1** | External pressure that raises stakes | Second call raises urgency, timeline discrepancies emerge |
| **Midpoint** | Protagonist shifts from reactive to proactive | Detectives shift from welfare check to homicide investigation |
| **Pinch Point 2** | Things get worse; ticking clock | Suspect flees, evidence at risk of disappearing, confession tip arrives |
| **Plot Turn 2** | Key information that enables the climax | The critical evidence: kennel video, daughter's confession, DNA match |
| **Resolution** | The outcome | Arrest, charges, trial verdict, sentencing |

**Dr Insanity's scripts consistently hit all 7 beats.** The Craig Thatford video (s6CXNbzKlks) maps perfectly:
- Hook: Bodycam + "What's that smell?"
- Plot Turn 1: Larry's welfare check call
- Pinch Point 1: Grandson Cody calls — 4 months missing, not 2
- Midpoint: Detective Curtis shifts to homicide investigation
- Pinch Point 2: Dena vanishes, suicide attempt, ticking clock
- Plot Turn 2: Co-worker Andrew calls — "She said she shot him"
- Resolution: Body found, arrest, charges filed

---

### 7.3 The Mystery Box Technique (Applied to True Crime)

Originated from J.J. Abrams' 2007 TED Talk. The core principle: withholding information creates more engagement than revealing it. The *promise* of what's inside the box is more compelling than the contents.

**True Crime Implementation:**

| Mystery Box Technique | How Dr Insanity Uses It |
|-----------------------|------------------------|
| **Central Mystery** | The overarching question: "Who did it?" or "How did they get caught?" — withheld until Act 3-4 |
| **Sub-Boxes** | Each piece of evidence creates a smaller mystery: "What's in the safe?" "Why did she mention the Caribbean?" "What's the smell?" |
| **Timed Reveals** | Each box is opened sequentially, and each answer spawns a new question. New information every 60-90 seconds |
| **False Opens** | The viewer thinks a box is about to open (e.g., officers notice the smell) but it stays closed (they dismiss it as wildlife) — creating agonizing dramatic irony |
| **Final Box** | The body discovery / confession / arrest — the payoff that resolves the central mystery |

**Critical rule:** In true crime, every mystery box MUST eventually open. Unlike fiction (where Lost infamously left boxes unopened), true crime audiences demand closure. The resolution section must address every question planted earlier.

---

### 7.4 Progressive Revelation Pattern

The signature technique of Dr Insanity's narration style. Instead of info-dumping, each witness adds one new piece of information. The truth emerges incrementally through contradictory accounts:

```
Witness 1 (Larry): "Missing for 2 months"
Witness 2 (Cody): "Actually 4 months. She says Mexico"
Witness 3 (Heidi): "No, she told me he's at his mom's"
Witness 4 (Dena): "He's in Mexico with another woman"
Witness 5 (Ex #2): "She's demon possessed"
Witness 6 (Ex #3): "She said she'd kill Craig"
Witness 7 (Daughter): "She's tried to kill me before"
Witness 8 (Co-worker): "She told me she shot him"
Witness 9 (Daughter Leslie): Full confession details
```

Each layer makes the previous one more suspicious. The viewer tracks the inconsistencies actively. This is the primary retention mechanism — viewers stay to see how the next witness's story contradicts Dena's.

---

### 7.5 Victim-Centered vs. Investigation-Centered Approaches

**Investigation-Centered (Dr Insanity's approach):**
- Follows the chronological investigation
- The victim is introduced with warmth but the narrative is driven by the pursuit of truth
- Emphasis on dramatic irony (viewer knows more than investigators)
- Higher engagement metrics — viewers are solving the case alongside detectives

**Victim-Centered (ethical trend in 2025-2026):**
- Centers the victim's life, relationships, and dreams — not just their death
- Treats victims as people, not plot devices
- Growing audience preference for respectful treatment
- Some research suggests channels that focus on victims' lives see 30% higher engagement than those that only describe deaths

**Recommendation for our pipeline:** Blend both approaches. The Dr Insanity formula is investigation-centered (and it works — 10M+ views per video), but the victim introduction section should be expanded. Currently, Dr Insanity's victim intros are 2-3 sentences. Expanding to 30-60 seconds with specific life details, hobbies, relationships, and personality traits would:
1. Increase emotional investment (viewers care more about solving a crime when they care about the victim)
2. Align with ethical content trends
3. Differentiate from competitors who treat victims as plot devices

---

### 7.6 The Dramatic Irony Engine

Dramatic irony is Dr Insanity's most frequently used technique. It appears in every video, often 4+ times. The pattern:

**Formula:** The narrator tells the viewer something that the characters in the story don't know.

**Structural placements:**
1. **Cold Open** — "This officer is unknowingly reacting to the decomposition odor coming from Craig Thatford's hidden body."
2. **First Investigation** — Viewer knows the smell is a body; officers dismiss it as wildlife
3. **Suspect Interview** — Viewer knows Dena is lying; she sounds calm and reasonable
4. **Confrontation** — Roger knows it's a homicide investigation; Dena thinks it's a welfare check
5. **Evidence Search** — Viewer knows the body location before police find it

**Why it works for true crime specifically:** True crime is retrospective storytelling — the narrator already knows the outcome. This makes dramatic irony natural and authentic rather than contrived. In fiction, dramatic irony requires careful setup. In true crime, the facts provide it for free.

---

### 7.7 Open Loop Architecture

Open loops are the primary retention mechanism. From the narration style guide, Dr Insanity maintains at least 2 open loops at all times:

**Loop Types:**
- **Information Promise:** "But that is about to change."
- **Foreshadowing Doom:** "What they don't realize is..."
- **Future Reveal Tease:** "A detail that will soon become central to solving this case."
- **Cliffhanger Before Ad:** "But before we get to that..."

**True Crime Optimal Loop Count by Segment:**

| Segment | Active Loops | Purpose |
|---------|-------------|---------|
| Cold Open | 5-7 | Maximum hooks — flash-forward montage creates multiple questions |
| Setup | 2-3 | Central mystery + 1-2 sub-mysteries |
| Investigation | 3-5 | Each witness opens new loops while closing others |
| Pre-Sponsor | 4+ | Maximum open loops = maximum retention through ad |
| Confrontation | 2-3 | Closing loops rapidly builds momentum |
| Climax | 1-2 | Final loops closing = satisfying payoff |
| Resolution | 0-1 | All loops closed except possibly trial outcome |

---

## 8. Engagement & Retention Psychology for True Crime

### 8.1 Why People Watch True Crime

Research from the British Journal of Psychology (Perchtold-Stefan, 2026) and engagement studies:

| Motivation | % of Viewers | Implication for Content |
|-----------|-------------|----------------------|
| **Curiosity** | 73% | Scripts must create and sustain curiosity gaps |
| **Safe threat experience** | ~60% | Provide fear/tension in a controlled environment (dopamine release) |
| **Preparedness/safety** | ~40% (2.5x more women) | Include practical safety lessons where appropriate |
| **Empathy / moral curiosity** | ~50% | Viewers want to understand both victims AND offenders |
| **Justice seeking** | ~45% | Resolution section must address whether justice was served |

### 8.2 True Crime Retention Data

- True crime viewers are **55% more likely to watch to the end** compared to the average across all content categories
- True crime viewers are **14% more likely to watch past the one-minute mark** on Facebook (likely similar or higher on YouTube)
- Documentary-style production earns **30-50% higher CPMs** than casual true crime commentary
- Expert segments boost retention by **35-40%**, but must not exceed 90 seconds without visual changes
- **Sensationalizing graphic details reduces audience trust by up to 40%**

### 8.3 What True Crime Viewers Specifically Respond To

From competitive analysis of top true crime channels and engagement data:

| Element | Impact on Engagement | Evidence |
|---------|---------------------|----------|
| "Accidentally" in title | +2-3x comment rate | Dr Insanity data: accidental crimes have highest engagement scores |
| Discovery/realization hooks | Highest per-video views | Top 2 channels both use this formula |
| Progressive revelation | Sustained retention | 60-90 second information cadence maintains watch time |
| Dramatic irony | Reduces early drop-off | Viewer investment from second 1 when they "know more" |
| Real audio/footage | Trust signal | 40% real audio ratio (per narration style guide) |
| Sponsor at peak tension | Ad break retention | Placed after major cliffhanger = viewer stays through ad |
| Present tense narration | Immersion | "Officers arrive" > "Officers arrived" — creates urgency |
| Clean, no-emoji titles | CTR optimization | 100% of 468 videos in niche use zero emoji |
| Statement titles > questions | Higher reach | 92% use statements; questions outperform but are underused (opportunity) |
| 35-45 min duration | Optimal watch time + ad revenue | Sweet spot for mid-rolls and retention |

### 8.4 What Kills Retention

| Anti-Pattern | Impact | How to Avoid |
|-------------|--------|-------------|
| Info-dumping | Major drop-off | Progressive revelation — one fact per witness |
| Flat pacing (>90 sec without new info) | Gradual bleed | New information every 60-90 seconds |
| Poor sponsor placement | Viewer leaves during/after ad | Place at maximum tension (35-50% of runtime) |
| Sensationalized gore | Trust loss (-40%) | Let facts speak; restrained narrator tone |
| Long resolution (>3 min) | End-of-video drop | Keep resolution to 2-3 minutes; factual, clean |
| Missing victim humanization | Lower emotional investment | Spend 30-60 sec on victim's life, personality, dreams |
| Chronology confusion | Cognitive load → exit | Primarily chronological with clearly signaled flashbacks |

---

## 9. True Crime Video Review Agent — Full Specification

This is the design specification for a Claude-based agent purpose-built to review and score true crime YouTube video scripts. It draws on all existing research in our true crime pipeline.

### 9.1 Agent Overview

| Property | Value |
|----------|-------|
| **Name** | True Crime Script Reviewer |
| **Model** | Claude Opus (or Sonnet for cost-sensitive runs) |
| **Input** | True crime video screenplay (text) |
| **Output** | Scoring rubric (8 dimensions, 0-100 each) + detailed notes + revision suggestions |
| **Reference Data** | Dr Insanity narration style guide, competitive analysis, visual clip taxonomy |
| **Target User** | Madhu / OpenClaw content pipeline |

### 9.2 System Prompt (Core)

```
You are a True Crime Video Script Reviewer — an expert analyst specialized in
YouTube true crime documentary narration. You review scripts for faceless true
crime channels producing 35-50 minute documentary-style videos.

Your analysis is calibrated against the performance patterns of Dr Insanity
(@DrInsanityCrime), the #1 true crime channel by per-video views (9.87M median,
4.3M subscribers, 50 videos analyzed). You also draw on competitive data from
16 true crime channels (468 videos) and narration DNA analysis from 17 Dr Insanity
transcripts (721K characters).

You score scripts across 8 dimensions on a 0-100 scale. You provide specific,
actionable notes for each dimension. You reference the Dr Insanity formula when
a script deviates from proven patterns, but you also flag genuine innovations
that might outperform the formula.

You are NOT a general screenplay reviewer. You are a true crime specialist. Do
not evaluate scripts using film/TV conventions unless they apply to YouTube true
crime. Do not suggest adding fictional elements, fictional dialogue, or invented
scenes — true crime scripts must be factually accurate.

Tone: Direct, specific, no filler. Give the score, explain why, and tell the
writer exactly what to change. Do not be encouraging for the sake of it.
```

### 9.3 Scoring Rubric — 8 Dimensions

#### Dimension 1: COLD OPEN / HOOK EFFECTIVENESS (0-100)

**What it measures:** Does the first 90 seconds create enough curiosity and emotional investment to prevent the viewer from clicking away?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Cold open uses real audio (911/bodycam), narrator delivers dramatic irony within 15 seconds, 4-7 flash-forward clips create multiple open loops, viewer immediately understands the emotional stakes |
| 70-89 | Strong hook with real audio and dramatic irony, but fewer than 4 open loops, or the stakes aren't immediately clear |
| 50-69 | Hook exists but relies too heavily on narration without real audio, or dramatic irony is weak/missing |
| 30-49 | Generic opening that could belong to any crime video — no specific case hook |
| 0-29 | No hook. Starts with background exposition. Viewer will leave within 15 seconds |

**Reference pattern (from narration style guide):**
1. Real audio clip (most dramatic moment)
2. "This is [name], [age]-year-old [descriptor]." — narrator identification
3. "In just a few seconds, [they] are about to [dramatic event]." — dramatic irony
4. 2-4 more audio clips interleaved with narrator context
5. Transition to story proper

**Checklist:**
- [ ] Opens with real audio (911, bodycam, interrogation)?
- [ ] Narrator identification line within first 30 seconds?
- [ ] Dramatic irony setup ("unknowingly," "about to," "has no idea")?
- [ ] At least 3 flash-forward clips from later in the video?
- [ ] Emotional stakes established (death, betrayal, discovery)?
- [ ] Transition to chronological narrative within 90 seconds?

---

#### Dimension 2: TENSION ARC & PACING (0-100)

**What it measures:** Does the script maintain escalating tension with properly spaced information reveals, matching the proven 60-90 second cadence?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | New information every 60-90 seconds, tension escalates continuously through Acts 2-3, at least 2 open loops active at all times, no flat spots longer than 90 seconds |
| 70-89 | Generally good pacing with 1-2 flat spots. Open loops mostly maintained but occasionally drop to 1 |
| 50-69 | Uneven pacing — some sections move well, others drag. Information arrival rate inconsistent |
| 30-49 | Significant flat spots (>2 minutes without new information). Tension drops in the middle |
| 0-29 | No discernible tension arc. Information presented as a report rather than a story |

**Expected arc pattern (based on Dr Insanity analysis):**
```
Tension
  |
  |    /\
  |   /  \    /\      /\
  |  /    \  /  \    /  \     /\
  | /      \/    \  /    \   /  \    /
  |/              \/      \ /    \  /
  |                        V      \/
  +---------------------------------------------> Time
  Cold  Setup  Invest.  Sponsor  Confront  Climax  Res.
  Open                  Break
```

**Checklist:**
- [ ] New information (audio clip, witness statement, evidence) every 60-90 seconds?
- [ ] At least 2 open loops active at all times during Acts 2-3?
- [ ] Tension escalates (not plateaus) through the investigation section?
- [ ] Sponsor break placed at peak tension (35-50% of runtime)?
- [ ] Post-sponsor pacing accelerates toward climax?
- [ ] Resolution section is 2-3 minutes maximum?
- [ ] No flat spot exceeds 90 seconds?

---

#### Dimension 3: EMOTIONAL IMPACT (0-100)

**What it measures:** Does the script create genuine emotional engagement — empathy for the victim, moral outrage at the perpetrator, relief at justice (or frustration at its absence)?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Victim introduced with warmth and specificity (occupation, personality, relationships). Progressive revelation of suspect's history creates escalating disgust/anger. Dramatic irony creates agonizing tension. Resolution provides emotional closure |
| 70-89 | Good victim humanization and emotional beats, but one element is underdeveloped (suspect too one-dimensional, or resolution too abrupt) |
| 50-69 | Victim is introduced but treated as a plot device. Emotional beats present but surface-level |
| 30-49 | Minimal emotional engagement. Clinical, report-style narration |
| 0-29 | No emotional resonance. Victim unnamed or described only as "the body" |

**Checklist:**
- [ ] Victim introduced with full name, age, occupation, and at least one personal detail?
- [ ] Victim described with warmth ("She adored her dogs," "He built a reputation for ambitious dreams")?
- [ ] Suspect introduced with behavioral red flags and ominous foreshadowing?
- [ ] At least one moment of dramatic irony that creates viewer anguish (e.g., officers walk away from the body)?
- [ ] Contrast/juxtaposition used (e.g., beautiful property vs. hidden body)?
- [ ] "Accidentally" element present if applicable (highest engagement)?
- [ ] Resolution addresses justice/injustice in a way that provides emotional closure?

---

#### Dimension 4: NARRATION QUALITY & TONE (0-100)

**What it measures:** Does the narration match the Dr Insanity documentary-thriller tone — factual reporting balanced with dramatic tension, present tense, third person omniscient, no sensationalism?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Present tense throughout. Third person omniscient. Alternating sentence rhythm (short punch, medium flow, long context). No editorializing — facts and audio speak. Transition phrases from the style guide used naturally. No exclamation marks |
| 70-89 | Mostly correct tone with occasional lapses (slipping into past tense, or one instance of editorializing) |
| 50-69 | Tone inconsistent — switches between present and past tense, or narrator expresses opinions about the suspect rather than letting facts speak |
| 30-49 | Sensationalized. Uses hyperbolic adjectives, exclamation marks, or performative outrage |
| 0-29 | Wrong genre entirely — reads like news reporting, academic paper, or entertainment tabloid |

**Key phrases that should appear (from style guide):**
- "But that is about to change."
- "What [they] don't realize is..."
- "[He/She] appears [visibly shaken / calm / cooperative]"
- "Following this..."
- "But before we get to that..." (pre-sponsor only)
- "With that said, let's get back to..." (post-sponsor only)
- "Needless to say..."

**Key phrases that should NOT appear:**
- Exclamation marks
- "We" including the viewer (viewer is always an observer)
- "In my opinion" or any first-person narrator opinion
- Hyperbolic adjectives ("horrifying," "unbelievable," "shocking" — unless quoting a witness)
- Emoji or informal language

---

#### Dimension 5: FACTUAL ACCURACY SIGNALS (0-100)

**What it measures:** Does the script demonstrate journalistic rigor through source attribution, proper legal language, and factual precision?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Sources attributed ("According to court records," "Neighbors told investigators"). Legal language correct (charges stated precisely). Timeline dates specific. Dollar amounts exact. Case status current. "Remains innocent until proven guilty" for pending cases |
| 70-89 | Generally accurate but missing 1-2 source attributions, or one imprecise legal term |
| 50-69 | Some factual claims without attribution. Legal terminology occasionally wrong |
| 30-49 | Multiple unattributed claims. Speculation presented as fact |
| 0-29 | Significant factual errors or fabricated details |

**Checklist:**
- [ ] Dates and times specific ("At approximately 2:17 a.m. on Sunday")?
- [ ] Dollar amounts precise where available?
- [ ] Charges stated with correct legal terminology?
- [ ] Witness statements attributed to specific named witnesses?
- [ ] "According to..." language used for unverified claims?
- [ ] Case status section reflects current legal status?
- [ ] "Remains innocent until proven guilty" for pre-trial cases?
- [ ] No speculative language presented as established fact?

---

#### Dimension 6: VISUAL STORYTELLING CUES (0-100)

**What it measures:** Does the script include clear visual direction using the clip taxonomy tags, and does the visual rhythm follow the proven pattern?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Every scene tagged with clip category codes. Visual variety across all 10 categories. Bodycam footage comprises ~45% of visual direction. Maps/establishing shots at every new location. Character photos at first introduction. Key quotes rendered as text overlays. B-roll fills narrator-heavy sections |
| 70-89 | Most scenes tagged. Good visual variety but missing one category (e.g., no map shots, or no timeline graphics) |
| 50-69 | Some tagging present but inconsistent. Visual direction vague in multiple sections |
| 30-49 | Minimal visual direction. Script reads as audio-only |
| 0-29 | No visual direction included |

**Expected clip distribution (from visual taxonomy analysis):**

| Category | % of Video | Required? |
|----------|-----------|----------|
| Bodycam footage | ~45% | Critical |
| B-roll (atmospheric, police, court) | ~12% | Required |
| Phone call audio visualization | ~10% | Required |
| Location/map shots | ~8% | Required |
| Text overlays & graphics | ~7% | Required |
| 911 call visualization | ~5% | Required |
| Photos (victim, mugshot, couple) | ~5% | Required |
| Evidence close-ups | ~3% | Optional |
| Interrogation footage | ~2% | Optional |
| Sponsor segment | ~3% | Required |

**Checklist:**
- [ ] Clip taxonomy tags used (`[BODYCAM-WELFARE]`, `[911-INITIAL]`, `[MAP-AERIAL]`, etc.)?
- [ ] At least 45% of visual direction is real footage (bodycam, 911, calls, interrogation)?
- [ ] Every new location has a map/establishing shot?
- [ ] Every character's first appearance has a `[PHOTO-*]` and `[TEXT-LOWERTHIRD]`?
- [ ] Key quotes tagged for `[TEXT-QUOTE]` overlay?
- [ ] B-roll fills narrator-only sections (no "dead air" where visual is unclear)?

---

#### Dimension 7: STRUCTURAL INTEGRITY (0-100)

**What it measures:** Does the script follow the proven 4-act structure, hit all 7 story beats, and properly allocate runtime across sections?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | 4-act structure clearly delineated. All 7 story beats present. Runtime allocation within 5% of targets. Sponsor break at 35-50% of runtime. Cold open 60-90 seconds. Resolution ≤3 minutes |
| 70-89 | Structure mostly correct but one act is over/under its target allocation by >10% |
| 50-69 | Structure recognizable but misallocated — investigation too long, or resolution too detailed |
| 30-49 | Structure unclear. Acts blend together without clear turning points |
| 0-29 | No discernible structure. Information presented linearly without dramatic architecture |

**Target runtime allocation:**

| Section | % of Runtime | Target (45-min video) |
|---------|-------------|----------------------|
| Cold Open | 3-4% | 1:30-2:00 |
| Act 1: Setup + Inciting Incident | 12-18% | 5:30-8:00 |
| Act 2: Investigation | 35-45% | 16:00-20:00 |
| Sponsor Break | 3% | 1:30 |
| Act 3: Confrontation | 20-25% | 9:00-11:00 |
| Act 4: Climax + Resolution | 10-15% | 4:30-7:00 |

---

#### Dimension 8: SEO & PACKAGING (0-100)

**What it measures:** Does the script support strong packaging — title, thumbnail concept, description — optimized for true crime YouTube?

**Scoring criteria:**

| Score Range | Description |
|-------------|-------------|
| 90-100 | Title follows one of the 5 proven formulas. 31-50 characters. No emoji. Statement format. Thumbnail concept described (dark mood, face, short text). Description includes case keywords. 3+ alternative titles provided |
| 70-89 | Title follows a proven formula but is slightly too long (51-70 chars) or thumbnail concept is vague |
| 50-69 | Title is decent but doesn't follow a proven formula, or missing thumbnail concept |
| 30-49 | Title is generic or uses anti-patterns (emoji, brackets, >70 chars) |
| 0-29 | No title provided or title inappropriate for the niche |

**Proven title formulas (from competitive analysis data):**
1. `[Person] [Discovers/Realizes] [Crime Detail]` — 9.8M+ median views
2. `[Police/Cops] [Find/Discover] [Crime Scene]` — 14.9M+ top performer
3. `[Person] Thinks [They] Can Get Away With [Crime]` — 21M+ top performer
4. `[Person] [Accidentally] [Unintended Crime]` — highest engagement rate
5. `How [Police] Captured [Descriptor] [Killer]` — 16.6M average

**Anti-patterns (from competitive data):**
- Emoji: 0% usage across 468 true crime videos
- Questions: only 6% usage (but 28% higher performance when used — untapped opportunity)
- Numbers: -12% performance vs. non-number titles
- Titles >50 chars: -17% performance
- Saturday uploads: -22% vs. Thursday (best day)

---

### 9.4 Agent Workflow

```
INPUT: True crime screenplay text file

STEP 1: STRUCTURAL PARSE
  - Identify cold open, acts, sponsor break, resolution
  - Calculate runtime allocations (est. 150 words/minute for narration)
  - Map the 7 story beats
  - Count open loops per section

STEP 2: NARRATION ANALYSIS
  - Check tense consistency (should be present tense)
  - Check POV (should be third person omniscient)
  - Detect editorializing / opinion statements
  - Check sentence rhythm (short/medium/long alternation)
  - Verify style guide phrases present
  - Flag anti-pattern phrases

STEP 3: EMOTIONAL ARC
  - Segment script into ~20 equal blocks
  - Score emotional intensity per block (using sentiment analysis)
  - Compare arc shape to "man in a hole" template
  - Flag segments that deviate from expected pattern
  - Identify victim humanization quality

STEP 4: TENSION MECHANICS
  - Count open loops per section
  - Verify minimum 2 active at all times during Acts 2-3
  - Measure information arrival rate (new info every 60-90 sec)
  - Identify dramatic irony instances (count and placement)
  - Check sponsor break placement (should be at peak tension)
  - Flag flat spots (>90 seconds without new information)

STEP 5: FACTUAL INTEGRITY
  - Check for source attribution patterns
  - Verify legal terminology
  - Flag speculative statements without "according to" qualifiers
  - Check for "remains innocent until proven guilty" for pending cases

STEP 6: VISUAL DIRECTION
  - Count clip taxonomy tags
  - Calculate visual category distribution
  - Flag sections with no visual direction
  - Verify bodycam footage ≥ 40% of visual direction
  - Check all characters have photo + lower third at first mention

STEP 7: PACKAGING REVIEW
  - Evaluate title against 5 proven formulas
  - Check character count (target 31-50)
  - Evaluate thumbnail concept (if provided)
  - Suggest 3 alternative titles

STEP 8: GENERATE REPORT
  - 8 dimension scores (0-100 each)
  - Composite score (weighted average)
  - Top 3 strengths
  - Top 3 critical issues to fix
  - Specific revision notes per dimension
  - Comparison to Dr Insanity benchmark
```

### 9.5 Score Weighting

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Cold Open / Hook | 20% | First 90 seconds determine whether 10M people watch or 1M |
| Tension Arc & Pacing | 20% | Primary retention driver — keeps viewers through 40 minutes |
| Emotional Impact | 15% | Differentiates 1% like rate from 4% like rate |
| Narration Quality | 15% | Brand consistency — must sound like "our" channel |
| Factual Accuracy | 10% | Credibility and ethical responsibility |
| Visual Storytelling | 5% | Important but secondary to script quality |
| Structural Integrity | 10% | Foundation that enables everything else |
| SEO & Packaging | 5% | Matters for discovery but doesn't drive retention |

**Composite Score Interpretation:**

| Score | Assessment | Action |
|-------|-----------|--------|
| 90-100 | Production-ready | Ship it |
| 80-89 | Strong — minor revisions | Fix specific noted issues, don't restructure |
| 70-79 | Promising — needs work | 1-2 revision passes on weak dimensions |
| 60-69 | Below threshold | Major revision needed before production |
| <60 | Reject | Start over or choose a different case |

### 9.6 Example System Prompt (Full)

```markdown
# True Crime Script Reviewer — System Prompt

## Identity
You are a True Crime Script Reviewer for the OpenClaw content pipeline. You
evaluate YouTube true crime documentary scripts against the standards set by
Dr Insanity (@DrInsanityCrime), the #1 channel by per-video views in the
true crime niche (9.87M median views, 4.3M subscribers).

## Reference Data
Your analysis is calibrated on:
- 16-channel competitive analysis (468 videos, March 2026)
- Dr Insanity narration DNA extracted from 17 transcripts (721K characters)
- Screenplay structural analysis of the Craig Thatford video (s6CXNbzKlks)
- Visual clip taxonomy with 10 categories and production workflow
- 70-channel non-English competitor analysis (1,382 videos, 5 languages)

## Key Benchmarks
- Target video duration: 35-50 minutes (~5,250-7,500 words at 150 WPM)
- Median views for Dr Insanity: 9,872,104
- Like rate: 1.2% (lowest in niche — opportunity to improve)
- Comment rate: 0.11% (lowest — opportunity)
- Upload frequency: 0.6/week (~2-3/month)
- Title: statement format, 31-50 chars, no emoji, no brackets
- Narration: present tense, third person omniscient, 60% narration / 40% real audio

## Scoring Process
For each script submitted, provide:

1. **Dimension Scores** (0-100 each):
   - D1: Cold Open / Hook Effectiveness
   - D2: Tension Arc & Pacing
   - D3: Emotional Impact
   - D4: Narration Quality & Tone
   - D5: Factual Accuracy Signals
   - D6: Visual Storytelling Cues
   - D7: Structural Integrity
   - D8: SEO & Packaging

2. **Composite Score** (weighted):
   D1×0.20 + D2×0.20 + D3×0.15 + D4×0.15 + D5×0.10 + D6×0.05 + D7×0.10 + D8×0.05

3. **Report Sections:**
   - STRENGTHS (top 3 things the script does well)
   - CRITICAL ISSUES (top 3 things that must be fixed)
   - DIMENSION NOTES (specific feedback per dimension with line references)
   - REVISION SUGGESTIONS (concrete changes, not vague advice)
   - TITLE ALTERNATIVES (3 titles following proven formulas)
   - BENCHMARK COMPARISON (how this script compares to Dr Insanity average)

## Rules
- Be specific. "The pacing drops at paragraph 47" not "pacing could be improved"
- Reference the narration style guide when critiquing tone or phrase choices
- Flag every instance where past tense is used in the main narrative thread
- Count open loops and report the count per act
- If the cold open doesn't use real audio, flag it as a critical issue
- If the sponsor break isn't at 35-50% of runtime, flag placement issue
- If victim introduction is <2 sentences, flag for expansion
- Do not suggest fictional additions — all content must be factual
- Do not soften criticism. Say what's wrong and how to fix it.
```

### 9.7 Implementation Options

| Approach | Tool | Cost | Complexity |
|----------|------|------|-----------|
| **Claude API + system prompt** | Claude Opus/Sonnet via API | ~$0.50-$2.00 per review | Low — paste script, get review |
| **Claude Code skill** | `.claude/skills/true-crime-reviewer.md` | Free (uses existing Claude Code sub) | Low — `/review-script` command |
| **Custom Python agent** | Claude API + Python (sentiment analysis, loop counting) | ~$1-3 per review + hosting | Medium — automated scoring with NLP validation |
| **Multi-agent pipeline** | Claude API + Largo.ai + OutlierKit | ~$15-20 per review | High — most comprehensive but expensive |

**Recommended starting approach:** Claude Code skill (`.claude/skills/`). The system prompt above can be placed in a SKILL.md file. When reviewing a script, invoke with `/review-script path/to/screenplay.md`. This costs nothing beyond the existing Claude Code subscription and can be iterated quickly.

**Advanced approach (Phase 2):** Python wrapper that:
1. Parses the script into structural segments
2. Runs VADER/limbic sentiment analysis to generate the emotional arc
3. Counts open loops algorithmically (regex for loop-opening phrases)
4. Measures information arrival rate (new proper nouns, dates, evidence per paragraph)
5. Sends the pre-analyzed data + script to Claude API with the system prompt
6. Outputs a structured JSON report + Markdown summary

---

## 10. Tool Comparison Matrix

### Script Analysis Tools

| Tool | Price | Speed | True Crime Fit | Best For |
|------|-------|-------|---------------|----------|
| **Largo.AI** | Custom | 15 min | High (emotion arcs) | Validating tension/emotion patterns |
| **Prescene** | $29-149/mo | 5 min | Moderate | Quick coverage + script chatbot |
| **ScriptReader.ai** | $9.99 | <1 hr | Moderate | Scene-by-scene conflict grading |
| **Callaia** | $79/script | <1 min | Moderate | Fast scoring across 10 dimensions |
| **Greenlight** | $45+ | 15-60 min | Moderate | Iterative revision with memory |
| **Script Intelligence** | Free trial | 3-4 hrs | Low | Detailed 30-page analysis |
| **Custom Claude Agent** | ~$1/review | ~2 min | **Highest** | True-crime-calibrated scoring |

### YouTube Analytics Tools

| Tool | Price | True Crime Fit | Best For |
|------|-------|---------------|----------|
| **OutlierKit** | $9/mo | High | Hook analysis, pacing patterns, outlier detection |
| **Subscribr** | Subscription | High | Niche research, script generation, outlier finding |
| **vidIQ** | Free-$39/mo | Moderate | Trend alerts, competitor monitoring |
| **TubeBuddy** | Free-$21.50/mo | Moderate | Retention analysis, A/B testing |
| **NemoVideo** | Subscription | High | Frame-by-frame viral video analysis |
| **ThumbnailTest** | $29/mo | High | Thumbnail A/B testing |

### Open Source Tools

| Tool | Language | True Crime Fit | Best For |
|------|----------|---------------|----------|
| **Limbic** | Python | High | Emotion curve generation from scripts |
| **Film_Script_Analysis** | Python | Moderate | Character/scene analysis |
| **Deep Narrative Analysis** | Python | Moderate | Bias detection in narratives |
| **VADER/NLTK** | Python | High | Sentiment arc analysis |
| **youtube-automation-agent** | Node.js | Moderate | Full channel automation scaffold |

---

## 11. Recommended Stack

### Phase 1: Manual Review with AI Assist (Now)

| Function | Tool | Cost |
|----------|------|------|
| Script review | Custom Claude Agent (system prompt above) | ~$1/review |
| Hook optimization | OutlierKit | $9/month |
| Thumbnail testing | ThumbnailTest | $29/month |
| Competitor monitoring | vidIQ (free tier) | Free |
| Narration voice | ElevenLabs (Creator) | $22/month |
| **Total** | | **~$61/month** |

### Phase 2: Semi-Automated Pipeline (3-6 months)

| Function | Tool | Cost |
|----------|------|------|
| Script review agent | Python + Claude API + Limbic | ~$2/review |
| Emotional arc validation | Limbic + VADER (Python) | Free (open source) |
| Hook analysis | OutlierKit | $9/month |
| Pacing validation | Custom Python (information arrival rate) | Free (build it) |
| A/B title testing | YouTube native + ThumbnailTest | $29/month |
| Competitor monitoring | vidIQ Pro | $7.50/month |
| Narration voice | ElevenLabs Pro | $99/month |
| Frame-by-frame analysis | NemoVideo | ~$30/month |
| **Total** | | **~$177/month** |

### Phase 3: Full Automation (6-12 months)

| Function | Tool | Cost |
|----------|------|------|
| End-to-end script review | Multi-agent pipeline (Claude + NLP + Largo) | ~$15/review |
| Automated case discovery | bee-content-research + Subscribr | Built + subscription |
| Script generation + review loop | Claude agent generates draft → reviewer agent scores → iterate until 80+ | ~$5-10/script |
| Voice generation + QA | ElevenLabs + voice consistency checker | $99/month |
| Visual assembly | Remotion/MoviePy pipeline | Free (open source) |
| Auto-optimization | ThumbnailTest + vidIQ + TubeBuddy | ~$60/month |
| **Total** | | **~$250-350/month** |

---

## Sources

### AI Script Analysis Tools
- [Largo.AI](https://home.largo.ai/) — Emotional intensity and pacing analysis for film/TV scripts
- [Prescene](https://www.prescene.ai/) — AI screenplay coverage with script chatbot
- [ScriptReader.ai](https://scriptreader.ai/) — Scene-by-scene AI script breakdown ($9.99)
- [Callaia](https://www.callaia.ai/) — Cinelytic's AI script coverage platform
- [Greenlight Coverage](https://glcoverage.com/) — Instant script analysis with revision memory
- [Script Intelligence](https://www.scriptintelligence.com/) — 30-page professional AI coverage
- [Jumpcut ScriptSense](https://scriptsense.app/) — Claude-powered studio script analysis
- [FilmTailor](https://www.filmtailor.ai/) — Pre-production AI with moodboard generation
- [Scriptation Blog: 9 Best AI Script Coverage Tools 2026](https://scriptation.com/blog/best-ai-script-coverage-feedback-analysis/)

### YouTube Analytics & Optimization
- [OutlierKit](https://outlierkit.com/) — Viral video analysis, hook scoring, pacing patterns
- [Subscribr](https://subscribr.ai/) — Niche research, script generation, outlier detection
- [vidIQ](https://vidiq.com/) — YouTube analytics, trend detection, competitor monitoring
- [TubeBuddy](https://www.tubebuddy.com/) — Retention analysis, A/B testing, bulk optimization
- [NemoVideo](https://www.nemovideo.com/) — Agentic AI video editing and viral video analysis
- [ThumbnailTest](https://thumbnailtest.com/) — YouTube thumbnail A/B testing

### Content Generation
- [Revid AI](https://www.revid.ai/tools/ai-true-crime-video-generator) — True crime video generator (short-form)
- [Faceless.so](https://faceless.so/niche/true-crime) — Automated true crime video creation
- [YouTube Automation Agent (GitHub)](https://github.com/darkzOGx/youtube-automation-agent) — Open source channel management

### Open Source & NLP Tools
- [Film_Script_Analysis (GitHub)](https://github.com/AdeboyeML/Film_Script_Analysis) — Python movie script analysis
- [Deep Narrative Analysis (GitHub)](https://github.com/ontoinsights/deep_narrative_analysis) — Narrative bias detection
- [Limbic (GitHub)](https://github.com/glhuilli/limbic) — Python emotion analysis from text
- [ShortGPT (GitHub)](https://github.com/RayVentura/ShortGPT) — AI YouTube Shorts framework
- [Three Stage Narrative Analysis (arXiv)](https://arxiv.org/html/2511.11857) — Plot-sentiment arc analysis

### Voice & Audio
- [ElevenLabs Documentary Voices](https://elevenlabs.io/voice-library/documentary-narrator-voices) — AI narration voices
- [ScreenApp Speech Analyzer](https://screenapp.io/features/speech-analyzer-online) — Voice quality analysis
- [JustBuildThings Voice Consistency Checker](https://justbuildthings.com/ai-audio-analysis/voice-consistency-checker) — Audio consistency tracking
- [Insight7 Voice Quality Metrics](https://insight7.io/7-voice-quality-metrics-ai-can-detect-in-real-time/) — Real-time voice scoring

### Storytelling Frameworks & Psychology
- [True Crime Documentary Typology (Tandfonline)](https://www.tandfonline.com/doi/full/10.1080/17503280.2024.2425132) — Academic framework for true crime documentary structure
- [Victim-Centered Storytelling Framework](https://truecrimeunheard.com/victim-centered-storytelling-framework/) — Ethical true crime storytelling
- [True Crime Psychology (British Journal of Psychology)](https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bjop.70038) — Why people watch true crime
- [True Crime Engagement Metrics (Jellysmack)](https://blog.jellysmack.com/true-crime-and-mystery-content-outperforms-in-view-time-metrics/) — True crime retention data
- [True Crime YouTube Retention Patterns (Subscribr)](https://subscribr.ai/p/true-crime-youtube-niche-ideas) — Niche-specific engagement research
- [True Crime Thumbnail Research (Tandfonline)](https://www.tandfonline.com/doi/full/10.1080/17512786.2023.2288921) — Visual gateway design for crime content
- [AI Screenplay Coverage with Claude (Medium)](https://medium.com/@cwc.annex/ai-screenplay-coverage-conversations-with-claude-449ceca015f8) — Claude screenplay analysis workflow
- [Jumpcut/Claude Customer Story](https://claude.com/customers/jumpcut) — Studio-scale AI script analysis
- [YouTube Algorithm 2026 (vidIQ)](https://vidiq.com/blog/post/understanding-youtube-algorithm/) — How YouTube ranks content in 2026
- [Mastering True Crime Storytelling (Cassian Creed)](https://www.cassiancreed.com/post/mastering-the-art-of-true-crime-storytelling) — Practical storytelling techniques
- [Writing True Crime (Atmosphere Press)](https://atmospherepress.com/how-to-write-true-crime/) — Narrative structure guide
- [Ken Burns Documentary Structure (MasterClass)](https://www.masterclass.com/articles/ken-burns-shares-tips-for-structuring-a-documentary) — Documentary storytelling principles
