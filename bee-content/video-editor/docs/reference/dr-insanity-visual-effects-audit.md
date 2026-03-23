# Visual Effects Audit: Dr Insanity — "Secret Killer Leads Cops Into Her $3,000,000 Murder Mansion"

**Source:** https://www.youtube.com/watch?v=s6CXNbzKlks
**Channel:** Dr Insanity (4.37M subscribers)
**Duration:** 49:56
**Genre:** True crime documentary
**Date audited:** 2026-03-22

---

## Summary of Effects Found

This video uses a consistent set of ~25 visual techniques. The production is heavily bodycam/interview footage-driven, with overlays and graphics used to add context, identify people, show locations, and emphasize key moments.

---

## 1. CAPTIONS / SUBTITLES

### 1a. Standard Captions (White)
- **Timestamps:** Throughout (e.g., 0:30, 8:20, 20:00, 23:00, 30:00)
- **Style:** White text, centered bottom or upper-center, with dark text stroke/outline for readability
- **Font:** Sans-serif, medium weight
- **Animation:** Word-by-word or phrase-by-phrase appearance
- **Status:** HAVE (CaptionOverlay component)

### 1b. Highlighted Keyword Captions (Yellow)
- **Timestamps:** 0:30, 1:15, 10:00, 48:00
- **Style:** Yellow/gold text with dark outline, same positioning as standard
- **Usage:** Used during bodycam/interview audio where speaker is visible
- **Status:** HAVE (CaptionOverlay supports color styles)

### 1c. Colored Emphasis Words (Red)
- **Timestamp:** 0:30
- **Style:** Individual words colored RED within a caption line (e.g., "bl**d" in red while rest is yellow)
- **Usage:** Dramatic emphasis on violent/important keywords
- **Status:** PARTIAL — CaptionOverlay has emphasis but may need per-word color control

---

## 2. SOURCE LABELS / BADGES

### 2a. Source Type Badge
- **Timestamps:** 0:55 "[ACTUAL]", 2:00 "[REENACTMENT]", 10:00 "[ACTUAL PHOTO]"
- **Style:** Small white text in brackets, bottom-left corner, semi-transparent
- **Font:** Monospace or small sans-serif, all-caps
- **Purpose:** Distinguishes actual footage from reenactments, photos, etc.
- **Status:** NEED — New component: `SourceBadge`

---

## 3. PHOTO CARDS / PERSON IDENTIFICATION

### 3a. Photo Card with Name (File Viewer Window)
- **Timestamps:** 0:15, 13:00, 15:00, 26:00, 44:00
- **Style:** Photo displayed inside a fake OS "Photo Viewer" or "File Viewer" window frame with:
  - Title bar ("Photo Viewer" / "File Viewer")
  - Menu bar (File, Edit, Image, View, Help)
  - Minimize/maximize/close buttons
  - Name label below the photo (e.g., "CRAIG THETFORD", "BILL CAISSE", "LESLIE")
  - Optional role/relationship subtitle (e.g., "Ex-husband")
- **Animation:** Slides in, slight scale animation
- **Face blur:** Often applied to protect identity
- **Status:** NEED — New component: `PhotoViewerCard` (OS window mockup frame + name label)

### 3b. Dual Photo Cards (Side by Side)
- **Timestamps:** 11:00, 26:00
- **Style:** Two Photo Viewer windows placed side by side for comparison
- **Usage:** Showing two people being discussed (e.g., victim and suspect)
- **Status:** NEED — Extension of PhotoViewerCard with multi-card layout

### 3c. Photo Inset (PiP on footage)
- **Timestamp:** 0:15, 6:00, 35:00
- **Style:** Small photo overlay on top-left or top-center of footage, with name label
- **Usage:** Identifying person while bodycam/aerial plays
- **Status:** HAVE (PictureInPicture component, but may need name label variant)

---

## 4. MAP / AERIAL EFFECTS

### 4a. Satellite/Aerial View with Pulsing Location Marker
- **Timestamp:** 7:00
- **Style:** Google Earth-style satellite imagery with animated blue/cyan pulsing dot marker
- **Animation:** Zoom-in from high altitude, marker pulses
- **Status:** HAVE (AnimatedMap component)

