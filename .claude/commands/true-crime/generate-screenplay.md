# Generate Screenplay from Case Research

You are generating a production-ready screenplay from a case research file. The screenplay follows the Dr Insanity-style true crime format defined in the production formula.

## Interactive Setup

### 1. Case research path
Ask: "Which case research file should I use?"
- Look for `case-research.md` files in `bee-content/discovery/true-crime/cases/*/`
- Suggest any obvious candidates

### 2. Archetype
Ask: "Which archetype? (Check section 8 of the case research for a recommendation)"
- **bodycam-domestic** — bodycam-driven, suspect cooperates on camera
- **trial-centric** — televised trial is the primary footage
- **interrogation-centric** — long recorded interrogation is the centerpiece
- **cold-case** — solved years later via new evidence

### 3. Target runtime
Ask: "Target runtime in minutes?"
- Suggest based on archetype (bodycam-domestic: 45-55, trial-centric: 50-60, interrogation-centric: 40-50, cold-case: 35-45)

### 4. Output path
Ask: "Where should I save the screenplay?"
- Default: same directory as case research, named `screenplay.md`

## Context Documents

**Read ALL of these before generating.** They are your source material and quality standards:

1. **Case research** — the file from step 1. Pay special attention to:
   - Section 5 (Narrative Angles) — use the hook, dramatic moments, central irony, and act structure suggestions to inform your screenplay structure
   - Section 2 (Footage Inventory) — only reference real audio clips that are marked **YES** in availability
   - Section 4 (Key Evidence) — pull verbatim quotes from here
   - Section 8 (Production Notes) — respect the archetype recommendation and challenges
2. **Production formula** — `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`
   - Phase 2: Screenplay structure template
   - Act percentages by archetype
   - Runtime variants (short/long form)
   - Open loop hierarchy
   - 90-second narrator stretch rule
   - Dramatic irony techniques
   - Advanced narrative techniques (Section 5.4)
3. **Visual bible** — `bee-content/discovery/true-crime/research/visual-storyboard-bible.md`
   - Visual codes to tag each scene with
4. **Narration style guide** — `bee-content/discovery/true-crime/channels/dr-insanity/narration-style-guide.md`
   - Voice, tone, pacing, sentence rhythm
5. **Reference example** — `bee-content/discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md`
   - Read this as a concrete example of the target output quality, format, and style
   - Match the level of detail, visual code density, and real audio integration frequency
   - This is a trial-centric screenplay — adapt the pattern for your case's archetype

## Screenplay Format

The output must follow this exact format:

```markdown
# SCREENPLAY: "[Title — Hook Format]"

**Style:** Dr Insanity narration DNA
**Target Duration:** [N] minutes
**Tense:** Present tense throughout
**POV:** Third person omniscient
**Audio Ratio:** 60% narration / 40% real audio clips
**Real Audio Integration:** Every 90-120 seconds
**Archetype:** [archetype name]

---

## COLD OPEN (0:00 - [end])

### Scene Title (start - end)

[VISUAL-CODE]
>> **SPEAKER (source context):** "Verbatim quote from footage"

**NARRATOR:** Present-tense narration text. Short punchy sentences.
Medium length setup. Then SHORT IMPACT. Then a longer unwinding
sentence that carries the tension forward.

---

## ACT 1: [TITLE] (start - end)

### Scene Title (start - end)

[VISUAL-CODE] [LOWER-THIRD: "Name — Role"]
**NARRATOR:** Narration for this scene.

>> **SPEAKER:** "Real audio quote."

...continue for all acts...
```

### Required elements per scene:
- `[VISUAL-CODE]` — at least one visual code from the bible
- Either `**NARRATOR:**` text OR `>> **SPEAKER:**` dialog (or both)
- `[LOWER-THIRD: "Name — Role"]` on first appearance of each character
- `[SOURCE-BADGE: "ACTUAL"]` on scenes using real footage (bodycam, interrogation, courtroom)
- `[DRAMATIC-QUOTE: "Quote"]` for dramatic splash quotes on footage (large italic colored text, no bg box)

