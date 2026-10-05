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
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and 0.0 <= x <= 1.0


def _se_ok(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x >= 0.0


def expected_layout(result: Dict) -> Dict:
    """What the result MUST look like, derived from the protocol and the mode alone."""
    proto = mc.load_protocol()
    mode = result.get("mode")
    if mode == "research":
        return {"conditions": mc.conditions(proto, "research"), "seeds": proto["seeds"]["research"], "pairs": proto["test"]["pairs"],
                "smode": proto["modes"]["research"]}
    if mode == "smoke":
        return {"conditions": mc.conditions(proto, "smoke"), "seeds": proto["seeds"]["smoke"], "pairs": proto["test"]["pairs"],
                "smode": proto["modes"]["smoke"]}
    if mode == "dev":
        seeds, pairs = result.get("seeds"), result.get("test_pairs")
        ok = isinstance(seeds, list) and seeds and all(isinstance(x, int) and not isinstance(x, bool) for x in seeds) \
            and isinstance(pairs, int) and not isinstance(pairs, bool) and pairs > 1
        return {"conditions": mc.conditions(proto, "dev"), "seeds": seeds if ok else None, "pairs": pairs if ok else None,
                "smode": proto["modes"]["dev"]}
    return {}


def structure_problems(result: Dict) -> List[str]:
    """Review M12-R5: complete, typed, finite, protocol-conform input -- checked BEFORE any
    diagnostic or confirmatory computation touches the values."""
    exp = expected_layout(result)
    if not exp:
        return ["unknown_mode"]
    if exp["seeds"] is None:
        return ["seeds_or_test_pairs_malformed"]
    bad: List[str] = []
    if result.get("conditions") != exp["conditions"]:
        bad.append("conditions_differ_from_protocol_grid")
    if result.get("seeds") != exp["seeds"]:
        bad.append("seeds_differ_from_protocol")
    if result.get("test_pairs") != exp["pairs"]:
        bad.append("test_pairs_differ")
    hb, ha = result.get("model_file_hashes_before"), result.get("model_file_hashes_after")
    if not isinstance(hb, dict) or not hb or not isinstance(ha, dict) or not ha:
        bad.append("model_file_hashes_missing")
    elif hb != ha:
        bad.append("model_files_changed")
    names = [c["name"] for c in exp["conditions"]]
    grid = {(sd, c) for sd in exp["seeds"] for c in names}
    rows = result.get("rows")
    if not isinstance(rows, list):
        return bad + ["rows_missing"]
    got = [(r.get("seed"), r.get("condition")) if isinstance(r, dict) else None for r in rows]
    if set(got) != grid or len(got) != len(grid):
        bad.append("grid_incomplete_or_duplicated")
    streams = {sd: {"test": [list(mc.stream(exp["smode"], sd, k, "test")[1]) for k in ("pattern", "noise")],
                    "train": [list(mc.stream(exp["smode"], sd, k, "train")[1]) for k in ("pattern", "noise")]} for sd in exp["seeds"]}
    flags = set()
    for r in rows:
        if not isinstance(r, dict) or r.get("seed") not in streams:
            flags.add("row_malformed")
            continue
        st = streams[r["seed"]]
        if r.get("test_streams") != st["test"]:
            flags.add("test_streams_not_the_expected_test_streams")
        if r.get("test_streams") == st["train"]:
            flags.add("test_streams_equal_training_streams")
        if r.get("n_test_pairs") != exp["pairs"] or isinstance(r.get("n_test_pairs"), bool):
            flags.add("row_test_pairs_differ")
        m, l, a = r.get("mlp"), r.get("lda"), r.get("advantage_test")
        if not all(isinstance(x, dict) for x in (m, l, a)):
            flags.add("row_values_missing")
            continue
        if not (_finite01(m.get("acc")) and _finite01(l.get("acc")) and _finite01(l.get("exact"))):
            flags.add("accuracy_not_finite_or_out_of_range")
        if not (_se_ok(m.get("se_pair")) and _se_ok(l.get("se_pair")) and _se_ok(a.get("se_pair"))):
            flags.add("standard_error_not_finite_or_negative")
        am = a.get("mean")
        if not (isinstance(am, (int, float)) and not isinstance(am, bool) and math.isfinite(am) and -1.0 <= am <= 1.0):
            flags.add("advantage_not_finite_or_out_of_range")
    return bad + sorted(flags)


def release(result: Dict, refs: Optional[Dict] = None) -> Dict:
    """Structural validity of a RESEARCH result (the confirmatory status is set in evaluate)."""
    reasons: List[str] = []
    if result.get("mode") != "research":
        reasons.append("mode_is_not_research")
    if result.get("status") != "complete" or result.get("failures"):
        reasons.append("run_not_complete")
    if any(v is not None for v in (result.get("overrides") or {}).values()):
        reasons.append("overrides_used")
    if result.get("fit_guard") != "active":
        reasons.append("fit_guard_missing")
    reasons += structure_problems(result)
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
            verified = mm.require_models("research")["file_hashes"]
            if result.get("model_file_hashes_before") != verified or result.get("model_file_hashes_after") != verified:
                reasons.append("model_file_hashes_not_the_verified_files")
    except Exception as e:                                    # any freeze problem blocks the release
        reasons.append(f"freeze_invalid: {type(e).__name__}: {e}")
    return {"structurally_valid": not reasons, "reasons": reasons}


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
    out["D1"].append({"diff": c["c0"]["B"] - src["B"], "tol": tol, "alarm": not abs(c["c0"]["B"] - src["B"]) <= tol})
    amp0 = c["c0"]["amplitude"]
    sig = sorted(((v["sigma"], k) for k, v in c.items() if v["amplitude"] == amp0), key=lambda x: x[0])
    for (s1, k1), (s2, k2) in zip(sig, sig[1:]):
        tol = Z4 * math.sqrt(c[k1]["B_se"] ** 2 + c[k2]["B_se"] ** 2)
        out["D2"].append({"lower_sigma": k1, "higher_sigma": k2, "increase": c[k2]["B"] - c[k1]["B"], "tol": tol,
                          "alarm": not c[k2]["B"] <= c[k1]["B"] + tol})
    for k, v in c.items():
        tol = Z4 * v["B_se"]
        out["D3"].append({"condition": k, "excess": v["lda_pop"]["acc"] - v["B"], "tol": tol, "alarm": not v["lda_pop"]["acc"] <= v["B"] + tol})
    for r in result.get("rows", []):
        tol = Z4 * r["lda"]["se_pair"]
        out["D4"].append({"seed": r["seed"], "condition": r["condition"], "diff": r["lda"]["exact"] - r["lda"]["acc"], "tol": tol,
                          "alarm": not abs(r["lda"]["exact"] - r["lda"]["acc"]) <= tol})
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


ALARM_RULE = ("an alarm withholds the confirmatory release until a documented review by Johann/Astra, referenced in a "
              "separate addendum; never an automatic rerun; computed p-values stay as a NOT released evaluation")


def evaluate(result: Dict, refs: Dict) -> Dict:
    """Review M12-R6: structural validity and confirmatory release are stored SEPARATELY;
    'released' is true only for a structurally valid research result WITHOUT diagnostic alarm.
    Malformed input is rejected before diagnostics and statistics touch it."""
    struct = structure_problems(result)
    if struct:
        return {"release": {"released": False, "structurally_valid": False, "reasons": struct, "confirmatory_status": "not_released",
                            "alarm_review_reference": None},
                "confirmatory_label": "rejected: malformed or incomplete result (no diagnostics, no statistics computed)"}
    rel = release(result, refs) if result.get("mode") == "research" else {"structurally_valid": False, "reasons": ["mode_is_not_research"]}
    diag = diagnostics(result, refs)
    conf = confirmatory(result)
    if not rel["structurally_valid"]:
        status = "not_released"
    elif diag["alarms"]:
        status = "withheld_diagnostic_alarm"
    else:
        status = "released"
    reasons = list(rel["reasons"]) + ([f"diagnostic_alarm: {', '.join(diag['alarms'])}"] if diag["alarms"] else [])
    for t in conf["tests"].values():
        if status != "released":
            t["wording"] = ("nicht freigegeben: Kriterium rechnerisch erfuellt" if t["rejected"] else
                            "nicht freigegeben: Kriterium rechnerisch nicht erfuellt") + f" ({status})"
    labels = {"released": "confirmatory (released)", "withheld_diagnostic_alarm": "withheld pending documented review (diagnostic alarm)",
              "not_released": "not released (descriptive only)"}
    return {"release": {"released": status == "released", "structurally_valid": rel["structurally_valid"], "reasons": reasons,
                        "confirmatory_status": status, "alarm_review_reference": None, "alarm_rule": ALARM_RULE},
            "diagnostics": diag, "descriptive": descriptive(result, refs), "confirmatory": conf, "confirmatory_label": labels[status]}


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
    print(json.dumps({"released": ev["release"]["released"], "structurally_valid": ev["release"]["structurally_valid"],
                      "confirmatory_status": ev["release"]["confirmatory_status"], "reasons": ev["release"]["reasons"][:6],
                      "label": ev["confirmatory_label"], "alarms": ev.get("diagnostics", {}).get("alarms")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
