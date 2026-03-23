# AI Dubbing Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `bee-video dub` CLI that takes an English YouTube compilation, translates and dubs it into Spanish (POC), with voice cloning and subtitles.

**Architecture:** 8 modular services communicating through a shared project directory. Each service is a separate module in `services/dub/`, exposed as a typer subcommand under `bee-video dub`. Services are idempotent — re-running skips completed work.

**Tech Stack:** Python 3.11+, typer, yt-dlp, openai-whisper, pyannote/whisperx, demucs, anthropic (Claude), elevenlabs, FFmpeg, pysubs2

**Spec:** `docs/superpowers/specs/2026-03-22-dub-pipeline-design.md`

---

## File Structure

```
src/bee_video_editor/
  adapters/
    cli.py                          # Modify: register dub command group
    cli_dub.py                      # Create: dub subcommand definitions
  services/
    dub/
      __init__.py                   # Create: package init
      models.py                     # Create: DubProject, DubConfig, DubSegment Pydantic models
      status.py                     # Create: status.json read/write, segment state tracking
      download.py                   # Create: yt-dlp wrapper
      transcribe.py                 # Create: Whisper API wrapper
      diarize.py                    # Create: speaker diarization + sample extraction
      separate.py                   # Create: demucs vocal separation
      translate.py                  # Create: Claude/DeepL/Google translation
      voices.py                     # Create: ElevenLabs voice cloning + mapping
      tts.py                        # Create: multilingual TTS generation
      compose.py                    # Create: audio mixing + subtitle burn
      pipeline.py                   # Create: orchestrate all services (dub run)
  processors/
    ffmpeg.py                       # Modify: add extract_audio()

tests/
  test_dub_models.py                # Create: model + config tests
  test_dub_status.py                # Create: status tracking tests
  test_dub_download.py              # Create: download service tests
  test_dub_transcribe.py            # Create: transcription tests
  test_dub_diarize.py               # Create: diarization tests
  test_dub_separate.py              # Create: vocal separation tests
  test_dub_translate.py             # Create: translation tests
  test_dub_voices.py                # Create: voice cloning tests
  test_dub_tts.py                   # Create: TTS generation tests
  test_dub_compose.py               # Create: compositor tests
  test_dub_pipeline.py              # Create: end-to-end pipeline tests

pyproject.toml                      # Modify: add dub extras
```

---

## Task 1: Dub Models & Config

**Files:**
- Create: `src/bee_video_editor/services/dub/__init__.py`
- Create: `src/bee_video_editor/services/dub/models.py`
- Test: `tests/test_dub_models.py`

- [ ] **Step 1: Write failing tests for DubConfig and DubSegment models**

```python
# tests/test_dub_models.py
import json
from pathlib import Path
from bee_video_editor.services.dub.models import DubConfig, DubSegment, SegmentState


class TestDubConfig:
    def test_default_config(self):
        config = DubConfig()
        assert config.languages == ["es"]
        assert config.transcription.engine == "whisper"
        assert config.translation.engine == "claude"
        assert config.voices.mode == "clone"
        assert config.tts.engine == "elevenlabs"
        assert config.compositor.target_lufs == -14.0

    def test_load_from_json(self, tmp_path):
        data = {
            "source": "source.mp4",
            "languages": ["es", "de"],
            "translation": {"engine": "deepl"},
        }
        config_path = tmp_path / "dub.json"
        config_path.write_text(json.dumps(data))
        config = DubConfig.load(config_path)
        assert config.source == "source.mp4"
        assert config.languages == ["es", "de"]
        assert config.translation.engine == "deepl"
        # defaults preserved for unset fields
        assert config.voices.mode == "clone"

    def test_save_config(self, tmp_path):
        config = DubConfig(source="test.mp4", languages=["ar"])
        out = tmp_path / "dub.json"
        config.save(out)
        loaded = json.loads(out.read_text())
        assert loaded["source"] == "test.mp4"
        assert loaded["languages"] == ["ar"]


class TestDubSegment:
    def test_segment_defaults(self):
        seg = DubSegment(
            id="seg_001",
            text="Hello world",
            speaker="speaker_0",
            start_ms=0,
            end_ms=5000,
        )
        assert seg.state == SegmentState.PENDING
        assert seg.translated_text is None
        assert seg.target_duration_ms == 5000

    def test_segment_duration(self):
        seg = DubSegment(
            id="seg_001", text="Hi", speaker="speaker_0",
            start_ms=1000, end_ms=3500,
        )
        assert seg.target_duration_ms == 2500
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bee_video_editor.services.dub'`

- [ ] **Step 3: Implement models**

