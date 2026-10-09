"""LR5 run management (plan sections 12, 13; review REVIEW_LR4 + LANTERN_LR4_NACHREVIEW LR5 duties).

A run is a folder with
  run.json      the run identity, written once and exclusively: kind, study, exact grid (contexts, conditions,
                controls, tasks, times), sizes, dt, surrogate proposals, code identity (SHA-256 of every
                production module and protocol file, LF-normalised; git commit/dirty for information), study
                configuration, registry snapshot pins, software;
  events.jsonl  append-only event log (fsync per line) with UTC and monotonic time; a gap between the two
                clocks is logged as a suspected sleep;
  cells/...     one folder per cell: model.npz/.json, predictions.npz and LAST record.json, each written
                exclusively and atomically (artifacts.write_exclusive) -- a cell exists only with its record;
  structure/    per context the deterministic reset / zero-impulse check (identical states for u and -u).

Status of a run: running -> complete | interrupted | incomplete | failed_integrity | numerically_invalid.
failed_integrity and numerically_invalid are terminal; no status is ever changed by a score.
Resume continues the SAME run id only if code, protocol, configuration, snapshot and grid are unchanged;
every recomputed cell is compared with an existing record or orphan files (identity, never bytes of the ZIP
container); a mismatch is an integrity failure and nothing is overwritten.

Study lifecycle (plan 12): development -> smoke_passed -> code_protocol_frozen -> trained -> model_frozen ->
evaluated -> reviewed. This module runs only 'development' and 'smoke' runs on the development study; a
research run needs the frozen protocol of LR6 and is refused."""
from __future__ import annotations

import datetime as dtm
import json
import os
import platform
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

from experiments.lantern_reconstruction import artifacts, contexts, decoders, episodes, runner, streams
from experiments.lantern_reconstruction import registry_adapter as ra
from experiments.lantern_reconstruction.artifacts import IntegrityError

HERE = streams.HERE
RESULTS = Path("D:/mandala/mandala-memory-results/lantern")
RUN_SCHEMA = "lantern-run-v1"
RECORD_SCHEMA = "lantern-cell-record-v1"
KINDS = ("development", "smoke")
LIFECYCLE = ("development", "smoke_passed", "code_protocol_frozen", "trained", "model_frozen", "evaluated", "reviewed")
RUN_STATES = ("running", "complete", "interrupted", "incomplete", "failed_integrity", "numerically_invalid")
TERMINAL = ("failed_integrity", "numerically_invalid")
TRANSITIONS = {"running": {"complete", "interrupted", "incomplete", "failed_integrity", "numerically_invalid"},
               "interrupted": {"running", "failed_integrity"}, "incomplete": {"running", "failed_integrity"},
               "complete": {"failed_integrity"}, "failed_integrity": set(), "numerically_invalid": set()}
CONTROL_CONDITION = "lantern"
CLOCK_GAP_SECONDS = 60.0


class LockError(RuntimeError):
    pass


class ResumeRefused(RuntimeError):
    pass


class Interrupted(RuntimeError):
    pass


class TruncatedLogError(RuntimeError):
    pass


def process_alive(pid: int):
    """True / False if decidable, None if not (then a recovery must refuse). A reused PID reads as alive:
    the conservative error is refusing a recovery, never overlapping two processes."""
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    if pid == os.getpid():
        return True
    if platform.system() == "Windows":
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        h = k32.OpenProcess(0x1000, False, pid)                     # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            err = ctypes.get_last_error()
            return False if err == 87 else (True if err == 5 else None)   # 87 no such process, 5 access denied
        try:
            code = ctypes.c_ulong()
            k32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
            if not k32.GetExitCodeProcess(ctypes.c_void_p(h), ctypes.byref(code)):
                return None
            return code.value == 259                                 # STILL_ACTIVE
        finally:
            k32.CloseHandle.argtypes = [ctypes.c_void_p]
            k32.CloseHandle(ctypes.c_void_p(h))
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return None
    return True


