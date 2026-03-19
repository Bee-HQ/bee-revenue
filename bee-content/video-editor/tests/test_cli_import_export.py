"""Tests for import-md and export CLI commands."""

from pathlib import Path
from typer.testing import CliRunner

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_import_md_creates_otio(tmp_path):
    from bee_video_editor.adapters.cli import app
    md_path = FIXTURES / "storyboard_v2_minimal.md"
    otio_path = tmp_path / "storyboard.otio"
    result = runner.invoke(app, ["import-md", str(md_path), "--output", str(otio_path)])
    assert result.exit_code == 0, result.output
    assert otio_path.exists()


def test_export_creates_md(tmp_path):
    from bee_video_editor.adapters.cli import app
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))
    md_path = tmp_path / "exported.md"
    result = runner.invoke(app, ["export", str(otio_path), "--format", "md", "--output", str(md_path)])
    assert result.exit_code == 0, result.output
    assert md_path.exists()
    assert "Test Project" in md_path.read_text()


def test_export_clean_otio(tmp_path):
    from bee_video_editor.adapters.cli import app
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))
    clean_path = tmp_path / "clean.otio"
    result = runner.invoke(app, ["export", str(otio_path), "--format", "otio", "--output", str(clean_path)])
    assert result.exit_code == 0, result.output
    clean_tl = otio_lib.adapters.read_from_file(str(clean_path))
    assert "bee_video" not in clean_tl.metadata


def test_import_md_default_output(tmp_path):
    from bee_video_editor.adapters.cli import app
    import shutil
    md_copy = tmp_path / "storyboard.md"
    shutil.copy(FIXTURES / "storyboard_v2_minimal.md", md_copy)
    result = runner.invoke(app, ["import-md", str(md_copy)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "storyboard.otio").exists()


def test_export_unknown_format(tmp_path):
    from bee_video_editor.adapters.cli import app
    import opentimelineio as otio_lib
    from bee_video_editor.formats.parser import parse_v2
    from bee_video_editor.formats.otio_convert import to_otio
    parsed = parse_v2(FIXTURES / "storyboard_v2_minimal.md")
    tl = to_otio(parsed)
    otio_path = tmp_path / "project.otio"
    otio_lib.adapters.write_to_file(tl, str(otio_path))
    result = runner.invoke(app, ["export", str(otio_path), "--format", "xml"])
    assert result.exit_code != 0
