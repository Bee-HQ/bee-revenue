"""Round-trip tests: parse → write → parse produces identical structure."""
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_roundtrip_minimal():
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    md = write_v2(parsed1)
    parsed2 = _parse_from_string(md)
    _assert_parsed_equal(parsed1, parsed2)


def test_roundtrip_full():
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed1 = parse_v2(FIXTURES / "storyboard_v2_full.md")
    md = write_v2(parsed1)
    parsed2 = _parse_from_string(md)
    _assert_parsed_equal(parsed1, parsed2)


def test_canonical_idempotent():
    """write → parse → write produces identical markdown."""
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    md1 = write_v2(parsed)
    parsed2 = _parse_from_string(md1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def _parse_from_string(text: str):
    from bee_video_editor.formats.parser import parse_v2
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        f.flush()
        try:
            return parse_v2(f.name)
        finally:
            os.unlink(f.name)


def test_otio_roundtrip_minimal():
    """parse → to_otio → from_otio → write produces identical markdown."""
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2

    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    md1 = write_v2(parsed1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def test_otio_roundtrip_full():
    """parse → to_otio → from_otio → write produces identical markdown (full fixture)."""
    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.writer import write_v2

    parsed1 = parse_v2(FIXTURES / "storyboard_v2_full.md")
    tl = to_otio(parsed1)
    parsed2 = from_otio(tl)
    md1 = write_v2(parsed1)
    md2 = write_v2(parsed2)
    assert md1 == md2


def test_otio_file_roundtrip(tmp_path):
    """parse → to_otio → write .otio → read .otio → from_otio round-trips."""
    import opentimelineio as otio

    from bee_video_editor.formats.otio_convert import from_otio, to_otio
    from bee_video_editor.formats.parser import parse_v2

    parsed1 = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed1)
    otio_path = tmp_path / "test.otio"
    otio.adapters.write_to_file(tl, str(otio_path))
    tl2 = otio.adapters.read_from_file(str(otio_path))
    parsed2 = from_otio(tl2)
    _assert_parsed_equal(parsed1, parsed2)


def _assert_parsed_equal(a, b):
    assert a.project.model_dump() == b.project.model_dump()
    assert len(a.sections) == len(b.sections)
    for sa, sb in zip(a.sections, b.sections):
        assert sa.title == sb.title
        assert sa.start == sb.start
        assert sa.end == sb.end
    assert len(a.segments) == len(b.segments)
    for sa, sb in zip(a.segments, b.segments):
        assert sa.title == sb.title
        assert sa.start == sb.start
        assert sa.end == sb.end
        assert sa.section == sb.section
        assert sa.narration == sb.narration
        assert sa.config.model_dump() == sb.config.model_dump()
