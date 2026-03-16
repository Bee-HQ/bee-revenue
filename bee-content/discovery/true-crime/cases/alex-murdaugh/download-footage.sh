#!/bin/bash
# Alex Murdaugh case footage download script
# Uses yt-dlp for video URLs, curl for direct media
export PATH="$HOME/.local/bin:/usr/bin:/bin:$PATH"

echo "=== Downloading Alex Murdaugh Case Footage ==="
echo "This will download key clips for video production."
echo ""

# 911 Call
echo "[1/10] 911 Call — Inside Edition"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/911-calls/murdaugh-911-call-insideedition.%(ext)s" \
  "https://www.insideedition.com/911-audio-from-the-murdaugh-murders-68596" 2>&1 || echo "  FAILED — try alternate URL"

# Bodycam — Crime Scene
echo "[2/10] Bodycam — Crime scene (Court TV redacted)"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/bodycam/crime-scene-bodycam-courttv.%(ext)s" \
  "https://www.courttv.com/title/bodycam-video-shows-alex-murdaugh-at-crime-scene-redacted/" 2>&1 || echo "  FAILED"

# Bodycam — Arrest at rehab
echo "[3/10] Bodycam — Arrest at rehab"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/bodycam/arrest-rehab-courttv.%(ext)s" \
  "https://www.courttv.com/title/body-camera-footage-shows-alex-murdaughs-arrest-outside-rehab/" 2>&1 || echo "  FAILED"

# SLED Interrogation — Full video
echo "[4/10] SLED Interrogation — Full first interview"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/interrogation/sled-first-interview-full.%(ext)s" \
  "https://www.courttv.com/title/alex-murdaugh-interrogation-full-video/" 2>&1 || echo "  FAILED"

# "I did him so bad" moment
echo "[5/10] 'I did him so bad' moment"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/interrogation/i-did-him-so-bad.%(ext)s" \
  "https://www.dailymotion.com/video/x8hrcfc" 2>&1 || echo "  FAILED"

# Trial — Opening statements (prosecution)
echo "[6/10] Trial — Prosecution opening statement"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/trial/prosecution-opening.%(ext)s" \
  "https://www.courttv.com/title/murdaugh-family-murders-prosecution-opening-statement/" 2>&1 || echo "  FAILED"

# Trial — Alex takes the stand
echo "[7/10] Trial — Alex testifies"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/trial/alex-testifies.%(ext)s" \
  "https://www.courttv.com/title/alex-murdaugh-says-he-didnt-kill-maggie-paul-but-lied-to-police/" 2>&1 || echo "  FAILED"

# Trial — Kennel video admission
echo "[8/10] Trial — Kennel lie admission"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/trial/kennel-lie-admission.%(ext)s" \
  "https://www.courttv.com/title/murdaugh-on-cross-everything-about-me-not-going-to-the-kennel-was-a-lie/" 2>&1 || echo "  FAILED"

# Trial — Verdict
echo "[9/10] Trial — Verdict reading"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/trial/verdict.%(ext)s" \
  "https://www.courttv.com/title/murdaugh-family-murders-watch-the-verdict/" 2>&1 || echo "  FAILED"

# Trial — Sentencing
echo "[10/10] Trial — Judge Newman sentencing"
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --no-playlist -o "footage/trial/sentencing-newman.%(ext)s" \
  "https://www.courttv.com/title/victim-to-verdict-murdaugh-family-murders/" 2>&1 || echo "  FAILED"

echo ""
echo "=== Download complete ==="
ls -lhR footage/
