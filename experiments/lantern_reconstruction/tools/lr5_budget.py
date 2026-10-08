"""LR5 budget measurement (plan section 13). DEVELOPMENT ONLY (development study, context 0, synthetic alarm
data). Separate timings for dynamics, Ridge, persistence and evaluation; peak RAM and real artifact bytes.
Every measurement block stays well below 5 minutes. The full-study numbers are an EXTRAPOLATION from these
measurements to the planned grid (20 contexts x (4 conditions + 3 control curves) x 2 tasks x 7 times),
labelled as such; budget (draft): production/training 2 h, evaluation 30 min, RAM and artifacts < 1 GiB.

    python experiments/lantern_reconstruction/tools/lr5_budget.py --scratch DIR
"""
from __future__ import annotations

import argparse
import ctypes
import json
import platform
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import contexts, episodes, metrics, observation, runner, runs, streams, training  # noqa: E402
from experiments.lantern_reconstruction import registry_adapter as ra  # noqa: E402


def peak_rss_bytes():
    if platform.system() != "Windows":
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    class PMC(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    c = PMC()
    c.cb = ctypes.sizeof(PMC)
    k32, psapi = ctypes.windll.kernel32, ctypes.windll.psapi
    k32.GetCurrentProcess.restype = ctypes.c_void_p                       # 64-bit pseudo handle
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        return None                                                       # measurement failed: say so, never 0
    return int(c.PeakWorkingSetSize)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", type=Path, required=True, help="empty folder for the persistence measurement")
    a = ap.parse_args()
    d = streams.defaults()
    sizes = dict(d["data_per_context"])
    n_ep = sum(sizes.values())
    snap = ra.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    ctx = contexts.make_context(d["development_study_id"], 0)
    m = {}

    t = time.perf_counter()
    prep = runner.prepare_context(ctx, C, sizes)
    m["prepare_context_s"] = time.perf_counter() - t                      # incl. 20000-proposal surrogate

    t = time.perf_counter()
    states = {s: episodes.simulate(ctx, prep["batches"][s], prep["mats"]["lantern"], g) for s in runner.SPLITS}
    m["dynamics_one_unit_s"] = time.perf_counter() - t                    # 2250 episodes, one condition

    t = time.perf_counter()
    models = []
    for task in runner.TASKS:
        for k in range(len(d["time_grid"])):
            X = {s: observation.observe(ctx, prep["specs"][task], states[s][:, k], prep["batches"][s].eps[:, k]) for s in runner.SPLITS}
            models.append((training.fit_ridge(prep["specs"][task], X["train"], prep["batches"]["train"].u, X["val"], prep["batches"]["val"].u,
                                              provenance={"context_id": 0, "task": task, "time": float(d["time_grid"][k])}), X["test"]))
    m["ridge_14_cells_s"] = time.perf_counter() - t

    a.scratch.mkdir(parents=True, exist_ok=False)
    run = {"run_identity": "budget", "grid": {"study_id": ctx.study_id, "dt": d["integration"]["dt"]}}
    t = time.perf_counter()
    for i, (model, Xt) in enumerate(models):
        c = {"context_id": 0, "condition": "lantern", "control": "none", "task": model.task, "time": float(d["time_grid"][i % 7]), "time_index": i % 7}
        runs._persist_cell(a.scratch, run, ctx, c, model, Xt, prep["batches"]["test"].u)
    m["persist_and_score_14_cells_s"] = time.perf_counter() - t
    cell_bytes = sum(p.stat().st_size for p in a.scratch.rglob("*") if p.is_file()) / len(models)
    m["bytes_per_cell"] = cell_bytes
    shutil.rmtree(a.scratch)

    rng = np.random.default_rng(1)                 # synthetic alarm data only: 20 contexts x 1000 test episodes
    cells = {cid: (np.clip(rng.normal(0, .3, (sizes["test"], 4)), -1, 1), rng.uniform(-1, 1, (sizes["test"], 4))) for cid in range(20)}
    t = time.perf_counter()
    metrics.permutation_gain_test(cells, np.random.default_rng(2), runner.ALARM_PERMUTATIONS)
    m["alarm_one_cell_20_contexts_s"] = time.perf_counter() - t
    m["peak_working_set_bytes"] = peak_rss_bytes()

    n_ctx = d["contexts"]["n"]
    n_units = len(episodes.CONDITIONS) + 3                                   # cell units: conditions + 3 control curves
    n_sims = len({runner.initial_state_key(ctx, prep, c, "none") for c in episodes.CONDITIONS} |
                 {runner.initial_state_key(ctx, prep, "lantern", c) for c in ("reset", "zero_impulse", "permuted_targets")})
    n_cells_ctx = n_units * 2 * len(d["time_grid"])
    per_cell_fit = m["ridge_14_cells_s"] / 14
    per_cell_persist = m["persist_and_score_14_cells_s"] / 14
    production = n_ctx * (m["prepare_context_s"] + n_sims * m["dynamics_one_unit_s"] + n_cells_ctx * (per_cell_fit + per_cell_persist))
    evaluation = 12 * m["alarm_one_cell_20_contexts_s"] + n_ctx * n_cells_ctx * per_cell_persist   # alarms + re-verification (upper bound)
    artifacts_bytes = n_ctx * n_cells_ctx * cell_bytes
    report = {
        "schema": "lantern-lr5-budget-v1", "status": "development measurement; full-study values are EXTRAPOLATIONS",
        "machine": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(), "processor": platform.processor()},
        "measured": m,
        "measurement_scope": {"dynamics_one_unit": f"{n_ep} episodes, one condition, RK4 dt {d['integration']['dt']}",
                              "ridge": "2 tasks x 7 times on those states", "persistence": "14 cells: model + predictions + record, exclusive",
                              "alarm": "one control cell, 20 synthetic contexts x 1000 episodes, B = 9999"},
        "extrapolated_full_study": {"grid": f"{n_ctx} contexts x {n_units} units x 2 tasks x 7 times = {n_ctx * n_cells_ctx} cells",
                                    "trajectory_simulations_per_context": n_sims,
                                    "production_training_s": production, "evaluation_s": evaluation, "artifacts_bytes": artifacts_bytes},
        "budget_draft": {"production_training_s": 7200, "evaluation_s": 1800, "ram_bytes": 2 ** 30, "artifacts_bytes": 2 ** 30},
    }
    report["within_budget"] = {"production_training": production <= 7200, "evaluation": evaluation <= 1800,
                               "ram_measured_peak": None if m["peak_working_set_bytes"] is None else m["peak_working_set_bytes"] <= 2 ** 30,
                               "artifacts": artifacts_bytes <= 2 ** 30}
    out = HERE / "lr5" / "lr5_budget.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    import yaml
    out.with_suffix(".yaml").write_text("# YAML twin of lr5_budget.json (generated; the JSON is authoritative)\n"
                                        + yaml.safe_dump(report, sort_keys=False, allow_unicode=True, width=10 ** 6), encoding="utf-8")
    print(json.dumps({"measured": m, "extrapolated": report["extrapolated_full_study"], "within_budget": report["within_budget"]}, indent=1))


if __name__ == "__main__":
    main()
