"""SQLAlchemy 2.0 ORM Models for SportStats Common Relational Framework.

Implements the layered relational schema in Section 6 (Reference, Tournament,
Participants, Matches/Events, Performance Stats, Rankings/Records, Provenance/Quality).
"""

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sportstats.db.session import Base


def generate_uuid() -> str:
    """Generate RFC 4122 compliant UUID v4 string for primary keys."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Current UTC timestamp."""
    return datetime.now(timezone.utc)


# ============================================================================
# 6.1 REFERENCE TABLES
# ============================================================================


class Sport(Base):
    """Sport entity representing each distinct athletic discipline."""

    __tablename__ = "sport"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_team_sport: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_individual_sport: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    # Relationships
    disciplines: Mapped[List["Discipline"]] = relationship(
        "Discipline", back_populates="sport", cascade="all, delete-orphan"
    )
    tournaments: Mapped[List["Tournament"]] = relationship("Tournament", back_populates="sport")
    metrics: Mapped[List["MetricDefinition"]] = relationship(
        "MetricDefinition", back_populates="sport", cascade="all, delete-orphan"
    )


class Discipline(Base):
    """Sub-disciplines under parent sports (e.g. Athletics, Swimming under Olympic)."""

    __tablename__ = "discipline"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (UniqueConstraint("sport_id", "code", name="uq_discipline_sport_code"),)

    # Relationships
    sport: Mapped["Sport"] = relationship("Sport", back_populates="disciplines")


class Country(Base):
    """Normalized country reference entity with ISO3 codes."""

    __tablename__ = "country"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    continent: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Relationships
    venues: Mapped[List["Venue"]] = relationship("Venue", back_populates="country")
    participants: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="country"
    )


class Venue(Base):
    """Stadium or arena hosting tournament match events."""

    __tablename__ = "venue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    country_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("country.id", ondelete="SET NULL"), nullable=True
    )
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    country: Mapped[Optional["Country"]] = relationship("Country", back_populates="venues")


class Source(Base):
    """Official or secondary data source documenting full provenance for every fact."""

    __tablename__ = "source"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organisation: Mapped[str] = mapped_column(String(128), nullable=False)  # ICC, FIFA, IOC, etc.
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    access_method: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # api | download | manual_csv | scrape
    tier: Mapped[str] = mapped_column(
        String(16), default="official", nullable=False
    )  # official | secondary
    terms_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ============================================================================
# 6.2 TOURNAMENT INFORMATION & TRACKING
# ============================================================================


class Tournament(Base):
    """Tournament entity definition (e.g. FIFA World Cup, ICC Cricket World Cup)."""

    __tablename__ = "tournament"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    discipline_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("discipline.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    governing_body: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[str] = mapped_column(
        String(16), default="men", nullable=False
    )  # men | women | mixed | open
    level: Mapped[str] = mapped_column(
        String(16), default="world", nullable=False
    )  # world | continental | league | multi_sport
    frequency_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    sport: Mapped["Sport"] = relationship("Sport", back_populates="tournaments")
    editions: Mapped[List["TournamentEdition"]] = relationship(
        "TournamentEdition", back_populates="tournament", cascade="all, delete-orphan"
    )


class TournamentEdition(Base):
    """Specific historical or upcoming edition of a tournament (report Table 2)."""

    __tablename__ = "tournament_edition"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tournament_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tournament.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_label: Mapped[str] = mapped_column(String(64), nullable=False)  # "2023", "2019"
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    host_country_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("country.id", ondelete="SET NULL"), nullable=True
    )
    host_city: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default="completed", nullable=False
    )  # upcoming | ongoing | completed
    participant_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    format_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    matches_or_events_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winner_participant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="SET NULL"), nullable=True
    )
    runner_up_participant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="SET NULL"), nullable=True
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="RESTRICT"), nullable=False
    )
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_edition_date_order"),
        UniqueConstraint("tournament_id", "edition_label", name="uq_tournament_edition_label"),
    )

    # Relationships
    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="editions")
    stages: Mapped[List["Stage"]] = relationship(
        "Stage", back_populates="edition", cascade="all, delete-orphan"
    )
    matches: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", back_populates="edition", cascade="all, delete-orphan"
    )
    edition_participants: Mapped[List["EditionParticipant"]] = relationship(
        "EditionParticipant", back_populates="edition", cascade="all, delete-orphan"
    )
    source: Mapped["Source"] = relationship("Source")


