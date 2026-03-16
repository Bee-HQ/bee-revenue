"""Rich tables, JSON/CSV export helpers for bee-content-research."""

import csv
import io
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def format_channels_table(channels: list[dict]) -> Table:
    """Format a list of channels as a Rich table."""
    table = Table(title="Channels")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Handle")
    table.add_column("Subscribers", justify="right")
    table.add_column("Country")
    table.add_column("Discovered Via")
    for ch in channels:
        table.add_row(
            ch.get("id", "")[:16],
            ch.get("name", ""),
            ch.get("handle", ""),
            f"{ch.get('subscriber_count', 0):,}" if ch.get("subscriber_count") else "-",
            ch.get("country", "") or "-",
            ch.get("discovered_via", ""),
        )
    return table


def format_outliers_table(result: dict) -> Table:
    """Format outlier analysis results as a Rich table."""
    table = Table(title="Outlier / Viral Videos")
    table.add_column("Title", style="bold", max_width=50)
    table.add_column("Views", justify="right")
    table.add_column("Multiplier", justify="right", style="red")
    table.add_column("Like Rate", justify="right")
    table.add_column("Published")
    table.add_column("Channel", style="dim")
    for o in result.get("outliers", []):
        table.add_row(
            o.get("title", "")[:50],
            f"{o.get('view_count', 0):,}",
            f"{o.get('multiplier', 0)}x",
            f"{o.get('like_rate', 0):.1f}%",
            o.get("published_at", ""),
            o.get("channel_id", "")[:12],
        )
    return table


def format_engagement_table(result: dict) -> Table:
    """Format engagement analysis results as a Rich table."""
    table = Table(title="Engagement Leaderboard")
    table.add_column("Title", style="bold", max_width=40)
    table.add_column("Views", justify="right")
    table.add_column("Like %", justify="right")
    table.add_column("Comment %", justify="right")
    table.add_column("Score", justify="right", style="green")
    for v in result.get("videos", [])[:30]:
        table.add_row(
            v.get("title", "")[:40],
            f"{v.get('view_count', 0):,}",
            f"{v.get('like_rate', 0):.2f}%",
            f"{v.get('comment_rate', 0):.3f}%",
            f"{v.get('composite_score', 0):.2f}",
        )
    return table


def format_benchmarks_table(result: dict) -> Table:
    """Format benchmark analysis results as a Rich table."""
    table = Table(title="Niche Benchmarks")
    table.add_column("Channel", style="bold")
    table.add_column("Videos", justify="right")
    table.add_column("Med. Views", justify="right")
    table.add_column("Avg. Views", justify="right")
    table.add_column("Uploads/wk", justify="right")
    table.add_column("Subs", justify="right")
    table.add_column("Deviation", justify="right")

    deviations = {d["channel_id"]: d for d in result.get("channel_deviations", [])}
    for cb in result.get("channel_benchmarks", []):
        dev = deviations.get(cb["channel_id"], {})
        dev_pct = dev.get("views_deviation_pct", 0)
        dev_str = f"{dev_pct:+.1f}%"
        dev_style = "green" if dev_pct > 0 else "red"
        table.add_row(
            cb.get("channel_name", "")[:20],
            str(cb.get("video_count", 0)),
            f"{cb.get('median_views', 0):,}",
            f"{cb.get('avg_views', 0):,}",
            f"{cb.get('uploads_per_week', 0):.1f}",
            f"{cb.get('subscriber_count', 0):,}" if cb.get("subscriber_count") else "-",
            f"[{dev_style}]{dev_str}[/{dev_style}]",
        )
    return table


