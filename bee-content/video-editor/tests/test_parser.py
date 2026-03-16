"""Tests for the assembly guide parser."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.models import SegmentType
from bee_video_editor.parsers.assembly_guide import parse_assembly_guide

SAMPLE_ASSEMBLY_GUIDE = """\
# Assembly Guide: "Test Video Title"

**Total Duration:** ~10 minutes
**Resolution:** 1080p
**Format:** MP4 (H.264 + AAC)

---

## Legend

- **NAR** = Narrator voiceover
- **REAL** = Real audio/video clip
- **GEN** = Generated asset
- **MIX** = Real footage with narrator

---

## Pre-Production Assets Needed

### Audio Track
- [ ] Generate full narrator voiceover from screenplay
- [x] Select background music

### Generated Graphics
- [ ] Lower thirds for characters
- [ ] Timeline markers

---

## Minute-by-Minute Assembly

### COLD OPEN (0:00 - 1:00)

| Time | Dur | Type | Visual | Audio | Source File / Notes |
|------|-----|------|--------|-------|-------------------|
| 0:00-0:15 | 15s | REAL | Black screen fade in | Alex 911 call: "I need help!" | `footage/911-calls/call.mkv` — trim opening |
| 0:15-0:30 | 15s | MIX | Dark atmospheric B-roll | NAR: "This is a test narrator line" + dark music | GEN: stock B-roll + TTS |
| 0:30-0:45 | 15s | GEN | TEXT-TIMELINE "June 7, 2021" | Beat. Music shifts | GEN: timeline graphic |
| 0:45-1:00 | 15s | NAR | Map zoom | NAR: "Welcome to the story" | TTS narrator |

### ACT 1 (1:00 - 3:00)

#### The Setup (1:00 - 2:00)

| Time | Dur | Type | Visual | Audio | Source File / Notes |
|------|-----|------|--------|-------|-------------------|
| 1:00-1:30 | 30s | MIX | Photo with Ken Burns + lower third "John Doe — Detective" | NAR: "Meet the detective" | Source: news photos |
| 1:30-2:00 | 30s | REAL | Trial footage | Witness: "I saw everything" | `footage/trial/clip.mkv` |

#### The Twist (2:00 - 3:00)

| Time | Dur | Type | Visual | Audio | Source File / Notes |
|------|-----|------|--------|-------|-------------------|
| 2:00-2:30 | 30s | MIX | Dark B-roll + TEXT-FINANCIAL "$1,000,000" | NAR: "The money was gone" | GEN + TTS |
| 2:30-3:00 | 30s | GEN | Map: location zoom | NAR: "Back to the scene" | GEN: MapLibre |

---

## Post-Assembly Checklist

After joining all segments:

- [ ] Add background music throughout
- [ ] Burn subtitles
- [x] Color grade
- [ ] Audio normalize to -14 LUFS

---

## Clip Trim Notes

### `footage/911-calls/call.mkv` (7.7MB)
- **Trim 1:** 0:00-0:15 — Opening "I need help!" (cold open)
- **Trim 2:** 0:15-1:05 — Extended call (~50s)

### `footage/trial/clip.mkv` (54MB)
- **Trim 1:** 0:00-0:30 — Witness testimony (act 1)
"""


@pytest.fixture
def sample_guide_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_ASSEMBLY_GUIDE)
        f.flush()
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestParseAssemblyGuide:
    def test_title(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert project.title == "Test Video Title"

    def test_metadata(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert project.total_duration == "~10 minutes"
        assert project.resolution == "1080p"
        assert project.format == "MP4 (H.264 + AAC)"

    def test_segment_count(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert project.total_segments == 8

    def test_segment_types(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        types = [s.segment_type for s in project.segments]
        assert types[0] == SegmentType.REAL
        assert types[1] == SegmentType.MIX
        assert types[2] == SegmentType.GEN
        assert types[3] == SegmentType.NAR

    def test_segment_timecodes(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        first = project.segments[0]
        assert first.start.total_seconds == 0
        assert first.end.total_seconds == 15
        assert first.duration_seconds == 15

    def test_segment_content(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        first = project.segments[0]
        assert "Black screen" in first.visual
        assert "911 call" in first.audio

    def test_sections(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert "COLD OPEN" in project.sections
        assert "ACT 1" in project.sections

    def test_subsections(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        # Segments in ACT 1 should have subsections
        act1_segs = [s for s in project.segments if s.section == "ACT 1"]
        subsections = {s.subsection for s in act1_segs if s.subsection}
        assert "The Setup" in subsections
        assert "The Twist" in subsections

    def test_pre_production(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert len(project.pre_production) == 4
        # One is done (background music)
        done_count = sum(1 for a in project.pre_production if a.done)
        assert done_count == 1

    def test_pre_production_categories(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        categories = {a.category for a in project.pre_production}
        assert "Audio Track" in categories
        assert "Generated Graphics" in categories

    def test_trim_notes(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert len(project.trim_notes) == 2
        assert project.trim_notes[0].source_file == "footage/911-calls/call.mkv"
        assert project.trim_notes[0].file_size == "7.7MB"
        assert len(project.trim_notes[0].trims) == 2

    def test_trim_instructions(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        first_trim = project.trim_notes[0].trims[0]
        assert first_trim.start == "0:00"
        assert "I need help" in first_trim.label

    def test_post_checklist(self, sample_guide_path):
        project = parse_assembly_guide(sample_guide_path)
        assert len(project.post_checklist) == 4
        done_count = sum(1 for c in project.post_checklist if c.done)
        assert done_count == 1


class TestParseRealAssemblyGuide:
    """Test against the actual Alex Murdaugh assembly guide."""

    REAL_GUIDE = Path("/home/user/bee-revenue/bee-content/discovery/true-crime/cases/alex-murdaugh/assembly-guide.md")

    @pytest.mark.skipif(
        not REAL_GUIDE.exists(),
        reason="Real assembly guide not available",
    )
    def test_parses_real_guide(self):
        project = parse_assembly_guide(self.REAL_GUIDE)
        assert "911" in project.title or "Snapchat" in project.title
        assert project.total_segments > 50
        assert project.resolution == "1080p"

    @pytest.mark.skipif(
        not REAL_GUIDE.exists(),
        reason="Real assembly guide not available",
    )
    def test_real_guide_sections(self):
        project = parse_assembly_guide(self.REAL_GUIDE)
        sections = project.sections
        assert len(sections) >= 4  # Cold open + 4 acts + sponsor

    @pytest.mark.skipif(
        not REAL_GUIDE.exists(),
        reason="Real assembly guide not available",
    )
    def test_real_guide_trim_notes(self):
        project = parse_assembly_guide(self.REAL_GUIDE)
        assert len(project.trim_notes) >= 8  # 8+ source files

    @pytest.mark.skipif(
        not REAL_GUIDE.exists(),
        reason="Real assembly guide not available",
    )
    def test_real_guide_all_types_present(self):
        project = parse_assembly_guide(self.REAL_GUIDE)
        types = {s.segment_type for s in project.segments}
        assert SegmentType.NAR in types
        assert SegmentType.REAL in types
        assert SegmentType.GEN in types
        assert SegmentType.MIX in types
