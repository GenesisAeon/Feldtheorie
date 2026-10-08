"""Review REVIEW_LR1_RK4: strict time arguments for BOTH integrators (only the input check became
stricter; the Euler and RK4 arithmetic is unchanged). Astra's counterexamples verbatim."""
from __future__ import annotations

import numpy as np
import pytest

from experiments.lantern_reconstruction import dynamics as dyn

TH, C, OM = np.array([[0.1, 0.0]]), np.zeros((2, 2)), np.ones(2)
METHODS = [dyn.integrate, dyn.integrate_rk4]


@pytest.mark.parametrize("fn", METHODS)
def test_astra_record_step_1_9_is_rejected_not_truncated(fn):
    with pytest.raises(dyn.DynamicsError, match="record_steps must be integers"):
        fn(TH, C, OM, 1.0, 0.02, 2, record_steps=[1.9])


@pytest.mark.parametrize("fn", METHODS)
def test_astra_dt_true_is_rejected(fn):
    with pytest.raises(dyn.DynamicsError, match="dt must be a finite positive number"):
        fn(TH, C, OM, 1.0, True, 1)


@pytest.mark.parametrize("fn", METHODS)
@pytest.mark.parametrize("dt", [np.bool_(True), 0.0, -0.02, float("nan"), float("inf"), "0.02", None])
def test_invalid_dt_rejected(fn, dt):
    with pytest.raises(dyn.DynamicsError, match="dt must be"):
        fn(TH, C, OM, 1.0, dt, 1)


@pytest.mark.parametrize("fn", METHODS)
@pytest.mark.parametrize("rec, match", [
    ([], "must not be empty"),
    ([True], "must be integers"),
    ([np.bool_(False)], "must be integers"),
    ([1.0], "must be integers"),
    (["1"], "must be integers"),
    ([2, 1], "sorted"),
    ([3], "within"),
    ([-1], "within"),
])
def test_invalid_record_steps_rejected(fn, rec, match):
    with pytest.raises(dyn.DynamicsError, match=match):
        fn(TH, C, OM, 1.0, 0.02, 2, record_steps=rec)


@pytest.mark.parametrize("fn", METHODS)
@pytest.mark.parametrize("n", [True, 2.0, -1, np.float64(2)])
def test_invalid_n_steps_rejected(fn, n):
    with pytest.raises(dyn.DynamicsError, match="n_steps"):
        fn(TH, C, OM, 1.0, 0.02, n)


@pytest.mark.parametrize("fn", METHODS)
def test_valid_integer_types_still_accepted(fn):
    a = fn(TH, C, OM, 1.0, 0.02, np.int64(2), record_steps=[np.int64(0), 1, np.int32(2)])
    assert a.shape == (3, 1, 2)
    assert np.allclose(a[:, 0, 0], [0.1, 0.12, 0.14]) and fn(TH, C, OM, 1.0, 1, 1)[0, 0, 1] == pytest.approx(1.0)


@pytest.mark.parametrize("times, dt, match", [
    ([-0.02], 0.02, "non-negative"),
    ([float("nan")], 0.02, "finite"),
    ([float("inf")], 0.02, "finite"),
    ([True], 0.02, "finite non-negative number"),
    (["1"], 0.02, "finite non-negative number"),
    ([1.0], True, "dt must be"),
    ([1.0], 0.0, "dt must be"),
    ([0.03], 0.02, "not a multiple"),
])
def test_steps_for_times_strict(times, dt, match):
    with pytest.raises(dyn.DynamicsError, match=match):
        dyn.steps_for_times(times, dt)


def test_steps_for_times_valid_grid_unchanged():
    assert dyn.steps_for_times([0, 0.5, 1, 2, 3, 5, 10], 0.02) == [0, 25, 50, 100, 150, 250, 500]
    assert dyn.steps_for_times([np.float64(1.0)], np.float64(0.02)) == [50]
