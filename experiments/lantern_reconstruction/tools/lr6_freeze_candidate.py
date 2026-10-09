"""LR6 freeze CANDIDATE (plan 12, 19.5): sources, hyperparameters, stream plan, budget, expected grid, control and
inference rules, declared known information and open findings -- for a separate review. It is NOT a freeze:
protocol/freeze.json is written only at a documented release by Johann/Astra (runs.frozen_candidate).

Every value is read from the code and protocol files (nothing retyped). The research master seed is drawn
ONCE with `secrets` (redrawn only if it falls into Aeon's excluded range or equals the development study);
the file is written exclusively and never replaced -- a new candidate needs a new, documented decision.

    python experiments/lantern_reconstruction/tools/lr6_freeze_candidate.py --acceptance <run dir>
"""
from __future__ import annotations

import argparse
import datetime as dtm
import json
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import (artifacts, decoders, episodes, metrics, runner, runs,  # noqa: E402
                                                streams, training)
from experiments.lantern_reconstruction import registry_adapter as ra  # noqa: E402

N_RESEARCH_CONTEXTS = 20


def draw_master_seed(d) -> dict:
    ex = d["streams"]["excluded_master_seeds"]
    draws = []
    while True:
        s = secrets.randbelow(2 ** 32)
        draws.append(s)
        if not (ex["from"] <= s <= ex["to"]) and s != d["development_study_id"]:
            return {"research_study_id": s, "draws": draws,
                    "method": "secrets.randbelow(2**32), drawn once at candidate creation; redrawn only if in the excluded range "
                              f"{ex['from']}-{ex['to']} or equal to the development study {d['development_study_id']}; never chosen by any result"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acceptance", type=Path, required=True, help="the LR6 development acceptance run folder")
    a = ap.parse_args()
    if runs.CANDIDATE_FILE.exists():
        raise SystemExit(f"{runs.CANDIDATE_FILE} exists: a candidate is never replaced")
    d = streams.defaults()
    acc = json.loads((a.acceptance / "acceptance_summary.json").read_text(encoding="utf-8"))
    acc_run = runs.load_run(a.acceptance)
    per_ctx_exec = acc["execute_seconds"] / len(acc["contexts"])
    snap = ra.load_verified_snapshot()
    alarms = metrics.control_alarm_protocol()
    cand = {
        "schema": runs.CANDIDATE_SCHEMA,
        "status": "CANDIDATE -- not frozen. Needs a separate review; the freeze is a documented release by Johann/Astra "
                  "(protocol/freeze.json), after which runs.create_research_run() is the only research entry point.",
        "created_utc": dtm.datetime.now(dtm.timezone.utc).isoformat(),
        "code_identity": runs.code_identity(exclude=("protocol/freeze.json",))["identity"],
        "code_files": runs.code_identity(exclude=("protocol/freeze.json",))["files"],
        "git": runs.code_identity()["git"],
        "software": runs.software(),
        "sources": {"registry_snapshot": {"canonical_sha256": snap.canonical_sha256, "manifest_sha256": snap.manifest_sha256,
                                          "pin": dict(ra.SNAPSHOT_PIN)},
                    "config_sha256": streams.config_sha256(),
                    "plan": "reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md (v2.0) + plan change AE-01"},
        "study": draw_master_seed(d),
        "grid": {"contexts": list(range(N_RESEARCH_CONTEXTS)), "conditions": list(episodes.CONDITIONS), "tasks": list(runner.TASKS),
                 "sizes": dict(d["data_per_context"]), "dt": d["integration"]["dt"], "integrator": "rk4 (AE-01)",
                 "proposals": d["strength_surrogate"]["proposals"], "times": [float(t) for t in d["time_grid"]],
                 "controls": ["reset", "zero_impulse", "permuted_targets"],
                 "cells": len(runs.expected_cells(runs._grid("development", list(range(N_RESEARCH_CONTEXTS)), episodes.CONDITIONS,
                                                             runner.TASKS, None, None, None)))},
        "model": {"impulse_rad": d["content"]["impulse_rad"], "sigma_rad": d["measurement"]["sigma_rad"],
                  "process_noise": d["measurement"]["process_noise"], "frequencies": d["frequencies"]["distribution"],
                  "coupling_scale": d["coupling_scale"]["rule"]},
        "decoder": {"primary": "Ridge (NumPy closed form, training.py)", "lambda_grid": list(training.LAMBDA_GRID),
                    "objective": decoders.OBJECTIVE, "standardisation": decoders.STANDARDISATION, "selection": decoders.SELECTION,
                    "projection": decoders.PROJECTION,
                    "mlp": {"decision": "PROPOSAL: waived for this study",
                            "reason": "plan 6/8: Ridge is primary and does not block on the MLP; the MLP was never implemented or validated "
                                      "(initialisation, regularisation and early stopping are unspecified in code), and plan 13 names it as the "
                                      "first item to drop under budget pressure. A later MLP needs its own protocol version."}},
        "streams": {"key": d["streams"]["key"], "roles": dict(d["streams"]["roles"]), "splits": dict(d["streams"]["splits"]),
                    "key_component_limit": "every numeric key component in [0, 2**32)",
                    "decoder_extras": {"1": "control-alarm permutation: (study, context 0, test, decoder, 0, 1, cell index)",
                                       "2": "permuted training targets: (study, context, train, decoder, 0, 2, task index, time index)"}},
        "inference": {"unit": "context", "grid_aggregate": "trapezoid on log(1+tau) / log(11) (K21)",
                      "task_A": "estimation: mean, SD, pointwise two-sided 95% t interval of A_lantern, A_uncoupled and their paired difference",
                      "task_B": {"H_B1": f"E[A_lantern] > {metrics.MARGIN_B}", "H_B2": f"E[A_lantern - A_strength_surrogate] > {metrics.MARGIN_B}",
                                 "test": "one-sided t on context values minus margin; Holm over exactly these two at "
                                         f"{metrics.FAMILY_ALPHA_B}; Bonferroni intervals at t .9875, df = contexts - 1",
                                 "allowed_statements": {f"{k[0]}|{k[1]}": v for k, v in __import__("experiments.lantern_reconstruction.release",
                                                                                                       fromlist=["x"]).ALLOWED_STATEMENTS.items()}}},
        "control_rules": {"control_alarms": alarms, "permutations": runner.ALARM_PERMUTATIONS,
                          "structure_check": "reset and zero impulse identical for u and -u (first 8 test episodes per context, lantern)",
                          "pipeline_gate_A_G0": "mean over contexts of G(task A, t = 0) > 0.90 for every condition",
                          "convergence_gate": "lr4/lr4_decoder_convergence.json (bound to protocol/decoder_convergence_gate.json): passed"},
        "release": "release.py: technically_complete, scientifically_interpretable (structure checks, both LR5-A1 alarms, convergence "
                   "and pipeline gates) and hypothesis (only for an interpretable research run) as separate fields",
        "budget": {"draft": {"production_training_s": 7200, "evaluation_s": 1800, "ram_bytes": 2 ** 30, "artifacts_bytes": 2 ** 30},
                   "measured_development_acceptance": {"contexts": acc["contexts"], "execute_seconds": acc["execute_seconds"],
                                                       "release_seconds": acc["release_seconds"], "artifact_bytes": acc["artifact_bytes"]},
                   "extrapolated_research": {"execute_seconds": per_ctx_exec * N_RESEARCH_CONTEXTS,
                                             "artifact_bytes": acc["artifact_bytes"] / len(acc["contexts"]) * N_RESEARCH_CONTEXTS,
                                             "note": "linear in the number of contexts from the measured acceptance run; the release gate's "
                                                     "permutations grow with the contexts as well (see lr5/lr5_budget.json)"}},
        "declared_known_information": [
            "Aeon's development pilot (seeds 900000-900104): known before this protocol; those seeds are excluded",
            f"development study {d['development_study_id']}: contexts 0 and 1 (LR4 decoder convergence gate, full G curves) and "
            f"contexts {acc['contexts']} (LR6 development acceptance run {acc_run['run_id']}) were seen; no protocol value was chosen from them",
        ],
        "operations": "lr6/BETRIEB.md (start, monitoring, recovery after a process loss, MANUAL handling of left-over administration "
                      "locks, release report, review package)",
        "open_findings": [
            "the GitHub CI workflow has never run (branch not pushed); Python 3.12 was not available locally",
            "left-over administration locks are handled manually by design (never auto-removed)",
            "the research run is bound to the software of the freeze (strict equality on resume)",
        ],
    }
    artifacts.write_json_exclusive(runs.CANDIDATE_FILE, cand)
    import yaml
    artifacts.write_exclusive(runs.CANDIDATE_FILE.with_suffix(".yaml"),
                              ("# YAML twin of freeze_candidate.json (generated; the JSON is authoritative)\n"
                               + yaml.safe_dump(cand, sort_keys=False, allow_unicode=True, width=10 ** 6)).encode("utf-8"))
    print(json.dumps({k: cand[k] for k in ("study", "grid", "budget")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
