# Review Case Research

You are reviewing a `case-research.md` file for completeness, accuracy, and production viability before it's used to generate a screenplay.

## Setup

Ask: "Which case research file should I review?"
- Look for `case-research.md` files in `bee-content/discovery/true-crime/cases/*/`
- Accept any path

## Review Process

Read the case research file and the production formula (`bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`, Section 1: Case Selection Criteria).

Evaluate against these criteria:

### 1. Formula Viability Check

Check each universal requirement from the formula:

| Requirement | Status | Notes |
|-------------|--------|-------|
| 20+ minutes of real footage | PASS/FAIL/UNCLEAR | Count estimated minutes from footage inventory |
| Clear victim + clear suspect | PASS/FAIL | |
| Suspect confronted on camera | PASS/FAIL | Which type: bodycam, interrogation, trial, or other? |
| Self-incriminating moment | PASS/FAIL/NONE FOUND | The money shot — what is it? |
| 2+ separate audio sources | PASS/FAIL | List what's available (911, bodycam, interview, trial) |
| Financial angle | PASS/N/A | Specific dollar amounts? |
| Multiple witnesses | PASS/FAIL | |
| Visual location | PASS/FAIL | Property/location with aerial potential? |

**Verdict:** VIABLE / NOT VIABLE / VIABLE WITH GAPS

If NOT VIABLE, explain clearly which dealbreakers are missing and whether they can be resolved.

### 2. Completeness Check

For each of the 8 sections, rate completeness:

| Section | Status | Issues |
|---------|--------|--------|
| 1. Case Timeline | COMPLETE/PARTIAL/MISSING | Are there date gaps? Missing events? |
| 2. Footage Inventory | COMPLETE/PARTIAL/MISSING | Are all footage categories searched? URLs verified? |
| 3. Key Characters | COMPLETE/PARTIAL/MISSING | Missing anyone important? Relationships clear? |
| 4. Key Evidence | COMPLETE/PARTIAL/MISSING | All evidence types covered? |
| 5. Narrative Angles | COMPLETE/PARTIAL/MISSING | Title suggestions? Hook identified? |
| 6. Source URLs | COMPLETE/PARTIAL/MISSING | URLs real and accessible? |
| 7. Sentencing Summary | COMPLETE/PARTIAL/MISSING | All charges and outcomes listed? |
| 8. Production Notes | COMPLETE/PARTIAL/MISSING | Archetype recommended? Challenges identified? |

### 3. Accuracy Spot Check

Pick 3-5 specific claims from the research (dates, quotes, amounts) and verify them via web search:
- Is the date correct?
- Is the quote accurate?
- Is the dollar amount right?
- Does the URL still work?

Flag any discrepancies as `[NEEDS CORRECTION]`.

### 4. Footage Gap Analysis

Compare the footage inventory against the recommended archetype's requirements from the formula:
- **Bodycam-Domestic:** needs 55%+ bodycam
- **Trial-Centric:** needs 35-40% trial + 10-15% interrogation
- **Interrogation-Centric:** needs 40-50% interrogation room footage
- **Cold-Case:** needs evidence reveal footage + archival material

Identify specific gaps: "No interrogation footage found — this weakens the investigation section."

### 5. Production Red Flags

Flag any issues that would cause problems during production:
- Footage behind paywalls with no alternative
- Only one audio source available
- Key moments referenced but no footage found
- Legal concerns (active case, sealed evidence, minor victims)
- Content that requires extra sensitivity (child victims, graphic evidence)

## Output

Present the review as:

```
## Case Research Review: [Case Name]

### Viability: VIABLE / NOT VIABLE / VIABLE WITH GAPS

### Formula Requirements
[table from check 1]

### Completeness
[table from check 2]

### Accuracy Issues
[any corrections needed from check 3]

### Footage Gaps
[from check 4]

### Red Flags
[from check 5]

### Recommended Actions
- [specific things to fix/add before proceeding]

### Verdict
[1-2 sentence summary: is this ready for screenplay generation?]
```

If the research needs work, list the specific actions to take, then ask:
"Want me to fix these issues now?"

If the user says yes, make the corrections directly in the file, then re-run the review checks on the updated file.

If it's ready, say: "Research is solid. Run `/true-crime:generate-screenplay` to create the screenplay."
