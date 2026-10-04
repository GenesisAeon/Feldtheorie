"""M11 evaluation (plan Fassung 2, section 4).

- release gate: research mode, complete, valid freeze, frozen references, the complete
  grid (cases x seeds x n) derived from the PROTOCOL, exact sizes, expected streams,
  finite accuracies in [0, 1];
- confirmatory family {C-Daten, C-Modell} on the main case: one-sided t test of
  (mean paired seed difference - delta), df = n_seeds - 1 (normality = assumption),
  zero-variance rule, Holm; bootstrap intervals alongside;
- descriptive: decomposition (signed sampling term), closed share (ratio of seed means,
  N/A if the denominator <= 0.01), convergence diagnostic, K0 controls; the Bayes SE
  from M10 is always reported separately.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np

from experiments.mandala_memory import m11_references as mref
from experiments.mandala_memory import m11_readout as mr


def t_one_sided_p(diffs: List[float], delta: float) -> Dict:
    from scipy.stats import t as tdist

    d = np.asarray(diffs, float)
    n, mean = d.size, float(d.mean())
    # zero-variance rule: all differences identical (checked on the values -- the floating
    # mean of identical values can leave a sd of ~1e-18 instead of an exact 0)
    sd = 0.0 if n < 2 or float(np.ptp(d)) == 0.0 else float(d.std(ddof=1))
    if sd == 0.0:
        return {"mean": mean, "sd": 0.0, "t": None, "p": 0.0 if mean > delta else 1.0, "ci95_t": [mean, mean]}
    se = sd / math.sqrt(n)
    tval = (mean - delta) / se
    q = float(tdist.ppf(0.975, n - 1))
    return {"mean": mean, "sd": sd, "t": tval, "p": float(tdist.sf(tval, n - 1)), "ci95_t": [mean - q * se, mean + q * se]}


def holm(pvals: Dict[str, float], alpha: float) -> Dict[str, Dict]:
    order = sorted(pvals, key=lambda k: pvals[k])
    m, out, still, running = len(order), {}, True, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        reject = still and pvals[k] <= alpha / (m - i)
        still = still and reject
        out[k] = {"p": pvals[k], "p_holm": running, "rejected": reject}
    return out


def bootstrap(values, reps: int, seed: int) -> List[float]:
    v = np.asarray(values, float)
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed])))
    means = v[rng.integers(0, v.size, size=(reps, v.size))].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def table(result: Dict) -> Dict:
    return {(r["seed"], r["case"], r["n"]): r for r in result["rows"]}


def completeness(result: Dict, proto: Dict, mode_key: str = "research") -> List[str]:
    probs = None
    problems = []
    seeds, cases, grid = proto["seeds"][mode_key], [c["name"] for c in proto["cases"]], proto["n_grid"]
    if result.get("seeds") != seeds:
        problems.append("seeds_differ_from_protocol")
    if result.get("n_grid") != grid:
        problems.append("n_grid_differs_from_protocol")
    if result.get("test_pairs") != proto["test_pairs"]:
        problems.append("test_pairs_differ_from_protocol")
    expected = {(s, c, n) for s in seeds for c in cases for n in grid}
    keys = [(r.get("seed"), r.get("case"), r.get("n")) for r in result.get("rows", [])]
    if len(keys) != len(set(keys)):
        problems.append("duplicate_rows")
    if set(keys) - expected:
        problems.append("extra_rows")
    if expected - set(keys):
        problems.append("missing_rows")
    smode = proto["modes"][mode_key]
    for r, key in zip(result.get("rows", []), keys):
        if key not in expected:
            continue
        s, c, n = key
        want_train = [list(mr.stream(smode, s, kind, "train")[1]) for kind in ("pattern", "noise")]
        want_test = [list(mr.stream(smode, s, kind, "test")[1]) for kind in ("pattern", "noise")]
        if r.get("train_streams") != want_train or r.get("test_streams") != want_test:
            problems.append(f"foreign_stream:{key}")
        if r.get("n_test_pairs") != proto["test_pairs"]:
            problems.append(f"wrong_test_size:{key}")
        fit = (r.get("mlp") or {}).get("fit") or {}
        if fit.get("n_fit_pairs") != n - n // 5 or fit.get("n_val_pairs") != n // 5 or len(fit.get("inits", [])) != proto["decoders"]["mlp"]["inits"]:
            problems.append(f"wrong_mlp_budget:{key}")
        vals = [(r.get("nm") or {}).get("exact"), (r.get("nm") or {}).get("test"), (r.get("lda") or {}).get("exact"),
                (r.get("lda") or {}).get("test"), (r.get("mlp") or {}).get("test")]
        if not all(isinstance(v, float) and math.isfinite(v) and 0.0 <= v <= 1.0 for v in vals):
            problems.append(f"non_finite_or_out_of_range:{key}")
    return problems


def release(result: Dict) -> Dict:
    from experiments.mandala_memory import m11_run

    proto = mref.load_protocol()
    reasons = []
    if result.get("mode") != "research":
        reasons.append("mode_is_not_research")
    if result.get("status") != "complete" or result.get("failures"):
        reasons.append("run_not_complete")
    try:
        rec = m11_run.require_frozen("release")
        if result.get("code_sha256") != rec["code_sha256"] or result.get("protocol_sha256") != rec["protocol_sha256"]:
            reasons.append("result_not_from_frozen_code_or_protocol")
    except Exception as e:
        reasons.append(f"freeze_invalid: {e}")
    if any(v is not None for v in result.get("overrides", {}).values()):
        reasons.append("overrides_used")
    reasons += completeness(result, proto)
    return {"released": not reasons, "reasons": reasons}


def confirmatory(result: Dict, proto: Dict) -> Dict:
    cf = proto["confirmatory"]
    T, case = table(result), cf["case"]
    seeds = sorted({r["seed"] for r in result["rows"]})
    d_data = [T[(s, case, 16000)]["lda"]["exact"] - T[(s, case, 1000)]["lda"]["exact"] for s in seeds]
    d_model = [T[(s, case, 1000)]["mlp"]["test"] - T[(s, case, 1000)]["lda"]["test"] for s in seeds]
    tests = {"C-Daten": t_one_sided_p(d_data, cf["delta"]), "C-Modell": t_one_sided_p(d_model, cf["delta"])}
    h = holm({k: v["p"] for k, v in tests.items()}, cf["alpha"])
    for k, v in tests.items():
        v.update(h[k])
        v["bootstrap95"] = bootstrap(d_data if k == "C-Daten" else d_model, 2000, 2026100412)
        v["wording"] = ("bestaetigt" if v["rejected"] else
                        "Richtung widerspricht der Hypothese" if v["ci95_t"][1] < 0 else "nicht bestaetigt")
    return {"delta": cf["delta"], "alpha": cf["alpha"], "n_seeds": len(seeds), "contrasts": tests,
            "assumption": cf["test"]}


def descriptive(result: Dict, refs: Dict, proto: Dict) -> Dict:
    T = table(result)
    seeds = sorted({r["seed"] for r in result["rows"]})
    out = {}
    for case in [c["name"] for c in proto["cases"]] if refs["case_set"] == "research" else sorted(refs["cases"]):
        ref = refs["cases"][case]
        B, Lf = ref["B"], ref["L_found"]
        lda1000 = float(np.mean([T[(s, case, 1000)]["lda"]["exact"] for s in seeds]))
        rows = {}
        for n in result["n_grid"]:
            for dec in ("nm", "lda", "mlp"):
                key = "test" if dec == "mlp" else "exact"
                vals = [T[(s, case, n)][dec][key] for s in seeds]
                m = float(np.mean(vals))
                item = {"mean": m, "bootstrap95": bootstrap(vals, 2000, 2026100412), "gap_to_B": B - m,
                        "B_se_separate": ref["B_se"]}
                if dec in ("nm", "lda"):
                    inf = ref[f"acc_{dec}_inf"]
                    item["decomposition"] = {"B_minus_L_found (upper bound of nonlinearity gap)": B - Lf,
                                             "criterion_L_found_minus_inf": Lf - inf,
                                             "sampling_inf_minus_n (signed)": inf - m}
                    item["convergence_abs_diff_to_inf"] = abs(m - inf) if n == max(result["n_grid"]) else None
                denom = B - lda1000
                item["closed_share_vs_LDA1000"] = (m - lda1000) / denom if denom > 0.01 else None
                rows[f"{dec}@{n}"] = item
        out[case] = {"B": B, "B_se": ref["B_se"], "L_found": Lf, "acc_nm_inf": ref["acc_nm_inf"],
                     "acc_lda_inf": ref["acc_lda_inf"], "rows": rows}
    return out


def evaluate(result: Dict, refs: Dict) -> Dict:
    proto = mref.load_protocol()
    rel = release(result)
    try:
        conf = confirmatory(result, proto)
    except KeyError as e:
        conf = {"not_computable": f"KeyError: {e}"}
    try:
        desc = descriptive(result, refs, proto)
    except KeyError as e:
        desc = {"not_computable": f"KeyError: {e}"}
    return {"run_id": result.get("run_id"), "mode": result.get("mode"), "release": rel, "confirmatory": conf,
            "confirmatory_label": "confirmatory (released)" if rel["released"] else "DESCRIPTIVE ONLY -- not released",
            "descriptive": desc, "evidence": {"kind": "numerical_sample", "empirical_status": "synthetic_only"}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    ap.add_argument("--references", type=Path, default=mref.RESEARCH_REFERENCES)
    a = ap.parse_args(argv)
    ev = evaluate(json.loads(a.result.read_text(encoding="utf-8")), json.loads(a.references.read_text(encoding="utf-8")))
    print(json.dumps({k: ev[k] for k in ("mode", "release", "confirmatory_label")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
