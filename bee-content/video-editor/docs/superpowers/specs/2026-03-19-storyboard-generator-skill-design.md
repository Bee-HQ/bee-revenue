# Storyboard Generator Skill Design

A Claude Code skill (`/generate-storyboard`) that interactively generates a new-format storyboard from a screenplay. Reads the production formula and visual bible as context, asks clarifying questions, then produces a complete storyboard markdown file with `bee-video:segment` JSON blocks.

## Problem

Generating a storyboard from a screenplay is a manual, multi-hour process. The creator needs to:
- Break scenes into time-coded segments
- Calculate timing from narration word count and act percentages
- Map visual codes to production specs (color grades, Ken Burns effects, overlay types)
- Structure each segment with precise JSON for the production pipeline
- Maintain consistency with the production formula and visual bible

All the reference material exists (formula, bible, OTIO format spec). Claude Code can do this directly — it just needs the right context and a repeatable interface.

## Solution

A Claude Code skill that:
1. Interactively gathers inputs (screenplay path, runtime, archetype)
2. Loads formula + bible + format spec as context
3. Generates a complete storyboard file in the new markdown+JSON format
4. Reports a summary and suggests next steps

## Screenplay Input Spec

The skill expects a screenplay in this format:

```markdown
# Screenplay: "Title Here"

**Archetype:** trial-centric
**Target Runtime:** 50

---

## ACT 1: TITLE

### Scene Title

[VISUAL-CODE]
**NARRATOR:** Narration text here. Multiple paragraphs
are allowed for longer narrator sections.

[REAL-AUDIO: footage/source-file.mp4]
Speaker: "Dialog line from real footage."

[LOWER-THIRD: "Name — Role"]

### Next Scene

[FOOTAGE: footage/bodycam/arrival.mp4]
[BROLL-DARK]
**NARRATOR:** More narration here.

[MAP-FLAT: lowcountry-sc]
[TIMELINE-MARKER: "June 7, 2021 — The Night Of"]
```

### Required elements

| Element | Format | Purpose |
|---------|--------|---------|
| Title | `# Screenplay: "Title"` | Project title |
| Act headers | `## ACT N: TITLE` | Act structure |
| Scene headers | `### Scene Title` | Become segment titles |
| Narrator text | `**NARRATOR:** text` | TTS narration content |
| Visual codes | `[CODE]` or `[CODE: qualifier]` | At least one per scene |

### Optional elements

| Element | Format | Purpose |
|---------|--------|---------|
| Archetype | `**Archetype:** name` | Formula archetype (prompted if missing) |
| Target Runtime | `**Target Runtime:** N` | Minutes (prompted if missing) |
| Source hints | `[CODE: path/to/file]` | Pre-assign media source |
| Dialog | `Speaker: "text"` | Real audio references |
| Overlays | `[LOWER-THIRD: "Name — Role"]` | Overlay directives |
| Overlays | `[TIMELINE-MARKER: "Date — Desc"]` | Date stamp overlays |
| Overlays | `[QUOTE-CARD: "Quote" — Author]` | Quote display |
| Overlays | `[FINANCIAL-CARD: "$Amount" — Desc]` | Financial overlay |

### Supported visual codes

All codes from the visual storyboard bible are supported. Core codes:

| Code | Maps to JSON type | Default color |
|------|-------------------|---------------|
| `[FOOTAGE]` | `FOOTAGE` | archetype-dependent |
| `[BROLL-DARK]` | `STOCK` | `dark_crime` |
| `[BROLL-WARM]` | `STOCK` | `warm_victim` |
| `[WAVEFORM-AERIAL]` | `WAVEFORM` | `green` |
| `[MAP-FLAT]` | `MAP` | `flat` style |
| `[MAP-TACTICAL]` | `MAP` | `tactical` style |
| `[MAP-PULSE]` | `MAP` | `pulse` style |
| `[MAP-ROUTE]` | `MAP` | `route` style |
| `[PHOTO]` | `PHOTO` | `warm_victim` |
| `[PIP-SINGLE]` | `PHOTO` | — |
| `[BLACK]` | `BLACK` | — |
| `[BRAND-STING]` | `GRAPHIC` | — |
| `[DISCLAIMER]` | `GRAPHIC` | — |

## Skill Interface

### Invocation

```
/generate-storyboard
```

### Interactive flow

**1. Ask for screenplay path**
- If an obvious screenplay file exists in the current directory or case directory, suggest it
- Accept any path

**2. Ask for archetype** (if not in screenplay header)
- Present the four options from the formula: bodycam-domestic, trial-centric, interrogation-centric, cold-case
- Brief description of each

