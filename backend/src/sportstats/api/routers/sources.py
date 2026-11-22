"""Data sources registry API router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.api.schemas.models import SourceOut
from sportstats.db.models import Source
from sportstats.db.session import get_db

router = APIRouter(prefix="/sources", tags=["Sources & Governance"])


@router.get("", response_model=ResponseEnvelope[List[SourceOut]])
def list_sources(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
):
    """List all registered official data sources and their verification status."""
    query = db.query(Source).order_by(Source.organisation, Source.name)
    total = query.count()
    sources = query.offset(offset).limit(limit).all()

    data = [
        SourceOut(
            id=s.id,
            organisation=s.organisation,
            name=s.name,
            url=s.url,
            access_method=s.access_method,
            tier=s.tier,
            terms_note=s.terms_note,
            is_verified=s.is_verified,
            retrieved_at=s.retrieved_at,
        )
        for s in sources
    ]

    return ResponseEnvelope(
        data=data,
        meta=DataMeta(total=total, limit=limit, offset=offset, returned=len(data)),
        provenance=[
            ProvenanceRecord(
                organisation="SportStats Source Governance Registry",
                url="docs/SOURCES.md",
                is_verified=True,
            )
        ],
    )
