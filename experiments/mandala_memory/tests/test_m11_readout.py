"""M11 readout core (plan Fassung 2, sections 2-3): exact linear accuracy, population
rules, nested draws, validation rule, MLP procedure. Synthetic mixtures only; the
scipy optimiser and kernel-based checks are in test_m11_kernel.py."""
import math
from statistics import NormalDist

import numpy as np
import pytest

from experiments.mandala_memory import m11_readout as mr

ND = NormalDist()


def _mixture(seed=0, K=5, N=4, scale=0.05):
    rng = np.random.default_rng(seed)
    z = rng.normal(0, scale, size=(2, K, N))
    z[1] += 0.03
    p = rng.random(K) + 0.2
    return z, p / p.sum()


def test_constant_rule_is_one_half():
    z, p = _mixture()
    assert mr.exact_accuracy(np.zeros(4), 0.7, z, p, 0.02) == 0.5


def test_single_component_matches_closed_form():
    z = np.array([[[0.0, 0.0, 0.0]], [[0.03, 0.01, -0.02]]])
    delta = z[1, 0] - z[0, 0]
    b = -0.5 * float(delta @ (z[0, 0] + z[1, 0]))
    assert mr.exact_accuracy(delta, b, z, np.ones(1), 0.02) == pytest.approx(
        ND.cdf(float(np.linalg.norm(delta)) / 0.04), abs=1e-14)


def test_exact_accuracy_matches_monte_carlo_and_is_scale_invariant():
    z, p = _mixture(1)
    w, b = np.array([1.0, -0.5, 0.3, 0.2]), -0.01
    rng = np.random.default_rng(2)
    n = 400_000
    s = rng.integers(0, 2, n)
    k = rng.choice(len(p), n, p=p)
    y = z[s, k] + rng.normal(0, 0.02, (n, 4))
    pred = mr.predict_linear(w, b, y)
    mc = np.mean([np.mean(pred[s == c] == c) for c in (0, 1)])
    ex = mr.exact_accuracy(w, b, z, p, 0.02)
    assert abs(mc - ex) <= 4 * math.sqrt(ex * (1 - ex) / (n / 2)) / math.sqrt(2) + 1e-4
    assert mr.exact_accuracy(3.7 * w, 3.7 * b, z, p, 0.02) == pytest.approx(ex, abs=1e-14)


def test_population_rules_are_the_limits_of_the_trained_rules():
    z, p = _mixture(3)
    rules = mr.population_rules(z, p, 0.02)
    mu = np.array([p @ z[s] for s in (0, 1)])
    assert np.allclose(rules["nm"][0], mu[1] - mu[0])
    draw = mr.draw_pairs("m11dev", 7, "train", 200_000, p, 4, 0.02)
    Y, lab, _ = mr.episodes(z, draw, 200_000)
    for name, fit in (("nm", mr.nm_rule), ("lda", mr.lda_rule)):
        w, b = fit(Y, lab)
        assert abs(mr.exact_accuracy(w, b, z, p, 0.02) - mr.exact_accuracy(*rules[name], z, p, 0.02)) < 0.003


def test_nm_rule_equals_the_nearest_mean_decoder():
    from experiments.mandala_memory.data import NearestMeanDecoder

    rng = np.random.default_rng(4)
    Y, lab = rng.normal(size=(500, 6)), np.repeat([0, 1], 250)
    w, b = mr.nm_rule(Y, lab)
    T = rng.normal(size=(2000, 6))
    assert np.array_equal(mr.predict_linear(w, b, T), NearestMeanDecoder().fit(Y, lab).predict(T))