### 4b. Aerial View with Red Highlight/Marking
- **Timestamps:** 6:00, 35:00
- **Style:** Satellite view with red painted/drawn highlights on specific areas (blood trail, path, location emphasis)
- **Animation:** Red marking appears/draws on
- **Status:** NEED — New feature: `MapAnnotation` / red highlight overlay on aerial

### 4c. Aerial View with Photo Inset + Quote Callouts
- **Timestamp:** 35:00
- **Style:** Satellite map base with:
  - Photo inset with lower-third name
  - Red location markers
  - Quote text callout boxes with quoted text
- **Usage:** Complex composite showing where events happened + who said what
- **Status:** PARTIAL — AnimatedMap exists but needs layered annotation support (callout boxes, photo insets on map)

---

## 5. TEXT OVERLAYS / LABELS

### 5a. Bold Dramatic Label
- **Timestamp:** 38:00
- **Style:** Large uppercase white text on black background bar, positioned top-left
- **Content:** "UNLOCKED DOOR" — contextual labels for what's being shown
- **Animation:** Likely a quick slide-in or cut
- **Status:** HAVE (TextOverlay component, but may need bar-background variant)

### 5b. Stacked Bullet List (Charge Sheet / Summary)
- **Timestamp:** 49:10
- **Style:** Multiple lines of uppercase bold monospace text, each on its own semi-transparent black bar, staggered vertically down the screen
- **Content:** "INTENTIONALLY SHOT CRAIG" / "MOVED AND HID THE BODY" / "LIED ABOUT HIS WHEREABOUTS" / "LOOTED SHARED ASSETS"
- **Background:** Blurred montage of case footage
- **Animation:** Lines appear one by one (stagger reveal)
- **Status:** NEED — New component: `BulletList` / `ChargeSheet` (staggered text bars)

### 5c. Charges/Sentencing Info Card
- **Timestamp:** 49:30
- **Style:** Split layout — text on left half, close-up photo on right half
  - Red header text: "Charges:" and "Sentence:"
  - White body text with details
- **Animation:** Text appears with reveal animation
- **Status:** NEED — New component: `SentencingCard` or `InfoCard` (split photo + structured text)

---

## 6. NOTEPAD / TYPEWRITER EFFECT

### 6a. Fake Notepad Window with Typewriter Text
- **Timestamp:** 44:00
- **Style:** Dark-themed "Notepad" OS window with:
  - Title bar + menu bar (File, Edit, Search, View, Help)
  - Bullet-point text typed out character by character (typewriter effect)
  - Blinking cursor
- **Usage:** Summarizing key findings, phone call notes, witness statements
- **Animation:** Text appears as if being typed in real-time
- **Status:** PARTIAL — TextOverlay has typewriter effect, but needs Notepad window frame wrapper

---

## 7. QUOTE / TEXT CALLOUTS ON FOOTAGE

### 7a. Quote Callout Box
- **Timestamp:** 35:00
- **Style:** Semi-transparent dark box with quoted text in serif/monospace font, positioned on aerial/map view
- **Content:** Quoted witness statements (e.g., "Deana was here", "She was trying to h*rm herself")
- **Status:** HAVE (QuoteCard exists but this is a lighter inline variant for map overlays)

---

## 8. COLOR GRADING / VISUAL TREATMENTS

### 8a. Desaturation / Black & White
- **Timestamp:** 17:30
- **Style:** Full B&W or heavily desaturated footage
- **Usage:** Flashbacks, dramatic emphasis
- **Status:** HAVE (COLOR_FILTERS in SafeMedia)

### 8b. Dark/Blue Cinematic Tint
- **Timestamp:** ~46:30
- **Style:** Blue-tinted dark color grade on B-roll (forest at night)
- **Usage:** Atmospheric establishing shots
- **Status:** HAVE (dark_crime, cold_blue presets)

### 8c. Teal/Cyan Animated Background
- **Timestamps:** 11:00, 15:00, 44:00
- **Style:** Abstract motion graphic background (flowing teal/cyan light streaks) behind Photo Viewer windows
- **Purpose:** Backdrop when showing photos/graphics instead of footage
- **Status:** NEED — New component: `AnimatedBackground` (motion graphics loop)

---

## 9. FACE BLUR / CENSORING

### 9a. Face Blur
- **Timestamps:** 3:00, 13:00, 15:00, 26:00
- **Style:** Gaussian blur applied to faces to protect identity
- **Tracking:** Follows face movement in video
- **Status:** OUT OF SCOPE for Remotion (requires ML face detection + tracking; done in FFmpeg/post)

