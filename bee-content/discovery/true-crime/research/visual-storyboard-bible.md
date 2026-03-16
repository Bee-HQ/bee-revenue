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
Default. No effect. Used 50% of the time.

### [TR-GLITCH] Glitch/Distortion
RGB shift + scan lines + frame displacement. 2-4 frames. Used in trailer and at tension peaks.

### [TR-FLASH] White Flash Frame
1-3 frames of pure white. Impact cut. Used in trailer and for major reveals.

### [TR-FADE] Fade to/from Black
0.5-1 second. Used for time jumps and act transitions.

### [TR-DISSOLVE] Cross-Dissolve
Soft blend. Used for photo introductions.

### [TR-ZOOM] Ken Burns Zoom/Pan
Applied to all static images. Nothing on screen is ever still.

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

| Element | Hex | Usage |
|---------|-----|-------|
| Background | `#0A0A0F` | Graphics, cards |
| Primary text | `#FFFFFF` | All body text |
| Secondary text | `#B4B4B4` | Roles, descriptions, labels |
| Brand red | `#DC3232` | Quotes, amounts, highlights, waveforms, road outlines, headers |
| Lower third bar | `rgba(0,0,0,180)` | Character introductions |
| Lower third accent | `#C81E1E` | Red line on lower thirds |
| Caption text | `#FFFFFF` + `#000000` stroke | Animated subtitles |
| Highlight red | `#FF3333` | Circles, arrows on evidence |
| Brand sting | `#DC1E1E` + bloom | Channel name |
| "Missing/danger" text | `#DC3232` | Key details in Police Database, charges |

---

## 11. Asset Checklist Per Video

Before production, gather or generate these assets:

### Must Source (FOIA / Court Records)
- [ ] Bodycam footage (multiple visits/scenes — need 20+ min)
- [ ] 911 call recording(s) (2-3 calls)
- [ ] Detective phone call recordings
- [ ] Interrogation footage (if available)
- [ ] Victim photo(s) — at least 2 (warm + neutral)
- [ ] Suspect mugshot
- [ ] Evidence photos/documents (if available from court filings)

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
- [ ] Quote cards → [QUOTE-CARD]
- [ ] Timeline markers → [TIMELINE-MARKER]
- [ ] Financial cards → [FINANCIAL-CARD]
- [ ] Charges/sentence card → [MUGSHOT-CARD]
- [ ] 911 waveform visualizations → [WAVEFORM-AERIAL]
- [ ] Animated captions (ASS/SRT file) → [CAPTION-ANIMATED]
- [ ] Background music selection
- [ ] TTS narration audio (ElevenLabs or equivalent)
