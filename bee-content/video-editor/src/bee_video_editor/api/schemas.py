"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from pydantic import BaseModel


class LoadProjectRequest(BaseModel):
    storyboard_path: str
    project_dir: str = "."


class LayerEntrySchema(BaseModel):
    content: str
    content_type: str
    time_start: str | None = None
    time_end: str | None = None
    raw: str = ""


class SegmentSchema(BaseModel):
    id: str
    start: str
    end: str
    title: str
    section: str
    section_time: str
    subsection: str
    duration_seconds: int
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
