"""Reporting service: runs all analyzers and produces full reports."""

from ..storage.db import Database
from . import analysis


def full_report(db: Database, niche: str) -> dict:
    """Run all analyzers on a niche group and produce a comprehensive report.

    Args:
        db: Database instance.
        niche: Niche group name or channel ID.

    Returns:
        Dict with results from all analyzers.
    """
    channel_ids = db.resolve_target(niche)
    if not channel_ids:
        return {"error": f"Target '{niche}' not found"}

    report = {
        "target": niche,
        "channel_count": len(channel_ids),
    }

    # Run each analyzer, catching errors to allow partial reports
    try:
        report["outliers"] = analysis.outliers(db, niche)
    except Exception as e:
        report["outliers"] = {"error": str(e)}

    try:
        report["engagement"] = analysis.engagement(db, niche)
    except Exception as e:
        report["engagement"] = {"error": str(e)}

    try:
        report["benchmarks"] = analysis.benchmarks(db, niche)
    except Exception as e:
        report["benchmarks"] = {"error": str(e)}

    try:
        report["titles"] = analysis.titles(db, niche)
    except Exception as e:
        report["titles"] = {"error": str(e)}

    try:
        report["seo"] = analysis.seo(db, niche)
    except Exception as e:
        report["seo"] = {"error": str(e)}

    try:
        report["timing"] = analysis.timing(db, niche)
    except Exception as e:
        report["timing"] = {"error": str(e)}

    try:
        report["regional"] = analysis.regional(db, niche)
    except Exception as e:
        report["regional"] = {"error": str(e)}

    try:
        report["content_gaps"] = analysis.content_gaps(db, niche)
    except Exception as e:
        report["content_gaps"] = {"error": str(e)}

    return report


def get_status(db: Database) -> dict:
    """Get database status and data freshness info."""
    return db.get_status()
