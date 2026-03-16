# Video Production Recipes — FFmpeg + Pillow

Tested and working recipes for producing true crime YouTube videos programmatically. All commands use FFmpeg 8.0+ and Python Pillow.

**Note:** This FFmpeg build lacks `drawtext` filter (no freetype). Use Pillow to generate text as PNG overlays, then composite with FFmpeg.

---

## Audio Visualizations

### 911 Call Waveform (green line on black background)

```bash
ffmpeg -y -ss 0 -t 15 \
  -i "input-audio.mkv" \
  -filter_complex "[0:a]showwaves=s=1920x200:mode=cline:rate=30:colors=0x00ff88[waves];color=black:s=1920x1080:r=30:d=15[bg];[bg][waves]overlay=0:440[out]" \
  -map "[out]" -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -t 15 \
  output-waveform.mp4
```

**Customize:**
- `colors=0x00ff88` — green waveform. Use `0xff4444` for red, `0x4488ff` for blue
- `mode=cline` — centered line. Other modes: `line`, `p2p`, `point`
- `s=1920x200` — waveform height. Adjust `overlay=0:440` to reposition vertically
- Add text overlay PNG on top for caller name/date

### Audio Spectrum (fire/cinematic style)

```bash
ffmpeg -y -ss 0 -t 15 \
  -i "input-audio.mkv" \
  -filter_complex "[0:a]showspectrum=s=1920x400:mode=combined:color=fire:slide=scroll:scale=cbrt[spec];color=black:s=1920x1080:r=30:d=15[bg];[bg][spec]overlay=0:340[out]" \
  -map "[out]" -map 0:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -t 15 \
  output-spectrum.mp4
```

**Customize:**
- `color=fire` — fire palette. Others: `intensity`, `rainbow`, `channel`, `cool`, `magma`
- `slide=scroll` — scrolls left. Use `replace` for static refresh
- `scale=cbrt` — cube root scaling (emphasizes quieter sounds). Use `log`, `sqrt`, `lin`

---

## Photo Effects

### Ken Burns Zoom (slow zoom on static image)

```bash
ffmpeg -y -loop 1 -i "photo.jpg" \
  -vf "zoompan=z='min(zoom+0.0015,1.3)':d=240:s=1920x1080:fps=30" \
  -c:v libx264 -preset fast -crf 23 -t 8 \
  output-ken-burns.mp4
```

**Customize:**
- `zoom+0.0015` — zoom speed. Lower = slower. `0.001` for very slow, `0.003` for faster
- `1.3` — max zoom level (1.0 = no zoom, 1.5 = 50% zoom)
- `d=240` — total frames (240 at 30fps = 8 seconds)
- `-t 8` — duration in seconds

### Ken Burns Zoom OUT (start zoomed, pull back)

```bash
ffmpeg -y -loop 1 -i "photo.jpg" \
  -vf "zoompan=z='if(eq(on,1),1.3,max(zoom-0.0015,1.0))':d=240:s=1920x1080:fps=30" \
  -c:v libx264 -preset fast -crf 23 -t 8 \
  output-ken-burns-out.mp4
```

### Ken Burns Pan (slow pan left to right)

```bash
ffmpeg -y -loop 1 -i "photo.jpg" \
  -vf "zoompan=z='1.2':x='if(eq(on,1),0,min(x+1,iw-iw/zoom))':d=240:s=1920x1080:fps=30" \
  -c:v libx264 -preset fast -crf 23 -t 8 \
  output-ken-burns-pan.mp4
```

---

## Video Effects

### Slow Zoom on Video Footage

```bash
ffmpeg -y -ss 30 -t 8 \
  -i "input-video.mkv" \
  -vf "scale=2560:1440,zoompan=z='min(zoom+0.001,1.2)':d=240:s=1920x1080:fps=30" \
  -c:v libx264 -preset fast -crf 23 -c:a copy -t 8 \
  output-slow-zoom.mp4
```

**Note:** Input is upscaled first (2560x1440) to give zoompan room to zoom without losing quality.

