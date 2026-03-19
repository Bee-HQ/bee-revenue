"""Pydantic models for the bee-video storyboard format v2."""

from __future__ import annotations
from pydantic import BaseModel, Field


class VoiceLock(BaseModel):
    engine: str
    voice: str
    model: str | None = None

class OutputConfig(BaseModel):
    resolution: str = "1920x1080"
    fps: int = 30
    codec: str = "h264"
    crf: int = 18

class TransitionConfig(BaseModel):
    type: str
    duration: float

class ProjectConfig(BaseModel):
    title: str
    version: int = 1
    voice_lock: VoiceLock | None = None
    color_preset: str | None = None
    default_transition: TransitionConfig | None = None
    output: OutputConfig | None = None

class VisualEntry(BaseModel):
    type: str
    src: str | None = None
    tc_in: str | None = Field(None, alias="in")
    out: str | None = None
    color: str | None = None
    ken_burns: str | None = None
    query: str | None = None
    duration: float | None = None
    style: str | None = None
    center: list[float] | None = None
    zoom: int | None = None
    markers: list[dict] | None = None
    template: str | None = None
    text: str | None = None
    subtext: str | None = None
    prompt: str | None = None
    provider: str | None = None
    model_config = {"populate_by_name": True}

class AudioEntry(BaseModel):
    type: str
    src: str | None = None
    volume: float | None = None
    tc_in: str | None = Field(None, alias="in")
    out: str | None = None
    fade_in: float | None = None
    fade_out: float | None = None
    engine: str | None = None
    voice: str | None = None
    model_config = {"populate_by_name": True}

class OverlayEntry(BaseModel):
    type: str
    text: str | None = None
    subtext: str | None = None
    duration: float | None = None
    position: str | None = None
    date: str | None = None
    description: str | None = None
    quote: str | None = None
    author: str | None = None
    amount: str | None = None

class CaptionsConfig(BaseModel):
    style: str = "phrase"
    font_size: int = 42

class SegmentConfig(BaseModel):
    visual: list[VisualEntry] = Field(default_factory=list)
    audio: list[AudioEntry] = Field(default_factory=list)
    overlay: list[OverlayEntry] = Field(default_factory=list)
    captions: CaptionsConfig | None = None
    transition_in: TransitionConfig | None = None
    model_config = {"extra": "allow"}
