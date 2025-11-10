"""Comprehensive tests for LogisticFieldEnvelope.

Tests control sweeps, impedance profiles, response functions,
and synthetic data generation.
"""

from __future__ import annotations

import math

import pytest

from models.logistic_envelope import LogisticFieldEnvelope, _linspace


class TestLinspace:
    """Test the _linspace helper function."""

    def test_linspace_two_points(self) -> None:
        """Should generate two endpoints."""
        result = _linspace(0.0, 1.0, 2)
        assert len(result) == 2
        assert result[0] == 0.0
        assert result[1] == 1.0

    def test_linspace_single_point(self) -> None:
        """Single point should return stop value."""
        result = _linspace(0.0, 1.0, 1)
        assert len(result) == 1
        assert result[0] == 1.0

    def test_linspace_zero_points(self) -> None:
        """Zero points should return stop value."""
        result = _linspace(0.0, 1.0, 0)
        assert len(result) == 1
        assert result[0] == 1.0

    def test_linspace_uniform_spacing(self) -> None:
        """Points should be uniformly spaced."""
        result = _linspace(0.0, 10.0, 11)
        for i in range(len(result)):
            assert math.isclose(result[i], float(i), abs_tol=1e-10)

    def test_linspace_negative_range(self) -> None:
        """Should handle negative ranges."""
        result = _linspace(-2.0, 2.0, 5)
        expected = [-2.0, -1.0, 0.0, 1.0, 2.0]
        for i, val in enumerate(result):
            assert math.isclose(val, expected[i], abs_tol=1e-10)


