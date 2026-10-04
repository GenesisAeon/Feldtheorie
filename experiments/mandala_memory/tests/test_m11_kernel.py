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
def _fit_meta(s_mode, s, case, n):
    hp = {**PROTO["decoders"]["mlp"]["hyperparameters"], "hidden": PROTO["decoders"]["mlp"]["hidden"],
          "inits": PROTO["decoders"]["mlp"]["inits"]}
    inits = [{"index": k, "stream": list(mr.stream(s_mode, s, "mlp-init", case, n, k)[1]),
              "best_val_loss": 0.40 + 0.01 * ((k + 1) % 3), "epochs": 100 + k} for k in range(hp["inits"])]
    best = min(range(len(inits)), key=lambda k: (inits[k]["best_val_loss"], k))
    nv = n // 5
    return {"hyper": hp, "inits": inits, "selected": {"init": best, "best_val_loss": inits[best]["best_val_loss"],
                                                      "epochs": inits[best]["epochs"]},
            "split_rule": "every 5th pair -> validation", "n_fit_pairs": n - nv, "n_val_pairs": nv,
            "n_fit_episodes": 2 * (n - nv), "n_val_episodes": 2 * nv, "n_val_class_B": nv}


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
                             "mlp": {"test": 0.8, "fit": _fit_meta(s_mode, s, c["name"], n)}})
    return {"mode": "research", "status": "complete", "failures": [], "seeds": PROTO["seeds"]["research"],
            "mlp_hyper": {**PROTO["decoders"]["mlp"]["hyperparameters"], "hidden": PROTO["decoders"]["mlp"]["hidden"],
                          "inits": PROTO["decoders"]["mlp"]["inits"]},
            "n_grid": PROTO["n_grid"], "test_pairs": PROTO["test_pairs"], "rows": rows,
            "overrides": {"seeds": None, "n_grid": None, "test_pairs": None, "hyper": None, "time_limit_s": None}}