### Dark/Desaturated Color Grade (crime scene look)

```bash
ffmpeg -y -ss 10 -t 8 \
  -i "input-video.mkv" \
  -vf "eq=brightness=-0.08:saturation=0.6:contrast=1.2,colorbalance=bs=0.1:bm=0.05" \
  -c:v libx264 -preset fast -crf 23 -c:a copy -t 8 \
  output-dark-grade.mp4
```

**Customize:**
- `brightness=-0.08` — slightly darker. Range: -1.0 to 1.0
- `saturation=0.6` — 60% saturation (desaturated). 0.0 = grayscale, 1.0 = normal
- `contrast=1.2` — slightly boosted contrast
- `colorbalance=bs=0.1:bm=0.05` — slight blue push in shadows/mids (cold crime look)

### Fade In from Black + Fade Out to Black

```bash
ffmpeg -y -ss 20 -t 8 \
  -i "input-video.mkv" \
  -vf "fade=in:0:30,fade=out:210:30" \
  -af "afade=in:st=0:d=1,afade=out:st=7:d=1" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -t 8 \
  output-faded.mp4
```

**Customize:**
- `fade=in:0:30` — video fade in starting at frame 0, over 30 frames (1 second at 30fps)
- `fade=out:210:30` — fade out starting at frame 210 (7 seconds), over 30 frames
- `afade=in:st=0:d=1` — audio fade in over 1 second
- `afade=out:st=7:d=1` — audio fade out starting at second 7

---

## Compositing

### Picture-in-Picture (photo over video)

```bash
ffmpeg -y -ss 10 -t 10 \
  -i "background-video.mkv" \
  -i "overlay-image.jpg" \
  -filter_complex "[1:v]scale=400:-1[pip];[0:v][pip]overlay=W-w-30:30" \
  -c:v libx264 -preset fast -crf 23 -c:a copy -t 10 \
  output-pip.mp4
```

**Customize:**
- `scale=400:-1` — overlay width 400px, height auto
- `overlay=W-w-30:30` — top-right corner with 30px margin
- Top-left: `overlay=30:30`
- Bottom-right: `overlay=W-w-30:H-h-30`
- Center: `overlay=(W-w)/2:(H-h)/2`

### PNG Overlay on Video (lower thirds, text cards)

```bash
ffmpeg -y -ss 30 -t 8 \
  -i "background-video.mkv" \
  -i "overlay.png" \
  -filter_complex "[0:v][1:v]overlay=0:0" \
  -c:v libx264 -preset fast -crf 23 -c:a copy \
  output-with-overlay.mp4
```

**The overlay PNG should be 1920x1080 with transparency (RGBA).** Only the non-transparent parts will show.

### Fade-in Overlay (lower third appears after 2 seconds)

```bash
ffmpeg -y -ss 30 -t 8 \
  -i "background-video.mkv" \
  -i "overlay.png" \
  -filter_complex "[1:v]fade=in:st=2:d=0.5:alpha=1[ovr];[0:v][ovr]overlay=0:0" \
  -c:v libx264 -preset fast -crf 23 -c:a copy \
  output-overlay-fadein.mp4
```

---

## Text/Graphics Generation (Pillow → PNG → FFmpeg)

Since this FFmpeg lacks `drawtext`, generate all text as PNG images with Pillow, then overlay.

### Lower Third

```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Semi-transparent dark bar
d.rectangle([(0, 920), (700, 1080)], fill=(0, 0, 0, 180))
# Red accent line
d.rectangle([(0, 920), (700, 924)], fill=(200, 30, 30, 255))
# Name
d.text((30, 940), "Person Name", fill=(255,255,255),
       font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42))
# Role
d.text((30, 990), "Role — Location", fill=(180,180,180),
       font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28))

img.save("lower-third.png")
```

### Key Quote Card

