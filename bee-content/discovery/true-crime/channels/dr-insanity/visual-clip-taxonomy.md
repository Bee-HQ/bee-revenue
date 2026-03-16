# Visual Clip Taxonomy — Dr Insanity Video Production Template

**Source Video:** "Secret Killer Leads Cops Into Her $3,000,000 Murder Mansion" (s6CXNbzKlks)
**Purpose:** Map every visual clip type used, how they're organized in the narrative, and how to source/generate each for future videos.

---

## Clip Categories

### Category 1: BODYCAM FOOTAGE
**What:** Raw police body-worn camera footage showing officers at the scene.
**Source:** FOIA requests to police departments, proactive release portals (Chicago COPA, LVMPD), YouTube aggregators (Police Activity, Body Cam Watch).
**Generate alternative:** Cannot be generated — must be sourced. If unavailable, use stock police footage + narration.
**Legal:** Government-produced = public domain, freely reusable.

**Subcategories:**
| Sub-type | Description | Example from video |
|----------|-------------|-------------------|
| 1A. Welfare check | Officers arriving, knocking, checking windows | Officers walking around Thatford property, checking doors |
| 1B. Conversation/interview | Officer speaking face-to-face with witness or suspect | Deputy Roger interviewing Dena at her house |
| 1C. Property search | Officers sweeping house/buildings with flashlights | Clearing the basement, checking rooms, finding the safe |
| 1D. Evidence discovery | Moment of finding key evidence | Opening the safe ($84K vs $1.5M), finding blood traces |
| 1E. Tactical entry | Officers with weapons drawn, clearing rooms | "Sheriff's office!" — garage entry, room clearing |
| 1F. Driving/arrival | Bodycam from patrol car or walking up to location | Pulling up to the long driveway |

**Usage in narrative:**
- Welfare check footage → Act 1 (setup, first visit)
- Conversation footage → Act 3 (confrontation with suspect)
- Search footage → Act 4 (climax, warrant execution)
- Evidence discovery → Act 4 (safe opening, body found)

---

### Category 2: 911 / DISPATCH CALL RECORDINGS
**What:** Audio recordings of emergency calls, played over visual.
**Source:** FOIA requests to dispatch centers. Best states: FL, TX, OH, GA.
**Generate alternative:** Cannot generate real calls. Audio waveform visualization over dark background.
**Legal:** Public records in most states.

**Subcategories:**
| Sub-type | Description | Visual treatment |
|----------|-------------|-----------------|
| 2A. Initial welfare check call | First report of concern | Audio waveform + caller ID text overlay + dark background |
| 2B. Follow-up call | Additional concerns | Same visual treatment |
| 2C. Tip call | Someone reporting suspicion/confession | Same, but with more dramatic lighting/color |

**Visual treatment during 911 audio:**
- Dark/black background with audio waveform animation (FFmpeg showwaves)
- Text overlay: caller name, relationship to case, date
- Occasional cut to relevant B-roll (exterior of property, photo of victim)
- Speaker labels: ">> Dispatcher" and ">> Caller" text indicators

**Usage in narrative:**
- 911 calls open Act 1 (the inciting incident)
- Additional calls escalate tension in Act 2
- Tip calls trigger Act 4 (the breakthrough)

---

### Category 3: PHONE CALL RECORDINGS (Detective calls)
**What:** Audio of detectives calling witnesses, ex-husbands, family members.
**Source:** Court exhibits, FOIA, discovery process documents.
**Generate alternative:** Audio waveform + speaker photos/silhouettes.
**Legal:** Public record when part of court proceedings.

**Subcategories:**
| Sub-type | Description | Visual treatment |
|----------|-------------|-----------------|
| 3A. Detective to witness | Gathering background info | Split screen: detective photo + witness photo/silhouette |
| 3B. Detective to suspect | Direct call to suspect | Audio waveform + suspect photo, tension-building color |
| 3C. Detective to family | Speaking with victim's family | Softer visual treatment, family photos |

**Visual treatment:**
- Phone interface mockup (dark background, caller/receiver icons)
- Speaker photos with name labels
- Audio waveform between speakers
- Key quote text overlay for damning statements

**Usage:** Act 2 (investigation, gathering witness testimonies)

---

