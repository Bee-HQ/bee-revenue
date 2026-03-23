# Debug Remotion Components

Debug and audit Remotion overlay/visual components in the Bee Video Editor. Requires Chrome browser access via Claude-in-Chrome.

**Two modes:**
- No arguments or `audit` → Full audit of all 14 component types
- A description (e.g., `"LowerThird not showing"`) → Debug a specific rendering issue

---

## Mode 1: Full Audit

Smoke test all 14 Remotion components using the 20-segment test storyboard.

### Step 1: Start dev servers

Check if ports 8420 and 5173 are in use:
```bash
lsof -i :8420 -i :5173 2>/dev/null | grep LISTEN
```

If not running, start them:
```bash
cd bee-content/video-editor/web && ./dev.sh
```
Wait 5 seconds, verify both ports are listening.

### Step 2: Load test storyboard

```bash
curl -s -X POST http://localhost:8420/api/projects/load \
  -H "Content-Type: application/json" \
  -d '{"storyboard_path": "test-new-components.md", "project_dir": "."}'
```

Use absolute paths resolved from the repo root if relative paths fail. The test storyboard is at `bee-content/video-editor/test-new-components.md` with project dir `bee-content/video-editor`.

### Step 3: Verify API data

Fetch the loaded project and check every segment:
```bash
curl -s http://localhost:8420/api/projects/current
```

For each segment, verify:
- **Visual types** are NOT collapsed to `GRAPHIC` — `TEXT_CHAT`, `SOCIAL_POST`, `EVIDENCE_BOARD`, `KINETIC_TEXT`, `CALLOUT`, `WAVEFORM` must be preserved
- **Overlay entries** have the expected `type` field (`LOWER_THIRD`, `TIMELINE_MARKER`, `QUOTE_CARD`, `FINANCIAL_CARD`, `TEXT_OVERLAY`, `CALLOUT`)
- **Structured fields** exist on entries with empty `content` (e.g., `text`, `subtext`, `date`, `description`, `quote`, `author`, `amount`)

If any visual type is wrongly mapped to `GRAPHIC`, the bug is in `web/shared/storyboard-parser.ts` → `VISUAL_TYPE_MAP`.

### Step 4: Open Chrome

1. Call `tabs_context_mcp` with `createIfEmpty: true`
2. Navigate to `http://localhost:5173`
3. Wait 3 seconds for project to load
4. Screenshot to verify the editor loaded with 20 segments

### Step 5: Test each component

For each of the 20 segments in order:
1. Click the segment name in the left sidebar
2. Press `ArrowRight` once or twice (advances 1-2 seconds past animation start)
3. Take a screenshot
4. Zoom into the preview area if needed to verify the component rendered
5. Record pass/fail

**Expected renders by segment:**

| # | Segment | Component | What to look for |
|---|---------|-----------|-----------------|
| 0 | LowerThird | LOWER_THIRD overlay | Name bar at bottom-left with red left border |
| 1 | TimelineMarker | TIMELINE_MARKER overlay | Red bar at top-right with date text |
| 2 | QuoteCard | QUOTE_CARD overlay | Centered quote with accent bar and author |
| 3 | FinancialCard | FINANCIAL_CARD overlay | Red panel at bottom with dollar amount |
| 4 | TextOverlay | TEXT_OVERLAY overlay | Centered text with typewriter effect |
| 5 | Callout Circle | CALLOUT overlay | SVG circle drawn on the frame |
| 6 | Callout Arrow | CALLOUT overlay | SVG arrow pointing to target |
| 7 | KineticText Punch | KINETIC_TEXT visual | Animated words with emphasis coloring |
| 8 | KineticText Highlight | KINETIC_TEXT visual | Words with highlight background |
| 9 | TextChat iMessage | TEXT_CHAT visual | iMessage-style chat bubbles |
| 10 | TextChat Android | TEXT_CHAT visual | Android-style chat bubbles |
| 11 | EvidenceBoard | EVIDENCE_BOARD visual | Conspiracy wall with pinned cards |
| 12 | SocialPost Twitter | SOCIAL_POST visual | Twitter card with author/text/likes |
| 13 | SocialPost Instagram | SOCIAL_POST visual | Instagram card |
| 14 | AudioVis Bars | WAVEFORM visual | Animated waveform bars with label |
| 15 | AudioVis Waveform | WAVEFORM visual | Waveform visualization |
| 16 | LT + QuoteCard stacked | Two overlays | Both LowerThird AND QuoteCard visible |
| 17 | Callout + TM stacked | Two overlays | Both TimelineMarker AND Callout visible |
| 18 | KT + Callout | Visual + overlay | KineticText background with Callout on top |
| 19 | Captions (NAR) | LowerThird + CC | LowerThird visible; enable CC button to test captions |

### Step 6: Check console

Read browser console for errors:
```
read_console_messages with pattern "error|Error|warn|Warning"
```
Report any component-related errors.

### Step 7: Report results

Output a summary table:

