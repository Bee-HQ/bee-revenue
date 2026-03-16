"""Core script reviewer — multi-pass LLM analysis across 7 pillars.

Uses the Anthropic Python SDK to analyze scripts one pillar at a time,
then aggregates scores into an overall weighted score.
"""

import json
import os

from .prompts import (
    SYSTEM_PROMPT,
    PILLAR_WEIGHTS,
    PILLAR_NAMES,
    ALL_PILLARS,
    build_metadata_section,
    get_pillar_prompt,
)

# Model to use for scoring (fast, cheap, good enough)
DEFAULT_MODEL = "claude-sonnet-4-20250514"


class ReviewError(Exception):
    """Raised when a review operation fails."""


def _get_client():
    """Get an Anthropic client, raising a clear error if the API key is missing."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ReviewError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Set it with: export ANTHROPIC_API_KEY=sk-ant-..."
        )
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ReviewError(
            "The 'anthropic' package is not installed. "
            "Install it with: uv pip install anthropic "
            "or: uv add --optional review anthropic"
        )
    return Anthropic(api_key=api_key)


def _analyze_pillar(
    client,
    pillar: str,
    script_text: str,
    metadata: dict | None = None,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Run a single pillar analysis via the Claude API.

    Returns the parsed JSON result for one pillar.
    """
    prompt_template = get_pillar_prompt(pillar)
    metadata_section = build_metadata_section(metadata)

    user_message = prompt_template.format(
        script_text=script_text,
        metadata_section=metadata_section,
    )

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # Extract text from response
    text = response.content[0].text.strip()

    # Parse JSON — handle potential markdown code fences
    if text.startswith("```"):
        # Strip ```json ... ``` wrapping
        lines = text.split("\n")
        text = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        )

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise ReviewError(
            f"Failed to parse {pillar} response as JSON: {e}\nRaw response: {text[:500]}"
        )

    # Validate required fields
    if "score" not in result:
        raise ReviewError(f"Missing 'score' in {pillar} response: {result}")

    # Ensure score is in range
    result["score"] = max(0, min(100, int(result["score"])))

    return result


def calculate_weighted_score(pillar_scores: dict[str, int]) -> float:
    """Calculate the overall weighted score from individual pillar scores.

    Args:
        pillar_scores: Dict mapping pillar name to score (0-100).

    Returns:
        Weighted average score (0-100).
    """
    if not pillar_scores:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for pillar, score in pillar_scores.items():
        weight = PILLAR_WEIGHTS.get(pillar, 0)
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 1)


def classify_score(score: float) -> str:
    """Classify a score into a tier label.

    Args:
        score: Score from 0-100.

    Returns:
        Tier label string.
    """
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Strong"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Decent"
    elif score >= 50:
        return "Needs Work"
    elif score >= 30:
        return "Weak"
    else:
        return "Poor"


def _aggregate_results(pillar_results: list[dict]) -> dict:
    """Aggregate individual pillar results into a full review report.

    Args:
        pillar_results: List of pillar result dicts from _analyze_pillar.

    Returns:
        Complete review report dict.
    """
    pillar_scores = {}
    all_strengths = []
    all_issues = []
    pillar_details = {}

    for result in pillar_results:
        pillar = result.get("pillar", "unknown")
        score = result.get("score", 0)
        pillar_scores[pillar] = score

        pillar_details[pillar] = {
            "score": score,
            "name": PILLAR_NAMES.get(pillar, pillar),
            "weight": PILLAR_WEIGHTS.get(pillar, 0),
            "justification": result.get("justification", ""),
            "issues": result.get("issues", []),
            "strengths": result.get("strengths", []),
        }

        # Collect strengths with source pillar
        for s in result.get("strengths", []):
            all_strengths.append({"pillar": pillar, "strength": s})

        # Collect issues with source pillar and score impact
        for issue in result.get("issues", []):
            all_issues.append({
                "pillar": pillar,
                "pillar_score": score,
                "pillar_weight": PILLAR_WEIGHTS.get(pillar, 0),
                **issue,
            })

    overall_score = calculate_weighted_score(pillar_scores)
    tier = classify_score(overall_score)

    # Sort issues by impact (lower score + higher weight = more important)
    all_issues.sort(key=lambda x: x["pillar_score"] * (1 - x["pillar_weight"]))

    # Find pillars that need attention (below 70)
    attention_needed = [
        pillar for pillar, score in pillar_scores.items() if score < 70
    ]

    # Predictions based on score
    predictions = _generate_predictions(overall_score, pillar_scores)

    return {
        "overall_score": overall_score,
        "tier": tier,
        "pillar_scores": pillar_scores,
        "pillar_details": pillar_details,
        "top_strengths": all_strengths[:3],
        "top_issues": all_issues[:3],
        "all_issues": all_issues,
        "attention_needed": attention_needed,
        "predictions": predictions,
    }


def _generate_predictions(overall: float, pillar_scores: dict[str, int]) -> dict:
    """Generate performance predictions based on scores."""
    hook = pillar_scores.get("hook", 50)
    pacing = pillar_scores.get("pacing", 50)
    engagement = pillar_scores.get("engagement", 50)

    # CTR prediction based on hook + SEO
    seo = pillar_scores.get("seo", 50)
    ctr_base = (hook * 0.7 + seo * 0.3) / 100
    if ctr_base >= 0.8:
        ctr_range = "8-12%"
    elif ctr_base >= 0.6:
        ctr_range = "5-8%"
    elif ctr_base >= 0.4:
        ctr_range = "3-5%"
    else:
        ctr_range = "1-3%"

    # Retention prediction based on pacing + storytelling
    storytelling = pillar_scores.get("storytelling", 50)
    retention_base = (pacing * 0.5 + storytelling * 0.3 + hook * 0.2) / 100
    if retention_base >= 0.8:
        avg_view_duration = "60-70%"
    elif retention_base >= 0.6:
        avg_view_duration = "45-60%"
    elif retention_base >= 0.4:
        avg_view_duration = "30-45%"
    else:
        avg_view_duration = "15-30%"

    # Engagement prediction
    engagement_base = (engagement * 0.6 + pacing * 0.2 + hook * 0.2) / 100
    if engagement_base >= 0.8:
        comment_rate = "High (3%+ like rate, active comments)"
    elif engagement_base >= 0.6:
        comment_rate = "Moderate (2-3% like rate)"
    elif engagement_base >= 0.4:
        comment_rate = "Low (1-2% like rate)"
    else:
        comment_rate = "Very Low (<1% like rate)"

    return {
        "estimated_ctr": ctr_range,
        "estimated_avg_view_duration": avg_view_duration,
        "estimated_engagement": comment_rate,
        "viral_potential": "High" if overall >= 85 else "Moderate" if overall >= 70 else "Low",
    }


def review_script(
    script_text: str,
    metadata: dict | None = None,
    model: str = DEFAULT_MODEL,
    pillars: list[str] | None = None,
) -> dict:
    """Review a script across 7 pillars using Claude API.

    Args:
        script_text: The full script/transcript text to review.
        metadata: Optional dict with title, description, tags, series_name, archetype.
        model: Claude model to use.
        pillars: Specific pillars to analyze (default: all 7).

    Returns:
        Dict with pillar_scores, overall_score, strengths, issues, predictions.
    """
    if not script_text or not script_text.strip():
        raise ReviewError("Script text is empty.")

    client = _get_client()
    target_pillars = pillars or ALL_PILLARS

    pillar_results = []
    for pillar in target_pillars:
        result = _analyze_pillar(client, pillar, script_text, metadata, model)
        pillar_results.append(result)

    return _aggregate_results(pillar_results)
