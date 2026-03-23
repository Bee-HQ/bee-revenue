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
        path.write_text(json.dumps(self.model_dump(exclude_defaults=True), indent=2))


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
