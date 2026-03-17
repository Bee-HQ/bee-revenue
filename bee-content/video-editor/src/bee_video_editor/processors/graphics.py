"""Generate production graphics (lower thirds, timeline markers, quotes, etc.)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
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
    # Chat / social
    "imessage_blue": (0, 122, 255),
    "imessage_grey": (229, 229, 234),
    "sms_green": (52, 199, 89),
    "facebook_blue": (24, 119, 242),
    "instagram_pink": (225, 48, 108),
    "snapchat_yellow": (255, 252, 0),
    "newsprint": (245, 240, 232),
    "corkboard": (42, 31, 20),
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


@dataclass
class ChatMessage:
    text: str
    sender: bool = True
    timestamp: str | None = None


@dataclass
class SocialPost:
    username: str
    text: str
    platform: str = "facebook"
    timestamp: str | None = None
    highlight_text: str | None = None


def _draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple,
) -> None:
    """Draw a filled rectangle with rounded corners."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius * 2, y0 + radius * 2], fill=fill)
    draw.ellipse([x1 - radius * 2, y0, x1, y0 + radius * 2], fill=fill)
    draw.ellipse([x0, y1 - radius * 2, x0 + radius * 2, y1], fill=fill)
    draw.ellipse([x1 - radius * 2, y1 - radius * 2, x1, y1], fill=fill)


def _underline_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    needle: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    line_color: tuple,
) -> None:
    """Draw a red underline under needle within text starting at (x, y)."""
    if needle not in text:
        return
    before = text[: text.index(needle)]
    bbox_before = draw.textbbox((0, 0), before, font=font)
    needle_bbox = draw.textbbox((0, 0), needle, font=font)
    ux = x + (bbox_before[2] - bbox_before[0])
    uw = needle_bbox[2] - needle_bbox[0]
    uh = needle_bbox[3] - needle_bbox[1]
    draw.line([(ux, y + uh + 2), (ux + uw, y + uh + 2)], fill=line_color, width=3)


def text_chat(
    messages: list[ChatMessage],
    output_path: str | Path,
    platform: str = "imessage",
    highlight_text: str | None = None,
) -> Path:
    """Generate a chat conversation screenshot graphic (1920x1080)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    # Platform bubble color for sender
    if platform == "imessage":
        sender_color = COLORS["imessage_blue"]
        sender_text = COLORS["white"]
    elif platform == "sms":
        sender_color = COLORS["sms_green"]
        sender_text = COLORS["white"]
    else:
        sender_color = (60, 60, 70)
        sender_text = COLORS["white"]

    receiver_color = COLORS["imessage_grey"]
    receiver_text = (30, 30, 30)

    body_font = _get_font(32)
    ts_font = _get_font(22)

    bubble_max_width = 700
    padding = 20
    radius = 18
    margin_x = 80
    y = 80

    for msg in messages:
        # Optional timestamp above bubble
        if msg.timestamp:
            ts_bbox = d.textbbox((0, 0), msg.timestamp, font=ts_font)
            ts_w = ts_bbox[2] - ts_bbox[0]
            d.text(((WIDTH - ts_w) // 2, y), msg.timestamp, fill=COLORS["gray"], font=ts_font)
            y += 36

        lines = _word_wrap(d, msg.text, body_font, bubble_max_width - padding * 2)
        line_h = 40
        bubble_h = len(lines) * line_h + padding * 2
        bubble_w = min(
            max(
                d.textbbox((0, 0), line, font=body_font)[2]
                for line in lines
            ) + padding * 2,
            bubble_max_width,
        )

        if msg.sender:
            bx0 = WIDTH - margin_x - bubble_w
            bx1 = WIDTH - margin_x
            fill = sender_color
            text_color = sender_text
        else:
            bx0 = margin_x
            bx1 = margin_x + bubble_w
            fill = receiver_color
            text_color = receiver_text

        _draw_rounded_rect(d, (bx0, y, bx1, y + bubble_h), radius, fill)

        ty = y + padding
        for line in lines:
            d.text((bx0 + padding, ty), line, fill=text_color, font=body_font)
            if highlight_text and highlight_text in line:
                _underline_text(d, line, highlight_text, bx0 + padding, ty, body_font, COLORS["red"])
            ty += line_h

        y += bubble_h + 16

        if y > HEIGHT - 80:
            break

    img.save(str(output_path))
    return output_path


def social_post(
    post: SocialPost,
    output_path: str | Path,
) -> Path:
    """Generate a social media post card graphic (1920x1080)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    platform_colors = {
        "facebook": COLORS["facebook_blue"],
        "instagram": COLORS["instagram_pink"],
        "twitter": (0, 0, 0),
        "snapchat": COLORS["snapchat_yellow"],
    }
    header_color = platform_colors.get(post.platform, COLORS["facebook_blue"])

    card_w = 1200
    card_x = (WIDTH - card_w) // 2
    card_y = 120
    header_h = 60
    card_padding = 40

    # Estimate card height based on text
    body_font = _get_font(34)
    meta_font = _get_font(26)
    username_font = _get_font(30, bold=True)

    body_lines = _word_wrap(d, post.text, body_font, card_w - card_padding * 2)
    body_h = len(body_lines) * 48

    card_h = header_h + 80 + body_h + card_padding * 2

    # Card background (dark surface)
    card_color = (28, 28, 35)
    d.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill=card_color)

    # Platform header bar
    d.rectangle([(card_x, card_y), (card_x + card_w, card_y + header_h)], fill=header_color)

    # Username + timestamp
    uy = card_y + header_h + 20
    d.text((card_x + card_padding, uy), post.username, fill=COLORS["white"], font=username_font)
    if post.timestamp:
        ts_bbox = d.textbbox((0, 0), post.timestamp, font=meta_font)
        ts_w = ts_bbox[2] - ts_bbox[0]
        d.text((card_x + card_w - card_padding - ts_w, uy + 2), post.timestamp, fill=COLORS["gray"], font=meta_font)

    # Body text
    ty = uy + 52
    for line in body_lines:
        d.text((card_x + card_padding, ty), line, fill=COLORS["white"], font=body_font)
        if post.highlight_text and post.highlight_text in line:
            _underline_text(d, line, post.highlight_text, card_x + card_padding, ty, body_font, COLORS["red"])
        ty += 48

    img.save(str(output_path))
    return output_path