### Format conventions:
- `**NARRATOR:**` for narration (present tense, third person)
- `>> **SPEAKER (context):** "Quote"` for real audio clips (double blockquote)
- `[VISUAL-CODE]` on its own line before the content it applies to
- `[VISUAL-CODE: qualifier]` when source is known (e.g., `[FOOTAGE: bodycam]`)
- Act headers: `## ACT N: TITLE (start - end)`
- Scene headers: `### Scene Title (start - end)`

**New visual codes (Remotion components):**
- `[PHOTO-VIEWER: "Name — Role"]` — macOS-style photo window (replaces `[PIP-SINGLE]`)
- `[DRAMATIC-QUOTE: "Quote text"]` — large colored italic text splash on footage
- `[SOURCE-BADGE: "REENACTMENT"]` or `[SOURCE-BADGE: "ACTUAL"]` — corner label for footage type
- `[NOTEPAD: "Investigation Notes"]` — macOS text editor with typewriter animation (replaces `[POLICE-DB]`, `[DOCUMENT-MOCKUP]`)
- `[BULLET-LIST]` — staggered reveal text bars with corner brackets (charges, summaries)
- `[INFO-CARD]` — split photo + structured sections (replaces `[MUGSHOT-CARD]`, `[SPLIT-INFO]`)
- `[MAP-ANNOTATION]` — red SVG circles/arrows on footage (replaces `[EVIDENCE-CLOSEUP]` red highlights)

## Generation Rules

### Structure (from the formula)

Apply the archetype's act percentages to the target runtime:

**Bodycam-Domestic:**
- Cold Open: 5% (trailer montage)
- Act 1: 12-15% (victim intro + normal life)
- Act 2: 40% (investigation beats, escalation)
- Act 3: 25% (confrontation — extended bodycam)
- Act 4: 8% (resolution)
- Sponsor: 2-3% (optional)

**Trial-Centric:**
- Cold Open: 5%
- Act 1: 15-20% (dynasty/backstory + victim humanization)
- Act 2: 35-40% (investigation + pre-trial)
- Act 3: 25% (trial cross-examination)
- Act 4: 8%
- Sponsor: 2-3% (optional)

**Interrogation-Centric:**
- Cold Open: 5%
- Act 1: 10-12% (setup)
- Act 2-3: 60-65% (interrogation with investigation flashbacks)
- Act 4: 8%

**Cold-Case:**
- Cold Open: 5%
- Act 1: 15% (original crime)
- Act 2: 30% (cold case years + failed leads)
- Act 3: 30% (new evidence + resolution)
- Act 4: 10%

### Narration style (from the style guide)

- **Present tense** throughout — "He walks to the door" not "He walked"
- **Short-punch rhythm** — medium sentence, medium sentence, long setup, SHORT IMPACT, long unwind
- **Dramatic irony** — tell the audience what the suspect doesn't know ("What Alex doesn't realize is...")
- **No narrator stretch > 90 seconds** without a real audio clip breaking it up
- **Open loops** — maintain 2-4 at all times (1 anchor + 1-2 structural + micro loops)
- **Real audio every 90-120 seconds** — alternate narrator with footage clips

### Visual tagging

Tag every scene with visual codes from the bible. Common patterns:

**Footage & atmosphere:**
- 911 calls → `[WAVEFORM-AERIAL]` (bars style, aerial background)
- 911 calls (alt) → `[WAVEFORM-BARS]` (bars, dark background) or `[WAVEFORM-PULSE]` (pulsing rings)
- Bodycam footage → `[BODYCAM]` or `[FOOTAGE: bodycam]`
- Interrogation → `[INTERROGATION]`
- Trial testimony → `[COURTROOM]`
- B-roll/atmosphere → `[BROLL-DARK]` or `[BROLL-WARM]`

**People & character intros:**
- Character intros → `[PHOTO-VIEWER: "Name — Role"]` (macOS window chrome) + `[LOWER-THIRD: "Name — Role"]`
- Side-by-side comparison → `[PHOTO-VIEWER-DUAL]` (two photos in viewer windows)
- Picture-in-picture → `[PIP-CORNER: position]` (position: bottom-right, bottom-left, top-right, top-left)
- Legacy: `[PIP-SINGLE]` and `[PIP-SPLIT]` still accepted, map to `PHOTO_VIEWER`

