"""Tests for OTIO conversion."""
from pathlib import Path

import opentimelineio as otio

FIXTURES = Path(__file__).parent / "fixtures"


def _load_minimal():
    from bee_video_editor.formats.parser import parse_v2
    return parse_v2(FIXTURES / "storyboard_v2_minimal.md")


# ---- to_otio tests ----

def test_to_otio_timeline_name():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    assert tl.name == "Test Project"


def test_to_otio_project_metadata():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    meta = tl.metadata.get("bee_video", {}).get("project", {})
    assert meta["title"] == "Test Project"
    assert meta["version"] == 1


def test_to_otio_tracks():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    track_names = [t.name for t in tl.tracks]
    assert "V1" in track_names
    assert "A1" in track_names
    assert "A2" in track_names
    assert "A3" in track_names
    assert "OV1" in track_names


def test_to_otio_v1_clips():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clips = [c for c in v1 if isinstance(c, otio.schema.Clip)]
    assert len(clips) == 2


def test_to_otio_media_ref():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clip0 = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert isinstance(clip0.media_reference, otio.schema.ExternalReference)
    assert "clip-a.mp4" in clip0.media_reference.target_url


def test_to_otio_segment_id():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    clip0 = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert clip0.metadata["bee_video"]["segment_id"] == "first-segment"


def test_to_otio_narration_track():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    a1 = [t for t in tl.tracks if t.name == "A1"][0]
    nar_clips = [c for c in a1 if isinstance(c, otio.schema.Clip)]
    assert len(nar_clips) >= 1
    meta = nar_clips[0].metadata["bee_video"]["narration"]
    assert "first narration line" in meta["text"].lower()


def test_to_otio_transition():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    transitions = [c for c in v1 if isinstance(c, otio.schema.Transition)]
    assert len(transitions) >= 1


def test_to_otio_section_markers():
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = _load_minimal()
    tl = to_otio(parsed)
    v1 = [t for t in tl.tracks if t.name == "V1"][0]
    first_clip = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    marker_names = [m.name for m in first_clip.markers]
    assert "Section One" in marker_names


# ---- from_otio tests ----

def test_from_otio_roundtrip():
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert parsed2.project.title == parsed1.project.title
    assert len(parsed2.segments) == len(parsed1.segments)
    for s1, s2 in zip(parsed1.segments, parsed2.segments):
        assert s1.title == s2.title
        assert s1.narration == s2.narration


def test_from_otio_preserves_visual_config():
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert parsed2.segments[0].config.visual[0].type == "FOOTAGE"
    assert parsed2.segments[0].config.visual[0].src == "footage/clip-a.mp4"


def test_from_otio_preserves_audio():
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    real_audio = [
        a for a in parsed2.segments[0].config.audio if a.type == "REAL_AUDIO"
    ]
    assert len(real_audio) == 1
    assert real_audio[0].volume == 0.8


def test_from_otio_preserves_sections():
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    parsed1 = _load_minimal()
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    assert len(parsed2.sections) == 1
    assert parsed2.sections[0].title == "Section One"
