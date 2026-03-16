"""Data models for the content automation pipeline."""

from dataclasses import dataclass, field


@dataclass
class Series:
    """A manga/manhwa/manhua series from AniList."""

    id: str
    title_english: str
    title_romaji: str
    title_native: str | None = None
    synopsis: str = ""
    genres: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: str = "UNKNOWN"  # RELEASING, FINISHED, NOT_YET_RELEASED, CANCELLED, HIATUS
    chapters: int | None = None
    popularity: int = 0
    score: float | None = None
    cover_url: str | None = None
    banner_url: str | None = None

    @property
    def display_title(self) -> str:
        """Best available title for display."""
        return self.title_english or self.title_romaji or self.title_native or "Unknown"


@dataclass
class Chapter:
    """A manga chapter from MangaDex."""

    id: str
    number: float
    title: str | None = None
    language: str = "en"
    pages: int = 0
    scanlation_group: str | None = None
    published_at: str = ""
    page_urls: list[str] = field(default_factory=list)


@dataclass
class ChapterSummary:
    """Chapter synopsis aggregated from wiki/database sources."""

    series_title: str
    chapter_number: float
    synopsis: str = ""
    characters: list[str] = field(default_factory=list)
    key_events: list[str] = field(default_factory=list)
    source: str = "unknown"  # "fandom_wiki", "anilist", "mangaupdates"


@dataclass
class ScriptSegment:
    """A segment of a generated video script."""

    type: str  # "hook", "intro", "recap", "analysis", "outro"
    text: str
    duration_estimate: float = 0.0  # seconds
    visual_notes: str = ""


@dataclass
class VideoScript:
    """A complete video script ready for production."""

    series_title: str
    chapter_number: float
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    segments: list[ScriptSegment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenated script text."""
        return "\n\n".join(seg.text for seg in self.segments)

    @property
    def total_duration(self) -> float:
        """Estimated total duration in seconds."""
        return sum(seg.duration_estimate for seg in self.segments)
