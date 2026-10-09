"""LR6 development acceptance (plan 14, LR6). DEVELOPMENT ONLY: development study, contexts 0-3, full sizes
(1000/250/1000), all four conditions, all three control curves, the complete artifact chain and the release
gate (incl. the 12 LR5-A1 control cells with B = 9999). Measures the real runtime (the LR5 budget was an
extrapolation). Prevents system sleep for this process only.

    python experiments/lantern_reconstruction/tools/lr6_development_acceptance.py [--resume RUN_DIR]
"""
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
CONTEXTS = [0, 1, 2, 3]


def keep_awake(on: bool) -> None:
    if platform.system() == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if on else 0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", type=Path)
    a = ap.parse_args()
    rd = a.resume or runs.create_run(RUNS_ROOT, "development", CONTEXTS,
                                     run_id=f"lr6-acceptance-{dtm.datetime.now(dtm.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    print("run", rd, flush=True)
    keep_awake(True)
    try:
        t0, w0 = time.perf_counter(), time.time()
        status = runs.execute(rd)
        t_exec = time.perf_counter() - t0
        t1 = time.perf_counter()
        rep = release.write_release_report(rd)
        t_release = time.perf_counter() - t1
    finally:
        keep_awake(False)
    events = runs.EventLog(rd / "events.jsonl").read()
    out = {"run_dir": str(rd), "status": status, "contexts": CONTEXTS, "execute_seconds": t_exec, "release_seconds": t_release,
           "wall_seconds": time.time() - w0, "n_cells": rep["n_verified_cells"],
           "clock_gaps": [e for e in events if e["event"] == "clock_gap"],
           "artifact_bytes": sum(p.stat().st_size for p in Path(rd).rglob("*") if p.is_file()),
           "technically_complete": rep["technically_complete"], "scientifically_interpretable": rep["scientifically_interpretable"],
           "scientific_blocks": rep["scientific_blocks"], "pipeline_gate_A_G0": rep.get("pipeline_gate_A_G0"),
           "control_alarms": {k: rep["control_alarms"][k] for k in ("positive_spurious_success_alarm", "target_dependence_alarm")}
           if rep.get("control_alarms") else None,
           "hypothesis": rep["hypothesis"]}
    (Path(rd) / "acceptance_summary.json").write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1), flush=True)
    return 0 if status == "complete" and rep["technically_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
