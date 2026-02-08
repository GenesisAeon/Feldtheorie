"""Week 1 — Thermal sigma_Phi simulation for HfO2 neuromorphic hardware.

Models how temperature drift in hafnium-dioxide memristive devices
affects the AFET metastability parameter sigma_Phi and maps the result
onto the safety zones defined by AFETSafetyMonitor.

Usage:
    python -m experiments.week1.thermal          # run + save JSON + plot
    python -m experiments.week1.thermal --no-plot # skip matplotlib
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from analysis.afet_safety_monitor import AFETSafetyMonitor, SafetyDecision

# ---------------------------------------------------------------------------
# Constants derived from the HfO2 interface contract (analysis/hfo2_interface_spec.py)
# ---------------------------------------------------------------------------
NOMINAL_TEMP_C = 25.0
NOMINAL_SIGMA_PHI = 0.0625
THERMAL_COEFF = -0.00070  # d(sigma_phi)/dT  [1/degC], empirical estimate
MAX_OPERATING_TEMP_C = 85.0  # HfO2 contract: "0-85C nominal"


@dataclass(frozen=True)
class ThermalSample:
    """Single temperature-to-sigma_Phi measurement."""

    temperature_c: float
    sigma_phi: float
    safety_state: str  # "stable" | "warning" | "critical"
    should_shutdown: bool


# ---------------------------------------------------------------------------
# Core model
# ---------------------------------------------------------------------------


def sigma_phi_at_temperature(temp_c: float) -> float:
    """Predict sigma_Phi from device temperature using linear thermal model.

    Linear approximation is valid in the 0-100 degC range where HfO2
    oxygen-vacancy mobility scales roughly linearly with temperature.
    """
    delta = temp_c - NOMINAL_TEMP_C
    return max(0.0, NOMINAL_SIGMA_PHI + THERMAL_COEFF * delta)


def classify_temperature(
    temp_c: float,
    monitor: AFETSafetyMonitor | None = None,
) -> ThermalSample:
    """Compute sigma_Phi and classify via the safety monitor."""
    if monitor is None:
        monitor = AFETSafetyMonitor()
    sigma = sigma_phi_at_temperature(temp_c)
    decision: SafetyDecision = monitor.evaluate_sigma_phi(sigma)
    return ThermalSample(
        temperature_c=temp_c,
        sigma_phi=sigma,
        safety_state=decision.state,
        should_shutdown=decision.should_shutdown,
    )


def find_boundary_temperature(
    target_sigma: float,
    *,
    tol: float = 0.01,
) -> float:
    """Solve for temperature where sigma_Phi == target_sigma."""
    # Linear model -> closed-form inverse:
    return NOMINAL_TEMP_C + (target_sigma - NOMINAL_SIGMA_PHI) / THERMAL_COEFF


def sweep_temperatures(
    start_c: float = 0.0,
    stop_c: float = 100.0,
    step_c: float = 1.0,
) -> list[ThermalSample]:
    """Run a temperature sweep and classify every point."""
    monitor = AFETSafetyMonitor()
    temps = np.arange(start_c, stop_c + step_c, step_c)
    return [classify_temperature(float(t), monitor) for t in temps]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def run_thermal_simulation(
    output_dir: Path | None = None,
    *,
    make_plot: bool = True,
) -> dict:
    """Execute full thermal simulation, persist JSON, optionally plot."""
    samples = sweep_temperatures()
    monitor = AFETSafetyMonitor()

    # Boundary temperatures
    warning_temp = find_boundary_temperature(monitor.sigma_phi_threshold)
    critical_temp = find_boundary_temperature(monitor.critical_threshold)

    result = {
        "model": {
            "nominal_temp_c": NOMINAL_TEMP_C,
            "nominal_sigma_phi": NOMINAL_SIGMA_PHI,
            "thermal_coeff": THERMAL_COEFF,
        },
        "boundaries": {
            "warning_temp_c": round(warning_temp, 2),
            "critical_temp_c": round(critical_temp, 2),
        },
        "thresholds": {
            "sigma_phi_warning": monitor.sigma_phi_threshold,
            "sigma_phi_critical": monitor.critical_threshold,
        },
        "sweep": [asdict(s) for s in samples],
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "week1_thermal.json"
        json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Results -> {json_path}")

    # Console summary
    print(f"Warning  boundary: {warning_temp:.1f} C  (sigma_Phi = {monitor.sigma_phi_threshold})")
    print(f"Critical boundary: {critical_temp:.1f} C  (sigma_Phi = {monitor.critical_threshold})")

    zone_counts = {"stable": 0, "warning": 0, "critical": 0}
    for s in samples:
        zone_counts[s.safety_state] += 1
    for zone, count in zone_counts.items():
        print(f"  {zone}: {count} points")

    if make_plot:
        _plot_thermal_sweep(samples, monitor, output_dir)

    return result


def _plot_thermal_sweep(
    samples: list[ThermalSample],
    monitor: AFETSafetyMonitor,
    output_dir: Path | None,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    temps = [s.temperature_c for s in samples]
    sigmas = [s.sigma_phi for s in samples]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(temps, sigmas, "k-", linewidth=1.5, label=r"$\sigma_\Phi(T)$")
    ax.axhline(
        monitor.sigma_phi_threshold,
        color="orange",
        linestyle="--",
        linewidth=1,
        label=f"warning = {monitor.sigma_phi_threshold}",
    )
    ax.axhline(
        monitor.critical_threshold,
        color="red",
        linestyle="--",
        linewidth=1,
        label=f"critical = {monitor.critical_threshold}",
    )
    ax.axvline(
        MAX_OPERATING_TEMP_C,
        color="gray",
        linestyle=":",
        linewidth=1,
        label=f"HfO2 max = {MAX_OPERATING_TEMP_C} C",
    )
    ax.set_xlabel("Temperature (C)")
    ax.set_ylabel(r"$\sigma_\Phi$")
    ax.set_title("HfO2 Thermal Stability — AFET Safety Zones")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if output_dir is not None:
        plot_dir = output_dir.parent / "plots"
        plot_dir.mkdir(parents=True, exist_ok=True)
        path = plot_dir / "sigma_phi_thermal.png"
        fig.savefig(str(path), dpi=200)
        print(f"Plot -> {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 1 thermal simulation")
    parser.add_argument("--no-plot", action="store_true", help="skip plot generation")
    args = parser.parse_args()
    run_thermal_simulation(
        output_dir=Path("experiments/week1/results"),
        make_plot=not args.no_plot,
    )
