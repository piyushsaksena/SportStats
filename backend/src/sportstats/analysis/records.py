"""Records and milestones analysis queries (Section 9.3)."""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from sportstats.db.models import (
    MetricDefinition,
    Participant,
    RecordEntry,
    Sport,
    TournamentEdition,
)


def records_and_milestones(
    db: Session,
    sport_code: Optional[str] = None,
    record_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve verified records, world records, and tournament milestones."""
    query = (
        db.query(
            RecordEntry,
            Sport.name.label("sport_name"),
            Sport.code.label("sport_code"),
            Participant.name.label("holder_name"),
            MetricDefinition.name.label("metric_name"),
            MetricDefinition.unit.label("metric_unit"),
            TournamentEdition.edition_label,
            TournamentEdition.year,
        )
        .join(Sport, RecordEntry.sport_id == Sport.id)
        .join(Participant, RecordEntry.holder_participant_id == Participant.id)
        .outerjoin(MetricDefinition, RecordEntry.metric_id == MetricDefinition.id)
        .outerjoin(TournamentEdition, RecordEntry.edition_id == TournamentEdition.id)
    )

    if sport_code:
        query = query.filter(Sport.code == sport_code)
    if record_type:
        query = query.filter(RecordEntry.record_type == record_type)

    rows = query.order_by(RecordEntry.achieved_on.desc().nullslast()).all()

    return [
        {
            "id": r.RecordEntry.id,
            "sport": r.sport_name,
            "sport_code": r.sport_code,
            "record_type": r.RecordEntry.record_type,
            "description": r.RecordEntry.description,
            "holder": r.holder_name,
            "value": float(r.RecordEntry.value) if r.RecordEntry.value is not None else None,
            "unit": r.metric_unit,
            "achieved_on": r.RecordEntry.achieved_on.isoformat()
            if r.RecordEntry.achieved_on
            else None,
            "edition": r.edition_label,
            "year": r.year,
        }
        for r in rows
    ]