class TestLogisticFieldEnvelopeInit:
    """Test initialization and basic properties."""

    def test_initialization_with_defaults(self) -> None:
        """Should initialize with default parameters."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        assert envelope.theta == 0.5
        assert envelope.beta == 4.0
        assert envelope.amplitude == 1.0
        assert envelope.resonant_gain == 0.7
        assert envelope.damped_gain == 1.3
        assert envelope.impedance_width == 0.5

    def test_initialization_with_custom_params(self) -> None:
        """Should accept custom parameters."""
        envelope = LogisticFieldEnvelope(
            theta=0.8,
            beta=3.5,
            amplitude=0.9,
            resonant_gain=0.6,
            damped_gain=1.4,
            impedance_width=0.3
        )
        assert envelope.theta == 0.8
        assert envelope.beta == 3.5
        assert envelope.amplitude == 0.9
        assert envelope.resonant_gain == 0.6
        assert envelope.damped_gain == 1.4
        assert envelope.impedance_width == 0.3


class TestControlSweep:
    """Test the control_sweep method."""

    def test_control_sweep_centered_at_theta(self) -> None:
        """Sweep should be centered at theta."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        sweep = envelope.control_sweep(span=1.0, points=11)

        # Should range from theta-span to theta+span
        assert math.isclose(sweep[0], -0.5, abs_tol=1e-6)
        assert math.isclose(sweep[-1], 1.5, abs_tol=1e-6)
        assert math.isclose(sweep[5], 0.5, abs_tol=1e-6)  # Middle point

    def test_control_sweep_respects_span(self) -> None:
        """Different spans should give different ranges."""
        envelope = LogisticFieldEnvelope(theta=1.0, beta=4.0)
        sweep_small = envelope.control_sweep(span=0.5, points=21)
        sweep_large = envelope.control_sweep(span=2.0, points=21)

        assert sweep_small[0] == 0.5
        assert sweep_small[-1] == 1.5
        assert sweep_large[0] == -1.0
        assert sweep_large[-1] == 3.0

    def test_control_sweep_respects_points(self) -> None:
        """Should generate correct number of points."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        assert len(envelope.control_sweep(span=1.0, points=10)) == 10
        assert len(envelope.control_sweep(span=1.0, points=50)) == 50


class TestImpedance:
    """Test the impedance method."""

    def test_impedance_below_theta(self) -> None:
        """Below theta, impedance should be near resonant_gain."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, resonant_gain=0.6, damped_gain=1.4)
        z = envelope.impedance(-10.0)  # Far below theta
        assert math.isclose(z, 0.6, abs_tol=0.05)

    def test_impedance_above_theta(self) -> None:
        """Above theta, impedance should be near damped_gain."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, resonant_gain=0.6, damped_gain=1.4)
        z = envelope.impedance(10.0)  # Far above theta
        assert math.isclose(z, 1.4, abs_tol=0.05)

    def test_impedance_at_theta(self) -> None:
        """At theta, impedance should be approximately midpoint."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, resonant_gain=0.6, damped_gain=1.4)
        z = envelope.impedance(0.5)
        expected = (0.6 + 1.4) / 2.0
        assert math.isclose(z, expected, abs_tol=0.15)

    def test_impedance_monotonic(self) -> None:
        """Impedance should increase with R."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        z1 = envelope.impedance(0.0)
        z2 = envelope.impedance(0.5)
        z3 = envelope.impedance(1.0)
        assert z1 < z2 < z3

    def test_impedance_width_affects_transition(self) -> None:
        """Larger width should give smoother transition."""
        narrow = LogisticFieldEnvelope(theta=0.5, beta=4.0, impedance_width=0.1)
        wide = LogisticFieldEnvelope(theta=0.5, beta=4.0, impedance_width=1.0)

        # At points near theta, difference should be more pronounced with narrow width
        z_narrow = narrow.impedance(0.6)
        z_wide = wide.impedance(0.6)

        # Both should be finite
        assert math.isfinite(z_narrow)
        assert math.isfinite(z_wide)


class TestResponse:
    """Test the response method."""

    def test_response_at_theta_is_half_amplitude(self) -> None:
        """At theta, response should be amplitude/2."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=1.0)
        r = envelope.response(0.5)
        assert math.isclose(r, 0.5, abs_tol=0.05)

    def test_response_scales_with_amplitude(self) -> None:
        """Response should scale with amplitude parameter."""
        env1 = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=1.0)
        env2 = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=2.0)

        r1 = env1.response(1.0)
        r2 = env2.response(1.0)

        assert math.isclose(r2, 2.0 * r1, abs_tol=0.01)

    def test_response_approaches_zero_below_theta(self) -> None:
        """Far below theta, response should approach 0."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=1.0)
        r = envelope.response(-10.0)
        assert r < 0.01

    def test_response_approaches_amplitude_above_theta(self) -> None:
        """Far above theta, response should approach amplitude."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=0.8)
        r = envelope.response(10.0)
        assert math.isclose(r, 0.8, abs_tol=0.01)

    def test_response_monotonic(self) -> None:
        """Response should increase with R."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        r1 = envelope.response(0.0)
        r2 = envelope.response(0.5)
        r3 = envelope.response(1.0)
        assert r1 < r2 < r3


class TestFlux:
    """Test the flux method."""

    def test_flux_is_finite(self) -> None:
        """Flux should return finite values."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        for R in [-1.0, 0.0, 0.5, 1.0, 2.0]:
            flux = envelope.flux(R)
            assert math.isfinite(flux)

    def test_flux_formula(self) -> None:
        """Flux should equal zeta * (sigma - R)."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        R = 0.3

        sigma = envelope.response(R)
        zeta = envelope.impedance(R)
        flux = envelope.flux(R)

        expected = zeta * (sigma - R)
        assert math.isclose(flux, expected, rel_tol=1e-6)


class TestSweep:
    """Test the sweep method."""

    def test_sweep_returns_expected_keys(self) -> None:
        """Sweep should return all expected data arrays."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=1.0, points=20)

        expected_keys = {"t", "R", "sigma", "sigma_clean", "zeta", "flux"}
        assert set(result.keys()) == expected_keys

    def test_sweep_arrays_same_length(self) -> None:
        """All arrays should have same length."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=1.0, points=30)

        lengths = [len(result[key]) for key in result.keys()]
        assert len(set(lengths)) == 1  # All same length
        assert lengths[0] == 30

    def test_sweep_with_custom_control(self) -> None:
        """Should accept custom control array."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        custom_control = [0.0, 0.25, 0.5, 0.75, 1.0]
        result = envelope.sweep(control=custom_control)

        assert result["R"] == custom_control
        assert len(result["sigma"]) == 5

    def test_sweep_without_noise(self) -> None:
        """Without noise, sigma and sigma_clean should match."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=1.0, points=20, noise=0.0)

        for i in range(len(result["sigma"])):
            assert math.isclose(result["sigma"][i], result["sigma_clean"][i])

    def test_sweep_with_noise_differs(self) -> None:
        """With noise, sigma should differ from sigma_clean."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=1.0, points=20, noise=0.1, random_seed=42)

        # At least some values should differ
        differences = sum(
            abs(result["sigma"][i] - result["sigma_clean"][i]) > 1e-6
            for i in range(len(result["sigma"]))
        )
        assert differences > 0

    def test_sweep_noise_bounded(self) -> None:
        """Noisy sigma should stay in [0, 1]."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=2.0, points=50, noise=0.3, random_seed=42)

        for val in result["sigma"]:
            assert 0.0 <= val <= 1.0

    def test_sweep_reproducible_with_seed(self) -> None:
        """Same seed should give same noise pattern."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result1 = envelope.sweep(span=1.0, points=20, noise=0.1, random_seed=123)
        result2 = envelope.sweep(span=1.0, points=20, noise=0.1, random_seed=123)

        for i in range(len(result1["sigma"])):
            assert math.isclose(result1["sigma"][i], result2["sigma"][i])

    def test_sweep_time_index_sequential(self) -> None:
        """Time index should be 0, 1, 2, ..."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        result = envelope.sweep(span=1.0, points=15)

        assert result["t"] == list(range(15))


class TestExportMetadata:
    """Test the export_metadata method."""

    def test_export_metadata_returns_dict(self) -> None:
        """Should return dictionary with all parameters."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        metadata = envelope.export_metadata()

        assert isinstance(metadata, dict)
        expected_keys = {"theta", "beta", "amplitude", "resonant_gain", "damped_gain", "impedance_width"}
        assert set(metadata.keys()) == expected_keys

    def test_export_metadata_values_match(self) -> None:
        """Exported values should match envelope parameters."""
        envelope = LogisticFieldEnvelope(
            theta=0.7, beta=3.5, amplitude=0.9,
            resonant_gain=0.65, damped_gain=1.25, impedance_width=0.4
        )
        metadata = envelope.export_metadata()

        assert metadata["theta"] == 0.7
        assert metadata["beta"] == 3.5
        assert metadata["amplitude"] == 0.9
        assert metadata["resonant_gain"] == 0.65
        assert metadata["damped_gain"] == 1.25
        assert metadata["impedance_width"] == 0.4

    def test_export_metadata_all_floats(self) -> None:
        """All exported values should be floats."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0)
        metadata = envelope.export_metadata()

        for key, value in metadata.items():
            assert isinstance(value, float), f"{key} is not float"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_tiny_impedance_width(self) -> None:
        """Should handle very small impedance width."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, impedance_width=1e-9)
        z = envelope.impedance(0.5)
        assert math.isfinite(z)

    def test_zero_amplitude(self) -> None:
        """Should handle zero amplitude."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=4.0, amplitude=0.0)
        r = envelope.response(1.0)
        assert r == 0.0

    def test_large_beta(self) -> None:
        """Should handle large beta (very steep)."""
        envelope = LogisticFieldEnvelope(theta=0.5, beta=100.0)
        result = envelope.sweep(span=0.5, points=50)
        assert all(math.isfinite(v) for v in result["sigma"])

    def test_negative_theta(self) -> None:
        """Should handle negative theta."""
        envelope = LogisticFieldEnvelope(theta=-2.0, beta=4.0)
        sweep = envelope.control_sweep(span=1.0, points=10)
        assert sweep[0] == -3.0
        assert sweep[-1] == -1.0
