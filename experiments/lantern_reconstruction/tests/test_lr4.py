"""LR4: Ridge (NumPy closed form) and evaluation. Plan section 14 acceptance: analytical scores, no
episode pseudo-replicates, artifact round trip; plus plan 8 (standardisation, unpenalised intercept,
lambda convention, selection, projection), plan 9 (S/G/A, context intervals, H-B1/B2 + Holm) and the
plan mutants 11, 13, 14, 15, 16 (12 = MLP initialisation: not applicable to Ridge; its analogue -- no
test data in the fit -- is tested). Every reference value is derived independently of the code under test."""
from __future__ import annotations

import ast
import inspect
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from experiments.lantern_reconstruction import (contexts, decoders, episodes, evaluate, metrics, observation,
                                                runner, streams, training)
from experiments.lantern_reconstruction import registry_adapter as ra

SID = streams.defaults()["development_study_id"]
HERE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ctx():
    return contexts.make_context(SID, 0)


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(12345)              # test data only, not a study stream
    N, d = 60, 8
    X = rng.normal(size=(N, d)) * np.arange(1, d + 1) + 3.0
    X[:, 2] = 7.0                                    # constant column -> scale 1
    X[:, 5] = 2 * X[:, 4] - 1                        # collinear column
    U = rng.uniform(-1, 1, (N, 4))
    return X, U


def _objective(Xs, U, W, b, lam):
    r = Xs @ W + b - U
    return float(np.sum(r ** 2) / Xs.shape[0] + lam * np.sum(W ** 2))


# --- Ridge: exact solution ---------------------------------------------------------------------------
def test_ridge_one_dimensional_exact_by_fractions():
    """X = (1, 3), U = (0, 4) in every output: mean 2, population SD 1 -> X_s = (-1, 1); the objective
    (1/2) sum (w x_s + b - u)^2 + lam w^2 is minimised by b = 2, w = 2 / (1 + lam)."""
    X = np.array([[1.0], [3.0]])
    U = np.repeat(np.array([[0.0], [4.0]]), 4, axis=1)
    mean, scale = training.standardisation(X)
    assert mean.tolist() == [2.0] and scale.tolist() == [1.0]
    for lam_f in (Fraction(1, 10000), Fraction(1, 2), Fraction(1), Fraction(100)):
        (W, b), = training.ridge_path((X - mean) / scale, U, [float(lam_f)])
        w_exact = Fraction(2) / (1 + lam_f)
        assert np.allclose(W, float(w_exact), rtol=0, atol=1e-15) and np.allclose(b, 2.0, rtol=0, atol=1e-15)


def test_ridge_equals_two_independent_solvers_and_zero_gradient(data):
    X, U = data
    mean, scale = training.standardisation(X)
    Xs, N, d = (X - mean) / scale, X.shape[0], X.shape[1]
    for lam, (W, b) in zip(training.LAMBDA_GRID, training.ridge_path(Xs, U, training.LAMBDA_GRID)):
        # (1) augmented least squares with an UNPENALISED intercept column
        A = np.vstack([np.hstack([Xs, np.ones((N, 1))]), np.hstack([math.sqrt(N * lam) * np.eye(d), np.zeros((d, 1))])])
        sol = np.linalg.lstsq(A, np.vstack([U, np.zeros((d, 4))]), rcond=None)[0]
        assert np.max(np.abs(sol[:d] - W)) < 1e-9 and np.max(np.abs(sol[d] - b)) < 1e-9
        # (2) normal equations of the plan objective incl. the intercept block
        M = np.zeros((d + 1, d + 1))
        M[:d, :d] = Xs.T @ Xs / N + lam * np.eye(d)
        M[:d, d] = M[d, :d] = Xs.mean(axis=0)
        M[d, d] = 1.0
        rhs = np.vstack([Xs.T @ U / N, U.mean(axis=0)])
        ne = np.linalg.solve(M, rhs)
        assert np.max(np.abs(ne[:d] - W)) < 1e-8 and np.max(np.abs(ne[d] - b)) < 1e-8
        # (3) gradient of the plan objective vanishes
        r = Xs @ W + b - U
        assert np.max(np.abs(2 / N * Xs.T @ r + 2 * lam * W)) < 1e-10 and np.max(np.abs(2 / N * r.sum(0))) < 1e-12
        # (4) a perturbation never lowers the objective
        rng = np.random.default_rng(7)
        f0 = _objective(Xs, U, W, b, lam)
        for _ in range(5):
            assert _objective(Xs, U, W + 1e-4 * rng.normal(size=W.shape), b + 1e-4 * rng.normal(size=4), lam) >= f0


