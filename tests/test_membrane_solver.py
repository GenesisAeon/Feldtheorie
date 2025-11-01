import math

import pytest

from models.membrane_solver import update_impedance


def test_update_impedance_tracks_logistic_gate() -> None:
    zeta_closed = update_impedance(R_trigger=-1.0, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)
    zeta_mid = update_impedance(R_trigger=0.5, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)
    zeta_open = update_impedance(R_trigger=1.5, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)

    assert math.isclose(zeta_closed, 1.4, rel_tol=1e-3)
    assert math.isclose(zeta_mid, (1.4 + 0.2) / 2.0, rel_tol=1e-6)
    assert zeta_open == pytest.approx(0.2, abs=0.005)


def test_update_impedance_monotonic() -> None:
    values = [update_impedance(R_trigger=r, Theta=0.0, beta=5.0, zeta_max=1.2, zeta_min=0.3) for r in (-1.0, 0.0, 1.0)]
    assert values[0] > values[1] > values[2]
