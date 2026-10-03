"""Command line: python -m experiments.mandala_memory.cli run --mode smoke|research [--out DIR]

Sets BLAS threads to the protocol limit before NumPy is imported and keeps
TEMP/TMP on D:. The benchmark configuration is the frozen protocol file;
results land under the given output directory (not on C:).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "protocol" / "startkonfiguration.json"
DEFAULT_OUT = Path(r"D:/mandala/mandala-memory-results")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Mandala memory lab: pulse -> pause -> recall")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mode", choices=("smoke", "research"), required=True)
    r.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    r.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text(encoding="utf-8"))
    threads = str(cfg["limits"]["blas_threads"])
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, threads)
    os.environ.setdefault("TMP", r"D:/mandala/.tmp/mandala-memory")
    os.environ.setdefault("TEMP", r"D:/mandala/.tmp/mandala-memory")
    from experiments.mandala_memory.runner import run_experiment

    res = run_experiment(cfg, a.mode, a.out / a.mode)
    print(json.dumps({"run_id": res["run_id"], "status": res["status"], "seeds": res["seeds"],
                      "failed_seeds": res["failed_seeds"], "output": res["output_path"],
                      "resources": res["resources"]}, indent=1))
    return 0 if res["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
