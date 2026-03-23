# Generate Storyboard from Screenplay

You are generating a production-ready storyboard from a screenplay. The storyboard uses the bee-video markdown+JSON format for automated video production.

## Interactive Setup

Before generating, gather these inputs by asking the user one at a time:

### 1. Screenplay path
Ask: "Which screenplay file should I use?"
- Look for `screenplay*.md` files in the current directory and nearby case directories
- Suggest any obvious candidates
- Accept any valid path

### 2. Archetype (if not in screenplay header)
Ask: "Which case archetype? This determines act pacing and footage mix."
- **bodycam-domestic** — Crime with extensive bodycam, suspect cooperates on camera (Act 3 = extended bodycam confrontation)
- **trial-centric** — High-profile case with televised trial as primary footage (Act 3 = cross-examination)
- **interrogation-centric** — Suspect breaks during formal interrogation (Act 3 = interrogation room)
- **cold-case** — Solved years later via new evidence/technology (Act 3 = evidence reveal)

### 3. Target runtime (if not in screenplay header)
Ask: "Target runtime in minutes?"
- Suggest a default based on archetype (bodycam-domestic: 45-55, trial-centric: 50-60, interrogation-centric: 40-50, cold-case: 35-45)

### 4. Output path
Ask: "Where should I save the storyboard?"
- Default: same directory as screenplay, named `storyboard.md`

### 5. Media scan (automatic, no prompt)
- If the screenplay's directory or parent has `footage/`, `stock/`, `photos/`, `music/` subdirectories, scan them
- List available files — use these to populate `src` fields when visual codes match

## Context Documents

**Read ALL of these before generating.** They contain the rules, specs, and examples you must follow:

1. **The screenplay** — read it fully. Pay attention to:
   - Visual codes per scene — these map directly to JSON visual entries
   - `**NARRATOR:**` blocks — these become `> NAR:` blockquotes
   - `>> **SPEAKER:**` dialog — these become REAL_AUDIO entries
   - `[LOWER-THIRD:]`, `[QUOTE-CARD:]`, etc. — these become overlay entries
   - Act headers with timecodes — these set the segment timing

2. **Output format spec** — `bee-content/video-editor/docs/superpowers/specs/2026-03-19-otio-project-format-design.md`
   - **Read the "Full Example" section carefully** — this is the exact format you must produce
   - JSON block structure (`bee-video:project`, `bee-video:segment`)
   - Visual/audio/overlay type definitions with required fields
   - Narration as `> NAR:` blockquotes below the JSON block
   - Timecode formats (header shorthand `M:SS` vs JSON precise `HH:MM:SS.mmm`)

5. **Case research** — if available in the same directory as the screenplay
   - Section 2 (Footage Inventory) — use to populate `src` fields for footage that's been located
   - Footage-sources.md — if it exists, use file paths from download commands

## Screenplay Input Format

The screenplay must have:
- `# Screenplay: "Title"` — title line
- `## ACT N: TITLE` — act headers
- `### Scene Title` — scene headers (become segment titles)
- `**NARRATOR:**` — narrator text blocks
- `[VISUAL-CODE]` — at least one per scene (e.g., `[FOOTAGE]`, `[BROLL-DARK]`, `[WAVEFORM-AERIAL]`)

Optional:
- `**Archetype:**` and `**Target Runtime:**` in the header
- `[CODE: path/to/file]` — source file hints
- `[REAL-AUDIO: path]` — real audio references
- `Speaker: "dialog"` — dialog lines
- `[LOWER-THIRD: "Name — Role"]`, `[TIMELINE-MARKER: "Date — Desc"]`, etc.

## Generation Rules

### Timing

1. Look up the archetype's act percentages from the formula
2. Total runtime × act percentage = act time budget
3. Within each act, distribute time across scenes proportional to narrator word count at 150 words per minute
4. Scenes with `[REAL-AUDIO]` or dialog get a minimum 8-second floor
5. No single segment should exceed 60 seconds — split long scenes into multiple segments
6. Apply the 90-second narrator stretch rule: if consecutive segments have only narration (no real audio), break it up
7. Accumulate timecodes sequentially

### Visual mapping

Map each `[VISUAL-CODE]` to a JSON visual entry using the bible specs:

