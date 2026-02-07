from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SafetyDecision:
    sigma_phi: float
    state: str
    should_shutdown: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AFETSafetyMonitor:
    """Monitor σ_Φ in training loops and raise on critical instability."""

    def __init__(self, sigma_phi_threshold: float = 0.0625, critical_threshold: float = 0.055) -> None:
        if critical_threshold >= sigma_phi_threshold:
            msg = "critical_threshold must stay below sigma_phi_threshold"
            raise ValueError(msg)
        self.sigma_phi_threshold = float(sigma_phi_threshold)
        self.critical_threshold = float(critical_threshold)

    def evaluate_sigma_phi(self, sigma_phi: float) -> SafetyDecision:
        value = float(sigma_phi)
        if value < self.critical_threshold:
            return SafetyDecision(
                sigma_phi=value,
                state="critical",
                should_shutdown=True,
                reason=(
                    f"σ_Φ={value:.4f} is below critical threshold "
                    f"{self.critical_threshold:.4f}; emergency shutdown requested"
                ),
            )
        if value < self.sigma_phi_threshold:
            return SafetyDecision(
                sigma_phi=value,
                state="warning",
                should_shutdown=False,
                reason=(
                    f"σ_Φ={value:.4f} is below warning threshold "
                    f"{self.sigma_phi_threshold:.4f}; stabilize training"
                ),
            )
        return SafetyDecision(
            sigma_phi=value,
            state="stable",
            should_shutdown=False,
            reason="σ_Φ inside metastable corridor",
        )

    def monitor_step(self, metrics: Mapping[str, float]) -> SafetyDecision:
        if "sigma_phi" not in metrics:
            msg = "Expected metrics['sigma_phi'] for AFET safety monitoring"
            raise KeyError(msg)
        decision = self.evaluate_sigma_phi(float(metrics["sigma_phi"]))
        if decision.should_shutdown:
            raise RuntimeError(f"AFET critical safety event: {decision.reason}")
        return decision

    def monitor_aeon_shell(self, shell: Any) -> SafetyDecision:
        """Bridge helper for Aeon shell summaries."""
        summary = shell.get_shell_summary()
        collective_metrics = summary.get("collective_metrics", {}) if isinstance(summary, Mapping) else {}
        sigma_phi = collective_metrics.get("sigma_phi", self.sigma_phi_threshold)
        return self.monitor_step({"sigma_phi": float(sigma_phi)})
