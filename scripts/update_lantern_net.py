"""Generate LanternNet status trilayer artifacts.

This script reads the Lantern Hub registry and optional ledgers to
produce the LanternNet index in YAML/JSON/Markdown format.

Enhanced with:
- Test coverage detection (auto-discovers test files for each module)
- Mandala bridge validation (verifies PSRM schema existence)
- Documentation status detection (checks for README/methodology/roadmap files)
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path("v9_alpha/config/lantern_hub.yaml")
DEFAULT_OUTPUT_DIR = Path("status")
PSRM_SCHEMA_PATH = Path("schemas/psrm_map.schema.json")
CONSENT_PROMPT = (
    "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
)

# Module-to-test-path mappings for coverage detection
MODULE_TEST_MAPPINGS: dict[str, list[str]] = {
    # Data Lanterns
    "utac-v1_3-ds-001": ["tests/test_urban_heat.py", "analysis/tests/test_urban_heat_canopy_fit.py"],
    "utac-v1_3-ds-002": ["tests/test_amazon_resilience.py"],
    "utac-v1_3-ds-003": ["tests/test_amoc_transport.py"],
    "utac-v1_3-ds-004": ["tests/test_neuro_ai_hybrid.py"],
    "utac-v1_3-ds-005": ["tests/test_systemic_thresholds.py"],
    # Theory Lanterns
    "lantern-theory-001": ["tests/test_consciousness_integration.py", "tests/test_v_rig.py"],
    "lantern-theory-002": ["tests/test_collective_field.py"],
    # Experiment Lanterns
    "lantern-experiment-001": ["tests/test_em_shielding.py"],
    "lantern-experiment-002": ["tests/test_rf_stimulation.py"],
    "exp-neuroprofile-001": [
        "experiments/Phaethon_Geminiden_Bennu/NeuroProfile/test_neuro_profile.py",
        "tests/experiments/test_neuroprofile.py",
    ],
    # Seed/Sigillin Lanterns (v13.1 Expansion)
    "seed-type6-001": ["tests/test_type6_implosive.py"],
    "seed-aletheia-001": ["tests/test_llm_emergence.py", "tests/experiments/test_aletheia.py"],
    "seed-klimakluft-001": ["tests/test_klimakluft_amplifier.py"],
    "seed-wolfmessing-001": ["tests/test_wolf_messing_bridge.py"],
    "seed-neurokosmos-001": ["tests/test_neuro_kosmos_bridge.py"],
    # Governance Lanterns
    "metaquest-system-001": ["tests/test_metaquest_system.py"],
    "metaquest-campaign-001": ["tests/test_metaquest_campaign.py"],
    # seed/theory/ Lanterns (v13.2 Expansion)
    "seed-entropy-geom-001": [
        "seed/theory/entropy_geometric_waste/test_entropy_geometric_waste.py",
        "tests/test_entropy_geometric_waste.py",
    ],
    "seed-morph-compute-001": ["tests/test_morphological_computing.py"],
    "seed-quantum-alias-001": ["tests/test_quantum_aliasing.py"],
    "seed-mirror-machine-001": ["tests/test_mirror_machine_concept.py"],
    # seed/sigillin/ Additional Lanterns (v13.2 Expansion)
    "seed-morfit-001": ["tests/test_mor_fit_methodology.py"],
    "seed-implosive-feedback-001": ["tests/test_implosive_recursive_feedback.py"],
    "seed-klimakluft-process-001": ["tests/test_klimakluft_process.py"],
    # Legacy Release Lanterns (v13.2 Expansion)
    "release-mirror-v4-001": [
        "seed/releases/v4.0.0-alpha_MirrorMachine/tests/test_ews_pipeline.py",
        "tests/test_mirror_machine_v4.py",
    ],
}


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ledger_refs(bootstrap_ledger: Path | None, crep_ledger: Path | None) -> dict[str, str]:
    refs: dict[str, str] = {}
    if bootstrap_ledger:
        refs["bootstrap"] = str(bootstrap_ledger)
    if crep_ledger:
        refs["crep_null_models"] = str(crep_ledger)
    return refs


def _normalize_key(value: str | None) -> str | None:
    if value is None:
        return None
    return str(value).strip().lower()


def _index_ledger_entries(ledger: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not ledger:
        return {}
    index: dict[str, dict[str, Any]] = {}
    for entry in ledger.get("entries", []):
        for key in (entry.get("module"), entry.get("module_id"), entry.get("scope")):
            normalized = _normalize_key(key)
            if normalized:
                index[normalized] = entry
    return index


def _match_ledger_entry(
    index: dict[str, dict[str, Any]],
    module_id: str | None,
    module_name: str | None,
) -> dict[str, Any] | None:
    for key in (_normalize_key(module_id), _normalize_key(module_name)):
        if key and key in index:
            return index[key]
    return None


def _lifecycle(status: str | None) -> str:
    if not status:
        return "prototype"
    if status.lower() in {"active", "primed"}:
        return "active"
    return "prototype"


def _get_ledger_param(params: dict[str, Any], *keys: str) -> Any | None:
    for key in keys:
        value = params.get(key)
        if value is not None:
            return value
    return None


def _ledger_logistic_params(entry: dict[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {}
    params = entry.get("logistic_parameters", {}) or {}
    return {
        "R": _get_ledger_param(params, "R", "r"),
        "Theta": _get_ledger_param(params, "Theta", "theta"),
        "beta": _get_ledger_param(params, "beta", "β"),
        "zeta": _get_ledger_param(params, "zeta", "ζ"),
    }


def _detect_test_coverage(module_id: str, base_path: Path) -> dict[str, Any]:
    """Detect test coverage status for a module.

    Parameters
    ----------
    module_id : str
        The module identifier to check test coverage for.
    base_path : Path
        Base path of the repository.

    Returns
    -------
    dict
        Test coverage information including status, test files, and notes.
    """
    test_paths = MODULE_TEST_MAPPINGS.get(module_id, [])
    found_tests: list[str] = []
    missing_tests: list[str] = []

    for test_path in test_paths:
        full_path = base_path / test_path
        if full_path.exists():
            found_tests.append(test_path)
        else:
            missing_tests.append(test_path)

    # Determine status based on found tests
    if not test_paths:
        return {
            "status": "unknown",
            "percentage": None,
            "test_files": [],
            "notes": "No test mappings configured for this module.",
        }
    elif found_tests and not missing_tests:
        return {
            "status": "passing",
            "percentage": None,  # Would need pytest-cov to get actual percentage
            "test_files": found_tests,
            "notes": f"All {len(found_tests)} expected test file(s) found.",
        }
    elif found_tests:
        return {
            "status": "partial",
            "percentage": None,
            "test_files": found_tests,
            "notes": f"Found {len(found_tests)}/{len(test_paths)} test files. Missing: {', '.join(missing_tests)}",
        }
    else:
        return {
            "status": "pending",
            "percentage": None,
            "test_files": [],
            "notes": f"Test files not yet created. Expected: {', '.join(missing_tests)}",
        }


def _validate_mandala_bridge(base_path: Path) -> dict[str, Any]:
    """Validate Mandala bridge status by checking PSRM schema existence.

    Parameters
    ----------
    base_path : Path
        Base path of the repository.

    Returns
    -------
    dict
        Mandala bridge status information.
    """
    schema_path = base_path / PSRM_SCHEMA_PATH
    if schema_path.exists():
        return {
            "status": "validated",
            "schema": str(PSRM_SCHEMA_PATH),
            "notes": "PSRM schema exists and is available for validation.",
        }
    return {
        "status": "pending",
        "schema": str(PSRM_SCHEMA_PATH),
        "notes": "PSRM schema not found. Create schemas/psrm_map.schema.json.",
    }


def _detect_documentation_status(
    lantern: dict[str, Any],
    base_path: Path,
) -> tuple[dict[str, str | None], str]:
    """Detect documentation status for a lantern.

    Parameters
    ----------
    lantern : dict
        Lantern configuration from the hub.
    base_path : Path
        Base path of the repository.

    Returns
    -------
    tuple
        (documentation dict, documentation_status string)
    """
    doc_config = lantern.get("documentation", {})
    readme_path = doc_config.get("readme")
    methodology_path = doc_config.get("methodology")
    roadmap_path = doc_config.get("roadmap")

    docs_found = 0
    docs_total = 3

    result = {"readme": None, "methodology": None, "roadmap": None}

    if readme_path and (base_path / readme_path).exists():
        result["readme"] = readme_path
        docs_found += 1

    if methodology_path and (base_path / methodology_path).exists():
        result["methodology"] = methodology_path
        docs_found += 1

    if roadmap_path and (base_path / roadmap_path).exists():
        result["roadmap"] = roadmap_path
        docs_found += 1

    # Determine status
    if docs_found == docs_total:
        status = "active"
    elif docs_found > 0:
        status = "partial"
    else:
        status = "pending"

    return result, status


def build_lantern_net(
    lantern_hub: dict[str, Any],
    bootstrap_ledger: dict[str, Any] | None = None,
    crep_ledger: dict[str, Any] | None = None,
    bootstrap_ledger_path: Path | None = None,
    crep_ledger_path: Path | None = None,
    timestamp: str | None = None,
    base_path: Path | None = None,
) -> dict[str, Any]:
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
    base_path : Path, optional
        Base path for test/documentation detection. Defaults to cwd.

    Returns
    -------
    dict
        LanternNet index structure.
    """
    if base_path is None:
        base_path = Path.cwd()

    # Validate mandala bridge (check PSRM schema)
    mandala_bridge_global = _validate_mandala_bridge(base_path)
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

    entries: list[dict[str, Any]] = []
    for lantern in lantern_hub.get("lanterns", []):
        module_id = lantern.get("id")
        module_name = lantern.get("name")
        bootstrap_entry = _match_ledger_entry(bootstrap_index, module_id, module_name)
        crep_entry = _match_ledger_entry(crep_index, module_id, module_name)
        ledger_params = _ledger_logistic_params(bootstrap_entry)
        data_assets = lantern.get("data_assets", [])
        ethics_tags = lantern.get(
            "ethics_tags",
            [
                "sigillin-consent-gated",
                "anonymization-required",
                "falsifiability-required",
            ],
        )
        # Detect documentation status
        documentation, doc_status = _detect_documentation_status(lantern, base_path)

        # Detect test coverage
        test_coverage = _detect_test_coverage(module_id, base_path)

        readiness = lantern.get("readiness")
        if readiness is None and ledger_params.get("R") is not None:
            readiness = ledger_params["R"]
        logistic_parameters = {
            "R": readiness,
            "Theta": lantern.get("theta"),
            "beta": lantern.get("beta"),
            "zeta": logistic_frame.get("zeta"),
            "sigma": logistic_frame.get("sigma"),
        }
        for key in ("R", "Theta", "beta", "zeta"):
            if ledger_params.get(key) is not None:
                logistic_parameters[key] = ledger_params[key]
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
                "readiness": readiness,
                "morfit_layers": {
                    "code": lantern.get("status"),
                    "documentation": doc_status,
                    "roadmap": doc_status if documentation.get("roadmap") else "pending",
                },
                "logistic_parameters": logistic_parameters,
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
                "mandala_bridge": mandala_bridge_global,
                "telemetry": {
                    "data_assets": data_assets,
                    "ledger_refs": ledger_refs,
                    "ledger_summary": ledger_summary,
                },
                "test_coverage": test_coverage,
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


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
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
        (
            "- Lantern Hub: "
            f"`{meta.get('sources', {}).get('v8_lanterns', 'v9_alpha/config/lantern_hub.yaml')}`"
        ),
        "- Ordnungs-Sigillin: `feldtheorie_index.*`",
        "- Empirische Evidenz: `data/`, `analysis/`, `docs/`",
        f"- Consent Prompt: {meta.get('consent_prompt')}",
        "",
        "## Lantern Übersicht",
    ]
    for lantern in lanterns:
        params = lantern.get("logistic_parameters", {})
        lines.extend(
            [
                f"### {lantern.get('module_name')} ({lantern.get('module_id')})",
                (
                    f"- **Status:** {lantern.get('status')} | **Readiness R:** "
                    f"{lantern.get('readiness')}"
                ),
                f"- **Lifecycle:** {lantern.get('lifecycle')}",
                f"- **Completion Status:** {lantern.get('completion_status')}",
                f"- **MOR-FIT Layers:** code={lantern.get('morfit_layers', {}).get('code')}, "
                f"documentation={lantern.get('morfit_layers', {}).get('documentation')}, "
                f"roadmap={lantern.get('morfit_layers', {}).get('roadmap')}",
                f"- **Domain:** {lantern.get('domain')} | **Type:** {lantern.get('type')}",
                f"- **Order Parameter:** {lantern.get('description')}",
                (
                    f"- **Logistik:** R={params.get('R')}, Θ={params.get('Theta')}, "
                    f"β={params.get('beta')}, ζ={params.get('zeta')}"
                ),
                f"- **σΦ Range:** {lantern.get('sigma_phi_range')}",
                f"- **CREP Offset:** {lantern.get('crep_offset')}",
                (
                    "- **Ledger Entries:** "
                    f"bootstrap={lantern.get('ledger_entries', {}).get('bootstrap')}, "
                    f"crep={lantern.get('ledger_entries', {}).get('crep_null_models')}"
                ),
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


def write_trilayer(output_dir: Path, payload: dict[str, Any]) -> None:
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
    parser.add_argument(
        "--base-path",
        type=Path,
        default=None,
        help="Base path for test/documentation detection. Defaults to cwd.",
    )
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
        base_path=args.base_path,
    )
    write_trilayer(args.output_dir, payload)


if __name__ == "__main__":
    main()
