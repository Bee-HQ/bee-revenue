# Check Media — Footage, Audio, Images Audit

You are auditing all media files in a project directory to determine usability for a faceless YouTube true crime channel. For each file, produce an action plan — not a pass/fail.

## Setup

Ask: "Which project directory should I audit?"
- Look for case directories in `bee-content/discovery/true-crime/cases/*/`
- Scan these subdirectories: `footage/`, `stock/`, `photos/`, `music/`, `audio/`
- Also accept a specific directory path

## Process

### Step 1: Inventory all media files

Use `find` or `ls -R` to list every media file in the project:
- Video: `.mp4`, `.mkv`, `.webm`, `.mov`, `.avi`, `.ts`
- Audio: `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`
- Image: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`

Report the total count and size.

### Step 2: Probe each file

For every video and audio file, run ffprobe to get:
- Duration
- Resolution (width × height)
- Codec (video + audio)
- Container format
- Bitrate

For images, check dimensions and format.

Flag immediately:
- **Video duration < 3 seconds** → REJECT (too short to use)
- **Video resolution < 480p** → REJECT (too low quality)
- **Non-browser-playable container** (MPEG-TS, MKV, AVI) → action: CONVERT (remux to MP4)

### Step 3: Extract frames for visual inspection

For each video file that passed Step 2:
- Extract 8-10 frames evenly distributed across the video duration using FFmpeg:
  ```bash
  ffmpeg -i input.mp4 -vf "select='not(mod(n\,INTERVAL))'" -vsync vfn -frames:v 10 frame_%03d.jpg
  ```
  Or use timestamp-based extraction:
  ```bash
  ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 frame_001.jpg
  ffmpeg -i input.mp4 -ss 00:00:15 -frames:v 1 frame_002.jpg
  # ... evenly spaced across duration
  ```
- Save frames to a temp directory (clean up after audit)

For each image file: use the image directly (no extraction needed).

### Step 4: Visual inspection (using vision)

Look at the extracted frames / images and check for:

#### Logos & Watermarks
- **What to look for:** News channel bugs (CNN, Fox News, Court TV, ABC, NBC, MSNBC, HLN), stock footage watermarks (Shutterstock, Getty, Adobe Stock), social media handles (@username), website URLs, "EXCLUSIVE" or "BREAKING NEWS" banners
- **Where they appear:** Usually corners (top-left, top-right, bottom-right) or bottom bar
- **Action if found:**
  - If in a corner and small (< 15% of frame) → `CROP: recommend crop dimensions that remove it`
  - If along the bottom bar only → `CROP: recommend bottom crop (e.g., crop 1920x1000 from top)`
  - If center or large (> 15% of frame) → `REJECT: logo too prominent to crop`
  - Note which frames have the logo (it may appear/disappear)

#### Burned-in Text
- **What to look for:** Hard-coded subtitles/captions, chyrons, news tickers, location stamps, timestamps baked into the video
- **Action if found:**
  - If bottom-only captions → `CROP: recommend bottom crop` or `NOTE: can overlay with our own graphics`
  - If persistent news ticker → `CROP: recommend crop dimensions`
  - If center text → `REJECT: text too prominent`

#### Sensitive Content
- **What to look for:** Visible injuries, blood, bodies, autopsy images, graphic crime scene photos, evidence of violence
- **Action if found:** `BLUR: note timestamp range and screen position for blur overlay`
- Note severity: mild (distant/unclear) vs graphic (close-up/detailed)

#### Minors
- **What to look for:** Children's faces clearly visible
- **Action if found:** `BLUR: note timestamp range and position — must blur faces of minors`

#### Other YouTube Artifacts
- **What to look for:** Subscribe buttons, end screens, like/comment overlays, other channel's branding, intro/outro graphics from another creator
- **Action if found:**
  - If at start/end only → `TRIM: remove first/last N seconds`
  - If persistent → `REJECT: another channel's content`

#### Quality Assessment
- **What to look for:** Severe compression artifacts (blocky/pixelated), extreme color banding, unusable darkness
- **Action if found:** `NOTE: poor quality — human should review if usable`

