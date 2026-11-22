"""Trend detection, linear regression, scoring patterns, and format comparisons (Section 9.3 & 9.4)."""

from typing import Any, Dict, List

import numpy as np
from scipy import stats
from sqlalchemy.orm import Session

from sportstats.db.models import (
    MatchEvent,
    MatchSide,
    MetricDefinition,
    PerformanceStat,
    TournamentEdition,
)


def year_to_year_trend(
    db: Session,
    participant_id: str,
    metric_code: str,
    scope: str = "edition",
) -> Dict[str, Any]:
    """Calculate historical year-to-year trend with linear regression and sample size warnings.

    Returns:
        Dict with series, percent change, slope, R², p-value, coverage band, and warnings.
    """
    rows = (
        db.query(
            PerformanceStat.value,
            TournamentEdition.year,
            TournamentEdition.edition_label,
            TournamentEdition.format_description,
        )
        .join(MetricDefinition, PerformanceStat.metric_id == MetricDefinition.id)
        .join(TournamentEdition, PerformanceStat.edition_id == TournamentEdition.id)
        .filter(
            PerformanceStat.participant_id == participant_id,
            MetricDefinition.code == metric_code,
            PerformanceStat.scope == scope,
        )
        .order_by(TournamentEdition.year.asc())
        .all()
    )

    if not rows:
        return {
            "participant_id": participant_id,
            "metric_code": metric_code,
            "sample_count": 0,
            "has_sufficient_data": False,
            "warning": "No historical data found for participant and metric.",
            "series": [],
            "coverage": None,
            "regression": None,
        }

    series = []
    x_years = []
    y_values = []
    for r in rows:
        val = float(r.value)
        series.append(
            {
                "year": r.year,
                "edition": r.edition_label,
                "value": val,
                "format": r.format_description,
            }
        )
        x_years.append(r.year)
        y_values.append(val)

    sample_count = len(y_values)
    min_year, max_year = min(x_years), max(x_years)
    coverage = f"Data available for {min_year}–{max_year}"

    # Calculate overall percent change
    first_val = y_values[0]
    last_val = y_values[-1]
    pct_change = (
        round(((last_val - first_val) / abs(first_val)) * 100.0, 2) if first_val != 0 else None
    )

    # Minimum data threshold (Report Section 9.3: < 5 points = insufficient for trend)
    has_sufficient_data = sample_count >= 5
    warning = (
        None
        if has_sufficient_data
        else f"Fewer than 5 data points ({sample_count} observations): Insufficient data for reliable statistical trend."
    )

    regression = None
    if sample_count >= 2:
        try:
            x_arr = np.array(x_years, dtype=float)
            y_arr = np.array(y_values, dtype=float)
            res = stats.linregress(x_arr, y_arr)
            regression = {
                "slope": round(float(res.slope), 4),
                "intercept": round(float(res.intercept), 4),
                "r_squared": round(float(res.rvalue**2), 4),
                "p_value": round(float(res.pvalue), 4),
                "std_err": round(float(res.stderr), 4) if res.stderr else 0.0,
                "direction": "upward"
                if res.slope > 0
                else ("downward" if res.slope < 0 else "flat"),
            }
        except Exception:
            regression = None

    return {
        "participant_id": participant_id,
        "metric_code": metric_code,
        "sample_count": sample_count,
        "has_sufficient_data": has_sufficient_data,
        "warning": warning,
        "coverage": coverage,
        "percent_change": pct_change,
        "series": series,
        "regression": regression,
    }


def scoring_patterns(db: Session, tournament_id: str) -> List[Dict[str, Any]]:
    """Compute average scoring patterns per match across tournament editions."""
    editions = (
        db.query(TournamentEdition)
        .filter(TournamentEdition.tournament_id == tournament_id)
        .order_by(TournamentEdition.year.asc())
        .all()
    )

    patterns = []
    for ed in editions:
        sides = (
            db.query(MatchSide.score_primary)
            .join(MatchEvent, MatchSide.match_event_id == MatchEvent.id)
            .filter(
                MatchEvent.edition_id == ed.id,
                MatchSide.score_primary.isnot(None),
            )
            .all()
        )
        scores = [float(s[0]) for s in sides if s[0] is not None]
        avg_score = round(float(np.mean(scores)), 2) if scores else None
        total_matches = ed.matches_or_events_count or len(ed.matches)

        patterns.append(
            {
                "edition_id": ed.id,
                "edition_label": ed.edition_label,
                "year": ed.year,
                "total_matches": total_matches,
                "average_score_per_side": avg_score,
                "total_scores_recorded": len(scores),
            }
        )

    return patterns


def participation_trends(db: Session, tournament_id: str) -> List[Dict[str, Any]]:
    """Analyze participant counts and roster growth across tournament editions."""
    editions = (
        db.query(TournamentEdition)
        .filter(TournamentEdition.tournament_id == tournament_id)
        .order_by(TournamentEdition.year.asc())
        .all()
    )

    return [
        {
            "edition_id": ed.id,
            "edition_label": ed.edition_label,
            "year": ed.year,
            "participant_count": ed.participant_count,
            "format": ed.format_description,
        }
        for ed in editions
    ]


def format_comparison(db: Session, tournament_id: str) -> List[Dict[str, Any]]:
    """Compare editions of a tournament to detect and annotate format changes."""
    editions = (
        db.query(TournamentEdition)
        .filter(TournamentEdition.tournament_id == tournament_id)
        .order_by(TournamentEdition.year.asc())
        .all()
    )

    comparisons = []
    prev_format = None
    for ed in editions:
        fmt = ed.format_description or "Standard"
        has_format_change = prev_format is not None and fmt != prev_format
        comparisons.append(
            {
                "edition_id": ed.id,
                "edition_label": ed.edition_label,
                "year": ed.year,
                "format": fmt,
                "has_format_changed": has_format_change,
                "participant_count": ed.participant_count,
                "matches_count": ed.matches_or_events_count,
            }
        )
        prev_format = fmt

    return comparisons
