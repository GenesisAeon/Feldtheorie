"""Review astra-m10-review (R9-R12): controls must reach status and release.

R9  release() derives the complete expected grid from the protocol; missing,
    duplicate, extra rows, wrong n, foreign streams, non-finite values -> no release
    (incl. the review's exact empty-result counterexample).
R10 failed leak/split checks and unexpected deterministic diagnostics end the run
    with status 'failed' and block the release; statistical 4-SE alarms do not.
R11 smoke (and research) only after a valid freeze (protocol + code hashes).
R12 the time limit is enforced during the run; timeout -> 'aborted_timeout',
    written exclusively, never released.
"""
import copy
import functools
import json

import numpy as np
import pytest

from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_evaluate as ev
from experiments.mandala_memory import m10_run
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory.core import MemoryLabError
from experiments.mandala_memory.data import stream

PROTO = mt.load_protocol()


@pytest.fixture()
def frozen(monkeypatch, tmp_path):
    """A valid freeze, IN MEMORY / tmp only: constant + freeze record with code hashes."""
    rec = {"protocol_sha256": m10_run.protocol_sha256(), "reviewed_code_commit": "0" * 40,
           "code_sha256": m10_run.code_sha256()}
    path = tmp_path / "m10_freeze.json"
    path.write_text(json.dumps(rec), encoding="utf-8")
    monkeypatch.setattr(m10_run, "FROZEN_PROTOCOL_SHA256", rec["protocol_sha256"])
    monkeypatch.setattr(m10_run, "FREEZE_RECORD", path)
    return path


@functools.lru_cache(maxsize=None)
def _update_counts(seed, d):
    """Training/test episodes of the update task, taken from the REAL episode generator
    (independent of the gate's own reconstruction)."""
    from experiments.mandala_memory import m10_decoders as md

    ld, pats = PROTO["level_D"], mt.patterns()
    tr = md.make_episodes("m10", seed, "decoder_train", d, ld["n_train_per_class"], pats, 12, 0.02)
    te = md.make_episodes("m10", seed, "test", d, ld["n_test_per_class"], pats, 12, 0.02)
    return int((tr.last > 0).sum()), int((te.last > 0).sum()), int((te.last == 0).sum())


def synthetic_complete_result():
    """A complete research result built INDEPENDENTLY of the gate code (own loops,
    own stream keys, counts from the real generator, FULL diagnostic structure);
    accuracies are placeholders, every required field is present (follow-up review)."""
    p = PROTO
    nets, nls, delays = ("modular", "uniform"), ("tanh", "identity"), p["delays"]["all"]
    lb, ld = p["level_B"], p["level_D"]
    res = {"mode": "research", "status": "complete", "failures": [], "protocol_sha256": m10_run.protocol_sha256(),
           "code_sha256": m10_run.code_sha256(), "delays": list(delays), "n_mc": lb["n_mc"], "seeds": list(ld["seeds"]),
           "overrides": {"delays": None, "n_mc": None, "seeds": None, "skip_level_d": False, "time_limit_s": None},
           "level_B": [], "level_D": [], "diagnostics": []}
    for n in nets:
        for nl in nls:
            for c, cond in p["conditions"].items():
                for d in delays:
                    if cond is None:
                        res["level_B"].append({"network": n, "nonlinearity": nl, "condition": c, "delay": d,
                                               "preserve": {"estimate": 0.9, "se": 0.0, "n": 0}, "update": None})
                        continue
                    row = {"network": n, "nonlinearity": nl, "condition": c, "delay": d}
                    for task in ("preserve", "update"):
                        row[task] = {"estimate": 0.8, "se": 1e-4, "n": lb["n_mc"], "block": lb["block"],
                                     "stream": list(stream("m10bayes", lb["streams"]["base_seed"], task, n, nl, c, d)[1])}
                    res["level_B"].append(row)
                    perm = mt.swap_permutation(12, p["networks"][n]["M"])
                    fixed = mt.condition_is_p_fixed(perm, cond)
                    tol1 = p["diagnostics"]["A1"]["tol_rel"]
                    diag = {"network": n, "nonlinearity": nl, "condition": c, "delay": d, "p_fixed": fixed,
                            "A1": {"max_rel_deviation": 0.0 if fixed else 0.4, "holds": fixed, "tol_rel": tol1},
                            "A1_expected": fixed, "A1_as_expected": True}
                    if nl == "identity" and fixed:
                        diag["A2_structural"] = {"max_norm_antisymmetric_part": 0.0, "holds": True,
                                                 "tol": p["diagnostics"]["A2_structural"]["tol"]}
                    res["diagnostics"].append(diag)
    for s in ld["seeds"]:
        for d in delays:
            u_tr, u_te, u_ex = _update_counts(s, d)
            streams = {role: [list(stream("m10", s, kind, role, d)[1]) for kind in ("pattern", "noise")]
                       for role in ("decoder_train", "test")}
            for n in nets:
                for nl in nls:
                    for c, cond in p["conditions"].items():
                        res["level_D"].append({
                            "seed": s, "delay": d, "network": n, "nonlinearity": nl, "condition": c, "streams": streams,
                            "checks": {"ids_disjoint": True, "streams_disjoint": True,
                                       "train_identical_pattern_counts": True, "test_identical_pattern_counts": True},
                            "preserve": {"n_train": 2 * ld["n_train_per_class"], "n_test": 2 * ld["n_test_per_class"],
                                         "n_excluded_test": 0, "nearest_mean": 0.8, "lda_ledoit_wolf": 0.81},
                            "update": None if cond is None else {"n_train": u_tr, "n_test": u_te, "n_excluded_test": u_ex,
                                                                 "nearest_mean": 0.7, "lda_ledoit_wolf": 0.72}})
    return res


