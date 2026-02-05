"""Generate LanternNet status trilayer artifacts.

This script reads the Lantern Hub registry and optional ledgers to
produce the LanternNet index in YAML/JSON/Markdown format.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

DEFAULT_CONFIG_PATH = Path("v9_alpha/config/lantern_hub.yaml")
DEFAULT_OUTPUT_DIR = Path("status")
CONSENT_PROMPT = (
    "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
)


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ledger_refs(bootstrap_ledger: Optional[Path], crep_ledger: Optional[Path]) -> Dict[str, str]:
    refs: Dict[str, str] = {}
    if bootstrap_ledger:
        refs["bootstrap"] = str(bootstrap_ledger)
    if crep_ledger:
        refs["crep_null_models"] = str(crep_ledger)
    return refs


def _normalize_key(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return str(value).strip().lower()


def _index_ledger_entries(ledger: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    if not ledger:
        return {}
    index: Dict[str, Dict[str, Any]] = {}
    for entry in ledger.get("entries", []):
        for key in (entry.get("module"), entry.get("module_id"), entry.get("scope")):
            normalized = _normalize_key(key)
            if normalized:
                index[normalized] = entry
    return index


def _match_ledger_entry(
    index: Dict[str, Dict[str, Any]],
    module_id: Optional[str],
    module_name: Optional[str],
) -> Optional[Dict[str, Any]]:
    for key in (_normalize_key(module_id), _normalize_key(module_name)):
        if key and key in index:
            return index[key]
    return None


def _lifecycle(status: Optional[str]) -> str:
    if not status:
        return "prototype"
    if status.lower() in {"active", "primed"}:
        return "active"
    return "prototype"


def build_lantern_net(
    lantern_hub: Dict[str, Any],
    bootstrap_ledger: Optional[Dict[str, Any]] = None,
    crep_ledger: Optional[Dict[str, Any]] = None,
    bootstrap_ledger_path: Optional[Path] = None,
    crep_ledger_path: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Build LanternNet index from config and ledgers.

    Parameters
    ----------
    lantern_hub : dict
        Parsed lantern hub configuration.
    bootstrap_ledger : dict, optional
        Parsed bootstrap ledger data.
    crep_ledger : dict, optional
        Parsed CREP null-model ledger data.
    timestamp : str, optional
        Override ISO-8601 timestamp.

    Returns
    -------
    dict
        LanternNet index structure.
    """
    meta = lantern_hub.get("meta", {})
    summary = lantern_hub.get("summary", {})
    logistic_frame = meta.get("logistic_frame", {})
    last_updated = timestamp or _timestamp()

    ledger_summary = {
        "bootstrap": bootstrap_ledger.get("meta") if bootstrap_ledger else None,
        "crep_null_models": crep_ledger.get("meta") if crep_ledger else None,
    }
    ledger_refs = _ledger_refs(bootstrap_ledger_path, crep_ledger_path)
    bootstrap_index = _index_ledger_entries(bootstrap_ledger)
    crep_index = _index_ledger_entries(crep_ledger)

    entries: List[Dict[str, Any]] = []
    for lantern in lantern_hub.get("lanterns", []):
        module_id = lantern.get("id")
        module_name = lantern.get("name")
        bootstrap_entry = _match_ledger_entry(bootstrap_index, module_id, module_name)
        crep_entry = _match_ledger_entry(crep_index, module_id, module_name)
        data_assets = lantern.get("data_assets", [])
        ethics_tags = lantern.get(
            "ethics_tags",
            [
                "sigillin-consent-gated",
                "anonymization-required",
                "falsifiability-required",
            ],
        )
        documentation = lantern.get(
            "documentation",
            {"readme": None, "methodology": None, "roadmap": None},
        )
        entries.append(
            {
                "module_id": module_id,
                "module_name": module_name,
                "description": lantern.get("order_parameter", "UTAC lantern module"),
                "version": meta.get("version"),
                "type": lantern.get("type"),
                "domain": lantern.get("domain"),
                "status": lantern.get("status"),
                "lifecycle": _lifecycle(lantern.get("status")),
                "completion_status": lantern.get("status"),
                "readiness": lantern.get("readiness"),
                "morfit_layers": {
                    "code": lantern.get("status"),
                    "documentation": lantern.get("documentation_status", "pending"),
                    "roadmap": lantern.get("roadmap_status", "pending"),
                },
                "logistic_parameters": {
                    "R": lantern.get("readiness"),
                    "Theta": lantern.get("theta"),
                    "beta": lantern.get("beta"),
                    "zeta": logistic_frame.get("zeta"),
                    "sigma": logistic_frame.get("sigma"),
                },
                "ethics_tags": ethics_tags,
                "consent_requirements": {
                    "prompt": CONSENT_PROMPT,
                    "protocol": "Sigillin consent gating + anonymization required",
                },
                "documentation": documentation,
                "crep_offset": crep_entry.get("crep_offset") if crep_entry else None,
                "sigma_phi_range": (
                    bootstrap_entry.get("sigma_phi_range") if bootstrap_entry else None
                ),
                "null_models": {
                    "bootstrap": bootstrap_entry.get("null_models") if bootstrap_entry else None,
                    "crep": crep_entry.get("null_models") if crep_entry else None,
                },
                "ci_95": {
                    "bootstrap": bootstrap_entry.get("ci_95") if bootstrap_entry else None,
                    "crep": crep_entry.get("ci_95") if crep_entry else None,
                },
                "ledger_entries": {
                    "bootstrap": bootstrap_entry.get("id") if bootstrap_entry else None,
                    "crep_null_models": crep_entry.get("id") if crep_entry else None,
                },
                "evidence": {
                    "ledgers": [
                        entry_id
                        for entry_id in [
                            bootstrap_entry.get("id") if bootstrap_entry else None,
                            crep_entry.get("id") if crep_entry else None,
                        ]
                        if entry_id
                    ],
                    "tests": lantern.get("test_refs", []),
                },
                "mandala_bridge": {
                    "status": "pending",
                    "schema": "schemas/psrm_map.schema.json",
                },
                "telemetry": {
                    "data_assets": data_assets,
                    "ledger_refs": ledger_refs,
                    "ledger_summary": ledger_summary,
                },
                "test_coverage": {
                    "status": "unknown",
                    "notes": "Pending per-module test coverage audit.",
                },
                "last_updated": last_updated,
                "notes": lantern.get("notes", {}),
            }
        )

    return {
        "meta": {
            "document": "LanternNet Status Index",
            "version": meta.get("version", "v9.0.0-alpha"),
            "created": meta.get("created"),
            "updated": last_updated,
            "logistic_frame": logistic_frame,
            "summary": summary,
            "sources": meta.get("sources", {}),
            "ledger_summary": ledger_summary,
            "ledger_refs": ledger_refs,
            "consent_prompt": CONSENT_PROMPT,
            "sigma_transition": "σ(β(R-Θ)) marks readiness transitions across lanterns.",
        },
        "lanterns": entries,
    }


