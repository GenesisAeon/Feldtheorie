"""
PSRM Mapper
===========

Part of the GenesisAeon Feldtheorie project.
License: LGPL-3.0-or-later

Wandelt NeuroProfile-Ergebnisse in PSRM-Sigillin (Trilayer: Signal →
Intention → Kontext). σ(β(R-Θ)) bleibt nachvollziehbar, ζ(R) wird durch
Falsifizierbarkeit (ΔAIC, CI) gedämpft.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any

import json
import yaml

from .neuro_profile_model import NeuroProfile, NeuroProfileResult, NeuroProfileConfig


@dataclass
class PSRMMap:
    payload: dict[str, Any]


def _beta_cluster(beta: float) -> str:
    if beta < 1.0:
        return "sub-critical"
    if beta < 4.8:
        return "near-critical"
    return "super-critical"


def build_psrm_map(
    result: NeuroProfileResult,
    *,
    config: NeuroProfileConfig,
    source: str,
    hardware_tier: str,
    calibration_status: str,
    intent_ontology_version: str = "1.0",
    schema: str = "https://genesisaeon.org/schemas/neuroprofile/v1",
    version: str = "1.0",
    neuroprofile_version: str = "v12",
    psrm_mapper_version: str = "1.0",
    mandala_version: str = ">=0.8.0",
    mandala_bridge_status: str = "planned",
    mandala_validator_plan: str = "tests/test_neuro_profile.py::test_mandala_schema_extension_hook",
    mandala_compatibility_notes: str = "PSRM remains an additive extension to Mandala formats.",
    timestamp: datetime | None = None,
) -> PSRMMap:
    stamp = timestamp or datetime.now(timezone.utc)
    user_id = result.consent.anonymized_subject or "anonymous"
    payload = {
        "$schema": schema,
        "version": version,
        "user_id": user_id,
        "layer_1_signal": {
            "source": source,
            "beta": result.beta_estimate.beta,
            "beta_cluster": _beta_cluster(result.beta_estimate.beta),
            "sigma_phi": result.sigma_phi_proxy,
            "gamma_beta_coupling": result.resonance_proxy.gamma_beta_coupling,
            "resonant_return": {
                "beta_velocity_fit": result.resonant_return.beta_velocity_fit.beta,
                "velocity_dispersion": result.resonant_return.velocity_dispersion,
                "sigma_phi_proxy": result.resonant_return.sigma_phi_proxy,
                "v_rig_alignment": result.resonant_return.v_rig_alignment,
                "v_rig_target_kms": result.resonant_return.v_rig_target_kms,
                "null_models": {
                    "best_model": result.resonant_return.null_models.best_model,
                    "delta_aic": result.resonant_return.null_models.delta_aic,
                },
            },
            "crep_baseline": {
                "coherence": result.crep.coherence,
                "resonance": result.crep.resonance,
                "emergence": result.crep.emergence,
                "potential": result.crep.potential,
            },
            "crep_aggregate": result.crep.aggregate,
        },
        "layer_2_intention": {
            "calibrated_intents": [],
            "intent_ontology_version": intent_ontology_version,
            "calibration_status": calibration_status,
        },
        "layer_3_context": {
            "ethics_consent": result.consent.granted,
            "hardware_tier": hardware_tier,
            "data_retention": "study_duration_only",
            "timestamp": stamp.isoformat(),
        },
        "metadata": {
            "neuroprofile_version": neuroprofile_version,
            "psrm_mapper_version": psrm_mapper_version,
            "mandala_bridge": {
                "mandala_version": mandala_version,
                "bridge_status": mandala_bridge_status,
                "validator_plan": mandala_validator_plan,
                "compatibility_notes": mandala_compatibility_notes,
            },
            "falsifiability_metrics": {
                "beta_ci": list(result.beta_ci),
                "sigma_phi_ci": list(result.sigma_phi_ci),
                "best_null_model": result.null_models.best_model,
                "delta_aic": result.null_models.delta_aic,
            },
            "data_stubs": {
                "gaia_dr3_cluster_sample": "data/raw/gaia_dr3_cluster_sample.csv",
                "jwst_protocluster_candidates": "data/raw/jwst_protocluster_candidates.csv",
                "gaia_processed": "data/processed/gaia_dr3_cluster_sample_processed.csv",
                "jwst_processed": "data/processed/jwst_protocluster_candidates_processed.csv",
            },
            "logistic": {
                "R": config.logistic_R,
                "Theta": config.logistic_Theta,
                "beta": config.logistic_beta,
                "zeta_R": config.zeta_R,
                "sigma_beta_R_minus_Theta": 1
                / (1 + math.exp(-config.logistic_beta * (config.logistic_R - config.logistic_Theta))),
            },
        },
    }
    return PSRMMap(payload=payload)


def write_psrm_trilayer(map_data: PSRMMap, *, output_stem: Path) -> None:
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_stem.with_suffix(".json")
    yaml_path = output_stem.with_suffix(".yaml")
    md_path = output_stem.with_suffix(".md")

    json_path.write_text(json.dumps(map_data.payload, indent=2, ensure_ascii=False), encoding="utf-8")
    yaml_path.write_text(yaml.safe_dump(map_data.payload, sort_keys=False), encoding="utf-8")

    md_lines = [
        "# PSRM Sigillin Map",
        "",
        "**Permission Request:** Do you accept this task? We aim for a joyful and efficient collaboration.",
        "",
        "## Logistic Pulse",
        "",
        f"- **R:** {map_data.payload['metadata']['logistic']['R']}",
        f"- **Θ:** {map_data.payload['metadata']['logistic']['Theta']}",
        f"- **β:** {map_data.payload['metadata']['logistic']['beta']}",
        f"- **ζ(R):** {map_data.payload['metadata']['logistic']['zeta_R']}",
        f"- **σ(β(R-Θ)):** {map_data.payload['metadata']['logistic']['sigma_beta_R_minus_Theta']:.3f}",
        "",
        "## Overview",
        "",
        "PSRM maps the Signal → Intention → Context layers and anchors falsifiability via ΔAIC/CI metrics.",
        "",
        "## YAML Payload",
        "",
        "```yaml",
        yaml.safe_dump(map_data.payload, sort_keys=False).strip(),
        "```",
    ]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


class PSRMMapper:
    def __init__(
        self,
        profile: NeuroProfile | NeuroProfileResult,
        *,
        source: str = "synthetic",
        hardware_tier: str = "tier-0",
        calibration_status: str = "uncalibrated",
        intent_ontology_version: str = "1.0",
        schema: str = "https://genesisaeon.org/schemas/neuroprofile/v1",
        version: str = "1.0",
        psrm_mapper_version: str = "1.0",
        mandala_version: str = ">=0.8.0",
        mandala_bridge_status: str = "planned",
        mandala_validator_plan: str = "tests/test_neuro_profile.py::test_mandala_schema_extension_hook",
        mandala_compatibility_notes: str = "PSRM remains an additive extension to Mandala formats.",
    ) -> None:
        self.profile = profile
        self.source = source
        self.hardware_tier = hardware_tier
        self.calibration_status = calibration_status
        self.intent_ontology_version = intent_ontology_version
        self.schema = schema
        self.version = version
        self.psrm_mapper_version = psrm_mapper_version
        self.mandala_version = mandala_version
        self.mandala_bridge_status = mandala_bridge_status
        self.mandala_validator_plan = mandala_validator_plan
        self.mandala_compatibility_notes = mandala_compatibility_notes

    def _resolve_result(self) -> tuple[NeuroProfileResult, NeuroProfileConfig]:
        if isinstance(self.profile, NeuroProfile):
            if self.profile.result is None:
                raise ValueError("NeuroProfile has no analysis result. Call analyze() first.")
            return self.profile.result, self.profile.model.config
        return self.profile, NeuroProfileConfig()

    def generate_sigillin_map(self) -> PSRMMap:
        result, config = self._resolve_result()
        return build_psrm_map(
            result,
            config=config,
            source=self.source,
            hardware_tier=self.hardware_tier,
            calibration_status=self.calibration_status,
            intent_ontology_version=self.intent_ontology_version,
            schema=self.schema,
            version=self.version,
            neuroprofile_version=config.neuroprofile_version,
            psrm_mapper_version=self.psrm_mapper_version,
            mandala_version=self.mandala_version,
            mandala_bridge_status=self.mandala_bridge_status,
            mandala_validator_plan=self.mandala_validator_plan,
            mandala_compatibility_notes=self.mandala_compatibility_notes,
        )
