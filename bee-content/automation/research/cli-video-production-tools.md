# CLI Video Production Tools for True Crime YouTube Content

> Research date: 2026-03-15
> Focus: Practical CLI tools for automated faceless true crime video production

---

## 1. FFmpeg (The Foundation)

FFmpeg is the backbone of nearly every video automation pipeline. Every tool in this document either wraps FFmpeg or depends on it.

### Overlay an image on video (photo hovering over footage)

```bash
# Place photo.png at position (100,50) on top of background.mp4
ffmpeg -i background.mp4 -i photo.png \
  -filter_complex "[0:v][1:v]overlay=100:50:enable='between(t,2,8)'" \
  -c:a copy output.mp4
```

The `enable` parameter controls when the overlay appears (seconds 2-8). For a centered overlay with padding/border effect, scale the image first:

```bash
ffmpeg -i background.mp4 -i photo.png \
  -filter_complex "\
    [1:v]scale=400:-1,pad=420:ih+20:10:10:white[img];\
    [0:v][img]overlay=(W-w)/2:(H-h)/2:enable='between(t,3,10)'" \
  output.mp4
```

### Ken Burns effect (zoom/pan on still photos)

```bash
# Slow zoom-in on a photo over 8 seconds, output 1920x1080
ffmpeg -loop 1 -i photo.jpg -t 8 \
  -vf "zoompan=z='min(zoom+0.001,1.5)':d=240:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30" \
  -c:v libx264 -pix_fmt yuv420p ken_burns.mp4
```

Parameters:
- `z='min(zoom+0.001,1.5)'` — zoom speed and max zoom (1.5x)
- `d=240` — duration in frames (240 frames = 8s at 30fps)
- `x` and `y` — pan position (centered here)

Zoom out variant: `z='if(eq(on,1),1.5,max(zoom-0.001,1))'`

### Burn styled subtitles (ASS/SSA)

```bash
# Burn ASS subtitles (styled, positioned)
ffmpeg -i video.mp4 -vf "ass=subtitles.ass" -c:a copy output.mp4

# Burn SRT with custom styling
ffmpeg -i video.mp4 \
  -vf "subtitles=subs.srt:force_style='FontName=Montserrat,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,MarginV=40'" \
  -c:a copy output.mp4
```

ASS format gives full control: per-word colors, karaoke timing, position, animations. SRT `force_style` is simpler but less flexible.

### Picture-in-picture

```bash
# Small video (320x180) in bottom-right corner
ffmpeg -i main.mp4 -i pip_source.mp4 \
  -filter_complex "\
    [1:v]scale=320:180[pip];\
    [0:v][pip]overlay=W-w-20:H-h-20" \
  -c:a copy output.mp4
```

### Audio mixing (narration + background music)

```bash
# Mix narration at full volume with music at 15% volume
ffmpeg -i narration.wav -i background_music.mp3 \
  -filter_complex "\
    [1:a]volume=0.15[music];\
    [0:a][music]amix=inputs=2:duration=first:dropout_transition=3" \
  -c:v copy mixed_audio.mp3

# Ducking: lower music volume when narration is present
ffmpeg -i narration.wav -i music.mp3 \
  -filter_complex "[0:a]asplit=2[voice][sc];[sc]silencedetect=n=-30dB:d=0.5[silence];[1:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=first" \
  output.wav
```

For true ducking, a Python script with pydub or MoviePy is more practical than pure FFmpeg.

### Text overlays (drawtext)

```bash
# White text with black outline, bottom-center
ffmpeg -i video.mp4 \
  -vf "drawtext=text='MISSING SINCE 2019':fontfile=/path/to/Montserrat-Bold.ttf:\
    fontsize=48:fontcolor=white:borderw=3:bordercolor=black:\
    x=(w-text_w)/2:y=h-th-60:enable='between(t,5,15)'" \
  output.mp4

# Multi-line with line breaks
ffmpeg -i video.mp4 \
  -vf "drawtext=text='Line 1\nLine 2':fontfile=font.ttf:\
    fontsize=36:fontcolor=white:borderw=2:bordercolor=black:\
    x=(w-text_w)/2:y=(h-text_h)/2" \
  output.mp4
```

### Transitions (crossfade)

```bash
# Crossfade between two clips (1 second transition)
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "\
    [0:v][1:v]xfade=transition=fade:duration=1:offset=4[v];\
    [0:a][1:a]acrossfade=d=1[a]" \
  -map "[v]" -map "[a]" output.mp4
```

