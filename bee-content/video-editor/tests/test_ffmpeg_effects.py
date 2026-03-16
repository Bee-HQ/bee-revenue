"""Tests for FFmpeg effects, transitions, color presets, and filter construction."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bee_video_editor.processors.ffmpeg import (
    COLOR_GRADE_PRESETS,
    XFADE_TRANSITIONS,
    FFmpegError,
)


# --- Color grade preset tests ---

class TestColorGradePresets:
    def test_all_presets_are_strings(self):
        for name, filt in COLOR_GRADE_PRESETS.items():
            assert isinstance(name, str)
            assert isinstance(filt, str)
            assert len(filt) > 0

    def test_original_presets_preserved(self):
        assert "dark_crime" in COLOR_GRADE_PRESETS
        assert "warm_victim" in COLOR_GRADE_PRESETS
        assert "bodycam" in COLOR_GRADE_PRESETS

    def test_new_presets_exist(self):
        expected = [
            "noir", "sepia", "cold_blue", "vintage",
            "bleach_bypass", "night_vision", "golden_hour",
            "surveillance", "vhs",
        ]
        for name in expected:
            assert name in COLOR_GRADE_PRESETS, f"Missing preset: {name}"

    def test_noir_is_zero_saturation(self):
        assert "saturation=0.0" in COLOR_GRADE_PRESETS["noir"]

    def test_sepia_uses_colorchannelmixer(self):
        assert "colorchannelmixer" in COLOR_GRADE_PRESETS["sepia"]

    def test_surveillance_has_noise(self):
        assert "noise=" in COLOR_GRADE_PRESETS["surveillance"]


# --- Transition list tests ---

class TestXfadeTransitions:
    def test_transitions_is_list(self):
        assert isinstance(XFADE_TRANSITIONS, list)
        assert len(XFADE_TRANSITIONS) > 20

    def test_common_transitions_present(self):
        for t in ["fade", "wipeleft", "wiperight", "dissolve", "fadeblack", "fadewhite"]:
            assert t in XFADE_TRANSITIONS, f"Missing transition: {t}"

    def test_all_transitions_are_strings(self):
        for t in XFADE_TRANSITIONS:
            assert isinstance(t, str)
            assert len(t) > 0


# --- color_grade function tests ---

class TestColorGrade:
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_applies_preset_filter(self, mock_run):
        from bee_video_editor.processors.ffmpeg import color_grade

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            color_grade(inp, out, preset="sepia")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "colorchannelmixer" in args[vf_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_unknown_preset_falls_back(self, mock_run):
        from bee_video_editor.processors.ffmpeg import color_grade

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            color_grade(inp, out, preset="nonexistent")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            # Falls back to dark_crime
            assert "brightness=-0.08" in args[vf_idx + 1]


# --- xfade function tests ---

class TestXfade:
    @patch("bee_video_editor.processors.ffmpeg.get_duration", return_value=10.0)
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_builds_correct_filter(self, mock_run, mock_dur):
        from bee_video_editor.processors.ffmpeg import xfade

        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "a.mp4"
            b = Path(d) / "b.mp4"
            out = Path(d) / "out.mp4"
            a.touch()
            b.touch()

            xfade(a, b, out, transition="dissolve", duration=1.5)

            args = mock_run.call_args[0][0]
            fc_idx = args.index("-filter_complex")
            fc = args[fc_idx + 1]
            assert "xfade=transition=dissolve" in fc
            assert "duration=1.5" in fc
            assert "offset=8.5" in fc  # 10.0 - 1.5

    @patch("bee_video_editor.processors.ffmpeg.get_duration", return_value=5.0)
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_invalid_transition_falls_back_to_fade(self, mock_run, mock_dur):
        from bee_video_editor.processors.ffmpeg import xfade

        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "a.mp4"
            b = Path(d) / "b.mp4"
            out = Path(d) / "out.mp4"
            a.touch()
            b.touch()

            xfade(a, b, out, transition="nonexistent")

            args = mock_run.call_args[0][0]
            fc_idx = args.index("-filter_complex")
            assert "transition=fade" in args[fc_idx + 1]


# --- drawtext function tests ---

class TestDrawtext:
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_basic_text(self, mock_run):
        from bee_video_editor.processors.ffmpeg import drawtext

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            drawtext(inp, out, text="Hello World")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            vf = args[vf_idx + 1]
            assert "drawtext=" in vf
            assert "Hello World" in vf

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_text_with_box(self, mock_run):
        from bee_video_editor.processors.ffmpeg import drawtext

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            drawtext(inp, out, text="Test", box=True)

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            vf = args[vf_idx + 1]
            assert "box=1" in vf
            assert "boxcolor=black@0.6" in vf

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_text_with_time_window(self, mock_run):
        from bee_video_editor.processors.ffmpeg import drawtext

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            drawtext(inp, out, text="Timed", start=2.0, end=5.0)

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            vf = args[vf_idx + 1]
            assert "enable=" in vf
            assert "between" in vf


# --- speed function tests ---

class TestSpeed:
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_double_speed(self, mock_run):
        from bee_video_editor.processors.ffmpeg import speed

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            speed(inp, out, factor=2.0)

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "setpts=0.5*PTS" in args[vf_idx + 1]
            af_idx = args.index("-af")
            assert "atempo=2.0" in args[af_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_slow_motion(self, mock_run):
        from bee_video_editor.processors.ffmpeg import speed

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            speed(inp, out, factor=0.5)

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "setpts=2.0*PTS" in args[vf_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_extreme_speed_chains_atempo(self, mock_run):
        from bee_video_editor.processors.ffmpeg import speed

        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "in.mp4"
            out = Path(d) / "out.mp4"
            inp.touch()

            speed(inp, out, factor=4.0)

            args = mock_run.call_args[0][0]
            af_idx = args.index("-af")
            af = args[af_idx + 1]
            # Should chain atempo filters since 4.0 > 2.0
            assert "atempo=2.0" in af
            assert af.count("atempo") >= 2


# --- picture_in_picture function tests ---

class TestPictureInPicture:
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_builds_pip_filter(self, mock_run):
        from bee_video_editor.processors.ffmpeg import picture_in_picture

        with tempfile.TemporaryDirectory() as d:
            main = Path(d) / "main.mp4"
            pip = Path(d) / "pip.mp4"
            out = Path(d) / "out.mp4"
            main.touch()
            pip.touch()

            picture_in_picture(main, pip, out, pip_width=320)

            args = mock_run.call_args[0][0]
            fc_idx = args.index("-filter_complex")
            fc = args[fc_idx + 1]
            assert "scale=320:-1" in fc
            assert "overlay=" in fc


# --- concat_with_transitions function tests ---

class TestConcatWithTransitions:
    @patch("bee_video_editor.processors.ffmpeg.get_duration", side_effect=[5.0, 5.0, 5.0])
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_three_clips_two_transitions(self, mock_run, mock_dur):
        from bee_video_editor.processors.ffmpeg import concat_with_transitions

        with tempfile.TemporaryDirectory() as d:
            clips = [Path(d) / f"{i}.mp4" for i in range(3)]
            for c in clips:
                c.touch()
            out = Path(d) / "out.mp4"

            concat_with_transitions(clips, out, transition="dissolve", transition_duration=1.0)

            args = mock_run.call_args[0][0]
            fc_idx = args.index("-filter_complex")
            fc = args[fc_idx + 1]
            assert fc.count("xfade") == 2
            assert fc.count("acrossfade") == 2

    @patch("bee_video_editor.processors.ffmpeg.concat_segments")
    def test_single_clip_falls_back(self, mock_concat):
        from bee_video_editor.processors.ffmpeg import concat_with_transitions

        with tempfile.TemporaryDirectory() as d:
            clip = Path(d) / "only.mp4"
            clip.touch()
            out = Path(d) / "out.mp4"

            concat_with_transitions([clip], out, transition="fade")

            mock_concat.assert_called_once()


# --- Ken Burns tests ---

class TestKenBurnsEffects:
    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_pan_right(self, mock_run):
        from bee_video_editor.processors.ffmpeg import image_to_video

        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / "img.jpg"
            out = Path(d) / "out.mp4"
            img.touch()

            image_to_video(img, out, duration=3.0, ken_burns="pan_right")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "zoompan" in args[vf_idx + 1]
            assert "max(x-1,0)" in args[vf_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_pan_up(self, mock_run):
        from bee_video_editor.processors.ffmpeg import image_to_video

        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / "img.jpg"
            out = Path(d) / "out.mp4"
            img.touch()

            image_to_video(img, out, duration=3.0, ken_burns="pan_up")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "zoompan" in args[vf_idx + 1]
            assert "max(y-1,0)" in args[vf_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_pan_down(self, mock_run):
        from bee_video_editor.processors.ffmpeg import image_to_video

        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / "img.jpg"
            out = Path(d) / "out.mp4"
            img.touch()

            image_to_video(img, out, duration=3.0, ken_burns="pan_down")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            assert "zoompan" in args[vf_idx + 1]

    @patch("bee_video_editor.processors.ffmpeg.run_ffmpeg")
    def test_zoom_in_pan_right(self, mock_run):
        from bee_video_editor.processors.ffmpeg import image_to_video

        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / "img.jpg"
            out = Path(d) / "out.mp4"
            img.touch()

            image_to_video(img, out, duration=3.0, ken_burns="zoom_in_pan_right")

            args = mock_run.call_args[0][0]
            vf_idx = args.index("-vf")
            vf = args[vf_idx + 1]
            assert "zoompan" in vf
            assert "zoom+0.0015" in vf
