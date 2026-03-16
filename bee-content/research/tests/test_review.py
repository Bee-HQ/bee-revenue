"""Tests for the script review module.

Tests cover:
- Prompt construction
- Score calculation (weighted average)
- Score classification (tiers)
- Output formatting
- Service routing (file vs text vs URL)
- Error handling (missing API key, empty script)
- Aggregation logic

All API calls are mocked — no real API calls are made.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from bee_content_research.reviewers.script_reviewer import (
    ReviewError,
    calculate_weighted_score,
    classify_score,
    review_script,
    _aggregate_results,
    _generate_predictions,
)
from bee_content_research.reviewers.prompts import (
    ALL_PILLARS,
    PILLAR_WEIGHTS,
    PILLAR_NAMES,
    build_metadata_section,
    get_pillar_prompt,
)
from bee_content_research.services.review import (
    _extract_video_id,
    _is_youtube_url,
    _is_file_path,
    review_from_file,
    review_from_text,
    review_from_source,
)
from bee_content_research.formatters import format_review_report


# --- Sample data ---

SAMPLE_SCRIPT = """
You think you know One Piece? Let me show you something that will change everything.

For 25 years, Oda has been hiding a pattern in plain sight. Every single arc follows the
same structure, but nobody talks about it. Today, we break it down.

Let's start with Alabasta. When Luffy first arrived in the desert kingdom, he wasn't just
fighting Crocodile — he was setting up a template that would repeat for the next two decades.

The pattern is this: Luffy enters a country, meets someone oppressed, fights the oppressor,
and liberates the nation. Simple, right? But here's what makes it genius — each time the
stakes get higher, and the personal connection gets deeper.

In Dressrosa, it wasn't just about beating Doflamingo. It was about Law's revenge, the
Tontatta tribe's freedom, and the legacy of Corazon. The layers kept building.

And now in Wano, we see the full evolution. Luffy isn't just freeing a country — he's
fulfilling a prophecy that was set up 800 years ago.

But the craziest part? The final arc is going to flip this entire pattern on its head.
And I think I know how.

