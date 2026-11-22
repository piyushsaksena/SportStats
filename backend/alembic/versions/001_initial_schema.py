"""Initial schema migration for SportStats common relational framework.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-17 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from sportstats.db.views import ALL_VIEWS

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Reference tables
    op.create_table(
        "sport",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("is_team_sport", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_individual_sport", sa.Boolean(), nullable=False, default=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sport_code", "sport", ["code"], unique=True)

    op.create_table(
        "discipline",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("sport_id", "code", name="uq_discipline_sport_code"),
    )
    op.create_index("ix_discipline_sport_id", "discipline", ["sport_id"])

    op.create_table(
        "country",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("iso3", sa.String(length=3), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("continent", sa.String(length=32), nullable=True),
    )
    op.create_index("ix_country_iso3", "country", ["iso3"], unique=True)

    op.create_table(
        "venue",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=False),
        sa.Column(
            "country_id",
            sa.String(length=36),
            sa.ForeignKey("country.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("capacity", sa.Integer(), nullable=True),
    )

    op.create_table(
        "source",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organisation", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("access_method", sa.String(length=32), nullable=False),
        sa.Column("tier", sa.String(length=16), nullable=False, default="official"),
        sa.Column("terms_note", sa.Text(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, default=True),
    )

    # 2. Tournament tables
    op.create_table(
        "tournament",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "discipline_id",
            sa.String(length=36),
            sa.ForeignKey("discipline.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("governing_body", sa.String(length=64), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False, default="men"),
        sa.Column("level", sa.String(length=16), nullable=False, default="world"),
        sa.Column("frequency_years", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_tournament_sport_id", "tournament", ["sport_id"])

    # 3. Participants
    op.create_table(
        "participant",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "country_id",
            sa.String(length=36),
            sa.ForeignKey("country.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_ids", sa.JSON(), nullable=True),
        sa.Column("is_sample", sa.Boolean(), nullable=False, default=False),
    )
    op.create_index("ix_participant_name", "participant", ["name"])
    op.create_index("ix_participant_sport_id", "participant", ["sport_id"])

    op.create_table(
        "player_profile",
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=16), nullable=True),
        sa.Column("role_or_position", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "team_profile",
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("team_type", sa.String(length=16), nullable=False, default="national"),
        sa.Column("short_code", sa.String(length=16), nullable=True),
    )

    # 4. Tournament Editions
    op.create_table(
        "tournament_edition",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "tournament_id",
            sa.String(length=36),
            sa.ForeignKey("tournament.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("edition_label", sa.String(length=64), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "host_country_id",
            sa.String(length=36),
            sa.ForeignKey("country.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("host_city", sa.String(length=64), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, default="completed"),
        sa.Column("participant_count", sa.Integer(), nullable=False, default=0),
        sa.Column("format_description", sa.Text(), nullable=True),
        sa.Column("matches_or_events_count", sa.Integer(), nullable=True),
        sa.Column(
            "winner_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "runner_up_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("is_sample", sa.Boolean(), nullable=False, default=False),
        sa.CheckConstraint("end_date >= start_date", name="chk_edition_date_order"),
        sa.UniqueConstraint("tournament_id", "edition_label", name="uq_tournament_edition_label"),
    )
    op.create_index("ix_tournament_edition_tournament_id", "tournament_edition", ["tournament_id"])
    op.create_index("ix_tournament_edition_year", "tournament_edition", ["year"])

    # 5. Stages, Matches & Events
    op.create_table(
        "stage",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, default=0),
        sa.Column("type", sa.String(length=16), nullable=False, default="knockout"),
    )
    op.create_index("ix_stage_edition_id", "stage", ["edition_id"])

    op.create_table(
        "match_event",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stage_id",
            sa.String(length=36),
            sa.ForeignKey("stage.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "discipline_id",
            sa.String(length=36),
            sa.ForeignKey("discipline.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "venue_id",
            sa.String(length=36),
            sa.ForeignKey("venue.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=16), nullable=False, default="completed"),
        sa.Column(
            "winner_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_draw", sa.Boolean(), nullable=False, default=False),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("is_sample", sa.Boolean(), nullable=False, default=False),
    )
    op.create_index("ix_match_event_edition_id", "match_event", ["edition_id"])
    op.create_index("ix_match_event_sport_id", "match_event", ["sport_id"])

    op.create_table(
        "match_side",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "match_event_id",
            sa.String(length=36),
            sa.ForeignKey("match_event.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("side_index", sa.Integer(), nullable=False, default=0),
        sa.Column("score_primary", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("score_detail", sa.JSON(), nullable=True),
        sa.Column("is_winner", sa.Boolean(), nullable=True),
        sa.UniqueConstraint("match_event_id", "participant_id", name="uq_match_side_participant"),
    )
    op.create_index("ix_match_side_match_event_id", "match_side", ["match_event_id"])
    op.create_index("ix_match_side_participant_id", "match_side", ["participant_id"])

    op.create_table(
        "olympic_result",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "discipline_id",
            sa.String(length=36),
            sa.ForeignKey("discipline.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_name", sa.String(length=128), nullable=False),
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("medal", sa.String(length=16), nullable=True),
        sa.Column("result_value", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("result_unit", sa.String(length=32), nullable=True),
        sa.Column("is_world_record", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_olympic_record", sa.Boolean(), nullable=False, default=False),
    )
    op.create_index("ix_olympic_result_edition_id", "olympic_result", ["edition_id"])

    op.create_table(
        "team_membership",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "team_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "player_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("role", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_team_membership_team", "team_membership", ["team_participant_id"])
    op.create_index("ix_team_membership_player", "team_membership", ["player_participant_id"])

    op.create_table(
        "edition_participant",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("group_label", sa.String(length=16), nullable=True),
        sa.Column("final_position", sa.Integer(), nullable=True),
        sa.UniqueConstraint("edition_id", "participant_id", name="uq_edition_participant"),
    )
    op.create_index("ix_edition_participant_edition_id", "edition_participant", ["edition_id"])
    op.create_index(
        "ix_edition_participant_participant_id", "edition_participant", ["participant_id"]
    )

    # 6. Performance Statistics
    op.create_table(
        "metric_definition",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("aggregation", sa.String(length=16), nullable=False),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("higher_is_better", sa.Boolean(), nullable=True, default=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("sport_id", "code", name="uq_metric_sport_code"),
    )
    op.create_index("ix_metric_definition_sport_id", "metric_definition", ["sport_id"])
    op.create_index("ix_metric_definition_code", "metric_definition", ["code"])

    op.create_table(
        "performance_stat",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "match_event_id",
            sa.String(length=36),
            sa.ForeignKey("match_event.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "metric_id",
            sa.String(length=36),
            sa.ForeignKey("metric_definition.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("scope", sa.String(length=16), nullable=False),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("is_sample", sa.Boolean(), nullable=False, default=False),
    )
    op.create_index("ix_performance_stat_participant", "performance_stat", ["participant_id"])
    op.create_index("ix_performance_stat_edition", "performance_stat", ["edition_id"])
    op.create_index("ix_performance_stat_metric", "performance_stat", ["metric_id"])
    op.create_index(
        "idx_stat_participant_metric_edition",
        "performance_stat",
        ["participant_id", "metric_id", "edition_id"],
    )

    # 7. Rankings and Records
    op.create_table(
        "ranking_snapshot",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ranking_system", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_ranking_snapshot_sport_id", "ranking_snapshot", ["sport_id"])
    op.create_index("ix_ranking_snapshot_date", "ranking_snapshot", ["as_of_date"])

    op.create_table(
        "ranking_entry",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "snapshot_id",
            sa.String(length=36),
            sa.ForeignKey("ranking_snapshot.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("points", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.UniqueConstraint(
            "snapshot_id", "participant_id", name="uq_ranking_snapshot_participant"
        ),
    )
    op.create_index("ix_ranking_entry_snapshot", "ranking_entry", ["snapshot_id"])
    op.create_index("ix_ranking_entry_participant", "ranking_entry", ["participant_id"])

    op.create_table(
        "record_entry",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "sport_id",
            sa.String(length=36),
            sa.ForeignKey("sport.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("record_type", sa.String(length=32), nullable=False),
        sa.Column(
            "metric_id",
            sa.String(length=36),
            sa.ForeignKey("metric_definition.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "holder_participant_id",
            sa.String(length=36),
            sa.ForeignKey("participant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("achieved_on", sa.Date(), nullable=True),
        sa.Column(
            "edition_id",
            sa.String(length=36),
            sa.ForeignKey("tournament_edition.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_record_entry_sport_id", "record_entry", ["sport_id"])

    # 8. Provenance & Quality
    op.create_table(
        "ingestion_run",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "source_id",
            sa.String(length=36),
            sa.ForeignKey("source.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, default="running"),
        sa.Column("rows_in", sa.Integer(), nullable=False, default=0),
        sa.Column("rows_loaded", sa.Integer(), nullable=False, default=0),
        sa.Column("rows_rejected", sa.Integer(), nullable=False, default=0),
        sa.Column("log", sa.Text(), nullable=True),
    )

    op.create_table(
        "data_quality_issue",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "ingestion_run_id",
            sa.String(length=36),
            sa.ForeignKey("ingestion_run.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("table_name", sa.String(length=64), nullable=False),
        sa.Column("row_ref", sa.String(length=128), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False, default="error"),
        sa.Column("rule_code", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_data_quality_issue_run_id", "data_quality_issue", ["ingestion_run_id"])

    # 9. Create 5 Required Database Views
    for view_sql in ALL_VIEWS:
        op.execute(view_sql)


def downgrade() -> None:
    # 1. Drop views
    view_names = [
        "v_previous_winners",
        "v_win_loss_record",
        "v_participant_edition_totals",
        "v_edition_summary",
        "v_tournament_tracking",
    ]
    for name in view_names:
        op.execute(f"DROP VIEW IF EXISTS {name}")

    # 2. Drop tables in reverse order
    op.drop_table("data_quality_issue")
    op.drop_table("ingestion_run")
    op.drop_table("record_entry")
    op.drop_table("ranking_entry")
    op.drop_table("ranking_snapshot")
    op.drop_table("performance_stat")
    op.drop_table("metric_definition")
    op.drop_table("edition_participant")
    op.drop_table("team_membership")
    op.drop_table("olympic_result")
    op.drop_table("match_side")
    op.drop_table("match_event")
    op.drop_table("stage")
    op.drop_table("tournament_edition")
    op.drop_table("team_profile")
    op.drop_table("player_profile")
    op.drop_table("participant")
    op.drop_table("tournament")
    op.drop_table("source")
    op.drop_table("venue")
    op.drop_table("country")
    op.drop_table("discipline")
    op.drop_table("sport")