# --- R9 ------------------------------------------------------------------------
def test_r9_complete_synthetic_result_is_released(frozen):
    rel = ev.release(synthetic_complete_result())
    assert rel == {"released": True, "reasons": []}


def test_r9_review_counterexample_empty_result_is_not_released(frozen):
    h = m10_run.protocol_sha256()
    rel = ev.release(dict(mode="research", status="complete", failures=[], protocol_sha256=h, overrides={},
                          level_B=[], level_D=[], diagnostics=[], seeds=[], delays=[], n_mc=1))
    assert not rel["released"]
    for r in ("level_B_missing_rows", "level_D_missing_rows", "seeds_differ_from_protocol", "n_mc_differs_from_protocol",
              "delays_differ_from_protocol", "diagnostics_grid_incomplete", "code_differs_from_frozen"):
        assert r in rel["reasons"], r


def _mutate(fn):
    res = synthetic_complete_result()
    fn(res)
    return ev.release(res)


@pytest.mark.parametrize("name,fn,reason", [
    ("removed B row", lambda r: r["level_B"].pop(7), "level_B_missing_rows"),
    ("duplicate B row", lambda r: r["level_B"].append(copy.deepcopy(r["level_B"][5])), "level_B_duplicate_rows"),
    ("extra B row", lambda r: r["level_B"].append({**copy.deepcopy(r["level_B"][5]), "delay": 5}), "level_B_extra_rows"),
    ("wrong n B", lambda r: r["level_B"][5]["preserve"].update(n=1000), "level_B_wrong_n"),
    ("foreign stream B", lambda r: r["level_B"][5]["update"].update(stream=[1, 2, 3]), "level_B_foreign_stream"),
    ("NaN se", lambda r: r["level_B"][5]["preserve"].update(se=float("nan")), "level_B_non_finite_or_out_of_range"),
    ("K0 update present", lambda r: r["level_B"][0].update(update={"estimate": 0.5}), "level_B_K0_invalid"),
    ("removed D row", lambda r: r["level_D"].pop(100), "level_D_missing_rows"),
    ("duplicate seed rows", lambda r: r["level_D"].extend(copy.deepcopy([x for x in r["level_D"] if x["seed"] == 31101])),
     "level_D_duplicate_rows"),
    ("duplicate seed in list", lambda r: r.update(seeds=r["seeds"][:-1] + [r["seeds"][0]]), "seeds_differ_from_protocol"),
    ("wrong n D", lambda r: r["level_D"][3]["preserve"].update(n_test=10), "level_D_wrong_n"),
    ("foreign stream D", lambda r: r["level_D"][3].update(streams={"decoder_train": [], "test": []}), "level_D_foreign_stream"),
    ("non-finite D", lambda r: r["level_D"][3]["preserve"].update(nearest_mean=float("inf")), "level_D_non_finite"),
    ("update count wrong", lambda r: next(x for x in r["level_D"] if x["update"])["update"].update(n_excluded_test=0),
     "level_D_update_invalid"),
    # --- follow-up review FOLLOWUP_R9_R12: the four reproduced gaps and their neighbours ---
    ("K0 NaN se (review)", lambda r: r["level_B"][0]["preserve"].update(se=float("nan")), "level_B_K0_invalid"),
    ("K0 non-zero se", lambda r: r["level_B"][0]["preserve"].update(se=1e-4), "level_B_K0_invalid"),
    ("leak checks incomplete (review)", lambda r: r["level_D"][0].update(checks={"ids_disjoint": True}), "level_D_control_failed"),
    ("leak check extra key", lambda r: r["level_D"][0]["checks"].update(other=True), "level_D_control_failed"),
    ("leak check truthy non-bool", lambda r: r["level_D"][0]["checks"].update(ids_disjoint=1), "level_D_control_failed"),
    ("A2 and p_fixed removed (review)", lambda r: [x.pop(k) for x in [next(z for z in r["diagnostics"] if "A2_structural" in z)]
                                                  for k in ("A2_structural", "p_fixed")], "A2_structural_failed"),
    ("A2 with other tolerance", lambda r: next(z for z in r["diagnostics"] if "A2_structural" in z)["A2_structural"].update(tol=1.0),
     "A2_structural_failed"),
    ("A2 on a non-fixed row", lambda r: next(z for z in r["diagnostics"] if not z["p_fixed"]).update(
        A2_structural={"max_norm_antisymmetric_part": 0.0, "holds": True, "tol": 1e-13}), "A2_structural_unexpected"),
    ("A1 measurement missing", lambda r: r["diagnostics"][0].pop("A1"), "A1_not_as_expected"),
    ("A1 holds inconsistent with value", lambda r: r["diagnostics"][0]["A1"].update(max_rel_deviation=1.0), "A1_not_as_expected"),
    ("p_fixed claimed wrongly", lambda r: next(z for z in r["diagnostics"] if not z["p_fixed"]).update(p_fixed=True),
     "A1_not_as_expected"),
    ("update zero training (review)", lambda r: next(x for x in r["level_D"] if x["update"])["update"].update(n_train=0),
     "level_D_update_invalid"),
    ("update count shifted by one pair", lambda r: (lambda u: u.update(n_test=u["n_test"] - 2, n_excluded_test=u["n_excluded_test"] + 2))(
        next(x for x in r["level_D"] if x["update"])["update"]), "level_D_update_invalid"),
    ("preserve excluded episodes", lambda r: r["level_D"][3]["preserve"].update(n_excluded_test=2), "level_D_wrong_n"),
    ("accuracy above 1", lambda r: r["level_D"][3]["preserve"].update(lda_ledoit_wolf=1.5), "level_D_non_finite"),
    ("n as float", lambda r: r["level_D"][3]["preserve"].update(n_test=4000.0), "level_D_wrong_n"),
    ("override used", lambda r: r["overrides"].update(n_mc=5), "overrides_used"),
    ("not research", lambda r: r.update(mode="smoke"), "mode_is_not_research"),
    ("failure logged", lambda r: r.update(failures=["x"]), "run_not_complete"),
    ("fewer seeds overall", lambda r: (r.update(seeds=r["seeds"][:2]), r.update(level_D=[x for x in r["level_D"] if x["seed"] in r["seeds"]])),
     "level_D_missing_rows"),
])
def test_r9_incomplete_or_foreign_data_is_not_released(frozen, name, fn, reason):
    rel = _mutate(fn)
    assert not rel["released"] and any(x.startswith(reason) for x in rel["reasons"]), (name, rel["reasons"][:5])


