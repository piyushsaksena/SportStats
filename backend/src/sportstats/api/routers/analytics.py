"""Analytics, cross-sport comparisons, rankings, records, and trends router."""

from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sportstats.analysis.compare import (
    CrossSportComparisonError,
    compare_players,
    compare_teams,
    compare_tournaments,
)
from sportstats.analysis.rankings import country_medal_distribution
from sportstats.analysis.records import records_and_milestones
from sportstats.analysis.trends import year_to_year_trend
from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import RankingOut
from sportstats.db.models import (
    Participant,
    RankingEntry,
    RankingSnapshot,
    Sport,
    Tournament,
    TournamentEdition,
)
from sportstats.db.session import get_db

router = APIRouter(tags=["Analytics & Comparisons"])


@router.get("/compare/players", response_model=ResponseEnvelope[Dict[str, Any]])
def compare_players_endpoint(
    ids: Annotated[str, Query(description="Comma-separated participant IDs")],
    metrics: Annotated[str, Query(description="Comma-separated metric codes")],
    edition_id: Annotated[Optional[str], Query(description="Optional edition filter")] = None,
    db: Session = Depends(get_db),
):
    """Head-to-head or multi-player comparison with Cross-Sport Comparison Guard."""
    participant_ids = [pid.strip() for pid in ids.split(",") if pid.strip()]
    metric_codes = [m.strip() for m in metrics.split(",") if m.strip()]

    if not participant_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one participant ID")

    try:
        res = compare_players(db, participant_ids, metric_codes, edition_id=edition_id)
    except CrossSportComparisonError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ResponseEnvelope(
        data=res,
        meta=DataMeta(
            total=len(res.get("participants", [])), returned=len(res.get("participants", []))
        ),
        provenance=[
            ProvenanceRecord(organisation="Official Statistical Comparison Layer", is_verified=True)
        ],
    )


@router.get("/compare/teams", response_model=ResponseEnvelope[Dict[str, Any]])
def compare_teams_endpoint(
    ids: Annotated[str, Query(description="Comma-separated team participant IDs")],
    metrics: Annotated[str, Query(description="Comma-separated metric codes")],
    edition_id: Annotated[Optional[str], Query(description="Optional edition filter")] = None,
    db: Session = Depends(get_db),
):
    """Team-level direct comparison or normalized cross-sport comparison."""
    participant_ids = [pid.strip() for pid in ids.split(",") if pid.strip()]
    metric_codes = [m.strip() for m in metrics.split(",") if m.strip()]

    if not participant_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one team participant ID")

    try:
        res = compare_teams(db, participant_ids, metric_codes, edition_id=edition_id)
    except CrossSportComparisonError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ResponseEnvelope(
        data=res,
        meta=DataMeta(
            total=len(res.get("participants", [])), returned=len(res.get("participants", []))
        ),
        provenance=[
            ProvenanceRecord(organisation="Official Statistical Comparison Layer", is_verified=True)
        ],
    )


@router.get("/compare/tournaments", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def compare_tournaments_endpoint(
    ids: Annotated[str, Query(description="Comma-separated tournament IDs")],
    db: Session = Depends(get_db),
):
    """Compare major tournaments across sports according to Report Table 5 framework."""
    tourn_ids = [tid.strip() for tid in ids.split(",") if tid.strip()]
    if not tourn_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one tournament ID")

    res = compare_tournaments(db, tourn_ids)
    return ResponseEnvelope(
        data=res,
        meta=DataMeta(total=len(res), returned=len(res)),
        provenance=[
            ProvenanceRecord(
                organisation="Report Table 5 Comparison Framework",
                is_verified=True,
            )
        ],
    )


@router.get("/trends", response_model=ResponseEnvelope[Dict[str, Any]])
def get_trends_endpoint(
    participant: Annotated[str, Query(description="Participant ID")],
    metric: Annotated[str, Query(description="Metric code (e.g. win_percentage, runs, points)")],
    scope: Annotated[str, Query(description="Scope: match, edition, career")] = "edition",
    db: Session = Depends(get_db),
):
    """Retrieve statistical trends over time with linear regression and sample size warnings."""
    res = year_to_year_trend(db, participant_id=participant, metric_code=metric, scope=scope)
    return ResponseEnvelope(
        data=res,
        meta=DataMeta(total=res.get("sample_count", 0), returned=res.get("sample_count", 0)),
        provenance=[
            ProvenanceRecord(organisation="Deterministic Regression Engine", is_verified=True)
        ],
    )


@router.get("/rankings", response_model=ResponseEnvelope[List[RankingOut]])
def get_rankings_endpoint(
    sport: Annotated[Optional[str], Query(description="Sport code")] = None,
    system: Annotated[Optional[str], Query(description="Ranking system name")] = None,
    db: Session = Depends(get_db),
):
    """Retrieve official ranking snapshots and standings."""
    query = (
        db.query(
            RankingSnapshot.ranking_system,
            RankingSnapshot.category,
            RankingSnapshot.as_of_date,
            RankingEntry.rank,
            RankingEntry.points,
            Participant.name.label("participant_name"),
        )
        .join(RankingEntry, RankingSnapshot.id == RankingEntry.snapshot_id)
        .join(Participant, RankingEntry.participant_id == Participant.id)
    )

    if sport:
        sport_rec = db.query(Sport).filter(Sport.code == sport.lower()).first()
        if sport_rec:
            query = query.filter(RankingSnapshot.sport_id == sport_rec.id)
        else:
            return ResponseEnvelope(data=[], meta=DataMeta(total=0, returned=0))

    if system:
        query = query.filter(RankingSnapshot.ranking_system.ilike(f"%{system}%"))

    rows = query.order_by(RankingSnapshot.as_of_date.desc(), RankingEntry.rank.asc()).all()

    data = [
        RankingOut(
            ranking_system=r.ranking_system,
            category=r.category,
            as_of_date=r.as_of_date,
            rank=r.rank,
            participant_name=r.participant_name,
            points=float(r.points) if r.points is not None else None,
        )
        for r in rows
    ]

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=len(data), returned=len(data)),
        provenance=[ProvenanceRecord(organisation="Official World Rankings", is_verified=True)],
    )


