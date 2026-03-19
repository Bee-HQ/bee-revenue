"""Tests for the new markdown storyboard parser."""
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_minimal():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.project.title == "Test Project"
    assert parsed.project.version == 1
    assert len(parsed.sections) == 1
    assert parsed.sections[0].title == "Section One"
    assert len(parsed.segments) == 2


def test_parse_segment_timecodes():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.segments[0].start == "0:00"
    assert parsed.segments[0].end == "0:15"
    assert parsed.segments[1].start == "0:15"
    assert parsed.segments[1].end == "0:30"


def test_parse_segment_config():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    seg0 = parsed.segments[0]
    assert len(seg0.config.visual) == 1
    assert seg0.config.visual[0].type == "FOOTAGE"
    assert seg0.config.visual[0].src == "footage/clip-a.mp4"


def test_parse_narration():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert "first narration line" in parsed.segments[0].narration
    assert "continues on the next line" in parsed.segments[0].narration
    assert parsed.segments[0].narration.startswith("This is")


def test_parse_narration_belongs_to_segment():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert "Second segment" in parsed.segments[1].narration
    assert "Second segment" not in parsed.segments[0].narration


def test_parse_transition():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    assert parsed.segments[1].config.transition_in is not None
    assert parsed.segments[1].config.transition_in.type == "dissolve"


def test_parse_section_association():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    for seg in parsed.segments:
        assert seg.section == "Section One"


def test_parse_no_project_block_uses_defaults():
    parsed = _parse_text("## Sec (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n")
    assert parsed.project.title == "Untitled"
    assert parsed.project.version == 1


def test_parse_duplicate_project_block_errors():
    from bee_video_editor.formats.parser import StoryboardParseError
    text = '```json bee-video:project\n{"title": "A"}\n```\n```json bee-video:project\n{"title": "B"}\n```\n'
    with pytest.raises(StoryboardParseError, match="multiple.*project"):
        _parse_text(text)


def test_parse_invalid_json_errors():
    from bee_video_editor.formats.parser import StoryboardParseError
    text = '```json bee-video:project\n{invalid json}\n```\n'
    with pytest.raises(StoryboardParseError, match="line"):
        _parse_text(text)


def test_parse_narration_before_segment_errors():
    from bee_video_editor.formats.parser import StoryboardParseError
    text = '> NAR: Orphan narration\n\n## Sec (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n'
    with pytest.raises(StoryboardParseError, match="NAR.*before"):
        _parse_text(text)


def test_parse_non_nar_blockquote_ignored():
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### 0:00 - 0:10 | Seg\n\n'
        '> NAR: Real narration.\n\n> Just a note.\n'
    )
    parsed = _parse_text(text)
    assert "Real narration" in parsed.segments[0].narration
    assert "Just a note" not in parsed.segments[0].narration


def test_parse_segment_without_json_block():
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### 0:00 - 0:10 | Narration Only\n\n'
        '> NAR: Just narration, no config.\n'
    )
    parsed = _parse_text(text)
    assert len(parsed.segments) == 1
    assert parsed.segments[0].config.visual == []
    assert "Just narration" in parsed.segments[0].narration


def test_parse_orphaned_json_block_errors():
    from bee_video_editor.formats.parser import StoryboardParseError
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n'
        '```json bee-video:segment\n{"visual": []}\n```\n'
        '### 0:00 - 0:10 | Seg\n'
    )
    with pytest.raises(StoryboardParseError, match="orphan"):
        _parse_text(text)


def test_parse_malformed_timecodes_errors():
    from bee_video_editor.formats.parser import StoryboardParseError
    text = (
        '```json bee-video:project\n{"title": "T"}\n```\n'
        '## S (0:00 - 0:10)\n\n### abc - def | Bad Timecodes\n'
    )
    with pytest.raises(StoryboardParseError, match="timecode"):
        _parse_text(text)


def test_parse_full():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_full.md")
    assert parsed.project.title == "The Murdaugh Murders"
    assert parsed.project.voice_lock is not None
    assert len(parsed.sections) == 2
    assert len(parsed.segments) >= 7  # at least 7 segments across 2 sections


def test_parse_full_visual_types():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_full.md")
    visual_types = set()
    for seg in parsed.segments:
        for v in seg.config.visual:
            visual_types.add(v.type)
    expected = {"FOOTAGE", "STOCK", "MAP", "GENERATED", "BLACK", "PHOTO", "WAVEFORM", "GRAPHIC"}
    assert expected.issubset(visual_types), f"Missing visual types: {expected - visual_types}"


def test_parse_full_section_association():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_full.md")
    act1_segs = [s for s in parsed.segments if "Night Of" in s.section]
    act2_segs = [s for s in parsed.segments if "Investigation" in s.section]
    assert len(act1_segs) == 3
    assert len(act2_segs) >= 4


def test_parse_full_multi_paragraph_narration():
    from bee_video_editor.formats.parser import parse_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_full.md")
    # Crime Scene Evidence segment has two NAR paragraphs
    crime_seg = [s for s in parsed.segments if s.title == "Crime Scene Evidence"][0]
    assert "\n\n" in crime_seg.narration


def _parse_text(text: str):
    from bee_video_editor.formats.parser import parse_v2
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        f.flush()
        try:
            return parse_v2(f.name)
        finally:
            os.unlink(f.name)