# --- identity ------------------------------------------------------------------------------------------
def code_identity() -> Dict:
    """SHA-256 (LF-normalised) of every production module and protocol file of the lab; tests excluded."""
    files = sorted([p for p in HERE.glob("*.py")] + [p for p in (HERE / "protocol").glob("*") if p.suffix in (".json", ".yaml", ".md")])
    hashes = {p.relative_to(HERE).as_posix(): artifacts.sha256(p.read_bytes().replace(b"\r\n", b"\n")) for p in files}
    git = {}
    try:
        repo = HERE.parents[1]
        git["commit"] = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        git["dirty"] = bool(subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", "experiments/lantern_reconstruction"],
                                           capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        git = {"commit": None, "dirty": None}
    return {"files": hashes, "identity": artifacts.identity(hashes), "git": git}


def _grid(kind, contexts_, conditions, tasks, sizes, dt, proposals) -> Dict:
    d = streams.defaults()
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS} (research runs need the LR6 freeze)")
    cids = list(contexts_)
    if not cids or len(set(cids)) != len(cids) or not all(isinstance(c, int) and not isinstance(c, bool) and c >= 0 for c in cids):
        raise ValueError("contexts must be distinct non-negative integers")
    sizes = runner.check_selection(sizes, conditions, tasks, "none")
    if CONTROL_CONDITION not in conditions:
        raise ValueError("the control curves run on the lantern condition: it must be part of the grid")
    return {"study_id": d["development_study_id"], "contexts": sorted(cids), "conditions": list(conditions),
            "controls": ["reset", "zero_impulse", "permuted_targets"], "tasks": list(tasks),
            "times": [float(t) for t in d["time_grid"]], "sizes": sizes,
            "dt": d["integration"]["dt"] if dt is None else float(dt),
            "proposals": d["strength_surrogate"]["proposals"] if proposals is None else proposals}


def expected_cells(grid: Dict) -> list:
    """Every cell of the exact grid: main cells (all conditions, control 'none') and the control curves."""
    cells = []
    for cid in grid["contexts"]:
        units = [(cond, "none") for cond in grid["conditions"]] + [(CONTROL_CONDITION, c) for c in grid["controls"]]
        for cond, ctl in units:
            for task in grid["tasks"]:
                for k, tau in enumerate(grid["times"]):
                    cells.append({"context_id": cid, "condition": cond, "control": ctl, "task": task, "time": tau, "time_index": k})
    return cells


def cell_dir_name(c: Dict) -> str:
    return f"c{c['context_id']:03d}__{c['condition']}__{c['control']}__{c['task']}__t{c['time_index']}"


def _identity_payload(run: Dict) -> Dict:
    return {k: run[k] for k in ("schema", "kind", "grid", "code", "config_sha256", "snapshot", "software")}


def run_identity(run: Dict) -> str:
    """Over kind, grid, the FULL code block (every file hash), configuration, snapshot and software, plus run id."""
    return artifacts.identity(_identity_payload(run) | {"run_id": run["run_id"]})


def _current(grid: Dict, kind: str) -> Dict:
    snap = ra.load_verified_snapshot()
    code = code_identity()
    return {"schema": RUN_SCHEMA, "kind": kind, "grid": grid, "code": code, "config_sha256": streams.config_sha256(),
            "snapshot": {"canonical_sha256": snap.canonical_sha256, "manifest_sha256": snap.manifest_sha256},
            "software": software()}, snap


def software() -> Dict:
    """The numerical environment a run is bound to; resume demands it unchanged (review REVIEW_LR5 R3)."""
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}


