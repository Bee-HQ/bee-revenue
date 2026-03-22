"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from pydantic import BaseModel


class LoadProjectRequest(BaseModel):
    storyboard_path: str = "../discovery/true-crime/cases/alex-murdaugh/storyboard.md"
    project_dir: str = "../discovery/true-crime/cases/alex-murdaugh"


class LayerEntrySchema(BaseModel):
    content: str
    content_type: str
    time_start: str | None = None
    time_end: str | None = None
    raw: str = ""
    metadata: dict | None = None


class SegmentSchema(BaseModel):
    id: str
    start: str
    end: str
    title: str
    section: str
    section_time: str
    subsection: str
    duration_seconds: float
    visual: list[LayerEntrySchema]
    audio: list[LayerEntrySchema]
    overlay: list[LayerEntrySchema]
    music: list[LayerEntrySchema]
    source: list[LayerEntrySchema]
    transition: list[LayerEntrySchema]
    assigned_media: dict[str, str]


class StoryboardSchema(BaseModel):
    title: str
    total_segments: int
    total_duration_seconds: int
    sections: list[str]
    segments: list[SegmentSchema]
    stock_footage_needed: int
    photos_needed: int
    maps_needed: int
    production_rules: list[str]


class MediaFileSchema(BaseModel):
    name: str
    path: str
    relative_path: str
    size_bytes: int
    category: str  # footage, stock, photos, graphics, narration, maps
    extension: str


class MediaListResponse(BaseModel):
    files: list[MediaFileSchema]
    categories: dict[str, int]


class AssignMediaRequest(BaseModel):
    segment_id: str
    layer: str  # visual, audio, overlay, etc.
    media_path: str
    layer_index: int = 0


class ReorderSegmentsRequest(BaseModel):
    segment_order: list[str]


class ProductionStatusSchema(BaseModel):
    phase: str
    segments_total: int
    segments_done: int
    narration_files: int
    graphics_files: int
    trimmed_files: int


class GenerateRequest(BaseModel):
    tts_engine: str = "edge"
    tts_voice: str | None = None


class DownloadScriptInfo(BaseModel):
    name: str
    path: str
    relative_to_project: str


class DownloadRequest(BaseModel):
    script_path: str


class DownloadStatusResponse(BaseModel):
    task_id: str
    running: bool
    output_lines: list[str]
    return_code: int | None = None


class CaptionRequest(BaseModel):
    precise: bool = False
    style: str = "karaoke"  # "karaoke" or "phrase"


class BatchGraphicsRequest(BaseModel):
    config_path: str


class VoiceLockRequest(BaseModel):
    engine: str = "edge"
    voice: str | None = None
    speed: float = 0.95


class AssetEntrySchema(BaseModel):
    segment_id: str
    layer: str
    visual_code: str
    qualifier: str
    status: str
    file_path: str | None = None


class PreflightReportSchema(BaseModel):
    total: int
    found: int
    missing: int
    generated: int
    needs_check: int
    entries: list[AssetEntrySchema]


class StockSearchRequest(BaseModel):
    query: str
    count: int = 3
    min_duration: int = 5
    orientation: str | None = None


class StockDownloadRequest(BaseModel):
    url: str
    filename: str


class UpdateSegmentRequest(BaseModel):
    segment_id: str
    updates: dict  # partial config: transition_in, visual_updates, audio_updates


class DownloadEntryRequest(BaseModel):
    segment_id: str
    layer: str = "visual"
    index: int = 0


class GenerateClipRequest(BaseModel):
    prompt: str
    provider: str = "stub"
    duration: float = 5.0
    width: int = 1280
    height: int = 720
    reference_images: list[str] = []
    reference_videos: list[str] = []
    style: str | None = None


# ─── BeeProject format (new) ──────────────────────────────────────────────────


class VisualEntrySchema(BaseModel):
    type: str
    src: str | None = None
    trim: list[float] | None = None
    color: str | None = None
    kenBurns: str | None = None
    query: str | None = None
    lat: float | None = None
    lng: float | None = None


class AudioEntrySchema(BaseModel):
    type: str
    src: str | None = None
    text: str | None = None
    volume: float | None = None


class OverlayEntrySchema(BaseModel):
    type: str
    content: str = ""
    startOffset: float | None = None
    duration: float | None = None
    platform: str | None = None
    animation: str | None = None


class MusicEntrySchema(BaseModel):
    type: str
    src: str | None = None
    volume: float | None = None


class TransitionEntrySchema(BaseModel):
    type: str
    duration: float


class BeeSegmentSchema(BaseModel):
    id: str
    title: str
    section: str
    start: float
    duration: float
    visual: list[VisualEntrySchema]
    audio: list[AudioEntrySchema]
    overlay: list[OverlayEntrySchema]
    music: list[MusicEntrySchema]
    transition: TransitionEntrySchema | None = None


class ProductionStateSchema(BaseModel):
    narrationEngine: str = "edge"
    narrationVoice: str = ""
    transitionMode: str = "overlap"
    status: dict = {"narration": None, "stock": None, "render": None}
    renders: list = []


class BeeProjectSchema(BaseModel):
    version: int = 1
    title: str
    fps: int = 30
    resolution: list[int] = [1920, 1080]
    createdAt: str = ""
    updatedAt: str = ""
    segments: list[BeeSegmentSchema]
    production: ProductionStateSchema = ProductionStateSchema()