### Category 4: INTERROGATION / INTERVIEW ROOM FOOTAGE
**What:** Video from police interview rooms (fixed camera, overhead angle).
**Source:** Court exhibits, FOIA, DA's office. Released after case is adjudicated.
**Generate alternative:** Cannot generate. If unavailable, use audio + silhouette.
**Legal:** Court exhibit = public record.

**Subcategories:**
| Sub-type | Description |
|----------|-------------|
| 4A. Suspect interrogation | Suspect in interview room (end of video) |
| 4B. Witness interview | Witness in police station |

**Usage:** Act 4 resolution — Dena lawyers up, brief but powerful.

---

### Category 5: LOCATION / ESTABLISHING SHOTS
**What:** Aerial or ground-level views of locations relevant to the case.
**Source:** Google Earth/Maps, MapLibre, Mapbox API, stock footage, drone footage.
**Generate:** YES — fully generatable.

**Subcategories:**
| Sub-type | Description | How to source/generate |
|----------|-------------|----------------------|
| 5A. Aerial zoom-in | Zoom from satellite to specific address | Google Earth Studio, MapLibre fly-to animation |
| 5B. Street view | Ground-level view of property/neighborhood | Google Maps Street View screenshots |
| 5C. Regional map | Map showing city/state with marker | MapLibre/Mapbox static map with pin |
| 5D. Distance/route map | Map showing distance between two locations | MapLibre with route line overlay |
| 5E. Neighborhood context | Wide shot showing surrounding area | Google Earth, stock aerial footage |

**Visual treatment:**
- Slow zoom from wide to tight (Ken Burns on map screenshot)
- Location name + state as text overlay
- Pin drop animation on exact address
- Transition: zoom into location → cut to bodycam footage at same location

**Usage:** Every time a new location is introduced in the narrative.

---

### Category 6: PHOTOS (People)
**What:** Photos of victim, suspect, witnesses, family members.
**Source:** Mugshots (public record), news media, social media (with care), court filings.
**Generate alternative:** AI-generated face (ethical concerns) or silhouette.
**Legal:** Mugshots = public record. Social media photos = fair use in news commentary.

**Subcategories:**
| Sub-type | Description | Visual treatment |
|----------|-------------|-----------------|
| 6A. Victim photo | Warm, humanizing photo | Soft frame, warm color grade, name/age overlay |
| 6B. Mugshot | Suspect booking photo | Stark frame, cold color grade, charges overlay |
| 6C. Couple/family photo | Victim + suspect together (happier times) | Contrast with present situation |
| 6D. Witness photo | Person providing testimony | Small inset or alongside audio waveform |

**Visual treatment:**
- Ken Burns (slow zoom) on static photos
- Soft photo frame with drop shadow (ImageMagick/Pillow)
- Name + age + relationship text overlay as lower third
- Photos dissolve in/out with background music

**Usage:** When introducing each character for the first time, and during emotional beats.

---

### Category 7: EVIDENCE / DOCUMENT CLOSE-UPS
**What:** Close-up shots of physical evidence, documents, or key objects.
**Source:** Court exhibits, bodycam footage (zoomed), news reports, FOIA.
**Generate alternative:** Recreate document mockups, text overlays describing evidence.

**Subcategories:**
| Sub-type | Description | Example from video |
|----------|-------------|-------------------|
| 7A. Handwritten note/letter | Physical document shown | "Note from Craig" that Dena presented to Roger |
| 7B. Financial records | Bank statements, spending | Dena's spending of hundreds of thousands |
| 7C. Physical evidence | Objects at crime scene | Bleach bottles, disabled cameras, blood traces |
| 7D. Safe/valuables | Money, weapons in safe | $84,200 counted from Craig's safe |
| 7E. Court document | Arrest warrant, charges | Arrest warrant for Dena |

**Visual treatment:**
- Zoom into document/evidence with slight rotation
- Highlight key text with box/circle overlay
- Narrator reads key portions aloud
- Red circle/arrow pointing to crucial details

**Usage:** Throughout investigation sections, each piece of evidence building the case.

---

### Category 8: NARRATOR B-ROLL (Generic atmosphere)
**What:** Stock footage or AI-generated visuals that set mood during narration sections.
**Source:** Stock libraries (Pexels, Storyblocks), AI video generation (Runway, Pika).
**Generate:** YES — fully generatable.

