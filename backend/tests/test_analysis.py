"""Unit and integration tests for statistical analysis engine (Part 9 & Table 5)."""

from datetime import date, datetime, timezone

import pytest

from sportstats.analysis.aggregates import (
    average_performance,
    extremes,
    win_percentage,
)
from sportstats.analysis.compare import (
    CrossSportComparisonError,
    calculate_percentiles,
    calculate_z_scores,
    compare_players,
    compare_teams,
    compare_tournaments,
)
from sportstats.analysis.rankings import (
    country_medal_distribution,
    ranking_history,
)
from sportstats.analysis.records import records_and_milestones
from sportstats.analysis.trends import (
    format_comparison,
    participation_trends,
    scoring_patterns,
    year_to_year_trend,
)
from sportstats.db.models import (
    Country,
    Discipline,
    MatchEvent,
    MatchSide,
    MetricDefinition,
    OlympicResult,
    Participant,
    PerformanceStat,
    RankingEntry,
    RankingSnapshot,
    RecordEntry,
    Source,
    Sport,
    Stage,
    Tournament,
    TournamentEdition,
)
from sportstats.db.seed.seed_catalogue import seed_database
from sportstats.db.session import Base, SessionLocal, engine
from sportstats.db.views import create_views, drop_views


@pytest.fixture(scope="module")
def analysis_db():
    """Sets up a populated database with realistic multi-sport fixtures across all 7 sports."""
    drop_views(engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_views(engine)
    db = SessionLocal()
    seed_database(db)

    # Fetch sports
    cricket = db.query(Sport).filter(Sport.code == "cricket").first()
    football = db.query(Sport).filter(Sport.code == "football").first()
    badminton = db.query(Sport).filter(Sport.code == "badminton").first()
    basketball = db.query(Sport).filter(Sport.code == "basketball").first()
    tennis = db.query(Sport).filter(Sport.code == "tennis").first()
    kabaddi = db.query(Sport).filter(Sport.code == "kabaddi").first()
    olympic = db.query(Sport).filter(Sport.code == "olympic").first()

    source = db.query(Source).first()
    ind = db.query(Country).filter(Country.iso3 == "IND").first()
    aus = db.query(Country).filter(Country.iso3 == "AUS").first()
    fra = db.query(Country).filter(Country.iso3 == "FRA").first()

    # 1. Tournaments
    cwc = Tournament(
        sport_id=cricket.id,
        name="ICC Cricket World Cup",
        governing_body="ICC",
        gender="men",
        level="world",
    )
    fwc = Tournament(
        sport_id=football.id,
        name="FIFA World Cup",
        governing_body="FIFA",
        gender="men",
        level="world",
    )
    wim = Tournament(
        sport_id=tennis.id,
        name="The Championships, Wimbledon",
        governing_body="AELTC",
        gender="men",
        level="world",
    )
    db.add_all([cwc, fwc, wim])
    db.flush()

    # 2. Editions
    cwc_2019 = TournamentEdition(
        tournament_id=cwc.id,
        edition_label="2019",
        year=2019,
        start_date=date(2019, 5, 30),
        end_date=date(2019, 7, 14),
        status="completed",
        participant_count=10,
        matches_or_events_count=48,
        format_description="Round-robin followed by knockout",
        source_id=source.id,
    )
    cwc_2023 = TournamentEdition(
        tournament_id=cwc.id,
        edition_label="2023",
        year=2023,
        start_date=date(2023, 10, 5),
        end_date=date(2023, 11, 19),
        status="completed",
        participant_count=10,
        matches_or_events_count=48,
        format_description="Round-robin followed by knockout",
        source_id=source.id,
    )
    fwc_2022 = TournamentEdition(
        tournament_id=fwc.id,
        edition_label="2022",
        year=2022,
        start_date=date(2022, 11, 20),
        end_date=date(2022, 12, 18),
        status="completed",
        participant_count=32,
        matches_or_events_count=64,
        format_description="8 groups of 4 followed by round of 16",
        source_id=source.id,
    )
    db.add_all([cwc_2019, cwc_2023, fwc_2022])
    db.flush()

    # 3. Participants
    team_ind = Participant(type="team", name="India", country_id=ind.id, sport_id=cricket.id)
    team_aus = Participant(type="team", name="Australia", country_id=aus.id, sport_id=cricket.id)
    player_kohli = Participant(
        type="player", name="Virat Kohli", country_id=ind.id, sport_id=cricket.id
    )
    player_messi = Participant(
        type="player", name="Lionel Messi", country_id=ind.id, sport_id=football.id
    )
    player_federer = Participant(
        type="player", name="Roger Federer", country_id=fra.id, sport_id=tennis.id
    )
    player_axelsen = Participant(
        type="player", name="Viktor Axelsen", country_id=fra.id, sport_id=badminton.id
    )
    player_curry = Participant(
        type="player", name="Stephen Curry", country_id=ind.id, sport_id=basketball.id
    )
    team_kabaddi_ind = Participant(
        type="team", name="India Kabaddi", country_id=ind.id, sport_id=kabaddi.id
    )
    db.add_all(
        [
            team_ind,
            team_aus,
            player_kohli,
            player_messi,
            player_federer,
            player_axelsen,
            player_curry,
            team_kabaddi_ind,
        ]
    )
    db.flush()

    # Link winners
    cwc_2023.winner_participant_id = team_aus.id
    cwc_2023.runner_up_participant_id = team_ind.id

    # 4. Metrics & Performance Stats
    m_runs = (
        db.query(MetricDefinition)
        .filter(MetricDefinition.code == "runs", MetricDefinition.sport_id == cricket.id)
        .first()
    )
    m_goals = (
        db.query(MetricDefinition)
        .filter(MetricDefinition.code == "goals", MetricDefinition.sport_id == football.id)
        .first()
    )

    # Historical runs for Kohli across 5 editions (for testing trend regression & threshold)
    years_runs = [(2007, 200), (2011, 282), (2015, 305), (2019, 443), (2023, 765)]
    for y, r_val in years_runs:
        ed = (
            db.query(TournamentEdition)
            .filter(TournamentEdition.year == y, TournamentEdition.tournament_id == cwc.id)
            .first()
        )
        if not ed:
            ed = TournamentEdition(
                tournament_id=cwc.id,
                edition_label=str(y),
                year=y,
                start_date=date(y, 1, 1),
                end_date=date(y, 2, 1),
                status="completed",
                participant_count=10,
                source_id=source.id,
            )
            db.add(ed)
            db.flush()

        stat = PerformanceStat(
            participant_id=player_kohli.id,
            edition_id=ed.id,
            metric_id=m_runs.id,
            value=r_val,
            scope="edition",
            source_id=source.id,
        )
        db.add(stat)

    # Messi football stat
    stat_messi = PerformanceStat(
        participant_id=player_messi.id,
        edition_id=fwc_2022.id,
        metric_id=m_goals.id,
        value=7,
        scope="edition",
        source_id=source.id,
    )
    db.add(stat_messi)

    # 5. Matches for win/loss testing
    stage = Stage(edition_id=cwc_2023.id, name="Group Stage", order_index=1, type="group")
    db.add(stage)
    db.flush()

    # Match 1: India beats Australia
    m1 = MatchEvent(
        edition_id=cwc_2023.id,
        stage_id=stage.id,
        sport_id=cricket.id,
        scheduled_at=datetime(2023, 10, 8, 8, 30, tzinfo=timezone.utc),
        status="completed",
        winner_participant_id=team_ind.id,
        source_id=source.id,
    )
    db.add(m1)
    db.flush()

    ms1_a = MatchSide(
        match_event_id=m1.id,
        participant_id=team_ind.id,
        side_index=0,
        score_primary=201,
        is_winner=True,
    )
    ms1_b = MatchSide(
        match_event_id=m1.id,
        participant_id=team_aus.id,
        side_index=1,
        score_primary=199,
        is_winner=False,
    )
    db.add_all([ms1_a, ms1_b])

    # 6. Olympic Results (Tokyo 2020)
    tokyo = TournamentEdition(
        tournament_id=cwc.id,  # dummy parent for olympic edition fixture
        edition_label="Tokyo 2020",
        year=2021,
        start_date=date(2021, 7, 23),
        end_date=date(2021, 8, 8),
        status="completed",
        participant_count=206,
        source_id=source.id,
    )
    db.add(tokyo)
    db.flush()

    athletics = db.query(Discipline).filter(Discipline.code == "athletics").first()
    athlete_ind = Participant(
        type="athlete", name="Neeraj Chopra", country_id=ind.id, sport_id=olympic.id
    )
    athlete_fra = Participant(
        type="athlete", name="Kevin Mayer", country_id=fra.id, sport_id=olympic.id
    )
    athlete_aus = Participant(
        type="athlete", name="Steve Solomon", country_id=aus.id, sport_id=olympic.id
    )
    db.add_all([athlete_ind, athlete_fra, athlete_aus])
    db.flush()

    res1 = OlympicResult(
        edition_id=tokyo.id,
        discipline_id=athletics.id,
        event_name="Men's Javelin Throw",
        participant_id=athlete_ind.id,
        rank=1,
        medal="gold",
        result_value=87.58,
        result_unit="meters",
    )
    res2 = OlympicResult(
        edition_id=tokyo.id,
        discipline_id=athletics.id,
        event_name="Men's Decathlon",
        participant_id=athlete_fra.id,
        rank=2,
        medal="silver",
        result_value=8726,
        result_unit="points",
    )
    res3 = OlympicResult(
        edition_id=tokyo.id,
        discipline_id=athletics.id,
        event_name="Men's 400m",
        participant_id=athlete_aus.id,
        rank=3,
        medal="bronze",
        result_value=44.90,
        result_unit="seconds",
    )
    db.add_all([res1, res2, res3])

    # 7. Ranking Snapshot
    rank_snap = RankingSnapshot(
        sport_id=cricket.id,
        ranking_system="ICC Men's ODI Team Rankings",
        category="Team",
        as_of_date=date(2023, 11, 20),
        source_id=source.id,
    )
    db.add(rank_snap)
    db.flush()
    r_entry = RankingEntry(
        snapshot_id=rank_snap.id, participant_id=team_ind.id, rank=1, points=121.0
    )
    db.add(r_entry)

    # 8. Records
    rec = RecordEntry(
        sport_id=cricket.id,
        record_type="tournament",
        metric_id=m_runs.id,
        description="Most runs in a single Cricket World Cup edition (765 runs)",
        holder_participant_id=player_kohli.id,
        value=765.0,
        achieved_on=date(2023, 11, 19),
        edition_id=cwc_2023.id,
        source_id=source.id,
    )
    db.add(rec)

    db.commit()
    yield db
    db.close()


def test_average_performance_and_extremes(analysis_db):
    """Verify average performance calculation and highest/lowest extremes."""
    kohli = analysis_db.query(Participant).filter(Participant.name == "Virat Kohli").first()
    res = average_performance(analysis_db, kohli.id, "runs")

    assert res["sample_count"] == 5
    assert res["total"] == 1995.0
    assert res["average"] == 399.0
    assert len(res["series"]) == 5

    # Test extremes
    ext = extremes(analysis_db, "runs")
    assert ext["highest"]["value"] == 765.0
    assert ext["highest"]["participant_name"] == "Virat Kohli"
    assert ext["lowest"]["value"] == 200.0


def test_cross_sport_comparison_guard_rejects_raw_metrics(analysis_db):
    """Verify that comparing participants from different sports on raw metrics is strictly blocked."""
    kohli = (
        analysis_db.query(Participant).filter(Participant.name == "Virat Kohli").first()
    )  # Cricket
    messi = (
        analysis_db.query(Participant).filter(Participant.name == "Lionel Messi").first()
    )  # Football

    # Attempting to compare raw runs or goals across Cricket and Football must fail!
    with pytest.raises(CrossSportComparisonError) as exc_info:
        compare_players(analysis_db, [kohli.id, messi.id], ["runs", "goals"])

    assert "Cross-Sport Comparison Guard Violation" in str(exc_info.value)
    assert "Raw statistical values" in str(exc_info.value)


def test_cross_sport_comparison_guard_allows_normalized_metrics(analysis_db):
    """Verify that comparing participants from different sports on normalized metrics is allowed."""
    kohli = analysis_db.query(Participant).filter(Participant.name == "Virat Kohli").first()
    messi = analysis_db.query(Participant).filter(Participant.name == "Lionel Messi").first()

    # Win percentage and z-score are normalized and must succeed
    res = compare_players(analysis_db, [kohli.id, messi.id], ["win_percentage", "z_score"])
    assert res["is_cross_sport"] is True
    assert "Cross-sport comparisons use normalized measures" in res["comparability_note"]


def test_compare_tournaments_report_table_5(analysis_db):
    """Verify tournament comparison matching Report Table 5 format."""
    cwc = analysis_db.query(Tournament).filter(Tournament.name == "ICC Cricket World Cup").first()
    fwc = analysis_db.query(Tournament).filter(Tournament.name == "FIFA World Cup").first()

    t_res = compare_tournaments(analysis_db, [cwc.id, fwc.id])
    assert len(t_res) == 2

    cwc_row = next(r for r in t_res if r["tournament"] == "ICC Cricket World Cup")
    assert cwc_row["sport"] == "Cricket"
    assert cwc_row["winner"] == "Australia"
    assert cwc_row["teams_or_players"] == 10
    assert cwc_row["matches_or_events"] == 48


def test_year_to_year_trend_and_sample_size_warnings(analysis_db):
    """Verify year-to-year trend calculation, regression R², and sample size warnings."""
    kohli = analysis_db.query(Participant).filter(Participant.name == "Virat Kohli").first()
    trend = year_to_year_trend(analysis_db, kohli.id, "runs")

    # Has 5 data points -> sufficient data
    assert trend["sample_count"] == 5
    assert trend["has_sufficient_data"] is True
    assert trend["warning"] is None
    assert trend["regression"] is not None
    assert trend["regression"]["direction"] == "upward"
    assert trend["regression"]["r_squared"] > 0.8
    assert "Data available for 2007–2023" in trend["coverage"]


def test_olympic_country_medal_distribution(analysis_db):
    """Verify Olympic medal distribution for Pie Charts (Report Figure 7 style)."""
    dist = country_medal_distribution(analysis_db)
    assert dist["total_medals_awarded"] == 3
    assert len(dist["slices"]) == 3

    ind_slice = next(s for s in dist["slices"] if s["iso3"] == "IND")
    assert ind_slice["gold"] == 1
    assert ind_slice["total"] == 1


def test_z_scores_and_percentiles():
    """Verify pure mathematical normalization functions."""
    vals = [10.0, 20.0, 30.0, 40.0, 50.0]
    z = calculate_z_scores(vals)
    assert len(z) == 5
    assert z[2] == 0.0  # Median/mean has z-score 0

    pcts = calculate_percentiles(vals)
    assert len(pcts) == 5
    assert pcts[0] == 10.0
    assert pcts[-1] == 90.0


def test_records_and_milestones(analysis_db):
    """Verify records and milestones query."""
    recs = records_and_milestones(analysis_db, sport_code="cricket")
    assert len(recs) >= 1
    assert recs[0]["holder"] == "Virat Kohli"
    assert recs[0]["value"] == 765.0


def test_win_percentage_query(analysis_db):
    """Verify win_percentage query for participant with matches."""
    team_ind = analysis_db.query(Participant).filter(Participant.name == "India").first()
    wp = win_percentage(analysis_db, team_ind.id)
    assert wp["matches_played"] == 1
    assert wp["wins"] == 1
    assert wp["win_percentage"] == 100.0


def test_compare_teams_and_single_sport(analysis_db):
    """Verify compare_teams within the same sport."""
    team_ind = analysis_db.query(Participant).filter(Participant.name == "India").first()
    team_aus = analysis_db.query(Participant).filter(Participant.name == "Australia").first()
    res = compare_teams(analysis_db, [team_ind.id, team_aus.id], ["runs"])
    assert res["is_cross_sport"] is False
    assert len(res["participants"]) == 2


def test_ranking_history(analysis_db):
    """Verify ranking history timeline for a participant."""
    team_ind = analysis_db.query(Participant).filter(Participant.name == "India").first()
    history = ranking_history(analysis_db, team_ind.id)
    assert history["participant_name"] == "India"
    assert history["best_rank"] == 1
    assert len(history["timeline"]) == 1


def test_scoring_patterns_and_participation(analysis_db):
    """Verify scoring patterns and participation trends."""
    cwc = analysis_db.query(Tournament).filter(Tournament.name == "ICC Cricket World Cup").first()
    patterns = scoring_patterns(analysis_db, cwc.id)
    assert len(patterns) >= 2

    trends = participation_trends(analysis_db, cwc.id)
    assert len(trends) >= 2
    assert trends[0]["participant_count"] == 10

    formats = format_comparison(analysis_db, cwc.id)
    assert len(formats) >= 2


def test_trend_insufficient_data_warning(analysis_db):
    """Verify that fewer than 5 data points generates an explicit sample-size warning."""
    messi = analysis_db.query(Participant).filter(Participant.name == "Lionel Messi").first()
    trend = year_to_year_trend(analysis_db, messi.id, "goals")
    assert trend["sample_count"] == 1
    assert trend["has_sufficient_data"] is False
    assert "Fewer than 5 data points" in trend["warning"]


def test_empty_results_handling(analysis_db):
    """Verify safe empty state handling across analysis functions."""
    trend_empty = year_to_year_trend(analysis_db, "non-existent-id", "runs")
    assert trend_empty["sample_count"] == 0
    assert trend_empty["has_sufficient_data"] is False

    ext_empty = extremes(analysis_db, "non-existent-metric")
    assert ext_empty["highest"] is None

    rank_empty = ranking_history(analysis_db, "non-existent-id")
    assert rank_empty["best_rank"] is None
