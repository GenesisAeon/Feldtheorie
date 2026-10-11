"""Runner for protocol SF-001-V2 (package V2). Writes raw per-replicate data.

    python -m experiments.kosmische_vererbung.sf001.run_v2 [--out DIR] [--force]

The evaluation is a separate step (evaluate_v2.py) that only reads the raw
file and the protocol.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

from . import branching

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v2.json"
DEFAULT_OUT = HERE / "runs" / "v2_s00_s01"


def text_sha256(path: Path) -> str:
    """SHA-256 of the file's text with LF line endings (checkout-independent)."""

    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inheritance_matrix(spec: dict, K: int) -> np.ndarray:
    if spec["kind"] == "mutation":
        return branching.mutation_matrix(K, spec["mu"])
    if spec["kind"] == "erasure":
        return branching.erasure_matrix(spec["pi"])
    raise ValueError(f"unknown inheritance kind {spec['kind']!r}")


def run(protocol: dict) -> dict:
    K = protocol["types"]
    raw = {"protocol_id": protocol["protocol_id"], "conditions": {}}
    for condition in protocol["conditions"]:
        M = inheritance_matrix(condition["inheritance"], K)
        b = protocol[condition["b"]]
        replicates = []
        for r in range(protocol["replicates"]):
            seed = np.random.SeedSequence(protocol["root_seed"], spawn_key=(r,))
            replicates.append(branching.simulate(M, b, protocol["founders_per_type"],
                                                 protocol["generations"], protocol["cap"], seed))
        raw["conditions"][condition["id"]] = {"M": M.tolist(), "b": b, "replicates": replicates}
    raw["provenance"] = {
        "protocol_sha256": text_sha256(PROTOCOL),
        "code_sha256": {name: text_sha256(HERE / name) for name in ("branching.py", "run_v2.py")},
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    return raw


def main(argv=None) -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true", help="overwrite an existing raw.json")
    args = parser.parse_args(argv)
    target = args.out / "raw.json"
    if target.exists() and not args.force:
        raise SystemExit(f"{target} exists; refusing to overwrite (use --force)")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    raw = run(protocol)
    args.out.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(raw, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {target}")
    return target


if __name__ == "__main__":
    main()
