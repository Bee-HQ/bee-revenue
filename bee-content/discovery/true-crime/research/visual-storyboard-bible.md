# True Crime Visual Storyboard Bible

> Reusable visual elements for producing Dr Insanity-style true crime documentary videos. Every technique below was confirmed from frame-by-frame analysis of actual videos. This document is genre-level — apply it to any case.

---

## How to Use This Document

When writing a screenplay, tag each scene with a **visual element code** from this bible. Example:

```
[SCENE 14: Detective calls victim's ex-wife]
NARRATOR: "Detective Curtis decides to call the people who might know Dena best."
VISUAL: [DUAL-PIP-3D] caller=Detective Curtis, subject=Ex-wife | [WAVEFORM-AERIAL] property aerial
AUDIO: Phone call recording
DURATION: 90 seconds
```

The codes map directly to the sections below. An editor or automation pipeline reads these codes and assembles the corresponding visual assets.

---

## 1. Opening Sequence Elements

### [BRAND-STING] Channel Brand Card

**What:** Channel name on black with horror-style treatment.

| Property | Value |
|----------|-------|
| Duration | 2-3 seconds |
| Background | Pure black (#000000) |
| Text | Channel name in distressed/horror serif font |
| Color | Red (#DC1E1E) with neon glow/bloom |
| Effects | Floating dust particles, subtle glow animation |
| Audio | Low bass drone or silence |

**Fonts:** Creepster, Nosifer, Bleeding Cowboys, or custom distressed serif.

```python
# Generate brand sting frame
img = Image.new('RGB', (1920, 1080), (0, 0, 0))
d = ImageDraw.Draw(img)
font = ImageFont.truetype("creepster.ttf", 96)

# Glow layers (drawn underneath, progressively blurred)
for blur_radius in [24, 18, 12, 6]:
    glow = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((960, 540), "DR. INSANITY",
        fill=(180, 20, 20, 40), font=font, anchor="mm")
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    img = Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB')

# Sharp text on top
ImageDraw.Draw(img).text((960, 540), "DR. INSANITY",
    fill=(220, 30, 30), font=font, anchor="mm")
```

---

### [DISCLAIMER] Footage Disclaimer Card

**What:** Legal/credibility text over dark aerial imagery.

| Property | Value |
|----------|-------|
| Duration | 3-4 seconds |
| Background | Dark-graded satellite imagery of case location |
| Text line 1 | "All footage is real" — RED (#DC3232) |
| Text line 2 | "and obtained from U.S. law enforcement." — WHITE |
| Font | Clean sans-serif, ~32pt |

**Why it matters:** Establishes credibility immediately. Viewers need to trust that this is real footage, not dramatization. Also provides legal protection.

---

### [TRAILER] Flash-Forward Montage (First 80 Seconds)

**What:** A movie-trailer-style rapid-fire montage of the most dramatic moments from later in the video.

| Property | Value |
|----------|-------|
| Duration | 60-90 seconds |
| Clips | 5-7 flash-forward audio/video clips from later in the video |
| Clip duration | 3-8 seconds each |
| Transitions | Glitch effects + white flash frames (aggressive editing) |
| Audio | Most dramatic clips: 911 calls, confessions, bodycam discoveries |
| Background music | Percussion-driven, cinematic — louder than rest of video |
| Color grade | Darker than main video |

**Transition types in trailer:**
- **Glitch/distortion:** RGB channel shift, scan lines, frame displacement (2-4 frames)
- **White flash:** 1-3 frames of pure white between dramatic clips
- **Hard cuts:** Between less dramatic clips

**Template:**
1. Most dramatic bodycam clip (discovery, arrest, gunshot)
2. Narrator: "This is [name]. [Dramatic irony setup.]"
3. Flash-forward audio clip 2
4. Flash-forward audio clip 3
5. Narrator bridge
6. Flash-forward clips 4-6
7. Final cliffhanger clip → fade to black → [BRAND-STING]

---

## 2. Location & Map Elements

### [MAP-FLAT] Dark Satellite Top-Down View

**What:** Google Earth satellite imagery, heavily dark-graded with extreme vignette.

| Property | Value |
|----------|-------|
| Source | Google Earth screenshots or Google Earth Studio export |
| Color grade | Brightness 20%, saturation 30%, contrast boost |
| Vignette | Heavy — edges nearly black |
| Motion | Slow Ken Burns zoom in (0.001/frame) |
| Duration | 3-8 seconds |

**When to use:** Establishing the general area. First location introduction.

---

### [MAP-3D] 3D Google Earth Studio Oblique View

**What:** Angled/oblique 3D rendered view from Google Earth Studio showing buildings and terrain in perspective.

| Property | Value |
|----------|-------|
| Source | Google Earth Studio (free, requires Google account) |
| Color grade | Desaturated to near-B&W, darkened |
| Camera | Slow orbit or pan (Google Earth Studio keyframes) |
| Duration | 5-10 seconds |

**When to use:** Establishing town/city context. Background for dual PIP during phone calls. More cinematic than flat satellite.

**How to create in Google Earth Studio:**
1. Navigate to location
2. Set camera to oblique angle (~45°)
3. Create keyframe animation (slow pan/orbit)
4. Export as image sequence or MP4
5. Apply dark color grade in post

---

### [MAP-TACTICAL] Dark Map with Red Glowing Road Outlines

**What:** Nearly-black satellite imagery with roads traced in glowing red neon lines.

| Property | Value |
|----------|-------|
| Roads | Red (#DC3232) with glow/bloom effect |
| Background | Satellite imagery at ~20% brightness |
| Labels | White text for area names ("WILDERNESS AREA") |
| Vignette | Very heavy |
| Duration | 3-5 seconds |

**When to use:** Showing the remote/isolated context. Emphasizing how far from civilization the location is. Creating a tactical/surveillance feel.

**Build options:**
- MapLibre GL JS with custom dark style + red road layers
- Pillow: download OSM road vectors, trace in red with GaussianBlur glow on dark satellite
- After Effects: import satellite, mask roads, apply red glow

---

### [MAP-PULSE] Satellite + Animated Red Radar Pulse

**What:** Satellite view with glowing red concentric circles animating outward from the target property.

| Property | Value |
|----------|-------|
| Pulse | Red (#DC3232) concentric circles, expanding with decreasing opacity |
| Cycle | 1-second pulse cycle |
| Center dot | Always-visible solid red dot on the property |
| PIP | File Viewer photo of victim on left side |
| Duration | 5-8 seconds |

**When to use:** Pinpointing the exact property/crime scene. Usually paired with victim PIP.

---

### [MAP-ROUTE] Distance/Route Map

**What:** Map showing route between two locations with animated red line.

**When to use:** Showing distance between suspect's location and crime scene, or escape routes.

---

## 3. Character & People Elements

### [PIP-SINGLE] Single File Viewer Photo Overlay

**What:** One person's photo in a "File Viewer" window chrome, overlaid on background footage.

| Property | Value |
|----------|-------|
| Window chrome | "File Viewer" title bar (dark gray) |
| Photo size | ~350-450px wide |
| Position | Left side of frame |
| Name label | White text below photo (first name or full name) |
| Animation | Fade in (0.5s), hold 4-8 seconds, fade out |
| Background | Bodycam footage, aerial, or B-roll continues playing |

**When to use:** Introducing or referencing a person during narration or phone calls.

**Photo selection guidelines:**
- **Victims:** Warm, humanizing photo. Smiling, with family/pets. Sometimes B&W for emotional weight.
- **Suspects:** Neutral or booking photo. Color. Cold treatment.
- **Multiple photos per person:** Use different photos for different emotional contexts (e.g., warm puppy photo for sad moments, outdoor adventure photo for factual establishing).

---

### [PIP-DUAL] Dual File Viewer Photos (Side by Side)

**What:** Two File Viewer photos positioned side by side, showing the relationship between two people.

| Property | Value |
|----------|-------|
| Layout | Two photos horizontally centered, ~100px gap between |
| Position | Upper-center of frame |
| Name labels | Below each photo |
| Background | [MAP-3D] Google Earth oblique view or dark B-roll |

**When to use:** During phone calls where both parties are identified (caller + subject, detective + witness). Establishes the relationship visually.

---

### [MUGSHOT-CARD] Charges / Sentence Split Screen

**What:** Full-screen graphic with mugshot on right, charges text on left.

| Property | Value |
|----------|-------|
| Layout | Mugshot ~40% right, text ~60% left |
| Mugshot | Color booking photo, cinderblock wall visible |
| Headers | "Charges:" and "Sentence:" in bold red (#DC3232) |
| Body text | White, dash-bulleted list |
| Background | Near-black (#0A0A0F) |
| Duration | 5-8 seconds |

**When to use:** Resolution section — final charges and sentencing information.

---

### [INTERROGATION] Interrogation Room Footage

**What:** Real police interrogation room footage — suspect seated at table, grey walls, overhead camera angle.

| Property | Value |
|----------|-------|
| Source | FOIA / court records |
| Overlay | [LOWER-THIRD] with suspect name + context |
| Color grade | Slightly desaturated, blue/grey tint |
| Caption | [CAPTION-ANIMATED] for any audible dialogue |
| Purpose | Shows suspect's demeanor under questioning |

**When to use:** Resolution section — after arrest. Usually brief (suspect lawyers up).

---

### [COURTROOM] Courtroom Footage

**What:** Real courtroom footage from legal proceedings — judge at bench, flags, formal setting.

| Property | Value |
|----------|-------|
| Source | Court TV / public court recordings |
| Duration | 3-5 seconds |
| Color grade | Natural, slightly desaturated |
| Purpose | Establishes legal proceedings, conviction, sentencing |

**When to use:** Resolution/epilogue — showing trial proceedings, arraignment, sentencing.

---

## 4. Investigation & Evidence Elements

### [POLICE-DB] Fake Police Database Application

**What:** Full custom mock-up of a law enforcement database application window.

| Property | Value |
|----------|-------|
| Window title | "Police Database" with person icon |
| Menu bar | File, Edit, Search, View, Help |
| Tabs | DASHBOARD / RECORDS / CASES / REPORTS |
| Search bar | "Search This Database" (top-right) |
| Content | "SEARCH RESULTS:" + photo + data fields |
| Fields | Name, Age, Address, Details (italic labels, white values) |
| Key detail | Critical info in RED (e.g., "Missing for 2 months") |
| Background | Blue Windows desktop behind app window |

**When to use:** When narrator describes detectives researching background, running database checks, looking up records. Bridges narration-heavy investigation sections with no available real footage.

**Variations:**
- Different search results for different people (victim, suspect, witnesses)
- Update the "Details" field as the investigation progresses
- Add/remove tabs or content as case evolves

---

### [DESKTOP-PHOTOS] Windows Desktop with Photo Viewer Windows

**What:** Fake Windows desktop with multiple Photo Viewer windows showing case photos/documents.

| Property | Value |
|----------|-------|
| Wallpaper | Red/warm-tinted OR standard blue Windows |
| Windows | 2-3 overlapping Photo Viewer windows |
| Content | Victim photos (B&W), suspect photos, missing person flyers, evidence photos |
| Effects | Lens flare / light streaks |

**When to use:** When showing what detectives are looking at — photos, flyers, evidence documents.

**Variations by case stage:**
- **Early investigation:** Missing person flyer + victim photo
- **Mid investigation:** Victim + suspect photos side by side
- **Financial investigation:** Bank statements, property records
- **Evidence review:** Crime scene photos, forensic reports

---

### [EVIDENCE-CLOSEUP] Evidence with Red Highlights

**What:** Close-up of physical evidence with red circles, arrows, or boxes highlighting key details.

| Property | Value |
|----------|-------|
| Red circle | #FF3333, 3px stroke |
| Red arrow | #FF3333, pointing to key detail |
| Red box/underline | Under key text in documents |
| Animation | Circle/arrow fades in 0.5s after clip starts |

**When to use:** When evidence needs viewer attention directed to a specific detail.

---

### [EVIDENCE-DISPLAY] Composed Evidence Presentation

**What:** Physical evidence items arranged and photographed/rendered against a blurred bokeh background. NOT from bodycam — this is a staged/composed shot for dramatic impact.

| Property | Value |
|----------|-------|
| Duration | 3-5 seconds per item |
| Background | Blurred/bokeh — soft, out-of-focus. Warm or neutral tones |
| Items | Evidence items arranged prominently (bleach bottles, tools, weapons) |
| Lighting | Soft, even lighting — product photography style |
| Caption | Animated caption at bottom describing the item |
| Purpose | Makes physical evidence look cinematic and significant |

**When to use:** During the search/climax when key evidence is found. Elevates mundane items (bleach, tools) into dramatic reveals.

**Example items seen:** Bleach jug, pink spray bottle, power drill — arranged together on the same blurred background in a single composed frame.

---

### [BODY-DIAGRAM] Forensic Illustration

**What:** Hand-drawn line illustration of human body showing injuries, bullet wounds, or cause of death.

| Property | Value |
|----------|-------|
| Duration | 4-6 seconds |
| Style | Clean line drawing / medical sketch — NOT photographic |
| Background | White or light neutral |
| Annotations | Labels pointing to injury locations |
| Purpose | Shows cause of death without graphic imagery |

**When to use:** When describing cause of death or injuries. Avoids graphic content while communicating medical/forensic details clearly.

---

### [DOCUMENT-MOCKUP] Phone/Document Display

**What:** Mobile phone screen or legal document displayed on a dark background with key text highlighted in red.

| Property | Value |
|----------|-------|
| Duration | 3-5 seconds |
| Background | Dark green or dark neutral |
| Content | Text list, legal document, or phone screen |
| Highlights | Key items highlighted in RED |
| Purpose | Shows documentary evidence (text messages, legal filings, lists) |

**When to use:** When referencing specific documents, text messages, court filings, or lists of evidence/charges.

---

### [SPLIT-INFO] Split-Screen Information Panel

**What:** Screen divided: text/data card on one side, footage on the other. Used for key information reveals alongside visual context.

| Property | Value |
|----------|-------|
| Layout | Left: text/info card on dark bg. Right: bodycam/exterior footage |
| Duration | 4-8 seconds |
| Text styling | White text on dark background with teal accent headers |
| Purpose | Presents key facts alongside visual context without interrupting footage flow |

**When to use:** When introducing a new character with extensive background info, or when presenting timeline/facts that need context from the footage.

---

### [TEXT-CHAT] Text Message / Chat Recreation

**What:** Styled recreation of text message conversations (iMessage, SMS, Snapchat, etc.) on a dark background.

| Property | Value |
|----------|-------|
| Duration | 4-8 seconds per exchange |
| Style — iMessage | Blue sender bubbles (right), grey receiver bubbles (left), iOS chrome |
| Style — SMS | Green sender bubbles (right), grey receiver bubbles (left) |
| Background | Dark blur or phone-frame mockup on near-black |
| Animation | Messages appear one by one with typing delay (0.3-0.5s per message) |
| Timestamp | Grey, small, between message groups |
| Key text | Highlighted with red underline or glow on critical messages |
| Purpose | Shows text evidence in the format audiences recognize instantly |

**When to use:** When referencing specific text messages, DMs, or chat conversations entered as evidence. More effective than [DOCUMENT-MOCKUP] for conversational text because the bubble format implies back-and-forth.

**Variants:**
- **Snapchat:** Yellow header bar, ghost icon, recipient name. Messages in chat bubble style
- **Facebook/Instagram DM:** Platform-specific bubble colors and chrome
- **Generic:** When platform isn't specified — use simple dark bubbles on dark background

---

### [SOCIAL-POST] Social Media Post Mockup

**What:** Recreation of a social media post (Facebook, Instagram, Snapchat, Twitter/X) with platform-specific styling.

| Property | Value |
|----------|-------|
| Duration | 3-5 seconds |
| Layout | Platform chrome (header, profile pic, timestamp) + post content |
| Background | Dark blur behind the post card |
| Highlight | Key text or image in the post highlighted with red circle/underline |
| Animation | Fade in, hold, optional slow zoom on the key detail |
| Purpose | Shows social media evidence in authentic-looking format |

**When to use:** When a suspect's social media post, a victim's last post, or any social media evidence is referenced. Snapchat videos/stories, Facebook updates, Instagram posts.

---

### [TIMELINE-SEQUENCE] Animated Timeline

**What:** Horizontal or vertical animated timeline showing progression of events across dates. A cursor or highlight moves along the line hitting dated nodes.

| Property | Value |
|----------|-------|
| Duration | 5-10 seconds |
| Layout | Horizontal line with nodes, dates above, event labels below |
| Colors | Line: grey. Active/past nodes: red. Current node: white pulsing. Future: dim grey |
| Background | Near-black (#0A0A0F) |
| Animation | Cursor sweeps from left to right, nodes illuminate as reached |
| Purpose | Shows how events relate temporally — essential for cases spanning months/years |

**When to use:** At act transitions to establish the temporal arc. Especially valuable for Archetype B (trial-centric) and D (cold case) where the timeline spans years. Replaces a series of [TIMELINE-MARKER] cards when you need the viewer to see the full picture at once.

---

### [EVIDENCE-BOARD] Connection/Conspiracy Board

**What:** Red-string-on-corkboard style visualization showing connections between suspects, victims, evidence, and events.

| Property | Value |
|----------|-------|
| Duration | 5-8 seconds |
| Layout | Dark corkboard background. Photos/cards pinned. Red string connecting related items |
| Photos | [PIP-SINGLE] style File Viewer photos for each person |
| Connections | Red string (#DC3232) with labels on lines (e.g., "married", "employed", "stole from") |
| Animation | Elements fade in progressively as narrator describes connections. Strings draw between nodes |
| Purpose | Maps complex relationship webs for cases with many players |

**When to use:** Cases with 5+ connected individuals where the relationships are central to understanding motive/opportunity. Murdaugh-scale cases with family, law firm, victims, co-conspirators. Also useful for financial crime webs.

---

### [FLOW-DIAGRAM] Financial / Process Flow

**What:** Animated diagram showing money movement, evidence chain, or process flow between entities.

| Property | Value |
|----------|-------|
| Duration | 6-10 seconds |
| Layout | Nodes (boxes/circles) connected by animated arrows |
| Colors | Nodes: dark bg with white text. Arrows: red for money/danger, teal for info |
| Amounts | Dollar figures in red on arrows or nodes |
| Animation | Arrows draw in sequence as narrator describes the flow. Amounts appear on draw |
| Background | Near-black (#0A0A0F) |
| Purpose | Visualizes money laundering schemes, fraud networks, evidence chains |

**When to use:** Financial crime cases with complex money movement (Forge account scheme, insurance fraud). Also useful for showing chains of custody, drug distribution networks, or evidence processing.

---

### [NEWS-MONTAGE] Headline Crawl

**What:** Stack of newspaper/web headlines appearing one after another, showing how a case played out in media.

| Property | Value |
|----------|-------|
| Duration | 4-6 seconds |
| Layout | Headlines stacked vertically, each slightly overlapping, slight rotation (-2° to +2°) |
| Style | Newspaper headline font (bold serif) on white/newsprint background cards |
| Animation | Headlines slide in from alternating sides, each 0.3s apart |
| Background | Dark with slight paper texture |
| Purpose | Shows public impact and media coverage in seconds |

**When to use:** High-profile cases where media coverage is part of the story. Transition element between investigation and trial in Archetype B cases. Also useful for cold cases where the reopening was triggered by media attention.

---

### [CENSOR-BLUR] Content Censoring

**What:** Soft black gaussian blur over sensitive areas.

| Property | Value |
|----------|-------|
| Method | Localized gaussian blur or black oval mask |
| Style | Soft black blur (NOT pixelation/mosaic) |
| Coverage | Only the specific sensitive area |

**When to use:** Body discovery location, graphic injury evidence, faces of minors.

---

## 5. Audio Visualization Elements

### [WAVEFORM-AERIAL] 911/Phone Call on Aerial Background

**What:** Red audio waveform + animated captions overlaid on dark aerial property footage.

| Property | Value |
|----------|-------|
| Background | Dark aerial/drone shot of the actual property |
| Waveform | Red (#DC3232) jagged line with red glow/bloom, upper-center |
| Captions | Bold white text, center-bottom, phrase-by-phrase animated |
| Audio | 911 call or phone recording playing |

**This is NOT black background + waveform.** The property footage keeps the viewer grounded in the location while the waveform provides audio visualization.

**Layer stack (bottom to top):**
1. Dark aerial footage (Ken Burns zoom)
2. Red audio waveform with glow
3. White animated captions

#### Preventing Waveform Staleness

The waveform-on-aerial composition gets stale by the 3rd phone call. **Vary the background for each call:**

| Call # | Background Variation |
|--------|---------------------|
| 1st call | [MAP-FLAT] aerial of property (classic) |
| 2nd call | [MAP-3D] oblique orbit of town/area |
| 3rd call | Bodycam B-roll from the scene (dark, slow) |
| 4th call | [MAP-TACTICAL] with red road outlines |
| Most important call | **Drop the waveform entirely.** Full-screen [CAPTION-ANIMATED] on near-black. The absence of the expected visual signals "this one matters more." |

Also vary the character elements during calls:
- Use [PIP-SINGLE] or [PIP-DUAL] over the waveform when both parties are identified
- Shift waveform position (upper-left, upper-right) to accommodate PIP overlays
- For calls where the suspect is speaking, add subtle red tint to the background

---

### [WAVEFORM-DARK] Audio on Dark Background (Fallback)

**What:** When no aerial footage is available, use dark atmospheric B-roll as background for waveform.

---

## 6. Text & Graphics Elements

### [LOWER-THIRD] Character Introduction

| Property | Value |
|----------|-------|
| Bar | Semi-transparent dark (#000000 70% opacity), bottom-left |
| Accent | Red line (#C81E1E) at top of bar |
| Name | White, ~42pt, bold |
| Role | Gray (#B4B4B4), ~28pt |
| Animation | Slide-in from left, red line draws in, text fades in sequentially |
| Duration | 4-6 seconds hold, then fade out |

---

### [QUOTE-CARD] Key Quote Highlight

| Property | Value |
|----------|-------|
| Background | Near-black (#0A0A0F) |
| Quote mark | Large red (#DC3232), ~120pt |
| Text | White, ~52pt, centered |
| Attribution | Gray, ~30pt, below quote |
| Duration | 3-5 seconds |

**When to use:** Damning statements. "If I could kill Craig and get away with it, I'd do it."

---

### [TIMELINE-MARKER] Time Jump Graphic

| Property | Value |
|----------|-------|
| Date | White, ~72pt, centered |
| Red accent line | Above the date |
| Description | Gray, ~36pt, below date |
| Duration | 2-3 seconds |

---

### [FINANCIAL-CARD] Dollar Amount Reveal

| Property | Value |
|----------|-------|
| Amount | Red (#DC3232), ~96pt, centered |
| Description | Gray, ~32pt, below amount |
| Animation | Fade in with slight scale-up |

---

### [CAPTION-ANIMATED] Animated Subtitles

| Property | Value |
|----------|-------|
| Style | Bold white with dark outline/shadow |
| Position | Bottom-center |
| Animation | Word-by-word or phrase-by-phrase highlight |
| Present | Throughout entire video (narrator + real audio) |

---

## 7. Transition Elements

### [TR-HARD] Hard Cut
Default. No effect. ~55% of transitions.

### [TR-GLITCH] Glitch/Distortion
RGB shift + scan lines + frame displacement. 2-4 frames. **Budget: 8% max.** Reserve exclusively for trailer and 3-4 biggest reveals (Level 3 bombshells). Using this on anything less than a genuine power-shift moment dilutes its impact.

### [TR-FLASH] White Flash Frame
1-3 frames of pure white. **Budget: 5% max.** Trailer + 2-3 shocking reveals only. More than ~15 in a 50-minute video causes physical discomfort.

### [TR-FADE] Fade to/from Black
0.5-1 second. Used for time jumps, act transitions, and emotional beats. ~12% of transitions.

### [TR-DISSOLVE] Cross-Dissolve
Soft blend. Used for photo introductions, location establishing, mood shifts (warm → dark). ~8%.

### [TR-ZOOM] Ken Burns Zoom/Pan
Applied to **90% of static images.** Reserve 3-5 moments of intentional stillness (see [STILL] below).

### [TR-SMASH] Smash Cut
A hard cut with deliberate **tonal whiplash** — calm scene to sudden loud scene, or sponsor → back to murder. Distinct from [TR-HARD] because the contrast is the point. ~3%.

### [TR-LCUT] L-Cut / J-Cut
Audio from the next scene starts before the visual cuts (L-cut) or audio from the previous scene trails into the next visual (J-cut). Essential documentary editing tool that makes footage feel like a story rather than a slideshow. ~2%.

### [STILL] Intentional Stillness
**Not a transition — a modifier.** A static image or held frame with NO Ken Burns motion, NO music, minimal or no narration. Used for 3-5 moments of maximum emotional weight per video:
- Body discovery / crime scene (held frame, censored if needed)
- Victim memorial photo (warm photo, no motion, 3-4 seconds of silence)
- Verdict landing ("Guilty" — hold the courtroom frame dead still)
- Key silence beat (let bodycam audio play alone for 10-15 seconds)

The sudden absence of motion after 45 minutes of constant movement is disorienting and powerful. Use sparingly — the rarity is what makes it work.

---

## 8. Persistent / Always-On Elements

### [VIGNETTE] Edge Darkening
On every frame. Focuses eye on center.

### [COLOR-GRADE] Dark Desaturated Crime Look
```bash
ffmpeg -vf "eq=brightness=-0.08:saturation=0.6:contrast=1.2,colorbalance=bs=0.1:bm=0.05"
```

### [LETTERBOX] Cinematic Black Bars
Top and bottom. ~60-80px each. Creates 2.35:1 widescreen feel. Applied to footage, NOT to full-screen graphics.

---

## 9. Screenplay Visual Tagging Reference

When writing a screenplay, tag each scene like this:

```
[SCENE 1: TRAILER]
VISUAL: [TRAILER] — 7 flash-forward clips with [TR-GLITCH] and [TR-FLASH]
AUDIO: Bodycam "What's that smell?" + narrator dramatic irony + phone calls
DURATION: 80 seconds

[SCENE 2: BRAND + DISCLAIMER]
VISUAL: [BRAND-STING] → [DISCLAIMER] → [MAP-FLAT] wide establishing
DURATION: 10 seconds

[SCENE 3: LOCATION ESTABLISHING]
VISUAL: [MAP-FLAT] zoom in → [MAP-PULSE] with [PIP-SINGLE] victim → [WAVEFORM-AERIAL]
AUDIO: Narrator "It's a late May evening in Cloudcroft, New Mexico..."
DURATION: 20 seconds

[SCENE 4: FIRST 911 CALL]
VISUAL: [WAVEFORM-AERIAL] property bg + [PIP-DUAL] caller + victim
AUDIO: 911 call recording
CAPTION: [CAPTION-ANIMATED]
DURATION: 90 seconds

[SCENE 5: OFFICERS ARRIVE]
VISUAL: Bodycam footage + [LOWER-THIRD] "Deputy Pensor — Otero County Sheriff"
AUDIO: Bodycam audio + narrator bridges
DURATION: 3 minutes

[SCENE 12: DETECTIVE RESEARCHES BACKGROUND]
VISUAL: [POLICE-DB] search results for victim → [DESKTOP-PHOTOS] missing person flyer
AUDIO: Narrator describing investigation
DURATION: 60 seconds

[SCENE 18: DAMNING QUOTE FROM EX-HUSBAND]
VISUAL: [QUOTE-CARD] "If I could kill Craig and get away with it, I'd do it."
AUDIO: Phone call recording of ex-husband
DURATION: 5 seconds (hold on quote)

[SCENE 25: SPONSOR]
VISUAL: Warm commercial footage, [TR-HARD] in/out
AUDIO: First-person sponsor read
DURATION: 90 seconds

[SCENE 30: BODY FOUND]
VISUAL: Bodycam night footage + [PIP-SINGLE] victim + [CENSOR-BLUR]
AUDIO: Bodycam audio + narrator
DURATION: 2 minutes

[SCENE 32: CHARGES]
VISUAL: [MUGSHOT-CARD] suspect mugshot + charges/sentence
AUDIO: Narrator reading charges
DURATION: 8 seconds
```

---

## 10. Color Palette Reference

### Core Palette

| Element | Hex | Usage |
|---------|-----|-------|
| Background | `#0A0A0F` | Graphics, cards |
| Primary text | `#FFFFFF` | All body text |
| Secondary text | `#B4B4B4` | Roles, descriptions, labels |
| Lower third bar | `rgba(0,0,0,180)` | Character introductions |
| Caption text | `#FFFFFF` + `#000000` stroke | Animated subtitles |

### Four Semantic Accents

| Color | Hex | Meaning | Used On |
|-------|-----|---------|---------|
| **Red** | `#DC3232` | Danger, alert, charges | Disclaimers, map pulses, road outlines, evidence highlights, mugshot charges, financial amounts, [EVIDENCE-BOARD] connections |
| **Teal** | `#00D4AA` | Information, identity, context | Map labels, location pins, brand sting glow, lower third accents, [FLOW-DIAGRAM] info arrows, [TIMELINE-SEQUENCE] nodes, informational quote cards |
| **Warm gold** | `#D4A843` | Victim, family, humanity | Victim photo color grade, family moments, memorial sections, victim-voiced quote cards |
| **Cool blue-grey** | `#7A8FA6` | Procedural, law enforcement | Police procedural sections, interrogation overlays, forensic details, bodycam UI elements |

### Accent Variants

| Element | Hex | Notes |
|---------|-----|-------|
| Lower third accent line | `#C81E1E` | Red line on lower thirds |
| Highlight red (circles/arrows) | `#FF3333` | Brighter red for evidence markup |
| Brand sting | `#DC1E1E` or `#00D4AA` + bloom | May alternate per video |
| "Missing/danger" text | `#DC3232` | Key details in Police Database, charges |

> **Quote card color follows content, not format:**
> - Damning/threatening quotes → **red** accent
> - Informational/contextual quotes → **teal** accent
> - Victim's own words → **warm gold** accent
>
> **Warm gold and cool blue-grey** are used sparingly — primarily in color grading shifts and occasional overlay accents. Red and teal remain the dominant pair. The expanded palette prevents monotony across 50 minutes without breaking the established dark aesthetic.

---

## 11. Asset Checklist Per Video

Before production, gather or generate these assets:

### Must Source (FOIA / Court Records)
- [ ] Bodycam footage (multiple visits/scenes — need 20+ min)
- [ ] 911 call recording(s) (2-3 calls)
- [ ] Detective phone call recordings
- [ ] Interrogation footage (if available) → [INTERROGATION]
- [ ] Courtroom footage (if available) → [COURTROOM]
- [ ] Victim photo(s) — at least 2 (warm + neutral)
- [ ] Suspect mugshot
- [ ] Evidence photos/documents (if available from court filings)
- [ ] Forensic/autopsy report (for body diagram reference) → [BODY-DIAGRAM]

### Must Generate (Pillow / FFmpeg / Google Earth)
- [ ] Brand sting frame → [BRAND-STING]
- [ ] Disclaimer card → [DISCLAIMER]
- [ ] Satellite views (flat + 3D) → [MAP-FLAT], [MAP-3D]
- [ ] Tactical map with red roads → [MAP-TACTICAL]
- [ ] Red pulse animation frames → [MAP-PULSE]
- [ ] File Viewer PIP overlays (per character) → [PIP-SINGLE], [PIP-DUAL]
- [ ] Police Database mockup(s) → [POLICE-DB]
- [ ] Desktop Photo Viewer mockup(s) → [DESKTOP-PHOTOS]
- [ ] Lower thirds (per character) → [LOWER-THIRD]
- [ ] Quote cards (teal accent) → [QUOTE-CARD]
- [ ] Timeline markers → [TIMELINE-MARKER]
- [ ] Financial cards → [FINANCIAL-CARD]
- [ ] Charges/sentence card → [MUGSHOT-CARD]
- [ ] 911 waveform visualizations → [WAVEFORM-AERIAL]
- [ ] Evidence display shots (bokeh bg) → [EVIDENCE-DISPLAY]
- [ ] Body diagram illustration → [BODY-DIAGRAM]
- [ ] Document/phone mockups → [DOCUMENT-MOCKUP]
- [ ] Split info panels → [SPLIT-INFO]
- [ ] Text message recreations (if applicable) → [TEXT-CHAT]
- [ ] Social media post mockups (if applicable) → [SOCIAL-POST]
- [ ] Connection/evidence board (if 5+ people) → [EVIDENCE-BOARD]
- [ ] Financial/process flow diagram (if applicable) → [FLOW-DIAGRAM]
- [ ] Animated timeline (if case spans 6+ months) → [TIMELINE-SEQUENCE]
- [ ] Headline montage (if high-profile case) → [NEWS-MONTAGE]
- [ ] Animated captions (ASS/SRT file) → [CAPTION-ANIMATED]
- [ ] Background music selection
- [ ] TTS narration audio (ElevenLabs or equivalent)
