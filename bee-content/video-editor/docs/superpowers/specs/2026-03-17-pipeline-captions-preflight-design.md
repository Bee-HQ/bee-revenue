# Design: Pipeline — ASS Captions + Asset Preflight

**Date:** 2026-03-17
**Scope:** Two independent pipeline features for v0.4.0
**Dependencies:** pysubs2 (core), openai-whisper (optional)

---

## 1. ASS Caption Generation

### Problem

The formula requires `[CAPTION-ANIMATED]` — "bold white animated subtitles, word-by-word or phrase-by-phrase highlight, present throughout entire video." No caption support exists in the tool. This is a high-impact gap for both production quality and accessibility.

### Solution

New processor: `src/bee_video_editor/processors/captions.py` using `pysubs2` to generate styled ASS subtitle files.

#### Segment extraction (the data pipeline)

A new function extracts `CaptionSegment` objects from a `Storyboard`:

```python
def extract_caption_segments(storyboard: Storyboard) -> list[CaptionSegment]:
    """Extract captionable text from storyboard segments.

    Walks every segment's audio layer entries. For each NAR or REAL AUDIO entry:
    - Strips quotes and trailing notes ("+ dark ambient...")
    - Converts segment start/end (MM:SS strings) to milliseconds
    - Uses LayerEntry.time_start/time_end if present (for sub-ranged audio)
    - Maps content_type to style: NAR → "Narrator", REAL AUDIO → "RealAudio"
    """
```

This function lives in `processors/captions.py` and handles the Storyboard model only. The assembly guide's `Project` model is NOT supported for captions — captions require the rich `LayerEntry` structure. The CLI `captions` command must accept a storyboard file (not an assembly guide).

#### Two generation modes

**Estimated mode (default):** Takes `list[CaptionSegment]` (extracted from storyboard), divides words evenly across each segment's time, generates ASS with karaoke fill timing. Zero dependencies beyond pysubs2. Instant generation.

**Precise mode (`--precise`):** Takes a list of `(audio_path, CaptionSegment)` pairs — individual narration audio files paired with their segments. Transcribes each with Whisper to get word-level timestamps within that segment's time range. Requires `openai-whisper` optional dependency.

#### Caption styles (ASS style definitions)

