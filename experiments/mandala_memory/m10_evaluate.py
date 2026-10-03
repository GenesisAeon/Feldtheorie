"""M10 evaluation of one result file (protocol/m10_protokoll.json).

- diagnostics A1, A2 (structural + numeric), A3 (numeric) with the fixed alarm
  policy: a 4-SE exceedance is a statistical ALARM, reported, never repaired and
  never repeated until it passes;
- level B interference I_n(b) = acc_B,n(K0) - acc_B,n(b) with MC SE;
- confirmatory family {H-N, H-F+} (one-sided, delta, Z from MC SEs, SE = 0 rule,
  Holm) -- only RELEASED for a complete research run with the frozen protocol;
  otherwise the same numbers are labelled descriptive;
- level D: descriptive paired seed differences with whole-seed bootstrap.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import NormalDist
from typing import Dict, List, Optional

import numpy as np

from experiments.mandala_memory import m10_task as mt

ND = NormalDist()


def b_table(result: Dict) -> Dict:
    return {(r["network"], r["nonlinearity"], r["condition"], r["delay"]): r for r in result["level_B"]}


def interference(tab: Dict, net: str, nl: str, cond: str, d: int, task: str = "preserve") -> Dict:
    k0, c = tab[(net, nl, "K0", d)][task], tab[(net, nl, cond, d)][task]
    return {"I": k0["estimate"] - c["estimate"], "se": float(np.hypot(k0["se"], c["se"])),
            "acc_K0": k0["estimate"], "acc_cond": c["estimate"]}


def one_sided_p(delta_hat: float, se: float, delta: float) -> float:
    if se == 0.0:                                         # protocol: se_zero_rule
        return 0.0 if delta_hat > delta else 1.0
    return 1.0 - ND.cdf((delta_hat - delta) / se)


def holm(pvals: Dict[str, float], alpha: float) -> Dict[str, Dict]:
    order = sorted(pvals, key=lambda k: pvals[k])
    m = len(order)
    out, still = {}, True
    running = 0.0
    for i, k in enumerate(order):
        adj = min(1.0, (m - i) * pvals[k])
        running = max(running, adj)                      # monotone adjusted p
        reject = still and pvals[k] <= alpha / (m - i)
        still = still and reject
        out[k] = {"p": pvals[k], "p_holm": running, "rejected": reject}
    return out


def wording(rejected: bool, delta_hat: float, se: float) -> str:
    if rejected:
        return "bestaetigt"
    if delta_hat + 1.96 * se < 0:
        return "Richtung widerspricht der Hypothese"
    return "nicht bestaetigt"


def confirmatory(result: Dict, proto: Dict) -> Dict:
    cf = proto["confirmatory"]
    tab, d, delta = b_table(result), cf["delay"], cf["delta"]
    if result["mode"] == "dev":
        cn, cf_ = "Ndev", "Fdev"                             # development stand-ins, never confirmatory
    else:
        cn, cf_ = "N", "Fplus"
    i_mod_n, i_uni_n = interference(tab, "modular", "tanh", cn, d), interference(tab, "uniform", "tanh", cn, d)
    i_uni_f, i_mod_f = interference(tab, "uniform", "tanh", cf_, d), interference(tab, "modular", "tanh", cf_, d)
    contrasts = {
        "H-N": {"delta_hat": i_mod_n["I"] - i_uni_n["I"], "se": float(np.hypot(i_mod_n["se"], i_uni_n["se"]))},
        "H-F+": {"delta_hat": i_uni_f["I"] - i_mod_f["I"], "se": float(np.hypot(i_uni_f["se"], i_mod_f["se"]))},
    }
    pv = {k: one_sided_p(v["delta_hat"], v["se"], delta) for k, v in contrasts.items()}
    h = holm(pv, cf["holm"]["alpha"])
    for k, v in contrasts.items():
        v.update(h[k])
        v["ci95_unadjusted"] = [v["delta_hat"] - 1.96 * v["se"], v["delta_hat"] + 1.96 * v["se"]]
        v["wording"] = wording(v["rejected"], v["delta_hat"], v["se"])
    return {"delta": delta, "alpha": cf["holm"]["alpha"], "contrasts": contrasts,
            "components": {"I_modular_N": i_mod_n, "I_uniform_N": i_uni_n, "I_uniform_F+": i_uni_f, "I_modular_F+": i_mod_f}}


def numeric_diagnostics(result: Dict, proto: Dict) -> Dict:
    tab = b_table(result)
    N, rows = proto["network"]["N"], []
    for (net, nl, cname, d), r in tab.items():
        if nl != "identity" or cname == "K0":
            continue
        perm = mt.swap_permutation(N, proto["networks"][net]["M"])
        cond = proto["conditions"].get(cname) or proto["development"]["conditions"].get(cname)
        i = interference(tab, net, nl, cname, d)
        a3_alarm = i["acc_cond"] > i["acc_K0"] + 4 * i["se"]
        row = {"network": net, "condition": cname, "delay": d, "I": i["I"], "se": i["se"], "A3_alarm": a3_alarm}
        if mt.condition_is_p_fixed(perm, cond):
            row["A2_alarm"] = abs(i["I"]) > 4 * i["se"]
        rows.append(row)
    return {"rows": rows, "n_A2_checks": sum("A2_alarm" in r for r in rows), "n_A3_checks": len(rows),
            "alarms": [r for r in rows if r["A3_alarm"] or r.get("A2_alarm")],
            "policy": proto["diagnostics"]["alarm_policy"]}


def release(result: Dict) -> Dict:
    from experiments.mandala_memory.m10_run import FROZEN_PROTOCOL_SHA256, protocol_sha256

    reasons = []
    if result["mode"] != "research":
        reasons.append("mode_is_not_research")
    if result["status"] != "complete" or result["failures"]:
        reasons.append("run_not_complete")
    if FROZEN_PROTOCOL_SHA256 is None:
        reasons.append("protocol_not_frozen")
    elif result["protocol_sha256"] != FROZEN_PROTOCOL_SHA256 or protocol_sha256() != FROZEN_PROTOCOL_SHA256:
        reasons.append("protocol_differs_from_frozen")
    if any(v not in (None, False) for v in result.get("overrides", {}).values()):
        reasons.append("overrides_used")
    return {"released": not reasons, "reasons": reasons}


def bootstrap(values: List[float], reps: int, seed: int) -> Dict:
    v = np.asarray(values, float)
    if v.size < 2:
        return {"mean": float(v.mean()) if v.size else None, "ci95": None}
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed])))
    means = v[rng.integers(0, v.size, size=(reps, v.size))].mean(axis=1)
    return {"mean": float(v.mean()), "ci95": [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
            "label": "descriptive, unadjusted, whole-seed bootstrap"}


def level_d_summary(result: Dict, proto: Dict) -> List[Dict]:
    bs = proto["level_D"]["bootstrap"]
    rows = {}
    for r in result["level_D"]:
        rows.setdefault((r["network"], r["nonlinearity"], r["delay"]), {}).setdefault(r["seed"], {})[r["condition"]] = r
    out = []
    for (net, nl, d), by_seed in sorted(rows.items()):
        conds = sorted({c for s in by_seed.values() for c in s if c != "K0"})
        for c in conds:
            for dec in ("nearest_mean", "lda_ledoit_wolf"):
                diffs = [s["K0"]["preserve"][dec] - s[c]["preserve"][dec] for s in by_seed.values()]
                upd = [s[c]["update"][dec] for s in by_seed.values()]
                out.append({"network": net, "nonlinearity": nl, "delay": d, "condition": c, "decoder": dec,
                            "preserve_interference": bootstrap(diffs, bs["reps"], bs["seed"]),
                            "update_accuracy": bootstrap(upd, bs["reps"], bs["seed"])})
    return out


def evaluate(result: Dict) -> Dict:
    proto = mt.load_protocol()
    rel = release(result)
    conf = confirmatory(result, proto) if 4 in result["delays"] else None
    return {"run_id": result.get("run_id"), "mode": result["mode"], "release": rel,
            "confirmatory": conf, "confirmatory_label": "confirmatory (released)" if rel["released"] else
            "DESCRIPTIVE ONLY -- not released: " + ", ".join(rel["reasons"]),
            "deterministic_diagnostics": {
                "A1_all_as_expected": all(r["A1_as_expected"] for r in result["diagnostics"]),
                "A2_structural_all_hold": all(r["A2_structural"]["holds"] for r in result["diagnostics"] if "A2_structural" in r)},
            "numeric_diagnostics": numeric_diagnostics(result, proto),
            "level_D": level_d_summary(result, proto) if result["level_D"] else [],
            "evidence": {"level_B": "numerical_sample (MC) of a deterministic model quantity", "level_D": "numerical_sample",
                         "empirical_status": "synthetic_only"}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    a = ap.parse_args(argv)
    ev = evaluate(json.loads(a.result.read_text(encoding="utf-8")))
    print(json.dumps({k: ev[k] for k in ("mode", "release", "confirmatory_label", "deterministic_diagnostics")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
