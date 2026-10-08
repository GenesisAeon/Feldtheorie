"""LR2 numerical core: original equivalence, ODE accuracy (incl. the OPEN gate), analytic oracles,
structural gates and the linear adapter. Run explicitly: python -m pytest experiments/lantern_reconstruction/tests"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from experiments.lantern_reconstruction import dynamics as dyn
from experiments.lantern_reconstruction import legacy_probe as lp
from experiments.lantern_reconstruction import linear_diagnostics as ld
from experiments.lantern_reconstruction import registry_adapter as ra

REF = ra.HERE / "artifacts" / "lr2_reference"
FILE_PINS = {  # anchored here (reviewed code), not only in the artifact's own manifest
    "kernel_cases.npz": "dcb3874aa4f128c7802d0b62f5464ceb19711fddc46b93eb1b37c7628ee53ad9",
    "ode_cases.npz": "cf90b1b83423c5a7f5152d4e7282ba43b42e33cdbdbb9294d5870145fa581b60",
    "kernel_original.npz": "e92896f2b966c3a5a6380609fe5f475d8ac3369d4bd068666870f652ecad9245",
}
GATE_KERNEL = 1e-12
GATE_ODE = 0.005


def _load(name):
    b = (REF / name).read_bytes()
    assert hashlib.sha256(b).hexdigest() == FILE_PINS[name], name
    with np.load(io.BytesIO(b), allow_pickle=False) as f:
        return {k: np.array(f[k]) for k in f.files}


@pytest.fixture(scope="module")
def ref():
    return {"kc": _load("kernel_cases.npz"), "ko": _load("kernel_original.npz"), "oc": _load("ode_cases.npz"),
            "man": json.loads((REF / "manifest.json").read_text(encoding="utf-8"))}


def _ours(kc, k):
    return dyn.integrate(kc[f"theta_{k}"][None], kc[f"C_{k}"], kc[f"omega_{k}"], float(kc[f"g_{k}"]), float(kc[f"dt_{k}"]),
                         int(kc[f"record_{k}"].max()), record_steps=[int(s) for s in kc[f"record_{k}"]])[:, 0]


# --- integration proof 1: equivalence with the ORIGINAL kernel ----------------------------------
def test_reference_artifact_provenance(ref):
    m = ref["man"]
    assert m["file_sha256"] == FILE_PINS and m["snapshot_canonical_sha256"] == ra.SNAPSHOT_PIN["canonical_sha256"]
    run = m["original_kernel_run"]
    assert run["n_cases"] == 100 and run["kernel_file_raw_sha256"] == hashlib.sha256(
        (ra.REPO / "v9_alpha/models/phase_dynamics.py").read_bytes()).hexdigest()
    assert run["global_rng_consumed_in_every_case"] is True                  # the original draws even at zero noise
    assert run["package_import_error"] in (None, "ModuleNotFoundError: No module named 'pandas'")


def test_batched_euler_equals_the_original_kernel_on_100_states(ref):
    kc, ko = ref["kc"], ref["ko"]
    kinds = ref["man"]["kernel_case_kinds"]
    assert int(kc["n_cases"]) == 100 and {k.split(":")[0] for k in kinds} >= {"lantern", "zero", "dense", "uniform", "sparse"}
    assert {int(k.split(":")[1]) for k in kinds} >= {2, 34}
    worst = max(float(dyn.circular_distance(_ours(kc, k), ko[f"states_{k}"]).max()) for k in range(100))
    assert worst <= GATE_KERNEL, worst


def test_live_original_kernel_subset(tmp_path):
    """A fresh run of the original in a separate process on three new cases (also a non-cached check)."""
    r = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2026100802, 999])))
    snap = ra.load_verified_snapshot()
    cases = {"n_cases": np.array(3)}
    U = np.triu(r.uniform(size=(7, 7)), 1)
    for k, (C, g) in enumerate([(np.array(snap.C), float(snap.structure["g"])), (np.zeros((6, 6)), 1.0), (U + U.T, 0.7)]):
        n = C.shape[0]
        om = r.normal(0, 0.1, n)
        cases.update({f"theta_{k}": r.uniform(-np.pi, np.pi, n), f"C_{k}": C, f"omega_{k}": om - om.mean(), f"g_{k}": np.array(g),
                      f"dt_{k}": np.array(0.02), f"record_{k}": np.array([1, 50, 120])})
    np.savez(tmp_path / "cases.npz", **cases)
    out = lp.run_original_kernel(ra.REPO, tmp_path / "cases.npz", tmp_path / "orig.npz")
    with np.load(out, allow_pickle=False) as f:
        orig = {k: np.array(f[k]) for k in f.files}
    for k in range(3):
        assert float(dyn.circular_distance(_ours(cases, k), orig[f"states_{k}"]).max()) <= GATE_KERNEL


# --- integration proof 2: ODE accuracy against a high-accuracy reference -----------------------------
def _euler_errors(oc, dt):
    times = list(oc["times"])
    steps = dyn.steps_for_times(times, dt)
    out = []
    for k in range(int(oc["n_cases"])):
        e = dyn.integrate(oc[f"theta_{k}"][None], oc[f"C_{k}"], oc[f"omega_{k}"], float(oc[f"g_{k}"]), dt, steps[-1], steps)[:, 0]
        out.append(float(dyn.circular_distance(e, oc[f"reference_{k}"]).max()))
    return np.array(out)


def test_ode_reference_is_itself_accurate(ref):
    oc = ref["oc"]
    times = list(oc["times"])
    for k in (0, 12, 31):                                                  # an independent solver (Radau) on stored cases
        sol = solve_ivp(dyn.ode_rhs(oc[f"C_{k}"], oc[f"omega_{k}"], float(oc[f"g_{k}"])), (0, 10), oc[f"theta_{k}"], method="Radau",
                        t_eval=times, rtol=1e-12, atol=1e-13)
        assert float(dyn.circular_distance(dyn.wrap(sol.y.T), oc[f"reference_{k}"]).max()) < 1e-8


def test_ode_gate_open_full_panel_fails_and_euler_is_first_order(ref):
    """OPEN GATE (LR2-G1): over the panel fixed BEFORE the run the 0.005 rad limit is NOT met at
    dt = 0.02, 0.01 or 0.005 (worst: strongly coupled random graphs from random phases). This test
    documents the state; it must be revisited by the gate decision before the freeze (LR6)."""
    e = {dt: _euler_errors(ref["oc"], dt) for dt in (0.02, 0.01, 0.005)}
    assert all(e[dt].max() > GATE_ODE for dt in e)                          # gate as defined: not passed
    assert e[0.02].max() == pytest.approx(0.1165, abs=5e-4)
    ratio = e[0.02].max() / e[0.01].max(), e[0.01].max() / e[0.005].max()
    assert all(1.8 < r < 2.2 for r in ratio)                                 # first-order convergence


def test_ode_accuracy_in_the_study_regime(ref):
    """Descriptive (not a substitute for the gate): Lantern C at the study g and 5g, study-type initial states."""
    kinds = ref["man"]["ode_case_kinds"]
    e = _euler_errors(ref["oc"], 0.02)
    lantern = [k for k, kind in enumerate(kinds) if kind.startswith("lantern:34") and kind.endswith(":study")]
    assert len(lantern) == 10 and float(e[lantern].max()) <= GATE_ODE
    assert float(e[lantern].max()) == pytest.approx(2.63e-3, abs=5e-5)


# --- analytic oracles -------------------------------------------------------------------------------
def test_two_node_exact_solution():
    d0, k, t = 0.4, 0.7, 1.3
    exact = 2 * math.atan(math.tan(d0 / 2) * math.exp(-2 * k * t))
    assert exact == pytest.approx(0.0656648863608956, abs=1e-15)
    C = np.array([[0.0, k], [k, 0.0]])
    sol = solve_ivp(dyn.ode_rhs(C, np.zeros(2), 1.0), (0, t), [d0, 0.0], method="DOP853", rtol=1e-12, atol=1e-14)
    assert abs((sol.y[0, -1] - sol.y[1, -1]) - exact) < 1e-10
    errs = []
    for dt in (0.013, 0.0065):
        x = dyn.integrate(np.array([[d0, 0.0]]), C, np.zeros(2), 1.0, dt, round(t / dt))[0, 0]
        errs.append(abs((x[0] - x[1]) - exact))
    assert errs[0] < 2e-3 and 1.8 < errs[0] / errs[1] < 2.2


def test_free_drift_is_exact():
    r = np.random.default_rng(3)
    th, om = r.uniform(-np.pi, np.pi, (5, 34)), r.normal(0, 0.1, 34)
    x = dyn.integrate(th, np.zeros((34, 34)), om, 1.0, 0.02, 500)[0]
    assert float(dyn.circular_distance(x, dyn.wrap(th + 10.0 * om)).max()) < 1e-12


def test_time_rescaling():
    r = np.random.default_rng(4)
    C = np.triu(r.uniform(size=(6, 6)), 1)
    C = C + C.T
    th = r.uniform(-1, 1, (1, 6))
    for u in (10.0, 1000.0):
        a = dyn.integrate(th, C, np.zeros(6), 0.4, 0.02, 40)[0]
        b = dyn.integrate(th, C, np.zeros(6), 0.4 / u, 0.02 * u, 40)[0]
        assert float(dyn.circular_distance(a, b).max()) < 1e-12


def test_remote_transfer_linear_and_small_amplitude_nonlinear():
    C = np.zeros((4, 4))
    for i, j in [(0, 2), (2, 3), (3, 1)]:
        C[i, j] = C[j, i] = 1.0
    v = np.array([1.0, -1.0, 0.0, 0.0]) / math.sqrt(2.0)
    D = ld.difference_operator(4, [2], 3)                                    # y = x2 - x3
    E = v[:, None]
    for t in (0.0, 0.1, 0.6232252401402304, 1.0, 4.0):
        y = float(ld.H(t, C, 1.0, E, 1.0, D)[0, 0])
        assert y == pytest.approx(math.exp(-2 * t) * math.sinh(math.sqrt(2) * t), abs=1e-14)
    tp = math.atanh(1 / math.sqrt(2)) / math.sqrt(2)
    assert tp == pytest.approx(0.6232252401402304, abs=1e-15)
    assert math.exp(-2 * tp) * math.sinh(math.sqrt(2) * tp) == pytest.approx(0.28752355827362913, abs=1e-15)
    eps = 1e-4                                                                # nonlinear dynamics at small amplitude
    x = dyn.integrate((eps * v)[None], C, np.zeros(4), 1.0, 0.001, 623, wrap_states=False)[0, 0]
    assert (x[2] - x[3]) / eps == pytest.approx(0.28752355827362913, rel=2e-3)


def test_uniform_complete_graph_leaves_unwritten_outputs_exactly_zero():
    n = 6
    C = np.ones((n, n)) - np.eye(n)
    th0 = 0.7 + 0.35 * np.array([1, -1, 0, 0, 0, 0]) / math.sqrt(2)
    x = dyn.integrate(th0[None], C, np.zeros(n), 1.0, 0.02, 200, record_steps=[0, 50, 200])[:, 0]
    assert np.all(np.abs(x[:, 2:] - x[:, 2:3]) < 1e-15)                    # remote differences stay 0 (nonlinear)
    D = ld.difference_operator(n, [2, 4, 5], 3)
    assert np.abs(ld.H(1.0, C, 1.0, ld.pair_write_matrix(n, [(0, 1)]), 0.35, D)).max() < 1e-15


# --- structural gates -------------------------------------------------------------------------------
def _case():
    s = ra.load_verified_snapshot()
    r = np.random.default_rng(7)
    om = r.normal(0, 0.1, 34)
    return np.array(s.C), om - om.mean(), float(s.structure["g"]), r.uniform(-np.pi, np.pi, (4, 34))


def test_joint_permutation_and_global_rotation_equivariance():
    C, om, g, th = _case()
    perm = np.random.default_rng(1).permutation(34)
    a = dyn.integrate(th, C, om, g, 0.02, 100)[0]
    b = dyn.integrate(th[:, perm], C[np.ix_(perm, perm)], om[perm], g, 0.02, 100)[0]
    assert float(dyn.circular_distance(a[:, perm], b).max()) < 1e-12
    c = dyn.integrate(dyn.wrap(th + 2.2), C, om, g, 0.02, 100)[0]
    assert float(dyn.circular_distance(dyn.wrap(a + 2.2), c).max()) < 1e-12


def test_coupling_pulls_towards_the_neighbour_axis_order():
    d = dyn.drift(np.array([[0.0, 0.1]]), np.array([[0.0, 1.0], [1.0, 0.0]]), np.zeros(2), 1.0)[0]
    assert d[0] == pytest.approx(math.sin(0.1)) and d[1] == pytest.approx(-math.sin(0.1))


def test_inputs_are_never_modified_and_no_global_rng_is_used():
    C, om, g, th = _case()
    C0, om0, th0 = C.copy(), om.copy(), th.copy()
    np.random.seed(5)
    st = np.random.get_state()[1].copy()
    dyn.integrate(th, C, om, g, 0.02, 50)
    assert np.array_equal(C, C0) and np.array_equal(om, om0) and np.array_equal(th, th0)
    assert np.array_equal(st, np.random.get_state()[1])


@pytest.mark.parametrize("mutate, match", [
    (lambda C, om: (C * -1.0, om), "negative"),
    (lambda C, om: (np.triu(C), om), "symmetric"),
    (lambda C, om: (C + np.eye(34) * 0.1, om), "diagonal"),
    (lambda C, om: (C, om[:-1]), "omega"),
    (lambda C, om: (C.astype(bool), om), "numeric"),
    (lambda C, om: (np.where(np.eye(34) > 0, 0.0, np.nan), om), "finite"),
])
def test_invalid_inputs_are_rejected(mutate, match):
    C, om, g, th = _case()
    C2, om2 = mutate(C, om)
    with pytest.raises(dyn.DynamicsError, match=match):
        dyn.integrate(th, C2, om2, g, 0.02, 5)


def test_time_grid_maps_to_steps():
    assert dyn.steps_for_times([0, 0.5, 1, 2, 3, 5, 10], 0.02) == [0, 25, 50, 100, 150, 250, 500]
    with pytest.raises(dyn.DynamicsError):
        dyn.steps_for_times([0.03], 0.02)


def test_lab_code_never_imports_legacy_or_calls_evolve_network():
    for name in ("dynamics.py", "linear_diagnostics.py", "registry_adapter.py"):
        src = (ra.HERE / name).read_text(encoding="utf-8")
        assert "evolve_network(" not in src and "import v9_alpha" not in src and "from v9_alpha" not in src
        assert "from models" not in src and "np.random.seed" not in src


# --- linear adapter -----------------------------------------------------------------------------------
def test_write_matrix_and_reference_noise_covariance():
    E = ld.pair_write_matrix(10, [(0, 1), (2, 3), (4, 5), (6, 7)])
    assert np.allclose(E.T @ E, np.eye(4)) and np.allclose(E.sum(axis=0), 0)
    D = ld.difference_operator(10, [8, 2, 5, 9], 9)
    assert np.allclose(ld.reference_noise_covariance(D.shape[0], 0.03), 0.03 ** 2 * D @ D.T)
    with pytest.raises(dyn.DynamicsError):
        ld.pair_write_matrix(10, [(0, 1), (1, 2)])


def test_whitened_singular_values_and_fisher():
    C, om, g, th = _case()
    E = ld.pair_write_matrix(34, [(0, 1), (2, 3), (4, 5), (6, 7)])
    D = ld.difference_operator(34, list(range(8, 17)), 16)
    Hm = ld.H(1.0, C, g, E, 0.35, D)
    sv = ld.whitened_singular_values(Hm, 0.03)
    F = ld.fisher_information(Hm, 0.03)
    assert np.allclose(np.sort(np.linalg.eigvalsh(F))[::-1], sv ** 2, rtol=1e-10, atol=1e-12)
    assert np.allclose(ld.H(0.0, C, g, E, 0.35, D), 0.0)                     # write and read nodes disjoint: nothing at t=0


def test_lr2_status_yaml_twin_equals_json():
    import yaml
    p = ra.HERE / "lr2" / "lr2_status"
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
