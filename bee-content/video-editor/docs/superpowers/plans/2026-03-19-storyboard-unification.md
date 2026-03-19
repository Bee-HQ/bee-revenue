# Storyboard Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make storyboard the single source of truth — absorb assembly guide features, switch remaining CLI commands, drop the conversion bridge, deprecate legacy code.

**Architecture:** Add header metadata + checklists to storyboard model/parser. Rewrite `init_project()` for storyboard. Rewrite `trim_source_footage()` to use source layers. Switch 6 CLI commands from `parse_assembly_guide()` to `parse_storyboard()`. Remove `_ensure_storyboard()` bridge, `converters.py`, and all assembly guide imports from services.

**Tech Stack:** Python stdlib dataclasses, existing parsers/models pattern. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-03-19-storyboard-unification-design.md`

---

### Task 1: Add `ChecklistItem` model and metadata fields to `Storyboard`

**Files:**
- Modify: `src/bee_video_editor/models_storyboard.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write tests for new model fields**

Append to `tests/test_models.py`:

```python
from bee_video_editor.models_storyboard import ChecklistItem, Storyboard


def test_checklist_item():
    item = ChecklistItem(text="Generate TTS", checked=False, category="audio")
    assert item.text == "Generate TTS"
    assert item.checked is False
    assert item.category == "audio"


def test_storyboard_metadata_defaults():
    sb = Storyboard(title="Test")
    assert sb.total_duration is None
    assert sb.resolution is None
    assert sb.format is None
    assert sb.pre_production == []
    assert sb.post_checklist == []


def test_storyboard_with_metadata():
    sb = Storyboard(
        title="Test",
        total_duration="~55 minutes",
        resolution="1080p",
        format="MP4 (H.264 + AAC)",
        pre_production=[ChecklistItem("TTS", False, "audio")],
        post_checklist=[ChecklistItem("Color check", True, "post")],
    )
    assert sb.total_duration == "~55 minutes"
    assert sb.resolution == "1080p"
    assert len(sb.pre_production) == 1
    assert sb.post_checklist[0].checked is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_models.py::test_checklist_item -v`
Expected: FAIL — `ImportError: cannot import name 'ChecklistItem'`

- [ ] **Step 3: Add ChecklistItem and new fields to Storyboard**

In `src/bee_video_editor/models_storyboard.py`, add before `StoryboardSegment`:

```python
@dataclass
class ChecklistItem:
    """A checklist item from pre-production or post-assembly sections."""
    text: str
    checked: bool
    category: str  # "audio", "graphics", "maps", "post"
```

Add new fields to `Storyboard` class (after `title`, before `segments`):

