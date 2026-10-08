"""LR2 plan change AE-01: classical RK4 for the same noise-free Lantern ODE.
The Euler path and its tests (test_lr2.py, incl. the documented Euler ODE-gate failure) stay unchanged.
RK4 steps are NOT required to equal the original Euler kernel. Run explicitly with the other Lantern tests."""
from __future__ import annotations

import hashlib
import io
import json
import math

import numpy as np
import pytest

from experiments.lantern_reconstruction import dynamics as dyn
from experiments.lantern_reconstruction import linear_diagnostics as ld
from experiments.lantern_reconstruction import registry_adapter as ra

REF = ra.HERE / "artifacts" / "lr2_reference"
ODE_PIN = "cf90b1b83423c5a7f5152d4e7282ba43b42e33cdbdbb9294d5870145fa581b60"
GATE_ODE = 0.005


@pytest.fixture(scope="module")
def panel():
    b = (REF / "ode_cases.npz").read_bytes()
    assert hashlib.sha256(b).hexdigest() == ODE_PIN                          # the UNCHANGED 32-case panel
    with np.load(io.BytesIO(b), allow_pickle=False) as f:
        return {k: np.array(f[k]) for k in f.files}


def _rk4_errors(oc, dt):
    times = list(oc["times"])
    steps = dyn.steps_for_times(times, dt)
    out = []
    for k in range(int(oc["n_cases"])):
        e = dyn.integrate_rk4(oc[f"theta_{k}"][None], oc[f"C_{k}"], oc[f"omega_{k}"], float(oc[f"g_{k}"]), dt, steps[-1], steps)[:, 0]
        out.append(float(dyn.circular_distance(e, oc[f"reference_{k}"]).max()))
    return np.array(out)


def test_rk4_passes_the_unchanged_panel_at_dt_002_and_is_fourth_order(panel):
    assert int(panel["n_cases"]) == 32 and list(panel["times"]) == [0, 0.5, 1, 2, 3, 5, 10]
    e = {dt: _rk4_errors(panel, dt) for dt in (0.02, 0.01, 0.005)}
    assert e[0.02].max() <= GATE_ODE                                        # gate passed at the planned dt
    assert e[0.02].max() == pytest.approx(3.244e-7, rel=0.02)              # reported value
    r1, r2 = e[0.02].max() / e[0.01].max(), e[0.01].max() / e[0.005].max()
    assert 12 < r1 < 18 and 12 < r2 < 18                                    # fourth order (factor ~16)


def test_rk4_step_matches_the_textbook_formula():
    C = np.array([[0.0, 0.7], [0.7, 0.0]])
    om = np.array([0.1, -0.1])
    x = np.array([[0.4, 0.0]])
    f = lambda y: dyn.drift(y, C, om, 1.0)
    h = 0.05
    k1 = f(x); k2 = f(x + h / 2 * k1); k3 = f(x + h / 2 * k2); k4 = f(x + h * k3)
    assert np.array_equal(dyn.rk4_step(x, C, om, 1.0, h), x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4))


def test_rk4_is_not_required_to_equal_euler():
    s = ra.load_verified_snapshot()
    th = np.random.default_rng(0).uniform(-np.pi, np.pi, (2, 34))
    a = dyn.integrate(th, np.array(s.C), np.zeros(34), float(s.structure["g"]), 0.02, 50)[0]
    b = dyn.integrate_rk4(th, np.array(s.C), np.zeros(34), float(s.structure["g"]), 0.02, 50)[0]
    assert float(dyn.circular_distance(a, b).max()) > 1e-8                  # different discretisations


# --- analytic oracles ------------------------------------------------------------------------------
def test_rk4_two_node_exact_solution_fourth_order():
    d0, k, t = 0.4, 0.7, 1.3
    exact = 2 * math.atan(math.tan(d0 / 2) * math.exp(-2 * k * t))
    C = np.array([[0.0, k], [k, 0.0]])
    errs = []
    for dt in (0.1, 0.05):
        x = dyn.integrate_rk4(np.array([[d0, 0.0]]), C, np.zeros(2), 1.0, dt, round(t / dt))[0, 0]
        errs.append(abs((x[0] - x[1]) - exact))
    assert errs[1] < 1e-7 and 12 < errs[0] / errs[1] < 20               # measured 2.5e-8 at dt 0.05


def test_rk4_free_drift_is_exact():
    r = np.random.default_rng(3)
    th, om = r.uniform(-np.pi, np.pi, (5, 34)), r.normal(0, 0.1, 34)
    x = dyn.integrate_rk4(th, np.zeros((34, 34)), om, 1.0, 0.02, 500)[0]
    assert float(dyn.circular_distance(x, dyn.wrap(th + 10.0 * om)).max()) < 1e-12


def test_rk4_time_rescaling():
    r = np.random.default_rng(4)
    U = np.triu(r.uniform(size=(6, 6)), 1)
    C = U + U.T
    th = r.uniform(-1, 1, (1, 6))
    for u in (10.0, 1000.0):
        a = dyn.integrate_rk4(th, C, np.zeros(6), 0.4, 0.02, 40)[0]
        b = dyn.integrate_rk4(th, C, np.zeros(6), 0.4 / u, 0.02 * u, 40)[0]
        assert float(dyn.circular_distance(a, b).max()) < 1e-12