| Style Name | Use | Font | Size | Color | Outline | Position | Animation |
|-----------|-----|------|------|-------|---------|----------|-----------|
| `Narrator` | Narrator voiceover | Bold Arial | 48pt | White (#FFFFFF) | 3px black | Bottom-center | Word-by-word karaoke fill (`\kf`) |
| `NarratorPhrase` | Long narration (alternative) | Bold Arial | 48pt | White (#FFFFFF) | 3px black | Bottom-center | Phrase-by-phrase (3-5 words per block) |
| `RealAudio` | 911 calls, bodycam, trial | Bold italic Arial | 44pt | White (#FFFFFF) | 2px black | Bottom-center | Word-by-word karaoke fill |

Font is `Arial` (available on macOS/Windows) with fallback to `Helvetica` then `DejaVu Sans`. Note: libass (FFmpeg's ASS renderer) uses fontconfig on Linux and CoreText on macOS — the font name must match what the system can resolve.

Style choice is determined by the segment's audio content_type: `NAR` → `Narrator` or `NarratorPhrase`, `REAL AUDIO` → `RealAudio`.

#### Functions

```python
@dataclass
class CaptionSegment:
    """A single captioned section."""
    text: str
    start_ms: int
    end_ms: int
    style_name: str  # "Narrator", "NarratorPhrase", "RealAudio"

def extract_caption_segments(storyboard: Storyboard) -> list[CaptionSegment]:
    """Extract captionable segments from storyboard. Storyboard model only."""

def generate_captions_estimated(
    segments: list[CaptionSegment],
    output_path: Path,
    style: str = "karaoke",  # "karaoke" or "phrase"
) -> Path:
    """Generate ASS captions from text + duration estimates."""

def generate_captions_precise(
    audio_segments: list[tuple[Path, CaptionSegment]],
    output_path: Path,
    style: str = "karaoke",
) -> Path:
    """Generate ASS captions from audio via Whisper transcription.

    Args:
        audio_segments: List of (audio_file, CaptionSegment) pairs.
            Each audio file is transcribed independently.
    """
```

#### ASS generation details

**Karaoke timing math:** Each word gets a `\kf` tag with duration proportional to word length. Use integer division with remainder redistribution to avoid cumulative rounding drift:

```python
total_cs = (end_ms - start_ms) // 10  # centiseconds
total_chars = sum(len(w) for w in words)
base_per_char = total_cs // total_chars
remainder = total_cs - (base_per_char * total_chars)
# Distribute remainder 1cs at a time to longest words first
```

This ensures word durations sum exactly to the segment duration with no drift.

**Phrase mode:** Group words into balanced chunks of 3-5 words. Algorithm: `chunk_size = min(5, max(3, len(words) // ceil(len(words) / 4)))`. Segments with fewer than 3 words get a single chunk. Each chunk is a separate ASS event spanning its proportional time range.

ASS file setup:
- PlayResX: 1920, PlayResY: 1080
- Style definitions for Narrator, NarratorPhrase, RealAudio
- Font: Arial (fallback: Helvetica, DejaVu Sans)

#### Integration

**CLI:** `bee-video captions <storyboard.md> -p ./proj [--precise] [--style karaoke|phrase]`
- Parses storyboard file (storyboard format only — not assembly guide)
- Calls `extract_caption_segments()` to get text + timing
- Calls `generate_captions_estimated()` or `generate_captions_precise()`
- Writes `output/captions/captions.ass`

**API:** `POST /api/production/captions` with optional `{ "precise": false, "style": "karaoke" }`. Uses session's loaded storyboard via `session.require_project()` (same pattern as other production endpoints).

**Assembly:** Caption burn-in is a **post-processing step** after `assemble_final()` concatenates the video. A new function `burn_captions(video_path, ass_path, output_path)` runs:
```
ffmpeg -i final_assembled.mp4 -vf "ass=/absolute/path/to/captions.ass" final_with_captions.mp4
```
This is a second encode pass. For a 50-minute video, this adds ~5-10 minutes of processing. The alternative (modifying concat functions to accept vf filters) would require changing `processors/ffmpeg.py`'s interface — not worth it for a single filter. The post-processing approach keeps the change isolated.

Path passed to the `ass` filter uses absolute path with proper escaping for FFmpeg filter syntax.

**Init directory:** `init_project` in `services/production.py` needs `"captions"` added to its output subdirectory list.

**New dependency:** `pysubs2` added to core deps in pyproject.toml.
**Optional:** `openai-whisper` in `[captions-precise]` extra.

---

## 2. Asset Preflight

### Problem

The #1 time-waster in production is finding missing assets mid-assembly. A 50-minute video has 50-80 visual segments, each needing specific footage, graphics, or stock files. Currently there's no way to check what's ready and what's missing before starting the 6-8 hour assembly session.

### Solution

New service: `src/bee_video_editor/services/preflight.py` that scans a storyboard, checks each segment's asset requirements against files on disk, and produces a structured report + JSON manifest.

#### Data model

```python
@dataclass
class AssetEntry:
    """A single asset requirement from one segment."""
    segment_id: str
    layer: str           # "visual", "audio", "overlay"
    visual_code: str     # "BROLL-DARK", "COURTROOM", "LOWER-THIRD"
    qualifier: str       # "arrival at Moselle", "testimony — Rogan Gibson"
    status: str          # "found", "missing", "generated", "needs-check"
    file_path: str | None

@dataclass
class PreflightReport:
    """Result of scanning a storyboard against project assets."""
    total: int
    found: int
    missing: int
    generated: int
    needs_check: int
    entries: list[AssetEntry]

    @property
    def ok(self) -> bool:
        return self.missing == 0
```

#### Asset resolution rules

The preflight scanner maps visual codes to expected file locations:

#### Generated graphics (bee-video can produce these)
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `LOWER-THIRD` | `output/graphics/` | `lower-third-*.png` | `missing` |
| `TIMELINE-MARKER` | `output/graphics/` | `timeline-*.png` | `missing` |
| `FINANCIAL-CARD` | `output/graphics/` | `financial-*.png` | `missing` |
| `MUGSHOT-CARD` | `output/graphics/` | `mugshot-*.png` | `missing` |
| `QUOTE-CARD` | `output/graphics/` | `quote-*.png` | `missing` |
| `BRAND-STING` | `output/graphics/` | `brand-*` | `missing` |
| `DISCLAIMER` | `output/graphics/` | `disclaimer-*` | `missing` |

#### Source footage (user must provide)
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `COURTROOM` | `footage/` | `trial-*.mp4` | `missing` |
| `BODYCAM` | `footage/` | `bodycam-*.mp4` | `missing` |
| `INTERROGATION` | `footage/` | `interrogation-*.mp4` | `missing` |
| `WAVEFORM-AERIAL` | `output/segments/` | any audio viz file | `missing` |
| `WAVEFORM-DARK` | `output/segments/` | any audio viz file | `missing` |

#### Photos and PIP
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `PIP-SINGLE` | `photos/` | `pip-*.png` | `missing` |
| `PIP-DUAL` | `photos/` | `pip-*.png` (needs 2+) | `missing` |

#### Maps
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `MAP-FLAT` | `maps/` | `map-*.png` or `map-*.mp4` | `missing` |
| `MAP-3D` | `maps/` | `map-*.png` or `map-*.mp4` | `missing` |
| `MAP-TACTICAL` | `maps/` | `map-*.png` or `map-*.mp4` | `missing` |
| `MAP-PULSE` | `maps/` | `map-*.png` or `map-*.mp4` | `missing` |
| `MAP-ROUTE` | `maps/` | `map-*.png` or `map-*.mp4` | `missing` |

#### Stock B-roll (can't match by qualifier)
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `BROLL-DARK` | `stock/` | any video file | `needs-check` |

#### Audio
| Visual Code | Look In | Match Pattern | Status if not found |
|------------|---------|---------------|-------------------|
| `NAR` (audio) | `output/narration/` | `nar-*.mp3` | `missing` |

#### Not yet supported by bee-video (report as `not-supported`)
| Visual Code | Notes |
|------------|-------|
| `DOCUMENT-MOCKUP` | Planned for future |
| `TEXT-CHAT` | v0.4.0 graphics |
| `SOCIAL-POST` | v0.4.0 graphics |
| `NEWS-MONTAGE` | v0.4.0 graphics |
| `EVIDENCE-BOARD` | v0.4.0 graphics |
| `FLOW-DIAGRAM` | v0.5.0 |
| `TIMELINE-SEQUENCE` | v0.5.0 |
| `POLICE-DB` | Future |
| `DESKTOP-PHOTOS` | Future |
| `EVIDENCE-CLOSEUP` | Future |
| `EVIDENCE-DISPLAY` | Future |
| `BODY-DIAGRAM` | Future |
| `SPLIT-INFO` | Future |
| `TRAILER` | Montage — not a single asset |

#### Persistent modifiers (not assets — excluded from preflight)
`COLOR-GRADE`, `VIGNETTE`, `LETTERBOX`, `CAPTION-ANIMATED`, `TR-*` transitions, `STILL`

For codes with qualifiers (e.g., `[COURTROOM: testimony — Rogan Gibson]`), the scanner checks if any matching file exists but can't verify content matches the qualifier — it reports `found` if a file matches the pattern, `needs-check` for stock/B-roll where qualifier matching isn't possible.

For unrecognized visual codes (any code not in the tables above), report as `unknown` with the raw code in the entry.

#### Function

```python
def run_preflight(storyboard: Storyboard, project_dir: Path) -> PreflightReport:
    """Scan storyboard against project assets and report gaps."""
```

Iterates every segment, every layer (visual, audio, overlay), extracts the visual code + qualifier from parsed `content_type` and `content` fields, looks up the resolution rule, checks disk.

#### CLI

`bee-video preflight <guide> -p ./proj`

Output: Rich table with columns: Segment | Layer | Code | Qualifier | Status | File
- Green: found
- Red: missing
- Yellow: needs-check

Summary line: `"42 assets: 28 found, 8 missing, 6 need manual check"`

#### JSON manifest

Written to `output/asset-manifest.json`:
```json
{
  "total": 42,
  "found": 28,
  "missing": 8,
  "generated": 0,
  "needs_check": 6,
  "entries": [
    {
      "segment_id": "0_00-0_05",
      "layer": "visual",
      "visual_code": "WAVEFORM-AERIAL",
      "qualifier": "911 call waveform over dark Moselle aerial",
      "status": "missing",
      "file_path": null
    }
  ]
}
```

#### API

`GET /api/production/preflight` — returns the PreflightReport as JSON.

---

## Files Changed

| File | Change |
|------|--------|
| `processors/captions.py` | **New.** `CaptionSegment`, `extract_caption_segments()`, `generate_captions_estimated()`, `generate_captions_precise()`, `burn_captions()`, ASS style definitions. |
| `services/preflight.py` | **New.** `run_preflight()`, `AssetEntry`, `PreflightReport`, resolution rules for all visual codes. |
| `adapters/cli.py` | Add `captions` and `preflight` commands. |
| `api/routes/production.py` | Add `POST /api/production/captions` and `GET /api/production/preflight` endpoints. Both use `session.require_project()`. |
| `api/schemas.py` | Add `PreflightReportSchema`, `AssetEntrySchema`, `CaptionRequest`. |
| `services/production.py` | Update `assemble_final()` to call `burn_captions()` as post-processing if ASS file exists. Add `"captions"` to `init_project()` directory list. |
| `pyproject.toml` | Add `pysubs2` to core deps, add `[captions-precise]` extra with `openai-whisper`. |
| `tests/test_captions.py` | **New.** Tests for extraction, estimated/precise generation, style application, karaoke timing, phrase grouping, burn-in. |
| `tests/test_preflight.py` | **New.** Tests for asset resolution, report generation, missing/found/needs-check/not-supported/unknown classification. |

## Files NOT Changed

- `processors/ffmpeg.py` — no change (burn_captions uses its own FFmpeg call; concat functions untouched)
- `processors/graphics.py` — no change
- `processors/tts.py` — no change
- `parsers/*` — no change (parser already recognizes bible codes from v0.3.1)
- `web/*` — no frontend changes in this spec

## Testing Strategy

### Captions
- Unit test: `extract_caption_segments` with mock storyboard containing NAR and REAL AUDIO entries, verify correct CaptionSegment output including time-ranged entries
- Unit test: extraction handles empty text, strips quotes and `+ music` suffixes
- Unit test: `generate_captions_estimated` with 3 segments, verify ASS file has correct event count, timing, karaoke tags
- Unit test: karaoke timing durations sum exactly to segment duration (no drift from rounding)
- Unit test: phrase mode groups words into balanced 3-5 word chunks, handles segments with <3 words
- Unit test: style selection based on content_type (NAR → Narrator, REAL AUDIO → RealAudio)
- Integration test: mock Whisper for precise mode, verify word-level timestamps in output
- Integration test: verify generated ASS file is valid (pysubs2 can re-parse it without error)

### Preflight
- Unit test: `run_preflight` with mock storyboard + mock project dir containing some files, verify found/missing/needs-check counts
- Unit test: each visual code resolves to correct directory and pattern
- Unit test: empty project dir → all entries missing
- Unit test: unknown visual code → status "unknown"
- Unit test: not-supported codes (TEXT-CHAT, FLOW-DIAGRAM etc.) → status "not-supported"
- Unit test: JSON manifest written correctly and can be re-parsed
- Unit test: `PreflightReport.ok` property (True when 0 missing, False otherwise)