def format_titles_table(result: dict) -> Table:
    """Format title analysis results as a Rich table."""
    table = Table(title="Title Pattern Performance")
    table.add_column("Pattern", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Avg Views", justify="right")
    table.add_column("Median Views", justify="right")
    for p in result.get("best_patterns", []):
        table.add_row(
            p.get("pattern", ""),
            str(p.get("count", 0)),
            f"{p.get('avg_views', 0):,}",
            f"{p.get('median_views', 0):,}",
        )
    return table


def format_seo_table(result: dict) -> Table:
    """Format SEO analysis results as a Rich table."""
    table = Table(title="Top Tags by Performance")
    table.add_column("Tag", style="bold")
    table.add_column("Usage", justify="right")
    table.add_column("Avg Views", justify="right")
    table.add_column("Median Views", justify="right")
    for tp in result.get("tag_performance", [])[:20]:
        table.add_row(
            tp.get("tag", ""),
            str(tp.get("usage_count", 0)),
            f"{tp.get('avg_views', 0):,}",
            f"{tp.get('median_views', 0):,}",
        )
    return table


def format_timing_table(result: dict) -> Table:
    """Format timing analysis results as a Rich table."""
    table = Table(title="Upload Timing Performance")
    table.add_column("Day", style="bold")
    table.add_column("Uploads", justify="right")
    table.add_column("Avg Views", justify="right")
    table.add_column("Median Views", justify="right")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in day_order:
        data = result.get("day_of_week", {}).get(day)
        if data:
            table.add_row(
                day,
                str(data.get("upload_count", 0)),
                f"{data.get('avg_views', 0):,}",
                f"{data.get('median_views', 0):,}",
            )
    return table


def format_regional_table(result: dict) -> Table:
    """Format regional analysis results as a Rich table."""
    table = Table(title="Language Distribution & Revenue Estimates")
    table.add_column("Language", style="bold")
    table.add_column("Videos", justify="right")
    table.add_column("% Share", justify="right")
    table.add_column("Avg Views", justify="right")
    table.add_column("Est. CPM", justify="right")
    table.add_column("Est. Revenue", justify="right", style="green")

    for re_item in result.get("revenue_estimates", []):
        table.add_row(
            re_item.get("language_name", ""),
            str(len([ld for ld in result.get("language_distribution", [])
                     if ld["language"] == re_item.get("language")])),
            "",
            "",
            f"${re_item.get('estimated_cpm', 0):.2f}",
            f"${re_item.get('estimated_revenue', 0):,.2f}",
        )
    return table


def format_compare_table(result: dict) -> Table:
    """Format channel comparison results as a Rich table."""
    table = Table(title="Channel Comparison")
    table.add_column("Metric", style="bold")
    for ch in result.get("channels", []):
        table.add_column(ch.get("channel_name", ch.get("channel_id", ""))[:15])

    metrics = [
        ("Subscribers", "subscriber_count", True),
        ("Total Views", "total_views", True),
        ("Avg Views", "avg_views", True),
        ("Median Views", "median_views", True),
        ("Videos", "video_count", False),
        ("Like Rate %", "like_rate", False),
        ("Comment Rate %", "comment_rate", False),
    ]

    winners = result.get("winners", {})
    for label, key, use_comma in metrics:
        row = [label]
        for ch in result.get("channels", []):
            val = ch.get(key, 0) or 0
            is_winner = (
                key in winners
                and winners[key]["channel_id"] == ch.get("channel_id")
            )
            if use_comma:
                formatted = f"{val:,}"
            elif isinstance(val, float):
                formatted = f"{val:.3f}"
            else:
                formatted = str(val)
            if is_winner:
                formatted = f"[bold green]{formatted}[/bold green]"
            row.append(formatted)
        table.add_row(*row)

    return table


def format_content_gaps_table(result: dict) -> Table:
    """Format content gaps results as a Rich table."""
    table = Table(title="Content Gaps (Uncovered Topics)")
    table.add_column("Topic", style="bold", max_width=50)
    table.add_column("Gap Score", justify="right", style="red")

    for gap in result.get("gaps", [])[:20]:
        table.add_row(
            gap.get("topic", ""),
            f"{gap.get('gap_score', 0):.3f}",
        )
    return table


def format_full_report(result: dict) -> Panel:
    """Format a full analysis report as a Rich Panel with multiple tables."""
    from rich.console import Group
    from rich.text import Text

    parts = []

    header = Text(f"\nFull Report: {result.get('target', 'N/A')}", style="bold blue")
    header.append(f"\nChannels: {result.get('channel_count', 0)}")
    parts.append(Panel(header, title="Report Summary"))

    if "outliers" in result and "error" not in result["outliers"]:
        parts.append(format_outliers_table(result["outliers"]))

    if "engagement" in result and "error" not in result["engagement"]:
        parts.append(format_engagement_table(result["engagement"]))

    if "benchmarks" in result and "error" not in result["benchmarks"]:
        parts.append(format_benchmarks_table(result["benchmarks"]))

    if "titles" in result and "error" not in result["titles"]:
        parts.append(format_titles_table(result["titles"]))

    if "seo" in result and "error" not in result["seo"]:
        parts.append(format_seo_table(result["seo"]))

    if "timing" in result and "error" not in result["timing"]:
        parts.append(format_timing_table(result["timing"]))

    if "regional" in result and "error" not in result["regional"]:
        parts.append(format_regional_table(result["regional"]))

    if "content_gaps" in result and "error" not in result["content_gaps"]:
        parts.append(format_content_gaps_table(result["content_gaps"]))

    return Panel(
        Group(*parts) if parts else Text("No data"),
        title="Bee Content Research Report",
    )


def format_review_report(result: dict) -> Panel:
    """Format a script review report as a Rich Panel."""
    from rich.console import Group
    from rich.text import Text

    parts = []

    # Header with overall score
    overall = result.get("overall_score", 0)
    tier = result.get("tier", "Unknown")
    tier_colors = {
        "Excellent": "bold green",
        "Strong": "green",
        "Good": "blue",
        "Decent": "yellow",
        "Needs Work": "red",
        "Weak": "bold red",
        "Poor": "bold red",
    }
    tier_style = tier_colors.get(tier, "white")

    header = Text()
    header.append("VIDEO REVIEW REPORT\n\n", style="bold blue")
    header.append("OVERALL SCORE: ", style="bold")
    header.append(f"{overall}/100", style=tier_style)
    header.append(f" ({tier})\n", style=tier_style)
    parts.append(Panel(header, title="Script Review"))

    # Pillar scores table
    pillar_table = Table(title="Pillar Scores")
    pillar_table.add_column("Pillar", style="bold", min_width=25)
    pillar_table.add_column("Score", justify="right", min_width=10)
    pillar_table.add_column("Weight", justify="right", style="dim")
    pillar_table.add_column("Status", min_width=15)

    pillar_details = result.get("pillar_details", {})
    attention = result.get("attention_needed", [])

    # Sort by weight descending
    sorted_pillars = sorted(
        pillar_details.items(),
        key=lambda x: x[1].get("weight", 0),
        reverse=True,
    )

    for pillar, details in sorted_pillars:
        score = details.get("score", 0)
        weight = details.get("weight", 0)
        name = details.get("name", pillar)

        if score >= 80:
            score_style = "green"
            status = "Strong"
        elif score >= 60:
            score_style = "yellow"
            status = "OK"
        else:
            score_style = "red"
            status = "Needs attention"

        flag = " <--" if pillar in attention else ""

        pillar_table.add_row(
            name,
            f"[{score_style}]{score}/100[/{score_style}]",
            f"{weight * 100:.0f}%",
            f"[{score_style}]{status}{flag}[/{score_style}]",
        )

    parts.append(pillar_table)

    # Top strengths
    strengths = result.get("top_strengths", [])
    if strengths:
        strength_text = Text()
        strength_text.append("TOP STRENGTHS\n\n", style="bold green")
        for i, s in enumerate(strengths, 1):
            pillar = s.get("pillar", "")
            strength = s.get("strength", "")
            strength_text.append(f"  {i}. ", style="bold")
            strength_text.append(f"[{pillar}] ", style="dim")
            strength_text.append(f"{strength}\n")
        parts.append(Panel(strength_text))

    # Top issues with fixes
    issues = result.get("top_issues", [])
    if issues:
        issue_text = Text()
        issue_text.append("TOP ISSUES (with fixes)\n\n", style="bold red")
        for i, issue in enumerate(issues, 1):
            pillar = issue.get("pillar", "")
            desc = issue.get("description", "")
            fix = issue.get("fix", "")
            location = issue.get("location", "")

            issue_text.append(f"  {i}. ", style="bold")
            issue_text.append(f"[{pillar}] ", style="dim")
            issue_text.append(f"{desc}\n")
            if location:
                issue_text.append(f"     Location: ", style="dim")
                issue_text.append(f"{location[:80]}\n", style="dim italic")
            if fix:
                issue_text.append(f"     Fix: ", style="green")
                issue_text.append(f"{fix}\n", style="green")
            issue_text.append("\n")
        parts.append(Panel(issue_text))

    # Predictions
    predictions = result.get("predictions", {})
    if predictions:
        pred_text = Text()
        pred_text.append("PREDICTIONS\n\n", style="bold cyan")
        pred_text.append(f"  Estimated CTR:         {predictions.get('estimated_ctr', 'N/A')}\n")
        pred_text.append(f"  Avg View Duration:     {predictions.get('estimated_avg_view_duration', 'N/A')}\n")
        pred_text.append(f"  Engagement Level:      {predictions.get('estimated_engagement', 'N/A')}\n")
        pred_text.append(f"  Viral Potential:       {predictions.get('viral_potential', 'N/A')}\n")
        parts.append(Panel(pred_text))

    return Panel(
        Group(*parts) if parts else Text("No data"),
        title="Bee Content Research - Script Review",
    )


def to_json(data: dict | list) -> str:
    """Convert data to pretty-printed JSON string."""
    return json.dumps(data, indent=2, default=str)


def to_csv(data: list[dict]) -> str:
    """Convert a list of dicts to CSV string."""
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()
