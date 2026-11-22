"""Participants and performance stats API router."""

from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import StatOut
from sportstats.db.models import (
    Country,
    MetricDefinition,
    Participant,
    PerformanceStat,
    PlayerProfile,
    Sport,
    TeamProfile,
    Tournament,
    TournamentEdition,
)
from sportstats.db.session import get_db

router = APIRouter(prefix="/participants", tags=["Participants & Stats"])


@router.get("/{id}", response_model=ResponseEnvelope[Dict[str, Any]])
def get_participant_profile(
    id: str,
    db: Session = Depends(get_db),
):
    """Retrieve participant profile and career summary."""
    p = db.query(Participant).filter(Participant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Participant with ID '{id}' not found")

    sport = db.query(Sport).filter(Sport.id == p.sport_id).first() if p.sport_id else None
    country = db.query(Country).filter(Country.id == p.country_id).first() if p.country_id else None

    profile_data = {
        "id": p.id,
        "name": p.name,
        "type": p.type,
        "sport_code": sport.code if sport else "unknown",
        "sport_name": sport.name if sport else "Unknown",
        "country_iso3": country.iso3 if country else None,
        "country_name": country.name if country else None,
        "is_sample": p.is_sample,
    }

    if p.type in ("player", "athlete"):
        player_prof = db.query(PlayerProfile).filter(PlayerProfile.participant_id == p.id).first()
        if player_prof:
            profile_data["full_name"] = player_prof.full_name
            profile_data["birth_date"] = (
                player_prof.birth_date.isoformat() if player_prof.birth_date else None
            )
            profile_data["gender"] = player_prof.gender
            profile_data["role_or_position"] = player_prof.role_or_position
    elif p.type == "team":
        team_prof = db.query(TeamProfile).filter(TeamProfile.participant_id == p.id).first()
        if team_prof:
            profile_data["team_type"] = team_prof.team_type
            profile_data["short_code"] = team_prof.short_code

    # Summary of stats
    stats_count = db.query(PerformanceStat).filter(PerformanceStat.participant_id == p.id).count()
    profile_data["total_recorded_stats"] = stats_count

    return ResponseEnvelope(
        data=profile_data,
        meta=DataMeta(total=1, returned=1),
        provenance=[
            ProvenanceRecord(organisation="Official Participant Profile", is_verified=True)
        ],
    )


@router.get("/{id}/stats", response_model=ResponseEnvelope[List[StatOut]])
def get_participant_stats(
    id: str,
    metric: Annotated[
        Optional[str], Query(description="Filter by metric code (e.g. runs, goals)")
    ] = None,
    scope: Annotated[
        Optional[str], Query(description="Filter by scope (match/edition/career)")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
):
    """Retrieve statistical series for an individual participant."""
    p = db.query(Participant).filter(Participant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Participant with ID '{id}' not found")

    query = db.query(PerformanceStat).filter(PerformanceStat.participant_id == p.id)

    if metric:
        metric_obj = (
            db.query(MetricDefinition).filter(MetricDefinition.code == metric.lower()).first()
        )
        if metric_obj:
            query = query.filter(PerformanceStat.metric_id == metric_obj.id)
        else:
            return ResponseEnvelope(data=[], meta=DataMeta(total=0, returned=0))

    if scope:
        query = query.filter(PerformanceStat.scope == scope)

    stats = query.offset(offset).limit(limit).all()
    out_stats: List[StatOut] = []

    for s in stats:
        m_def = db.query(MetricDefinition).filter(MetricDefinition.id == s.metric_id).first()
        ed = (
            db.query(TournamentEdition).filter(TournamentEdition.id == s.edition_id).first()
            if s.edition_id
            else None
        )
        tourn = (
            db.query(Tournament).filter(Tournament.id == ed.tournament_id).first() if ed else None
        )

        out_stats.append(
            StatOut(
                id=s.id,
                participant_name=p.name,
                tournament_name=tourn.name if tourn else None,
                edition_label=ed.edition_label if ed else None,
                metric_code=m_def.code if m_def else "unknown",
                metric_name=m_def.name if m_def else "Unknown",
                value=float(s.value),
                unit=m_def.unit if m_def else None,
                scope=s.scope,
                is_sample=s.is_sample,
            )
        )

    return ResponseEnvelope(
        data=out_stats,
        meta=DataMeta(total=len(out_stats), limit=limit, offset=offset, returned=len(out_stats)),
        provenance=[
            ProvenanceRecord(
                organisation="Official Statistical Record",
                is_verified=True,
            )
        ],
    )
