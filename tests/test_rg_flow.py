"""Unit tests for RG Flow Simulator.

Tests phenomenological RG flow implementation for UTAC β-mechanik.

Author: Claude Code
Date: 2025-11-12
Version: 1.0.0
"""

import numpy as np
import pytest

from models.rg_flow_simulator import (
    FlowVariant,
    RGFlowConfig,
    RGFlowSimulator,
    compare_to_phi_ladder,
    context_dependent_flow,
    cubic_root_amplification_flow,
    linear_phi_attractor,
    multi_basin_flow,
    phi_convergence_score,
    polynomial_flow,
)
from models.utac_type6_implosive import BETA_FIXPOINT_PHI3, BETA_STEPS


# ═══════════════════════════════════════════════════════════════
# FLOW FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════


class TestFlowFunctions:
    """Test individual flow function implementations."""

    def test_linear_phi_attractor_converges(self):
        """Linear flow should converge to fixpoint."""
        beta_initial = 3.5
        fixpoint = BETA_FIXPOINT_PHI3  # ~4.236

        # Flow should be negative (pulling toward higher β)
        flow = linear_phi_attractor(beta_initial, alpha=0.5, fixpoint=fixpoint)
        assert flow < 0, "Flow should be negative when β < fixpoint"

        # At fixpoint, flow should be zero
        flow_at_fixpoint = linear_phi_attractor(
            fixpoint, alpha=0.5, fixpoint=fixpoint
        )
        assert abs(flow_at_fixpoint) < 1e-6, "Flow at fixpoint should be zero"

    def test_polynomial_flow_symmetry(self):
        """Polynomial flow should have correct sign."""
        fixpoint = BETA_FIXPOINT_PHI3

        # Below fixpoint → positive flow (toward fixpoint)
        flow_below = polynomial_flow(3.0, gamma=0.1, fixpoint=fixpoint, exponent=3)
        assert flow_below < 0, "Flow should be negative below fixpoint"

        # Above fixpoint → negative flow (toward fixpoint)
        flow_above = polynomial_flow(5.0, gamma=0.1, fixpoint=fixpoint, exponent=3)
        assert flow_above > 0, "Flow should be positive above fixpoint"

    def test_multi_basin_weighted_flow(self):
        """Multi-basin flow should combine all attractors."""
        beta = 3.0
        flow = multi_basin_flow(beta, alpha=0.5)

        # Flow should be finite
        assert np.isfinite(flow), "Flow should be finite"
        assert abs(flow) < 10.0, "Flow magnitude should be reasonable"

    def test_context_dependent_modulation(self):
        """Context flow should be modulated by R/Θ and ζ."""
        beta = 3.5
        fixpoint = BETA_FIXPOINT_PHI3

        # Near threshold (R/Θ ≈ 1) → amplified flow
        flow_near = context_dependent_flow(
            beta,
            R_over_Theta=1.0,
            zeta=0.0,
            alpha=0.5,
            fixpoint=fixpoint,
        )

        # Far from threshold → weaker flow
        flow_far = context_dependent_flow(
            beta,
            R_over_Theta=0.5,
            zeta=0.0,
            alpha=0.5,
            fixpoint=fixpoint,
        )

        assert abs(flow_near) > abs(flow_far), "Flow near threshold should be stronger"

        # With damping (ζ > 0) → reduced flow
        flow_damped = context_dependent_flow(
            beta,
            R_over_Theta=1.0,
            zeta=0.5,
            alpha=0.5,
            fixpoint=fixpoint,
        )

        assert (
            abs(flow_damped) < abs(flow_near)
        ), "Damping should reduce flow magnitude"

    def test_cubic_root_amplification_drive(self):
        """Cubic root flow should drive β above threshold."""
        # Above threshold → positive drive
        flow_above = cubic_root_amplification_flow(
            beta=4.0,
            R_over_Theta=1.1,
            k=5.0,
            beta_base=4.236,
        )
        assert flow_above > 0, "Flow above threshold should be positive (amplifying)"

        # Below threshold → relaxation to baseline
        flow_below = cubic_root_amplification_flow(
            beta=6.0,
            R_over_Theta=0.9,
            k=5.0,
            beta_base=4.236,
        )
        assert (
            flow_below < 0
        ), "Flow below threshold should be negative (relaxing to baseline)"


