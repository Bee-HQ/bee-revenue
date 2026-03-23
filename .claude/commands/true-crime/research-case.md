# Research Case for True Crime Video Production

You are researching a true crime case to produce a comprehensive `case-research.md` file. This file becomes the foundation for screenplay writing, storyboard generation, and video production.

## Interactive Setup

### 1. Case identifier
Ask: "Which case should I research? Give me a name, brief description, or a news article URL to start from."

Accept any of:
- A suspect/victim name (e.g., "Alex Murdaugh", "Chris Watts")
- A case description (e.g., "the Idaho student murders")
- A news article or Wikipedia URL
- A court case number

### 2. Output directory
Ask: "Where should I save the research?"
- Suggest: `bee-content/discovery/true-crime/cases/<case-slug>/case-research.md`
- Create the full directory structure:
  ```
  cases/<case-slug>/
  ├── case-research.md
  ├── footage-sources.md
  ├── footage/
  ├── stock/
  ├── photos/
  └── music/
  ```

## Context Documents

**Read before researching:**

1. **Reference example** — `bee-content/discovery/true-crime/cases/alex-murdaugh/case-research.md`
   - Read this as the gold standard for depth, structure, and level of detail
   - Match the specificity: exact dates, exact dollar amounts, verbatim quotes, direct URLs

2. **Reference footage sources** — `bee-content/discovery/true-crime/cases/alex-murdaugh/footage-sources.md`
   - Read this as the gold standard for the footage-sources document

Keep the case selection dealbreakers (below) in mind throughout research — if you discover early that a case has no real footage or no suspect confrontation, flag it immediately rather than completing the full research.

## Case Selection Criteria

<!-- Inlined from screenplay-storyboard-formula.md Phase 1 -->

### Universal Requirements

Every case must have these regardless of archetype:

| Requirement | Why | Dealbreaker? |
|-------------|-----|-------------|
| 20+ minutes of real footage (any type) | The format needs real audio/video to work — below 60% real content, it becomes a slideshow | Yes |
| Clear victim + clear suspect | Audience needs someone to root for + against | Yes |
| Suspect confronted on camera (interview, interrogation, trial, OR bodycam) | The confrontation IS the video's centerpiece — format doesn't matter, the power shift does | Yes |
| Self-incriminating moment | The money shot — suspect catches themselves on tape/record | Strongly preferred |
| 2+ separate audio sources (911, bodycam, interview, trial) | Creates audio variety and contradiction timeline | Strongly preferred |
| Financial angle ($$ amounts) | Title bait + concrete stakes | Preferred |
| Multiple witnesses with conflicting info | Builds investigation tension | Preferred |
| Property/location with visual interest | Thumbnail + aerial shots | Preferred |

### Case Archetypes

Not all cases look the same. Identify which archetype fits, then use that archetype's footage targets and act adaptations.

#### Archetype A: Bodycam-Domestic (the Thetford model)

The original formula case. A domestic crime with extensive bodycam, a suspect who cooperates on camera, and a progressive investigation leading to body discovery.

| Property | Value |
|----------|-------|
| Primary footage | Bodycam (55%+) |
| Confrontation type | Bodycam face-to-face — detective visits suspect |
| Act 3 centerpiece | Extended bodycam conversation where power shifts in real time |
| Best for | Domestic homicide, missing persons with body recovery, welfare-check-to-murder cases |

#### Archetype B: Trial-Centric (the Murdaugh model)

High-profile case with a televised trial as the primary footage source. Bodycam is supplementary, not dominant.

| Property | Value |
|----------|-------|
| Primary footage | Trial testimony (35-40%) + interrogation clips (10-15%) |
| Confrontation type | Cross-examination — prosecutor dismantles defendant on the stand |
| Act 3 centerpiece | Extended trial testimony/cross-examination with real audio exchanges |
| Act 1 adaptation | Longer setup needed (dynasty, backstory) — may require 15-20% instead of 12% |
| Visual adaptation | Heavier stock B-roll, photos, maps for exposition sections. Stock can reach 15-20% |
| Best for | High-profile trials, family dynasty/corruption cases |

#### Archetype C: Interrogation-Centric (the JCS model)

The interrogation IS the content. A long recorded interview where the suspect's story unravels in real time.

| Property | Value |
|----------|-------|
| Primary footage | Interrogation room footage (40-50%) |
| Confrontation type | Extended interrogation — detective breaks suspect over hours |
| Structural inversion | The confrontation becomes Acts 2-3; investigation is backstory |
| Act 3 centerpiece | The moment the suspect cracks or lawyers up |
| Visual adaptation | Static camera angles need more overlay work (quote cards, behavioral annotation) |
| Best for | Cases with long recorded interrogations, false confessions, behavioral analysis content |

#### Archetype D: Cold Case / Forensic

Non-linear timeline spanning years. No bodycam from the original incident.

