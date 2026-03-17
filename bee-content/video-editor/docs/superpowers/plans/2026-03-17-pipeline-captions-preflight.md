# Pipeline: ASS Captions + Asset Preflight Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ASS caption generation (word-by-word karaoke + phrase mode) and asset preflight checking to bee-video-editor.

**Architecture:** Two independent features. Captions: new `processors/captions.py` using pysubs2 to generate styled ASS files from storyboard segments, with FFmpeg burn-in as post-processing. Preflight: new `services/preflight.py` that scans storyboard visual codes against project files on disk, produces a report + JSON manifest.

**Tech Stack:** Python 3.11+, pysubs2, FFmpeg (ass filter), pytest

**Spec:** `docs/superpowers/specs/2026-03-17-pipeline-captions-preflight-design.md`

---

## Chunk 1: ASS Caption Generation

### Task 1: Add pysubs2 dependency + CaptionSegment dataclass + extraction tests

**Files:**
- Modify: `pyproject.toml`
- Create: `src/bee_video_editor/processors/captions.py`
- Create: `tests/test_captions.py`

- [ ] **Step 1: Add pysubs2 to pyproject.toml**

Add `"pysubs2>=1.7.0"` to the `dependencies` list in `pyproject.toml`. Also add:
```toml
captions-precise = ["openai-whisper"]
```
to `[project.optional-dependencies]`.

Run: `cd bee-content/video-editor && uv sync`

- [ ] **Step 2: Write failing tests for CaptionSegment + extraction**

Create `tests/test_captions.py`:

```python
"""Tests for ASS caption generation."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.processors.captions import (
    CaptionSegment,
    extract_caption_segments,
)
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _make_segment(id, start, end, title, audio_entries):
    """Helper to create a StoryboardSegment with audio entries."""
    return StoryboardSegment(
        id=id, start=start, end=end, title=title,
        section="TEST", section_time=f"{start} - {end}", subsection="",
        audio=[
            LayerEntry(content=text, content_type=ctype, time_start=ts, time_end=te, raw=text)
            for text, ctype, ts, te in audio_entries
        ],
    )


class TestCaptionSegment:
    def test_basic(self):
        seg = CaptionSegment(text="Hello world", start_ms=0, end_ms=5000, style_name="Narrator")
        assert seg.text == "Hello world"
        assert seg.start_ms == 0
        assert seg.end_ms == 5000


class TestExtractCaptionSegments:
    def test_extracts_nar_entries(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("This is the narrator speaking.", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].text == "This is the narrator speaking."
        assert result[0].start_ms == 0
        assert result[0].end_ms == 10000
        assert result[0].style_name == "Narrator"

    def test_extracts_real_audio(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_10-0_20", "0:10", "0:20", "911", [
                ("I need help!", "REAL AUDIO", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].style_name == "RealAudio"

    def test_uses_time_range_if_present(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_30-0_40", "0:30", "0:40", "MIX", [
                ("Deputy speaks here", "REAL AUDIO", "0:30", "0:35"),
                ("Narrator bridges", "NAR", "0:35", "0:40"),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 2
        assert result[0].start_ms == 30000
        assert result[0].end_ms == 35000
        assert result[1].start_ms == 35000
        assert result[1].end_ms == 40000

    def test_strips_quotes_and_trailing_notes(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ('"This is quoted text" + dark ambient music', "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert result[0].text == "This is quoted text"

    def test_skips_empty_text(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 0

    def test_skips_non_caption_types(self):
        sb = Storyboard(title="Test", segments=[
            _make_segment("0_00-0_10", "0:00", "0:10", "INTRO", [
                ("Background music", "MUSIC", None, None),
                ("Narrator line", "NAR", None, None),
            ]),
        ], production_rules=ProductionRules())
        result = extract_caption_segments(sb)
        assert len(result) == 1
        assert result[0].text == "Narrator line"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_captions.py -v`
Expected: FAIL with ImportError

- [ ] **Step 4: Implement CaptionSegment and extract_caption_segments**

Create `src/bee_video_editor/processors/captions.py`:

