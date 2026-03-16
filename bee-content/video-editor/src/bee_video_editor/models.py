"""Data models for video production projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SegmentType(Enum):
    NAR = "NAR"      # Narrator voiceover (AI TTS)
    REAL = "REAL"    # Real audio/video clip from footage
    GEN = "GEN"      # Generated asset (map, graphic, overlay, B-roll)
    MIX = "MIX"      # Real footage with narrator overlay
    SFX = "SFX"      # Sound effect / background music
    SPONSOR = "SPONSOR"


@dataclass
class Timecode:
    minutes: int
    seconds: int

    @classmethod
    def parse(cls, s: str) -> Timecode:
        """Parse 'M:SS' or 'MM:SS' format."""
        s = s.strip()
        parts = s.split(":")
        if len(parts) == 2:
            return cls(minutes=int(parts[0]), seconds=int(parts[1]))
        raise ValueError(f"Invalid timecode: {s}")

    @property
    def total_seconds(self) -> int:
        return self.minutes * 60 + self.seconds

    def __str__(self) -> str:
        return f"{self.minutes}:{self.seconds:02d}"


@dataclass
class Segment:
    """A single row from the assembly guide table."""
    start: Timecode
    end: Timecode
    duration_seconds: int
    segment_type: SegmentType
    visual: str
    audio: str
    source_notes: str
    section: str         # e.g. "COLD OPEN", "ACT 1: THE DYNASTY"
    subsection: str      # e.g. "Murdaugh Country", "The Boat Crash"

    @property
    def duration_str(self) -> str:
        return f"{self.duration_seconds}s"


@dataclass
class TrimNote:
    """A clip trim instruction from the assembly guide."""
    source_file: str     # glob pattern like "footage/911-calls/8HdmZyPZqoY-*.mkv"
    file_size: str       # e.g. "7.7MB"
    trims: list[TrimInstruction] = field(default_factory=list)


@dataclass
class TrimInstruction:
    """A specific trim within a source file."""
    label: str           # e.g. "Opening 'I need the police'"
    start: str           # ffmpeg-style timestamp e.g. "0:00"
    duration: str        # e.g. "15s" or "~50s"
    usage: str           # where this trim is used in the assembly


@dataclass
class PreProductionAsset:
    """An asset that needs to be created before assembly."""
    category: str        # "Audio Track", "Generated Graphics"
    description: str
    done: bool = False


@dataclass
class PostChecklistItem:
    """Post-assembly checklist item."""
    description: str
    done: bool = False


@dataclass
class Project:
    """A complete video production project parsed from an assembly guide."""
    title: str
    total_duration: str           # e.g. "~55 minutes"
    resolution: str               # e.g. "1080p"
    format: str                   # e.g. "MP4 (H.264 + AAC)"
    segments: list[Segment] = field(default_factory=list)
    pre_production: list[PreProductionAsset] = field(default_factory=list)
    trim_notes: list[TrimNote] = field(default_factory=list)
    post_checklist: list[PostChecklistItem] = field(default_factory=list)

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

    def segments_by_type(self, seg_type: SegmentType) -> list[Segment]:
        return [s for s in self.segments if s.segment_type == seg_type]

    def segments_in_section(self, section: str) -> list[Segment]:
        return [s for s in self.segments if s.section == section]

    def summary(self) -> dict:
        type_counts = {}
        type_durations = {}
        for seg in self.segments:
            t = seg.segment_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            type_durations[t] = type_durations.get(t, 0) + seg.duration_seconds

        total_dur = sum(s.duration_seconds for s in self.segments)

        return {
            "title": self.title,
            "total_duration": self.total_duration,
            "total_segments": self.total_segments,
            "sections": self.sections,
            "segment_type_counts": type_counts,
            "segment_type_durations_seconds": type_durations,
            "total_assembled_seconds": total_dur,
            "pre_production_assets": len(self.pre_production),
            "pre_production_done": sum(1 for a in self.pre_production if a.done),
            "trim_notes": len(self.trim_notes),
            "post_checklist_items": len(self.post_checklist),
            "post_checklist_done": sum(1 for c in self.post_checklist if c.done),
        }
