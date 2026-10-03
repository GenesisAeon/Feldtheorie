"""M9c: check the FROZEN predictions against the tested kernel and decoders.

Order (docs/M9_HERLEITUNG.md section 7):
1. integrity: the frozen file has the recorded SHA-256 and predict.py, the
   derivation and the registry are unchanged since the freeze;
2. primary (deterministic, every held-out combination, every d = 0..64):
   kernel separation inside the frozen band, kernel D inside [D_lo, D_hi];
3. secondary (statistical): trained nearest-mean decoders at d = D_lin and
   D_lin + 1 inside the frozen decoder band;
4. informative: point predictions, naive q rule, Z1.

The result is written exclusively (never overwritten) to
D:/mandala/mandala-memory-results/m9/. Nothing in the frozen protocol is
changed; a violation is reported, not repaired.

    python -m experiments.mandala_memory.m9_evaluate [--out-dir DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from experiments.mandala_memory import lab, m9_freeze, predict
from experiments.mandala_memory.data import NearestMeanDecoder, balanced_accuracy, make_episodes, observe_episodes

FROZEN_SHA256 = "1e872cecaaa4ff10d796e921a289119cde32ba1fee8698cc0881e4137867de13"
OUT_DIR = Path(r"D:/mandala/mandala-memory-results/m9")
SCHEMA = "mandala-memory-m9-evaluation-v1"


class IntegrityError(RuntimeError):
    pass


def load_frozen(path: Path = m9_freeze.FROZEN, expected_sha: str = FROZEN_SHA256) -> Dict:
    raw = path.read_bytes().replace(b"\r\n", b"\n")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected_sha:
        raise IntegrityError(f"frozen predictions changed: sha256 {sha} != {expected_sha}")
    fr = json.loads(raw.decode("utf-8"))
    for key, f in (("predict_py_sha256", "predict.py"), ("derivation_sha256", "docs/M9_HERLEITUNG.md"),
                   ("registry_sha256", "m9_registry.py")):
        if fr[key] != m9_freeze.sha256_file(m9_freeze.HERE / f):
            raise IntegrityError(f"{f} changed after the freeze")
    return fr


def knobs_of(c: Dict, p_star: float) -> Dict:
    k = {key: c[key] for key in ("N", "M", "gamma", "ell", "amplitude", "sigma", "inputs", "readout", "readout_node",
                                 "nonlinearity")}
    k["c"] = 0.25 if c["c"] is None else c["c"]          # ignored for M = 1
    k["p_star"] = p_star
    return k


def _d(v: Optional[int]) -> int:
    return -1 if v is None else v


def check_primary(pred: Dict, ker: Dict) -> Dict:
    s_lin, E, Hn = pred["separation_linear"], pred["error_bound_E"], pred["H_norm2"]
    s_k = ker["curve"]["separation_l2"]
    worst, violations = 0.0, []
    for d, (s, e, k) in enumerate(zip(s_lin, E, s_k)):
        allowed = Hn * e + 1e-12 * max(1.0, s) + 1e-15
        ratio = abs(k - s) / allowed
        worst = max(worst, ratio)
        if ratio > 1:
            violations.append({"d": d, "kernel": k, "linear": s, "allowed": allowed})
    D_k = ker["memory_duration"]["last_delay_at_or_above"]
    lo, hi = pred["D_interval"]
    D_ok = _d(lo) <= _d(D_k) <= _d(hi)
    return {"band_ok": not violations, "D_ok": D_ok, "passed": (not violations) and D_ok, "D_kernel": D_k,
            "D_interval": [lo, hi], "D_linear": pred["D_linear"], "worst_deviation_over_allowed": worst,
            "violations": violations[:10], "n_violations": len(violations),
            "max_rel_nonlinear_deviation": max((abs(k - s) / s for s, k in zip(s_lin, s_k) if s > 1e-12), default=0.0)}


def decoder_check(pred: Dict, ker: Dict, seed: int, d: int, rules: Dict) -> Dict:
    c = pred["combination"]
    H = predict.readout_matrix(c)
    xa, xb = np.array(ker["trajectory"]["A"][d + 1]), np.array(ker["trajectory"]["B"][d + 1])
    sec = rules["secondary"]
    tr = make_episodes(sec["mode"], seed, "decoder_train", d, sec["n_train_per_class"], H.shape[0], c["sigma"])
    te = make_episodes(sec["mode"], seed, "test", d, sec["n_test_per_class"], H.shape[0], c["sigma"])
    states = {0: xa, 1: xb}
    dec = NearestMeanDecoder().fit(observe_episodes(states, H, tr), tr.labels)
    acc = balanced_accuracy(te.labels, dec.predict(observe_episodes(states, H, te)))
    lo, hi = pred["bayes_band_lo"][d], pred["bayes_band_hi"][d]
    p = (lo + hi) / 2
    se = math.sqrt(p * (1 - p) / (2 * sec["n_test_per_class"]))
    band = [lo - 0.01 - 4 * se, hi + 4 * se]
    return {"d": d, "seed": seed, "balanced_accuracy": acc, "band": band, "bayes_band": [lo, hi], "se": se,
            "kernel_bayes": ker["curve"]["bayes"][d], "passed": band[0] <= acc <= band[1]}


def evaluate(fr: Dict) -> Dict:
    rules, p_star = fr["rules"], fr["rules"]["p_star"]
    rows, dec_rows = [], []
    for it in fr["held_out"]:
        pred = it["prediction"]
        c = pred["combination"]
        ker = lab.compute(knobs_of(c, p_star))
        prim = check_primary(pred, ker)
        s_lin, s_k = pred["separation_linear"], ker["curve"]["separation_l2"]
        z1_applies = c["readout"] == "full" and not pred["modes"]["same_module"]
        z1 = all(k <= s + 1e-12 * max(1.0, s) + 1e-15 for s, k in zip(s_lin, s_k)) if z1_applies else None
        rows.append({"id": it["id"], "combination": c, **prim, "D_naive_q_rule": pred["D_naive_q_rule"],
                     "naive_q_rule_misses": pred["D_naive_q_rule"] != prim["D_kernel"],
                     "point_prediction": pred["D_point_prediction"], "Z1_applies": z1_applies, "Z1_holds": z1,
                     "kernel_bayes_at": {d: ker["curve"]["bayes"][d] for d in (0, 4, 8, 16)}})
        Dl = pred["D_linear"]
        if Dl is not None and 0 <= Dl <= 63:
            for d in (Dl, Dl + 1):
                dec_rows.append({"id": it["id"], **decoder_check(pred, ker, 9000 + it["index"], d, rules)})
    n = len(rows)
    primary_pass = all(r["passed"] for r in rows)
    z1_rows = [r for r in rows if r["Z1_applies"]]
    return {
        "schema": SCHEMA, "created_unix": time.time(), "frozen_sha256": FROZEN_SHA256,
        "frozen_git_head": fr["git_head_at_freeze"], "git_head_at_evaluation": m9_freeze.git_head(),
        "primary": {"passed": primary_pass, "n_combinations": n, "n_passed": sum(r["passed"] for r in rows),
                    "n_delays_per_combination": len(fr["held_out"][0]["prediction"]["separation_linear"]),
                    "evidence_kind_declared_set": "exhaustive_finite",
                    "evidence_kind_family": "analytic_argument (bound) + numerical_sample (24 held-out combinations)",
                    "all_candidates_scanned": True, "search_complete": True},
        "secondary": {"passed": all(r["passed"] for r in dec_rows), "n_checks": len(dec_rows),
                      "n_passed": sum(r["passed"] for r in dec_rows),
                      "evidence_kind": "numerical_sample", "empirical_status": "synthetic_only"},
        "informative": {
            "point_predictions": sum(r["point_prediction"] for r in rows),
            "point_predictions_exact": sum(r["point_prediction"] and r["D_kernel"] == r["D_interval"][0] for r in rows),
            "naive_q_rule_misses": sum(r["naive_q_rule_misses"] for r in rows),
            "naive_q_rule_misses_among_with_memory": sum(r["naive_q_rule_misses"] for r in rows if r["D_kernel"] is not None),
            "with_memory": sum(r["D_kernel"] is not None for r in rows),
            "Z1": {"n_applicable": len(z1_rows), "n_holds": sum(bool(r["Z1_holds"]) for r in z1_rows),
                   "status": "hypothesis, not proven; reported either way"},
            "max_rel_nonlinear_deviation": max(r["max_rel_nonlinear_deviation"] for r in rows),
        },
        "combinations": rows, "decoder_checks": dec_rows,
        "not_claimed": ["no statement outside family F (ablation, interventions, adapted or unequal modules)",
                        "no biological statement", "no winner",
                        "the 24 combinations are a sample of F; the bound itself is the general argument"],
    }


def write_result(res: Dict, out_dir: Path = OUT_DIR) -> Path:
    from experiments.mandala_memory.core import is_drive_c

    if is_drive_c(out_dir):
        raise RuntimeError("results must not be written to C:")
    text = json.dumps(res, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    exe = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
    path = out_dir / f"m9-evaluation--{exe}.json"
    m9_freeze.write_exclusive(path, text)
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    a = ap.parse_args(argv)
    fr = load_frozen()
    res = evaluate(fr)
    path = write_result(res, a.out_dir)
    print(json.dumps({"written": str(path), "primary": res["primary"], "secondary": {k: res["secondary"][k] for k in ("passed", "n_checks", "n_passed")},
                      "informative": res["informative"]}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
