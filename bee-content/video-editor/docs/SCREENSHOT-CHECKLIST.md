# Screenshot Checklist

Run through this before any release that changes the UI (any `.tsx` file modified since last release).

## Setup

1. Start dev server: `./dev.sh`
2. Open browser at **1440×900** viewport
3. Load the Murdaugh storyboard (pre-filled default)

## Required Screenshots

| # | File | What to capture |
|---|------|-----------------|
| 01 | `01-load-project.png` | Fresh state, no project loaded, form visible |
| 02 | `02-editor-main.png` | Project loaded, segment selected, media visible — full layout |
| 03 | `03-segment-list.png` | Left sidebar: multiple sections, one segment highlighted |
| 04 | `04-video-player.png` | Center: playing or paused with transport controls visible |
| 05 | `05-media-library.png` | Right sidebar: files listed, category tabs, download panel closed |
| 06 | `06-production-bar.png` | Bottom bar: at least one action completed (green state) |
| 07 | `07-storyboard-timeline.png` | Timeline expanded for a segment showing all layers |

## Save Process

```bash
# 1. Save screenshots to the new version directory
cp *.png docs/screenshots/vX.Y.Z/

# 2. Update latest/
rm docs/screenshots/latest/*.png
cp docs/screenshots/vX.Y.Z/*.png docs/screenshots/latest/

# 3. Update CHANGELOG.md if new UI features were added
```

## Tips

- Use browser DevTools device toolbar for consistent 1440×900 viewport
- Crop to browser content area (no browser chrome)
- PNG format, no compression artifacts
- If a screenshot hasn't changed, skip it — only update what's new
