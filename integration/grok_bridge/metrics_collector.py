"""Real-time metrics collection for Grok-AFET monitoring.

Aggregates readings from GrokLayerMonitor and safety alerts from
GrokSafetyHooks into a unified dashboard payload.  Supports periodic
snapshots and JSON export for downstream visualization.

Usage:
    collector = GrokMetricsCollector(monitor, safety)
    collector.take_snapshot()
    dashboard = collector.get_dashboard()
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from integration.grok_bridge.layer_monitor import GrokLayerMonitor
from integration.grok_bridge.safety_hooks import GrokSafetyHooks
from theory.afet import AFETConstants


@dataclass(frozen=True)
class MetricsSnapshot:
    """Point-in-time snapshot of all monitored layers."""

    timestamp: float
    layers: dict[str, dict[str, float]]
    overall_sigma_phi: float
    safety_summary: dict[str, Any]


@dataclass
class GrokMetricsCollector:
    """Collects and aggregates Grok-AFET monitoring metrics.

    Parameters
    ----------
    monitor : GrokLayerMonitor
        The layer monitor providing σ_Φ readings.
    safety : GrokSafetyHooks
        The safety hooks providing alert data.
    """

    monitor: GrokLayerMonitor
    safety: GrokSafetyHooks
    _snapshots: list[MetricsSnapshot] = field(default_factory=list)
    max_snapshots: int = 1000

    def take_snapshot(self) -> MetricsSnapshot:
        """Capture current state of all monitored layers."""
        layer_data: dict[str, dict[str, float]] = {}
        all_sigmas: list[float] = []

        for layer_name in self.monitor.attached_layers:
            drift = self.monitor.get_drift_report(layer_name)
            layer_data[layer_name] = drift
            if drift["n_readings"] > 0:
                all_sigmas.append(drift["latest"])

        overall = float(np.mean(all_sigmas)) if all_sigmas else 0.0

        snapshot = MetricsSnapshot(
            timestamp=time.time(),
            layers=layer_data,
            overall_sigma_phi=round(overall, 6),
            safety_summary=self.safety.get_alert_summary(),
        )

        self._snapshots.append(snapshot)
        if len(self._snapshots) > self.max_snapshots:
            self._snapshots = self._snapshots[-self.max_snapshots :]

        return snapshot

    def get_dashboard(self) -> dict[str, Any]:
        """Generate a dashboard payload for visualization."""
        if not self._snapshots:
            return {"error": "No snapshots available", "snapshot_count": 0}

        latest = self._snapshots[-1]
        sigma_history = [s.overall_sigma_phi for s in self._snapshots]

        return {
            "snapshot_count": len(self._snapshots),
            "latest": {
                "timestamp": latest.timestamp,
                "overall_sigma_phi": latest.overall_sigma_phi,
                "layers": latest.layers,
                "safety": latest.safety_summary,
            },
            "sigma_phi_history": {
                "values": sigma_history[-100:],  # last 100 for plotting
                "mean": round(float(np.mean(sigma_history)), 6),
                "std": round(float(np.std(sigma_history)), 6),
                "trend": _compute_trend(sigma_history),
            },
            "thresholds": {
                "stable": AFETConstants.SIGMA_PHI,
                "critical": 0.055,
            },
        }

    def export_json(self, path: Path) -> None:
        """Export the full snapshot history to a JSON file."""
        data = {
            "exported_at": time.time(),
            "snapshot_count": len(self._snapshots),
            "snapshots": [
                {
                    "timestamp": s.timestamp,
                    "overall_sigma_phi": s.overall_sigma_phi,
                    "layers": s.layers,
                    "safety": s.safety_summary,
                }
                for s in self._snapshots
            ],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_snapshots(self) -> list[MetricsSnapshot]:
        return list(self._snapshots)

    def clear(self) -> None:
        self._snapshots.clear()


def _compute_trend(values: list[float], window: int = 10) -> str:
    """Simple trend detection: 'rising', 'falling', or 'stable'."""
    if len(values) < window:
        return "insufficient_data"
    recent = values[-window:]
    earlier = values[-2 * window : -window] if len(values) >= 2 * window else values[:window]
    diff = np.mean(recent) - np.mean(earlier)
    if diff > 0.005:
        return "rising"
    if diff < -0.005:
        return "falling"
    return "stable"
