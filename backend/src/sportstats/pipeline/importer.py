"""CSV Ingestion Engine for SportStats.

Coordinates data parsing, cleaning, validation, audit logging to IngestionRun
and DataQualityIssue, and database insertion with immutable raw file guarantees.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from sportstats.db.models import (
    Country,
    DataQualityIssue,
    Discipline,
    IngestionRun,
    MatchEvent,
    MatchSide,
    MetricDefinition,
    OlympicResult,
    Participant,
    PerformanceStat,
    PlayerProfile,
    RankingEntry,
    RankingSnapshot,
    Sport,
    Stage,
    TeamProfile,
    Tournament,
    TournamentEdition,
)
from sportstats.pipeline.adapters.base import Dataset, StagedRecord
from sportstats.pipeline.adapters.csv_adapter import CSVSourceAdapter
from sportstats.pipeline.cleaners import (
    normalize_participant_name,
)
from sportstats.pipeline.registry import SourceRegistry
from sportstats.pipeline.validators import RecordValidator, ValidationReport


@dataclass
class IngestionResult:
    """Summary of an ingestion run."""

    run_id: str
    status: str  # success | partial | failed | dry_run_ok | dry_run_rejected
    rows_in: int
    rows_loaded: int
    rows_rejected: int
    dry_run: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    log_summary: str = ""


class CSVImporter:
    """Engine for ingesting CSV datasets into SportStats normalized tables."""

    def __init__(self, db: Session, raw_storage_dir: Optional[Path] = None):
        self.db = db
        self.raw_storage_dir = raw_storage_dir or Path("data/raw")
        self.source_registry = SourceRegistry(db)
        self.validator = RecordValidator(db)
        self.adapter = CSVSourceAdapter(raw_storage_dir=self.raw_storage_dir)

    # -------------------------------------------------------------------------
    # Participant & Reference Resolution Helpers
    # -------------------------------------------------------------------------

    def _get_country_by_iso3(self, iso3: Optional[str]) -> Optional[Country]:
        if not iso3:
            return None
        return self.db.query(Country).filter(Country.iso3 == iso3.upper()).first()

    def _get_or_create_participant(
        self,
        name: str,
        sport_id: str,
        part_type: str = "team",
        country_id: Optional[str] = None,
        is_sample: bool = False,
    ) -> Participant:
        """Find participant by normalized name and sport, or create new participant record."""
        norm_name = normalize_participant_name(name) or name.strip()
        part = (
            self.db.query(Participant)
            .filter(
                and_(
                    Participant.name == norm_name,
                    Participant.sport_id == sport_id,
                )
            )
            .first()
        )
        if part:
            return part

        new_part = Participant(
            name=norm_name,
            type=part_type,
            sport_id=sport_id,
            country_id=country_id,
            is_sample=is_sample,
        )
        self.db.add(new_part)
        self.db.flush()

        # Add profile
        if part_type in ("team", "national"):
            profile = TeamProfile(
                participant_id=new_part.id,
                team_type="national" if country_id else "club",
            )
            self.db.add(profile)
        else:
            profile = PlayerProfile(
                participant_id=new_part.id,
                full_name=norm_name,
            )
            self.db.add(profile)
        self.db.flush()
        return new_part

    def _get_or_create_tournament(
        self,
        sport_id: str,
        name: str,
        governing_body: str = "Official",
        gender: str = "men",
        level: str = "world",
    ) -> Tournament:
        """Find or create a tournament header record."""
        tourn = (
            self.db.query(Tournament)
            .filter(
                and_(
                    Tournament.sport_id == sport_id,
                    Tournament.name == name.strip(),
                )
            )
            .first()
        )
        if tourn:
            return tourn

        new_tourn = Tournament(
            sport_id=sport_id,
            name=name.strip(),
            governing_body=governing_body.strip(),
            gender=gender,
            level=level,
        )
        self.db.add(new_tourn)
        self.db.flush()
        return new_tourn

    def _get_or_create_stage(self, edition_id: str, stage_name: str) -> Stage:
        """Find or create a tournament stage."""
        clean_name = (stage_name or "Main Stage").strip()
        stage = (
            self.db.query(Stage)
            .filter(and_(Stage.edition_id == edition_id, Stage.name == clean_name))
            .first()
        )
        if stage:
            return stage

        stage_type = "knockout"
        name_lower = clean_name.lower()
        if "group" in name_lower:
            stage_type = "group"
        elif "league" in name_lower or "round-robin" in name_lower:
            stage_type = "league"
        elif "final" in name_lower:
            stage_type = "final"
        elif "heat" in name_lower:
            stage_type = "heat"

        new_stage = Stage(
            edition_id=edition_id,
            name=clean_name,
            type=stage_type,
            order_index=1,
        )
        self.db.add(new_stage)
        self.db.flush()
        return new_stage

    # -------------------------------------------------------------------------
    # Core Import Runners per Target Type
    # -------------------------------------------------------------------------

    def import_csv(
        self,
        file_path: Path,
        dataset_type: str,
        dry_run: bool = False,
    ) -> IngestionResult:
        """Main entry point to import a CSV file into the database."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        # Ensure raw file copy with sidecar exists (preserving input file immutability)
        dataset = Dataset(
            dataset_id=dataset_type,
            sport_code="multi",
            name=f"Import of {path.name}",
            description=f"CSV import from {path.name}",
            source_org="CSV Import",
            source_url=f"file://{path.resolve()}",
            access_method="manual_csv",
        )

        raw_payload = self.adapter.fetch_from_file(path, dataset)
        staged_records = self.adapter.parse(raw_payload)

        # Create IngestionRun record
        started_at = datetime.now(timezone.utc)
        resolved_source = self.source_registry.resolve_source(
            source_org=dataset.source_org,
            source_url=raw_payload.source_url,
        )

        run = IngestionRun(
            source_id=resolved_source.id,
            started_at=started_at,
            status="running",
            rows_in=len(staged_records),
            rows_loaded=0,
            rows_rejected=0,
        )
        if not dry_run:
            self.db.add(run)
            self.db.flush()

        loaded_count = 0
        rejected_count = 0
        collected_issues: List[Dict[str, Any]] = []

        # Process records based on target dataset type
        for record in staged_records:
            validation_report = self._validate_record(record, dataset_type)
            if not validation_report.is_valid:
                rejected_count += 1
                for issue in validation_report.issues:
                    issue_dict = {
                        "table_name": issue.table_name,
                        "row_ref": issue.row_ref,
                        "severity": issue.severity,
                        "rule_code": issue.rule_code,
                        "message": issue.message,
                    }
                    collected_issues.append(issue_dict)
                    if not dry_run:
                        db_issue = DataQualityIssue(
                            ingestion_run_id=run.id,
                            table_name=issue.table_name,
                            row_ref=issue.row_ref,
                            severity=issue.severity,
                            rule_code=issue.rule_code,
                            message=issue.message,
                        )
                        self.db.add(db_issue)
                continue

            # Valid record
            if not dry_run:
                try:
                    self._persist_record(
                        record=record,
                        dataset_type=dataset_type,
                        cleaned_data=validation_report.cleaned_data,
                        default_source_id=resolved_source.id,
                    )
                    loaded_count += 1
                except Exception as e:
                    self.db.rollback()
                    rejected_count += 1
                    err_issue = {
                        "table_name": record.table_target,
                        "row_ref": f"row_{record.row_number}",
                        "severity": "critical",
                        "rule_code": "DB_PERSISTENCE_ERROR",
                        "message": str(e),
                    }
                    collected_issues.append(err_issue)
                    if not dry_run:
                        # Re-add run since rollback wiped it
                        self.db.add(run)
                        db_issue = DataQualityIssue(
                            ingestion_run_id=run.id,
                            table_name=record.table_target,
                            row_ref=f"row_{record.row_number}",
                            severity="critical",
                            rule_code="DB_PERSISTENCE_ERROR",
                            message=str(e),
                        )
                        self.db.add(db_issue)
            else:
                loaded_count += 1

        # Finalize run status
        if dry_run:
            status = "dry_run_ok" if rejected_count == 0 else "dry_run_rejected"
            summary_log = f"Dry-run completed. Total: {len(staged_records)}, Valid: {loaded_count}, Rejected: {rejected_count}"
            return IngestionResult(
                run_id="dry-run",
                status=status,
                rows_in=len(staged_records),
                rows_loaded=loaded_count,
                rows_rejected=rejected_count,
                dry_run=True,
                issues=collected_issues,
                log_summary=summary_log,
            )

        run.rows_loaded = loaded_count
        run.rows_rejected = rejected_count
        run.finished_at = datetime.now(timezone.utc)
        if rejected_count == 0:
            run.status = "success"
        elif loaded_count > 0:
            run.status = "partial"
        else:
            run.status = "failed"

        summary_log = f"Run {run.id}: In={len(staged_records)}, Loaded={loaded_count}, Rejected={rejected_count}, Status={run.status}"
        run.log = summary_log
        self.db.commit()

        return IngestionResult(
            run_id=run.id,
            status=run.status,
            rows_in=len(staged_records),
            rows_loaded=loaded_count,
            rows_rejected=rejected_count,
            dry_run=False,
            issues=collected_issues,
            log_summary=summary_log,
        )

    def _validate_record(self, record: StagedRecord, dataset_type: str) -> ValidationReport:
        """Route record to corresponding validator."""
        if dataset_type == "tournament_editions":
            return self.validator.validate_tournament_edition(record)
        elif dataset_type == "matches":
            return self.validator.validate_match(record)
        elif dataset_type == "performance_stats":
            return self.validator.validate_performance_stat(record)
        elif dataset_type == "rankings":
            return self.validator.validate_ranking(record)
        elif dataset_type == "olympic_results":
            return self.validator.validate_olympic_result(record)
        else:
            rep = ValidationReport()
            rep.add_error(
                table_name=dataset_type,
                row_ref=f"row_{record.row_number}",
                rule_code="UNKNOWN_DATASET_TYPE",
                message=f"Dataset type '{dataset_type}' is not recognized",
            )
            return rep

    def _persist_record(
        self,
        record: StagedRecord,
        dataset_type: str,
        cleaned_data: Dict[str, Any],
        default_source_id: str,
    ) -> None:
        """Persist cleaned staged record into the database."""
        # Resolve record-specific source if provided in row
        row_source_org = record.data.get("source_org") or record.source_org
        row_source_url = record.data.get("source_url") or record.source_url
        source = self.source_registry.resolve_source(row_source_org, row_source_url)
        source_id = source.id if source else default_source_id

        if dataset_type == "tournament_editions":
            self._persist_tournament_edition(record, cleaned_data, source_id)
        elif dataset_type == "matches":
            self._persist_match(record, cleaned_data, source_id)
        elif dataset_type == "performance_stats":
            self._persist_performance_stat(record, cleaned_data, source_id)
        elif dataset_type == "rankings":
            self._persist_ranking(record, cleaned_data, source_id)
        elif dataset_type == "olympic_results":
            self._persist_olympic_result(record, cleaned_data, source_id)

    # -------------------------------------------------------------------------
    # Target-Specific Entity Persistence
    # -------------------------------------------------------------------------

    def _persist_tournament_edition(
        self, record: StagedRecord, data: Dict[str, Any], source_id: str
    ) -> None:
        sport = self.db.query(Sport).filter(Sport.code == data["sport_code"]).first()
        if not sport:
            raise ValueError(f"Sport {data['sport_code']} not found")

        tourn = self._get_or_create_tournament(
            sport_id=sport.id,
            name=data["tournament_name"],
            governing_body=data.get("governing_body") or "Official",
        )

        host_country = self._get_country_by_iso3(data.get("host_country_iso3"))
        host_country_id = host_country.id if host_country else None

        part_type = "team" if sport.is_team_sport else "player"

        winner_id = None
        if data.get("winner"):
            winner_part = self._get_or_create_participant(
                name=data["winner"],
                sport_id=sport.id,
                part_type=part_type,
                is_sample=record.is_sample,
            )
            winner_id = winner_part.id

        runner_up_id = None
        if data.get("runner_up"):
            runner_up_part = self._get_or_create_participant(
                name=data["runner_up"],
                sport_id=sport.id,
                part_type=part_type,
                is_sample=record.is_sample,
            )
            runner_up_id = runner_up_part.id

        # Determine status
        start_date = data["start_date"]
        end_date = data["end_date"]
        today = datetime.now(timezone.utc).date()
        if end_date < today:
            status = "completed"
        elif start_date <= today <= end_date:
            status = "ongoing"
        else:
            status = "upcoming"

        edition_label = str(data["edition_label"]).strip()

        # Check existing edition (idempotent de-duplication)
        edition = (
            self.db.query(TournamentEdition)
            .filter(
                and_(
                    TournamentEdition.tournament_id == tourn.id,
                    TournamentEdition.edition_label == edition_label,
                )
            )
            .first()
        )

        if not edition:
            edition = TournamentEdition(
                tournament_id=tourn.id,
                edition_label=edition_label,
                year=int(data.get("year") or start_date.year),
                host_country_id=host_country_id,
                host_city=data.get("host_city"),
                start_date=start_date,
                end_date=end_date,
                status=status,
                participant_count=int(data.get("participant_count") or 0),
                format_description=data.get("format_description"),
                matches_or_events_count=int(data.get("matches_or_events_count"))
                if data.get("matches_or_events_count")
                else None,
                winner_participant_id=winner_id,
                runner_up_participant_id=runner_up_id,
                source_id=source_id,
                is_sample=record.is_sample,
            )
            self.db.add(edition)
        else:
            # Update existing
            edition.year = int(data.get("year") or start_date.year)
            edition.host_country_id = host_country_id
            edition.host_city = data.get("host_city")
            edition.start_date = start_date
            edition.end_date = end_date
            edition.status = status
            edition.participant_count = int(
                data.get("participant_count") or edition.participant_count
            )
            edition.format_description = (
                data.get("format_description") or edition.format_description
            )
            if data.get("matches_or_events_count"):
                edition.matches_or_events_count = int(data.get("matches_or_events_count"))
            edition.winner_participant_id = winner_id or edition.winner_participant_id
            edition.runner_up_participant_id = runner_up_id or edition.runner_up_participant_id
            edition.source_id = source_id
            edition.is_sample = record.is_sample

        self.db.flush()

    def _persist_match(self, record: StagedRecord, data: Dict[str, Any], source_id: str) -> None:
        sport = self.db.query(Sport).filter(Sport.code == data["sport_code"]).first()
        if not sport:
            raise ValueError(f"Sport {data['sport_code']} not found")

        tourn = self._get_or_create_tournament(
            sport_id=sport.id,
            name=data["tournament_name"],
        )

        edition = (
            self.db.query(TournamentEdition)
            .filter(
                and_(
                    TournamentEdition.tournament_id == tourn.id,
                    TournamentEdition.edition_label == str(data["edition_label"]).strip(),
                )
            )
            .first()
        )
        if not edition:
            # Create edition header if not present
            match_date = data["match_date_utc"].date()
            edition = TournamentEdition(
                tournament_id=tourn.id,
                edition_label=str(data["edition_label"]).strip(),
                year=match_date.year,
                start_date=match_date,
                end_date=match_date,
                status="completed",
                source_id=source_id,
                is_sample=record.is_sample,
            )
            self.db.add(edition)
            self.db.flush()

        stage = self._get_or_create_stage(edition.id, data.get("stage") or "Regular")

        part_type = "team" if sport.is_team_sport else "player"
        part_a = self._get_or_create_participant(
            name=data["participant_a"],
            sport_id=sport.id,
            part_type=part_type,
            is_sample=record.is_sample,
        )
        part_b = self._get_or_create_participant(
            name=data["participant_b"],
            sport_id=sport.id,
            part_type=part_type,
            is_sample=record.is_sample,
        )

        winner_id = None
        if data.get("winner"):
            winner_clean = normalize_participant_name(data["winner"])
            if winner_clean == part_a.name:
                winner_id = part_a.id
            elif winner_clean == part_b.name:
                winner_id = part_b.id

        match_event = MatchEvent(
            edition_id=edition.id,
            stage_id=stage.id,
            sport_id=sport.id,
            scheduled_at=data["match_date_utc"],
            status="completed",
            winner_participant_id=winner_id,
            is_draw=data["is_draw"],
            result_summary=data.get("result_summary"),
            source_id=source_id,
            is_sample=record.is_sample,
        )
        self.db.add(match_event)
        self.db.flush()

        # Sides
        score_a = (
            float(data["score_a"])
            if data.get("score_a") is not None and str(data["score_a"]).strip() != ""
            else None
        )
        score_b = (
            float(data["score_b"])
            if data.get("score_b") is not None and str(data["score_b"]).strip() != ""
            else None
        )

        side_a = MatchSide(
            match_event_id=match_event.id,
            participant_id=part_a.id,
            side_index=0,
            score_primary=score_a,
            is_winner=(winner_id == part_a.id) if winner_id else None,
        )
        side_b = MatchSide(
            match_event_id=match_event.id,
            participant_id=part_b.id,
            side_index=1,
            score_primary=score_b,
            is_winner=(winner_id == part_b.id) if winner_id else None,
        )
        self.db.add_all([side_a, side_b])
        self.db.flush()

    def _persist_performance_stat(
        self, record: StagedRecord, data: Dict[str, Any], source_id: str
    ) -> None:
        sport = self.db.query(Sport).filter(Sport.code == data["sport_code"]).first()
        if not sport:
            raise ValueError(f"Sport {data['sport_code']} not found")

        metric = (
            self.db.query(MetricDefinition)
            .filter(
                and_(
                    MetricDefinition.sport_id == sport.id,
                    MetricDefinition.code == data["metric_code"],
                )
            )
            .first()
        )
        if not metric:
            raise ValueError(f"Metric {data['metric_code']} not found for {sport.code}")

        tourn = self._get_or_create_tournament(
            sport_id=sport.id,
            name=data["tournament_name"],
        )

        edition = (
            self.db.query(TournamentEdition)
            .filter(
                and_(
                    TournamentEdition.tournament_id == tourn.id,
                    TournamentEdition.edition_label == str(data["edition_label"]).strip(),
                )
            )
            .first()
        )
        if not edition:
            today = datetime.now(timezone.utc).date()
            edition = TournamentEdition(
                tournament_id=tourn.id,
                edition_label=str(data["edition_label"]).strip(),
                year=today.year,
                start_date=today,
                end_date=today,
                source_id=source_id,
                is_sample=record.is_sample,
            )
            self.db.add(edition)
            self.db.flush()

        part_type = "team" if sport.is_team_sport else "player"
        part = self._get_or_create_participant(
            name=data["participant"],
            sport_id=sport.id,
            part_type=part_type,
            is_sample=record.is_sample,
        )

        stat = PerformanceStat(
            participant_id=part.id,
            edition_id=edition.id,
            metric_id=metric.id,
            value=data["value"],
            scope=data["scope"],
            source_id=source_id,
            is_sample=record.is_sample,
        )
        self.db.add(stat)
        self.db.flush()

    def _persist_ranking(self, record: StagedRecord, data: Dict[str, Any], source_id: str) -> None:
        sport = self.db.query(Sport).filter(Sport.code == data["sport_code"]).first()
        if not sport:
            raise ValueError(f"Sport {data['sport_code']} not found")

        ranking_system = str(data.get("ranking_system") or "Official World Ranking").strip()
        category = str(data.get("category") or "General").strip()
        as_of_date = data["as_of_date"]

        snapshot = (
            self.db.query(RankingSnapshot)
            .filter(
                and_(
                    RankingSnapshot.sport_id == sport.id,
                    RankingSnapshot.ranking_system == ranking_system,
                    RankingSnapshot.as_of_date == as_of_date,
                )
            )
            .first()
        )
        if not snapshot:
            snapshot = RankingSnapshot(
                sport_id=sport.id,
                ranking_system=ranking_system,
                category=category,
                as_of_date=as_of_date,
                source_id=source_id,
            )
            self.db.add(snapshot)
            self.db.flush()

        part_type = "team" if sport.is_team_sport else "player"
        part = self._get_or_create_participant(
            name=data["participant"],
            sport_id=sport.id,
            part_type=part_type,
            is_sample=record.is_sample,
        )

        points = (
            float(data["points"])
            if data.get("points") is not None and str(data["points"]).strip() != ""
            else None
        )

        entry = RankingEntry(
            snapshot_id=snapshot.id,
            participant_id=part.id,
            rank=int(data["rank"]),
            points=points,
        )
        self.db.add(entry)
        self.db.flush()

    def _persist_olympic_result(
        self, record: StagedRecord, data: Dict[str, Any], source_id: str
    ) -> None:
        olympic_sport = self.db.query(Sport).filter(Sport.code == "olympic").first()
        if not olympic_sport:
            raise ValueError("Olympic sport not found")

        discipline = (
            self.db.query(Discipline)
            .filter(
                and_(
                    Discipline.sport_id == olympic_sport.id,
                    Discipline.code == str(data["discipline"]).strip().lower(),
                )
            )
            .first()
        )
        if not discipline:
            # Fallback by discipline name or create
            discipline = (
                self.db.query(Discipline).filter(Discipline.sport_id == olympic_sport.id).first()
            )

        tourn = self._get_or_create_tournament(
            sport_id=olympic_sport.id,
            name="Olympic Games",
            governing_body="IOC",
            level="multi_sport",
        )

        edition = (
            self.db.query(TournamentEdition)
            .filter(
                and_(
                    TournamentEdition.tournament_id == tourn.id,
                    TournamentEdition.edition_label == str(data["edition_label"]).strip(),
                )
            )
            .first()
        )
        if not edition:
            today = datetime.now(timezone.utc).date()
            edition = TournamentEdition(
                tournament_id=tourn.id,
                edition_label=str(data["edition_label"]).strip(),
                year=today.year,
                start_date=today,
                end_date=today,
                source_id=source_id,
                is_sample=record.is_sample,
            )
            self.db.add(edition)
            self.db.flush()

        country = self._get_country_by_iso3(data.get("country_iso3"))
        country_id = country.id if country else None

        athlete = self._get_or_create_participant(
            name=data["participant"],
            sport_id=olympic_sport.id,
            part_type="athlete",
            country_id=country_id,
            is_sample=record.is_sample,
        )

        rank_val = (
            int(data["rank"])
            if data.get("rank") is not None and str(data["rank"]).strip() != ""
            else None
        )
        res_val = (
            float(data["result_value"])
            if data.get("result_value") is not None and str(data["result_value"]).strip() != ""
            else None
        )

        olympic_res = OlympicResult(
            edition_id=edition.id,
            discipline_id=discipline.id,
            event_name=data["event_name"].strip(),
            participant_id=athlete.id,
            rank=rank_val,
            medal=data.get("medal"),
            result_value=res_val,
            result_unit=data.get("result_unit"),
            is_world_record=data["is_world_record"],
            is_olympic_record=data["is_olympic_record"],
        )
        self.db.add(olympic_res)
        self.db.flush()
