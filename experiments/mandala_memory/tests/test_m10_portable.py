"""M10 portable tests (numpy only): patterns, schedule, the level-B estimator
against closed form and 1-D quadrature, numerics, the update mixture, LDA,
the inference rules, the research gate and the protocol decisions."""
import json
from fractions import Fraction
from statistics import NormalDist

import numpy as np
import pytest

from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory.core import MemoryLabError
from experiments.mandala_memory.data import stream

PROTO = mt.load_protocol()


def test_patterns_and_last_channel_probabilities():
    pats = mt.patterns()
    assert len(pats) == 27 and sum(p for _, p in pats) == 1
    p_last = {lab: sum(p for pat, p in pats if mt.last_channel(pat) == lab) for lab in (mt.X, mt.Y, None)}
    assert p_last == {mt.X: Fraction(7, 16), mt.Y: Fraction(7, 16), None: Fraction(1, 8)}
    assert sum(1 for pat, _ in pats if mt.last_channel(pat) == mt.X) == 13


@pytest.mark.parametrize("d", [3, 4, 6])
def test_window_sits_directly_before_the_readout(d):
    seq = mt.input_sequence(1, (mt.X, mt.NONE, mt.Y), d)
    assert len(seq) == d + 1 and seq[0][1] == 1 and seq[0].sum() == 1
    assert seq[d - 2][2] == 1 and not seq[d - 1].any() and seq[d][3] == 1
    assert not any(seq[k].any() for k in range(1, d - 2))
    with pytest.raises(MemoryLabError):
        mt.input_sequence(0, (0, 0, 0), 2)


def _rng(*names):
    return stream("m10bayes", 77, *names)[0]


def test_estimator_matches_closed_form_for_single_components():
    m = np.array([[0.0, 0.0], [0.03, 0.01]])
    sigma = 0.02
    exact = NormalDist().cdf(np.linalg.norm(m[0] - m[1]) / (2 * sigma))
    r = mb.bayes_accuracy_mc([(m[:1], np.ones(1)), (m[1:], np.ones(1))], sigma, 400_000, _rng("single"), block=50_000)
    assert r["se"] > 0 and abs(r["estimate"] - exact) <= 4 * r["se"]


def test_estimator_matches_one_dimensional_quadrature_for_mixtures():
    A = (np.array([[0.0], [1.0]]), np.array([0.5, 0.5]))
    B = (np.array([[0.4], [2.0]]), np.array([0.3, 0.7]))
    s = 0.35
    grid = np.linspace(-4, 6, 400_001)
    pdf = lambda mix: sum(w * np.exp(-(grid - m[0]) ** 2 / (2 * s * s)) / (s * np.sqrt(2 * np.pi)) for m, w in zip(*mix))
    exact = float(np.trapezoid(np.maximum(0.5 * pdf(A), 0.5 * pdf(B)), grid))
    r = mb.bayes_accuracy_mc([A, B], s, 400_000, _rng("quad"))
    assert abs(r["estimate"] - exact) <= 4 * r["se"]


def test_log_sum_exp_is_stable_and_se_zero_is_reported():
    far = [(np.array([[0.0] * 3]), np.ones(1)), (np.array([[1.0] * 3]), np.ones(1))]
    r = mb.bayes_accuracy_mc(far, 1e-4, 20_000, _rng("far"))
    assert r["estimate"] == 1.0 and r["se"] == 0.0
    v = mb.max_posterior(np.array([[50.0, 50.0, 50.0]]), far, 1e-4)
    assert np.isfinite(v).all() and v[0] == 1.0


def test_centred_distances_equal_direct_computation():
    rng = np.random.default_rng(3)
    classes = [(rng.normal(size=(5, 4)) * 0.1 + 0.3, rng.random(5) + 0.1), (rng.normal(size=(7, 4)) * 0.1 + 0.3, rng.random(7) + 0.1)]
    y = rng.normal(size=(200, 4)) * 0.1 + 0.3
    sigma = 0.05

    def direct(y):
        ll = []
        for m, w in classes:
            d2 = ((y[:, None, :] - m[None]) ** 2).sum(-1)
            a = np.log(w / w.sum() * 0 + w)[None] - d2 / (2 * sigma ** 2)
            ll.append(np.log(np.exp(a - a.max(1, keepdims=True)).sum(1)) + a.max(1))
        ll = np.stack(ll, 1)
        return np.exp(ll.max(1) - (np.log(np.exp(ll - ll.max(1, keepdims=True)).sum(1)) + ll.max(1)))

    assert np.allclose(mb.max_posterior(y, classes, sigma), direct(y), rtol=1e-10, atol=1e-12)


def test_streams_are_fixed_and_independent():
    mix = [(np.zeros((1, 2)), np.ones(1)), (np.full((1, 2), 0.02), np.ones(1))]
    a = mb.bayes_accuracy_mc(mix, 0.02, 10_000, _rng("x"))
    b = mb.bayes_accuracy_mc(mix, 0.02, 10_000, _rng("x"))
    c = mb.bayes_accuracy_mc(mix, 0.02, 10_000, _rng("y"))
    assert a == b and a["estimate"] != c["estimate"]