```python
@dataclass
class Storyboard:
    """A complete storyboard parsed from markdown."""
    title: str
    total_duration: str | None = None
    resolution: str | None = None
    format: str | None = None
    pre_production: list[ChecklistItem] = field(default_factory=list)
    post_checklist: list[ChecklistItem] = field(default_factory=list)
    segments: list[StoryboardSegment] = field(default_factory=list)
    # ... rest unchanged
```

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_models.py -v`
Expected: All PASS

- [ ] **Step 5: Run full suite to verify no regressions**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All existing tests PASS (new fields default to None/[])

- [ ] **Step 6: Commit**

```bash
git add src/bee_video_editor/models_storyboard.py tests/test_models.py
git commit -m "add ChecklistItem model and metadata fields to Storyboard"
```

---

### Task 2: Parse header metadata, pre-production, and post-assembly from storyboard

**Files:**
- Modify: `src/bee_video_editor/parsers/storyboard.py`
- Test: `tests/test_storyboard_parser.py`

- [ ] **Step 1: Write tests for header metadata parsing**

Append to `tests/test_storyboard_parser.py`:

```python
class TestParseMetadata:
    """Test parsing of header metadata, pre-production, and post-assembly."""

    METADATA_STORYBOARD = textwrap.dedent("""\
    # Shot-by-Shot Storyboard: "Test Video"

    **Total Duration:** ~55 minutes
    **Resolution:** 1080p
    **Format:** MP4 (H.264 + AAC)

    **Legend:**
    - `FOOTAGE:` = Real clip

    ---

    ## COLD OPEN (0:00 - 0:30)

    ### 0:00 - 0:10 | TEST SEGMENT
    | Layer | Content |
    |-------|---------|
    | Visual | `FOOTAGE:` Test footage |
    """)

    def test_header_metadata(self, tmp_path):
        sb_file = tmp_path / "storyboard.md"
        sb_file.write_text(self.METADATA_STORYBOARD)
        sb = parse_storyboard(str(sb_file))
        assert sb.total_duration == "~55 minutes"
        assert sb.resolution == "1080p"
        assert sb.format == "MP4 (H.264 + AAC)"

    def test_missing_metadata_defaults_to_none(self, tmp_path):
        sb_file = tmp_path / "storyboard.md"
        sb_file.write_text("# Storyboard: \"No metadata\"\n\n## SECTION (0:00 - 0:10)\n\n### 0:00 - 0:10 | TEST\n| Layer | Content |\n|---|---|\n| Visual | `FOOTAGE:` test |\n")
        sb = parse_storyboard(str(sb_file))
        assert sb.total_duration is None
        assert sb.resolution is None
        assert sb.format is None
```

- [ ] **Step 2: Write tests for pre-production parsing**

```python
    PRE_PROD_STORYBOARD = textwrap.dedent("""\
    # Storyboard: "Test"

    ## PRE-PRODUCTION

    ### Audio
    - [ ] Generate TTS narration
    - [x] Select background music

    ### Graphics
    - [ ] Lower thirds for 10 characters

    ---

    ## COLD OPEN (0:00 - 0:10)

    ### 0:00 - 0:10 | TEST
    | Layer | Content |
    |-------|---------|
    | Visual | `FOOTAGE:` test |
    """)

    def test_pre_production_parsing(self, tmp_path):
        sb_file = tmp_path / "storyboard.md"
        sb_file.write_text(self.PRE_PROD_STORYBOARD)
        sb = parse_storyboard(str(sb_file))
        assert len(sb.pre_production) == 3
        assert sb.pre_production[0].text == "Generate TTS narration"
        assert sb.pre_production[0].checked is False
        assert sb.pre_production[0].category == "audio"
        assert sb.pre_production[1].text == "Select background music"
        assert sb.pre_production[1].checked is True
        assert sb.pre_production[2].category == "graphics"
```

- [ ] **Step 3: Write tests for post-assembly parsing**

```python
    POST_STORYBOARD = textwrap.dedent("""\
    # Storyboard: "Test"

    ## COLD OPEN (0:00 - 0:10)

    ### 0:00 - 0:10 | TEST
    | Layer | Content |
    |-------|---------|
    | Visual | `FOOTAGE:` test |

    ---

    ## POST-ASSEMBLY

    - [ ] Color grade consistency pass
    - [x] Audio levels check
    """)

    def test_post_assembly_parsing(self, tmp_path):
        sb_file = tmp_path / "storyboard.md"
        sb_file.write_text(self.POST_STORYBOARD)
        sb = parse_storyboard(str(sb_file))
        assert len(sb.post_checklist) == 2
        assert sb.post_checklist[0].text == "Color grade consistency pass"
        assert sb.post_checklist[0].checked is False
        assert sb.post_checklist[0].category == "post"
        assert sb.post_checklist[1].checked is True
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_storyboard_parser.py::TestParseMetadata -v`
Expected: FAIL

- [ ] **Step 5: Implement parser functions**

In `src/bee_video_editor/parsers/storyboard.py`, add three functions:

```python
def _parse_header_metadata(lines: list[str]) -> dict:
    """Extract **Key:** value metadata from lines before first ## section."""
    metadata = {}
    key_map = {
        "total duration": "total_duration",
        "resolution": "resolution",
        "format": "format",
    }
    for line in lines:
        if line.strip().startswith("## "):
            break
        match = re.match(r'\*\*([^*]+):\*\*\s*(.*)', line.strip())
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            if key in key_map and value:
                metadata[key_map[key]] = value
    return metadata


