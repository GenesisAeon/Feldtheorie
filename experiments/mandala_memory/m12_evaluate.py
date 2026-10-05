"""M12 evaluation (plan Fassung 2, sections 6 and 8).

- release gate (research, complete, frozen protocol/references/models/code, complete grid,
  unchanged model files, fit guard, test stream != training stream, finite values);
- diagnostics D1-D4 (statistical cross-checks at 4 SE with the alarm rule: an alarm
  withholds the confirmatory release pending a documented review; never a repetition);
- descriptive: absolute accuracy, loss vs c0, delta_B with its Monte Carlo SE (no seed
  interval), delta_G with seed intervals CONDITIONAL on the stored B values plus the MC-SE
  of delta_B, the LDA split relative to the condition-specific population LDA (NOT the
  best linear rule), and the MLP-LDA advantage per condition and its change vs c0;
- confirmatory R-a / R-sigma: fixed MLP better than fixed LDA by more than delta at the two
  raised endpoints (same test episodes, paired by seed), one-sided t, Holm.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from experiments.mandala_memory import m11_evaluate as e11
from experiments.mandala_memory import m12_common as mc
from experiments.mandala_memory import m12_models as mm
from experiments.mandala_memory import m12_references as mref
from experiments.mandala_memory.core import MemoryLabError

Z4 = 4.0


def _finite01(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x) and 0.0 <= x <= 1.0


def release(result: Dict, refs: Optional[Dict] = None) -> Dict:
    reasons: List[str] = []
    proto = mc.load_protocol()
    if result.get("mode") != "research":
        reasons.append("mode_is_not_research")
    if result.get("status") != "complete" or result.get("failures"):
        reasons.append("run_not_complete")
    if any(v is not None for v in (result.get("overrides") or {}).values()):
        reasons.append("overrides_used")
    try:
        prec = mref.require_protocol_frozen("release")
        if result.get("protocol_sha256") != prec["protocol_sha256"] or result.get("frozen_protocol_sha256") != prec["protocol_sha256"]:
            reasons.append("result_not_from_frozen_protocol")
        if result.get("code_sha256") != prec["code_sha256"]:
            reasons.append("result_not_from_frozen_code")
        art = mref.require_references("research")
        if result.get("references_sha256") != art["sha256"] or (refs is not None and refs != art["refs"]):
            reasons.append("references_not_the_frozen_artifact")
        frz = json.loads(mm.MODEL_FREEZE.read_text(encoding="utf-8")) if mm.MODEL_FREEZE.is_file() else None
        if frz is None:
            reasons.append("model_freeze_missing")
        elif (result.get("manifest_sha256") != frz.get("manifest_sha256") or result.get("model_freeze_sha256") != mc.sha(mm.MODEL_FREEZE)
              or frz.get("references_sha256") != art["sha256"]):
            reasons.append("models_not_the_frozen_models")
        else:
            mm.require_models("research")
    except Exception as e:                                    # any freeze problem blocks the release
        reasons.append(f"freeze_invalid: {type(e).__name__}: {e}")
    if result.get("model_file_hashes_before") != result.get("model_file_hashes_after"):
        reasons.append("model_files_changed")
    if result.get("fit_guard") != "active":
        reasons.append("fit_guard_missing")
    if result.get("seeds") != proto["seeds"]["research"]:
        reasons.append("seeds_differ_from_protocol")
    if result.get("test_pairs") != proto["test"]["pairs"]:
        reasons.append("test_pairs_differ")
    names = [c["name"] for c in proto["grid"]["conditions"]]
    if [c["name"] for c in result.get("conditions", [])] != names:
        reasons.append("conditions_differ_from_protocol")
    grid = {(s, c) for s in proto["seeds"]["research"] for c in names}
    got = [(r.get("seed"), r.get("condition")) for r in result.get("rows", [])]
    if set(got) != grid or len(got) != len(grid):
        reasons.append("grid_incomplete_or_duplicated")
    for r in result.get("rows", []):
        vals = [r.get("mlp", {}).get("acc"), r.get("lda", {}).get("acc"), r.get("lda", {}).get("exact")]
        if not all(_finite01(v) for v in vals):
            reasons.append("non_finite_or_out_of_range_value")
            break
    return {"released": not reasons, "reasons": reasons}


def table(result: Dict) -> Dict:
    t: Dict = {}
    for r in result["rows"]:
        t.setdefault(r["condition"], {})[r["seed"]] = r
    return t


def delta_b(refs: Dict) -> Dict:
    """delta_B(c) = B(c0) - B(c) with its MC-SE; exactly 0 (SE 0) at c0; no seed interval."""
    c = refs["conditions"]
    b0, s0 = c["c0"]["B"], c["c0"]["B_se"]
    return {k: {"value": 0.0 if k == "c0" else b0 - v["B"], "mc_se": 0.0 if k == "c0" else math.sqrt(s0 ** 2 + v["B_se"] ** 2),
                "note": "MC estimate of a fixed model value; errors correlated across conditions through the shared B(c0)"}
            for k, v in c.items()}


def diagnostics(result: Dict, refs: Dict) -> Dict:
    c = refs["conditions"]
    out = {"D1": [], "D2": [], "D3": [], "D4": []}
    src = refs["d1_source"]
    tol = Z4 * math.sqrt(c["c0"]["B_se"] ** 2 + src["B_se"] ** 2)
    out["D1"].append({"diff": c["c0"]["B"] - src["B"], "tol": tol, "alarm": abs(c["c0"]["B"] - src["B"]) > tol})
    amp0 = c["c0"]["amplitude"]
    sig = sorted(((v["sigma"], k) for k, v in c.items() if v["amplitude"] == amp0), key=lambda x: x[0])
    for (s1, k1), (s2, k2) in zip(sig, sig[1:]):
        tol = Z4 * math.sqrt(c[k1]["B_se"] ** 2 + c[k2]["B_se"] ** 2)
        out["D2"].append({"lower_sigma": k1, "higher_sigma": k2, "increase": c[k2]["B"] - c[k1]["B"], "tol": tol,
                          "alarm": c[k2]["B"] > c[k1]["B"] + tol})
    for k, v in c.items():
        tol = Z4 * v["B_se"]
        out["D3"].append({"condition": k, "excess": v["lda_pop"]["acc"] - v["B"], "tol": tol, "alarm": v["lda_pop"]["acc"] > v["B"] + tol})
    for r in result.get("rows", []):
        tol = Z4 * r["lda"]["se_pair"]
        out["D4"].append({"seed": r["seed"], "condition": r["condition"], "diff": r["lda"]["exact"] - r["lda"]["acc"], "tol": tol,
                          "alarm": abs(r["lda"]["exact"] - r["lda"]["acc"]) > tol})
    alarms = [f"{k}:{i}" for k, lst in out.items() for i, x in enumerate(lst) if x["alarm"]]
    return {"checks": {k: len(v) for k, v in out.items()}, "alarms": alarms, "details": out,
            "rule": "statistical cross-checks at 4 SE, not proofs; an alarm withholds the confirmatory release pending a documented review; no repetition until passing"}


def _summ(vals, reps: int, seed: int) -> Dict:
    v = np.asarray(vals, float)
    t = e11.t_one_sided_p(v.tolist(), 0.0)
    return {"mean": float(v.mean()), "ci95_t": t["ci95_t"], "bootstrap95": e11.bootstrap(v, reps, seed)}


def descriptive(result: Dict, refs: Dict) -> Dict:
    proto = mc.load_protocol()
    bs = proto["uncertainty"]["bootstrap"]
    t, c, dB = table(result), refs["conditions"], delta_b(refs)
    seeds = result["seeds"]
    acc = {"mlp": lambda r: r["mlp"]["acc"], "lda_test": lambda r: r["lda"]["acc"], "lda_exact": lambda r: r["lda"]["exact"]}
    out = {"conditions": {}, "conventions": {
        "loss": "acc(c0) - acc(c), positive = worse than c0",
        "delta_G": "seed intervals conditional on the stored B values; the MC-SE of delta_B is reported alongside",
        "lda_split": "relative to the condition-specific POPULATION LDA (the LDA criterion), not to the best linear rule; "
                     "the second term includes the finite estimation of the fixed model",
        "mlp": "delta_G of the MLP mixes model class, mismatch, finite data and optimisation/regularisation; not attributed to a cause",
        "lda_decomposition_uses": "exact population accuracy of the fixed LDA rule"}}
    for name in c:
        row = {"B": c[name]["B"], "B_se": c[name]["B_se"], "delta_B": dB[name], "lda_pop": c[name]["lda_pop"]["acc"], "decoders": {}}
        for dec, f in acc.items():
            a = [f(t[name][s]) for s in seeds]
            a0 = [f(t["c0"][s]) for s in seeds]
            loss = [x0 - x for x0, x in zip(a0, a)]
            dG = [(c[name]["B"] - x) - (c["c0"]["B"] - x0) for x0, x in zip(a0, a)]
            d = {"acc": _summ(a, bs["reps"], bs["seed"]), "loss": _summ(loss, bs["reps"], bs["seed"]),
                 "delta_G": {**_summ(dG, bs["reps"], bs["seed"]), "extra_mc_se": dB[name]["mc_se"]}}
            if dec == "lda_exact":
                pop, pop0 = c[name]["lda_pop"]["acc"], c["c0"]["lda_pop"]["acc"]
                d["lda_split"] = {
                    "bayes_gap_of_lda_pop_change": (c[name]["B"] - pop) - (c["c0"]["B"] - pop0),
                    "gap_fixed_to_lda_pop_change": _summ([(pop - x) - (pop0 - x0) for x0, x in zip(a0, a)], bs["reps"], bs["seed"])}
            row["decoders"][dec] = d
        adv = [t[name][s]["mlp"]["acc"] - t[name][s]["lda"]["acc"] for s in seeds]
        adv0 = [t["c0"][s]["mlp"]["acc"] - t["c0"][s]["lda"]["acc"] for s in seeds]
        row["advantage_mlp_minus_lda_test"] = _summ(adv, bs["reps"], bs["seed"])
        row["advantage_change_vs_c0"] = _summ([x - x0 for x0, x in zip(adv0, adv)], bs["reps"], bs["seed"])
        out["conditions"][name] = row
    return out


def raised_endpoints(conds: List[Dict]) -> Dict[str, str]:
    """The pre-specified raised endpoints: largest amplitude (base sigma) and largest sigma (base amplitude)."""
    c0 = next(c for c in conds if c["name"] == "c0")
    amp = max((c for c in conds if c["sigma"] == c0["sigma"]), key=lambda c: c["amplitude"])
    sig = max((c for c in conds if c["amplitude"] == c0["amplitude"]), key=lambda c: c["sigma"])
    return {"R-a": amp["name"], "R-sigma": sig["name"]}


def confirmatory(result: Dict) -> Dict:
    proto = mc.load_protocol()
    cf = proto["confirmatory"]
    t = table(result)
    bs = proto["uncertainty"]["bootstrap"]
    ends = raised_endpoints(result["conditions"])
    if result.get("mode") in ("research", "smoke") and {k: v["condition"] for k, v in cf["tests"].items()} != ends:
        raise MemoryLabError("protocol endpoints are not the raised endpoints of the grid")
    tests, pv = {}, {}
    for key in cf["tests"]:
        cond = ends[key]
        diffs = [t[cond][s]["mlp"]["acc"] - t[cond][s]["lda"]["acc"] for s in result["seeds"]]
        r = e11.t_one_sided_p(diffs, cf["delta"])
        r["bootstrap95"] = e11.bootstrap(diffs, bs["reps"], bs["seed"])
        tests[key] = {"condition": cond, **r}
        pv[key] = r["p"]
    for key, h in e11.holm(pv, cf["alpha"]).items():
        tests[key].update(h)
        tests[key]["wording"] = "bestaetigt" if h["rejected"] else "nicht bestaetigt (Kriterium nicht erfuellt; weitere Aussagen nur mit Intervall)"
    return {"question": cf["question"], "delta": cf["delta"], "tests": tests, "not_tested": cf["not_tested"]}


def evaluate(result: Dict, refs: Dict) -> Dict:
    rel = release(result, refs) if result.get("mode") == "research" else {"released": False, "reasons": ["mode_is_not_research"]}
    diag = diagnostics(result, refs)
    out = {"release": rel, "diagnostics": diag, "descriptive": descriptive(result, refs), "confirmatory": confirmatory(result)}
    if not rel["released"]:
        out["confirmatory_label"] = "not released (descriptive only)"
    elif diag["alarms"]:
        out["confirmatory_label"] = "withheld pending documented review (diagnostic alarm)"
    else:
        out["confirmatory_label"] = "confirmatory (released)"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    ap.add_argument("--refs", type=Path, help="dev results only; research/smoke use the frozen artifact")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = json.loads(a.result.read_text(encoding="utf-8"))
    if res["mode"] == "dev":
        if a.refs is None:
            raise SystemExit("--refs is required for dev results")
        refs = mref.require_references("dev", a.refs)["refs"]
    else:
        if a.refs is not None:
            raise SystemExit("research/smoke results are evaluated with the frozen reference artifact only")
        refs = mref.require_references(res["mode"])["refs"]
    ev = evaluate(res, refs)
    mc.write_json_exclusive(a.out, ev)
    print(json.dumps({"released": ev["release"]["released"], "reasons": ev["release"]["reasons"][:6], "label": ev["confirmatory_label"],
                      "alarms": ev["diagnostics"]["alarms"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
