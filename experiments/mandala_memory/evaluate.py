"""M4: evaluation of a result file (IMPLEMENTIERUNGSPLAN.md §6).

Pre-registered primary contrast (protocol "research.primary_delay"):
refitted decoder, ADAPTED minus FROZEN network, balanced accuracy at d = 8,
as a PAIRED difference per seed (same test episodes and noise). Reported
with a 95 % bootstrap interval of the mean paired difference over whole
seeds (2000 repetitions, own seed "bootstrap_seed"). This interval is a
synthetic uncertainty under exactly this seed/noise distribution -- not a
biological or general statement.

All other delays and conditions are descriptive. Several delays are NOT
reported as independently confirmed main tests. An optional exact
sign-flip p-value (SCF) is given for the primary contrast only and is
bound to sign exchangeability of the paired differences under the null.
Evidence vocabulary as in SCF: evidence_kind numerical_sample,
empirical_status synthetic_only.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List

import numpy as np

from experiments.mandala_memory.summarize import CONDITIONS, table


def bootstrap_mean_ci(values: List[float], reps: int, seed: int, level: float = 0.95) -> Dict:
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return {"low": None, "high": None, "reps": reps, "note": "fewer than 2 seeds"}
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([int(seed)])))
    idx = rng.integers(0, v.size, size=(reps, v.size))
    means = v[idx].mean(axis=1)
    a = (1 - level) / 2
    return {"low": float(np.quantile(means, a)), "high": float(np.quantile(means, 1 - a)), "reps": reps,
            "resampling_unit": "whole seed", "level": level}


def paired_differences(result: Dict, a: str, b: str, delay: str) -> List[float]:
    return [run["delays"][delay][a]["balanced_accuracy"] - run["delays"][delay][b]["balanced_accuracy"]
            for run in result["runs"]]


def evaluate(result: Dict) -> Dict:
    from scoped_correspondence.epistemic.records import EMPIRICAL_STATUSES, EVIDENCE_KINDS
    from scoped_correspondence.validation.modular_networks.decoders import sign_flip_test

    cfg = result["config"]
    mode = result["mode"]
    block = cfg[mode]
    primary_d = str(block.get("primary_delay", cfg["research"]["primary_delay"]))
    reps = int(cfg["research"]["bootstrap_repetitions"])
    bseed = int(cfg["research"]["bootstrap_seed"])
    diffs = paired_differences(result, "adapted", "frozen", primary_d)
    primary = {
        "contrast": "balanced accuracy, refitted decoder, adapted minus frozen network",
        "delay": int(primary_d), "n_seeds": len(diffs), "per_seed_paired_differences": diffs,
        "mean_paired_difference": float(np.mean(diffs)) if diffs else None,
        "bootstrap_95": bootstrap_mean_ci(diffs, reps, bseed),
        "uncertainty_kind": "synthetic uncertainty under this seed/noise distribution (whole-seed bootstrap)",
    }
    if 1 <= len(diffs) <= 20:
        exact = [Fraction(d).limit_denominator(10 ** 6) for d in diffs]
        primary["sign_flip_p_two_sided"] = str(sign_flip_test(exact))
        primary["sign_flip_assumption"] = "sign exchangeability of the paired seed differences under H0"
    curves = {}
    for d in result["runs"][0]["delays"] if result["runs"] else []:
        curves[d] = {
            "adapted_minus_frozen": paired_differences(result, "adapted", "frozen", d),
            "frozen_decoder_on_adapted_minus_frozen": paired_differences(result, "adapted_with_frozen_decoder", "frozen", d),
        }
    weight = [{"seed": r["seed"], "fro": r["adaptation"]["weight_change_fro"], "max": r["adaptation"]["weight_change_max"]}
              for r in result["runs"]]
    record = {"evidence_kind": "numerical_sample", "empirical_status": "synthetic_only"}
    assert record["evidence_kind"] in EVIDENCE_KINDS and record["empirical_status"] in EMPIRICAL_STATUSES
    return {
        "run_id": result["run_id"], "mode": mode, "config_sha256": result["config_sha256"], "status": result["status"],
        "failed_seeds": result["failed_seeds"], **record,
        "inferential_claims": bool(mode == "research"),
        "primary": primary,
        "descriptive_curves": table(result),
        "descriptive_paired_differences_by_delay": curves,
        "weight_change": weight,
        "assumptions": [
            "deterministic dynamics, no process noise; variability only from observation noise and adaptation order",
            "seeds are synthetic repetitions, not biological preparations",
            "delays of one seed share the same adapted network (dependence kept; not independent tests)",
            "nearest-mean decoder without standardisation, tie -> class 0",
            "the leak model has a smaller coupling budget; the sum observation has another dimension (no resource-equal comparisons)",
        ],
        "not_claimed": ["no winner", "no general memory capacity", "no statement about Feldtheorie as a whole",
                        "smoke values are descriptive only"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    res = json.loads(a.result.read_text(encoding="utf-8"))
    ev = evaluate(res)
    text = json.dumps(ev, indent=1, ensure_ascii=False, allow_nan=False)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({"run_id": ev["run_id"], "primary": {k: ev["primary"][k] for k in ("delay", "n_seeds", "mean_paired_difference", "bootstrap_95")},
                      "sign_flip_p": ev["primary"].get("sign_flip_p_two_sided")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
