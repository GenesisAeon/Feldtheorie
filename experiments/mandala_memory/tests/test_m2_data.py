"""M2 tests: named streams, splits, paired noise, decoder; controls K2, K4, K5, K6.

No exact-chance assertions on finite data (plan §9): K2 is checked with a
fixed seed and a wide 4-standard-error tolerance around the analytic value.
"""
import math
from statistics import NormalDist

import numpy as np
import pytest

from experiments.mandala_memory.core import MemoryLabError, build_network, recall_state
from experiments.mandala_memory.data import (
    NearestMeanDecoder,
    assert_disjoint,
    balanced_accuracy,
    confusion,
    make_episodes,
    observe_episodes,
    permutation_observation,
    stream,
    sum_observation,
)


# --- streams and determinism ----------------------------------------------------------

def test_streams_are_deterministic_and_named():
    a, ka = stream("smoke", 2026100300, "observation", "test", 8)
    b, kb = stream("smoke", 2026100300, "observation", "test", 8)
    assert ka == kb and np.array_equal(a.normal(size=5), b.normal(size=5))
    c, _ = stream("research", 2026100300, "observation", "test", 8)
    d, _ = stream("smoke", 2026100300, "observation", "validation", 8)
    e, _ = stream("smoke", 2026100300, "adaptation")
    ref = stream("smoke", 2026100300, "observation", "test", 8)[0].normal(size=5)
    for other in (c, d, e):
        assert not np.array_equal(other.normal(size=5), ref), "smoke/research, roles and purposes are disjoint streams"


def test_episode_sets_reproducible_and_ids_disjoint():
    e1 = make_episodes("smoke", 7, "test", 8, 40, 12, 0.02)
    e2 = make_episodes("smoke", 7, "test", 8, 40, 12, 0.02)
    assert e1.ids == e2.ids and np.array_equal(e1.noise, e2.noise)
    tr = make_episodes("smoke", 7, "decoder_train", 8, 40, 12, 0.02)
    va = make_episodes("smoke", 7, "validation", 8, 40, 12, 0.02)
    assert_disjoint(tr, va, e1)
    from scoped_correspondence.errors import ScopeViolationError
    with pytest.raises(ScopeViolationError):
        assert_disjoint(e1, e2)
    assert e1.labels.count(0) == e1.labels.count(1) == 40


def test_paired_conditions_share_test_noise():
    """Noise depends on the episode, not on the network condition."""
    eps = make_episodes("smoke", 11, "test", 8, 10, 12, 0.02)
    H = np.eye(12)
    frozen = build_network()
    other = build_network(coupling=False)
    Y1 = observe_episodes({c: recall_state(frozen, c, 8) for c in (0, 1)}, H, eps)
    Y2 = observe_episodes({c: recall_state(other, c, 8) for c in (0, 1)}, H, eps)
    resid1 = Y1 - np.array([recall_state(frozen, c, 8) for c in eps.labels])
    resid2 = Y2 - np.array([recall_state(other, c, 8) for c in eps.labels])
    # (x + e) - x is not bit-exact in floating point, hence a 1e-15 tolerance;
    # the noise ARRAY itself is one and the same object for both conditions
    assert np.allclose(resid1, eps.noise, rtol=0, atol=1e-15) and np.allclose(resid2, eps.noise, rtol=0, atol=1e-15)
    eps_again = make_episodes("smoke", 11, "test", 8, 10, 12, 0.02)
    assert np.array_equal(eps_again.noise, eps.noise), "regenerating the episode set gives bit-identical noise"


# --- decoder ---------------------------------------------------------------------------

def test_decoder_tie_break_and_no_labels_in_predict():
    dec = NearestMeanDecoder().fit([[0.0], [2.0]], [0, 1])
    assert dec.predict([[1.0]]).tolist() == [0], "exact tie -> class 0"
    assert dec.predict([[0.4], [1.6]]).tolist() == [0, 1]
    import inspect
    assert list(inspect.signature(dec.predict).parameters) == ["Y"], "predict takes no labels"
    with pytest.raises(MemoryLabError):
        NearestMeanDecoder().predict([[0.0]])
    with pytest.raises(MemoryLabError):
        dec.predict([[0.0, 1.0]])
    with pytest.raises(MemoryLabError):
        dec.predict([[float("nan")]])
    with pytest.raises(MemoryLabError):
        NearestMeanDecoder().fit([[0.0], [1.0]], [0, 0])
    assert dec.params()["standardization"] == "none"