# ============================================================================
# 6.3 PARTICIPANTS (Teams and Players in One Common Abstraction)
# ============================================================================


class Participant(Base):
    """Universal participant abstraction representing teams, individual players, pairs, and athletes."""

    __tablename__ = "participant"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # team | player | pair | athlete
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    country_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("country.id", ondelete="SET NULL"), nullable=True
    )
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_ids: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    country: Mapped[Optional["Country"]] = relationship("Country", back_populates="participants")
    player_profile: Mapped[Optional["PlayerProfile"]] = relationship(
        "PlayerProfile", back_populates="participant", uselist=False, cascade="all, delete-orphan"
    )
    team_profile: Mapped[Optional["TeamProfile"]] = relationship(
        "TeamProfile", back_populates="participant", uselist=False, cascade="all, delete-orphan"
    )


class PlayerProfile(Base):
    """Personal athlete information for individual participants."""

    __tablename__ = "player_profile"

    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    role_or_position: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    participant: Mapped["Participant"] = relationship(
        "Participant", back_populates="player_profile"
    )


class TeamProfile(Base):
    """Team details for national, franchise, or club squads."""

    __tablename__ = "team_profile"

    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), primary_key=True
    )
    team_type: Mapped[str] = mapped_column(
        String(16), default="national", nullable=False
    )  # national | club | franchise
    short_code: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Relationships
    participant: Mapped["Participant"] = relationship("Participant", back_populates="team_profile")


class TeamMembership(Base):
    """Mapping of players to teams per tournament edition or season."""

    __tablename__ = "team_membership"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    team_participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tournament_edition.id", ondelete="CASCADE"), nullable=True
    )
    role: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )  # Captain, Goalkeeper, Raider, etc.


class EditionParticipant(Base):
    """Entry roster of participants in a specific tournament edition."""

    __tablename__ = "edition_participant"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    edition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tournament_edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    group_label: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    final_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("edition_id", "participant_id", name="uq_edition_participant"),
    )

    # Relationships
    edition: Mapped["TournamentEdition"] = relationship(
        "TournamentEdition", back_populates="edition_participants"
    )
    participant: Mapped["Participant"] = relationship("Participant")


# ============================================================================
# 6.4 MATCHES AND EVENTS
# ============================================================================


class Stage(Base):
    """Tournament progression stage (Group, Knockout, Final, Heats)."""

    __tablename__ = "stage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    edition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tournament_edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    type: Mapped[str] = mapped_column(
        String(16), default="knockout", nullable=False
    )  # group | league | knockout | round | heat | final

    # Relationships
    edition: Mapped["TournamentEdition"] = relationship(
        "TournamentEdition", back_populates="stages"
    )
    matches: Mapped[List["MatchEvent"]] = relationship("MatchEvent", back_populates="stage")


class MatchEvent(Base):
    """Individual match, game, or athletic contest."""

    __tablename__ = "match_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    edition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tournament_edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("stage.id", ondelete="SET NULL"), nullable=True
    )
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    discipline_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("discipline.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("venue.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16), default="completed", nullable=False
    )  # scheduled | live | completed | abandoned
    winner_participant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="SET NULL"), nullable=True
    )
    is_draw: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="RESTRICT"), nullable=False
    )
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    edition: Mapped["TournamentEdition"] = relationship(
        "TournamentEdition", back_populates="matches"
    )
    stage: Mapped[Optional["Stage"]] = relationship("Stage", back_populates="matches")
    sides: Mapped[List["MatchSide"]] = relationship(
        "MatchSide", back_populates="match_event", cascade="all, delete-orphan"
    )
    source: Mapped["Source"] = relationship("Source")


class MatchSide(Base):
    """Side/contestant in a match event holding sport-specific score details."""

    __tablename__ = "match_side"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    match_event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("match_event.id", ondelete="CASCADE"), nullable=False, index=True
    )
    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    side_index: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 0: Home / Side A, 1: Away / Side B
    score_primary: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    score_detail: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # Cricket overs/wickets, Tennis sets, etc.
    is_winner: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        UniqueConstraint("match_event_id", "participant_id", name="uq_match_side_participant"),
    )

    # Relationships
    match_event: Mapped["MatchEvent"] = relationship("MatchEvent", back_populates="sides")
    participant: Mapped["Participant"] = relationship("Participant")


