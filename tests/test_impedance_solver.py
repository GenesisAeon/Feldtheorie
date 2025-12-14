import math

from models.impedance_solver import (
    ImpedanceFitReport,
    ImpedanceSolver,
    ImpedanceSolverConfig,
    load_measurements,
)


def test_sigma_centered_on_theta():
    config = ImpedanceSolverConfig()
    sigma_at_theta = config.sigma(config.beta_reference)
    assert 0.49 < sigma_at_theta < 0.51


def test_impedance_monotonic_with_beta():
    solver = ImpedanceSolver()
    betas = [4.5, 7.4, 11.0]
    impedances = [solver.impedance(beta) for beta in betas]
    assert impedances == sorted(impedances)
    assert impedances[0] < solver.config.base_impedance() < impedances[-1]


def test_profile_velocity_consistency():
    solver = ImpedanceSolver()
    point = solver.profile([solver.config.beta_reference])[0]
    expected_velocity = solver.config.c_light_km_s / point.impedance
    assert math.isclose(point.integration_velocity, expected_velocity, rel_tol=1e-6)
    assert math.isclose(point.impedance, solver.config.base_impedance(), rel_tol=1e-6)


def test_solver_outperforms_null_model():
    solver = ImpedanceSolver()
    measurements = load_measurements()
    report = solver.compare_to_measurements(measurements)
    assert isinstance(report, ImpedanceFitReport)

    null_rmse = math.sqrt(
        sum((row.z_null - row.z_measured) ** 2 for row in measurements) / len(measurements)
    )

    assert report.rmse < null_rmse
    assert report.n == len(measurements)
