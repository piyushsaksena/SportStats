"""Pure mathematical formulas for sports statistics (Report Table 4 & Section 7).

All functions are pure, deterministic, and zero-division safe:
if the denominator is zero or invalid, they return None (never raise exceptions,
and never return 0.0 unless the true calculated value is 0.0).
"""

from typing import List, Optional, Union

Number = Union[int, float]


# ============================================================================
# 9.1 CORE MEASURES (Report Table 4)
# ============================================================================


def calculate_total(values: List[Number]) -> Optional[float]:
    """Calculate the total (sum) of a collection of values.

    Formula: Total = Σ values
    Returns None if values list is empty.
    """
    if not values:
        return None
    return float(sum(values))


def calculate_average(values: List[Number]) -> Optional[float]:
    """Calculate the arithmetic mean.

    Formula: Average = (Σ values) ÷ count
    Returns None if count is zero.
    """
    if not values:
        return None
    return round(float(sum(values)) / len(values), 2)


def calculate_win_percentage(
    wins: int, total_matches: int, round_digits: int = 2
) -> Optional[float]:
    """Calculate win percentage from wins and total matches.

    Formula: Win % = (wins ÷ total_matches) × 100
    Returns None if total_matches is <= 0.
    """
    if total_matches <= 0 or wins < 0:
        return None
    pct = (wins / total_matches) * 100.0
    return round(pct, round_digits)


def calculate_loss_percentage(
    losses: int, total_matches: int, round_digits: int = 2
) -> Optional[float]:
    """Calculate loss percentage from losses and total matches.

    Formula: Loss % = (losses ÷ total_matches) × 100
    Returns None if total_matches is <= 0.
    """
    if total_matches <= 0 or losses < 0:
        return None
    pct = (losses / total_matches) * 100.0
    return round(pct, round_digits)


def calculate_draw_percentage(
    draws: int, total_matches: int, round_digits: int = 2
) -> Optional[float]:
    """Calculate draw/tie percentage from draws and total matches.

    Formula: Draw % = (draws ÷ total_matches) × 100
    Returns None if total_matches is <= 0.
    """
    if total_matches <= 0 or draws < 0:
        return None
    pct = (draws / total_matches) * 100.0
    return round(pct, round_digits)


# ============================================================================
# 9.2 SPORT-SPECIFIC MEASURES
# ============================================================================


def calculate_batting_average(runs: int, dismissals: int) -> Optional[float]:
    """Cricket Batting Average.

    Formula: Batting Average = runs ÷ dismissals
    Note: Returns None if dismissals is 0 (batter is "not out"), not an error.
    """
    if dismissals <= 0 or runs < 0:
        return None
    return round(runs / dismissals, 2)


def calculate_bowling_average(runs_conceded: int, wickets: int) -> Optional[float]:
    """Cricket Bowling Average.

    Formula: Bowling Average = runs_conceded ÷ wickets
    Note: Lower is better. Returns None if wickets is 0.
    """
    if wickets <= 0 or runs_conceded < 0:
        return None
    return round(runs_conceded / wickets, 2)


def calculate_strike_rate(runs: int, balls_faced: int) -> Optional[float]:
    """Cricket Batting Strike Rate.

    Formula: Strike Rate = (runs ÷ balls_faced) × 100
    Returns None if balls_faced is <= 0.
    """
    if balls_faced <= 0 or runs < 0:
        return None
    return round((runs / balls_faced) * 100.0, 2)


def calculate_economy_rate(runs_conceded: int, overs_bowled: float) -> Optional[float]:
    """Cricket Bowling Economy Rate.

    Formula: Economy Rate = runs_conceded ÷ overs_bowled
    Note: Lower is better. Returns None if overs_bowled is <= 0.
    """
    if overs_bowled <= 0 or runs_conceded < 0:
        return None
    return round(runs_conceded / overs_bowled, 2)


def calculate_passing_accuracy(completed_passes: int, attempted_passes: int) -> Optional[float]:
    """Football Passing Accuracy Percentage.

    Formula: Passing Accuracy = (completed_passes ÷ attempted_passes) × 100
    Returns None if attempted_passes <= 0.
    """
    if attempted_passes <= 0 or completed_passes < 0:
        return None
    return round((completed_passes / attempted_passes) * 100.0, 2)


def calculate_field_goal_percentage(made: int, attempted: int) -> Optional[float]:
    """Basketball Field Goal Percentage (FG%).

    Formula: FG% = (made ÷ attempted) × 100
    Returns None if attempted <= 0.
    """
    if attempted <= 0 or made < 0:
        return None
    return round((made / attempted) * 100.0, 2)


def calculate_three_point_percentage(made: int, attempted: int) -> Optional[float]:
    """Basketball 3-Point Percentage (3P%).

    Formula: 3P% = (made ÷ attempted) × 100
    Returns None if attempted <= 0.
    """
    if attempted <= 0 or made < 0:
        return None
    return round((made / attempted) * 100.0, 2)


def calculate_free_throw_percentage(made: int, attempted: int) -> Optional[float]:
    """Basketball Free Throw Percentage (FT%).

    Formula: FT% = (made ÷ attempted) × 100
    Returns None if attempted <= 0.
    """
    if attempted <= 0 or made < 0:
        return None
    return round((made / attempted) * 100.0, 2)


def calculate_first_serve_percentage(first_serves_in: int, total_serves: int) -> Optional[float]:
    """Tennis First Serve Percentage.

    Formula: First Serve % = (first_serves_in ÷ total_serves) × 100
    Returns None if total_serves <= 0.
    """
    if total_serves <= 0 or first_serves_in < 0:
        return None
    return round((first_serves_in / total_serves) * 100.0, 2)


def calculate_break_point_percentage(converted: int, opportunities: int) -> Optional[float]:
    """Tennis Break Points Converted Percentage.

    Formula: Break Point % = (converted ÷ opportunities) × 100
    Returns None if opportunities <= 0.
    """
    if opportunities <= 0 or converted < 0:
        return None
    return round((converted / opportunities) * 100.0, 2)


def calculate_raid_success_percentage(successful_raids: int, total_raids: int) -> Optional[float]:
    """Kabaddi Raid Success Percentage.

    Formula: Raid Success % = (successful_raids ÷ total_raids) × 100
    Returns None if total_raids <= 0.
    """
    if total_raids <= 0 or successful_raids < 0:
        return None
    return round((successful_raids / total_raids) * 100.0, 2)


def calculate_tackle_success_percentage(
    successful_tackles: int, total_tackles: int
) -> Optional[float]:
    """Kabaddi Tackle Success Percentage.

    Formula: Tackle Success % = (successful_tackles ÷ total_tackles) × 100
    Returns None if total_tackles <= 0.
    """
    if total_tackles <= 0 or successful_tackles < 0:
        return None
    return round((successful_tackles / total_tackles) * 100.0, 2)
