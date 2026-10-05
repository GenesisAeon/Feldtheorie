"""M12 (docs/M12_PLAN_ROBUSTHEIT.md, Fassung 2): required checks of section 9 incl. negative
controls. Only development settings and temporary paths; the real reference/training phases
never run here."""
from __future__ import annotations

import copy
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pytest

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m12_common as mc
from experiments.mandala_memory import m12_evaluate as ev
from experiments.mandala_memory import m12_models as mm
from experiments.mandala_memory import m12_references as mref
from experiments.mandala_memory import m12_robust as rob
from experiments.mandala_memory.core import MemoryLabError

PROTO = mc.load_protocol()
SEEDS = [921, 922]
FAKE_D1 = {"B": 0.9244750482736879, "B_se": 8.44358983574704e-05, "file": "synthetic", "sha256": "synthetic"}


@pytest.fixture(scope="module")
def dev(tmp_path_factory):
    """Small development pipeline: references (n_mc 5000), models (n 300), evaluation (1000 test pairs)."""
    root = tmp_path_factory.mktemp("m12dev")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(mref, "d1_source", lambda case_set: dict(FAKE_D1))       # the real source is a lab_integration test
        refs = mref.compute("dev", n_mc=5000)
        mc.write_json_exclusive(root / "refs.json", refs)
        rec = mm.train("dev", root / "models", seeds=SEEDS, n_pairs=300, refs_path=root / "refs.json")
        res = rob.run("dev", root, models_dir=root / "models", refs_path=root / "refs.json", seeds=SEEDS, test_pairs=1000)
    return {"root": root, "refs": refs, "rec": rec, "res": res}


# --- conditions, streams, hyperparameters --------------------------------------------
def test_research_conditions_follow_the_rule_and_dev_is_generated():
    research = mc.conditions(PROTO, "research")
    assert [c["name"] for c in research] == [c["name"] for c in PROTO["grid"]["conditions"]] and len(research) == 9
    dev = mc.conditions(PROTO, "dev")
    assert len(dev) == 9 and dev[0] == {"name": "c0", "amplitude": 0.9, "sigma": 0.02}
    assert sorted(c["amplitude"] for c in dev if c["sigma"] == 0.02) == [0.45, 0.675, 0.9, 1.125, 1.35]
    bad = copy.deepcopy(PROTO)
    bad["grid"]["conditions"][4]["amplitude"] = 0.95                       # not a factor of the base
    with pytest.raises(MemoryLabError, match="factor rule"):
        mc.conditions(bad, "research")


def test_raised_endpoints_are_the_protocol_endpoints():
    ends = ev.raised_endpoints(mc.conditions(PROTO, "research"))
    assert ends == {k: v["condition"] for k, v in PROTO["confirmatory"]["tests"].items()} == {"R-a": "a0.90", "R-sigma": "s0.030"}


def test_own_streams_never_coincide_with_m11():
    k12 = mc.stream("m12", 41201, "pattern", "train")[1]
    k11 = mr.stream("m11", 41201, "pattern", "train")[1]
    assert k12[1] == 13 and k11[1] == 11 and k12 != k11
    assert mc.stream("m12dev", 921, "x")[1][1] == 14 and mc.stream("m12bayes", 1, "x")[1][1] == 15
    with pytest.raises(MemoryLabError):
        mc.stream("m11", 1, "x")


def test_hyperparameters_are_read_from_the_frozen_m11_protocol_by_hash():
    h = mc.mlp_hyper(PROTO)
    assert h == {"lr": 0.03, "l2": 0.001, "patience": 100, "max_epochs": 3000, "hidden": 32, "inits": 3}
    bad = copy.deepcopy(PROTO)
    bad["training"]["hyper_source"]["m11_protocol_sha256"] = "0" * 64
    with pytest.raises(MemoryLabError, match="hyperparameter source"):
        mc.mlp_hyper(bad)


def test_predecessors_m10_and_m11_are_frozen_and_unchanged():
    b = mc.require_predecessors_frozen()
    assert b["m11"]["m11_protocol_sha256"] == PROTO["training"]["hyper_source"]["m11_protocol_sha256"]
    assert b["m10"]["m10_reviewed_code_commit"]