# --- event log, status, lock ----------------------------------------------------------------------------
class EventLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._last = None

    def append(self, event: str, **data) -> None:
        now_wall, now_mono = time.time(), time.monotonic()
        rec = {"utc": dtm.datetime.now(dtm.timezone.utc).isoformat(), "monotonic": now_mono, "event": event, **data}
        if self._last is not None:
            gap = (now_wall - self._last[0]) - (now_mono - self._last[1])
            if gap > CLOCK_GAP_SECONDS:
                self._write({"utc": rec["utc"], "monotonic": now_mono, "event": "clock_gap", "seconds": gap,
                             "note": "wall clock advanced more than the monotonic clock: suspected sleep"})
        self._last = (now_wall, now_mono)
        self._write(rec)

    def _write(self, rec) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def read(self) -> list:
        """Strict: an unparsable line is only tolerated if the NEXT line is the 'log_line_truncated' event that
        recover() appends after a process loss; an unacknowledged broken line raises TruncatedLogError."""
        if not self.path.exists():
            return []
        events, broken = [], None
        for i, line in enumerate(self.path.read_bytes().split(b"\n")):
            if not line.strip():
                continue
            try:
                e = json.loads(line.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                if broken is not None:
                    raise IntegrityError(f"{self.path}: two unparsable event lines") from None
                broken = i
                continue
            if broken is not None:
                if e.get("event") != "log_line_truncated":
                    raise IntegrityError(f"{self.path}: unparsable event line {broken + 1} without a recorded truncation")
                broken = None
            events.append(e)
        if broken is not None:
            raise TruncatedLogError(f"{self.path}: the last event line is incomplete (process loss?); use runs.recover()")
        return events

    def acknowledge_truncation(self):
        """Append-only repair after a process loss: terminate an incomplete last line with a newline and record
        its bytes (SHA-256, length) in a 'log_line_truncated' event. Nothing is rewritten or removed."""
        if not self.path.exists():
            return None
        raw = self.path.read_bytes()
        last = raw.rstrip(b"\n").split(b"\n")[-1] if raw.strip() else b""
        try:
            json.loads(last.decode("utf-8"))
            if raw.endswith(b"\n") or not raw:
                return None
        except (ValueError, UnicodeDecodeError):
            pass
        with open(self.path, "ab") as f:
            if not raw.endswith(b"\n"):
                f.write(b"\n")
            f.flush()
            os.fsync(f.fileno())
        info = {"fragment_sha256": artifacts.sha256(last), "fragment_bytes": len(last)}
        self._write({"utc": dtm.datetime.now(dtm.timezone.utc).isoformat(), "monotonic": time.monotonic(),
                     "event": "log_line_truncated", **info})
        return info


def status(run_dir: Path) -> Optional[str]:
    st = [e["to"] for e in EventLog(Path(run_dir) / "events.jsonl").read() if e["event"] == "status"]
    return st[-1] if st else None


def set_status(log: EventLog, new: str, reason: str) -> None:
    cur = [e["to"] for e in log.read() if e["event"] == "status"]
    cur = cur[-1] if cur else None
    if new not in RUN_STATES or (cur is not None and new not in TRANSITIONS[cur]):
        raise ValueError(f"status transition {cur} -> {new} is not allowed")
    log.append("status", to=new, reason=reason, **({} if cur is None else {"from": cur}))


class StudyLock:
    """One exclusive lock per (study, phase), independent of the run folder."""

    def __init__(self, lock_root: Path, study_id: int, phase: str, run_id: str):
        self.path = Path(lock_root) / f"study-{study_id}-{phase}.lock"
        self.run_id = run_id

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise LockError(f"{self.path} is held ({self.path.read_text(encoding='utf-8', errors='replace')}); "
                            "remove it manually only after checking that no run is active") from None
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": self.run_id, "pid": os.getpid(), "utc": dtm.datetime.now(dtm.timezone.utc).isoformat()}))
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)
        return False


# --- the run ----------------------------------------------------------------------------------------------
def create_run(runs_root: Path, kind: str, contexts_: Sequence[int], *, conditions: Sequence[str] = episodes.CONDITIONS,
               tasks: Sequence[str] = runner.TASKS, sizes: Optional[Dict] = None, dt: Optional[float] = None,
               proposals: Optional[int] = None, run_id: Optional[str] = None) -> Path:
    grid = _grid(kind, contexts_, conditions, tasks, sizes, dt, proposals)
    run, _ = _current(grid, kind)
    run_id = run_id or f"{kind}-{dtm.datetime.now(dtm.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    run_dir = Path(runs_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    run.update(run_id=run_id, created_utc=dtm.datetime.now(dtm.timezone.utc).isoformat())
    run["run_identity"] = run_identity(run)
    artifacts.write_json_exclusive(run_dir / "run.json", run)
    (run_dir / "cells").mkdir()
    (run_dir / "structure").mkdir()
    EventLog(run_dir / "events.jsonl").append("run_created", run_id=run_id, run_identity=run["run_identity"])
    return run_dir


def load_run(run_dir: Path) -> Dict:
    run = ra.strict_json((Path(run_dir) / "run.json").read_text(encoding="utf-8"))
    if run.get("schema") != RUN_SCHEMA or run_identity(run) != run.get("run_identity"):
        raise IntegrityError("run.json does not match its own run identity")
    return run