# ═══════════════════════════════════════════════════════════════
# SIMULATOR TESTS
# ═══════════════════════════════════════════════════════════════


class TestRGFlowSimulator:
    """Test RGFlowSimulator class methods."""

    @pytest.fixture
    def simulator(self):
        """Create default simulator."""
        return RGFlowSimulator()

    def test_simulator_initialization(self, simulator):
        """Simulator should initialize with default config."""
        assert simulator.config is not None
        assert simulator.flow_func is not None
        assert simulator.config.variant == FlowVariant.LINEAR_PHI_ATTRACTOR

    def test_simulate_convergence(self, simulator):
        """β should converge to fixpoint under RG flow."""
        beta_initial = 3.0
        ln_lambda, beta_traj = simulator.simulate(
            beta_initial=beta_initial,
            lambda_range=(1.0, 100.0),
            n_points=100,
        )

        # Check shapes
        assert len(ln_lambda) == len(beta_traj)
        assert len(beta_traj) == 100

        # β should move toward fixpoint
        beta_final = beta_traj[-1]
        assert (
            abs(beta_final - beta_initial) > 0.1
        ), "β should change under RG flow"

        # Should converge to one of the Φⁿ fixpoints
        distances = np.abs(BETA_STEPS - beta_final)
        min_distance = np.min(distances)
        assert (
            min_distance < 0.5
        ), f"β should converge near Φⁿ fixpoint (closest: {min_distance:.3f})"

    def test_find_fixed_points(self, simulator):
        """Simulator should find Φⁿ fixed points."""
        fixed_points = simulator.find_fixed_points(
            beta_range=(1.0, 10.0),
            n_samples=2000,
            tolerance=0.02,
        )

        # Should find at least some fixpoints
        assert len(fixed_points) > 0, "Should find at least one fixed point"

        # Fixed points should be near Φⁿ values
        for fp in fixed_points:
            distances = np.abs(BETA_STEPS - fp)
            min_distance = np.min(distances)
            assert (
                min_distance < 0.3
            ), f"Fixed point {fp:.3f} should be near a Φⁿ value"

    def test_basin_of_attraction(self, simulator):
        """Basin of attraction should contain fixpoint."""
        fixpoint = BETA_FIXPOINT_PHI3  # ~4.236

        basin_min, basin_max = simulator.basin_of_attraction(
            fixpoint=fixpoint,
            beta_range=(2.0, 6.0),
            n_trajectories=10,
            lambda_max=50.0,
            convergence_threshold=0.15,
        )

        # Basin should be finite
        assert np.isfinite(basin_min) and np.isfinite(basin_max)

        # Fixpoint should be within basin
        assert (
            basin_min <= fixpoint <= basin_max
        ), "Fixpoint should be within its own basin"

    def test_euler_vs_rk45_consistency(self, simulator):
        """Euler and RK45 methods should give similar results."""
        beta_initial = 3.5

        _, beta_euler = simulator.simulate(
            beta_initial=beta_initial,
            lambda_range=(1.0, 10.0),
            n_points=100,
            method="Euler",
        )

        _, beta_rk45 = simulator.simulate(
            beta_initial=beta_initial,
            lambda_range=(1.0, 10.0),
            n_points=100,
            method="RK45",
        )

        # Final values should be close (within 10%)
        final_euler = beta_euler[-1]
        final_rk45 = beta_rk45[-1]
        relative_diff = abs(final_euler - final_rk45) / final_rk45

        assert (
            relative_diff < 0.1
        ), f"Euler and RK45 should agree within 10% (diff: {relative_diff:.2%})"


# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════


class TestUtilities:
    """Test utility functions."""

    def test_compare_to_phi_ladder(self):
        """Compare β to Φⁿ ladder."""
        # Trajectory ending near Φ³
        beta_traj = np.linspace(3.0, 4.2, 50)
        ln_lambda = np.linspace(0, 4, 50)

        result = compare_to_phi_ladder(beta_traj, ln_lambda)

        assert "beta_final" in result
        assert "nearest_phi_n" in result
        assert "step" in result
        assert "deviation" in result

        # Should identify Φ³ as nearest
        assert result["step"] == 9, "Should identify step 9 (Φ³)"
        assert (
            abs(result["deviation"]) < 0.05
        ), f"Deviation should be <5% (got {result['deviation']:.1%})"

    def test_phi_convergence_score(self):
        """Φⁿ convergence score should be 1.0 when converged."""
        # Perfectly converged to Φ³
        beta_traj = np.array([3.0, 3.5, 4.0, 4.2, 4.236])
        score = phi_convergence_score(beta_traj, threshold=0.05)

        assert score == 1.0, "Score should be 1.0 when converged to Φⁿ"

        # Not converged
        beta_traj_far = np.array([3.0, 3.5, 4.0, 5.0, 6.0])
        score_far = phi_convergence_score(beta_traj_far, threshold=0.05)

        assert score_far < 0.5, "Score should be low when not converged"