def test_update_mixture_conditions_on_the_last_channel():
    pats = mt.patterns()
    z = np.random.default_rng(1).normal(size=(2, 27, 3))
    mixX, mixY = mb.update_mixtures(z, pats)
    for means, w in (mixX, mixY):
        assert means.shape == (26, 3) and abs(w.sum() - 1) < 1e-15
    idx = [i for i, (p, _) in enumerate(pats) if mt.last_channel(p) == mt.X]
    assert np.array_equal(mixX[0][:13], z[0][idx]) and np.array_equal(mixX[0][13:], z[1][idx])


def test_lda_ledoit_wolf_shrinkage_and_benefit_under_anisotropy():
    from experiments.mandala_memory.m10_decoders import LedoitWolfLDA
    from experiments.mandala_memory.data import NearestMeanDecoder

    def balanced_accuracy(y, p):                            # numpy only (data.balanced_accuracy uses SCF)
        return float(np.mean([np.mean(p[y == c] == c) for c in (0, 1)]))

    rng = np.random.default_rng(5)
    cov = np.diag([1.0, 0.01])
    mu = np.array([[0, 0], [0.5, 0.2]])
    def draw(n):
        X = np.concatenate([rng.multivariate_normal(m, cov, n) for m in mu])
        return X, np.repeat([0, 1], n)
    Xtr, ytr = draw(2000)
    Xte, yte = draw(4000)
    lda = LedoitWolfLDA().fit(Xtr, ytr)
    assert 0 <= lda.shrinkage <= 1
    acc_lda = balanced_accuracy(yte, lda.predict(Xte))
    acc_nm = balanced_accuracy(yte, NearestMeanDecoder().fit(Xtr, ytr).predict(Xte))
    assert acc_lda > acc_nm + 0.05
    iso = LedoitWolfLDA().fit(rng.normal(size=(4000, 3)), np.repeat([0, 1], 2000))
    assert iso.shrinkage > 0.5                              # isotropic data: strong shrinkage


def test_inference_rules():
    from experiments.mandala_memory.m10_evaluate import holm, one_sided_p, wording

    assert one_sided_p(0.02, 0.0, 0.01) == 0.0 and one_sided_p(0.01, 0.0, 0.01) == 1.0
    assert abs(one_sided_p(0.01 + 1.6448536, 1.0, 0.01) - 0.05) < 1e-6
    h = holm({"H-N": 0.01, "H-F+": 0.04}, 0.05)
    assert h["H-N"]["rejected"] and h["H-F+"]["rejected"] and h["H-N"]["p_holm"] == 0.02
    h = holm({"H-N": 0.03, "H-F+": 0.001}, 0.05)
    assert h["H-F+"]["rejected"] and h["H-N"]["rejected"]
    h = holm({"H-N": 0.03, "H-F+": 0.04}, 0.05)               # p(1) = 0.03 > 0.025: stop, nothing rejected
    assert not h["H-N"]["rejected"] and not h["H-F+"]["rejected"]
    assert wording(True, 0.05, 0.001) == "bestaetigt"
    assert wording(False, 0.005, 0.001) == "nicht bestaetigt"
    assert wording(False, -0.01, 0.001) == "Richtung widerspricht der Hypothese"


# research/smoke gate and release gate: see test_m10_controls.py (review R9-R12)


def test_protocol_records_the_decisions():
    p = PROTO
    assert p["status"].startswith("freeze-candidate") and p["confirmatory"]["delta"] == 0.01
    assert p["level_B"]["n_mc"] == 2_000_000 and p["delays"]["primary"] == 4
    assert p["level_D"]["role"].startswith("descriptive only") and "N/A" in p["tasks"]["update"]
    assert "DIAGNOSTIC ALARM" in p["diagnostics"]["alarm_policy"] and "No repetition" in p["diagnostics"]["alarm_policy"]
    assert p["confirmatory"]["family"] == ["H-N", "H-F+"] and p["confirmatory"]["holm"]["alpha"] == 0.05
    # the stated numbers of numeric diagnostic checks follow from the conditions and the symmetry
    n_a2 = sum(mt.condition_is_p_fixed(mt.swap_permutation(12, p["networks"][n]["M"]), c)
               for n in ("modular", "uniform") for k, c in p["conditions"].items() if c is not None) * len(p["delays"]["all"])
    n_a3 = 2 * 3 * len(p["delays"]["all"])
    assert (n_a2, n_a3) == (15, 18) and "A2_numeric 15" in p["diagnostics"]["alarm_policy"]
    assert set(p["development"]["conditions"]) == {"K0", "Fdev", "Ndev"}
    research_sites = {(c["X"], c["Y"], c["amplitude"]) for c in p["conditions"].values() if c}
    dev_sites = {(c["X"], c["Y"], c["amplitude"]) for c in p["development"]["conditions"].values() if c}
    assert not research_sites & dev_sites and not set(p["level_D"]["seeds"]) & set(p["development"]["seeds"])
