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
            "software": {"python": platform.python_version(), "numpy": np.__version__}}, snap


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
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    if diffs:
        raise ResumeRefused(f"run {run['run_id']} cannot be resumed: changed {diffs} (a new study version needs a new run)")


def _record_path(run_dir: Path, c: Dict) -> Path:
    return Path(run_dir) / "cells" / cell_dir_name(c) / "record.json"


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
    cur = status(run_dir)
    if cur in TERMINAL or cur == "complete":
        raise ResumeRefused(f"run status is {cur}: nothing to resume, nothing is overwritten")
    check_resumable(run)
    grid = run["grid"]
    snap = ra.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    written = 0
    lock_root = Path(lock_root) if lock_root is not None else RESULTS / "runs" / "_locks"
    with StudyLock(lock_root, grid["study_id"], run["kind"], run["run_id"]):
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
        missing = [cell_dir_name(c) for c in expected_cells(grid) if not _record_path(run_dir, c).exists()]
        set_status(log, "incomplete" if missing else "complete", f"{len(missing)} cells missing" if missing else "all cells present")
    return status(run_dir)


def _persist_cell(run_dir: Path, run: Dict, ctx, c: Dict, model, X_test, U_test) -> Dict:
    """New cell: model, predictions, record (last), all exclusive. Existing record or orphan files: the
    recomputed cell must have the same model identity and prediction identities -- else integrity failure."""
    folder = Path(run_dir) / "cells" / cell_dir_name(c)
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
    if (folder / "model.json").exists() or (folder / "model.npz").exists() or (folder / "predictions.npz").exists():
        _adopt_orphans(folder, ident, pred_ids)
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


def _adopt_orphans(folder: Path, ident: str, pred_ids: Dict) -> None:
    """Files of an interrupted cell without record: they may only be adopted if they ARE the recomputed cell."""
    if (folder / "model.json").exists():
        meta = ra.strict_json((folder / "model.json").read_text(encoding="utf-8"))
        if artifacts.identity(meta) != ident:
            raise IntegrityError(f"orphan model in {folder.name} differs from the recomputed one")
        if (folder / "model.npz").exists():
            with np.load(folder / "model.npz", allow_pickle=False) as z:
                if any(decoders.array_identity(k, z[k]) != meta["arrays"][k] for k in decoders.ARRAYS):
                    raise IntegrityError(f"orphan model arrays in {folder.name} differ from the recomputed ones")
    if (folder / "predictions.npz").exists():
        with np.load(folder / "predictions.npz", allow_pickle=False) as z:
            if sorted(z.files) != sorted(pred_ids) or any(artifacts.array_identity(k, z[k]) != pred_ids[k] for k in z.files):
                raise IntegrityError(f"orphan predictions in {folder.name} differ from the recomputed ones")


def _existing_or_save_model(folder: Path, model) -> Dict:
    if (folder / "model.npz").exists() and (folder / "model.json").exists():
        meta = (folder / "model.json").read_bytes()
        return {"model_identity": artifacts.identity(json.loads(meta)), "npz": "model.npz",
                "npz_sha256": artifacts.sha256((folder / "model.npz").read_bytes()), "json": "model.json", "json_sha256": artifacts.sha256(meta)}
    if (folder / "model.npz").exists() or (folder / "model.json").exists():
        for name in ("model.npz", "model.json"):                     # half a model: keep it visible, never overwrite
            if (folder / name).exists():
                (folder / name).rename(folder / f"{name}.orphan-{uuid.uuid4().hex[:8]}")
    return artifacts.save_model_exclusive(model, folder, "model")


def _existing_or_save_arrays(folder: Path, arrays: Dict, pred_ids: Dict) -> Dict:
    if (folder / "predictions.npz").exists():
        return {"file": "predictions.npz", "sha256": artifacts.sha256((folder / "predictions.npz").read_bytes()), "arrays": pred_ids}
    return artifacts.save_arrays_exclusive(folder / "predictions.npz", **arrays)
