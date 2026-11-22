"""Comparison framework for players, teams, tournaments, and cross-sport analysis (Section 9.3 & Table 5)."""

from typing import Any, Dict, List, Optional

import numpy as np
from sqlalchemy.orm import Session

from sportstats.db.models import (
    MetricDefinition,
    Participant,
    PerformanceStat,
    Sport,
    Tournament,
    TournamentEdition,
)

ALLOWED_CROSS_SPORT_METRICS = {
    "win_percentage",
    "loss_percentage",
    "draw_percentage",
    "matches_played",
    "z_score",
    "percentile",
    "participant_count",
}


class CrossSportComparisonError(ValueError):
    """Exception raised when an invalid raw-value comparison across different sports is requested."""

    pass


def validate_cross_sport_safety(sport_codes: List[str], metric_codes: List[str]) -> None:
    """Enforces the Non-Negotiable Cross-Sport Comparison Rule.

    Raw values (goals vs runs vs points) are NOT directly comparable across different sports.
    If multiple distinct sports are involved, only normalized measures (win %, percentile,
    z-score, matches_played) are permitted.
    """
    distinct_sports = set(sport_codes)
    if len(distinct_sports) > 1:
        invalid_metrics = [m for m in metric_codes if m not in ALLOWED_CROSS_SPORT_METRICS]
        if invalid_metrics:
            raise CrossSportComparisonError(
                f"Cross-Sport Comparison Guard Violation: Raw statistical values ({', '.join(invalid_metrics)}) "
                f"cannot be directly compared across different sports ({', '.join(distinct_sports)}). "
                f"Cross-sport analysis must use normalized measures only: {', '.join(sorted(ALLOWED_CROSS_SPORT_METRICS))}."
            )


def calculate_z_scores(values: List[float]) -> List[float]:
    """Compute standard z-scores: z = (x - μ) / σ."""
    if len(values) <= 1:
        return [0.0 for _ in values]
    arr = np.array(values, dtype=float)
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0.0:
        return [0.0 for _ in values]
    return [round(float((x - mean) / std), 3) for x in arr]


def calculate_percentiles(values: List[float]) -> List[float]:
    """Compute empirical percentile rank for each value in a sample (0 to 100)."""
    if not values:
        return []
    arr = np.array(values, dtype=float)
    n = len(arr)
    ranks = []
    for val in arr:
        count_less = np.sum(arr < val)
        count_equal = np.sum(arr == val)
        pct = ((count_less + (0.5 * count_equal)) / n) * 100.0
        ranks.append(round(float(pct), 1))
    return ranks


def compare_players(
    db: Session,
    player_ids: List[str],
    metric_codes: List[str],
    edition_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare multiple players on selected metrics."""
    return _compare_participants(
        db, player_ids, metric_codes, participant_type="player", edition_id=edition_id
    )


def compare_teams(
    db: Session,
    team_ids: List[str],
    metric_codes: List[str],
    edition_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare multiple teams on selected metrics."""
    return _compare_participants(
        db, team_ids, metric_codes, participant_type="team", edition_id=edition_id
    )


def _compare_participants(
    db: Session,
    participant_ids: List[str],
    metric_codes: List[str],
    participant_type: str,
    edition_id: Optional[str] = None,
) -> Dict[str, Any]:
    participants = (
        db.query(Participant, Sport.code.label("sport_code"), Sport.name.label("sport_name"))
        .join(Sport, Participant.sport_id == Sport.id)
        .filter(Participant.id.in_(participant_ids))
        .all()
    )

    if not participants:
        return {"participants": [], "metrics": [], "matrix": {}}

    sport_codes = [p.sport_code for p in participants]
    is_cross_sport = len(set(sport_codes)) > 1

    # Validate cross-sport safety
    validate_cross_sport_safety(sport_codes, metric_codes)

    results = []
    for p, sport_code, sport_name in participants:
        p_stats = {}
        for m_code in metric_codes:
            stat_query = (
                db.query(PerformanceStat.value)
                .join(MetricDefinition, PerformanceStat.metric_id == MetricDefinition.id)
                .filter(
                    PerformanceStat.participant_id == p.id,
                    MetricDefinition.code == m_code,
                )
            )
            if edition_id:
                stat_query = stat_query.filter(PerformanceStat.edition_id == edition_id)

            stat_row = stat_query.first()
            p_stats[m_code] = float(stat_row.value) if stat_row else None

        results.append(
            {
                "id": p.id,
                "name": p.name,
                "sport_code": sport_code,
                "sport_name": sport_name,
                "stats": p_stats,
            }
        )

    return {
        "is_cross_sport": is_cross_sport,
        "participants": results,
        "metrics_requested": metric_codes,
        "comparability_note": (
            "Cross-sport comparisons use normalized measures to ensure scientific validity."
            if is_cross_sport
            else "Single-sport direct statistical comparison."
        ),
    }


def compare_tournaments(
    db: Session,
    tournament_ids: List[str],
    key_metric_codes: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Compare major tournaments across sports (Implements Report Table 5).

    Table 5 columns:
    - Sport
    - Tournament
    - Teams / Players (Participant count)
    - Matches / Events
    - Winner (Latest Edition)
    - Key Statistic
    """
    tournaments = (
        db.query(Tournament, Sport.code.label("sport_code"), Sport.name.label("sport_name"))
        .join(Sport, Tournament.sport_id == Sport.id)
        .filter(Tournament.id.in_(tournament_ids))
        .all()
    )

    table5_rows = []
    for tourney, sport_code, sport_name in tournaments:
        # Get latest completed edition
        latest_edition = (
            db.query(TournamentEdition)
            .filter(
                TournamentEdition.tournament_id == tourney.id,
                TournamentEdition.status == "completed",
            )
            .order_by(TournamentEdition.year.desc())
            .first()
        )

        winner_name = "Not Available"
        participant_count = 0
        matches_count = 0
        key_statistic_desc = "Not Available"

        if latest_edition:
            participant_count = latest_edition.participant_count
            matches_count = latest_edition.matches_or_events_count or 0
            if latest_edition.winner_participant_id:
                winner = (
                    db.query(Participant)
                    .filter(Participant.id == latest_edition.winner_participant_id)
                    .first()
                )
                if winner:
                    winner_name = winner.name

            # Look up key stat if provided
            if key_metric_codes and sport_code in key_metric_codes:
                target_metric = key_metric_codes[sport_code]
                stat = (
                    db.query(PerformanceStat.value, MetricDefinition.unit)
                    .join(MetricDefinition, PerformanceStat.metric_id == MetricDefinition.id)
                    .filter(
                        PerformanceStat.edition_id == latest_edition.id,
                        MetricDefinition.code == target_metric,
                    )
                    .first()
                )
                if stat:
                    key_statistic_desc = f"{target_metric}: {float(stat.value)} {stat.unit}"

        table5_rows.append(
            {
                "sport": sport_name,
                "sport_code": sport_code,
                "tournament": tourney.name,
                "latest_edition": latest_edition.edition_label if latest_edition else "N/A",
                "teams_or_players": participant_count,
                "matches_or_events": matches_count,
                "winner": winner_name,
                "key_statistic": key_statistic_desc,
            }
        )

    return table5_rows