```python
# src/bee_video_editor/services/dub/__init__.py
"""AI dubbing pipeline services."""

# src/bee_video_editor/services/dub/models.py
from __future__ import annotations
import json
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class SegmentState(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TranscriptionConfig(BaseModel):
    engine: str = "whisper"
    model: str = "large-v3"


class DiarizationConfig(BaseModel):
    engine: str = "whisperx"
    min_speakers: int = 2
    max_speakers: int = 10
    min_sample_duration: int = 30


class SeparationConfig(BaseModel):
    engine: str = "demucs"
    model: str = "htdemucs"


class TranslationConfig(BaseModel):
    engine: str = "claude"
    model: str = "claude-sonnet-4-6"
    style: str = (
        "Translate as a native speaker telling a funny dating story. "
        "Keep slang natural. Don't be literal — capture the vibe."
    )


class VoicesConfig(BaseModel):
    mode: str = "clone"
    engine: str = "elevenlabs"
    overrides: dict[str, str] = Field(default_factory=dict)


class TTSConfig(BaseModel):
    engine: str = "elevenlabs"
    model: str = "eleven_multilingual_v2"
    stability: float = 0.5
    similarity_boost: float = 0.75


class CompositorConfig(BaseModel):
    keep_background_audio: bool = True
    background_volume: float = 0.05
    subtitles: bool = True
    subtitle_style: str = "phrase"
    target_lufs: float = -14.0


class DubConfig(BaseModel):
    source: str | None = None
    languages: list[str] = Field(default_factory=lambda: ["es"])
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    diarization: DiarizationConfig = Field(default_factory=DiarizationConfig)
    separation: SeparationConfig = Field(default_factory=SeparationConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    voices: VoicesConfig = Field(default_factory=VoicesConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    compositor: CompositorConfig = Field(default_factory=CompositorConfig)

    @classmethod
    def load(cls, path: Path) -> DubConfig:
        data = json.loads(path.read_text())
        return cls(**data)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.model_dump(), indent=2))


class DubSegment(BaseModel):
    id: str
    text: str
    speaker: str
    start_ms: int
    end_ms: int
    state: SegmentState = SegmentState.PENDING
    translated_text: str | None = None
    error: str | None = None

    @property
    def target_duration_ms(self) -> int:
        return self.end_ms - self.start_ms
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_models.py -v`
Expected: PASS (all 5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/ tests/test_dub_models.py
git commit -m "feat(dub): add DubConfig and DubSegment models"
```

---

## Task 2: Status Tracking

**Files:**
- Create: `src/bee_video_editor/services/dub/status.py`
- Test: `tests/test_dub_status.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_status.py
import json
from pathlib import Path
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.models import SegmentState


class TestStatusTracker:
    def test_init_creates_file(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        assert tracker.path.exists()

    def test_set_and_get(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "transcribe", SegmentState.COMPLETED)
        assert tracker.get("seg_001", "transcribe") == SegmentState.COMPLETED

    def test_get_unknown_returns_pending(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        assert tracker.get("seg_999", "transcribe") == SegmentState.PENDING

    def test_set_failed_with_error(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.FAILED, error="API timeout")
        assert tracker.get("seg_001", "tts") == SegmentState.FAILED
        assert tracker.get_error("seg_001", "tts") == "API timeout"

    def test_persistence(self, tmp_path):
        path = tmp_path / "status.json"
        tracker = StatusTracker(path)
        tracker.set("seg_001", "translate", SegmentState.COMPLETED)
        # Load from disk
        tracker2 = StatusTracker(path)
        assert tracker2.get("seg_001", "translate") == SegmentState.COMPLETED

    def test_pending_segments(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.COMPLETED)
        tracker.set("seg_002", "tts", SegmentState.PENDING)
        tracker.set("seg_003", "tts", SegmentState.FAILED)
        pending = tracker.incomplete("tts", ["seg_001", "seg_002", "seg_003"])
        assert pending == ["seg_002", "seg_003"]

    def test_retry_failed_resets(self, tmp_path):
        tracker = StatusTracker(tmp_path / "status.json")
        tracker.set("seg_001", "tts", SegmentState.FAILED, error="timeout")
        tracker.retry_failed("tts")
        assert tracker.get("seg_001", "tts") == SegmentState.PENDING
        assert tracker.get_error("seg_001", "tts") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_status.py -v`
Expected: FAIL

- [ ] **Step 3: Implement StatusTracker**

```python
# src/bee_video_editor/services/dub/status.py
from __future__ import annotations
import json
from pathlib import Path
from bee_video_editor.services.dub.models import SegmentState


class StatusTracker:
    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            self._data = json.loads(path.read_text())
        else:
            self._data = {}
            self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    def _key(self, segment_id: str, step: str) -> str:
        return f"{segment_id}:{step}"

    def set(
        self, segment_id: str, step: str, state: SegmentState, error: str | None = None
    ) -> None:
        key = self._key(segment_id, step)
        self._data[key] = {"state": state.value, "error": error}
        self._save()

    def get(self, segment_id: str, step: str) -> SegmentState:
        key = self._key(segment_id, step)
        entry = self._data.get(key)
        if entry is None:
            return SegmentState.PENDING
        return SegmentState(entry["state"])

    def get_error(self, segment_id: str, step: str) -> str | None:
        key = self._key(segment_id, step)
        entry = self._data.get(key)
        return entry.get("error") if entry else None

    def incomplete(self, step: str, segment_ids: list[str]) -> list[str]:
        return [
            sid for sid in segment_ids
            if self.get(sid, step) != SegmentState.COMPLETED
        ]

    def retry_failed(self, step: str) -> None:
        for key, entry in list(self._data.items()):
            if key.endswith(f":{step}") and entry["state"] == SegmentState.FAILED.value:
                entry["state"] = SegmentState.PENDING.value
                entry["error"] = None
        self._save()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_status.py -v`
Expected: PASS (all 7 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/status.py tests/test_dub_status.py
git commit -m "feat(dub): add StatusTracker for per-segment state tracking"
```

---

## Task 3: FFmpeg extract_audio

**Files:**
- Modify: `src/bee_video_editor/processors/ffmpeg.py`
- Test: `tests/test_ffmpeg_effects.py`

- [ ] **Step 1: Write failing test**

```python
# Add to tests/test_ffmpeg_effects.py
from bee_video_editor.processors.ffmpeg import extract_audio

class TestExtractAudio:
    def test_extract_audio_command(self, tmp_path):
        src = tmp_path / "video.mp4"
        src.touch()
        out = tmp_path / "audio.mp3"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            extract_audio(src, out)
            cmd = mock_run.call_args[0][0]
            assert "ffmpeg" in cmd[0]
            assert "-vn" in cmd
            assert str(out) in cmd
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_ffmpeg_effects.py::TestExtractAudio -v`
Expected: FAIL — `ImportError: cannot import name 'extract_audio'`

- [ ] **Step 3: Implement extract_audio**

Add to `src/bee_video_editor/processors/ffmpeg.py`:

```python
def extract_audio(
    input_path: str | Path,
    output_path: str | Path,
    codec: str = "mp3",
    bitrate: str = "192k",
) -> Path:
    """Extract audio stream from a video file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vn", "-acodec", codec, "-b:a", bitrate,
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise FFmpegError(f"extract_audio failed: {result.stderr}")
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_ffmpeg_effects.py::TestExtractAudio -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/processors/ffmpeg.py tests/test_ffmpeg_effects.py
git commit -m "feat(ffmpeg): add extract_audio function"
```

---

## Task 4: Download Service

**Files:**
- Create: `src/bee_video_editor/services/dub/download.py`
- Test: `tests/test_dub_download.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_download.py
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.download import download_video


class TestDownload:
    def test_download_calls_ytdlp(self, tmp_path):
        out = tmp_path / "source.mp4"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            download_video("https://youtube.com/watch?v=abc123", out)
            cmd = mock_run.call_args[0][0]
            assert "yt-dlp" in cmd[0]
            assert "https://youtube.com/watch?v=abc123" in cmd

    def test_skip_if_exists(self, tmp_path):
        out = tmp_path / "source.mp4"
        out.write_bytes(b"existing")
        with patch("subprocess.run") as mock_run:
            result = download_video("https://youtube.com/watch?v=abc", out)
            mock_run.assert_not_called()
            assert result == out

    def test_raises_on_failure(self, tmp_path):
        out = tmp_path / "source.mp4"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="error")
            import pytest
            with pytest.raises(RuntimeError):
                download_video("https://youtube.com/watch?v=abc", out)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_download.py -v`
Expected: FAIL

- [ ] **Step 3: Implement download service**

```python
# src/bee_video_editor/services/dub/download.py
from __future__ import annotations
import subprocess
from pathlib import Path


def download_video(url: str, output_path: Path) -> Path:
    """Download a video from YouTube using yt-dlp."""
    if output_path.exists() and output_path.stat().st_size > 0:
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_download.py -v`
Expected: PASS (all 3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/download.py tests/test_dub_download.py
git commit -m "feat(dub): add download service (yt-dlp)"
```

---

## Task 5: Transcription Service

**Files:**
- Create: `src/bee_video_editor/services/dub/transcribe.py`
- Test: `tests/test_dub_transcribe.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_transcribe.py
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.transcribe import transcribe_audio


class TestTranscribe:
    def test_returns_segments(self, tmp_path):
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "transcript.json"
        with patch("bee_video_editor.services.dub.transcribe._whisper_api") as mock_api:
            mock_api.return_value = [
                {"id": 0, "start_ms": 0, "end_ms": 2500, "text": "Hello there"},
                {"id": 1, "start_ms": 2500, "end_ms": 5000, "text": "How are you"},
            ]
            result = transcribe_audio(audio_path, output_path, engine="whisper")
            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 2
            assert data["segments"][0]["text"] == "Hello there"
            assert data["segments"][0]["start_ms"] == 0
            assert data["segments"][0]["end_ms"] == 2500

    def test_skip_if_exists(self, tmp_path):
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "transcript.json"
        output_path.write_text(json.dumps({"segments": []}))
        with patch("bee_video_editor.services.dub.transcribe._whisper_api") as mock_api:
            transcribe_audio(audio_path, output_path)
            mock_api.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_transcribe.py -v`
Expected: FAIL

- [ ] **Step 3: Implement transcription service**

```python
# src/bee_video_editor/services/dub/transcribe.py
from __future__ import annotations
import json
import os
from pathlib import Path
from openai import OpenAI


def transcribe_audio(
    audio_path: Path,
    output_path: Path,
    engine: str = "whisper",
    model: str = "large-v3",
) -> Path:
    """Transcribe audio to timestamped segments."""
    if output_path.exists():
        return output_path
    if engine == "whisper":
        segments = _whisper_api(audio_path, model)
    else:
        raise ValueError(f"Unknown transcription engine: {engine}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments}, indent=2))
    return output_path


def _whisper_api(audio_path: Path, model: str) -> list[dict]:
    """Transcribe using OpenAI Whisper API."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
    return [
        {
            "id": i,
            "start_ms": int(seg.start * 1000),
            "end_ms": int(seg.end * 1000),
            "text": seg.text.strip(),
        }
        for i, seg in enumerate(response.segments)
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_transcribe.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/transcribe.py tests/test_dub_transcribe.py
git commit -m "feat(dub): add transcription service (Whisper API)"
```

---

## Task 6: Diarization Service

**Files:**
- Create: `src/bee_video_editor/services/dub/diarize.py`
- Test: `tests/test_dub_diarize.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_diarize.py
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.diarize import diarize_segments


class TestDiarize:
    def _make_transcript(self, tmp_path):
        transcript = {
            "segments": [
                {"id": 0, "start_ms": 0, "end_ms": 5000, "text": "Welcome to the show"},
                {"id": 1, "start_ms": 5000, "end_ms": 10000, "text": "Thanks for having me"},
                {"id": 2, "start_ms": 10000, "end_ms": 15000, "text": "So tell us what happened"},
            ]
        }
        path = tmp_path / "transcript.json"
        path.write_text(json.dumps(transcript))
        return path

    def test_assigns_speakers(self, tmp_path):
        transcript_path = self._make_transcript(tmp_path)
        audio_path = tmp_path / "source.mp4"
        audio_path.touch()
        output_path = tmp_path / "diarization.json"
        voices_dir = tmp_path / "voices"

        with patch("bee_video_editor.services.dub.diarize._diarize_pyannote") as mock:
            mock.return_value = [
                {"start_ms": 0, "end_ms": 5000, "speaker": "speaker_0"},
                {"start_ms": 5000, "end_ms": 10000, "speaker": "speaker_1"},
                {"start_ms": 10000, "end_ms": 15000, "speaker": "speaker_0"},
            ]
            result = diarize_segments(
                audio_path, transcript_path, output_path, voices_dir
            )
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 3
            assert data["segments"][0]["speaker"] == "speaker_0"
            assert data["segments"][1]["speaker"] == "speaker_1"
            assert data["speakers"] == ["speaker_0", "speaker_1"]

    def test_skip_if_exists(self, tmp_path):
        transcript_path = self._make_transcript(tmp_path)
        output_path = tmp_path / "diarization.json"
        output_path.write_text(json.dumps({"segments": [], "speakers": []}))
        with patch("bee_video_editor.services.dub.diarize._diarize_pyannote") as mock:
            diarize_segments(
                tmp_path / "source.mp4", transcript_path, output_path, tmp_path / "voices"
            )
            mock.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_diarize.py -v`
Expected: FAIL

- [ ] **Step 3: Implement diarization service**

```python
# src/bee_video_editor/services/dub/diarize.py
from __future__ import annotations
import json
from pathlib import Path
from bee_video_editor.processors.ffmpeg import extract_audio


def diarize_segments(
    audio_path: Path,
    transcript_path: Path,
    output_path: Path,
    voices_dir: Path,
    engine: str = "pyannote",
    min_speakers: int = 2,
    max_speakers: int = 10,
    min_sample_duration: int = 30,
) -> Path:
    """Assign speakers to transcript segments and extract voice samples."""
    if output_path.exists():
        return output_path

    transcript = json.loads(transcript_path.read_text())
    segments = transcript["segments"]

    if engine == "pyannote":
        speaker_turns = _diarize_pyannote(audio_path, min_speakers, max_speakers)
    else:
        raise ValueError(f"Unknown diarization engine: {engine}")

    # Assign speakers to transcript segments by overlap
    for seg in segments:
        seg["speaker"] = _best_speaker(seg, speaker_turns)

    speakers = sorted(set(seg["speaker"] for seg in segments))

    # Extract voice samples
    voices_dir.mkdir(parents=True, exist_ok=True)
    _extract_voice_samples(audio_path, segments, speakers, voices_dir, min_sample_duration)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments, "speakers": speakers}, indent=2))
    return output_path


def _best_speaker(segment: dict, turns: list[dict]) -> str:
    """Find the speaker with most overlap for a given segment."""
    best = "speaker_unknown"
    best_overlap = 0
    for turn in turns:
        overlap_start = max(segment["start_ms"], turn["start_ms"])
        overlap_end = min(segment["end_ms"], turn["end_ms"])
        overlap = max(0, overlap_end - overlap_start)
        if overlap > best_overlap:
            best_overlap = overlap
            best = turn["speaker"]
    return best


def _diarize_pyannote(audio_path: Path, min_speakers: int, max_speakers: int) -> list[dict]:
    """Run pyannote speaker diarization."""
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    diarization = pipeline(str(audio_path), min_speakers=min_speakers, max_speakers=max_speakers)
    turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        turns.append({
            "start_ms": int(turn.start * 1000),
            "end_ms": int(turn.end * 1000),
            "speaker": speaker,
        })
    return turns


def _extract_voice_samples(
    audio_path: Path,
    segments: list[dict],
    speakers: list[str],
    voices_dir: Path,
    min_duration: int,
) -> None:
    """Extract clean audio samples per speaker for voice cloning."""
    import subprocess
    for speaker in speakers:
        speaker_segs = [s for s in segments if s["speaker"] == speaker]
        speaker_segs.sort(key=lambda s: s["end_ms"] - s["start_ms"], reverse=True)
        # Collect segments until we have enough duration
        collected = []
        total_ms = 0
        for seg in speaker_segs:
            collected.append(seg)
            total_ms += seg["end_ms"] - seg["start_ms"]
            if total_ms >= min_duration * 1000:
                break
        if not collected:
            continue
        # Extract and concat samples
        sample_path = voices_dir / f"{speaker}.mp3"
        parts = []
        for i, seg in enumerate(collected):
            part = voices_dir / f"_tmp_{speaker}_{i}.mp3"
            start_s = seg["start_ms"] / 1000
            duration_s = (seg["end_ms"] - seg["start_ms"]) / 1000
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(audio_path),
                 "-ss", str(start_s), "-t", str(duration_s),
                 "-vn", "-acodec", "mp3", "-b:a", "192k", str(part)],
                capture_output=True,
            )
            if part.exists():
                parts.append(part)
        if len(parts) == 1:
            parts[0].rename(sample_path)
        elif parts:
            list_file = voices_dir / f"_concat_{speaker}.txt"
            list_file.write_text("\n".join(f"file '{p.name}'" for p in parts))
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", str(list_file), "-c", "copy", str(sample_path)],
                capture_output=True,
            )
            list_file.unlink(missing_ok=True)
        # Cleanup temp files
        for p in parts:
            p.unlink(missing_ok=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_diarize.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/diarize.py tests/test_dub_diarize.py
git commit -m "feat(dub): add diarization service with voice sample extraction"
```

---

## Task 7: Vocal Separation Service

**Files:**
- Create: `src/bee_video_editor/services/dub/separate.py`
- Test: `tests/test_dub_separate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_separate.py
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.separate import separate_vocals


class TestSeparate:
    def test_calls_demucs(self, tmp_path):
        audio = tmp_path / "source.mp4"
        audio.touch()
        out_dir = tmp_path / "separated"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Simulate demucs output
            demucs_out = tmp_path / "separated" / "htdemucs" / "source"
            demucs_out.mkdir(parents=True)
            (demucs_out / "vocals.wav").write_bytes(b"vocals")
            (demucs_out / "no_vocals.wav").write_bytes(b"accompaniment")
            vocals, accompaniment = separate_vocals(audio, out_dir)
            assert vocals.exists()
            assert accompaniment.exists()

    def test_skip_if_exists(self, tmp_path):
        out_dir = tmp_path / "separated"
        out_dir.mkdir()
        (out_dir / "vocals.wav").write_bytes(b"v")
        (out_dir / "accompaniment.wav").write_bytes(b"a")
        with patch("subprocess.run") as mock_run:
            separate_vocals(tmp_path / "source.mp4", out_dir)
            mock_run.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_separate.py -v`
Expected: FAIL

- [ ] **Step 3: Implement separation service**

```python
# src/bee_video_editor/services/dub/separate.py
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path


def separate_vocals(
    audio_path: Path,
    output_dir: Path,
    model: str = "htdemucs",
) -> tuple[Path, Path]:
    """Separate vocals from accompaniment using demucs."""
    vocals_path = output_dir / "vocals.wav"
    accompaniment_path = output_dir / "accompaniment.wav"
    if vocals_path.exists() and accompaniment_path.exists():
        return vocals_path, accompaniment_path

    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["python", "-m", "demucs", "-n", model, "--two-stems", "vocals",
         "-o", str(output_dir), str(audio_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"demucs failed: {result.stderr}")

    # demucs outputs to output_dir/model_name/stem_name/
    stem_name = audio_path.stem
    demucs_dir = output_dir / model / stem_name
    shutil.move(str(demucs_dir / "vocals.wav"), str(vocals_path))
    shutil.move(str(demucs_dir / "no_vocals.wav"), str(accompaniment_path))
    # Cleanup demucs intermediate dirs
    shutil.rmtree(output_dir / model, ignore_errors=True)
    return vocals_path, accompaniment_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_separate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/separate.py tests/test_dub_separate.py
git commit -m "feat(dub): add vocal separation service (demucs)"
```

---

## Task 8: Translation Service

**Files:**
- Create: `src/bee_video_editor/services/dub/translate.py`
- Test: `tests/test_dub_translate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_translate.py
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.translate import translate_segments


class TestTranslate:
    def _make_diarization(self, tmp_path):
        data = {
            "segments": [
                {"id": 0, "start_ms": 0, "end_ms": 3000, "text": "Welcome to the show", "speaker": "speaker_0"},
                {"id": 1, "start_ms": 3000, "end_ms": 6000, "text": "Thanks for having me", "speaker": "speaker_1"},
            ],
            "speakers": ["speaker_0", "speaker_1"],
        }
        path = tmp_path / "diarization.json"
        path.write_text(json.dumps(data))
        return path

    def test_translates_all_segments(self, tmp_path):
        diarization_path = self._make_diarization(tmp_path)
        output_path = tmp_path / "translations" / "es.json"

        with patch("bee_video_editor.services.dub.translate._translate_claude") as mock:
            mock.return_value = [
                {"id": 0, "text": "Bienvenidos al show", "target_duration_ms": 3000},
                {"id": 1, "text": "Gracias por invitarme", "target_duration_ms": 3000},
            ]
            translate_segments(diarization_path, output_path, lang="es")
            data = json.loads(output_path.read_text())
            assert len(data["segments"]) == 2
            assert data["segments"][0]["translated_text"] == "Bienvenidos al show"
            assert data["segments"][0]["target_duration_ms"] == 3000
            assert data["lang"] == "es"

    def test_skip_if_exists(self, tmp_path):
        diarization_path = self._make_diarization(tmp_path)
        output_path = tmp_path / "translations" / "es.json"
        output_path.parent.mkdir(parents=True)
        output_path.write_text(json.dumps({"segments": [], "lang": "es"}))
        with patch("bee_video_editor.services.dub.translate._translate_claude") as mock:
            translate_segments(diarization_path, output_path, lang="es")
            mock.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_translate.py -v`
Expected: FAIL

- [ ] **Step 3: Implement translation service**

```python
# src/bee_video_editor/services/dub/translate.py
from __future__ import annotations
import json
import os
from pathlib import Path


LANG_NAMES = {
    "es": "Spanish", "de": "German", "ar": "Arabic",
    "pt": "Portuguese", "hi": "Hindi", "fr": "French",
}


def translate_segments(
    diarization_path: Path,
    output_path: Path,
    lang: str = "es",
    engine: str = "claude",
    model: str = "claude-sonnet-4-6",
    style: str | None = None,
) -> Path:
    """Translate diarized segments to target language."""
    if output_path.exists():
        return output_path

    diarization = json.loads(diarization_path.read_text())
    segments = diarization["segments"]

    if engine == "claude":
        translations = _translate_claude(segments, lang, model, style)
    else:
        raise ValueError(f"Unknown translation engine: {engine}")

    # Merge translations back into segments
    trans_map = {t["id"]: t for t in translations}
    for seg in segments:
        t = trans_map.get(seg["id"], {})
        seg["translated_text"] = t.get("text", seg["text"])
        seg["target_duration_ms"] = t.get("target_duration_ms", seg["end_ms"] - seg["start_ms"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments, "lang": lang}, indent=2))
    return output_path


def _translate_claude(
    segments: list[dict],
    lang: str,
    model: str,
    style: str | None,
) -> list[dict]:
    """Translate segments using Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    lang_name = LANG_NAMES.get(lang, lang)
    style_instruction = style or (
        f"Translate to {lang_name} as a native speaker telling a funny dating story. "
        "Keep slang natural. Don't be literal — capture the vibe."
    )
    # Batch segments into chunks to reduce API calls
    batch_size = 20
    results = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i + batch_size]
        segments_text = "\n".join(
            f'[{s["id"]}] ({s["end_ms"] - s["start_ms"]}ms) {s["text"]}' for s in batch
        )
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": (
                    f"{style_instruction}\n\n"
                    f"Translate each segment below to {lang_name}. "
                    "Return JSON array with objects: "
                    '{"id": <number>, "text": "<translated>", "target_duration_ms": <original_duration>}\n'
                    "Keep the same segment IDs. Match the original duration in target_duration_ms.\n\n"
                    f"Segments:\n{segments_text}"
                ),
            }],
        )
        text = response.content[0].text
        # Extract JSON from response
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            results.extend(json.loads(text[start:end]))
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_translate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/translate.py tests/test_dub_translate.py
git commit -m "feat(dub): add translation service (Claude API)"
```

---

## Task 9: Voice Cloning Service

**Files:**
- Create: `src/bee_video_editor/services/dub/voices.py`
- Test: `tests/test_dub_voices.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_voices.py
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.voices import setup_voices


