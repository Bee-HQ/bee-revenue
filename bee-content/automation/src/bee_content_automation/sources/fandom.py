"""Fandom Wiki API integration.

Uses the MediaWiki API that every Fandom wiki exposes to pull chapter
synopses, character descriptions, and plot summaries.

Fandom wikis follow the pattern: https://{subdomain}.fandom.com/api.php
"""

import re

import httpx

from ..models import ChapterSummary

FANDOM_SEARCH_URL = "https://community.fandom.com/api/v1/Search/CrossWiki"
RATE_LIMIT_DELAY = 0.5


class FandomError(Exception):
    """Fandom Wiki API error."""


async def _wiki_api(wiki: str, params: dict) -> dict:
    """Call the MediaWiki API on a Fandom wiki.

    Args:
        wiki: Wiki subdomain (e.g. "naruto", "onepiece").
        params: MediaWiki API parameters.
    """
    base_params = {
        "format": "json",
        "action": "query",
    }
    base_params.update(params)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"https://{wiki}.fandom.com/api.php",
            params=base_params,
            headers={"User-Agent": "bee-content-automation/0.1.0"},
        )
        if resp.status_code == 429:
            raise FandomError("Rate limited")
        resp.raise_for_status()
        return resp.json()


def _clean_wikitext(text: str) -> str:
    """Strip common wikitext markup to get plain-ish text."""
    # Remove references
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^/]*/?>", "", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove file/image links
    text = re.sub(r"\[\[File:[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[Image:[^\]]*\]\]", "", text)
    # Convert wiki links [[Page|Display]] -> Display, [[Page]] -> Page
    text = re.sub(r"\[\[[^\]]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    # Remove bold/italic markup
    text = re.sub(r"'{2,}", "", text)
    # Remove templates (simple ones)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def search_wiki(series_name: str) -> str | None:
    """Find the Fandom wiki for a series.

    Args:
        series_name: Name of the series to find a wiki for.

    Returns:
        Wiki subdomain (e.g. "naruto") or None if not found.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            FANDOM_SEARCH_URL,
            params={
                "query": series_name,
                "lang": "en",
                "limit": 5,
            },
            headers={"User-Agent": "bee-content-automation/0.1.0"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()

    results = data.get("items", [])
    if not results:
        return None

    # Find the best match — look for the wiki URL
    for result in results:
        url = result.get("url", "")
        # Extract subdomain from https://xyz.fandom.com
        match = re.match(r"https?://([^.]+)\.fandom\.com", url)
        if match:
            subdomain = match.group(1)
            # Skip community/general wikis
            if subdomain not in ("community", "www"):
                return subdomain

    return None


async def get_chapter_summary(
    wiki: str, chapter_number: int
) -> ChapterSummary | None:
    """Get chapter synopsis from a Fandom wiki.

    Tries multiple page naming conventions that wikis use for chapters.

    Args:
        wiki: Wiki subdomain.
        chapter_number: Chapter number to look up.

    Returns:
        ChapterSummary or None if not found.
    """
    # Different wikis use different naming conventions for chapter pages
    page_candidates = [
        f"Chapter {chapter_number}",
        f"Chapter_{chapter_number}",
        f"Ch. {chapter_number}",
        f"Episode {chapter_number}",
    ]

    for page_title in page_candidates:
        data = await _wiki_api(wiki, {
            "titles": page_title,
            "prop": "extracts|revisions",
            "explaintext": "1",
            "exlimit": "1",
            "rvprop": "content",
            "rvslots": "main",
        })
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                continue
            # Try extract first (clean text)
            synopsis = page.get("extract", "")
            if not synopsis:
                # Fall back to raw wikitext
                revisions = page.get("revisions", [])
                if revisions:
                    content = (
                        revisions[0]
                        .get("slots", {})
                        .get("main", {})
                        .get("*", "")
                    )
                    synopsis = _clean_wikitext(content)

            if synopsis:
                # Try to extract character names from links in the content
                characters = _extract_characters(synopsis)
                events = _extract_key_events(synopsis)
                return ChapterSummary(
                    series_title=wiki.replace("-", " ").title(),
                    chapter_number=float(chapter_number),
                    synopsis=synopsis[:3000],  # cap length
                    characters=characters,
                    key_events=events,
                    source="fandom_wiki",
                )

    return None


def _extract_characters(text: str) -> list[str]:
    """Extract likely character names from synopsis text.

    Very basic heuristic: capitalized multi-word sequences that appear
    more than once.
    """
    # Find capitalized words that aren't common English words
    common = {
        "The", "This", "That", "They", "Their", "There", "These", "Those",
        "When", "Where", "What", "Which", "While", "With", "Without",
        "After", "Before", "During", "Since", "Until", "About", "Above",
        "Below", "Between", "Through", "However", "Although", "Because",
        "Chapter", "Episode", "Volume", "Part", "Also", "Then", "Later",
    }
    pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")
    matches = pattern.findall(text)
    # Count occurrences, filter common words
    counts: dict[str, int] = {}
    for m in matches:
        if m not in common and len(m) > 2:
            counts[m] = counts.get(m, 0) + 1
    # Return names mentioned more than once, sorted by frequency
    return sorted(
        [name for name, count in counts.items() if count >= 2],
        key=lambda n: counts[n],
        reverse=True,
    )[:10]


def _extract_key_events(text: str) -> list[str]:
    """Extract key events from synopsis. Splits by sentence and picks notable ones."""
    sentences = re.split(r"[.!?]+\s+", text)
    events = []
    for s in sentences:
        s = s.strip()
        if len(s) > 30 and len(s) < 200:
            events.append(s)
        if len(events) >= 5:
            break
    return events


async def get_character_info(wiki: str, character_name: str) -> dict | None:
    """Get character description from wiki.

    Args:
        wiki: Wiki subdomain.
        character_name: Character name as it appears on the wiki.

    Returns:
        Dict with keys: name, description, image_url, or None.
    """
    data = await _wiki_api(wiki, {
        "titles": character_name,
        "prop": "extracts|pageimages",
        "explaintext": "1",
        "exintro": "1",
        "pithumbsize": 300,
    })
    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1":
            return None
        return {
            "name": page.get("title", character_name),
            "description": page.get("extract", ""),
            "image_url": page.get("thumbnail", {}).get("source"),
        }
    return None