def test_r9_changed_code_after_freeze_blocks_release(frozen):
    res = synthetic_complete_result()
    res["code_sha256"] = {**res["code_sha256"], "m10_bayes.py": "0" * 64}
    assert "code_differs_from_frozen" in ev.release(res)["reasons"]


# --- R10 (gate side, portable) -------------------------------------------------
def test_r10_failed_controls_in_data_block_the_release(frozen):
    rel = _mutate(lambda r: r["level_D"][0]["checks"].update(train_identical_pattern_counts=False))
    assert not rel["released"] and any(x.startswith("level_D_control_failed") for x in rel["reasons"])
    rel = _mutate(lambda r: r["diagnostics"][0].update(A1_as_expected=False))
    assert any(x.startswith("A1_not_as_expected") for x in rel["reasons"])
    rel = _mutate(lambda r: next(x for x in r["diagnostics"] if "A2_structural" in x)["A2_structural"].update(holds=False))
    assert any(x.startswith("A2_structural_failed") for x in rel["reasons"])


def test_r10_statistical_alarm_is_reported_but_does_not_block(frozen):
    res = synthetic_complete_result()
    for r in res["level_B"]:                               # linear twin above its K0 value by far more than 4 SE
        if r["nonlinearity"] == "identity" and r["condition"] == "N":
            r["preserve"]["estimate"] = 0.99
    out = ev.evaluate(res)
    assert out["release"]["released"]
    assert out["numeric_diagnostics"]["alarms"], "the A3 alarm must be reported"


