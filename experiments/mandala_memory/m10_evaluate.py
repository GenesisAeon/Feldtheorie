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


def _finite(*xs) -> bool:
    return all(isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x) for x in xs)


def completeness(result: Dict, proto: Dict) -> List[str]:
    """Review R9: the expected grid is derived from the PROTOCOL alone (never from
    the result's own metadata) and compared row by row with the data."""
    from experiments.mandala_memory.data import stream

    problems: List[str] = []
    nets, nls = ("modular", "uniform"), ("tanh", "identity")
    conds, delays = proto["conditions"], proto["delays"]["all"]
    lb, ld = proto["level_B"], proto["level_D"]
    if result.get("delays") != delays:
        problems.append("delays_differ_from_protocol")
    if result.get("n_mc") != lb["n_mc"]:
        problems.append("n_mc_differs_from_protocol")
    if result.get("seeds") != ld["seeds"]:
        problems.append("seeds_differ_from_protocol")
    # level B: exactly one row per (network, nonlinearity, condition, delay)
    expected_b = {(n, nl, c, d) for n in nets for nl in nls for c in conds for d in delays}
    keys_b = [(r.get("network"), r.get("nonlinearity"), r.get("condition"), r.get("delay")) for r in result.get("level_B", [])]
    if len(keys_b) != len(set(keys_b)):
        problems.append("level_B_duplicate_rows")
    if set(keys_b) - expected_b:
        problems.append("level_B_extra_rows")
    if expected_b - set(keys_b):
        problems.append("level_B_missing_rows")
    for r, key in zip(result.get("level_B", []), keys_b):
        if key not in expected_b:
            continue
        n, nl, c, d = key
        if conds[c] is None:
            pv = r.get("preserve") or {}
            if (r.get("update") is not None or pv.get("n") != 0 or not _finite(pv.get("estimate"), pv.get("se"))
                    or not 0.5 <= pv["estimate"] <= 1 or pv["se"] != 0.0):        # K0 is analytic: SE exactly 0
                problems.append(f"level_B_K0_invalid:{key}")
            continue
        for task in ("preserve", "update"):
            v = r.get(task) or {}
            want = list(stream("m10bayes", lb["streams"]["base_seed"], task, n, nl, c, d)[1])
            if v.get("n") != lb["n_mc"] or v.get("block") != lb["block"]:
                problems.append(f"level_B_wrong_n:{task}:{key}")
            if v.get("stream") != want:
                problems.append(f"level_B_foreign_stream:{task}:{key}")
            if not _finite(v.get("estimate"), v.get("se")) or not 0.5 <= v["estimate"] <= 1 or v["se"] < 0:
                problems.append(f"level_B_non_finite_or_out_of_range:{task}:{key}")
    # level D: exactly one row per (seed, delay, network, nonlinearity, condition)
    expected_d = {(s, d, n, nl, c) for s in ld["seeds"] for d in delays for n in nets for nl in nls for c in conds}
    rows_d = result.get("level_D", [])
    keys_d = [(r.get("seed"), r.get("delay"), r.get("network"), r.get("nonlinearity"), r.get("condition")) for r in rows_d]
    if len(keys_d) != len(set(keys_d)):
        problems.append("level_D_duplicate_rows")
    if set(keys_d) - expected_d:
        problems.append("level_D_extra_rows")
    if expected_d - set(keys_d):
        problems.append("level_D_missing_rows")
    n_tr, n_te = 2 * ld["n_train_per_class"], 2 * ld["n_test_per_class"]
    no_pulse = _no_pulse_counts(ld, delays)
    for r, key in zip(rows_d, keys_d):
        if key not in expected_d:
            continue
        s, d, n, nl, c = key
        want = {role: [list(stream("m10", s, kind, role, d)[1]) for kind in ("pattern", "noise")]
                for role in ("decoder_train", "test")}
        if r.get("streams") != want:
            problems.append(f"level_D_foreign_stream:{key}")
        chk = r.get("checks")
        if not isinstance(chk, dict) or set(chk) != REQUIRED_D_CHECKS or any(v is not True for v in chk.values()):
            problems.append(f"level_D_control_failed:{key}")
        pv = r.get("preserve") or {}
        if not _exact_int(pv, n_train=n_tr, n_test=n_te, n_excluded_test=0):
            problems.append(f"level_D_wrong_n:{key}")
        if not _accuracies(pv):
            problems.append(f"level_D_non_finite:{key}")
        up = r.get("update")
        k_tr, k_te = no_pulse[(s, d, "decoder_train")], no_pulse[(s, d, "test")]
        if (conds[c] is None) != (up is None):
            problems.append(f"level_D_update_presence:{key}")
        elif up is not None and not (_exact_int(up, n_train=n_tr - 2 * k_tr, n_test=n_te - 2 * k_te,
                                                n_excluded_test=2 * k_te) and _accuracies(up)):
            problems.append(f"level_D_update_invalid:{key}")
    # deterministic diagnostics: one row per non-K0 (network, nonlinearity, condition, delay), all as expected
    expected_g = {(n, nl, c, d) for n in nets for nl in nls for c in conds if conds[c] is not None for d in delays}
    keys_g = [(r.get("network"), r.get("nonlinearity"), r.get("condition"), r.get("delay")) for r in result.get("diagnostics", [])]
    if len(keys_g) != len(set(keys_g)) or set(keys_g) != expected_g:
        problems.append("diagnostics_grid_incomplete")
    tol1, tol2 = proto["diagnostics"]["A1"]["tol_rel"], proto["diagnostics"]["A2_structural"]["tol"]
    for r, key in zip(result.get("diagnostics", []), keys_g):
        if key not in expected_g:
            continue
        n, nl, c, d = key
        fixed = mt.condition_is_p_fixed(mt.swap_permutation(proto["network"]["N"], proto["networks"][n]["M"]), conds[c])
        a1 = r.get("A1")
        a1_ok = (isinstance(a1, dict) and _finite(a1.get("max_rel_deviation")) and a1["max_rel_deviation"] >= 0
                 and a1.get("tol_rel") == tol1 and a1.get("holds") is (a1["max_rel_deviation"] <= tol1)
                 and r.get("p_fixed") is fixed and r.get("A1_expected") is fixed
                 and r.get("A1_as_expected") is True and a1["holds"] is fixed)
        if not a1_ok:
            problems.append(f"A1_not_as_expected:{key}")
        need_a2 = nl == "identity" and fixed                   # derived from protocol, NOT from the result
        a2 = r.get("A2_structural")
        if need_a2:
            if not (isinstance(a2, dict) and _finite(a2.get("max_norm_antisymmetric_part"))
                    and a2["max_norm_antisymmetric_part"] >= 0 and a2.get("tol") == tol2
                    and a2.get("holds") is True and a2["max_norm_antisymmetric_part"] <= tol2):
                problems.append(f"A2_structural_failed:{key}")
        elif a2 is not None:
            problems.append(f"A2_structural_unexpected:{key}")
    return problems


