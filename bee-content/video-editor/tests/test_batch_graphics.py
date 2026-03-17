"""Tests for batch graphics config parsing and generation."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.services.batch_graphics import GraphicSpec, generate_batch, parse_graphics_config


class TestParseGraphicsConfig:
    def test_parses_basic_config(self):
        config = {
            "output_dir": "output/graphics",
            "graphics": [
                {"type": "lower_third", "name": "Test Person", "role": "Witness"},
            ],
        }
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps(config))
            specs, output_dir = parse_graphics_config(p)

        assert len(specs) == 1
        assert specs[0].type == "lower_third"
        assert specs[0].kwargs == {"name": "Test Person", "role": "Witness"}
        assert output_dir == "output/graphics"

    def test_rejects_unknown_type(self):
        config = {
            "graphics": [{"type": "nonexistent_graphic"}],
        }
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps(config))
            with pytest.raises(ValueError, match="nonexistent_graphic"):
                parse_graphics_config(p)

    def test_default_output_dir(self):
        config = {"graphics": []}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps(config))
            _, output_dir = parse_graphics_config(p)

        assert output_dir == "output/graphics"

    def test_empty_graphics_list(self):
        config = {"graphics": []}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps(config))
            specs, _ = parse_graphics_config(p)

        assert specs == []

    def test_invalid_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text("not valid json{{{")
            with pytest.raises(Exception):
                parse_graphics_config(p)


class TestGenerateBatch:
    def test_calls_correct_processor(self):
        specs = [GraphicSpec(type="lower_third", kwargs={"name": "Test", "role": "Witness"})]
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            with patch("bee_video_editor.services.batch_graphics.gfx") as mock_gfx:
                mock_gfx.lower_third.return_value = output_dir / "lower-third-00-test.png"
                result = generate_batch(specs, output_dir)

            mock_gfx.lower_third.assert_called_once()
            call_kwargs = mock_gfx.lower_third.call_args
            assert call_kwargs.kwargs["name"] == "Test"
            assert call_kwargs.kwargs["role"] == "Witness"
            assert len(result.succeeded) == 1

    def test_skips_existing_files(self):
        specs = [GraphicSpec(type="lower_third", kwargs={"name": "Test", "role": "Witness"})]
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            expected_path = output_dir / "lower-third-00-test.png"
            expected_path.write_bytes(b"existing")

            with patch("bee_video_editor.services.batch_graphics.gfx") as mock_gfx:
                result = generate_batch(specs, output_dir)

            mock_gfx.lower_third.assert_not_called()
            assert len(result.skipped) == 1

    def test_handles_processor_error(self):
        specs = [GraphicSpec(type="lower_third", kwargs={"name": "Bad", "role": ""})]
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            with patch("bee_video_editor.services.batch_graphics.gfx") as mock_gfx:
                mock_gfx.lower_third.side_effect = Exception("Pillow error")
                result = generate_batch(specs, output_dir)

            assert len(result.failed) == 1
            assert "Pillow error" in result.failed[0].error

    def test_multiple_graphics_sequential_numbering(self):
        specs = [
            GraphicSpec(type="lower_third", kwargs={"name": "A", "role": "X"}),
            GraphicSpec(type="lower_third", kwargs={"name": "B", "role": "Y"}),
            GraphicSpec(type="timeline_marker", kwargs={"date": "Jan 1", "description": "Event"}),
        ]
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            with patch("bee_video_editor.services.batch_graphics.gfx") as mock_gfx:
                mock_gfx.lower_third.return_value = Path("out.png")
                mock_gfx.timeline_marker.return_value = Path("out.png")
                result = generate_batch(specs, output_dir)

            assert mock_gfx.lower_third.call_count == 2
            assert mock_gfx.timeline_marker.call_count == 1
            assert len(result.succeeded) == 3
