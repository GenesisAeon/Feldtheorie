"""Evaluation for protocol KV-V5. Reads only protocol_v5.json and raw.json.

    python -m experiments.kosmische_vererbung.chem.evaluate_v5 [--run DIR]

Does not import the kernel. Writes results.json, results.yaml, RESULTS.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v5.json"
DEFAULT_RUN = HERE / "runs" / "v5_mean_vs_distribution"


def _index(raw):
    return {(r["rule"], r["init"], r["k"], r["dt"]): r["series"] for r in raw["runs"]}


def _rel(a, b):
    return abs(a - b) / abs(b) if b else (0.0 if a == b else float("inf"))


def evaluate(protocol: dict, raw: dict) -> dict:
    runs = _index(raw)
    dt0 = protocol["primary_dt_myr"]
    dt1 = min(protocol["dt_myr"])
    delta, tol = protocol["metrics"]["delta"], protocol["metrics"]["D4_tolerance"]
    res = {"protocol_id": protocol["protocol_id"], "raw_provenance": raw["provenance"], "rules": {}}
    for rule in protocol["rules"]:
        out = {"by_k": {}}
        C = runs[(rule, "C", 0.0, dt0)]
        for k in protocol["exchange_rates_per_myr"]:
            A, B = runs[(rule, "A", k, dt0)], runs[(rule, "B", k, dt0)]
            r = [(a - b) / b for a, b in zip(A["mean_Z"], B["mean_Z"])]
            t_sep = next((t for t, x in zip(A["t"], r) if abs(x) > delta), None)
            resolution = {}
            for init in ("A", "B"):
                lo, hi = runs[(rule, init, k, dt0)], runs[(rule, init, k, dt1)]
                dz = max(_rel(a, b) for a, b in zip(lo["mean_Z"], hi["mean_Z"]) if b)
                pa, pb = lo["pop3_mass_formed"][-1], hi["pop3_mass_formed"][-1]
                dp = _rel(pa, pb) if (pa or pb) else 0.0
                resolution[init] = {
                    "mean_Z_max_rel_diff": dz,
                    "mean_Z_state": "evaluated" if dz <= tol else "numerical_failure",
                    "pop3_mass_rel_diff": dp,
                    "pop3_mass_state": "evaluated" if dp <= tol else "numerical_failure",
                }
            out["by_k"][str(k)] = {
                "r_max_abs": max(abs(x) for x in r),
                "r_signed_at_max": max(r, key=abs),
                "r_final": r[-1],
                "t_sep_myr": t_sep,
                "t": A["t"], "r": r,
                "f0_A": A["f0"], "f0_B": B["f0"],
                "f_primordial_origin_A": A["f_primordial_origin"],
                "pop3_mass_A": A["pop3_mass_formed"][-1], "pop3_mass_B": B["pop3_mass_formed"][-1],
                "synthesized_O_A": A["synthesized_O"][-1], "synthesized_O_B": B["synthesized_O"][-1],
                "budget_rel_error_max": max(max(A["budget_rel_error"]), max(B["budget_rel_error"])),
                "resolution": resolution,
            }
        B0 = runs[(rule, "B", 0.0, dt0)]
        out["D2_B_vs_C_max_rel_diff"] = max(_rel(b, c) for b, c in zip(B0["mean_Z"], C["mean_Z"]))
        out["oracle5_t0"] = {"mean_Z_A": runs[(rule, "A", 0.0, dt0)]["mean_Z"][0], "mean_Z_B": B0["mean_Z"][0],
                             "f0_A": runs[(rule, "A", 0.0, dt0)]["f0"][0], "f0_B": B0["f0"][0]}
        res["rules"][rule] = out
    return res


def _num(x, fmt=".2e"):
    return "–" if x is None else format(x, fmt)


def render_markdown(protocol: dict, res: dict) -> str:
    p = res["raw_provenance"]
    lines = [
        f"# Ergebnis {protocol['protocol_id']}: Mittelwert gegen Verteilung",
        "",
        f"Protokoll `protocol_v5.json` (sha256 `{p['protocol_sha256'][:16]}…`), deterministisch, dt {protocol['primary_dt_myr']} Myr "
        f"(Auflösungsprüfung mit {min(protocol['dt_myr'])} Myr), {protocol['duration_myr']:.0f} Myr. "
        f"Python {p['python']}, NumPy {p['numpy']}, SciPy {p['scipy']}.",
        "",
        "**Reichweite:** synthetisches Zwei-Zonen-Modell mit deklarierten Erträgen. Keine Sternphysik, keine Beobachtungsaussage, kein JWST-Bezug.",
        "",
        "r(t) = (Z̄_A − Z̄_B)/Z̄_B: A heterogen (Z = 0 und 0,02), B homogen (0,01 und 0,01); beide Anfangszustände haben dasselbe Z̄ = 0,01.",
        "",
        "| Regel | k [1/Myr] | max abs(r) (Vorzeichen) | r bei 100 Myr | t_sep [Myr] | Pop-III-Masse A [M☉] | Auflösung Z̄ (A/B) | Auflösung Pop III (A) | Bilanzfehler |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for rule, out in res["rules"].items():
        for k, c in out["by_k"].items():
            ra, rb = c["resolution"]["A"], c["resolution"]["B"]
            lines.append(
                f"| {rule} | {k} | {_num(c['r_signed_at_max'], '+.3e')} | {_num(c['r_final'], '+.3e')} | {_num(c['t_sep_myr'], '.1f')} | "
                f"{c['pop3_mass_A']:.4g} | {ra['mean_Z_state']} ({ra['mean_Z_max_rel_diff']:.1e}) / {rb['mean_Z_state']} ({rb['mean_Z_max_rel_diff']:.1e}) | "
                f"{ra['pop3_mass_state']} ({ra['pop3_mass_rel_diff']:.1e}) | {c['budget_rel_error_max']:.1e} |")
    lines += ["", "| Regel | Z̄ B gegen C (max rel.) | Orakel 5 bei t = 0: Z̄_A, Z̄_B, f0_A, f0_B |", "|---|---|---|"]
    for rule, out in res["rules"].items():
        o = out["oracle5_t0"]
        lines.append(f"| {rule} | {out['D2_B_vs_C_max_rel_diff']:.1e} | {o['mean_Z_A']:.6g}, {o['mean_Z_B']:.6g}, {o['f0_A']:.3g}, {o['f0_B']:.3g} |")
    lines += ["", "Erwartungen aus den Regeln (vor dem Lauf im Protokoll-Commit festgehalten):", ""]
    lines += [f"- {e}" for e in protocol["expectations_from_rules"]] + [""]
    return "\n".join(lines)


def main(argv=None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args(argv)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    res = evaluate(protocol, json.loads((args.run / "raw.json").read_text(encoding="utf-8")))
    (args.run / "results.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (args.run / "results.yaml").write_text(yaml.safe_dump(res, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    (args.run / "RESULTS.md").write_text(render_markdown(protocol, res), encoding="utf-8", newline="\n")
    print("wrote results")
    return res


if __name__ == "__main__":
    main()
