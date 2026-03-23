# All Remotion Components Test

```bee-video:project
{"title": "Remotion Component Tests", "fps": 30, "resolution": [1920, 1080], "quality": "standard"}
```

## Overlay Components

### seg-01 | LowerThird

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "LOWER_THIRD", "content": "", "text": "Alex Murdaugh", "subtext": "Defendant — Double Murder Trial"}],
  "music": [],
  "duration": 5
}
```

### seg-02 | TimelineMarker

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "TIMELINE_MARKER", "content": "", "date": "June 7, 2021", "description": "10:07 PM — 911 call received"}],
  "music": [],
  "duration": 5
}
```

### seg-03 | QuoteCard

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "QUOTE_CARD", "content": "", "quote": "That's the video that broke the case wide open.", "author": "Prosecution", "color": "red"}],
  "music": [],
  "duration": 5
}
```

### seg-04 | FinancialCard

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "FINANCIAL_CARD", "content": "", "amount": "$10.5 Million", "description": "Stolen from clients over 20 years"}],
  "music": [],
  "duration": 5
}
```

### seg-05 | TextOverlay

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "TEXT_OVERLAY", "content": "", "text": "Alex Murdaugh was sentenced to two consecutive life terms without parole."}],
  "music": [],
  "duration": 5
}
```

### seg-06 | Callout Circle

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "CALLOUT", "content": "Key evidence", "style": "circle", "target": [0.5, 0.4], "animation": "draw", "targetSize": 120}],
  "music": [],
  "duration": 4
}
```

