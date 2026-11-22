"""Integration and Acceptance Tests for Phase 3 Ingestion Pipeline.

Verifies:
- Valid fixtures load rows with complete provenance.
- Invalid fixtures produce itemized rejections with exact rule codes (e.g. RANGE_PCT).
- Dry-run mode produces reports without mutating database state.
- Raw files remain strictly immutable.
- Formula injection attempts are quarantined.
"""

from pathlib import Path

import pytest

from sportstats.db.models import (
    DataQualityIssue,
    IngestionRun,
    MatchEvent,
    MatchSide,
    OlympicResult,
    PerformanceStat,
    RankingEntry,
    RankingSnapshot,
    Source,
    TournamentEdition,
)
from sportstats.db.seed.seed_catalogue import seed_database
from sportstats.db.session import Base, SessionLocal, engine
from sportstats.db.views import create_views, drop_views
from sportstats.pipeline.adapters.base import calculate_sha256
from sportstats.pipeline.cleaners import has_formula_injection, normalize_country_iso3
from sportstats.pipeline.cli import main as cli_main
from sportstats.pipeline.importer import CSVImporter
from sportstats.pipeline.verification import VerificationWorkflow

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for each ingestion test."""
    drop_views(engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_views(engine)
    db = SessionLocal()
    seed_database(db)
    yield db
    db.close()


def test_import_valid_tournament_editions(db_session, tmp_path):
    """Verify that importing a valid tournament_editions CSV loads entities and populates provenance."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    file_path = VALID_DIR / "tournament_editions_valid.csv"

    result = importer.import_csv(file_path, "tournament_editions", dry_run=False)

    assert result.status == "success"
    assert result.rows_in == 3
    assert result.rows_loaded == 3
    assert result.rows_rejected == 0

    # Verify entities
    editions = db_session.query(TournamentEdition).all()
    assert len(editions) == 3

    # Verify provenance on every row
    for ed in editions:
        assert ed.source_id is not None
        source = db_session.query(Source).filter(Source.id == ed.source_id).first()
        assert source is not None
        assert ed.winner_participant_id is not None

    # Check specific tournament edition
    cwc = (
        db_session.query(TournamentEdition)
        .filter(TournamentEdition.edition_label == "2023")
        .first()
    )
    assert cwc is not None
    assert cwc.year == 2023
    assert cwc.status == "completed"
    assert cwc.host_city == "Ahmedabad"


def test_import_valid_matches(db_session, tmp_path):
    """Verify that importing matches creates MatchEvent, stages, participants, and MatchSide rows."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    # First seed editions
    importer.import_csv(VALID_DIR / "tournament_editions_valid.csv", "tournament_editions")

    matches_file = VALID_DIR / "matches_valid.csv"
    result = importer.import_csv(matches_file, "matches", dry_run=False)

    assert result.status == "success"
    assert result.rows_loaded == 2

    matches = db_session.query(MatchEvent).all()
    assert len(matches) == 2

    # Check match sides
    for match in matches:
        sides = db_session.query(MatchSide).filter(MatchSide.match_event_id == match.id).all()
        assert len(sides) == 2
        assert {s.side_index for s in sides} == {0, 1}
        assert match.source_id is not None


def test_import_valid_performance_stats(db_session, tmp_path):
    """Verify importing performance_stats records linked to participants and metric catalogue."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    importer.import_csv(VALID_DIR / "tournament_editions_valid.csv", "tournament_editions")

    stats_file = VALID_DIR / "performance_stats_valid.csv"
    result = importer.import_csv(stats_file, "performance_stats", dry_run=False)

    assert result.status == "success"
    assert result.rows_loaded == 6

    stats = db_session.query(PerformanceStat).all()
    assert len(stats) == 6
    for s in stats:
        assert s.value is not None
        assert s.source_id is not None


def test_import_valid_rankings(db_session, tmp_path):
    """Verify importing ranking snapshots and entries."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    rankings_file = VALID_DIR / "rankings_valid.csv"

    result = importer.import_csv(rankings_file, "rankings", dry_run=False)

    assert result.status == "success"
    assert result.rows_loaded == 3

    snapshots = db_session.query(RankingSnapshot).all()
    assert len(snapshots) >= 1

    entries = db_session.query(RankingEntry).all()
    assert len(entries) == 3
    ranks = [e.rank for e in entries]
    assert sorted(ranks) == [1, 2, 3]


def test_import_valid_olympic_results(db_session, tmp_path):
    """Verify importing Olympic results, disciplines, medals, and record flags."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    olympic_file = VALID_DIR / "olympic_results_valid.csv"

    result = importer.import_csv(olympic_file, "olympic_results", dry_run=False)

    assert result.status == "success"
    assert result.rows_loaded == 3

    results = db_session.query(OlympicResult).all()
    assert len(results) == 3
    gold_medals = [r for r in results if r.medal == "gold"]
    assert len(gold_medals) == 2