def test_intercept_is_unpenalised(data):
    """Shifting every target by c shifts b by exactly c and leaves W unchanged, also at lambda = 100."""
    X, U = data
    mean, scale = training.standardisation(X)
    Xs = (X - mean) / scale
    for (W, b), (W2, b2) in zip(training.ridge_path(Xs, U, [1e-4, 100.0]), training.ridge_path(Xs, U + 5.0, [1e-4, 100.0])):
        assert np.allclose(W, W2, rtol=0, atol=1e-12) and np.allclose(b2 - b, 5.0, rtol=0, atol=1e-12)


def test_lambda_convention_is_averaged_plan_mutant_13(data):
    """With the 1/N objective, duplicating every training row leaves W unchanged at the same lambda; with
    the unaveraged (scikit-learn) objective the equivalent alpha is N * lambda."""
    X, U = data
    mean, scale = training.standardisation(X)
    Xs = (X - mean) / scale
    N = Xs.shape[0]
    (W1, b1), = training.ridge_path(Xs, U, [0.1])
    (W2, b2), = training.ridge_path(np.vstack([Xs, Xs]), np.vstack([U, U]), [0.1])
    assert np.max(np.abs(W1 - W2)) < 1e-12 and np.max(np.abs(b1 - b2)) < 1e-12
    Xc, Uc = Xs - Xs.mean(0), U - U.mean(0)
    alpha = N * 0.1
    W_unavg = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(Xs.shape[1]), Xc.T @ Uc)
    assert np.max(np.abs(W_unavg - W1)) < 1e-10
    W_wrong = np.linalg.solve(Xc.T @ Xc + 0.1 * np.eye(Xs.shape[1]), Xc.T @ Uc)      # the mutant: alpha = lambda
    assert np.max(np.abs(W_wrong - W1)) > 1e-3


def test_standardisation_train_only_constant_column_ddof0_plan_mutant_11(data, ctx):
    X, U = data
    mean, scale = training.standardisation(X)
    assert np.array_equal(mean, X.mean(0)) and scale[2] == 1.0
    assert np.allclose(scale[[0, 1, 3]], np.sqrt(np.mean((X[:, [0, 1, 3]] - X[:, [0, 1, 3]].mean(0)) ** 2, axis=0)), rtol=1e-15)
    spec = observation.observation_spec(ctx, "B")
    rng = np.random.default_rng(3)
    Xtr, Xva = rng.normal(size=(50, 16)), rng.normal(size=(20, 16))
    Utr, Uva = rng.uniform(-1, 1, (50, 4)), rng.uniform(-1, 1, (20, 4))
    m1 = training.fit_ridge(spec, Xtr, Utr, Xva, Uva)
    m2 = training.fit_ridge(spec, Xtr, Utr, Xva * 50 + 9, Uva)            # other validation data: same statistics
    assert np.array_equal(m1.mean, Xtr.mean(0)) and np.array_equal(m1.mean, m2.mean) and np.array_equal(m1.scale, m2.scale)
    assert list(inspect.signature(training.fit_ridge).parameters) == ["spec", "X_train", "U_train", "X_val", "U_val",
                                                                        "lambda_grid", "provenance"]   # no test argument (mutant 12 analogue)