### seg-07 | Callout Arrow

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "CALLOUT", "content": "Look here", "style": "arrow", "target": [0.7, 0.5], "animation": "pop"}],
  "music": [],
  "duration": 4
}
```

## Visual Components

### seg-08 | KineticText Punch

```bee-video:segment
{
  "visual": [{"type": "KINETIC_TEXT", "src": null, "content": "This is *really* **important** news", "preset": "punch"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 5
}
```

### seg-09 | KineticText Highlight

```bee-video:segment
{
  "visual": [{"type": "KINETIC_TEXT", "src": null, "content": "The *DNA evidence* proved that **Alex Murdaugh** was at the scene", "preset": "highlight", "background": "dark"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 5
}
```

### seg-10 | TextChat iMessage

```bee-video:segment
{
  "visual": [{"type": "TEXT_CHAT", "src": null, "content": "[{\"from\": \"Paul\", \"text\": \"Come to Moselle tonight\"}, {\"from\": \"Rogan\", \"text\": \"On my way\"}, {\"from\": \"Paul\", \"text\": \"Bring the dogs they got out again\"}]", "platform": "imessage", "animation": "typing"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 8
}
```

### seg-11 | TextChat Android

```bee-video:segment
{
  "visual": [{"type": "TEXT_CHAT", "src": null, "content": "[{\"from\": \"Alex\", \"text\": \"Where are you?\"}, {\"from\": \"Maggie\", \"text\": \"Almost there\"}, {\"from\": \"Alex\", \"text\": \"Hurry up\"}]", "platform": "android", "animation": "instant"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-12 | EvidenceBoard

```bee-video:segment
{
  "visual": [{"type": "EVIDENCE_BOARD", "src": null, "content": "{\"items\": [{\"label\": \"Alex Murdaugh\"}, {\"label\": \"Maggie Murdaugh\"}, {\"label\": \"Paul Murdaugh\"}, {\"label\": \"$10M Stolen\"}, {\"label\": \"Insurance Fraud\"}], \"connections\": [[0,1],[0,2],[0,3],[3,4]]}"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 8
}
```

### seg-13 | SocialPost Twitter

```bee-video:segment
{
  "visual": [{"type": "SOCIAL_POST", "src": null, "content": "{\"author\": \"@CourtTV\", \"text\": \"BREAKING: Alex Murdaugh found GUILTY of murdering his wife Maggie and son Paul. #MurdaughTrial\", \"likes\": 12400, \"retweets\": 3200}", "platform": "twitter", "animation": "slide"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-14 | SocialPost Instagram

```bee-video:segment
{
  "visual": [{"type": "SOCIAL_POST", "src": null, "content": "{\"author\": \"truecrimedaily\", \"text\": \"Justice served. Alex Murdaugh sentenced to life without parole.\", \"likes\": 45000}", "platform": "instagram", "animation": "reveal"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-15 | AudioVisualization Bars

```bee-video:segment
{
  "visual": [{"type": "WAVEFORM", "src": null, "content": "{\"label\": \"911 Call — June 7, 2021\", \"style\": \"bars\"}"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 8
}
```

### seg-16 | AudioVisualization Waveform

```bee-video:segment
{
  "visual": [{"type": "WAVEFORM", "src": null, "content": "{\"label\": \"Police Interview Recording\", \"style\": \"waveform\"}"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

## P0 Components

### seg-21 | PhotoViewerCard Single

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "PHOTO_VIEWER", "content": "Craig Thetford — Victim", "animation": "slide-up"}],
  "music": [],
  "duration": 6
}
```

### seg-22 | PhotoViewerCard Multi

```bee-video:segment
{
  "visual": [{"type": "PHOTO_VIEWER", "src": null, "content": "[{\"name\":\"Bill Caisse\",\"role\":\"Ex-husband\"},{\"name\":\"Scott Griffin\",\"role\":\"Neighbor\"}]", "animation": "slide-up"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-23 | SourceBadge

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "SOURCE_BADGE", "content": "REENACTMENT"}],
  "music": [],
  "duration": 5
}
```

### seg-24 | SourceBadge top-right

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "SOURCE_BADGE", "content": "ACTUAL PHOTO", "position": "top-right"}],
  "music": [],
  "duration": 5
}
```

### seg-25 | BulletList Stagger

```bee-video:segment
{
  "visual": [{"type": "BULLET_LIST", "src": null, "content": "INTENTIONALLY SHOT CRAIG\nMOVED AND HID THE BODY\nLIED ABOUT HIS WHEREABOUTS\nLOOTED SHARED ASSETS", "accent": "red", "style": "stagger"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-26 | BulletList Cascade Teal

```bee-video:segment
{
  "visual": [{"type": "BULLET_LIST", "src": null, "content": "Found the weapon\nRecovered DNA evidence\nMatched fingerprints\nPhone records confirmed", "accent": "teal", "style": "cascade"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-27 | InfoCard with sections

```bee-video:segment
{
  "visual": [{"type": "INFO_CARD", "src": null, "content": "{\"sections\":[{\"header\":\"Charges\",\"body\":\"First degree murder\\nSecond degree murder\"},{\"header\":\"Sentence\",\"body\":\"Life in prison without parole\"}]}", "photoSide": "right"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 7
}
```

### seg-28 | InfoCard no photo

```bee-video:segment
{
  "visual": [{"type": "INFO_CARD", "src": null, "content": "{\"sections\":[{\"header\":\"Timeline\",\"body\":\"June 7: Murders committed\"},{\"header\":\"Investigation\",\"body\":\"June 8: Bodies discovered\"},{\"header\":\"Arrest\",\"body\":\"October 14: Murdaugh arrested\"}]}", "photoSide": "none"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 7
}
```

## P1 Components

### seg-29 | Caption Keyword Coloring

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [{"type": "NAR", "src": null, "text": "Or is that {red:blood} on the floor? She had {red:multiple injuries} on the {teal:property}"}],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-30 | NotepadWindow Typewriter

```bee-video:segment
{
  "visual": [{"type": "NOTEPAD", "src": null, "content": "Previous Phone Call:\n- said her mom is crazy\n- thinks she might've poisoned Craig\n- Current whereabouts unknown", "animation": "typewriter", "windowTitle": "Case Notes"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 8
}
```

### seg-31 | NotepadWindow Lines

```bee-video:segment
{
  "visual": [{"type": "NOTEPAD", "src": null, "content": "Key Evidence:\n1. Blood spatter pattern\n2. Shell casings matched\n3. Phone location data\n4. Financial motive confirmed", "animation": "lines", "windowTitle": "Evidence Summary"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 7
}
```

### seg-32 | NotepadWindow with AnimatedBG

```bee-video:segment
{
  "visual": [{"type": "NOTEPAD", "src": null, "content": "Witness Statement:\n- Saw suspect leave at 10:15 PM\n- Vehicle was a dark SUV\n- Heard two shots fired", "animation": "typewriter", "background": "animated-teal"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 8
}
```

### seg-33 | PhotoViewerCard with AnimatedBG

```bee-video:segment
{
  "visual": [{"type": "PHOTO_VIEWER", "src": null, "content": "Deana Thetford — Suspect", "animation": "slide-up", "background": "animated-red"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "duration": 6
}
```

### seg-34 | MapAnnotation

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "MAP_ANNOTATION", "content": "[{\"type\":\"circle\",\"x\":0.35,\"y\":0.4,\"r\":0.05},{\"type\":\"path\",\"points\":[[0.35,0.4],[0.5,0.45],[0.65,0.5]]},{\"type\":\"rect\",\"x\":0.6,\"y\":0.35,\"w\":0.15,\"h\":0.12}]", "color": "red"}],
  "music": [],
  "duration": 7
}
```

### seg-35 | MapAnnotation Teal

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [{"type": "MAP_ANNOTATION", "content": "[{\"type\":\"circle\",\"x\":0.5,\"y\":0.5,\"r\":0.08},{\"type\":\"circle\",\"x\":0.3,\"y\":0.3,\"r\":0.04}]", "color": "teal"}],
  "music": [],
  "duration": 6
}
```

## Combination Tests

### seg-17 | LowerThird + QuoteCard stacked

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [
    {"type": "LOWER_THIRD", "content": "", "text": "Prosecutor", "subtext": "State of South Carolina"},
    {"type": "QUOTE_CARD", "content": "", "quote": "He looked them in the eyes and lied.", "author": "Creighton Waters", "color": "teal"}
  ],
  "music": [],
  "duration": 6
}
```

### seg-18 | Callout + TimelineMarker stacked

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [],
  "overlay": [
    {"type": "TIMELINE_MARKER", "content": "", "date": "March 2, 2023", "description": "Verdict Day"},
    {"type": "CALLOUT", "content": "Defendant's reaction", "style": "circle", "target": [0.4, 0.5], "animation": "draw"}
  ],
  "music": [],
  "duration": 5
}
```

### seg-19 | KineticText with Callout overlay

```bee-video:segment
{
  "visual": [{"type": "KINETIC_TEXT", "src": null, "content": "The jury found him **GUILTY** on all counts", "preset": "punch"}],
  "audio": [],
  "overlay": [{"type": "CALLOUT", "content": "Verdict", "style": "underline", "target": [0.5, 0.5], "animation": "draw"}],
  "music": [],
  "duration": 5
}
```

### seg-20 | Captions test (NAR audio)

```bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [{"type": "NAR", "src": null, "text": "On the night of June seventh, two thousand twenty-one, a call came in to Colleton County dispatch."}],
  "overlay": [{"type": "LOWER_THIRD", "content": "", "text": "Colleton County", "subtext": "Night of the murders"}],
  "music": [],
  "duration": 8
}
```
