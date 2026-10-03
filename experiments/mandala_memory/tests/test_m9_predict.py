"""M9a tests: closed-form predictions (predict.py) against the derivation's
hand controls and -- ONLY for development combinations -- against the kernel.

The development combinations use exclusively values that are NOT in the
held-out grid of m9_freeze.py (c, gamma, ell, amplitude, sigma), so the held-out
combinations stay unseen. m9_freeze checks this disjointness mechanically."""
import json
import os
import subprocess
import sys
from fractions import Fraction

import numpy as np
import pytest

from experiments.mandala_memory import lab, predict

BASE = {"N": 12, "M": 3, "c": 0.25, "gamma": 0.8, "ell": 0.5, "amplitude": 0.6, "sigma": 0.02, "inputs": [0, 4],
        "readout": "full", "readout_node": 0, "nonlinearity": "tanh"}
DEV_COMBOS = [
    BASE,
    {**BASE, "gamma": 0.95}, {**BASE, "gamma": 0.5}, {**BASE, "ell": 0.25}, {**BASE, "ell": 0.9}, {**BASE, "c": 0.05},
    {**BASE, "c": 0.5}, {**BASE, "amplitude": 1.2}, {**BASE, "inputs": [0, 1]}, {**BASE, "M": 1, "c": None},
    {**BASE, "readout": "module_means"}, {**BASE, "readout": "sum"}, {**BASE, "readout": "node", "readout_node": 0},
    {**BASE, "readout": "node", "readout_node": 5}, {**BASE, "amplitude": 3.0, "ell": 1.0, "gamma": 0.95, "c": 0.0},
    {**BASE, "N": 24, "M": 12, "c": 0.05, "inputs": [3, 10], "readout": "module_means"},
    {**BASE, "N": 6, "M": 3, "c": 1.0, "inputs": [1, 4], "sigma": 0.05},
    {**BASE, "N": 18, "M": 2, "c": 0.5, "gamma": 0.95, "inputs": [2, 15], "readout": "node", "readout_node": 15, "amplitude": 3.0},
    {**BASE, "N": 18, "M": 9, "ell": 1.0, "inputs": [4, 5], "amplitude": 1.2},
    {**BASE, "nonlinearity": "identity", "amplitude": 3.0},
]


def knobs(p):
    k = {key: p[key] for key in ("N", "M", "gamma", "ell", "amplitude", "sigma", "inputs", "readout", "readout_node",
                                 "nonlinearity")}
    k["c"] = 0.25 if p["c"] is None else p["c"]
    return k


def test_benchmark_modes_equal_the_exact_hand_controls():
    m = predict.modes(BASE)
    assert m["q"] == pytest.approx(float(Fraction(9, 10)), abs=1e-15)
    assert m["mu_D"] == pytest.approx(0.75, abs=1e-15) and m["mu_I"] == pytest.approx(0.4, abs=1e-15)
    pr = predict.predict(BASE)
    for d, v in {4: 0.935319, 6: 0.801089, 7: 0.736887, 8: 0.682698, 16: 0.518973}.items():   # controls/m9_hand_controls.py
        assert pr["bayes_linear"][d] == pytest.approx(v, abs=2e-6)
    assert pr["D_linear"] == 6 and pr["D_interval"] == [6, 6] and pr["D_point_prediction"]
    assert pr["D_naive_q_rule"] == 25          # hand: 0.9^d >= r*/(g sqrt 2) = 0.07105  <=>  d <= 25.1
    assert pr["weights"]["PD_u_norm2"] == pytest.approx(2 / 4) and pr["weights"]["PI_u_norm2"] == pytest.approx(2 - 2 / 4)
    assert pr["error_bound_E"][8] < 1e-2 * pr["separation_linear"][8]          # the band is narrow here


