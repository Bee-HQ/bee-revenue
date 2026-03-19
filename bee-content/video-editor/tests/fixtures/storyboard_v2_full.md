```json bee-video:project
{
  "title": "The Murdaugh Murders",
  "version": 1,
  "voice_lock": {"engine": "elevenlabs", "voice": "Daniel"},
  "color_preset": "dark_crime",
  "default_transition": {"type": "dissolve", "duration": 1.0},
  "output": {"resolution": "1920x1080", "fps": 30, "codec": "h264", "crf": 18}
}
```

## Act 1: The Night Of (0:00 - 2:30)

### 0:00 - 0:45 | Surveillance Footage

```json bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": "footage/moselle-cam.mp4", "in": "00:02:14.500", "out": "00:02:59.500", "color": "surveillance", "ken_burns": "zoom_in"}],
  "audio": [
    {"type": "REAL_AUDIO", "src": "footage/moselle-cam.mp4", "volume": 0.6},
    {"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.15, "fade_in": 2.0, "fade_out": 1.5}
  ],
  "overlay": [{"type": "LOWER_THIRD", "text": "Moselle Property", "subtext": "Colleton County, SC", "duration": 4.0, "position": "bottom-left"}],
  "captions": {"style": "karaoke", "font_size": 42},
  "transition_in": {"type": "fade_from_black", "duration": 1.5}
}
```

> NAR: On the night of June 7th, 2021, a 911 call shattered the silence
> of the South Carolina Lowcountry.

### 0:45 - 1:30 | Aerial Establishing

```json bee-video:segment
{
  "visual": [{"type": "STOCK", "src": null, "query": "aerial farm dusk"}],
  "overlay": [{"type": "TIMELINE_MARKER", "date": "June 7, 2021", "description": "10:07 PM — 911 call placed"}],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: Alex Murdaugh told dispatchers he had found the bodies of his wife
> Maggie and son Paul at the family's hunting estate.

### 1:30 - 2:30 | Moselle Property Map

```json bee-video:segment
{
  "visual": [{"type": "MAP", "style": "tactical", "center": [32.5916, -80.6754], "zoom": 13, "markers": [{"label": "Moselle Estate", "lat": 32.5916, "lng": -80.6754}, {"label": "Dog Kennels", "lat": 32.5920, "lng": -80.6760}]}],
  "audio": [{"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.2}]
}
```

> NAR: The Moselle property sprawled across 1,700 acres — a hunting lodge,
> dog kennels, and the main residence connected by dirt roads and tree lines.

## Act 2: The Investigation (2:30 - 5:00)

### 2:30 - 3:15 | Crime Scene Evidence

```json bee-video:segment
{
  "visual": [
    {"type": "FOOTAGE", "src": "footage/bodycam-arrival.mp4", "in": "00:00:10.000", "out": "00:00:45.000", "color": "bodycam"},
    {"type": "FOOTAGE", "src": "footage/evidence-photos.mp4", "in": "00:00:00.000", "out": "00:00:30.000"}
  ],
  "audio": [{"type": "SFX", "src": "sfx/radio-chatter.wav", "volume": 0.4}],
  "overlay": [{"type": "QUOTE_CARD", "quote": "I've been up to it now.", "author": "Alex Murdaugh, 911 call"}],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: First responders arrived at 10:28 PM. What they found
> was a scene that would take months to fully process.
>
> NAR: Two weapons had been used — a shotgun for Paul,
> a rifle for Maggie. No casings were ever recovered.

### 3:15 - 3:45 | AI Courtroom Visualization

```json bee-video:segment
{
  "visual": [{"type": "GENERATED", "src": null, "prompt": "courtroom interior dark wood paneling overhead angle", "provider": "stub"}],
  "overlay": [{"type": "FINANCIAL_CARD", "amount": "$8.5 Million", "description": "Alleged stolen client funds"}],
  "transition_in": {"type": "wipeleft", "duration": 0.8}
}
```

> NAR: As investigators dug deeper, a web of financial crimes began to surface.

### 3:45 - 4:15 | Narration Only

> NAR: The Murdaugh family had dominated the legal landscape of
> Hampton County for over a century. Three generations of solicitors.
>
> NAR: But beneath the veneer of Southern respectability lay a pattern
> of obstruction, influence, and unchecked power.

### 4:15 - 4:30 | Photo Evidence

```json bee-video:segment
{
  "visual": [{"type": "PHOTO", "src": "photos/murdaugh-family.jpg", "ken_burns": "zoom_in", "duration": 5.0}],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: The family portrait told one story. The evidence would tell another.

### 4:30 - 4:40 | Waveform Interstitial

```json bee-video:segment
{
  "visual": [{"type": "WAVEFORM", "src": "audio/911-call.wav", "duration": 10.0}],
  "audio": [{"type": "REAL_AUDIO", "src": "audio/911-call.wav", "volume": 0.9}]
}
```

> NAR: The 911 recording would become a critical piece of evidence.

### 4:40 - 4:50 | Evidence Graphic

```json bee-video:segment
{
  "visual": [{"type": "GRAPHIC", "src": "graphics/evidence-timeline.png", "duration": 10.0}]
}
```

> NAR: Investigators mapped every movement that night.

### 4:50 - 5:00 | Closing Black

```json bee-video:segment
{
  "visual": [{"type": "BLACK", "duration": 5.0}],
  "overlay": [{"type": "TEXT_OVERLAY", "text": "Alex Murdaugh was convicted of double murder on March 2, 2023."}],
  "transition_in": {"type": "fade_from_black", "duration": 2.0}
}
```

> NAR: Justice, when it finally came, was decisive.