def check_resumable(run: Dict) -> None:
    """Resume only the SAME experiment: code, protocol, configuration, snapshot, software line and grid unchanged."""
    cur, _ = _current(run["grid"], run["kind"])
    diffs = [k for k in ("config_sha256", "snapshot", "grid") if cur[k] != run[k]]
    if cur["code"]["identity"] != run["code"]["identity"]:
        changed = sorted(k for k in set(cur["code"]["files"]) | set(run["code"]["files"])
                         if cur["code"]["files"].get(k) != run["code"]["files"].get(k))
        diffs.append(f"code {changed}")
    if cur["software"] != run["software"]:                 # strict equality, no compatibility rule (REVIEW_LR5 R3)
        diffs.append(f"software {run['software']} -> {cur['software']}")
    if diffs:
        raise ResumeRefused(f"run {run['run_id']} cannot be resumed: changed {diffs} (a new study version needs a new run)")


def _record_path(run_dir: Path, c: Dict) -> Path:
    return Path(run_dir) / "cells" / cell_dir_name(c) / "record.json"


def check_model_against_run(model, run: Dict, where: str) -> None:
    """Expected model parameters come from the RUN and the protocol, not from the model's own manifest
    (review REVIEW_LR5 R2): training/validation sizes, the lambda grid and the numerical environment."""
    from experiments.lantern_reconstruction import training

    sizes, sw = run["grid"]["sizes"], run["software"]
    wrong = {}
    if (model.n_train, model.n_val) != (sizes["train"], sizes["val"]):
        wrong["sizes"] = {"model": [model.n_train, model.n_val], "run": [sizes["train"], sizes["val"]]}
    if tuple(model.lambda_grid.tolist()) != training.LAMBDA_GRID:
        wrong["lambda_grid"] = model.lambda_grid.tolist()
    if (model.software.get("python"), model.software.get("numpy")) != (sw["python"], sw["numpy"]):
        wrong["software"] = dict(model.software)
    if wrong:
        raise IntegrityError(f"model of {where} does not match the run's expected parameters: {wrong}")


def verify_record(run_dir: Path, run: Dict, c: Dict, ctx) -> Dict:
    """A cell record against the run identity, the expected cell and every file it names."""
    folder = _record_path(run_dir, c).parent
    rec = ra.strict_json((folder / "record.json").read_text(encoding="utf-8"))
    expected_cell = {"study_id": run["grid"]["study_id"], "context_id": c["context_id"], "context_fingerprint": contexts.fingerprint(ctx),
                     "condition": c["condition"], "control": c["control"], "task": c["task"], "time": c["time"],
                     "time_index": c["time_index"], "dt": run["grid"]["dt"]}
    if rec.get("schema") != RECORD_SCHEMA or rec.get("run_identity") != run["run_identity"] or rec.get("cell") != expected_cell:
        raise IntegrityError(f"record of {cell_dir_name(c)} does not belong to this run and cell")
    model = artifacts.load_model_verified(folder, rec["model"], ctx, c["task"], condition=c["condition"], time=c["time"],
                                          control=c["control"], dt=run["grid"]["dt"])
    check_model_against_run(model, run, cell_dir_name(c))
    arr = artifacts.load_arrays_verified(folder, rec["predictions"])
    n = run["grid"]["sizes"]["test"]
    if arr["projected"].shape != (n, 4) or arr["targets"].shape != (n, 4) or not all(np.all(np.isfinite(a)) for a in arr.values()):
        raise IntegrityError(f"predictions of {cell_dir_name(c)} have the wrong sample count or are not finite")
    # the scores are not trusted as written: they must follow EXACTLY from the verified predictions and model
    from experiments.lantern_reconstruction import metrics
    sc = metrics.scores(*metrics.episode_losses(arr["projected"], arr["targets"]))
    if not np.array_equal(arr["projected"], metrics.project(arr["raw"])) or \
            (sc["G"], sc["S"], sc["n_episodes"], model.lam) != (rec["scores"]["G"], rec["scores"]["S"], rec["scores"]["n_episodes"], rec["scores"]["lambda"]):
        raise IntegrityError(f"scores of {cell_dir_name(c)} do not follow from its verified predictions and model")
    return rec


