# Dr Insanity-Style Screenplay & Storyboard Formula

> Complete production formula reverse-engineered from 300-frame storyboard analysis, transcript deep-dive, and visual element cataloging. Apply this to any true crime case with bodycam footage.

> **This is a living document.** Every correction, idea, or observation from Madhu should be confirmed and folded back into this formula. The goal is continuous evolution — each video we analyze or produce should make this formula sharper.

---

## Evolution Protocol

**When Madhu gives feedback, corrections, or new ideas:**

1. **Confirm the change** — restate what's being updated and why
2. **Update this formula** — edit the relevant section directly (don't just note it somewhere)
3. **Update the storyboard bible** (`visual-storyboard-bible.md`) if it affects visual elements
4. **Update the video analysis** (`video-analysis-s6CXNbzKlks.md`) if it corrects a prior observation
5. **Log the change** in the changelog below so we can track how the formula evolves

### Changelog

| Date | Change | Source |
|------|--------|--------|
| 2026-03-16 | Initial formula created | 300-frame storyboard analysis of s6CXNbzKlks |
| 2026-03-16 | Added 6 new visual elements: [EVIDENCE-DISPLAY], [BODY-DIAGRAM], [INTERROGATION], [COURTROOM], [DOCUMENT-MOCKUP], [SPLIT-INFO] | Frame-by-frame analysis |
| 2026-03-16 | Color correction: dual accent system (red + teal/cyan) confirmed | Storyboard frame analysis |
| 2026-03-16 | Bodycam % revised upward: 45% → 55% | 300-frame count |
| 2026-03-16 | **Reconciliation:** Act percentages, dramatic irony frequency, and sponsor placement aligned to 17-video style guide analysis. Single-video numbers replaced with ranges. | Sub-agent critique cross-referencing style guide vs formula vs video analysis |
| 2026-03-16 | **Case archetypes:** Removed universal bodycam dealbreaker. Added 4 case archetypes (bodycam-domestic, trial-centric, interrogation-centric, cold-case) with per-type footage mix targets and act adaptations. | Murdaugh case stress test + critique |
| 2026-03-16 | **Open loop hierarchy:** Added anchor/structural/micro loop classification with early-resolution fallback guidance. | Critique analysis |
| 2026-03-16 | **Sponsor optional:** Sponsor break marked as optional throughout (master template, archetype table, section 2.6, production checklist, appendix template). Added no-sponsor transition guidance. | Madhu feedback |
| 2026-03-16 | **New visual elements:** Added [TEXT-CHAT], [SOCIAL-POST], [TIMELINE-SEQUENCE], [EVIDENCE-BOARD], [FLOW-DIAGRAM], [NEWS-MONTAGE] to catalog + bible. | Critique: missing visual elements for text evidence, social media, financial flows, complex relationship webs |
| 2026-03-16 | **Act 1 visual palette expanded:** Progressive escalation rewritten — base palette now includes maps, photos, lower thirds, B-roll, document mockups from the start. Escalation = layering complexity, not withholding element types. | Critique: Act 1 too visually impoverished for exposition-heavy Archetype B/D cases |
| 2026-03-16 | **Audio break rule:** Added 90-second max narrator stretch rule (Section 5.1.1). No narration should run 2+ minutes without a real audio clip. Added to production checklist. | Critique: Murdaugh screenplay had 3.5 min narrator-only stretches |
| 2026-03-16 | **Storyboard-to-assembly pipeline:** Added Phase 6.5 with asset manifest, preflight checklist, naming convention, and guidance on merging storyboard into assembly guide. Added preflight step to production checklist. | Critique: biggest time-waste gap in production pipeline |
| 2026-03-16 | **Transition rebalance:** Glitch capped at 8%, flash at 5%. Added [TR-SMASH], [TR-LCUT], [STILL]. Stillness rule: 3-5 moments per video reserved for maximum emotional weight. | Critique: glitch overuse + no tool for intentional stillness |
| 2026-03-16 | **Color system expanded:** Dual accent → four semantic accents (red=danger, teal=info, warm gold=victim/family, cool blue-grey=procedural). Quote card color now follows content, not format. | Critique: two-color monotony across 50 min |
| 2026-03-16 | **Waveform variation:** Added per-call background variation guide. Most important call drops waveform entirely for full-screen captions. | Critique: waveform stale by 3rd call |
| 2026-03-16 | **Advanced narrative techniques:** Added Section 5.4 — false resolution, visual silence, behavioral analysis, callback structure. | Critique: missing techniques used by JCS, Matt Orchard, Eleanor Neale |
| 2026-03-16 | **Runtime variants:** Added Section 2.1.1 — short form (30-35 min) and long form (55-70 min) variant templates with per-act compression/expansion guidance. | Critique: no guidance for non-50-min cases |
| 2026-03-16 | **Screenplay tags aligned to bible codes.** Replaced all ad-hoc tags in screenplay-v2.md with standard bible visual codes. | Code review suggestion: three vocabularies across three documents |
| 2026-03-16 | **Scalability issues documented.** Added Appendix C with 4 known scale issues (asset gen time, FOIA bottleneck, production velocity, 10-video breakpoints) for future work. | Critique analysis |
| 2026-03-19 | **Storyboard unification.** Assembly guide eliminated. Storyboard is now the single source of truth for all production — CLI, web editor, and services. Phase 6.5 rewritten from "storyboard-to-assembly pipeline" to "storyboard-to-production pipeline". Preflight checklist updated to use `bee-video preflight`. | Storyboard unification implementation |

---

## Phase 1: Case Selection Criteria

### 1.1 Universal Requirements

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

### 1.2 Case Archetypes

Not all cases look the same. Identify which archetype fits, then use that archetype's footage targets and act adaptations.

#### Archetype A: Bodycam-Domestic (the Thetford model)

The original formula case. A domestic crime with extensive bodycam, a suspect who cooperates on camera, and a progressive investigation leading to body discovery.

| Property | Value |
|----------|-------|
| Primary footage | Bodycam (55%+) |
| Confrontation type | Bodycam face-to-face — detective visits suspect |
| Act 3 centerpiece | Extended bodycam conversation where power shifts in real time |
| Best for | Domestic homicide, missing persons with body recovery, welfare-check-to-murder cases |
| Example | Craig Thetford / Dr Insanity s6CXNbzKlks |

#### Archetype B: Trial-Centric (the Murdaugh model)

High-profile case with a televised trial as the primary footage source. Bodycam is supplementary, not dominant. The confrontation is cross-examination, not a bodycam visit.

| Property | Value |
|----------|-------|
| Primary footage | Trial testimony (35-40%) + interrogation clips (10-15%) |
| Confrontation type | Cross-examination — prosecutor dismantles defendant on the stand |
| Act 3 centerpiece | Extended trial testimony/cross-examination with real audio exchanges |
| Act 1 adaptation | Longer setup needed (dynasty, backstory, victim humanization) — may require 15-20% instead of 12% |
| Visual adaptation | Heavier stock B-roll, photos, maps for exposition sections. Stock can reach 15-20% |
| Best for | High-profile trials, cases with extensive court footage, family dynasty/corruption cases |
| Example | Alex Murdaugh |

#### Archetype C: Interrogation-Centric (the JCS model)

The interrogation IS the content. A long recorded interview where the suspect's story unravels in real time. The investigation is revealed through interrogation flashbacks, not a linear timeline.

| Property | Value |
|----------|-------|
| Primary footage | Interrogation room footage (40-50%) |
| Confrontation type | Extended interrogation — detective breaks suspect over hours |
| Structural inversion | The confrontation becomes Acts 2-3; investigation is backstory revealed through interview context |
| Act 3 centerpiece | The moment the suspect cracks or lawyers up |
| Visual adaptation | Static camera angles need more overlay work (quote cards, split-info, behavioral annotation text) |
| Best for | Cases with long recorded interrogations, false confessions, behavioral analysis content |

#### Archetype D: Cold Case / Forensic

Non-linear timeline spanning years. No bodycam from the original incident. Resolution through DNA, financial forensics, or witness testimony years later.

| Property | Value |
|----------|-------|
| Primary footage | Mixed — news footage, later-era bodycam/interviews, court proceedings |
| Confrontation type | Arrest + interrogation based on accumulated evidence, OR courtroom testimony |
| Structural adaptation | Act 1 must establish TWO timelines (original crime + reopening). Time-jump mechanics become critical |
| Timeline handling | Use [TIMELINE-MARKER] heavily — anchor the viewer in which era they're watching |
| Visual adaptation | More historical photos, news clippings, map comparisons (then vs now). Heavy narrator reliance |
| Best for | Cold case DNA hits, cases reopened after new witness testimony, serial cases spanning years |

#### Footage Mix Targets by Archetype

> Midpoint values for each archetype sum to ~100%. When one category goes high, pull another low to compensate.

| Category | A: Bodycam-Domestic | B: Trial-Centric | C: Interrogation | D: Cold Case |
|----------|---------------------|-------------------|-------------------|--------------|
| Primary real footage | 55% (bodycam) | 38% (trial) | 45% (interrogation) | 30% (mixed) |
| Secondary real footage | 3% (interrogation) | 12% (interrogation/bodycam) | 8% (bodycam/911) | 12% (later-era footage) |
| Audio visualizations | 15% | 10% | 10% | 10% |
| Maps & location | 8% | 8% | 5% | 8% |
| Photos/PIP | 5% | 8% | 5% | 12% |
| Stock B-roll | 4% | 12% | 10% | 13% |
| Graphics/cards | 7% | 9% | 14% (behavioral annotations) | 12% |
| Sponsor (if applicable) | 0-3% | 0-3% | 0-3% | 0-3% |
| **Total** | **100%** | **100%** | **100%** | **100%** |
| **Real content** | **73%** | **60%** | **63%** | **52%** |

**Critical ratio:** Total real content (primary + secondary + audio viz) should target **60%+** for archetypes A-C. Archetype D (cold case) is the exception — real footage from decades-old cases is limited. For Archetype D, the floor is **50%**, but compensate with more frequent real audio integration (narrator should never go more than 60 seconds without a real audio clip or quote).

**Cases that WON'T work (any archetype):** Single-source investigations with no audio variety, purely forensic cases with no human drama, cases where the suspect is never confronted on camera in any format.

---

## Phase 2: The Screenplay Structure

### 2.1 Master Template (45-55 minutes)

> **Note:** These are target ranges derived from analysis of 17 Dr Insanity videos, not fixed values. Adjust within the ranges based on case material and archetype.

```
TRAILER ──→ OPENING ──→ ACT 1 ──→ ACT 2 ──→ [SPONSOR] ──→ ACT 3 ──→ ACT 4
(1-2 min)   (0:30)    (6-12 min) (16-22 min) (0-1:30)    (10-15 min) (5-10 min)
  3%          1%       15-25%      35-45%       0-3%        20-30%      5-10%
```

**Act sizing guidance:**
- **Act 1 (Setup):** 15-25%. Use the low end (15%) when bodycam delivers fast and victim is already known. Use the high end (25%) when backstory/dynasty context is needed (Archetype B/D) or when victim humanization requires more time.
- **Act 2 (Investigation):** 35-45%, target 40%. This is always the longest act. Compress only if the case has fewer than 6 investigation beats.
- **Act 3 (Confrontation):** 20-30%. Scales with footage quality — a 5-minute unbroken bodycam confrontation needs less narrator padding than a trial cross-examination built from clips.
- **Act 4 (Resolution):** 5-10%. Don't rush the legal outcome — the resolution is where viewers decide if the video was "worth it." Cases with full confessions or dramatic courtroom moments need the high end.

### 2.1.1 Runtime Variants

The master template targets 45-55 minutes. When a case has more or less material, use these guidelines:

#### Short Form (30-35 minutes)

For cases with limited footage or a tight narrative arc.

| What changes | How |
|-------------|-----|
| Trailer | Trim to 45-60 seconds, 3-5 clips |
| Act 1 | Compress to 15%. Cut backstory to 2-3 narrator paragraphs. No dynasty/history deep-dive |
| Act 2 | Compress to 35%. 4-5 investigation beats instead of 6-8. Cut the weakest witnesses |
| Act 3 | Stays at 25-30%. The confrontation is never cut — it's the reason people watch |
| Act 4 | Stays at 5-10%. Resolution still needs room to breathe |
| Reveals target | 20+ (down from 35+) |
| Open loops | 1 anchor + 1 structural + micro. Max 3 active at any time |
| Sponsor | Push to 55-65% window (later in a short video = more retention through the ad) |

**What to cut first:** Backstory exposition, the weakest investigation beat, financial detail deep-dives, background witnesses who corroborate but don't escalate.

**What to never cut:** The trailer, the victim humanization, the confrontation centerpiece, the verdict/resolution.

#### Long Form (55-70 minutes)

For mega-cases with extensive footage, complex timelines, or multiple victims.

| What changes | How |
|-------------|-----|
| Trailer | Can extend to 2-2:30 minutes for complex cases (Murdaugh model) |
| Act 1 | Can expand to 25%. Room for full dynasty/backstory, multiple victim introductions |
| Act 2 | Can expand to 45%. 8-10 investigation beats. Add financial deep-dives, parallel timelines |
| Act 3 | Can expand to 30%. Extended cross-examination, multiple confrontation scenes |
| Act 4 | Can expand to 10%. Room for aftermath, related deaths, appeal status |
| Reveals target | 45+ |
| Open loops | 1 anchor + 2-3 structural + micro. Structural loops can run longer (20-30 min) |
| Sponsor | Place at 40-50% window (earlier placement since the back half is longer) |

**Risk at 60+ minutes:** The 30-minute wall hits harder. Place a Level 3 reveal (bombshell) at exactly the 30-minute mark to catch wavering viewers. Consider a mid-Act-2 "mini-cliffhanger" even without a sponsor — a narrator beat of silence, a [TR-FADE], then resume.

**Risk at 70+ minutes:** Viewer fatigue. If you're above 65 minutes, seriously consider splitting into Part 1 and Part 2 with a natural cliffhanger break at the midpoint.

### 2.2 The Trailer (0:00 – 1:20)

**Purpose:** Movie trailer. Maximum open loops in 80 seconds.

**Formula:** 5-7 audio clips, rapid-fire, no context.

Pick clips that:
1. Raise a question without answering it
2. Contain emotional peaks (anger, fear, revelation)
3. Come from different sources (bodycam, 911, phone call, interrogation)

**Clip selection order:**
```
1. The sensory hook     — "What's that smell?" (bodycam)
2. The victim context   — 911 caller describing the disappearance
3. The narrator tease   — dramatic irony line hinting at what's coming
4. The witness bombshell — ex-husband/friend: "She's tried to kill me before"
5. The suspect voice    — Dena's calm lie on the phone (contrast with #4)
6. The misdirect        — "You might start looking in the Caribbean"
7. The confession tease — "She said she shot him" (co-worker tip)
```

**Visual treatment:**
```
VISUAL: Rapid-cut bodycam clips matching each audio clip
TRANSITION: [TR-GLITCH] or [TR-FLASH] between EVERY clip
COLOR: Darker than main video — extra desaturation, extra vignette
MOTION: Ken Burns zoom on any static shots
TEXT: Key narrator phrases appear as animated text overlays
MUSIC: Loudest here — cinematic, percussion-driven hits
```

**Rule:** Each clip is 3-8 seconds. No context given. No narrator bridges. Pure montage.

### 2.3 Opening Sequence (1:20 – 1:50)

Five beats, always in this order:

| Beat | Element | Duration | Purpose |
|------|---------|----------|---------|
| 1 | [BRAND-STING] | 2-3 sec | Channel identity |
| 2 | [DISCLAIMER] | 3-4 sec | Credibility + legal protection |
| 3 | [MAP-FLAT] wide aerial | 3-5 sec | WHERE — geographic context |
| 4 | [MAP-PULSE] + [PIP-SINGLE] victim | 5-8 sec | WHO + WHERE — victim at location |
| 5 | [WAVEFORM-AERIAL] + [CAPTION-ANIMATED] | Flows into Act 1 | WHAT — 911 call begins |

**Flow:** brand → credibility → where → who+where → what happened

### 2.4 Act 1: Setup — 15-25% of video

**Goal:** Establish victim, location, inciting incident (the 911 call).

**Beat sheet:**
```
BEAT 1: 911 call plays over [WAVEFORM-AERIAL]
        → Narrator contextualizes: who is calling, why
        → [PIP-DUAL] caller + victim photos over [MAP-3D]

BEAT 2: Officers dispatched → bodycam begins
        → Night/dark bodycam — arriving at property
        → [MAP-TACTICAL] showing the route / property in red roads

BEAT 3: First investigation — something is wrong
        → Bodycam exploration of property
        → The SENSORY DETAIL (smell, mess, locked door)
        → Narrator dramatic irony: "What they don't realize is..."

BEAT 4: Officers leave — WRONG CONCLUSION
        → They dismiss the evidence
        → Open loop: "But that is about to change"
        → [TIMELINE-MARKER] time jump to next event
```

**Key technique:** Officers make a mistake. The audience already knows from the trailer that something terrible happened. Dramatic irony begins here and NEVER stops.

### 2.5 Act 2: Investigation — 35-45% of video

**Goal:** Build the case through progressive revelation. Each witness adds ONE piece.

**Structure:** 6-8 investigation beats, each following this mini-formula:

```
INVESTIGATION BEAT FORMULA:
1. Narrator bridge (1-2 sentences setting up next source)
2. New source introduced → [PIP-SINGLE] or [PIP-DUAL] + [LOWER-THIRD]
3. Audio plays (911 call / phone recording / bodycam conversation)
4. Narrator contextualizes what was just heard
5. NEW INFORMATION drops — contradiction, escalation, or reveal
6. Narrator plants dramatic irony or opens a new loop
```

**Beat progression (each beat MUST escalate):**

| Beat | Source | New Info | Escalation |
|------|--------|----------|------------|
| 1 | Second 911 call (relative) | Timeline doesn't match first call | Contradiction introduced |
| 2 | Neighbor canvass (bodycam) | Haven't seen victim in months | Corroboration of disappearance |
| 3 | Another neighbor/friend | Suspect told a DIFFERENT story | Suspect's lies multiply |
| 4 | Suspect calls police | Calm, reasonable explanation | Villain sounds innocent (dramatic irony) |
| 5 | Ex-husband/family #1 | History of violence | Character assassination begins |
| 6 | Ex-husband/family #2 | Death threats, prior incidents | Pattern established |
| 7 | Daughter/close family | "She's tried to kill before" | Escalation to attempted murder |
| 8 | Financial analysis | Money missing, accounts drained | Motive revealed |

**Visual escalation across Act 2:**
- Beats 1-3: Bodycam + basic [PIP-SINGLE] + [MAP-FLAT]
- Beats 4-5: [DESKTOP-PHOTOS] + [POLICE-DB] + [WAVEFORM-AERIAL]
- Beats 6-8: [PIP-DUAL] + [DOCUMENT-MOCKUP] + [FINANCIAL-CARD]

**Pacing rule:** New information every 60-90 seconds. If a section runs 2+ minutes without a reveal, cut it or add narrator dramatic irony.

**Open loop management:** At any point during Acts 2-3, the audience should have 2-4 unanswered questions. Not all loops are equal — use this hierarchy:

**Anchor loop (1):** The central mystery that carries the entire video. "Where is the body?" or "Will they be convicted?" Opens at 0:00, resolves in the final 10% of runtime. If this resolves early, the video's engine dies — see fallback below.

**Structural loops (1-2):** Major sub-mysteries that sustain 15-30 minute stretches. "What's on the locked phone?" or "What happened to the money?" Open in Act 1-2, resolve in Act 3-4.

**Micro loops (2-3):** Small questions that resolve within 2-5 minutes. "What will this witness say?" or "Will the alibi hold up?" These keep individual investigation beats moving.

**Rules:**
- Never close two structural loops within 3 minutes of each other — creates a false ending where viewers feel the story is "done" and click away
- When you close a structural loop, open a new micro loop within 60 seconds
- When the anchor loop resolves, you have 5-8 minutes of runway before viewers leave — use it for resolution, not new mysteries

**Early resolution fallback:** If the anchor loop resolves before the final 10% (body found early, confession mid-video), immediately promote a structural loop to anchor status. Common replacements: "Will they confess?" → "Will they be convicted?" → "What's the full scope of their crimes?" The Murdaugh screenplay does this naturally — the murder mystery resolves through the kennel video, but the anchor shifts to "Will the jury convict?"

### 2.6 Sponsor Break (optional) — 0-3% of video

**The sponsor is optional.** Early videos may have no sponsor. When you do have one, the placement and execution matter — a badly placed ad kills retention. When there's no sponsor, Acts 2 and 3 flow directly into each other with a narrator bridge or a [TR-FADE] beat.

**When you have a sponsor:**

**Placement rule:** Immediately after the single highest-tension moment in the video so far, targeting the **40-65% window** of runtime. The narrative beat matters more than the percentage — find the biggest bomb and sit the sponsor right on top of it.

> **Range from 17-video analysis:** Dr Insanity places sponsors between 35-68% of runtime. The variance is because the confrontation scene runs different lengths. Don't force the sponsor to a fixed minute mark — let the narrative determine it.

**The cliffhanger formula:**
```
BEAT BEFORE SPONSOR:
→ Drop the biggest bomb of the investigation
→ Narrator: "But before we get to that..."
→ [TR-HARD] cut to sponsor

SPONSOR:
→ Thematic bridge to product (crime about money → banking app)
→ Warm, bright footage — complete visual departure
→ 60-90 seconds
→ Keep [LETTERBOX] bars

RETURN FROM SPONSOR:
→ "With that said, let's get back to [character]..."
→ Re-hook with the open loop: "...who is about to hear something that changes everything"
→ [TR-HARD] cut back to primary footage
```

**When there's no sponsor:**

Use the same narrative beat (biggest bomb of the investigation) as the Act 2 → Act 3 transition. The cliffhanger still works — it just resolves immediately instead of after an ad:

```
→ Drop the biggest bomb of the investigation
→ Brief narrator beat or [TR-FADE] to black (1-2 seconds of breathing room)
→ Resume into Act 3
```

The "But before we get to that..." / "With that said..." phrases are sponsor-specific — don't use them without a sponsor. Instead, use a direct transition: "And that is exactly what happens next." or a simple [TR-FADE] beat.

### 2.7 Act 3: Confrontation — 20-30% of video

**Goal:** Face-to-face with the suspect. This is the video's centerpiece.

**Structure:**

```
CONFRONTATION BEAT 1: Arrival
→ Bodycam — driving to suspect's location
→ [MAP-FLAT] or [MAP-TACTICAL] re-establishing the property
→ Narrator: sets up what investigator knows vs. what suspect thinks

CONFRONTATION BEAT 2: The Interview
→ Extended bodycam conversation (3-5 minutes of real footage)
→ [CAPTION-ANIMATED] throughout — essential for bodycam audio quality
→ [LOWER-THIRD] for suspect identification
→ Suspect tells their story — sounds reasonable on surface
→ [QUOTE-CARD] for the key statements (teal/blue accent)

CONFRONTATION BEAT 3: The Cracks
→ Investigator presses on contradictions
→ Bodycam captures micro-reactions
→ Evidence visible in frame naturally (bleach bottle, mess, evidence in situ)
→ Narrator: "What Dena doesn't realize is..."

CONFRONTATION BEAT 4: The Power Shift
→ Investigator reveals they know more than suspect thought
→ [TR-GLITCH] before the reveal line
→ [QUOTE-CARD] for the reveal statement
→ Suspect's demeanor changes — bodycam captures it

CONFRONTATION BEAT 5: The Self-Incrimination
→ Suspect says something that accidentally reveals guilt
→ [TR-FLASH] or [TR-GLITCH] to mark the moment
→ [QUOTE-CARD] with the exact words
→ Narrator: "Whether she realizes what she just said remains to be seen"
```

**Visual elements in Act 3:**
- Bodycam dominates (70%+ of this act)
- [QUOTE-CARD] with teal glow for key statements
- [SPLIT-INFO] for presenting new facts alongside footage
- [MAP-PULSE] when re-establishing body location
- Evidence shown through bodycam naturally — the footage IS the evidence

### 2.8 Act 4: Climax & Resolution — 5-10% of video

**Goal:** Everything converges. Body found. Suspect arrested. Case resolved.

**Structure:**

```
CLIMAX BEAT 1: Escalation (40:00-42:00)
→ Suspect's behavior changes (disappears, flees, attempts self-harm)
→ [TIMELINE-MARKER] for each escalation
→ [WAVEFORM-AERIAL] for tip calls
→ Narrator creates URGENCY: "Time is running out"

CLIMAX BEAT 2: The Tip (42:00-44:00)
→ Someone calls with the critical information
→ [WAVEFORM-AERIAL] + [PIP-SINGLE] for the tipster
→ The confession-by-proxy: "She told me she shot him"
→ [TR-GLITCH] before the bombshell line
→ [QUOTE-CARD] with the exact words

CLIMAX BEAT 3: The Search (44:00-47:00)
→ Search warrant executed — bodycam tactical entry
→ [EVIDENCE-DISPLAY] — composed evidence items on bokeh bg
→ [EVIDENCE-CLOSEUP] with red highlights
→ [FINANCIAL-CARD] for safe contents / money discrepancy
→ Building toward body discovery

CLIMAX BEAT 4: Body Found (47:00-48:30)
→ The payoff for the master open loop
→ [CENSOR-BLUR] for graphic content
→ [MAP-PULSE] confirming exact location
→ [BODY-DIAGRAM] showing cause of death / injuries
→ Narrator delivers the facts plainly — no embellishment needed
→ [TR-FADE] to black — moment of silence

RESOLUTION BEAT 5: Arrest + Legal (48:30-50:00)
→ [INTERROGATION] footage — suspect in grey room, lawyers up
→ [COURTROOM] footage — judge, proceedings
→ [MUGSHOT-CARD] — split screen: mugshot left, RED charges right
→ [TIMELINE-MARKER] — current case status
→ Narrator epilogue: 2-3 sentences on what happened next
→ Final [TR-FADE] to black → end card
```

**Visual escalation in Act 4:**
This is where the most sophisticated visual elements appear:
- [EVIDENCE-DISPLAY] (composed product-photography style)
- [BODY-DIAGRAM] (forensic illustration)
- [INTERROGATION] (new footage source)
- [COURTROOM] (new footage source)
- [MUGSHOT-CARD] (final resolution graphic)

The progressive escalation means viewers see NEW visual elements for the first time in the climax — keeping the visual language fresh even 45 minutes in.

---

## Phase 3: The Narrator Voice

### 3.1 Tense

**95% present tense.** Always.

| Wrong | Right |
|-------|-------|
| "Officers arrived at the property" | "Officers arrive at the property" |
| "Dena had told the deputy..." | "Dena tells the deputy..." |
| "The search warrant was executed" | "The search warrant is executed" |

**Exception:** Background/backstory uses past tense: "She had already been married three times."

### 3.2 Sentence Rhythm

The pattern: medium → medium → medium → long → **SHORT PUNCH** → long

```
NARRATOR:
"Detective Curtis decides to contact Dena's ex-husbands."     [medium - 8 words]
"What he discovers is deeply troubling."                       [medium - 7 words]
"Scott, Dena's second husband, describes years of erratic      [long - 22 words]
behavior, binge drinking, and violent outbursts."
"He says she was, quote, 'demon possessed.'"                   [medium - 9 words]
"Then he drops a bombshell."                                   [SHORT PUNCH - 5 words]
"According to Scott, Dena once told him: 'If I could kill      [long - 18 words]
Craig and get away with it, I'd do it.'"
```

The short punches are what make the narration addictive. They land like gut punches after buildup.

### 3.3 Signature Phrases (Use These)

| Phrase | When to Use |
|--------|------------|
| "But that is about to change." | Transition — current theory about to be demolished |
| "What they don't realize is..." | Dramatic irony — narrator reveals what characters can't see |
| "Unknowingly, [character] is [doing something near the truth]" | Irony — character literally standing on evidence |
| "Following this..." | Scene transition to next beat |
| "In the days/weeks that follow..." | Time skip |
| "A detail that's highly unusual..." | Tension building before a reveal |
| "And just like that..." | Dramatic reveal has happened |
| "But before we get to that..." | Pre-sponsor bridge |
| "With that said, let's get back to..." | Post-sponsor return |
| "Whether [suspect] realizes it or not remains to be seen." | After self-incrimination |

### 3.4 Dramatic Irony Formula

**Frequency: 4-5 per video, roughly every 10-15 minutes.** The actual Thetford reference video uses 4 across 50 minutes. More than 5 and the "What they don't realize is..." construction becomes a predictable cue that blunts its own impact.

**Variety rule:** Use at least 3 of the 5 types below. Never use the same type back-to-back — proximity and belief irony do similar psychological work (both say "the character doesn't know what you know"), so space them apart.

The pattern:

```
Step 1: Show character doing/saying something innocent
Step 2: Narrator tells audience what the character doesn't know
Step 3: Audience feels superior tension — they KNOW and the character DOESN'T
```

**Types of dramatic irony to use:**

| Type | Example | Limit |
|------|---------|-------|
| **Proximity irony** | "Officers are unknowingly standing feet from where the body was hidden" | 1 per video max |
| **Belief irony** | "Dena has no idea that three ex-husbands have already testified against her" | 1-2 per video |
| **Timeline irony** | "What Craig doesn't know is that this will be his last weekend alive" | 1 per video max |
| **Evidence irony** | "The smell that officers dismiss as wildlife will later prove to be decomposition" | 1-2 per video |
| **Identity irony** | "Dena thinks Roger is a routine deputy. He's a retired homicide detective." | 1 per video max |

**Advanced technique — delayed dramatic irony:** Instead of the narrator telling the viewer what the character doesn't know, plant a visual or audio detail that attentive viewers recognize as significant on their own. Example: bodycam pans past the carport without the narrator saying "the body is right there." The viewer who's been paying attention figures it out. Use this sparingly (1-2 per video) for a more participatory form of tension.

---

## Phase 4: The Visual Storyboard

### 4.1 Visual Tagging System

Every scene in the screenplay gets tagged. Tags map to production assets.

**Qualifier syntax:** When a bible code needs context, use `[CODE: qualifier]`. The code tells the editor the visual treatment; the qualifier tells them what content to find.

```
[COURTROOM: testimony — Rogan Gibson]     ← bible code + who's on screen
[BROLL-DARK: financial — office/money]     ← bible code + what kind of stock footage
[BODYCAM: arrival at Moselle]              ← bible code + which bodycam moment
[INTERROGATION: David Owen patrol car]     ← bible code + which interview
```

Standard qualifiers by code:
- `[COURTROOM: testimony | cross-examination | verdict | sentencing | exhibit | opening statement | wide]`
- `[BROLL-DARK: atmospheric | financial | courthouse/legal | police/crime | time passage | water/night]`
- `[BODYCAM: arrival | conversation | evidence | arrest]`
- `[INTERROGATION: suspect name or context]`
- `[WAVEFORM-AERIAL: call description]`

**Full scene format:**
```
[SCENE 14: Detective calls victim's ex-wife]
NARRATOR: "Detective Curtis decides to call the people who might know Dena best."
VISUAL: [PIP-DUAL] caller=Detective Curtis, subject=Ex-wife | [WAVEFORM-AERIAL] property aerial
AUDIO: Phone call recording
OVERLAY: [CAPTION-ANIMATED], [VIGNETTE], [LETTERBOX]
TRANSITION IN: [TR-HARD]
TRANSITION OUT: [TR-GLITCH] (before damning quote)
DURATION: 90 seconds
```

### 4.2 Complete Visual Element Catalog

#### Opening & Brand
| Code | What | When |
|------|------|------|
| [BRAND-STING] | "DR. INSANITY" text with glow on black | After trailer, before story |
| [DISCLAIMER] | "All footage is real" (RED) + source (WHITE) on dark aerial | After brand sting |
| [TRAILER] | Rapid-cut montage with [TR-GLITCH]/[TR-FLASH] | First 80 seconds |

#### Maps & Location
| Code | What | When |
|------|------|------|
| [MAP-FLAT] | Dark satellite top-down, heavy vignette | Establishing location |
| [MAP-3D] | Google Earth Studio 3D oblique view | Background for phone call PIP |
| [MAP-TACTICAL] | Dark map + red glowing road outlines | Remote/isolation emphasis |
| [MAP-PULSE] | Satellite + animated red radar circles on property | Pinpointing crime scene |
| [MAP-ROUTE] | Route line between two locations | Travel/distance context |

#### People & Characters
| Code | What | When |
|------|------|------|
| [PIP-SINGLE] | One File Viewer photo over footage/map | Any character mention |
| [PIP-DUAL] | Two File Viewer photos side by side | Phone calls between two people |
| [MUGSHOT-CARD] | Split: mugshot left, RED charges right | Final resolution |
| [LOWER-THIRD] | Name + role bar (dark bg, red accent line) | First intro of each character |

#### Investigation & Evidence
| Code | What | When |
|------|------|------|
| [POLICE-DB] | Fake database app with photo + fields | Investigation/research scenes |
| [DESKTOP-PHOTOS] | Windows desktop with Photo Viewer windows | Showing detective research |
| [EVIDENCE-CLOSEUP] | Bodycam zoom with red highlight circle/arrow | Evidence on camera |
| [EVIDENCE-DISPLAY] | Evidence items on bokeh/blurred background | Composed evidence reveal (climax) |
| [BODY-DIAGRAM] | Forensic line drawing of body + injuries | Cause of death description |
| [DOCUMENT-MOCKUP] | Phone/document on dark bg, red highlights | Text evidence, court filings |
| [TEXT-CHAT] | iMessage/SMS/Snapchat chat bubble recreation | Text message evidence |
| [SOCIAL-POST] | Social media post mockup (platform-specific) | Social media evidence, suspect/victim posts |
| [EVIDENCE-BOARD] | Red-string corkboard showing connections | Complex relationship webs (5+ people) |
| [FLOW-DIAGRAM] | Animated money/process flow between nodes | Financial crime, evidence chains |
| [CENSOR-BLUR] | Soft black blur over graphic content | Body discovery, graphic evidence |

#### Audio Visualization
| Code | What | When |
|------|------|------|
| [WAVEFORM-AERIAL] | Red waveform + captions over dark aerial footage | Every 911/phone call |
| [WAVEFORM-DARK] | Waveform on pure dark background (fallback) | When no aerial available |

#### Text & Graphics
| Code | What | When |
|------|------|------|
| [QUOTE-CARD] | Key quote in large text, teal/blue glow | Damning/important statements |
| [TIMELINE-MARKER] | Date/time in large text, red accent line | Time jumps |
| [TIMELINE-SEQUENCE] | Animated horizontal timeline with cursor/nodes | Act transitions, multi-year cases |
| [FINANCIAL-CARD] | Red dollar amount, grey description | Money reveals |
| [NEWS-MONTAGE] | Stacked newspaper headlines sliding in | Media coverage, public impact |
| [CAPTION-ANIMATED] | Bold white animated subtitles | Always — entire video |
| [SPLIT-INFO] | Split screen: text card left, footage right | Key data alongside footage |

#### Courtroom & Resolution
| Code | What | When |
|------|------|------|
| [INTERROGATION] | Real interrogation room footage + lower third | After arrest |
| [COURTROOM] | Real courtroom footage (judge, flag) | Legal proceedings |

#### Transitions
| Code | What | When | Frequency |
|------|------|------|-----------|
| [TR-HARD] | Hard cut | Default — between most clips | 55% |
| [TR-GLITCH] | RGB shift + scan lines + frame tear | Trailer + 3-4 biggest reveals ONLY | 8% max |
| [TR-FLASH] | 1-3 frames pure white | Trailer + 2-3 shocking reveals ONLY | 5% max |
| [TR-FADE] | Fade to/from black | Time jumps, act breaks, emotional beats | 12% |
| [TR-DISSOLVE] | Cross-dissolve | Photo intros, location establishing, mood shifts | 8% |
| [TR-ZOOM] | Ken Burns zoom/pan | 90% of static images (see stillness rule below) | 7% |
| [TR-SMASH] | Hard cut with tonal whiplash | Calm → sudden loud, sponsor → back to murder | 3% |
| [TR-LCUT] | Audio from next scene starts before visual cuts | Investigation beat transitions | 2% |

> **Glitch/flash budget:** In a 50-min video with ~300 cuts, 8% glitch = ~24 and 5% flash = ~15. That's still substantial. The key constraint: **never use [TR-GLITCH] or [TR-FLASH] outside the trailer or a Level 3 reveal.** If it's not a bombshell, it's a hard cut.

> **Stillness rule:** Reserve [TR-ZOOM]-free stillness for 3-5 moments of maximum emotional weight: body discovery, victim memorial, verdict landing, a key silence beat. The sudden absence of motion after 45 minutes of constant movement is disorienting and powerful. Tag these as `[STILL]` in the storyboard.

#### Persistent (Always On)
| Code | What |
|------|------|
| [VIGNETTE] | Dark edge gradient on every frame |
| [COLOR-GRADE] | Desaturated, blue-shifted shadows, contrast boost |
| [LETTERBOX] | Black bars top/bottom (2.35:1 widescreen) |

### 4.3 Color System

**Four semantic accents** — each carries a distinct emotional register:

| Color | Hex | Meaning | Used On |
|-------|-----|---------|---------|
| **Red** | `#DC3232` | Danger, alert, charges | Disclaimer text, map pulses, road outlines, evidence highlights, mugshot charges, financial amounts, [EVIDENCE-BOARD] connections |
| **Teal** | `#00D4AA` | Information, identity, context | Map labels, location pins, brand sting glow, lower third accents, [FLOW-DIAGRAM] info arrows, [TIMELINE-SEQUENCE] nodes |
| **Warm gold** | `#D4A843` | Victim, family, humanity | Victim photo color grade, family moments, memorial sections, humanization beats |
| **Cool blue-grey** | `#7A8FA6` | Procedural, law enforcement, clinical | Police/SLED procedural sections, interrogation overlays, forensic details, bodycam UI elements |
| White | `#FFFFFF` | Primary text | All body text, captions |
| Grey | `#B4B4B4` | Secondary text | Roles, descriptions, labels |
| Near-black | `#0A0A0F` | Background | All graphics, cards |

**Rule of thumb:**
- WARNING the viewer → **red**
- INFORMING the viewer → **teal**
- HUMANIZING a person → **warm gold**
- SHOWING procedure/investigation → **cool blue-grey**

**Quote card color follows content, not format:** A damning threat ("If I could kill him...") gets red accent, not teal. An informational quote ("The Murdaugh name carries weight") gets teal. A victim's own words get warm gold. The semantic meaning of the content determines the color, not the element type.

> The warm gold and cool blue-grey accents are used sparingly — primarily in color grading choices and occasional overlay accents. Red and teal remain the dominant pair. The expanded palette prevents 50-minute visual monotony without breaking the established look.

### 4.4 Progressive Visual Escalation

The video introduces progressively more **complex compositions** as it progresses. Escalation is about **layering and sophistication**, not withholding element types — Act 1 needs a rich enough palette to carry exposition-heavy sections (dynasty backstory, victim humanization) that may have zero bodycam.

```
ACT 1 (foundation — broad palette, simple compositions):
  Bodycam + [PIP-SINGLE] + [MAP-FLAT] + [MAP-3D] + [WAVEFORM-AERIAL]
  + [LOWER-THIRD] + [TIMELINE-MARKER] + [BROLL-DARK]
  + [DOCUMENT-MOCKUP] (for early evidence like phone/text)
  Compositions: single-layer. One visual element at a time.

ACT 2 (layered — same palette, multi-element compositions):
  + [DESKTOP-PHOTOS] + [POLICE-DB] + [PIP-DUAL] + [FINANCIAL-CARD]
  + [TEXT-CHAT] + [SOCIAL-POST] + [NEWS-MONTAGE]
  Compositions: two-layer. PIP over footage. Waveform over aerial.
  New in Act 2: contradiction stacking gets visual support (side-by-side quotes, timeline comparisons)

ACT 3 (complex — new high-impact elements):
  + [QUOTE-CARD] + [SPLIT-INFO] + [MAP-TACTICAL] + [EVIDENCE-BOARD]
  + [FLOW-DIAGRAM] + [TIMELINE-SEQUENCE]
  + Extended real footage sequences (3-5 min unbroken bodycam/interrogation/trial)
  Compositions: multi-layer composites. Split screens. Footage with overlaid data.

ACT 4 (maximum — climax-only elements, first appearances):
  + [EVIDENCE-DISPLAY] + [BODY-DIAGRAM]
  + [INTERROGATION] + [COURTROOM] + [MUGSHOT-CARD]
  Compositions: everything available. The viewer sees visual elements
  for the first time in the climax — keeping the visual language fresh even 45 minutes in.
```

**The key principle:** Escalation means viewers see **more elements on screen simultaneously** and **new element types** as the video progresses. But the base palette (maps, photos, lower thirds, B-roll) is available from the start. Don't starve Act 1 of visual variety — especially for Archetype B/D cases where Act 1 is 20%+ of the video.

### 4.5 Footage Mix Targets

Targets vary by case archetype — see **Section 1.2** for the full per-archetype breakdown table.

**Archetype A (Bodycam-Domestic) quick reference:**

| Category | % of Video | Source |
|----------|-----------|--------|
| Bodycam footage | 55% | FOIA |
| Phone/911 call visualizations | 15% | Generated ([WAVEFORM-AERIAL]) |
| Maps & location shots | 8% | Google Earth + MapLibre |
| Text overlays & graphics | 7% | Generated (Pillow/FFmpeg) |
| People photos (PIP) | 5% | News, social media, mugshots |
| B-roll (atmospheric stock) | 4% | Stock footage or AI |
| Sponsor segment (if applicable) | 0-3% | Self-produced |
| Interrogation + Courtroom | 3% | Court records |

**For other archetypes** (trial-centric, interrogation-centric, cold case), the primary footage source changes and stock B-roll increases to compensate. See the archetype table in Section 1.2.

**Critical ratio (all archetypes):** Total real content (primary footage + secondary footage + audio visualizations) must stay above **60%.** Below that, the video feels like a narrated slideshow regardless of how good the narration is.

---

## Phase 5: Retention Engineering

### 5.1 Information Delivery Rate

**Target: one new fact every 60-90 seconds.**

In a 50-minute video, that's **35+ distinct reveals.** If you count and get fewer than 30, the script needs more investigation beats.

### 5.1.1 Audio Break Rule

**The narrator should never speak for more than 90 seconds without a real audio clip breaking in.** If a section runs 2+ minutes of pure narration, insert a relevant audio clip — trial testimony, news report, 911 call excerpt, even a brief witness quote. This is especially critical in exposition-heavy sections (dynasty backstory, financial crime explanations) where no bodycam exists.

When no directly relevant audio is available for a section, use one of these:
- A trial quote that foreshadows the section's content (prosecutor summarizing the dynasty, witness describing the fraud)
- A brief 911/dispatch clip that re-grounds the viewer in the crime
- A news report audio clip establishing public reaction

The 60/40 narration-to-audio ratio is a whole-video target. But the distribution matters — front-loading all narration into Act 1 and all audio into Act 3 feels unbalanced. Every 90-second stretch should have at least a brief audio interruption.

### 5.2 Open Loop Management

**Always maintain 2-4 active open loops.**

| Loop Type | Opens | Closes | Duration |
|-----------|-------|--------|----------|
| **Master loop** (where is the body?) | 0:00 | Act 4 climax | Entire video |
| **Evidence loop** (what's that smell/clue?) | Trailer | Act 4 search | ~45 min |
| **Character loops** (what happened to X?) | As introduced | 5-15 min later | Medium |
| **Micro loops** (will X confirm suspicion?) | Per beat | Next beat | 2-5 min |

**Rule:** Never close all loops simultaneously. When you close one, open another within 60 seconds.

### 5.3 Contradiction Stacking

Each witness contradicts the previous version slightly:

```
Caller 1: "Missing for 2 months"
Caller 2: "Missing for 4 months"        ← contradiction
Neighbor: "Haven't seen him since Jan"   ← corroborates caller 2
Suspect:  "He's in Mexico"              ← contradicts everyone
Ex #1:    "She's dangerous"             ← explains WHY suspect lies
Ex #2:    "She threatened to kill him"   ← escalation
Daughter: "She's tried before"          ← PATTERN confirmed
```

The audience becomes increasingly confident the suspect is guilty — but the characters in the video are still catching up. This gap IS dramatic irony, sustained for 30+ minutes.

### 5.4 Advanced Narrative Techniques

These are optional tools that elevate a screenplay beyond the core formula. Use 2-3 per video — not all of them.

#### The False Resolution

A moment where the case appears to collapse before coming back stronger. The suspect's alibi checks out, evidence is ruled inconclusive, or a witness recants. The audience briefly believes the investigation is over — then a new piece of evidence shatters the false calm.

**When to use:** Act 2, roughly 60-70% through the investigation. Plant it after the audience has built confidence in the suspect's guilt. The momentary doubt makes the eventual evidence MORE convincing, not less.

**Example:** "Alex's attorney files a motion to exclude the kennel video. The judge allows arguments. For a moment, it appears the prosecution's centerpiece evidence may never reach the jury. But the ruling comes back: the video is admissible."

**Avoid:** Don't fake a false resolution that requires the narrator to mislead the audience. The uncertainty should be real (a legal motion, an alibi that initially checks out, a witness who hesitates) — not the narrator withholding known facts.

#### Visual Silence

10-15 seconds where footage plays with **no narration and no music**. Just ambient sound — bodycam hiss, courtroom murmur, interrogation room hum. Forces the viewer to lean in.

**When to use:** Maximum 2-3 times per video. Best moments:
- Bodycam walking through a dark property at night (the silence IS the tension)
- After a devastating reveal, before the narrator contextualizes (let it land)
- During the verdict — hold the courtroom audio, no narrator overlay

**Tag as:** `[VISUAL-SILENCE]` in the storyboard. Duration: 8-15 seconds. Any longer and viewers think something is broken.

#### Behavioral Analysis Commentary

Brief narrator commentary explaining **why** a suspect behaves a certain way — body language shifts, linguistic tells, interrogation tactics. Adds psychological depth beyond "here's what happened."

**When to use:** During interrogation or trial testimony sequences. 2-3 moments per video, maximum. Always tied to visible behavior the viewer can see.

**Examples:**
- "Notice how Alex shifts forward in his chair the moment Owen mentions the kennels. His body reacts before his words do."
- "When Waters asks about the stolen money, Alex's response is immediate — no pause, no thought. A truthful person recalling events pauses to access memory. A rehearsed person answers instantly."

**Avoid:** Armchair psychology or unfalsifiable claims. Only comment on observable behavior. Keep it brief — one sentence of analysis per moment, not a lecture.

#### Callback Structure

A detail planted early (Act 1) that becomes the key to understanding a revelation late (Act 3-4). Unlike open loops (which are questions), callbacks are **details the audience notices only in retrospect**.

**When to use:** Plant in Act 1 setup, pay off in Act 3-4. The audience should feel "oh — THAT'S why they mentioned that."

**Examples:**
- Act 1: "Maggie tells Blanca she'd give everything to make this go away." → Act 3: Waters cross-examines Alex about Maggie's awareness of the finances. The audience connects: Maggie knew something was wrong.
- Act 1: "The Murdaugh name opens every door." → Act 4: "The dynasty that shaped the Lowcountry for a century was dismantled by the one man who was supposed to carry it forward." The opening observation becomes the closing irony.

**Technique:** Don't signal the callback when you plant it. Just state the detail naturally. The payoff should feel earned, not telegraphed.

---

## Phase 6: Title & Thumbnail Formula

### 6.1 Title Formula

**Pattern:** `[Hidden Role] + [Action With Police] + [Dollar/Dramatic Noun]`

| Component | Function | Examples |
|-----------|----------|---------|
| Hidden role | Mystery — who is this person? | "Secret Killer", "Twisted Neighbor", "Double Life Doctor" |
| Action with police | Active verb, implies control | "Leads Cops Into", "Fools Detectives With", "Invites Police To" |
| Dollar/dramatic noun | Stakes + curiosity | "$3,000,000 Murder Mansion", "$500K Underground Bunker", "House of Horrors" |

**Rules:**
- 50-65 characters
- No emoji, no brackets, no question marks
- 3+ power words (Secret, Killer, Murder, Hidden, Deadly, etc.)
- Alliteration when possible ("Murder Mansion")

### 6.2 Thumbnail Formula

**The Irony Shot:** Show the killer looking innocent + the crime scene looking normal.

```
1. Extract clean bodycam frame: suspect smiling/calm, well-lit
2. Background: the property/crime scene looking ordinary
3. Overlay: "●REC" indicator (top-left) + camera UI elements
4. Color grade: NATURAL (bright) — NOT the dark grade of the video
5. No text — title does the work
6. No red accents — clean documentary feel
```

**The gap between pleasant thumbnail + horrifying title = the click.**

---

## Phase 6.5: Storyboard-to-Production Pipeline

> The gap between "what should be on screen" (storyboard) and "which actual file goes on the timeline" (production) is a full production step. This section defines that step.

### The Problem

The storyboard says things like: `[BROLL-DARK] Slow aerial of rural Southern estate at dusk (Pexels: "aerial farm dusk southern")`. Production needs: `segments/stock-broll-001.mp4 trim 0:00-0:10`. Someone has to find, download, verify, name, and trim each asset. For a 50-minute video, that's 50-80 visual segments.

### The Solution: Storyboard + Preflight + Web Editor

**The storyboard is the single source of truth.** There is no separate assembly guide — the storyboard drives everything: CLI commands, web editor, and the production pipeline.

**Step 1: Write the storyboard with rich layer descriptions.**

Each segment has typed layers (Visual, Audio, Overlay, Music, Source, Transition) with content type prefixes (`FOOTAGE:`, `STOCK:`, `NAR:`, `GRAPHIC:`, etc.). The storyboard also contains:
- Header metadata (duration, resolution, format)
- Pre-production checklist (audio, graphics, maps tasks)
- Asset need tables (stock footage, photos, maps)
- Production rules
- Post-assembly checklist

**Step 2: Use `bee-video preflight` to check readiness.**

```bash
bee-video preflight storyboard.md -p ./project
```

This scans the storyboard against project files and reports found/missing/needs-check for every asset.

**Step 3: Use the web editor for human-in-the-loop corrections.**

```bash
./start.sh  # or: bee-video serve
```

Load the storyboard in the web editor. Review segments, assign media files via drag-and-drop, adjust as needed. The editor reads the storyboard and saves media assignments as sidecar JSON.

**Step 4: Produce.**

```bash
bee-video produce storyboard.md -p ./project
```

Or step by step: `init` → `graphics` → `narration` → `trim-footage` → `assemble`. All commands read the storyboard directly.

### Naming Convention

```
segments/
├── footage/          # Real clips from FOIA / Court TV
│   ├── 911-call-{description}.mp4
│   ├── bodycam-{description}.mp4
│   ├── trial-{description}.mp4
│   └── interrogation-{description}.mp4
├── stock/            # Downloaded stock B-roll
│   └── broll-{description}.mp4
├── photos/           # Character photos formatted for PIP
│   └── pip-{character-name}.png
├── graphics/         # Generated overlays
│   ├── lower-third-{character}.png
│   ├── quote-card-{number}.png
│   ├── timeline-{date}.png
│   ├── financial-{amount}.png
│   └── mugshot-card.png
├── maps/             # Generated map images/videos
│   └── map-{location}-{type}.mp4
└── narration/        # TTS audio segments
    └── nar-{act}-{scene}.wav
```

---

## Phase 7: Production Checklist

> **Claude Code skills** automate steps 1-6. Run `/true-crime:research-case` to start. Each skill reads this formula as context.
>
> | Step | Skill | Output |
> |------|-------|--------|
> | Research | `/true-crime:research-case` | `case-research.md` |
> | Review | `/true-crime:review-case-research` | Viability check |
> | Screenplay | `/true-crime:generate-screenplay` | `screenplay.md` |
> | Review | `/true-crime:review-screenplay` | Formula compliance |
> | Storyboard | `/true-crime:generate-storyboard` | `storyboard.md` |
> | Review | `/true-crime:review-storyboard` | Production readiness |
> | Produce | `bee-video produce storyboard.md` | Final video |

### Pre-Production (2-4 weeks)
- [ ] Select case matching criteria (Section 1) — or run `/true-crime:research-case`
- [ ] File FOIA requests: bodycam, 911, detective recordings
- [ ] Gather: victim photo (2 variants), suspect mugshot, property address
- [ ] Research: court records, news articles, public documents — or run `/true-crime:review-case-research`
- [ ] Verify narrative arc exists before committing

### Screenplay (4-6 hours) — or run `/true-crime:generate-screenplay`
- [ ] Write trailer: select 5-7 audio clips
- [ ] Write Act 1: 911 call + first police visit + wrong conclusion
- [ ] Write Act 2: 6-8 investigation beats, each escalating
- [ ] Write sponsor bridge (in + out) — skip if no sponsor
- [ ] Write Act 3: confrontation face-to-face (use real bodycam heavily)
- [ ] Write Act 4: escalation → tip → search → body → arrest → charges
- [ ] Tag every scene with visual codes from Section 4.2
- [ ] Verify: 35+ reveals, 60-90 sec info rate
- [ ] Verify: 2-4 open loops active at all times (1 anchor + 1-2 structural + micro)
- [ ] Verify: 4-5 dramatic irony moments, using 3+ different types
- [ ] Verify: present tense throughout
- [ ] Verify: short-punch rhythm (medium-medium-long-SHORT-long)
- [ ] Verify: no narrator stretch exceeds 90 seconds without a real audio clip

### Asset Generation (6-8 hours)
- [ ] [BRAND-STING] frame
- [ ] [DISCLAIMER] card
- [ ] [MAP-FLAT], [MAP-3D], [MAP-TACTICAL], [MAP-PULSE] for property
- [ ] [PIP-SINGLE] for each character (File Viewer style)
- [ ] [PIP-DUAL] for each phone call pair
- [ ] [POLICE-DB] mockup with victim data
- [ ] [DESKTOP-PHOTOS] with victim/missing person photos
- [ ] [LOWER-THIRD] for each character
- [ ] [QUOTE-CARD] for 4-6 key statements (teal accent)
- [ ] [TIMELINE-MARKER] for 3-4 time jumps
- [ ] [FINANCIAL-CARD] for money reveals
- [ ] [EVIDENCE-DISPLAY] composed evidence shot (bokeh bg)
- [ ] [BODY-DIAGRAM] forensic illustration
- [ ] [DOCUMENT-MOCKUP] for text evidence
- [ ] [SPLIT-INFO] panels for key data
- [ ] [TEXT-CHAT] message recreations (if text evidence exists)
- [ ] [SOCIAL-POST] mockups (if social media evidence exists)
- [ ] [EVIDENCE-BOARD] connection diagram (if 5+ connected individuals)
- [ ] [FLOW-DIAGRAM] money/process flow (if financial crime)
- [ ] [TIMELINE-SEQUENCE] animated timeline (if case spans 6+ months)
- [ ] [NEWS-MONTAGE] headline stack (if high-profile media coverage)
- [ ] [MUGSHOT-CARD] split: mugshot + RED charges
- [ ] [WAVEFORM-AERIAL] for each 911/phone call
- [ ] [CAPTION-ANIMATED] subtitle file (ASS/SRT)

### Narration (1-2 hours)
- [ ] Generate TTS (ElevenLabs, deep male, low variability)
- [ ] Present tense throughout
- [ ] Add pause markers before reveals
- [ ] Verify sentence rhythm (medium → SHORT PUNCH → long)

### Preflight (1 hour)
- [ ] Run `bee-video preflight storyboard.md -p ./project` — generates asset manifest from storyboard
- [ ] Verify all footage segments exist at expected paths
- [ ] Verify all stock clips downloaded, named per convention, and correct duration
- [ ] Verify all generated graphics rendered (lower thirds, quote cards, maps, etc.)
- [ ] Verify all photos collected and formatted as PIP overlays
- [ ] Verify narration audio segmented per scene
- [ ] Flag any missing assets — resolve before starting assembly

### Assembly (6-8 hours)
- [ ] Lay narration as audio backbone
- [ ] Place bodycam aligned to transcript timestamps
- [ ] Fill narrator sections with generated overlays
- [ ] Apply [COLOR-GRADE] + [VIGNETTE] + [LETTERBOX] globally
- [ ] Insert [TR-GLITCH] at 4-6 tension peaks
- [ ] Insert [TR-FLASH] at 2-3 shocking reveals
- [ ] Mix audio: narration loudest, music at 12-15%, real audio natural
- [ ] Normalize to -14 LUFS
- [ ] Sponsor segment: warm/bright visual departure — skip if no sponsor

### Post-Production (30 min)
- [ ] Thumbnail: bodycam frame + REC overlay + natural color
- [ ] Title: [Hidden Role] + [Action] + [$$ Dramatic Noun]
- [ ] Description: disclaimer + case context (+ sponsor links if applicable)
- [ ] Tags: none (zero)
- [ ] Category: News & Politics

---

## Appendix: Screenplay Template

```markdown
# [VIDEO TITLE]

> Case: [Case name]
> Location: [City, State]
> Duration target: 45-50 minutes
> Sponsor: [Brand] @ 40-65% mark (after biggest revelation) — or omit if no sponsor

---

## TRAILER (0:00 - 1:20)

[TRAILER]
CLIP 1: [Source] — "[Quote]" (X seconds)
CLIP 2: [Source] — "[Quote]" (X seconds)
CLIP 3: NARRATOR — "[Dramatic irony line]" (X seconds)
CLIP 4: [Source] — "[Quote]" (X seconds)
CLIP 5: [Source] — "[Quote]" (X seconds)
CLIP 6: [Source] — "[Misdirect quote]" (X seconds)
CLIP 7: [Source] — "[Confession tease]" (X seconds)
TRANSITION: [TR-GLITCH] between each, [TR-FLASH] before clip 7

## OPENING SEQUENCE (1:20 - 1:50)

[BRAND-STING] → [DISCLAIMER] → [MAP-FLAT] wide → [MAP-PULSE] + [PIP-SINGLE] victim → [WAVEFORM-AERIAL] + [CAPTION-ANIMATED]

## ACT 1: SETUP (1:50 - ~8:00)

### Scene 1: The 911 Call
NARRATOR: "[Present tense setup]"
VISUAL: [WAVEFORM-AERIAL] property bg + [PIP-DUAL] caller + victim
AUDIO: 911 call recording
OVERLAY: [CAPTION-ANIMATED]
DURATION: 90 seconds

### Scene 2: Officers Arrive
NARRATOR: "[Officers dispatched to property]"
VISUAL: Bodycam — night arrival + [MAP-TACTICAL]
AUDIO: Bodycam audio
OVERLAY: [CAPTION-ANIMATED], [LOWER-THIRD] officer name
TRANSITION: [TR-HARD]
DURATION: 120 seconds

[... continue for each scene ...]

## ACT 2: INVESTIGATION (8:00 - 26:00)

### Scene X: [Investigation beat title]
NARRATOR: "[Bridge sentence]"
VISUAL: [Element codes]
AUDIO: [Source]
OVERLAY: [Always-on elements]
TRANSITION: [Transition type]
DURATION: XX seconds
NEW INFO: [What the audience learns]
OPEN LOOP: [Question opened or closed]
DRAMATIC IRONY: [If applicable]

[... 6-8 investigation beats ...]

## SPONSOR (optional — ~40-65% of runtime, after biggest revelation)

[Include this section only if you have a sponsor. Otherwise, transition directly from Act 2 to Act 3 with a narrator beat or [TR-FADE].]

BRIDGE IN: "But before we get to that, [thematic connection to sponsor]..."
VISUAL: Warm, bright sponsor footage
BRIDGE OUT: "With that said, let's get back to [character], who [re-hook]..."

## ACT 3: CONFRONTATION (28:00 - 40:00)

[... confrontation beats ...]

## ACT 4: CLIMAX (40:00 - 50:00)

[... climax + resolution beats ...]

### Final Card
VISUAL: [MUGSHOT-CARD] — charges in RED
NARRATOR: "[2-3 sentence epilogue. Case status.]"
TRANSITION: [TR-FADE] to black
```

---

## Appendix B: Related Documents

This formula doesn't live alone. These documents evolve together:

| Document | What It Covers | Update When |
|----------|---------------|-------------|
| **This file** (`screenplay-storyboard-formula.md`) | The complete production formula | Any structural, narrative, or process insight |
| `visual-storyboard-bible.md` | Every visual element with specs, code, and implementation | New visual elements discovered, color/style corrections |
| `video-analysis-s6CXNbzKlks.md` | Deep analysis of the reference video | Corrections to observations, new frame analysis |
| `screenplay-analysis-dr-insanity-s6CXNbzKlks.md` | Scene-by-scene screenplay breakdown | Scene structure corrections, visual tag updates |

**When analyzing a NEW video:** Create a new `video-analysis-{id}.md`, extract any techniques that differ from the formula, and fold those differences back into this formula as either corrections or "variant" notes.

**When producing OUR video:** Use the screenplay template (Appendix A above), and after production, do a post-mortem: what worked, what didn't, what should change in the formula. Log it in the changelog.

---

## Appendix C: Scalability & Tooling

> **Actionable items are tracked in `bee-content/video-editor/ROADMAP.md`** (the single source of truth for what needs to be built). This appendix captures the strategic context — the "why" behind the roadmap items.

### Production Velocity

At current efficiency: **15-21 hours of active human work per video** (screenplay 4-6h, assets 6-8h, narration 1-2h, assembly 6-8h, preflight 1h). Plus 2-4 weeks FOIA wait time for non-famous cases.

**Realistic trajectory:**
- Months 1-3: 1 video/month (learning the pipeline, building templates)
- Months 4-6: 2 videos/month (templates mature, parallel FOIA, LLM screenplay drafts)
- Months 7-12: 2-3 videos/month (stock library built, asset generation mostly automated)
- Year 2+: 4 videos/month possible with LLM drafts, full automation, pre-built asset library, and 6-8 week FOIA lead time

### FOIA Strategy

FOIA is the least automatable bottleneck. Mitigation:
- File on day 1 of case selection — before writing the screenplay
- Maintain 2-3 cases at different pipeline stages (FOIA pending, screenplay in progress, in assembly)
- Pre-select cases with known public footage (Court TV, widely covered cases) to reduce FOIA dependency
- Florida and Texas have fastest response times

### What Breaks After 10 Videos

- **Stock footage repetition** — viewers notice the same "dark hallway" clip across videos. Need a tagged stock library with usage tracking.
- **Formula fatigue** — regular viewers pattern-match the structure. Need progressive evolution: rotate cold open styles, vary act structure, introduce series arcs.
- **Narration voice drift** — TTS parameters shift between videos. Lock one voice config and version it.
- **No cross-video brand building** — no consistent intro/outro, no series arcs, no community engagement patterns, no YouTube algorithm feedback loop.