def _parse_checklists(lines: list[str], section_header: str, default_category: str = "") -> list:
    """Parse checkbox items from a markdown section.

    Returns list of (text, checked, category) tuples.
    """
    from bee_video_editor.models_storyboard import ChecklistItem

    items = []
    in_section = False
    category = default_category

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## ") and section_header.upper() in stripped.upper():
            in_section = True
            continue

        if in_section and stripped.startswith("## "):
            break  # Hit next top-level section

        if in_section and stripped.startswith("---"):
            break

        if in_section and stripped.startswith("### "):
            category = stripped.lstrip("# ").strip().lower()
            continue

        if not in_section:
            continue

        # Match checkbox: - [ ] text or - [x] text
        checkbox_match = re.match(r'^- \[([ xX])\]\s+(.*)', stripped)
        if checkbox_match:
            checked = checkbox_match.group(1).lower() == "x"
            text = checkbox_match.group(2).strip()
            items.append(ChecklistItem(text=text, checked=checked, category=category))

    return items
```

Update `parse_storyboard()` to call these and populate the new fields:

```python
def parse_storyboard(path: str | Path) -> Storyboard:
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")

    # Parse header metadata
    metadata = _parse_header_metadata(lines)

    storyboard = Storyboard(
        title=_extract_title(lines),
        total_duration=metadata.get("total_duration"),
        resolution=metadata.get("resolution"),
        format=metadata.get("format"),
    )

    # Parse segments (existing code)
    storyboard.segments = _parse_segments(lines)
    storyboard.stock_footage = _parse_stock_footage(lines)
    storyboard.photos_needed = _parse_photos(lines)
    storyboard.maps_needed = _parse_maps(lines)
    storyboard.production_rules = _parse_production_rules(lines)

    # Parse checklists (NEW)
    storyboard.pre_production = _parse_checklists(lines, "PRE-PRODUCTION")
    storyboard.post_checklist = _parse_checklists(lines, "POST-ASSEMBLY", default_category="post")

    logger.info(...)  # existing log line
    return storyboard
```

- [ ] **Step 6: Run tests**

Run: `uv run --extra dev pytest tests/test_storyboard_parser.py -v`
Expected: All PASS including new TestParseMetadata tests

- [ ] **Step 7: Run full suite**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/bee_video_editor/parsers/storyboard.py tests/test_storyboard_parser.py
git commit -m "parse header metadata, pre-production, and post-assembly from storyboard"
```

---

### Task 3: Rewrite `init_project()` for storyboard and rename `ProductionState.assembly_guide_path`

**Files:**
- Modify: `src/bee_video_editor/services/production.py:118-201`
- Test: `tests/test_production.py`

- [ ] **Step 1: Write test for storyboard-based init**

```python
def test_init_project_from_storyboard(tmp_path):
    """init_project works with a storyboard file."""
    from bee_video_editor.services.production import ProductionConfig, init_project

    sb_content = textwrap.dedent("""\
    # Storyboard: "Test"

    **Resolution:** 1080p

    ## SECTION (0:00 - 0:20)

    ### 0:00 - 0:10 | SEGMENT ONE
    | Layer | Content |
    |-------|---------|
    | Visual | `FOOTAGE:` test.mp4 |
    | Audio | `NAR:` "Hello world" |
    | Source | `footage/test.mp4` trim 0:00-0:10 |

    ### 0:10 - 0:20 | SEGMENT TWO
    | Layer | Content |
    |-------|---------|
    | Visual | `STOCK:` aerial shot |
    | Audio | `REAL AUDIO:` interview |
    """)
    sb_file = tmp_path / "storyboard.md"
    sb_file.write_text(sb_content)

    config = ProductionConfig(project_dir=tmp_path)
    storyboard, state = init_project(str(sb_file), config)

    assert storyboard.title == 'Test'
    assert len(state.segment_statuses) == 2
    assert state.storyboard_path == str(sb_file)
    assert state.segment_statuses[0].segment_type == "MIX"  # FOOTAGE + NAR
    assert state.segment_statuses[1].segment_type == "REAL"  # REAL AUDIO
    assert (config.output_dir / "segments").exists()
```

