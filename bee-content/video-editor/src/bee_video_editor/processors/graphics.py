"""Generate production graphics (lower thirds, timeline markers, quotes, etc.)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Color palette (Dr Insanity style)
COLORS = {
    "bg_dark": (10, 10, 15),
    "bg_darker": (15, 15, 20),
    "white": (255, 255, 255),
    "gray": (180, 180, 180),
    "light_gray": (150, 150, 150),
    "red": (200, 50, 50),
    "dark_red": (200, 30, 30),
    "accent_red": (220, 40, 40),
    "bar_bg": (0, 0, 0, 180),  # semi-transparent
    "green_wave": (0, 255, 136),
    "blue_wave": (68, 136, 255),
    "teal": (0, 212, 170),      # #00D4AA — information, context
    "gold": (212, 168, 67),     # #D4A843 — victim, family
}

WIDTH = 1920
HEIGHT = 1080


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a font, falling back to default if system fonts unavailable."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def lower_third(
    name: str,
    role: str,
    output_path: str | Path,
    bar_width: int = 700,
) -> Path:
    """Generate a lower third overlay PNG (transparent background)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Semi-transparent dark bar at bottom
    d.rectangle([(0, 920), (bar_width, HEIGHT)], fill=COLORS["bar_bg"])
    # Red accent line on top of bar
    d.rectangle([(0, 920), (bar_width, 924)], fill=COLORS["dark_red"])

    # Name text
    name_font = _get_font(42, bold=True)
    d.text((30, 940), name, fill=COLORS["white"], font=name_font)

    # Role text
    role_font = _get_font(28)
    d.text((30, 990), role, fill=COLORS["gray"], font=role_font)

    img.save(str(output_path))
    return output_path


def timeline_marker(
    date: str,
    description: str,
    output_path: str | Path,
) -> Path:
    """Generate a timeline marker graphic (full-frame, dark background)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    # Red accent line
    d.rectangle([(860, 400), (1060, 404)], fill=COLORS["accent_red"])

    # Date
    date_font = _get_font(72, bold=True)
    bbox = d.textbbox((0, 0), date, font=date_font)
    text_width = bbox[2] - bbox[0]
    d.text(((WIDTH - text_width) // 2, 420), date, fill=COLORS["white"], font=date_font)

    # Description
    desc_font = _get_font(36)
    bbox = d.textbbox((0, 0), description, font=desc_font)
    text_width = bbox[2] - bbox[0]
    d.text(((WIDTH - text_width) // 2, 510), description, fill=COLORS["light_gray"], font=desc_font)

    img.save(str(output_path))
    return output_path


def quote_card(
    quote: str,
    speaker: str,
    output_path: str | Path,
    context: str = "",
    accent: str = "red",  # "red" (threats), "teal" (info), "gold" (victim)
) -> Path:
    """Generate a key quote card."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_darker"])
    d = ImageDraw.Draw(img)

    accent_color = COLORS.get(accent, COLORS["red"])

    # Big quote mark in accent color
    quote_mark_font = _get_font(120, bold=True)
    d.text((200, 300), "\u201c", fill=accent_color, font=quote_mark_font)

    # Quote text (word wrap)
    quote_font = _get_font(48)
    lines = _word_wrap(d, quote, quote_font, max_width=1400)
    y = 400
    for line in lines:
        d.text((250, y), line, fill=COLORS["white"], font=quote_font)
        y += 60

    # Attribution
    attr_font = _get_font(30)
    attribution = f"\u2014 {speaker}"
    if context:
        attribution += f", {context}"
    d.text((250, y + 40), attribution, fill=COLORS["light_gray"], font=attr_font)

    img.save(str(output_path))
    return output_path


def financial_card(
    amount: str,
    description: str,
    output_path: str | Path,
) -> Path:
    """Generate a financial amount card."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    # Big red amount
    amount_font = _get_font(96, bold=True)
    bbox = d.textbbox((0, 0), amount, font=amount_font)
    text_width = bbox[2] - bbox[0]
    d.text(((WIDTH - text_width) // 2, 420), amount, fill=COLORS["red"], font=amount_font)

    # Description
    desc_font = _get_font(32)
    bbox = d.textbbox((0, 0), description, font=desc_font)
    text_width = bbox[2] - bbox[0]
    d.text(((WIDTH - text_width) // 2, 540), description, fill=COLORS["gray"], font=desc_font)

    img.save(str(output_path))
    return output_path


def text_overlay(
    text: str,
    output_path: str | Path,
    position: str = "center",
    font_size: int = 48,
    color: tuple = COLORS["white"],
) -> Path:
    """Generate a text overlay PNG (transparent background)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    font = _get_font(font_size, bold=True)
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    positions = {
        "center": ((WIDTH - text_width) // 2, (HEIGHT - text_height) // 2),
        "bottom": ((WIDTH - text_width) // 2, HEIGHT - text_height - 100),
        "top": ((WIDTH - text_width) // 2, 100),
    }
    x, y = positions.get(position, positions["center"])

    d.text((x, y), text, fill=color, font=font)

    img.save(str(output_path))
    return output_path


def black_frame(output_path: str | Path) -> Path:
    """Generate a solid black frame (useful for fade transitions)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    img.save(str(output_path))
    return output_path


def mugshot_card(
    photo_path: str | Path,
    charges: list[str],
    sentence: str,
    output_path: str | Path,
) -> Path:
    """Generate a mugshot + charges split card.

    Layout: Photo on right (~40%), charges in red on left (~60%), dark background.
    Spec: visual-storyboard-bible.md [MUGSHOT-CARD]
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    # Right panel: photo (~40% = 768px wide), vertically centered
    photo_panel_x = WIDTH - 768
    photo_loaded = False
    try:
        photo = Image.open(str(photo_path)).convert("RGB")
        # Scale to fit within 768 x HEIGHT, preserving aspect ratio
        photo.thumbnail((768, HEIGHT), Image.LANCZOS)
        px = photo_panel_x + (768 - photo.width) // 2
        py = (HEIGHT - photo.height) // 2
        img.paste(photo, (px, py))
        photo_loaded = True
    except Exception:
        pass

    if not photo_loaded:
        # Gray placeholder rectangle
        d.rectangle(
            [(photo_panel_x, 0), (WIDTH, HEIGHT)],
            fill=(80, 80, 80),
        )

    # Left panel text (~60% = 1152px wide), starting at x=80
    text_x = 80
    text_max_width = photo_panel_x - text_x - 40

    header_font = _get_font(42, bold=True)
    body_font = _get_font(28)

    y = 200

    # "Charges:" header in red
    d.text((text_x, y), "Charges:", fill=COLORS["red"], font=header_font)
    y += 60

    # Each charge as a bulleted line in white
    for charge in charges:
        lines = _word_wrap(d, f"\u2022 {charge}", body_font, text_max_width)
        for line in lines:
            d.text((text_x, y), line, fill=COLORS["white"], font=body_font)
            y += 40
    y += 30

    # "Sentence:" header in red
    d.text((text_x, y), "Sentence:", fill=COLORS["red"], font=header_font)
    y += 60

    # Sentence text in white
    sentence_lines = _word_wrap(d, sentence, body_font, text_max_width)
    for line in sentence_lines:
        d.text((text_x, y), line, fill=COLORS["white"], font=body_font)
        y += 40

    img.save(str(output_path))
    return output_path


def _word_wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Simple word wrap for text within a given pixel width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines
