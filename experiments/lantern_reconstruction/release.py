"""LR5 release gate (plan 10, 12; review LANTERN_LR4_NACHREVIEW LR5 duties, LR5-A1).

Three SEPARATE fields, never one flag:
  technically_complete         exact grid: every expected cell has a verified record (run identity, cell,
                               files, model identity, sample counts, finite values), no extra cells, a
                               structure record per context, run status 'complete';
  scientifically_interpretable technically complete AND every structure check (reset / zero impulse) passed
                               AND neither LR5-A1 alarm (proposal rule, protocol/control_alarms.json) AND the
                               numerical gates (decoder convergence gate bound and passed; task-A G0 > 0.90);
  hypothesis                   only for research runs (H-B1/H-B2 of plan 9); a development or smoke run
                               reports 'not_evaluated' -- never a hypothesis decision from development data.
Missing controls BLOCK; they are never treated as passed. Nothing here reads a score to change a status."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict

import numpy as np

from experiments.lantern_reconstruction import artifacts, contexts, metrics, runner, runs, streams
from experiments.lantern_reconstruction import registry_adapter as ra

PIPELINE_G0_A = 0.90


def _convergence_gate() -> Dict:
    p = runs.HERE / "lr4" / "lr4_decoder_convergence.json"
    if not p.exists():
        return {"passed": False, "reason": "lr4/lr4_decoder_convergence.json missing"}
    s = ra.strict_json(p.read_text(encoding="utf-8"))
    gate = (runs.HERE / "protocol" / "decoder_convergence_gate.json").read_bytes().replace(b"\r\n", b"\n")
    bound = s.get("gate_file_sha256") == hashlib.sha256(gate).hexdigest() and not s.get("smoke_only", True)
    dg = s.get("decoder_gate", {})
    ok = bound and dg.get("max_abs_dG", 1) <= 0.01 and dg.get("max_abs_dA", 1) <= 0.01
    return {"passed": bool(ok), "bound_to_gate_definition": bool(bound), "max_abs_dG": dg.get("max_abs_dG"), "max_abs_dA": dg.get("max_abs_dA")}


def release_report(run_dir: Path) -> Dict:
    run_dir = Path(run_dir)
    problems, blocks = [], []
    try:
        run = runs.load_run(run_dir)
    except Exception as e:                                   # noqa: BLE001 -- any failure here blocks everything
        return {"technically_complete": False, "scientifically_interpretable": False,
                "hypothesis": {"status": "not_evaluated"}, "problems": [f"run identity: {e}"]}
    grid = run["grid"]
    try:
        st = runs.status(run_dir)
    except Exception as e:                                   # noqa: BLE001 -- e.g. an unacknowledged truncated log
        st = f"unreadable ({type(e).__name__})"
    if st != "complete":
        problems.append(f"run status is {st}, not complete")
    expected = runs.expected_cells(grid)
    expected_dirs = {runs.cell_dir_name(c) for c in expected}
    present = {p.name for p in (run_dir / "cells").iterdir() if p.is_dir()} if (run_dir / "cells").exists() else set()
    if present - expected_dirs:
        problems.append(f"cells outside the grid: {sorted(present - expected_dirs)}")
    records = {}
    for c in expected:
        name = runs.cell_dir_name(c)
        if not (run_dir / "cells" / name / "record.json").exists():
            problems.append(f"missing cell {name}")
            continue
        try:
            records[name] = runs.verify_record(run_dir, run, c, contexts.make_context(grid["study_id"], c["context_id"]))
        except Exception as e:                               # noqa: BLE001
            problems.append(f"cell {name}: {e}")
    structure = {}
    snap = ra.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    for cid in grid["contexts"]:
        p = run_dir / "structure" / f"c{cid:03d}.json"
        if not p.exists():
            problems.append(f"structure check of context {cid} missing")
            continue
        s = ra.strict_json(p.read_text(encoding="utf-8"))
        if s.get("run_identity") != run["run_identity"] or s.get("context_id") != cid or set(s.get("checks", {})) != {"reset", "zero_impulse"}:
            problems.append(f"structure record of context {cid} does not belong to this run")
            continue
        # deterministic and cheap: recomputed here, so an edited structure record cannot pass
        again = runs._structure_check(contexts.make_context(grid["study_id"], cid), C, g, grid["sizes"])
        if {k: s[k] for k in again} != again:
            problems.append(f"structure record of context {cid} differs from its recomputation")
            continue
        structure[cid] = s
    technically_complete = not problems
    report = {"run_id": run["run_id"], "run_identity": run["run_identity"], "kind": run["kind"], "status": st,
              "n_expected_cells": len(expected), "n_verified_cells": len(records), "problems": problems,
              "technically_complete": technically_complete}
    # --- scientific interpretability -------------------------------------------------------------------
    failed_structure = [cid for cid, s in structure.items() if not (s["passed"] and all(s["checks"].values()))]
    if failed_structure or len(structure) != len(grid["contexts"]):
        blocks.append(f"reset/zero-impulse structure checks failed or missing for contexts {failed_structure or 'missing'}")
    alarms = None
    if technically_complete:
        if len(grid["contexts"]) < 2:
            blocks.append("control alarms need at least two contexts")
        else:
            per = {cid: {} for cid in grid["contexts"]}
            for name in metrics.control_alarm_cells():
                ctl, task, tau = name.split("|")
                k = grid["times"].index(float(tau))
                for cid in grid["contexts"]:
                    c = {"context_id": cid, "condition": runs.CONTROL_CONDITION, "control": ctl, "task": task, "time": float(tau), "time_index": k}
                    arr = artifacts.load_arrays_verified(run_dir / "cells" / runs.cell_dir_name(c), records[runs.cell_dir_name(c)]["predictions"])
                    per[cid][name] = (arr["projected"], arr["targets"])
            alarms = metrics.control_alarms(runner.alarm_inputs(per, grid["study_id"]))
            if alarms["positive_spurious_success_alarm"]:
                blocks.append("LR5-A1 positive spurious success alarm")
            if alarms["target_dependence_alarm"]:
                blocks.append("LR5-A1 target dependence alarm (proposal rule: blocks until investigated)")
        g0 = {cond: float(np.mean([records[runs.cell_dir_name({"context_id": cid, "condition": cond, "control": "none", "task": "A",
                                                                "time": grid["times"][0], "time_index": 0})]["scores"]["G"]
                                   for cid in grid["contexts"]])) for cond in grid["conditions"]} if "A" in grid["tasks"] else {}
        if not g0 or not all(v > PIPELINE_G0_A for v in g0.values()):
            blocks.append(f"pipeline gate task A G0 > {PIPELINE_G0_A} not met or not evaluable: {g0}")
        report["pipeline_gate_A_G0"] = g0
    else:
        blocks.append("not technically complete")
    conv = _convergence_gate()
    if not conv["passed"]:
        blocks.append("decoder convergence gate not passed or not bound")
    report.update(structure_checks={str(k): v["checks"] for k, v in structure.items()}, control_alarms=alarms, convergence_gate=conv,
                  scientific_blocks=blocks, scientifically_interpretable=technically_complete and not blocks,
                  hypothesis={"status": "not_evaluated", "reason": f"{run['kind']} run: no hypothesis decision from development data"})
    return report


def write_release_report(run_dir: Path) -> Dict:
    """Exclusive: a release report is written once per run and never replaced."""
    rep = release_report(run_dir)
    artifacts.write_json_exclusive(Path(run_dir) / "release_report.json", rep)
    return rep
