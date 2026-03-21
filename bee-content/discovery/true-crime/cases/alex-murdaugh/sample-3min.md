```json bee-video:project
{
  "title": "Sample Project — 3 Minute Test",
  "version": 1,
  "voice_lock": {
    "engine": "edge",
    "voice": "en-US-GuyNeural"
  },
  "color_preset": "dark_crime",
  "default_transition": {"type": "dissolve", "duration": 1.0},
  "output": {
    "resolution": "1920x1080",
    "fps": 30,
    "codec": "h264",
    "crf": 18
  }
}
```

## Cold Open (0:00 - 0:45)

### 0:00 - 0:15 | 911 Call Opening

```json bee-video:segment
{
  "visual": [
    {
      "type": "FOOTAGE",
      "src": "footage/bodycam-arrival.mp4",
      "in": "00:00:05.000",
      "out": "00:00:20.000",
      "color": "surveillance"
    }
  ],
  "audio": [
    {"type": "REAL_AUDIO", "src": "footage/bodycam-arrival.mp4", "volume": 0.7}
  ],
  "overlay": [
    {
      "type": "TIMELINE_MARKER",
      "date": "June 7, 2021",
      "description": "10:07 PM — 911 call received"
    }
  ],
  "transition_in": {"type": "fade_from_black", "duration": 1.5}
}
```

> NAR: On the night of June 7th, 2021, a 911 call
> shattered the silence of a South Carolina estate.

### 0:15 - 0:30 | The Estate

