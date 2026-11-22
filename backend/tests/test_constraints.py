"""Constraint verification tests for schema integrity."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from sportstats.db.models import (
    Country,
    Source,
    Sport,
    Tournament,
    TournamentEdition,
)
from sportstats.db.seed.seed_catalogue import seed_database
from sportstats.db.session import Base, SessionLocal, engine
from sportstats.db.views import create_views, drop_views


@pytest.fixture
def fresh_db():
    """Provides a fresh database session for constraint testing."""
    drop_views(engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_views(engine)
    db = SessionLocal()
    seed_database(db)
    yield db
    db.close()


def test_edition_date_order_constraint(fresh_db):
    """Verify that an edition with end_date < start_date violates chk_edition_date_order."""
    cricket = fresh_db.query(Sport).filter(Sport.code == "cricket").first()
    source = fresh_db.query(Source).first()

    tournament = Tournament(
        sport_id=cricket.id,
        name="Test Cup",
        governing_body="ICC",
        gender="men",
        level="world",
    )
    fresh_db.add(tournament)
    fresh_db.flush()

    # Invalid edition: end_date precedes start_date
    invalid_edition = TournamentEdition(
        tournament_id=tournament.id,
        edition_label="2025-Invalid",
        year=2025,
        start_date=date(2025, 10, 20),
        end_date=date(2025, 10, 10),  # earlier than start_date
        status="completed",
        participant_count=8,
        source_id=source.id,
    )
    fresh_db.add(invalid_edition)

    with pytest.raises(IntegrityError):
        fresh_db.commit()

    fresh_db.rollback()


def test_unique_country_iso3_constraint(fresh_db):
    """Verify that duplicate country ISO3 violates uniqueness."""
    duplicate_country = Country(
        iso3="IND",  # Already exists
        name="Republic of India",
        continent="Asia",
    )
    fresh_db.add(duplicate_country)

    with pytest.raises(IntegrityError):
        fresh_db.commit()

    fresh_db.rollback()


def test_unique_sport_code_constraint(fresh_db):
    """Verify that duplicate sport code violates uniqueness."""
    duplicate_sport = Sport(
        code="cricket",  # Already exists
        name="Cricket Duplicate",
        is_team_sport=True,
    )
    fresh_db.add(duplicate_sport)

    with pytest.raises(IntegrityError):
        fresh_db.commit()

    fresh_db.rollback()


def test_unique_tournament_edition_label_constraint(fresh_db):
    """Verify that duplicate edition label for the same tournament violates uniqueness."""
    cricket = fresh_db.query(Sport).filter(Sport.code == "cricket").first()
    source = fresh_db.query(Source).first()

    tournament = Tournament(
        sport_id=cricket.id,
        name="Duplicate Edition Test Cup",
        governing_body="ICC",
        gender="men",
        level="world",
    )
    fresh_db.add(tournament)
    fresh_db.flush()

    ed1 = TournamentEdition(
        tournament_id=tournament.id,
        edition_label="2023",
        year=2023,
        start_date=date(2023, 10, 5),
        end_date=date(2023, 11, 19),
        status="completed",
        participant_count=10,
        source_id=source.id,
    )
    fresh_db.add(ed1)
    fresh_db.commit()

    # Second edition with same tournament_id and edition_label
    ed2 = TournamentEdition(
        tournament_id=tournament.id,
        edition_label="2023",
        year=2023,
        start_date=date(2023, 10, 5),
        end_date=date(2023, 11, 19),
        status="completed",
        participant_count=10,
        source_id=source.id,
    )
    fresh_db.add(ed2)

    with pytest.raises(IntegrityError):
        fresh_db.commit()

    fresh_db.rollback()
