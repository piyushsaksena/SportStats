"""Generic response envelopes and provenance metadata models for SportStats REST API."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ProvenanceRecord(BaseModel):
    """Provenance tracking envelope indicating source origin for statistics."""

    source_id: Optional[str] = None
    organisation: str = "Official Federation"
    url: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    is_verified: bool = True
    is_sample: bool = False


class DataMeta(BaseModel):
    """Metadata envelope for pagination and summary counts."""

    total: int = 0
    limit: Optional[int] = None
    offset: Optional[int] = None
    returned: int = 0
    extra: Dict[str, Any] = Field(default_factory=dict)


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standardized top-level response envelope for all SportStats API endpoints."""

    data: T
    meta: DataMeta = Field(default_factory=DataMeta)
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
