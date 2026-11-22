"""Sports and metric catalogue API router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import MetricOut, SportOut
from sportstats.db.models import MetricDefinition, Sport, Tournament
from sportstats.db.session import get_db

router = APIRouter(prefix="/sports", tags=["Sports & Metrics"])


@router.get("", response_model=ResponseEnvelope[List[SportOut]])
def list_sports(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
):
    """Retrieve all tracked sports with tournament and metric catalogue counts."""
    query = db.query(Sport).order_by(Sport.name)
    total = query.count()
    sports = query.offset(offset).limit(limit).all()

    data: List[SportOut] = []
    for s in sports:
        tourn_cnt = db.query(Tournament).filter(Tournament.sport_id == s.id).count()
        metric_cnt = db.query(MetricDefinition).filter(MetricDefinition.sport_id == s.id).count()
        data.append(
            SportOut(
                id=s.id,
                code=s.code,
                name=s.name,
                is_team_sport=s.is_team_sport,
                is_individual_sport=s.is_individual_sport,
                tournament_count=tourn_cnt,
                metric_count=metric_cnt,
                notes=s.notes,
            )
        )

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=total, limit=limit, offset=offset, returned=len(data)),
        provenance=[ProvenanceRecord(organisation="SportStats Core System", is_verified=True)],
    )


@router.get("/{code}/metrics", response_model=ResponseEnvelope[List[MetricOut]])
def get_sport_metrics(
    code: str,
    db: Session = Depends(get_db),
):
    """Retrieve the official metric catalogue for a given sport code."""
    sport = db.query(Sport).filter(Sport.code == code.lower()).first()
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport '{code}' not found")

    metrics = (
        db.query(MetricDefinition)
        .filter(MetricDefinition.sport_id == sport.id)
        .order_by(MetricDefinition.category, MetricDefinition.name)
        .all()
    )

    data = [
        MetricOut(
            id=m.id,
            sport_code=sport.code,
            code=m.code,
            name=m.name,
            unit=m.unit,
            category=m.category,
            aggregation=m.aggregation,
            higher_is_better=m.higher_is_better,
            formula=m.formula,
            description=m.description,
        )
        for m in metrics
    ]

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=len(data), returned=len(data)),
        provenance=[
            ProvenanceRecord(
                organisation="SportStats Metric Catalogue",
                url="docs/DATA_DICTIONARY.md",
                is_verified=True,
            )
        ],
    )
