# Screenshot Checklist

Run through this before any release that changes the UI (any `.tsx` file modified since last release).

## Automated (recommended)

```bash
# Captures all 7 screenshots, saves to docs/screenshots/vX.Y.Z/ and latest/
node scripts/capture-screenshots.mjs

# Or specify a version explicitly
node scripts/capture-screenshots.mjs v0.4.0
```

The script starts backend + frontend, loads the default storyboard, captures all views at 1440×900, and copies to `latest/`. Requires `playwright` (installed as dev dep).

## Required Screenshots

| # | File | What to capture |
|---|------|-----------------|
| 01 | `01-load-project.png` | Fresh state, no project loaded, form visible |
| 02 | `02-editor-main.png` | Project loaded, full layout with all panels |
| 03 | `03-segment-list.png` | Left sidebar: sections, segment highlighted |
| 04 | `04-video-player.png` | Center: player with transport controls |
| 05 | `05-media-library.png` | Right sidebar: file browser and categories |
| 06 | `06-production-bar.png` | Bottom bar: production controls |
| 07 | `07-storyboard-timeline.png` | Center column: player + timeline with segment selected |

## Manual Capture (fallback)

If the script doesn't capture what you need:

1. Start dev server: `./dev.sh`
2. Open browser at **1440×900** viewport
3. Load the Murdaugh storyboard (pre-filled default)
4. Capture each screenshot
5. Save to `docs/screenshots/vX.Y.Z/` and copy to `docs/screenshots/latest/`
