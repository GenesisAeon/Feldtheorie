import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from analysis.beta_meta_regression_v2 import run_beta_regression
from modules.therapist import SigillinTherapist
from scripts.sigillin_storage import store_sigillin
from scripts.utils.audit import audit_delta_AIC

therapist = SigillinTherapist()


def _extract_numeric(
    source: Mapping[str, Any] | Any, keys: tuple[str, ...], default: float = 0.0
) -> float:
    """Best-effort extraction of a numeric value from mappings or objects."""

    for key in keys:
        candidate = None
        if isinstance(source, Mapping) and key in source:
            candidate = source.get(key)
        else:
            candidate = getattr(source, key, None)

        try:
            return float(candidate)
        except (TypeError, ValueError):
            continue
    return default


def check_mental_health(
    beta_fit: Mapping[str, Any] | Any, audit_result: Mapping[str, Any] | None = None
) -> None:
    """Run the therapist after heavy computation to detect narrative drift."""

    audit_result = audit_result or {}
    metrics = {
        "beta": _extract_numeric(beta_fit, ("beta", "beta_fit", "slope"), default=0.0),
        "entropy": _extract_numeric(
            audit_result, ("entropy", "entropy_measure", "delta_AIC", "delta_aic"), default=0.0
        ),
        "crep_score": _extract_numeric(
            audit_result, ("crep_score", "ethics_score", "compliance"), default=0.0
        ),
        "kappa": _extract_numeric(beta_fit, ("kappa", "κ"), default=0.0),
    }

    insights = therapist.diagnose(metrics)
    for label, message in insights:
        print(f"[ψ-therapist] {label}: {message}")

    if insights:
        print(f"[ψ-therapist] Intervention: {therapist.intervene()}")


def mirror_machine(trilayer_data):
    # Platzhalter: Mirror-Machine verarbeitet Tri-Layer-Eintrag
    return trilayer_data  # Noch zu verfeinern mit Spiegelungslogik


def sigillin_kernel(trilayer_path):
    trilayer_data = json.loads(Path(trilayer_path).read_text())
    mirror_output = mirror_machine(trilayer_data)
    beta_fit = run_beta_regression(mirror_output)
    audit_result = audit_delta_AIC(beta_fit)
    check_mental_health(beta_fit, audit_result)

    if audit_result["pass"]:
        store_sigillin(beta_fit, audit_result)
        print("[✔] Sigillin gespeichert: Schwelle überschritten.")
        return True
    else:
        print("[✘] Keine Speicherung: ΔAIC zu gering.")
        return False


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_trilayer.json"
    sigillin_kernel(path)