Available transitions: `fade`, `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `circlecrop`, `dissolve`, `pixelize`, `diagtl`, `diagtr`, `hlslice`, `hrslice`, and more.

### Fade in/out

```bash
# 2-second fade in, 2-second fade out (video is 30 seconds)
ffmpeg -i video.mp4 \
  -vf "fade=t=in:st=0:d=2,fade=t=out:st=28:d=2" \
  -af "afade=t=in:st=0:d=2,afade=t=out:st=28:d=2" \
  output.mp4
```

### Concatenate clips with transitions (batch)

```bash
# Simple concat (no transitions, same codec)
# Create file list:
echo "file 'clip1.mp4'" > filelist.txt
echo "file 'clip2.mp4'" >> filelist.txt
echo "file 'clip3.mp4'" >> filelist.txt

ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

---

## 2. Python Video Libraries

### MoviePy

- **GitHub**: ~13k stars, actively maintained
- **Current version**: 2.2.1 (Feb 2026) — major v2.0 rewrite
- **License**: MIT
- **Status**: Seeking additional maintainers but functional

MoviePy wraps FFmpeg with a Pythonic API. v2.0 renamed all `.set_*` methods to `.with_*` (immutable pattern).

```python
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip

# Composite: narration video + photo overlay + text
bg = VideoFileClip("dark_bg.mp4").subclipped(0, 30)
photo = (ImageClip("victim_photo.jpg")
         .resized(width=400)
         .with_position(("center", 100))
         .with_start(3).with_duration(8)
         .with_effects([vfx.CrossFadeIn(1), vfx.CrossFadeOut(1)]))

title = (TextClip("Montserrat-Bold.ttf", text="THE DISAPPEARANCE",
                   font_size=52, color="white", stroke_color="black", stroke_width=2)
         .with_position(("center", 500))
         .with_start(3).with_duration(5))

narration = AudioFileClip("narration.wav")
music = AudioFileClip("ambient.mp3").with_effects([afx.MultiplyVolume(0.15)])

video = CompositeVideoClip([bg, photo, title])
video = video.with_audio(CompositeAudioClip([narration, music]))
video.write_videofile("output.mp4", fps=30, codec="libx264", audio_codec="aac")
```

**Strengths**: Easy compositing, overlays, text. Good for assembling pre-rendered assets.
**Weaknesses**: Slow rendering (no GPU), memory-hungry on long videos (>20 min). For 40-min videos, consider rendering in segments.

### Remotion (React/Node.js)

- **GitHub**: ~22k stars
- **License**: Business Source License (free for individuals/small teams, paid for companies >$1M revenue)
- **Approach**: Write video as React components, render with headless Chromium + FFmpeg

```tsx
// MyVideo.tsx
import { useCurrentFrame, useVideoConfig, Img, AbsoluteFill } from "remotion";

export const CrimeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = Math.min(1, frame / (fps * 2)); // 2-second fade in

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <Img src="/victim.jpg"
        style={{ opacity, transform: `scale(${1 + frame * 0.0005})` }} />
      <h1 style={{ color: "white", position: "absolute", bottom: 100 }}>
        THE DISAPPEARANCE
      </h1>
    </AbsoluteFill>
  );
};
```

```bash
# Render from CLI
npx remotion render src/index.ts MyVideo output.mp4 --codec h264
```

**Strengths**: Full CSS/JS power, complex animations, cloud rendering via Remotion Lambda (AWS).
**Weaknesses**: Heavy setup, slow rendering (Chromium overhead), BSL license for larger companies.

### Editly

- **GitHub**: ~5k stars
- **License**: MIT
- **Approach**: JSON spec -> FFmpeg rendering via Node.js

```json
{
  "outPath": "output.mp4",
  "width": 1920, "height": 1080, "fps": 30,
  "defaults": { "transition": { "name": "fade", "duration": 0.5 } },
  "clips": [
    {
      "duration": 8,
      "layers": [
        { "type": "image", "path": "crime_scene.jpg", "zoomDirection": "in" },
        { "type": "title", "text": "THE CASE OF...", "position": "bottom" }
      ]
    },
    {
      "duration": 10,
      "layers": [
        { "type": "video", "path": "b_roll.mp4", "cutFrom": 5, "cutTo": 15 },
        { "type": "subtitle", "text": "Police arrived at 11:42 PM" }
      ]
    }
  ]
}
```

