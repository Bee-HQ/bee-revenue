# Design: Graphics Batch — Text Chat, Social Post, News Montage, Evidence Board

**Date:** 2026-03-17
**Scope:** 4 new Pillow graphics functions for formula visual codes
**Approach:** Recognizable approximation — correct at a glance for 3-5 second inserts

---

## Functions

### 1. text_chat()

```python
@dataclass
class ChatMessage:
    text: str
    sender: bool        # True = right/blue bubble, False = left/grey bubble
    timestamp: str | None = None

def text_chat(
    messages: list[ChatMessage],
    output_path: Path,
    platform: str = "imessage",  # "imessage", "sms", "generic"
    highlight_text: str | None = None,  # text to underline in red
) -> Path:
```

- **iMessage**: blue (#007AFF) sender bubbles right, grey (#E5E5EA) receiver left, white text on blue, dark text on grey
- **SMS**: green (#34C759) sender bubbles instead of blue
- **Generic**: dark grey bubbles on near-black background
- All: 1920x1080, dark background (#0A0A0F), messages stacked vertically, rounded corners, optional timestamps between groups
- If `highlight_text` provided, matching text gets red underline

### 2. social_post()

```python
@dataclass
class SocialPost:
    username: str
    text: str
    platform: str       # "facebook", "instagram", "twitter", "snapchat"
    timestamp: str | None = None
    highlight_text: str | None = None

def social_post(
    post: SocialPost,
    output_path: Path,
) -> Path:
```

- Platform header bar: Facebook (#1877F2), Instagram (#E1306C), Twitter/X (#000000), Snapchat (#FFFC00)
- Username + timestamp below header
- Post text as body
- Dark background (#0A0A0F) behind the card
- Card has slight shadow/border for depth
- Optional red highlight on key text

### 3. news_montage()

```python
def news_montage(
    headlines: list[str],
    output_path: Path,
) -> Path:
```

- Headlines on white/newsprint-colored (#F5F0E8) cards
- Bold serif font (Georgia or Times New Roman with fallback)
- Stacked vertically, each slightly overlapping previous, slight rotation (-2° to +2°)
- Dark background (#0A0A0F)
- 3-6 headlines per image

### 4. evidence_board()

```python
@dataclass
class BoardPerson:
    name: str
    photo_path: Path | None = None

@dataclass
class BoardConnection:
    from_name: str
    to_name: str
    label: str          # "married", "stole from", "employed"

def evidence_board(
    people: list[BoardPerson],
    connections: list[BoardConnection],
    output_path: Path,
) -> Path:
```

- Dark corkboard background (#2A1F14, slight texture via noise)
- Person cards: photo (or grey placeholder) with name label below, pinned look
- Red lines (#DC3232) drawn between connected people
- Connection labels in white on the line midpoints
- Auto-layout: arrange people in a circle for ≤6 people, grid for more

---

## Shared Patterns

All functions follow existing `graphics.py` conventions:
- Output: 1920x1080 PNG
- Use existing `COLORS` dict, `_get_font()`, `_word_wrap()` helpers
- `output_path.parent.mkdir(parents=True, exist_ok=True)` at top
- Return `Path` of written file

New colors added to `COLORS` dict:
```python
"imessage_blue": (0, 122, 255),
"imessage_grey": (229, 229, 234),
"sms_green": (52, 199, 89),
"facebook_blue": (24, 119, 242),
"instagram_pink": (225, 48, 108),
"snapchat_yellow": (255, 252, 0),
"newsprint": (245, 240, 232),
"corkboard": (42, 31, 20),
```

## Files Changed

| File | Change |
|------|--------|
| `processors/graphics.py` | Add `text_chat()`, `social_post()`, `news_montage()`, `evidence_board()` + dataclasses + new colors |
| `tests/test_graphics.py` | Add tests for all 4 functions |

## Files NOT Changed

Everything else — these are pure additions to one existing file.

## Testing Strategy

Each function gets 2-3 tests:
- Basic output: function produces a 1920x1080 PNG
- Variant: platform/style parameter works (e.g., imessage vs sms)
- Edge case: empty input, single item, missing photo

~12 tests total.
