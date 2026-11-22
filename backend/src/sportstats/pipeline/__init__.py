"""SportStats Ingestion Pipeline and Data Quality Framework.

Provides source adapters, data validation, audit trail logging, and CSV importing.
"""

from sportstats.pipeline.adapters.base import (
    Dataset,
    RawPayload,
    SourceAdapter,
    StagedRecord,
)
from sportstats.pipeline.adapters.csv_adapter import CSVSourceAdapter
from sportstats.pipeline.cleaners import (
    has_formula_injection,
    normalize_country_iso3,
    normalize_participant_name,
    parse_iso_date,
    parse_iso_datetime_utc,
)
from sportstats.pipeline.importer import CSVImporter, IngestionResult
from sportstats.pipeline.registry import SourceRegistry
from sportstats.pipeline.validators import (
    QualityIssue,
    RecordValidator,
    ValidationReport,
)
from sportstats.pipeline.verification import VerificationWorkflow

__all__ = [
    "SourceAdapter",
    "CSVSourceAdapter",
    "Dataset",
    "RawPayload",
    "StagedRecord",
    "SourceRegistry",
    "RecordValidator",
    "ValidationReport",
    "QualityIssue",
    "CSVImporter",
    "IngestionResult",
    "VerificationWorkflow",
    "normalize_country_iso3",
    "normalize_participant_name",
    "parse_iso_date",
    "parse_iso_datetime_utc",
    "has_formula_injection",
]