def _structure_check(ctx, C, g, sizes) -> Dict:
    """Deterministic plan-10 gate per context: reset and zero impulse give EXACTLY the same states for u and
    -u at all grid times (same phi and eps), on the first test episodes with the lantern matrix."""
    b = episodes.make_batch(ctx, "test", range(min(8, sizes["test"])))
    from dataclasses import replace
    out = {}
    for control in ("reset", "zero_impulse"):
        s1 = episodes.simulate(ctx, b, C, g, control)
        s2 = episodes.simulate(ctx, replace(b, u=-b.u), C, g, control)
        out[control] = bool(np.array_equal(s1, s2))
    return {"context_id": ctx.context_id, "episodes": int(b.u.shape[0]), "checks": out, "passed": all(out.values())}


def execute(run_dir: Path, *, lock_root: Optional[Path] = None, stop_after: Optional[int] = None) -> str:
    """Run or resume. stop_after=N raises an interruption after N newly written cells (tests of resume)."""
    run_dir = Path(run_dir)
    run = load_run(run_dir)
    log = EventLog(run_dir / "events.jsonl")
    cur = status(run_dir)                                   # TruncatedLogError after a process loss -> recover()
    if cur in TERMINAL or cur == "complete":
        raise ResumeRefused(f"run status is {cur}: nothing to resume, nothing is overwritten")
    if cur == "running":
        raise ResumeRefused("run status is running: another process may still be active, or one was lost; "
                            "runs.recover() checks that and makes the run resumable")
    check_resumable(run)
    grid = run["grid"]
    snap = ra.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    written = 0
    lock_root = Path(lock_root) if lock_root is not None else RESULTS / "runs" / "_locks"
    with StudyLock(lock_root, grid["study_id"], run["kind"], run["run_id"]) as lock:
        log.append("lock_acquired", lock=str(lock.path.resolve()), pid=os.getpid(), host=platform.node())
        set_status(log, "running", "start" if cur is None else f"resume from {cur}")
        try:
            for cid in grid["contexts"]:
                ctx = contexts.make_context(grid["study_id"], cid)
                sp = run_dir / "structure" / f"c{cid:03d}.json"
                if not sp.exists():
                    artifacts.write_json_exclusive(sp, {"run_identity": run["run_identity"], **_structure_check(ctx, C, g, grid["sizes"])})
                prep, state_cache = None, {}
                units =[(cond, "none") for cond in grid["conditions"]] + [(CONTROL_CONDITION, c) for c in grid["controls"]]
                for cond, ctl in units:
                    todo = [c for c in expected_cells(grid) if c["context_id"] == cid and c["condition"] == cond and c["control"] == ctl]
                    done = [c for c in todo if _record_path(run_dir, c).exists()]
                    for c in done:
                        verify_record(run_dir, run, c, ctx)
                    if len(done) == len(todo):
                        continue
                    if prep is None:
                        prep = runner.prepare_context(ctx, C, grid["sizes"], grid["proposals"])
                    log.append("unit_started", context_id=cid, condition=cond, control=ctl)

                    def scorer(model, cell, X_test, U_test, cid=cid, ctx=ctx):
                        c = {"context_id": cid, "condition": cell["condition"], "control": cell["control"], "task": cell["task"],
                             "time": cell["time"], "time_index": cell["time_index"]}
                        return _persist_cell(run_dir, run, ctx, c, model, X_test, U_test)

                    for res in runner.iter_cells(ctx, prep, g, cond, ctl, grid["tasks"], None if grid["dt"] == streams.defaults()["integration"]["dt"] else grid["dt"],
                                               scorer=scorer, state_cache=state_cache):
                        if res["result"].get("newly_written"):
                            written += 1
                            log.append("cell_completed", cell=res["result"]["cell_dir"])
                            if stop_after is not None and written >= stop_after:
                                raise Interrupted(f"stopped after {written} new cells (test hook)")
                    log.append("unit_completed", context_id=cid, condition=cond, control=ctl)
        except IntegrityError as e:
            set_status(log, "failed_integrity", str(e))
            raise
        except (Interrupted, KeyboardInterrupt) as e:
            set_status(log, "interrupted", str(e) or type(e).__name__)
            raise
        except FloatingPointError as e:
            set_status(log, "numerically_invalid", str(e))
            raise
        except Exception as e:                              # any other failure: a defined, resumable state
            set_status(log, "interrupted", f"unexpected {type(e).__name__}: {e}")
            raise
        missing =[cell_dir_name(c) for c in expected_cells(grid) if not _record_path(run_dir, c).exists()]
        set_status(log, "incomplete" if missing else "complete", f"{len(missing)} cells missing" if missing else "all cells present")
    return status(run_dir)