```python
img = Image.new('RGB', (1920, 1080), (15, 15, 20))
d = ImageDraw.Draw(img)

# Big red quote mark
d.text((200, 340), '"', fill=(200, 50, 50), font=get_font(120))

# Quote text (multi-line)
lines = ["Line one of the quote", "Line two continues", "Line three ends."]
y = 400
for line in lines:
    d.text((250, y), line, fill=(255,255,255), font=get_font(52))
    y += 65

# Attribution
d.text((250, y+40), "— Speaker Name, context", fill=(150,150,150), font=get_font(30))

img.save("quote-card.png")
# Convert to video:
# ffmpeg -y -loop 1 -i quote-card.png -c:v libx264 -t 5 -pix_fmt yuv420p -r 30 quote-card.mp4
```

### Timeline Marker

```python
img = Image.new('RGB', (1920, 1080), (10, 10, 15))
d = ImageDraw.Draw(img)

# Red accent line
d.rectangle([(860, 400), (1060, 404)], fill=(200, 40, 40))
# Date
d.text((960, 420), "June 7, 2021", fill=(255,255,255), font=get_font(72), anchor="mt")
# Description
d.text((960, 510), "The Night of the Murders", fill=(160,160,160), font=get_font(36), anchor="mt")

img.save("timeline.png")
# ffmpeg -y -loop 1 -i timeline.png -c:v libx264 -t 3 -pix_fmt yuv420p -r 30 timeline.mp4
```

### Financial Amount Card

```python
img = Image.new('RGB', (1920, 1080), (10, 10, 15))
d = ImageDraw.Draw(img)

d.text((960, 420), "$8,800,000+", fill=(220, 50, 50), font=get_font(96), anchor="mt")
d.text((960, 540), "Stolen from clients over a decade", fill=(180,180,180), font=get_font(32), anchor="mt")

img.save("financial.png")
# ffmpeg -y -loop 1 -i financial.png -c:v libx264 -t 4 -pix_fmt yuv420p -r 30 financial.mp4
```

### Map Location Card (placeholder — use Mapbox/MapLibre for real maps)

```python
img = Image.new('RGB', (1920, 1080), (20, 25, 30))
d = ImageDraw.Draw(img)

# Map area
d.rectangle([(100, 100), (1820, 900)], fill=(30, 40, 50))
# Location name
d.text((960, 200), "LOCATION NAME", fill=(255,255,255), font=get_font(48), anchor="mt")
d.text((960, 270), "City, County, State", fill=(180,180,180), font=get_font(32), anchor="mt")
# Pin
d.ellipse([(930, 450), (990, 510)], fill=(220, 40, 40))
d.polygon([(945, 500), (975, 500), (960, 540)], fill=(220, 40, 40))

img.save("map-card.png")
```

---

## Clip Operations

### Trim a Segment from Source Footage

```bash
# Extract 15 seconds starting at 2:30
ffmpeg -y -ss 2:30 -t 15 -i "source.mkv" -c copy "trimmed.mp4"

# Extract with re-encoding (needed if source has variable framerate)
ffmpeg -y -ss 2:30 -t 15 -i "source.mkv" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
  "trimmed.mp4"
```

### Normalize All Clips to Same Format Before Joining

```bash
# Normalize to 1920x1080, 30fps, H.264+AAC
ffmpeg -y -i "input.mkv" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,fps=30" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 \
  "normalized.mp4"
```

### Join/Concatenate Clips (the final assembly step)

**Method 1: Concat demuxer (fastest, no re-encoding if formats match)**

Create `segments.txt`:
```
file 'segment-01-cold-open.mp4'
file 'segment-02-dynasty.mp4'
file 'segment-03-victims.mp4'
...
```

```bash
ffmpeg -y -f concat -safe 0 -i segments.txt -c copy output-final.mp4
```

**Method 2: Concat filter (if formats differ, re-encodes)**

```bash
ffmpeg -y \
  -i segment1.mp4 -i segment2.mp4 -i segment3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
  output-final.mp4
```

---

## Audio Operations

### Mix Narration + Background Music

```bash
ffmpeg -y \
  -i "narration.wav" \
  -i "background-music.mp3" \
  -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:a aac -b:a 192k \
  "mixed-audio.m4a"
```

