"""LR4 decoder convergence gate (plan 10.2, definition in protocol/decoder_convergence_gate.json, fixed
before the run). DEVELOPMENT ONLY. Runs the complete pipeline per dt on the declared panel, compares
G / A / S / lambda / states between dt 0.02 and the dt 0.005 reference, and writes

  --out DIR/decoder_convergence_full.json   every cell, per dt (results folder outside the repo)
  lr4/lr4_decoder_convergence.json (+ .yaml) the gate summary (in the repo).

Prevents system sleep for THIS process only (SetThreadExecutionState); no permanent system change."""
from __future__ import annotations

import argparse
import ctypes
import datetime as dtm
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import contexts, runner, streams  # noqa: E402
from experiments.lantern_reconstruction import registry_adapter as ra  # noqa: E402
from experiments.lantern_reconstruction.dynamics import circular_distance  # noqa: E402

GATE = HERE / "protocol" / "decoder_convergence_gate.json"


def keep_awake(on: bool) -> None:
    if platform.system() == "Windows":
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def cells_json(cells):
    return {f"{c}|{t}": {k: ({str(tau): v for tau, v in val.items()} if isinstance(val, dict) else val) for k, val in cell.items()}
            for (c, t), cell in cells.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--smoke", action="store_true", help="tiny panel to test the tool itself; writes nothing into the repo")
    args = ap.parse_args()
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    smoke = {"sizes": {"train": 30, "val": 12, "test": 30}, "proposals": 200} if args.smoke else {}
    if args.smoke:
        gate["panel"]["contexts"] = [0]
    d = streams.defaults()
    assert gate["dt"]["protocol"] == d["integration"]["dt"], "gate file and protocol dt disagree"
    snap = ra.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    dts = [gate["dt"]["protocol"], gate["dt"]["half"], gate["dt"]["reference"]]
    full = {"gate_file_sha256": __import__("hashlib").sha256(GATE.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "config_sha256": streams.config_sha256(), "snapshot_canonical_sha256": snap.canonical_sha256,
            "software": {"python": platform.python_version(), "numpy": np.__version__},
            "started_utc": dtm.datetime.now(dtm.timezone.utc).isoformat(), "runs": {}, "state_max_circular_diff": {}}
    keep_awake(True)
    try:
        for cid in gate["panel"]["contexts"]:
            ctx = contexts.make_context(d["development_study_id"], cid)
            states = {}
            for dt in dts:
                t0, w0 = time.perf_counter(), time.time()
                r = runner.run_context(ctx, C, g, dt=dt, keep_states=True, conditions=tuple(gate["panel"]["conditions"]),
                                       tasks=tuple(gate["panel"]["tasks"]), control=gate["panel"]["control"], **smoke)
                elapsed, wall = time.perf_counter() - t0, time.time() - w0
                states[dt] = r.pop("states")
                full["runs"][f"{cid}|{dt}"] = {"cells": cells_json(r["cells"]), "surrogate_report": r["surrogate_report"],
                                               "sizes": r["sizes"], "dt": r["dt"], "seconds": elapsed, "wall_seconds": wall}
                print(f"context {cid} dt {dt}: {elapsed:.0f}s (wall {wall:.0f}s)", flush=True)
            for dt in dts[:-1]:
                full["state_max_circular_diff"][f"{cid}|{dt}"] = max(
                    float(np.max(circular_distance(states[dt][c][s], states[dts[-1]][c][s]))) for c in states[dt] for s in states[dt][c])
            del states
    finally:
        keep_awake(False)
    full["finished_utc"] = dtm.datetime.now(dtm.timezone.utc).isoformat()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "decoder_convergence_full.json").write_text(json.dumps(full, indent=1, allow_nan=False) + "\n", encoding="utf-8")

    # --- gate evaluation -------------------------------------------------------------------------------
    def cmp(dt):
        dG = dA = dS = 0.0
        lam_changes = 0
        for cid in gate["panel"]["contexts"]:
            a, ref = full["runs"][f"{cid}|{dt}"]["cells"], full["runs"][f"{cid}|{dts[-1]}"]["cells"]
            for key in a:
                dA = max(dA, abs(a[key]["A"] - ref[key]["A"]))
                for tau in a[key]["G"]:
                    dG = max(dG, abs(a[key]["G"][tau] - ref[key]["G"][tau]))
                    dS = max(dS, abs(a[key]["S"][tau] - ref[key]["S"][tau]))
                    lam_changes += a[key]["lambda"][tau] != ref[key]["lambda"][tau]
        return {"max_abs_dG": dG, "max_abs_dA": dA, "max_abs_dS": dS, "lambda_changes": lam_changes}

    comparisons = {str(dt): cmp(dt) for dt in dts[:-1]}
    prot = comparisons[str(dts[0])]
    G0A = {cond: float(np.mean([full["runs"][f"{cid}|{dts[0]}"]["cells"][f"{cond}|A"]["G"]["0.0"] for cid in gate["panel"]["contexts"]]))
           for cond in gate["panel"]["conditions"]}
    G0B = {cond: [full["runs"][f"{cid}|{dts[0]}"]["cells"][f"{cond}|B"]["G"]["0.0"] for cid in gate["panel"]["contexts"]]
           for cond in gate["panel"]["conditions"]}
    summary = {
        "schema": "lantern-lr4-decoder-convergence-v1",
        "gate_definition": "protocol/decoder_convergence_gate.json (fixed before the run)",
        "gate_file_sha256": full["gate_file_sha256"], "config_sha256": full["config_sha256"],
        "smoke_only": bool(args.smoke),
        "panel": {"study_id": d["development_study_id"], "contexts": gate["panel"]["contexts"],
                  "sizes": smoke.get("sizes", dict(d["data_per_context"])),
                  "conditions": gate["panel"]["conditions"], "tasks": gate["panel"]["tasks"], "dt": dts},
        "comparisons_to_reference_dt": comparisons,
        "state_max_circular_diff_rad": full["state_max_circular_diff"],
        "decoder_gate": {"criterion": gate["criterion"], "max_abs_dG": prot["max_abs_dG"], "max_abs_dA": prot["max_abs_dA"],
                         "passed": prot["max_abs_dG"] <= 0.01 and prot["max_abs_dA"] <= 0.01},
        "pipeline_gate_A_t0": {"mean_G0_by_condition": G0A, "rule": "> 0.90 for every condition",
                               "passed": all(v > 0.90 for v in G0A.values())},
        "B_t0_G_reported": G0B,
        "runtime_seconds": {k: v["seconds"] for k, v in full["runs"].items()},
        "use_of_values": gate["use_of_values"],
        "full_results": str(args.out / "decoder_convergence_full.json"),
    }
    js = (args.out if args.smoke else HERE / "lr4") / "lr4_decoder_convergence.json"
    js.parent.mkdir(exist_ok=True)
    js.write_text(json.dumps(summary, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    import yaml
    js.with_suffix(".yaml").write_text("# YAML twin of lr4_decoder_convergence.json (generated; the JSON is authoritative)\n"
                                       + yaml.safe_dump(summary, sort_keys=False, allow_unicode=True, width=10 ** 6), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("comparisons_to_reference_dt", "decoder_gate", "pipeline_gate_A_t0")}, indent=1))


if __name__ == "__main__":
    main()