**Subcategories:**
| Sub-type | Description | How to source/generate |
|----------|-------------|----------------------|
| 8A. Dark atmospheric | Foggy roads, dark hallways, shadows | Stock footage + color grading |
| 8B. Police/crime generic | Police cars, crime tape, flashing lights | Stock footage libraries |
| 8C. Courthouse/legal | Courtroom exterior, gavel, legal docs | Stock footage |
| 8D. Money/financial | Cash, bank, spending visuals | Stock footage, AI generated |
| 8E. Emotional/human | Hands, tears, isolation | Stock footage |
| 8F. Time passage | Clock, calendar, seasons changing | Stock footage, simple animation |
| 8G. Technology | Phone screens, computers, surveillance | Stock footage, screen recordings |

**Usage:** During narrator-heavy sections where no real footage exists. Fills 20-30% of total video.

---

### Category 9: TEXT OVERLAYS & GRAPHICS
**What:** On-screen text, titles, lower thirds, data displays.
**Source:** Generated programmatically (FFmpeg drawtext, Pillow, Remotion).
**Generate:** YES — always generated.

**Subcategories:**
| Sub-type | Description | When used |
|----------|-------------|----------|
| 9A. Character lower third | Name, age, role (e.g., "Craig Thatford, 60 — Victim") | First introduction of each person |
| 9B. Location identifier | City, state, date | Each new location |
| 9C. Timeline marker | "2 months later", "January 2025" | Time jumps |
| 9D. Key quote highlight | Damning statement in large text | "If I could kill Craig and get away with it, I'd do it" |
| 9E. Financial data | Dollar amounts, spending breakdown | Financial investigation sections |
| 9F. Case status | "Pre-trial", "Charged with first-degree murder" | Resolution section |
| 9G. Sponsor overlay | QR code, link, brand logo | Sponsor section |

---

### Category 10: SPONSOR SEGMENT
**What:** Pre-produced ad read with product visuals.
**Source:** Provided by sponsor or self-produced.
**Generate:** Screen recordings of app/product, text overlays.

**Subcategories:**
| Sub-type | Description |
|----------|-------------|
| 10A. Product demo | Screen recording of app (Chime in this video) |
| 10B. Comparison graphic | "National average 0.39% vs Chime 3%" style comparison |
| 10C. CTA overlay | QR code, link, discount code |

---

## Scene-by-Scene Visual Map

This maps the exact transcript to clip categories, showing how visuals are organized:

### COLD OPEN (0:00 - 1:30)

| Timestamp | Narration/Audio | Clip Category | Notes |
|-----------|----------------|---------------|-------|
| 0:00-0:05 | "Doesn't look like anyone's been here" | **1A** Bodycam (welfare check) | Raw bodycam, officers at property |
| 0:05-0:10 | "What's that smell?" | **1A** Bodycam | Officer reacting to decomposition |
| 0:10-0:30 | Narrator: "This officer is unknowingly reacting..." | **1A** Bodycam (slowed) + **9D** Quote overlay | Bodycam continues in background, text overlay for dramatic irony |
| 0:30-0:35 | "Where's that blood?" | **1C** Bodycam (search) | Flash-forward clip from later search |
| 0:35-0:40 | "This is the only way I've been able to have any communication" | **3A** Phone call audio | Flash-forward from later call |
| 0:40-0:45 | "I wouldn't even know where to start" | **1B** Bodycam (conversation) | Flash-forward clip |
| 0:45-0:50 | "There's some weird going on" | **1B** Bodycam (neighbor) | Flash-forward from neighbor interview |
| 0:50-1:00 | Narrator: "Whoever killed Craig covered their tracks..." | **8A** Dark atmospheric B-roll | Mood-setting stock footage |
| 1:00-1:05 | "Holy smokes" | **1D** Bodycam (evidence) | Flash-forward from safe opening |
| 1:05-1:15 | "I don't want to implicate her" / "You need to say it" | **1B** Bodycam (neighbor) | Flash-forward |
| 1:15-1:30 | "You might start looking in the Caribbean" | **3A** Phone call | Flash-forward from witness call |

