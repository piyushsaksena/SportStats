"""AI Grounded Assistant router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sportstats.ai.assistant import GroundedAnswer, SportStatsAssistant
from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.db.session import get_db

router = APIRouter(prefix="/ai", tags=["AI Analyst Layer"])

assistant = SportStatsAssistant()


class AskRequest(BaseModel):
    """User query request for the AI assistant."""

    question: str = Field(
        ..., min_length=2, max_length=500, description="Natural language sports query"
    )


@router.post("/ask", response_model=ResponseEnvelope[GroundedAnswer])
def ask_assistant_endpoint(
    req: AskRequest,
    db: Session = Depends(get_db),
):
    """Grounded AI query endpoint returning cited numbers, sources, and caveats."""
    res = assistant.ask(req.question, db=db)

    provenance = [
        ProvenanceRecord(
            organisation=s.get("organisation", "Official Federation"),
            url=s.get("url"),
            is_verified=True,
        )
        for s in res.sources
    ]

    return ResponseEnvelope(
        data=res,
        meta=DataMeta(total=len(res.numbers_used), returned=len(res.numbers_used)),
        provenance=provenance,
    )