def _get_serif_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a bold serif font for news/print graphics, falling back to sans-serif."""
    serif_paths = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ]
    for path in serif_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return _get_font(size, bold=True)


def news_montage(
    headlines: list[str],
    output_path: str | Path,
) -> Path:
    """Generate a news headline montage (1920x1080, stacked newspaper cards)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])

    if headlines:
        headline_font = _get_serif_font(52)
        card_w = 1400
        card_h = 130
        overlap = 20
        total_h = len(headlines) * card_h - (len(headlines) - 1) * overlap
        start_y = (HEIGHT - total_h) // 2

        rotations = [-2, 1.5, -1, 2, -1.5, 1]

        for i, headline in enumerate(headlines[:6]):
            angle = rotations[i % len(rotations)]
            card_x = (WIDTH - card_w) // 2
            card_y = start_y + i * (card_h - overlap)

            # Create card as separate image so we can rotate it
            card = Image.new("RGBA", (card_w + 20, card_h + 20), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            cd.rectangle([(10, 10), (card_w + 10, card_h + 10)], fill=COLORS["newsprint"])

            # Wrap and draw headline text on the card
            lines = _word_wrap(cd, headline, headline_font, card_w - 60)
            ty = 10 + (card_h - len(lines) * 58) // 2
            for line in lines:
                cd.text((40, ty), line, fill=(20, 20, 20), font=headline_font)
                ty += 58

            # Rotate card
            card_rotated = card.rotate(angle, expand=True, resample=Image.BICUBIC)

            # Paste rotated card onto main image
            paste_x = card_x - (card_rotated.width - card_w) // 2
            paste_y = card_y - (card_rotated.height - card_h) // 2
            img.paste(card_rotated, (paste_x, paste_y), card_rotated)

    img.save(str(output_path))
    return output_path


@dataclass
class BoardPerson:
    name: str
    photo_path: Path | None = None


@dataclass
class BoardConnection:
    from_name: str
    to_name: str
    label: str


def evidence_board(
    people: list[BoardPerson],
    connections: list[BoardConnection],
    output_path: str | Path,
) -> Path:
    """Generate an evidence board graphic with person cards and red connection lines."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["corkboard"])
    d = ImageDraw.Draw(img)

    if not people:
        img.save(str(output_path))
        return output_path

    card_w = 160
    card_h = 200
    photo_h = 150
    name_font = _get_font(24, bold=True)
    label_font = _get_font(20)

    # Compute person card center positions
    positions: dict[str, tuple[int, int]] = {}

    n = len(people)
    if n <= 6:
        # Arrange in a circle
        cx, cy = WIDTH // 2, HEIGHT // 2
        radius = min(WIDTH, HEIGHT) // 2 - 160
        for i, person in enumerate(people):
            angle = 2 * math.pi * i / n - math.pi / 2
            px = int(cx + radius * math.cos(angle))
            py = int(cy + radius * math.sin(angle))
            positions[person.name] = (px, py)
    else:
        # Grid layout
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        x_spacing = WIDTH // (cols + 1)
        y_spacing = HEIGHT // (rows + 1)
        for i, person in enumerate(people):
            col = i % cols
            row = i // cols
            positions[person.name] = ((col + 1) * x_spacing, (row + 1) * y_spacing)

    # Draw red connection lines first (behind cards)
    line_color = (220, 50, 50)  # #DC3232
    for conn in connections:
        if conn.from_name in positions and conn.to_name in positions:
            x0, y0 = positions[conn.from_name]
            x1, y1 = positions[conn.to_name]
            d.line([(x0, y0), (x1, y1)], fill=line_color, width=3)
            # Label at midpoint
            mx, my = (x0 + x1) // 2, (y0 + y1) // 2
            lbbox = d.textbbox((0, 0), conn.label, font=label_font)
            lw = lbbox[2] - lbbox[0]
            lh = lbbox[3] - lbbox[1]
            d.rectangle([(mx - lw // 2 - 4, my - lh // 2 - 2), (mx + lw // 2 + 4, my + lh // 2 + 2)], fill=COLORS["corkboard"])
            d.text((mx - lw // 2, my - lh // 2), conn.label, fill=COLORS["white"], font=label_font)

    # Draw person cards
    for person in people:
        cx, cy = positions[person.name]
        card_x = cx - card_w // 2
        card_y = cy - card_h // 2

        # Card background (cream/off-white)
        d.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill=(230, 220, 200))

        # Photo area
        photo_loaded = False
        if person.photo_path is not None:
            try:
                photo = Image.open(str(person.photo_path)).convert("RGB")
                photo.thumbnail((card_w - 4, photo_h - 4), Image.LANCZOS)
                px = card_x + (card_w - photo.width) // 2
                py = card_y + 2 + (photo_h - photo.height) // 2
                img.paste(photo, (px, py))
                photo_loaded = True
            except Exception:
                pass

        if not photo_loaded:
            # Grey placeholder
            d.rectangle(
                [(card_x + 2, card_y + 2), (card_x + card_w - 2, card_y + photo_h)],
                fill=(140, 140, 140),
            )

        # Name label below photo
        nbbox = d.textbbox((0, 0), person.name, font=name_font)
        nw = nbbox[2] - nbbox[0]
        nx = card_x + (card_w - nw) // 2
        ny = card_y + photo_h + 8
        d.text((nx, ny), person.name, fill=(20, 20, 20), font=name_font)

    img.save(str(output_path))
    return output_path


@dataclass
class FlowNode:
    name: str
    node_type: str = "box"  # "box" or "circle"


@dataclass
class FlowArrow:
    from_name: str
    to_name: str
    label: str          # e.g. "$4.3M", "settlement funds"
    color: str = "red"  # "red" for money/danger, "teal" for info


def _draw_arrowhead(
    d: ImageDraw.ImageDraw,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: tuple,
    size: int = 15,
) -> None:
    """Draw a filled triangle arrowhead at (x2, y2) pointing from (x1, y1)."""
    angle = math.atan2(y2 - y1, x2 - x1)
    left_x = x2 - size * math.cos(angle - math.pi / 6)
    left_y = y2 - size * math.sin(angle - math.pi / 6)
    right_x = x2 - size * math.cos(angle + math.pi / 6)
    right_y = y2 - size * math.sin(angle + math.pi / 6)
    d.polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], fill=color)


def flow_diagram(
    nodes: list[FlowNode],
    arrows: list[FlowArrow],
    output_path: str | Path,
) -> Path:
    """Generate a flow diagram showing connections between entities.

    Nodes arranged left-to-right, connected by directional arrows.
    Spec: visual-storyboard-bible.md [FLOW-DIAGRAM]
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    if not nodes:
        img.save(str(output_path))
        return output_path

    node_w = 200
    node_h = 80
    circle_r = 50  # radius for circle nodes

    # Layout: single row for ≤4 nodes, two rows for 5+
    n = len(nodes)
    if n <= 4:
        rows = 1
        cols = n
    else:
        rows = 2
        cols = math.ceil(n / 2)

    # Compute center positions for each node
    positions: dict[str, tuple[int, int]] = {}

    if rows == 1:
        # Single row, vertically centered
        x_spacing = WIDTH // (cols + 1)
        cy = HEIGHT // 2
        for i, node in enumerate(nodes):
            cx = (i + 1) * x_spacing
            positions[node.name] = (cx, cy)
    else:
        # Two rows
        x_spacing = WIDTH // (cols + 1)
        row_y = [HEIGHT // 3, 2 * HEIGHT // 3]
        for i, node in enumerate(nodes):
            col = i % cols
            row = i // cols
            cx = (col + 1) * x_spacing
            cy = row_y[row]
            positions[node.name] = (cx, cy)

    name_font = _get_font(28, bold=True)
    label_font = _get_font(24)

    # Draw arrows first (behind nodes)
    for arrow in arrows:
        if arrow.from_name not in positions or arrow.to_name not in positions:
            continue
        x0, y0 = positions[arrow.from_name]
        x1, y1 = positions[arrow.to_name]
        arrow_color = COLORS.get(arrow.color, COLORS["red"])

        # Shorten line so it doesn't overlap node boundaries
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue

        # Offset start and end by node half-size
        src_node = next((node for node in nodes if node.name == arrow.from_name), None)
        dst_node = next((node for node in nodes if node.name == arrow.to_name), None)
        src_offset = circle_r if (src_node and src_node.node_type == "circle") else max(node_w, node_h) // 2
        dst_offset = circle_r if (dst_node and dst_node.node_type == "circle") else max(node_w, node_h) // 2

        # Add a little padding
        src_offset += 5
        dst_offset += 20  # leave room for arrowhead

        sx = int(x0 + dx / dist * src_offset)
        sy = int(y0 + dy / dist * src_offset)
        ex = int(x1 - dx / dist * dst_offset)
        ey = int(y1 - dy / dist * dst_offset)

        d.line([(sx, sy), (ex, ey)], fill=arrow_color, width=3)

        # Arrowhead at destination end
        _draw_arrowhead(d, sx, sy, int(x1 - dx / dist * (dst_offset - 15)), int(y1 - dy / dist * (dst_offset - 15)), arrow_color)

        # Label at midpoint
        mx = (sx + ex) // 2
        my = (sy + ey) // 2
        lbbox = d.textbbox((0, 0), arrow.label, font=label_font)
        lw = lbbox[2] - lbbox[0]
        lh = lbbox[3] - lbbox[1]
        # Small dark background behind label for readability
        pad = 4
        d.rectangle(
            [(mx - lw // 2 - pad, my - lh // 2 - pad), (mx + lw // 2 + pad, my + lh // 2 + pad)],
            fill=COLORS["bg_dark"],
        )
        d.text((mx - lw // 2, my - lh // 2), arrow.label, fill=COLORS["white"], font=label_font)

    # Draw nodes on top
    for node in nodes:
        cx, cy = positions[node.name]

        if node.node_type == "circle":
            # Dark circle with subtle border
            d.ellipse(
                [(cx - circle_r, cy - circle_r), (cx + circle_r, cy + circle_r)],
                fill=COLORS["bg_darker"],
                outline=(60, 60, 70),
                width=2,
            )
            # Center text
            nbbox = d.textbbox((0, 0), node.name, font=name_font)
            nw = nbbox[2] - nbbox[0]
            nh = nbbox[3] - nbbox[1]
            d.text((cx - nw // 2, cy - nh // 2), node.name, fill=COLORS["white"], font=name_font)
        else:
            # Dark rectangle with subtle border (~200x80)
            rx0 = cx - node_w // 2
            ry0 = cy - node_h // 2
            rx1 = cx + node_w // 2
            ry1 = cy + node_h // 2
            d.rectangle([(rx0, ry0), (rx1, ry1)], fill=COLORS["bg_darker"], outline=(60, 60, 70), width=2)
            # Center text (wrap if needed)
            lines = _word_wrap(d, node.name, name_font, node_w - 16)
            line_h = 34
            total_text_h = len(lines) * line_h
            ty = cy - total_text_h // 2
            for line in lines:
                lbbox = d.textbbox((0, 0), line, font=name_font)
                lw = lbbox[2] - lbbox[0]
                d.text((cx - lw // 2, ty), line, fill=COLORS["white"], font=name_font)
                ty += line_h

    img.save(str(output_path))
    return output_path


@dataclass
class TimelineEvent:
    date: str               # e.g. "June 7, 2021", "Feb 24, 2019"
    label: str              # e.g. "Double Murder", "Boat Crash"
    active: bool = True     # True = past/current (red), False = future (dim grey)
    current: bool = False   # True = highlighted as current event (white, larger)


def timeline_sequence(
    events: list[TimelineEvent],
    output_path: str | Path,
    title: str = "",
) -> Path:
    """Generate a horizontal timeline showing event progression.

    Events are placed left-to-right along a horizontal line.
    Spec: visual-storyboard-bible.md [TIMELINE-SEQUENCE]
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    d = ImageDraw.Draw(img)

    # Optional title at top center
    if title:
        title_font = _get_font(36, bold=True)
        tbbox = d.textbbox((0, 0), title, font=title_font)
        tw = tbbox[2] - tbbox[0]
        d.text(((WIDTH - tw) // 2, 60), title, fill=COLORS["white"], font=title_font)

    # Timeline geometry
    line_y = HEIGHT // 2
    line_x0 = 100
    line_x1 = 1820

    node_radius = 20
    current_radius = 25

    date_font = _get_font(22)
    label_font = _get_font(20)

    # Colours
    grey_line = (85, 85, 85)        # #555555 for future line segments
    dim_grey = (68, 68, 68)         # #444444 for future nodes
    red = COLORS["red"]
    white = COLORS["white"]

    if not events:
        # Just draw a plain grey line
        d.line([(line_x0, line_y), (line_x1, line_y)], fill=grey_line, width=2)
        img.save(str(output_path))
        return output_path

    n = len(events)
    if n == 1:
        positions = [(line_x0 + line_x1) // 2]
    else:
        span = line_x1 - line_x0
        positions = [line_x0 + round(i * span / (n - 1)) for i in range(n)]

    # Draw the line in segments: red between active nodes, grey between future
    for i in range(len(positions) - 1):
        x0 = positions[i]
        x1 = positions[i + 1]
        # Segment colour: red if both endpoints are active (past), else grey
        seg_color = red if (events[i].active and events[i + 1].active) else grey_line
        d.line([(x0, line_y), (x1, line_y)], fill=seg_color, width=2)

    # If only one node, still draw the background line
    if n == 1:
        line_color = red if events[0].active else grey_line
        d.line([(line_x0, line_y), (line_x1, line_y)], fill=line_color, width=2)

    # Draw nodes and labels
    for i, (event, x) in enumerate(zip(events, positions)):
        if event.current:
            r = current_radius
            node_fill = white
        elif event.active:
            r = node_radius
            node_fill = red
        else:
            r = node_radius
            node_fill = dim_grey

        # Circle on the line
        d.ellipse([(x - r, line_y - r), (x + r, line_y + r)], fill=node_fill)

        # Date text above the node
        dbbox = d.textbbox((0, 0), event.date, font=date_font)
        dw = dbbox[2] - dbbox[0]
        dh = dbbox[3] - dbbox[1]
        d.text((x - dw // 2, line_y - r - dh - 10), event.date, fill=white, font=date_font)

        # Label text below the node (word-wrapped, grey)
        label_max_w = max(120, (line_x1 - line_x0) // n - 10)
        label_lines = _word_wrap(d, event.label, label_font, label_max_w)
        ly = line_y + r + 12
        for line in label_lines:
            lbbox = d.textbbox((0, 0), line, font=label_font)
            lw = lbbox[2] - lbbox[0]
            d.text((x - lw // 2, ly), line, fill=COLORS["light_gray"], font=label_font)
            ly += 26

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
