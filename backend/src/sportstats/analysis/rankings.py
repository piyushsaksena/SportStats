"""Rankings history and Olympic medal distribution analysis (Report Figure 7 & Section 9.3)."""

from typing import Any, Dict, Optional

from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from sportstats.db.models import (
    Country,
    OlympicResult,
    Participant,
    RankingEntry,
    RankingSnapshot,
)


def ranking_history(
    db: Session,
    participant_id: str,
    system: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve chronological ranking timeline for a participant."""
    query = (
        db.query(
            RankingEntry.rank,
            RankingEntry.points,
            RankingSnapshot.as_of_date,
            RankingSnapshot.ranking_system,
            RankingSnapshot.category,
            Participant.name.label("participant_name"),
        )
        .join(RankingSnapshot, RankingEntry.snapshot_id == RankingSnapshot.id)
        .join(Participant, RankingEntry.participant_id == Participant.id)
        .filter(RankingEntry.participant_id == participant_id)
        .order_by(RankingSnapshot.as_of_date.asc())
    )

    if system:
        query = query.filter(RankingSnapshot.ranking_system == system)

    rows = query.all()
    if not rows:
        return {
            "participant_id": participant_id,
            "timeline": [],
            "best_rank": None,
            "latest_rank": None,
        }

    timeline = [
        {
            "as_of_date": r.as_of_date.isoformat(),
            "rank": r.rank,
            "points": float(r.points) if r.points is not None else None,
            "system": r.ranking_system,
            "category": r.category,
        }
        for r in rows
    ]

    best_rank = min(r.rank for r in rows)
    latest_rank = rows[-1].rank

    return {
        "participant_id": participant_id,
        "participant_name": rows[0].participant_name,
        "best_rank": best_rank,
        "latest_rank": latest_rank,
        "timeline": timeline,
    }


def country_medal_distribution(
    db: Session,
    edition_id: Optional[str] = None,
    max_slices: int = 6,
) -> Dict[str, Any]:
    """Generate Olympic medal distribution suitable for Pie Charts (Report Figure 7 style).

    Aggregates gold, silver, and bronze medals by nation.
    Limits to top (max_slices - 1) nations and consolidates the rest into 'Others'.
    """
    query = (
        db.query(
            Country.iso3,
            Country.name.label("country_name"),
            func.count(OlympicResult.id).label("total_medals"),
            func.sum(case((OlympicResult.medal == "gold", 1), else_=0)).label("gold_medals"),
            func.sum(case((OlympicResult.medal == "silver", 1), else_=0)).label("silver_medals"),
            func.sum(case((OlympicResult.medal == "bronze", 1), else_=0)).label("bronze_medals"),
        )
        .join(Participant, OlympicResult.participant_id == Participant.id)
        .join(Country, Participant.country_id == Country.id)
        .filter(OlympicResult.medal.isnot(None))
    )

    if edition_id:
        query = query.filter(OlympicResult.edition_id == edition_id)

    query = query.group_by(Country.iso3, Country.name).order_by(
        desc("gold_medals"), desc("total_medals")
    )

    rows = query.all()
    if not rows:
        return {"slices": [], "total_medals_awarded": 0}

    total_medals_all = sum(r.total_medals for r in rows)
    slices = []

    top_rows = rows[: max_slices - 1]
    other_rows = rows[max_slices - 1 :]

    for r in top_rows:
        pct = round((r.total_medals / total_medals_all) * 100.0, 1) if total_medals_all > 0 else 0.0
        slices.append(
            {
                "iso3": r.iso3,
                "country": r.country_name,
                "gold": int(r.gold_medals or 0),
                "silver": int(r.silver_medals or 0),
                "bronze": int(r.bronze_medals or 0),
                "total": int(r.total_medals),
                "percentage": pct,
            }
        )

    if other_rows:
        other_total = sum(r.total_medals for r in other_rows)
        other_gold = sum(r.gold_medals or 0 for r in other_rows)
        other_silver = sum(r.silver_medals or 0 for r in other_rows)
        other_bronze = sum(r.bronze_medals or 0 for r in other_rows)
        other_pct = (
            round((other_total / total_medals_all) * 100.0, 1) if total_medals_all > 0 else 0.0
        )
        slices.append(
            {
                "iso3": "OTH",
                "country": "Others",
                "gold": int(other_gold),
                "silver": int(other_silver),
                "bronze": int(other_bronze),
                "total": int(other_total),
                "percentage": other_pct,
            }
        )

    return {
        "total_medals_awarded": total_medals_all,
        "slices": slices,
    }
