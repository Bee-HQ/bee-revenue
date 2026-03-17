"""Tests for the storyboard parser."""

import textwrap
import tempfile
from pathlib import Path

import pytest

from bee_video_editor.parsers.storyboard import parse_storyboard
from bee_video_editor.models_storyboard import Storyboard


SAMPLE_STORYBOARD = textwrap.dedent("""\
    # Shot-by-Shot Storyboard: "Test Video Title"

    **Legend:**
    - `FOOTAGE:` = Real clip
    - `NAR:` = Narrator voiceover

    ---

    ## COLD OPEN (0:00 - 2:30)

    ### 0:00 - 0:05 | THE HOOK
    | Layer | Content |
    |-------|---------|
    | Visual | `WAVEFORM:` Green audio waveform on black background |
    | Audio | `REAL AUDIO:` Alex 911 call — "I need the police!" |
    | Overlay | `GRAPHIC:` Small text at bottom: "911 CALL" |
    | Music | Dark ambient drone fades in |
    | Source | `segments/911-call-full.mp4` trim 0:00-0:05 |

    ### 0:05 - 0:15 | NARRATOR INTRO
    | Layer | Content |
    |-------|---------|
    | Visual (0:05-0:10) | `STOCK:` Slow aerial of rural estate |
    | Visual (0:10-0:15) | `STOCK:` Dark hallway cinematic |
    | Audio | `NAR:` "This is a test narration line." |
    | Music | Drone builds slightly |
    | Transition | Quick fade (0.3s) |

    ---

    ## ACT 1: THE STORY (2:30 - 10:00)

    ### Background (2:30 - 5:00)

    #### 2:30 - 2:42 | ESTABLISHING SHOT
    | Layer | Content |
    |-------|---------|
    | Visual | `MAP:` South Carolina map with counties highlighted |
    | Audio | `NAR:` "The lowcountry of South Carolina." |

    #### 2:42 - 2:54 | DYNASTY BEGINS
    | Layer | Content |
    |-------|---------|
    | Visual | `PHOTO:` Historical photo — sepia tone |
    | Audio | `NAR:` "One family controlled who went to prison." |
    | Overlay | `GRAPHIC:` Lower third — "Randolph Murdaugh Sr. — Solicitor, 1920" |

    ---

    ## STOCK FOOTAGE NEEDED

    | # | Search Term | Used In | Duration Needed |
    |---|-------------|---------|----------------|
    | 1 | "aerial farm dusk southern" | 0:05-0:10 | 5s |
    | 2 | "dark hallway cinematic" | 0:10-0:15 | 5s |

    ---

    ## PHOTOS NEEDED

    | # | Subject | Source | Used In |
    |---|---------|--------|---------|
    | 1 | Historical courthouse | News archives | 2:42 dynasty |

    ---

    ## MAP IMAGES NEEDED

    | # | Location | Zoom Level | Style | Used In |
    |---|----------|-----------|-------|---------|
    | 1 | SC Lowcountry | State level | Dark red | 2:30 |

    ---

    ## PRODUCTION RULES

    1. **No visual lasts more than 12 seconds**
    2. **Every narrator line has a relevant visual**
    3. **Ken Burns on every static image**
""")


@pytest.fixture
def sample_storyboard() -> Storyboard:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_STORYBOARD)
        f.flush()
        return parse_storyboard(f.name)


