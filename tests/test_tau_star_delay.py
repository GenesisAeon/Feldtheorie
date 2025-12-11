import numpy as np
import pytest
from pipelines.fit_tau_star import (
    apply_safety_delay,
    compute_tau_star,
    compute_zeta_risk,
    rk4_step_with_tau_star,
)


def test_compute_tau_star_scalar_and_array():
    tau_scalar = compute_tau_star(R=0.3, Theta=0.5, beta=4.8)
    assert pytest.approx(0.02, rel=1e-6) == tau_scalar

    R_values = np.array([0.2, 0.5, 0.8])
    tau_array = compute_tau_star(R=R_values, Theta=0.5, beta=4.8)
    np.testing.assert_allclose(tau_array, np.array([0.03, 0.0, 0.03]))


def test_apply_safety_delay_modes():
    R_prev = 0.5
    R_current = 0.3
    tau_star = 0.02
    dt = 0.001

    delayed_exp = apply_safety_delay(R_current, R_prev, tau_star, dt, mode="exponential")
    delayed_lin = apply_safety_delay(R_current, R_prev, tau_star, dt, mode="linear")

    assert delayed_exp < R_prev
    assert delayed_lin < R_prev
    assert delayed_exp > R_current
    assert delayed_lin > R_current


def test_compute_zeta_risk_marks_implosive_regime():
    zeta_low = compute_zeta_risk(R=0.2, Theta=0.5, beta=4.8)
    zeta_high = compute_zeta_risk(R=0.8, Theta=0.5, beta=4.8)

    assert np.all(zeta_low < 0)
    assert np.all(zeta_high < 0)
    assert np.all(zeta_high > zeta_low)


def test_rk4_step_with_tau_star_applies_delay():
    def dR_dt(R):
        return -0.5 * R

    R_start = 1.0
    Theta = 0.5
    beta = 4.8
    dt = 0.01

    R_next, tau_star = rk4_step_with_tau_star(R_start, dR_dt, dt, Theta, beta, R_history=[R_start])

    assert tau_star > 0
    assert R_next < R_start
    assert R_next > 0
