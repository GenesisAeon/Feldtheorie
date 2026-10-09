"""Local readiness check for the research start (LR7; review LANTERN_LR6_REVIEW_29af52f R4). It deliberately depends on
THIS machine: freeze present and valid, code equal to the frozen identity, and the EXACT frozen Python, NumPy and SciPy.
Every deviation is named; exit code 0 only if runs.create_research_run() would be allowed. Nothing is created or run.

    python experiments/lantern_reconstruction/tools/lr7_readiness.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parents[1]))
from experiments.lantern_reconstruction import runs  # noqa: E402


def main() -> int:
    r = runs.research_readiness()
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0 if r["research_start_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
