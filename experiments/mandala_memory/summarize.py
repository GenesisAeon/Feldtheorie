"""Descriptive per-delay summary of a result file: mean and per-seed values of
the balanced accuracy for every condition. No inference, no aggregate score.

    python -m experiments.mandala_memory.summarize RESULT.json [--markdown]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONDITIONS = ["frozen", "adapted", "adapted_with_frozen_decoder", "uncoupled_leak", "linear", "uniform_M1",
              "renamed_M3_c8_11", "reset_control", "sum_observation_frozen", "permutation_frozen_decoder",
              "permutation_refit_decoder"]


def table(result: dict) -> dict:
    out = {}
    delays = list(result["runs"][0]["delays"]) if result["runs"] else []
    for d in delays:
        out[d] = {}
        for c in CONDITIONS:
            vals = [run["delays"][d][c]["balanced_accuracy"] for run in result["runs"]]
            out[d][c] = {"mean": sum(vals) / len(vals), "per_seed": vals}
    return out


def markdown(result: dict) -> str:
    t = table(result)
    head = ["d"] + CONDITIONS
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for d, row in t.items():
        lines.append("| " + " | ".join([d] + [f"{row[c]['mean']:.3f}" for c in CONDITIONS]) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args(argv)
    r = json.loads(a.result.read_text(encoding="utf-8"))
    print(markdown(r) if a.markdown else json.dumps(table(r), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
