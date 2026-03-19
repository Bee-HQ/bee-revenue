"""Asset preflight scanner — checks storyboard requirements against project files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment


@dataclass
class AssetEntry:
    """A single asset requirement from one segment."""
    segment_id: str
    layer: str
    visual_code: str
    qualifier: str
    status: str  # "found", "missing", "needs-check", "not-supported", "unknown"
    file_path: str | None = None


@dataclass
class PreflightReport:
    """Result of scanning a storyboard against project assets."""
    total: int = 0
    found: int = 0
    missing: int = 0
    generated: int = 0
    needs_check: int = 0
    entries: list[AssetEntry] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.missing == 0


# Resolution rules: visual_code → (directory, glob_pattern, default_status_if_missing)
RESOLUTION_RULES: dict[str, tuple[str, str, str]] = {
    # Generated graphics
    "LOWER-THIRD": ("output/graphics", "lower-third-*.png", "missing"),
    "TIMELINE-MARKER": ("output/graphics", "timeline-*.png", "missing"),
    "FINANCIAL-CARD": ("output/graphics", "financial-*.png", "missing"),
    "MUGSHOT-CARD": ("output/graphics", "mugshot-*.png", "missing"),
    "QUOTE-CARD": ("output/graphics", "quote-*.png", "missing"),
    "BRAND-STING": ("output/graphics", "brand-*", "missing"),
    "DISCLAIMER": ("output/graphics", "disclaimer-*", "missing"),
    # Source footage
    "COURTROOM": ("footage", "trial-*.mp4", "missing"),
    "BODYCAM": ("footage", "bodycam-*.mp4", "missing"),
    "INTERROGATION": ("footage", "interrogation-*.mp4", "missing"),
    "WAVEFORM-AERIAL": ("output/segments", "*.mp4", "missing"),
    "WAVEFORM-DARK": ("output/segments", "*.mp4", "missing"),
    # Photos
    "PIP-SINGLE": ("photos", "pip-*.png", "missing"),
    "PIP-DUAL": ("photos", "pip-*.png", "missing"),
    # Maps
    "MAP-FLAT": ("maps", "map-*", "missing"),
    "MAP-3D": ("maps", "map-*", "missing"),
    "MAP-TACTICAL": ("maps", "map-*", "missing"),
    "MAP-PULSE": ("maps", "map-*", "missing"),
    "MAP-ROUTE": ("maps", "map-*", "missing"),
    # Stock (can't match qualifier)
    "BROLL-DARK": ("stock", "*.mp4", "needs-check"),
    # Audio
    "NAR": ("output/narration", "nar-*.mp3", "missing"),
}

NOT_SUPPORTED_CODES = {
    "DOCUMENT-MOCKUP", "TEXT-CHAT", "SOCIAL-POST", "NEWS-MONTAGE",
    "EVIDENCE-BOARD", "FLOW-DIAGRAM", "TIMELINE-SEQUENCE",
    "POLICE-DB", "DESKTOP-PHOTOS", "EVIDENCE-CLOSEUP",
    "EVIDENCE-DISPLAY", "BODY-DIAGRAM", "SPLIT-INFO", "TRAILER",
}

PERSISTENT_MODIFIERS = {
    "COLOR-GRADE", "VIGNETTE", "LETTERBOX", "CAPTION-ANIMATED", "STILL",
}


def _is_modifier(code: str) -> bool:
    """Check if code is a persistent modifier or transition (not an asset)."""
    return code in PERSISTENT_MODIFIERS or code.startswith("TR-")


def run_preflight(parsed: ParsedStoryboard, project_dir: Path) -> PreflightReport:
    """Scan storyboard against project assets and report gaps."""
    report = PreflightReport()

    for seg in parsed.segments:
        # Walk all three config layers
        layer_map = {
            "visual": seg.config.visual,
            "audio": seg.config.audio,
            "overlay": seg.config.overlay,
        }

        # Also check narration as a synthetic NAR audio entry
        if seg.narration:
            code = "NAR"
            qualifier = seg.narration

            if not _is_modifier(code) and code != "UNKNOWN":
                report.total += 1
                if code in RESOLUTION_RULES:
                    subdir, pattern, default_status = RESOLUTION_RULES[code]
                    search_dir = project_dir / subdir
                    found_files = list(search_dir.glob(pattern)) if search_dir.exists() else []
                    if found_files:
                        report.found += 1
                        report.entries.append(AssetEntry(
                            segment_id=seg.id, layer="audio",
                            visual_code=code, qualifier=qualifier,
                            status="found",
                            file_path=str(found_files[0]),
                        ))
                    elif default_status == "needs-check":
                        report.needs_check += 1
                        report.entries.append(AssetEntry(
                            segment_id=seg.id, layer="audio",
                            visual_code=code, qualifier=qualifier,
                            status="needs-check",
                        ))
                    else:
                        report.missing += 1
                        report.entries.append(AssetEntry(
                            segment_id=seg.id, layer="audio",
                            visual_code=code, qualifier=qualifier,
                            status="missing",
                        ))

        for layer_name, entries in layer_map.items():
            for entry in entries:
                code = entry.type
                qualifier = entry.src if hasattr(entry, "src") else (entry.text or "")

                # Skip persistent modifiers and transitions
                if _is_modifier(code) or code == "UNKNOWN":
                    continue

                report.total += 1

                if code in NOT_SUPPORTED_CODES:
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="not-supported",
                    ))
                    continue

                if code not in RESOLUTION_RULES:
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="unknown",
                    ))
                    continue

                subdir, pattern, default_status = RESOLUTION_RULES[code]
                search_dir = project_dir / subdir
                found_files = list(search_dir.glob(pattern)) if search_dir.exists() else []

                if found_files:
                    report.found += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="found",
                        file_path=str(found_files[0]),
                    ))
                elif default_status == "needs-check":
                    report.needs_check += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="needs-check",
                    ))
                else:
                    report.missing += 1
                    report.entries.append(AssetEntry(
                        segment_id=seg.id, layer=layer_name,
                        visual_code=code, qualifier=qualifier,
                        status="missing",
                    ))

    return report
