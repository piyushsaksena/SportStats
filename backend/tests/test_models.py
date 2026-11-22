"""Unit tests for SQLAlchemy models, seed catalogue, and database views."""

import pytest
from sqlalchemy import text

from sportstats.db.models import (
    Country,
    Discipline,
    Source,
    Sport,
)
from sportstats.db.seed.seed_catalogue import seed_database
from sportstats.db.session import Base, SessionLocal, engine
from sportstats.db.views import create_views, drop_views
from sportstats.metrics.catalog import (
    get_catalogue_counts_by_sport,
)


@pytest.fixture(scope="module")
def db_session():
    """Sets up an in-memory SQLite or fresh test database with tables and views."""
    drop_views(engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_views(engine)
    db = SessionLocal()
    seed_database(db)
    yield db
    db.close()


def test_catalogue_counts_per_sport_match_report_figure_3():
    """Verify that metric counts per sport strictly match Section 7 and report Figure 3."""
    counts = get_catalogue_counts_by_sport()
    assert counts["cricket"] == 10, f"Expected 10 cricket metrics, got {counts['cricket']}"
    assert counts["football"] == 10, f"Expected 10 football metrics, got {counts['football']}"
    assert counts["badminton"] == 9, f"Expected 9 badminton metrics, got {counts['badminton']}"
    assert counts["basketball"] == 10, f"Expected 10 basketball metrics, got {counts['basketball']}"
    assert counts["tennis"] == 10, f"Expected 10 tennis metrics, got {counts['tennis']}"
    assert counts["kabaddi"] == 10, f"Expected 10 kabaddi metrics, got {counts['kabaddi']}"
    assert counts["olympic"] == 10, f"Expected 10 olympic metrics, got {counts['olympic']}"
    assert sum(counts.values()) == 69, "Expected 69 total metrics across the 7 sports"


def test_seeded_sports_and_disciplines(db_session):
    """Verify all 7 sports and 10 Olympic disciplines are present in the DB."""
    sports = db_session.query(Sport).all()
    assert len(sports) == 7

    olympic_sport = db_session.query(Sport).filter(Sport.code == "olympic").first()
    assert olympic_sport is not None

    disciplines = db_session.query(Discipline).filter(Discipline.sport_id == olympic_sport.id).all()
    assert len(disciplines) == 10


def test_seeded_sources_and_countries(db_session):
    """Verify official sources and core ISO3 countries are seeded."""
    sources = db_session.query(Source).all()
    assert len(sources) >= 7

    icc_source = db_session.query(Source).filter(Source.organisation == "ICC").first()
    assert icc_source is not None
    assert icc_source.tier == "official"

    atp_source = db_session.query(Source).filter(Source.organisation == "ATP/WTA").first()
    assert atp_source is not None
    assert atp_source.tier == "secondary"

    ind_country = db_session.query(Country).filter(Country.iso3 == "IND").first()
    assert ind_country is not None
    assert ind_country.name == "India"


def test_database_views_queryable(db_session):
    """Verify that all 5 database views in Section 6.8 can be queried without SQL syntax errors."""
    views = [
        "v_tournament_tracking",
        "v_edition_summary",
        "v_participant_edition_totals",
        "v_win_loss_record",
        "v_previous_winners",
    ]
    for view_name in views:
        result = db_session.execute(text(f"SELECT * FROM {view_name} LIMIT 1")).fetchall()
        assert isinstance(result, list)
