"""Evaluation for protocol KV-V5c. Reads only protocol_v5c.json and raw.json.

    python -m experiments.kosmische_vererbung.chem.evaluate_v5c [--run DIR]

Does not import the kernel or the runner. Writes results.json, results.yaml,
RESULTS.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v5c.json"
DEFAULT_RUN = HERE / "runs" / "v5c_resolution"


def _series(raw):
    return {(r["scheme"], r["rule"], r["init"], r["k"], r["dt"]): r for r in raw["runs"]}


def _r(A, B):
    return [(a - b) / b for a, b in zip(A["mean_Z"], B["mean_Z"])]


def _converged(coarse, fine, tol):
    if coarse is None or fine is None:
        return "not_evaluated", None
    diff = abs(coarse - fine)
    return ("evaluated" if diff <= tol["atol"] + tol["rtol"] * abs(fine) else "numerical_failure"), diff


def evaluate(protocol: dict, raw: dict) -> dict:
    runs = _series(raw)
    dts = protocol["dt_myr"]
    coarse_dt, fine_dt = sorted(dts)[1], sorted(dts)[0]
    conv = protocol["convergence"]
    tol_p = {"atol": conv["pop3_mass_formed"]["atol_msun"], "rtol": conv["pop3_mass_formed"]["rtol"]}
    tol_r = conv["r"]
    out = {"protocol_id": protocol["protocol_id"], "raw_provenance": raw["provenance"],
           "failed_runs": [{k: r[k] for k in ("scheme", "rule", "init", "k", "dt", "error")} for r in raw["runs"] if r["state"] != "completed"],
           "max_budget_rel_error": max(max(r["series"]["budget_rel_error"]) for r in raw["runs"] if r["state"] == "completed"),
           "quantities": {}}

    def value(scheme, rule, k, dt, what):
        A, B = runs.get((scheme, rule, "A", k, dt)), runs.get((scheme, rule, "B", k, dt))
        if not A or not B or A["state"] != "completed" or B["state"] != "completed":
            return None
        if what == "pop3":
            return A["series"]["pop3_mass_formed"][-1]
        r = _r(A["series"], B["series"])
        return max(r, key=abs) if what == "r_max_signed" else r[-1]

    for rule in protocol["rules"]:
        for k in protocol["exchange_rates_per_myr"]:
            whats = ["r_max_signed", "r_final"] + (["pop3"] if rule == "P3" else [])
            for what in whats:
                tol = tol_p if what == "pop3" else tol_r
                entry = {}
                for scheme in protocol["schemes"]:
                    by_dt = {str(dt): value(scheme, rule, k, dt, what) for dt in dts}
                    state, diff = _converged(by_dt[str(coarse_dt)], by_dt[str(fine_dt)], tol)
                    entry[scheme] = {"by_dt": by_dt, "state": state, "finest_pair_abs_diff": diff}
                    fine = by_dt[str(fine_dt)]
                    if what != "pop3" and fine is not None and abs(fine) <= tol_r["atol"]:
                        entry[scheme]["note"] = "nicht von 0 unterscheidbar (|r| <= atol)"
                g, e = entry["grid"]["by_dt"][str(fine_dt)], entry["event"]["by_dt"][str(fine_dt)]
                entry["scheme_agreement_at_finest_dt"] = None if g is None or e is None else {
                    "abs_diff": abs(g - e), "within_tolerance": abs(g - e) <= tol["atol"] + tol["rtol"] * abs(e)}
                out["quantities"][f"{rule}|k={k}|{what}"] = entry
    out["event_splits_max"] = max(r["series"]["event_splits"] for r in raw["runs"] if r["state"] == "completed")
    return out


def render_markdown(protocol: dict, res: dict) -> str:
    p = res["raw_provenance"]
    lines = [
        f"# Ergebnis {protocol['protocol_id']}: Auflösungsstudie",
        "",
        f"Protokoll `protocol_v5c.json` (sha256 `{p['protocol_sha256'][:16]}…`), deterministisch. Python {p['python']}, NumPy {p['numpy']}, SciPy {p['scipy']}. "
        f"Fehlgeschlagene Läufe: {len(res['failed_runs'])}. Maximaler relativer Bilanzfehler: {res['max_budget_rel_error']:.1e}.",
        "",
        "Konvergenz: Vergleich der feinsten Schrittweiten 0,125 und 0,0625 mit absoluter und relativer Toleranz (siehe Protokoll).",
        "",
        "| Größe | Schema | dt 0,5 | dt 0,25 | dt 0,125 | dt 0,0625 | Status | Hinweis |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, entry in res["quantities"].items():
        for scheme in ("grid", "event"):
            e = entry[scheme]
            vals = [("–" if v is None else f"{v:.6g}") for v in e["by_dt"].values()]
            lines.append(f"| {name} | {scheme} | " + " | ".join(vals) + f" | {e['state']} | {e.get('note', '')} |")
    lines += ["", "Erwartungen (vor dem Lauf im Protokoll-Commit festgehalten):", ""]
    lines += [f"- {x}" for x in protocol["expectations"]] + [""]
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