- [ ] **Step 2: Write test for ProductionState backward compat**

```python
def test_production_state_loads_old_format(tmp_path):
    """ProductionState.load() reads old assembly_guide_path field."""
    state_file = tmp_path / "state.json"
    state_file.write_text('{"assembly_guide_path": "/old/path.md", "phase": "init", "segment_statuses": []}')

    from bee_video_editor.services.production import ProductionState
    state = ProductionState.load(state_file)
    assert state.storyboard_path == "/old/path.md"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_production.py::test_init_project_from_storyboard -v`
Expected: FAIL

- [ ] **Step 4: Rename ProductionState field and add backward compat**

In `src/bee_video_editor/services/production.py`:

```python
@dataclass
class ProductionState:
    """Persistent state for a production run."""
    storyboard_path: str = ""  # renamed from assembly_guide_path
    segment_statuses: list[SegmentStatus] = field(default_factory=list)
    phase: str = "init"

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> ProductionState:
        with open(path) as f:
            data = json.load(f)
        state = cls(
            storyboard_path=data.get("storyboard_path", data.get("assembly_guide_path", "")),
            phase=data["phase"],
        )
        state.segment_statuses = [
            SegmentStatus(**s) for s in data.get("segment_statuses", [])
        ]
        return state
    # ... track() unchanged
```

- [ ] **Step 5: Add segment type derivation helper**

```python
def _derive_segment_type(seg: StoryboardSegment) -> str:
    """Derive a production segment type from storyboard layers."""
    has_footage = any(e.content_type in ("FOOTAGE",) for e in seg.visual)
    has_nar = any(e.content_type == "NAR" for e in seg.audio)
    has_real_audio = any(e.content_type == "REAL AUDIO" for e in seg.audio)
    has_gen_visual = any(e.content_type in ("GRAPHIC", "MAP", "STOCK", "WAVEFORM") for e in seg.visual)

    if has_footage and has_nar:
        return "MIX"
    if has_footage or has_real_audio:
        return "REAL"
    if has_nar:
        return "NAR"
    if has_gen_visual:
        return "GEN"
    return "GEN"
```

- [ ] **Step 6: Rewrite init_project()**

```python
def init_project(
    storyboard_path: str | Path,
    config: ProductionConfig,
) -> tuple[Storyboard, ProductionState]:
    """Initialize a production project from a storyboard."""
    from bee_video_editor.parsers.storyboard import parse_storyboard

    storyboard = parse_storyboard(storyboard_path)

    state = ProductionState(
        storyboard_path=str(storyboard_path),
        phase="parsed",
    )
    state.segment_statuses = [
        SegmentStatus(
            index=i,
            time_range=f"{seg.start}-{seg.end}",
            segment_type=_derive_segment_type(seg),
        )
        for i, seg in enumerate(storyboard.segments)
    ]

    for subdir in ["segments", "normalized", "composited", "graphics", "narration", "captions", "final", "previews"]:
        (config.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    state.save(config.state_path)
    return storyboard, state
```

- [ ] **Step 7: Run tests**

Run: `uv run --extra dev pytest tests/test_production.py -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "rewrite init_project for storyboard, rename ProductionState.assembly_guide_path"
```

---

### Task 4: Rewrite `trim_source_footage()` for storyboard source layers

