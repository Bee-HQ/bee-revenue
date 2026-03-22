# Remotion Text Chat Component

## Goal

Add an animated text message component that renders conversations as chat bubbles in the Remotion preview and MP4 export. Supports iMessage, Android, and generic platform styles with three animation modes (typing indicator, instant, scroll).

## Rendering Modes

- **Visual** (`TEXT_CHAT` in `seg.visual[]`) — full-screen phone background, messages fill the frame
- **Overlay** (`TEXT_CHAT` in `seg.overlay[]`) — semi-transparent backdrop over footage

## Content Format

JSON string in the `content` field of the `LayerEntry`:

```json
[
  {"from": "Alex", "text": "Hey can you come to Moselle?"},
  {"from": "Maggie", "text": "On my way"},
  {"from": "Alex", "text": "Love you"}
]
```

Parser: `JSON.parse(content)` → `ChatMessage[]`. Falls back to displaying raw text if JSON parsing fails.

```ts
interface ChatMessage {
  from: string;
  text: string;
}
```

## Metadata Fields

Read from `LayerEntry.metadata`:

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `platform` | string | `'imessage'` | `'imessage'`, `'android'`, `'generic'` |
| `animation` | string | `'typing'` | `'typing'`, `'instant'`, `'scroll'` |

## Platform Styles

### iMessage
- Incoming (first sender): light gray `#e5e5ea`, dark text, rounded 18px
- Outgoing (other senders): blue `#007aff`, white text, rounded 18px
- Background: white `#fff` (or dark `#1c1c1e` for visual mode)
- Font: system sans-serif, 16px
- Sender name: small gray label above bubble

### Android
- Incoming: white `#fff`, dark text, rounded 8px, slight shadow
- Outgoing: green `#dcf8c6`, dark text, rounded 8px
- Background: `#e5ddd5` chat wallpaper pattern
- Font: Roboto-style sans-serif, 16px

### Generic
- Incoming: dark gray `#2a2a2e`, white text, rounded 12px
- Outgoing: teal `#0d9488`, white text, rounded 12px
- Background: `#111` dark
- Font: sans-serif, 16px

## Animation Modes

### Typing (`animation: 'typing'`)
For each message:
1. Typing indicator appears (3 bouncing dots, ~15 frames)
2. Indicator disappears, message bubble slides up with spring animation
3. Hold ~10 frames before next message starts

Frame budget per message: ~40 frames (at 30fps ≈ 1.3s per message). Total frames distributed evenly across messages, capped to segment duration.

### Instant (`animation: 'instant'`)
Messages pop in one at a time with fade + slight slide-up. ~10 frame gap between each. No typing indicator. Faster pacing.

Frame budget per message: ~20 frames.

### Scroll (`animation: 'scroll'`)
All messages rendered at once in a tall container. Camera (`translateY`) scrolls from top to bottom over the segment duration. No per-message animation.

## Sender Detection

First unique sender name encountered in the messages array = **incoming** (left-aligned). All other senders = **outgoing** (right-aligned). This means the conversation starter appears on the left.

## Component Interface

```ts
interface TextChatProps {
  content: string;           // JSON string of ChatMessage[]
  metadata?: LayerEntryMetadata | null;
  durationInFrames: number;
  mode: 'visual' | 'overlay';  // full-screen or overlay
}
```

For overlay registration, the component receives `OverlayProps` (content, metadata, durationInFrames). `mode` defaults to `'overlay'` when used via the overlay registry.

For visual rendering in `SegmentVisual`, `mode` is set to `'visual'`.

## Integration

### Overlay Mode
Add to `OVERLAY_COMPONENTS` registry in BeeComposition:
```ts
TEXT_CHAT: TextChatOverlay,  // wrapper that passes mode='overlay'
```

Add to `DEFAULT_DURATIONS`:
```ts
TEXT_CHAT: 5,  // 5 seconds default
```

### Visual Mode
In `SegmentVisual`, when `contentType === 'TEXT_CHAT'`, render `<TextChat>` with `mode='visual'` instead of a video/image.

## Files

| File | Action |
|------|--------|
| `web/src/components/remotion/TextChat.tsx` | Create |
| `web/src/components/remotion/overlays.ts` | Add TEXT_CHAT to DEFAULT_DURATIONS |
| `web/src/components/remotion/overlays.test.ts` | Add parser test |
| `web/src/components/BeeComposition.tsx` | Add to OVERLAY_COMPONENTS + SegmentVisual |

## Testing

- Parser: valid JSON → ChatMessage array, invalid JSON → fallback
- Sender detection: first sender = incoming, second = outgoing
- Component renders without crash for each platform × animation combination

## Success Criteria

1. `TEXT_CHAT` in overlay array renders animated chat bubbles over footage
2. `TEXT_CHAT` in visual array renders full-screen chat conversation
3. Platform style changes with `metadata.platform`
4. Animation mode changes with `metadata.animation`
5. Messages animate in correct order with sender alignment