def test_import_invalid_tournament_editions_itemized_rejections(db_session, tmp_path):
    """Verify that an invalid CSV produces itemized rejections logged to DataQualityIssue."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    invalid_file = INVALID_DIR / "tournament_editions_invalid.csv"

    result = importer.import_csv(invalid_file, "tournament_editions", dry_run=False)

    assert result.status in ("partial", "failed")
    assert result.rows_rejected == 4
    assert result.rows_loaded == 0

    issues = db_session.query(DataQualityIssue).all()
    assert len(issues) >= 4

    rule_codes = {i.rule_code for i in issues}
    assert "INVALID_DATE_ORDER" in rule_codes
    assert "INVALID_COUNTRY" in rule_codes
    assert "FORMULA_INJECTION" in rule_codes
    assert "MISSING_SOURCE" in rule_codes


def test_appendix_b_acceptance_case_5_range_pct_rejection(db_session, tmp_path):
    """Appendix B Test Case 5: Importing a CSV row with win_percentage/fg_pct = 120 -> rejected with rule RANGE_PCT."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    invalid_file = INVALID_DIR / "performance_stats_invalid.csv"

    result = importer.import_csv(invalid_file, "performance_stats", dry_run=False)

    assert result.rows_rejected >= 4

    issues = db_session.query(DataQualityIssue).all()
    rule_codes = {i.rule_code for i in issues}

    # Verify RANGE_PCT was triggered for 120.0
    assert "RANGE_PCT" in rule_codes
    range_issue = [i for i in issues if i.rule_code == "RANGE_PCT"][0]
    assert "between 0 and 100" in range_issue.message

    # Verify UNKNOWN_METRIC was triggered for non_existent_metric
    assert "UNKNOWN_METRIC" in rule_codes

    # Verify NEGATIVE_COUNT was triggered for negative value
    assert "NEGATIVE_COUNT" in rule_codes


def test_dry_run_does_not_mutate_database(db_session, tmp_path):
    """Verify that dry_run=True returns validation results without inserting rows."""
    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    file_path = VALID_DIR / "tournament_editions_valid.csv"

    initial_editions_count = db_session.query(TournamentEdition).count()
    initial_runs_count = db_session.query(IngestionRun).count()

    result = importer.import_csv(file_path, "tournament_editions", dry_run=True)

    assert result.dry_run is True
    assert result.rows_loaded == 3
    assert result.rows_rejected == 0

    # Ensure no rows were committed
    assert db_session.query(TournamentEdition).count() == initial_editions_count
    assert db_session.query(IngestionRun).count() == initial_runs_count


def test_raw_file_immutability(db_session, tmp_path):
    """Verify that raw source files are strictly read-only and never modified by the ingestion process."""
    file_path = VALID_DIR / "tournament_editions_valid.csv"
    initial_hash = calculate_sha256(file_path.read_bytes())

    importer = CSVImporter(db=db_session, raw_storage_dir=tmp_path)
    importer.import_csv(file_path, "tournament_editions", dry_run=False)

    post_hash = calculate_sha256(file_path.read_bytes())
    assert initial_hash == post_hash, "Raw file content was modified during ingestion!"

    # Verify that a copy and sidecar metadata were placed into raw_storage_dir
    raw_files = list(tmp_path.glob("*.csv"))
    assert len(raw_files) >= 1
    sidecar_files = list(tmp_path.glob("*.meta.json"))
    assert len(sidecar_files) >= 1


def test_formula_injection_defense():
    """Verify detection of spreadsheet formula injection prefixes (=, +, -, @)."""
    assert has_formula_injection("=SUM(A1:A10)") is True
    assert has_formula_injection("+cmd|' /C calc'!A0") is True
    assert has_formula_injection("-2+3*cmd|' /C calc'!A0") is True
    assert has_formula_injection("@SUM(1,2)") is True
    assert has_formula_injection("Normal Text") is False
    assert has_formula_injection("India") is False


def test_country_normalization():
    """Verify country name to ISO3 resolution."""
    assert normalize_country_iso3("India") == "IND"
    assert normalize_country_iso3("usa") == "USA"
    assert normalize_country_iso3("Great Britain") == "GBR"
    assert normalize_country_iso3("FRA") == "FRA"
    assert normalize_country_iso3("Unknown Land") is None


def test_verification_workflow_lifecycle(db_session):
    """Verify unverified source approval and audit note recording."""
    workflow = VerificationWorkflow(db_session)
    source = Source(
        organisation="TEST_SECONDARY",
        name="Secondary Unverified Source",
        url="https://secondary.internal/sports",
        access_method="manual_csv",
        tier="secondary",
        terms_note="Initial import",
        is_verified=False,
    )
    db_session.add(source)
    db_session.commit()

    assert workflow.requires_verification(source) is True

    # Approve
    ok = workflow.approve_source(source.id, reviewer_name="lead_analyst")
    assert ok is True

    db_session.refresh(source)
    assert source.is_verified is True
    assert "Verified by lead_analyst" in source.terms_note


def test_cli_execution_dry_run():
    """Verify CLI interface runs import dry-run and exits cleanly."""
    file_path = str(VALID_DIR / "tournament_editions_valid.csv")
    exit_code = cli_main(
        ["import", "--type", "tournament_editions", "--file", file_path, "--dry-run"]
    )
    assert exit_code == 0
