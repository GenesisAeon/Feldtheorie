"""Tests for the dynamic Robin boundary weaving impedance and gate telemetry."""

from __future__ import annotations

import pytest

from models import DynamicRobinBoundary, ThresholdFieldSolver, logistic_response


def test_robin_gate_and_impedance_bounds() -> None:
    """Gate and impedance should stay within physical limits and respond to R."""

    boundary = DynamicRobinBoundary(theta=0.5, beta_robin=6.2, zeta_floor=0.6, zeta_ceiling=1.4)

    gate_low = boundary.gate(0.2)
    gate_high = boundary.gate(0.8)

    assert 0.0 <= gate_low <= 1.0
    assert 0.0 <= gate_high <= 1.0
    assert gate_high > gate_low

    impedance_low = boundary.impedance(0.2)
    impedance_high = boundary.impedance(0.8)

    assert boundary.zeta_floor <= impedance_low <= boundary.zeta_ceiling
    assert boundary.zeta_floor <= impedance_high <= boundary.zeta_ceiling
    assert impedance_high > impedance_low


def test_boundary_flux_tracks_driver_gap() -> None:
    """Increasing the driver should amplify the Robin flux adjustment."""

    theta = 0.45
    boundary = DynamicRobinBoundary(theta=theta, beta_robin=5.4, logistic_weight=0.25, driver_weight=0.2)

    R = 0.4
    sigma = float(logistic_response(R, theta, 5.0))

    flux_low = boundary.boundary_flux(R, sigma, driver=0.3)
    flux_high = boundary.boundary_flux(R, sigma, driver=0.9)

    assert flux_high > flux_low


def test_solver_step_emits_boundary_gate_fields() -> None:
    """ThresholdFieldSolver.step should expose gate telemetry alongside flux."""

    boundary = DynamicRobinBoundary(theta=0.4, beta_robin=5.0)
    solver = ThresholdFieldSolver(theta=0.4, beta=6.0, boundary_condition=boundary, dt=0.05)

    payload = solver.step(0.35, driver=0.6)

    assert "boundary_flux" in payload
    assert "boundary_gate" in payload
    assert "boundary_gate_next" in payload

    gate_now = payload["boundary_gate"]
    gate_next = payload["boundary_gate_next"]

    assert gate_now is not None
    assert gate_next is not None
    assert 0.0 <= gate_now <= 1.0
    assert 0.0 <= gate_next <= 1.0


def test_simulate_tracks_boundary_gate_series() -> None:
    """Simulations should return boundary gate traces aligned with time indices."""

    boundary = DynamicRobinBoundary(theta=0.42, beta_robin=5.8)
    solver = ThresholdFieldSolver(theta=0.42, beta=5.7, boundary_condition=boundary, dt=0.1)

    drivers = [0.3, 0.45, 0.6, 0.7]
    results = solver.simulate(drivers, R0=0.25)

    assert "boundary_gate" in results
    gate_series = results["boundary_gate"]

    assert len(gate_series) == len(results["t"])
    assert pytest.approx(gate_series[0], rel=1e-9) == boundary.gate(0.25)
    assert all(0.0 <= value <= 1.0 for value in gate_series)
    assert max(gate_series) > min(gate_series)