def test_selection_projected_val_mse_and_tie_to_larger_lambda(ctx):
    assert decoders.select_lambda([1e-4, 1e-2, 1.0], [0.3, 0.2, 0.25]) == 1e-2
    assert decoders.select_lambda([1e-4, 1e-2, 1.0], [0.2, 0.2, 0.25]) == 1e-2          # exact tie -> larger
    assert decoders.select_lambda([1.0, 1e-4, 1e-2], [0.2, 0.2, 0.2]) == 1.0
    spec = observation.observation_spec(ctx, "B")
    rng = np.random.default_rng(4)
    Xtr, Xva = rng.normal(size=(80, 16)), rng.normal(size=(30, 16))
    Utr, Uva = rng.uniform(-1, 1, (80, 4)), rng.uniform(-1, 1, (30, 4))
    m = training.fit_ridge(spec, Xtr, Utr, Xva, Uva)
    mean, scale = training.standardisation(Xtr)
    for lam, (W, b), mse in zip(training.LAMBDA_GRID, training.ridge_path((Xtr - mean) / scale, Utr, training.LAMBDA_GRID), m.val_mse):
        assert mse == np.mean((np.clip(((Xva - mean) / scale) @ W + b, -1, 1) - Uva) ** 2)
    assert m.lam == decoders.select_lambda(training.LAMBDA_GRID, m.val_mse) and tuple(m.lambda_grid) == training.LAMBDA_GRID
    # few training episodes, small lambda: raw validation predictions leave [-1, 1], so projection matters
    # (mutation check: on the data above the clip never acted and an unprojected selection survived)
    Xs_tr, Xs_va, Us_tr = rng.normal(size=(18, 16)), rng.normal(size=(30, 16)), rng.uniform(-1, 1, (18, 4))
    m2 = training.fit_ridge(spec, Xs_tr, Us_tr, Xs_va, Uva)
    mean, scale = training.standardisation(Xs_tr)
    W, b = training.ridge_path((Xs_tr - mean) / scale, Us_tr, [1e-4])[0]
    raw = ((Xs_va - mean) / scale) @ W + b
    assert np.any(np.abs(raw) > 1)
    assert m2.val_mse[0] == np.mean((np.clip(raw, -1, 1) - Uva) ** 2) != np.mean((raw - Uva) ** 2)
    with pytest.raises(ValueError, match="lambda grid"):
        training.fit_ridge(spec, Xtr, Utr, Xva, Uva, lambda_grid=(0.0, 1.0))
    with pytest.raises(ValueError):
        training.fit_ridge(spec, Xtr[:, :15], Utr, Xva, Uva)