```python
"""ASS caption generation — word-by-word karaoke and phrase-by-phrase subtitles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import ceil
from pathlib import Path

from bee_video_editor.models_storyboard import Storyboard


@dataclass
class CaptionSegment:
    """A single captioned section."""
    text: str
    start_ms: int
    end_ms: int
    style_name: str  # "Narrator", "NarratorPhrase", "RealAudio"


def _time_to_ms(t: str) -> int:
    """Convert MM:SS or H:MM:SS string to milliseconds."""
    parts = t.strip().split(":")
    if len(parts) == 2:
        return (int(parts[0]) * 60 + int(parts[1])) * 1000
    if len(parts) == 3:
        return (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])) * 1000
    return 0


def _clean_text(raw: str) -> str:
    """Strip quotes, smart quotes, and trailing notes from caption text."""
    text = re.sub(r'\s*\+\s*.*$', '', raw)
    text = text.strip().strip('"').strip('\u201c').strip('\u201d')
    return text.strip()


CAPTION_CONTENT_TYPES = {"NAR", "REAL AUDIO"}

STYLE_MAP = {
    "NAR": "Narrator",
    "REAL AUDIO": "RealAudio",
}


def extract_caption_segments(storyboard: Storyboard) -> list[CaptionSegment]:
    """Extract captionable text from storyboard segments.

    Walks every segment's audio layer entries. For each NAR or REAL AUDIO entry:
    - Strips quotes and trailing notes
    - Converts times to milliseconds
    - Uses LayerEntry.time_start/time_end if present
    - Maps content_type to style name
    """
    results = []
    for seg in storyboard.segments:
        seg_start_ms = _time_to_ms(seg.start)
        seg_end_ms = _time_to_ms(seg.end)

        for entry in seg.audio:
            if entry.content_type not in CAPTION_CONTENT_TYPES:
                continue

            text = _clean_text(entry.content)
            if not text:
                continue

            # Use entry-level time range if available, else segment range
            if entry.time_start and entry.time_end:
                start_ms = _time_to_ms(entry.time_start)
                end_ms = _time_to_ms(entry.time_end)
            else:
                start_ms = seg_start_ms
                end_ms = seg_end_ms

            style_name = STYLE_MAP.get(entry.content_type, "Narrator")

            results.append(CaptionSegment(
                text=text,
                start_ms=start_ms,
                end_ms=end_ms,
                style_name=style_name,
            ))

    return results
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_captions.py -v`
Expected: PASS (7 tests)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/bee_video_editor/processors/captions.py tests/test_captions.py
git commit -m "feat(video-editor): add CaptionSegment dataclass and storyboard extraction"
```

### Task 2: Implement generate_captions_estimated (karaoke + phrase mode) + tests

**Files:**
- Modify: `src/bee_video_editor/processors/captions.py`
- Modify: `tests/test_captions.py`

- [ ] **Step 1: Write failing tests for estimated caption generation**

Add to `tests/test_captions.py`:

```python
from bee_video_editor.processors.captions import generate_captions_estimated
import pysubs2


