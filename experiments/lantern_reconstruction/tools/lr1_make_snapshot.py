"""LR1: run the legacy probe once (separate process) and build the canonical registry snapshot.

    python experiments/lantern_reconstruction/tools/lr1_make_snapshot.py --out experiments/lantern_reconstruction/artifacts/registry_snapshot_v2 --probe-dir D:/mandala/.tmp/lantern-lr1/probe-v2

Prints the two pins (canonical + manifest SHA-256). They are then entered ONCE into
registry_adapter.SNAPSHOT_PIN (reviewed code) -- the artifact never pins itself.
"""
from __future__ import annotations

import argparse
import hashlib
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
    pins = {"canonical_sha256": man["hashes"]["canonical_sha256"],
            "manifest_sha256": hashlib.sha256((a.out / "snapshot.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest()}
    snap = registry_adapter.load_snapshot(a.out, canonical_pin=pins["canonical_sha256"], manifest_pin=pins["manifest_sha256"])
    print(json.dumps({"snapshot": str(a.out), "pins": pins, "structure": dict(snap.structure),
                      "formula_check": man["formula_check"], "global_rng": man["probe"]["global_rng"],
                      "modules": man["import_manifest"]["count"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