# --- predict / evaluator separation / artifacts ------------------------------------------------------------
def test_predict_sees_only_features_and_evaluator_has_no_fit():
    assert list(inspect.signature(decoders.predict).parameters) == ["model", "X"]
    tree = ast.parse((HERE / "evaluate.py").read_text(encoding="utf-8"))
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
               {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not any("training" in m for m in imported) and not hasattr(evaluate, "fit_ridge")
    for module in ("decoders.py", "evaluate.py"):
        defs = [n.name for n in ast.walk(ast.parse((HERE / module).read_text(encoding="utf-8"))) if isinstance(n, ast.FunctionDef)]
        assert not any("fit" in name for name in defs), (module, defs)


@pytest.fixture(scope="module")
def model(ctx):
    rng = np.random.default_rng(5)
    spec = observation.observation_spec(ctx, "A")
    return training.fit_ridge(spec, rng.normal(size=(120, 66)), rng.uniform(-1, 1, (120, 4)), rng.normal(size=(40, 66)),
                              rng.uniform(-1, 1, (40, 4)), provenance={"context_id": 0, "time": 1.0})


@pytest.mark.parametrize("bad", [np.zeros((3, 65)), np.zeros(66), np.full((3, 66), np.nan), np.zeros((3, 66), dtype=bool),
                                 np.zeros((0, 66)), np.zeros((3, 66), dtype=complex)])
def test_predict_rejects_invalid_features(model, bad):
    with pytest.raises(ValueError, match="features"):
        decoders.predict(model, bad)


def test_artifact_round_trip_numeric_identity(model, tmp_path):
    decoders.save(model, tmp_path / "m")
    back = decoders.load(tmp_path / "m")
    X = np.random.default_rng(6).normal(size=(25, 66))
    assert np.array_equal(decoders.predict(back, X), decoders.predict(model, X))
    for k in decoders.ARRAYS:
        assert np.array_equal(getattr(back, k), getattr(model, k)) and not getattr(back, k).flags.writeable
    assert back.lam == model.lam and back.provenance == model.provenance and back.software == model.software
    meta = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert meta["objective"] == decoders.OBJECTIVE and set(meta["arrays"]) == set(decoders.ARRAYS)


def test_artifact_tampering_detected(model, tmp_path):
    decoders.save(model, tmp_path / "m")
    with np.load(tmp_path / "m.npz", allow_pickle=False) as z:
        arrays = {k: z[k].copy() for k in z.files}
    arrays["W"][0, 0] += 1e-12
    np.savez(tmp_path / "w.npz", **arrays)
    (tmp_path / "w.json").write_text((tmp_path / "m.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        decoders.load(tmp_path / "w")
    np.savez(tmp_path / "x.npz", **{**{k: v for k, v in arrays.items()}, "extra": np.zeros(1)})
    (tmp_path / "x.json").write_text((tmp_path / "m.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly"):
        decoders.load(tmp_path / "x")
    obj = dict(arrays)
    obj["b"] = np.array([{"a": 1}], dtype=object)
    np.savez(tmp_path / "p.npz", **obj)
    (tmp_path / "p.json").write_text((tmp_path / "m.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError):
        decoders.load(tmp_path / "p")                                   # object arrays need pickle: refused
    meta = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    other = [x for x in training.LAMBDA_GRID if x != model.lam][0]
    (tmp_path / "m.json").write_text(json.dumps({**meta, "lambda": other}), encoding="utf-8")
    with pytest.raises(ValueError, match="selection rule"):
        decoders.load(tmp_path / "m")
    (tmp_path / "m.json").write_text(json.dumps(meta).replace('"n_train": 120', '"n_train": NaN'), encoding="utf-8")
    with pytest.raises(ValueError):
        decoders.load(tmp_path / "m")


# --- metrics: analytical controls K19-K22 and scores -------------------------------------------------------
def test_k19_score_is_not_gain_and_k22_negative_gain_is_valid_plan_mutant_14():
    target = np.array([[.1] * 4, [.2] * 4])
    s = metrics.scores(*metrics.episode_losses(np.zeros_like(target), target))
    assert math.isclose(s["S"], 0.925, abs_tol=1e-15) and s["G"] == 0.0
    s_bad = metrics.scores(*metrics.episode_losses(np.ones_like(target), target))
    assert math.isclose(s_bad["G"], -2.1, abs_tol=1e-14)                   # 3 * (0.025 - 0.725)
    cell = {0.0: -2.1, 0.5: -1.0, 1.0: 0.0, 2.0: 0.0, 3.0: 0.0, 5.0: 0.0, 10.0: 0.0}
    assert metrics.curve_aggregate(cell) < 0                                 # negative values enter unchanged


def test_analytical_scores_perfect_and_zero_predictions():
    u = np.random.default_rng(8).uniform(-1, 1, (500, 4))
    perfect = metrics.scores(*metrics.episode_losses(u, u))
    assert perfect["S"] == 1.0 and math.isclose(perfect["G"], 3 * np.mean(u ** 2), rel_tol=1e-15)
    zero = metrics.scores(*metrics.episode_losses(np.zeros_like(u), u))
    assert zero["G"] == 0.0 and math.isclose(zero["S"], 1 - 3 * np.mean(u ** 2), rel_tol=1e-14)
    with pytest.raises(ValueError, match="projected"):
        metrics.episode_losses(u * 2, u)
    assert np.array_equal(metrics.project(np.array([[-3, -1, 0.5, 2]])), np.array([[-1, -1, 0.5, 1]]))


def test_k21_grid_weights_closed_form():
    """w0 = ln1.5/(2 ln11); w1..w4 = ln2/(2 ln11) (log-steps ln1.5 and ln(4/3) alternate); w5 = ln(11/4)/(2 ln11);
    w6 = ln(11/6)/(2 ln11)."""
    L = 2 * math.log(11)
    expect = [math.log(1.5) / L] + [math.log(2) / L] * 4 + [math.log(11 / 4) / L, math.log(11 / 6) / L]
    w = metrics.grid_weights()
    assert np.max(np.abs(w - expect)) < 1e-15 and abs(w.sum() - 1) < 1e-15
    ref = [0.08454604183671918, 0.1445324131589439, 0.14453241315894394, 0.1445324131589439, 0.14453241315894388,
           0.21093517368211218, 0.126389131845393]                          # K21 values of the review package
    assert np.max(np.abs(w - ref)) < 1e-15
    grid = [0, .5, 1, 2, 3, 5, 10]
    assert math.isclose(metrics.curve_aggregate({t: 0.37 for t in grid}), 0.37, rel_tol=1e-15)
    lin = metrics.curve_aggregate({t: math.log1p(t) for t in grid})        # trapezoid is exact for linear in z
    assert math.isclose(lin, math.log(11) / 2, rel_tol=1e-15)


@pytest.mark.parametrize("bad", [{0: 1, .5: 1, 1: 1, 2: 1, 3: 1, 5: 1},                      # missing cell (mutant 16)
                                 {0: 1, .5: 1, 1: 1, 2: 1, 3: 1, 5: 1, 10: 1, 20: 1},          # extra time
                                 {0: 1, .5: 1, 1: 1, 2: 1, 3: 1, 5: 1, 10: float("nan")},
                                 [1, 1, 1, 1, 1, 1, 1]])                                       # no time keys
def test_curve_aggregate_requires_the_complete_grid(bad):
    with pytest.raises(ValueError):
        metrics.curve_aggregate(bad)


# --- context inference -------------------------------------------------------------------------------------
def _t_cdf_independent(x, df, n=20000):
    """Student t CDF by Simpson integration of the density from 0 (no scipy.stats)."""
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    h = x / n
    f = [c * (1 + (k * h) ** 2 / df) ** (-(df + 1) / 2) for k in range(n + 1)]
    return 0.5 + h / 3 * (f[0] + f[-1] + 4 * sum(f[1:-1:2]) + 2 * sum(f[2:-1:2]))


def test_t_interval_and_bonferroni_quantiles_independent():
    vals = {c: v for c, v in enumerate(np.linspace(-.1, .3, 20))}
    s = metrics.summarize(vals)
    assert s["n_contexts"] == 20 and s["df"] == 19 and math.isclose(s["t_quantile"], 2.093024054408263, rel_tol=1e-12)
    assert abs(_t_cdf_independent(s["t_quantile"], 19) - 0.975) < 1e-10
    bonf = metrics.summarize(vals, 1 - 0.05 / 2)
    assert abs(_t_cdf_independent(bonf["t_quantile"], 19) - 0.9875) < 1e-10
    v = np.array(list(vals.values()))
    se = np.std(v, ddof=1) / math.sqrt(20)
    assert np.allclose(s["interval"], [v.mean() - 2.093024054408263 * se, v.mean() + 2.093024054408263 * se], rtol=1e-12)


def test_one_sided_t_closed_form_df2():
    """df = 2: P(T > t) = (1 - t / sqrt(t^2 + 2)) / 2. Values .1, .2, .3, margin .05: t = .15 / (.1 / sqrt 3)."""
    r = metrics.one_sided_t({3: .1, 7: .2, 9: .3}, 0.05)
    t = 0.15 / (0.1 / math.sqrt(3))
    assert math.isclose(r["t"], t, rel_tol=1e-12) and math.isclose(r["p"], (1 - t / math.sqrt(t * t + 2)) / 2, rel_tol=1e-10)
    assert r["df"] == 2 and r["n_contexts"] == 3


def test_no_episode_pseudo_replicates_plan_mutant_15():
    """The inference sees one value per context ID: episode arrays are refused; df = contexts - 1."""
    for bad in (np.ones(1000), [0.1] * 1000, {0: 0.1}, {0.5: 0.1, 1: 0.2}, {True: .1, 2: .2}, {-1: .1, 2: .2}):
        with pytest.raises(ValueError):
            metrics.summarize(bad)
    s = metrics.summarize({0: .1, 1: .3})
    assert s["df"] == 1 and s["n_contexts"] == 2
    with pytest.raises(ValueError, match="same contexts"):
        metrics.paired_differences({0: .1, 1: .2}, {0: .1, 2: .2})


def test_degenerate_sd_is_descriptive():
    s = metrics.summarize({0: .2, 1: .2, 2: .2})
    assert s["degenerate"] and s["interval"] == [.2, .2]
    r = metrics.one_sided_t({0: .2, 1: .2}, .05)
    assert r["degenerate"] and r["t"] is None and r["p"] is None
    h = metrics.hypotheses_B({0: .2, 1: .2}, {0: .1, 1: .0})
    assert h["rejected"] is None and "degenerate" in h["note"]


def test_k20_holm_and_hypotheses_B():
    assert np.allclose(metrics.holm([.03, .04]), [.06, .06])
    assert np.allclose(metrics.holm([.04, .03]), [.06, .06])
    assert np.allclose(metrics.holm([.01, .2, .03]), [.03, .2, .06])
    assert metrics.holm([.6, .7]) == [1.0, 1.0]
    lan = {c: .30 + .01 * c for c in range(20)}
    sur = {c: .10 + .012 * c for c in range(20)}
    h = metrics.hypotheses_B(lan, sur)
    d = {c: lan[c] - sur[c] for c in lan}
    p1, p2 = metrics.one_sided_t(lan, .05)["p"], metrics.one_sided_t(d, .05)["p"]
    assert h["holm_adjusted"] == metrics.holm([p1, p2]) and h["rejected"] == [a <= .05 for a in metrics.holm([p1, p2])]
    assert h["bonferroni_intervals"]["H_B1"]["level"] == 0.975 and "not simultaneous" in h["raw_intervals_95"]["H_B1"]["interval_kind"]


def test_permutation_p_and_leak_alarm():
    assert metrics.permutation_p(0, 9999) == 1e-4 and metrics.permutation_p(9999, 9999) == 1.0
    for b, B in ((-1, 10), (11, 10), (True, 10), (1, 0), (1.0, 10)):
        with pytest.raises(ValueError):
            metrics.permutation_p(b, B)
    rng = np.random.default_rng(9)
    u = {c: rng.uniform(-1, 1, (60, 4)) for c in range(3)}
    perfect = metrics.permutation_gain_test({c: (u[c], u[c]) for c in u}, np.random.default_rng(1), 199)
    assert perfect["b"] == 0 and perfect["p"] == 1 / 200
    noise = metrics.permutation_gain_test({c: (np.clip(rng.normal(0, .3, (60, 4)), -1, 1), u[c]) for c in u}, np.random.default_rng(2), 199)
    assert noise["p"] > 0.01
    assert not metrics.leak_alarm([.5] * 12)["alarm"] and metrics.leak_alarm([1e-4] + [.5] * 11)["alarm"]
    held = metrics.leak_alarm([.005] + [.5] * 11)                  # raw p <= .01, Holm-adjusted .06: no alarm
    assert not held["alarm"] and math.isclose(held["holm_adjusted"][0], .06)
    with pytest.raises(ValueError):
        metrics.leak_alarm([.5] * 11)
    with pytest.raises(ValueError, match="Generator"):
        metrics.permutation_gain_test({0: (u[0], u[0]), 1: (u[1], u[1])}, None, 9)


# --- runner: development only, phases and splits --------------------------------------------------------------
@pytest.fixture(scope="module")
def lantern():
    s = ra.load_verified_snapshot()
    return np.array(s.C), float(s.structure["g"])


SMALL = {"train": 40, "val": 20, "test": 30}


def test_runner_refuses_non_development_study(lantern):
    with pytest.raises(ValueError, match="development-only"):
        runner.run_context(contexts.make_context(SID + 1, 0), *lantern, sizes=SMALL)


def test_runner_uses_observe_and_keeps_splits_apart(ctx, lantern, monkeypatch):
    calls, fits = [], []
    real_observe, real_fit = observation.observe, runner.fit_ridge
    monkeypatch.setattr(observation, "observe", lambda *a, **k: calls.append(a[1].task) or real_observe(*a, **k))
    monkeypatch.setattr(runner, "fit_ridge", lambda spec, Xtr, Utr, Xva, Uva, **k: fits.append((Xtr.shape, Utr, Xva.shape, Uva)) or real_fit(spec, Xtr, Utr, Xva, Uva, **k))
    r = runner.run_context(ctx, *lantern, sizes=SMALL, conditions=("lantern", "uncoupled"), proposals=200)
    assert len(calls) == 2 * 2 * 7 * 3 and set(calls) == {"A", "B"}
    tr, va = episodes.make_batch(ctx, "train", range(40)).u, episodes.make_batch(ctx, "val", range(20)).u
    assert len(fits) == 2 * 2 * 7 and all(s1[0] == 40 and np.array_equal(u1, tr) and s2[0] == 20 and np.array_equal(u2, va) for s1, u1, s2, u2 in fits)
    for task in ("A", "B"):                                    # t = 0: identical states for all conditions
        assert r["cells"][("lantern", task)]["G"][0.0] == r["cells"][("uncoupled", task)]["G"][0.0]
    for cell in r["cells"].values():
        assert sorted(cell["G"]) == [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0] and math.isclose(cell["A"], metrics.curve_aggregate(cell["G"]))


def test_runner_features_only_through_observe(ctx, lantern, monkeypatch):
    """features() may run only inside observe(): the runner never calls the context-free kernel directly."""
    import sys
    real = observation.features

    def guarded(*a, **k):
        if sys._getframe(1).f_code.co_name != "observe":
            pytest.fail("features() called outside observe()")
        return real(*a, **k)
    monkeypatch.setattr(observation, "features", guarded)
    runner.run_context(ctx, *lantern, sizes=SMALL, conditions=("uncoupled",), tasks=("B",), proposals=200)


@pytest.mark.parametrize("stem", ["protocol/decoder_convergence_gate", "lr4/lr4_status"])
def test_yaml_twins(stem):
    import yaml
    p = HERE / stem
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))


def test_gate_result_bound_to_its_definition_and_consistent():
    """The stored gate summary must come from THIS gate definition (SHA of the LF-normalised file) and its
    pass flags must follow from its own numbers."""
    import hashlib
    import yaml
    p = HERE / "lr4" / "lr4_decoder_convergence"
    s = json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == s and not s["smoke_only"]
    gate = (HERE / "protocol" / "decoder_convergence_gate.json").read_bytes().replace(b"\r\n", b"\n")
    assert s["gate_file_sha256"] == hashlib.sha256(gate).hexdigest() and s["config_sha256"] == streams.config_sha256()
    dg = s["decoder_gate"]
    assert dg["passed"] == (dg["max_abs_dG"] <= 0.01 and dg["max_abs_dA"] <= 0.01)
    assert s["pipeline_gate_A_t0"]["passed"] == all(v > 0.90 for v in s["pipeline_gate_A_t0"]["mean_G0_by_condition"].values())
    assert s["panel"]["contexts"] == [0, 1] and s["panel"]["dt"] == [0.02, 0.01, 0.005]


def test_simulate_dt_override_only_for_convergence(ctx, lantern):
    C, g = lantern
    b = episodes.make_batch(ctx, "test", range(3))
    base = episodes.simulate(ctx, b, C, g)
    assert np.array_equal(base, episodes.simulate(ctx, b, C, g, dt=streams.defaults()["integration"]["dt"]))
    half = episodes.simulate(ctx, b, C, g, dt=0.01)
    assert 0 < np.max(np.abs(np.angle(np.exp(1j * (half - base))))) < 1e-5
    for bad in (0.03, True, 0.0, -0.01, float("nan")):
        with pytest.raises(ValueError):
            episodes.simulate(ctx, b, C, g, dt=bad)
