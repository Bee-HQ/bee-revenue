# Review Screenplay

You are reviewing a screenplay for formula compliance, narrative quality, and production readiness before it's used to generate a storyboard.

## Setup

Ask: "Which screenplay should I review?"
- Look for `screenplay*.md` files in `bee-content/discovery/true-crime/cases/*/`
- Accept any path

Also ask: "Is there a case research file I should cross-reference?"
- Look for `case-research.md` in the same directory

## Context Documents

Read before reviewing:

1. **The screenplay** (the file being reviewed)
2. **Case research** (if available — for fact-checking quotes and sources)
3. **Production formula** — `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`
   - Phase 2: Screenplay structure
   - Act percentages by archetype
   - Open loop rules
   - Dramatic irony frequency
   - 90-second narrator stretch rule
4. **Narration style guide** — `bee-content/discovery/true-crime/channels/dr-insanity/narration-style-guide.md`
   - Sentence rhythm
   - Tone and vocabulary

## Review Checklist

### 1. Structure & Pacing

- **Act percentages:** Calculate actual act durations from timecodes, compare against archetype targets. Flag any act that's more than 5% off target.
- **Cold open:** Does it hook in the first 15 seconds? Is there a flash-forward montage with 5-7 dramatic moments?
- **Act transitions:** Are they clear? Does each act end with a cliffhanger or reveal?
- **Total runtime:** Does it match the target?

### 2. Narration Quality

- **Present tense:** Find any past-tense narration and flag it. Every `**NARRATOR:**` line should be present tense.
- **Sentence rhythm:** Check for the short-punch pattern (medium-medium-long-SHORT-long). Flag any section where all sentences are the same length.
- **Narrator stretches:** Find the longest continuous narrator section without a real audio clip. Flag anything over 90 seconds.
- **Word count:** Count total narrator words. At 150 wpm, does it fit the target runtime's narration allocation (60% of total)?

### 3. Real Audio Integration

- **Frequency:** Real audio should appear every 90-120 seconds. Calculate the average gap between real audio clips. Flag any gap over 2 minutes.
- **Quote accuracy:** If case research is available, spot-check 5 quotes against the research. Are they verbatim?
- **Attribution:** Every real audio clip should have a speaker name and context (`>> **SPEAKER (context):**`)
- **Source variety:** Are there at least 2 different audio source types (911, bodycam, interrogation, trial)?

### 4. Visual Codes

- **Coverage:** Every scene should have at least one `[VISUAL-CODE]`. Flag any scenes without one.
- **Variety:** Count unique visual codes used. A 50-minute video should use 8+ different types.
- **First appearances:** Every character's first appearance should have `[LOWER-THIRD: "Name — Role"]`.
- **Valid codes:** Check that all codes are from the visual bible. Flag any unrecognized codes.

### 5. Narrative Techniques

- **Open loops:** Are there 2-4 open loops active at any time? Trace the major loops through the screenplay.
- **Dramatic irony:** Count instances of dramatic irony ("What X doesn't know is..."). Formula says 4-5 per video, using 3+ types.
- **Central irony:** Is there one clear overarching irony that drives the whole narrative?
- **Reveals:** Count significant reveals (new facts presented to the audience). Formula says 35+ per video.

### 6. Title

- Does it follow the hook pattern? ("He [action] — Then [reveal] Surfaced")
- Is it YouTube-optimized? (curiosity gap, implies a twist)
- Length: should be under 80 characters

### 7. Production Readiness

- **Shot list summary:** Does the screenplay end with a shot list table?
- **Production notes:** Are footage requirements listed?
- **Narration stats:** Word count, longest stretch, audio integration rate?

## Output

Present the review as:

```
## Screenplay Review: "[Title]"

### Overall: READY / NEEDS WORK / MAJOR ISSUES

### Structure & Pacing
- Act durations: [actual vs target table]
- [specific issues]

### Narration Quality
- Tense violations: [count, with examples]
- Longest narrator stretch: [N seconds, location]
- Word count: [N words, estimated N minutes at 150 wpm]
- [rhythm observations]

### Real Audio Integration
- Average gap between clips: [N seconds]
- Longest gap: [N seconds, location]
- Source types used: [list]
- Quote accuracy: [spot-check results]

### Visual Codes
- Unique codes: [N, list]
- Scenes without codes: [count, locations]
- Missing lower thirds: [characters without intros]

### Narrative Techniques
- Open loops tracked: [list]
- Dramatic irony count: [N]
- Reveal count: [estimated N]

### Issues
[numbered list, each with location and suggested fix]

### Verdict
[1-2 sentences: ready for storyboard generation or what needs fixing first?]
```

If the screenplay needs work, provide specific, actionable fixes with scene references, then ask:
"Want me to fix these issues now?"

If the user says yes, make the corrections directly in the file, then re-run the review checks on the updated file.

If it's ready, say: "Screenplay is solid. Run `/true-crime:generate-storyboard` to create the storyboard."
