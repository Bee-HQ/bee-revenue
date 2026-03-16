# Subtitle Generation Guide — Word-by-Word Animated Captions

Practical guide for generating styled, word-by-word animated captions for true crime YouTube videos. Covers transcription, timestamp refinement, ASS subtitle styling, and burn-in.

**Target style:** White text, dark outline, bottom-center, each word highlights as spoken (YouTube Shorts / Dr Insanity style).

**Important:** Our FFmpeg build lacks `drawtext` (no freetype). Check whether `subtitles` / `ass` filters are available:

```bash
ffmpeg -filters 2>&1 | grep -i "subtitles\|libass\|ass"
```

If the output shows `subtitles` and/or `ass` filters, you can burn ASS subtitles directly. If not, use the Pillow-based alternative documented in Section 6.

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [faster-whisper — Transcription with Word Timestamps](#2-faster-whisper--transcription-with-word-timestamps)
3. [stable-ts — Refined Timestamps and ASS Export](#3-stable-ts--refined-timestamps-and-ass-export)
4. [ASS/SSA Subtitle Format](#4-asssa-subtitle-format)
5. [Burning Subtitles into Video with FFmpeg](#5-burning-subtitles-into-video-with-ffmpeg)
6. [Pillow-Based Alternative (No libass)](#6-pillow-based-alternative-no-libass)
7. [Complete Pipeline Script](#7-complete-pipeline-script)
8. [Style Reference](#8-style-reference)

---

## 1. Pipeline Overview

```
Audio file (.wav/.mp3)
    │
    ▼
faster-whisper (word-level timestamps)
    │
    ▼
stable-ts (refine timestamps, regroup words)
    │
    ▼
ASS subtitle file (styled, word-by-word karaoke)
    │
    ▼
FFmpeg burn-in (ass= filter)  ─OR─  Pillow PNG frames + FFmpeg overlay
    │
    ▼
Final video with hardcoded animated captions
```

---

## 2. faster-whisper — Transcription with Word Timestamps

### Installation

```bash
pip install faster-whisper
```

Requires: Python 3.8+. Uses CTranslate2 backend for optimized inference. GPU optional (CUDA 12 for GPU acceleration).

### Model Sizes — Speed vs Accuracy

| Model | Parameters | VRAM | English WER | Relative Speed | Recommended For |
|-------|-----------|------|-------------|----------------|-----------------|
| `tiny` | 39M | ~1GB | ~7.5% | 32x | Quick previews, testing pipeline |
| `base` | 74M | ~1GB | ~5.5% | 16x | Drafts, rapid iteration |
| `small` | 244M | ~2GB | ~4.2% | 6x | Good balance for clear narration |
| `medium` | 769M | ~5GB | ~3.5% | 2x | Production quality for single speaker |
| `large-v3` | 1.5B | ~10GB | ~2.7% | 1x | Best accuracy, final output |

For true crime narration (clear speech, single speaker, studio-quality TTS audio), `medium` is usually sufficient. Use `large-v3` for final renders or when transcribing real-world audio (911 calls, interviews).

### Basic Transcription with Word Timestamps

```python
from faster_whisper import WhisperModel

# CPU usage (no GPU required)
model = WhisperModel("medium", device="cpu", compute_type="int8")

# GPU usage (if CUDA available)
# model = WhisperModel("large-v3", device="cuda", compute_type="int8")

segments, info = model.transcribe(
    "narration.wav",
    word_timestamps=True,
    language="en",
    vad_filter=True,          # Filter out silence using Silero VAD
    vad_parameters=dict(
        min_silence_duration_ms=300,  # Minimum silence to split on
    ),
)

print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")

for segment in segments:
    print(f"\n[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    if segment.words:
        for word in segment.words:
            print(f"  '{word.word.strip()}' [{word.start:.2f}s - {word.end:.2f}s] (p={word.probability:.2f})")
```

### Output Format

Each `segment` contains:
- `segment.start` / `segment.end` — float, seconds
- `segment.text` — full segment text
- `segment.words` — list of `Word` objects:
  - `word.word` — the word string (may have leading space)
  - `word.start` / `word.end` — float, seconds
  - `word.probability` — confidence (0.0–1.0)

### Performance

On CPU (Apple Silicon M-series), `medium` model transcribes at roughly 6-10x realtime (a 10-minute audio file in ~1-2 minutes). On NVIDIA GPU with INT8 quantization, `large-v3` can do the same in ~40 seconds.

Batched mode can achieve 12x speedup over original Whisper:

```python
from faster_whisper import BatchedInferencePipeline

model = WhisperModel("large-v3", device="cuda", compute_type="int8")
batched = BatchedInferencePipeline(model=model)
segments, info = batched.transcribe("narration.wav", word_timestamps=True, batch_size=16)
```

---

## 3. stable-ts — Refined Timestamps and ASS Export

### Installation

```bash
pip install stable-ts
```

### What It Does

stable-ts improves Whisper's timestamps using Dynamic Time Warping (DTW) on cross-attention weights. This fixes the common problem where Whisper word timestamps are slightly off — words starting too early or too late. For word-by-word captions, accurate timestamps are critical.

Key improvements over raw Whisper:
- More accurate word-level start/end times
- Better handling of silence gaps between words
- Regrouping words into natural phrases (by punctuation, pause length)
- Direct ASS/SRT/VTT export with styling

### Using stable-ts with faster-whisper

```python
import stable_whisper

# Load faster-whisper model through stable-ts
model = stable_whisper.load_faster_whisper("medium")

# Transcribe with refined timestamps
result = model.transcribe_stable("narration.wav", word_timestamps=True)

# Inspect words
for segment in result.segments:
    for word in segment.words:
        print(f"  '{word.word}' [{word.start:.3f}s - {word.end:.3f}s]")
```

### Direct ASS Export (with word-level highlights)

```python
import stable_whisper

model = stable_whisper.load_faster_whisper("medium")
result = model.transcribe_stable("narration.wav", word_timestamps=True)

# Regroup into natural segments (by sentence, max 7 words per line)
result = result.split_by_punctuation(['.', '?', '!', ','])

# Export ASS with word-level karaoke highlighting
result.to_ass(
    "captions.ass",
    word_level=True,               # Enable word-by-word highlighting
    segment_level=False,           # Don't show full segment, show word-by-word
    font="Montserrat",
    font_size=52,
    highlight_color="00FFFF",      # Yellow highlight for active word (BGR)
    karaoke=True,                  # Use \kf tags for smooth fill
)
```

### Custom Regrouping

stable-ts lets you control how words are grouped into subtitle lines:

```python
# Regroup by punctuation + max words per line
result = result.split_by_punctuation(['.', '?', '!'])
result = result.split_by_length(max_words=8)

# Or regroup by gap duration (split when gap > 0.5s)
result = result.split_by_gap(0.5)

# Clamp segment durations (min 1s, max 5s)
result = result.clamp_max(5.0)
```

### Standalone Refinement (if you already have faster-whisper output)

If you already have word timestamps from faster-whisper and just want to refine them:

```python
import stable_whisper

# Refine existing timestamps from audio
result = stable_whisper.non_whisper.transcribe_any(
    inference_func,    # Your existing transcription function
    audio="narration.wav",
    inference_kwargs={},
)
```

---

## 4. ASS/SSA Subtitle Format

### Format Overview

ASS (Advanced SubStation Alpha) is the subtitle format that supports rich styling, positioning, and animation — exactly what's needed for word-by-word animated captions.

### Template ASS Header (True Crime Style)

This header produces white text with a dark outline, bottom-center, matching the style used by channels like Dr Insanity:

```ass
[Script Info]
Title: True Crime Captions
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat,52,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,20,20,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```

### Style Field Breakdown

```
PrimaryColour:   &H00FFFFFF   = White (the default text color)
SecondaryColour: &H0000FFFF   = Yellow (the highlight/karaoke color — active word)
OutlineColour:   &H00000000   = Black outline
BackColour:      &H80000000   = Semi-transparent black shadow
Bold:            1            = Bold text
BorderStyle:     1            = Outline + shadow
Outline:         3            = 3px outline thickness
Shadow:          1            = 1px shadow offset
Alignment:       2            = Bottom center
MarginV:         80           = 80px from bottom edge
```

**Color format:** `&HAABBGGRR` — Alpha, Blue, Green, Red. `&H00FFFFFF` = fully opaque white.

### Key ASS Tags for Word-by-Word Animation

#### Karaoke Tags (the core of word-by-word highlighting)

| Tag | Description | Example |
|-----|-------------|---------|
| `\k<d>` | Hard cut: word highlights instantly after `d` centiseconds | `{\k50}word` (0.5s delay then highlight) |
| `\kf<d>` | Smooth fill: word fills left-to-right over `d` centiseconds | `{\kf50}word` (fills over 0.5s) |
| `\ko<d>` | Outline fill: outline changes color over `d` centiseconds | `{\ko50}word` |
| `\K<d>` | Same as `\kf` | `{\K50}word` |

For YouTube-style word-by-word captions, `\kf` (smooth fill) looks best.

#### How Karaoke Timing Works

The `\k` / `\kf` duration is the time **before** the word highlights (the "wait" time), in centiseconds (1/100th of a second).

Example line: "The body was found at midnight"
```
{\kf0}The {\kf30}body {\kf25}was {\kf20}found {\kf25}at {\kf35}midnight
```

Breakdown:
- `{\kf0}The` — "The" highlights immediately when the line appears
- `{\kf30}body` — "body" starts highlighting 0.30s after "The" finished
- `{\kf25}was` — "was" starts 0.25s after "body"
- etc.

The word stays unhighlighted (PrimaryColour) until its turn, then transitions to SecondaryColour.

#### Other Useful ASS Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `\pos(x,y)` | Exact position | `{\pos(960,900)}Text` |
| `\an2` | Bottom-center alignment | `{\an2}Text` |
| `\an8` | Top-center alignment | `{\an8}Text` |
| `\c&HBBGGRR&` | Change primary color | `{\c&H0000FF&}Red text` |
| `\3c&HBBGGRR&` | Change outline color | `{\3c&H000088&}` |
| `\fs48` | Font size | `{\fs48}Bigger` |
| `\b1` | Bold on | `{\b1}Bold text` |
| `\fad(in,out)` | Fade (milliseconds) | `{\fad(200,200)}Fades in and out` |
| `\t(t1,t2,\tag)` | Animate a tag over time | `{\t(0,500,\fs72)}Grows` |

#### Example: Word-by-Word Dialogue Line

```ass
Dialogue: 0,0:00:05.00,0:00:08.20,Default,,0,0,0,,{\kf0}The {\kf32}body {\kf28}was {\kf22}found {\kf30}at {\kf40}the {\kf25}bottom {\kf35}of {\kf20}the {\kf28}stairs
```

### Alternative Style: Active Word in Different Color

Instead of karaoke fill, show each word group with the current word in a different color. This requires generating one dialogue line per word:

```ass
Dialogue: 0,0:00:05.00,0:00:05.32,Default,,0,0,0,,{\c&H00FFFF&}The{\c&HFFFFFF&} body was found
Dialogue: 0,0:00:05.32,0:00:05.60,Default,,0,0,0,,The {\c&H00FFFF&}body{\c&HFFFFFF&} was found
Dialogue: 0,0:00:05.60,0:00:05.82,Default,,0,0,0,,The body {\c&H00FFFF&}was{\c&HFFFFFF&} found
Dialogue: 0,0:00:05.82,0:00:06.12,Default,,0,0,0,,The body was {\c&H00FFFF&}found{\c&HFFFFFF&}
```

This gives you the "one word pops" effect popular on YouTube Shorts. More subtitle events but more visual control.

---

## 5. Burning Subtitles into Video with FFmpeg

### Method A: `ass` filter (requires libass)

```bash
# Direct ASS burn-in (preserves all styling, karaoke, positioning)
ffmpeg -i video.mp4 -vf "ass=captions.ass" -c:v libx264 -preset fast -crf 20 -c:a copy output.mp4

# With custom fonts directory
ffmpeg -i video.mp4 -vf "ass=captions.ass:fontsdir=/path/to/fonts/" -c:v libx264 -preset fast -crf 20 -c:a copy output.mp4
```

### Method B: `subtitles` filter (also requires libass, more flexible)

```bash
# SRT with forced styling
ffmpeg -i video.mp4 \
  -vf "subtitles=captions.srt:force_style='FontName=Montserrat,FontSize=28,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=50'" \
  -c:v libx264 -preset fast -crf 20 -c:a copy output.mp4

# ASS file (styling from file takes priority over force_style)
ffmpeg -i video.mp4 \
  -vf "subtitles=captions.ass" \
  -c:v libx264 -preset fast -crf 20 -c:a copy output.mp4
```

### Check Filter Availability

```bash
# Check for ass/subtitles filter
ffmpeg -filters 2>&1 | grep -i "subtitles\|ass"

# Expected output (if available):
#  T.. ass              V->V       Render ASS subtitles onto input video using the libass library.
#  T.. subtitles        V->V       Render text subtitles onto input video using the libass library.
```

If neither filter is available, use the Pillow-based approach in Section 6.

---

## 6. Pillow-Based Alternative (No libass)

When FFmpeg lacks `subtitles`/`ass` filters (our current build lacks `drawtext`/freetype — `subtitles` may also be missing), render captions as transparent PNG frames with Pillow and composite them.

### Approach: Generate PNG Sequence + FFmpeg Overlay

```python
"""
Render word-by-word captions as transparent PNG frames.
Each frame shows the current subtitle line with the active word highlighted.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import json

# Configuration
WIDTH, HEIGHT = 1920, 1080
FPS = 30
FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"  # macOS; adjust for your system
FONT_SIZE = 52
TEXT_COLOR = (255, 255, 255, 255)       # White
HIGHLIGHT_COLOR = (255, 255, 0, 255)    # Yellow (active word)
OUTLINE_COLOR = (0, 0, 0, 255)         # Black outline
OUTLINE_WIDTH = 3
MARGIN_BOTTOM = 80


def draw_text_with_outline(draw, pos, text, font, fill, outline_fill, outline_width):
    """Draw text with outline (stroke)."""
    x, y = pos
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
    # Draw text
    draw.text((x, y), text, font=font, fill=fill)


def render_caption_frame(words, active_index, font):
    """
    Render a single caption frame.
    words: list of word strings for this line
    active_index: which word is currently highlighted (-1 for none)
    Returns: PIL Image (RGBA, transparent background)
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Measure total line width
    full_text = " ".join(words)
    bbox = font.getbbox(full_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position: bottom center
    x_start = (WIDTH - text_width) // 2
    y = HEIGHT - MARGIN_BOTTOM - text_height

    # Draw word by word
    x = x_start
    for i, word in enumerate(words):
        color = HIGHLIGHT_COLOR if i == active_index else TEXT_COLOR
        draw_text_with_outline(draw, (x, y), word, font, color, OUTLINE_COLOR, OUTLINE_WIDTH)
        word_bbox = font.getbbox(word + " ")
        x += word_bbox[2] - word_bbox[0]

    return img


def generate_caption_frames(word_timestamps, output_dir, fps=30):
    """
    Generate PNG frames for the entire caption track.

    word_timestamps: list of dicts with keys:
        - "word": str
        - "start": float (seconds)
        - "end": float (seconds)
        - "line_words": list of words in the same display line
        - "line_index": index of this word within line_words

    output_dir: directory to write PNG frames
    """
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Determine total duration
    if not word_timestamps:
        return
    total_duration = max(w["end"] for w in word_timestamps)
    total_frames = int(total_duration * fps) + 1

    # Build frame-to-caption lookup
    # Group words into display lines (e.g., 6-8 words per line)
    lines = group_words_into_lines(word_timestamps, max_words=7)

    for frame_num in range(total_frames):
        t = frame_num / fps

        # Find active line and active word
        active_line = None
        active_word_idx = -1
        for line in lines:
            line_start = line[0]["start"]
            line_end = line[-1]["end"]
            if line_start <= t <= line_end + 0.1:  # small buffer
                active_line = line
                # Find which word is active
                for idx, w in enumerate(line):
                    if w["start"] <= t < w["end"] + 0.05:
                        active_word_idx = idx
                        break
                    elif t < w["start"]:
                        # Between words, keep previous highlighted
                        active_word_idx = max(0, idx - 1)
                        break
                else:
                    active_word_idx = len(line) - 1
                break

        if active_line:
            words = [w["word"] for w in active_line]
            img = render_caption_frame(words, active_word_idx, font)
        else:
            img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

        img.save(os.path.join(output_dir, f"caption_{frame_num:06d}.png"))

    print(f"Generated {total_frames} caption frames in {output_dir}")


def group_words_into_lines(word_timestamps, max_words=7):
    """Group word timestamps into display lines of max_words each."""
    lines = []
    current_line = []
    for w in word_timestamps:
        current_line.append(w)
        # Split on sentence boundaries or max words
        if len(current_line) >= max_words or w["word"].rstrip().endswith(('.', '?', '!', ',')):
            lines.append(current_line)
            current_line = []
    if current_line:
        lines.append(current_line)
    return lines
```

### Composite PNG Frames onto Video with FFmpeg

```bash
# Overlay the caption PNG sequence onto the video
ffmpeg -i video.mp4 \
  -framerate 30 -i "caption_frames/caption_%06d.png" \
  -filter_complex "[0:v][1:v]overlay=0:0:shortest=1" \
  -c:v libx264 -preset fast -crf 20 -c:a copy \
  output_with_captions.mp4
```

### Performance Note

Generating thousands of PNG frames is slow. For a 10-minute video at 30fps, that is 18,000 frames. Optimizations:

1. **Only generate frames where captions change** (on word boundaries), then use FFmpeg to hold each frame until the next change.
2. **Use a single PNG per word-change event** and overlay with timed `overlay=enable='between(t,start,end)'`:

```bash
# More efficient: one PNG per word event, timed overlay
ffmpeg -i video.mp4 \
  -i "caption_word_001.png" -i "caption_word_002.png" \
  -filter_complex "\
    [1:v]setpts=PTS-STARTPTS[c1]; \
    [2:v]setpts=PTS-STARTPTS[c2]; \
    [0:v][c1]overlay=0:0:enable='between(t,5.00,5.32)'[v1]; \
    [v1][c2]overlay=0:0:enable='between(t,5.32,5.60)'[v2]" \
  -map "[v2]" -map 0:a -c:v libx264 -preset fast -crf 20 -c:a copy \
  output.mp4
```

For many word events, generate the filter_complex string programmatically (see Section 7).

---

## 7. Complete Pipeline Script

### Pipeline A: faster-whisper + ASS file (for FFmpeg with libass)

```python
#!/usr/bin/env python3
"""
subtitle_pipeline.py

Input:  audio file (wav, mp3, etc.)
Output: styled ASS subtitle file with word-by-word karaoke highlighting

Usage:
    python subtitle_pipeline.py narration.wav --output captions.ass --model medium
"""
import argparse
import sys


def transcribe_with_word_timestamps(audio_path, model_size="medium", device="cpu"):
    """Transcribe audio and return word-level timestamps."""
    from faster_whisper import WhisperModel

    print(f"Loading faster-whisper model '{model_size}' on {device}...")
    model = WhisperModel(model_size, device=device, compute_type="int8")

    print(f"Transcribing '{audio_path}'...")
    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language="en",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=300),
    )

    words = []
    for segment in segments:
        if segment.words:
            for w in segment.words:
                words.append({
                    "word": w.word.strip(),
                    "start": w.start,
                    "end": w.end,
                    "probability": w.probability,
                })

    print(f"Transcribed {len(words)} words. Duration: {info.duration:.1f}s")
    return words


def refine_with_stable_ts(audio_path, model_size="medium"):
    """Use stable-ts for better timestamps. Returns word list."""
    import stable_whisper

    print(f"Loading stable-ts with faster-whisper model '{model_size}'...")
    model = stable_whisper.load_faster_whisper(model_size)

    print(f"Transcribing with stable-ts refinement...")
    result = model.transcribe_stable(audio_path, word_timestamps=True)

    words = []
    for segment in result.segments:
        for w in segment.words:
            words.append({
                "word": w.word.strip(),
                "start": w.start,
                "end": w.end,
            })

    print(f"Refined {len(words)} words.")
    return words


def group_into_lines(words, max_words=7, max_duration=4.0):
    """Group words into display lines."""
    lines = []
    current = []

    for w in words:
        current.append(w)

        # Check split conditions
        at_max_words = len(current) >= max_words
        at_punctuation = w["word"].rstrip().endswith(('.', '?', '!'))
        line_too_long = (len(current) > 1 and
                         current[-1]["end"] - current[0]["start"] > max_duration)

        if at_max_words or at_punctuation or line_too_long:
            lines.append(current)
            current = []

    if current:
        lines.append(current)

    return lines


def format_ass_time(seconds):
    """Convert seconds to ASS time format: H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def generate_ass_karaoke(words, output_path, style="karaoke"):
    """
    Generate ASS file with word-by-word highlighting.

    style options:
        "karaoke"  — uses \\kf tags, words fill as spoken
        "pop"      — one line per word-change, active word in different color
    """
    lines = group_into_lines(words)

    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write("[Script Info]\n")
        f.write("Title: True Crime Captions\n")
        f.write("ScriptType: v4.00+\n")
        f.write("PlayResX: 1920\n")
        f.write("PlayResY: 1080\n")
        f.write("WrapStyle: 0\n")
        f.write("ScaledBorderAndShadow: yes\n")
        f.write("\n")

        # Style
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                "Alignment, MarginL, MarginR, MarginV, Encoding\n")

        if style == "karaoke":
            # PrimaryColour = white (unhighlighted), SecondaryColour = yellow (highlighted)
            f.write("Style: Default,Montserrat,52,&H00FFFFFF,&H0000FFFF,&H00000000,"
                    "&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,20,20,80,1\n")
        else:
            # For "pop" style, primary is white
            f.write("Style: Default,Montserrat,52,&H00FFFFFF,&H0000FFFF,&H00000000,"
                    "&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,20,20,80,1\n")
            f.write("Style: Highlight,Montserrat,56,&H0000FFFF,&H0000FFFF,&H00000000,"
                    "&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,20,20,80,1\n")

        f.write("\n")

        # Events
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

        if style == "karaoke":
            for line in lines:
                start = line[0]["start"]
                end = line[-1]["end"]

                # Build karaoke tags
                parts = []
                prev_end = start
                for w in line:
                    # Gap before this word (in centiseconds)
                    gap_cs = max(0, int((w["start"] - prev_end) * 100))
                    # Duration of this word (in centiseconds)
                    dur_cs = max(1, int((w["end"] - w["start"]) * 100))

                    if gap_cs > 0:
                        parts.append(f"{{\\k{gap_cs}}}")
                    parts.append(f"{{\\kf{dur_cs}}}{w['word']}")
                    prev_end = w["end"]

                text = " ".join(parts)
                # Clean up spacing (\\kf tags already separate words)
                text = text.replace("} {", "}{")

                f.write(f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},"
                        f"Default,,0,0,0,,{text}\n")

        elif style == "pop":
            # One dialogue event per word, showing the full line with active word colored
            for line in lines:
                line_words = [w["word"] for w in line]
                for idx, w in enumerate(line):
                    start = w["start"]
                    end = w["end"]

                    # Build text with active word highlighted
                    parts = []
                    for j, lw in enumerate(line_words):
                        if j == idx:
                            parts.append(f"{{\\c&H0000FFFF&}}{lw}{{\\c&HFFFFFF&}}")
                        else:
                            parts.append(lw)

                    text = " ".join(parts)
                    f.write(f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},"
                            f"Default,,0,0,0,,{text}\n")

    print(f"Wrote ASS file: {output_path} ({len(lines)} lines, style={style})")


def main():
    parser = argparse.ArgumentParser(description="Generate word-by-word ASS subtitles from audio")
    parser.add_argument("audio", help="Input audio file")
    parser.add_argument("--output", "-o", default="captions.ass", help="Output ASS file")
    parser.add_argument("--model", "-m", default="medium", help="Whisper model size")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Device")
    parser.add_argument("--style", default="karaoke", choices=["karaoke", "pop"],
                        help="Caption style: karaoke (fill) or pop (color switch)")
    parser.add_argument("--use-stable-ts", action="store_true",
                        help="Use stable-ts for refined timestamps")

    args = parser.parse_args()

    # Transcribe
    if args.use_stable_ts:
        words = refine_with_stable_ts(args.audio, args.model)
    else:
        words = transcribe_with_word_timestamps(args.audio, args.model, args.device)

    if not words:
        print("No words transcribed. Check audio file.", file=sys.stderr)
        sys.exit(1)

    # Generate ASS
    generate_ass_karaoke(words, args.output, style=args.style)

    print(f"\nDone. To burn into video:")
    print(f"  ffmpeg -i video.mp4 -vf \"ass={args.output}\" -c:v libx264 -crf 20 -c:a copy output.mp4")


if __name__ == "__main__":
    main()
```

### Usage Examples

```bash
# Basic: transcribe and generate karaoke-style ASS
python subtitle_pipeline.py narration.wav -o captions.ass

# With stable-ts refinement (better timestamps)
python subtitle_pipeline.py narration.wav -o captions.ass --use-stable-ts

# Pop style (active word changes color)
python subtitle_pipeline.py narration.wav -o captions.ass --style pop

# Use large model on GPU for best quality
python subtitle_pipeline.py narration.wav -o captions.ass --model large-v3 --device cuda --use-stable-ts

# Then burn into video
ffmpeg -i video.mp4 -vf "ass=captions.ass" -c:v libx264 -preset fast -crf 20 -c:a copy final.mp4
```

### Pipeline B: Pillow Frames (if no libass in FFmpeg)

```python
#!/usr/bin/env python3
"""
subtitle_pillow_pipeline.py

For FFmpeg builds without libass. Generates caption PNGs and a FFmpeg
filter_complex command to overlay them.

Usage:
    python subtitle_pillow_pipeline.py narration.wav video.mp4 --output final.mp4
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

# --- Import transcription functions from pipeline above ---
# from subtitle_pipeline import transcribe_with_word_timestamps, group_into_lines

WIDTH, HEIGHT = 1920, 1080
FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
FONT_SIZE = 52
TEXT_COLOR = (255, 255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0, 255)
OUTLINE_COLOR = (0, 0, 0, 255)
OUTLINE_W = 3
MARGIN_BOTTOM = 80


def render_line_png(words, active_idx, font, output_path):
    """Render a single caption state as transparent PNG."""
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    full = " ".join(words)
    bbox = font.getbbox(full)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = HEIGHT - MARGIN_BOTTOM - th

    for i, word in enumerate(words):
        color = HIGHLIGHT_COLOR if i == active_idx else TEXT_COLOR
        # Outline
        for dx in range(-OUTLINE_W, OUTLINE_W + 1):
            for dy in range(-OUTLINE_W, OUTLINE_W + 1):
                if dx or dy:
                    draw.text((x + dx, y + dy), word, font=font, fill=OUTLINE_COLOR)
        draw.text((x, y), word, font=font, fill=color)
        wb = font.getbbox(word + " ")
        x += wb[2] - wb[0]

    img.save(output_path)


def build_pillow_captions(words, video_path, output_path):
    """Full pipeline: transcribe -> render PNGs -> FFmpeg composite."""
    from subtitle_pipeline import group_into_lines

    lines = group_into_lines(words)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    frames_dir = "caption_pngs"
    os.makedirs(frames_dir, exist_ok=True)

    # Generate one PNG per word event
    events = []  # (png_path, start_time, end_time)
    png_idx = 0

    for line in lines:
        line_words = [w["word"] for w in line]
        for idx, w in enumerate(line):
            png_path = os.path.join(frames_dir, f"cap_{png_idx:04d}.png")
            render_line_png(line_words, idx, font, png_path)
            events.append((png_path, w["start"], w["end"]))
            png_idx += 1

    print(f"Generated {len(events)} caption PNGs")

    # Build FFmpeg command with overlay chain
    # For large numbers of events, process in batches to avoid command-line limits
    inputs = ["-i", video_path]
    for png_path, _, _ in events:
        inputs.extend(["-i", png_path])

    filter_parts = []
    prev = "[0:v]"
    for i, (_, start, end) in enumerate(events):
        inp = f"[{i + 1}:v]"
        out = f"[v{i}]"
        filter_parts.append(
            f"{prev}{inp}overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{out}"
        )
        prev = out

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", prev.strip("[]"),
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        output_path,
    ]

    print(f"Running FFmpeg with {len(events)} overlay events...")
    subprocess.run(cmd, check=True)
    print(f"Output: {output_path}")
```

**Note:** For very long videos (1000+ word events), FFmpeg filter_complex chains become impractical. In that case, render the entire caption track as a video stream (PNG sequence at 30fps), then do a single overlay:

```bash
# Step 1: Render caption PNGs as a video
ffmpeg -framerate 30 -i "caption_frames/caption_%06d.png" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 \
  captions_overlay.webm

# Step 2: Overlay onto main video
ffmpeg -i video.mp4 -i captions_overlay.webm \
  -filter_complex "[0:v][1:v]overlay=0:0:shortest=1" \
  -c:v libx264 -preset fast -crf 20 -c:a copy \
  final.mp4
```

---

## 8. Style Reference

### True Crime Caption Style (Dr Insanity / MrBallen / JCS)

| Property | Value |
|----------|-------|
| Font | Montserrat Bold (or Helvetica Bold, Inter Bold) |
| Size | 48-56px at 1080p |
| Primary color | White `&H00FFFFFF` |
| Highlight color | Yellow `&H0000FFFF` or cyan `&H00FFFF00` |
| Outline | Black, 2-3px |
| Shadow | 1px, dark |
| Position | Bottom center, ~80px from bottom |
| Alignment | Center (ASS alignment 2) |
| Words per line | 5-8 words |
| Line duration | 2-5 seconds |
| Animation | Word-by-word fill (karaoke `\kf`) or color pop |

### Color Presets (ASS BGR format)

| Color | ASS Code | Use Case |
|-------|----------|----------|
| White | `&H00FFFFFF` | Default text |
| Yellow | `&H0000FFFF` | Active word highlight |
| Cyan | `&H00FFFF00` | Alternative highlight |
| Red | `&H000000FF` | Emphasis / danger |
| Green | `&H0000FF00` | Positive context |
| Black | `&H00000000` | Outline |
| Semi-transparent black | `&H80000000` | Shadow / background |

### Font Recommendations

1. **Montserrat Bold** — the most common YouTube caption font. Clean, wide, high legibility.
2. **Inter Bold** — similar to Montserrat, slightly more modern.
3. **Helvetica Bold** — available on macOS by default, good fallback.
4. **Roboto Bold** — Google's font, good for Android-centric audiences.

Install Montserrat: download from [Google Fonts](https://fonts.google.com/specimen/Montserrat), place in `/usr/local/share/fonts/` (Linux) or `~/Library/Fonts/` (macOS).

---

## Quick Reference: Dependencies

```bash
# Core transcription
pip install faster-whisper

# Refined timestamps + ASS export
pip install stable-ts

# Subtitle file manipulation (optional, for format conversion)
pip install pysubs2

# Image rendering (for Pillow-based alternative)
pip install Pillow

# All at once
pip install faster-whisper stable-ts pysubs2 Pillow
```

## Quick Reference: One-Liner Pipeline

```bash
# If you have libass in FFmpeg:
python subtitle_pipeline.py narration.wav -o captions.ass --use-stable-ts && \
ffmpeg -i video.mp4 -vf "ass=captions.ass" -c:v libx264 -crf 20 -c:a copy final.mp4
```