@router.get("/records", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_records_endpoint(
    sport: Annotated[Optional[str], Query(description="Filter by sport code")] = None,
    record_type: Annotated[
        Optional[str], Query(description="Record type: world, olympic, tournament")
    ] = None,
    db: Session = Depends(get_db),
):
    """Retrieve verified records, world records, and milestones."""
    res = records_and_milestones(db, sport_code=sport, record_type=record_type)
    return ResponseEnvelope(
        data=res,
        meta=DataMeta(total=len(res), returned=len(res)),
        provenance=[
            ProvenanceRecord(organisation="Official Federation Record Books", is_verified=True)
        ],
    )


@router.get("/olympics/medals", response_model=ResponseEnvelope[Dict[str, Any]])
def get_olympics_medals_endpoint(
    edition: Annotated[Optional[str], Query(description="Edition ID or Label")] = None,
    max_slices: Annotated[
        int, Query(ge=3, le=15, description="Max pie slices (top N + Others)")
    ] = 6,
    db: Session = Depends(get_db),
):
    """Retrieve Olympic medal distribution formatted for Figure 7 pie charts."""
    edition_id = None
    if edition:
        ed_obj = (
            db.query(TournamentEdition)
            .filter(
                (TournamentEdition.id == edition)
                | (TournamentEdition.edition_label.ilike(f"%{edition}%"))
            )
            .first()
        )
        if ed_obj:
            edition_id = ed_obj.id

    res = country_medal_distribution(db, edition_id=edition_id, max_slices=max_slices)
    return ResponseEnvelope(
        data=res,
        meta=DataMeta(
            total=res.get("total_medals_awarded", 0), returned=len(res.get("slices", []))
        ),
        provenance=[
            ProvenanceRecord(organisation="International Olympic Committee (IOC)", is_verified=True)
        ],
    )
    """Retrieve Olympic medal distribution formatted for Figure 7 pie charts."""
    edition_id = None
    if edition:
        ed_obj = (
            db.query(TournamentEdition)
            .filter(
                (TournamentEdition.id == edition)
                | (TournamentEdition.edition_label.ilike(f"%{edition}%"))
            )
            .first()
        )
        if ed_obj:
            edition_id = ed_obj.id

    res = country_medal_distribution(db, edition_id=edition_id, max_slices=max_slices)
    return ResponseEnvelope(
        data=res,
        meta=DataMeta(
            total=res.get("total_medals_awarded", 0), returned=len(res.get("slices", []))
        ),
        provenance=[
            ProvenanceRecord(organisation="International Olympic Committee (IOC)", is_verified=True)
        ],
    )


@router.get("/tracking", response_model=ResponseEnvelope[Dict[str, Any]])
def get_tournament_tracking_feed(
    db: Session = Depends(get_db),
):
    """Retrieve unified tournament tracking feed grouped into upcoming, ongoing, and completed."""
    editions = db.query(TournamentEdition).order_by(TournamentEdition.start_date.desc()).all()

    upcoming = []
    ongoing = []
    completed = []

    for ed in editions:
        tourn = db.query(Tournament).filter(Tournament.id == ed.tournament_id).first()
        sport = db.query(Sport).filter(Sport.id == tourn.sport_id).first() if tourn else None
        winner_p = (
            db.query(Participant).filter(Participant.id == ed.winner_participant_id).first()
            if ed.winner_participant_id
            else None
        )

        item = {
            "id": ed.id,
            "tournament_name": tourn.name if tourn else "Unknown",
            "sport_code": sport.code if sport else "unknown",
            "edition_label": ed.edition_label,
            "year": ed.year,
            "host_city": ed.host_city,
            "start_date": ed.start_date.isoformat(),
            "end_date": ed.end_date.isoformat(),
            "status": ed.status,
            "winner": winner_p.name if winner_p else None,
        }

        if ed.status == "upcoming":
            upcoming.append(item)
        elif ed.status == "ongoing":
            ongoing.append(item)
        else:
            completed.append(item)

    data = {
        "upcoming": upcoming,
        "ongoing": ongoing,
        "completed": completed,
        "summary": {
            "total_tracked": len(editions),
            "upcoming_count": len(upcoming),
            "ongoing_count": len(ongoing),
            "completed_count": len(completed),
        },
    }

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=len(editions), returned=len(editions)),
        provenance=[
            ProvenanceRecord(organisation="SportStats Global Tracking Pipeline", is_verified=True)
        ],
    )