class TestVoices:
    def test_clone_mode(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        (voices_dir / "speaker_0.mp3").write_bytes(b"audio")
        (voices_dir / "speaker_1.mp3").write_bytes(b"audio")
        manifest_path = voices_dir / "manifest.json"

        mock_voice = MagicMock()
        mock_voice.voice_id = "cloned_voice_123"
        with patch("bee_video_editor.services.dub.voices._clone_voice") as mock_clone:
            mock_clone.return_value = "cloned_voice_123"
            setup_voices(voices_dir, manifest_path, speakers=["speaker_0", "speaker_1"], mode="clone")
            manifest = json.loads(manifest_path.read_text())
            assert manifest["speaker_0"] == "cloned_voice_123"
            assert manifest["speaker_1"] == "cloned_voice_123"

    def test_mapped_mode_with_overrides(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        manifest_path = voices_dir / "manifest.json"
        overrides = {"speaker_0": "voice_abc", "speaker_1": "voice_def"}
        setup_voices(
            voices_dir, manifest_path,
            speakers=["speaker_0", "speaker_1"],
            mode="mapped", overrides=overrides,
        )
        manifest = json.loads(manifest_path.read_text())
        assert manifest["speaker_0"] == "voice_abc"
        assert manifest["speaker_1"] == "voice_def"

    def test_skip_if_manifest_exists(self, tmp_path):
        voices_dir = tmp_path / "voices"
        voices_dir.mkdir()
        manifest_path = voices_dir / "manifest.json"
        manifest_path.write_text(json.dumps({"speaker_0": "existing"}))
        with patch("bee_video_editor.services.dub.voices._clone_voice") as mock:
            setup_voices(voices_dir, manifest_path, speakers=["speaker_0"], mode="clone")
            mock.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_voices.py -v`
Expected: FAIL

- [ ] **Step 3: Implement voice service**

```python
# src/bee_video_editor/services/dub/voices.py
from __future__ import annotations
import json
import os
from pathlib import Path


def setup_voices(
    voices_dir: Path,
    manifest_path: Path,
    speakers: list[str],
    mode: str = "clone",
    overrides: dict[str, str] | None = None,
) -> Path:
    """Set up voice mappings — clone from samples or map to existing voices."""
    if manifest_path.exists():
        return manifest_path

    overrides = overrides or {}
    manifest = {}

    for speaker in speakers:
        if speaker in overrides:
            manifest[speaker] = overrides[speaker]
        elif mode == "clone":
            sample = voices_dir / f"{speaker}.mp3"
            if sample.exists():
                manifest[speaker] = _clone_voice(sample, speaker)
            else:
                manifest[speaker] = _default_voice(speaker)
        elif mode == "mapped":
            manifest[speaker] = _default_voice(speaker)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


def _clone_voice(sample_path: Path, name: str) -> str:
    """Clone a voice using ElevenLabs."""
    from elevenlabs import ElevenLabs
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)
    voice = client.clone(
        name=f"dub_{name}",
        files=[str(sample_path)],
    )
    return voice.voice_id


def _default_voice(speaker: str) -> str:
    """Return a default ElevenLabs voice ID based on speaker index."""
    defaults = ["Daniel", "Charlotte", "Brian", "Lily", "George"]
    idx = int(speaker.split("_")[-1]) if "_" in speaker else 0
    return defaults[idx % len(defaults)]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_voices.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/voices.py tests/test_dub_voices.py
git commit -m "feat(dub): add voice cloning/mapping service"
```

---

## Task 10: TTS Generation Service

**Files:**
- Create: `src/bee_video_editor/services/dub/tts.py`
- Test: `tests/test_dub_tts.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_tts.py
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.tts import generate_dubbed_audio
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.models import SegmentState


class TestTTS:
    def _setup(self, tmp_path):
        translations = {
            "lang": "es",
            "segments": [
                {"id": 0, "translated_text": "Hola", "speaker": "speaker_0",
                 "start_ms": 0, "end_ms": 3000, "target_duration_ms": 3000},
                {"id": 1, "translated_text": "Adios", "speaker": "speaker_1",
                 "start_ms": 3000, "end_ms": 6000, "target_duration_ms": 3000},
            ],
        }
        trans_path = tmp_path / "translations" / "es.json"
        trans_path.parent.mkdir(parents=True)
        trans_path.write_text(json.dumps(translations))
        manifest = {"speaker_0": "voice_a", "speaker_1": "voice_b"}
        manifest_path = tmp_path / "voices" / "manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest))
        tts_dir = tmp_path / "tts" / "es"
        status = StatusTracker(tmp_path / "status.json")
        return trans_path, manifest_path, tts_dir, status

    def test_generates_audio_per_segment(self, tmp_path):
        trans_path, manifest_path, tts_dir, status = self._setup(tmp_path)
        with patch("bee_video_editor.services.dub.tts._generate_segment") as mock:
            mock.return_value = True
            generate_dubbed_audio(trans_path, manifest_path, tts_dir, status)
            assert mock.call_count == 2

    def test_skips_completed_segments(self, tmp_path):
        trans_path, manifest_path, tts_dir, status = self._setup(tmp_path)
        status.set("seg_000", "tts", SegmentState.COMPLETED)
        tts_dir.mkdir(parents=True)
        (tts_dir / "seg_000.mp3").write_bytes(b"audio")
        with patch("bee_video_editor.services.dub.tts._generate_segment") as mock:
            mock.return_value = True
            generate_dubbed_audio(trans_path, manifest_path, tts_dir, status)
            # Only seg_001 should be generated
            assert mock.call_count == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_tts.py -v`
Expected: FAIL

- [ ] **Step 3: Implement TTS service**

```python
# src/bee_video_editor/services/dub/tts.py
from __future__ import annotations
import json
import os
from pathlib import Path
from bee_video_editor.services.dub.models import SegmentState
from bee_video_editor.services.dub.status import StatusTracker


def generate_dubbed_audio(
    translations_path: Path,
    manifest_path: Path,
    tts_dir: Path,
    status: StatusTracker,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> Path:
    """Generate TTS audio for each translated segment."""
    translations = json.loads(translations_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    tts_dir.mkdir(parents=True, exist_ok=True)

    for seg in translations["segments"]:
        seg_id = f"seg_{seg['id']:03d}"
        output_path = tts_dir / f"{seg_id}.mp3"

        if status.get(seg_id, "tts") == SegmentState.COMPLETED and output_path.exists():
            continue

        try:
            _generate_segment(
                text=seg["translated_text"],
                voice_id=manifest.get(seg["speaker"], "Daniel"),
                output_path=output_path,
                target_duration_ms=seg["target_duration_ms"],
                model=model,
                stability=stability,
                similarity_boost=similarity_boost,
            )
            status.set(seg_id, "tts", SegmentState.COMPLETED)
        except Exception as e:
            status.set(seg_id, "tts", SegmentState.FAILED, error=str(e))

    return tts_dir


def _generate_segment(
    text: str,
    voice_id: str,
    output_path: Path,
    target_duration_ms: int,
    model: str,
    stability: float,
    similarity_boost: float,
) -> None:
    """Generate TTS for a single segment using ElevenLabs."""
    from elevenlabs import ElevenLabs
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)

    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model,
        output_format="mp3_44100_128",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    # Adjust duration if needed (drift tolerance: 500ms)
    _adjust_duration(output_path, target_duration_ms)


def _adjust_duration(audio_path: Path, target_ms: int, tolerance_ms: int = 500) -> None:
    """Speed up/slow down audio to match target duration."""
    import subprocess
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return
    actual_ms = int(float(result.stdout.strip()) * 1000)
    drift = abs(actual_ms - target_ms)
    if drift <= tolerance_ms:
        return
    # Apply atempo to match target
    ratio = actual_ms / target_ms
    ratio = max(0.5, min(2.0, ratio))  # atempo range
    adjusted = audio_path.with_suffix(".adj.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(audio_path),
         "-filter:a", f"atempo={ratio}", str(adjusted)],
        capture_output=True,
    )
    if adjusted.exists():
        adjusted.replace(audio_path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_tts.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/tts.py tests/test_dub_tts.py
git commit -m "feat(dub): add TTS generation service with duration matching"
```

---

## Task 11: Compositor Service

**Files:**
- Create: `src/bee_video_editor/services/dub/compose.py`
- Test: `tests/test_dub_compose.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dub_compose.py
import json
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from bee_video_editor.services.dub.compose import compose_dubbed_video


class TestCompose:
    def _setup(self, tmp_path):
        translations = {
            "lang": "es",
            "segments": [
                {"id": 0, "translated_text": "Hola", "speaker": "speaker_0",
                 "start_ms": 0, "end_ms": 3000, "target_duration_ms": 3000},
                {"id": 1, "translated_text": "Adios", "speaker": "speaker_1",
                 "start_ms": 3000, "end_ms": 6000, "target_duration_ms": 3000},
            ],
        }
        trans_path = tmp_path / "translations" / "es.json"
        trans_path.parent.mkdir(parents=True)
        trans_path.write_text(json.dumps(translations))
        tts_dir = tmp_path / "tts" / "es"
        tts_dir.mkdir(parents=True)
        (tts_dir / "seg_000.mp3").write_bytes(b"audio0")
        (tts_dir / "seg_001.mp3").write_bytes(b"audio1")
        source = tmp_path / "source.mp4"
        source.touch()
        output = tmp_path / "output" / "es.mp4"
        return source, trans_path, tts_dir, output

    def test_compose_calls_ffmpeg(self, tmp_path):
        source, trans_path, tts_dir, output = self._setup(tmp_path)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            compose_dubbed_video(
                source_video=source,
                translations_path=trans_path,
                tts_dir=tts_dir,
                output_path=output,
            )
            assert mock_run.called

    def test_skip_if_exists(self, tmp_path):
        source, trans_path, tts_dir, output = self._setup(tmp_path)
        output.parent.mkdir(parents=True)
        output.write_bytes(b"existing")
        with patch("subprocess.run") as mock_run:
            compose_dubbed_video(source, trans_path, tts_dir, output)
            mock_run.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_compose.py -v`
Expected: FAIL

- [ ] **Step 3: Implement compositor service**

```python
# src/bee_video_editor/services/dub/compose.py
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from bee_video_editor.processors.captions import CaptionSegment, generate_captions_estimated, burn_captions
from bee_video_editor.processors.ffmpeg import normalize_loudness


def compose_dubbed_video(
    source_video: Path,
    translations_path: Path,
    tts_dir: Path,
    output_path: Path,
    accompaniment_path: Path | None = None,
    background_volume: float = 0.05,
    subtitles: bool = True,
    subtitle_style: str = "phrase",
    target_lufs: float = -14.0,
) -> Path:
    """Compose the final dubbed video from TTS segments + source video."""
    if output_path.exists() and output_path.stat().st_size > 0:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    translations = json.loads(translations_path.read_text())
    segments = translations["segments"]

    # Step 1: Build mixed audio track from TTS segments
    mixed_audio = output_path.parent / "mixed_audio.mp3"
    _mix_tts_segments(segments, tts_dir, mixed_audio)

    # Step 2: Optionally mix in background audio
    if accompaniment_path and accompaniment_path.exists():
        bg_mixed = output_path.parent / "bg_mixed.mp3"
        _mix_with_background(mixed_audio, accompaniment_path, bg_mixed, background_volume)
        mixed_audio = bg_mixed

    # Step 3: Normalize loudness
    normalized = output_path.parent / "normalized.mp3"
    normalize_loudness(mixed_audio, normalized, target_lufs)

    # Step 4: Replace audio in source video
    no_subs = output_path.parent / "no_subs.mp4"
    _replace_audio(source_video, normalized, no_subs)

    # Step 5: Generate and burn subtitles
    if subtitles:
        caption_segs = [
            CaptionSegment(
                text=seg["translated_text"],
                start_ms=seg["start_ms"],
                end_ms=seg["end_ms"],
                style_name="Narrator",
            )
            for seg in segments
        ]
        ass_path = output_path.parent / "captions.ass"
        generate_captions_estimated(caption_segs, ass_path, style=subtitle_style)
        burn_captions(no_subs, ass_path, output_path)
    else:
        no_subs.rename(output_path)

    # Cleanup temp files
    for f in [mixed_audio, normalized, no_subs]:
        if f.exists() and f != output_path:
            f.unlink(missing_ok=True)

    return output_path


def _mix_tts_segments(segments: list[dict], tts_dir: Path, output: Path) -> None:
    """Concatenate TTS segments with silence padding at correct timestamps."""
    # Build a filter that places each segment at its start_ms offset
    inputs = []
    filter_parts = []
    for i, seg in enumerate(segments):
        seg_file = tts_dir / f"seg_{seg['id']:03d}.mp3"
        if not seg_file.exists():
            continue
        inputs.extend(["-i", str(seg_file)])
        delay_ms = seg["start_ms"]
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

    if not filter_parts:
        return

    mix_inputs = "".join(f"[a{i}]" for i in range(len(filter_parts)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(filter_parts)}:duration=longest")
    filter_str = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, str(output)]
    subprocess.run(cmd, capture_output=True, text=True)


def _mix_with_background(
    foreground: Path, background: Path, output: Path, bg_volume: float
) -> None:
    """Mix foreground audio with background at given volume."""
    cmd = [
        "ffmpeg", "-y", "-i", str(foreground), "-i", str(background),
        "-filter_complex",
        f"[1:a]volume={bg_volume}[bg];[0:a][bg]amix=inputs=2:duration=first",
        "-ac", "2", str(output),
    ]
    subprocess.run(cmd, capture_output=True, text=True)


def _replace_audio(video: Path, audio: Path, output: Path) -> None:
    """Replace a video's audio track with a new audio file."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
        "-c:v", "copy", "-map", "0:v", "-map", "1:a",
        "-shortest", str(output),
    ]
    subprocess.run(cmd, capture_output=True, text=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_compose.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/compose.py tests/test_dub_compose.py
git commit -m "feat(dub): add compositor service with subtitle burn"
```

---

## Task 12: Pipeline Orchestrator

**Files:**
- Create: `src/bee_video_editor/services/dub/pipeline.py`
- Test: `tests/test_dub_pipeline.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_dub_pipeline.py
from unittest.mock import patch, MagicMock
from pathlib import Path
from bee_video_editor.services.dub.pipeline import run_pipeline
from bee_video_editor.services.dub.models import DubConfig


class TestPipeline:
    def test_runs_all_steps(self, tmp_path):
        config = DubConfig(source="source.mp4", languages=["es"])
        config.save(tmp_path / "dub.json")
        (tmp_path / "source.mp4").touch()
        with patch("bee_video_editor.services.dub.pipeline.download_video") as dl, \
             patch("bee_video_editor.services.dub.pipeline.transcribe_audio") as tr, \
             patch("bee_video_editor.services.dub.pipeline.diarize_segments") as di, \
             patch("bee_video_editor.services.dub.pipeline.separate_vocals") as sep, \
             patch("bee_video_editor.services.dub.pipeline.translate_segments") as tl, \
             patch("bee_video_editor.services.dub.pipeline.setup_voices") as vo, \
             patch("bee_video_editor.services.dub.pipeline.generate_dubbed_audio") as tts, \
             patch("bee_video_editor.services.dub.pipeline.compose_dubbed_video") as comp:
            sep.return_value = (tmp_path / "vocals.wav", tmp_path / "accompaniment.wav")
            run_pipeline(tmp_path)
            tr.assert_called_once()
            di.assert_called_once()
            sep.assert_called_once()
            tl.assert_called_once()
            vo.assert_called_once()
            tts.assert_called_once()
            comp.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline orchestrator**

```python
# src/bee_video_editor/services/dub/pipeline.py
from __future__ import annotations
import json
from pathlib import Path
from rich.console import Console
from bee_video_editor.services.dub.models import DubConfig
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.download import download_video
from bee_video_editor.services.dub.transcribe import transcribe_audio
from bee_video_editor.services.dub.diarize import diarize_segments
from bee_video_editor.services.dub.separate import separate_vocals
from bee_video_editor.services.dub.translate import translate_segments
from bee_video_editor.services.dub.voices import setup_voices
from bee_video_editor.services.dub.tts import generate_dubbed_audio
from bee_video_editor.services.dub.compose import compose_dubbed_video

console = Console()


def run_pipeline(
    project_dir: Path,
    url: str | None = None,
    lang: str | None = None,
) -> Path:
    """Run the full dubbing pipeline."""
    config_path = project_dir / "dub.json"
    config = DubConfig.load(config_path) if config_path.exists() else DubConfig()
    status = StatusTracker(project_dir / "status.json")

    source = project_dir / (config.source or "source.mp4")
    target_lang = lang or config.languages[0]

    # Step 0: Download
    if url:
        console.print("[bold]Step 0:[/] Downloading source...")
        download_video(url, source)

    # Step 1: Transcribe
    transcript_path = project_dir / "transcript.json"
    console.print("[bold]Step 1:[/] Transcribing...")
    transcribe_audio(source, transcript_path, engine=config.transcription.engine)

    # Step 2: Diarize
    diarization_path = project_dir / "diarization.json"
    voices_dir = project_dir / "voices"
    console.print("[bold]Step 2:[/] Diarizing speakers...")
    diarize_segments(
        source, transcript_path, diarization_path, voices_dir,
        engine=config.diarization.engine,
        min_speakers=config.diarization.min_speakers,
        max_speakers=config.diarization.max_speakers,
    )

    # Step 3: Separate vocals
    separated_dir = project_dir / "separated"
    console.print("[bold]Step 3:[/] Separating vocals...")
    vocals, accompaniment = separate_vocals(source, separated_dir, model=config.separation.model)

    # Step 4: Translate
    translations_path = project_dir / "translations" / f"{target_lang}.json"
    console.print(f"[bold]Step 4:[/] Translating to {target_lang}...")
    translate_segments(
        diarization_path, translations_path, lang=target_lang,
        engine=config.translation.engine, model=config.translation.model,
        style=config.translation.style,
    )

    # Step 5: Setup voices
    manifest_path = voices_dir / "manifest.json"
    console.print("[bold]Step 5:[/] Setting up voices...")
    diarization = json.loads(diarization_path.read_text())
    setup_voices(
        voices_dir, manifest_path, speakers=diarization["speakers"],
        mode=config.voices.mode, overrides=config.voices.overrides,
    )

    # Step 6: Generate TTS
    tts_dir = project_dir / "tts" / target_lang
    console.print("[bold]Step 6:[/] Generating dubbed audio...")
    generate_dubbed_audio(
        translations_path, manifest_path, tts_dir, status,
        model=config.tts.model,
        stability=config.tts.stability,
        similarity_boost=config.tts.similarity_boost,
    )

    # Step 7: Compose
    output_path = project_dir / "output" / f"{target_lang}.mp4"
    console.print("[bold]Step 7:[/] Composing final video...")
    compose_dubbed_video(
        source, translations_path, tts_dir, output_path,
        accompaniment_path=accompaniment if config.compositor.keep_background_audio else None,
        background_volume=config.compositor.background_volume,
        subtitles=config.compositor.subtitles,
        subtitle_style=config.compositor.subtitle_style,
        target_lufs=config.compositor.target_lufs,
    )

    console.print(f"[bold green]Done![/] Output: {output_path}")
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/services/dub/pipeline.py tests/test_dub_pipeline.py
git commit -m "feat(dub): add pipeline orchestrator"
```

---

## Task 13: CLI Commands

**Files:**
- Create: `src/bee_video_editor/adapters/cli_dub.py`
- Modify: `src/bee_video_editor/adapters/cli.py`

- [ ] **Step 1: Create CLI dub subcommands**

```python
# src/bee_video_editor/adapters/cli_dub.py
from __future__ import annotations
from pathlib import Path
import typer
from rich.console import Console

dub_app = typer.Typer(name="dub", help="AI dubbing pipeline.", no_args_is_help=True)
console = Console()


@dub_app.command()
def run(
    source: str = typer.Argument(..., help="YouTube URL or local file path"),
    lang: str = typer.Option("es", "--lang", "-l", help="Target language code"),
    voices: str = typer.Option("clone", "--voices", help="Voice mode: clone or mapped"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Project directory"),
):
    """Run the full dubbing pipeline."""
    from bee_video_editor.services.dub.pipeline import run_pipeline
    project = Path(project_dir)
    project.mkdir(parents=True, exist_ok=True)
    url = source if source.startswith("http") else None
    run_pipeline(project, url=url, lang=lang)


@dub_app.command()
def download(
    url: str = typer.Argument(..., help="YouTube URL"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Download source video."""
    from bee_video_editor.services.dub.download import download_video
    out = Path(project_dir) / "source.mp4"
    download_video(url, out)
    console.print(f"Downloaded to {out}")


@dub_app.command()
def transcribe(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Transcribe source audio."""
    from bee_video_editor.services.dub.transcribe import transcribe_audio
    p = Path(project_dir)
    transcribe_audio(p / "source.mp4", p / "transcript.json")
    console.print("Transcription complete.")


@dub_app.command()
def diarize(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Identify speakers in transcript."""
    from bee_video_editor.services.dub.diarize import diarize_segments
    p = Path(project_dir)
    diarize_segments(p / "source.mp4", p / "transcript.json", p / "diarization.json", p / "voices")
    console.print("Diarization complete.")


@dub_app.command()
def separate(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Separate vocals from background audio."""
    from bee_video_editor.services.dub.separate import separate_vocals
    p = Path(project_dir)
    separate_vocals(p / "source.mp4", p / "separated")
    console.print("Vocal separation complete.")


@dub_app.command()
def translate(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    engine: str = typer.Option("claude", "--engine", help="Translation engine"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Translate segments to target language."""
    from bee_video_editor.services.dub.translate import translate_segments
    p = Path(project_dir)
    translate_segments(p / "diarization.json", p / "translations" / f"{lang}.json", lang=lang, engine=engine)
    console.print(f"Translation to {lang} complete.")


@dub_app.command(name="voices")
def voices_cmd(
    mode: str = typer.Option("clone", "--mode", help="clone or mapped"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Set up voices (clone or map)."""
    import json
    from bee_video_editor.services.dub.voices import setup_voices
    p = Path(project_dir)
    diarization = json.loads((p / "diarization.json").read_text())
    setup_voices(p / "voices", p / "voices" / "manifest.json", diarization["speakers"], mode=mode)
    console.print("Voices configured.")


@dub_app.command()
def tts(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    retry_failed: bool = typer.Option(False, "--retry-failed", help="Retry failed segments"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Generate dubbed TTS audio."""
    from bee_video_editor.services.dub.tts import generate_dubbed_audio
    from bee_video_editor.services.dub.status import StatusTracker
    p = Path(project_dir)
    status = StatusTracker(p / "status.json")
    if retry_failed:
        status.retry_failed("tts")
    generate_dubbed_audio(p / "translations" / f"{lang}.json", p / "voices" / "manifest.json", p / "tts" / lang, status)
    console.print(f"TTS generation for {lang} complete.")


@dub_app.command()
def compose(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Compose final dubbed video."""
    from bee_video_editor.services.dub.compose import compose_dubbed_video
    p = Path(project_dir)
    accompaniment = p / "separated" / "accompaniment.wav"
    compose_dubbed_video(
        p / "source.mp4",
        p / "translations" / f"{lang}.json",
        p / "tts" / lang,
        p / "output" / f"{lang}.mp4",
        accompaniment_path=accompaniment if accompaniment.exists() else None,
    )
    console.print(f"Composed {lang} video.")


@dub_app.command()
def status(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Show pipeline status."""
    import json
    from rich.table import Table
    p = Path(project_dir)
    status_file = p / "status.json"
    if not status_file.exists():
        console.print("No status file found.")
        return
    data = json.loads(status_file.read_text())
    table = Table(title="Dub Pipeline Status")
    table.add_column("Segment")
    table.add_column("Step")
    table.add_column("State")
    table.add_column("Error")
    for key, entry in sorted(data.items()):
        seg, step = key.rsplit(":", 1)
        table.add_row(seg, step, entry["state"], entry.get("error", ""))
    console.print(table)
```

- [ ] **Step 2: Register dub command group in main CLI**

Add to `src/bee_video_editor/adapters/cli.py`:

```python
from bee_video_editor.adapters.cli_dub import dub_app
app.add_typer(dub_app, name="dub")
```

- [ ] **Step 3: Test CLI loads**

Run: `cd bee-content/video-editor && uv run bee-video dub --help`
Expected: Shows dub subcommands (run, download, transcribe, diarize, separate, translate, voices-cmd, tts, compose, status)

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/adapters/cli_dub.py src/bee_video_editor/adapters/cli.py
git commit -m "feat(dub): add CLI command group with all subcommands"
```

---

## Task 14: Dependencies & Extras

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dub extras to pyproject.toml**

Add to `[project.optional-dependencies]`:

```toml
dub = [
    "yt-dlp",
    "anthropic",
    "elevenlabs",
    "openai",
]
dub-local = [
    "demucs",
    "pyannote.audio",
]
```

- [ ] **Step 2: Verify install**

Run: `cd bee-content/video-editor && uv pip install -e ".[dub]"`
Expected: Installs successfully with yt-dlp, anthropic, elevenlabs, openai

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat(dub): add dub dependency extras"
```

---

## Task 15: End-to-End Smoke Test

- [ ] **Step 1: Run full test suite**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/test_dub_*.py -v`
Expected: All dub tests pass

- [ ] **Step 2: Run existing test suite to verify no regressions**

Run: `cd bee-content/video-editor && uv run --extra dev pytest tests/ -v --ignore=tests/test_dub_*.py`
Expected: All existing tests still pass

- [ ] **Step 3: Verify CLI integration**

Run: `cd bee-content/video-editor && uv run bee-video dub --help`
Expected: Shows all dub subcommands

- [ ] **Step 4: Final commit with version bump**

Update version in `pyproject.toml` from current to next minor, then:

```bash
git add -A
git commit -m "feat(dub): complete AI dubbing pipeline v1 (POC)"
```
