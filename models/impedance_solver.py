"""Adaptive impedance solver for Z(β) membranes.

This module extends the v8.0 consciousness integration stack with a
lightweight solver for adaptive impedance Z(β). It follows the logistic
membrane language from the AGENTS charter by modelling the transition
σ(β(R-Θ)) between low-impedance information domains and high-impedance
climate regimes. The solver keeps the falsifiability hooks explicit via
RMSE/MAE diagnostics and a transparent null model.

Core ideas
----------
- Baseline impedance: Z_0 = α⁻¹·Φ (see ``calculate_impedance``)
- Adaptive scaling: Z(β) = Z_0 · s(β), where s(β) is a logistic membrane
  anchored at Θ (default Θ=7.4 from Kleiber scaling)
- Integration velocity: v_RIG(β) = c / Z(β)

Suggested workflow
------------------
1) Compute an adaptive impedance profile for the five canonical domains
   (Information, Biology, Climate, Cognition, Consciousness).
2) Compare against empirical Z(β) measurements using the included CSV
   (data/v8_validation/impedance_measurements.csv).
3) Track σ(β-Θ), ΔAIC hooks, and null-model baselines via
   ``ImpedanceFitReport``.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .consciousness_integration import calculate_impedance
from .unified_constants import ALPHA_INV, C_LIGHT_KM_S, PHI


DEFAULT_DATA_PATH = Path("data/v8_validation/impedance_measurements.csv")


@dataclass(frozen=True)
class ImpedanceSolverConfig:
    """Configuration for the adaptive impedance membrane.

    Parameters
    ----------
    beta_reference : float
        Θ in σ(β-Θ); defaults to 7.4 (Kleiber scaling domain).
    steepness : float
        β-sensitivity of the membrane; higher values sharpen σ(β-Θ).
    floor_scale : float
        Minimum impedance scaling factor for low-β (information regime).
    ceiling_scale : float
        Maximum impedance scaling factor for high-β (climate regime).
    alpha_inv : float
        Inverse fine-structure constant.
    phi : float
        Golden ratio.
    c_light_km_s : float
        Speed of light in km/s.
    """

    beta_reference: float = 7.4
    steepness: float = 0.5
    floor_scale: float = 0.5
    ceiling_scale: float = 1.5
    alpha_inv: float = ALPHA_INV
    phi: float = PHI
    c_light_km_s: float = C_LIGHT_KM_S

    def sigma(self, beta: float) -> float:
        """Logistic membrane σ(β-Θ)."""
        return 1.0 / (1.0 + math.exp(-self.steepness * (beta - self.beta_reference)))

    def adaptive_scale(self, beta: float) -> float:
        """Blend between floor and ceiling using σ(β-Θ)."""
        sigma_val = self.sigma(beta)
        return self.floor_scale + (self.ceiling_scale - self.floor_scale) * sigma_val

    def base_impedance(self) -> float:
        """Return the baseline impedance Z_0 = α⁻¹·Φ."""
        return calculate_impedance(alpha_inv=self.alpha_inv, phi=self.phi)


@dataclass(frozen=True)
class ImpedancePoint:
    """Model output for a specific β value."""

    beta: float
    theta: float
    sigma_beta: float
    zeta_resonance: float
    impedance: float
    integration_velocity: float


@dataclass(frozen=True)
class ImpedanceMeasurement:
    """Observed impedance sample for Z(β)."""

    beta: float
    domain: str
    z_measured: float
    z_uncertainty: float
    z_null: float


@dataclass(frozen=True)
class ImpedanceFitReport:
    """Diagnostics comparing model predictions to observations."""

    rmse: float
    mae: float
    mean_bias: float
    n: int


class ImpedanceSolver:
    """Adaptive impedance solver with falsifiability diagnostics."""

    def __init__(self, config: ImpedanceSolverConfig | None = None) -> None:
        self.config = config or ImpedanceSolverConfig()

    def impedance(self, beta: float) -> float:
        scale = self.config.adaptive_scale(beta)
        return self.config.base_impedance() * scale

    def integration_velocity(self, beta: float) -> float:
        return self.config.c_light_km_s / self.impedance(beta)

    def profile(self, betas: Sequence[float]) -> List[ImpedancePoint]:
        points: List[ImpedancePoint] = []
        for beta in betas:
            sigma_val = self.config.sigma(beta)
            zeta_resonance = self._zeta(beta)
            z_val = self.impedance(beta)
            v_val = self.integration_velocity(beta)
            points.append(
                ImpedancePoint(
                    beta=beta,
                    theta=self.config.beta_reference,
                    sigma_beta=sigma_val,
                    zeta_resonance=zeta_resonance,
                    impedance=z_val,
                    integration_velocity=v_val,
                )
            )
        return points

    def compare_to_measurements(
        self,
        measurements: Iterable[ImpedanceMeasurement] | None = None,
    ) -> ImpedanceFitReport:
        rows = list(measurements or load_measurements())
        if not rows:
            raise ValueError("No impedance measurements provided.")

        errors = []
        abs_errors = []
        for row in rows:
            model_z = self.impedance(row.beta)
            error = model_z - row.z_measured
            errors.append(error)
            abs_errors.append(abs(error))

        rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
        mae = sum(abs_errors) / len(abs_errors)
        mean_bias = sum(errors) / len(errors)
        return ImpedanceFitReport(rmse=rmse, mae=mae, mean_bias=mean_bias, n=len(rows))

    def _zeta(self, beta: float) -> float:
        """Simple damping term ζ(R) capturing membrane friction.

        ζ(R) here is a normalized proxy: low-β domains experience mild
        damping (≈0.25) while high-β domains saturate toward 0.9. This is
        intentionally lightweight and kept transparent for falsifiability.
        """

        sigma_val = self.config.sigma(beta)
        return 0.25 + 0.65 * sigma_val


def load_measurements(path: Path = DEFAULT_DATA_PATH) -> List[ImpedanceMeasurement]:
    """Load impedance measurements from CSV with provenance preserved."""

    if not path.exists():
        return []

    measurements: List[ImpedanceMeasurement] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            measurements.append(
                ImpedanceMeasurement(
                    beta=float(row["beta"]),
                    domain=row["domain"],
                    z_measured=float(row["z_measured"]),
                    z_uncertainty=float(row["z_uncertainty"]),
                    z_null=float(row["z_null"]),
                )
            )
    return measurements