# --- R11 -----------------------------------------------------------------------
@pytest.mark.parametrize("mode", ["smoke", "research"])
def test_r11_smoke_and_research_require_a_valid_freeze(monkeypatch, tmp_path, mode):
    with pytest.raises(MemoryLabError, match="not frozen"):
        m10_run.mode_settings(PROTO, mode)                 # review counterexample: smoke before the freeze
    monkeypatch.setattr(m10_run, "FROZEN_PROTOCOL_SHA256", "0" * 64)
    with pytest.raises(MemoryLabError, match="differs"):
        m10_run.mode_settings(PROTO, mode)
    monkeypatch.setattr(m10_run, "FROZEN_PROTOCOL_SHA256", m10_run.protocol_sha256())
    monkeypatch.setattr(m10_run, "FREEZE_RECORD", tmp_path / "missing.json")
    with pytest.raises(MemoryLabError, match="freeze record"):
        m10_run.mode_settings(PROTO, mode)
    rec = tmp_path / "rec.json"
    rec.write_text(json.dumps({"protocol_sha256": m10_run.protocol_sha256(), "reviewed_code_commit": "abc",
                               "code_sha256": {**m10_run.code_sha256(), "m10_run.py": "0" * 64}}), encoding="utf-8")
    monkeypatch.setattr(m10_run, "FREEZE_RECORD", rec)
    with pytest.raises(MemoryLabError, match="code differs"):
        m10_run.mode_settings(PROTO, mode)
    rec.write_text(json.dumps({"protocol_sha256": m10_run.protocol_sha256(), "reviewed_code_commit": "abc",
                               "code_sha256": m10_run.code_sha256()}), encoding="utf-8")
    assert m10_run.mode_settings(PROTO, mode)["conditions"] == PROTO["conditions"]
    with pytest.raises(MemoryLabError, match="overrides"):
        m10_run.run(mode, None, n_mc=10, write=False)
    assert m10_run.mode_settings(PROTO, "dev")["conditions"] == PROTO["development"]["conditions"]


# --- R12 (portable unit) ---------------------------------------------------------
def test_r12_deadline_is_checked_before_every_mc_block():
    calls = {"n": 0}

    def deadline():
        calls["n"] += 1
        if calls["n"] > 3:
            raise m10_run.RunTimeout("budget")

    mix = [(np.zeros((1, 2)), np.ones(1)), (np.full((1, 2), 0.02), np.ones(1))]
    with pytest.raises(m10_run.RunTimeout):
        mb.bayes_accuracy_mc(mix, 0.02, 1_000_000, stream("m10bayes", 1, "t")[0], block=1000, deadline=deadline)
    assert calls["n"] == 4                                # 3 blocks ran, stopped before the 4th: overshoot <= one block


def test_r12_protocol_states_the_limit_and_the_unenforced_budgets():
    r = PROTO["resources"]
    assert r["time_limit"]["seconds"] == 1200 and "wall-clock" in r["time_limit"]["kind"]
    assert "NOT enforced" in r["ram_limit_gib"]["status"] and "NOT enforced" in r["results_limit_mb"]["status"]
    assert "cpu_hard_limit_s" not in r


# --- R10 / R12 through the real runner (kernel; development settings) ------------
def test_r10_failed_leak_check_fails_the_run(monkeypatch):
    from experiments.mandala_memory import m10_decoders as md

    monkeypatch.setattr(md, "check_class_independence", lambda ep, n: {"identical_pattern_counts": False})
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False)   # the review's counterexample
    assert res["status"] == "failed" and any("ControlFailure" in f and "identical_pattern_counts" in f for f in res["failures"])
    assert "run_not_complete" in ev.release(res)["reasons"]


