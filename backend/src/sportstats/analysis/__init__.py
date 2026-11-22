"""Analysis package for SportStats statistical engine."""

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
    validate_cross_sport_safety,
)
from sportstats.analysis.rankings import (
    country_medal_distribution,
    ranking_history,
)
from sportstats.analysis.records import (
    records_and_milestones,
)
from sportstats.analysis.trends import (
    format_comparison,
    participation_trends,
    scoring_patterns,
    year_to_year_trend,
)

__all__ = [
    "average_performance",
    "extremes",
    "win_percentage",
    "compare_players",
    "compare_teams",
    "compare_tournaments",
    "validate_cross_sport_safety",
    "CrossSportComparisonError",
    "calculate_z_scores",
    "calculate_percentiles",
    "year_to_year_trend",
    "scoring_patterns",
    "participation_trends",
    "format_comparison",
    "ranking_history",
    "country_medal_distribution",
    "records_and_milestones",
]
