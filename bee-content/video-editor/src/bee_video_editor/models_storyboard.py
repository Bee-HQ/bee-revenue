"""Data models for storyboard-based video production."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VisualType(Enum):
    """Type of visual content in a storyboard layer."""
    FOOTAGE = "FOOTAGE"
    STOCK = "STOCK"
    PHOTO = "PHOTO"
    MAP = "MAP"
    GRAPHIC = "GRAPHIC"
    WAVEFORM = "WAVEFORM"
    BLACK = "BLACK"
    UNKNOWN = "UNKNOWN"


class AudioType(Enum):
    """Type of audio content in a storyboard layer."""
    NAR = "NAR"
    REAL_AUDIO = "REAL AUDIO"
    MUSIC = "MUSIC"
    SFX = "SFX"
    UNKNOWN = "UNKNOWN"


@dataclass
class LayerEntry:
    """A single entry within a layer, possibly time-ranged."""
    content: str
    content_type: str  # e.g. "FOOTAGE", "NAR", "GRAPHIC"
    time_start: str | None = None  # optional sub-range within segment
    time_end: str | None = None
    raw: str = ""  # original markdown content


@dataclass
class ChecklistItem:
    """A checklist item from pre-production or post-assembly sections."""
    text: str
    checked: bool
    category: str  # "audio", "graphics", "maps", "post"


@dataclass
class StoryboardSegment:
    """A single time-coded segment from a storyboard."""
    id: str  # e.g. "0_00-0_05"
    start: str  # "0:00"
    end: str  # "0:05"
    title: str  # "THE HOOK"
    section: str  # "COLD OPEN"
    section_time: str  # "0:00 - 2:30"
    subsection: str  # "Murdaugh Country"

    visual: list[LayerEntry] = field(default_factory=list)
    audio: list[LayerEntry] = field(default_factory=list)
    overlay: list[LayerEntry] = field(default_factory=list)
    music: list[LayerEntry] = field(default_factory=list)
    source: list[LayerEntry] = field(default_factory=list)
    transition: list[LayerEntry] = field(default_factory=list)

    # Media assignment (populated by user in editor, persisted in sidecar JSON)
    assigned_media: dict[str, str] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> int:
        """Calculate duration from start/end times."""
        def _to_secs(t: str) -> int:
            parts = t.strip().split(":")
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        return _to_secs(self.end) - _to_secs(self.start)

    @property
    def all_layers(self) -> dict[str, list[LayerEntry]]:
        return {
            "visual": self.visual,
            "audio": self.audio,
            "overlay": self.overlay,
            "music": self.music,
            "source": self.source,
            "transition": self.transition,
        }


@dataclass
class StockFootageNeeded:
    """A stock footage item needed for the project."""
    index: int
    search_term: str
    used_in: str
    duration_needed: str


@dataclass
class PhotoNeeded:
    """A photo needed for the project."""
    index: int
    subject: str
    source: str
    used_in: str


@dataclass
class MapNeeded:
    """A map image needed for the project."""
    index: int
    location: str
    zoom_level: str
    style: str
    used_in: str


@dataclass
class ProductionRules:
    """Production rules extracted from the storyboard."""
    rules: list[str] = field(default_factory=list)


@dataclass
class Storyboard:
    """A complete storyboard parsed from markdown."""
    title: str
    total_duration: str | None = None
    resolution: str | None = None
    format: str | None = None
    pre_production: list[ChecklistItem] = field(default_factory=list)
    post_checklist: list[ChecklistItem] = field(default_factory=list)
    segments: list[StoryboardSegment] = field(default_factory=list)
    stock_footage: list[StockFootageNeeded] = field(default_factory=list)
    photos_needed: list[PhotoNeeded] = field(default_factory=list)
    maps_needed: list[MapNeeded] = field(default_factory=list)
    production_rules: ProductionRules = field(default_factory=ProductionRules)

    @property
    def total_segments(self) -> int:
        return len(self.segments)

    @property
    def sections(self) -> list[str]:
        seen = []
        for seg in self.segments:
            if seg.section not in seen:
                seen.append(seg.section)
        return seen

    @property
    def total_duration_seconds(self) -> int:
        if not self.segments:
            return 0
        def _to_secs(t: str) -> int:
            parts = t.strip().split(":")
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        return max(_to_secs(s.end) for s in self.segments)

    def segments_in_section(self, section: str) -> list[StoryboardSegment]:
        return [s for s in self.segments if s.section == section]

    def summary(self) -> dict:
        visual_types: dict[str, int] = {}
        for seg in self.segments:
            for v in seg.visual:
                vt = v.content_type
                visual_types[vt] = visual_types.get(vt, 0) + 1

        return {
            "title": self.title,
            "total_segments": self.total_segments,
            "total_duration_seconds": self.total_duration_seconds,
            "sections": self.sections,
            "visual_type_counts": visual_types,
            "stock_footage_needed": len(self.stock_footage),
            "photos_needed": len(self.photos_needed),
            "maps_needed": len(self.maps_needed),
            "production_rules": len(self.production_rules.rules),
        }
