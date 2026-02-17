#!/usr/bin/env python3
"""Claim-to-Evidence Trace checker.

Reads ``docs/science/claim_evidence_registry.yaml`` and verifies that every
referenced artifact exists on disk.  Reports missing files so maintainers
can reconcile narrative claims with empirical evidence.

Usage
-----
Human-readable output::

    python scripts/check_claim_evidence.py

JSON output (for CI / Field Health Contract)::

    python scripts/check_claim_evidence.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
REGISTRY = BASE_DIR / "docs" / "science" / "claim_evidence_registry.yaml"


def load_registry(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def check_claims(registry: dict) -> list[dict]:
    """Check each claim's artifacts for existence.  Returns per-claim results."""
    results: list[dict] = []
    for claim in registry.get("claims", []):
        claim_id = claim.get("claim_id", "unknown")
        artifacts = claim.get("artifacts", [])
        missing: list[str] = []
        for artifact in artifacts:
            full_path = BASE_DIR / artifact
            if not full_path.exists():
                missing.append(artifact)
        results.append(
            {
                "claim_id": claim_id,
                "claim": claim.get("claim", ""),
                "source": claim.get("source", ""),
                "status": claim.get("status", "unknown"),
                "artifact_count": len(artifacts),
                "missing": missing,
                "ok": len(missing) == 0,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Check claim-to-evidence trace")
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY,
        help="Path to claim evidence registry YAML",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not args.registry.exists():
        print(f"ERROR: Registry not found: {args.registry}", file=sys.stderr)
        return 2

    registry = load_registry(args.registry)
    results = check_claims(registry)

    total = len(results)
    passed = sum(1 for r in results if r["ok"])
    missing_count = sum(len(r["missing"]) for r in results)

    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "registry": str(args.registry.relative_to(BASE_DIR)),
            "registry_version": registry.get("meta", {}).get("version", "unknown"),
        },
        "total_claims": total,
        "claims_with_evidence": passed,
        "missing_count": missing_count,
        "ok": missing_count == 0,
        "claims": results,
    }

    if args.json:
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    else:
        status = "ALL TRACED" if envelope["ok"] else "GAPS FOUND"
        print(f"Claim-to-Evidence Trace: {status}")
        print(f"  {passed}/{total} claims fully traced, {missing_count} missing artifacts")
        print()
        for r in results:
            icon = "PASS" if r["ok"] else "FAIL"
            print(f"  [{icon}] {r['claim_id']}: {r['claim'][:70]}")
            if r["missing"]:
                for m in r["missing"]:
                    print(f"         MISSING: {m}")
        print()

    return 0 if envelope["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
