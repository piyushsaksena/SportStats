"""Aggregates and performance analysis queries (Section 9.1 & 9.3)."""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from sportstats.db.models import (
    MatchEvent,
    MatchSide,
    MetricDefinition,
    Participant,
    PerformanceStat,
    Sport,
    TournamentEdition,
)
from sportstats.metrics.formulas import (
    calculate_average,
    calculate_draw_percentage,
    calculate_loss_percentage,
    calculate_total,
    calculate_win_percentage,
)


def average_performance(
    db: Session,
    participant_id: str,
    metric_code: str,
    scope: str = "edition",
    window: Optional[int] = None,
) -> Dict[str, Any]:
    """Calculate average and historical series for a participant and metric.

    Returns:
        Dict containing average, total, sample_count, and chronological series.
    """
    query = (
        db.query(
            PerformanceStat.value,
            TournamentEdition.year,
            TournamentEdition.edition_label,
            TournamentEdition.id.label("edition_id"),
        )
        .join(MetricDefinition, PerformanceStat.metric_id == MetricDefinition.id)
        .join(TournamentEdition, PerformanceStat.edition_id == TournamentEdition.id)
        .filter(
            PerformanceStat.participant_id == participant_id,
            MetricDefinition.code == metric_code,
            PerformanceStat.scope == scope,
        )
        .order_by(TournamentEdition.year.asc())
    )

    rows = query.all()
    if window and len(rows) > window:
        rows = rows[-window:]

    values = [float(r.value) for r in rows]
    series = [{"year": r.year, "edition": r.edition_label, "value": float(r.value)} for r in rows]

    return {
        "participant_id": participant_id,
        "metric_code": metric_code,
        "scope": scope,
        "sample_count": len(values),
        "total": calculate_total(values),
        "average": calculate_average(values),
        "series": series,
    }


def extremes(
    db: Session,
    metric_code: str,
    scope: str = "edition",
    sport_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Find the highest and lowest historical values for a metric along with their holders."""
    query = (
        db.query(
            PerformanceStat.value,
            Participant.id.label("participant_id"),
            Participant.name.label("participant_name"),
            TournamentEdition.edition_label,
            TournamentEdition.year,
            MetricDefinition.unit,
            MetricDefinition.name.label("metric_name"),
            MetricDefinition.higher_is_better,
        )
        .join(MetricDefinition, PerformanceStat.metric_id == MetricDefinition.id)
        .join(Participant, PerformanceStat.participant_id == Participant.id)
        .join(TournamentEdition, PerformanceStat.edition_id == TournamentEdition.id)
        .filter(
            MetricDefinition.code == metric_code,
            PerformanceStat.scope == scope,
        )
    )

    if sport_code:
        query = query.join(Sport, Participant.sport_id == Sport.id).filter(Sport.code == sport_code)

    rows = query.all()
    if not rows:
        return {
            "metric_code": metric_code,
            "scope": scope,
            "highest": None,
            "lowest": None,
        }

    highest_row = max(rows, key=lambda r: float(r.value))
    lowest_row = min(rows, key=lambda r: float(r.value))

    return {
        "metric_code": metric_code,
        "metric_name": highest_row.metric_name,
        "unit": highest_row.unit,
        "higher_is_better": highest_row.higher_is_better,
        "highest": {
            "value": float(highest_row.value),
            "participant_id": highest_row.participant_id,
            "participant_name": highest_row.participant_name,
            "edition": highest_row.edition_label,
            "year": highest_row.year,
        },
        "lowest": {
            "value": float(lowest_row.value),
            "participant_id": lowest_row.participant_id,
            "participant_name": lowest_row.participant_name,
            "edition": lowest_row.edition_label,
            "year": lowest_row.year,
        },
    }


def win_percentage(
    db: Session,
    participant_id: str,
    edition_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute matches played, wins, losses, draws, and win/loss/draw percentages."""
    query = (
        db.query(MatchSide, MatchEvent)
        .join(MatchEvent, MatchSide.match_event_id == MatchEvent.id)
        .filter(
            MatchSide.participant_id == participant_id,
            MatchEvent.status == "completed",
        )
    )

    if edition_id:
        query = query.filter(MatchEvent.edition_id == edition_id)

    records = query.all()
    total = len(records)
    wins = sum(1 for ms, me in records if ms.is_winner is True)
    losses = sum(1 for ms, me in records if ms.is_winner is False and not me.is_draw)
    draws = sum(1 for ms, me in records if me.is_draw is True)

    return {
        "participant_id": participant_id,
        "matches_played": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_percentage": calculate_win_percentage(wins, total),
        "loss_percentage": calculate_loss_percentage(losses, total),
        "draw_percentage": calculate_draw_percentage(draws, total),
    }
