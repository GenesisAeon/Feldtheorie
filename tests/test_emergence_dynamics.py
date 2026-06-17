"""Tests for the Emergence Dynamics analysis module."""
from __future__ import annotations

from analysis.emergence_dynamics import (
    EmergenceParams,
    simulate_concept_spread,
    simulate_stabilization,
)


class TestStabilization:
    def test_converges_below_critical_beta(self) -> None:
        """Below β_critical, concepts should stabilize (not diverge)."""
        params = EmergenceParams(beta=20.0, sigma_phi=0.0625, damping=0.1)
        result = simulate_stabilization(params, steps=200)
        # Activation should settle to a finite value
        assert result["converged"] is True
        assert result["final_activation"] < 100.0

    def test_runaway_above_critical_without_damping(self) -> None:
        """Above β_critical with zero damping, activation should run away."""
        params = EmergenceParams(beta=50.0, sigma_phi=0.0625, damping=0.0)
        result = simulate_stabilization(params, steps=200)
        assert result["converged"] is False

    def test_damping_prevents_runaway(self) -> None:
        """Even above β_critical, sufficient damping should stabilize."""
        params = EmergenceParams(beta=50.0, sigma_phi=0.0625, damping=0.5)
        result = simulate_stabilization(params, steps=200)
        assert result["converged"] is True

    def test_history_length_matches_steps(self) -> None:
        params = EmergenceParams(beta=20.0, sigma_phi=0.0625, damping=0.1)
        result = simulate_stabilization(params, steps=50)
        assert len(result["history"]) == 50


class TestConceptSpread:
    def test_spread_increases_with_beta(self) -> None:
        """Higher β should lead to faster spread."""
        low = simulate_concept_spread(beta=10.0, v_rig=1.352, steps=50)
        high = simulate_concept_spread(beta=37.6, v_rig=1.352, steps=50)
        # Higher beta should reach more nodes
        assert high["peak_spread"] >= low["peak_spread"]

    def test_spread_bounded(self) -> None:
        """Spread fraction should never exceed 1.0."""
        result = simulate_concept_spread(beta=100.0, v_rig=1.352, steps=100)
        assert all(0.0 <= v <= 1.0 for v in result["spread_history"])

    def test_zero_beta_no_spread(self) -> None:
        """With β=0, no significant spread should occur."""
        result = simulate_concept_spread(beta=0.0, v_rig=1.352, steps=50)
        assert result["peak_spread"] < 0.1


class TestEmergenceParams:
    def test_defaults(self) -> None:
        p = EmergenceParams()
        assert p.beta == 37.6
        assert p.sigma_phi == 0.0625
        assert p.damping == 0.1

    def test_custom_values(self) -> None:
        p = EmergenceParams(beta=10.0, sigma_phi=0.1, damping=0.5)
        assert p.beta == 10.0
        assert p.sigma_phi == 0.1
        assert p.damping == 0.5