# ═══════════════════════════════════════════════════════════════
# VARIANT-SPECIFIC TESTS
# ═══════════════════════════════════════════════════════════════


class TestFlowVariants:
    """Test different RG flow variants."""

    @pytest.mark.parametrize(
        "variant",
        [
            FlowVariant.LINEAR_PHI_ATTRACTOR,
            FlowVariant.POLYNOMIAL_FLOW,
            FlowVariant.MULTI_BASIN,
            FlowVariant.CONTEXT_DEPENDENT,
            FlowVariant.CUBIC_ROOT_AMPLIFICATION,
        ],
    )
    def test_variant_converges(self, variant):
        """All variants should produce finite trajectories."""
        config = RGFlowConfig(variant=variant)
        simulator = RGFlowSimulator(config)

        beta_initial = 3.5
        ln_lambda, beta_traj = simulator.simulate(
            beta_initial=beta_initial,
            lambda_range=(1.0, 50.0),
            n_points=100,
        )

        # All values should be finite
        assert np.all(np.isfinite(beta_traj)), f"{variant.value}: β should be finite"

        # β should stay positive
        assert np.all(beta_traj > 0), f"{variant.value}: β should stay positive"

        # β should change (not stuck)
        beta_change = abs(beta_traj[-1] - beta_traj[0])
        assert (
            beta_change > 0.01
        ), f"{variant.value}: β should change under RG flow"


# ═══════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ═══════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_beta_initial_at_fixpoint(self):
        """Starting at fixpoint should remain there."""
        simulator = RGFlowSimulator()
        beta_initial = BETA_FIXPOINT_PHI3

        _, beta_traj = simulator.simulate(
            beta_initial=beta_initial,
            lambda_range=(1.0, 100.0),
            n_points=100,
        )

        # Should remain close to fixpoint
        final_deviation = abs(beta_traj[-1] - beta_initial)
        assert (
            final_deviation < 0.05
        ), f"Should stay at fixpoint (deviation: {final_deviation:.3f})"

    def test_extreme_beta_values(self):
        """Extreme β values should not cause numerical issues."""
        simulator = RGFlowSimulator()

        # Very low β
        _, beta_low = simulator.simulate(
            beta_initial=0.5,
            lambda_range=(1.0, 10.0),
            n_points=50,
        )
        assert np.all(np.isfinite(beta_low)), "Low β should remain finite"

        # Very high β
        _, beta_high = simulator.simulate(
            beta_initial=20.0,
            lambda_range=(1.0, 10.0),
            n_points=50,
        )
        assert np.all(np.isfinite(beta_high)), "High β should remain finite"

    def test_invalid_method_raises_error(self):
        """Invalid integration method should raise error."""
        simulator = RGFlowSimulator()

        with pytest.raises(ValueError, match="Unknown method"):
            simulator.simulate(
                beta_initial=3.5,
                lambda_range=(1.0, 10.0),
                method="InvalidMethod",
            )


# ═══════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_phi3_is_universal_attractor(self):
        """Φ³ should attract β from various initial conditions."""
        simulator = RGFlowSimulator()
        fixpoint = BETA_FIXPOINT_PHI3

        initial_values = [2.0, 3.0, 3.5, 4.0, 4.5, 5.0]
        converged_count = 0

        for beta_0 in initial_values:
            _, beta_traj = simulator.simulate(
                beta_initial=beta_0,
                lambda_range=(1.0, 100.0),
                n_points=200,
            )

            final_distance = abs(beta_traj[-1] - fixpoint)
            if final_distance < 0.2:
                converged_count += 1

        # At least half should converge to Φ³
        assert (
            converged_count >= len(initial_values) // 2
        ), f"Φ³ should attract at least half of initial conditions (got {converged_count}/{len(initial_values)})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