@pytest.mark.parametrize("p", DEV_COMBOS)
def test_mode_eigenvalues_match_the_kernel_matrix(p):
    A = lab.build_lab_network(lab.validate_knobs(knobs(p)))["spec"].A
    m = predict.modes(p)
    N, M = p["N"], p["M"]
    want = [p["gamma"]] + ([m["lam_D"]] * (M - 1)) + [m["lam_I"]] * (N - M)
    assert np.allclose(sorted(np.linalg.eigvalsh(A)), sorted(want), atol=1e-12)


@pytest.mark.parametrize("NM", [(12, 3), (18, 2), (24, 6), (12, 1), (6, 3), (18, 9)])
def test_symmetry_permutation_is_an_automorphism(NM):
    N, M = NM
    A = lab.build_lab_network(lab.validate_knobs({"N": N, "M": M, "c": 0.3, "inputs": [0, 1]}))["spec"].A
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            P = predict.symmetry_permutation(N, M, i, j)
            assert P[i] == j and all(P[P[k]] == k for k in range(N))
            assert np.array_equal(A[np.ix_(P, P)], A)


@pytest.mark.parametrize("p", [c for c in DEV_COMBOS if c["nonlinearity"] == "identity"] + [{**BASE, "nonlinearity": "identity"}])
def test_identity_is_predicted_exactly(p):
    pr = predict.predict(p)
    ker = lab.compute(knobs(p))["curve"]["separation_l2"]
    assert all(e == 0 for e in pr["error_bound_E"])
    for s, k in zip(pr["separation_linear"], ker):
        assert abs(s - k) <= 1e-10 * max(s, 1e-300) + 1e-15


@pytest.mark.parametrize("p", DEV_COMBOS)
def test_band_contains_the_kernel_on_development_combinations(p):
    pr = predict.predict(p)
    ker = lab.compute(knobs(p))
    s_k = ker["curve"]["separation_l2"]
    for d, (s, e, k) in enumerate(zip(pr["separation_linear"], pr["error_bound_E"], s_k)):
        tol = 1e-12 * max(1.0, s) + 1e-15
        assert abs(k - s) <= pr["H_norm2"] * e + tol, (d, k, s, e)
    D = ker["memory_duration"]["last_delay_at_or_above"]
    lo, hi = pr["D_interval"]
    assert (-1 if lo is None else lo) <= (-1 if D is None else D) <= (-1 if hi is None else hi)


def test_sum_readout_and_module_means_structure():
    s = predict.predict({**BASE, "readout": "sum"})
    assert max(s["separation_linear"]) < 1e-15
    mm = predict.predict({**BASE, "readout": "module_means"})
    g = 0.5 * np.tanh(0.6)
    for d in (0, 3, 9):
        assert mm["separation_linear"][d] == pytest.approx(g * 0.75 ** d * np.sqrt(2) / 4, rel=1e-12)
    same = predict.predict({**BASE, "readout": "module_means", "inputs": [0, 1]})
    assert max(same["separation_linear"]) < 1e-15 and same["D_interval"][0] is None


@pytest.mark.parametrize("bad", [
    {**BASE, "M": 5}, {**BASE, "N": 12, "M": 12}, {**BASE, "gamma": 1.0}, {**BASE, "inputs": [2, 2]},
    {**BASE, "readout": "x"}, {k: v for k, v in BASE.items() if k != "sigma"}, {**BASE, "extra": 1}, {**BASE, "c": None},
])
def test_outside_family_is_rejected(bad):
    with pytest.raises(predict.OutsideFamily):
        predict.predict(bad)


def test_predict_does_not_import_the_kernel():
    code = ("import sys, experiments.mandala_memory.predict as p; "
            "bad = [m for m in sys.modules if m.startswith(('experiments.mandala_memory.core', 'experiments.mandala_memory.lab', "
            "'experiments.mandala_memory.serve', 'scoped_correspondence'))]; print(bad)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={**os.environ},
                         cwd=os.getcwd(), timeout=60)
    assert out.returncode == 0 and out.stdout.strip() == "[]", out.stderr


def test_hand_controls_script_passes():
    script = os.path.join(os.path.dirname(predict.__file__), "controls", "m9_hand_controls.py")
    out = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout)["benchmark_linear_D75"] == 6