### 9b. Content Blur
- **Timestamp:** 40:00
- **Style:** Area blur on graphic content (blood, bodies, etc.)
- **Status:** OUT OF SCOPE (same as face blur — post-processing)

---

## 10. TRANSITIONS

### 10a. Hard Cut
- **Throughout**
- **Style:** Direct cut between clips, most common transition
- **Status:** HAVE (default)

### 10b. Cross-Dissolve
- **Various points between sections**
- **Style:** Gradual opacity blend between two clips
- **Status:** HAVE (TransitionRenderer DISSOLVE)

### 10c. Fade to/from Black
- **Section transitions**
- **Style:** Fade out to black, hold, fade in to new section
- **Status:** HAVE (TransitionRenderer FADE_FROM_BLACK)

---

## 11. CAMERA/FOOTAGE EFFECTS

### 11a. Ken Burns on Photos
- **Timestamps:** 10:00, 28:00
- **Style:** Slow zoom-in or pan on still photos
- **Status:** HAVE (KenBurns component, 7 presets)

### 11b. Surveillance Camera Timestamp
- **Timestamp:** 4:00
- **Style:** Camera ID + date/time stamp in bottom-left (e.g., "OTERO14_LL0014 2025/05/12 20:02:51")
- **Built into source footage, not added in post**
- **Status:** N/A (source footage metadata)

### 11c. Bodycam Audio Captions
- **Throughout**
- **Style:** Captions styled to match bodycam footage context (white/yellow, centered)
- **Status:** HAVE (CaptionOverlay)

---

## 12. WATERMARK

### 12a. Channel Watermark
- **Throughout**
- **Style:** Semi-transparent "DR. INSANITY" logo in bottom-right corner
- **Status:** NEED — New component: `Watermark` (persistent semi-transparent overlay)

---

## 13. RED ATMOSPHERIC GLOW

### 13a. Red Glow/Mist Effect
- **Timestamp:** 2:30
- **Style:** Animated red glow/smoke/mist hovering above building in dark establishing shot
- **Usage:** Dramatic/ominous atmosphere for crime scene
- **Status:** NEED — New component: `AtmosphericGlow` (particle/gradient animation overlay)

---

## Priority Implementation List

### HIGH PRIORITY (frequently used, high impact)
1. **PhotoViewerCard** — Fake OS window with photo + name label (used ~10x in video)
2. **SourceBadge** — [ACTUAL], [REENACTMENT], [ACTUAL PHOTO] corner labels (used ~8x)
3. **BulletList / ChargeSheet** — Staggered reveal text bars (used at climax)
4. **SentencingCard** — Split photo + charges/sentence info card (used at end)
5. **Watermark** — Persistent channel logo overlay

### MEDIUM PRIORITY (adds polish)
6. **AnimatedBackground** — Teal/cyan motion graphics backdrop for graphics segments
7. **MapAnnotation** — Red highlight markers on aerial/satellite views
8. **Caption keyword coloring** — Per-word color emphasis in captions (red for violent terms)
9. **NotepadWindow** — Fake Notepad OS window frame wrapping typewriter text

### LOW PRIORITY (rare or out of scope)
10. **AtmosphericGlow** — Red mist/smoke particle effect (used once, complex)
11. Face blur — ML-based, out of scope for Remotion
12. Content blur — Same as above

---

## Existing Components That Cover This Video Well

| Component | Used For |
|-----------|----------|
| CaptionOverlay | All subtitle/caption moments |
| KenBurns | Photo zoom/pan effects |
| AnimatedMap | Satellite/aerial views with markers |
| TransitionRenderer | Dissolve, fade to/from black |
| TextOverlay | Bold text labels (partial) |
| QuoteCard | Quote callouts (partial) |
| PictureInPicture | Photo insets on footage |
| LowerThird | Name/role labels (partial — used differently here) |
| COLOR_FILTERS | B&W, dark tint, blue grade |

## Gap Analysis

The biggest gaps are:
1. **Photo Viewer window frame** — The signature Dr Insanity style of presenting photos in a fake OS window. This is their most distinctive graphic element.
2. **Source badges** — Simple but essential for credibility/context
3. **Structured info cards** — Charges, sentencing, case summary layouts
4. **Animated backgrounds** — Motion graphics behind graphic segments