**Customize:**
- `volume=0.15` — music at 15% volume (under narration). Adjust to taste.
- `duration=first` — output length matches the narration, not the music

### Normalize Audio to YouTube Standard (-14 LUFS)

```bash
# Two-pass loudness normalization
ffmpeg -y -i "input.mp4" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null /dev/null 2>&1 | tail -12
# Use the measured values in second pass:
ffmpeg -y -i "input.mp4" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=-18:measured_TP=-3:measured_LRA=9:measured_thresh=-28" \
  -c:v copy -c:a aac -b:a 192k \
  "normalized.mp4"
```

### Extract Audio Only

```bash
ffmpeg -y -i "video.mkv" -vn -c:a aac -b:a 128k "audio-only.m4a"
# Or as WAV for TTS processing:
ffmpeg -y -i "video.mkv" -vn -c:a pcm_s16le -ar 44100 "audio-only.wav"
```

---

## Production Workflow (Step by Step)

### 1. Generate Assets
```bash
# Run Pillow script to create all PNGs:
python3 generate_graphics.py
# Creates: lower-thirds/*.png, quotes/*.png, timelines/*.png, financials/*.png, maps/*.png
```

### 2. Convert PNGs to Short Video Clips
```bash
for f in graphics/*.png; do
  ffmpeg -y -loop 1 -i "$f" -c:v libx264 -t 4 -pix_fmt yuv420p -r 30 "${f%.png}.mp4"
done
```

### 3. Trim Source Footage
```bash
# Per the assembly-guide.md trim notes:
ffmpeg -y -ss 0 -t 15 -i "footage/911-calls/call.mkv" -c:v libx264 -crf 23 -c:a aac "segments/01-911-call.mp4"
ffmpeg -y -ss 10 -t 10 -i "footage/bodycam/arrival.mkv" -c:v libx264 -crf 23 -c:a aac "segments/02-bodycam-arrival.mp4"
# ... etc for all segments in assembly guide
```

### 4. Normalize All Segments
```bash
for f in segments/*.mp4; do
  ffmpeg -y -i "$f" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,fps=30" \
    -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -ar 44100 \
    "normalized/${f##*/}"
done
```

### 5. Apply Overlays (lower thirds on footage segments)
```bash
ffmpeg -y -i "normalized/02-bodycam-arrival.mp4" \
  -i "graphics/lower-third-deputy-greene.png" \
  -filter_complex "[1:v]fade=in:st=2:d=0.5:alpha=1[ovr];[0:v][ovr]overlay=0:0" \
  -c:v libx264 -crf 23 -c:a copy \
  "composited/02-bodycam-with-lowerthird.mp4"
```

### 6. Generate Concat List
```bash
ls -1 composited/*.mp4 | sed 's/^/file /' > segments.txt
```

### 7. Final Join
```bash
ffmpeg -y -f concat -safe 0 -i segments.txt -c copy "FINAL-murdaugh-video.mp4"
```

### 8. Add Background Music
```bash
ffmpeg -y -i "FINAL-murdaugh-video.mp4" -i "background-music.mp3" \
  -filter_complex "[1:a]volume=0.12[bg];[0:a][bg]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k \
  "FINAL-murdaugh-with-music.mp4"
```

---

## Color Palette (Dr Insanity Style)

| Element | Color | Hex |
|---------|-------|-----|
| Background (dark) | Near black | `#0A0A0F` or `#0F0F14` |
| Primary text | White | `#FFFFFF` |
| Secondary text | Light gray | `#B4B4B4` |
| Accent (quotes, amounts, pins) | Dark red | `#DC3232` |
| Lower third bar | Black 70% opacity | `rgba(0,0,0,180)` |
| Lower third accent | Red | `#C81E1E` |
| Waveform (911 calls) | Green | `#00FF88` |
| Waveform (interrogation) | Blue | `#4488FF` |
| Financial amounts | Red | `#DC3232` |
| Timeline markers | Red accent line | `#C82828` |