```bash
npx editly spec.json5 --fast  # preview mode (lower quality, faster)
npx editly spec.json5          # full quality render
```

**Strengths**: Simple declarative format, built-in transitions/effects, Ken Burns built in.
**Weaknesses**: Less maintained recently, limited animation control vs Remotion.

### Manim (3B1B's math animation library)

- **GitHub**: Community Edition ~25k stars
- **Use case**: Data visualizations, timeline animations, map overlays

```python
from manim import *

class CrimeTimeline(Scene):
    def construct(self):
        timeline = NumberLine(x_range=[0, 24, 1], length=10,
                              include_numbers=True, label_direction=DOWN)
        self.play(Create(timeline))

        events = [(8, "Last seen"), (11, "911 call"), (14, "Body found")]
        for hour, label in events:
            dot = Dot(timeline.n2p(hour), color=RED)
            text = Text(label, font_size=20).next_to(dot, UP)
            self.play(FadeIn(dot), Write(text))
            self.wait(0.5)
```

```bash
manim -pqh crime_timeline.py CrimeTimeline  # render at 1080p
```

Output is a video file that can be composited as an overlay.

### Pillow / ImageMagick

For pre-processing images before video assembly:

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Create a "evidence photo" effect with border and label
img = Image.open("photo.jpg")
img = img.resize((600, 400))

# Add white border
bordered = Image.new("RGB", (640, 470), "white")
bordered.paste(img, (20, 20))

# Add label
draw = ImageDraw.Draw(bordered)
font = ImageFont.truetype("Montserrat-Bold.ttf", 24)
draw.text((20, 435), "Evidence Photo #3", fill="black", font=font)
bordered.save("evidence_card.png")
```

ImageMagick CLI for batch operations:

```bash
# Add vignette + desaturate for "old photo" effect
magick photo.jpg -modulate 100,50 -vignette 0x40 old_photo.jpg