### Step 5: Audio check

For video files with audio and standalone audio files:
- Listen description isn't possible, but note from ffprobe:
  - Audio codec and bitrate
  - Number of audio channels (mono/stereo)
  - If audio track exists at all

Note for the human to check:
- `AUDIO NOTE: check for copyrighted background music — replace with narration/our music if present`
- `AUDIO NOTE: check for other channel's narration/commentary — replace audio track if present`

For audio-only files (911 calls, interview recordings):
- Check duration (< 3s → REJECT)
- Check quality (bitrate < 32kbps → `NOTE: very low audio quality`)

### Step 6: Image check

For standalone images (photos, evidence, maps):
- Check dimensions (< 640px on either side → `NOTE: low resolution, will look pixelated at 1080p`)
- Check for watermarks/logos (same visual inspection as video frames)
- Check for sensitive content / minors (same rules as video)

## Output

Write a `media-audit.md` file in the project directory:

```markdown
# Media Audit: [Case Name]

**Audit Date:** [today]
**Total Files:** [N] ([N video] / [N audio] / [N image])
**Total Size:** [GB/MB]

## Summary

| Status | Count | Files |
|--------|-------|-------|
| USABLE | [N] | Ready to use as-is |
| USABLE WITH ACTIONS | [N] | Needs crop/convert/blur |
| NEEDS HUMAN REVIEW | [N] | Quality or audio concerns |
| REJECT | [N] | Too short / too low-res / unusable |

---

## File-by-File Report

### footage/bodycam/arrival.mp4
- **Duration:** 12:34
- **Resolution:** 1280x720
- **Codec:** H.264 / AAC
- **Status:** USABLE WITH ACTIONS
- **Actions:**
  1. CROP: Court TV logo in top-right corner → crop to 1200x720 from (0,0) or overlay with graphics
  2. CONVERT: container is MPEG-TS → remux to MP4
- **Content Notes:**
  - Crime scene visible at 3:45-4:12 — not graphic but review for sensitivity
  - No minors visible

### footage/trial/cross-exam.mp4
- **Duration:** 45:22
- **Resolution:** 1920x1080
- **Codec:** H.264 / AAC
- **Status:** USABLE WITH ACTIONS
- **Actions:**
  1. CROP: CNN bug bottom-right → crop to 1920x1040 from (0,0)
  2. TRIM: First 5 seconds has CNN intro bumper → trim from 0:05
- **Audio Notes:**
  - Check for background music during transitions — may need replacement

### photos/victim-portrait.jpg
- **Resolution:** 800x600
- **Status:** USABLE
- **Notes:** Good resolution for PIP overlay. No watermarks. No sensitive content.

### footage/911-call-clip.mp4
- **Duration:** 2.1s
- **Status:** REJECT
- **Reason:** Duration below 3-second minimum

---

## Recommended Actions Summary

### Immediate (before production)
- [ ] Remux 3 MPEG-TS files to MP4
- [ ] Crop Court TV logo from 5 files (all same position — batch crop possible)

### During editing
- [ ] Blur crime scene footage at bodycam/arrival.mp4 3:45-4:12
- [ ] Replace audio on trial/coverage.mp4 (contains CNN commentary)

### Human review needed
- [ ] Check audio/interview-raw.mp3 for usability (very low bitrate)
- [ ] Verify 2 files flagged for possible copyrighted music
```

## After the audit

1. Report the summary table
2. Highlight any files that are REJECT — these should not be used
3. Ask: "Want me to automatically remux/convert the files that need container conversion?"
4. Suggest: "Run `/true-crime:review-case-research` to verify footage inventory matches what's actually available"

## Important Notes

- **Clean up extracted frames** after the audit — don't leave hundreds of JPGs in the project
- **Be conservative with REJECT** — only reject if truly unusable. Most issues can be worked around with crop/blur/trim/audio replacement
- **Watermark position matters** — a small corner logo on bodycam footage is normal and croppable. A large center watermark on stock footage means we need a different source
- **Frame extraction count:** 8-10 frames for videos under 30 minutes, 15-20 for longer videos. Space them evenly — don't cluster at the beginning
