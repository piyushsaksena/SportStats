"""API endpoint contract and response verification tests."""

import pytest
from fastapi import HTTPException

from sportstats.api.routers.analytics import (
    compare_players_endpoint,
    compare_tournaments_endpoint,
    get_olympics_medals_endpoint,
    get_rankings_endpoint,
    get_tournament_tracking_feed,
    get_trends_endpoint,
)
from sportstats.api.routers.editions import (
    get_edition_detail,
    get_edition_matches,
    get_edition_participants,
    get_edition_standings,
)
from sportstats.api.routers.participants import (
    get_participant_profile,
    get_participant_stats,
)
from sportstats.api.routers.sources import list_sources
from sportstats.api.routers.sports import get_sport_metrics, list_sports
from sportstats.api.routers.tournaments import get_tournament_detail, list_tournaments
from sportstats.db.models import Participant, Tournament, TournamentEdition
from sportstats.db.session import SessionLocal
from sportstats.pipeline.generate_wave1 import import_wave1_data


@pytest.fixture(scope="module")
def db_session():
    """Provides a database session for API unit tests, ensuring Wave 1 data is loaded."""
    session = SessionLocal()
    import_wave1_data(session)
    try:
        yield session
    finally:
        session.close()


# -----------------------------------------------------------------------------
# Sports and Metrics
# -----------------------------------------------------------------------------
def test_api_list_sports(db_session):
    resp = list_sports(limit=10, offset=0, db=db_session)
    assert resp.meta.total >= 7
    assert len(resp.data) >= 7
    assert resp.provenance[0].organisation == "SportStats Core System"
    sport_codes = {s.code for s in resp.data}
    assert "cricket" in sport_codes
    assert "football" in sport_codes


def test_api_get_sport_metrics(db_session):
    resp = get_sport_metrics(code="cricket", db=db_session)
    assert resp.meta.total == 10
    metric_codes = {m.code for m in resp.data}
    assert "runs" in metric_codes
    assert "batting_average" in metric_codes


def test_api_get_sport_metrics_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_sport_metrics(code="nonexistent_sport", db=db_session)
    assert exc_info.value.status_code == 404


# -----------------------------------------------------------------------------
# Tournaments and Editions
# -----------------------------------------------------------------------------
def test_api_list_tournaments(db_session):
    resp = list_tournaments(sport="cricket", db=db_session)
    assert resp.meta.total >= 1
    names = [t.name for t in resp.data]
    assert "Cricket World Cup" in names


def test_api_get_tournament_detail(db_session):
    tourn = db_session.query(Tournament).filter(Tournament.name == "Cricket World Cup").first()
    assert tourn is not None
    resp = get_tournament_detail(id=tourn.id, db=db_session)
    assert resp.data["name"] == "Cricket World Cup"
    assert len(resp.data["editions_history"]) >= 2


def test_api_get_edition_detail(db_session):
    ed = (
        db_session.query(TournamentEdition)
        .join(Tournament, TournamentEdition.tournament_id == Tournament.id)
        .filter(Tournament.name == "Cricket World Cup", TournamentEdition.edition_label == "2023")
        .first()
    )
    assert ed is not None
    resp = get_edition_detail(id=ed.id, db=db_session)
    card = resp.data
    assert card["edition_label"] == "2023"
    assert card["winner"] == "Australia"
    assert card["runner_up"] == "India"
    assert card["host_country_iso3"] == "IND"
    assert len(resp.provenance) >= 1


def test_api_get_edition_matches(db_session):
    ed = (
        db_session.query(TournamentEdition)
        .join(Tournament, TournamentEdition.tournament_id == Tournament.id)
        .filter(Tournament.name == "Cricket World Cup", TournamentEdition.edition_label == "2023")
        .first()
    )
    assert ed is not None
    resp = get_edition_matches(id=ed.id, db=db_session)
    assert len(resp.data) >= 1
    winners = {m.winner for m in resp.data}
    assert "Australia" in winners
    assert "India" in winners


def test_api_get_edition_participants(db_session):
    ed = (
        db_session.query(TournamentEdition)
        .filter(TournamentEdition.winner_participant_id.isnot(None))
        .first()
    )
    assert ed is not None
    resp = get_edition_participants(id=ed.id, db=db_session)
    assert len(resp.data) >= 1