**Locations & maps:**
- Static location → `[MAP-FLAT]`, `[MAP-TACTICAL]`
- Dramatic location reveal → `[MAP-FLY-TO: location]` (cinematic zoom from globe)
- Location orbit → `[MAP-ORBIT: location]` (rotating aerial view)
- Travel route → `[MAP-ROUTE]`

**Evidence & information:**
- Evidence → `[EVIDENCE-DISPLAY]`, `[NOTEPAD: "title"]` (replaces `[DOCUMENT-MOCKUP]`)
- Evidence highlights → `[MAP-ANNOTATION]` (red circles/arrows on footage, replaces `[EVIDENCE-CLOSEUP]`)
- Financial reveals → `[FINANCIAL-CARD: "$Amount — Description"]`
- Key quotes → `[QUOTE-CARD: "Quote" — Speaker]`
- Charges/sentencing → `[INFO-CARD]` (split photo + sections, replaces `[MUGSHOT-CARD]`)
- Charge lists → `[BULLET-LIST]` (staggered reveal bars)
- Text messages → `[TEXT-CHAT: platform]` (platform: imessage, android, generic)
- Social media → `[SOCIAL-POST: platform]` (platform: facebook, instagram, twitter)
- Connections → `[EVIDENCE-BOARD]`
- Footage type label → `[SOURCE-BADGE: "ACTUAL"]` or `[SOURCE-BADGE: "REENACTMENT"]`

**Text & emphasis:**
- Dramatic emphasis → `[KINETIC-TEXT: "Key phrase" — preset]` (preset: punch, flow, stack, highlight)
- Dramatic quote splash → `[DRAMATIC-QUOTE: "Quote"]` (large colored italic text on footage)
- Timelines → `[TIMELINE-SEQUENCE]`
- Captions for real audio → `[CAPTION: style]` (style: karaoke, phrase) — supports `{red:keyword}` color markup

### Real audio integration

Pull quotes directly from the case research. Use the exact quotes documented there:
- 911 call quotes
- Bodycam dialog
- Interrogation exchanges
- Trial testimony
- Witness statements

Format as: `>> **SPEAKER (context):** "Verbatim quote"`

If the case research has the quote, use it verbatim. Do not fabricate quotes.

### Title

Generate a YouTube-optimized title following the formula pattern:
- "He [action] — Then [shocking reveal] Surfaced"
- "She Told Police [lie] — The Security Camera Told a Different Story"
- "[Shocking statement] — [dramatic consequence]"

The title should contain a hook (curiosity gap) and imply a reveal.

## Post-Screenplay Sections

After the acts, include:

### Shot List Summary
```markdown
## SHOT LIST SUMMARY

| Category | Count |
|----------|-------|
| Total scenes | [N] |
| Narrator sections | [N] |
| Real audio clips | [N] |
| Visual codes used | [list unique codes] |
| Lower thirds needed | [N] |
| Maps needed | [N] |
| Quote cards | [N] |
```

### Production Notes
```markdown
## PRODUCTION NOTES

### Footage Requirements
- [list specific footage needed with sources from case research]

### Key Moments to Source
- [list the most important real audio clips to find/trim]

### Narration Stats
- Total narrator word count: [N]
- Estimated narration duration: [N] minutes (at 150 wpm)
- Longest narrator stretch: [N] seconds
- Real audio integration rate: every [N] seconds average
```

## Post-Generation

After writing the file, report:

1. **Summary** — total scenes, acts, estimated duration per act
2. **Audio ratio** — narrator vs real audio percentage
3. **Formula compliance:**
   - Act percentages within archetype targets?
   - No narrator stretch > 90 seconds?
   - Open loops maintained?
   - Real audio every 90-120 seconds?
4. **Unresolved items** — quotes that couldn't be found verbatim, footage gaps
5. **Next step** — "Review the screenplay, then run `/review-screenplay` to check formula compliance"
