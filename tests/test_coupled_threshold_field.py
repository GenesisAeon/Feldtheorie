"""Comprehensive tests for CoupledThresholdField.

Tests initialization, coupling kernels, step integration, simulation,
observables export, and driver utilities.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from models.coupled_threshold_field import (
    CoupledThresholdField,
    logistic_semantic_kernel,
    ramp_driver,
)


class TestCoupledThresholdFieldInit:
    """Test initialization and basic properties."""

    def test_initialization_with_defaults(self) -> None:
        """Should initialize with default parameters."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        assert field.theta == 0.5
        assert field.beta == 4.0
        assert field.coupling == 0.3
        assert field.dt == 0.05
        assert field.zeta_floor == 0.65
        assert field.zeta_ceiling == 1.35
        assert field.beta_robin == 4.5
        assert field.phi_relaxation == 1.2

    def test_initialization_with_custom_params(self) -> None:
        """Should accept custom parameters."""
        field = CoupledThresholdField(
            theta=0.8,
            beta=5.0,
            coupling=0.5,
            dt=0.01,
            zeta_floor=0.5,
            zeta_ceiling=1.5,
            beta_robin=6.0,
            phi_relaxation=1.5,
        )
        assert field.theta == 0.8
        assert field.beta == 5.0
        assert field.coupling == 0.5
        assert field.dt == 0.01
        assert field.zeta_floor == 0.5
        assert field.zeta_ceiling == 1.5
        assert field.beta_robin == 6.0
        assert field.phi_relaxation == 1.5

    def test_post_init_creates_impedance_profile(self) -> None:
        """Post-init should create impedance profile callable."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        assert field.impedance_profile is not None
        assert callable(field.impedance_profile)

    def test_post_init_sets_default_coupling_kernel(self) -> None:
        """Should set default coupling kernel if none provided."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        assert field.coupling_kernel is not None
        assert callable(field.coupling_kernel)


class TestRobinImpedance:
    """Test the robin_impedance method."""

    def test_robin_impedance_below_theta(self) -> None:
        """Below theta, impedance should be near zeta_floor."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        z = field.robin_impedance(-10.0)
        assert math.isclose(z, field.zeta_floor, abs_tol=0.05)

    def test_robin_impedance_above_theta(self) -> None:
        """Above theta, impedance should be near zeta_ceiling."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        z = field.robin_impedance(10.0)
        assert math.isclose(z, field.zeta_ceiling, abs_tol=0.05)

    def test_robin_impedance_at_theta(self) -> None:
        """At theta, impedance should be approximately midpoint."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        z = field.robin_impedance(0.5)
        expected = (field.zeta_floor + field.zeta_ceiling) / 2.0
        assert math.isclose(z, expected, abs_tol=0.15)

    def test_robin_impedance_monotonic(self) -> None:
        """Impedance should increase monotonically with R."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        z1 = field.robin_impedance(0.0)
        z2 = field.robin_impedance(0.5)
        z3 = field.robin_impedance(1.0)
        assert z1 < z2 < z3


class TestDefaultCouplingKernel:
    """Test the default_coupling_kernel static method."""

    def test_default_coupling_kernel_returns_phi_minus_psi(self) -> None:
        """Default kernel should return phi - psi."""
        result = CoupledThresholdField.default_coupling_kernel(
            R=0.5, psi=0.3, phi=0.8, driver=1.0, sigma=0.6
        )
        expected = 0.8 - 0.3
        assert math.isclose(result, expected)

    def test_default_coupling_kernel_ignores_other_params(self) -> None:
        """Default kernel should only depend on phi and psi."""
        result1 = CoupledThresholdField.default_coupling_kernel(
            R=0.0, psi=0.2, phi=0.7, driver=0.0, sigma=0.0
        )
        result2 = CoupledThresholdField.default_coupling_kernel(
            R=1.0, psi=0.2, phi=0.7, driver=1.0, sigma=1.0
        )
        assert math.isclose(result1, result2)


