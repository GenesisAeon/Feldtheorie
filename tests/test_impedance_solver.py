"""Tests for the adaptive impedance solver (σ(β(R-Θ)))."""

import math

from models.impedance_solver import (
    BASELINE_BETA,
    falsification_gap,
    impedance_from_beta,
    simulate_impedance_trajectory,
    solve_impedance_state,
)
from models.consciousness_integration import calculate_impedance


def test_impedance_scaling_with_beta():
    """Impedance should scale linearly with β in the null model."""
    base_impedance = calculate_impedance()
    z_at_baseline = impedance_from_beta(beta=BASELINE_BETA)
    z_at_double = impedance_from_beta(beta=BASELINE_BETA * 2)

    assert math.isclose(z_at_baseline, base_impedance, rel_tol=1e-9)
    assert z_at_double > z_at_baseline
    assert math.isclose(z_at_double, 2 * z_at_baseline, rel_tol=1e-9)


def test_logistic_activation_and_damping():
    """Higher β and ζ reduce impedance through stronger activation."""
    state_low_beta = solve_impedance_state(beta=3.0, R=1.2, Theta=1.0, zeta=0.3)
    state_high_beta = solve_impedance_state(beta=8.0, R=1.2, Theta=1.0, zeta=0.3)

    assert 0 < state_low_beta.activation < state_high_beta.activation <= 1
    assert state_low_beta.damped_impedance_z < state_low_beta.null_impedance_z
    assert state_high_beta.damped_impedance_z < state_high_beta.null_impedance_z

    # Higher β should yield stronger relative damping (lower impedance ratio)
    damping_ratio_low = state_low_beta.damped_impedance_z / state_low_beta.null_impedance_z
    damping_ratio_high = state_high_beta.damped_impedance_z / state_high_beta.null_impedance_z
    assert damping_ratio_high < damping_ratio_low


def test_impedance_trajectory_is_sorted_with_beta():
    """Trajectory preserves ordering of β and activation bounds."""
    betas = [3.0, 4.8, 6.5, 9.0]
    trajectory = simulate_impedance_trajectory(betas, R=1.5, Theta=1.0, zeta=0.25)

    activations = [state.activation for state in trajectory]
    assert activations == sorted(activations)
    assert all(0.0 <= a <= 1.0 for a in activations)


def test_falsification_gap_improves_over_null_model():
    """Adaptive damping should reduce MSE relative to the null model."""
    base_impedance = calculate_impedance()
    trajectory = simulate_impedance_trajectory(
        betas=[3.0, 5.0, 7.0, 9.0], R=1.3, Theta=1.0, zeta=0.4
    )

    gap = falsification_gap(trajectory, target_impedance=base_impedance)

    assert gap > 0  # Adaptive model beats null scaling
    assert isinstance(gap, float)
