"""M11 optimiser, reference phase, runner and gate (development cases only; needs scipy
and the kernel/SCF). Research references are NOT computed here."""
import json
from statistics import NormalDist

import numpy as np
import pytest

from experiments.mandala_memory import m11_evaluate as ev
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m11_references as mref
from experiments.mandala_memory import m11_run
from experiments.mandala_memory.core import MemoryLabError

PROTO = mref.load_protocol()
SMALL = {"hidden": 8, "lr": 0.03, "l2": 1e-4, "patience": 10, "max_epochs": 60, "inits": 2}


def test_optimiser_finds_a_known_linear_optimum():
    z = np.zeros((2, 1, 6))
    z[1, 0, :2] = [0.02, -0.01]                            # two Gaussians: the Bayes rule is linear
    bayes = NormalDist().cdf(float(np.linalg.norm(z[1, 0] - z[0, 0])) / 0.04)
    ref = mr.linear_reference(z, np.ones(1), 0.02, mr.stream("m11dev", 1, "t")[0], n_random=5)
    assert ref["L_found"] == pytest.approx(bayes, abs=1e-8) and len(ref["runs"]) == 7


def test_l_found_never_below_the_population_rules_on_a_mixture():
    rng = np.random.default_rng(3)
    z = rng.normal(0, 0.04, size=(2, 6, 5))
    z[1] += 0.02
    p = rng.random(6) + 0.1
    p /= p.sum()
    rules = mr.population_rules(z, p, 0.02)
    ref = mr.linear_reference(z, p, 0.02, mr.stream("m11dev", 2, "t")[0], n_random=4)
    assert ref["L_found"] >= max(mr.exact_accuracy(*rules[k], z, p, 0.02) for k in ("nm", "lda")) - 1e-15
    assert ref["n_within_1e-4_of_best"] >= 1 and ref["label"].startswith("numerical linear reference")


def test_reference_phase_refuses_unversioned_procedures(monkeypatch):
    monkeypatch.setattr(mref, "git_clean", lambda paths: False)
    with pytest.raises(SystemExit, match="not committed"):
        mref.main(["--cases", "research"])
    with pytest.raises(SystemExit):
        mref.main(["--cases", "research", "--out", "D:/mandala/.tmp/x.json"])


def test_dev_references_and_the_bayes_source_check(monkeypatch):
    refs = mref.compute("dev")
    for name, r in refs["cases"].items():
        assert 0.5 <= r["acc_nm_inf"] <= r["L_found"] + 1e-15 and r["acc_lda_inf"] <= r["L_found"] + 1e-15
        assert r["L_found"] <= r["B"] + 4 * r["B_se"] + 1e-9          # a linear rule cannot beat Bayes (up to MC SE)
    bad = {**PROTO["bayes_source"]["dev"], "sha256": "0" * 64}
    with pytest.raises(MemoryLabError, match="SHA-256"):
        mref.bayes_reference(PROTO["development"]["cases"][0], bad)


@pytest.mark.parametrize("mode", ["smoke", "research"])
def test_smoke_and_research_blocked_before_the_freeze(mode):
    with pytest.raises(MemoryLabError, match="not frozen"):
        m11_run.run(mode, None, write=False)


def test_small_development_run_end_to_end_and_exact_vs_test():
    res = m11_run.run("dev", None, seeds=[901], n_grid=[250, 1000], test_pairs=20_000, hyper=SMALL, write=False)
    assert res["status"] == "complete" and len(res["rows"]) == 4 * 2
    for r in res["rows"]:
        for dec in ("nm", "lda"):                          # test-set cross-check of the exact formula
            assert abs(r[dec]["exact"] - r[dec]["test"]) < 0.015
        assert r["mlp"]["fit"]["n_val_pairs"] == r["n"] // 5
    assert not ev.release(res)["released"]


def test_timeout_is_enforced(monkeypatch):
    t = {"now": 0.0}

    def clock():
        t["now"] += 50.0
        return t["now"]
    monkeypatch.setattr(m11_run, "clock", clock)
    res = m11_run.run("dev", None, seeds=[901], n_grid=[250], test_pairs=2000, hyper=SMALL, time_limit_s=120.0, write=False)
    assert res["status"] == "aborted_timeout"


