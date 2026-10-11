"""Evaluation for protocol SF-001-V2. Reads only protocol_v2.json and raw.json.

    python -m experiments.kosmische_vererbung.sf001.evaluate_v2 [--run DIR]

Deliberately does not import the simulator (independent evaluation). The
deterministic reference recursion is re-implemented here from the protocol.
Writes results.json, results.yaml and RESULTS.md (trilayer).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v2.json"
DEFAULT_RUN = HERE / "runs" / "v2_s00_s01"
OPTIMUM = 2


def _matrix(spec: dict, K: int) -> np.ndarray:
    if spec["kind"] == "erasure":
        return np.tile(np.asarray(spec["pi"], dtype=float)[:, None], (1, K))
    mu = spec["mu"]
    M = np.eye(K) * (1 - mu)
    for i in range(K):
        nb = [j for j in (i - 1, i + 1) if 0 <= j < K]
        for j in nb:
            M[j, i] += mu / len(nb)
    return M


def reference_frequencies(M: np.ndarray, b, generations: int) -> list:
    p = np.full(len(b), 1.0 / len(b))
    for _ in range(generations):
        q = M @ (np.asarray(b) * p)
        p = q / q.sum()
    return p.tolist()


def misfit(counts) -> float:
    counts = np.asarray(counts, dtype=float)
    return float((counts * np.abs(np.arange(len(counts)) - OPTIMUM)).sum() / counts.sum())


def entropy_bits(counts) -> float:
    p = np.asarray(counts, dtype=float)
    p = p[p > 0] / p.sum()
    return float(-(p * np.log2(p)).sum())


def summary(values: list) -> dict:
    if not values:
        return {"state": "not_evaluated", "reason": "no surviving replicate"}
    a = np.asarray(values, dtype=float)
    return {"state": "evaluated", "n": len(values), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if len(a) > 1 else 0.0,
            "min": float(a.min()), "max": float(a.max())}


def evaluate(protocol: dict, raw: dict) -> dict:
    K, G = protocol["types"], protocol["generations"]
    out = {"protocol_id": protocol["protocol_id"], "root_seed": protocol["root_seed"],
           "raw_provenance": raw["provenance"], "conditions": {}}
    for condition in protocol["conditions"]:
        cid = condition["id"]
        reps = raw["conditions"][cid]["replicates"]
        b = protocol[condition["b"]]
        M = _matrix(condition["inheritance"], K)
        if not np.allclose(M, np.asarray(raw["conditions"][cid]["M"]), atol=1e-15, rtol=0):
            raise ValueError(f"{cid}: raw M differs from protocol")
        final = [r["type_counts"][G] for r in reps]
        alive = [c for c in final if sum(c) > 0]
        ref = reference_frequencies(M, b, G)
        out["conditions"][cid] = {
            "label": condition["label"],
            "replicates": len(reps),
            "E1_misfit": summary([misfit(c) for c in alive]),
            "E2_type_entropy_bits": summary([entropy_bits(c) for c in alive]),
            "E3_lineages_alive": summary([r["lineages_alive"][G] for r in reps]),
            "E4_extinct_fraction": sum(r["extinct_generation"] is not None for r in reps) / len(reps),
            "E5_individual_generations": summary([r["individual_generations"] for r in reps]),
            "restarts": sum(r["restarts"] for r in reps),
            "mean_final_type_frequencies": (np.asarray(alive, float) / np.asarray(alive, float).sum(1, keepdims=True)).mean(0).tolist() if alive else None,
            "reference_final_frequencies": ref,
            "reference_E1_misfit": float(np.dot(ref, np.abs(np.arange(K) - OPTIMUM))),
            "reference_E2_type_entropy_bits": entropy_bits(ref),
        }
    return out


def _fmt(s: dict, digits=3) -> str:
    if s.get("state") != "evaluated":
        return "nicht ausgewertet"
    return f"{s['mean']:.{digits}f} ± {s['sd']:.{digits}f}"


def render_markdown(protocol: dict, res: dict) -> str:
    lines = [
        f"# Ergebnis {protocol['protocol_id']}: S00/S01 Modellpopulationen",
        "",
        f"Protokoll `protocol_v2.json` (sha256 `{res['raw_provenance']['protocol_sha256'][:16]}…`), Wurzel-Seed {res['root_seed']}, "
        f"{protocol['replicates']} Replikate je Bedingung, {protocol['generations']} Generationen, Obergrenze {protocol['cap']}, 100 Gründer. "
        f"Python {res['raw_provenance']['python']}, NumPy {res['raw_provenance']['numpy']}.",
        "",
        "**Reichweite:** künstliche Modellpopulationen mit einer ausdrücklich künstlichen Reproduktionsregel. "
        "Keine Aussage über Kosmologie, Schwarze Löcher oder Naturkonstanten.",
        "",
        "Mittelwert ± Standardabweichung über Replikate (E1/E2 nur über nicht ausgestorbene Replikate). "
        "E1 ist durch Konstruktion an die Selektionsregel gebunden; E2–E5 gehen nicht in die Selektion ein.",
        "",
        "| Bedingung | E1 Fehlanpassung | E1 Referenz | E2 Typentropie [Bit] | E2 Referenz | E3 Gründerlinien | E4 ausgestorben | E5 Individuen-Generationen |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, c in res["conditions"].items():
        lines.append(
            f"| {cid}: {c['label']} | {_fmt(c['E1_misfit'])} | {c['reference_E1_misfit']:.3f} | "
            f"{_fmt(c['E2_type_entropy_bits'])} | {c['reference_E2_type_entropy_bits']:.3f} | "
            f"{_fmt(c['E3_lineages_alive'], 1)} | {c['E4_extinct_fraction']:.2f} | {_fmt(c['E5_individual_generations'], 0)} |")
    lines += [
        "",
        "Die Referenz ist die deterministische Frequenzrekursion ohne Obergrenze und ohne Drift. "
        "Sie ist kein Erwartungswert der endlichen Population (Plan §7) und dient nur zur Einordnung.",
        "",
        "Erwartungen aus den Regeln (vor dem Lauf im Protokoll festgehalten):",
        "",
    ] + [f"- {e}" for e in protocol["expectations_from_rules"]] + [""]
    return "\n".join(lines)


def main(argv=None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args(argv)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    raw = json.loads((args.run / "raw.json").read_text(encoding="utf-8"))
    res = evaluate(protocol, raw)
    (args.run / "results.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (args.run / "results.yaml").write_text(yaml.safe_dump(res, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    (args.run / "RESULTS.md").write_text(render_markdown(protocol, res), encoding="utf-8", newline="\n")
    print(render_markdown(protocol, res))
    return res


if __name__ == "__main__":
    main()
