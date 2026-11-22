"""Pydantic schemas for SportStats REST API data models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SportOut(BaseModel):
    id: str
    code: str
    name: str
    is_team_sport: bool
    is_individual_sport: bool
    tournament_count: int = 0
    metric_count: int = 0
    notes: Optional[str] = None


class MetricOut(BaseModel):
    id: str
    sport_code: str
    code: str
    name: str
    unit: Optional[str] = None
    category: str
    aggregation: str
    higher_is_better: Optional[bool] = None
    formula: Optional[str] = None
    description: Optional[str] = None


class TournamentOut(BaseModel):
    id: str
    sport_code: str
    name: str
    governing_body: str
    gender: str
    level: str
    frequency_years: Optional[int] = None
    edition_count: int = 0
    latest_edition: Optional[str] = None
    status: Optional[str] = None


class EditionOut(BaseModel):
    id: str
    tournament_id: str
    tournament_name: str
    sport_code: str
    edition_label: str
    year: int
    host_country_iso3: Optional[str] = None
    host_city: Optional[str] = None
    start_date: date
    end_date: date
    status: str
    participant_count: int
    format_description: Optional[str] = None
    matches_or_events_count: Optional[int] = None
    winner: Optional[str] = None
    runner_up: Optional[str] = None
    is_sample: bool = False


class MatchOut(BaseModel):
    id: str
    edition_id: str
    stage: str
    scheduled_at: datetime
    venue: Optional[str] = None
    status: str
    participant_a: str
    participant_b: str
    score_a: Optional[str] = None
    score_b: Optional[str] = None
    winner: Optional[str] = None
    is_draw: bool = False
    result_summary: Optional[str] = None
    is_sample: bool = False


class ParticipantOut(BaseModel):
    id: str
    type: str
    name: str
    sport_code: str
    country_iso3: Optional[str] = None
    role_or_position: Optional[str] = None
    is_sample: bool = False


class StandingOut(BaseModel):
    rank: int
    participant_id: str
    participant_name: str
    played: int = 0
    won: int = 0
    lost: int = 0
    drawn: int = 0
    points: Optional[float] = None
    win_percentage: Optional[float] = None


class StatOut(BaseModel):
    id: str
    participant_name: str
    tournament_name: Optional[str] = None
    edition_label: Optional[str] = None
    metric_code: str
    metric_name: str
    value: float
    unit: Optional[str] = None
    scope: str
    is_sample: bool = False


class SourceOut(BaseModel):
    id: str
    organisation: str
    name: str
    url: str
    access_method: str
    tier: str
    terms_note: Optional[str] = None
    is_verified: bool
    retrieved_at: datetime


class RankingOut(BaseModel):
    ranking_system: str
    category: str
    as_of_date: date
    rank: int
    participant_name: str
    points: Optional[float] = None


class OlympicMedalOut(BaseModel):
    country_iso3: str
    country_name: Optional[str] = None
    gold: int = 0
    silver: int = 0
    bronze: int = 0
    total: int = 0
    share_pct: Optional[float] = None
