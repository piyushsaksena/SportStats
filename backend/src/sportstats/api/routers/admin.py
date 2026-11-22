"""Admin API router for CSV dataset ingestion and data quality auditing."""

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from sportstats.api.schemas.envelope import DataMeta, ProvenanceRecord, ResponseEnvelope
from sportstats.config import settings
from sportstats.db.session import get_db
from sportstats.pipeline.importer import CSVImporter

router = APIRouter(prefix="/admin", tags=["Admin & Ingestion"])


def verify_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")):
    """Verify administrator authorization key."""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin authorization key")
    return x_admin_key


@router.post("/import/dry-run", response_model=ResponseEnvelope[Dict[str, Any]])
def admin_import_dry_run(
    dataset_type: str = Form(
        ...,
        description="tournament_editions, matches, performance_stats, rankings, olympic_results",
    ),
    file: UploadFile = File(...),
    admin_key: str = Depends(verify_admin_key),
    db: Session = Depends(get_db),
):
    """Simulate CSV import without mutating the database, returning itemized rejections."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        importer = CSVImporter(db)
        result = importer.import_csv(tmp_path, dataset_type=dataset_type, dry_run=True)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return ResponseEnvelope(
        data={
            "run_id": result.run_id,
            "status": result.status,
            "rows_in": result.rows_in,
            "rows_loaded": result.rows_loaded,
            "rows_rejected": result.rows_rejected,
            "issues": result.issues,
            "log_summary": result.log_summary,
        },
        meta=DataMeta(total=result.rows_in, returned=result.rows_loaded),
        provenance=[
            ProvenanceRecord(organisation="SportStats Pipeline Audit Engine", is_verified=True)
        ],
    )


@router.post("/import/commit", response_model=ResponseEnvelope[Dict[str, Any]])
def admin_import_commit(
    dataset_type: str = Form(
        ...,
        description="tournament_editions, matches, performance_stats, rankings, olympic_results",
    ),
    file: UploadFile = File(...),
    admin_key: str = Depends(verify_admin_key),
    db: Session = Depends(get_db),
):
    """Commit verified CSV import to the database with audit provenance logging."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        importer = CSVImporter(db)
        result = importer.import_csv(tmp_path, dataset_type=dataset_type, dry_run=False)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return ResponseEnvelope(
        data={
            "run_id": result.run_id,
            "status": result.status,
            "rows_in": result.rows_in,
            "rows_loaded": result.rows_loaded,
            "rows_rejected": result.rows_rejected,
            "issues": result.issues,
            "log_summary": result.log_summary,
        },
        meta=DataMeta(total=result.rows_in, returned=result.rows_loaded),
        provenance=[
            ProvenanceRecord(organisation="SportStats Pipeline Audit Engine", is_verified=True)
        ],
    )