def test_r10_failed_split_check_fails_the_run(monkeypatch):
    from experiments.mandala_memory import m10_decoders as md

    def broken(tr, te):
        raise MemoryLabError("train and test share a random stream")
    monkeypatch.setattr(md, "check_split", broken)
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False)
    assert res["status"] == "failed" and any("share a random stream" in f for f in res["failures"])


@pytest.mark.parametrize("target", ["A1", "A2"])
def test_r10_unexpected_deterministic_diagnostic_fails_the_run(monkeypatch, target):
    if target == "A1":
        real = mt.check_a1
        monkeypatch.setattr(mt, "check_a1", lambda *a: {**real(*a), "holds": not real(*a)["holds"]})
    else:
        real = mt.check_a2_structural
        monkeypatch.setattr(mt, "check_a2_structural", lambda *a: {**real(*a), "holds": False})
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False)
    assert res["status"] == "failed" and any("deterministic control failed" in f for f in res["failures"])
    assert res["level_B"] == [] and res["level_D"] == []        # stops before level B/D


def test_r10_expected_negative_a1_control_does_not_fail_the_run():
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False)
    neg = [r for r in res["diagnostics"] if r["network"] == "modular" and r["condition"] == "Ndev"]
    assert neg and all(not r["A1"]["holds"] and r["A1_as_expected"] for r in neg)
    assert res["status"] == "complete"


def test_r12_overrun_in_the_last_unit_is_not_complete(monkeypatch):
    """Follow-up review: an overrun during the LAST level-D unit must still end as aborted_timeout."""
    from experiments.mandala_memory import m10_decoders as md

    t = {"now": 0.0}
    monkeypatch.setattr(m10_run, "clock", lambda: t["now"])
    real, calls = md.evaluate_level_d, {"n": 0}
    total = 2 * 2 * 3 + 2 * 2 * 2                         # preserve for 3 dev conditions + update for 2, per net x nl

    def last_unit_overruns(*a):
        calls["n"] += 1
        if calls["n"] == total:
            t["now"] = 1e9                                 # the clock jumps during the very last unit
        return real(*a)
    monkeypatch.setattr(md, "evaluate_level_d", last_unit_overruns)
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False, time_limit_s=100.0)
    assert calls["n"] == total and res["status"] == "aborted_timeout"


def test_r12_deadline_is_checked_inside_the_diagnostics(monkeypatch):
    t = {"now": 0.0}
    monkeypatch.setattr(m10_run, "clock", lambda: t["now"])
    real = mt.check_a1

    def slow_a1(*a):
        t["now"] += 60.0                                   # every diagnostic unit takes "60 s"
        return real(*a)
    monkeypatch.setattr(mt, "check_a1", slow_a1)
    res = m10_run.run("dev", None, delays=[3], n_mc=10, seeds=[901], write=False, time_limit_s=100.0)
    assert res["status"] == "aborted_timeout" and res["diagnostics"] == [] and t["now"] <= 180.0


def test_r12_timeout_through_the_runner(monkeypatch, tmp_path):
    t = {"now": 0.0}

    def fake_clock():
        t["now"] += 7.0                                    # every check advances the controlled clock by 7 s
        return t["now"]
    monkeypatch.setattr(m10_run, "clock", fake_clock)
    # 12 state units + 8 diagnostic units = 20 clock steps of 7 s (140 s) fit into 160 s; the budget then runs out
    # in the first Monte Carlo estimate (4 blocks of 50 000)
    res = m10_run.run("dev", tmp_path, delays=[3], n_mc=200_000, seeds=[901], time_limit_s=160.0)
    assert res["status"] == "aborted_timeout" and any("RunTimeout" in f for f in res["failures"])
    # the budget ran out INSIDE the Monte Carlo loop (level B never completed), not only later
    assert res["diagnostics"] and res["level_B"] == [] and res["level_D"] == []
    saved = json.loads(open(res["output_path"], encoding="utf-8").read())
    assert saved["status"] == "aborted_timeout" and saved["time_limit_s"] == 160.0
    assert "run_not_complete" in ev.release(saved)["reasons"]
    with pytest.raises(MemoryLabError):                    # exclusive: the same file is never overwritten
        m10_run.write_exclusive(m10_run.Path(res["output_path"]), "x")