**Pattern:** Cold open = 5-7 flash-forward clips (real footage from later in video) sandwiched between narrator dramatic irony setup. Creates open loops.

---

### SETUP (1:30 - 4:00)

| Narration/Audio | Clip Category | Notes |
|----------------|---------------|-------|
| "It's a late May evening in Cloudcroft, New Mexico" | **5A** Aerial zoom + **5C** Regional map | Google Earth zoom into Cloudcroft, NM |
| "Tucked among wooded acreage and mountain terrain" | **5B** Street view or **5E** Neighborhood | Establishing shot of property area |
| "60-year-old Craig Thatford" | **6A** Victim photo + **9A** Lower third | Warm photo, name/age overlay |
| "He lives inside this large three-story house with his wife, Dena" | **6C** Couple photo | Happy times photo |
| "Craig's roofing business" | **8D** Financial B-roll | Stock footage of business/money |
| "They own multiple residential properties" | **5A** Aerial of multiple properties | Map showing property locations |
| "the Otero County Sheriff's Office receives a disturbing call" | **8B** Police B-roll | Stock police station, then transition to... |
| 911 call: "Communications on a recorded line" | **2A** 911 call audio visualization | Dark background + waveform + text |
| Full 911 call plays | **2A** continues | Caller name overlay, key details |

**Pattern:** Setup = location establishing → character photos → inciting incident (911 call). Visual rhythm: wide → tight → atmospheric → raw audio.

---

### INVESTIGATION (4:00 - 26:00)

**First police visit (4:00-8:00):**

| Content | Clip Category |
|---------|---------------|
| Officers arrive at property | **1F** Bodycam (driving/arrival) + **5A** aerial |
| Walking around house | **1A** Bodycam (welfare check) |
| Checking windows, doors locked | **1A** Bodycam |
| "What's that smell?" | **1A** Bodycam — KEY MOMENT |
| Officers leave | **1F** Bodycam (departure) |
| Narrator commentary between clips | **8A** Dark atmospheric + **5B** property shots |

**Second call + grandson (8:00-10:00):**

| Content | Clip Category |
|---------|---------------|
| 911 call from Cody | **2B** 911 call visualization |
| Narrator fills in timeline details | **9C** Timeline graphic + **8F** Time passage B-roll |

**Neighbor canvass (10:00-14:00):**

| Content | Clip Category |
|---------|---------------|
| Deputy talking to firefighter friend | **1B** Bodycam (conversation) |
| Deputy talking to Heidi (neighbor) | **1B** Bodycam (conversation) |
| Narrator connecting contradictions | **9D** Quote comparisons (what Dena told X vs Y) |

**Dena calls back (14:00-18:00):**

| Content | Clip Category |
|---------|---------------|
| Phone call audio | **3B** Detective-to-suspect call |
| Narrator analyzing inconsistencies | **6B** Dena photo + **9D** Quote overlays |

**Ex-husbands / daughter (18:00-26:00):**

| Content | Clip Category |
|---------|---------------|
| Detective calls ex-husband #1 | **3A** Phone call + **6D** Witness photo |
| Detective calls ex-husband #2 (Scott) | **3A** Phone call + **6D** Witness photo |
| "If I could kill Craig and get away with it, I'd do it" | **9D** KEY QUOTE in large text |
| Detective calls daughter Leslie | **3C** Phone call + **6D** Photo |
| "My mom is crazy. She's tried to kill me before" | **9D** KEY QUOTE |
| Financial investigation | **7B** Financial records + **8D** Money B-roll + **9E** Dollar amounts |

**Pattern:** Investigation cycles between real footage (bodycam/calls) and narrator bridges (B-roll + text overlays). Each witness gets their own "visual identity" (photo + name).

---

### CONFRONTATION (28:00 - 40:00)

