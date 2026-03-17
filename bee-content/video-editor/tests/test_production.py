"""Tests for production service (state management, project init)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bee_video_editor.converters import assembly_guide_to_storyboard
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)
from bee_video_editor.services.production import (
    FailedItem,
    PipelineResult,
    PipelineStep,
    ProductionConfig,
    ProductionResult,
    ProductionState,
    SegmentStatus,
    _ensure_storyboard,
    _extract_narrator_text,
    _slugify,
    generate_all_previews,
    generate_preview,
    trim_source_footage,
)


class TestProductionState:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                assembly_guide_path="/path/to/guide.md",
                phase="parsed",
            )
            state.segment_statuses = [
                SegmentStatus(index=0, time_range="0:00-0:15", segment_type="REAL"),
                SegmentStatus(index=1, time_range="0:15-0:30", segment_type="MIX", status="done"),
            ]

            path = Path(d) / "state.json"
            state.save(path)

            loaded = ProductionState.load(path)
            assert loaded.assembly_guide_path == "/path/to/guide.md"
            assert loaded.phase == "parsed"
            assert len(loaded.segment_statuses) == 2
            assert loaded.segment_statuses[1].status == "done"

    def test_state_json_format(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                assembly_guide_path="/path/to/guide.md",
                phase="init",
            )
            path = Path(d) / "state.json"
            state.save(path)

            data = json.loads(path.read_text())
            assert "assembly_guide_path" in data
            assert "phase" in data
            assert "segment_statuses" in data


class TestProductionResult:
    def test_empty_result_is_ok(self):
        result = ProductionResult()
        assert result.ok is True
        assert result.succeeded == []
        assert result.failed == []
        assert result.skipped == []

    def test_result_with_failures_is_not_ok(self):
        result = ProductionResult()
        result.failed.append(FailedItem(path="/bad/file.mp4", error="FFmpeg crashed"))
        assert result.ok is False

    def test_result_accumulates(self):
        result = ProductionResult()
        result.succeeded.append(Path("/out/a.mp4"))
        result.succeeded.append(Path("/out/b.mp4"))
        result.failed.append(FailedItem(path="/src/c.mkv", error="codec error"))
        result.skipped.append("d.mp4 already exists")
        assert len(result.succeeded) == 2
        assert len(result.failed) == 1
        assert len(result.skipped) == 1
        assert result.ok is False


class TestProductionConfig:
    def test_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            assert config.output_dir == Path(d) / "output"
            assert config.footage_dir == Path(d) / "footage"
            assert config.tts_engine == "edge"
            assert config.width == 1920
            assert config.height == 1080

    def test_custom_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(
                project_dir=Path(d),
                output_dir=Path(d) / "custom_output",
                footage_dir=Path(d) / "custom_footage",
            )
            assert config.output_dir == Path(d) / "custom_output"
            assert config.footage_dir == Path(d) / "custom_footage"

    def test_state_path(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            assert config.state_path == Path(d) / "output" / "production_state.json"

    def test_state_path_custom_output(self):
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d), output_dir=Path(d) / "custom")
            assert config.state_path == Path(d) / "custom" / "production_state.json"


class TestProductionStateTrack:
    def _make_state(self):
        state = ProductionState(assembly_guide_path="/test.md", phase="parsed")
        state.segment_statuses = [
            SegmentStatus(index=0, time_range="0:00-0:15", segment_type="NAR"),
            SegmentStatus(index=1, time_range="0:15-0:30", segment_type="REAL"),
        ]
        return state

    def test_track_success(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with state.track(0, state_path):
                assert state.segment_statuses[0].status == "processing"
            assert state.segment_statuses[0].status == "done"
            loaded = ProductionState.load(state_path)
            assert loaded.segment_statuses[0].status == "done"

    def test_track_error(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with pytest.raises(RuntimeError):
                with state.track(1, state_path):
                    raise RuntimeError("ffmpeg died")
            assert state.segment_statuses[1].status == "error"
            assert "ffmpeg died" in state.segment_statuses[1].error
            loaded = ProductionState.load(state_path)
            assert loaded.segment_statuses[1].status == "error"

    def test_track_bounds_check(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with pytest.raises(ValueError, match="out of range"):
                with state.track(5, state_path):
                    pass

    def test_track_saves_processing_on_enter(self):
        with tempfile.TemporaryDirectory() as d:
            state = self._make_state()
            state_path = Path(d) / "state.json"
            with pytest.raises(RuntimeError):
                with state.track(0, state_path):
                    intermediate = ProductionState.load(state_path)
                    assert intermediate.segment_statuses[0].status == "processing"
                    raise RuntimeError("crash")


class TestExtractNarratorText:
    def test_quoted(self):
        text = _extract_narrator_text('NAR: "This is Alex Murdaugh..." + dark ambient music')
        assert text == "This is Alex Murdaugh..."

    def test_unquoted(self):
        text = _extract_narrator_text('NAR: This is a test line + music')
        assert text == "This is a test line"

    def test_no_narrator(self):
        text = _extract_narrator_text('Alex 911 call: "I need help!"')
        assert text == ""

    def test_empty(self):
        text = _extract_narrator_text('')
        assert text == ""

    def test_nar_only(self):
        text = _extract_narrator_text('NAR: "Welcome to the story"')
        assert text == "Welcome to the story"


class TestSlugify:
    def test_basic(self):
        assert _slugify("Cold Open") == "cold-open"

    def test_special_chars(self):
        assert _slugify('$792,000 — Missing') == "792000-missing"

    def test_multiple_spaces(self):
        assert _slugify("ACT  1:  THE  DYNASTY") == "act-1-the-dynasty"


class TestEnsureStoryboard:
    def test_storyboard_passes_through(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        assert _ensure_storyboard(sb) is sb

    def test_project_converts(self):
        from bee_video_editor.models import Project
        proj = Project(title="Test", total_duration="10m", resolution="1080p", format="MP4")
        result = _ensure_storyboard(proj)
        assert isinstance(result, Storyboard)
        assert result.title == "Test"


class TestPipelineResult:
    def test_ok_when_all_done(self):
        result = PipelineResult(steps=[
            PipelineStep(name="init", status="done"),
            PipelineStep(name="graphics", status="skipped"),
        ])
        assert result.ok is True

    def test_not_ok_when_failed(self):
        result = PipelineResult(steps=[
            PipelineStep(name="init", status="done"),
            PipelineStep(name="graphics", status="failed"),
        ])
        assert result.ok is False

    def test_ok_empty_steps(self):
        result = PipelineResult(steps=[])
        assert result.ok is True

    def test_output_path_default_none(self):
        result = PipelineResult(steps=[])
        assert result.output_path is None


class TestTrimWithStoryboard:
    def test_trim_storyboard_returns_empty(self):
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            (config.output_dir / "segments").mkdir(parents=True)
            result = trim_source_footage(sb, config)
            assert isinstance(result, ProductionResult)
            assert result.ok
            assert len(result.succeeded) == 0


class TestGeneratePreview:
    def test_video_preview(self):
        """Test preview of a video file (mocked FFmpeg)."""
        with tempfile.TemporaryDirectory() as d:
            media = Path(d) / "test.mp4"
            media.touch()
            out = Path(d) / "preview.mp4"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = generate_preview(media, out)
                mock_run.assert_called_once()
                cmd = mock_run.call_args[0][0]
                assert "ultrafast" in cmd
                assert "360" in " ".join(cmd)
                assert result == out

    def test_video_preview_ffmpeg_error(self):
        """Test that FFmpeg failure raises RuntimeError."""
        with tempfile.TemporaryDirectory() as d:
            media = Path(d) / "test.mp4"
            media.touch()
            out = Path(d) / "preview.mp4"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="codec not found")
                with pytest.raises(RuntimeError, match="Preview generation failed"):
                    generate_preview(media, out)

    def test_creates_output_parent_dirs(self):
        """Test that nested output directories are created automatically."""
        with tempfile.TemporaryDirectory() as d:
            media = Path(d) / "test.mp4"
            media.touch()
            out = Path(d) / "deep" / "nested" / "preview.mp4"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                generate_preview(media, out)
                assert out.parent.exists()


class TestGenerateAllPreviews:
    def _make_storyboard_with_segment(self, seg_id: str) -> Storyboard:
        seg = StoryboardSegment(
            id=seg_id,
            start="0:00",
            end="0:15",
            title="Test Segment",
            section="Act 1",
            section_time="0:00 - 1:00",
            subsection="",
        )
        sb = Storyboard(title="Test", production_rules=ProductionRules())
        sb.segments = [seg]
        return sb

    def test_no_assignments_skips_all(self):
        """Segments without assignments produce no output."""
        with tempfile.TemporaryDirectory() as d:
            sb = self._make_storyboard_with_segment("seg-001")
            result = generate_all_previews(sb, Path(d))
            assert result.ok
            assert len(result.succeeded) == 0
            assert len(result.failed) == 0

    def test_missing_file_adds_to_failed(self):
        """Assigned media that doesn't exist is recorded as failed."""
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            seg_id = "seg-001"
            sb = self._make_storyboard_with_segment(seg_id)

            assignments_dir = proj / ".bee-video"
            assignments_dir.mkdir(parents=True)
            assignments_path = assignments_dir / "assignments.json"
            assignments_path.write_text(json.dumps({
                seg_id: {"visual:0": "/nonexistent/file.mp4"}
            }))

            result = generate_all_previews(sb, proj)
            assert len(result.failed) == 1
            assert "not found" in result.failed[0].error

    def test_already_existing_preview_is_skipped(self):
        """Segments whose preview already exists are skipped."""
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            seg_id = "seg-001"
            sb = self._make_storyboard_with_segment(seg_id)

            media = proj / "media.mp4"
            media.touch()

            assignments_dir = proj / ".bee-video"
            assignments_dir.mkdir(parents=True)
            (assignments_dir / "assignments.json").write_text(json.dumps({
                seg_id: {"visual:0": str(media)}
            }))

            # Pre-create the preview so it gets skipped
            previews_dir = proj / "output" / "previews"
            previews_dir.mkdir(parents=True)
            (previews_dir / f"{seg_id}.mp4").touch()

            result = generate_all_previews(sb, proj)
            assert len(result.skipped) == 1
            assert len(result.succeeded) == 0

    def test_successful_preview_generation(self):
        """Full success path with mocked FFmpeg."""
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            seg_id = "seg-001"
            sb = self._make_storyboard_with_segment(seg_id)

            media = proj / "media.mp4"
            media.touch()

            assignments_dir = proj / ".bee-video"
            assignments_dir.mkdir(parents=True)
            (assignments_dir / "assignments.json").write_text(json.dumps({
                seg_id: {"visual:0": str(media)}
            }))

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = generate_all_previews(sb, proj)
                assert len(result.succeeded) == 1
                assert result.ok


class TestParallelNarration:
    def test_workers_parameter_accepted(self):
        """Verify workers parameter doesn't crash with default value."""
        import inspect
        from bee_video_editor.services.production import generate_narration_for_project
        sig = inspect.signature(generate_narration_for_project)
        assert "workers" in sig.parameters
        assert sig.parameters["workers"].default == 1
