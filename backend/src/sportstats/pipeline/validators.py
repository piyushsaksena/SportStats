"""Validation Engine and Quality Rule Definitions for SportStats.

Validates staged records against domain constraints and generates itemized
DataQualityIssue records as required by Section 6.7, 8.4, and Appendix B.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from sqlalchemy.orm import Session

from sportstats.db.models import Country, MetricDefinition, Sport
from sportstats.pipeline.adapters.base import StagedRecord
from sportstats.pipeline.cleaners import (
    has_formula_injection,
    normalize_country_iso3,
    parse_iso_date,
    parse_iso_datetime_utc,
)


@dataclass
class QualityIssue:
    """Itemized data quality rejection or warning."""

    table_name: str
    row_ref: str
    severity: str  # error | warning | critical
    rule_code: str
    message: str


@dataclass
class ValidationReport:
    """Aggregated validation report for a staged record or dataset."""

    is_valid: bool = True
    issues: List[QualityIssue] = field(default_factory=list)
    cleaned_data: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, table_name: str, row_ref: str, rule_code: str, message: str) -> None:
        self.is_valid = False
        self.issues.append(
            QualityIssue(
                table_name=table_name,
                row_ref=row_ref,
                severity="error",
                rule_code=rule_code,
                message=message,
            )
        )

    def add_warning(self, table_name: str, row_ref: str, rule_code: str, message: str) -> None:
        self.issues.append(
            QualityIssue(
                table_name=table_name,
                row_ref=row_ref,
                severity="warning",
                rule_code=rule_code,
                message=message,
            )
        )


class RecordValidator:
    """Validates staged records against database catalogue, ranges, and consistency constraints."""

    def __init__(self, db: Session):
        self.db = db
        self._load_cache()

    def _load_cache(self) -> None:
        """Cache reference entities for fast validation lookups."""
        self.sports: Set[str] = {s.code for s in self.db.query(Sport.code).all()}
        self.countries: Set[str] = {c.iso3 for c in self.db.query(Country.iso3).all()}
        # Map sport_code -> set of metric_codes
        metrics = (
            self.db.query(Sport.code, MetricDefinition.code)
            .join(MetricDefinition, MetricDefinition.sport_id == Sport.id)
            .all()
        )
        self.sport_metrics: Dict[str, Set[str]] = {}
        for s_code, m_code in metrics:
            self.sport_metrics.setdefault(s_code, set()).add(m_code)

    def check_formula_injection(
        self, data: Dict[str, Any], table_name: str, row_ref: str, report: ValidationReport
    ) -> None:
        """Scan all string values for formula injection characters."""
        for field_name, value in data.items():
            if isinstance(value, str) and has_formula_injection(value):
                report.add_error(
                    table_name=table_name,
                    row_ref=f"{row_ref}:{field_name}",
                    rule_code="FORMULA_INJECTION",
                    message=f"Potentially unsafe formula character detected at start of field '{field_name}': {value[:10]}",
                )

    def check_mandatory_provenance(self, record: StagedRecord, report: ValidationReport) -> None:
        """Verify presence of source_url and retrieved_on."""
        row_ref = f"row_{record.row_number}"
        if not record.source_url or not str(record.source_url).strip():
            report.add_error(
                table_name=record.table_target,
                row_ref=row_ref,
                rule_code="MISSING_SOURCE",
                message="Mandatory column 'source_url' is missing or empty",
            )
        if not record.retrieved_on or not str(record.retrieved_on).strip():
            report.add_error(
                table_name=record.table_target,
                row_ref=row_ref,
                rule_code="MISSING_SOURCE",
                message="Mandatory column 'retrieved_on' is missing or empty",
            )

    def validate_tournament_edition(self, record: StagedRecord) -> ValidationReport:
        """Validate a tournament_editions staged record."""
        report = ValidationReport()
        row_ref = f"row_{record.row_number}"
        data = record.data

        self.check_formula_injection(data, "tournament_edition", row_ref, report)
        self.check_mandatory_provenance(record, report)

        # 1. Sport code
        sport_code = data.get("sport_code")
        if not sport_code or sport_code not in self.sports:
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="UNKNOWN_SPORT",
                message=f"Unknown sport_code '{sport_code}'. Must match seeded sports.",
            )

        # 2. Tournament Name & Edition Label
        if not data.get("tournament_name"):
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="MISSING_FIELD",
                message="Mandatory field 'tournament_name' is missing",
            )
        if not data.get("edition_label"):
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="MISSING_FIELD",
                message="Mandatory field 'edition_label' is missing",
            )

        # 3. Dates
        start_date = parse_iso_date(data.get("start_date"))
        end_date = parse_iso_date(data.get("end_date"))
        if not start_date:
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="INVALID_DATE",
                message=f"Invalid or unparseable 'start_date': {data.get('start_date')}",
            )
        if not end_date:
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="INVALID_DATE",
                message=f"Invalid or unparseable 'end_date': {data.get('end_date')}",
            )
        if start_date and end_date and end_date < start_date:
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="INVALID_DATE_ORDER",
                message=f"Edition end_date ({end_date}) cannot be earlier than start_date ({start_date})",
            )

        # 4. Host Country ISO3
        raw_country = data.get("host_country_iso3") or data.get("host_country")
        country_iso3 = normalize_country_iso3(raw_country) if raw_country else None
        if raw_country and not country_iso3:
            report.add_error(
                table_name="tournament_edition",
                row_ref=row_ref,
                rule_code="INVALID_COUNTRY",
                message=f"Host country '{raw_country}' could not be resolved to a valid ISO3 country code",
            )

        # 5. Non-negative counts
        for count_field in ("participant_count", "matches_or_events_count", "year"):
            val = data.get(count_field)
            if val is not None and str(val).strip() != "":
                try:
                    num = int(val)
                    if num < 0:
                        report.add_error(
                            table_name="tournament_edition",
                            row_ref=row_ref,
                            rule_code="NEGATIVE_COUNT",
                            message=f"Field '{count_field}' must be non-negative, got {num}",
                        )
                except ValueError:
                    report.add_error(
                        table_name="tournament_edition",
                        row_ref=row_ref,
                        rule_code="INVALID_NUMBER",
                        message=f"Field '{count_field}' must be an integer, got {val}",
                    )

        report.cleaned_data = {
            **data,
            "start_date": start_date,
            "end_date": end_date,
            "host_country_iso3": country_iso3,
        }
        return report

    def validate_match(self, record: StagedRecord) -> ValidationReport:
        """Validate a matches staged record."""
        report = ValidationReport()
        row_ref = f"row_{record.row_number}"
        data = record.data

        self.check_formula_injection(data, "match_event", row_ref, report)
        self.check_mandatory_provenance(record, report)

        # Sport code
        sport_code = data.get("sport_code")
        if not sport_code or sport_code not in self.sports:
            report.add_error(
                table_name="match_event",
                row_ref=row_ref,
                rule_code="UNKNOWN_SPORT",
                message=f"Unknown sport_code '{sport_code}'",
            )

        # Tournament & Edition
        if not data.get("tournament_name") or not data.get("edition_label"):
            report.add_error(
                table_name="match_event",
                row_ref=row_ref,
                rule_code="MISSING_FIELD",
                message="Fields 'tournament_name' and 'edition_label' are required to link match to edition",
            )

        # Participants
        part_a = data.get("participant_a")
        part_b = data.get("participant_b")
        if not part_a or not part_b:
            report.add_error(
                table_name="match_event",
                row_ref=row_ref,
                rule_code="MISSING_PARTICIPANT",
                message="Both 'participant_a' and 'participant_b' must be specified for a match event",
            )

        # Match Date
        match_date = parse_iso_datetime_utc(data.get("match_date_utc") or data.get("match_date"))
        if not match_date:
            report.add_error(
                table_name="match_event",
                row_ref=row_ref,
                rule_code="INVALID_DATE",
                message=f"Invalid match datetime: {data.get('match_date_utc') or data.get('match_date')}",
            )

        # Winner consistency
        winner = data.get("winner")
        is_draw = str(data.get("is_draw", "false")).lower() in ("true", "1", "yes")
        if winner and not is_draw and winner not in (part_a, part_b):
            report.add_error(
                table_name="match_event",
                row_ref=row_ref,
                rule_code="MATCH_BALANCE",
                message=f"Match winner '{winner}' does not match participant_a ('{part_a}') or participant_b ('{part_b}')",
            )

        report.cleaned_data = {
            **data,
            "match_date_utc": match_date,
            "is_draw": is_draw,
        }
        return report

    def validate_performance_stat(self, record: StagedRecord) -> ValidationReport:
        """Validate a performance_stats staged record."""
        report = ValidationReport()
        row_ref = f"row_{record.row_number}"
        data = record.data

        self.check_formula_injection(data, "performance_stat", row_ref, report)
        self.check_mandatory_provenance(record, report)

        sport_code = data.get("sport_code")
        if not sport_code or sport_code not in self.sports:
            report.add_error(
                table_name="performance_stat",
                row_ref=row_ref,
                rule_code="UNKNOWN_SPORT",
                message=f"Unknown sport_code '{sport_code}'",
            )

        # Metric definition check
        metric_code = data.get("metric_code")
        sport_metric_set = self.sport_metrics.get(sport_code, set())
        if not metric_code or metric_code not in sport_metric_set:
            report.add_error(
                table_name="performance_stat",
                row_ref=row_ref,
                rule_code="UNKNOWN_METRIC",
                message=f"Metric '{metric_code}' not defined for sport '{sport_code}' in metric catalogue",
            )

        # Scope
        scope = data.get("scope", "edition").lower()
        if scope not in ("match", "edition", "career"):
            report.add_error(
                table_name="performance_stat",
                row_ref=row_ref,
                rule_code="INVALID_SCOPE",
                message=f"Stat scope must be 'match', 'edition', or 'career', got '{scope}'",
            )

        # Numeric value and percentage range check
        val_str = data.get("value")
        try:
            val_float = float(val_str)
            # If metric is a percentage metric (e.g. fg_pct, three_pt_pct, raid_success_pct, passing_accuracy)
            if metric_code and (
                "pct" in metric_code or "accuracy" in metric_code or "percentage" in metric_code
            ):
                if val_float < 0.0 or val_float > 100.0:
                    report.add_error(
                        table_name="performance_stat",
                        row_ref=row_ref,
                        rule_code="RANGE_PCT",
                        message=f"Percentage metric '{metric_code}' must be between 0 and 100, got {val_float}",
                    )
            elif val_float < 0 and metric_code not in ("plus_minus", "goal_difference"):
                report.add_error(
                    table_name="performance_stat",
                    row_ref=row_ref,
                    rule_code="NEGATIVE_COUNT",
                    message=f"Non-negative metric '{metric_code}' received negative value {val_float}",
                )
        except (ValueError, TypeError):
            report.add_error(
                table_name="performance_stat",
                row_ref=row_ref,
                rule_code="INVALID_NUMBER",
                message=f"Value '{val_str}' cannot be parsed as a float",
            )
            val_float = 0.0

        report.cleaned_data = {
            **data,
            "scope": scope,
            "value": val_float,
        }
        return report

    def validate_ranking(self, record: StagedRecord) -> ValidationReport:
        """Validate a rankings staged record."""
        report = ValidationReport()
        row_ref = f"row_{record.row_number}"
        data = record.data

        self.check_formula_injection(data, "ranking_entry", row_ref, report)
        self.check_mandatory_provenance(record, report)

        sport_code = data.get("sport_code")
        if not sport_code or sport_code not in self.sports:
            report.add_error(
                table_name="ranking_entry",
                row_ref=row_ref,
                rule_code="UNKNOWN_SPORT",
                message=f"Unknown sport_code '{sport_code}'",
            )

        # Rank must be positive integer >= 1
        rank_val = data.get("rank")
        try:
            rank_int = int(rank_val)
            if rank_int < 1:
                report.add_error(
                    table_name="ranking_entry",
                    row_ref=row_ref,
                    rule_code="INVALID_RANK",
                    message=f"Rank must be >= 1, got {rank_int}",
                )
        except (ValueError, TypeError):
            report.add_error(
                table_name="ranking_entry",
                row_ref=row_ref,
                rule_code="INVALID_NUMBER",
                message=f"Rank '{rank_val}' must be an integer",
            )

        as_of_date = parse_iso_date(data.get("as_of_date"))
        if not as_of_date:
            report.add_error(
                table_name="ranking_snapshot",
                row_ref=row_ref,
                rule_code="INVALID_DATE",
                message=f"Invalid as_of_date: {data.get('as_of_date')}",
            )

        report.cleaned_data = {
            **data,
            "as_of_date": as_of_date,
        }
        return report

    def validate_olympic_result(self, record: StagedRecord) -> ValidationReport:
        """Validate an olympic_results staged record."""
        report = ValidationReport()
        row_ref = f"row_{record.row_number}"
        data = record.data

        self.check_formula_injection(data, "olympic_result", row_ref, report)
        self.check_mandatory_provenance(record, report)

        # Medal validation if present
        medal = data.get("medal")
        if medal:
            medal_clean = str(medal).strip().lower()
            if medal_clean not in ("gold", "silver", "bronze"):
                report.add_error(
                    table_name="olympic_result",
                    row_ref=row_ref,
                    rule_code="INVALID_MEDAL",
                    message=f"Medal must be 'gold', 'silver', or 'bronze', got '{medal}'",
                )

        # Country ISO3
        country_raw = data.get("country_iso3") or data.get("country")
        country_iso3 = normalize_country_iso3(country_raw) if country_raw else None
        if country_raw and not country_iso3:
            report.add_error(
                table_name="olympic_result",
                row_ref=row_ref,
                rule_code="INVALID_COUNTRY",
                message=f"Athlete country '{country_raw}' could not be resolved to valid ISO3",
            )

        report.cleaned_data = {
            **data,
            "medal": medal.strip().lower() if medal else None,
            "country_iso3": country_iso3,
            "is_world_record": str(data.get("is_world_record", "false")).lower()
            in ("true", "1", "yes"),
            "is_olympic_record": str(data.get("is_olympic_record", "false")).lower()
            in ("true", "1", "yes"),
        }
        return report
