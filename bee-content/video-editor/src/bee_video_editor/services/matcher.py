"""Media matching service — auto-assign media files to storyboard segments.

Scores available media files against segment descriptions and assigns
best matches. Works without an LLM using keyword overlap + fuzzy matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment


@dataclass
class Assignment:
    segment_id: str
    layer: str
    layer_index: int
    file_path: Path
    confidence: float  # 0.0-1.0
    reason: str


@dataclass
class AssignmentPlan:
    assignments: list[Assignment] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


@dataclass
class _MediaFile:
    path: Path
    name: str
    tokens: set[str]
    media_type: str  # "video" or "photo"


_STOP_WORDS = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "is", "it",
    "and", "or", "but", "with", "from", "by", "as", "into", "that", "this",
    "be", "are", "was", "were", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "no", "not", "very", "just", "all", "also", "then", "than", "so",
    "up", "out", "off", "over", "under", "about", "between",
}

_MEDIA_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".jpg", ".jpeg", ".png", ".webp"}
_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}


def _tokenize(text: str) -> set[str]:
    words = re.split(r'[^a-zA-Z0-9]+', text.lower())
    return {w for w in words if w and len(w) > 2 and w not in _STOP_WORDS}


def _build_inventory(media_dirs: list[Path]) -> list[_MediaFile]:
    inventory: list[_MediaFile] = []
    for media_dir in media_dirs:
        if not media_dir.exists():
            continue
        for f in sorted(media_dir.rglob("*")):
            if f.is_file() and f.suffix.lower() in _MEDIA_EXTENSIONS:
                inventory.append(_MediaFile(
                    path=f,
                    name=f.stem.lower(),
                    tokens=_tokenize(f.stem),
                    media_type="video" if f.suffix.lower() in _VIDEO_EXTENSIONS else "photo",
                ))
    return inventory


def _segment_description(seg: ParsedSegment) -> str:
    """Build a description string from segment data for keyword matching."""
    parts = [seg.title]
    for v in seg.config.visual:
        if v.query:
            parts.append(v.query)
        if v.src:
            parts.append(Path(v.src).stem)
        if v.text:
            parts.append(v.text)
    if seg.narration:
        parts.append(seg.narration[:200])  # first 200 chars of narration
    return " ".join(parts)


def _try_src_match(seg: ParsedSegment, inventory: list[_MediaFile]) -> Assignment | None:
    """Try to match a segment's visual src to an inventory file."""
    for i, v in enumerate(seg.config.visual):
        if not v.src:
            continue
        ref_name = Path(v.src).stem.lower()
        for mf in inventory:
            if ref_name in mf.name or mf.name in ref_name:
                return Assignment(
                    segment_id=seg.id, layer="visual", layer_index=i,
                    file_path=mf.path, confidence=0.95,
                    reason=f"src match: {v.src}",
                )
    return None


def _find_best_keyword_match(
    segment_id: str, layer: str, layer_index: int,
    description: str, inventory: list[_MediaFile],
    used_files: dict[Path, int],
) -> Assignment | None:
    desc_tokens = _tokenize(description)
    if not desc_tokens:
        return None

    best_score = 0.0
    best_file: _MediaFile | None = None

    for mf in inventory:
        if not mf.tokens:
            continue
        overlap = desc_tokens & mf.tokens
        if not overlap:
            continue
        score = len(overlap) / min(len(desc_tokens), len(mf.tokens))
        uses = used_files.get(mf.path, 0)
        if uses > 0:
            score *= max(0.3, 1.0 - (uses * 0.2))
        if score > best_score:
            best_score = score
            best_file = mf

    if best_file and best_score > 0:
        return Assignment(
            segment_id=segment_id, layer=layer, layer_index=layer_index,
            file_path=best_file.path, confidence=min(best_score, 1.0),
            reason=f"keyword match ({best_score:.2f}): {', '.join(desc_tokens & best_file.tokens)}",
        )
    return None


def auto_assign_media(
    parsed: ParsedStoryboard,
    media_dirs: list[Path],
    *,
    min_confidence: float = 0.1,
) -> AssignmentPlan:
    """Auto-assign media files to storyboard segments."""
    plan = AssignmentPlan()
    inventory = _build_inventory(media_dirs)
    if not inventory:
        plan.unmatched = [seg.id for seg in parsed.segments]
        return plan

    used_files: dict[Path, int] = {}

    for seg in parsed.segments:
        matched = False

        # Strategy 1: src match (visual entries already have src paths)
        assignment = _try_src_match(seg, inventory)
        if assignment and assignment.confidence >= min_confidence:
            plan.assignments.append(assignment)
            used_files[assignment.file_path] = used_files.get(assignment.file_path, 0) + 1
            matched = True

        # Strategy 2: keyword match using segment description
        if not matched:
            description = _segment_description(seg)
            best = _find_best_keyword_match(
                seg.id, "visual", 0, description, inventory, used_files,
            )
            if best and best.confidence >= min_confidence:
                plan.assignments.append(best)
                used_files[best.file_path] = used_files.get(best.file_path, 0) + 1
                matched = True

        if not matched:
            plan.unmatched.append(seg.id)

    for path, count in used_files.items():
        if count > 3:
            plan.conflicts.append(f"{path.name} used {count} times")

    return plan
