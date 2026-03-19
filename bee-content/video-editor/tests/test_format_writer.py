"""Tests for the canonical markdown writer."""

from bee_video_editor.formats.models import (
    ProjectConfig, SegmentConfig, VisualEntry, AudioEntry,
    OverlayEntry, TransitionConfig, CaptionsConfig,
)
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSection, ParsedSegment


def test_write_minimal():
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="Test"),
        sections=[ParsedSection(title="Sec", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="seg",
            title="Seg", start="0:00", end="0:10", section="Sec",
            config=SegmentConfig(visual=[VisualEntry(type="FOOTAGE", src="clip.mp4")]),
            narration="Hello world.",
        )],
    )
    md = write_v2(parsed)
    assert '```json bee-video:project' in md
    assert '"title": "Test"' in md
    assert '## Sec (0:00 - 0:10)' in md
    assert '### 0:00 - 0:10 | Seg' in md
    assert '```json bee-video:segment' in md
    assert '"type": "FOOTAGE"' in md
    assert '> NAR: Hello world.' in md


def test_write_json_key_order():
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(
                visual=[VisualEntry(type="FOOTAGE", src="a.mp4")],
                audio=[AudioEntry(type="REAL_AUDIO", src="a.mp4", volume=0.5)],
                transition_in=TransitionConfig(type="dissolve", duration=1.0),
            ),
            narration="",
        )],
    )
    md = write_v2(parsed)
    vis_pos = md.index('"visual"')
    aud_pos = md.index('"audio"')
    trans_pos = md.index('"transition_in"')
    assert vis_pos < aud_pos < trans_pos


def test_write_omits_none_fields():
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(visual=[VisualEntry(type="BLACK")]),
            narration="",
        )],
    )
    md = write_v2(parsed)
    assert '"src"' not in md


def test_write_multiline_narration():
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(),
            narration="First paragraph.\n\nSecond paragraph.",
        )],
    )
    md = write_v2(parsed)
    assert "> NAR: First paragraph." in md
    assert "> NAR: Second paragraph." in md


def test_write_no_narration():
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(),
            narration="",
        )],
    )
    md = write_v2(parsed)
    assert "> NAR:" not in md


def test_write_omits_empty_lists():
    """Empty visual/audio/overlay lists should not appear in JSON output."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(
                visual=[VisualEntry(type="FOOTAGE", src="a.mp4")],
                # audio and overlay are empty
            ),
            narration="",
        )],
    )
    md = write_v2(parsed)
    assert '"audio"' not in md
    assert '"overlay"' not in md


def test_write_narration_only_segment_no_json_block():
    """Segment with empty config should not emit a JSON block."""
    from bee_video_editor.formats.writer import write_v2
    parsed = ParsedStoryboard(
        project=ProjectConfig(title="T"),
        sections=[ParsedSection(title="S", start="0:00", end="0:10")],
        segments=[ParsedSegment(
            id="x",
            title="X", start="0:00", end="0:10", section="S",
            config=SegmentConfig(),
            narration="Just narration.",
        )],
    )
    md = write_v2(parsed)
    assert "bee-video:segment" not in md
    assert "> NAR: Just narration." in md
