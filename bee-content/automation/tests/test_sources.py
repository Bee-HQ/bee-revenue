"""Tests for data source integrations.

All tests mock HTTP calls — no real API requests.
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from bee_content_automation.models import Series, Chapter, ChapterSummary
from bee_content_automation.sources import anilist, mangadex, mangaupdates, fandom


# --- Fixtures ---

def _anilist_media():
    """Sample AniList media response."""
    return {
        "id": 30013,
        "title": {
            "english": "One Piece",
            "romaji": "One Piece",
            "native": "\u30ef\u30f3\u30d4\u30fc\u30b9",
        },
        "description": "A boy named Luffy sets out to become the Pirate King.",
        "genres": ["Action", "Adventure", "Comedy"],
        "tags": [
            {"name": "Shounen", "rank": 92},
            {"name": "Pirates", "rank": 88},
            {"name": "Superpowers", "rank": 40},  # below 50 threshold
        ],
        "status": "RELEASING",
        "chapters": None,
        "popularity": 500000,
        "meanScore": 88,
        "coverImage": {"large": "https://example.com/cover.jpg"},
        "bannerImage": "https://example.com/banner.jpg",
    }


def _mangadex_chapter():
    """Sample MangaDex chapter feed item."""
    return {
        "id": "abc-123-def",
        "type": "chapter",
        "attributes": {
            "chapter": "1",
            "title": "Romance Dawn",
            "translatedLanguage": "en",
            "pages": 24,
            "publishAt": "2024-01-15T00:00:00+00:00",
        },
        "relationships": [
            {
                "type": "scanlation_group",
                "attributes": {"name": "TCB Scans"},
            }
        ],
    }


# ==================== Model Tests ====================

class TestModels:
    def test_series_display_title_english(self):
        s = Series(id="1", title_english="One Piece", title_romaji="One Piece")
        assert s.display_title == "One Piece"

    def test_series_display_title_fallback_romaji(self):
        s = Series(id="1", title_english="", title_romaji="Wan Piisu")
        assert s.display_title == "Wan Piisu"

    def test_series_display_title_fallback_native(self):
        s = Series(id="1", title_english="", title_romaji="", title_native="\u30ef\u30f3\u30d4\u30fc\u30b9")
        assert s.display_title == "\u30ef\u30f3\u30d4\u30fc\u30b9"

    def test_series_display_title_fallback_unknown(self):
        s = Series(id="1", title_english="", title_romaji="")
        assert s.display_title == "Unknown"

    def test_series_defaults(self):
        s = Series(id="1", title_english="Test", title_romaji="Test")
        assert s.genres == []
        assert s.tags == []
        assert s.status == "UNKNOWN"
        assert s.chapters is None
        assert s.popularity == 0
        assert s.score is None

    def test_chapter_defaults(self):
        ch = Chapter(id="abc", number=1.0)
        assert ch.language == "en"
        assert ch.pages == 0
        assert ch.page_urls == []

    def test_chapter_summary_defaults(self):
        cs = ChapterSummary(series_title="Test", chapter_number=1.0)
        assert cs.synopsis == ""
        assert cs.characters == []
        assert cs.key_events == []
        assert cs.source == "unknown"


# ==================== AniList Tests ====================

class TestAniListParsing:
    def test_parse_series(self):
        data = _anilist_media()
        result = anilist._parse_series(data)
        assert result.id == "30013"
        assert result.title_english == "One Piece"
        assert result.title_romaji == "One Piece"
        assert result.title_native == "\u30ef\u30f3\u30d4\u30fc\u30b9"
        assert result.status == "RELEASING"
        assert result.popularity == 500000
        assert result.score == 8.8  # 88/10
        assert "Action" in result.genres
        # Only tags with rank >= 50
        assert "Shounen" in result.tags
        assert "Pirates" in result.tags
        assert "Superpowers" not in result.tags

    def test_parse_series_no_score(self):
        data = _anilist_media()
        data["meanScore"] = None
        result = anilist._parse_series(data)
        assert result.score is None

    def test_parse_series_missing_fields(self):
        data = {"id": 1, "title": {}, "tags": []}
        result = anilist._parse_series(data)
        assert result.id == "1"
        assert result.title_english == ""
        assert result.genres == []


class TestAniListAPI:
    @pytest.mark.asyncio
    async def test_search_manga(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "Page": {
                    "media": [_anilist_media()]
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            results = await anilist.search_manga("One Piece", limit=5)
            assert len(results) == 1
            assert results[0].title_english == "One Piece"
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_manga_empty(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"Page": {"media": []}}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            results = await anilist.search_manga("xyznonexistent")
            assert results == []

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "30"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(anilist.RateLimitError):
                await anilist.search_manga("test")

    @pytest.mark.asyncio
    async def test_graphql_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "Invalid query"}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(anilist.AniListError, match="Invalid query"):
                await anilist.search_manga("test")

    @pytest.mark.asyncio
    async def test_get_trending(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "Page": {
                    "media": [_anilist_media(), _anilist_media()]
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            results = await anilist.get_trending_manga(limit=10)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_series_details(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"Media": _anilist_media()}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await anilist.get_series_details(30013)
            assert result.title_english == "One Piece"

    @pytest.mark.asyncio
    async def test_get_series_not_found(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"Media": None}}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(anilist.AniListError, match="not found"):
                await anilist.get_series_details(99999999)

    @pytest.mark.asyncio
    async def test_get_characters(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "Media": {
                    "characters": {
                        "edges": [
                            {
                                "role": "MAIN",
                                "node": {
                                    "id": 1,
                                    "name": {"full": "Monkey D. Luffy", "native": "\u30eb\u30d5\u30a3"},
                                    "description": "The captain of the Straw Hat Pirates.",
                                    "image": {"large": "https://example.com/luffy.jpg"},
                                },
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            chars = await anilist.get_characters(30013)
            assert len(chars) == 1
            assert chars[0]["name"] == "Monkey D. Luffy"
            assert chars[0]["role"] == "MAIN"


# ==================== MangaDex Tests ====================

class TestMangaDexParsing:
    def test_chapter_parsing(self):
        """Test that MangaDex chapter feed items are parsed correctly."""
        item = _mangadex_chapter()
        attrs = item["attributes"]
        ch = Chapter(
            id=item["id"],
            number=float(attrs["chapter"]),
            title=attrs.get("title"),
            language="en",
            pages=attrs.get("pages", 0),
            scanlation_group="TCB Scans",
            published_at=attrs.get("publishAt", ""),
        )
        assert ch.id == "abc-123-def"
        assert ch.number == 1.0
        assert ch.title == "Romance Dawn"
        assert ch.pages == 24
        assert ch.scanlation_group == "TCB Scans"


class TestMangaDexAPI:
    @pytest.mark.asyncio
    async def test_search_manga(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "manga-uuid-123",
                    "attributes": {
                        "title": {"en": "Solo Leveling"},
                        "altTitles": [{"ko": "\ub098 \ud63c\uc790\ub9cc \ub808\ubca8\uc5c5"}],
                        "description": {"en": "A hunter story"},
                        "status": "completed",
                        "year": 2018,
                        "tags": [
                            {"attributes": {"name": {"en": "Action"}}}
                        ],
                        "contentRating": "safe",
                    },
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            results = await mangadex.search_manga("Solo Leveling")
            assert len(results) == 1
            assert results[0]["title"] == "Solo Leveling"
            assert results[0]["id"] == "manga-uuid-123"
            assert "Action" in results[0]["tags"]

    @pytest.mark.asyncio
    async def test_get_chapters(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                _mangadex_chapter(),
                {
                    "id": "abc-456-ghi",
                    "attributes": {
                        "chapter": "2",
                        "title": "They Call Him Luffy",
                        "translatedLanguage": "en",
                        "pages": 20,
                        "publishAt": "2024-01-22T00:00:00+00:00",
                    },
                    "relationships": [],
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            chapters = await mangadex.get_chapters("manga-id")
            assert len(chapters) == 2
            assert chapters[0].number == 1.0
            assert chapters[1].number == 2.0
            assert chapters[0].scanlation_group == "TCB Scans"
            assert chapters[1].scanlation_group is None

    @pytest.mark.asyncio
    async def test_get_chapters_skips_invalid_numbers(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "valid",
                    "attributes": {
                        "chapter": "5",
                        "title": None,
                        "pages": 18,
                        "publishAt": "",
                    },
                    "relationships": [],
                },
                {
                    "id": "no-number",
                    "attributes": {
                        "chapter": None,
                        "title": "Oneshot",
                        "pages": 30,
                        "publishAt": "",
                    },
                    "relationships": [],
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            chapters = await mangadex.get_chapters("manga-id")
            assert len(chapters) == 1
            assert chapters[0].number == 5.0

    @pytest.mark.asyncio
    async def test_get_chapter_pages(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "baseUrl": "https://uploads.mangadex.org",
            "chapter": {
                "hash": "abc123hash",
                "data": ["page1.jpg", "page2.jpg", "page3.jpg"],
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            urls = await mangadex.get_chapter_pages("ch-id")
            assert len(urls) == 3
            assert "abc123hash" in urls[0]
            assert urls[0].startswith("https://")

    @pytest.mark.asyncio
    async def test_get_cover(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "attributes": {"fileName": "cover.jpg"},
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            url = await mangadex.get_cover("manga-id")
            assert url is not None
            assert "manga-id" in url
            assert "cover.jpg" in url

    @pytest.mark.asyncio
    async def test_get_cover_none(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            url = await mangadex.get_cover("manga-id")
            assert url is None

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(mangadex.RateLimitError):
                await mangadex.search_manga("test")


# ==================== MangaUpdates Tests ====================

class TestMangaUpdatesAPI:
    @pytest.mark.asyncio
    async def test_search_series(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "record": {
                        "series_id": 12345,
                        "title": "Chainsaw Man",
                        "url": "https://mangaupdates.com/series/12345",
                        "description": "Denji is a young man living a life of poverty.",
                        "year": "2018",
                        "type": "Manga",
                        "genres": [{"genre": "Action"}, {"genre": "Horror"}],
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            results = await mangaupdates.search_series("Chainsaw Man")
            assert len(results) == 1
            assert results[0]["title"] == "Chainsaw Man"
            assert results[0]["id"] == 12345
            assert "Action" in results[0]["genres"]

    @pytest.mark.asyncio
    async def test_get_series_info(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "series_id": 12345,
            "title": "Chainsaw Man",
            "url": "https://mangaupdates.com/series/12345",
            "description": "Denji story",
            "type": "Manga",
            "year": "2018",
            "genres": [{"genre": "Action"}],
            "categories": [{"category": "Gore"}],
            "status": "Complete",
            "latest_chapter": 97,
            "authors": [{"name": "FUJIMOTO Tatsuki"}],
            "publishers": [{"publisher_name": "Shueisha"}],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            info = await mangaupdates.get_series_info(12345)
            assert info["title"] == "Chainsaw Man"
            assert "Action" in info["genres"]
            assert "FUJIMOTO Tatsuki" in info["authors"]

    @pytest.mark.asyncio
    async def test_rate_limit(self):
        mock_response = MagicMock()
        mock_response.status_code = 429

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(mangaupdates.MangaUpdatesError):
                await mangaupdates.search_series("test")


# ==================== Fandom Tests ====================

class TestFandomWikitext:
    def test_clean_wikitext_basic(self):
        text = "'''Bold''' and ''italic'' text with [[Link|display]]."
        result = fandom._clean_wikitext(text)
        assert "Bold" in result
        assert "italic" in result
        assert "display" in result
        assert "[[" not in result
        assert "''" not in result

    def test_clean_wikitext_refs(self):
        text = 'Text<ref name="ch1">Chapter 1</ref> more text.'
        result = fandom._clean_wikitext(text)
        assert "Chapter 1" not in result
        assert "more text" in result

    def test_clean_wikitext_templates(self):
        text = "Before {{Template|arg=val}} after."
        result = fandom._clean_wikitext(text)
        assert "Template" not in result
        assert "Before" in result
        assert "after" in result

    def test_clean_wikitext_images(self):
        text = "Text [[File:Image.png|thumb|Caption]] more."
        result = fandom._clean_wikitext(text)
        assert "File:" not in result
        assert "Text" in result

    def test_clean_wikitext_plain_links(self):
        text = "See [[Naruto Uzumaki]] for details."
        result = fandom._clean_wikitext(text)
        assert result == "See Naruto Uzumaki for details."


class TestFandomCharacterExtraction:
    def test_extract_characters(self):
        text = (
            "Naruto Uzumaki faced Sasuke Uchiha in battle. "
            "Naruto Uzumaki used his jutsu. Sasuke Uchiha countered. "
            "Sakura watched from the sidelines."
        )
        chars = fandom._extract_characters(text)
        assert "Naruto Uzumaki" in chars
        assert "Sasuke Uchiha" in chars
        # Sakura only mentioned once
        assert "Sakura" not in chars

    def test_extract_characters_filters_common_words(self):
        text = "The battle happened. When The attack started. The hero fought."
        chars = fandom._extract_characters(text)
        assert "The" not in chars

    def test_extract_key_events(self):
        text = (
            "Short. "
            "Naruto unleashed his ultimate technique against the enemy forces. "
            "Sasuke activated his Sharingan and saw through the illusion. "
            "Tiny."
        )
        events = fandom._extract_key_events(text)
        # Should skip short sentences
        assert len(events) == 2
        assert any("Naruto" in e for e in events)


class TestFandomAPI:
    @pytest.mark.asyncio
    async def test_search_wiki(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"url": "https://naruto.fandom.com/wiki/Naruto_Wiki"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            wiki = await fandom.search_wiki("Naruto")
            assert wiki == "naruto"

    @pytest.mark.asyncio
    async def test_search_wiki_not_found(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            wiki = await fandom.search_wiki("xyznonexistent")
            assert wiki is None

    @pytest.mark.asyncio
    async def test_search_wiki_skips_community(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"url": "https://community.fandom.com/wiki/Something"},
                {"url": "https://onepiece.fandom.com/wiki/One_Piece_Wiki"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            wiki = await fandom.search_wiki("One Piece")
            assert wiki == "onepiece"

    @pytest.mark.asyncio
    async def test_get_chapter_summary(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Chapter 1",
                        "extract": (
                            "Luffy arrives at the island. Luffy meets Shanks for the first time. "
                            "The bandit group attacks the village but Shanks protects everyone. "
                            "Luffy eats the Gomu Gomu no Mi and gains rubber powers."
                        ),
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await fandom.get_chapter_summary("onepiece", 1)
            assert result is not None
            assert result.chapter_number == 1.0
            assert "Luffy" in result.synopsis
            assert result.source == "fandom_wiki"

    @pytest.mark.asyncio
    async def test_get_chapter_summary_not_found(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "-1": {"title": "Chapter 999", "missing": ""}
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            # Need to return the not-found response for all naming conventions
            result = await fandom.get_chapter_summary("onepiece", 999)
            assert result is None

    @pytest.mark.asyncio
    async def test_get_character_info(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "456": {
                        "title": "Monkey D. Luffy",
                        "extract": "Captain of the Straw Hat Pirates.",
                        "thumbnail": {"source": "https://example.com/luffy.jpg"},
                    }
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            info = await fandom.get_character_info("onepiece", "Monkey D. Luffy")
            assert info is not None
            assert info["name"] == "Monkey D. Luffy"
            assert "Captain" in info["description"]
            assert info["image_url"] is not None


# ==================== Script Generator Tests ====================

class TestScriptGenerator:
    def test_build_prompt(self):
        from bee_content_automation.scripts.generator import build_prompt

        series = Series(
            id="1",
            title_english="Solo Leveling",
            title_romaji="Na Honjaman Level-Up",
            genres=["Action", "Fantasy"],
            status="RELEASING",
            synopsis="Sung Jin-Woo is the weakest hunter.",
        )
        summary = ChapterSummary(
            series_title="Solo Leveling",
            chapter_number=1.0,
            synopsis="Jin-Woo enters the double dungeon.",
            key_events=["Discovers hidden dungeon", "Nearly dies"],
        )
        prompt = build_prompt(series, summary)
        assert "Solo Leveling" in prompt
        assert "Chapter 1" in prompt
        assert "Jin-Woo" in prompt
        assert "HOOK" in prompt
        assert "ANALYSIS" in prompt

    def test_build_prompt_with_characters(self):
        from bee_content_automation.scripts.generator import build_prompt

        series = Series(id="1", title_english="Test", title_romaji="Test")
        summary = ChapterSummary(
            series_title="Test", chapter_number=1.0, synopsis="Events happen."
        )
        chars = [
            {"name": "Hero", "description": "The main character"},
            {"name": "Villain", "description": "The antagonist"},
        ]
        prompt = build_prompt(series, summary, characters=chars)
        assert "Hero" in prompt
        assert "Villain" in prompt

    def test_build_prompt_styles(self):
        from bee_content_automation.scripts.generator import build_prompt

        series = Series(id="1", title_english="Test", title_romaji="Test")
        summary = ChapterSummary(
            series_title="Test", chapter_number=1.0, synopsis="Events."
        )
        for style in ["analytical", "hype", "recap"]:
            prompt = build_prompt(series, summary, style=style)
            assert len(prompt) > 100

    def test_parse_script_response(self):
        from bee_content_automation.scripts.generator import parse_script_response

        response = """
