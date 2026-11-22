"""Source Registry for SportStats.

Manages data source registration, verification status, and provenance records.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from sportstats.db.models import Source


class SourceRegistry:
    """Registry for querying, registering, and verifying data sources."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_organisation(self, org: str) -> Optional[Source]:
        """Lookup source by governing body organisation code (e.g. ICC, FIFA)."""
        return self.db.query(Source).filter(Source.organisation == org).first()

    def get_by_url(self, url: str) -> Optional[Source]:
        """Lookup source by exact or prefix URL."""
        return self.db.query(Source).filter(Source.url == url).first()

    def get_or_create(
        self,
        organisation: str,
        name: str,
        url: str,
        access_method: str = "manual_csv",
        tier: str = "official",
        terms_note: Optional[str] = None,
        is_verified: bool = True,
    ) -> Source:
        """Find existing source by organisation or URL, or create new source record."""
        source = (
            self.db.query(Source)
            .filter((Source.organisation == organisation) | (Source.url == url))
            .first()
        )
        if source:
            return source

        new_source = Source(
            organisation=organisation,
            name=name,
            url=url,
            access_method=access_method,
            tier=tier,
            terms_note=terms_note,
            retrieved_at=datetime.now(timezone.utc),
            is_verified=is_verified,
        )
        self.db.add(new_source)
        self.db.flush()
        return new_source

    def resolve_source(self, source_org: Optional[str], source_url: Optional[str]) -> Source:
        """Resolve the most accurate Source database record from provided metadata."""
        org = (source_org or "").strip()
        url = (source_url or "").strip()

        # Try by organisation first
        if org:
            source = self.get_by_organisation(org)
            if source:
                return source

        # Try by url
        if url:
            source = self.get_by_url(url)
            if source:
                return source

        # Default fallback or new registered source
        fallback_org = org or "Official Source"
        fallback_url = url or "https://sportstats.internal/unspecified"
        return self.get_or_create(
            organisation=fallback_org,
            name=f"{fallback_org} Sports Data Archive",
            url=fallback_url,
            access_method="manual_csv",
            tier="official"
            if org in ["ICC", "FIFA", "IOC", "BWF", "FIBA", "ITF", "AELTC", "NBA"]
            else "secondary",
            terms_note="Auto-registered source during ingestion",
            is_verified=True,
        )
