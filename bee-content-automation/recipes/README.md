# Video Production Recipes

Tested, working recipes for producing faceless YouTube videos programmatically. All tools are free/open source.

## Recipe Index

| Recipe | Lines | What It Covers |
|--------|-------|---------------|
| [video-production-recipes.md](video-production-recipes.md) | 443 | FFmpeg + Pillow core techniques (16 recipes) |
| [tts-narration-guide.md](tts-narration-guide.md) | — | TTS engines comparison + narration generation script |
| [subtitle-generation-guide.md](subtitle-generation-guide.md) | — | Word-by-word animated captions pipeline |
| [map-visuals-guide.md](map-visuals-guide.md) | 805 | Map zoom animations + satellite imagery |

---

## Genre Compatibility

### Universal Recipes (work for ANY faceless YouTube genre)

These recipes apply to true crime, finance, education, history, horror, documentary, explainer, motivation, travel, and any other narrated faceless content.

| Recipe | Technique | Notes |
|--------|-----------|-------|
| **TTS narration** | Kokoro, Edge TTS, OpenAI, ElevenLabs, Piper | Just change the voice/tone per genre |
| **Subtitles / captions** | faster-whisper → stable-ts → ASS | Every YouTube video needs captions |
| **Ken Burns zoom on photos** | FFmpeg zoompan | Any video using static images |
| **Lower thirds** | Pillow PNG → FFmpeg overlay | Any video introducing people |
| **Quote cards** | Pillow text on dark background | Education, motivation, documentary, true crime |
| **Timeline markers** | Pillow date/event cards | History, true crime, documentary, biography |
| **Picture-in-picture** | FFmpeg overlay filter | Any multi-source video |
| **Fade in/out** | FFmpeg fade + afade | Every video |
| **Slow zoom on video** | FFmpeg scale + zoompan | Adds cinematic feel to any footage |
| **Audio mixing** | FFmpeg amix (narration + background music) | Every narrated video |
| **Audio normalization** | FFmpeg loudnorm (-14 LUFS) | Every YouTube upload |
| **Video assembly** | FFmpeg concat demuxer | Every production |
| **Map zoom-ins** | py-staticmaps + FFmpeg zoompan | Travel, history, geopolitics, true crime, news |
| **Financial amount cards** | Pillow text overlays | Finance, business, true crime, documentary |
| **Clip trimming & normalization** | FFmpeg trim + scale + fps | Every production |

### Genre-Specific Recipes (true crime only)

These recipes are specifically designed for the Dr Insanity-style true crime format and would need adaptation for other genres.

| Recipe | Technique | Why It's Genre-Specific |
|--------|-----------|------------------------|
| **911 call waveform** | FFmpeg showwaves (green on black) | Only true crime has emergency call audio |
| **Audio spectrum (fire)** | FFmpeg showspectrum | Designed for interrogation/call audio visualization |
| **Dark color grading** | FFmpeg eq (desaturated, cold blue) | Matches somber crime tone — too dark for education/travel |
| **Red/dark color palette** | `#DC3232` accent, `#0A0A0F` background | Dr Insanity-specific aesthetic |
| **Bodycam overlay style** | Specific framing/grading for police footage | Only relevant for police bodycam content |

### Adapting for Other Genres

To use this toolkit for a different genre, swap these components:

| Component | True Crime | Finance | Education | History | Horror |
|-----------|-----------|---------|-----------|---------|--------|
| **Color palette** | Dark/red/cold blue | Blue/green/white | Bright/clean/blue | Warm sepia/gold | Dark/purple/green |
| **Background** | `#0A0A0F` near black | `#FFFFFF` white | `#F5F5F5` light gray | `#1A1510` warm dark | `#0A0A0F` black |
| **Accent color** | `#DC3232` red | `#00AA55` green | `#2196F3` blue | `#D4A843` gold | `#6B2FA0` purple |
| **TTS voice** | Deep, calm male | Authoritative, clear | Friendly, engaging | Measured, scholarly | Low, ominous |
| **Kokoro voice** | `am_adam` | `am_adam` | `af_nova` | `am_adam` | `am_adam` (slower) |
| **Music mood** | Dark ambient | Corporate/upbeat | Light electronic | Orchestral | Eerie ambient |
| **Color grade** | Desaturated cold | Clean natural | Bright saturated | Warm vintage | Desaturated dark |
| **Waveform color** | Green `#00FF88` | N/A | N/A | N/A | Green or red |
| **Card style** | Dark bg, red text | White bg, dark text | Colored bg, white text | Dark bg, gold text | Dark bg, purple text |

### Example: Adapting Lower Third for Finance

```python
# True crime (original)
d.rectangle([(0, 920), (700, 1080)], fill=(0, 0, 0, 180))      # dark bar
d.rectangle([(0, 920), (700, 924)], fill=(200, 30, 30, 255))    # red accent

# Finance (adapted)
d.rectangle([(0, 920), (700, 1080)], fill=(255, 255, 255, 220)) # white bar
d.rectangle([(0, 920), (700, 924)], fill=(0, 170, 85, 255))     # green accent
```

### Example: Adapting Color Grade for Education

```bash
# True crime: dark, desaturated, cold
-vf "eq=brightness=-0.08:saturation=0.6:contrast=1.2,colorbalance=bs=0.1:bm=0.05"

# Education: bright, clean, warm
-vf "eq=brightness=0.05:saturation=1.1:contrast=1.05,colorbalance=rs=0.03:gm=0.02"
```

---

## Production Cost Summary

| Tool | Cost | Used For |
|------|------|----------|
| FFmpeg | Free | Everything (compositing, transitions, audio, assembly) |
| Pillow (Python) | Free | Text overlays, graphics, lower thirds |
| Kokoro TTS | Free | Narrator voiceover |
| faster-whisper | Free | Transcription for subtitles |
| stable-ts | Free | Word-level timestamp refinement |
| py-staticmaps | Free | Map satellite imagery (no API key) |
| MusicGen (optional) | Free | Background music generation |
| **Total** | **$0** | Full video production |

Optional paid upgrades:
- ElevenLabs ($5-22/mo) — better voice quality
- Mapbox API (free 100K/mo) — styled maps with markers
- Storyblocks ($17/mo) — stock footage library
