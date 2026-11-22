"""Property-based testing using Hypothesis for statistical invariants (Part 14)."""

import math

from hypothesis import given
from hypothesis import strategies as st

from sportstats.metrics.formulas import (
    calculate_draw_percentage,
    calculate_loss_percentage,
    calculate_win_percentage,
)


@given(
    wins=st.integers(min_value=0, max_value=500),
    losses=st.integers(min_value=0, max_value=500),
    draws=st.integers(min_value=0, max_value=500),
)
def test_win_loss_draw_percentage_sum_invariant(wins: int, losses: int, draws: int):
    """Property Invariant: For any non-empty match record,

    win_pct + loss_pct + draw_pct == 100.0 (within rounding precision ± 0.05).
    """
    total = wins + losses + draws
    if total == 0:
        assert calculate_win_percentage(wins, total) is None
        assert calculate_loss_percentage(losses, total) is None
        assert calculate_draw_percentage(draws, total) is None
        return

    win_pct = calculate_win_percentage(wins, total, round_digits=4)
    loss_pct = calculate_loss_percentage(losses, total, round_digits=4)
    draw_pct = calculate_draw_percentage(draws, total, round_digits=4)

    assert win_pct is not None
    assert loss_pct is not None
    assert draw_pct is not None

    # Each individual percentage is bounded between 0 and 100
    assert 0.0 <= win_pct <= 100.0
    assert 0.0 <= loss_pct <= 100.0
    assert 0.0 <= draw_pct <= 100.0

    # The sum of percentages must equal 100.0
    total_pct = win_pct + loss_pct + draw_pct
    assert math.isclose(total_pct, 100.0, abs_tol=1e-3)