| Code | JSON type | Default fields |
|------|-----------|---------------|
| `[FOOTAGE]` or `[FOOTAGE: path]` | `FOOTAGE` | `"color"` from archetype default, `"src"` from path or null |
| `[BROLL-DARK]` | `STOCK` | `"color": "dark_crime"`, `"ken_burns": "zoom_in"`, `"src": null` |
| `[BROLL-WARM]` | `STOCK` | `"color": "warm_victim"`, `"ken_burns": "zoom_in"`, `"src": null` |
| `[WAVEFORM-AERIAL]` | `WAVEFORM` | `"style": "bars"`, `"color": "green"` |
| `[WAVEFORM-BARS]` | `WAVEFORM` | `"style": "bars"`, `"color": "green"` |
| `[WAVEFORM-PULSE]` | `WAVEFORM` | `"style": "pulse"`, `"color": "green"` |
| `[MAP-FLAT]` or `[MAP-FLAT: location]` | `MAP` | `"style": "flat"`, `"animation": "pulse"` |
| `[MAP-TACTICAL]` | `MAP` | `"style": "tactical"`, `"animation": "pulse"` |
| `[MAP-FLY-TO]` or `[MAP-FLY-TO: location]` | `MAP` | `"style": "satellite"`, `"animation": "fly_to"` |
| `[MAP-ORBIT]` or `[MAP-ORBIT: location]` | `MAP` | `"style": "satellite"`, `"animation": "orbit"` |
| `[MAP-ROUTE]` | `MAP` | `"style": "tactical"`, `"animation": "route"` |
| `[PHOTO]` or `[PHOTO: path]` | `PHOTO` | `"ken_burns": "zoom_in"`, `"color": "warm_victim"` |
| `[PIP-SINGLE]` or `[PIP-SINGLE: path]` | `PHOTO_VIEWER` | `"content": "Name — Role"`, `"animation": "slide-up"` |
| `[PIP-SPLIT]` or `[PIP-DUAL]` | `PHOTO_VIEWER` | `"content": "[{\"name\":\"Name1\"},{\"name\":\"Name2\"}]"` — JSON array for dual |
| `[PHOTO-VIEWER]` or `[PHOTO-VIEWER: "Name — Role"]` | `PHOTO_VIEWER` | `"content": "Name — Role"`, `"animation": "slide-up"` |
| `[PHOTO-VIEWER-DUAL]` | `PHOTO_VIEWER` | `"content": "[{\"name\":\"Name1\"},{\"name\":\"Name2\"}]"` |
| `[NOTEPAD]` or `[NOTEPAD: title]` | `NOTEPAD` | `"animation": "typewriter"`, `"windowTitle": title or "Notepad"` |
| `[BULLET-LIST]` | `BULLET_LIST` | `"accent": "red"`, `"style": "stagger"` |
| `[INFO-CARD]` | `INFO_CARD` | `"photoSide": "right"` |
| `[PIP-CORNER: position]` | `PIP` | `"layout": position` (bottom-right, bottom-left, top-right, top-left) |
| `[BLACK]` | `BLACK` | `"duration"` from segment timing |
| `[BRAND-STING]` | `GRAPHIC` | `"template": "brand_sting"` |
| `[DISCLAIMER]` | `GRAPHIC` | `"template": "disclaimer"` |

For codes with `: path` suffix, set `"src": "path"`. Otherwise `"src": null`.

For `STOCK` types without a source, add a `"query"` field with a Pexels search term derived from the scene context (e.g., `"query": "aerial farm dusk southern"`).

**Ken Burns effects** — when assigning `"ken_burns"` to STOCK/PHOTO, vary for visual interest. Available effects: `zoom_in` (default), `zoom_out`, `pan_left`, `pan_right`, `pan_up`, `pan_down`, `zoom_in_pan_right`.

**Color filters** — available presets for `"color"`: `dark_crime`, `warm_victim`, `surveillance`, `noir`, `bodycam`, `cold_blue`, `sepia`, `vintage`, `bleach_bypass`, `night_vision`, `golden_hour`, `vhs`. Match to scene mood.

### Audio mapping

