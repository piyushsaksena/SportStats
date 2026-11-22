"""Tournaments API router."""

from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import TournamentOut
from sportstats.db.models import Participant, Sport, Tournament, TournamentEdition
from sportstats.db.session import get_db

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


@router.get("", response_model=ResponseEnvelope[List[TournamentOut]])
def list_tournaments(
    sport: Annotated[Optional[str], Query(description="Filter by sport code")] = None,
    status: Annotated[
        Optional[str], Query(description="Filter by edition status (upcoming/ongoing/completed)")
    ] = None,
    year: Annotated[Optional[int], Query(description="Filter by year")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
):
    """List tournaments with tracking status and edition summary counts."""
    query = db.query(Tournament)

    if sport:
        sport_obj = db.query(Sport).filter(Sport.code == sport.lower()).first()
        if sport_obj:
            query = query.filter(Tournament.sport_id == sport_obj.id)
        else:
            return ResponseEnvelope(data=[], meta=DataMeta(total=0, returned=0))

    tournaments = query.order_by(Tournament.name).all()
    filtered: List[TournamentOut] = []

    for t in tournaments:
        ed_query = db.query(TournamentEdition).filter(TournamentEdition.tournament_id == t.id)
        if year:
            ed_query = ed_query.filter(TournamentEdition.year == year)
        if status:
            ed_query = ed_query.filter(TournamentEdition.status == status)

        editions = ed_query.order_by(TournamentEdition.year.desc()).all()
        if (year or status) and not editions:
            continue

        sport_rec = db.query(Sport).filter(Sport.id == t.sport_id).first()
        sport_code = sport_rec.code if sport_rec else "multi"

        latest_ed = editions[0].edition_label if editions else None
        latest_status = editions[0].status if editions else "completed"

        filtered.append(
            TournamentOut(
                id=t.id,
                sport_code=sport_code,
                name=t.name,
                governing_body=t.governing_body,
                gender=t.gender,
                level=t.level,
                frequency_years=t.frequency_years,
                edition_count=len(editions),
                latest_edition=latest_ed,
                status=latest_status,
            )
        )

    paginated = filtered[offset : offset + limit]

    return ResponseEnvelope(
        data=paginated,
        meta=DataMeta(total=len(filtered), limit=limit, offset=offset, returned=len(paginated)),
        provenance=[
            ProvenanceRecord(
                organisation="Official Federations",
                is_verified=True,
            )
        ],
    )


@router.get("/{id}", response_model=ResponseEnvelope[Dict[str, Any]])
def get_tournament_detail(
    id: str,
    db: Session = Depends(get_db),
):
    """Retrieve tournament summary including historical winners timeline."""
    t = db.query(Tournament).filter(Tournament.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail=f"Tournament with ID '{id}' not found")

    sport_rec = db.query(Sport).filter(Sport.id == t.sport_id).first()
    sport_code = sport_rec.code if sport_rec else "multi"

    editions = (
        db.query(TournamentEdition)
        .filter(TournamentEdition.tournament_id == t.id)
        .order_by(TournamentEdition.year.desc())
        .all()
    )

    history = []
    for ed in editions:
        winner_p = (
            db.query(Participant).filter(Participant.id == ed.winner_participant_id).first()
            if ed.winner_participant_id
            else None
        )
        runner_up_p = (
            db.query(Participant).filter(Participant.id == ed.runner_up_participant_id).first()
            if ed.runner_up_participant_id
            else None
        )
        history.append(
            {
                "edition_id": ed.id,
                "edition_label": ed.edition_label,
                "year": ed.year,
                "host_city": ed.host_city,
                "winner": winner_p.name if winner_p else None,
                "runner_up": runner_up_p.name if runner_up_p else None,
                "status": ed.status,
            }
        )

    return ResponseEnvelope(
        data={
            "id": t.id,
            "name": t.name,
            "sport_code": sport_code,
            "governing_body": t.governing_body,
            "gender": t.gender,
            "level": t.level,
            "frequency_years": t.frequency_years,
            "notes": t.notes,
            "editions_history": history,
        },
        meta=DataMeta(total=len(history), returned=len(history)),
        provenance=[
            ProvenanceRecord(
                organisation=t.governing_body,
                is_verified=True,
            )
        ],
    )
