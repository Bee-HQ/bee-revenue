"""Tests for migrating old Storyboard format to new ParsedStoryboard."""

import pytest
from bee_video_editor.models_storyboard import Storyboard, StoryboardSegment, LayerEntry


def test_migrate_basic():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            visual=[LayerEntry(content="clip.mp4", content_type="FOOTAGE")],
            audio=[LayerEntry(content="Narration text here", content_type="NAR")]),
    ])
    parsed = old_to_new(old)
    assert parsed.project.title == "Test"
    assert len(parsed.segments) == 1
    assert parsed.segments[0].config.visual[0].type == "FOOTAGE"


def test_migrate_music_to_audio():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            music=[LayerEntry(content="bg-track.mp3", content_type="MUSIC")]),
    ])
    parsed = old_to_new(old)
    music = [a for a in parsed.segments[0].config.audio if a.type == "MUSIC"]
    assert len(music) == 1


def test_migrate_source_to_visual_src():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            visual=[LayerEntry(content="description", content_type="FOOTAGE")],
            source=[LayerEntry(content="footage/file.mp4 00:01:30-00:02:00", content_type="FOOTAGE")]),
    ])
    parsed = old_to_new(old)
    assert parsed.segments[0].config.visual[0].src is not None


def test_migrate_narration_extracted():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            audio=[LayerEntry(content="The narrator says this.", content_type="NAR")]),
    ])
    parsed = old_to_new(old)
    assert "narrator says this" in parsed.segments[0].narration


def test_migrate_transition_to_structured():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            transition=[LayerEntry(content="Dissolve to next", content_type="DISSOLVE")]),
    ])
    parsed = old_to_new(old)
    assert parsed.segments[0].config.transition_in is not None
    assert parsed.segments[0].config.transition_in.type == "dissolve"


def test_migrate_sections_derived():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg1", section="Act One", section_time="0:00 - 0:30", subsection=""),
        StoryboardSegment(id="0_15-0_30", start="0:15", end="0:30",
            title="Seg2", section="Act One", section_time="0:00 - 0:30", subsection=""),
        StoryboardSegment(id="0_30-0_45", start="0:30", end="0:45",
            title="Seg3", section="Act Two", section_time="0:30 - 1:00", subsection=""),
    ])
    parsed = old_to_new(old)
    section_titles = [s.title for s in parsed.sections]
    assert "Act One" in section_titles
    assert "Act Two" in section_titles
    assert len(parsed.sections) == 2


def test_migrate_real_audio_not_extracted_as_narration():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Test", segments=[
        StoryboardSegment(id="0_00-0_15", start="0:00", end="0:15",
            title="Seg", section="Sec", section_time="0:00 - 0:15", subsection="",
            audio=[
                LayerEntry(content="The narration.", content_type="NAR"),
                LayerEntry(content="ambient.wav", content_type="REAL_AUDIO"),
            ]),
    ])
    parsed = old_to_new(old)
    seg = parsed.segments[0]
    assert "narration" in seg.narration
    real_audio = [a for a in seg.config.audio if a.type == "REAL_AUDIO"]
    assert len(real_audio) == 1


def test_migrate_empty_storyboard():
    from bee_video_editor.formats.migrate import old_to_new
    old = Storyboard(title="Empty")
    parsed = old_to_new(old)
    assert parsed.project.title == "Empty"
    assert parsed.segments == []
    assert parsed.sections == []