# --- gate on a synthetic research result built independently -----------------------
def synthetic():
    s_mode = PROTO["modes"]["research"]
    rows = []
    for s in PROTO["seeds"]["research"]:
        tr = [list(mr.stream(s_mode, s, k, "train")[1]) for k in ("pattern", "noise")]
        te = [list(mr.stream(s_mode, s, k, "test")[1]) for k in ("pattern", "noise")]
        for c in PROTO["cases"]:
            for n in PROTO["n_grid"]:
                rows.append({"seed": s, "case": c["name"], "n": n, "train_streams": tr, "test_streams": te,
                             "n_test_pairs": PROTO["test_pairs"], "nm": {"exact": 0.6, "test": 0.6},
                             "lda": {"exact": 0.75 + 0.000001 * n, "test": 0.75},
                             "mlp": {"test": 0.8, "fit": {"n_fit_pairs": n - n // 5, "n_val_pairs": n // 5,
                                                          "inits": [{}] * PROTO["decoders"]["mlp"]["inits"]}}})
    return {"mode": "research", "status": "complete", "failures": [], "seeds": PROTO["seeds"]["research"],
            "n_grid": PROTO["n_grid"], "test_pairs": PROTO["test_pairs"], "rows": rows,
            "overrides": {"seeds": None, "n_grid": None, "test_pairs": None, "hyper": None, "time_limit_s": None}}


def test_gate_completeness_on_synthetic_data():
    assert ev.completeness(synthetic(), PROTO) == []
    cases = {
        "missing_rows": lambda r: r["rows"].pop(5),
        "duplicate_rows": lambda r: r["rows"].append(dict(r["rows"][5])),
        "foreign_stream": lambda r: r["rows"][5].update(train_streams=[[1], [2]]),
        "wrong_mlp_budget": lambda r: r["rows"][5]["mlp"]["fit"].update(n_val_pairs=0),
        "non_finite_or_out_of_range": lambda r: r["rows"][5]["nm"].update(exact=float("nan")),
        "wrong_test_size": lambda r: r["rows"][5].update(n_test_pairs=10),
        "seeds_differ_from_protocol": lambda r: r.update(seeds=r["seeds"][:3]),
    }
    for reason, fn in cases.items():
        x = synthetic()
        fn(x)
        assert any(p.startswith(reason) for p in ev.completeness(x, PROTO)), reason
    rel = ev.release(synthetic())
    assert not rel["released"] and any(r.startswith("freeze_invalid") for r in rel["reasons"])


def test_t_test_holm_and_zero_variance_rules():
    r = ev.t_one_sided_p([0.03] * 20, 0.01)
    assert r["p"] == 0.0 and r["sd"] == 0.0
    assert ev.t_one_sided_p([0.0] * 20, 0.01)["p"] == 1.0
    d = list(np.linspace(0.005, 0.035, 20))
    r = ev.t_one_sided_p(d, 0.01)
    from scipy.stats import ttest_1samp
    assert r["p"] == pytest.approx(ttest_1samp(np.array(d) - 0.01, 0.0, alternative="greater").pvalue, rel=1e-10)
    h = ev.holm({"C-Daten": 0.03, "C-Modell": 0.04}, 0.05)
    assert not h["C-Daten"]["rejected"] and not h["C-Modell"]["rejected"]
    h = ev.holm({"C-Daten": 0.001, "C-Modell": 0.04}, 0.05)
    assert h["C-Daten"]["rejected"] and h["C-Modell"]["rejected"]


def test_closed_share_is_na_for_a_small_denominator():
    res = synthetic()
    refs = {"case_set": "research", "cases": {c["name"]: {"B": 0.755, "B_se": 1e-4, "L_found": 0.754, "acc_nm_inf": 0.6,
                                                          "acc_lda_inf": 0.751} for c in PROTO["cases"]}}
    d = ev.descriptive(res, refs, PROTO)
    assert d["modular_N"]["rows"]["mlp@1000"]["closed_share_vs_LDA1000"] is None   # B - LDA(1000) <= 0.01
    assert d["modular_N"]["rows"]["lda@16000"]["decomposition"]["sampling_inf_minus_n (signed)"] < 0
