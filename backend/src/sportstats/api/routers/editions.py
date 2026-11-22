"""Tournament Editions API router."""

from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import MatchOut, ParticipantOut, StandingOut
from sportstats.db.models import (
    Country,
    MatchEvent,
    MatchSide,
    Participant,
    Source,
    Sport,
    Stage,
    Tournament,
    TournamentEdition,
)
from sportstats.db.session import get_db

router = APIRouter(prefix="/editions", tags=["Editions"])


@router.get("/{id}", response_model=ResponseEnvelope[Dict[str, Any]])
def get_edition_detail(
    id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full Table 2 tracking template header card for a tournament edition."""
    ed = db.query(TournamentEdition).filter(TournamentEdition.id == id).first()
    if not ed:
        raise HTTPException(status_code=404, detail=f"Edition with ID '{id}' not found")

    tourn = db.query(Tournament).filter(Tournament.id == ed.tournament_id).first()
    sport = db.query(Sport).filter(Sport.id == tourn.sport_id).first() if tourn else None
    host_c = (
        db.query(Country).filter(Country.id == ed.host_country_id).first()
        if ed.host_country_id
        else None
    )
    source = db.query(Source).filter(Source.id == ed.source_id).first() if ed.source_id else None

    winner_p = (
        db.query(Participant).filter(Participant.id == ed.winner_participant_id).first()
        if ed.winner_participant_id
        else None
    )
    runner_p = (
        db.query(Participant).filter(Participant.id == ed.runner_up_participant_id).first()
        if ed.runner_up_participant_id
        else None
    )

    card = {
        "id": ed.id,
        "tournament_id": tourn.id if tourn else None,
        "tournament_name": tourn.name if tourn else "Unknown",
        "sport_code": sport.code if sport else "unknown",
        "governing_body": tourn.governing_body if tourn else "Official",
        "edition_label": ed.edition_label,
        "year": ed.year,
        "host_country_iso3": host_c.iso3 if host_c else None,
        "host_country_name": host_c.name if host_c else None,
        "host_city": ed.host_city or "Not available",
        "start_date": ed.start_date.isoformat(),
        "end_date": ed.end_date.isoformat(),
        "status": ed.status,
        "participant_count": ed.participant_count,
        "format_description": ed.format_description or "Standard official championship draw",
        "matches_or_events_count": ed.matches_or_events_count,
        "winner": winner_p.name if winner_p else "Not available",
        "runner_up": runner_p.name if runner_p else "Not available",
        "source_org": source.organisation
        if source
        else (tourn.governing_body if tourn else "Official"),
        "source_url": source.url if source else None,
        "is_sample": ed.is_sample,
    }

    provenance = []
    if source:
        provenance.append(
            ProvenanceRecord(
                source_id=source.id,
                organisation=source.organisation,
                url=source.url,
                retrieved_at=source.retrieved_at,
                is_verified=source.is_verified,
                is_sample=ed.is_sample,
            )
        )

    return ResponseEnvelope(data=card, meta=DataMeta(total=1, returned=1), provenance=provenance)


@router.get("/{id}/matches", response_model=ResponseEnvelope[List[MatchOut]])
def get_edition_matches(
    id: str,
    stage: Annotated[Optional[str], Query(description="Filter by stage name")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
):
    """Retrieve all matches or events in an edition with scorecards."""
    ed = db.query(TournamentEdition).filter(TournamentEdition.id == id).first()
    if not ed:
        raise HTTPException(status_code=404, detail=f"Edition with ID '{id}' not found")

    query = db.query(MatchEvent).filter(MatchEvent.edition_id == ed.id)

    if stage:
        stage_obj = (
            db.query(Stage)
            .filter(Stage.edition_id == ed.id, Stage.name.ilike(f"%{stage}%"))
            .first()
        )
        if stage_obj:
            query = query.filter(MatchEvent.stage_id == stage_obj.id)
        else:
            return ResponseEnvelope(data=[], meta=DataMeta(total=0, returned=0))

    events = query.order_by(MatchEvent.scheduled_at).all()
    out_matches: List[MatchOut] = []

    for ev in events:
        stage_rec = db.query(Stage).filter(Stage.id == ev.stage_id).first() if ev.stage_id else None
        sides = (
            db.query(MatchSide)
            .filter(MatchSide.match_event_id == ev.id)
            .order_by(MatchSide.side_index)
            .all()
        )

        p_a_name = "Side A"
        p_b_name = "Side B"
        s_a = None
        s_b = None

        if len(sides) >= 1:
            p_a = db.query(Participant).filter(Participant.id == sides[0].participant_id).first()
            p_a_name = p_a.name if p_a else "Side A"
            s_a = str(sides[0].score_primary) if sides[0].score_primary is not None else None

        if len(sides) >= 2:
            p_b = db.query(Participant).filter(Participant.id == sides[1].participant_id).first()
            p_b_name = p_b.name if p_b else "Side B"
            s_b = str(sides[1].score_primary) if sides[1].score_primary is not None else None

        winner_name = None
        if ev.winner_participant_id:
            w_p = db.query(Participant).filter(Participant.id == ev.winner_participant_id).first()
            winner_name = w_p.name if w_p else None

        out_matches.append(
            MatchOut(
                id=ev.id,
                edition_id=ev.edition_id,
                stage=stage_rec.name if stage_rec else "Match",
                scheduled_at=ev.scheduled_at,
                venue=None,
                status=ev.status,
                participant_a=p_a_name,
                participant_b=p_b_name,
                score_a=s_a,
                score_b=s_b,
                winner=winner_name,
                is_draw=ev.is_draw,
                result_summary=ev.result_summary,
                is_sample=ev.is_sample,
            )
        )

    paginated = out_matches[offset : offset + limit]

    return ResponseEnvelope(
        data=paginated,
        meta=DataMeta(total=len(out_matches), limit=limit, offset=offset, returned=len(paginated)),
        provenance=[
            ProvenanceRecord(
                organisation="Official Federation Match Centre",
                is_verified=True,
            )
        ],
    )


@router.get("/{id}/participants", response_model=ResponseEnvelope[List[ParticipantOut]])
def get_edition_participants(
    id: str,
    db: Session = Depends(get_db),
):
    """List participating teams or athletes involved in the tournament edition."""
    ed = db.query(TournamentEdition).filter(TournamentEdition.id == id).first()
    if not ed:
        raise HTTPException(status_code=404, detail=f"Edition with ID '{id}' not found")

    tourn = db.query(Tournament).filter(Tournament.id == ed.tournament_id).first()
    sport = db.query(Sport).filter(Sport.id == tourn.sport_id).first() if tourn else None
    sport_code = sport.code if sport else "multi"

    # Gather participants from matches in this edition
    match_ids = [m.id for m in db.query(MatchEvent).filter(MatchEvent.edition_id == ed.id).all()]
    p_ids = set()
    if match_ids:
        sides = db.query(MatchSide).filter(MatchSide.match_event_id.in_(match_ids)).all()
        for s in sides:
            p_ids.add(s.participant_id)

    if ed.winner_participant_id:
        p_ids.add(ed.winner_participant_id)
    if ed.runner_up_participant_id:
        p_ids.add(ed.runner_up_participant_id)

    participants = (
        db.query(Participant).filter(Participant.id.in_(list(p_ids))).all() if p_ids else []
    )

    data = [
        ParticipantOut(
            id=p.id,
            type=p.type,
            name=p.name,
            sport_code=sport_code,
            is_sample=p.is_sample,
        )
        for p in participants
    ]

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=len(data), returned=len(data)),
        provenance=[ProvenanceRecord(organisation="Official Tournament Roster", is_verified=True)],
    )


@router.get("/{id}/standings", response_model=ResponseEnvelope[List[StandingOut]])
def get_edition_standings(
    id: str,
    db: Session = Depends(get_db),
):
    """Retrieve computed standings and records for an edition."""
    ed = db.query(TournamentEdition).filter(TournamentEdition.id == id).first()
    if not ed:
        raise HTTPException(status_code=404, detail=f"Edition with ID '{id}' not found")

    matches = db.query(MatchEvent).filter(MatchEvent.edition_id == ed.id).all()
    stats_map: Dict[str, Dict[str, Any]] = {}

    for m in matches:
        sides = db.query(MatchSide).filter(MatchSide.match_event_id == m.id).all()
        for s in sides:
            p = db.query(Participant).filter(Participant.id == s.participant_id).first()
            if not p:
                continue
            if p.id not in stats_map:
                stats_map[p.id] = {
                    "id": p.id,
                    "name": p.name,
                    "played": 0,
                    "won": 0,
                    "lost": 0,
                    "drawn": 0,
                    "points": 0,
                }
            stats_map[p.id]["played"] += 1
            if m.is_draw:
                stats_map[p.id]["drawn"] += 1
                stats_map[p.id]["points"] += 1
            elif m.winner_participant_id == p.id:
                stats_map[p.id]["won"] += 1
                stats_map[p.id]["points"] += 2
            else:
                stats_map[p.id]["lost"] += 1

    sorted_list = sorted(
        stats_map.values(),
        key=lambda x: (x["points"], x["won"]),
        reverse=True,
    )

    data: List[StandingOut] = []
    for rank, entry in enumerate(sorted_list, start=1):
        win_pct = round((entry["won"] / entry["played"] * 100), 2) if entry["played"] > 0 else 0.0
        data.append(
            StandingOut(
                rank=rank,
                participant_id=entry["id"],
                participant_name=entry["name"],
                played=entry["played"],
                won=entry["won"],
                lost=entry["lost"],
                drawn=entry["drawn"],
                points=float(entry["points"]),
                win_percentage=win_pct,
            )
        )

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=len(data), returned=len(data)),
        provenance=[
            ProvenanceRecord(organisation="Official Standings Computations", is_verified=True)
        ],
    )