def recover(run_dir: Path) -> str:
    """Explicit recovery after a process loss (review REVIEW_LR5 R1). Only for a run left in status 'running':
      1. an incomplete last event line is terminated and recorded (append-only, nothing rewritten);
      2. the process that held the run is identified from the run's own 'lock_acquired' event (lock path, pid,
         host) -- recovery refuses if that host is another machine, the pid may still be alive or its state is
         undecidable, or the lock now belongs to someone else;
      3. a stale lock of THAT process is removed and its content logged;
      4. under the study lock the status becomes 'interrupted'; execute() then resumes the same run identity
         with all artifacts kept (every existing cell re-verified, orphans checked)."""
    run_dir = Path(run_dir)
    run = load_run(run_dir)
    log = EventLog(run_dir / "events.jsonl")
    truncated = log.acknowledge_truncation()
    cur = status(run_dir)
    if cur in TERMINAL or cur == "complete":
        raise ResumeRefused(f"run status is {cur}: nothing to recover")
    events = log.read()
    acquired = [e for e in events if e["event"] == "lock_acquired"]
    if not acquired:
        if cur == "running":
            raise ResumeRefused("status running but no lock_acquired event: the holding process cannot be identified")
        raise ResumeRefused(f"nothing to recover (status {cur}, no lock was ever taken)")
    last = acquired[-1]
    stale_lock = Path(last["lock"]).exists()
    released_after = any(e["event"] == "status" and e["to"] != "running" for e in events[events.index(last) + 1:])
    if cur != "running" and (released_after or not stale_lock):
        raise ResumeRefused(f"nothing to recover (status {cur}, no stale lock of this run)")
    if last.get("host") != platform.node():
        raise ResumeRefused(f"the run was held on host {last.get('host')!r}: its process cannot be checked from here")
    alive = process_alive(last.get("pid"))
    if alive is not False:
        raise ResumeRefused(f"process {last.get('pid')} may still be active (alive={alive}); not recovered")
    lock_path = Path(last["lock"])
    if lock_path.exists():
        try:
            held = json.loads(lock_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            raise ResumeRefused(f"{lock_path} is unreadable; check it manually") from None
        if held.get("run_id") != run["run_id"] or held.get("pid") != last.get("pid"):
            raise ResumeRefused(f"{lock_path} is now held by {held}; not recovered")
        lock_path.unlink()
        log.append("stale_lock_removed", lock=str(lock_path), content=held)
    with StudyLock(lock_path.parent, run["grid"]["study_id"], run["kind"], run["run_id"]) as lock:
        if lock.path.resolve() != lock_path.resolve():
            raise ResumeRefused("lock path of the run does not match the study lock")
        reason = f"recovered after process loss of pid {last.get('pid')}" + (f"; truncated event line {truncated}" if truncated else "")
        if cur == "running":
            set_status(log, "interrupted", reason)
        else:
            log.append("recovered", reason=reason + f"; status stays {cur} (lost before it became running)")
    return status(run_dir)


def _persist_cell(run_dir: Path, run: Dict, ctx, c: Dict, model, X_test, U_test) -> Dict:
    """New cell: model, predictions, record (last), all exclusive. Existing record or orphan files: the
    recomputed cell must have the same model identity and prediction identities -- else integrity failure."""
    folder = Path(run_dir) / "cells" / cell_dir_name(c)
    check_model_against_run(model, run, cell_dir_name(c))           # also before anything is written
    ident = artifacts.model_identity(model)
    res = artifacts.evaluate_with_integrity(model, ident, X_test, U_test)
    arrays = {"projected": res["projected"], "raw": res["raw"], "targets": np.asarray(U_test, dtype=np.float64)}
    pred_ids = {k: artifacts.array_identity(k, v) for k, v in arrays.items()}
    rec_path = folder / "record.json"
    if rec_path.exists():
        rec = ra.strict_json(rec_path.read_text(encoding="utf-8"))
        if rec["model"]["model_identity"] != ident or rec["predictions"]["arrays"] != pred_ids:
            raise IntegrityError(f"recomputed {cell_dir_name(c)} differs from its record (changed model, seed or code?)")
        return {**res, "cell_dir": folder.name, "newly_written": False}
    folder.mkdir(parents=True, exist_ok=True)
    _adopt_orphans(folder, model, pred_ids)
    model_rec = _existing_or_save_model(folder, model)
    pred_rec = _existing_or_save_arrays(folder, arrays, pred_ids)
    record = {"schema": RECORD_SCHEMA, "run_identity": run["run_identity"],
              "cell": {"study_id": run["grid"]["study_id"], "context_id": c["context_id"], "context_fingerprint": contexts.fingerprint(ctx),
                       "condition": c["condition"], "control": c["control"], "task": c["task"], "time": c["time"],
                       "time_index": c["time_index"], "dt": run["grid"]["dt"]},
              "model": model_rec, "predictions": pred_rec,
              "scores": {"G": res["G"], "S": res["S"], "n_episodes": res["n_episodes"], "lambda": model.lam,
                         "n_raw_outside_unit_box": res["n_raw_outside_unit_box"]},
              "integrity": {"model_identity_checked_before_and_after_evaluation": True}}
    artifacts.write_json_exclusive(rec_path, record)
    return {**res, "cell_dir": folder.name, "newly_written": True}


def _npz_identities(path: Path, where: str) -> Dict[str, str]:
    try:
        with np.load(path, allow_pickle=False) as z:
            out = {}
            for k in z.files:
                a = z[k]
                if a.dtype != np.float64:
                    raise IntegrityError(f"{where}: array {k!r} is {a.dtype}, not float64")
                out[k] = artifacts.array_identity(k, a)
            return out
    except IntegrityError:
        raise
    except Exception as e:                                       # unreadable / not an NPZ / needs pickle
        raise IntegrityError(f"{where}: unreadable NPZ ({type(e).__name__}: {e})") from None


def _adopt_orphans(folder: Path, model, pred_ids: Dict) -> None:
    """Files of an interrupted cell without record may only be adopted if they ARE the recomputed cell, EACH
    file on its own (review REVIEW_LR5 R4: an NPZ without JSON is compared too). Any deviation is an
    integrity failure; nothing is renamed, replaced or overwritten."""
    expected = decoders._json_meta(model)
    if (folder / "model.json").exists():
        try:
            meta = ra.strict_json((folder / "model.json").read_text(encoding="utf-8"))
        except Exception as e:                                   # noqa: BLE001
            raise IntegrityError(f"orphan model.json in {folder.name} is unreadable ({e})") from None
        if artifacts.identity(meta) != artifacts.identity(expected):
            raise IntegrityError(f"orphan model in {folder.name} differs from the recomputed one")
    if (folder / "model.npz").exists():
        if _npz_identities(folder / "model.npz", f"orphan model.npz in {folder.name}") != expected["arrays"]:
            raise IntegrityError(f"orphan model arrays in {folder.name} differ from the recomputed ones")
    if (folder / "predictions.npz").exists():
        if _npz_identities(folder / "predictions.npz", f"orphan predictions in {folder.name}") != pred_ids:
            raise IntegrityError(f"orphan predictions in {folder.name} differ from the recomputed ones")


def _existing_or_save_model(folder: Path, model) -> Dict:
    """After _adopt_orphans verified any existing half: write only the MISSING part (exclusively)."""
    if not (folder / "model.npz").exists():
        artifacts.write_exclusive(folder / "model.npz", artifacts.model_npz_bytes(model))
    if not (folder / "model.json").exists():
        artifacts.write_json_exclusive(folder / "model.json", decoders._json_meta(model))
    meta = (folder / "model.json").read_bytes()
    return {"model_identity": artifacts.identity(json.loads(meta)), "npz": "model.npz",
            "npz_sha256": artifacts.sha256((folder / "model.npz").read_bytes()), "json": "model.json", "json_sha256": artifacts.sha256(meta)}


def _existing_or_save_arrays(folder: Path, arrays: Dict, pred_ids: Dict) -> Dict:
    if (folder / "predictions.npz").exists():
        return {"file": "predictions.npz", "sha256": artifacts.sha256((folder / "predictions.npz").read_bytes()), "arrays": pred_ids}
    return artifacts.save_arrays_exclusive(folder / "predictions.npz", **arrays)