Let me know in the comments what you think the final arc will look like. Hit subscribe
if you want to see my breakdown when it drops.
"""

SAMPLE_METADATA = {
    "title": "One Piece Has Been Lying to You for 25 Years",
    "description": "Breaking down the hidden pattern in every One Piece arc",
    "tags": ["one piece", "anime", "manga", "oda", "theory"],
    "series_name": "One Piece",
    "archetype": "essay",
}


def _make_pillar_result(pillar: str, score: int) -> dict:
    """Create a mock pillar result."""
    return {
        "pillar": pillar,
        "score": score,
        "justification": f"Test justification for {pillar}",
        "issues": [
            {
                "description": f"Test issue for {pillar}",
                "location": "Test location",
                "fix": "Test fix suggestion",
            }
        ],
        "strengths": [f"Test strength for {pillar}"],
    }


def _make_mock_response(pillar: str, score: int) -> MagicMock:
    """Create a mock Anthropic API response."""
    result = _make_pillar_result(pillar, score)
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = json.dumps(result)
    mock_response.content = [mock_content]
    return mock_response


# --- Prompt construction tests ---


class TestPrompts:
    def test_all_pillars_have_prompts(self):
        for pillar in ALL_PILLARS:
            prompt = get_pillar_prompt(pillar)
            assert "{script_text}" in prompt
            assert "{metadata_section}" in prompt

    def test_all_pillars_have_weights(self):
        for pillar in ALL_PILLARS:
            assert pillar in PILLAR_WEIGHTS
            assert 0 < PILLAR_WEIGHTS[pillar] <= 1.0

    def test_weights_sum_to_one(self):
        total = sum(PILLAR_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_all_pillars_have_names(self):
        for pillar in ALL_PILLARS:
            assert pillar in PILLAR_NAMES

    def test_invalid_pillar_raises(self):
        with pytest.raises(ValueError, match="Unknown pillar"):
            get_pillar_prompt("nonexistent")

    def test_build_metadata_section_full(self):
        section = build_metadata_section(SAMPLE_METADATA)
        assert "METADATA:" in section
        assert "One Piece" in section
        assert "essay" in section
        assert "one piece" in section

    def test_build_metadata_section_none(self):
        section = build_metadata_section(None)
        assert "No metadata" in section

    def test_build_metadata_section_empty(self):
        section = build_metadata_section({})
        assert "No metadata" in section

    def test_build_metadata_section_partial(self):
        section = build_metadata_section({"title": "Test Title"})
        assert "Test Title" in section
        assert "METADATA:" in section

    def test_build_metadata_tags_as_list(self):
        section = build_metadata_section({"tags": ["tag1", "tag2"]})
        assert "tag1, tag2" in section

    def test_build_metadata_tags_as_string(self):
        section = build_metadata_section({"tags": "tag1, tag2"})
        assert "tag1, tag2" in section

    def test_prompt_contains_rubric(self):
        prompt = get_pillar_prompt("hook")
        assert "SCORING RUBRIC" in prompt
        assert "90-100" in prompt
        assert "0-29" in prompt

    def test_prompt_mentions_archetypes(self):
        prompt = get_pillar_prompt("niche_fit")
        assert "Editorial Essay" in prompt
        assert "Power Fantasy Recap" in prompt
        assert "Explainer" in prompt


# --- Score calculation tests ---


class TestScoreCalculation:
    def test_weighted_score_all_100(self):
        scores = {p: 100 for p in ALL_PILLARS}
        assert calculate_weighted_score(scores) == 100.0

    def test_weighted_score_all_0(self):
        scores = {p: 0 for p in ALL_PILLARS}
        assert calculate_weighted_score(scores) == 0.0

    def test_weighted_score_all_50(self):
        scores = {p: 50 for p in ALL_PILLARS}
        assert calculate_weighted_score(scores) == 50.0

    def test_weighted_score_empty(self):
        assert calculate_weighted_score({}) == 0.0

    def test_weighted_score_partial(self):
        scores = {"hook": 80, "pacing": 60}
        result = calculate_weighted_score(scores)
        # hook weight 0.20, pacing weight 0.20
        expected = (80 * 0.20 + 60 * 0.20) / (0.20 + 0.20)
        assert abs(result - expected) < 0.2

    def test_weighted_score_hook_dominates(self):
        # hook (20%) and pacing (20%) are highest weight
        scores_high_hook = {p: 50 for p in ALL_PILLARS}
        scores_high_hook["hook"] = 100
        scores_high_hook["pacing"] = 100

        scores_high_niche = {p: 50 for p in ALL_PILLARS}
        scores_high_niche["niche_fit"] = 100  # only 10% weight

        result_hook = calculate_weighted_score(scores_high_hook)
        result_niche = calculate_weighted_score(scores_high_niche)
        assert result_hook > result_niche


class TestScoreClassification:
    def test_excellent(self):
        assert classify_score(95) == "Excellent"
        assert classify_score(90) == "Excellent"

    def test_strong(self):
        assert classify_score(85) == "Strong"
        assert classify_score(80) == "Strong"

    def test_good(self):
        assert classify_score(75) == "Good"
        assert classify_score(70) == "Good"

    def test_decent(self):
        assert classify_score(65) == "Decent"
        assert classify_score(60) == "Decent"

    def test_needs_work(self):
        assert classify_score(55) == "Needs Work"
        assert classify_score(50) == "Needs Work"

    def test_weak(self):
        assert classify_score(40) == "Weak"
        assert classify_score(30) == "Weak"

    def test_poor(self):
        assert classify_score(20) == "Poor"
        assert classify_score(0) == "Poor"


# --- Aggregation tests ---


class TestAggregation:
    def test_aggregate_all_pillars(self):
        results = [_make_pillar_result(p, 75) for p in ALL_PILLARS]
        report = _aggregate_results(results)

        assert report["overall_score"] == 75.0
        assert report["tier"] == "Good"
        assert len(report["pillar_scores"]) == 7
        assert len(report["pillar_details"]) == 7
        assert len(report["top_strengths"]) == 3
        assert len(report["top_issues"]) == 3
        assert "predictions" in report

    def test_aggregate_mixed_scores(self):
        results = [
            _make_pillar_result("hook", 90),
            _make_pillar_result("pacing", 40),
            _make_pillar_result("storytelling", 70),
            _make_pillar_result("engagement", 60),
            _make_pillar_result("narration", 80),
            _make_pillar_result("seo", 55),
            _make_pillar_result("niche_fit", 85),
        ]
        report = _aggregate_results(results)

        assert report["pillar_scores"]["hook"] == 90
        assert report["pillar_scores"]["pacing"] == 40
        assert "pacing" in report["attention_needed"]
        assert "hook" not in report["attention_needed"]

    def test_aggregate_attention_needed(self):
        results = [
            _make_pillar_result("hook", 90),
            _make_pillar_result("pacing", 50),
            _make_pillar_result("storytelling", 65),
            _make_pillar_result("engagement", 80),
            _make_pillar_result("narration", 45),
            _make_pillar_result("seo", 75),
            _make_pillar_result("niche_fit", 60),
        ]
        report = _aggregate_results(results)

        assert "pacing" in report["attention_needed"]
        assert "narration" in report["attention_needed"]
        assert "niche_fit" in report["attention_needed"]
        assert "storytelling" in report["attention_needed"]
        assert "hook" not in report["attention_needed"]


class TestPredictions:
    def test_high_scores_predict_high_ctr(self):
        preds = _generate_predictions(90, {p: 90 for p in ALL_PILLARS})
        assert "8-12%" in preds["estimated_ctr"]

    def test_low_scores_predict_low_ctr(self):
        preds = _generate_predictions(30, {p: 30 for p in ALL_PILLARS})
        assert "1-3%" in preds["estimated_ctr"]

    def test_viral_potential_high(self):
        preds = _generate_predictions(90, {p: 90 for p in ALL_PILLARS})
        assert preds["viral_potential"] == "High"

    def test_viral_potential_moderate(self):
        preds = _generate_predictions(75, {p: 75 for p in ALL_PILLARS})
        assert preds["viral_potential"] == "Moderate"

    def test_viral_potential_low(self):
        preds = _generate_predictions(50, {p: 50 for p in ALL_PILLARS})
        assert preds["viral_potential"] == "Low"


# --- Formatting tests ---


class TestFormatting:
    def test_format_review_report_renders(self):
        results = [_make_pillar_result(p, 75) for p in ALL_PILLARS]
        report = _aggregate_results(results)
        panel = format_review_report(report)
        # Should be a Rich Panel
        assert panel is not None
        assert hasattr(panel, "renderable")

    def test_format_review_report_with_mixed_scores(self):
        results = [
            _make_pillar_result("hook", 90),
            _make_pillar_result("pacing", 40),
            _make_pillar_result("storytelling", 70),
            _make_pillar_result("engagement", 60),
            _make_pillar_result("narration", 80),
            _make_pillar_result("seo", 55),
            _make_pillar_result("niche_fit", 85),
        ]
        report = _aggregate_results(results)
        panel = format_review_report(report)
        assert panel is not None


# --- Service routing tests ---


class TestServiceRouting:
    def test_extract_video_id_standard_url(self):
        assert _extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_short_url(self):
        assert _extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_embed_url(self):
        assert _extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_bare_id(self):
        assert _extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_invalid(self):
        assert _extract_video_id("not a url at all") is None

    def test_is_youtube_url(self):
        assert _is_youtube_url("https://www.youtube.com/watch?v=abc")
        assert _is_youtube_url("https://youtu.be/abc")
        assert not _is_youtube_url("/path/to/file.txt")
        assert not _is_youtube_url("just some text")

    def test_is_file_path_existing(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            assert _is_file_path(f.name)
        os.unlink(f.name)

    def test_is_file_path_txt_extension(self):
        # .txt extension makes it look like a file even if it doesn't exist
        assert _is_file_path("nonexistent.txt")

    def test_is_file_path_md_extension(self):
        assert _is_file_path("script.md")

    def test_review_from_file_not_found(self):
        with pytest.raises(ReviewError, match="File not found"):
            review_from_file("/nonexistent/path/script.txt")

    def test_review_from_file_empty(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()
            path = f.name
        try:
            with pytest.raises(ReviewError, match="empty"):
                review_from_file(path)
        finally:
            os.unlink(path)


# --- Error handling tests ---


class TestErrorHandling:
    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            # Make sure ANTHROPIC_API_KEY is not set
            env = os.environ.copy()
            env.pop("ANTHROPIC_API_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(ReviewError, match="ANTHROPIC_API_KEY"):
                    review_script(SAMPLE_SCRIPT)

    def test_empty_script(self):
        with pytest.raises(ReviewError, match="empty"):
            review_script("")

    def test_whitespace_only_script(self):
        with pytest.raises(ReviewError, match="empty"):
            review_script("   \n\n  ")


# --- Full review with mocked API ---


class TestReviewWithMockedAPI:
    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_script_full(self, mock_get_client):
        """Test full review with all 7 pillars mocked."""
        mock_client = MagicMock()

        # Return different scores per pillar
        scores = {
            "hook": 85, "pacing": 72, "storytelling": 78,
            "engagement": 80, "narration": 70, "seo": 65, "niche_fit": 88,
        }

        def side_effect(**kwargs):
            # Parse which pillar from the user message content
            user_msg = kwargs.get("messages", [{}])[0].get("content", "")
            for pillar, score in scores.items():
                # The prompt contains the pillar name in the expected JSON structure
                if f'"pillar": "{pillar}"' in get_pillar_prompt(pillar):
                    pass
            # Determine pillar from prompt content
            if "HOOK" in user_msg:
                pillar, score = "hook", 85
            elif "PACING" in user_msg:
                pillar, score = "pacing", 72
            elif "STORYTELLING" in user_msg:
                pillar, score = "storytelling", 78
            elif "ENGAGEMENT TRIGGERS" in user_msg:
                pillar, score = "engagement", 80
            elif "NARRATION" in user_msg:
                pillar, score = "narration", 70
            elif "SEO" in user_msg:
                pillar, score = "seo", 65
            elif "NICHE FIT" in user_msg:
                pillar, score = "niche_fit", 88
            else:
                pillar, score = "unknown", 50

            return _make_mock_response(pillar, score)

        mock_client.messages.create.side_effect = side_effect
        mock_get_client.return_value = mock_client

        result = review_script(SAMPLE_SCRIPT, SAMPLE_METADATA)

        assert result["overall_score"] > 0
        assert result["tier"] in ["Excellent", "Strong", "Good", "Decent", "Needs Work", "Weak", "Poor"]
        assert len(result["pillar_scores"]) == 7
        assert result["pillar_scores"]["hook"] == 85
        assert result["pillar_scores"]["pacing"] == 72
        assert "predictions" in result
        assert mock_client.messages.create.call_count == 7

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_script_specific_pillars(self, mock_get_client):
        """Test reviewing only specific pillars."""
        mock_client = MagicMock()

        def side_effect(**kwargs):
            user_msg = kwargs.get("messages", [{}])[0].get("content", "")
            if "HOOK" in user_msg:
                return _make_mock_response("hook", 80)
            return _make_mock_response("pacing", 70)

        mock_client.messages.create.side_effect = side_effect
        mock_get_client.return_value = mock_client

        result = review_script(SAMPLE_SCRIPT, pillars=["hook", "pacing"])

        assert len(result["pillar_scores"]) == 2
        assert "hook" in result["pillar_scores"]
        assert "pacing" in result["pillar_scores"]
        assert mock_client.messages.create.call_count == 2

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_from_file_success(self, mock_get_client):
        """Test reviewing from a file."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("hook", 75)
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(SAMPLE_SCRIPT)
            f.flush()
            path = f.name

        try:
            result = review_from_file(path, SAMPLE_METADATA)
            assert result["overall_score"] > 0
        finally:
            os.unlink(path)

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_from_text_success(self, mock_get_client):
        """Test reviewing from raw text."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("hook", 75)
        mock_get_client.return_value = mock_client

        result = review_from_text(SAMPLE_SCRIPT, SAMPLE_METADATA)
        assert result["overall_score"] > 0

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_from_source_text(self, mock_get_client):
        """Test auto-routing for raw text input."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("hook", 75)
        mock_get_client.return_value = mock_client

        result = review_from_source("This is a raw script about anime")
        assert result["overall_score"] > 0

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_from_source_file(self, mock_get_client):
        """Test auto-routing for file path input."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("hook", 75)
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(SAMPLE_SCRIPT)
            f.flush()
            path = f.name

        try:
            result = review_from_source(path)
            assert result["overall_score"] > 0
        finally:
            os.unlink(path)

    @patch("bee_content_research.reviewers.script_reviewer._get_client")
    def test_review_handles_markdown_fenced_json(self, mock_get_client):
        """Test that the reviewer strips markdown code fences from API response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content = MagicMock()
        # Simulate Claude wrapping JSON in code fences
        result_data = _make_pillar_result("hook", 82)
        mock_content.text = f"```json\n{json.dumps(result_data)}\n```"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = review_script(SAMPLE_SCRIPT, pillars=["hook"])
        assert result["pillar_scores"]["hook"] == 82