**Files:**
- Modify: `src/bee_video_editor/services/production.py:371-410`
- Test: `tests/test_production.py`

- [ ] **Step 1: Write test for source layer trim parsing**

```python
def test_trim_from_storyboard_source_layers(tmp_path):
    """trim_source_footage extracts trim info from storyboard source layers."""
    from bee_video_editor.services.production import _parse_trim_from_source

    # With trim info
    path, start, end = _parse_trim_from_source("`footage/test.mp4` trim 0:00-0:10")
    assert path == "footage/test.mp4"
    assert start == "0:00"
    assert end == "0:10"

    # Without trim info
    path, start, end = _parse_trim_from_source("`footage/test.mp4`")
    assert path == "footage/test.mp4"
    assert start is None
    assert end is None

    # Without backticks
    path, start, end = _parse_trim_from_source("footage/test.mp4 trim 1:30-2:00")
    assert path == "footage/test.mp4"
    assert start == "1:30"
    assert end == "2:00"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --extra dev pytest tests/test_production.py::test_trim_from_storyboard_source_layers -v`
Expected: FAIL

- [ ] **Step 3: Implement `_parse_trim_from_source()` and rewrite `trim_source_footage()`**

```python
def _parse_trim_from_source(content: str) -> tuple[str, str | None, str | None]:
    """Parse a source layer content string into (file_path, start, end).

    Handles formats:
        `footage/test.mp4` trim 0:00-0:10
        footage/test.mp4 trim 0:00-0:10
        `footage/test.mp4`
    """
    # Strip backticks
    text = content.strip().replace("`", "")

    # Check for trim directive
    trim_match = re.match(r'(.+?)\s+trim\s+(\d+:\d+)-(\d+:\d+)', text)
    if trim_match:
        return trim_match.group(1).strip(), trim_match.group(2), trim_match.group(3)

    return text.strip(), None, None


def trim_source_footage(
    project: Storyboard,
    config: ProductionConfig,
    state: ProductionState | None = None,
) -> ProductionResult:
    """Trim source footage based on storyboard source layers."""
    result = ProductionResult()
    segments_dir = config.output_dir / "segments"

    if state:
        state.phase = "trimming"
        state.save(config.state_path)

    for seg in project.segments:
        for layer in seg.source:
            file_path, start, end = _parse_trim_from_source(layer.content)
            if not file_path or not start or not end:
                continue

            # Resolve file path relative to project dir
            source = config.project_dir / file_path
            if not source.exists() and config.footage_dir:
                source = config.footage_dir / file_path.replace("footage/", "")

            if not source.exists():
                # Try glob pattern
                matches = globmod.glob(str(config.project_dir / file_path))
                if not matches:
                    result.failed.append(FailedItem(path=file_path, error="Source file not found"))
                    continue
                source = Path(matches[0])

            slug = _slugify(seg.title)[:40]
            out = segments_dir / f"trim-{slug}-{seg.id}.mp4"
            if out.exists():
                result.skipped.append(str(out))
            else:
                try:
                    trim(source, out, start=start, end=end)
                    result.succeeded.append(out)
                except Exception as e:
                    result.failed.append(FailedItem(path=str(out), error=str(e)))

    return result
```

Note: The function signature changes from `Project | Storyboard` to `Storyboard` only. The `isinstance(project, Storyboard): return result` early return is removed.

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_production.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/test_production.py
git commit -m "rewrite trim_source_footage for storyboard source layers"
```

---

### Task 5: Drop `Project | Storyboard` union — services accept `Storyboard` only

**Files:**
- Modify: `src/bee_video_editor/services/production.py`

- [ ] **Step 1: Remove `_ensure_storyboard()` and converter import**

