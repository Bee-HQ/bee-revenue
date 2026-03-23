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
   - Section 5 (Narrative Angles) — use the hook, dramatic moments, central irony, and act structure suggestions
   - Section 2 (Footage Inventory) — only reference real audio clips marked **YES** in availability
   - Section 4 (Key Evidence) — pull verbatim quotes from here
   - Section 8 (Production Notes) — respect the archetype recommendation and challenges
2. **Reference example** — `bee-content/discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md`
   - Read this as the gold standard for output quality, format, and style
   - Match the level of detail, visual code density, and real audio integration frequency

All formula rules, visual codes, and narration style are inlined below — no external files needed.

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

## Narration Style Guide (Dr Insanity DNA)

<!-- Inlined from narration-style-guide.md -->

### Voice & Tense
- **Present tense** for the primary narrative: "Officers are dispatched." "She has no idea."
- **Past tense** only for backstory: "She had already been married three times."
- **Third person omniscient** — narrator knows everything, reveals strategically
- **Never** use "we" to include the viewer. Viewer is an observer.
- **No exclamation marks** or hyperbolic adjectives. Drama comes from understatement and juxtaposition.

### Sentence Rhythm
Average 15-22 words. Alternate:
- **Short punch:** "This is where things become very peculiar." (7 words)
- **Medium flow:** "Officers are dispatched to conduct a welfare check on the couple." (11 words)
- **Long context:** "With all these findings combined, investigators begin to suspect they may be dealing with something far more serious than a missing person case." (23 words)

Pattern: medium, medium, short punch, long context, short punch.

### Cold Open Formula
1. Real audio clip (most dramatic moment)
2. Narrator: "This is [name], [age]-year-old [descriptor]."
3. Dramatic irony: "In just a few seconds, [he/she] [is] about to [dramatic event]."
4. 2-4 more audio clips from different phases
5. Transition to story proper: time/place anchor

### Character Introductions
- **Victims** — warmth and specificity: "[Age]-year-old [Name] [is] [occupation]. [He/She] lives [location] with [family]."
- **Suspects** — behavioral red flags: "[Name/relationship]. [Something normal]. But [ominous detail]."
- **Officers** — professional context: "Detective [Name] with the [unit]"
- **Witnesses** — relationship to case: "On the line is [Name] requesting a welfare check on [his/her] friend."

### Key Phrases (from 17-video analysis)
**Tension:** "What [they] don't realize is..." | "But that is about to change." | "Unknowingly..." | "Things are about to take a turn."
**Reveals:** "And just like that..." | "Needless to say..." | "It's at this point that..." | "For the first time..."
**Transitions:** "Following this..." | "In the days that follow..." | "At the same time..." | "Shortly after..."
**Suspect behavior:** "[He/She] appears [visibly shaken / calm / cooperative]." | "[Name] sticks to [his/her] story."
**Pre-sponsor:** "But before we get to that..."
**Post-sponsor:** "With that said, let's get back to [the investigation] where [setup]."

### Dramatic Irony (4-5 per video, 3+ types)
- "What [they] don't know is that [shocking fact]."
- "Officers are unknowingly [doing X that relates to hidden fact]."
- "[Name] has no idea that [consequence is coming]."
- "Police don't know it yet, but [suspect] is showing them [the crime scene]."

### Open Loop Types
- **Anchor loop:** The central mystery — opened in trailer, closed in Act 3/4
- **Structural loops:** 2-3 major questions opened across Acts 1-2, each closed with a reveal
- **Micro loops:** "But that is about to change" — opened and closed within 2-5 minutes

### Closing Formula
1. **Legal outcome:** "[Suspect] is [charged/found guilty/sentenced to] [details]."
2. **Case context:** Brief investigator conclusion
3. **Current status:** "As of [date], [name]'s case is still in [phase]."
- No "like and subscribe." No sign-off catchphrase. Factual and restrained.

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