| Content | Clip Category |
|---------|---------------|
| Roger arrives at property | **1F** Bodycam arrival |
| Face-to-face with Dena | **1B** Bodycam (extended conversation) |
| Dena shows handwritten note | **7A** Evidence close-up (note) |
| Dena mentions $1.5M safe | **9E** Dollar amount overlay |
| Walking downstairs to safe | **1B** Bodycam (walking through house) |
| Seeing the safe | **7D** Evidence (safe) |
| Narrator: "He's standing where Craig's body was" | **1B** Bodycam + **9D** Dramatic text overlay |
| Roger reveals: "homicide unit in Albuquerque" | **1B** Bodycam — KEY MOMENT (face reactions) |
| **SPONSOR (Chime)** | **10A/10B/10C** Sponsor segment |
| Roger returns 5 days later | **1F** Bodycam arrival |
| Hole in the ground | **1A** Bodycam + **9D** Text overlay |
| "If I had just left when he told me to..." | **1B** Bodycam — SELF-INCRIMINATION |
| Narrator: neighbors reveal more | **1B** Bodycam (neighbor interviews) |

**Pattern:** Confrontation is 80%+ bodycam footage — longest continuous real footage segment. Minimal B-roll needed. The footage IS the content.

---

### CLIMAX & RESOLUTION (40:00 - 50:00)

| Content | Clip Category |
|---------|---------------|
| Dena vanishes | **8A** Dark atmospheric + **5A** Maps |
| Co-worker tip call (Andrew) | **3A** Phone call visualization |
| "She said she shot him" | **9D** KEY QUOTE |
| Search warrant coordination | **8B** Police B-roll |
| Interview with Dena's mother | **1B** Bodycam (at mother's house) |
| Search warrant execution | **1E** Tactical entry (room clearing) |
| Finding bleach, disabled cameras | **1C** Bodycam search + **7C** Evidence close-ups |
| Safe opened: $84,200 | **1D** Evidence discovery + **9E** Amount overlay |
| Daughter Leslie calls detective | **3C** Phone call |
| "She shot him... left him on the floor for a day" | **9D** KEY QUOTE |
| Body found in carport | **1D** Bodycam (CLIMAX MOMENT) |
| Autopsy results | **8C** Courthouse B-roll + **9F** Text overlay |
| Arrest at hospital | **8B** Police B-roll |
| Interrogation room | **4A** Interrogation footage |
| "I'm going to need a lawyer" | **4A** + **9D** Quote |
| Case status | **9F** Case status graphic |

---

## Clip Category Distribution (estimated for this video)

| Category | % of Total Video | Sourceability |
|----------|-----------------|---------------|
| **1. Bodycam** | **45%** | Must source (FOIA) |
| **2. 911 calls** | **5%** | Must source (FOIA) |
| **3. Phone calls** | **10%** | Must source (court records) |
| **4. Interrogation** | **2%** | Must source (court records) |
| **5. Location shots** | **8%** | **Generate** (Google Earth, MapLibre) |
| **6. Photos** | **5%** | Source (mugshots, news, social media) |
| **7. Evidence close-ups** | **3%** | Source (bodycam zooms, court exhibits) |
| **8. Narrator B-roll** | **12%** | **Generate** (stock footage, AI) |
| **9. Text overlays** | **7%** | **Generate** (FFmpeg, Pillow, Remotion) |
| **10. Sponsor** | **3%** | Self-produced |

**Key insight:** ~62% of visuals MUST be sourced from real case footage. ~27% can be generated. ~8% is photos. The quality of the video depends entirely on the quality and quantity of available bodycam/call footage.

---

## Case Selection Criteria (Based on Visual Needs)

A case is "video-ready" if it has:

| Requirement | Priority | Source |
|------------|----------|--------|
| Bodycam footage (multiple visits) | **Critical** | FOIA to police department |
| 911 call recording(s) | **High** | FOIA to dispatch center |
| Detective phone call recordings | **High** | Court exhibits |
| Victim photo | **High** | News, mugshot database, social media |
| Suspect mugshot | **High** | Booking database (public record) |
| Property address (for maps) | **Medium** | Court records, news reports |
| Interrogation footage | **Nice to have** | Court exhibits |
| Financial records | **Nice to have** | Court filings |

**Red flag:** If a case has NO bodycam footage, the video quality will suffer significantly. The bodycam footage is the backbone — it provides 45% of the visual content.

---

## Production Workflow: From Case to Video

### Step 1: Case Research & Footage Assessment
```
Input: Case name / court case number
Actions:
  1. Search CourtListener / PACER for case documents
  2. Identify police department(s) involved
  3. File FOIA requests for: bodycam, 911 calls, detective recordings
  4. Search YouTube for existing coverage (may have footage already)
  5. Gather: victim photos, mugshots, property addresses
  6. DECISION: Does enough footage exist? If <20 min of real footage → skip case
```