# Batch resize all photos
magick mogrify -resize 1920x1080^ -gravity center -extent 1920x1080 photos/*.jpg
```

---

## 3. Map Animations

### Mapbox Static API

```bash
# Get a satellite image of a location
curl "https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/static/-73.9857,40.7484,14,0/1280x720@2x?access_token=YOUR_TOKEN" -o map.png

# Dark style (good for true crime)
curl "https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/-73.9857,40.7484,14,0/1280x720@2x?access_token=YOUR_TOKEN" -o map_dark.png

# With a marker
curl "https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/pin-l+ff0000(-73.9857,40.7484)/-73.9857,40.7484,14/1280x720@2x?access_token=YOUR_TOKEN" -o map_marker.png
```

**Pricing** (as of 2026):
- Free tier: 100,000 static map requests/month
- Beyond free tier: $0.50 per 1,000 requests
- 1280x720@2x images count as 2 requests

### Google Maps Static API

```bash
curl "https://maps.googleapis.com/maps/api/staticmap?\
center=40.7484,-73.9857&zoom=14&size=1280x720&scale=2\
&maptype=satellite&key=YOUR_KEY" -o google_map.png
```

**Pricing**:
- $2.00 per 1,000 requests (first 100k/month)
- Free $200/month credit = ~100k free requests
- More expensive than Mapbox at scale

### Google Earth Studio

Google Earth Studio is a **browser-based** animation tool (earth.google.com/studio). It renders 3D Earth flyovers.

**Can it be scripted?** Not officially. It is a manual browser GUI tool. However:
- You can save and re-render project files (.esp)
- No CLI or API exists
- Workaround: Use Puppeteer/Playwright to automate the browser, but this is fragile and against ToS
- Better alternative: Pre-render flyover clips manually and integrate them via automation pipeline

### Programmatic "zoom into location" animation

The simplest approach: generate map images at increasing zoom levels, then animate with FFmpeg.

```python
import requests

# Generate 30 frames zooming from level 3 to level 16
lat, lon = 40.7484, -73.9857
token = "YOUR_MAPBOX_TOKEN"
frames = []

for i in range(30):
    zoom = 3 + (13 * i / 29)  # 3 -> 16
    url = f"https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/{lon},{lat},{zoom:.1f},0/1920x1080@2x?access_token={token}"
    r = requests.get(url)
    frame_path = f"frames/frame_{i:03d}.png"
    with open(frame_path, "wb") as f:
        f.write(r.content)
    frames.append(frame_path)
```

Then assemble with FFmpeg:

```bash
# Turn frames into a smooth zoom animation (hold each frame for 0.2s)
ffmpeg -framerate 5 -i frames/frame_%03d.png \
  -vf "minterpolate=fps=30:mi_mode=blend" \
  -c:v libx264 -pix_fmt yuv420p zoom_animation.mp4
```

Cost: 30 Mapbox API calls = negligible (well within free tier).

### FFmpeg zoompan on a single map image (simplest)

If you just need a basic zoom effect, download one high-res map image and use zoompan:

```bash
# Download a high-res map, then Ken Burns zoom into it
ffmpeg -loop 1 -i map_highres.png -t 6 \
  -vf "zoompan=z='min(zoom+0.003,2.5)':d=180:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30" \
  -c:v libx264 -pix_fmt yuv420p map_zoom.mp4
```

This is free and requires no API calls, but lacks the "Google Earth" 3D effect.

---

## 4. Subtitle & Caption Tools (CLI)

### OpenAI Whisper

```bash
# Install
pip install openai-whisper

# Transcribe with word-level timestamps
whisper narration.wav --model large-v3 --output_format all --word_timestamps True

# Output files: narration.srt, narration.vtt, narration.json, narration.ass
```

**Models and accuracy**:
| Model | Size | VRAM | English WER | Speed (rel.) |
|-------|------|------|-------------|--------------|
| tiny | 39M | ~1GB | ~7.5% | 32x |
| base | 74M | ~1GB | ~5.5% | 16x |
| small | 244M | ~2GB | ~4.2% | 6x |
| medium | 769M | ~5GB | ~3.5% | 2x |
| large-v3 | 1.5B | ~10GB | ~2.7% | 1x |

For true crime narration (clear speech, single speaker), `medium` typically achieves excellent results.

### faster-whisper

```bash
pip install faster-whisper

# Python usage
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="int8")
segments, info = model.transcribe("narration.wav", word_timestamps=True)

for segment in segments:
    print(f"[{segment.start:.2f} -> {segment.end:.2f}] {segment.text}")
    for word in segment.words:
        print(f"  {word.word} [{word.start:.2f}-{word.end:.2f}]")
```

**Speed improvement**: 4x faster than OpenAI Whisper with identical accuracy. Uses CTranslate2 (INT8/FP16 quantization). On CPU, a 40-minute audio file transcribes in ~4 minutes with `large-v3`.

Batched faster-whisper can achieve 12x speedup over original Whisper.

### ASS/SSA format for styled subtitles

ASS gives per-word control over colors, position, and animation:

```ass
[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,Italic,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV
Style: Default,Montserrat,48,&H00FFFFFF,&H00000000,&H80000000,1,0,1,3,1,2,20,20,60

[Events]
Format: Layer,Start,End,Style,Text
Dialogue: 0,0:00:05.00,0:00:08.00,Default,{\pos(960,900)}The body was found at {\c&H0000FF&}midnight{\c&HFFFFFF&}.
```

Key ASS tags:
- `\pos(x,y)` — exact position
- `\c&HBBGGRR&` — color (BGR format)
- `\fad(fadein_ms,fadeout_ms)` — fade timing
- `\k50` — karaoke timing (word highlight, centiseconds)
- `\an8` — top-center alignment

### Word-by-word animated captions

Generate karaoke-style ASS from Whisper word timestamps:

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="int8")
segments, _ = model.transcribe("narration.wav", word_timestamps=True)

with open("captions.ass", "w") as f:
    f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n")
    f.write("[V4+ Styles]\n")
    f.write("Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,BorderStyle,Outline,Shadow,Alignment,MarginV\n")
    f.write("Style: Default,Montserrat,52,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,1,3,1,2,80\n\n")
    f.write("[Events]\nFormat: Layer,Start,End,Style,Text\n")

    for seg in segments:
        words = list(seg.words)
        if not words:
            continue
        start = words[0].start
        end = words[-1].end

        # Build karaoke line: highlight each word as it's spoken
        line_parts = []
        prev_end = start
        for w in words:
            gap = int((w.start - prev_end) * 100)
            dur = int((w.end - w.start) * 100)
            if gap > 0:
                line_parts.append(f"{{\\k{gap}}}")
            line_parts.append(f"{{\\kf{dur}}}{w.word}")
            prev_end = w.end

        def fmt(t):
            h, m, s = int(t//3600), int((t%3600)//60), t%60
            return f"{h}:{m:02d}:{s:05.2f}"

        f.write(f"Dialogue: 0,{fmt(start)},{fmt(end)},Default,{''.join(line_parts)}\n")
```

### FFmpeg subtitle burn-in commands

```bash
# Burn ASS subtitles (preserves all styling)
ffmpeg -i video.mp4 -vf "ass=captions.ass" -c:a copy output.mp4

# Burn SRT with custom font
ffmpeg -i video.mp4 \
  -vf "subtitles=captions.srt:force_style='FontName=Montserrat,FontSize=28,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=50'" \
  -c:a copy output.mp4

# For fonts not in system path, specify fontsdir
ffmpeg -i video.mp4 \
  -vf "subtitles=captions.ass:fontsdir=/path/to/fonts/" \
  -c:a copy output.mp4
```

---

## 5. Audio Visualization

### FFmpeg showwaves (911 call waveform)

```bash
# Green waveform on black background
ffmpeg -i 911_call.wav \
  -filter_complex "showwaves=s=1920x200:mode=cline:colors=0x00ff00:rate=30[waves];\
    color=c=black:s=1920x1080:d=60[bg];\
    [bg][waves]overlay=0:(H-h)/2" \
  -c:v libx264 -pix_fmt yuv420p -shortest waveform.mp4

# With showspectrum (frequency visualization)
ffmpeg -i 911_call.wav \
  -filter_complex "showspectrum=s=1920x400:mode=combined:color=intensity:scale=log:slide=scroll[spec];\
    color=c=black:s=1920x1080:d=60[bg];\
    [bg][spec]overlay=0:(H-h)/2" \
  -c:v libx264 -shortest spectrum.mp4
```

**showwaves modes**: `point`, `line`, `p2p` (point-to-point), `cline` (centered line)

### Composite waveform over video

```bash
# Overlay waveform at bottom of existing video
ffmpeg -i video.mp4 -i 911_call.wav \
  -filter_complex "\
    [1:a]showwaves=s=1920x150:mode=cline:colors=0x00ff00@0.8:rate=30[waves];\
    [0:v][waves]overlay=0:H-h-50" \
  -c:a copy -shortest output.mp4
```

### Python librosa + matplotlib (custom visualization)

```python
import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load audio
y, sr = librosa.load("911_call.wav", sr=22050)
duration = librosa.get_duration(y=y, sr=sr)
fps = 30
total_frames = int(duration * fps)

fig, ax = plt.subplots(figsize=(19.2, 2), dpi=100)
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
ax.set_xlim(0, 1)
ax.set_ylim(-1, 1)
ax.axis("off")

window = sr // fps  # samples per frame

def animate(frame_num):
    ax.clear()
    ax.set_facecolor("black")
    ax.set_xlim(0, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")

    start = frame_num * window
    end = start + window * 60  # show ~2 seconds of audio
    chunk = y[start:end]

    if len(chunk) > 0:
        x = np.linspace(0, 1, len(chunk))
        ax.plot(x, chunk, color="#00ff00", linewidth=0.5, alpha=0.8)
        ax.fill_between(x, chunk, alpha=0.3, color="#00ff00")

    return []

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=True)
anim.save("waveform_custom.mp4", writer="ffmpeg", fps=fps,
          savefig_kwargs={"facecolor": "black"})
```

For true crime 911 calls, this approach lets you add custom elements: caller ID labels, timestamp overlays, redaction bleeps visualization, etc.

---

## 6. AI Dubbing & Translation — Pricing Comparison

### Cost estimate for a 40-minute true crime video (single target language)

| Tool | Cost Model | ~Cost for 40 min (1 lang) | Languages | Voice Clone | API | Quality Notes |
|------|-----------|---------------------------|-----------|-------------|-----|---------------|
| **ElevenLabs** | $0.24-0.60/min (plan-dependent) | $10-24 | 29 | Yes (excellent) | Yes | Best voice quality, natural prosody |
| **Rask AI** | $1.50-3.00/min | $60-120 | 130+ | Yes (lip-sync extra) | Yes | Good lip-sync, high cost |
| **HeyGen** | ~$0.25-0.50/min (credit-based) | $10-20 | 40+ | Yes | Yes | Best for avatar videos, unlimited dubbing on paid plans (Feb 2026+) |
| **Speechify** | ~$0.48/min (3 credits/sec) | $19 (Starter plan covers 40 min) | 100+ | Limited | Yes | Good for narration, credit-hungry for dubbing |
| **Murf AI** | $19-59/mo plans | $19-59 (plan) | 44 | No (voice library) | Yes | Clean TTS, translation only on Enterprise |
| **Papercup** | Custom quote | $200-500+ (enterprise) | 70+ | Yes (human QA) | No | Highest quality (human review), enterprise only |
| **Dubverse** | $18-30/mo plans | $18-30 (plan) | 30+ | Limited | Yes | Budget option, decent quality |
| **OpenAI Whisper+TTS (DIY)** | ~$0.015/min TTS + transcription | $1-2 total | 50+ | No | Yes | Cheapest, requires pipeline work |

### DIY Pipeline cost breakdown (OpenAI Whisper + TTS)

For a 40-minute video:
1. **Transcription** (Whisper API): ~$0.006/min = $0.24
2. **Translation** (GPT-4o-mini): ~5,000 words = ~$0.02
3. **TTS** (tts-1): ~40,000 chars = $0.60
4. **Total**: ~$0.86 per language

This is 10-100x cheaper but requires building the pipeline and quality is below ElevenLabs.

### Open Source Alternatives

**Meta SeamlessM4T**
- Speech-to-speech translation in 100+ languages
- Free, runs locally (needs GPU with 8GB+ VRAM)
- Quality: Good for European languages, weaker on low-resource languages
- No voice cloning — uses generic voices
```bash
pip install seamless_communication
# Python: translate audio directly
from seamless_communication.inference import Translator
translator = Translator("seamlessM4T_v2_large", "vocoder_v2", device="cuda")
translated, _, _ = translator.predict("narration.wav", "s2st", "spa")
```

**Coqui TTS** (archived but still functional)
- Open source TTS with voice cloning (XTTS-v2)
- Supports 17 languages
- Voice cloning from 6-second sample
- Quality: Good, not ElevenLabs-level
- Note: Coqui the company shut down in late 2023, but the open-source code lives on
```bash
pip install TTS
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "The victim was last seen..." \
    --speaker_wav reference_voice.wav \
    --language_idx en \
    --out_path output.wav
```

**Bark (Suno)**
- Open source, generates highly natural speech with emotions, laughter, etc.
- Supports ~13 languages
- No voice cloning (speaker presets only)
- Slow generation (~10x realtime on GPU)
- Best for short clips, not 40-minute narrations
```python
from bark import generate_audio, SAMPLE_RATE
import scipy
audio = generate_audio("The police arrived at [sighs] eleven forty-two PM.")
scipy.io.wavfile.write("output.wav", rate=SAMPLE_RATE, data=audio)
```

---

## 7. Automation Pipeline Architecture

### End-to-end pipeline: Script to Upload

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌────────┐
│  Script  │───>│   TTS   │───>│  Video   │───>│ Subtitles │───>│ Upload │
│Generator │    │(Narrate)│    │ Assembly │    │  Burn-in  │    │(YT API)│
└─────────┘    └─────────┘    └──────────┘    └───────────┘    └────────┘
     │              │              │                │
     v              v              v                v
  GPT-4o      ElevenLabs/     MoviePy or      Whisper +
  or local    OpenAI TTS      FFmpeg          ASS generation
  LLM         or Coqui
```

### Detailed pipeline steps

```python
# pipeline.py — simplified orchestrator
import subprocess, json, os

def pipeline(topic: str, output_path: str):
    # 1. Generate script (via LLM API)
    script = generate_script(topic)  # returns structured JSON with segments

    # 2. Generate narration audio
    audio_path = generate_tts(script["narration_text"])  # -> narration.wav

    # 3. Transcribe for subtitles (word-level)
    subs_path = transcribe_to_ass(audio_path)  # -> captions.ass

    # 4. Gather visual assets
    assets = gather_assets(script["segments"])  # download stock, maps, photos

    # 5. Assemble video segments with Ken Burns / overlays
    segments = []
    for seg in script["segments"]:
        clip = render_segment(seg, assets)  # FFmpeg commands per segment
        segments.append(clip)

    # 6. Concatenate + add audio + burn subtitles
    concat_clips(segments, "raw_video.mp4")
    mix_audio("raw_video.mp4", audio_path, "bg_music.mp3", "with_audio.mp4")
    burn_subtitles("with_audio.mp4", subs_path, output_path)

    # 7. Upload (optional)
    # upload_to_youtube(output_path, script["title"], script["description"])
```

### Cloud Rendering: Shotstack vs Creatomate vs Remotion

| Feature | Shotstack | Creatomate | Remotion Lambda |
|---------|-----------|------------|-----------------|
| **Pricing** | $49/mo (200 min) | $41/mo (~200 min) | AWS Lambda costs (~$0.01-0.05/min) |
| **Per-minute cost** | $0.20-0.40 | $0.20-0.35 | ~$0.01-0.05 (AWS) |
| **Resolution** | Up to 4K (same price) | 4K costs more credits | Any (you control) |
| **API style** | JSON timeline | JSON timeline | React components |
| **Render speed** | ~10x faster than Creatomate | Slower at high res | Depends on Lambda config |
| **Best for** | Simple automated videos | Template-based content | Complex custom animations |
| **Self-host** | No | No | Yes (your AWS account) |

For true crime content (40-min long-form), cloud rendering gets expensive. Recommended approach:
- **Remotion Lambda** for complex segments (intros, map animations) — render in parallel
- **FFmpeg locally** for bulk assembly (concatenation, audio mixing, subtitle burn-in)

### MoneyPrinterTurbo

An open-source Python tool (MIT license, ~20k GitHub stars) for automated short video generation.

**What it does**:
1. Takes a topic/keyword as input
2. Generates a script via LLM (OpenAI, Moonshot, Azure, etc.)
3. Sources stock video from Pexels/Pixabay
4. Generates voiceover via TTS
5. Creates subtitles
6. Assembles everything into a short video (typically under 1 minute)

**Limitations for true crime**:
- Designed for short-form (< 1 min), not 40-minute documentaries
- Generic stock footage, no evidence photos or maps
- No advanced compositing (overlays, picture-in-picture)
- Good as a starting point / reference architecture, not a production tool for this use case

**Setup**:
```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
pip install -r requirements.txt
# Configure API keys in config.toml
python main.py  # launches web UI
```

### Estimated Rendering Times

For a 40-minute true crime video (1080p, 30fps):

| Method | Hardware | Approx Time |
|--------|----------|-------------|
| FFmpeg (libx264) | M2 MacBook Pro | 15-25 min |
| FFmpeg (libx264) | Linux, i7 12th gen | 20-35 min |
| FFmpeg (h264_videotoolbox) | M2 Mac (HW accel) | 5-10 min |
| FFmpeg (h264_nvenc) | Linux + RTX 3080 | 3-8 min |
| MoviePy | M2 MacBook Pro | 40-60 min |
| Remotion | M2 MacBook Pro | 60-120 min |
| Remotion Lambda | 200 Lambda functions | 5-15 min |
| Shotstack API | Cloud | 4-8 min |

**Optimization tips**:
- Use hardware-accelerated encoding: `-c:v h264_videotoolbox` (macOS) or `-c:v h264_nvenc` (NVIDIA)
- Render segments in parallel, concatenate at the end
- Use `-preset ultrafast` for drafts, `-preset slow` for final render
- Pre-render Ken Burns clips and composites as intermediate files
- For MoviePy, use `threads=4` or higher in `write_videofile()`

### Recommended Stack for True Crime Automation

```
Script:        GPT-4o / Claude (structured JSON output)
Narration:     ElevenLabs (quality) or OpenAI TTS (budget)
Subtitles:     faster-whisper (local) → ASS with word-level karaoke
Maps:          Mapbox Static API → FFmpeg zoompan
Photos:        Pillow (borders, effects) → FFmpeg overlay
Assembly:      FFmpeg (concat, overlay, transitions)
Audio:         FFmpeg (amix for narration + music)
Orchestrator:  Python script chaining all steps
```

Total cost per video (excluding LLM for script):
- **Budget**: ~$1-3 (OpenAI TTS + free tools)
- **Quality**: ~$15-30 (ElevenLabs + Mapbox)
- **Per-language dub**: +$10-24 (ElevenLabs) or +$1 (DIY)