| Property | Value |
|----------|-------|
| Primary footage | Mixed — news footage, later-era bodycam/interviews, court proceedings |
| Confrontation type | Arrest + interrogation based on accumulated evidence, OR courtroom testimony |
| Structural adaptation | Act 1 must establish TWO timelines (original crime + reopening) |
| Timeline handling | Use TIMELINE_MARKER heavily — anchor the viewer in which era |
| Visual adaptation | More historical photos, news clippings, heavy narrator reliance |
| Best for | Cold case DNA hits, cases reopened after new witness testimony, serial cases spanning years |

### Footage Mix Targets by Archetype

| Category | A: Bodycam-Domestic | B: Trial-Centric | C: Interrogation | D: Cold Case |
|----------|---------------------|-------------------|-------------------|--------------|
| Primary real footage | 55% (bodycam) | 38% (trial) | 45% (interrogation) | 30% (mixed) |
| Secondary real footage | 3% (interrogation) | 12% (interrogation/bodycam) | 8% (bodycam/911) | 12% (later-era footage) |
| Audio visualizations | 15% | 10% | 10% | 10% |
| Maps & location | 8% | 8% | 5% | 8% |
| Photos/PIP | 5% | 8% | 5% | 12% |
| Stock B-roll | 4% | 12% | 10% | 13% |
| Graphics/cards | 7% | 9% | 14% (behavioral annotations) | 12% |
| **Total real content** | **73%** | **60%** | **63%** | **52%** |

**Critical ratio:** Total real content should target **60%+** for archetypes A-C. Archetype D floor is **50%** — compensate with more frequent real audio integration.

**Cases that WON'T work (any archetype):** Single-source investigations with no audio variety, purely forensic cases with no human drama, cases where the suspect is never confronted on camera.

## Research Process

### Phase 1: Broad search
Search the web extensively for the case. Cast a wide net:
- `"[suspect name] case timeline"`
- `"[suspect name] murder charges verdict"`
- `"[case name] bodycam footage"`
- `"[case name] 911 call"`
- `"[case name] interrogation video"`
- `"[case name] trial footage court tv"`
- `"[suspect name] wikipedia"`
- `"[case name] court documents"`

### Phase 2: Deep fetch
Fetch key pages to extract specific facts:
- Wikipedia article (if exists) — for timeline, characters, outcome
- Major news articles (CNN, ABC, NBC, Fox, AP) — for verified facts and quotes
- Court TV / Law & Crime — for footage availability
- YouTube search — for bodycam, interrogation, trial uploads with view counts
- Local news outlets — for details national media missed

### Phase 3: Footage inventory
This is critical — the video format requires 20+ minutes of real footage. Search specifically for:
- Bodycam footage (police body cameras)
- 911 call audio/recordings
- Interrogation/interview recordings
- Trial footage (Court TV, news networks)
- Surveillance camera footage
- Dash cam footage
- Phone recordings/evidence
- Drone/aerial footage of locations
- Documentary footage (Netflix, Hulu, HBO, Peacock, etc.)

For each piece of footage found, note:
- What it shows
- Approximate duration (if known)
- Where to find it (direct URL preferred)
- Whether it's publicly available or behind a paywall

### Phase 4: Compile

Write the `case-research.md` file following the exact structure below.

### Phase 5: Footage sources document

After writing `case-research.md`, also create `footage-sources.md` in the same directory. For every piece of footage marked **YES** or **Partial** in the inventory, include:
- Direct URL
- yt-dlp download command (for YouTube/news sites): `yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --remux-video mp4 -o "footage/<category>/<description>.mp4" "<url>"`
- Expected file category (`footage/bodycam/`, `footage/trial/`, `footage/interrogation/`, `footage/911-calls/`)
- Notes on trim points if specific moments are needed
- Fair use / copyright notes

Reference the existing example at `bee-content/discovery/true-crime/cases/alex-murdaugh/footage-sources.md` for the expected format and level of detail.

## Output Template

```markdown
# [Case Name] — Deep Research for True Crime Video

**Research Date:** [today's date]
**Case Status:** [e.g., "Convicted, sentenced to life without parole" or "Awaiting trial" or "Under investigation"]

---

## 1. COMPLETE CASE TIMELINE

Chronological account of all significant events. Include:
- Exact dates when known
- Dollar amounts for any financial elements
- Direct quotes from key moments (911 calls, interrogations, trial testimony)
- Locations with specific addresses/property names when available

Start from the earliest relevant backstory and continue through the most recent development.

Use `###` subheadings for major timeline phases (e.g., "### Background", "### The Crime", "### The Investigation", "### The Trial", "### The Verdict").

Separate each event with `---` for readability.

---

## 2. AVAILABLE FOOTAGE INVENTORY

Organize into tables by category. Each table has columns:
| Footage | Available? | Details | Where to Find |

Categories:
### Bodycam Footage
### 911 Calls
### Interrogation/Interview Footage
### Trial Footage
### Surveillance/Other Footage

For each entry:
- **Available?** — **YES**, **Partial**, **NO**, or **Unclear**
- **Details** — what it shows, approximate duration, key moments
- **Where to Find** — direct URLs to news outlets, YouTube, Court TV, etc.

This section is the most important for production viability. Be thorough.

---