Remove these lines from `production.py`:
- `from bee_video_editor.converters import assembly_guide_to_storyboard` (line 12)
- `from bee_video_editor.parsers.assembly_guide import parse_assembly_guide` (line 15)
- `from bee_video_editor.models import Project, ...` (line 14 — keep only if other models from it are used; likely remove entirely)
- The `_ensure_storyboard()` function (lines 165-169)

- [ ] **Step 2: Update function signatures**

Change all `project: Project | Storyboard` parameters to `project: Storyboard`:

- `generate_graphics_for_project(project: Storyboard, ...)` — remove `sb = _ensure_storyboard(project)`, use `project` directly (or rename param to `storyboard`)
- `generate_narration_for_project(project: Storyboard, ...)` — same
- `rough_cut_export(project: Storyboard, ...)` — same

Also remove `_extract_narrator_text()` if it exists and is dead code (assembly guide era helper).

- [ ] **Step 3: Run full test suite**

Run: `uv run --extra dev pytest tests/ -v`
Expected: Most tests PASS. Some tests in `test_production.py` and `test_converters.py` may fail if they pass `Project` objects to service functions — those will be addressed in the next task.

- [ ] **Step 4: Fix any failing tests**

Update test fixtures that pass `Project` to services to use `Storyboard` instead. If `test_converters.py` tests the converter independently, it can stay (converter is being deprecated, not deleted yet).

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/production.py tests/
git commit -m "services accept Storyboard only, remove _ensure_storyboard bridge"
```

---

### Task 6: Switch 6 legacy CLI commands to storyboard parser

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py:19-251,1015-1017`

- [ ] **Step 1: Rewrite `parse` command**

```python
@app.command()
def parse(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
):
    """Parse a storyboard and show project summary."""
    from bee_video_editor.parsers.storyboard import parse_storyboard

    sb = parse_storyboard(storyboard)
    summary = sb.summary()

    console.print(f"\n[bold]{sb.title}[/bold]")
    if sb.total_duration:
        console.print(f"Duration: {sb.total_duration}", end="")
        if sb.resolution:
            console.print(f" | {sb.resolution}", end="")
        if sb.format:
            console.print(f" | {sb.format}", end="")
        console.print()
    console.print(f"Total segments: {summary['total_segments']}")
    console.print()

    # Visual type breakdown
    table = Table(title="Visual Types")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    for vtype, count in summary["visual_type_counts"].items():
        table.add_row(vtype, str(count))
    console.print(table)

    # Sections
    console.print("\n[bold]Sections:[/bold]")
    for section in summary["sections"]:
        seg_count = len(sb.segments_in_section(section))
        console.print(f"  {section} ({seg_count} segments)")

    # Pre-production
    if sb.pre_production:
        done = sum(1 for p in sb.pre_production if p.checked)
        console.print(f"\n[bold]Pre-production:[/bold] {done}/{len(sb.pre_production)} items done")

    # Post-assembly
    if sb.post_checklist:
        done = sum(1 for p in sb.post_checklist if p.checked)
        console.print(f"[bold]Post-assembly:[/bold] {done}/{len(sb.post_checklist)} checklist items done")

    # Asset needs
    console.print(f"\n[bold]Assets needed:[/bold]")
    console.print(f"  Stock footage: {summary['stock_footage_needed']}")
    console.print(f"  Photos: {summary['photos_needed']}")
    console.print(f"  Maps: {summary['maps_needed']}")
    console.print()
```

- [ ] **Step 2: Rewrite `segments` command**

