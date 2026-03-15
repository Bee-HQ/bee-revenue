"""Tests for the search/suggestions fetcher."""

from bee_content_research.fetchers.search import fetch_youtube_suggestions, search_channels


def test_fetch_youtube_suggestions_returns_list():
    """Verify the function returns a list (structural test).
    Network failures are handled gracefully and return empty list.
    """
    result = fetch_youtube_suggestions("python tutorial")
    assert isinstance(result, list)


def test_search_channels_callable():
    """Verify search_channels is importable and callable."""
    assert callable(search_channels)
