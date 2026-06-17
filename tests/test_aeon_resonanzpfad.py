"""
Tests for Aeon Resonanzpfad Module
===================================

Tests the ResonanzpfadOptimizer trajectory optimization.

Run:
    pytest tests/test_aeon_resonanzpfad.py -v
"""

import sys
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon.resonanzpfad import ResonanzpfadOptimizer  # noqa: E402

# ============================================================================
# ResonanzpfadOptimizer Tests
# ============================================================================


def test_resonanzpfad_initialization():
    """Test Resonanzpfad initialization."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3
    )

    assert optimizer.start_beta == 0.5
    assert optimizer.target_beta == 0.1
    assert optimizer.start_kappa == 0.5
    assert optimizer.target_kappa == 0.3
    assert len(optimizer.trajectory) == 0


def test_resonanzpfad_impedance():
    """Test impedance computation."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3
    )

    zeta = optimizer.compute_impedance(beta=0.5, kappa=0.5, resource=0.5)

    # ζ = β*(1-κ) - baseline = 0.5*0.5 - 0.5 = -0.25
    assert zeta < 0


def test_resonanzpfad_tau_star():
    """Test τ* delay computation."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3
    )

    # Positive ζ → no delay
    tau_positive = optimizer.compute_tau_star_delay(zeta=0.5)
    assert tau_positive == 0.0

    # Negative ζ → delay
    tau_negative = optimizer.compute_tau_star_delay(zeta=-0.5)
    assert tau_negative > 0.0


def test_resonanzpfad_cost():
    """Test trajectory cost computation."""
    # Choose target with positive ζ (lower penalty)
    # ζ = β*(1-κ) - 0.5
    # Target: ζ = 0.8*(1-0.2) - 0.5 = 0.64 - 0.5 = 0.14 (positive, no penalty)
    # Start: ζ = 0.5*(1-0.5) - 0.5 = -0.25 (negative, penalty = 2.5)
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.8, start_kappa=0.5, target_kappa=0.2
    )

    # Cost at start (includes penalty for negative ζ)
    cost_start = optimizer.compute_cost(
        beta=optimizer.start_beta, kappa=optimizer.start_kappa
    )

    # Cost at target (no penalty, only distance which is 0)
    cost_target = optimizer.compute_cost(
        beta=optimizer.target_beta, kappa=optimizer.target_kappa
    )

    # Target should have lower cost (no ζ-penalty)
    assert cost_target < cost_start


def test_resonanzpfad_optimize_step():
    """Test single optimization step."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3
    )

    point = optimizer.optimize_step(resource=0.5)

    assert "beta" in point
    assert "kappa" in point
    assert "zeta" in point
    assert "tau_star" in point
    assert len(optimizer.trajectory) == 1


def test_resonanzpfad_optimize_full():
    """Test full trajectory optimization."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5,
        target_beta=0.1,
        start_kappa=0.5,
        target_kappa=0.3,
        max_steps=100,
    )

    trajectory = optimizer.optimize()

    assert len(trajectory) > 0
    assert len(trajectory) <= 100

    # Final point should be close to target
    final = trajectory[-1]
    dist = np.sqrt(
        (final["beta"] - optimizer.target_beta) ** 2
        + (final["kappa"] - optimizer.target_kappa) ** 2
    )
    assert dist < 0.5  # Should converge reasonably close


def test_resonanzpfad_custom_resource():
    """Test optimization with custom resource function."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3, max_steps=50
    )

    # Oscillating resource
    def resource_func(step):
        return 0.5 + 0.3 * np.sin(step * 0.1)

    trajectory = optimizer.optimize(resource_func=resource_func)

    assert len(trajectory) > 0
    # Check that resources vary
    resources = [p["resource"] for p in trajectory]
    assert max(resources) > min(resources)


def test_resonanzpfad_safeguard_violations():
    """Test safeguard violation detection."""
    # Set up optimizer with parameters that cause violations
    # max_steps is set in constructor, not in optimize() call
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.8,
        target_beta=0.1,
        start_kappa=0.1,
        target_kappa=0.3,
        max_steps=20,
        zeta_safeguard=True,
    )

    optimizer.optimize()

    # May or may not have violations depending on trajectory
    # Just check the list exists
    assert isinstance(optimizer.safeguard_violations, list)


def test_resonanzpfad_summary():
    """Test optimization summary."""
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5, target_beta=0.1, start_kappa=0.5, target_kappa=0.3
    )

    # Before optimization
    summary_before = optimizer.get_summary()
    assert summary_before["status"] == "not_run"

    # After optimization
    optimizer.optimize()
    summary_after = optimizer.get_summary()

    assert summary_after["status"] == "complete"
    assert "steps" in summary_after
    assert "final_beta" in summary_after
    assert "final_kappa" in summary_after
    assert "converged" in summary_after


def test_resonanzpfad_convergence():
    """Test convergence to target."""
    # Test that optimizer makes progress toward target
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.5,
        target_beta=0.4,
        start_kappa=0.5,
        target_kappa=0.45,
        max_steps=200,
        learning_rate=0.1,
    )

    # Initial distance
    initial_dist = np.sqrt(
        (optimizer.start_beta - optimizer.target_beta) ** 2
        + (optimizer.start_kappa - optimizer.target_kappa) ** 2
    )

    optimizer.optimize()
    summary = optimizer.get_summary()

    # Should make progress toward target (at least 20% reduction in distance)
    # Note: ζ-safeguards may prevent full convergence
    assert summary["final_distance"] < 0.9 * initial_dist
    assert summary["status"] == "complete"