# --- wrapper, draws, pair SE ---------------------------------------------------------------
def test_wrapper_is_bit_equal_to_m11_fit_mlp_with_the_same_streams():
    """Intentionally the SAME (M11) streams -- productive M12 streams stay separate."""
    pats = mt.patterns()
    probs = mc.probabilities(pats)
    z = mc.states(PROTO, "dev", 0.9, pats)
    d = mr.draw_pairs("m11dev", 903, "train", 200, probs, 12, 0.02)
    Y, lab, pair = mr.episodes(z, d, 200)
    hyper = {**mc.mlp_hyper(PROTO), "max_epochs": 40}
    m1, i1 = mr.fit_mlp(Y, lab, pair, 200, hyper, "m11dev", 903, mc.CASE_LABEL)
    m2, i2 = mc.fit_mlp(Y, lab, pair, 200, hyper, "m11dev", 903, _stream=mr.stream)
    assert i1 == i2
    assert all(np.array_equal(m1.p[k], m2.p[k]) for k in m1.p) and np.array_equal(m1.mean, m2.mean) and np.array_equal(m1.std, m2.std)


def test_test_episodes_are_paired_across_conditions_and_noise_scales_exactly():
    pats = mt.patterns()
    probs = mc.probabilities(pats)
    d = mc.draw("m12dev", 921, "test", 500, probs)
    z1, z2 = mc.states(PROTO, "dev", 0.9, pats), mc.states(PROTO, "dev", 1.35, pats)
    Ya, _, _ = mc.episodes(z1, d, 500, 0.02)
    Yb, _, _ = mc.episodes(z2, d, 500, 0.03)
    pi = d["pattern_index"]
    noise_a = Ya - np.concatenate([z1[0][pi], z1[1][pi]])
    noise_b = Yb - np.concatenate([z2[0][pi], z2[1][pi]])
    eps = np.concatenate([d["eps"][:, 0], d["eps"][:, 1]])
    assert np.allclose(noise_a, 0.02 * eps, rtol=0, atol=1e-15) and np.allclose(noise_b, 0.03 * eps, rtol=0, atol=1e-15)
    assert np.array_equal(mc.draw("m12dev", 921, "test", 500, probs)["eps"], d["eps"])       # deterministic
    assert mc.draw("m12dev", 921, "train", 500, probs)["streams"] != d["streams"]


def test_pair_se_from_pair_contributions():
    rng = np.random.default_rng(5)
    n = 400
    pred = rng.integers(0, 2, size=2 * n)
    r = 0.5 * ((pred[:n] == 0).astype(float) + (pred[n:] == 1).astype(float))     # (bool + bool is OR in numpy)
    got = mc.acc_and_se(pred, n)
    assert got["acc"] == pytest.approx(mr.balanced_accuracy(np.repeat([0, 1], n), pred), abs=1e-15)
    assert got["se_pair"] == pytest.approx(math.sqrt(np.var(r, ddof=1) / n), rel=1e-12)


# --- artifacts ---------------------------------------------------------------------------
def test_training_record_and_roundtrip(dev):
    rec = dev["rec"]
    assert rec["status"] == "complete" and [p["roundtrip"] for p in rec["per_seed"]] == ["bit-identical"] * 2
    loaded = mm.require_models("dev", dev["root"] / "models", seeds=SEEDS, references_sha256=mc.sha(dev["root"] / "refs.json"))
    assert set(loaded["models"]) == set(SEEDS)
    arr, meta = loaded["models"][921]
    Y = np.random.default_rng(1).normal(size=(50, 12)) * 0.05
    m = mc.mlp_from_arrays(arr, mc.mlp_hyper(PROTO))
    arr2, _ = mc.load_seed(dev["root"] / "models", 921)
    assert np.array_equal(mc.mlp_logits(m, Y), mc.mlp_logits(mc.mlp_from_arrays(arr2, mc.mlp_hyper(PROTO)), Y))
    assert meta["condition"]["name"] == "c0" and meta["n_pairs"] == 300