def test_rk4_remote_transfer_small_amplitude():
    C = np.zeros((4, 4))
    for i, j in [(0, 2), (2, 3), (3, 1)]:
        C[i, j] = C[j, i] = 1.0
    v = np.array([1.0, -1.0, 0.0, 0.0]) / math.sqrt(2.0)
    eps, tp = 1e-5, math.atanh(1 / math.sqrt(2)) / math.sqrt(2)
    n = 1000
    x = dyn.integrate_rk4((eps * v)[None], C, np.zeros(4), 1.0, tp / n, n, wrap_states=False)[0, 0]
    assert (x[2] - x[3]) / eps == pytest.approx(0.28752355827362913, rel=1e-6)


def test_rk4_uniform_complete_graph_unwritten_outputs_stay_equal():
    n = 6
    C = np.ones((n, n)) - np.eye(n)
    th0 = 0.7 + 0.35 * np.array([1, -1, 0, 0, 0, 0]) / math.sqrt(2)
    x = dyn.integrate_rk4(th0[None], C, np.zeros(n), 1.0, 0.02, 200, record_steps=[0, 50, 200])[:, 0]
    assert np.all(np.abs(x[:, 2:] - x[:, 2:3]) < 1e-15)


# --- structural gates ------------------------------------------------------------------------------
def _case():
    s = ra.load_verified_snapshot()
    r = np.random.default_rng(7)
    om = r.normal(0, 0.1, 34)
    return np.array(s.C), om - om.mean(), float(s.structure["g"]), r.uniform(-np.pi, np.pi, (6, 34))


def test_rk4_permutation_and_rotation_equivariance():
    C, om, g, th = _case()
    perm = np.random.default_rng(1).permutation(34)
    a = dyn.integrate_rk4(th, C, om, g, 0.02, 100)[0]
    b = dyn.integrate_rk4(th[:, perm], C[np.ix_(perm, perm)], om[perm], g, 0.02, 100)[0]
    assert float(dyn.circular_distance(a[:, perm], b).max()) < 1e-12
    c = dyn.integrate_rk4(dyn.wrap(th + 2.2), C, om, g, 0.02, 100)[0]
    assert float(dyn.circular_distance(dyn.wrap(a + 2.2), c).max()) < 1e-12


def test_rk4_inputs_unchanged_and_no_global_rng():
    C, om, g, th = _case()
    C0, om0, th0 = C.copy(), om.copy(), th.copy()
    np.random.seed(5)
    st = np.random.get_state()[1].copy()
    dyn.integrate_rk4(th, C, om, g, 0.02, 50)
    assert np.array_equal(C, C0) and np.array_equal(om, om0) and np.array_equal(th, th0)
    assert np.array_equal(st, np.random.get_state()[1])


@pytest.mark.parametrize("method", ["euler", "rk4"])
def test_batch_independence(method):
    """Each episode's trajectory is independent of the batch it is computed in (size and order)."""
    fn = dyn.integrate if method == "euler" else dyn.integrate_rk4
    C, om, g, _ = _case()
    th = np.random.default_rng(11).uniform(-np.pi, np.pi, (9, 34))
    full = fn(th, C, om, g, 0.02, 100)[0]
    single = np.stack([fn(th[i:i + 1], C, om, g, 0.02, 100)[0, 0] for i in range(9)])
    rev = fn(th[::-1], C, om, g, 0.02, 100)[0][::-1]
    split = np.concatenate([fn(th[:4], C, om, g, 0.02, 100)[0], fn(th[4:], C, om, g, 0.02, 100)[0]])
    for other in (single, rev, split):
        assert float(dyn.circular_distance(full, other).max()) <= 1e-13


@pytest.mark.parametrize("method", ["euler", "rk4"])
def test_wrap_convention(method):
    """Recorded states lie in [-pi, pi] (wrap_states=True, default); wrap_states=False keeps the unwrapped
    phases (mutation check found that only circular comparisons were tested)."""
    fn = dyn.integrate if method == "euler" else dyn.integrate_rk4
    th = np.array([[3.0, -3.0, 0.5]])
    om = np.array([0.5, -0.5, 0.0])
    w = fn(th, np.zeros((3, 3)), om, 1.0, 0.02, 100, record_steps=[50, 100])
    assert np.all(np.abs(w) <= np.pi)
    u = fn(th, np.zeros((3, 3)), om, 1.0, 0.02, 100, wrap_states=False)[0, 0]
    assert u == pytest.approx(th[0] + 2.0 * om, abs=1e-12) and abs(u[0]) > np.pi


def test_rk4_rejects_invalid_inputs_like_euler():
    C, om, g, th = _case()
    with pytest.raises(dyn.DynamicsError, match="negative"):
        dyn.integrate_rk4(th, -C, om, g, 0.02, 5)
    with pytest.raises(dyn.DynamicsError, match="symmetric"):
        dyn.integrate_rk4(th, np.triu(C), om, g, 0.02, 5)


def test_plan_change_record_trilayer():
    import yaml
    p = ra.HERE / "protocol" / "plan_changes"
    d = json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == d
    ae = {c["id"]: c for c in d["changes"]}["AE-01"]
    assert ae["title"] == "Lantern-Differentialgleichung mit geprüftem RK4-Verfahren"
    assert ae["euler_failure_retained"] is True
    assert ae["decoder_metric_gate"] == "passed in LR4 (lr4/lr4_decoder_convergence.json)"     # was "open until LR4" up to LR3
