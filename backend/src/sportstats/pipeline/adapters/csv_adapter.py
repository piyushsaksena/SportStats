"""CSV Source Adapter for SportStats.

Implements SourceAdapter protocol for structured CSV imports corresponding to Table 2
and Appendix A of the master specification.
"""

import csv
import io
from pathlib import Path
from typing import List, Optional

from sportstats.pipeline.adapters.base import (
    Dataset,
    RawPayload,
    SourceAdapter,
    StagedRecord,
    save_raw_payload,
)


class CSVSourceAdapter(SourceAdapter):
    """Adapter for importing tabular sports data from CSV files."""

    source_code = "csv_manual"

    def __init__(self, raw_storage_dir: Optional[Path] = None):
        self.raw_storage_dir = raw_storage_dir or Path("data/raw")

    def discover(self) -> List[Dataset]:
        """Discover default CSV template types."""
        return [
            Dataset(
                dataset_id="tournament_editions",
                sport_code="multi",
                name="Tournament Editions",
                description="Tournament editions, host cities, dates, format and winners",
                source_org="Official Governing Bodies",
                source_url="https://sportstats.internal/templates/tournament_editions.csv",
                access_method="manual_csv",
                format="csv",
            ),
            Dataset(
                dataset_id="matches",
                sport_code="multi",
                name="Match Events",
                description="Match fixtures, results, scores, stages, and venues",
                source_org="Official Governing Bodies",
                source_url="https://sportstats.internal/templates/matches.csv",
                access_method="manual_csv",
                format="csv",
            ),
            Dataset(
                dataset_id="performance_stats",
                sport_code="multi",
                name="Performance Statistics",
                description="Player and team performance metrics matching the catalogue",
                source_org="Official Governing Bodies",
                source_url="https://sportstats.internal/templates/performance_stats.csv",
                access_method="manual_csv",
                format="csv",
            ),
            Dataset(
                dataset_id="rankings",
                sport_code="multi",
                name="Ranking Snapshots",
                description="Official historical and current participant rankings",
                source_org="Official Governing Bodies",
                source_url="https://sportstats.internal/templates/rankings.csv",
                access_method="manual_csv",
                format="csv",
            ),
            Dataset(
                dataset_id="olympic_results",
                sport_code="olympic",
                name="Olympic Results",
                description="Olympic discipline event results, medals, and record flags",
                source_org="IOC / Olympics.com",
                source_url="https://sportstats.internal/templates/olympic_results.csv",
                access_method="manual_csv",
                format="csv",
            ),
        ]

    def fetch_from_file(self, file_path: Path, dataset: Dataset) -> RawPayload:
        """Store a copy of an input CSV file in data/raw with sidecar metadata (immutable storage)."""
        content = file_path.read_bytes()
        dest_filename = f"{dataset.dataset_id}_{Path(file_path).name}"
        return save_raw_payload(
            content=content,
            filename=dest_filename,
            dataset=dataset,
            destination_dir=self.raw_storage_dir,
            http_status=200,
        )

    def fetch(self, dataset: Dataset, destination_dir: Optional[Path] = None) -> RawPayload:
        """Fetch raw payload from remote URL or local path."""
        target_dir = destination_dir or self.raw_storage_dir
        # If url is a local file
        if dataset.source_url.startswith("file://") or Path(dataset.source_url).exists():
            clean_path = dataset.source_url.replace("file://", "")
            content = Path(clean_path).read_bytes()
            filename = f"{dataset.dataset_id}_{Path(clean_path).name}"
        else:
            # Placeholder for local template/fixture fetch
            content = b""
            filename = f"{dataset.dataset_id}.csv"

        return save_raw_payload(
            content=content,
            filename=filename,
            dataset=dataset,
            destination_dir=target_dir,
        )

    def parse(self, raw: RawPayload) -> List[StagedRecord]:
        """Parse raw CSV payload into StagedRecord items with 1-indexed row numbers."""
        content = raw.payload_path.read_text(encoding="utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        staged: List[StagedRecord] = []

        table_target = raw.dataset_id
        for idx, row in enumerate(reader, start=2):  # line 1 is header
            # Trim whitespace from all keys and values
            cleaned_row = {
                (k.strip() if k else ""): (v.strip() if isinstance(v, str) else v)
                for k, v in row.items()
                if k is not None
            }
            # Remove any empty key that may have been created
            cleaned_row.pop("", None)

            source_url = (
                cleaned_row["source_url"] if "source_url" in cleaned_row else raw.source_url
            )
            retrieved_on = (
                cleaned_row["retrieved_on"] if "retrieved_on" in cleaned_row else raw.retrieved_at
            )
            source_org = (
                cleaned_row["source_org"] if "source_org" in cleaned_row else raw.source_org
            )

            # Quarantine flag detection
            is_sample = str(cleaned_row.get("is_sample", "false")).lower() in ("true", "1", "yes")

            staged.append(
                StagedRecord(
                    table_target=table_target,
                    row_number=idx,
                    data=cleaned_row,
                    source_url=source_url,
                    retrieved_on=retrieved_on,
                    source_org=source_org,
                    is_sample=is_sample,
                )
            )

        return staged
