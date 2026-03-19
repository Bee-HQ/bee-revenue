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

**Read these three documents before generating.** They contain the rules and specs you must follow:

1. **Production formula** — `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`
   - Act percentage targets by archetype
   - 90-second max narrator stretch rule
   - Open loop hierarchy
   - Footage mix targets
   - Visual palette progression

2. **Visual storyboard bible** — `bee-content/discovery/true-crime/research/visual-storyboard-bible.md`
   - Visual code → production spec mapping
   - Color values, durations, effects for each element
   - Overlay specs (lower thirds, quote cards, etc.)

3. **Output format spec** — `bee-content/video-editor/docs/superpowers/specs/2026-03-19-otio-project-format-design.md`
   - Exact JSON block structure (`bee-video:project`, `bee-video:segment`)
   - Visual/audio/overlay type definitions and fields
   - Narration as `> NAR:` blockquotes
   - Timecode formats (header shorthand vs JSON precise)

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
| `[WAVEFORM-AERIAL]` | `WAVEFORM` | `"color": "green"` |
| `[MAP-FLAT]` or `[MAP-FLAT: location]` | `MAP` | `"style": "flat"` |
| `[MAP-TACTICAL]` | `MAP` | `"style": "tactical"` |
| `[MAP-PULSE]` | `MAP` | `"style": "pulse"` |
| `[MAP-ROUTE]` | `MAP` | `"style": "route"` |
| `[PHOTO]` or `[PHOTO: path]` | `PHOTO` | `"ken_burns": "zoom_in"`, `"color": "warm_victim"` |
| `[PIP-SINGLE]` or `[PIP-SINGLE: path]` | `PHOTO` | `"ken_burns": "zoom_in"` |
| `[BLACK]` | `BLACK` | `"duration"` from segment timing |
| `[BRAND-STING]` | `GRAPHIC` | `"template": "brand_sting"` |
| `[DISCLAIMER]` | `GRAPHIC` | `"template": "disclaimer"` |

For codes with `: path` suffix, set `"src": "path"`. Otherwise `"src": null`.

For `STOCK` types without a source, add a `"query"` field with a Pexels search term derived from the scene context (e.g., `"query": "aerial farm dusk southern"`).

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
   - "Open in web editor (`bee-video serve`) to assign media and review"
   - "Run `bee-video preflight storyboard.md -p ./project` to check asset readiness"
   - "Run `bee-video narration storyboard.md -p ./project` to generate TTS"
