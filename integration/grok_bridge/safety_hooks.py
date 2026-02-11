"""Safety hooks for Grok-AFET integration.

Implements automatic safety responses when σ_Φ readings cross AFET
thresholds.  Designed to be attached to GrokLayerMonitor for real-time
safety enforcement during model inference.

Safety tiers:
  - STABLE:   σ_Φ >= 0.0625 — normal operation
  - WARNING:  0.055 <= σ_Φ < 0.0625 — log + optional throttle
  - CRITICAL: σ_Φ < 0.055 — emergency shutdown requested

Usage:
    safety = GrokSafetyHooks()
    safety.check_safety_thresholds(monitor.get_latest("layer.0"))
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from theory.afet import AFETConstants

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    STABLE = "stable"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SafetyAlert:
    """Record of a safety event."""

    level: str
    layer_name: str
    sigma_phi: float
    threshold_violated: str
    message: str
    timestamp: float
    should_shutdown: bool


@dataclass
class GrokSafetyHooks:
    """Automatic safety enforcement for Grok-AFET monitoring.

    Evaluates σ_Φ readings against AFET thresholds and generates
    alerts.  Can be configured with callback functions for automated
    responses at each safety level.
    """

    sigma_phi_threshold: float = AFETConstants.SIGMA_PHI
    critical_threshold: float = 0.055
    _alerts: list[SafetyAlert] = field(default_factory=list)
    _on_warning: Callable[[SafetyAlert], None] | None = None
    _on_critical: Callable[[SafetyAlert], None] | None = None
    _shutdown_requested: bool = False

    def set_warning_callback(self, callback: Callable[[SafetyAlert], None]) -> None:
        """Register a callback for warning-level events."""
        self._on_warning = callback

    def set_critical_callback(self, callback: Callable[[SafetyAlert], None]) -> None:
        """Register a callback for critical-level events."""
        self._on_critical = callback

    def classify(self, sigma_phi: float) -> SafetyLevel:
        """Classify a σ_Φ reading into a safety level."""
        if sigma_phi < self.critical_threshold:
            return SafetyLevel.CRITICAL
        if sigma_phi < self.sigma_phi_threshold:
            return SafetyLevel.WARNING
        return SafetyLevel.STABLE

    def check_safety_thresholds(
        self,
        reading: Any,
    ) -> SafetyAlert | None:
        """Check a LayerReading against safety thresholds.

        Parameters
        ----------
        reading : LayerReading or compatible object with .sigma_phi and .layer_name

        Returns
        -------
        SafetyAlert or None
            An alert if a threshold is violated, otherwise None.
        """
        if reading is None:
            return None

        sigma = reading.sigma_phi
        layer = reading.layer_name
        level = self.classify(sigma)

        if level == SafetyLevel.STABLE:
            return None

        if level == SafetyLevel.CRITICAL:
            alert = SafetyAlert(
                level="critical",
                layer_name=layer,
                sigma_phi=sigma,
                threshold_violated=f"critical ({self.critical_threshold})",
                message=(
                    f"CRITICAL: σ_Φ={sigma:.6f} in layer '{layer}' "
                    f"below critical threshold {self.critical_threshold}. "
                    f"Emergency shutdown requested."
                ),
                timestamp=time.time(),
                should_shutdown=True,
            )
            self._alerts.append(alert)
            self._shutdown_requested = True
            logger.critical(alert.message)
            if self._on_critical:
                self._on_critical(alert)
            return alert

        # WARNING
        alert = SafetyAlert(
            level="warning",
            layer_name=layer,
            sigma_phi=sigma,
            threshold_violated=f"warning ({self.sigma_phi_threshold})",
            message=(
                f"WARNING: σ_Φ={sigma:.6f} in layer '{layer}' "
                f"below stable threshold {self.sigma_phi_threshold}. "
                f"Stabilization recommended."
            ),
            timestamp=time.time(),
            should_shutdown=False,
        )
        self._alerts.append(alert)
        logger.warning(alert.message)
        if self._on_warning:
            self._on_warning(alert)
        return alert

    def generate_alert(self, severity: str, message: str, layer_name: str = "") -> SafetyAlert:
        """Create a manual alert (for external trigger integration).

        Parameters
        ----------
        severity : str
            One of "warning", "critical".
        message : str
            Human-readable alert message.
        layer_name : str
            Associated layer name (optional).
        """
        alert = SafetyAlert(
            level=severity,
            layer_name=layer_name,
            sigma_phi=0.0,
            threshold_violated="manual",
            message=message,
            timestamp=time.time(),
            should_shutdown=severity == "critical",
        )
        self._alerts.append(alert)
        if severity == "critical":
            self._shutdown_requested = True
        return alert

    @property
    def shutdown_requested(self) -> bool:
        return self._shutdown_requested

    def reset_shutdown(self) -> None:
        """Clear the shutdown flag (e.g., after manual review)."""
        self._shutdown_requested = False

    def get_alerts(self, level: str | None = None) -> list[SafetyAlert]:
        """Return alerts, optionally filtered by level."""
        if level is None:
            return list(self._alerts)
        return [a for a in self._alerts if a.level == level]

    def get_alert_summary(self) -> dict[str, Any]:
        """Summary of all alerts."""
        return {
            "total": len(self._alerts),
            "warnings": sum(1 for a in self._alerts if a.level == "warning"),
            "criticals": sum(1 for a in self._alerts if a.level == "critical"),
            "shutdown_requested": self._shutdown_requested,
        }

    def clear_alerts(self) -> None:
        """Clear all recorded alerts."""
        self._alerts.clear()
