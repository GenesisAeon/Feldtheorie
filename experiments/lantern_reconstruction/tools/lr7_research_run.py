"""LR7 research run -- the ONLY start path (runs.create_research_run + runs.execute + release report), subject to the
separate pre-start review. Without --start it is a DRY RUN: readiness and plan are printed, nothing is created or run.

    python experiments/lantern_reconstruction/tools/lr7_research_run.py                    # dry run (default)
    python experiments/lantern_reconstruction/tools/lr7_research_run.py --start --confirm-study <research study id>
    python experiments/lantern_reconstruction/tools/lr7_research_run.py --resume <run dir> [--confirm-study <id>]

--resume continues an interrupted/incomplete research run (after runs.recover() if a process was lost) OR finishes a
run whose computation is complete but whose release report is missing (report only, no new computation), see
BETRIEB.md. Before ANY effect the target is checked (pre-start review LR7-F2): valid freeze, intact manifest, kind
'research', the frozen study and grid, unchanged code/software binding, and a given --confirm-study must match.

Every parameter comes from the frozen candidate (protocol/freeze.json -> lr6/freeze_candidate.json); create_research_run
takes none. The run is bound to the frozen code and the EXACT frozen software (refused otherwise). Operating window: at
least 2.5 h (freeze decision); the runtime estimate is no guarantee. The 20 contexts are fixed: a runtime problem is
resumed by protocol or reported openly, never answered by dropping contexts. Nothing is ever deleted or overwritten.
Prevents system sleep for this process only."""
from __future__ import annotations

import argparse
import ctypes
import datetime as dtm
import json
import platform
import sys
import time
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import registry_adapter as ra  # noqa: E402
from experiments.lantern_reconstruction import release, runs  # noqa: E402

RUNS_ROOT = runs.RESULTS / "runs"
REPORT_NAME = "release_report.json"


def keep_awake(on: bool) -> None:
    if platform.system() == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if on else 0))


def plan() -> dict:
    ready = runs.research_readiness()
    out = {"readiness": ready}
    if ready["research_start_allowed"]:
        cand = runs.frozen_candidate()
        g = runs.research_grid(cand)
        b = cand["budget"]
        out["plan"] = {"research_study_id": g["study_id"], "contexts": g["contexts"], "cells": len(runs.expected_cells(g)),
                       "runs_root": str(RUNS_ROOT), "software": cand["software"],
                       "extrapolated_execute_s": b["extrapolated_research"]["execute_seconds"],
                       "extrapolated_release_s": b["extrapolated_research"]["release_seconds"],
                       "operating_window_s": b["operating_window"]["recommended_s"],
                       "note": "linear extrapolation, no guarantee; plan at least 2.5 h"}
    return out


def frozen_research_grid() -> dict:
    """The research grid of the valid freeze; any freeze/candidate/software problem refuses (exit, no effect)."""
    try:
        return runs.research_grid(runs.frozen_candidate())
    except ValueError as e:
        raise SystemExit(f"research tool refused: {e}") from None


def verify_target(rd: Path, confirm: Optional[int] = None) -> dict:
    """Pre-start review LR7-F2: before ANY effect (no keep_awake, no event, no execution, no report) the target must be
    a research run of the frozen study. Order: freeze (frozen_candidate), manifest integrity (load_run), kind, study
    and the whole grid against research_grid(candidate), code/snapshot/software binding (check_resumable), and an
    explicitly given --confirm-study must equal the frozen study -- a wrong value is never ignored."""
    grid = frozen_research_grid()
    sid = grid["study_id"]
    if confirm is not None and confirm != sid:
        raise SystemExit(f"--confirm-study {confirm} is not the frozen research study id {sid}")
    try:
        run = runs.load_run(rd)
    except Exception as e:                                  # noqa: BLE001 -- unreadable or edited manifest: refuse
        raise SystemExit(f"research tool refused: {rd} is not an intact run ({type(e).__name__}: {e})") from None
    if run.get("kind") != "research":
        raise SystemExit(f"research tool refused: {rd} is a {run.get('kind')!r} run, not a research run")
    if run["grid"].get("study_id") != sid:
        raise SystemExit(f"research tool refused: {rd} belongs to study {run['grid'].get('study_id')}, not {sid}")
    if run["grid"] != grid:
        raise SystemExit(f"research tool refused: the grid of {rd} differs from the frozen research grid")
    try:
        runs.check_resumable(run)
    except runs.ResumeRefused as e:
        raise SystemExit(f"research tool refused: {e}") from None
    return run


def existing_research_runs(root: Path, grid: dict) -> list:
    """Run folders under root whose manifest is a research run of this grid -- or cannot be read (fail closed).
    Pre-start review section 6: a second first start of the same study is refused. NOT atomic (two concurrent
    calls could both pass); concurrent execution is still excluded by the existing StudyLock."""
    found = []
    if not Path(root).exists():
        return found
    for p in sorted(Path(root).iterdir()):
        if not (p / "run.json").exists():
            continue
        try:
            run = runs.load_run(p)
        except Exception as e:                              # noqa: BLE001 -- an unreadable manifest is not ignored
            found.append({"run_dir": str(p), "status": f"unreadable manifest ({type(e).__name__})"})
            continue
        if run.get("kind") == "research" and run["grid"] == grid:
            try:
                st = runs.status(p)
            except Exception as e:                          # noqa: BLE001
                st = f"unreadable log ({type(e).__name__})"
            found.append({"run_dir": str(p), "status": st,
                          "release_report": (p / REPORT_NAME).exists()})
    return found


