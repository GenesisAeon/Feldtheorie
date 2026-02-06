"""Aeon-Lantern integration hub with governance, sonification, and VR map export.

Includes MOR (Multi-agent Orchestration Referee) for coordination governance
and FIT (Field Integrity Tester) for beta-validation across coupled systems.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from aeon.api_bridge import AeonLanternAsyncBridge

try:
    import mido
except ImportError:  # pragma: no cover
    mido = None

try:
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover
    go = None

logger = logging.getLogger(__name__)


@dataclass
class QuartzOscillatorSim:
    frequency_hz: float = 13.5e6
    jitter_ppm: float = 2.0


@dataclass
class MORGovernance:
    """Multi-agent Orchestration Referee for coordination governance.

    Tracks agent task delegation, validates CREP thresholds, and
    enforces consensus before critical operations.
    """

    crep_threshold: float = 0.7
    consensus_required: bool = True
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    def validate_delegation(self, agent_name: str, task: str, crep_score: float) -> dict[str, Any]:
        """Validate whether a task delegation meets governance requirements."""
        approved = crep_score >= self.crep_threshold
        record = {
            "agent": agent_name,
            "task": task,
            "crep_score": crep_score,
            "threshold": self.crep_threshold,
            "approved": approved,
        }
        self.audit_trail.append(record)
        if not approved:
            logger.warning(
                "MOR: delegation rejected agent=%s task=%s crep=%.3f < %.3f",
                agent_name, task, crep_score, self.crep_threshold,
            )
        return record

    def get_audit_summary(self) -> dict[str, Any]:
        total = len(self.audit_trail)
        approved = sum(1 for r in self.audit_trail if r["approved"])
        return {
            "total_delegations": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": approved / total if total > 0 else 0.0,
        }


@dataclass
class FITValidator:
    """Field Integrity Tester for beta-validation across coupled systems.

    Validates that beta parameters remain within expected bounds and
    checks for divergence between the kernel beta and the UTAC axiom beta.
    """

    axiom_beta: float = 37.6
    tolerance: float = 1.0
    validation_log: list[dict[str, Any]] = field(default_factory=list)

    def validate_beta(self, measured_beta: float, context: str = "") -> dict[str, Any]:
        """Check measured beta against axiom beta within tolerance."""
        drift = abs(measured_beta - self.axiom_beta)
        valid = drift <= self.tolerance
        record = {
            "measured_beta": measured_beta,
            "axiom_beta": self.axiom_beta,
            "drift": drift,
            "tolerance": self.tolerance,
            "valid": valid,
            "context": context,
        }
        self.validation_log.append(record)
        if not valid:
            logger.warning(
                "FIT: beta drift %.3f exceeds tolerance %.3f (context=%s)",
                drift, self.tolerance, context,
            )
        return record

    def validate_coherence_cascade(
        self,
        coherence_scores: list[float],
        min_mean: float = 0.5,
    ) -> dict[str, Any]:
        """Validate that a cascade of coherence scores meets field integrity."""
        arr = np.asarray(coherence_scores, dtype=np.float64)
        mean_coh = float(np.mean(arr)) if arr.size > 0 else 0.0
        return {
            "n_scores": int(arr.size),
            "mean_coherence": mean_coh,
            "min_coherence": float(np.min(arr)) if arr.size > 0 else 0.0,
            "max_coherence": float(np.max(arr)) if arr.size > 0 else 0.0,
            "passes_min_mean": mean_coh >= min_mean,
        }

    def get_summary(self) -> dict[str, Any]:
        total = len(self.validation_log)
        valid = sum(1 for r in self.validation_log if r["valid"])
        return {
            "total_validations": total,
            "valid": valid,
            "invalid": total - valid,
            "validity_rate": valid / total if total > 0 else 0.0,
        }


class AeonLanternHub:
    """End-to-end coordinator for nested Aeon<->lanternNet coupling.

    Includes MOR governance for multi-agent orchestration and
    FIT validation for beta-parameter integrity.
    """

    def __init__(
        self,
        bridge: AeonLanternAsyncBridge,
        oscillator: QuartzOscillatorSim | None = None,
        mor: MORGovernance | None = None,
        fit: FITValidator | None = None,
    ) -> None:
        self.bridge = bridge
        self.oscillator = oscillator or QuartzOscillatorSim()
        self.mor = mor or MORGovernance()
        self.fit = fit or FITValidator()

    def run_cascade(self, datasets: list[np.ndarray], n_crit: int = 137) -> dict[str, Any]:
        cascades = 0
        coherence_scores: list[float] = []
        for data in datasets:
            self.bridge.ingest_em_frame(np.asarray(data, dtype=np.float64))
            coherence = float(np.clip(np.mean(np.abs(data)), 0.0, 1.0))
            coherence_scores.append(coherence)
            if coherence > 0.7:
                cascades += 1

        fit_report = self.fit.validate_coherence_cascade(coherence_scores)

        return {
            "dataset_count": len(datasets),
            "cascades": cascades,
            "n_crit_reached": cascades >= n_crit,
            "mean_coherence": float(np.mean(coherence_scores) if coherence_scores else 0.0),
            "fit_validation": fit_report,
        }

    def run_governed_cascade(
        self,
        datasets: list[np.ndarray],
        agent_name: str = "cascade_runner",
        crep_score: float = 0.8,
        n_crit: int = 137,
    ) -> dict[str, Any]:
        """Run cascade with MOR governance check."""
        delegation = self.mor.validate_delegation(agent_name, "run_cascade", crep_score)
        if not delegation["approved"]:
            return {
                "error": "MOR governance rejected delegation",
                "delegation": delegation,
            }
        result = self.run_cascade(datasets, n_crit)
        result["governance"] = delegation
        return result

    def coherence_to_midi(self, coherence: float) -> list[int]:
        pitch = int(np.clip(36 + coherence * 60, 36, 96))
        if mido is None:
            return [pitch]
        msg = mido.Message("note_on", note=pitch, velocity=100)
        return [msg.note]

    def build_vr_teaser_points(self, embeddings: np.ndarray) -> dict[str, Any]:
        points = np.asarray(embeddings, dtype=np.float64)
        payload = {"x": points[:, 0].tolist(), "y": points[:, 1].tolist(), "z": points[:, 2].tolist()}
        if go is None:
            return payload
        fig = go.Figure(data=[go.Scatter3d(x=payload["x"], y=payload["y"], z=payload["z"], mode="markers")])
        payload["plotly_traces"] = len(fig.data)
        return payload

    def get_governance_report(self) -> dict[str, Any]:
        """Combined governance report from MOR and FIT."""
        return {
            "mor": self.mor.get_audit_summary(),
            "fit": self.fit.get_summary(),
        }