## 3. KEY CHARACTERS

Organize into tables by role grouping:

### The [Family/Suspect] Side
| Person | Role |
- Full name, age at time of crime, relationship to suspect/victim

### Victims
| Person | Role |
- Full name, age, cause of death, relationship to case

### Law Enforcement & Prosecution
| Person | Role |
- Detectives, prosecutors, agents — with their specific role in the case

### Defense
| Person | Role |
- Defense attorneys, expert witnesses

### Key Witnesses
| Person | Role |
- What they witnessed or testified about

### Other Key Figures
| Person | Role |
- Anyone else significant (media figures, community members, etc.)

---

## 4. KEY EVIDENCE

Organize by evidence type:

### Physical Evidence
- Murder weapons, forensic findings, DNA, fingerprints

### Digital Evidence
- Phone records, GPS data, social media, surveillance footage
- Include specific timestamps and data points when known

### Forensic Evidence
- Autopsy findings, blood evidence, ballistics

### Testimony
- Key witness statements that moved the case
- Include direct quotes when available

### Financial Evidence (if applicable)
- Amounts, transactions, fraud schemes

---

## 5. MOST COMPELLING NARRATIVE ANGLES

Analyze the case for video production potential:

### Potential Titles
- 3-5 YouTube-optimized title suggestions (hook + mystery + reveal format)
- Follow the pattern: "He [did X] — Then [shocking Y] Surfaced"

### The Hook
- What's the single most gripping moment to open the video with?
- Usually: 911 call, bodycam arrival, or a damning quote

### Key Dramatic Moments
- List 5-8 moments with the highest dramatic impact
- These become the "flash-forward" moments in the cold open trailer

### The Central Irony
- What makes this case narratively powerful?
- Usually: the suspect's own actions/words that betray them

### Potential Act Structure
- Brief outline of how the case maps to a 4-act structure
- Where does the investigation pivot?
- What's the confrontation centerpiece?

---

## 6. SOURCE URLS — ORGANIZED BY TYPE

### Court Documents & Legal Records
- Links to court filings, indictments, sentencing docs

### News Coverage
- Major national outlets (CNN, ABC, NBC, Fox, AP)
- Local outlets (often have the best details)

### Video Sources
- YouTube channels with footage
- Court TV archives
- News network video pages

### Podcasts & Documentaries
- Any long-form coverage

### Other
- Wikipedia, Reddit threads with good aggregation, etc.

---

## 7. QUICK REFERENCE — SENTENCING SUMMARY

| Charge | Verdict | Sentence |
|--------|---------|----------|
| [charge 1] | [guilty/not guilty] | [sentence] |
| ... | ... | ... |

**Total effective sentence:** [summary]

---

## 8. NOTES FOR VIDEO PRODUCTION

### Recommended Archetype
Based on available footage, recommend one of:
- **Bodycam-Domestic** — if extensive bodycam footage drives the narrative
- **Trial-Centric** — if televised trial is the primary footage source
- **Interrogation-Centric** — if a long recorded interrogation is the centerpiece
- **Cold-Case** — if solved years later via new evidence/technology

Explain why this archetype fits.

### Footage Assessment
- Estimated total real footage available (minutes)
- Primary footage type breakdown (bodycam %, trial %, interrogation %, other %)
- Is the 20-minute minimum met? Is the 60% real content target achievable?

### Potential Challenges
- Missing footage categories
- Paywall restrictions on key footage
- Content sensitivity issues
- Legal considerations (ongoing cases, sealed evidence)

### Content Warnings
- Graphic content present in footage
- Sensitive topics requiring disclaimer
```

## Quality Standards

### What makes a good case research file:
- **Dates are specific** — "June 7, 2021" not "mid-2021"
- **Dollar amounts are exact** — "$792,000" not "hundreds of thousands"
- **Quotes are verbatim** — from transcripts, not paraphrased
- **URLs are real** — verify each link works before including it
- **Footage assessment is honest** — clearly distinguish YES/Partial/NO/Unclear
- **Nothing is fabricated** — if you can't verify something, mark it `[UNVERIFIED]` or omit it

### Common pitfalls to avoid:
- Don't invent quotes you haven't found in sources
- Don't assume footage exists — search for it specifically
- Don't confuse footage "played at trial" (may not be independently available) with footage "publicly released"
- Don't include paywalled sources without noting the paywall
- Local news outlets often have details and footage that national outlets miss — always search local

## Post-Research

After writing the file, report:

1. **Viability assessment** — does this case meet the formula's universal requirements?
   - 20+ minutes of real footage? YES/NO/MAYBE
   - Clear victim + suspect? YES/NO
   - Suspect confronted on camera? YES/NO
   - Self-incriminating moment? YES/NO/UNKNOWN
   - 2+ audio sources? YES/NO

2. **Recommended archetype** with reasoning

3. **Footage gaps** — what's missing that would strengthen the video?

4. **Files created** — list `case-research.md`, `footage-sources.md`, and directories created

5. **Next step** — "Review the research, then run `/true-crime:review-case-research` to check viability"
