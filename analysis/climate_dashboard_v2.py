"""Climate monitoring dashboard v2 with per-system sigma_Phi tracking.

Provides sigma_Phi calculation for climate tipping elements using the
AFET coefficient-of-variation metric.  Simulates data when external
APIs (NOAA, ERA5) are unavailable.

Usage:
    python -m analysis.climate_dashboard_v2
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from theory.afet import AFETConstants

EPSILON = 1e-12

# Predefined climate systems with characteristic parameters
CLIMATE_SYSTEMS = {
    "AMOC": {"description": "Atlantic Meridional Overturning Circulation", "beta_c": 38.0},
    "Arctic_Sea_Ice": {"description": "Arctic sea ice extent", "beta_c": 35.0},
    "Amazon_Rainforest": {"description": "Amazon dieback threshold", "beta_c": 40.0},
    "ENSO": {"description": "El Nino Southern Oscillation", "beta_c": 30.0},
    "Permafrost": {"description": "Permafrost thaw feedback", "beta_c": 42.0},
}


@dataclass(frozen=True)
class SystemStatus:
    """sigma_Phi status for a single climate system."""

    name: str
    sigma_phi: float
    safety_state: str
    description: str


@dataclass
class ClimateDashboard:
    """Per-system sigma_Phi tracker for climate tipping elements."""

    sigma_phi_threshold: float = AFETConstants.SIGMA_PHI
    critical_threshold: float = 0.055
    _systems: dict[str, list[float]] = field(default_factory=dict)

    def compute_sigma_phi(self, time_series: np.ndarray) -> float:
        """Coefficient of variation of a climate time series."""
        arr = np.asarray(time_series, dtype=np.float64).flatten()
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=0))
        return std / max(abs(mean), EPSILON)

    def track_system(self, name: str, data: np.ndarray) -> dict:
        """Track sigma_Phi for a named climate system."""
        sigma = self.compute_sigma_phi(data)
        self._systems.setdefault(name, []).append(sigma)

        if sigma < self.critical_threshold:
            state = "critical"
        elif sigma < self.sigma_phi_threshold:
            state = "warning"
        else:
            state = "stable"

        return {"name": name, "sigma_phi": round(sigma, 6), "safety_state": state}

    def get_alerts(self) -> list[dict]:
        """Return systems with sigma_Phi below the stable threshold."""
        alerts = []
        for name, history in self._systems.items():
            if not history:
                continue
            latest = history[-1]
            if latest < self.sigma_phi_threshold:
                state = "critical" if latest < self.critical_threshold else "warning"
                alerts.append({"name": name, "sigma_phi": round(latest, 6), "state": state})
        return alerts

    def get_all_systems(self) -> dict:
        """Return all tracked systems and their latest sigma_Phi."""
        result = {}
        for name, history in self._systems.items():
            if history:
                result[name] = {
                    "latest_sigma_phi": round(history[-1], 6),
                    "n_readings": len(history),
                    "mean_sigma_phi": round(float(np.mean(history)), 6),
                }
        return result

    # --- API endpoint stubs ---

    def api_get_sigma_phi(self, system: str) -> dict:
        """GET /sigma_phi/{system}"""
        history = self._systems.get(system, [])
        if not history:
            return {"error": f"System '{system}' not found"}
        return {"system": system, "sigma_phi": round(history[-1], 6), "n_readings": len(history)}

    def api_get_alerts(self) -> dict:
        """GET /alerts/current"""
        return {"alerts": self.get_alerts(), "timestamp": time.time()}

    def api_subscribe(self, email: str, systems: list[str] | None = None) -> dict:
        """POST /subscribe"""
        return {
            "status": "subscribed",
            "email": email,
            "systems": systems or list(CLIMATE_SYSTEMS.keys()),
        }


def simulate_climate_data(seed: int = 42) -> dict[str, np.ndarray]:
    """Generate synthetic climate time series for testing."""
    rng = np.random.default_rng(seed)
    data = {}
    for name, info in CLIMATE_SYSTEMS.items():
        # Simulate 100 data points with system-specific characteristics
        base = rng.normal(loc=info["beta_c"], scale=info["beta_c"] * 0.05, size=100)
        data[name] = base
    return data


def run_climate_dashboard(output_dir: Path | None = None) -> dict:
    """Run the climate dashboard with simulated data."""
    print("=" * 60)
    print("Climate Monitoring Dashboard v2")
    print("=" * 60)

    dashboard = ClimateDashboard()
    simulated = simulate_climate_data()

    for name, data in simulated.items():
        result = dashboard.track_system(name, data)
        desc = CLIMATE_SYSTEMS[name]["description"]
        print(f"  {name:20s} sigma_Phi={result['sigma_phi']:.6f} [{result['safety_state']}]")

    alerts = dashboard.get_alerts()
    print(f"\nAlerts: {len(alerts)} systems below threshold")

    payload = {
        "systems": dashboard.get_all_systems(),
        "alerts": alerts,
        "timestamp": time.time(),
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "climate_dashboard_v2.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Results -> {path}")

    return payload


if __name__ == "__main__":
    run_climate_dashboard(output_dir=Path("analysis/results"))