- `**NARRATOR:**` text → `> NAR:` blockquote below the JSON block. Add `{"type": "NAR"}` to the audio array only if you need to override voice/engine for this segment.
- `[REAL-AUDIO: path]` → `{"type": "REAL_AUDIO", "src": "path", "volume": 0.8}`
- `Speaker: "dialog"` without a path → `{"type": "REAL_AUDIO", "src": null, "volume": 0.8}`
- Every segment gets a music entry: `{"type": "MUSIC", "src": null, "volume": 0.2}` — human assigns the music track later

### Overlay mapping

- `[LOWER-THIRD: "Name — Role"]` → `{"type": "LOWER_THIRD", "text": "Name", "subtext": "Role", "duration": 5.0, "position": "bottom-left"}`
- `[TIMELINE-MARKER: "Date — Desc"]` → `{"type": "TIMELINE_MARKER", "date": "Date", "description": "Desc"}`
- `[QUOTE-CARD: "Quote" — Author]` → `{"type": "QUOTE_CARD", "quote": "Quote", "author": "Author"}`
- `[FINANCIAL-CARD: "$Amount" — Desc]` → `{"type": "FINANCIAL_CARD", "amount": "$Amount", "description": "Desc"}`
- `[KINETIC-TEXT: "Text" — preset]` → `{"type": "KINETIC_TEXT", "text": "Text with **emphasis** markers", "preset": "punch|flow|stack|highlight", "position": "center"}`
- `[CAPTION: style]` → `{"type": "CAPTION", "style": "karaoke|phrase"}` — auto-syncs to narration/audio timing. Narration text can include `{red:keyword}` color markup for emphasis
- `[SOURCE-BADGE: "REENACTMENT"]` → `{"type": "SOURCE_BADGE", "content": "REENACTMENT"}`
- `[SOURCE-BADGE: "ACTUAL"]` → `{"type": "SOURCE_BADGE", "content": "ACTUAL"}`
- `[MAP-ANNOTATION: shapes]` → `{"type": "MAP_ANNOTATION", "content": "[shapes JSON]", "color": "red"}`
- `[DRAMATIC-QUOTE: "Quote"]` → `{"type": "DRAMATIC_QUOTE", "content": "Quote", "color": "red", "italic": true}`
- `[BULLET-LIST: items]` → `{"type": "BULLET_LIST", "content": "item1\\nitem2\\nitem3", "accent": "red"}`
- `[INFO-CARD: sections]` → `{"type": "INFO_CARD", "content": "{\"sections\":[...]}", "src": "photo.jpg"}`
- `[NOTEPAD: text]` → `{"type": "NOTEPAD", "content": "line1\\nline2", "animation": "typewriter"}`
- `[TEXT-CHAT: platform]` → `{"type": "TEXT_CHAT", "platform": "imessage|android|generic", "messages": [{"sender": "Name", "text": "Message", "sent": true|false}]}`
- `[SOCIAL-POST: platform]` → `{"type": "SOCIAL_POST", "platform": "facebook|instagram|twitter", "author": "Name", "handle": "@handle", "text": "Post content"}`
- `[EVIDENCE-BOARD]` → `{"type": "EVIDENCE_BOARD", "people": [{"name": "Name"}], "connections": [{"from": "Name1", "to": "Name2", "label": "Relationship"}]}`

### Transitions

- First segment of the video: `"transition_in": {"type": "fade_from_black", "duration": 1.5}`
- Between mood shifts (warm → dark, narration → real footage): `"transition_in": {"type": "dissolve", "duration": 1.0}`
- Impact moments (verdict, key quotes): no transition (hard cut — omit `transition_in`)
- Act transitions: `"transition_in": {"type": "dissolve", "duration": 1.5}`
- Default (if unsure): use project's `default_transition`

### Media matching

If media files were found during the scan (step 5):
- Match `[FOOTAGE: bodycam]` to files containing "bodycam" in their path
- Match `[STOCK]` with query "aerial farm" to files like `stock/aerial-farm-dusk-001.mp4`
- Simple substring matching on filenames — not AI, not fuzzy
- Only populate `src` if the match is unambiguous (one clear match). If multiple matches, leave `src: null`

## Production Rules

<!-- Inlined from screenplay-storyboard-formula.md + visual-storyboard-bible.md -->

### Act Percentage Targets