```python
@app.command()
def segments(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    section: str | None = typer.Option(None, "--section", "-s", help="Filter by section name"),
    content_type: str | None = typer.Option(None, "--type", "-t", help="Filter by content type (FOOTAGE/STOCK/NAR/GRAPHIC/...)"),
):
    """List all segments from the storyboard."""
    from bee_video_editor.parsers.storyboard import parse_storyboard

    sb = parse_storyboard(storyboard)
    segs = sb.segments

    if section:
        segs = [s for s in segs if section.lower() in s.section.lower()]
    if content_type:
        ct = content_type.upper()
        segs = [s for s in segs if any(
            e.content_type == ct
            for layer_list in s.all_layers.values()
            for e in layer_list
        )]

    table = Table(title=f"Segments ({len(segs)} total)")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Time", style="cyan")
    table.add_column("Dur", justify="right")
    table.add_column("Section")
    table.add_column("Title")
    table.add_column("Visuals", max_width=40, overflow="ellipsis")

    for i, seg in enumerate(segs):
        visual_types = ", ".join(e.content_type for e in seg.visual)
        table.add_row(
            str(i),
            f"{seg.start}-{seg.end}",
            f"{seg.duration_seconds}s",
            seg.subsection or seg.section,
            seg.title,
            visual_types,
        )

    console.print(table)
```

- [ ] **Step 3: Rewrite `init` command**

```python
@app.command()
def init(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Project root directory"),
    tts_engine: str = typer.Option("edge", "--tts", help="TTS engine"),
):
    """Initialize a production project from a storyboard."""
    from bee_video_editor.services.production import ProductionConfig, init_project

    config = ProductionConfig(project_dir=Path(project_dir), tts_engine=tts_engine)
    sb, state = init_project(storyboard, config)

    console.print(f"\n[bold green]Project initialized![/bold green]")
    console.print(f"Title: {sb.title}")
    console.print(f"Segments: {sb.total_segments}")
    console.print(f"Output: {config.output_dir}")
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print("  bee-video graphics <storyboard>  — Generate graphics assets")
    console.print("  bee-video narration <storyboard>  — Generate TTS narration")
    console.print("  bee-video trim-footage <storyboard> — Trim source footage")
    console.print("  bee-video assemble               — Final assembly")
```

- [ ] **Step 4: Rewrite `graphics`, `narration`, `trim_footage` commands**

Change all three to use `parse_storyboard()` instead of `_load_project()`. The argument name changes from `assembly_guide` to `storyboard`. Example for `graphics`:

```python
@app.command()
def graphics(
    storyboard: str = typer.Argument(..., help="Path to storyboard markdown file"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    animated: bool = typer.Option(False, "--animated"),
):
    """Generate all graphics assets."""
    from bee_video_editor.parsers.storyboard import parse_storyboard
    from bee_video_editor.services.production import ProductionConfig, generate_graphics_for_project

    config = ProductionConfig(project_dir=Path(project_dir))
    sb = parse_storyboard(storyboard)
    # ... rest same, replace `project` with `sb`
```

Apply same pattern to `narration` and `trim_footage`.

- [ ] **Step 5: Remove `_load_project()` helper**

Delete the `_load_project()` function at the bottom of cli.py (lines 1015-1017).

- [ ] **Step 6: Update app help text**

Change `help="AI-assisted video production from assembly guides."` to `help="AI-assisted video production from storyboards."` on the typer app or callback.