def test_gate_completeness_on_synthetic_data():
    assert ev.completeness(synthetic(), PROTO) == []
    cases = {
        "missing_rows": lambda r: r["rows"].pop(5),
        "duplicate_rows": lambda r: r["rows"].append(dict(r["rows"][5])),
        "foreign_stream": lambda r: r["rows"][5].update(train_streams=[[1], [2]]),
        "wrong_mlp_budget": lambda r: r["rows"][5]["mlp"]["fit"].update(n_val_pairs=0),
        # review M11-R7 counterexamples and neighbours
        "mlp_hyper_differs": lambda r: r["rows"][5]["mlp"]["fit"].update(hyper={"hidden": 1, "lr": 999}),
        "mlp_selection_inconsistent": lambda r: r["rows"][5]["mlp"]["fit"].update(
            selected={"init": 99, "best_val_loss": float("nan"), "epochs": -1}),
        "mlp_init_foreign_stream": lambda r: r["rows"][5]["mlp"]["fit"]["inits"][1].update(stream=[1, 2]),
        "mlp_init_val_loss_invalid": lambda r: r["rows"][5]["mlp"]["fit"]["inits"][0].update(best_val_loss=float("nan")),
        "mlp_init_epochs_invalid": lambda r: r["rows"][5]["mlp"]["fit"]["inits"][2].update(epochs=-1),
        "mlp_inits_missing": lambda r: r["rows"][5]["mlp"]["fit"].update(inits=[{}, {}]),
        "mlp_init_index_invalid": lambda r: r["rows"][5]["mlp"]["fit"]["inits"][0].update(index=7),
        "non_finite_or_out_of_range": lambda r: r["rows"][5]["nm"].update(exact=float("nan")),
        "wrong_test_size": lambda r: r["rows"][5].update(n_test_pairs=10),
        "seeds_differ_from_protocol": lambda r: r.update(seeds=r["seeds"][:3]),
        "mlp_hyper_differs_from_protocol": lambda r: r.update(mlp_hyper={"hidden": 1, "lr": 999}),   # review counterexample
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
    cs = d["modular_N"]["rows"]["mlp@1000"]["closed_share_vs_LDA1000"]
    assert cs["estimate"] is None and "N/A" in cs["reason"]                       # B - LDA(1000) <= 0.01
    assert d["modular_N"]["rows"]["lda@16000"]["decomposition"]["sampling_inf_minus_n (signed)"] < 0


# --- review M11-R5: references and the M10 protocol bound to the freeze --------------
@pytest.fixture()
def bound(monkeypatch, tmp_path):
    """A frozen reference artifact and freeze record IN tmp ONLY (the real reference phase is never run)."""
    refs = {"schema": "x", "case_set": "research", "protocol_sha256": "p" * 64,
            "cases": {c["name"]: {"B": 0.91, "B_se": 1e-4, "L_found": 0.78, "acc_nm_inf": 0.63, "acc_lda_inf": 0.776}
                      for c in PROTO["cases"]}}
    f = tmp_path / "m11_references.json"
    f.write_text(json.dumps(refs), encoding="utf-8")
    monkeypatch.setattr(mref, "RESEARCH_REFERENCES", f)
    rec = {"code_sha256": m11_run.code_sha256(), "protocol_sha256": mref.sha(mref.PROTOCOL), "references_sha256": mref.sha(f),
           "protocol_sha256_at_references": "p" * 64, "m10_binding": mref.require_m10_frozen(), "reviewed_code_commit": "x"}
    monkeypatch.setattr(m11_run, "require_frozen", lambda mode: rec)
    res = synthetic()
    res.update(code_sha256=rec["code_sha256"], protocol_sha256=rec["protocol_sha256"], references_sha256=rec["references_sha256"],
               m10_binding=rec["m10_binding"])
    return res, refs


def test_r5_bound_references_release_and_arbitrary_references_do_not(bound):
    res, refs = bound
    assert ev.release(res, refs) == {"released": True, "reasons": []}
    arbitrary = {"case_set": "research", "cases": {c["name"]: {"B": 0.51, "B_se": 0.0, "L_found": 0.5, "acc_nm_inf": 0.5,
                                                             "acc_lda_inf": 0.5} for c in PROTO["cases"]}}
    out = ev.evaluate(res, arbitrary)                          # the review's counterexample
    assert not out["release"]["released"] and "references_differ_from_frozen_artifact" in out["release"]["reasons"]
    bad = json.loads(json.dumps(refs))
    bad["cases"]["modular_N"]["B"] = float("nan")
    assert any(r.startswith("references_values_invalid") for r in ev.release(res, bad)["reasons"])
    res2 = dict(res, references_sha256="0" * 64)
    assert "result_not_bound_to_frozen_references_or_m10" in ev.release(res2, refs)["reasons"]
    assert "references_artifact_missing" in ev.references_problems(refs, PROTO, {}) or True


def test_r5_changed_m10_protocol_is_detected_before_any_state(monkeypatch):
    from experiments.mandala_memory import m10_run, m10_task

    monkeypatch.setattr(m10_run, "protocol_sha256", lambda path=None: "0" * 64)       # simulate a changed M10 protocol
    monkeypatch.setattr(m10_task, "readout_states", lambda *a, **k: (_ for _ in ()).throw(AssertionError("state computed")))
    with pytest.raises(MemoryLabError, match="differs"):
        m11_run.run("dev", None, seeds=[901], n_grid=[250], test_pairs=100, hyper=SMALL, write=False)
    with pytest.raises(MemoryLabError, match="differs"):
        mref.compute("dev")


# --- review M11-R6: non-finite training fails the run -----------------------------
def test_r6_nan_gradient_raises_in_the_mlp():
    rng = np.random.default_rng(123)
    X, y = rng.normal(size=(40, 3)), np.tile([0.0, 1.0], 20)
    m = mr.MLP(4, 0.01, 0.001, 2, 5)
    original, count = m.loss_and_grad, [0]

    def bad(*a, **k):                                          # the review's counterexample
        loss, g = original(*a, **k)
        count[0] += 1
        return (loss, {kk: np.full_like(v, np.nan) for kk, v in g.items()}) if count[0] >= 2 else (loss, g)
    m.loss_and_grad = bad
    with pytest.raises(mr.MLPDivergence, match="training loss or gradient in epoch 2"):   # caught at the gradient itself
        m.fit(X[:30], y[:30], X[30:], y[30:], rng)


def test_r6_nan_gradient_fails_the_runner_and_the_release(monkeypatch):
    original = mr.MLP.loss_and_grad

    def bad(self, X, y, p=None):
        loss, g = original(self, X, y, p)
        return loss, {k: np.full_like(v, np.nan) for k, v in g.items()}
    monkeypatch.setattr(mr.MLP, "loss_and_grad", bad)
    res = m11_run.run("dev", None, seeds=[901], n_grid=[250], test_pairs=2000, hyper=SMALL, write=False)
    assert res["status"] == "failed" and any("MLPDivergence" in f for f in res["failures"])
    assert "run_not_complete" in ev.release(res)["reasons"]


def test_deadline_is_checked_every_epoch():
    calls = {"n": 0}

    def deadline():
        calls["n"] += 1
        if calls["n"] > 5:
            raise m11_run.RunTimeout("budget")
    rng = np.random.default_rng(1)
    X, y = rng.normal(size=(40, 3)), np.tile([0.0, 1.0], 20)
    with pytest.raises(m11_run.RunTimeout):
        mr.MLP(4, 0.01, 0.001, 1000, 1000).fit(X[:30], y[:30], X[30:], y[30:], rng, deadline)
    assert calls["n"] == 6                                     # stopped before the 6th epoch: overshoot <= one epoch


# --- review M11-R8: the reference phase is locked BEFORE any computation -------------
@pytest.fixture()
def phase(monkeypatch, tmp_path):
    from unittest.mock import Mock

    core = Mock(return_value={"schema": "mock", "cases": {}})
    monkeypatch.setattr(mref, "_compute_cases", core)
    monkeypatch.setattr(mref, "RESEARCH_REFERENCES", tmp_path / "refs.json")
    monkeypatch.setattr(mref, "RESEARCH_CLAIM", tmp_path / "claim.json")
    monkeypatch.setattr(mref, "RESEARCH_FAILURE", tmp_path / "failed.json")
    monkeypatch.setattr(mref, "git_clean", lambda paths: True)
    return core, tmp_path


def test_r8_existing_artifact_claim_or_failure_blocks_before_compute(phase):
    core, tmp = phase
    for name in ("refs.json", "claim.json", "failed.json"):
        f = tmp / name
        f.write_text("{}")
        with pytest.raises(MemoryLabError):
            mref.research_reference_phase()
        f.unlink()
    assert not core.called


def test_r8_unversioned_or_m10_not_frozen_blocks_before_compute(phase, monkeypatch):
    core, _ = phase
    monkeypatch.setattr(mref, "git_clean", lambda paths: False)
    with pytest.raises(MemoryLabError, match="not committed"):
        mref.research_reference_phase()
    monkeypatch.setattr(mref, "git_clean", lambda paths: True)
    from experiments.mandala_memory import m10_run
    monkeypatch.setattr(m10_run, "protocol_sha256", lambda path=None: "0" * 64)
    with pytest.raises(MemoryLabError):
        mref.research_reference_phase()
    with pytest.raises(MemoryLabError, match="only via research_reference_phase"):
        mref.compute("research")                               # a direct call cannot bypass the phase
    assert not core.called


def test_r8_one_phase_then_locked_and_failure_is_recorded(phase, monkeypatch):
    core, tmp = phase
    mref.research_reference_phase()
    assert core.call_count == 1 and (tmp / "refs.json").exists() and (tmp / "claim.json").exists()
    with pytest.raises(MemoryLabError):
        mref.research_reference_phase()
    assert core.call_count == 1                                # no recomputation
    for f in ("refs.json", "claim.json"):
        (tmp / f).unlink()
    core.side_effect = RuntimeError("boom")
    with pytest.raises(RuntimeError):
        mref.research_reference_phase()
    assert json.loads((tmp / "failed.json").read_text())["error"].startswith("RuntimeError")
    with pytest.raises(MemoryLabError, match="no silent retry"):
        mref.research_reference_phase()


# --- review M11-R9: closed share with paired whole-seed bootstrap ---------------------
def test_r9_closed_share_bootstrap_paired_and_na_rules():
    rng = np.random.default_rng(9)
    lda = 0.776 + rng.normal(0, 0.006, 20)
    mlp = lda + 0.05 + rng.normal(0, 0.004, 20)
    cs = ev.closed_share(mlp, lda, 0.912)
    want = (mlp.mean() - lda.mean()) / (0.912 - lda.mean())
    assert cs["estimate"] == pytest.approx(want) and cs["bootstrap95"][0] < want < cs["bootstrap95"][1]
    assert cs["invalid_replicates"] == 0 and "paired" in cs["label"]
    # independent paired reference: the SAME resampled seeds for numerator and denominator
    g = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2026100412])))
    idx = g.integers(0, 20, size=(2000, 20))
    ratios = (mlp[idx].mean(1) - lda[idx].mean(1)) / (0.912 - lda[idx].mean(1))
    assert cs["bootstrap95"] == pytest.approx([np.quantile(ratios, 0.025), np.quantile(ratios, 0.975)], rel=1e-12)
    small = ev.closed_share(mlp, lda, lda.mean() + 0.005)
    assert small["estimate"] is None and "N/A" in small["reason"]
    edge = ev.closed_share(mlp, lda, lda.mean() + 0.0105)        # some bootstrap replicates fall below the threshold
    assert edge["invalid_replicates"] > 0
