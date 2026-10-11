"""V2 (S00/S01): exact hand cases of plan §7, stochastic oracles, run contract.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import ast
import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import pytest

from experiments.kosmische_vererbung.sf001 import branching, evaluate_v2, run_v2

HERE = Path(__file__).resolve().parents[1] / "sf001"
RUN_DIR = HERE / "runs" / "v2_s00_s01"
I2 = [[1, 0], [0, 1]]


def test_modules_come_from_this_checkout():
    repo = Path(__file__).resolve().parents[3]
    assert Path(branching.__file__).resolve().is_relative_to(repo)


# --- exact hand cases (plan §7), values derived by hand before the code --------

def test_k1_identity_keeps_composition():
    p = [Fr(2, 5), Fr(3, 5)]
    assert branching.frequency_step(I2, [1, 1], p) == p


def test_k2_identity_with_unequal_reproduction():
    n1 = branching.expected_step(I2, [1, 2], [Fr(1), Fr(1)])
    n2 = branching.expected_step(I2, [1, 2], n1)
    assert n1 == [1, 2] and n2 == [1, 4]
    assert [x / sum(n2) for x in n2] == [Fr(1, 5), Fr(4, 5)]


def test_k3_erased_inheritance_returns_pi():
    pi = [Fr(1, 4), Fr(3, 4)]
    M = [[pi[0], pi[0]], [pi[1], pi[1]]]
    n1 = branching.expected_step(M, [1, 2], [Fr(2, 5), Fr(3, 5)])
    assert n1 == [Fr(2, 5), Fr(6, 5)]
    for p0 in ([Fr(1), Fr(0)], [Fr(0), Fr(1)], [Fr(2, 5), Fr(3, 5)]):
        assert branching.frequency_step(M, [1, 2], p0) == pi


def test_k4_zero_reproduction_is_extinction_without_division():
    assert branching.expected_step(I2, [0, 0], [Fr(3), Fr(5)]) == [0, 0]
    assert branching.frequency_step(I2, [0, 0], [Fr(1, 2), Fr(1, 2)]) is None
    out = branching.simulate(np.eye(2), [0, 0], [3, 5], generations=4, cap=None, seed=1)
    assert out["extinct_generation"] == 1 and out["restarts"] == 0
    assert out["type_counts"][1:] == [[0, 0]] * 4


def test_k5_relabelling_types_permutes_the_exact_result():
    M = [[Fr(9, 10), Fr(1, 5)], [Fr(1, 10), Fr(4, 5)]]
    b, n = [Fr(1), Fr(3, 2)], [Fr(2), Fr(7)]
    swap = lambda v: [v[1], v[0]]
    M_swapped = [[M[1][1], M[1][0]], [M[0][1], M[0][0]]]
    assert branching.expected_step(M_swapped, swap(b), swap(n)) == swap(branching.expected_step(M, b, n))


@pytest.mark.parametrize("M, b", [
    ([[1, 0], [1, 1]], [1, 1]),                 # column sums 2 and 1
    ([[1, 0], [0, 1]], [1, -1]),                # negative reproduction
    ([[0.5, 0.5], [0.5, 0.6]], [1, 1]),         # float column not stochastic
    ([[1, 0], [0, 1]], [1, float("nan")]),
])
def test_invalid_models_are_rejected(M, b):
    with pytest.raises(ValueError):
        branching.validate_model(M, b)


def test_mutation_and_erasure_matrices_are_column_stochastic():
    for mu in (0, 0.05, 0.2, 1):
        M = branching.mutation_matrix(5, mu)
        assert np.allclose(M.sum(0), 1) and (M >= 0).all()
    assert branching.mutation_matrix(5, 0.2)[1, 0] == pytest.approx(0.2)  # reflecting end
    assert np.allclose(branching.erasure_matrix([0.2] * 5).sum(0), 1)


# --- stochastic layer against independent oracles ------------------------------

def test_mean_population_matches_expected_operator():
    M = np.array([[0.9, 0.2], [0.1, 0.8]])
    b, n0, g, R = [1.0, 2.0], [50, 50], 3, 1500
    finals = np.array([branching.simulate(M, b, n0, g, None, np.random.SeedSequence(99, spawn_key=(r,)))["type_counts"][g]
                       for r in range(R)], dtype=float)
    expected = np.linalg.matrix_power(M @ np.diag(b), g) @ np.array(n0, float)
    se = finals.std(0, ddof=1) / math.sqrt(R)
    assert np.all(np.abs(finals.mean(0) - expected) < 4 * se), (finals.mean(0), expected, se)


def test_galton_watson_extinction_probability():
    # Poisson(2) offspring, one founder: q solves q = exp(2(q-1)); bisection here,
    # independent of the simulator.
    lo, hi = 0.0, 0.5
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if math.exp(2 * (mid - 1)) > mid else (lo, mid)
    q = lo
    assert q == pytest.approx(0.2031878699799799, abs=1e-12)
    R = 4000
    extinct = sum(branching.simulate(np.eye(1), [2.0], [1], 25, 10_000, np.random.SeedSequence(7, spawn_key=(r,)))["extinct_generation"] is not None
                  for r in range(R))
    assert abs(extinct / R - q) < 4 * math.sqrt(q * (1 - q) / R)


def test_cap_is_respected_and_never_creates_individuals():
    out = branching.simulate(np.eye(3), [3.0, 3.0, 3.0], [5, 5, 5], 8, 40, seed=3)
    totals = [sum(c) for c in out["type_counts"]]
    assert max(totals[1:]) <= 40 and out["cap_events"] >= 1
    # without mutation, types never appear from nothing
    out = branching.simulate(np.eye(3), [3.0, 3.0, 3.0], [5, 0, 5], 8, 40, seed=3)
    assert all(c[1] == 0 for c in out["type_counts"])


def test_cap_draws_uniformly_and_does_not_favour_layout_order():
    # Two equally fit types without mutation: after one capped generation the
    # share of the second type (laid out last) must stay ~1/2 on average.
    R = 400
    shares = [branching.simulate(np.eye(2), [3.0, 3.0], [50, 50], 1, 60, np.random.SeedSequence(11, spawn_key=(r,)))["type_counts"][1][1] / 60
              for r in range(R)]
    se = np.std(shares, ddof=1) / math.sqrt(R)
    assert abs(np.mean(shares) - 0.5) < 4 * se


def test_simulation_is_repeatable_and_seed_sensitive():
    args = (branching.mutation_matrix(5, 0.05), [1.0, 1.5, 2.0, 1.5, 1.0], [4] * 5, 10, 50)
    a = branching.simulate(*args, seed=np.random.SeedSequence(1, spawn_key=(0,)))
    b = branching.simulate(*args, seed=np.random.SeedSequence(1, spawn_key=(0,)))
    c = branching.simulate(*args, seed=np.random.SeedSequence(1, spawn_key=(1,)))
    assert a == b and a != c


def test_budget_counts_parents():
    out = branching.simulate(np.eye(1), [1.0], [3], 4, None, seed=5)
    assert out["individual_generations"] == sum(sum(c) for c in out["type_counts"][:4])


# --- protocol, fairness, independent evaluation ---------------------------------

@pytest.fixture(scope="module")
def protocol():
    return json.loads((HERE / "protocol_v2.json").read_text(encoding="utf-8"))


def test_protocol_is_fair(protocol):
    assert np.mean(protocol["b_neutral"]) == pytest.approx(np.mean(protocol["b_selective"]))
    assert {c["b"] for c in protocol["conditions"]} == {"b_neutral", "b_selective"}
    assert protocol["extinction_rule"] == branching.EXTINCTION_RULE
    independent = [k for k, m in protocol["metrics"].items() if m["independent_of_selection"]]
    assert len(independent) >= 3 and not protocol["metrics"]["E1_misfit"]["independent_of_selection"]


def test_evaluation_does_not_import_the_simulator():
    tree = ast.parse((HERE / "evaluate_v2.py").read_text(encoding="utf-8"))
    names = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    modules = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert "branching" not in names and not any(m and "branching" in m for m in modules)
    assert "run_v2" not in names


def test_evaluation_reference_matches_exact_layer(protocol):
    # independent re-implementation in evaluate_v2 vs. exact Fraction recursion
    K = protocol["types"]
    for c in protocol["conditions"]:
        M_eval = evaluate_v2._matrix(c["inheritance"], K)
        M_run = run_v2.inheritance_matrix(c["inheritance"], K)
        assert np.allclose(M_eval, M_run, atol=1e-15, rtol=0)
        b = [Fr(x).limit_denominator(1000) for x in protocol[c["b"]]]
        Mf = [[Fr(x).limit_denominator(10**6) for x in row] for row in M_run.tolist()]
        p = [Fr(1, K)] * K
        for _ in range(5):
            p = branching.frequency_step(Mf, b, p)
        assert np.allclose([float(x) for x in p], evaluate_v2.reference_frequencies(M_eval, protocol[c["b"]], 5), atol=1e-12)


def test_committed_run_is_reproducible_and_evaluation_is_current(protocol, tmp_path):
    committed = json.loads((RUN_DIR / "raw.json").read_text(encoding="utf-8"))
    assert committed["provenance"]["protocol_sha256"] == run_v2.text_sha256(HERE / "protocol_v2.json")
    for name, sha in committed["provenance"]["code_sha256"].items():
        assert sha == run_v2.text_sha256(HERE / name), name
    fresh = run_v2.run(protocol)
    fresh["provenance"].pop("python"), fresh["provenance"].pop("numpy")
    for key in ("python", "numpy"):
        committed["provenance"].pop(key)
    assert fresh == committed
    results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
    assert results == json.loads(json.dumps(evaluate_v2.evaluate(protocol, json.loads((RUN_DIR / "raw.json").read_text(encoding="utf-8")))))


def test_run_refuses_to_overwrite(tmp_path):
    (tmp_path / "raw.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        run_v2.main(["--out", str(tmp_path)])
