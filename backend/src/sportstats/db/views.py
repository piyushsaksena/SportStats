"""SQL View definitions for SportStats (Section 6.8).

Defines standard database views for tournament tracking, edition summaries,
participant totals, win/loss records, and previous tournament winners.
Compatible with PostgreSQL and SQLite.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

VIEW_TOURNAMENT_TRACKING = """
CREATE VIEW IF NOT EXISTS v_tournament_tracking AS
SELECT
    te.id AS edition_id,
    t.id AS tournament_id,
    s.code AS sport_code,
    s.name AS sport_name,
    t.name AS tournament_name,
    te.edition_label,
    te.year,
    te.start_date,
    te.end_date,
    te.status,
    te.participant_count,
    te.matches_or_events_count,
    pw.name AS winner_name,
    pr.name AS runner_up_name,
    te.is_sample
FROM tournament_edition te
JOIN tournament t ON te.tournament_id = t.id
JOIN sport s ON t.sport_id = s.id
LEFT JOIN participant pw ON te.winner_participant_id = pw.id
LEFT JOIN participant pr ON te.runner_up_participant_id = pr.id;
"""

VIEW_EDITION_SUMMARY = """
CREATE VIEW IF NOT EXISTS v_edition_summary AS
SELECT
    te.id AS edition_id,
    t.id AS tournament_id,
    t.name AS tournament_name,
    s.code AS sport_code,
    te.edition_label,
    te.year,
    c.name AS host_country,
    te.host_city,
    te.participant_count,
    COUNT(m.id) AS total_matches_recorded,
    pw.name AS champion_name,
    te.status,
    te.is_sample
FROM tournament_edition te
JOIN tournament t ON te.tournament_id = t.id
JOIN sport s ON t.sport_id = s.id
LEFT JOIN country c ON te.host_country_id = c.id
LEFT JOIN match_event m ON m.edition_id = te.id
LEFT JOIN participant pw ON te.winner_participant_id = pw.id
GROUP BY
    te.id, t.id, t.name, s.code, te.edition_label, te.year,
    c.name, te.host_city, te.participant_count, pw.name, te.status, te.is_sample;
"""

VIEW_PARTICIPANT_EDITION_TOTALS = """
CREATE VIEW IF NOT EXISTS v_participant_edition_totals AS
SELECT
    ps.edition_id,
    ps.participant_id,
    p.name AS participant_name,
    p.type AS participant_type,
    m.id AS metric_id,
    m.code AS metric_code,
    m.name AS metric_name,
    m.unit AS metric_unit,
    m.aggregation,
    SUM(ps.value) AS total_value,
    AVG(ps.value) AS average_value,
    COUNT(ps.id) AS sample_count,
    ps.is_sample
FROM performance_stat ps
JOIN participant p ON ps.participant_id = p.id
JOIN metric_definition m ON ps.metric_id = m.id
GROUP BY
    ps.edition_id, ps.participant_id, p.name, p.type,
    m.id, m.code, m.name, m.unit, m.aggregation, ps.is_sample;
"""

VIEW_WIN_LOSS_RECORD = """
CREATE VIEW IF NOT EXISTS v_win_loss_record AS
SELECT
    ms.participant_id,
    p.name AS participant_name,
    p.sport_id,
    s.code AS sport_code,
    COUNT(ms.id) AS matches_played,
    SUM(CASE WHEN ms.is_winner = 1 OR ms.is_winner = true THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN (ms.is_winner = 0 OR ms.is_winner = false) AND (m.is_draw = 0 OR m.is_draw = false) THEN 1 ELSE 0 END) AS losses,
    SUM(CASE WHEN m.is_draw = 1 OR m.is_draw = true THEN 1 ELSE 0 END) AS draws,
    ROUND(CAST(SUM(CASE WHEN ms.is_winner = 1 OR ms.is_winner = true THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / NULLIF(COUNT(ms.id), 0), 2) AS win_percentage,
    ROUND(CAST(SUM(CASE WHEN (ms.is_winner = 0 OR ms.is_winner = false) AND (m.is_draw = 0 OR m.is_draw = false) THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / NULLIF(COUNT(ms.id), 0), 2) AS loss_percentage,
    ROUND(CAST(SUM(CASE WHEN m.is_draw = 1 OR m.is_draw = true THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / NULLIF(COUNT(ms.id), 0), 2) AS draw_percentage
FROM match_side ms
JOIN match_event m ON ms.match_event_id = m.id
JOIN participant p ON ms.participant_id = p.id
JOIN sport s ON p.sport_id = s.id
WHERE m.status = 'completed'
GROUP BY ms.participant_id, p.name, p.sport_id, s.code;
"""

VIEW_PREVIOUS_WINNERS = """
CREATE VIEW IF NOT EXISTS v_previous_winners AS
SELECT
    t.id AS tournament_id,
    t.name AS tournament_name,
    s.code AS sport_code,
    te.id AS edition_id,
    te.edition_label,
    te.year,
    pw.id AS winner_participant_id,
    pw.name AS winner_name,
    pr.id AS runner_up_participant_id,
    pr.name AS runner_up_name,
    te.is_sample
FROM tournament_edition te
JOIN tournament t ON te.tournament_id = t.id
JOIN sport s ON t.sport_id = s.id
JOIN participant pw ON te.winner_participant_id = pw.id
LEFT JOIN participant pr ON te.runner_up_participant_id = pr.id
WHERE te.status = 'completed';
"""

ALL_VIEWS = [
    VIEW_TOURNAMENT_TRACKING,
    VIEW_EDITION_SUMMARY,
    VIEW_PARTICIPANT_EDITION_TOTALS,
    VIEW_WIN_LOSS_RECORD,
    VIEW_PREVIOUS_WINNERS,
]


def create_views(engine: Engine) -> None:
    """Execute DDL statements to create all 5 required views."""
    with engine.begin() as conn:
        for view_ddl in ALL_VIEWS:
            conn.execute(text(view_ddl))


def drop_views(engine: Engine) -> None:
    """Drop all views if they exist."""
    view_names = [
        "v_tournament_tracking",
        "v_edition_summary",
        "v_participant_edition_totals",
        "v_win_loss_record",
        "v_previous_winners",
    ]
    with engine.begin() as conn:
        for name in view_names:
            conn.execute(text(f"DROP VIEW IF EXISTS {name}"))