def _write_yaml(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _write_markdown(path: Path, payload: Dict[str, Any]) -> None:
    meta = payload.get("meta", {})
    lanterns = payload.get("lanterns", [])
    lines = [
        "# LanternNet Status Index",
        "",
        "Dieses Dokument bündelt $(R, \\Theta, \\beta, \\zeta(R))$ für jede Laterne und",
        "markiert Übergänge über $\\sigma(\\beta(R-\\Theta))$ als Resonanzschwellen.",
        "",
        f"**Version:** {meta.get('version')}",
        f"**Updated:** {meta.get('updated')}",
        "",
        "## Quellen",
        f"- Lantern Hub: `{meta.get('sources', {}).get('v8_lanterns', 'v9_alpha/config/lantern_hub.yaml')}`",
        f"- Ordnungs-Sigillin: `feldtheorie_index.*`",
        f"- Empirische Evidenz: `data/`, `analysis/`, `docs/`",
        f"- Consent Prompt: {meta.get('consent_prompt')}",
        "",
        "## Lantern Übersicht",
    ]
    for lantern in lanterns:
        params = lantern.get("logistic_parameters", {})
        lines.extend(
            [
                f"### {lantern.get('module_name')} ({lantern.get('module_id')})",
                f"- **Status:** {lantern.get('status')} | **Readiness R:** {lantern.get('readiness')}",
                f"- **Lifecycle:** {lantern.get('lifecycle')}",
                f"- **Completion Status:** {lantern.get('completion_status')}",
                f"- **MOR-FIT Layers:** code={lantern.get('morfit_layers', {}).get('code')}, "
                f"documentation={lantern.get('morfit_layers', {}).get('documentation')}, "
                f"roadmap={lantern.get('morfit_layers', {}).get('roadmap')}",
                f"- **Domain:** {lantern.get('domain')} | **Type:** {lantern.get('type')}",
                f"- **Order Parameter:** {lantern.get('description')}",
                f"- **Logistik:** R={params.get('R')}, Θ={params.get('Theta')}, β={params.get('beta')}, ζ={params.get('zeta')}",
                f"- **σΦ Range:** {lantern.get('sigma_phi_range')}",
                f"- **CREP Offset:** {lantern.get('crep_offset')}",
                f"- **Ledger Entries:** bootstrap={lantern.get('ledger_entries', {}).get('bootstrap')}, "
                f"crep={lantern.get('ledger_entries', {}).get('crep_null_models')}",
                f"- **Evidence:** ledgers={lantern.get('evidence', {}).get('ledgers')}, "
                f"tests={lantern.get('evidence', {}).get('tests')}",
                f"- **Ethics Tags:** {', '.join(lantern.get('ethics_tags', []))}",
                f"- **Documentation:** README={lantern.get('documentation', {}).get('readme')}, "
                f"Methodology={lantern.get('documentation', {}).get('methodology')}, "
                f"Roadmap={lantern.get('documentation', {}).get('roadmap')}",
                "",
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_trilayer(output_dir: Path, payload: Dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(output_dir / "lantern_net.yaml", payload)
    _write_json(output_dir / "lantern_net.json", payload)
    _write_markdown(output_dir / "lantern_net.md", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update LanternNet index.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap-ledger", type=Path, default=None)
    parser.add_argument("--crep-ledger", type=Path, default=None)
    args = parser.parse_args()

    lantern_hub = _load_yaml(args.config)
    bootstrap_data = _load_json(args.bootstrap_ledger) if args.bootstrap_ledger else None
    crep_data = _load_json(args.crep_ledger) if args.crep_ledger else None

    payload = build_lantern_net(
        lantern_hub=lantern_hub,
        bootstrap_ledger=bootstrap_data,
        crep_ledger=crep_data,
        bootstrap_ledger_path=args.bootstrap_ledger,
        crep_ledger_path=args.crep_ledger,
    )
    write_trilayer(args.output_dir, payload)


if __name__ == "__main__":
    main()
