"""Tests for the transcript fetcher."""


def test_transcript_import():
    """Verify the module imports correctly."""
    from bee_content_research.fetchers.transcript import fetch_transcript
    assert callable(fetch_transcript)
