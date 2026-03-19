```json bee-video:project
{
  "title": "Test Project",
  "version": 1
}
```

## Section One (0:00 - 0:30)

### 0:00 - 0:15 | First Segment

```json bee-video:segment
{
  "visual": [{"type": "FOOTAGE", "src": "footage/clip-a.mp4"}],
  "audio": [{"type": "REAL_AUDIO", "src": "footage/clip-a.mp4", "volume": 0.8}]
}
```

> NAR: This is the first narration line.
> It continues on the next line.

### 0:15 - 0:30 | Second Segment

```json bee-video:segment
{
  "visual": [{"type": "STOCK", "src": "stock/aerial.mp4", "in": "00:00:05.000", "out": "00:00:20.000"}],
  "transition_in": {"type": "dissolve", "duration": 1.0}
}
```

> NAR: Second segment narration.
