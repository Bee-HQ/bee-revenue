"""Tests for the new format Pydantic models."""
import pytest
from pydantic import ValidationError

def test_project_config_minimal():
    from bee_video_editor.formats.models import ProjectConfig
    p = ProjectConfig(title="Test")
    assert p.title == "Test"
    assert p.version == 1
    assert p.voice_lock is None

def test_project_config_full():
    from bee_video_editor.formats.models import ProjectConfig
    p = ProjectConfig(**{
        "title": "The Murdaugh Murders", "version": 1,
        "voice_lock": {"engine": "elevenlabs", "voice": "Daniel", "model": "eleven_multilingual_v2"},
        "color_preset": "dark_crime",
        "default_transition": {"type": "dissolve", "duration": 1.0},
        "output": {"resolution": "1920x1080", "fps": 30, "codec": "h264", "crf": 18},
    })
    assert p.voice_lock.engine == "elevenlabs"
    assert p.default_transition.duration == 1.0
    assert p.output.fps == 30

def test_voice_lock_requires_engine_and_voice():
    from bee_video_editor.formats.models import VoiceLock
    vl = VoiceLock(engine="edge", voice="en-US-GuyNeural")
    assert vl.model is None
    with pytest.raises(ValidationError):
        VoiceLock(engine="edge")

def test_visual_entry_footage():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{"type": "FOOTAGE", "src": "footage/clip.mp4", "in": "00:02:14.500", "out": "00:02:29.500", "color": "surveillance", "ken_burns": "zoom_in"})
    assert v.type == "FOOTAGE"
    assert v.tc_in == "00:02:14.500"

def test_visual_entry_stock_with_query():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(type="STOCK", src=None, query="aerial farm dusk")
    assert v.src is None
    assert v.query == "aerial farm dusk"

def test_visual_entry_map():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{"type": "MAP", "style": "tactical", "center": [32.5916, -80.6754], "zoom": 13, "markers": [{"label": "Moselle"}]})
    assert v.center == [32.5916, -80.6754]

def test_audio_entry_types():
    from bee_video_editor.formats.models import AudioEntry
    real = AudioEntry(type="REAL_AUDIO", src="footage/clip.mp4", volume=0.6)
    music = AudioEntry(type="MUSIC", src="music/bg.mp3", volume=0.2, fade_in=2.0)
    sfx = AudioEntry(type="SFX", src="sfx/bang.wav", volume=0.8)
    nar = AudioEntry(type="NAR", engine="elevenlabs", voice="Daniel")
    assert real.volume == 0.6
    assert music.fade_in == 2.0
    assert sfx.type == "SFX"
    assert nar.engine == "elevenlabs"

def test_overlay_entry_types():
    from bee_video_editor.formats.models import OverlayEntry
    lt = OverlayEntry(type="LOWER_THIRD", text="Name", subtext="Role", duration=4.0, position="bottom-left")
    tm = OverlayEntry(type="TIMELINE_MARKER", date="June 7, 2021", description="10:07 PM")
    qc = OverlayEntry(type="QUOTE_CARD", quote="Some quote", author="Author")
    assert lt.position == "bottom-left"
    assert tm.date == "June 7, 2021"
    assert qc.author == "Author"

def test_segment_config_full():
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig(**{
        "visual": [{"type": "FOOTAGE", "src": "clip.mp4"}],
        "audio": [{"type": "REAL_AUDIO", "src": "clip.mp4", "volume": 0.6}],
        "overlay": [{"type": "LOWER_THIRD", "text": "Name"}],
        "captions": {"style": "karaoke", "font_size": 42},
        "transition_in": {"type": "dissolve", "duration": 1.0},
    })
    assert len(sc.visual) == 1
    assert sc.captions.style == "karaoke"
    assert sc.transition_in.type == "dissolve"

def test_segment_config_empty():
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig()
    assert sc.visual == []
    assert sc.captions is None

def test_segment_config_preserves_unknown_keys():
    from bee_video_editor.formats.models import SegmentConfig
    sc = SegmentConfig(**{"visual": [], "future_feature": {"key": "value"}})
    extras = sc.model_dump(exclude_none=True)
    assert "future_feature" in extras

def test_visual_entry_serializes_in_as_in():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{"type": "FOOTAGE", "src": "clip.mp4", "in": "00:01:00.000", "out": "00:02:00.000"})
    d = v.model_dump(by_alias=True, exclude_none=True)
    assert "in" in d
    assert "tc_in" not in d

def test_visual_entry_download_fields():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(**{
        "type": "FOOTAGE",
        "src": "footage/clip.mp4",
        "download_url": "https://youtube.com/watch?v=abc123",
        "download_trim": "2:14-2:29",
    })
    assert v.download_url == "https://youtube.com/watch?v=abc123"
    assert v.download_trim == "2:14-2:29"
    d = v.model_dump(by_alias=True, exclude_none=True)
    assert "download_url" in d

def test_visual_entry_pexels_url():
    from bee_video_editor.formats.models import VisualEntry
    v = VisualEntry(type="STOCK", src=None, query="aerial farm", pexels_url="https://www.pexels.com/video/12345/")
    assert v.pexels_url is not None

def test_audio_entry_download_url():
    from bee_video_editor.formats.models import AudioEntry
    a = AudioEntry(type="MUSIC", download_url="https://example.com/track.mp3")
    assert a.download_url == "https://example.com/track.mp3"
