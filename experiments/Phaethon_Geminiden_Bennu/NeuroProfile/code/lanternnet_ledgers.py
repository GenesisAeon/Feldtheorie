"""
LanternNet Ledger Logging
=========================

Schreibt NeuroProfile-Ausgaben in die globalen LanternNet-Ledger
(`data/bootstrap_ledger.*`, `data/crep_null_model_ledger.*`). σ(β(R-Θ))
bleibt nachvollziehbar, Consent-Tokens werden gehasht gespeichert und
ζ(R) bleibt durch ΔAIC/CI-Telemetrie gedämpft.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import json
import re

import yaml

from .beta_extractor_neuro import BetaEstimate


CONSENT_PROMPT = (
    "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _trilayer_paths(base_path: Path) -> dict[str, Path]:
    stem = base_path.with_suffix("")
    return {
        "json": stem.with_suffix(".json"),
        "yaml": stem.with_suffix(".yaml"),
        "md": stem.with_suffix(".md"),
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"meta": {}, "entries": []}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _next_id(prefix: str, existing: Iterable[str]) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    numbers = []
    for entry_id in existing:
        match = pattern.match(entry_id)
        if match:
            numbers.append(int(match.group(1)))
    next_number = max(numbers) + 1 if numbers else 1
    return f"{prefix}{next_number:04d}"


def _render_bootstrap_markdown(payload: dict[str, Any]) -> str:
    meta = payload.get("meta", {})
    entries = payload.get("entries", [])
    lines = [
        "# Bootstrap Ledger – LanternNet",
        "",
        "Dieses Ledger dokumentiert Bootstrap-Schätzungen entlang der UTAC-Steigung",
        "und hält die Nullmodelle (constant, linear, power law) samt ΔAIC/CI bereit.",
        "Der Übergang über $\\sigma(\\beta(R-\\Theta))$ bleibt als Resonanzindikator",
        "explizit gekennzeichnet.",
        "",
        "## Meta",
        f"- **Version:** {meta.get('version')}",
        f"- **Consent Protocol:** {meta.get('consent_protocol')}",
        f"- **Consent Prompt:** {meta.get('consent_prompt')}",
        f"- **Updated:** {meta.get('updated')}",
        "",
        "## Einträge",
        "",
    ]
    for entry in entries:
        params = entry.get("logistic_parameters", {})
        lines.extend(
            [
                f"### {entry.get('id')}",
                f"- **Modul:** {entry.get('module')} ({entry.get('module_id')})",
                f"- **Logistik:** R={params.get('R')}, Θ={params.get('Theta')}, "
                f"β={params.get('beta')}, ζ={params.get('zeta')}",
                f"- **σΦ Range:** {entry.get('sigma_phi_range')}",
                f"- **Nullmodelle:** {', '.join([m.get('name') for m in entry.get('null_models', [])])}",
                f"- **CI (β/σΦ):** {entry.get('ci_95')}",
                f"- **Status:** {entry.get('status')}",
                "",
                "**Notizen**",
                f"- *Formal:* {entry.get('notes', {}).get('formal')}",
                f"- *Empirisch:* {entry.get('notes', {}).get('empirical')}",
                f"- *Poetisch:* {entry.get('notes', {}).get('poetic')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Kopplungen",
            "- LanternNet Index: `status/lantern_net.*`",
            "- Ordnungs-Sigillin: `feldtheorie_index.*`",
            "- Empirische Evidenz: `data/`, `analysis/`, `docs/`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_crep_markdown(payload: dict[str, Any]) -> str:
    meta = payload.get("meta", {})
    entries = payload.get("entries", [])
    lines = [
        "# CREP Null-Model Ledger – LanternNet",
        "",
        "Dieses Ledger dokumentiert CREP-Offsets, ΔAIC-Vergleiche und CI-Notizen,",
        "damit ζ(R) im Übergang über $\\sigma(\\beta(R-\\Theta))$ stabil bleibt.",
        "",
        "## Meta",
        f"- **Version:** {meta.get('version')}",
        f"- **Consent Protocol:** {meta.get('consent_protocol')}",
        f"- **Consent Prompt:** {meta.get('consent_prompt')}",
        f"- **Updated:** {meta.get('updated')}",
        "",
        "## Einträge",
        "",
    ]
    for entry in entries:
        lines.extend(
            [
                f"### {entry.get('id')}",
                f"- **Modul:** {entry.get('module')} ({entry.get('module_id')})",
                f"- **CREP Offset:** {entry.get('crep_offset')}",
                f"- **Nullmodelle:** {', '.join([m.get('name') for m in entry.get('null_models', [])])}",
                f"- **CI-Notizen:** {entry.get('ci_95')}",
                f"- **Status:** {entry.get('status')}",
                "",
                "**Notizen**",
                f"- *Formal:* {entry.get('notes', {}).get('formal')}",
                f"- *Empirisch:* {entry.get('notes', {}).get('empirical')}",
                f"- *Poetisch:* {entry.get('notes', {}).get('poetic')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Kopplungen",
            "- LanternNet Index: `status/lantern_net.*`",
            "- Ordnungs-Sigillin: `feldtheorie_index.*`",
            "- Empirische Evidenz: `data/`, `analysis/`, `docs/`",
            "",
        ]
    )
    return "\n".join(lines)


def _beta_payload(beta: BetaEstimate) -> dict[str, float]:
    return {"beta": beta.beta, "threshold": beta.threshold, "r_value": beta.r_value}


def log_lanternnet_ledgers(
    *,
    result: Any,
    config: Any,
    module_id: str,
    module_name: str,
    source_id: str,
    seed: int,
    bootstrap_ledger_path: Path,
    crep_ledger_path: Path,
    timestamp: str | None = None,
) -> None:
    """Append NeuroProfile analysis to LanternNet ledgers (trilayer)."""
    stamp = timestamp or _timestamp()
    bootstrap_paths = _trilayer_paths(bootstrap_ledger_path)
    crep_paths = _trilayer_paths(crep_ledger_path)

    bootstrap_payload = _load_json(bootstrap_paths["json"])
    crep_payload = _load_json(crep_paths["json"])

    bootstrap_meta = bootstrap_payload.setdefault("meta", {})
    crep_meta = crep_payload.setdefault("meta", {})
    bootstrap_meta["updated"] = stamp
    crep_meta["updated"] = stamp
    bootstrap_meta.setdefault("consent_prompt", CONSENT_PROMPT)
    crep_meta.setdefault("consent_prompt", CONSENT_PROMPT)
    bootstrap_meta.setdefault(
        "consent_protocol",
        "Sigillin consent gating + anonymization required",
    )
    crep_meta.setdefault(
        "consent_protocol",
        "Sigillin consent gating + anonymization required",
    )

    bootstrap_entries = bootstrap_payload.setdefault("entries", [])
    crep_entries = crep_payload.setdefault("entries", [])

    bootstrap_id = _next_id("bootstrap-run-", [entry.get("id", "") for entry in bootstrap_entries])
    crep_id = _next_id("crep-null-", [entry.get("id", "") for entry in crep_entries])

    sigma_phi_range = [float(result.sigma_phi_ci[0]), float(result.sigma_phi_ci[1])]
    beta_ci = [float(result.beta_ci[0]), float(result.beta_ci[1])]

    bootstrap_entries.append(
        {
            "id": bootstrap_id,
            "module": module_name,
            "module_id": module_id,
            "scope": "experiments/Phaethon_Geminiden_Bennu/NeuroProfile",
            "source_id": source_id,
            "subject_hash": result.consent.anonymized_subject,
            "consent_token_hash": result.consent.consent_token_hash,
            "seed": seed,
            "logistic_parameters": {
                "R": float(result.crep.aggregate),
                "Theta": config.logistic_Theta,
                "beta": float(result.beta_estimate.beta),
                "zeta": config.zeta_R,
            },
            "beta_estimate": _beta_payload(result.beta_estimate),
            "sigma_phi_range": sigma_phi_range,
            "null_models": [
                {"name": name, "delta_aic": delta}
                for name, delta in result.null_models.delta_aic.items()
            ],
            "ci_95": {
                "beta": beta_ci,
                "sigma_phi": sigma_phi_range,
            },
            "status": "synthetic",
            "notes": {
                "formal": (
                    "Bootstrap-Run für σ(β(R-Θ)); Nullmodelle (constant/linear/power law) mit ΔAIC "
                    f"best={result.null_models.best_model}."
                ),
                "empirical": (
                    f"σΦ={result.sigma_phi_proxy:.4f}, β={result.beta_estimate.beta:.3f}, "
                    f"R≈{result.crep.aggregate:.3f} aus Synthetic Run."
                ),
                "poetic": "Die Laterne tastet die Steilflanke – σ(β(R-Θ)) bleibt klar fokussiert.",
            },
        }
    )

    crep_entries.append(
        {
            "id": crep_id,
            "module": module_name,
            "module_id": module_id,
            "scope": "experiments/Phaethon_Geminiden_Bennu/NeuroProfile",
            "source_id": source_id,
            "subject_hash": result.consent.anonymized_subject,
            "consent_token_hash": result.consent.consent_token_hash,
            "null_models": [
                {"name": name, "delta_aic": delta}
                for name, delta in result.null_models.delta_aic.items()
            ],
            "crep_offset": float(result.crep.aggregate - 0.5),
            "ci_95": {
                "beta": beta_ci,
                "sigma_phi": sigma_phi_range,
                "gamma_beta": list(result.gamma_beta_ci),
                "resonance_alignment": list(result.resonance_alignment_ci),
            },
            "status": "synthetic",
            "notes": {
                "formal": "CREP-Offset gegen Nullmodelle dokumentiert; ΔAIC und CI bereitgestellt.",
                "empirical": (
                    f"CREP={result.crep.aggregate:.4f} (Offset={result.crep.aggregate - 0.5:.4f})."
                ),
                "poetic": "Das Schattenmodell hält ζ(R) gedämpft, bis neue Resonanz entsteht.",
            },
        }
    )

    _write_json(bootstrap_paths["json"], bootstrap_payload)
    _write_yaml(bootstrap_paths["yaml"], bootstrap_payload)
    bootstrap_paths["md"].write_text(_render_bootstrap_markdown(bootstrap_payload), encoding="utf-8")

    _write_json(crep_paths["json"], crep_payload)
    _write_yaml(crep_paths["yaml"], crep_payload)
    crep_paths["md"].write_text(_render_crep_markdown(crep_payload), encoding="utf-8")
