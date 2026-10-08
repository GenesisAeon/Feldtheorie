"""LR5: artifact chain, run management, deterministic resume and the release gate (plan 12/13; review
LANTERN_LR4_NACHREVIEW LR5 duties). Interruption and manipulation cases must be detected; nothing may be
overwritten; a resumed run must equal an uninterrupted one exactly. Smoke runs only, development study."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from experiments.lantern_reconstruction import artifacts, decoders, evaluate, observation, release, runs, streams, training
from experiments.lantern_reconstruction import contexts
from experiments.lantern_reconstruction.artifacts import IntegrityError

GRID = dict(conditions=("lantern", "uncoupled"), sizes={"train": 30, "val": 12, "test": 20}, proposals=100)


def _identities(run_dir):
    out = {}
    for rec in sorted((Path(run_dir) / "cells").glob("*/record.json")):
        r = json.loads(rec.read_text(encoding="utf-8"))
        out[rec.parent.name] = (r["model"]["model_identity"], r["predictions"]["arrays"], r["scores"])
    return out


@pytest.fixture(scope="module")
def complete_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("lr5")
    rd = runs.create_run(root / "runs", "smoke", [0, 1], run_id="reference", **GRID)
    assert runs.execute(rd, lock_root=root / "locks") == "complete"
    return root, rd


def _copy(complete_run, tmp_path, name="copy"):
    dst = tmp_path / name
    shutil.copytree(complete_run[1], dst)
    return dst


# --- artifacts -----------------------------------------------------------------------------------------
def test_write_exclusive_never_overwrites_and_leaves_no_temp(tmp_path):
    p = tmp_path / "a.bin"
    artifacts.write_exclusive(p, b"first")
    with pytest.raises(FileExistsError):
        artifacts.write_exclusive(p, b"second")
    assert p.read_bytes() == b"first" and [q.name for q in tmp_path.iterdir()] == ["a.bin"]


def test_write_exclusive_holds_under_a_race(tmp_path, monkeypatch):
    """The name appears between the existence check and the final step (another writer): os.link must refuse.
    (Mutation check: with os.replace the second writer silently overwrote -- the sequential test missed it.)"""
    p = tmp_path / "race.bin"
    artifacts.write_exclusive(p, b"first")
    real_exists = Path.exists
    monkeypatch.setattr(artifacts.Path, "exists", lambda self: False if self == p else real_exists(self))
    with pytest.raises(FileExistsError):
        artifacts.write_exclusive(p, b"second")
    monkeypatch.undo()
    assert p.read_bytes() == b"first" and [q.name for q in tmp_path.iterdir()] == ["race.bin"]


def test_model_identity_binds_arrays_and_metadata_and_integrity_before_after(monkeypatch):
    ctx = contexts.make_context(streams.defaults()["development_study_id"], 0)
    spec = observation.observation_spec(ctx, "B")
    rng = np.random.default_rng(3)
    m = training.fit_ridge(spec, rng.normal(size=(30, 16)), rng.uniform(-1, 1, (30, 4)), rng.normal(size=(10, 16)), rng.uniform(-1, 1, (10, 4)))
    ident = artifacts.model_identity(m)
    from dataclasses import replace
    assert artifacts.model_identity(replace(m, n_val=11)) != ident                 # metadata
    assert artifacts.model_identity(replace(m, b=m.b + 1e-12)) != ident            # arrays
    X, U = rng.normal(size=(5, 16)), rng.uniform(-1, 1, (5, 4))
    artifacts.evaluate_with_integrity(m, ident, X, U)
    with pytest.raises(IntegrityError, match="before"):
        artifacts.evaluate_with_integrity(m, "0" * 64, X, U)
    real = evaluate.score_cell

    def tampering(model, X, U):                                                   # swaps W during the evaluation
        object.__setattr__(model, "W", decoders._ro(np.zeros_like(model.W)))
        return real(model, X, U)
    monkeypatch.setattr(evaluate, "score_cell", tampering)
    with pytest.raises(IntegrityError, match="during"):
        artifacts.evaluate_with_integrity(m, ident, X, U)


# --- complete run and release -----------------------------------------------------------------------------
def test_complete_run_release_fields_are_separate(complete_run):
    rep = release.release_report(complete_run[1])
    assert rep["technically_complete"] and rep["n_verified_cells"] == rep["n_expected_cells"] == 2 * (2 + 3) * 2 * 7
    assert rep["hypothesis"]["status"] == "not_evaluated" and rep["convergence_gate"]["passed"]
    assert not rep["control_alarms"]["positive_spurious_success_alarm"] and "target_dependence_alarm" in rep["control_alarms"]
    assert not rep["scientifically_interpretable"] and any("G0" in b for b in rep["scientific_blocks"])   # 30 train episodes
    assert all(v == {"reset": True, "zero_impulse": True} for v in rep["structure_checks"].values())
    assert [e["to"] for e in runs.EventLog(complete_run[1] / "events.jsonl").read() if e["event"] == "status"] == ["running", "complete"]


def test_release_report_is_written_once(complete_run, tmp_path):
    rd = _copy(complete_run, tmp_path)
    release.write_release_report(rd)
    with pytest.raises(FileExistsError):
        release.write_release_report(rd)


def test_completed_run_cannot_be_executed_again(complete_run, tmp_path):
    rd = _copy(complete_run, tmp_path)
    with pytest.raises(runs.ResumeRefused, match="complete"):
        runs.execute(rd, lock_root=tmp_path / "locks")


# --- interruption and deterministic resume (plan mutant 18) ---------------------------------------------
def test_interrupted_run_resumes_to_exactly_the_uninterrupted_result(complete_run, tmp_path):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="resumed", **GRID)
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=tmp_path / "locks", stop_after=23)
    assert runs.status(rd) == "interrupted"
    # a crash between the files and the record: drop the record of the last finished cell (files stay)
    last = [e["cell"] for e in runs.EventLog(rd / "events.jsonl").read() if e["event"] == "cell_completed"][-1]
    (rd / "cells" / last / "record.json").unlink()
    assert runs.execute(rd, lock_root=tmp_path / "locks") == "complete"
    assert _identities(rd) == _identities(complete_run[1])                      # same models, predictions, scores
    assert release.release_report(rd)["technically_complete"]
    assert [e["to"] for e in runs.EventLog(rd / "events.jsonl").read() if e["event"] == "status"] == ["running", "interrupted", "running", "complete"]


def test_resume_refused_after_code_or_configuration_change(tmp_path, monkeypatch):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="changed", **GRID)
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=tmp_path / "locks", stop_after=3)
    real = runs.code_identity

    def other_code():
        c = real()
        c["files"]["training.py"] = "0" * 64
        c["identity"] = artifacts.identity(c["files"])
        return c
    monkeypatch.setattr(runs, "code_identity", other_code)
    with pytest.raises(runs.ResumeRefused, match="training.py"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    monkeypatch.setattr(runs, "code_identity", real)
    monkeypatch.setattr(runs.streams, "config_sha256", lambda: "f" * 64)
    with pytest.raises(runs.ResumeRefused, match="config"):
        runs.execute(rd, lock_root=tmp_path / "locks")


def test_resume_with_a_changed_model_is_an_integrity_failure_and_terminal(tmp_path):
    """Plan mutant 18: continuing with another seed/model. An orphan model that is not the recomputed one
    must not be adopted; the run becomes failed_integrity and stays so."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="orphan", **GRID)
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=tmp_path / "locks", stop_after=5)
    last = [e["cell"] for e in runs.EventLog(rd / "events.jsonl").read() if e["event"] == "cell_completed"][-1]
    (rd / "cells" / last / "record.json").unlink()
    meta = json.loads((rd / "cells" / last / "model.json").read_text(encoding="utf-8"))
    meta["provenance"]["dt"] = 0.01                                              # a different model
    (rd / "cells" / last / "model.json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(IntegrityError, match="orphan"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) == "failed_integrity"
    with pytest.raises(runs.ResumeRefused, match="failed_integrity"):
        runs.execute(rd, lock_root=tmp_path / "locks")


def test_run_json_tampering_is_detected(complete_run, tmp_path):
    rd = _copy(complete_run, tmp_path)
    run = json.loads((rd / "run.json").read_text(encoding="utf-8"))
    run["grid"]["study_id"] += 1                                                   # "a new seed"
    (rd / "run.json").write_text(json.dumps(run), encoding="utf-8")
    with pytest.raises(IntegrityError, match="run identity"):
        runs.load_run(rd)
    rep = release.release_report(rd)
    assert not rep["technically_complete"] and not rep["scientifically_interpretable"]


# --- manipulation of artifacts ---------------------------------------------------------------------------
def _first_cell(rd):
    return sorted((rd / "cells").iterdir())[0]


@pytest.mark.parametrize("attack", ["score", "model_npz_swap", "model_json", "predictions", "delete_cell", "extra_cell", "foreign_record",
                                    "record_run_identity", "record_cell"])
def test_release_detects_manipulated_artifacts(complete_run, tmp_path, attack):
    rd = _copy(complete_run, tmp_path)
    cells = sorted((rd / "cells").iterdir())
    a, b = cells[0], cells[1]
    rec = json.loads((a / "record.json").read_text(encoding="utf-8"))
    if attack == "score":
        rec["scores"]["G"] += 0.25
        (a / "record.json").write_text(json.dumps(rec), encoding="utf-8")
    elif attack == "model_npz_swap":
        (a / "model.npz").unlink()
        shutil.copy(b / "model.npz", a / "model.npz")
    elif attack == "model_json":
        meta = json.loads((a / "model.json").read_text(encoding="utf-8"))
        meta["n_train"] = 31
        (a / "model.json").write_text(json.dumps(meta), encoding="utf-8")
    elif attack == "predictions":
        (a / "predictions.npz").unlink()
        shutil.copy(b / "predictions.npz", a / "predictions.npz")
    elif attack == "delete_cell":
        shutil.rmtree(a)
    elif attack == "extra_cell":
        shutil.copytree(a, rd / "cells" / "c009__lantern__none__A__t0")
    elif attack == "foreign_record":
        (a / "record.json").unlink()
        shutil.copy(b / "record.json", a / "record.json")
    elif attack in ("record_run_identity", "record_cell"):      # only the record's binding can catch these
        if attack == "record_run_identity":                      # (mutation check: a gap that survived first)
            rec["run_identity"] = "0" * 64                       # a record that claims another run
        else:
            rec["cell"]["context_fingerprint"] = "0" * 64       # a record that claims another cell definition
        (a / "record.json").write_text(json.dumps(rec), encoding="utf-8")
    rep = release.release_report(rd)
    assert not rep["technically_complete"] and not rep["scientifically_interpretable"] and rep["problems"]


def test_edited_structure_record_is_detected(complete_run, tmp_path):
    rd = _copy(complete_run, tmp_path)
    p = rd / "structure" / "c000.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s["checks"]["reset"], s["passed"] = False, False
    p.write_text(json.dumps(s), encoding="utf-8")
    rep = release.release_report(rd)
    assert not rep["technically_complete"] and any("recomputation" in x for x in rep["problems"])


def test_failed_reset_control_blocks_release_plan_mutant_17(complete_run, tmp_path, monkeypatch):
    """If the reset control really fails (recorded AND recomputed), the release is blocked."""
    rd = _copy(complete_run, tmp_path)
    failing = lambda ctx, C, g, sizes: {"context_id": ctx.context_id, "episodes": 8, "checks": {"reset": False, "zero_impulse": True}, "passed": False}
    p = rd / "structure" / "c001.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s.update(checks={"reset": False, "zero_impulse": True}, passed=False)
    p.write_text(json.dumps(s), encoding="utf-8")
    monkeypatch.setattr(runs, "_structure_check", failing)
    rep = release.release_report(rd)
    assert not rep["scientifically_interpretable"] and any("reset" in b for b in rep["scientific_blocks"])


# --- trajectory reuse (plan 13; LR5 budget) ----------------------------------------------------------------
def test_permuted_targets_reuses_the_trajectories_bit_identically(monkeypatch):
    from experiments.lantern_reconstruction import episodes, registry_adapter as ra, runner
    s = ra.load_verified_snapshot()
    ctx = contexts.make_context(streams.defaults()["development_study_id"], 0)
    prep = runner.prepare_context(ctx, np.array(s.C), {"train": 30, "val": 12, "test": 20}, 100)
    g = float(s.structure["g"])
    fresh = [c["result"]["projected"] for c in runner.iter_cells(ctx, prep, g, "lantern", "permuted_targets", ("A", "B"))]
    calls, real = [], episodes.simulate
    monkeypatch.setattr(episodes, "simulate", lambda *a, **k: calls.append(a[4] if len(a) > 4 else k.get("control")) or real(*a, **k))
    cache = {}
    list(runner.iter_cells(ctx, prep, g, "lantern", "none", ("A", "B"), state_cache=cache))
    cached = [c["result"]["projected"] for c in runner.iter_cells(ctx, prep, g, "lantern", "permuted_targets", ("A", "B"), state_cache=cache)]
    assert len(calls) == 3 and all(np.array_equal(a, b) for a, b in zip(fresh, cached))       # 3 splits, once
    # reset and zero impulse start from the same phi * 1: integrated once, results bit-identical to fresh runs
    zi_fresh = [c["result"]["projected"] for c in runner.iter_cells(ctx, prep, g, "lantern", "zero_impulse", ("A",))]
    calls.clear()
    list(runner.iter_cells(ctx, prep, g, "lantern", "reset", ("A",), state_cache=cache))
    zi = [c["result"]["projected"] for c in runner.iter_cells(ctx, prep, g, "lantern", "zero_impulse", ("A",), state_cache=cache)]
    assert len(calls) == 3 and all(np.array_equal(a, b) for a, b in zip(zi_fresh, zi))
    assert runner.initial_state_key(ctx, prep, "lantern", "reset") == runner.initial_state_key(ctx, prep, "lantern", "zero_impulse")
    assert runner.initial_state_key(ctx, prep, "lantern", "none") != runner.initial_state_key(ctx, prep, "lantern", "reset")
    assert runner.initial_state_key(ctx, prep, "lantern", "none") != runner.initial_state_key(ctx, prep, "uncoupled", "none")


# --- lock, status, kinds, clock ---------------------------------------------------------------------------
def test_study_lock_is_exclusive(tmp_path):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="locked", **GRID)
    lock = tmp_path / "locks" / f"study-{streams.defaults()['development_study_id']}-smoke.lock"
    lock.parent.mkdir()
    lock.write_text("{}", encoding="utf-8")
    with pytest.raises(runs.LockError):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) is None and lock.exists()