def test_api_get_edition_standings(db_session):
    ed = (
        db_session.query(TournamentEdition)
        .join(Tournament, TournamentEdition.tournament_id == Tournament.id)
        .filter(Tournament.name == "FIFA World Cup", TournamentEdition.edition_label == "2022")
        .first()
    )
    assert ed is not None
    resp = get_edition_standings(id=ed.id, db=db_session)
    assert len(resp.data) >= 1
    assert resp.data[0].played >= 1


# -----------------------------------------------------------------------------
# Participants and Stats
# -----------------------------------------------------------------------------
def test_api_get_participant_profile(db_session):
    p = db_session.query(Participant).filter(Participant.name == "Virat Kohli").first()
    assert p is not None
    resp = get_participant_profile(id=p.id, db=db_session)
    assert resp.data["name"] == "Virat Kohli"
    assert resp.data["sport_code"] == "cricket"


def test_api_get_participant_stats(db_session):
    p = db_session.query(Participant).filter(Participant.name == "Virat Kohli").first()
    assert p is not None
    resp = get_participant_stats(id=p.id, db=db_session)
    assert len(resp.data) >= 1
    run_stats = [s for s in resp.data if s.metric_code == "runs"]
    assert len(run_stats) >= 1
    values = {s.value for s in run_stats}
    assert 765.0 in values


# -----------------------------------------------------------------------------
# Analytics: Comparisons, Trends, Rankings, Olympics
# -----------------------------------------------------------------------------
def test_api_compare_players_same_sport(db_session):
    p1 = db_session.query(Participant).filter(Participant.name == "Virat Kohli").first()
    p2 = db_session.query(Participant).filter(Participant.name == "Rohit Sharma").first()
    assert p1 and p2
    resp = compare_players_endpoint(ids=f"{p1.id},{p2.id}", metrics="runs", db=db_session)
    assert len(resp.data["participants"]) == 2
    assert resp.data["is_cross_sport"] is False


def test_api_compare_players_cross_sport_guard_blocks_raw_metrics(db_session):
    p1 = db_session.query(Participant).filter(Participant.name == "Virat Kohli").first()
    p2 = db_session.query(Participant).filter(Participant.name == "Lionel Messi").first()
    assert p1 and p2
    # Comparing cricket runs with football goals must raise HTTP 400
    with pytest.raises(HTTPException) as exc_info:
        compare_players_endpoint(ids=f"{p1.id},{p2.id}", metrics="runs,goals", db=db_session)
    assert exc_info.value.status_code == 400
    assert "Cross-Sport Comparison Guard Violation" in exc_info.value.detail


def test_api_compare_tournaments(db_session):
    tourneys = db_session.query(Tournament).limit(2).all()
    assert len(tourneys) == 2
    t_ids = f"{tourneys[0].id},{tourneys[1].id}"
    resp = compare_tournaments_endpoint(ids=t_ids, db=db_session)
    assert len(resp.data) == 2


def test_api_trends_endpoint(db_session):
    p = db_session.query(Participant).filter(Participant.name == "Virat Kohli").first()
    assert p is not None
    resp = get_trends_endpoint(participant=p.id, metric="runs", db=db_session)
    assert resp.data["participant_id"] == p.id


def test_api_rankings_endpoint(db_session):
    resp = get_rankings_endpoint(sport="cricket", db=db_session)
    assert len(resp.data) >= 1
    assert resp.data[0].ranking_system == "ICC Men's ODI Team Rankings"


def test_api_olympics_medals_endpoint(db_session):
    resp = get_olympics_medals_endpoint(max_slices=6, db=db_session)
    assert "slices" in resp.data
    assert resp.meta.total >= 1


def test_api_tracking_feed(db_session):
    resp = get_tournament_tracking_feed(db=db_session)
    assert resp.data["summary"]["total_tracked"] >= 14
    assert len(resp.data["completed"]) >= 14


def test_api_list_sources(db_session):
    resp = list_sources(limit=20, offset=0, db=db_session)
    assert resp.meta.total >= 8
    orgs = {s.organisation for s in resp.data}
    assert "ICC" in orgs