```markdown
## Remotion Component Audit — [date]

| # | Component | Type | Result | Notes |
|---|-----------|------|--------|-------|
| 0 | LowerThird | overlay | PASS | Name and role rendered |
| 1 | TimelineMarker | overlay | FAIL | Empty — metadata fallback missing |
...

### Errors
- [any console errors]

### Failures
- [root cause analysis for each FAIL]
```

---

## Mode 2: Debug Specific Issue

Systematic root cause investigation for a specific rendering problem.

### Step 1: Identify the component

Ask the user:
- Which component or segment is broken?
- What do they see vs what they expect?

### Step 2: Check the data shape

Fetch the project and inspect the relevant segment:
```bash
curl -s http://localhost:8420/api/projects/current | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data['segments']:
    if 'SEARCH_TERM' in s['title'].lower():
        print(json.dumps(s, indent=2))
"
```

Check:
- Is `content` empty? If so, are the structured fields present (`text`, `subtext`, `date`, `quote`, etc.)?
- Is the visual `type` correct, or was it collapsed to `GRAPHIC`?

### Step 3: Trace through the parser

Read `web/shared/storyboard-parser.ts`:
- Check `VISUAL_TYPE_MAP` — is the type mapped correctly?
- Check `normalizeVisualType()` — does it fall through to `GRAPHIC`?

If the type is being collapsed, the fix is adding it to `VISUAL_TYPE_MAP` with pass-through mapping.

### Step 4: Trace through BeeComposition

Read `web/src/components/BeeComposition.tsx`:
- For **overlays**: check `OVERLAY_COMPONENTS` registry — is the type registered?
- For **visuals**: check `VISUAL_COMPONENTS` registry and the `if (contentType === 'TYPE')` blocks in `SegmentVisual`
- For **LowerThird** specifically: check that `parseLowerThirdContent` is called with the overlay entry as second argument

### Step 5: Check the component

Read the specific component file in `web/src/components/remotion/`:
- Does it destructure `metadata` from props?
- Does it fall back to `metadata` fields when `content` is empty?
- For overlay parsers (`parseQuoteContent`, `parseDollarAmount`, `parseLowerThirdContent`): do they accept and use the optional `metadata` parameter?

### Step 6: Visual verification

Open Chrome, navigate to the segment, screenshot. Compare with expected render.

### Step 7: Report

```markdown
## Debug Report: [Component Name]

**Symptom:** [what the user reported]
**Root Cause:** [what's actually wrong]
**Location:** [file:line]
**Fix:** [what needs to change]
```

---

## Common Root Causes

These are the known failure patterns, ordered by frequency:

1. **Parser type collapse** — `storyboard-parser.ts` maps a Remotion-capable type to `GRAPHIC`. Fix: add pass-through entry in `VISUAL_TYPE_MAP`.

2. **Empty content without metadata fallback** — overlay entry has `content: ""` with data in separate fields (`text`, `subtext`, `date`, etc.), but the component only reads `content`. Fix: update parser function in `overlays.ts` to accept optional `metadata` param, update component to pass it.

3. **Component not in registry** — new component exists but isn't registered in `OVERLAY_COMPONENTS` or `VISUAL_COMPONENTS` in `BeeComposition.tsx`. Fix: add the mapping.

4. **Animation timing** — overlay appears to not render because the screenshot was taken at frame 0 (before slide-in/fade-in). Fix: advance 1-2 seconds past segment start before screenshotting.

5. **Missing metadata destructure** — component's function signature doesn't destructure `metadata` from `OverlayProps`. Fix: add `metadata` to the destructured props.

6. **Browser automation can't click timeline clips** — react-timeline-editor clips are small and coordinate-based clicks often miss. Each clip now has a `data-action-id` attribute and an `onClick` handler with `stopPropagation` (in `TimelineActionRenderer.tsx`). To select a clip via automation, use: `document.querySelector('[data-action-id="seg-01-ov-0"]').click()`. Action IDs follow the pattern `seg-{N}-{track}-{index}` (e.g., `seg-01-ov-0`, `seg-05-v-0`). For standard UI buttons (position grid, sliders, etc.), use the `find` tool with ref-based clicking.

## Key Files

| File | What to check |
|------|--------------|
| `web/shared/storyboard-parser.ts` | `VISUAL_TYPE_MAP`, `normalizeVisualType()` |
| `web/src/components/BeeComposition.tsx` | `OVERLAY_COMPONENTS`, `VISUAL_COMPONENTS`, `SegmentVisual`, `SegmentOverlays` |
| `web/src/components/remotion/overlays.ts` | `parseQuoteContent`, `parseDollarAmount`, `parseLowerThirdContent`, `OverlayProps` |
| `web/src/components/remotion/*.tsx` | Individual component prop handling |
| `bee-content/video-editor/test-new-components.md` | 20-segment test storyboard |
| `web/shared/types.ts` | `OverlayEntry` (has `[key: string]: any` index signature) |

## After debugging

1. Run tests: `cd web && npx vitest run`
2. Verify visually in Chrome
3. Commit fixes with descriptive message
