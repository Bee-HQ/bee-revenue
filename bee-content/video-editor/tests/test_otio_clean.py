"""Tests for clean OTIO export (strip bee_video metadata)."""
from pathlib import Path

import opentimelineio as otio

FIXTURES = Path(__file__).parent / "fixtures"


def test_clean_otio_strips_metadata():
    from bee_video_editor.formats.otio_convert import clean_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    assert "bee_video" not in clean.metadata
    for track in clean.tracks:
        for item in track:
            if hasattr(item, "metadata"):
                assert "bee_video" not in item.metadata


def test_clean_otio_preserves_clips():
    from bee_video_editor.formats.otio_convert import clean_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    orig_clips = sum(
        1 for t in tl.tracks for c in t if isinstance(c, otio.schema.Clip)
    )
    clean_clips = sum(
        1 for t in clean.tracks for c in t if isinstance(c, otio.schema.Clip)
    )
    assert clean_clips == orig_clips


def test_clean_otio_preserves_media_refs():
    from bee_video_editor.formats.otio_convert import clean_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    clean = clean_otio(tl)
    v1 = [t for t in clean.tracks if t.name == "V1"][0]
    clip = [c for c in v1 if isinstance(c, otio.schema.Clip)][0]
    assert isinstance(clip.media_reference, otio.schema.ExternalReference)


def test_clean_otio_does_not_mutate_original():
    from bee_video_editor.formats.otio_convert import clean_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    _ = clean_otio(tl)
    assert "bee_video" in tl.metadata