def _copy_models(dev, tmp_path) -> Path:
    d = tmp_path / "models"
    shutil.copytree(dev["root"] / "models", d)
    return d


def test_tampered_missing_or_extra_artifact_is_rejected(dev, tmp_path):
    d = _copy_models(dev, tmp_path)
    b = bytearray((d / "seed-921.npz").read_bytes())
    b[-30] ^= 0xFF
    (d / "seed-921.npz").write_bytes(bytes(b))
    with pytest.raises(MemoryLabError, match="SHA-256 differs"):
        mc.load_models(d, "dev", SEEDS)
    d2 = tmp_path / "m2"
    shutil.copytree(dev["root"] / "models", d2)
    (d2 / "seed-922.json").unlink()
    with pytest.raises(MemoryLabError, match="content differs"):
        mc.load_models(d2, "dev", SEEDS)
    d3 = tmp_path / "m3"
    shutil.copytree(dev["root"] / "models", d3)
    (d3 / "extra.npz").write_bytes(b"x")
    with pytest.raises(MemoryLabError, match="content differs"):
        mc.load_models(d3, "dev", SEEDS)
    with pytest.raises(MemoryLabError, match="protocol seeds"):
        mc.load_models(dev["root"] / "models", "dev", [921])                 # not exactly the expected seeds