def test_status_transitions(tmp_path):
    log = runs.EventLog(tmp_path / "events.jsonl")
    runs.set_status(log, "running", "start")
    runs.set_status(log, "complete", "done")
    with pytest.raises(ValueError):
        runs.set_status(log, "running", "a score looked good")
    runs.set_status(log, "failed_integrity", "tamper found")
    for s in ("running", "complete", "interrupted"):
        with pytest.raises(ValueError):
            runs.set_status(log, s, "no way back")


@pytest.mark.parametrize("kw", [{"kind": "research"}, {"contexts_": [0, 0]}, {"conditions": ("uncoupled",)}, {"contexts_": [-1]}])
def test_create_run_refuses_invalid_runs(tmp_path, kw):
    args = {"kind": "smoke", "contexts_": [0, 1], **GRID, **kw}
    with pytest.raises(ValueError):
        runs.create_run(tmp_path / "runs", args.pop("kind"), args.pop("contexts_"), **args)


def test_clock_gap_is_logged(tmp_path, monkeypatch):
    log = runs.EventLog(tmp_path / "e.jsonl")
    clock = {"wall": 1000.0, "mono": 50.0}
    monkeypatch.setattr(runs.time, "time", lambda: clock["wall"])
    monkeypatch.setattr(runs.time, "monotonic", lambda: clock["mono"])
    log.append("a")
    clock["wall"] += 600.0                      # wall clock jumped 10 min, monotonic only 1 s: sleep
    clock["mono"] += 1.0
    log.append("b")
    assert [e["event"] for e in log.read()] == ["a", "clock_gap", "b"]
