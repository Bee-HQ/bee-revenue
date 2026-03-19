"""Tests for production service (state management, project init)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bee_video_editor.formats.models import (
    AudioEntry,
    OverlayEntry,
    ProjectConfig,
    SegmentConfig,
    VisualEntry,
)
from bee_video_editor.formats.parser import ParsedSection, ParsedSegment, ParsedStoryboard
from bee_video_editor.services.production import (
    FailedItem,
    PipelineResult,
    PipelineStep,
    ProductionConfig,
    ProductionResult,
    ProductionState,
    SegmentStatus,
    _derive_segment_type,
    _slugify,
    generate_all_previews,
    generate_preview,
    init_project,
    trim_source_footage,
)


def _make_segment(
    seg_id: str = "test-seg",
    title: str = "Test",
    start: str = "0:00",
    end: str = "0:15",
    section: str = "Act 1",
    visual_types: tuple = (),
    audio_types: tuple = (),
    narration: str = "",
    visual_entries: list | None = None,
    overlay_entries: list | None = None,
) -> ParsedSegment:
    """Helper to build a ParsedSegment for testing."""
    if visual_entries is not None:
        visuals = visual_entries
    else:
        visuals = [VisualEntry(type=t) for t in visual_types]

    audios = [AudioEntry(type=t) for t in audio_types]
    overlays = overlay_entries or []

    config = SegmentConfig(
        visual=visuals,
        audio=audios,
        overlay=overlays,
    )
    return ParsedSegment(
        id=seg_id,
        title=title,
        start=start,
        end=end,
        section=section,
        config=config,
        narration=narration,
    )


def _make_storyboard(segments: list[ParsedSegment] | None = None) -> ParsedStoryboard:
    """Helper to build a ParsedStoryboard for testing."""
    return ParsedStoryboard(
        project=ProjectConfig(title="Test", version=1),
        sections=[ParsedSection(title="Act 1", start="0:00", end="1:00")],
        segments=segments or [],
    )


class TestProductionState:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                storyboard_path="/path/to/storyboard.md",
                phase="parsed",
            )
            state.segment_statuses = [
                SegmentStatus(index=0, time_range="0:00-0:15", segment_type="REAL"),
                SegmentStatus(index=1, time_range="0:15-0:30", segment_type="MIX", status="done"),
            ]

            path = Path(d) / "state.json"
            state.save(path)

            loaded = ProductionState.load(path)
            assert loaded.storyboard_path == "/path/to/storyboard.md"
            assert loaded.phase == "parsed"
            assert len(loaded.segment_statuses) == 2
            assert loaded.segment_statuses[1].status == "done"

    def test_state_json_format(self):
        with tempfile.TemporaryDirectory() as d:
            state = ProductionState(
                storyboard_path="/path/to/storyboard.md",
                phase="init",
            )
            path = Path(d) / "state.json"
            state.save(path)

            data = json.loads(path.read_text())
            assert "storyboard_path" in data
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
        state = ProductionState(storyboard_path="/test.md", phase="parsed")
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


class TestSlugify:
    def test_basic(self):
        assert _slugify("Cold Open") == "cold-open"

    def test_special_chars(self):
        assert _slugify('$792,000 — Missing') == "792000-missing"

    def test_multiple_spaces(self):
        assert _slugify("ACT  1:  THE  DYNASTY") == "act-1-the-dynasty"


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
        parsed = _make_storyboard()
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            (config.output_dir / "segments").mkdir(parents=True)
            result = trim_source_footage(parsed, config)
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
    def _make_storyboard_with_segment(self, seg_id: str) -> ParsedStoryboard:
        seg = _make_segment(
            seg_id=seg_id,
            title="Test Segment",
            section="Act 1",
            visual_entries=[VisualEntry(type="FOOTAGE")],
        )
        return _make_storyboard(segments=[seg])

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
            seg = _make_segment(
                seg_id="seg-001",
                title="Test Segment",
                section="Act 1",
                visual_entries=[VisualEntry(type="FOOTAGE", src="/nonexistent/file.mp4")],
            )
            sb = _make_storyboard(segments=[seg])

            result = generate_all_previews(sb, Path(d))
            assert len(result.failed) == 1
            assert "not found" in result.failed[0].error

    def test_already_existing_preview_is_skipped(self):
        """Segments whose preview already exists are skipped."""
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            media = proj / "media.mp4"
            media.touch()

            seg = _make_segment(
                seg_id="seg-001",
                title="Test Segment",
                section="Act 1",
                visual_entries=[VisualEntry(type="FOOTAGE", src=str(media))],
            )
            sb = _make_storyboard(segments=[seg])

            # Pre-create the preview so it gets skipped
            previews_dir = proj / "output" / "previews"
            previews_dir.mkdir(parents=True)
            (previews_dir / "seg-001.mp4").touch()

            result = generate_all_previews(sb, proj)
            assert len(result.skipped) == 1
            assert len(result.succeeded) == 0

    def test_successful_preview_generation(self):
        """Full success path with mocked FFmpeg."""
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d)
            media = proj / "media.mp4"
            media.touch()

            seg = _make_segment(
                seg_id="seg-001",
                title="Test Segment",
                section="Act 1",
                visual_entries=[VisualEntry(type="FOOTAGE", src=str(media))],
            )
            sb = _make_storyboard(segments=[seg])

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


class TestDeriveSegmentType:
    def test_footage_and_nar_is_mix(self):
        seg = _make_segment(visual_types=("FOOTAGE",), narration="Some narration")
        assert _derive_segment_type(seg) == "MIX"

    def test_footage_only_is_real(self):
        seg = _make_segment(visual_types=("FOOTAGE",))
        assert _derive_segment_type(seg) == "REAL"

    def test_real_audio_only_is_real(self):
        seg = _make_segment(audio_types=("REAL_AUDIO",))
        assert _derive_segment_type(seg) == "REAL"

    def test_nar_only_is_nar(self):
        seg = _make_segment(narration="Some narration text")
        assert _derive_segment_type(seg) == "NAR"

    def test_graphic_only_is_gen(self):
        seg = _make_segment(visual_types=("GRAPHIC",))
        assert _derive_segment_type(seg) == "GEN"

    def test_map_is_gen(self):
        seg = _make_segment(visual_types=("MAP",))
        assert _derive_segment_type(seg) == "GEN"

    def test_empty_is_gen(self):
        seg = _make_segment()
        assert _derive_segment_type(seg) == "GEN"


class TestInitProject:
    def test_init_project_returns_production_state(self):
        """init_project accepts ParsedStoryboard, returns ProductionState."""
        seg1 = _make_segment(
            seg_id="seg-1",
            start="0:00",
            end="0:15",
            visual_types=("FOOTAGE",),
            narration="Welcome to the story.",
        )
        seg2 = _make_segment(
            seg_id="seg-2",
            start="0:15",
            end="0:30",
            visual_types=("WAVEFORM",),
            audio_types=("REAL_AUDIO",),
        )
        parsed = _make_storyboard(segments=[seg1, seg2])

        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            state = init_project(parsed, config)

            assert isinstance(state, ProductionState)
            assert len(state.segment_statuses) == 2
            assert state.phase == "parsed"

            # FOOTAGE + narration -> MIX
            assert state.segment_statuses[0].segment_type == "MIX"
            # REAL_AUDIO -> REAL
            assert state.segment_statuses[1].segment_type == "REAL"

    def test_init_project_creates_output_dirs(self):
        """init_project creates expected output subdirectories."""
        parsed = _make_storyboard(segments=[
            _make_segment(seg_id="seg-1"),
        ])
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            init_project(parsed, config)

            for subdir in ["segments", "narration", "graphics", "final"]:
                assert (config.output_dir / subdir).exists()

    def test_init_project_saves_state(self):
        """init_project persists state to disk."""
        parsed = _make_storyboard(segments=[
            _make_segment(seg_id="seg-1"),
            _make_segment(seg_id="seg-2", start="0:15", end="0:30"),
        ])
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            state = init_project(parsed, config)

            assert config.state_path.exists()
            loaded = ProductionState.load(config.state_path)
            assert len(loaded.segment_statuses) == 2


class TestApplyVoiceLock:
    def test_apply_voice_lock_with_voice_lock(self):
        """Voice lock updates engine and voice when defaults are set."""
        from bee_video_editor.formats.models import VoiceLock
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            vl = VoiceLock(engine="elevenlabs", voice="Daniel")
            config.apply_voice_lock(vl)
            assert config.tts_engine == "elevenlabs"
            assert config.tts_voice == "Daniel"

    def test_apply_voice_lock_none(self):
        """None voice lock is a no-op."""
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d))
            config.apply_voice_lock(None)
            assert config.tts_engine == "edge"
            assert config.tts_voice is None

    def test_apply_voice_lock_doesnt_override_explicit(self):
        """Voice lock doesn't override explicitly set engine/voice."""
        from bee_video_editor.formats.models import VoiceLock
        with tempfile.TemporaryDirectory() as d:
            config = ProductionConfig(project_dir=Path(d), tts_engine="openai", tts_voice="alloy")
            vl = VoiceLock(engine="elevenlabs", voice="Daniel")
            config.apply_voice_lock(vl)
            assert config.tts_engine == "openai"
            assert config.tts_voice == "alloy"


class TestProductionStateLoadsOldFormat:
    def test_production_state_loads_old_format(self):
        """JSON with assembly_guide_path (old key) populates storyboard_path."""
        with tempfile.TemporaryDirectory() as d:
            state_path = Path(d) / "state.json"
            old_data = {
                "assembly_guide_path": "/old/path/guide.md",
                "phase": "parsed",
                "segment_statuses": [
                    {"index": 0, "time_range": "0:00-0:15", "segment_type": "REAL",
                     "status": "done", "output_file": None, "error": None},
                ],
            }
            state_path.write_text(json.dumps(old_data))

            loaded = ProductionState.load(state_path)
            assert loaded.storyboard_path == "/old/path/guide.md"
            assert loaded.phase == "parsed"
            assert len(loaded.segment_statuses) == 1
            assert loaded.segment_statuses[0].status == "done"
