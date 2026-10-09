"""Review REVIEW_LR5 (Astra, 1c24292): one regression per reproduced counterexample, positive references first.
R1 resume after a process loss (killed child process, truncated log, unexpected exception), R2 training and
validation sizes bound to the run, R3 changed software refuses resume, R4 a lone/incomplete model file is
checked against the recomputed model (integrity failure, nothing replaced)."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

from experiments.lantern_reconstruction import artifacts, contexts, decoders, release, runner, runs, streams
from experiments.lantern_reconstruction.artifacts import IntegrityError

GRID = dict(conditions=("lantern", "uncoupled"), sizes={"train": 30, "val": 12, "test": 20}, proposals=100)
REPO = runs.HERE.parents[1]


def _identities(run_dir):
    out = {}
    for rec in sorted((Path(run_dir) / "cells").glob("*/record.json")):
        r = json.loads(rec.read_text(encoding="utf-8"))
        out[rec.parent.name] = (r["model"]["model_identity"], r["predictions"]["arrays"], r["scores"])
    return out


@pytest.fixture(scope="module")
def reference(tmp_path_factory):
    root = tmp_path_factory.mktemp("lr5r")
    rd = runs.create_run(root / "runs", "smoke", [0, 1], run_id="reference", **GRID)
    assert runs.execute(rd, lock_root=root / "locks") == "complete"
    return rd


def _events(rd):
    return runs.EventLog(Path(rd) / "events.jsonl").read()


# --- R1 ----------------------------------------------------------------------------------------------
def test_r1_review_state_running_is_not_a_value_error_and_needs_an_identifiable_process(tmp_path):
    """Review: status set to running without any process -> 'ValueError running -> running'. Now execute()
    refuses with a pointer to recover(); recover() refuses because no process can be identified."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], conditions=("lantern",), sizes={"train": 2, "val": 2, "test": 2}, proposals=1)
    runs.set_status(runs.EventLog(rd / "events.jsonl"), "running", "simulate last durable event before process death")
    with pytest.raises(runs.ResumeRefused, match="recover"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    with pytest.raises(runs.ResumeRefused, match="cannot be identified"):
        runs.recover(rd)
    assert runs.status(rd) == "running"


def test_r1_killed_child_process_recovers_to_the_uninterrupted_result(reference, tmp_path):
    """A real process loss: a child process runs the same grid and is killed mid-run (TerminateProcess /
    SIGKILL, no except-block runs). recover() checks the pid is dead, removes ITS stale lock (logged),
    sets 'interrupted'; execute() resumes the same run identity; the result equals the uninterrupted run."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="killed", **GRID)
    locks = tmp_path / "locks"
    code = ("import sys; sys.path.insert(0, r'%s'); from experiments.lantern_reconstruction import runs; "
            "runs.execute(r'%s', lock_root=r'%s')" % (REPO, rd, locks))
    env = dict(os.environ, PYTHONPATH=str(REPO), PYTHONDONTWRITEBYTECODE="1")
    child = subprocess.Popen([sys.executable, "-c", code], cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pid = None
    try:
        deadline = time.time() + 300
        while sum(e["event"] == "cell_completed" for e in _events(rd)) < 5:
            assert child.poll() is None and time.time() < deadline, "child ended or stalled before it could be killed"
            time.sleep(0.2)
        # kill the process that HOLDS the lock (on Windows a venv python.exe is a launcher with the real
        # interpreter as its own child; killing only the launcher would not be the process loss we test)
        pid = [e for e in _events(rd) if e["event"] == "lock_acquired"][-1]["pid"]
        assert runs.process_alive(pid) is True
        os.kill(pid, 9)                                                          # TerminateProcess / SIGKILL
    finally:
        child.kill()
        child.wait()
        if pid is not None:
            t_end = time.time() + 20
            while runs.process_alive(pid) and time.time() < t_end:
                time.sleep(0.1)
    assert runs.status(rd) == "running" and any(locks.glob("*.lock"))           # what a process loss leaves behind
    assert runs.process_alive(pid) is False
    with pytest.raises(runs.ResumeRefused, match="recover"):
        runs.execute(rd, lock_root=locks)
    assert runs.recover(rd) == "interrupted"
    removed = [e for e in _events(rd) if e["event"] == "stale_lock_removed"]
    assert len(removed) == 1 and removed[0]["content"]["pid"] == pid and removed[0]["content"]["run_id"] == "killed"
    assert runs.execute(rd, lock_root=locks) == "complete"
    assert _identities(rd) == _identities(reference)
    assert release.release_report(rd)["technically_complete"]
    assert [e["to"] for e in _events(rd) if e["event"] == "status"] == ["running", "interrupted", "running", "complete"]


def test_r1_truncated_last_log_line_is_acknowledged_append_only(tmp_path):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="trunc", **GRID)
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=tmp_path / "locks", stop_after=2)
    log = rd / "events.jsonl"
    # simulate a process loss in the middle of a running phase: status running + lock + half a line
    runs.EventLog(log).append("lock_acquired", lock=str((tmp_path / "locks" / f"study-{streams.defaults()['development_study_id']}-smoke.lock").resolve()),
                              pid=99999999, host=platform.node())
    runs.set_status(runs.EventLog(log), "running", "resume")
    before = log.read_bytes() + b'{"utc": "2026-10-09T10:00'
    log.write_bytes(before)
    with pytest.raises(runs.TruncatedLogError):
        runs.status(rd)
    assert not release.release_report(rd)["technically_complete"]
    assert runs.recover(rd) == "interrupted"
    assert log.read_bytes().startswith(before)                                 # nothing rewritten
    ev = _events(rd)
    assert any(e["event"] == "log_line_truncated" and e["fragment_bytes"] == len(b'{"utc": "2026-10-09T10:00') for e in ev)
    assert runs.execute(rd, lock_root=tmp_path / "locks") == "complete"


def _running_with_incomplete_line(tmp_path, run_id, pid, host):
    """A run whose holder took the real study lock and is 'running'; the log ends mid-way in a JSON event."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id=run_id, conditions=("lantern",), sizes={"train": 2, "val": 2, "test": 2}, proposals=1)
    locks = tmp_path / "locks"
    lock = runs.StudyLock(locks, runs.load_run(rd)["grid"]["study_id"], "smoke", run_id).__enter__()
    held = json.loads(lock.path.read_text(encoding="utf-8"))
    held["pid"] = pid
    lock.path.write_text(json.dumps(held), encoding="utf-8")
    log = runs.EventLog(rd / "events.jsonl")
    log.append("lock_acquired", lock=str(lock.path.resolve()), pid=pid, host=host)
    runs.set_status(log, "running", "a writer between two writes")
    with open(log.path, "ab") as f:
        f.write(b'{"event":"unit_')
    return rd, lock


@pytest.mark.parametrize("case", ["alive_owner", "foreign_host", "undecidable", "lock_of_another_run", "recovery_in_progress"])
def test_r1_refused_recovery_leaves_log_and_lock_byte_identical(tmp_path, monkeypatch, case):
    """Review of b9c405b (F1): recover() appended a repair BEFORE it found the owner alive; the writer's
    completed line then made the log unreadable. Every refusal must now leave log and lock untouched."""
    pid, host = (os.getpid(), platform.node()) if case == "alive_owner" else (99999999, platform.node())
    if case == "foreign_host":
        host = "another-machine"
    rd, lock = _running_with_incomplete_line(tmp_path, case, pid, host)
    if case == "undecidable":
        monkeypatch.setattr(runs, "process_alive", lambda p: None)
    if case == "lock_of_another_run":
        held = json.loads(lock.path.read_text(encoding="utf-8"))
        held["run_id"] = "someone-else"
        lock.path.write_text(json.dumps(held), encoding="utf-8")
    guard = lock.path.parent / (lock.path.name + ".admin")
    if case == "recovery_in_progress":
        guard.write_text("{}", encoding="utf-8")
    log_before, lock_before = (rd / "events.jsonl").read_bytes(), lock.path.read_bytes()
    with pytest.raises(runs.ResumeRefused):
        runs.recover(rd)
    assert (rd / "events.jsonl").read_bytes() == log_before and lock.path.read_bytes() == lock_before
    assert guard.exists() == (case == "recovery_in_progress")
    if case == "alive_owner":                                   # the live writer completes its line: still readable
        with open(rd / "events.jsonl", "ab") as f:
            f.write(b'completed"}\n')
        assert runs.status(rd) == "running"


def test_r1_change_between_diagnosis_and_guard_is_caught(tmp_path, monkeypatch):
    """Race window: after the read-only diagnosis, another run takes over the study lock just as the recovery
    guard is created. The re-check under the guard must refuse -- the other run's lock and the log stay
    byte-identical. (Mutation check: without the re-check the foreign lock was deleted.)"""
    rd, lock = _running_with_incomplete_line(tmp_path, "race", 99999999, platform.node())
    real_open, foreign = os.open, json.dumps({"run_id": "other-run", "pid": os.getpid(), "utc": "now"})

    def open_with_race(path, *a, **k):
        if str(path).endswith(".admin"):
            lock.path.write_text(foreign, encoding="utf-8")     # the other run wins the lock in this window
        return real_open(path, *a, **k)
    monkeypatch.setattr(runs.os, "open", open_with_race)
    log_before = (rd / "events.jsonl").read_bytes()
    with pytest.raises(runs.ResumeRefused, match="held by"):
        runs.recover(rd)
    assert lock.path.read_text(encoding="utf-8") == foreign and (rd / "events.jsonl").read_bytes() == log_before
    assert not (lock.path.parent / (lock.path.name + ".admin")).exists()


def test_r1_dead_owner_incomplete_line_recovers_and_keeps_the_original_bytes(reference, tmp_path):
    """Positive counterpart: a really dead owner (pid that no longer exists), incomplete line: recovery
    succeeds, the original bytes stay the prefix of the log, the run resumes to the uninterrupted result."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="deadowner", **GRID)
    locks = tmp_path / "locks"
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=locks, stop_after=3)
    lock = runs.StudyLock(locks, runs.load_run(rd)["grid"]["study_id"], "smoke", "deadowner").__enter__()
    held = json.loads(lock.path.read_text(encoding="utf-8"))
    held["pid"] = 99999999
    lock.path.write_text(json.dumps(held), encoding="utf-8")
    log = runs.EventLog(rd / "events.jsonl")
    log.append("lock_acquired", lock=str(lock.path.resolve()), pid=99999999, host=platform.node())
    runs.set_status(log, "running", "resume")
    with open(log.path, "ab") as f:
        f.write(b'{"event":"cell_')
    original = (rd / "events.jsonl").read_bytes()
    assert runs.process_alive(99999999) is False
    assert runs.recover(rd) == "interrupted"
    assert (rd / "events.jsonl").read_bytes().startswith(original) and not lock.path.exists()
    assert not (lock.path.parent / (lock.path.name + ".admin")).exists()
    assert runs.execute(rd, lock_root=locks) == "complete"
    assert _identities(rd) == _identities(reference)


def test_event_log_lines_end_with_lf_on_every_platform(tmp_path):
    log = runs.EventLog(tmp_path / "e.jsonl")
    log.append("a")
    log.append("b")
    assert b"\r" not in (tmp_path / "e.jsonl").read_bytes()


def test_r1_an_unparsable_line_without_acknowledgement_is_an_integrity_error(tmp_path):
    log = runs.EventLog(tmp_path / "e.jsonl")
    log.append("a")
    with open(tmp_path / "e.jsonl", "ab") as f:
        f.write(b"garbage\n")
    log.append("b")
    with pytest.raises(IntegrityError, match="without a recorded truncation"):
        log.read()


def test_r1_unexpected_exception_leaves_a_resumable_state(tmp_path, monkeypatch):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="boom", **GRID)
    real, n = runner.iter_cells, {"k": 0}

    def flaky(*a, **k):
        for c in real(*a, **k):
            n["k"] += 1
            if n["k"] == 4:
                raise RuntimeError("boom")
            yield c
    monkeypatch.setattr(runner, "iter_cells", flaky)
    with pytest.raises(RuntimeError, match="boom"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    st = [e for e in _events(rd) if e["event"] == "status"][-1]
    assert st["to"] == "interrupted" and "unexpected RuntimeError: boom" in st["reason"]
    monkeypatch.setattr(runner, "iter_cells", real)
    assert runs.execute(rd, lock_root=tmp_path / "locks") == "complete"


def test_r1_recover_refuses_a_possibly_alive_or_foreign_process(tmp_path):
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="alive", **GRID)
    lock = (tmp_path / "locks" / f"study-{streams.defaults()['development_study_id']}-smoke.lock").resolve()
    log = runs.EventLog(rd / "events.jsonl")
    log.append("lock_acquired", lock=str(lock), pid=os.getpid(), host=platform.node())     # this process: alive
    runs.set_status(log, "running", "start")
    with pytest.raises(runs.ResumeRefused, match="may still be active"):
        runs.recover(rd)
    log.append("lock_acquired", lock=str(lock), pid=99999999, host="another-machine")
    with pytest.raises(runs.ResumeRefused, match="host"):
        runs.recover(rd)
    assert runs.process_alive(os.getpid()) is True and runs.process_alive(-1) is None


# --- R2 ----------------------------------------------------------------------------------------------
def _copy(reference, tmp_path):
    dst = tmp_path / "copy"
    shutil.copytree(reference, dst)
    return dst


def _rewrite_model_meta(rd, change):
    """The review's attack: change the model metadata and CONSISTENTLY renew the JSON hash and identity."""
    run = runs.load_run(rd)
    c = runs.expected_cells(run["grid"])[0]
    folder = rd / "cells" / runs.cell_dir_name(c)
    rec = json.loads((folder / "record.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "model.json").read_text(encoding="utf-8"))
    change(meta)
    (folder / "model.json").write_text(json.dumps(meta), encoding="utf-8")
    rec["model"]["json_sha256"] = artifacts.sha256((folder / "model.json").read_bytes())
    rec["model"]["model_identity"] = artifacts.identity(meta)
    (folder / "record.json").write_text(json.dumps(rec), encoding="utf-8")
    return run, c, contexts.make_context(run["grid"]["study_id"], c["context_id"])


def test_r2_reference_cell_is_accepted(reference):
    run = runs.load_run(reference)
    c = runs.expected_cells(run["grid"])[0]
    runs.verify_record(reference, run, c, contexts.make_context(run["grid"]["study_id"], 0))


@pytest.mark.parametrize("change", [{"n_train": 2, "n_val": 2}, {"n_train": 2}, {"n_val": 2}, {"n_train": 31}])
def test_r2_wrong_training_or_validation_size_is_refused(reference, tmp_path, change):
    rd = _copy(reference, tmp_path)
    run, c, ctx = _rewrite_model_meta(rd, lambda m: m.update(change))
    with pytest.raises(IntegrityError, match="expected parameters"):
        runs.verify_record(rd, run, c, ctx)
    rep = release.release_report(rd)
    assert not rep["technically_complete"] and any("expected parameters" in p for p in rep["problems"])


def test_r2_model_software_must_be_the_runs(reference, tmp_path):
    rd = _copy(reference, tmp_path)
    run, c, ctx = _rewrite_model_meta(rd, lambda m: m["software"].update(numpy="0.0.changed"))
    with pytest.raises(IntegrityError, match="expected parameters"):
        runs.verify_record(rd, run, c, ctx)


def test_r2_wrong_sizes_refused_before_anything_is_written(reference, tmp_path):
    run = runs.load_run(reference)
    c = runs.expected_cells(run["grid"])[0]
    ctx = contexts.make_context(run["grid"]["study_id"], 0)
    good = artifacts.load_model_verified(reference / "cells" / runs.cell_dir_name(c),
                                         json.loads((reference / "cells" / runs.cell_dir_name(c) / "record.json").read_text(encoding="utf-8"))["model"])
    from dataclasses import replace
    bad = replace(good, n_train=2)
    with pytest.raises(IntegrityError, match="expected parameters"):
        runs._persist_cell(tmp_path, run, ctx, c, bad, np.zeros((20, 66)), np.zeros((20, 4)))
    assert not (tmp_path / "cells").exists()


# --- R3 ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("key", ["python", "numpy", "scipy"])
def test_r3_changed_software_refuses_resume(reference, monkeypatch, key):
    run = runs.load_run(reference)
    runs.check_resumable(run)                                                  # positive reference: unchanged
    real = runs.software
    monkeypatch.setattr(runs, "software", lambda: {**real(), key: "0.0.changed"})
    with pytest.raises(runs.ResumeRefused, match="software"):
        runs.check_resumable(run)


# --- R4 ----------------------------------------------------------------------------------------------
@pytest.fixture()
def model_and_ids(reference):
    run = runs.load_run(reference)
    c = runs.expected_cells(run["grid"])[0]
    folder = reference / "cells" / runs.cell_dir_name(c)
    rec = json.loads((folder / "record.json").read_text(encoding="utf-8"))
    return artifacts.load_model_verified(folder, rec["model"]), rec["predictions"]["arrays"]


def test_r4_review_wrong_lone_npz_is_an_integrity_failure_not_replaced(model_and_ids, tmp_path):
    """Review: an NPZ with only wrong=[123.] passed and was renamed + replaced. Now: integrity failure,
    file untouched, nothing new written."""
    model, pred = model_and_ids
    np.savez(tmp_path / "model.npz", wrong=np.array([123.]))
    before = (tmp_path / "model.npz").read_bytes()
    with pytest.raises(IntegrityError, match="orphan model arrays"):
        runs._adopt_orphans(tmp_path, model, pred)
    assert (tmp_path / "model.npz").read_bytes() == before and [p.name for p in tmp_path.iterdir()] == ["model.npz"]


@pytest.mark.parametrize("payload", ["right_names_wrong_values", "garbage_bytes", "object_array"])
def test_r4_other_wrong_lone_npz_files(model_and_ids, tmp_path, payload):
    model, pred = model_and_ids
    if payload == "right_names_wrong_values":
        np.savez(tmp_path / "model.npz", **{k: np.asarray(getattr(model, k)) + 1.0 for k in decoders.ARRAYS})
    elif payload == "garbage_bytes":
        (tmp_path / "model.npz").write_bytes(b"PK\x03\x04 truncated")
    else:
        np.savez(tmp_path / "model.npz", **{k: np.array([{"x": 1}], dtype=object) for k in decoders.ARRAYS})
    with pytest.raises(IntegrityError):
        runs._adopt_orphans(tmp_path, model, pred)


def test_r4_valid_lone_npz_is_completed(model_and_ids, tmp_path):
    model, pred = model_and_ids
    (tmp_path / "model.npz").write_bytes(artifacts.model_npz_bytes(model))
    before = (tmp_path / "model.npz").read_bytes()
    runs._adopt_orphans(tmp_path, model, pred)
    rec = runs._existing_or_save_model(tmp_path, model)
    assert (tmp_path / "model.npz").read_bytes() == before and rec["model_identity"] == artifacts.model_identity(model)
    assert artifacts.load_model_verified(tmp_path, rec).lam == model.lam


def test_r4_lone_json_valid_is_completed_wrong_is_refused(model_and_ids, tmp_path):
    model, pred = model_and_ids
    artifacts.write_json_exclusive(tmp_path / "model.json", decoders._json_meta(model))
    runs._adopt_orphans(tmp_path, model, pred)
    rec = runs._existing_or_save_model(tmp_path, model)
    assert artifacts.load_model_verified(tmp_path, rec).lam == model.lam
    other = tmp_path / "other"
    other.mkdir()
    meta = decoders._json_meta(model)
    meta["n_val"] = 99
    (other / "model.json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(IntegrityError, match="orphan model in"):
        runs._adopt_orphans(other, model, pred)


def test_r4_end_to_end_crash_after_the_npz(reference, tmp_path):
    """Interrupted run whose last cell has only its model.npz (JSON and record lost): resume completes the
    cell from the verified NPZ and ends identical to the uninterrupted run."""
    rd = runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id="npzonly", **GRID)
    with pytest.raises(runs.Interrupted):
        runs.execute(rd, lock_root=tmp_path / "locks", stop_after=6)
    last = [e["cell"] for e in _events(rd) if e["event"] == "cell_completed"][-1]
    for name in ("record.json", "model.json", "predictions.npz"):
        (rd / "cells" / last / name).unlink()
    assert runs.execute(rd, lock_root=tmp_path / "locks") == "complete"
    assert _identities(rd) == _identities(reference)


# --- Nachreview 9b52d95 (Astra): N1 log framing, N2 one administration lock for recovery and normal starts --
_CHILD_TAIL = """
import os, sys, platform
from pathlib import Path
from experiments.lantern_reconstruction import runs
rd, root, tail = Path(sys.argv[1]), Path(sys.argv[2]), bytes.fromhex(sys.argv[3])
r = runs.load_run(rd)
lock = runs.StudyLock(root, r['grid']['study_id'], r['kind'], r['run_id']).__enter__()
log = runs.EventLog(rd / 'events.jsonl')
log.append('lock_acquired', lock=str(lock.path.resolve()), pid=os.getpid(), host=platform.node())
runs.set_status(log, 'running', 'synthetic recovery control')
with open(log.path, 'ab') as f:
    f.write(tail); f.flush(); os.fsync(f.fileno())
os._exit(0)
"""
_CONTENDER = """
import json, sys
from pathlib import Path
from experiments.lantern_reconstruction import runs
root, sid, phase = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
try:
    lock = runs.StudyLock(root, sid, phase, 'contender').__enter__()
except runs.LockError as e:
    print(json.dumps({'acquired': False, 'error': str(e)[:200]}), flush=True)
    sys.exit(0)
print(json.dumps({'acquired': True}), flush=True)
sys.stdin.readline()
lock.__exit__(None, None, None)
"""
_ENV = dict(os.environ, PYTHONPATH=str(REPO), PYTHONDONTWRITEBYTECODE="1")


def _small_run(tmp_path, name):
    return runs.create_run(tmp_path / "runs", "smoke", [0, 1], run_id=name, conditions=("lantern",), tasks=("A",),
                           sizes={"train": 2, "val": 2, "test": 2}, proposals=1)


def _dead_owner(tmp_path, name, tail):
    """A REAL child process takes the production StudyLock, logs lock_acquired + running, writes `tail`
    (fsync) and dies without releasing anything."""
    rd = _small_run(tmp_path, name)
    p = subprocess.run([sys.executable, "-c", _CHILD_TAIL, str(rd), str(tmp_path / "locks"), tail.hex()], env=_ENV, cwd=REPO, timeout=120)
    assert p.returncode == 0
    pid = [e for e in runs.EventLog(rd / "events.jsonl").read_tolerating_tail()[0] if e["event"] == "lock_acquired"][-1]["pid"]
    assert runs.process_alive(pid) is False
    return rd


@pytest.mark.parametrize("name, tail, kind", [
    ("valid_without_lf", b'{"event":"unit_completed"}', "unterminated_event"),
    ("valid_with_lf", b'{"event":"unit_completed"}\n', None),
    ("incomplete_object", b'{"event":"unit_', "incomplete"),
    ("cut_utf8", b'{"event":"unit_\xc3', "incomplete"),
    ("empty_tail", b"", None),
])
def test_n1_log_end_recovered_with_valid_events_kept(tmp_path, name, tail, kind):
    """Review 9b52d95 N1: a valid JSON object WITHOUT its LF was diagnosed clean; recovery appended the next
    event onto it -> unreadable line, TruncatedLogError, lock already gone. Syntax and framing are now judged
    separately; the valid event stays an event before and after the repair."""
    rd = _dead_owner(tmp_path, name, tail)
    log = runs.EventLog(rd / "events.jsonl")
    before = log.path.read_bytes()
    diag = runs._recovery_diagnosis(runs.load_run(rd), log)
    assert (diag["tail"] or {}).get("kind") == kind
    if kind == "unterminated_event":
        assert {"event": "unit_completed"} in log.read_tolerating_tail()[0]
        with pytest.raises(runs.TruncatedLogError):            # strict read demands the complete frame
            log.read()
    assert runs.recover(rd) == "interrupted"
    after = log.path.read_bytes()
    assert after.startswith(before) and after.endswith(b"\n")
    events = log.read()                                         # strict read works again
    assert runs.status(rd) == "interrupted"
    if tail.startswith(b'{"event":"unit_completed"}'):
        assert {"event": "unit_completed"} in events
    if kind == "unterminated_event":
        assert any(e["event"] == "log_line_terminated" and e["fragment_bytes"] == len(tail) for e in events)
    if kind == "incomplete":
        assert any(e["event"] == "log_line_truncated" and e["fragment_bytes"] == len(tail) for e in events)
    assert not any((tmp_path / "locks").glob("*"))              # neither the dead lock nor an admin lock is left


@pytest.mark.parametrize("owner", ["alive", "undecidable"])
def test_n1_unterminated_valid_event_with_live_or_unclear_owner_stays_byte_identical(tmp_path, monkeypatch, owner):
    rd, lock = _running_with_incomplete_line(tmp_path, f"n1-{owner}", os.getpid() if owner == "alive" else 99999999, platform.node())
    with open(rd / "events.jsonl", "ab") as f:                 # make the incomplete tail a complete event without LF
        f.write(b'completed"}')
    if owner == "undecidable":
        monkeypatch.setattr(runs, "process_alive", lambda p: None)
    log_before, lock_before = (rd / "events.jsonl").read_bytes(), lock.path.read_bytes()
    with pytest.raises(runs.ResumeRefused, match="may still be active"):
        runs.recover(rd)
    assert (rd / "events.jsonl").read_bytes() == log_before and lock.path.read_bytes() == lock_before


def _start_contender(lock_root, sid, phase):
    p = subprocess.Popen([sys.executable, "-c", _CONTENDER, str(lock_root), str(sid), phase], env=_ENV, cwd=REPO,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    line = p.stdout.readline()
    assert line, p.stderr.read()
    return p, json.loads(line)


def _finish(p):
    p.communicate("release\n", timeout=60)
    assert p.returncode == 0


@pytest.mark.parametrize("sync_point", ["after_stale_lock_removed", "right_before_new_acquisition"])
def test_n2_normal_start_cannot_interleave_with_recovery(tmp_path, monkeypatch, sync_point):
    """Review 9b52d95 N2: a normal StudyLock acquisition in a SECOND PROCESS, started inside recovery's
    critical section, got the study lock (the .recover guard was ignored); recovery then failed after its
    changes. Now both share the AdminLock: the contender is refused, recovery finishes, the start can
    follow afterwards."""
    rd = _dead_owner(tmp_path, f"n2-{sync_point}", b'{"event":"unit_')
    run = runs.load_run(rd)
    sid, phase, locks = run["grid"]["study_id"], run["kind"], tmp_path / "locks"
    seen, procs = [], []
    if sync_point == "after_stale_lock_removed":
        real_append = runs.EventLog.append

        def hook(self, event, **data):
            real_append(self, event, **data)
            if event == "stale_lock_removed":
                p, obs = _start_contender(locks, sid, phase)
                procs.append(p)
                seen.append(obs)
        monkeypatch.setattr(runs.EventLog, "append", hook)
    else:
        real_create = runs.StudyLock._create

        def hook(self):
            if self.admin is not None:                          # recovery's own acquisition, admin held
                p, obs = _start_contender(locks, sid, phase)
                procs.append(p)
                seen.append(obs)
            return real_create(self)
        monkeypatch.setattr(runs.StudyLock, "_create", hook)
    try:
        assert runs.recover(rd) == "interrupted"
    finally:
        for p in procs:
            _finish(p)
    assert seen and seen[0]["acquired"] is False and "administration" in seen[0]["error"]
    assert runs.status(rd) == "interrupted" and not any(locks.glob("*"))
    monkeypatch.undo()
    p, obs = _start_contender(locks, sid, phase)                # afterwards a normal start proceeds
    _finish(p)
    assert obs["acquired"] is True


def test_n2_normal_start_before_recovery_wins_and_recovery_changes_nothing(tmp_path, monkeypatch):
    """Sync point before the last diagnosis: a normal start (second process) takes the study lock first ->
    recovery's re-diagnosis under the admin lock refuses BEFORE any log change; the live lock is untouched."""
    rd = _dead_owner(tmp_path, "n2-start-first", b'{"event":"unit_')
    run = runs.load_run(rd)
    locks = tmp_path / "locks"
    lock_path = locks / f"study-{run['grid']['study_id']}-{run['kind']}.lock"
    lock_path.unlink()                                          # the dead lock was cleared by an operator ...
    real_diag, calls, procs = runs._recovery_diagnosis, [], []

    def diag(run_, log_):
        out = real_diag(run_, log_)
        calls.append(1)
        if len(calls) == 1:                                     # ... and a normal start wins before recovery's admin lock
            p, obs = _start_contender(locks, run["grid"]["study_id"], run["kind"])
            procs.append(p)
            assert obs["acquired"] is True
        return out
    monkeypatch.setattr(runs, "_recovery_diagnosis", diag)
    log_before = (rd / "events.jsonl").read_bytes()
    try:
        with pytest.raises(runs.ResumeRefused, match="changed|held by"):
            runs.recover(rd)
        assert (rd / "events.jsonl").read_bytes() == log_before
        assert json.loads(lock_path.read_text(encoding="utf-8"))["run_id"] == "contender"
    finally:
        for p in procs:
            _finish(p)


def test_n2_recovery_against_recovery_in_two_processes(tmp_path):
    """A second recovery (separate process) while the first holds the admin lock is refused without changes."""
    rd = _dead_owner(tmp_path, "n2-rr", b'{"event":"unit_')
    run = runs.load_run(rd)
    lock_path = tmp_path / "locks" / f"study-{run['grid']['study_id']}-{run['kind']}.lock"
    holder = subprocess.Popen([sys.executable, "-c",
                               "import sys; from pathlib import Path; from experiments.lantern_reconstruction import runs; "
                               "a = runs.AdminLock(Path(sys.argv[1]), 'recover other').__enter__(); print('held', flush=True); "
                               "sys.stdin.readline(); a.__exit__(None, None, None)", str(lock_path)],
                              env=_ENV, cwd=REPO, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert holder.stdout.readline().strip() == "held"
    log_before, lock_before = (rd / "events.jsonl").read_bytes(), lock_path.read_bytes()
    try:
        with pytest.raises(runs.ResumeRefused, match="administration"):
            runs.recover(rd)
        assert (rd / "events.jsonl").read_bytes() == log_before and lock_path.read_bytes() == lock_before
    finally:
        _finish(holder)
    assert runs.recover(rd) == "interrupted"                     # after the other one released


def test_n2_admin_lock_is_never_removed_by_someone_else(tmp_path):
    lock_path = tmp_path / "study-1-smoke.lock"
    a = runs.AdminLock(lock_path, "x").__enter__()
    other = runs.AdminLock(lock_path, "y")
    with pytest.raises(runs.LockError, match="administration"):
        other.__enter__()
    other.__exit__(None, None, None)                            # a non-holder never deletes it
    assert a.path.exists()
    with pytest.raises(runs.LockError, match="not held"):
        runs.StudyLock(tmp_path, 1, "smoke", "r", admin=other).__enter__()
    a.__exit__(None, None, None)
    assert not a.path.exists()
