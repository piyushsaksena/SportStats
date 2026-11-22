"""Unit tests for pure mathematical formulas (Section 9.1, 9.2, and Appendix B)."""

from sportstats.metrics.formulas import (
    calculate_average,
    calculate_batting_average,
    calculate_bowling_average,
    calculate_break_point_percentage,
    calculate_draw_percentage,
    calculate_economy_rate,
    calculate_field_goal_percentage,
    calculate_first_serve_percentage,
    calculate_free_throw_percentage,
    calculate_loss_percentage,
    calculate_passing_accuracy,
    calculate_raid_success_percentage,
    calculate_strike_rate,
    calculate_tackle_success_percentage,
    calculate_three_point_percentage,
    calculate_total,
    calculate_win_percentage,
)

# ============================================================================
# APPENDIX B ACCEPTANCE TEST CASES
# ============================================================================


def test_appendix_b_case_1_team_record_percentages():
    """Appendix B.1: Team with 20 matches, 14 wins, 4 losses, 2 draws.

    Expected: win % = 70.0, loss % = 20.0, draw % = 10.0.
    """
    total = 20
    assert calculate_win_percentage(14, total) == 70.0
    assert calculate_loss_percentage(4, total) == 20.0
    assert calculate_draw_percentage(2, total) == 10.0


def test_appendix_b_case_2_cricket_batting_average():
    """Appendix B.2: Batter with 512 runs and 8 dismissals -> 64.0.

    With 0 dismissals (not out) -> None, never zero and never an error.
    """
    assert calculate_batting_average(512, 8) == 64.0
    assert calculate_batting_average(512, 0) is None
    assert calculate_batting_average(0, 0) is None


def test_appendix_b_case_3_cricket_strike_rate():
    """Appendix B.3: Batter with 478 runs off 400 balls -> strike rate = 119.5."""
    assert calculate_strike_rate(478, 400) == 119.5


def test_appendix_b_case_4_basketball_field_goal_percentage():
    """Appendix B.4: Basketball player with 45 made of 90 field goals -> fg_pct = 50.0."""
    assert calculate_field_goal_percentage(45, 90) == 50.0


# ============================================================================
# ZERO-DIVISION AND BOUNDARY VERIFICATION
# ============================================================================


def test_zero_division_behavior_all_formulas_return_none():
    """Verify that all formulas safely return None upon zero or negative denominators."""
    assert calculate_total([]) is None
    assert calculate_average([]) is None
    assert calculate_win_percentage(5, 0) is None
    assert calculate_loss_percentage(5, 0) is None
    assert calculate_draw_percentage(1, 0) is None
    assert calculate_batting_average(100, 0) is None
    assert calculate_bowling_average(45, 0) is None
    assert calculate_strike_rate(100, 0) is None
    assert calculate_economy_rate(50, 0.0) is None
    assert calculate_passing_accuracy(30, 0) is None
    assert calculate_field_goal_percentage(10, 0) is None
    assert calculate_three_point_percentage(5, 0) is None
    assert calculate_free_throw_percentage(8, 0) is None
    assert calculate_first_serve_percentage(40, 0) is None
    assert calculate_break_point_percentage(3, 0) is None
    assert calculate_raid_success_percentage(12, 0) is None
    assert calculate_tackle_success_percentage(6, 0) is None


def test_core_totals_and_averages():
    """Verify core measures: total and average calculations."""
    vals = [10, 20, 30, 40]
    assert calculate_total(vals) == 100.0
    assert calculate_average(vals) == 25.0


def test_bowling_average_and_economy_rate():
    """Verify bowling metrics: average and economy rate."""
    # 250 runs conceded for 10 wickets -> 25.0 average
    assert calculate_bowling_average(250, 10) == 25.0
    # 48 runs conceded in 10.0 overs -> 4.8 economy
    assert calculate_economy_rate(48, 10.0) == 4.8


def test_passing_accuracy():
    """Verify football passing accuracy."""
    # 450 completed of 500 attempted -> 90.0%
    assert calculate_passing_accuracy(450, 500) == 90.0


def test_tennis_serve_and_break_points():
    """Verify tennis first serve % and break point conversion %."""
    assert calculate_first_serve_percentage(68, 100) == 68.0
    assert calculate_break_point_percentage(4, 10) == 40.0


def test_kabaddi_raid_and_tackle_success():
    """Verify kabaddi raid and tackle success percentages."""
    # 15 successful raids out of 25 -> 60.0%
    assert calculate_raid_success_percentage(15, 25) == 60.0
    # 8 successful tackles out of 16 -> 50.0%
    assert calculate_tackle_success_percentage(8, 16) == 50.0
