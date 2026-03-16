"""Transcript fetcher using youtube-transcript-api (v1.0.0+)."""

from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> dict | None:
    """Fetch transcript for a video. Returns {language, text} or None.

    Uses the v1.0.0+ API where YouTubeTranscriptApi is instantiated.
    """
    if languages is None:
        languages = ["en"]
    try:
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.list(video_id)
        try:
            transcript = transcript_list.find_transcript(languages)
        except Exception:
            transcript = transcript_list.find_generated_transcript(languages)

        fetched = transcript.fetch()
        full_text = " ".join(snippet.text for snippet in fetched)
        return {"language": transcript.language_code, "text": full_text}
    except Exception:
        return None