def test_draws_are_nested_and_streams_separate():
    p = np.full(27, 1 / 27)
    big = mr.draw_pairs("m11", 31, "train", 16000, p, 12, 0.02)
    small = mr.draw_pairs("m11", 31, "train", 250, p, 12, 0.02)
    assert np.array_equal(big["pattern_index"][:250], small["pattern_index"])
    assert np.array_equal(big["noise"][:250], small["noise"])
    assert big["streams"] == small["streams"]                      # the streams do not depend on n
    test = mr.draw_pairs("m11", 31, "test", 250, p, 12, 0.02)
    other = mr.draw_pairs("m11", 32, "train", 250, p, 12, 0.02)
    assert not set(map(tuple, test["streams"])) & set(map(tuple, big["streams"]))
    assert not np.array_equal(other["noise"], small["noise"])
    assert mr.stream("m11", 1, "x")[1][1] not in __import__("experiments.mandala_memory.data", fromlist=["MODES"]).MODES.values()
    with pytest.raises(mr.MemoryLabError):
        mr.stream("research", 1)


def test_validation_split_is_stratified_and_keeps_pairs():
    for n in (250, 1000):
        val = mr.validation_split(n)
        assert val.sum() == n // 5
        z, p = _mixture(5, N=12)
        draw = mr.draw_pairs("m11dev", 1, "train", n, p, 12, 0.02)
        _, lab, pair = mr.episodes(z, draw, n)
        is_val = val[pair]
        assert np.sum(is_val & (lab == 0)) == np.sum(is_val & (lab == 1)) == n // 5
        assert all(is_val[pair == i].all() or not is_val[pair == i].any() for i in range(0, n, 37))


def test_mlp_gradient_matches_finite_differences():
    rng = np.random.default_rng(6)
    X, y = rng.normal(size=(40, 5)), rng.integers(0, 2, 40).astype(float)
    m = mr.MLP(hidden=7, lr=0.01, l2=1e-3, patience=5, max_epochs=10)
    m._init(rng, 5)
    _, grad = m.loss_and_grad(X, y)
    eps = 1e-6
    for k in ("W1", "b1", "w2", "b2"):
        flat = m.p[k].ravel()
        for idx in (0, len(flat) // 2, len(flat) - 1):
            old = flat[idx]
            flat[idx] = old + eps
            lp, _ = m.loss_and_grad(X, y)
            flat[idx] = old - eps
            lm, _ = m.loss_and_grad(X, y)
            flat[idx] = old
            assert grad[k].ravel()[idx] == pytest.approx((lp - lm) / (2 * eps), rel=1e-5, abs=1e-8)


HYPER = {"hidden": 32, "lr": 0.01, "l2": 1e-4, "patience": 50, "max_epochs": 1500, "inits": 2}


def test_mlp_is_deterministic_standardises_on_fit_part_and_reaches_bayes_on_two_gaussians():
    z = np.zeros((2, 1, 12))
    z[1, 0, :3] = 0.02                                     # two Gaussians: Bayes rule linear
    p = np.ones(1)
    bayes = ND.cdf(float(np.linalg.norm(z[1, 0] - z[0, 0])) / 0.04)
    draw = mr.draw_pairs("m11dev", 5, "train", 4000, p, 12, 0.02)
    Y, lab, pair = mr.episodes(z, draw, 4000)
    m1, info1 = mr.fit_mlp(Y, lab, pair, 4000, HYPER, "m11dev", 5, "two_gauss")
    m2, info2 = mr.fit_mlp(Y, lab, pair, 4000, HYPER, "m11dev", 5, "two_gauss")
    assert info1 == info2 and all(np.array_equal(m1.p[k], m2.p[k]) for k in m1.p)
    fit = ~mr.validation_split(4000)[pair]
    assert np.allclose(m1.mean, Y[fit].mean(axis=0)) and not np.allclose(m1.mean, Y.mean(axis=0), atol=0, rtol=0)
    test = mr.draw_pairs("m11dev", 5, "test", 50_000, p, 12, 0.02)
    T, tl, _ = mr.episodes(z, test, 50_000)
    assert mr.balanced_accuracy(tl, m1.predict(T)) > bayes - 0.01
    assert info1["n_fit_pairs"] == 3200 and info1["n_val_pairs"] == 800 and len(info1["inits"]) == 2
