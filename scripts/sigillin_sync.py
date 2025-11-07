#!/usr/bin/env python3
"""Sigillin Sync Telemetry Harness

This utility inspects Sigillin trilayers (YAML/JSON/MD) and produces a
telemetry report so Metaquest compasses can quote fresh timestamps and
Codex IDs.  It keeps the logistic quartet explicit: R measures the number
of outstanding trilayer sync actions, Θ is the expectation that each
trilayer shares the same meta.sigil/meta.version fields, β≈4.6 sharpens
any drift detection, and ζ(R) is damped when we log sync runs in the
Codex before automation escalates.

Usage examples
--------------
1. Create a report for the Metaquest trilayers referenced in the
   compasses:

   ``python scripts/sigillin_sync.py report --roots seed/bedeutungssigillin/metaquest --roots seed/shadow_sigillin/metaquest``

2. Store the report in machine-readable form for downstream automation:

   ``python scripts/sigillin_sync.py report --roots seed --output analysis/sigillin_sync/latest.json``

3. Stamp the Codex with a sync event (adds a short entry to
   `seed/codexfeedback.md` and friends):

   ``python scripts/sigillin_sync.py stamp --codex-id mq-sync-2025-12-09 --note "Tri-layer status harvest"``

The script is intentionally conservative: it **never mutates Sigillin
content**.  Instead it reports the logistic state so humans (or future
automation) can decide whether to update metadata fields or propagate
new timestamps.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
CODEX_BASE = BASE_DIR / "seed" / "codexfeedback"


@dataclass
class TrilayerStatus:
    """Represents the resonance state of a trilayer grouping."""

    base_path: Path
    sigil: Optional[str]
    version: Optional[str]
    updated: Optional[str]
    json_version: Optional[str]
    json_updated: Optional[str]
    md_present: bool
    gaps: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "path": self.base_path.as_posix(),
            "sigil": self.sigil,
            "version": self.version,
            "updated": self.updated,
            "json_version": self.json_version,
            "json_updated": self.json_updated,
            "md_present": self.md_present,
            "gaps": self.gaps,
        }


def discover_trilayers(roots: Sequence[Path]) -> List[Path]:
    trilayers: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for yaml_path in root.rglob("*.yaml"):
            base = yaml_path.with_suffix("")
            json_path = base.with_suffix(".json")
            md_path = base.with_suffix(".md")
            if json_path.exists() and md_path.exists():
                trilayers.append(base)
    return sorted(set(trilayers))


def load_yaml(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def inspect_trilayer(base: Path) -> TrilayerStatus:
    yaml_data = load_yaml(base.with_suffix(".yaml"))
    json_path = base.with_suffix(".json")
    json_data = load_json(json_path) if json_path.exists() else {}
    md_present = base.with_suffix(".md").exists()

    sigil = None
    version = None
    updated = None
    json_version = None
    json_updated = None
    gaps: List[str] = []

    meta_yaml = yaml_data.get("meta") if isinstance(yaml_data, dict) else None
    if isinstance(meta_yaml, dict):
        sigil = meta_yaml.get("sigil")
        version = meta_yaml.get("version")
        updated = meta_yaml.get("updated")
    meta_json = json_data.get("meta") if isinstance(json_data, dict) else None
    if isinstance(meta_json, dict):
        json_version = meta_json.get("version")
        json_updated = meta_json.get("updated")

    if sigil is None:
        gaps.append("yaml-missing-sigil")
    if version is None:
        gaps.append("yaml-missing-version")
    if json_version != version:
        gaps.append("version-mismatch")
    if updated and json_updated and updated != json_updated:
        gaps.append("updated-mismatch")
    if not md_present:
        gaps.append("missing-markdown")

    return TrilayerStatus(
        base_path=base.relative_to(BASE_DIR),
        sigil=sigil,
        version=version,
        updated=updated,
        json_version=json_version,
        json_updated=json_updated,
        md_present=md_present,
        gaps=gaps,
    )


def generate_report(trilayers: Iterable[Path]) -> Dict[str, object]:
    statuses = [inspect_trilayer(base) for base in trilayers]
    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "roots": sorted({str(base.parent) for base in trilayers}),
            "logistic": {
                "R": "Count of trilayers inspected for parity.",
                "Theta": "All tri-layer sigils share version + updated metadata.",
                "beta": 4.6,
                "zeta": "Damped when reports reach codexfeedback within one sprint.",
            },
            "counts": {
                "total": len(statuses),
                "with_gaps": sum(1 for status in statuses if status.gaps),
            },
        },
        "trilayers": [status.to_dict() for status in statuses],
    }
    return envelope


def write_output(envelope: Dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(envelope, handle, ensure_ascii=False, indent=2)


CODEx_TEMPLATE_MD = """### {codex_id} — Sigillin Sync Run
- **Zeitpunkt (UTC):** {timestamp}
- **R:** {total} Trilayer geprüft
- **Θ:** {theta}
- **β:** 4.6
- **ζ(R):** {zeta}
- **Notiz:** {note}
"""

CODEx_TEMPLATE_JSON = {
    "id": None,
    "title": None,
    "scope": [],
    "parameters": {
        "R": None,
        "Theta": None,
        "beta": 4.6,
    },
    "resonance": None,
    "status": "draft",
    "notes": {
        "formal": None,
        "empirical": None,
        "poetic": None,
    },
    "created_at": None,
}


CODEx_TEMPLATE_YAML = {
    "id": None,
    "title": None,
    "scope": [],
    "parameters": {
        "R": None,
        "Theta": None,
        "beta": 4.6,
    },
    "resonance": None,
    "status": "draft",
    "notes": {
        "formal": None,
        "empirical": None,
        "poetic": None,
    },
    "created_at": None,
}
CODEx_MD_PATH = CODEX_BASE.with_suffix(".md")
CODEx_JSON_PATH = CODEX_BASE.with_suffix(".json")
CODEx_YAML_PATH = CODEX_BASE.with_suffix(".yaml")


def _append_to_entries(store: Dict[str, object], entry: Dict[str, object]) -> None:
    """Append ``entry`` to the ``entries`` list inside ``store``.

    The Codex tri-layer keeps a shared schema where the top-level document is an
    object with an ``entries`` list. Earlier versions of this tool attempted to
    call ``append`` on the top-level mapping directly, which crashes as soon as
    the script encounters the first codex run. This helper centralises the
    guardrails so JSON and YAML layers remain synchronised.
    """

    entries = store.setdefault("entries", [])
    if not isinstance(entries, list):
        raise TypeError("codexfeedback entries container must be a list")
    entries.append(entry)


def append_codex_entry(
    envelope: Dict[str, object], codex_id: str, note: str, dry_run: bool = False
) -> None:
    timestamp = envelope["meta"]["generated_at"]
    total = envelope["meta"]["counts"]["total"]
    theta = "Trilayer meta fields aligned"
    zeta = "Logged in codex"

    if not CODEx_MD_PATH.exists() or not CODEx_JSON_PATH.exists() or not CODEx_YAML_PATH.exists():
        raise FileNotFoundError("Codexfeedback trilayer not found; cannot append.")

    md_entry = CODEx_TEMPLATE_MD.format(
        codex_id=codex_id,
        timestamp=timestamp,
        total=total,
        theta=theta,
        zeta=zeta,
        note=note,
    )

    if dry_run:
        print(md_entry)
        return

    with CODEx_MD_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n" + md_entry)

    json_entry = CODEx_TEMPLATE_JSON.copy()
    json_entry.update(
        {
            "id": codex_id,
            "title": "Sigillin Sync Run",
            "scope": ["scripts/sigillin_sync.py"],
            "parameters": {
                "R": f"{total} trilayers inspected",
                "Theta": theta,
                "beta": 4.6,
            },
            "resonance": note,
            "notes": {
                "formal": "Telemetry sweep executed via sigillin_sync.py",
                "empirical": f"{total} trilayers scanned",
                "poetic": "Logistic membrane hums in phase with the Codex.",
            },
            "created_at": timestamp,
        }
    )

    with CODEx_JSON_PATH.open("r", encoding="utf-8") as handle:
        codex_json = json.load(handle)
    if not isinstance(codex_json, dict):
        raise TypeError("codexfeedback.json must contain an object with an 'entries' list")
    _append_to_entries(codex_json, json_entry)
    with CODEx_JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(codex_json, handle, ensure_ascii=False, indent=2)

    with CODEx_YAML_PATH.open("r", encoding="utf-8") as handle:
        codex_yaml = yaml.safe_load(handle) or {}
    if not isinstance(codex_yaml, dict):
        raise TypeError("codexfeedback.yaml must contain an object with an 'entries' list")
    _append_to_entries(codex_yaml, deepcopy(json_entry))
    with CODEx_YAML_PATH.open("w", encoding="utf-8") as handle:
        yaml.dump(codex_yaml, handle, allow_unicode=True, sort_keys=False)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Metaquest Sigillin Sync Harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="Generate trilayer telemetry report")
    report_parser.add_argument(
        "--roots",
        action="append",
        default=[],
        help="Directory roots to inspect (default: Metaquest + shadow directories)",
    )
    report_parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write JSON report",
    )

    stamp_parser = subparsers.add_parser("stamp", help="Generate report and append codex entry")
    stamp_parser.add_argument("--codex-id", required=True)
    stamp_parser.add_argument("--note", required=True)
    stamp_parser.add_argument(
        "--roots",
        action="append",
        default=[],
        help="Directory roots to inspect before stamping",
    )
    stamp_parser.add_argument("--dry-run", action="store_true", help="Preview codex entry without writing")

    return parser.parse_args(argv)


def resolve_roots(raw_roots: Sequence[str]) -> List[Path]:
    if raw_roots:
        roots = [Path(root) if Path(root).is_absolute() else BASE_DIR / root for root in raw_roots]
    else:
        roots = [
            BASE_DIR / "seed" / "bedeutungssigillin" / "metaquest",
            BASE_DIR / "seed" / "shadow_sigillin" / "metaquest",
        ]
    return roots


def handle_report(args: argparse.Namespace) -> int:
    roots = resolve_roots(args.roots)
    trilayers = discover_trilayers(roots)
    envelope = generate_report(trilayers)
    print(json.dumps(envelope, ensure_ascii=False, indent=2))
    if args.output:
        write_output(envelope, args.output if args.output.is_absolute() else BASE_DIR / args.output)
    return 0


def handle_stamp(args: argparse.Namespace) -> int:
    roots = resolve_roots(args.roots)
    trilayers = discover_trilayers(roots)
    envelope = generate_report(trilayers)
    append_codex_entry(envelope, args.codex_id, args.note, dry_run=args.dry_run)
    if args.dry_run:
        return 0
    print(json.dumps(envelope, ensure_ascii=False, indent=2))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.command == "report":
        return handle_report(args)
    if args.command == "stamp":
        return handle_stamp(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