1. HOOK
What if everything you knew about power was wrong?
[VISUAL: Dark screen with glowing text]

2. INTRO
Welcome back to another chapter breakdown of Solo Leveling.
[VISUAL: Series logo and title card]

3. RECAP
Last time, Jin-Woo entered the dungeon and discovered his powers.
[VISUAL: Montage of previous chapter key moments]

4. ANALYSIS
This chapter reveals the true nature of the system. The way Jin-Woo confronts
the statue shows incredible character development. His fear transforms into
determination, marking a turning point in the series.
[VISUAL: AI-generated art of a warrior facing a stone giant]

5. OUTRO
What do you think will happen next? Drop your theories in the comments.
[VISUAL: Subscribe button animation]
"""
        script = parse_script_response(response, "Solo Leveling", 1.0)
        assert script.series_title == "Solo Leveling"
        assert script.chapter_number == 1.0
        assert len(script.segments) == 5
        assert script.segments[0].type == "hook"
        assert script.segments[3].type == "analysis"
        assert "Solo Leveling" in script.title
        assert script.total_duration > 0
        assert len(script.full_text) > 0
        # Check visual notes were extracted
        assert "Dark screen" in script.segments[0].visual_notes

    def test_parse_script_response_partial(self):
        from bee_content_automation.scripts.generator import parse_script_response

        # LLM might not produce all sections perfectly
        response = """
HOOK
Attention grabber line here.

INTRO
Brief intro.

ANALYSIS
The deep analysis part goes here with lots of content.
"""
        script = parse_script_response(response, "Test", 5.0)
        # Should parse what it can
        assert script.series_title == "Test"
        assert len(script.segments) >= 2