class OlympicResult(Base):
    """Event finish result and medal placement in Olympic disciplines."""

    __tablename__ = "olympic_result"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    edition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tournament_edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    discipline_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("discipline.id", ondelete="CASCADE"), nullable=False
    )
    event_name: Mapped[str] = mapped_column(
        String(128), nullable=False
    )  # "Men's 100m", "Women's All-Around"
    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False
    )
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    medal: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True
    )  # gold | silver | bronze
    result_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    result_unit: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True
    )  # seconds, meters, points
    is_world_record: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_olympic_record: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# ============================================================================
# 6.5 PERFORMANCE STATISTICS (Typed EAV-style Store)
# ============================================================================


class MetricDefinition(Base):
    """Catalogue definition of statistical metrics per sport."""

    __tablename__ = "metric_definition"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # batting, bowling, attack, defense, etc.
    aggregation: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # sum, avg, max, min, ratio, custom
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    higher_is_better: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("sport_id", "code", name="uq_metric_sport_code"),)

    # Relationships
    sport: Mapped["Sport"] = relationship("Sport", back_populates="metrics")


class PerformanceStat(Base):
    """Atomic statistical observation linked to participant, edition, metric and source."""

    __tablename__ = "performance_stat"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tournament_edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    match_event_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("match_event.id", ondelete="CASCADE"), nullable=True
    )
    metric_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("metric_definition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    scope: Mapped[str] = mapped_column(String(16), nullable=False)  # match | edition | career
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="RESTRICT"), nullable=False
    )
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_stat_participant_metric_edition", "participant_id", "metric_id", "edition_id"),
    )

    # Relationships
    participant: Mapped["Participant"] = relationship("Participant")
    metric: Mapped["MetricDefinition"] = relationship("MetricDefinition")
    source: Mapped["Source"] = relationship("Source")


# ============================================================================
# 6.6 RANKINGS AND RECORDS (Objective O6)
# ============================================================================


class RankingSnapshot(Base):
    """Point-in-time official ranking publication snapshot."""

    __tablename__ = "ranking_snapshot"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ranking_system: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # "ICC Men's ODI", "FIFA Men's World Ranking"
    category: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # "Team", "Singles", "Batting"
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="RESTRICT"), nullable=False
    )

    # Relationships
    entries: Mapped[List["RankingEntry"]] = relationship(
        "RankingEntry", back_populates="snapshot", cascade="all, delete-orphan"
    )


class RankingEntry(Base):
    """Rank position of participant in a ranking snapshot."""

    __tablename__ = "ranking_entry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    snapshot_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ranking_snapshot.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)

    __table_args__ = (
        UniqueConstraint("snapshot_id", "participant_id", name="uq_ranking_snapshot_participant"),
    )

    # Relationships
    snapshot: Mapped["RankingSnapshot"] = relationship("RankingSnapshot", back_populates="entries")
    participant: Mapped["Participant"] = relationship("Participant")


class RecordEntry(Base):
    """Historical athletic milestone or all-time record entry."""

    __tablename__ = "record_entry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sport.id", ondelete="CASCADE"), nullable=False, index=True
    )
    record_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # world | olympic | tournament | career
    metric_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("metric_definition.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    holder_participant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("participant.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[Optional[float]] = mapped_column(Numeric(14, 4), nullable=True)
    achieved_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    edition_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tournament_edition.id", ondelete="SET NULL"), nullable=True
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="RESTRICT"), nullable=False
    )


# ============================================================================
# 6.7 PROVENANCE, AUDIT AND QUALITY
# ============================================================================


class IngestionRun(Base):
    """Audit log of dataset collection and import runs."""

    __tablename__ = "ingestion_run"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("source.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), default="running", nullable=False
    )  # running | success | partial | failed
    rows_in: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    issues: Mapped[List["DataQualityIssue"]] = relationship(
        "DataQualityIssue", back_populates="ingestion_run", cascade="all, delete-orphan"
    )


class DataQualityIssue(Base):
    """Itemized record validation or range rejection error."""

    __tablename__ = "data_quality_issue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    ingestion_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("ingestion_run.id", ondelete="CASCADE"), nullable=True, index=True
    )
    table_name: Mapped[str] = mapped_column(String(64), nullable=False)
    row_ref: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    severity: Mapped[str] = mapped_column(
        String(16), default="error", nullable=False
    )  # warning | error | critical
    rule_code: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # RANGE_PCT, MISSING_SOURCE, etc.
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    ingestion_run: Mapped[Optional["IngestionRun"]] = relationship(
        "IngestionRun", back_populates="issues"
    )