**3. Ask for target runtime** (if not in screenplay header)
- Default suggestion based on archetype (bodycam-domestic: 45-55 min, trial-centric: 50-60 min)
- Accept any integer (minutes)

**4. Ask for output path**
- Default: same directory as screenplay, named `storyboard.md`
- Accept any path

**5. Scan for existing media** (automatic, no prompt)
- If project directory has `footage/`, `stock/`, `photos/`, `music/` subdirectories, list available files
- Use these to populate `src` fields where visual codes match filenames

### Generation

The skill reads three reference documents as context:

| Document | Path | Purpose |
|----------|------|---------|
| Production formula | `discovery/true-crime/research/screenplay-storyboard-formula.md` | Act percentages, archetype rules, pacing, audio break rules |
| Visual bible | `discovery/true-crime/research/visual-storyboard-bible.md` | Visual code → production spec mapping |
| Output format | `docs/superpowers/specs/2026-03-19-otio-project-format-design.md` | Target markdown+JSON format |

With this context, Claude Code:

1. **Parses the screenplay** — extracts acts, scenes, narrator blocks, visual codes, dialog, overlays
2. **Calculates timing** — applies formula act percentages to target runtime, distributes across scenes by narrator word count (150 wpm), applies minimum segment duration (5s), applies 90-second max narrator stretch rule
3. **Generates segment JSON blocks** — maps visual codes to production specs using the bible, builds audio/overlay/transition layers, sets `src: null` for unassigned media
4. **Populates `src` fields** where possible — matches visual codes to scanned media files by keyword similarity
5. **Writes the storyboard file** — `bee-video:project` header block + sections + segments with JSON blocks + `> NAR:` blockquotes

### Output format

The generated file follows the OTIO project format spec exactly:

````markdown
```json bee-video:project
{
  "title": "The Murdaugh Murders",
  "version": 1,
  "voice_lock": { "engine": "elevenlabs", "voice": "Daniel" },
  "color_preset": "dark_crime",
  "default_transition": { "type": "dissolve", "duration": 1.0 },
  "output": { "resolution": "1920x1080", "fps": 30, "codec": "h264", "crf": 18 }
}
```

## ACT 1: THE DYNASTY AND THE DEAD (0:00 - 10:00)

### 0:00 - 0:15 | The 911 Call

```json bee-video:segment
{
  "visual": [{
    "type": "WAVEFORM",
    "src": null,
    "color": "green"
  }],
  "audio": [
    { "type": "REAL_AUDIO", "src": "footage/911-calls/call.mp4", "volume": 0.8 }
  ],
  "overlay": [{
    "type": "TIMELINE_MARKER",
    "date": "June 7, 2021",
    "description": "10:07 PM — 911 call received"
  }],
  "transition_in": { "type": "fade_from_black", "duration": 1.5 }
}
```

> NAR: On the night of June 7th, 2021, a 911 call
> shattered the silence of a South Carolina estate.
````

### Post-generation summary

After writing the file, report:
- Total segments and duration
- Per-act breakdown (segments, duration, % of total)
- Assets needing assignment (`src: null` count by type)
- Any formula violations detected (narrator stretches > 90s, acts outside percentage range)
- Next steps: "Open in web editor" / "Run preflight" / "Generate narration"

## Skill file structure

```
.claude/commands/generate-storyboard.md
```

The skill is a single markdown prompt file that Claude Code loads when `/generate-storyboard` is invoked. It contains:
- The interactive flow instructions
- References to the three context documents (formula, bible, format spec)
- The output format spec (inline or by reference)
- The screenplay input spec

## What this does NOT include

- No new Python code — the skill is a Claude Code prompt, not a bee-video CLI command
- No API integration — Claude Code generates the file directly
- No TTS generation — run `bee-video narration` after
- No asset downloading — run `bee-video fetch-stock` after
- No video assembly — run `bee-video produce` after
- No screenplay generation from case research — that's a separate future skill

## Context document paths

These paths are relative to the repo root (`bee-revenue/`). The skill must reference them correctly:

| Document | Relative path from repo root |
|----------|------------------------------|
| Formula | `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md` |
| Visual bible | `bee-content/discovery/true-crime/research/visual-storyboard-bible.md` |
| OTIO format spec | `bee-content/video-editor/docs/superpowers/specs/2026-03-19-otio-project-format-design.md` |

Note: these paths are true-crime-specific. For a different genre, you'd swap the formula and bible. The format spec stays the same.