def _summary(rd: Path, status: str, rep: dict, timings: dict, mode: str) -> int:
    events = runs.EventLog(rd / "events.jsonl").read()
    out = {"run_dir": str(rd), "mode": mode, "status": status, **timings, "n_cells": rep.get("n_verified_cells"),
           "clock_gaps": [e for e in events if e["event"] == "clock_gap"],
           "technically_complete": rep["technically_complete"], "scientifically_interpretable": rep["scientifically_interpretable"],
           "scientific_blocks": rep.get("scientific_blocks"),
           "results": f"{REPORT_NAME} in the run folder (hypothesis section evaluated only for an interpretable research run)"}
    print(json.dumps(out, indent=1), flush=True)
    return 0 if status == "complete" and rep["technically_complete"] else 1


def check_existing_report(rd: Path) -> int:
    """'complete' with a report: no overwrite and no new computation. The stored report is compared with a read-only
    recomputation (release_report has no time stamps); on any difference the tool stops and keeps the file."""
    path = rd / REPORT_NAME
    stored = json.loads(path.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(release.release_report(rd)))
    if json.dumps(stored, sort_keys=True) != json.dumps(fresh, sort_keys=True):
        raise SystemExit(f"the stored {REPORT_NAME} of {rd} differs from a read-only recomputation: file kept, stop "
                         "(no overwrite; inspect manually)")
    return _summary(rd, "complete", stored, {}, "report_verified")


def run(rd: Path, confirm: Optional[int] = None) -> int:
    """Pre-start review LR7-F1: the state decides the action (BETRIEB.md):
    new / interrupted / incomplete -> execute, then report;  running -> refuse, use runs.recover();
    complete without report -> report only (no execute, no training);  complete with report -> verify, never overwrite;
    failed_integrity / numerically_invalid -> refuse, no automatic replacement run."""
    rd = Path(rd)
    verify_target(rd, confirm)
    try:
        st = runs.status(rd)
    except runs.TruncatedLogError as e:
        raise SystemExit(f"research tool refused: event log not readable ({e}); see BETRIEB.md / runs.recover()") from None
    if st in runs.TERMINAL:
        raise SystemExit(f"research tool refused: run status is {st} (final); no automatic replacement run")
    if st == "running":
        raise SystemExit("research tool refused: run status is running -- another process may be active or one was "
                         "lost; runs.recover() checks that (BETRIEB.md); this tool removes no locks")
    report = rd / REPORT_NAME
    if st == "complete" and report.exists():
        return check_existing_report(rd)
    if st != "complete" and report.exists():
        raise SystemExit(f"research tool refused: {REPORT_NAME} exists but the run status is {st}; inspect manually")
    print("run", rd, "status", st, flush=True)
    keep_awake(True)
    try:
        w0, timings = time.time(), {}
        if st == "complete":                                # computation finished, report missing: report only
            mode = "report_only"
            status = st
        else:
            mode = "execute_and_report"
            t0 = time.perf_counter()
            status = runs.execute(rd)                       # re-checks the freeze, code and software before anything runs
            timings["execute_seconds"] = time.perf_counter() - t0
        t1 = time.perf_counter()
        rep = release.write_release_report(rd)              # exclusive writer: never replaces an existing report
        timings["release_seconds"] = time.perf_counter() - t1
        timings["wall_seconds"] = time.time() - w0
    finally:
        keep_awake(False)
    return _summary(rd, status, rep, timings, mode)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", action="store_true", help="really create and execute the research run")
    ap.add_argument("--confirm-study", type=int, help="must equal the frozen research study id (required with --start; "
                                                      "checked, never ignored, with --resume)")
    ap.add_argument("--resume", type=Path, help="continue an interrupted research run, or finish a complete run whose "
                                                "release report is missing (report only)")
    a = ap.parse_args()
    if a.resume is not None:
        if a.start:
            raise SystemExit("--resume and --start exclude each other")
        return run(a.resume, a.confirm_study)
    p = plan()
    print(json.dumps(p, indent=1, ensure_ascii=False), flush=True)
    if not a.start:
        print("DRY RUN: nothing created or started (use --start --confirm-study <id> after the pre-start review)", flush=True)
        return 0 if p["readiness"]["research_start_allowed"] else 1
    if not p["readiness"]["research_start_allowed"]:
        raise SystemExit(f"research start refused: {p['readiness']['refusal']}")
    if a.confirm_study != p["plan"]["research_study_id"]:
        raise SystemExit(f"--confirm-study must be the frozen research study id {p['plan']['research_study_id']}")
    existing = existing_research_runs(RUNS_ROOT, frozen_research_grid())
    if existing:
        raise SystemExit("research start refused: a research run of this study already exists -- continue or finish it "
                         f"with --resume (a replacement needs a documented decision): {json.dumps(existing)}")
    rd = runs.create_research_run(RUNS_ROOT, run_id=f"lr7-research-{dtm.datetime.now(dtm.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    return run(rd, a.confirm_study)


if __name__ == "__main__":
    raise SystemExit(main())