- [ ] **Step 7: Run full test suite**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "switch 6 legacy CLI commands from assembly guide to storyboard parser"
```

---

### Task 7: Deprecate legacy code and clean up imports

**Files:**
- Modify: `src/bee_video_editor/services/production.py` (remove any remaining assembly guide imports)
- Modify: `src/bee_video_editor/adapters/dashboard.py` (add deprecation warning)
- Remove: `src/bee_video_editor/converters.py`

- [ ] **Step 1: Verify no remaining assembly guide imports in services**

Search for `parse_assembly_guide`, `from bee_video_editor.models import`, `from bee_video_editor.converters import` in `production.py`. Remove any that remain.

- [ ] **Step 2: Remove converters.py**

```bash
git rm src/bee_video_editor/converters.py
```

- [ ] **Step 3: Add deprecation notice to dashboard.py**

Add at the top of the file:

```python
import warnings
warnings.warn(
    "dashboard.py is deprecated. Use the web editor (bee-video serve) instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

- [ ] **Step 4: Handle test_converters.py**

Either delete `tests/test_converters.py` or skip all tests with a comment:

```bash
git rm tests/test_converters.py
```

- [ ] **Step 5: Run full test suite**

Run: `uv run --extra dev pytest tests/ -v`
Expected: All PASS (converter tests removed, no remaining assembly guide imports in production code path)

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "deprecate assembly guide code, remove converters.py"
```

---

### Task 8: Update storyboard.md with new sections

**Files:**
- Modify: `../discovery/true-crime/cases/alex-murdaugh/storyboard.md`

- [ ] **Step 1: Add header metadata after title**

Add after the title line, before the Legend:

```markdown
**Total Duration:** ~55 minutes
**Resolution:** 1080p
**Format:** MP4 (H.264 + AAC)
```

- [ ] **Step 2: Add pre-production section**

Add after the legend and `---`, before the first `## COLD OPEN`:

```markdown
## PRE-PRODUCTION

### Audio
- [ ] Generate full narrator voiceover from screenplay (TTS)
- [ ] Select/generate dark ambient background music (MusicGen or licensed)
- [ ] Normalize all audio to -14 LUFS (YouTube standard)

### Graphics
- [ ] Lower thirds for 15+ characters
- [ ] Timeline markers (date stamps)
- [ ] Financial amount overlays ($792K, $4.3M, $8.8M, $12M)
- [ ] Key quote overlays
- [ ] Case status graphic (charges + sentences)

### Maps
- [ ] Lowcountry SC region with 5 counties highlighted
- [ ] Moselle property aerial zoom-in
- [ ] Archers Creek Bridge (boat crash location)
- [ ] Walterboro courthouse
- [ ] Route from Moselle to Almeda (mother's house)

---
```

- [ ] **Step 3: Add post-assembly section at the end**

Add after `## PRODUCTION RULES`:

```markdown
---

## POST-ASSEMBLY

- [ ] Color grade consistency pass across all segments
- [ ] Audio levels check (-14 LUFS narrator, -30 LUFS music bed)
- [ ] Transition timing review (0.5-1s dissolves, hard cuts for impact)
- [ ] Background music continuity check
- [ ] Thumbnail generation
- [ ] Export at 1080p H.264 + AAC
```

- [ ] **Step 4: Verify parser handles the updated file**

Run: `uv run bee-video parse ../discovery/true-crime/cases/alex-murdaugh/storyboard.md`
Expected: Shows title, duration, resolution, format, pre-production status, segments, etc.

- [ ] **Step 5: Commit**

```bash
git add ../discovery/true-crime/cases/alex-murdaugh/storyboard.md
git commit -m "add header metadata, pre-production, and post-assembly sections to storyboard"
```

---

### Task 9: Update documentation

**Files:**
- Modify: `CLAUDE.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update CLAUDE.md**

- Remove or update the "Two Parser Problem" section (if it exists in the current CLAUDE.md) — storyboard is now the only format
- Update CLI command references from `assembly_guide` to `storyboard`
- Note that assembly guide format is deprecated

- [ ] **Step 2: Update CHANGELOG.md under [Unreleased]**

Add:

```markdown
### Changed

- **Storyboard is now the single source of truth** — all CLI commands use storyboard format
- `init_project()` accepts storyboard path instead of assembly guide
- `trim_source_footage()` reads source layers from storyboard instead of trim notes
- `ProductionState.assembly_guide_path` renamed to `storyboard_path`
- CLI argument `assembly_guide` renamed to `storyboard` in all commands

### Deprecated

- Assembly guide parser (`parsers/assembly_guide.py`) — no longer imported
- Assembly guide model (`models.py` Project/Segment) — no longer imported
- Converter (`converters.py`) — removed
- Streamlit dashboard (`adapters/dashboard.py`) — use web editor instead
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md CHANGELOG.md
git commit -m "document storyboard unification in CLAUDE.md and CHANGELOG.md"
```
