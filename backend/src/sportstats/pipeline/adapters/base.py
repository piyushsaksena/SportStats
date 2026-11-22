"""Adapter Protocol and Data Structures for SportStats Ingestion Pipeline.

Defines the contract for external and local data source adapters as specified
in Section 8.2 of the Master Specification.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


def utc_now_iso() -> str:
    """Current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Dataset:
    """Description of an ingestible dataset available from a source."""

    dataset_id: str
    sport_code: str
    name: str
    description: str
    source_org: str
    source_url: str
    access_method: str = "manual_csv"  # manual_csv | api | download | scrape
    format: str = "csv"  # csv | json
    tier: str = "official"  # official | secondary
    license_terms: Optional[str] = None
    extra_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RawPayload:
    """Raw payload fetched from a source and persisted to data/raw with sidecar metadata."""

    payload_path: Path
    sidecar_path: Path
    dataset_id: str
    source_org: str
    source_url: str
    retrieved_at: str
    checksum_sha256: str
    http_status: Optional[int] = None
    license_note: Optional[str] = None
    byte_count: int = 0
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_sidecar_dict(self) -> Dict[str, Any]:
        """Convert payload provenance to serializable dictionary."""
        return {
            "dataset_id": self.dataset_id,
            "source_org": self.source_org,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "checksum_sha256": self.checksum_sha256,
            "http_status": self.http_status,
            "license_note": self.license_note,
            "byte_count": self.byte_count,
            "extra_metadata": self.extra_metadata,
        }


@dataclass
class StagedRecord:
    """Single parsed record ready for cleaning and validation."""

    table_target: (
        str  # tournament_edition | match_event | performance_stat | ranking | olympic_result
    )
    row_number: int
    data: Dict[str, Any]
    source_url: str
    retrieved_on: str
    source_org: str = "UNKNOWN"
    is_sample: bool = False


@runtime_checkable
class SourceAdapter(Protocol):
    """Adapter contract for all SportStats data providers."""

    source_code: str

    def discover(self) -> List[Dataset]:
        """Discover available datasets from this provider."""
        ...

    def fetch(self, dataset: Dataset, destination_dir: Optional[Path] = None) -> RawPayload:
        """Fetch raw payload, persist to data/raw with sidecar JSON metadata, and return payload metadata."""
        ...

    def parse(self, raw: RawPayload) -> List[StagedRecord]:
        """Parse raw payload into staged records for validation and ingestion."""
        ...


def calculate_sha256(content: bytes) -> str:
    """Calculate SHA256 checksum for byte sequence."""
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()


def save_raw_payload(
    content: bytes,
    filename: str,
    dataset: Dataset,
    destination_dir: Path,
    http_status: Optional[int] = 200,
) -> RawPayload:
    """Save raw byte content and JSON sidecar metadata to target directory (immutable storage)."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    payload_file = destination_dir / filename
    sidecar_file = destination_dir / f"{filename}.meta.json"

    checksum = calculate_sha256(content)
    retrieved_at = utc_now_iso()

    # Write payload file
    with open(payload_file, "wb") as f:
        f.write(content)

    payload = RawPayload(
        payload_path=payload_file,
        sidecar_path=sidecar_file,
        dataset_id=dataset.dataset_id,
        source_org=dataset.source_org,
        source_url=dataset.source_url,
        retrieved_at=retrieved_at,
        checksum_sha256=checksum,
        http_status=http_status,
        license_note=dataset.license_terms,
        byte_count=len(content),
        extra_metadata=dataset.extra_metadata,
    )

    # Write sidecar JSON metadata
    with open(sidecar_file, "w", encoding="utf-8") as f:
        json.dump(payload.to_sidecar_dict(), f, indent=2)

    return payload
