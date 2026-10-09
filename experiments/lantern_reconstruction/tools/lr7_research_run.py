"""LR7 research run -- the ONLY start path (runs.create_research_run + runs.execute + release report), subject to the
separate pre-start review. Without --start it is a DRY RUN: readiness and plan are printed, nothing is created or run.

    python experiments/lantern_reconstruction/tools/lr7_research_run.py                    # dry run (default)
    python experiments/lantern_reconstruction/tools/lr7_research_run.py --start --confirm-study <research study id>
    python experiments/lantern_reconstruction/tools/lr7_research_run.py --resume <run dir>  # after runs.recover(), see BETRIEB.md

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

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import release, runs  # noqa: E402

RUNS_ROOT = runs.RESULTS / "runs"


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


def run(rd: Path) -> int:
    print("run", rd, flush=True)
    keep_awake(True)
    try:
        t0, w0 = time.perf_counter(), time.time()
        status = runs.execute(rd)                       # re-checks the freeze, code and software before anything runs
        t_exec = time.perf_counter() - t0
        t1 = time.perf_counter()
        rep = release.write_release_report(rd)
        t_release = time.perf_counter() - t1
    finally:
        keep_awake(False)
    events = runs.EventLog(rd / "events.jsonl").read()
    out = {"run_dir": str(rd), "status": status, "execute_seconds": t_exec, "release_seconds": t_release,
           "wall_seconds": time.time() - w0, "n_cells": rep["n_verified_cells"],
           "clock_gaps": [e for e in events if e["event"] == "clock_gap"],
           "technically_complete": rep["technically_complete"], "scientifically_interpretable": rep["scientifically_interpretable"],
           "scientific_blocks": rep["scientific_blocks"],
           "results": "release_report.json in the run folder (hypothesis section evaluated only for an interpretable research run)"}
    print(json.dumps(out, indent=1), flush=True)
    return 0 if status == "complete" and rep["technically_complete"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", action="store_true", help="really create and execute the research run")
    ap.add_argument("--confirm-study", type=int, help="must equal the frozen research study id (guard against an accidental start)")
    ap.add_argument("--resume", type=Path, help="resume an interrupted research run (after runs.recover() if it was lost)")
    a = ap.parse_args()
    if a.resume is not None:
        if a.start:
            raise SystemExit("--resume and --start exclude each other")
        return run(a.resume)
    p = plan()
    print(json.dumps(p, indent=1, ensure_ascii=False), flush=True)
    if not a.start:
        print("DRY RUN: nothing created or started (use --start --confirm-study <id> after the pre-start review)", flush=True)
        return 0 if p["readiness"]["research_start_allowed"] else 1
    if not p["readiness"]["research_start_allowed"]:
        raise SystemExit(f"research start refused: {p['readiness']['refusal']}")
    if a.confirm_study != p["plan"]["research_study_id"]:
        raise SystemExit(f"--confirm-study must be the frozen research study id {p['plan']['research_study_id']}")
    rd = runs.create_research_run(RUNS_ROOT, run_id=f"lr7-research-{dtm.datetime.now(dtm.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    return run(rd)


if __name__ == "__main__":
    raise SystemExit(main())
