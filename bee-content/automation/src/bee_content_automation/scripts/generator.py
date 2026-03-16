"""LLM-assisted script generator for YouTube videos.

Takes chapter summaries, character info, and series context to produce
a narrated video script with visual cues.

Requires the `anthropic` package (install with: pip install bee-content-automation[llm]).
"""

from ..models import ChapterSummary, Series, VideoScript, ScriptSegment


def build_prompt(
    series: Series,
    summary: ChapterSummary,
    characters: list[dict] | None = None,
    style: str = "analytical",
) -> str:
    """Build the LLM prompt for script generation.

    Args:
        series: Series metadata.
        summary: Chapter synopsis and events.
        characters: Optional character info dicts.
        style: Script style — "analytical", "hype", "recap".

    Returns:
        Formatted prompt string.
    """
    style_instructions = {
        "analytical": (
            "Write in an analytical, thoughtful tone. Break down themes, "
            "symbolism, and character development. Think like a literature "
            "professor who's also a huge fan."
        ),
        "hype": (
            "Write with energy and excitement. Use dramatic pauses, build "
            "tension, and make the audience feel the hype. Think like a "
            "sports commentator narrating an anime fight."
        ),
        "recap": (
            "Write a clear, engaging recap. Cover all major events in order, "
            "but add your own observations and reactions. Think like a friend "
            "catching someone up on what they missed."
        ),
    }

    char_section = ""
    if characters:
        char_lines = []
        for c in characters[:5]:  # top 5 characters
            name = c.get("name", "Unknown")
            desc = c.get("description", "")[:200]
            char_lines.append(f"- {name}: {desc}")
        char_section = f"\n\nKEY CHARACTERS:\n" + "\n".join(char_lines)

    events_section = ""
    if summary.key_events:
        events_section = "\n\nKEY EVENTS:\n" + "\n".join(
            f"- {e}" for e in summary.key_events
        )

    return f"""You are a YouTube content creator making a video about {series.display_title} Chapter {summary.chapter_number}.

SERIES INFO:
- Title: {series.display_title}
- Genres: {', '.join(series.genres)}
- Status: {series.status}
- Synopsis: {series.synopsis[:500]}
{char_section}

CHAPTER {summary.chapter_number} SYNOPSIS:
{summary.synopsis[:2000]}
{events_section}

STYLE: {style_instructions.get(style, style_instructions['analytical'])}

Write a video script with these sections:
1. HOOK (5-10 seconds) — An attention-grabbing opening line
2. INTRO (15-20 seconds) — Brief series context for new viewers
3. RECAP (30-60 seconds) — Quick recap of relevant previous events
4. ANALYSIS (2-4 minutes) — Deep dive into this chapter's events, themes, and implications
5. OUTRO (15-20 seconds) — Wrap up with predictions or questions for viewers

For each section, include:
- The narration text
- [VISUAL: description] tags for what should appear on screen
- Estimated duration

Keep the total script between 4-6 minutes of narration.
Do NOT use copyrighted panel images — describe what should be shown as AI-generated art or text overlays.
"""


def parse_script_response(
    response_text: str,
    series_title: str,
    chapter_number: float,
) -> VideoScript:
    """Parse LLM response into a structured VideoScript.

    This is a best-effort parser — LLM output is inherently variable.

    Args:
        response_text: Raw LLM response text.
        series_title: Series title for metadata.
        chapter_number: Chapter number for metadata.

    Returns:
        VideoScript with parsed segments.
    """
    import re

    segments = []
    section_patterns = [
        (r"(?:1\.\s*)?HOOK", "hook"),
        (r"(?:2\.\s*)?INTRO", "intro"),
        (r"(?:3\.\s*)?RECAP", "recap"),
        (r"(?:4\.\s*)?ANALYSIS", "analysis"),
        (r"(?:5\.\s*)?OUTRO", "outro"),
    ]

    # Split by section headers
    section_texts = re.split(
        r"(?:^|\n)(?:\d+\.\s*)?(?:HOOK|INTRO|RECAP|ANALYSIS|OUTRO)\b",
        response_text,
        flags=re.IGNORECASE,
    )

    # Match sections to types
    for i, (pattern, seg_type) in enumerate(section_patterns):
        text_idx = i + 1  # first split is text before first header
        if text_idx < len(section_texts):
            text = section_texts[text_idx].strip()
            # Extract visual notes
            visual_notes = []
            for match in re.finditer(r"\[VISUAL:\s*([^\]]+)\]", text):
                visual_notes.append(match.group(1))

            # Estimate duration: ~150 words per minute for narration
            word_count = len(text.split())
            duration = (word_count / 150) * 60

            segments.append(ScriptSegment(
                type=seg_type,
                text=text,
                duration_estimate=duration,
                visual_notes="\n".join(visual_notes),
            ))

    # Generate title and description
    title = f"{series_title} Chapter {chapter_number} - Analysis & Discussion"
    description = (
        f"Deep dive into {series_title} Chapter {chapter_number}. "
        f"Analysis, discussion, and predictions.\n\n"
        f"#anime #manga #{series_title.replace(' ', '')}"
    )

    return VideoScript(
        series_title=series_title,
        chapter_number=chapter_number,
        title=title,
        description=description,
        tags=[
            series_title.lower(),
            "manga",
            "anime",
            f"chapter {int(chapter_number)}",
            "analysis",
            "discussion",
        ],
        segments=segments,
    )


async def generate_script(
    series: Series,
    summary: ChapterSummary,
    characters: list[dict] | None = None,
    style: str = "analytical",
    api_key: str | None = None,
) -> VideoScript:
    """Generate a video script using Claude.

    Requires the `anthropic` package.

    Args:
        series: Series metadata.
        summary: Chapter synopsis.
        characters: Optional character info.
        style: Script style.
        api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var).

    Returns:
        VideoScript ready for production.

    Raises:
        ImportError: If anthropic package not installed.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package required for script generation. "
            "Install with: pip install bee-content-automation[llm]"
        )

    prompt = build_prompt(series, summary, characters, style)

    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    return parse_script_response(
        response_text, series.display_title, summary.chapter_number
    )
