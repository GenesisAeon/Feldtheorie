"""LR1: run the legacy probe once (separate process) and build the canonical registry snapshot.

    python experiments/lantern_reconstruction/tools/lr1_make_snapshot.py --out experiments/lantern_reconstruction/artifacts/registry_snapshot_v1 --probe-dir D:/mandala/.tmp/lantern-lr1/probe

The probe output stays outside the repo (it is regenerated, not versioned); the snapshot directory
(snapshot.npz + snapshot.json) is written exclusively.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.lantern_reconstruction import legacy_probe, registry_adapter  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--probe-dir", type=Path, required=True)
    ap.add_argument("--hashseed", default="0")
    a = ap.parse_args(argv)
    legacy_probe.run_probe(registry_adapter.REPO, a.probe_dir, hashseed=a.hashseed)
    man = registry_adapter.build_snapshot(a.probe_dir, a.out)
    snap = registry_adapter.load_snapshot(a.out)
    print(json.dumps({"snapshot": str(a.out), "canonical_sha256": snap.canonical_sha256, "container_sha256": snap.container_sha256,
                      "formula_check": man["formula_check"], "structure": man["structure"],
                      "global_rng": man["probe"]["global_rng"], "modules": man["probe"]["modules"]["count"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