class TestParseStoryboard:
    def test_title(self, sample_storyboard):
        assert sample_storyboard.title == "Test Video Title"

    def test_segment_count(self, sample_storyboard):
        assert sample_storyboard.total_segments == 4

    def test_sections(self, sample_storyboard):
        assert sample_storyboard.sections == ["COLD OPEN", "ACT 1: THE STORY"]

    def test_first_segment_basic(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert seg.id == "0_00-0_05"
        assert seg.start == "0:00"
        assert seg.end == "0:05"
        assert seg.title == "THE HOOK"
        assert seg.section == "COLD OPEN"
        assert seg.duration_seconds == 5

    def test_first_segment_visual(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert len(seg.visual) == 1
        assert seg.visual[0].content_type == "WAVEFORM"
        assert "waveform" in seg.visual[0].content.lower()

    def test_first_segment_audio(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert len(seg.audio) == 1
        assert seg.audio[0].content_type == "REAL AUDIO"

    def test_first_segment_overlay(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert len(seg.overlay) == 1
        assert seg.overlay[0].content_type == "GRAPHIC"
        assert "911 CALL" in seg.overlay[0].content

    def test_first_segment_music(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert len(seg.music) == 1
        assert "ambient" in seg.music[0].content.lower()

    def test_first_segment_source(self, sample_storyboard):
        seg = sample_storyboard.segments[0]
        assert len(seg.source) == 1
        assert "911-call" in seg.source[0].raw

    def test_time_ranged_visual(self, sample_storyboard):
        # Second segment has two time-ranged visuals
        seg = sample_storyboard.segments[1]
        assert len(seg.visual) == 2
        assert seg.visual[0].time_start == "0:05"
        assert seg.visual[0].time_end == "0:10"
        assert seg.visual[0].content_type == "STOCK"
        assert seg.visual[1].time_start == "0:10"
        assert seg.visual[1].time_end == "0:15"

    def test_narrator_audio(self, sample_storyboard):
        seg = sample_storyboard.segments[1]
        assert len(seg.audio) == 1
        assert seg.audio[0].content_type == "NAR"

    def test_transition(self, sample_storyboard):
        seg = sample_storyboard.segments[1]
        assert len(seg.transition) == 1
        assert "fade" in seg.transition[0].raw.lower()

    def test_subsection_segments(self, sample_storyboard):
        # Segments under "Background" subsection
        seg = sample_storyboard.segments[2]
        assert seg.subsection == "Background"
        assert seg.section == "ACT 1: THE STORY"
        assert seg.title == "ESTABLISHING SHOT"

    def test_map_visual(self, sample_storyboard):
        seg = sample_storyboard.segments[2]
        assert seg.visual[0].content_type == "MAP"

    def test_photo_visual(self, sample_storyboard):
        seg = sample_storyboard.segments[3]
        assert seg.visual[0].content_type == "PHOTO"

    def test_lower_third_overlay(self, sample_storyboard):
        seg = sample_storyboard.segments[3]
        assert len(seg.overlay) == 1
        assert "Lower third" in seg.overlay[0].content or "lower third" in seg.overlay[0].content.lower()

    def test_stock_footage_count(self, sample_storyboard):
        assert len(sample_storyboard.stock_footage) == 2
        assert sample_storyboard.stock_footage[0].search_term == '"aerial farm dusk southern"'

    def test_photos_needed(self, sample_storyboard):
        assert len(sample_storyboard.photos_needed) == 1
        assert "courthouse" in sample_storyboard.photos_needed[0].subject.lower()

    def test_maps_needed(self, sample_storyboard):
        assert len(sample_storyboard.maps_needed) == 1
        assert "SC Lowcountry" in sample_storyboard.maps_needed[0].location

    def test_production_rules(self, sample_storyboard):
        rules = sample_storyboard.production_rules.rules
        assert len(rules) == 3
        assert "12 seconds" in rules[0]

    def test_summary(self, sample_storyboard):
        summary = sample_storyboard.summary()
        assert summary["total_segments"] == 4
        assert summary["stock_footage_needed"] == 2
        assert summary["photos_needed"] == 1
        assert summary["maps_needed"] == 1
        assert summary["production_rules"] == 3


class TestStoryboardParserResilience:
    def test_malformed_segment_header_skipped(self):
        md = """# Test Storyboard

## SECTION (0:00 - 0:30)

#### this is not a valid header
| Layer | Content |
|-------|---------|
| Visual | `FOOTAGE:` test |

#### 0:10 - 0:20 | VALID
| Layer | Content |
|-------|---------|
| Visual | `FOOTAGE:` real content |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.storyboard import parse_storyboard
            sb = parse_storyboard(f.name)
            # Should parse at least the valid segment
            valid = [s for s in sb.segments if s.title == "VALID"]
            assert len(valid) >= 1

    def test_normalize_cell_preserves_backticks(self):
        from bee_video_editor.parsers.storyboard import _normalize_cell
        assert _normalize_cell("  `FOOTAGE:` test  ") == "`FOOTAGE:` test"

    def test_wrong_column_count_skipped(self):
        md = """# Test Storyboard

## SECTION (0:00 - 0:10)

#### 0:00 - 0:10 | TEST
| Layer | Content |
|-------|---------|
| Visual | content |
| Bad row with no pipe separator
| Audio | audio content |
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            from bee_video_editor.parsers.storyboard import parse_storyboard
            sb = parse_storyboard(f.name)
            # Should not crash, should parse what it can
            assert len(sb.segments) >= 1


class TestParseRealStoryboard:
    """Test against the actual Alex Murdaugh storyboard."""

    @pytest.fixture
    def real_storyboard(self):
        path = Path(__file__).parent.parent.parent / (
            "discovery/true-crime/cases/alex-murdaugh/storyboard.md"
        )
        if not path.exists():
            pytest.skip("Real storyboard not found")
        return parse_storyboard(path)

    def test_parses_real_storyboard(self, real_storyboard):
        assert real_storyboard.title
        assert real_storyboard.total_segments > 0

    def test_real_sections(self, real_storyboard):
        sections = real_storyboard.sections
        assert len(sections) >= 2
        assert "COLD OPEN" in sections[0].upper()

    def test_real_stock_footage(self, real_storyboard):
        assert len(real_storyboard.stock_footage) >= 10

    def test_real_photos(self, real_storyboard):
        assert len(real_storyboard.photos_needed) >= 4

    def test_real_maps(self, real_storyboard):
        assert len(real_storyboard.maps_needed) >= 3

    def test_real_production_rules(self, real_storyboard):
        assert len(real_storyboard.production_rules.rules) >= 5

    def test_real_segment_layers(self, real_storyboard):
        # Every segment should have at least a visual or audio layer
        for seg in real_storyboard.segments:
            has_content = seg.visual or seg.audio or seg.overlay or seg.music
            assert has_content, f"Segment {seg.id} ({seg.title}) has no content layers"

    def test_real_visual_types(self, real_storyboard):
        # Check that we parse multiple visual types (bible codes like BROLL-DARK, COURTROOM, etc.)
        visual_types = set()
        for seg in real_storyboard.segments:
            for v in seg.visual:
                visual_types.add(v.content_type)
        # Storyboard uses bible visual codes — at least some should be recognized
        recognized = visual_types - {"UNKNOWN"}
        assert len(recognized) > 0, f"No recognized visual types, got: {visual_types}"