```
TRAILER → OPENING → ACT 1 → ACT 2 → [SPONSOR] → ACT 3 → ACT 4
(1-2 min) (0:30)  (6-12 min) (16-22 min) (0-1:30) (10-15 min) (5-10 min)
  3%       1%      15-25%     35-45%      0-3%      20-30%     5-10%
```

### Timing Rules
- No single segment > 60 seconds — split long scenes
- No narrator stretch > 90 seconds without a real audio clip
- Real audio should appear every 90-120 seconds
- New information every 60-90 seconds

### Color Palette

| Element | Hex | Usage |
|---------|-----|-------|
| Background | `#0A0A0F` | Graphics, cards |
| Primary text | `#FFFFFF` | Body text |
| Secondary text | `#B4B4B4` | Roles, labels |
| **Red** | `#DC2626` | Danger, charges, evidence highlights, financial amounts |
| **Teal** | `#0D9488` | Information, identity, context, informational quotes |
| **Gold** | `#D97706` | Victim, family, humanity, victim-voiced quotes |
| **Green** | `#16A34A` | Positive outcomes, lesser charges |
| **White** | `#FFFFFF` | Neutral accent |

### Color Filter Presets
Available for `"color"` field: `dark_crime`, `warm_victim`, `surveillance`, `noir`, `bodycam`, `cold_blue`, `sepia`, `vintage`, `bleach_bypass`, `night_vision`, `golden_hour`, `vhs`

### Ken Burns Effects
Available for `"ken_burns"` field: `zoom_in` (default), `zoom_out`, `pan_left`, `pan_right`, `pan_up`, `pan_down`, `zoom_in_pan_right`

### Visual Element Specs

**PHOTO_VIEWER (person identification):**
- macOS window chrome: traffic lights, "Photo Viewer" title, menu bar
- `content`: "Name — Role" or JSON array for multi-card
- `animation`: slide-up (default), slide-left, scale
- Duration: 5 seconds default

**SOURCE_BADGE (footage label):**
- Corner label: [ACTUAL], [REENACTMENT], [ACTUAL PHOTO]
- Position: bottom-left (default)
- Duration: fills segment (30s default, clamped to segment)

**NOTEPAD (investigation notes):**
- macOS window: Notepad title, File/Edit/Search/View/Help menu
- `animation`: typewriter (default), lines, instant
- Monospace font, blinking cursor
- Duration: 6 seconds default

**BULLET_LIST (charge sheet):**
- Staggered text bars with corner bracket decorations
- `accent`: red (default), teal, gold, white, green
- `style`: stagger (default), cascade, instant
- Duration: 6 seconds default

**INFO_CARD (charges/sentencing):**
- Split layout: sections on one side, optional photo on other
- `sections`: [{header, body, color?}]
- `photoSide`: right (default), left, none
- Duration: 6 seconds default

**DRAMATIC_QUOTE (splash text):**
- Large colored italic text, no background box
- `color`: red (default), any named or hex color
- `italic`: true (default)
- Duration: 4 seconds default

**MAP_ANNOTATION (evidence highlights):**
- SVG overlay with shapes: circle, path, rect
- Coordinates normalized [0-1]
- `color`: red (default), any named color
- Duration: 6 seconds default

**WATERMARK (persistent):**
- Project-level config, not per-segment
- `text` or `src` (image), position, opacity

## Output Structure

Write the file with this structure:

```
bee-video:project JSON block (title, version, voice_lock, color_preset, default_transition, output)

## ACT 1: TITLE (start - end)

### start - end | Scene Title
bee-video:segment JSON block
> NAR: narrator text

### start - end | Next Scene
...

## ACT 2: TITLE (start - end)
...
```

## Post-Generation

After writing the file, report:

1. **Summary** — total segments, total duration, per-act breakdown
2. **Unassigned assets** — count of `src: null` entries by type (STOCK, FOOTAGE, MUSIC, etc.)
3. **Formula checks** — flag any violations:
   - Act percentages outside the archetype's target range
   - Narrator stretches exceeding 90 seconds
   - Segments exceeding 60 seconds
4. **Next steps:**
   - "Open in web editor (`./start.sh`) to assign media and review"
   - "Run `bee-video preflight storyboard.md -p ./project` to check asset readiness"
   - "Run `bee-video narration storyboard.md -p ./project` to generate TTS"
