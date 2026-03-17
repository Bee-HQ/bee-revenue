"""Map generation — produce styled map images from coordinates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Monkey-patch for Pillow 11 compatibility with py-staticmaps
# py-staticmaps calls ImageDraw.textsize which was removed in Pillow 11.
from PIL import ImageDraw, Image, ImageFilter

if not hasattr(ImageDraw.ImageDraw, "textsize"):

    def _textsize(self, text, font=None, **kwargs):
        bbox = self.textbbox((0, 0), text, font=font, **kwargs)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    ImageDraw.ImageDraw.textsize = _textsize

import staticmaps


WIDTH = 1920
HEIGHT = 1080


@dataclass
class MapLocation:
    lat: float
    lng: float
    label: str = ""
    pin_color: str = "red"  # "red" or "teal"


@dataclass
class MapRoute:
    points: list[tuple[float, float]]  # list of (lat, lng) pairs
    color: str = "red"


def _apply_dark_grade(img: Image.Image) -> Image.Image:
    """Apply dark, desaturated color grade matching the formula's aesthetic."""
    from PIL import ImageEnhance

    # Desaturate
    img = ImageEnhance.Color(img).enhance(0.3)
    # Darken
    img = ImageEnhance.Brightness(img).enhance(0.25)
    # Boost contrast slightly
    img = ImageEnhance.Contrast(img).enhance(1.3)

    return img


def _apply_vignette(img: Image.Image, strength: float = 0.7) -> Image.Image:
    """Apply dark edge vignette using a radial gradient mask."""
    w, h = img.size
    # Create a black image
    black = Image.new("RGB", (w, h), (0, 0, 0))
    # Create an elliptical white mask (center bright, edges dark)
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    margin_x = int(w * 0.2)
    margin_y = int(h * 0.2)
    d.ellipse([margin_x, margin_y, w - margin_x, h - margin_y], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) // 4))

    # Composite: where mask is white, show original; where black, show darkened
    result = Image.composite(img, black, mask)
    return result


def _make_context(
    center_lat: float,
    center_lng: float,
    zoom: int,
) -> staticmaps.Context:
    """Create a configured staticmaps context."""
    ctx = staticmaps.Context()
    ctx.set_tile_provider(staticmaps.tile_provider_OSM)
    ctx.set_center(staticmaps.create_latlng(center_lat, center_lng))
    ctx.set_zoom(zoom)
    return ctx


def _render_and_post_process(
    ctx: staticmaps.Context,
    output_path: Path,
    dark_grade: bool = True,
    vignette: bool = True,
) -> Path:
    """Render a staticmaps context to Pillow, apply post-processing, save PNG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = ctx.render_pillow(WIDTH, HEIGHT)

    # render_pillow returns RGBA; convert to RGB for processing
    if img.mode == "RGBA":
        img = img.convert("RGB")

    if dark_grade:
        img = _apply_dark_grade(img)
    if vignette:
        img = _apply_vignette(img)

    # Ensure final size is exactly 1920x1080
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

    img.save(str(output_path))
    return output_path


def map_flat(
    center_lat: float,
    center_lng: float,
    output_path: Path,
    zoom: int = 12,
    markers: list[MapLocation] | None = None,
) -> Path:
    """[MAP-FLAT] Dark satellite-style top-down view with heavy vignette.

    Uses OSM tiles, applies dark color grade + vignette in post-processing.
    """
    ctx = _make_context(center_lat, center_lng, zoom)

    if markers:
        for loc in markers:
            pin_color = staticmaps.RED if loc.pin_color == "red" else staticmaps.Color(0, 212, 170)
            ctx.add_object(staticmaps.Marker(staticmaps.create_latlng(loc.lat, loc.lng), color=pin_color, size=12))

    return _render_and_post_process(ctx, output_path, dark_grade=True, vignette=True)


def map_tactical(
    center_lat: float,
    center_lng: float,
    output_path: Path,
    zoom: int = 12,
    markers: list[MapLocation] | None = None,
    label: str = "",
) -> Path:
    """[MAP-TACTICAL] Dark map with red glowing markers and label text.

    Nearly black with red accent markers. Isolation/remote emphasis.
    """
    ctx = _make_context(center_lat, center_lng, zoom)

    if markers:
        for loc in markers:
            ctx.add_object(staticmaps.Marker(staticmaps.create_latlng(loc.lat, loc.lng), color=staticmaps.RED, size=14))

    output_path = _render_and_post_process(ctx, output_path, dark_grade=True, vignette=True)

    # Add label text overlay if provided
    if label:
        img = Image.open(str(output_path))
        d = ImageDraw.Draw(img)
        from PIL import ImageFont

        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ]
            font = None
            for fp in font_paths:
                if Path(fp).exists():
                    font = ImageFont.truetype(fp, 42)
                    break
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        bbox = d.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        # Bottom-center, red text
        d.text(((WIDTH - tw) // 2, HEIGHT - 120), label, fill=(200, 50, 50), font=font)
        img.save(str(output_path))

    return output_path


def map_pulse(
    lat: float,
    lng: float,
    output_path: Path,
    zoom: int = 14,
    label: str = "",
) -> Path:
    """[MAP-PULSE] Satellite view with red marker on target location.

    Single prominent red marker with label.
    """
    ctx = _make_context(lat, lng, zoom)
    ctx.add_object(staticmaps.Marker(staticmaps.create_latlng(lat, lng), color=staticmaps.RED, size=16))

    output_path = _render_and_post_process(ctx, output_path, dark_grade=True, vignette=True)

    if label:
        img = Image.open(str(output_path))
        d = ImageDraw.Draw(img)
        from PIL import ImageFont

        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ]
            font = None
            for fp in font_paths:
                if Path(fp).exists():
                    font = ImageFont.truetype(fp, 48)
                    break
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        bbox = d.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        d.text(((WIDTH - tw) // 2, HEIGHT - 120), label, fill=(200, 50, 50), font=font)
        img.save(str(output_path))

    return output_path


def map_route(
    points: list[tuple[float, float]],
    output_path: Path,
    zoom: int = 12,
    label: str = "",
) -> Path:
    """[MAP-ROUTE] Map showing route between locations with red line.

    Draws a red path connecting the points.
    """
    if not points:
        raise ValueError("map_route requires at least one point")

    # Use midpoint of first and last point as center
    center_lat = (points[0][0] + points[-1][0]) / 2
    center_lng = (points[0][1] + points[-1][1]) / 2

    ctx = _make_context(center_lat, center_lng, zoom)

    # Draw the route as a red line (requires at least 2 points)
    latlngs = [staticmaps.create_latlng(lat, lng) for lat, lng in points]
    if len(latlngs) >= 2:
        ctx.add_object(staticmaps.Line(latlngs, color=staticmaps.RED, width=4))

    # Add start/end markers
    ctx.add_object(staticmaps.Marker(latlngs[0], color=staticmaps.RED, size=12))
    if len(latlngs) > 1:
        ctx.add_object(staticmaps.Marker(latlngs[-1], color=staticmaps.RED, size=12))

    output_path = _render_and_post_process(ctx, output_path, dark_grade=True, vignette=True)

    if label:
        img = Image.open(str(output_path))
        d = ImageDraw.Draw(img)
        from PIL import ImageFont

        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ]
            font = None
            for fp in font_paths:
                if Path(fp).exists():
                    font = ImageFont.truetype(fp, 42)
                    break
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        bbox = d.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        d.text(((WIDTH - tw) // 2, HEIGHT - 120), label, fill=(200, 50, 50), font=font)
        img.save(str(output_path))

    return output_path