```json bee-video:segment
{
  "visual": [
    {
      "type": "STOCK",
      "src": null,
      "query": "aerial farm dusk southern plantation",
      "color": "dark_crime",
      "ken_burns": "zoom_out"
    }
  ],
  "audio": [
    {"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.15, "fade_in": 3.0}
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "Moselle Estate",
      "subtext": "1,770 acres — Colleton County, SC"
    }
  ],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: The Moselle estate sprawled across seventeen hundred acres
> of Colleton County. Hunting grounds, dog kennels, and a main
> house that spoke to old money.

### 0:30 - 0:45 | The Dynasty

```json bee-video:segment
{
  "visual": [
    {
      "type": "PHOTO",
      "src": "photos/murdaugh-family.jpg",
      "ken_burns": "zoom_in"
    }
  ],
  "audio": [
    {"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.15}
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "The Murdaugh Family",
      "subtext": "Three generations of solicitors"
    }
  ],
  "captions": {"style": "karaoke", "font_size": 42},
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: The Murdaugh name carried weight in the Lowcountry.
> Three generations of solicitors — a dynasty built on
> power and proximity to the law.

## Act 1: The Night Of (0:45 - 1:30)

### 0:45 - 1:00 | Bodies Found

```json bee-video:segment
{
  "visual": [
    {
      "type": "MAP",
      "style": "tactical",
      "center": [32.5916, -80.6754],
      "zoom": 14,
      "markers": [
        {"label": "Moselle", "lat": 32.5916, "lng": -80.6754}
      ]
    }
  ],
  "audio": [
    {"type": "REAL_AUDIO", "src": "audio/911-call-edited.wav", "volume": 1.0}
  ],
  "overlay": [
    {
      "type": "TIMELINE_MARKER",
      "date": "June 7, 2021",
      "description": "10:07 PM"
    }
  ],
  "transition_in": {"type": "fade_from_black", "duration": 1.0}
}
```

> NAR: That night, Alex Murdaugh called 911 to report
> finding his wife Maggie and son Paul shot dead
> near the dog kennels.

### 1:00 - 1:15 | Bodycam Arrival

```json bee-video:segment
{
  "visual": [
    {
      "type": "FOOTAGE",
      "src": "footage/bodycam-arrival.mp4",
      "in": "00:00:30.000",
      "out": "00:00:45.000",
      "color": "bodycam"
    }
  ],
  "audio": [
    {"type": "REAL_AUDIO", "src": "footage/bodycam-arrival.mp4", "volume": 0.8},
    {"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.1}
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "Colleton County Sheriff's Office",
      "subtext": "Night of June 7, 2021"
    }
  ],
  "transition_in": {"type": "dissolve", "duration": 0.5}
}
```

> NAR: Deputies arrived to find Alex Murdaugh standing
> in the driveway, covered in blood, pointing toward
> the kennels.

### 1:15 - 1:30 | The Scene

```json bee-video:segment
{
  "visual": [
    {
      "type": "STOCK",
      "src": null,
      "query": "crime scene tape night rural",
      "color": "noir"
    }
  ],
  "audio": [
    {"type": "SFX", "src": "sfx/police-radio.wav", "volume": 0.3}
  ],
  "captions": {"style": "phrase", "font_size": 48},
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: What followed would unravel decades of power,
> privilege, and murder.

## Act 2: The Investigation (1:30 - 2:15)

### 1:30 - 1:45 | Courtroom

```json bee-video:segment
{
  "visual": [
    {
      "type": "FOOTAGE",
      "src": "footage/courtroom-testimony.mp4",
      "in": "00:01:00.000",
      "out": "00:01:15.000",
      "color": "cold_blue"
    }
  ],
  "audio": [
    {"type": "REAL_AUDIO", "src": "footage/courtroom-testimony.mp4", "volume": 1.0}
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "Rogan Gibson",
      "subtext": "Witness — Paul's friend"
    }
  ],
  "transition_in": {"type": "dissolve", "duration": 0.8}
}
```

### 1:45 - 2:00 | The Snapchat Video

```json bee-video:segment
{
  "visual": [
    {
      "type": "GRAPHIC",
      "template": "document-mockup",
      "text": "Snapchat Video Evidence",
      "subtext": "Recovered from Paul's phone"
    }
  ],
  "audio": [],
  "overlay": [
    {
      "type": "QUOTE_CARD",
      "quote": "That's the video that broke the case wide open.",
      "author": "Prosecution"
    }
  ],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: A Snapchat video, recovered from Paul's phone,
> placed Alex at the kennels minutes before the murders.
> He had denied being there.

### 2:00 - 2:15 | Financial Trail

```json bee-video:segment
{
  "visual": [
    {
      "type": "GENERATED",
      "src": null,
      "prompt": "dark office desk with scattered financial documents, cinematic lighting",
      "provider": "stub"
    }
  ],
  "audio": [
    {"type": "MUSIC", "src": "music/tension-building.mp3", "volume": 0.2, "fade_in": 2.0}
  ],
  "overlay": [
    {
      "type": "FINANCIAL_CARD",
      "amount": "$10.5 Million",
      "description": "Stolen from clients over 20 years"
    }
  ]
}
```

> NAR: But the murders were just the surface.
> Investigators would uncover a web of financial fraud
> stretching back two decades — ten and a half million
> dollars stolen from his own clients.

## Closing (2:15 - 3:00)

### 2:15 - 2:35 | Verdict

```json bee-video:segment
{
  "visual": [
    {
      "type": "FOOTAGE",
      "src": "footage/verdict-reaction.mp4",
      "color": "dark_crime",
      "ken_burns": "zoom_in"
    }
  ],
  "audio": [
    {"type": "REAL_AUDIO", "src": "footage/verdict-reaction.mp4", "volume": 1.0}
  ],
  "overlay": [
    {
      "type": "TIMELINE_MARKER",
      "date": "March 2, 2023",
      "description": "Verdict Day"
    }
  ],
  "transition_in": {"type": "fade_from_black", "duration": 1.5}
}
```

> NAR: On March second, twenty twenty-three,
> after just three hours of deliberation,
> the jury returned its verdict.

### 2:35 - 2:50 | Mugshot

```json bee-video:segment
{
  "visual": [
    {
      "type": "PHOTO",
      "src": "photos/murdaugh-mugshot.jpg",
      "ken_burns": "zoom_in_pan_right"
    }
  ],
  "audio": [
    {"type": "MUSIC", "src": "music/dark-ambient.mp3", "volume": 0.2, "fade_out": 3.0}
  ],
  "overlay": [
    {
      "type": "LOWER_THIRD",
      "text": "Alex Murdaugh",
      "subtext": "Guilty — Two counts of murder"
    }
  ],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: Guilty. On both counts. The man who called 911
> on his own family was the one who pulled the trigger.

### 2:50 - 3:00 | End Card

```json bee-video:segment
{
  "visual": [
    {
      "type": "BLACK",
      "duration": 10
    }
  ],
  "audio": [],
  "overlay": [
    {
      "type": "TEXT_OVERLAY",
      "text": "Alex Murdaugh was sentenced to two consecutive life terms without parole.",
      "position": "center"
    }
  ],
  "transition_in": {"type": "fade_from_black", "duration": 2.0}
}
```
