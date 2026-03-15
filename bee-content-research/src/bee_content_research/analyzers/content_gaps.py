"""Content gap finder analyzer.

Identifies topics with high search demand but low competitor coverage by:
1. Building a topic frequency map from titles, tags, and transcripts (n-gram counting)
2. Cross-referencing with YouTube search suggestions
3. Scoring gaps as high demand + low coverage
"""

import json
import re
from collections import Counter


# Common English stop words to filter out
_STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "this", "that", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "can", "shall",
    "not", "no", "so", "if", "how", "what", "when", "where", "who", "which",
    "why", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "just", "about", "up", "out",
    "into", "over", "after", "before", "between", "under", "again", "then",
    "here", "there", "these", "those", "my", "your", "his", "her", "our",
    "their", "i", "me", "we", "you", "he", "she", "they", "them", "us",
    "am", "as", "also", "only", "even", "like", "get", "got", "go", "going",
    "one", "two", "new", "make", "know", "way", "use", "video", "channel",
})


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip non-alphanum, remove stop words."""
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]


def _extract_ngrams(tokens: list[str], n: int) -> list[str]:
    """Extract n-grams from a list of tokens."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _build_topic_map(videos: list[dict], transcripts: list[dict] | None = None) -> Counter:
    """Build a topic frequency map from video titles, tags, and transcripts."""
    counter: Counter = Counter()

    for v in videos:
        # Title tokens (weighted higher)
        title_tokens = _tokenize(v.get("title", ""))
        for token in title_tokens:
            counter[token] += 3  # title words weighted 3x

        # Title bigrams
        for bigram in _extract_ngrams(title_tokens, 2):
            counter[bigram] += 5  # title bigrams weighted 5x

        # Tags
        tags_raw = v.get("tags", "[]")
        try:
            tags = json.loads(tags_raw) if isinstance(tags_raw, str) else (tags_raw or [])
        except (json.JSONDecodeError, TypeError):
            tags = []
        for tag in tags:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in _STOP_WORDS:
                counter[tag_lower] += 2  # tags weighted 2x

    # Transcripts (if available, weighted lower)
    if transcripts:
        for t in transcripts:
            text = t.get("text", "")
            tokens = _tokenize(text)
            # Only count unique tokens per transcript to avoid length bias
            unique_tokens = set(tokens)
            for token in unique_tokens:
                counter[token] += 1
            for bigram in set(_extract_ngrams(tokens, 2)):
                counter[bigram] += 1

    return counter


def find_content_gaps(videos: list[dict],
                      transcripts: list[dict] | None = None,
                      suggestions: list[str] | None = None) -> dict:
    """Identify content topics with high search demand but low competitor coverage.

    Args:
        videos: List of video dicts from the niche group.
        transcripts: Optional list of transcript dicts.
        suggestions: Optional list of YouTube search suggestions to cross-reference.

    Returns:
        Dict with 'gaps' (ranked topics), 'covered_topics' (well-covered),
        and 'topic_counts' (full frequency map).
    """
    if not videos:
        return {"gaps": [], "covered_topics": [], "topic_counts": {}}

    topic_map = _build_topic_map(videos, transcripts)

    if not topic_map:
        return {"gaps": [], "covered_topics": [], "topic_counts": {}}

    # Determine coverage thresholds
    counts = list(topic_map.values())
    if not counts:
        return {"gaps": [], "covered_topics": [], "topic_counts": {}}

    total_videos = len(videos)
    # A topic is "well covered" if it appears in > 10% of videos (by weighted count)
    coverage_threshold = max(total_videos * 0.1, 3)

    covered_topics = []
    for topic, count in topic_map.most_common(50):
        if count >= coverage_threshold:
            covered_topics.append({"topic": topic, "coverage_count": count})

    # Cross-reference with suggestions to find gaps
    gaps = []
    if suggestions:
        covered_set = {t["topic"] for t in covered_topics}
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower().strip()
            suggestion_tokens = _tokenize(suggestion_lower)

            # Check if the suggestion is already well covered
            is_covered = False
            for covered in covered_set:
                if covered in suggestion_lower or suggestion_lower in covered:
                    is_covered = True
                    break

            if not is_covered:
                # Calculate how many existing videos touch this topic
                existing_coverage = 0
                for token in suggestion_tokens:
                    existing_coverage += topic_map.get(token, 0)

                # Higher demand = appears in suggestions
                # Lower coverage = low existing_coverage
                demand_score = 10  # base demand score for being a suggestion
                coverage_score = existing_coverage

                # Gap score: high demand, low coverage is a gap
                gap_score = demand_score / (1 + coverage_score)

                gaps.append({
                    "topic": suggestion,
                    "demand_score": demand_score,
                    "coverage_score": coverage_score,
                    "gap_score": round(gap_score, 3),
                })

        gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    else:
        # Without suggestions, identify low-frequency topics that seem relevant
        # These are topics that only 1-2 channels cover
        all_topics = topic_map.most_common()
        low_coverage = [
            {"topic": topic, "coverage_count": count, "gap_score": 1.0 / count}
            for topic, count in all_topics
            if 1 <= count < coverage_threshold and len(topic) > 3
        ]
        low_coverage.sort(key=lambda x: x["gap_score"], reverse=True)
        gaps = low_coverage[:30]

    return {
        "gaps": gaps[:30],
        "covered_topics": covered_topics[:20],
        "topic_counts": dict(topic_map.most_common(100)),
    }