class TestGenerateCaptionsEstimated:
    def test_karaoke_generates_ass(self):
        segments = [
            CaptionSegment("Hello world test", 0, 3000, "Narrator"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            result = generate_captions_estimated(segments, out, style="karaoke")
            assert result.exists()
            # Verify it's valid ASS
            subs = pysubs2.load(str(result))
            assert len(subs.events) == 1
            assert r"\kf" in subs.events[0].text

    def test_karaoke_timing_sums_exactly(self):
        segments = [
            CaptionSegment("This is a test sentence with several words", 0, 5000, "Narrator"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="karaoke")
            subs = pysubs2.load(str(out))
            event = subs.events[0]
            # Extract all \kfNN values and sum them
            kf_values = [int(m) for m in re.findall(r'\\kf(\d+)', event.text)]
            total_cs = 500  # 5000ms = 500cs
            assert sum(kf_values) == total_cs

    def test_phrase_mode(self):
        text = "This is a test sentence with many words in it"
        segments = [CaptionSegment(text, 0, 5000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="phrase")
            subs = pysubs2.load(str(out))
            # Phrase mode creates multiple events per segment
            assert len(subs.events) >= 2
            # Each event should have 3-5 words
            for event in subs.events:
                word_count = len(event.text.strip().split())
                assert 1 <= word_count <= 5

    def test_phrase_mode_short_segment(self):
        segments = [CaptionSegment("Two words", 0, 2000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out, style="phrase")
            subs = pysubs2.load(str(out))
            assert len(subs.events) == 1

    def test_multiple_segments(self):
        segments = [
            CaptionSegment("First segment", 0, 3000, "Narrator"),
            CaptionSegment("Second segment", 3000, 6000, "RealAudio"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            subs = pysubs2.load(str(out))
            assert len(subs.events) == 2
            assert subs.events[0].style == "Narrator"
            assert subs.events[1].style == "RealAudio"

    def test_styles_defined(self):
        segments = [CaptionSegment("Test", 0, 1000, "Narrator")]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            subs = pysubs2.load(str(out))
            assert "Narrator" in subs.styles
            assert "NarratorPhrase" in subs.styles
            assert "RealAudio" in subs.styles

    def test_reparse_is_valid(self):
        segments = [
            CaptionSegment("Hello world", 0, 2000, "Narrator"),
            CaptionSegment("Real audio clip", 2000, 4000, "RealAudio"),
        ]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "captions.ass"
            generate_captions_estimated(segments, out)
            # Should not raise
            subs = pysubs2.load(str(out))
            resaved = Path(d) / "resaved.ass"
            subs.save(str(resaved))
            assert resaved.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_captions.py::TestGenerateCaptionsEstimated -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement generate_captions_estimated**

Add to `src/bee_video_editor/processors/captions.py`:

```python
import pysubs2


def _create_ass_styles(subs: pysubs2.SSAFile) -> None:
    """Add caption styles to an ASS file."""
    base = dict(
        fontname="Arial",
        fontsize=48,
        primarycolor=pysubs2.Color(255, 255, 255, 0),
        outlinecolor=pysubs2.Color(0, 0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 128),
        bold=True,
        outline=3,
        shadow=2,
        alignment=2,  # bottom-center
        marginl=40,
        marginr=40,
        marginv=50,
    )
    subs.styles["Narrator"] = pysubs2.SSAStyle(**base)
    subs.styles["NarratorPhrase"] = pysubs2.SSAStyle(**base)
    subs.styles["RealAudio"] = pysubs2.SSAStyle(
        **{**base, "fontsize": 44, "italic": True, "outline": 2},
    )


def _karaoke_text(text: str, duration_ms: int) -> str:
    """Generate karaoke-tagged text with \kf tags.

    Distributes duration proportionally to word length with
    integer division + remainder redistribution.
    """
    words = text.split()
    if not words:
        return text

    total_cs = duration_ms // 10
    if total_cs <= 0:
        return text

    total_chars = sum(len(w) for w in words)
    if total_chars == 0:
        # All empty strings somehow
        per_word = total_cs // len(words)
        return " ".join(f"{{\\kf{per_word}}}{w}" for w in words)

    base_per_char = total_cs // total_chars
    remainder = total_cs - (base_per_char * total_chars)

    # Sort word indices by length (longest first) for remainder distribution
    sorted_indices = sorted(range(len(words)), key=lambda i: len(words[i]), reverse=True)
    extras = set(sorted_indices[:remainder])

    parts = []
    for i, word in enumerate(words):
        dur = base_per_char * len(word) + (1 if i in extras else 0)
        parts.append(f"{{\\kf{dur}}}{word}")

    return " ".join(parts)


def _phrase_chunks(words: list[str], target_size: int = 4) -> list[list[str]]:
    """Split words into balanced chunks of 3-5 words."""
    if len(words) <= 5:
        return [words]

    chunk_size = min(5, max(3, len(words) // ceil(len(words) / target_size)))
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


def generate_captions_estimated(
    segments: list[CaptionSegment],
    output_path: Path,
    style: str = "karaoke",
) -> Path:
    """Generate ASS captions from text + duration estimates.

    Args:
        segments: List of CaptionSegment with text, timing, and style.
        output_path: Where to write the .ass file.
        style: "karaoke" for word-by-word fill, "phrase" for 3-5 word blocks.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = "1920"
    subs.info["PlayResY"] = "1080"
    _create_ass_styles(subs)

    for seg in segments:
        if style == "phrase":
            words = seg.text.split()
            chunks = _phrase_chunks(words)
            total_dur = seg.end_ms - seg.start_ms
            dur_per_chunk = total_dur // len(chunks) if chunks else total_dur

            for j, chunk in enumerate(chunks):
                chunk_start = seg.start_ms + j * dur_per_chunk
                chunk_end = chunk_start + dur_per_chunk
                if j == len(chunks) - 1:
                    chunk_end = seg.end_ms  # last chunk gets remainder

                event = pysubs2.SSAEvent(
                    start=chunk_start,
                    end=chunk_end,
                    text=" ".join(chunk),
                    style=seg.style_name if seg.style_name != "Narrator" else "NarratorPhrase",
                )
                subs.events.append(event)
        else:
            # Karaoke mode
            duration_ms = seg.end_ms - seg.start_ms
            tagged_text = _karaoke_text(seg.text, duration_ms)
            event = pysubs2.SSAEvent(
                start=seg.start_ms,
                end=seg.end_ms,
                text=tagged_text,
                style=seg.style_name,
            )
            subs.events.append(event)

    subs.save(str(output_path))
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_captions.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/processors/captions.py tests/test_captions.py
git commit -m "feat(video-editor): ASS caption generation with karaoke and phrase modes"
```

### Task 3: Add burn_captions function + integrate with assembly

**Files:**
- Modify: `src/bee_video_editor/processors/captions.py`
- Modify: `src/bee_video_editor/services/production.py`

- [ ] **Step 1: Add burn_captions to captions.py**

```python
import subprocess


def burn_captions(
    video_path: Path,
    ass_path: Path,
    output_path: Path,
) -> Path:
    """Burn ASS subtitles into video via FFmpeg ass filter.

    This is a post-processing step — runs a second encode pass.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg ass filter needs absolute path with escaped colons
    abs_ass = str(ass_path.resolve()).replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"ass={abs_ass}",
        "-c:a", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg caption burn failed: {result.stderr[:500]}")

    return output_path
```

- [ ] **Step 2: Update init_project to create captions directory**

In `services/production.py`, add `"captions"` to the subdirectory list in `init_project`:

```python
for subdir in ["segments", "normalized", "composited", "graphics", "narration", "captions", "final"]:
```

- [ ] **Step 3: Update assemble_final to burn captions if present**

At the end of `assemble_final()` in `services/production.py`, after the video is assembled, add:

```python
    # Burn in captions if ASS file exists
    captions_path = config.output_dir / "captions" / "captions.ass"
    if output and captions_path.exists():
        from bee_video_editor.processors.captions import burn_captions
        captioned = output.parent / "final_with_captions.mp4"
        try:
            burn_captions(output, captions_path, captioned)
            return captioned
        except RuntimeError:
            pass  # Fall through to return uncaptioned video

    return output
```

- [ ] **Step 4: Run full tests**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/processors/captions.py src/bee_video_editor/services/production.py
git commit -m "feat(video-editor): burn_captions function + assembly integration"
```

### Task 4: Add captions CLI command + API endpoint

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`
- Modify: `src/bee_video_editor/api/routes/production.py`
- Modify: `src/bee_video_editor/api/schemas.py`

- [ ] **Step 1: Add CLI command**

Add to `cli.py`:

```python
@app.command()
def captions(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    precise: bool = typer.Option(False, "--precise", help="Use Whisper for word-level timestamps"),
    caption_style: str = typer.Option("karaoke", "--style", "-s", help="Caption style: karaoke or phrase"),
):
    """Generate ASS captions from storyboard narrator text."""
    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.processors.captions import (
        extract_caption_segments,
        generate_captions_estimated,
    )

    sb = parse_storyboard(storyboard_path)
    segments = extract_caption_segments(sb)

    if not segments:
        console.print("[yellow]No captionable segments found.[/yellow]")
        return

    out_dir = Path(project_dir) / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    console.print(f"[bold]Generating captions ({caption_style}, {len(segments)} segments)...[/bold]")

    if precise:
        console.print("[yellow]Precise mode not yet implemented — falling back to estimated.[/yellow]")

    generate_captions_estimated(segments, out, style=caption_style)
    console.print(f"[green]Captions written to {out}[/green]")
```

- [ ] **Step 2: Add CaptionRequest schema**

Add to `api/schemas.py`:

```python
class CaptionRequest(BaseModel):
    precise: bool = False
    style: str = "karaoke"  # "karaoke" or "phrase"
```

- [ ] **Step 3: Add API endpoint**

Add to `api/routes/production.py`:

```python
@router.post("/captions")
def generate_captions(req: CaptionRequest, session: SessionStore = Depends(get_session)):
    """Generate ASS captions from storyboard."""
    from bee_video_editor.processors.captions import (
        extract_caption_segments,
        generate_captions_estimated,
    )

    storyboard, project_dir = session.require_project()
    segments = extract_caption_segments(storyboard)

    if not segments:
        return {"status": "ok", "count": 0, "message": "No captionable segments found"}

    out_dir = project_dir / "output" / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "captions.ass"

    generate_captions_estimated(segments, out, style=req.style)

    return {"status": "ok", "count": len(segments), "output": str(out)}
```

Add import for `CaptionRequest` at the top of production.py routes:
```python
from bee_video_editor.api.schemas import CaptionRequest, GenerateRequest, ProductionStatusSchema
```

- [ ] **Step 4: Run full tests**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py src/bee_video_editor/api/routes/production.py src/bee_video_editor/api/schemas.py
git commit -m "feat(video-editor): add captions CLI command and API endpoint"
```

---

## Chunk 2: Asset Preflight

### Task 5: Create preflight service + data model + tests

**Files:**
- Create: `src/bee_video_editor/services/preflight.py`
- Create: `tests/test_preflight.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_preflight.py`:

```python
"""Tests for asset preflight scanner."""

import json
import tempfile
from pathlib import Path

import pytest

from bee_video_editor.services.preflight import (
    AssetEntry,
    PreflightReport,
    run_preflight,
)
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def _seg(id, visual_code, qualifier="", layer="visual"):
    """Create a segment with one visual/audio/overlay entry."""
    entries = [LayerEntry(content=qualifier, content_type=visual_code, raw=f"[{visual_code}] {qualifier}")]
    kwargs = {layer: entries}
    return StoryboardSegment(
        id=id, start="0:00", end="0:10", title="TEST",
        section="TEST", section_time="0:00 - 0:10", subsection="",
        **kwargs,
    )


class TestPreflightReport:
    def test_ok_when_no_missing(self):
        report = PreflightReport(total=3, found=3, missing=0, generated=0, needs_check=0, entries=[])
        assert report.ok is True

    def test_not_ok_when_missing(self):
        report = PreflightReport(total=3, found=1, missing=2, generated=0, needs_check=0, entries=[])
        assert report.ok is False


class TestRunPreflight:
    def test_finds_existing_graphics(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            (proj / "output" / "graphics").mkdir(parents=True)
            (proj / "output" / "graphics" / "lower-third-00-test.png").touch()

            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "test name", layer="overlay"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.found >= 1

    def test_reports_missing_footage(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "COURTROOM", "testimony"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.missing >= 1
            missing = [e for e in report.entries if e.status == "missing"]
            assert any(e.visual_code == "COURTROOM" for e in missing)

    def test_broll_is_needs_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "BROLL-DARK", "atmospheric"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.needs_check >= 1

    def test_unsupported_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "TEXT-CHAT", "messages"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            not_supported = [e for e in report.entries if e.status == "not-supported"]
            assert len(not_supported) >= 1

    def test_unknown_code_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "TOTALLY-MADE-UP", "whatever"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            unknown = [e for e in report.entries if e.status == "unknown"]
            assert len(unknown) >= 1

    def test_empty_project_all_missing(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
                _seg("s2", "COURTROOM", "testimony"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.missing == 2
            assert report.found == 0

    def test_json_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "LOWER-THIRD", "name", layer="overlay"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            # Serialize to JSON
            manifest = {
                "total": report.total,
                "found": report.found,
                "missing": report.missing,
                "entries": [
                    {"segment_id": e.segment_id, "visual_code": e.visual_code, "status": e.status}
                    for e in report.entries
                ],
            }
            data = json.dumps(manifest)
            parsed = json.loads(data)
            assert parsed["total"] == report.total

    def test_narration_audio_check(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            (proj / "output" / "narration").mkdir(parents=True)
            (proj / "output" / "narration" / "nar-001-test.mp3").touch()

            sb = Storyboard(title="T", segments=[
                _seg("s1", "NAR", "narrator text", layer="audio"),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.found >= 1

    def test_persistent_modifiers_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            sb = Storyboard(title="T", segments=[
                _seg("s1", "COLOR-GRADE", "dark_crime"),
                _seg("s2", "TR-FADE", ""),
                _seg("s3", "VIGNETTE", ""),
            ], production_rules=ProductionRules())

            report = run_preflight(sb, proj)
            assert report.total == 0  # All excluded
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_preflight.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement preflight service**

Create `src/bee_video_editor/services/preflight.py`:

```python
"""Asset preflight scanner — checks storyboard requirements against project files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.models_storyboard import Storyboard


@dataclass
class AssetEntry:
    """A single asset requirement from one segment."""
    segment_id: str
    layer: str
    visual_code: str
    qualifier: str
    status: str  # "found", "missing", "needs-check", "not-supported", "unknown"
    file_path: str | None = None


@dataclass
class PreflightReport:
    """Result of scanning a storyboard against project assets."""
    total: int = 0
    found: int = 0
    missing: int = 0
    generated: int = 0
    needs_check: int = 0
    entries: list[AssetEntry] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.missing == 0


# Resolution rules: visual_code → (directory, glob_pattern, default_status_if_missing)
RESOLUTION_RULES: dict[str, tuple[str, str, str]] = {
    # Generated graphics
    "LOWER-THIRD": ("output/graphics", "lower-third-*.png", "missing"),
    "TIMELINE-MARKER": ("output/graphics", "timeline-*.png", "missing"),
    "FINANCIAL-CARD": ("output/graphics", "financial-*.png", "missing"),
    "MUGSHOT-CARD": ("output/graphics", "mugshot-*.png", "missing"),
    "QUOTE-CARD": ("output/graphics", "quote-*.png", "missing"),
    "BRAND-STING": ("output/graphics", "brand-*", "missing"),
    "DISCLAIMER": ("output/graphics", "disclaimer-*", "missing"),
    # Source footage
    "COURTROOM": ("footage", "trial-*.mp4", "missing"),
    "BODYCAM": ("footage", "bodycam-*.mp4", "missing"),
    "INTERROGATION": ("footage", "interrogation-*.mp4", "missing"),
    "WAVEFORM-AERIAL": ("output/segments", "*.mp4", "missing"),
    "WAVEFORM-DARK": ("output/segments", "*.mp4", "missing"),
    # Photos
    "PIP-SINGLE": ("photos", "pip-*.png", "missing"),
    "PIP-DUAL": ("photos", "pip-*.png", "missing"),
    # Maps
    "MAP-FLAT": ("maps", "map-*", "missing"),
    "MAP-3D": ("maps", "map-*", "missing"),
    "MAP-TACTICAL": ("maps", "map-*", "missing"),
    "MAP-PULSE": ("maps", "map-*", "missing"),
    "MAP-ROUTE": ("maps", "map-*", "missing"),
    # Stock (can't match qualifier)
    "BROLL-DARK": ("stock", "*.mp4", "needs-check"),
    # Audio
    "NAR": ("output/narration", "nar-*.mp3", "missing"),
}

NOT_SUPPORTED_CODES = {
    "DOCUMENT-MOCKUP", "TEXT-CHAT", "SOCIAL-POST", "NEWS-MONTAGE",
    "EVIDENCE-BOARD", "FLOW-DIAGRAM", "TIMELINE-SEQUENCE",
    "POLICE-DB", "DESKTOP-PHOTOS", "EVIDENCE-CLOSEUP",
    "EVIDENCE-DISPLAY", "BODY-DIAGRAM", "SPLIT-INFO", "TRAILER",
}

PERSISTENT_MODIFIERS = {
    "COLOR-GRADE", "VIGNETTE", "LETTERBOX", "CAPTION-ANIMATED", "STILL",
}


def _is_modifier(code: str) -> bool:
    """Check if code is a persistent modifier or transition (not an asset)."""
    return code in PERSISTENT_MODIFIERS or code.startswith("TR-")


def run_preflight(storyboard: Storyboard, project_dir: Path) -> PreflightReport:
    """Scan storyboard against project assets and report gaps."""
    report = PreflightReport()

    for seg in storyboard.segments:
        for layer_name in ("visual", "audio", "overlay"):
            layer_entries = getattr(seg, layer_name, [])
            for entry in layer_entries:
                code = entry.content_type
                qualifier = entry.content

                # Skip persistent modifiers and transitions
                if _is_modifier(code) or code == "UNKNOWN":
                    continue

                report.total += 1

                if code in NOT_SUPPORTED_CODES:
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="not-supported",
                    ))
                    continue

                if code not in RESOLUTION_RULES:
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="unknown",
                    ))
                    continue

                subdir, pattern, default_status = RESOLUTION_RULES[code]
                search_dir = project_dir / subdir
                found_files = list(search_dir.glob(pattern)) if search_dir.exists() else []

                if found_files:
                    report.found += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="found",
                        file_path=str(found_files[0]),
                    ))
                elif default_status == "needs-check":
                    report.needs_check += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="needs-check",
                    ))
                else:
                    report.missing += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="missing",
                    ))

    return report
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_preflight.py -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/preflight.py tests/test_preflight.py
git commit -m "feat(video-editor): asset preflight scanner with resolution rules for all visual codes"
```

### Task 6: Add preflight CLI command + API endpoint + JSON manifest

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`
- Modify: `src/bee_video_editor/api/routes/production.py`
- Modify: `src/bee_video_editor/api/schemas.py`

- [ ] **Step 1: Add CLI command**

Add to `cli.py`:

```python
@app.command()
def preflight(
    storyboard_path: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
):
    """Check which assets are ready and which are missing."""
    from rich.table import Table

    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.services.preflight import run_preflight

    sb = parse_storyboard(storyboard_path)
    proj = Path(project_dir)
    report = run_preflight(sb, proj)

    table = Table(title="Asset Preflight Report")
    table.add_column("Segment", style="dim")
    table.add_column("Layer")
    table.add_column("Code")
    table.add_column("Qualifier", max_width=40)
    table.add_column("Status")
    table.add_column("File", max_width=50)

    status_colors = {
        "found": "green",
        "missing": "red",
        "needs-check": "yellow",
        "not-supported": "dim",
        "unknown": "magenta",
    }

    for entry in report.entries:
        color = status_colors.get(entry.status, "white")
        table.add_row(
            entry.segment_id,
            entry.layer,
            entry.visual_code,
            entry.qualifier[:40],
            f"[{color}]{entry.status}[/{color}]",
            entry.file_path or "",
        )

    console.print(table)
    console.print(
        f"\n[bold]{report.total} assets:[/bold] "
        f"[green]{report.found} found[/green], "
        f"[red]{report.missing} missing[/red], "
        f"[yellow]{report.needs_check} need check[/yellow]"
    )

    # Write JSON manifest
    import json
    from dataclasses import asdict
    manifest_dir = proj / "output"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "asset-manifest.json"
    manifest = {
        "total": report.total,
        "found": report.found,
        "missing": report.missing,
        "generated": report.generated,
        "needs_check": report.needs_check,
        "entries": [asdict(e) for e in report.entries],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    console.print(f"\n[dim]Manifest written to {manifest_path}[/dim]")
```

- [ ] **Step 2: Add API schemas**

Add to `api/schemas.py`:

```python
class AssetEntrySchema(BaseModel):
    segment_id: str
    layer: str
    visual_code: str
    qualifier: str
    status: str
    file_path: str | None = None


class PreflightReportSchema(BaseModel):
    total: int
    found: int
    missing: int
    generated: int
    needs_check: int
    entries: list[AssetEntrySchema]
```

- [ ] **Step 3: Add API endpoint**

Add to `api/routes/production.py`:

```python
@router.get("/preflight")
def get_preflight(session: SessionStore = Depends(get_session)):
    """Run asset preflight check against loaded project."""
    from bee_video_editor.services.preflight import run_preflight

    storyboard, project_dir = session.require_project()
    report = run_preflight(storyboard, project_dir)

    return {
        "total": report.total,
        "found": report.found,
        "missing": report.missing,
        "generated": report.generated,
        "needs_check": report.needs_check,
        "entries": [
            {
                "segment_id": e.segment_id,
                "layer": e.layer,
                "visual_code": e.visual_code,
                "qualifier": e.qualifier,
                "status": e.status,
                "file_path": e.file_path,
            }
            for e in report.entries
        ],
    }
```

- [ ] **Step 4: Run full tests**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py src/bee_video_editor/api/routes/production.py src/bee_video_editor/api/schemas.py
git commit -m "feat(video-editor): add preflight CLI command and API endpoint with JSON manifest"
```

### Task 7: Final verification

- [ ] **Step 1: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev --extra web pytest tests/ -v`
Expected: All tests pass (128 existing + ~17 new ≈ 145+)

- [ ] **Step 2: Verify new CLI commands exist**

Run: `cd bee-content/video-editor && uv run bee-video --help`
Expected: `captions` and `preflight` appear in the command list

- [ ] **Step 3: Fix time estimate in docs**

In `bee-content/video-editor/ROADMAP.md`, check off the "Asset generation time estimate" item. In `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`, update the production checklist time from "3-4 hours" to "6-8 hours" for Asset Generation.

- [ ] **Step 4: Push**

```bash
git push
```