def test_strict_npz_rules(tmp_path):
    good = {k: np.ones(s) for k, s in mc.NPZ_SHAPES.items()}
    mc.check_arrays(good, "ok")
    for k, change in (("W1", lambda a: a.astype(np.float32)), ("b1", lambda a: a[:-1]), ("std", lambda a: a * 0),
                      ("mean", lambda a: a * np.nan)):
        bad = dict(good)
        bad[k] = change(good[k])
        with pytest.raises(MemoryLabError):
            mc.check_arrays(bad, "bad")
    with pytest.raises(MemoryLabError, match="keys"):
        mc.check_arrays({**good, "extra": np.ones(1)}, "bad")
    # an object array under a VALID key: only the pickle refusal itself may stop it (MemoryLabError is a
    # ValueError too, so the message is checked -- mutation check found this gap)
    np.savez(tmp_path / "seed-1.npz", **{**good, "lda_b": np.array([{"a": 1}], dtype=object)})
    (tmp_path / "seed-1.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="allow_pickle"):
        mc.load_seed(tmp_path, 1)


def test_metadata_must_be_complete_before_saving(tmp_path):
    good = {k: np.ones(s) for k, s in mc.NPZ_SHAPES.items()}
    with pytest.raises(MemoryLabError, match="metadata incomplete"):
        mc.save_seed(tmp_path, 7, good, {"seed": 7})


def test_provenance_problems_detect_wrong_streams_selection_and_binding(dev):
    loaded = mm.require_models("dev", dev["root"] / "models", seeds=SEEDS)
    _, meta = loaded["models"][921]
    b = loaded["binding"]
    assert mm.provenance_problems(meta, PROTO, "dev", 921, b) == []
    m1 = copy.deepcopy(meta)
    m1["train_streams"][0][0] = 1
    m2 = copy.deepcopy(meta)
    m2["fit"]["selected"]["init"] = (m2["fit"]["selected"]["init"] + 1) % 3
    m3 = copy.deepcopy(meta)
    m3["references_sha256"] = "0" * 64
    assert "train_streams_differ" in mm.provenance_problems(m1, PROTO, "dev", 921, b)
    assert "selection_rule_violated" in mm.provenance_problems(m2, PROTO, "dev", 921, b)
    assert "references_sha256_differs" in mm.provenance_problems(m3, PROTO, "dev", 921, b)
    assert "train_streams_differ" in mm.provenance_problems(meta, PROTO, "dev", 922, b)       # metadata of another seed


def test_smoke_or_dev_manifest_is_never_accepted_as_research(dev):
    with pytest.raises(MemoryLabError, match="manifest mode"):
        mc.load_models(dev["root"] / "models", "research", SEEDS)


def test_existing_model_directory_is_never_overwritten(dev):
    with pytest.raises(MemoryLabError, match="exists already"):
        mm.train("dev", dev["root"] / "models", seeds=SEEDS, n_pairs=300)


def test_training_never_reads_the_shift_grid(dev, monkeypatch, tmp_path):
    monkeypatch.setattr(mc, "conditions", lambda *a, **k: (_ for _ in ()).throw(AssertionError("grid read during training")))
    rec = mm.train("dev", tmp_path / "models", seeds=[923], n_pairs=200)
    assert rec["status"] == "complete"


# --- evaluation ----------------------------------------------------------------------------
def test_evaluation_complete_unchanged_models_and_fit_guard(dev):
    res = dev["res"]
    assert res["status"] == "complete" and res["fit_guard"] == "active"
    assert res["model_file_hashes_before"] == res["model_file_hashes_after"]
    assert len(res["rows"]) == 2 * 9 and {r["condition"] for r in res["rows"]} == set(dev["refs"]["conditions"])


def test_a_fit_during_the_evaluation_fails_the_run(dev, monkeypatch, tmp_path):
    orig = mc.mlp_from_arrays

    def sneaky(arr, hyper):
        m = orig(arr, hyper)
        m.fit(np.zeros((4, 12)), np.zeros(4), np.zeros((2, 12)), np.zeros(2), np.random.default_rng(0))
        return m

    monkeypatch.setattr(mc, "mlp_from_arrays", sneaky)
    res = rob.run("dev", tmp_path, models_dir=dev["root"] / "models", refs_path=dev["root"] / "refs.json", seeds=SEEDS, test_pairs=200)
    assert res["status"] == "failed" and "FitCalledDuringEvaluation" in res["failures"][0]
    with rob.no_fit():
        with pytest.raises(rob.FitCalledDuringEvaluation):
            mr.lda_rule(np.zeros((4, 12)), np.array([0, 0, 1, 1]))
    assert mr.MLP.fit is not None and mr.lda_rule.__name__ == "lda_rule"            # restored


def test_changed_weights_during_the_evaluation_fail_the_run(dev, monkeypatch, tmp_path):
    orig = mc.mlp_from_arrays

    def changing(arr, hyper):
        m = orig(arr, hyper)
        m.std = m.std * 1.0001
        return m

    monkeypatch.setattr(mc, "mlp_from_arrays", changing)
    res = rob.run("dev", tmp_path, models_dir=dev["root"] / "models", refs_path=dev["root"] / "refs.json", seeds=SEEDS, test_pairs=200)
    assert res["status"] == "failed" and "changed during the evaluation" in res["failures"][0]


def test_a_model_file_changed_during_the_evaluation_fails_the_run(dev, monkeypatch, tmp_path):
    d = _copy_models(dev, tmp_path)
    orig = mc.mlp_from_arrays

    def touching(arr, hyper):
        with open(d / "seed-922.json", "a", encoding="utf-8") as fh:              # another process edits a file
            fh.write(" ")
        return orig(arr, hyper)

    monkeypatch.setattr(mc, "mlp_from_arrays", touching)
    res = rob.run("dev", tmp_path, models_dir=d, refs_path=dev["root"] / "refs.json", seeds=SEEDS, test_pairs=200)
    assert res["status"] == "failed" and "model files changed" in res["failures"][0]
    assert res["model_file_hashes_before"] != res["model_file_hashes_after"]


def test_decomposition_identity_and_zero_at_c0(dev):
    res, refs = dev["res"], dev["refs"]
    e = ev.evaluate(res, refs)
    c = refs["conditions"]
    dB = ev.delta_b(refs)
    assert dB["c0"] == {"value": 0.0, "mc_se": 0.0, "note": dB["c0"]["note"]}
    k = "s0.03"
    assert dB[k]["mc_se"] == pytest.approx(math.sqrt(c["c0"]["B_se"] ** 2 + c[k]["B_se"] ** 2), rel=1e-15)
    t = ev.table(res)
    for name in c:
        for s in SEEDS:
            for f in (lambda r: r["mlp"]["acc"], lambda r: r["lda"]["exact"]):
                a, a0 = f(t[name][s]), f(t["c0"][s])
                loss, dG = a0 - a, (c[name]["B"] - a) - (c["c0"]["B"] - a0)
                assert loss == pytest.approx(dB[name]["value"] + dG, abs=1e-14)
    d0 = e["descriptive"]["conditions"]["c0"]["decoders"]
    assert all(d0[x]["loss"]["mean"] == 0.0 and d0[x]["delta_G"]["mean"] == 0.0 for x in d0)
    split = e["descriptive"]["conditions"][k]["decoders"]["lda_exact"]
    assert split["delta_G"]["mean"] == pytest.approx(split["lda_split"]["bayes_gap_of_lda_pop_change"]
                                                    + split["lda_split"]["gap_fixed_to_lda_pop_change"]["mean"], abs=1e-14)
    assert e["descriptive"]["conditions"][k]["delta_B"]["mc_se"] > 0 and "ci95_t" not in e["descriptive"]["conditions"][k]["delta_B"]


def test_exact_lda_and_test_lda_agree_within_the_diagnostic(dev):
    d = ev.diagnostics(dev["res"], dev["refs"])
    assert d["checks"] == {"D1": 1, "D2": 4, "D3": 9, "D4": 18}
    assert not [a for a in d["alarms"] if a.startswith("D4")]


def test_artificial_alarm_withholds_confirmatory_and_triggers_no_repeat(dev, monkeypatch):
    refs = copy.deepcopy(dev["refs"])
    refs["conditions"]["s0.03"]["lda_pop"]["acc"] = refs["conditions"]["s0.03"]["B"] + 0.1          # D3 violated
    d = ev.diagnostics(dev["res"], refs)
    assert any(a.startswith("D3") for a in d["alarms"])
    monkeypatch.setattr(ev, "release", lambda result, refs=None: {"released": True, "reasons": []})
    monkeypatch.setattr(ev, "confirmatory", lambda result: {"tests": {}})       # dev grid relabelled as research
    res = dict(dev["res"], mode="research")
    calls = []
    monkeypatch.setattr(rob, "run", lambda *a, **k: calls.append(1))
    out = ev.evaluate(res, refs)
    assert out["confirmatory_label"].startswith("withheld") and calls == []


def test_confirmatory_uses_the_same_episodes_and_holm(dev):
    c = ev.confirmatory(dev["res"])
    assert set(c["tests"]) == {"R-a", "R-sigma"} and c["tests"]["R-a"]["condition"] == "a1.35" and c["tests"]["R-sigma"]["condition"] == "s0.03"
    t = ev.table(dev["res"])
    diffs = [t["a1.35"][s]["mlp"]["acc"] - t["a1.35"][s]["lda"]["acc"] for s in SEEDS]
    assert c["tests"]["R-a"]["mean"] == pytest.approx(np.mean(diffs), abs=1e-15)
    assert all("p_holm" in v for v in c["tests"].values())


def test_release_gate_rejects_dev_and_manipulated_results(dev):
    rel = ev.release(dev["res"], dev["refs"])
    assert not rel["released"] and "mode_is_not_research" in rel["reasons"]
    bad = dict(dev["res"], mode="research", fit_guard=None, model_file_hashes_after={"x": "y"}, overrides={"test_pairs": 5})
    r = ev.release(bad, dev["refs"])["reasons"]
    for reason in ("fit_guard_missing", "model_files_changed", "overrides_used", "seeds_differ_from_protocol", "test_pairs_differ"):
        assert reason in r
    assert any(x.startswith("freeze_invalid") for x in r)                        # protocol not frozen yet


def test_timeouts_are_enforced(dev, tmp_path):
    rec = mm.train("dev", tmp_path / "models", seeds=[923], n_pairs=200, time_limit_s=0.0)
    assert rec["status"] == "aborted_timeout" and not (tmp_path / "models" / "manifest.json").exists()
    res = rob.run("dev", tmp_path, models_dir=dev["root"] / "models", refs_path=dev["root"] / "refs.json", seeds=SEEDS,
                  test_pairs=200, time_limit_s=0.0)
    assert res["status"] == "aborted_timeout"
    with pytest.raises(MemoryLabError, match="time limit"):
        mref.compute("dev", n_mc=5000, time_limit_s=0.0)


# --- phases and freeze gates ---------------------------------------------------------------
def test_research_and_smoke_are_blocked_before_the_freeze(tmp_path, monkeypatch):
    with pytest.raises(MemoryLabError, match="reference_phase|research_reference_phase"):
        mref.compute("research")
    with pytest.raises(MemoryLabError, match="training_phase"):
        mm.train("research")
    with pytest.raises(MemoryLabError, match="not frozen"):
        mm.train("smoke")
    with pytest.raises(MemoryLabError, match="not frozen"):
        rob.run("research", tmp_path)
    with pytest.raises(MemoryLabError, match="no overrides"):
        rob.run("research", tmp_path, test_pairs=5)


def _phase_paths(monkeypatch, tmp_path):
    for name in ("RESEARCH_REFERENCES", "RESEARCH_CLAIM", "RESEARCH_FAILURE"):
        monkeypatch.setattr(mref, name, tmp_path / f"{name}.json")
    for name in ("RESEARCH_MODELS", "TRAINING_CLAIM", "TRAINING_FAILURE", "MODEL_FREEZE"):
        monkeypatch.setattr(mm, name, tmp_path / name)


def test_reference_phase_checks_before_compute_and_locks(monkeypatch, tmp_path):
    _phase_paths(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(mref, "compute", lambda *a, **k: calls.append(1) or {"schema": "x"})
    monkeypatch.setattr(mref, "git_clean", lambda paths: False)
    with pytest.raises(MemoryLabError, match="not committed"):
        mref.research_reference_phase()
    monkeypatch.setattr(mref, "git_clean", lambda paths: True)
    with pytest.raises(MemoryLabError, match="not frozen"):
        mref.research_reference_phase()
    assert calls == [] and not mref.RESEARCH_CLAIM.exists()
    monkeypatch.setattr(mref, "require_protocol_frozen", lambda what: {"protocol_sha256": "p"})
    mref.research_reference_phase()
    assert calls == [1] and mref.RESEARCH_CLAIM.exists() and mref.RESEARCH_REFERENCES.exists()
    with pytest.raises(MemoryLabError, match="already completed"):
        mref.research_reference_phase()
    mref.RESEARCH_REFERENCES.unlink()
    with pytest.raises(MemoryLabError, match="already started"):
        mref.research_reference_phase()
    assert calls == [1]


def test_training_phase_checks_before_compute_and_records_failure(monkeypatch, tmp_path):
    _phase_paths(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(mm, "train", lambda *a, **k: calls.append(1) or (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(mref, "git_clean", lambda paths: True)
    with pytest.raises(MemoryLabError, match="not frozen"):
        mm.training_phase()
    assert calls == []
    monkeypatch.setattr(mref, "require_protocol_frozen", lambda what: {"protocol_sha256": "p"})
    monkeypatch.setattr(mref, "require_references", lambda case_set, path=None: {"refs": {}, "sha256": "r"})
    with pytest.raises(RuntimeError, match="boom"):
        mm.training_phase()
    assert calls == [1] and mm.TRAINING_CLAIM.exists() and mm.TRAINING_FAILURE.exists()
    with pytest.raises(MemoryLabError, match="already started or failed"):
        mm.training_phase()
    assert calls == [1]


def test_frozen_files_of_m10_and_m11_are_unchanged():
    from experiments.mandala_memory import m11_run

    rec = json.loads(m11_run.FREEZE_RECORD.read_text(encoding="utf-8"))
    assert rec["code_sha256"] == m11_run.code_sha256()


def test_real_d1_source_is_the_frozen_m10_value():
    src = mref.d1_source("research")
    assert src["B"] == pytest.approx(0.9115818840370391, abs=1e-15) and src["B_se"] > 0
    dsrc = mref.d1_source("dev")
    assert 0.5 < dsrc["B"] < 1


def test_protocol_yaml_twin_equals_the_json():
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load((mc.HERE / "protocol" / "m12_protokoll.yaml").read_text(encoding="utf-8")) == PROTO