class TestComputeCoupling:
    """Test the compute_coupling method."""

    def test_compute_coupling_scales_kernel_by_coupling(self) -> None:
        """Should scale kernel result by coupling constant."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.4)
        result = field.compute_coupling(
            R=0.5, psi=0.3, phi=0.8, driver=1.0, sigma=0.6
        )
        kernel_value = 0.8 - 0.3  # default kernel: phi - psi
        expected = 0.4 * kernel_value
        assert math.isclose(result, expected)

    def test_compute_coupling_uses_custom_kernel(self) -> None:
        """Should use custom kernel if provided."""

        def custom_kernel(R, psi, phi, driver, sigma):
            return 2.0 * (phi - psi)

        field = CoupledThresholdField(
            theta=0.5, beta=4.0, coupling=0.3, coupling_kernel=custom_kernel
        )
        result = field.compute_coupling(
            R=0.5, psi=0.2, phi=0.6, driver=1.0, sigma=0.5
        )
        expected = 0.3 * 2.0 * (0.6 - 0.2)
        assert math.isclose(result, expected)


class TestStep:
    """Test the step method."""

    def test_step_returns_expected_keys(self) -> None:
        """Step should return all expected state keys."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        state = {"R": 0.4, "psi": 0.3, "phi": 0.5}
        result = field.step(state, driver=0.6)

        expected_keys = {"R", "psi", "phi", "sigma", "zeta", "flux", "coupling_term"}
        assert set(result.keys()) == expected_keys

    def test_step_advances_state(self) -> None:
        """Step should produce different state values."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        state = {"R": 0.4, "psi": 0.3, "phi": 0.5}
        result = field.step(state, driver=0.6)

        # At least one value should change
        assert not (
            result["R"] == state["R"]
            and result["psi"] == state["psi"]
            and result["phi"] == state["phi"]
        )

    def test_step_respects_dt(self) -> None:
        """Smaller dt should produce smaller changes."""
        field_small = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3, dt=0.01)
        field_large = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3, dt=0.1)

        state = {"R": 0.4, "psi": 0.3, "phi": 0.5}
        result_small = field_small.step(state.copy(), driver=0.8)
        result_large = field_large.step(state.copy(), driver=0.8)

        # Larger dt should produce larger changes
        delta_small = abs(result_small["R"] - state["R"])
        delta_large = abs(result_large["R"] - state["R"])
        assert delta_small < delta_large


class TestSimulate:
    """Test the simulate method."""

    def test_simulate_returns_expected_keys(self) -> None:
        """Simulate should return all expected trace arrays."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.0, 0.5, 1.0]
        result = field.simulate(drivers)

        expected_keys = {
            "t",
            "driver",
            "R",
            "psi",
            "phi",
            "sigma",
            "zeta",
            "flux",
            "coupling_term",
            "theta",
            "beta",
        }
        assert set(result.keys()) == expected_keys

    def test_simulate_arrays_have_correct_length(self) -> None:
        """All arrays should have correct lengths."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.0, 0.5, 1.0, 1.5]
        result = field.simulate(drivers)

        # Most arrays have length = len(drivers) + 1
        assert len(result["t"]) == 5
        assert len(result["R"]) == 5
        assert len(result["psi"]) == 5
        assert len(result["phi"]) == 5
        assert len(result["sigma"]) == 5
        assert len(result["zeta"]) == 5

        # flux and coupling_term have length = len(drivers)
        assert len(result["flux"]) == 4
        assert len(result["coupling_term"]) == 4

    def test_simulate_respects_initial_conditions(self) -> None:
        """Initial conditions should be set correctly."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.5, 1.0]
        result = field.simulate(drivers, R0=0.2, psi0=0.3, phi0=0.4)

        assert math.isclose(result["R"][0], 0.2)
        assert math.isclose(result["psi"][0], 0.3)
        assert math.isclose(result["phi"][0], 0.4)

    def test_simulate_with_constant_driver(self) -> None:
        """Should handle constant driver input."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.5] * 10
        result = field.simulate(drivers)

        # Should converge to some steady state
        assert all(math.isfinite(v) for v in result["R"])
        assert all(math.isfinite(v) for v in result["psi"])
        assert all(math.isfinite(v) for v in result["phi"])

    def test_simulate_with_ramp_driver(self) -> None:
        """Should handle ramping driver input."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = np.linspace(0.0, 1.0, 20)
        result = field.simulate(drivers)

        # R should generally increase with ramping driver
        assert result["R"][-1] > result["R"][0]

    def test_simulate_theta_and_beta_constant(self) -> None:
        """Theta and beta arrays should be constant."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.0, 0.5, 1.0]
        result = field.simulate(drivers)

        assert all(v == 0.5 for v in result["theta"])
        assert all(v == 4.0 for v in result["beta"])


class TestExportObservables:
    """Test the export_observables method."""

    def test_export_observables_returns_expected_keys(self) -> None:
        """Should return all expected observable keys."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.0, 0.5, 1.0]
        results = field.simulate(drivers)
        observables = field.export_observables(results)

        expected_keys = {
            "theta",
            "beta",
            "R_min",
            "R_max",
            "sigma_peak",
            "sigma_valley",
            "zeta_mean",
            "zeta_std",
            "flux_mean",
            "flux_std",
            "phi_proxy_mean",
            "phi_proxy_peak",
            "coupling_mean",
            "coupling_std",
            "coupling_peak",
        }
        assert set(observables.keys()) == expected_keys

    def test_export_observables_values_finite(self) -> None:
        """All exported values should be finite."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = np.linspace(0.0, 1.0, 20)
        results = field.simulate(drivers)
        observables = field.export_observables(results)

        for key, value in observables.items():
            assert math.isfinite(value), f"{key} is not finite"

    def test_export_observables_theta_beta_match(self) -> None:
        """Exported theta and beta should match field parameters."""
        field = CoupledThresholdField(theta=0.7, beta=5.0, coupling=0.3)
        drivers = [0.5, 1.0]
        results = field.simulate(drivers)
        observables = field.export_observables(results)

        assert observables["theta"] == 0.7
        assert observables["beta"] == 5.0

    def test_export_observables_R_min_max_valid(self) -> None:
        """R_min should be <= R_max."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = np.linspace(0.0, 1.5, 30)
        results = field.simulate(drivers)
        observables = field.export_observables(results)

        assert observables["R_min"] <= observables["R_max"]

    def test_export_observables_can_update_existing_dict(self) -> None:
        """Should update existing dictionary if provided."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        drivers = [0.5, 1.0]
        results = field.simulate(drivers)

        existing = {"custom_key": 42}
        observables = field.export_observables(results, store=existing)

        assert observables["custom_key"] == 42
        assert "theta" in observables
        assert observables is existing  # Should be same object


class TestIntegratedInformationProxy:
    """Test the integrated_information_proxy static method."""

    def test_integrated_information_proxy_returns_array(self) -> None:
        """Should return numpy array."""
        psi = np.array([0.1, 0.2, 0.3, 0.4])
        phi = np.array([0.15, 0.25, 0.35, 0.45])
        result = CoupledThresholdField.integrated_information_proxy(psi, phi)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(psi)

    def test_integrated_information_proxy_non_negative(self) -> None:
        """Should return non-negative values (absolute value)."""
        psi = np.array([0.0, 0.5, 1.0, 0.5, 0.0])
        phi = np.array([0.0, 0.3, 0.8, 1.2, 1.0])
        result = CoupledThresholdField.integrated_information_proxy(psi, phi)

        assert all(v >= 0 for v in result)

    def test_integrated_information_proxy_with_constant_fields(self) -> None:
        """Should be near zero for constant fields (zero gradient)."""
        psi = np.ones(10) * 0.5
        phi = np.ones(10) * 0.3
        result = CoupledThresholdField.integrated_information_proxy(psi, phi)

        assert result.max() < 1e-6  # Near zero


class TestLogisticSemanticKernel:
    """Test the logistic_semantic_kernel factory function."""

    def test_logistic_semantic_kernel_returns_callable(self) -> None:
        """Should return a callable kernel."""
        kernel = logistic_semantic_kernel(theta=0.5, beta=4.0)
        assert callable(kernel)

    def test_logistic_semantic_kernel_with_defaults(self) -> None:
        """Should work with default parameters."""
        kernel = logistic_semantic_kernel(theta=0.5, beta=4.0)
        result = kernel(R=0.5, psi=0.3, phi=0.7, driver=0.8, sigma=0.5)
        assert math.isfinite(result)

    def test_logistic_semantic_kernel_with_custom_params(self) -> None:
        """Should accept custom resonance_bias and driver_weight."""
        kernel = logistic_semantic_kernel(
            theta=0.5, beta=4.0, resonance_bias=0.8, driver_weight=0.4
        )
        result = kernel(R=0.5, psi=0.3, phi=0.7, driver=0.8, sigma=0.5)
        assert math.isfinite(result)

    def test_logistic_semantic_kernel_modulates_with_R(self) -> None:
        """Kernel output should change with R crossing theta."""
        kernel = logistic_semantic_kernel(theta=0.5, beta=8.0)
        result_below = kernel(R=0.0, psi=0.3, phi=0.7, driver=0.8, sigma=0.1)
        result_above = kernel(R=1.0, psi=0.3, phi=0.7, driver=0.8, sigma=0.9)

        # Results should differ due to logistic gate modulation
        assert not math.isclose(result_below, result_above)

    def test_logistic_semantic_kernel_can_be_used_with_field(self) -> None:
        """Custom kernel should work with CoupledThresholdField."""
        kernel = logistic_semantic_kernel(theta=0.5, beta=4.0)
        field = CoupledThresholdField(
            theta=0.5, beta=4.0, coupling=0.3, coupling_kernel=kernel
        )
        drivers = [0.0, 0.5, 1.0]
        result = field.simulate(drivers)

        assert all(math.isfinite(v) for v in result["R"])


class TestRampDriver:
    """Test the ramp_driver utility function."""

    def test_ramp_driver_returns_array(self) -> None:
        """Should return numpy array."""
        result = ramp_driver(length=10)
        assert isinstance(result, np.ndarray)
        assert len(result) == 10

    def test_ramp_driver_starts_and_stops_at_bounds(self) -> None:
        """Should start at 'start' and end at 'stop'."""
        result = ramp_driver(length=100, start=0.2, stop=0.8)
        assert math.isclose(result[0], 0.2, abs_tol=0.05)
        assert math.isclose(result[-1], 0.8, abs_tol=0.05)

    def test_ramp_driver_monotonic_increasing(self) -> None:
        """Should be monotonically increasing for start < stop."""
        result = ramp_driver(length=50, start=0.0, stop=1.0)
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    def test_ramp_driver_curvature_affects_shape(self) -> None:
        """Different curvature should produce different ramps."""
        ramp1 = ramp_driver(length=50, curvature=1.0)
        ramp2 = ramp_driver(length=50, curvature=3.0)

        # Midpoints should differ with different curvature
        mid_idx = len(ramp1) // 2
        assert not math.isclose(ramp1[mid_idx], ramp2[mid_idx], abs_tol=0.01)

    def test_ramp_driver_with_single_point(self) -> None:
        """Should handle single point."""
        result = ramp_driver(length=1, start=0.5, stop=1.5)
        assert len(result) == 1
        # Single point is at start for length=1
        assert math.isclose(result[0], 0.5, abs_tol=0.1)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_field_with_zero_coupling(self) -> None:
        """Should handle zero coupling."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.0)
        drivers = [0.5, 1.0]
        result = field.simulate(drivers)
        assert all(math.isfinite(v) for v in result["R"])

    def test_field_with_negative_coupling(self) -> None:
        """Should handle negative coupling."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=-0.3)
        drivers = [0.5, 1.0]
        result = field.simulate(drivers)
        assert all(math.isfinite(v) for v in result["R"])

    def test_field_with_large_beta(self) -> None:
        """Should handle very steep logistic (large beta)."""
        field = CoupledThresholdField(theta=0.5, beta=50.0, coupling=0.3)
        drivers = [0.0, 0.5, 1.0]
        result = field.simulate(drivers)
        assert all(math.isfinite(v) for v in result["sigma"])

    def test_field_with_very_small_dt(self) -> None:
        """Should handle very small timestep."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3, dt=0.001)
        drivers = [0.5, 1.0]
        result = field.simulate(drivers)
        assert all(math.isfinite(v) for v in result["R"])

    def test_simulate_with_empty_drivers(self) -> None:
        """Should handle empty driver sequence."""
        field = CoupledThresholdField(theta=0.5, beta=4.0, coupling=0.3)
        result = field.simulate([])

        # Should return arrays with just initial conditions
        assert len(result["R"]) == 1
        assert len(result["psi"]) == 1
        assert len(result["flux"]) == 0
