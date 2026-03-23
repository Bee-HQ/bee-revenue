# Review Storyboard

You are reviewing a storyboard for production readiness — checking that every segment has valid JSON, timing is correct, the formula is followed, and the storyboard can be fed directly into the bee-video production pipeline.

## Setup

Ask: "Which storyboard should I review?"
- Look for `storyboard.md` files in `bee-content/discovery/true-crime/cases/*/`
- Accept any path

## Context Documents

Read before reviewing:

1. **The storyboard** (the file being reviewed)
2. **Output format spec** — `bee-content/video-editor/docs/superpowers/specs/2026-03-19-otio-project-format-design.md`
   - Valid JSON block structure
   - Visual/audio/overlay type definitions
   - Required fields per type

Production rules are inlined below in the review checklist.

## Review Checklist

### 1. Format Validity

- **Project block:** Is there exactly one `` ```json bee-video:project `` block? Is it valid JSON?
- **Segment blocks:** Does every `### time | title` segment have a `` ```json bee-video:segment `` block? Is each valid JSON?
- **Narration:** Are `> NAR:` blockquotes present where narration is needed? Are they below the JSON block (not inside it)?
- **Timecodes:** Do segment headers use valid `M:SS` or `H:MM:SS` format? Are they sequential (no overlaps, no gaps)?
- **Section headers:** Do `## ACT` headers have time ranges that match their segments?

### 2. Visual Completeness

For each segment's `visual` array:
- **Type valid?** Must be one of: FOOTAGE, STOCK, PHOTO, MAP, GRAPHIC, GENERATED, WAVEFORM, BLACK, PIP, PHOTO_VIEWER, BULLET_LIST, INFO_CARD, NOTEPAD, KINETIC_TEXT, CALLOUT, TEXT_CHAT, SOCIAL_POST, EVIDENCE_BOARD
- **Source assignment:** Count segments with `"src": null` vs assigned. Report the ratio.
- **Required fields:** FOOTAGE needs `src`/`in`/`out` (or null). MAP needs `style`. PHOTO needs `ken_burns`.
- **Duration rule:** No single visual should last more than 12 seconds (from production rules). Flag violations.

### 3. Audio Completeness

For each segment's `audio` array:
- **Type valid?** Must be one of: REAL_AUDIO, MUSIC, SFX, NAR
- **Music continuity:** Does every segment have a MUSIC entry? (Formula: background music never stops)
- **Volume levels:** NAR should be ~0.8-1.0, REAL_AUDIO ~0.6-0.8, MUSIC ~0.15-0.25
- **Narration present:** If `> NAR:` blockquote exists, is there narration content?
- **90-second rule:** Check for consecutive segments totaling >90 seconds with only NAR audio (no REAL_AUDIO). Flag violations.

### 4. Overlay Completeness

- **Lower thirds:** Does every character's first appearance have a LOWER_THIRD overlay?
- **Type valid?** Must be one of: LOWER_THIRD, TIMELINE_MARKER, QUOTE_CARD, FINANCIAL_CARD, TEXT_OVERLAY, KINETIC_TEXT, CAPTION, TEXT_CHAT, SOCIAL_POST, EVIDENCE_BOARD, SOURCE_BADGE, MAP_ANNOTATION, DRAMATIC_QUOTE, PHOTO_VIEWER, BULLET_LIST, INFO_CARD, NOTEPAD, CALLOUT, PIP
- **Duration:** LOWER_THIRD should have duration 4-6 seconds
- **KINETIC_TEXT:** Must have `text` and `preset` (punch, flow, stack, highlight). Check that `**emphasis**` markers are balanced.
- **TEXT_CHAT:** Must have `platform` and `messages` array with sender/text/sent fields.
- **SOCIAL_POST:** Must have `platform`, `author`, and `text`.
- **EVIDENCE_BOARD:** Must have `people` array and `connections` array with from/to/label fields.
- **PHOTO_VIEWER:** Must have `content` (Name — Role or JSON array for multi-card). Check `animation` is valid (slide-up, slide-left, scale).
- **SOURCE_BADGE:** Must have `content` (ACTUAL, REENACTMENT, ACTUAL PHOTO, etc.). Should appear on real footage segments.
- **DRAMATIC_QUOTE:** Must have `content` (the quote text). Optional `color` (red default), `italic` (true default).
- **BULLET_LIST:** Must have `content` (newline-separated items or JSON array). Optional `accent` (red default), `style` (stagger default).
- **INFO_CARD:** Must have `content` (JSON with sections array). Optional `src` for photo, `photoSide`.
- **NOTEPAD:** Must have `content` (newline-separated text). Optional `animation` (typewriter default), `windowTitle`.
- **MAP_ANNOTATION:** Must have `content` (JSON array of shapes with type/coords). Optional `color` (red default).

### 5. Transitions

- **First segment:** Should have `"transition_in": {"type": "fade_from_black", ...}`
- **Act transitions:** Should have dissolves (1-1.5s)
- **Impact moments:** Should NOT have transitions (hard cuts)
- **Consistency:** Check that transitions follow the pattern from the formula

### 6. Timing

- **Total duration:** Does it match the project's expected runtime?
- **Act percentages:** Calculate actual percentages, compare against archetype targets
- **Segment duration range:** Most segments should be 8-30 seconds. Flag outliers.

### 7. Asset Readiness

- **Count unassigned:** How many `"src": null` entries by type?
- **Stock footage queries:** Do STOCK entries with null src have a `"query"` field?
- **Maps:** Do MAP entries have `style` and coordinates?
- **Generated:** Do GENERATED entries have a `"prompt"` field?

## Output

```
## Storyboard Review: "[Title]"

### Overall: PRODUCTION-READY / NEEDS WORK / MAJOR ISSUES

### Format Validity
- Project block: VALID/INVALID
- Segment blocks: [N valid] / [N total]
- Timecode issues: [list]

### Visual Coverage
- Segments with assigned media: [N] / [N total] ([%])
- Segments with null src: [N] (these need media assignment)
- Visual type distribution: [table]
- Duration violations (>12s): [list]

### Audio Coverage
- Segments with music: [N] / [N total]
- Segments with narration: [N]
- Segments with real audio: [N]
- 90-second narrator stretches: [list any violations]

### Overlay Coverage
- Characters with lower thirds: [N] / [N total characters]
- Missing lower thirds: [list]

### Transitions
- [any issues]

### Timing
- Total duration: [actual vs target]
- Act percentages: [table: actual vs target]

### Asset Summary
| Type | Assigned | Unassigned |
|------|----------|------------|
| FOOTAGE | [N] | [N] |
| STOCK | [N] | [N] |
| PHOTO | [N] | [N] |
| MAP | [N] | [N] |
| MUSIC | [N] | [N] |

### Issues
[numbered list with segment references and fixes]

### Verdict
[ready for production, or what needs to happen first?]
```

If the storyboard needs work, list specific fixes with segment references, then ask:
"Want me to fix these issues now?"

If the user says yes, make the corrections directly in the file, then re-run the review checks on the updated file.

If production-ready, say: "Storyboard is ready. Next steps:"
- "Assign remaining media in web editor (`./start.sh`)"
- "Run `bee-video preflight storyboard.md` to verify assets"
- "Run `bee-video produce storyboard.md -p ./project` to generate the video"
