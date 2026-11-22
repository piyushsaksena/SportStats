"""Verification Queue and Workflow Management for SportStats.

Implements the verification workflow specified in Section 8.5:
- Tracks sources and records requiring verification
- Maintains pending verification queue
- Manages approval audit trail
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from sportstats.db.models import DataQualityIssue, IngestionRun, Source


class VerificationWorkflow:
    """Manages the verification lifecycle for ingested datasets and records."""

    def __init__(self, db: Session):
        self.db = db

    def requires_verification(self, source: Source) -> bool:
        """Determine if records from this source must be held for review before public exposure."""
        # Non-official sources or unverified sources require review
        if source.tier != "official" or not source.is_verified:
            return True
        return False

    def get_pending_runs(self) -> List[IngestionRun]:
        """Fetch all ingestion runs with status 'partial' or unverified sources."""
        return (
            self.db.query(IngestionRun)
            .join(Source, IngestionRun.source_id == Source.id)
            .filter((Source.is_verified == False) | (IngestionRun.rows_rejected > 0))  # noqa: E712
            .order_by(IngestionRun.started_at.desc())
            .all()
        )

    def get_run_issues(self, run_id: str) -> List[DataQualityIssue]:
        """Fetch all itemized issues for a given ingestion run."""
        return (
            self.db.query(DataQualityIssue)
            .filter(DataQualityIssue.ingestion_run_id == run_id)
            .order_by(DataQualityIssue.created_at.asc())
            .all()
        )

    def approve_source(self, source_id: str, reviewer_name: str) -> bool:
        """Approve a secondary or unverified source, marking it verified."""
        source = self.db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return False

        source.is_verified = True
        note = source.terms_note or ""
        source.terms_note = (
            f"{note} [Verified by {reviewer_name} on {datetime.now(timezone.utc).isoformat()}]"
        )
        self.db.commit()
        return True