REQUIRED_D_CHECKS = {"ids_disjoint", "streams_disjoint", "train_identical_pattern_counts", "test_identical_pattern_counts"}


def _exact_int(d: Dict, **want) -> bool:
    return all(type(d.get(k)) is int and d.get(k) == v for k, v in want.items())


def _accuracies(d: Dict) -> bool:
    return all(_finite(d.get(k)) and 0.0 <= d[k] <= 1.0 for k in ("nearest_mean", "lda_ledoit_wolf"))


def _no_pulse_counts(ld: Dict, delays) -> Dict:
    """Number of drawn patterns without any pulse per (seed, delay, role), reconstructed
    WITHOUT network dynamics from the fixed pattern streams (each drawn pattern is used
    for one A and one B episode, so the excluded episodes are twice this number)."""
    from experiments.mandala_memory.data import stream

    pats = mt.patterns()
    probs = np.array([float(pr) for _, pr in pats])
    none = next(i for i, (pat, _) in enumerate(pats) if mt.last_channel(pat) is None)
    out = {}
    for s in ld["seeds"]:
        for d in delays:
            for role, n in (("decoder_train", ld["n_train_per_class"]), ("test", ld["n_test_per_class"])):
                pi = stream("m10", s, "pattern", role, d)[0].choice(len(pats), size=n, p=probs / probs.sum())
                out[(s, d, role)] = int(np.sum(pi == none))
    return out


def release(result: Dict) -> Dict:
    """Confirmatory release only for a complete research run with the frozen protocol
    and code (reviews R2-analogue, R9, R10)."""
    from experiments.mandala_memory import m10_run

    reasons = []
    if result.get("mode") != "research":
        reasons.append("mode_is_not_research")
    if result.get("status") != "complete" or result.get("failures"):
        reasons.append("run_not_complete")
    if m10_run.FROZEN_PROTOCOL_SHA256 is None:
        reasons.append("protocol_not_frozen")
    else:
        if result.get("protocol_sha256") != m10_run.FROZEN_PROTOCOL_SHA256 or m10_run.protocol_sha256() != m10_run.FROZEN_PROTOCOL_SHA256:
            reasons.append("protocol_differs_from_frozen")
        try:
            rec = m10_run.require_frozen("release")
            if result.get("code_sha256") != rec["code_sha256"]:
                reasons.append("code_differs_from_frozen")
        except Exception as e:
            reasons.append(f"freeze_invalid: {e}")
    if any(v not in (None, False) for v in result.get("overrides", {}).values()):
        reasons.append("overrides_used")
    reasons += completeness(result, mt.load_protocol())
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


def _safe(fn, *args):
    try:
        return fn(*args)
    except (KeyError, TypeError) as e:                 # incomplete data: reported, never released
        return {"not_computable": f"{type(e).__name__}: {e}"}


def evaluate(result: Dict) -> Dict:
    proto = mt.load_protocol()
    rel = release(result)
    try:
        conf = confirmatory(result, proto)
    except (KeyError, TypeError) as e:                 # incomplete data: not computable (and never released)
        conf = {"not_computable": f"{type(e).__name__}: {e}"}
    return {"run_id": result.get("run_id"), "mode": result["mode"], "release": rel,
            "confirmatory": conf, "confirmatory_label": "confirmatory (released)" if rel["released"] else
            "DESCRIPTIVE ONLY -- not released: " + ", ".join(rel["reasons"]),
            "deterministic_diagnostics": {
                "A1_all_as_expected": all(r["A1_as_expected"] for r in result["diagnostics"]),
                "A2_structural_all_hold": all(r["A2_structural"]["holds"] for r in result["diagnostics"] if "A2_structural" in r)},
            "numeric_diagnostics": _safe(numeric_diagnostics, result, proto),
            "level_D": _safe(level_d_summary, result, proto) if result.get("level_D") else [],
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