### Step 2: Screenplay Writing
```
Input: Case facts + available footage inventory
Actions:
  1. Write screenplay following Dr Insanity 4-act structure
  2. Mark each scene with clip category tags: [BODYCAM-1A], [911-2A], [MAP-5A], etc.
  3. Identify which moments need B-roll vs real footage
  4. Place sponsor break at peak tension (35-50% of runtime)
```

### Step 3: Visual Asset Preparation
```
For each clip category needed:
  [BODYCAM] → Trim relevant sections, color correct if needed
  [911/PHONE] → Extract audio, generate waveform visualization (FFmpeg showwaves)
  [MAP] → Generate location shots (MapLibre/Google Earth)
  [PHOTOS] → Process with frames, Ken Burns prep (ImageMagick/Pillow)
  [TEXT] → Generate all lower thirds, quote overlays, timeline markers
  [B-ROLL] → Select stock footage or generate with AI
```

### Step 4: Assembly
```
Timeline assembly (MoviePy / Editly / Remotion):
  1. Lay down narration audio track
  2. Place real footage clips aligned to transcript timestamps
  3. Fill narrator sections with B-roll + text overlays
  4. Add background music (MusicGen or licensed)
  5. Burn subtitles (stable-ts + ASS + FFmpeg)
  6. Add transitions between sections
  7. Insert sponsor segment
  8. Final audio mix (normalize levels)
```

### Step 5: Export & Upload
```
  1. Render at 1080p (FFmpeg / Remotion Lambda)
  2. Generate thumbnail (Rembg + Real-ESRGAN + text overlay)
  3. Write title using Dr Insanity formula
  4. Write description with SEO keywords
  5. Upload via YouTube Data API v3
```

---

## Clip Category Quick Reference (for screenplay tagging)

```
[BODYCAM-WELFARE]     — Officers checking on someone
[BODYCAM-CONVO]       — Officer interviewing person face-to-face
[BODYCAM-SEARCH]      — Officers searching property
[BODYCAM-EVIDENCE]    — Finding physical evidence
[BODYCAM-TACTICAL]    — Weapons drawn, clearing rooms
[BODYCAM-ARRIVE]      — Driving up, getting out of car

[911-INITIAL]         — First emergency call
[911-FOLLOWUP]        — Additional call raising stakes
[911-TIP]             — Critical tip or confession call

[CALL-DETECTIVE]      — Detective calling witnesses
[CALL-SUSPECT]        — Detective calling suspect
[CALL-FAMILY]         — Detective calling victim's family

[INTERROGATION]       — Interview room footage

[MAP-AERIAL]          — Zoom into location
[MAP-STREET]          — Ground-level view
[MAP-REGION]          — Wide area with pin
[MAP-ROUTE]           — Distance/route between locations

[PHOTO-VICTIM]        — Victim photo (warm treatment)
[PHOTO-MUGSHOT]       — Suspect booking photo
[PHOTO-COUPLE]        — Victim + suspect together
[PHOTO-WITNESS]       — Witness/family member photo

[EVIDENCE-DOCUMENT]   — Close-up of physical document
[EVIDENCE-FINANCIAL]  — Financial records
[EVIDENCE-PHYSICAL]   — Crime scene objects
[EVIDENCE-VALUABLES]  — Safe, money, weapons

[BROLL-DARK]          — Dark atmospheric stock footage
[BROLL-POLICE]        — Generic police/crime footage
[BROLL-COURT]         — Courthouse, legal imagery
[BROLL-MONEY]         — Financial imagery
[BROLL-EMOTION]       — Human emotion footage
[BROLL-TIME]          — Time passage imagery

[TEXT-LOWERTHIRD]      — Name, age, role
[TEXT-LOCATION]        — City, state, date
[TEXT-TIMELINE]        — Time marker
[TEXT-QUOTE]           — Key quote highlighted
[TEXT-FINANCIAL]       — Dollar amounts
[TEXT-STATUS]          — Case status/charges

[SPONSOR]             — Ad segment
```