def test_decoder_has_no_standardisation():
    # standardising would rescale the two coordinates and change this decision
    dec = NearestMeanDecoder().fit([[0.0, 0.0], [0.0, 0.0], [1.0, 100.0], [1.0, 100.0]], [0, 0, 1, 1])
    assert np.allclose(dec.means, [[0.0, 0.0], [1.0, 100.0]])
    assert dec.predict([[1.0, 40.0]]).tolist() == [0]


# --- K2: analytic Bayes reference vs finite decoder (fixed seed, wide tolerance) ----------

@pytest.mark.parametrize("d", [0, 1, 2, 4])
def test_k2_decoder_near_bayes(d):
    a, sigma, n = 2.0 ** -d, 0.25, 20000
    rng, _ = stream("test", 1, "k2", d)
    y = np.concatenate([a + sigma * rng.normal(size=n), -a + sigma * rng.normal(size=n)])[:, None]
    lab = np.array([0] * n + [1] * n)
    tr = np.r_[0:n // 2, n:n + n // 2]
    te = np.setdiff1d(np.arange(2 * n), tr)
    dec = NearestMeanDecoder().fit(y[tr], lab[tr])
    acc = balanced_accuracy(lab[te], dec.predict(y[te]))
    bayes = NormalDist().cdf(a / sigma)
    se = math.sqrt(bayes * (1 - bayes) / n) + 1e-4
    assert abs(acc - bayes) < 4 * se + 0.005, f"d={d}: {acc} vs Bayes {bayes}"


# --- K4: sum observation loses the identity ----------------------------------------------

def test_k4_sum_observation():
    a = 0.125
    states = {0: np.array([a, 0.0]), 1: np.array([0.0, a])}
    eps = make_episodes("test", 3, "test", 0, 50, 1, 0.02)
    eps_full = make_episodes("test", 3, "test", 0, 50, 2, 0.02)
    Ys = observe_episodes(states, sum_observation(2), eps)
    n = 50
    # with the same noise row per index, both classes give IDENTICAL sum observations
    paired = make_episodes("test", 3, "validation", 0, 50, 1, 0.02)
    same_noise = np.vstack([paired.noise[:n], paired.noise[:n]])
    from dataclasses import replace
    Yp = observe_episodes(states, sum_observation(2), replace(paired, noise=same_noise))
    assert np.array_equal(Yp[:n], Yp[n:]), "sum observation: identical for both classes"
    Yf = observe_episodes(states, np.eye(2), eps_full)
    assert not np.array_equal(Yf[:n].mean(axis=0), Yf[n:].mean(axis=0)), "full observation keeps them apart"
    assert Ys.shape == (2 * n, 1)


# --- K5: units ---------------------------------------------------------------------------------

def test_k5_scale_invariance_of_decoder():
    rng, _ = stream("test", 5, "k5")
    Y = np.vstack([rng.normal(0.1, 0.02, size=(30, 3)), rng.normal(0.0, 0.02, size=(30, 3))])
    lab = [0] * 30 + [1] * 30
    Z = rng.normal(0.05, 0.05, size=(40, 3))
    p1 = NearestMeanDecoder().fit(Y, lab).predict(Z)
    p2 = NearestMeanDecoder().fit(Y * 1000, lab).predict(Z * 1000)
    assert np.array_equal(p1, p2)


# --- K6: invertible sensor permutation ------------------------------------------------------

def test_k6_permutation_frozen_vs_refit():
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    lab = [0, 1]
    P = permutation_observation(2, [1, 0])
    assert abs(np.linalg.det(P)) == 1
    frozen = NearestMeanDecoder().fit(X, lab)
    Xs = X @ P.T
    assert balanced_accuracy(lab, frozen.predict(Xs)) == 0.0
    refit = NearestMeanDecoder().fit(Xs, lab)
    assert balanced_accuracy(lab, refit.predict(Xs)) == 1.0
    with pytest.raises(MemoryLabError):
        permutation_observation(3, [0, 0, 1])


def test_confusion_counts():
    assert confusion([0, 0, 1, 1], [0, 1, 1, 1]) == [[1, 1], [0, 2]]
