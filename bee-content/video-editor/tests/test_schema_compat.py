"""Tests for ParsedStoryboard → StoryboardSchema conversion."""
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_parsed_to_schema_title():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.title == "Test Project"


def test_parsed_to_schema_segment_count():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.total_segments == 2
    assert len(schema.segments) == 2


def test_parsed_to_schema_segment_fields():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert seg.id == "first-segment"
    assert seg.start == "0:00"
    assert seg.end == "0:15"
    assert seg.title == "First Segment"
    assert seg.section == "Section One"
    assert seg.duration_seconds == 15.0


def test_parsed_to_schema_visual_layer():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert len(seg.visual) == 1
    assert seg.visual[0].content_type == "FOOTAGE"
    assert "clip-a.mp4" in seg.visual[0].content


def test_parsed_to_schema_audio_excludes_music():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert any(a.content_type == "REAL_AUDIO" for a in seg.audio)
    assert not any(a.content_type == "REAL_AUDIO" for a in seg.music)


def test_parsed_to_schema_narration_in_audio():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    nar_entries = [a for a in seg.audio if a.content_type == "NAR"]
    assert len(nar_entries) == 1
    assert "first narration line" in nar_entries[0].content


def test_parsed_to_schema_assigned_media():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[0]
    assert seg.assigned_media.get("visual:0") == "footage/clip-a.mp4"


def test_parsed_to_schema_transition():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    seg = schema.segments[1]
    assert len(seg.transition) == 1
    assert seg.transition[0].content_type == "DISSOLVE"


def test_parsed_to_schema_stock_count():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert schema.stock_footage_needed == 1


def test_parsed_to_schema_sections():
    from bee_video_editor.api.schema_compat import parsed_to_schema
    parsed = _load_minimal()
    schema = parsed_to_schema(parsed)
    assert "Section One" in schema.sections


def _load_minimal():
    from bee_video_editor.formats.parser import parse_v2
    return parse_v2(FIXTURES / "storyboard_v2_minimal.md")
