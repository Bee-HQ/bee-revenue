"""Batch graphics generation from a JSON config file."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from bee_video_editor.processors import graphics as gfx
from bee_video_editor.services.production import FailedItem, ProductionResult

# Valid graphic types — only functions whose args are JSON-serializable plain types.
# Complex types (text_chat, social_post, evidence_board, flow_diagram, timeline_sequence)
# require dataclass deserialization and are excluded for now.
VALID_GRAPHIC_TYPES = {
    "lower_third", "timeline_marker", "quote_card", "financial_card",
    "text_overlay", "black_frame", "mugshot_card", "news_montage",
}


@dataclass
class GraphicSpec:
    """A single graphic to generate."""
    type: str
    kwargs: dict

    @property
    def slug(self) -> str:
        """Generate a filename slug from the spec."""
        if "name" in self.kwargs:
            return self.kwargs["name"].lower().replace(" ", "-")[:30]
        if "date" in self.kwargs:
            return self.kwargs["date"].lower().replace(" ", "-").replace(",", "")[:30]
        if "amount" in self.kwargs:
            return self.kwargs["amount"].lower().replace("$", "").replace(" ", "-")[:30]
        if "text" in self.kwargs:
            return self.kwargs["text"].lower().replace(" ", "-")[:30]
        return self.type


def parse_graphics_config(config_path: Path) -> tuple[list[GraphicSpec], str]:
    """Parse a graphics batch config JSON file.

    Returns:
        (list of GraphicSpec, output_dir string)
    """
    data = json.loads(config_path.read_text())
    output_dir = data.get("output_dir", "output/graphics")
    graphics = data.get("graphics", [])

    specs = []
    for i, entry in enumerate(graphics):
        gtype = entry.get("type")
        if not gtype:
            raise ValueError(f"Graphics entry {i} missing 'type' field")
        if gtype not in VALID_GRAPHIC_TYPES:
            raise ValueError(
                f"Unknown graphic type '{gtype}'. "
                f"Valid types: {', '.join(sorted(VALID_GRAPHIC_TYPES))}"
            )
        kwargs = {k: v for k, v in entry.items() if k != "type"}
        specs.append(GraphicSpec(type=gtype, kwargs=kwargs))

    return specs, output_dir


def generate_batch(specs: list[GraphicSpec], output_dir: Path) -> ProductionResult:
    """Generate all graphics from a list of specs.

    Each graphic gets a numbered filename: {type}-{NN}-{slug}.png
    Skips if the output file already exists (idempotent).
    """
    result = ProductionResult()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Track counts per type for numbered filenames
    type_counts: dict[str, int] = {}

    for spec in specs:
        idx = type_counts.get(spec.type, 0)
        type_counts[spec.type] = idx + 1

        filename = f"{spec.type.replace('_', '-')}-{idx:02d}-{spec.slug}.png"
        out_path = output_dir / filename

        if out_path.exists():
            result.skipped.append(str(out_path))
            continue

        try:
            func = getattr(gfx, spec.type)
            func(output_path=out_path, **spec.kwargs)
            result.succeeded.append(out_path)
        except Exception as exc:
            result.failed.append(FailedItem(path=str(out_path), error=str(exc)))

    return result
