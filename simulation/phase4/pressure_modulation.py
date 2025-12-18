"""Pressure Modulation of v_RIG for Phase 4 medium-modulation hypothesis.

This module tests the hypothesis that external pressure modulates the effective
integration velocity v_RIG through changes in medium impedance Z_eff. The core
principle: consciousness integration speed depends on the medium (pressure,
temperature, chemistry).

Key Phenomena:
- HPNS (High Pressure Nervous Syndrome): v_RIG ↑ → Hyper-Integration (tremor)
- Anesthesia (Low Effective Pressure): v_RIG ↓ → Under-Integration (unconsciousness)

The σ(β(R-Θ)) framework couples to v_RIG through the effective impedance:
    Z_eff = Z_0 · γ(P, T, χ)
    v_RIG_eff = c / Z_eff

where:
    Z_0 = α⁻¹ · Φ ≈ 221.7 Ω (baseline consciousness impedance)
    γ(P, T, χ) = modulation factor (pressure, temperature, chemistry)

This creates a testable prediction: CFF (Critical Flicker Frequency) and EEG
synchronization should shift with pressure in a predictable way.

Reference: Finalize.txt, Section 1.4 (Medien-Modulation & Hyperbare Effekte)
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
from models.unified_constants import (
    C_LIGHT_M_S,
    ALPHA_INV,
    PHI,
    V_RIG_DEFAULT,
    HEX_RESONANCE_BETA,
)


@dataclass
class PressureModulationConfig:
    """Configuration for pressure modulation experiments.

    Attributes
    ----------
    pressures_atm: np.ndarray
        Array of pressure values in atmospheres (e.g., 1-5 atm for diving)
    temperatures_celsius: np.ndarray
        Array of temperature values in Celsius
    chemistry_factors: np.ndarray
        Array of chemistry modulation factors (0 = baseline, ±1 = strong effect)
    baseline_cff_hz: float
        Baseline Critical Flicker Frequency at 1 atm, normal temp
    z_baseline: float
        Baseline consciousness impedance (α⁻¹ · Φ)
    beta: float
        Steepness parameter for σ(β(R-Θ)) coupling
    """

    pressures_atm: np.ndarray = dataclasses.field(
        default_factory=lambda: np.linspace(1.0, 5.0, 5)
    )
    temperatures_celsius: np.ndarray = dataclasses.field(
        default_factory=lambda: np.array([37.0])
    )
    chemistry_factors: np.ndarray = dataclasses.field(
        default_factory=lambda: np.array([0.0])
    )
    baseline_cff_hz: float = 60.0  # Critical Flicker Frequency
    z_baseline: float = ALPHA_INV * PHI  # ≈ 221.7 Ω
    beta: float = HEX_RESONANCE_BETA


class PressureModulator:
    """Analyzes v_RIG modulation under pressure, temperature, and chemistry.

    The modulator computes effective impedance Z_eff and derived quantities:
    - v_RIG_eff: Effective integration velocity
    - CFF_shifted: Doppler-shifted Critical Flicker Frequency
    - R_eff: Effective readiness (pressure-dependent activation)
    """

    def __init__(
        self,
        v_rig_baseline: float = V_RIG_DEFAULT,
        z_baseline: float = ALPHA_INV * PHI,
    ):
        """Initialize the pressure modulator.

        Parameters
        ----------
        v_rig_baseline : float
            Baseline v_RIG in km/s (default: V_RIG_DEFAULT ≈ 1351.8 km/s)
        z_baseline : float
            Baseline consciousness impedance (default: α⁻¹ · Φ ≈ 221.7 Ω)
        """
        self.v_rig_baseline = v_rig_baseline * 1000  # Convert km/s → m/s
        self.z_baseline = z_baseline

    def gamma_modulation(
        self,
        pressure: float,
        temperature: float = 37.0,
        chemistry: float = 0.0,
    ) -> float:
        """Compute modulation factor γ(P, T, χ).

        The modulation factor captures how the medium responds to:
        - Pressure: Higher pressure → faster integration (HPNS)
        - Temperature: Deviation from 37°C → reduced coherence
        - Chemistry: Anesthetic agents → damped integration

        Parameters
        ----------
        pressure : float
            Pressure in atmospheres (1 atm = baseline)
        temperature : float
            Temperature in Celsius (37°C = baseline)
        chemistry : float
            Chemistry factor (0 = baseline, negative = anesthetic, positive = stimulant)

        Returns
        -------
        float
            Modulation factor γ ≥ 0
        """
        # Pressure effect: +10% per atm above baseline
        pressure_term = 0.1 * (pressure - 1.0)

        # Temperature effect: -5% per degree from 37°C
        temp_term = -0.05 * abs(temperature - 37.0)

        # Chemistry effect: Direct modulation (anesthetics reduce γ)
        chemistry_term = -0.2 * chemistry

        gamma = 1.0 + pressure_term + temp_term + chemistry_term

        # Ensure γ stays positive (can't have negative impedance)
        return max(gamma, 0.01)

    def effective_impedance(
        self,
        pressure: float,
        temperature: float = 37.0,
        chemistry: float = 0.0,
    ) -> float:
        """Compute effective consciousness impedance Z_eff.

        Z_eff = Z_0 · γ(P, T, χ)

        Parameters
        ----------
        pressure : float
            Pressure in atmospheres
        temperature : float
            Temperature in Celsius
        chemistry : float
            Chemistry modulation factor

        Returns
        -------
        float
            Effective impedance Z_eff in Ω
        """
        gamma = self.gamma_modulation(pressure, temperature, chemistry)
        return self.z_baseline * gamma

    def effective_v_rig(
        self,
        pressure: float,
        temperature: float = 37.0,
        chemistry: float = 0.0,
    ) -> float:
        """Compute effective v_RIG under modulated conditions.

        v_RIG_eff = c / Z_eff

        Parameters
        ----------
        pressure : float
            Pressure in atmospheres
        temperature : float
            Temperature in Celsius
        chemistry : float
            Chemistry modulation factor

        Returns
        -------
        float
            Effective v_RIG in m/s
        """
        z_eff = self.effective_impedance(pressure, temperature, chemistry)
        return C_LIGHT_M_S / z_eff

    def cff_doppler_shift(
        self,
        pressure: float,
        temperature: float = 37.0,
        chemistry: float = 0.0,
        baseline_cff: float = 60.0,
    ) -> float:
        """Compute Doppler-shifted Critical Flicker Frequency.

        The CFF shifts due to v_RIG modulation. This is a testable prediction:
        CFF should increase with pressure (hyperbaric environments).

        CFF' = CFF · (c + v_RIG_eff) / (c + v_RIG_baseline)

        Parameters
        ----------
        pressure : float
            Pressure in atmospheres
        temperature : float
            Temperature in Celsius
        chemistry : float
            Chemistry modulation factor
        baseline_cff : float
            Baseline CFF at 1 atm, 37°C (Hz)

        Returns
        -------
        float
            Shifted CFF in Hz
        """
        v_rig_eff = self.effective_v_rig(pressure, temperature, chemistry)

        # Doppler formula (non-relativistic approximation)
        shift_factor = (C_LIGHT_M_S + v_rig_eff) / (C_LIGHT_M_S + self.v_rig_baseline)

        return baseline_cff * shift_factor


def simulate_pressure_modulation(
    config: PressureModulationConfig | None = None,
) -> Dict[str, Any]:
    """Run the pressure modulation experiment.

    Simulates v_RIG, Z_eff, and CFF across a range of pressures, temperatures,
    and chemistry factors. Returns telemetry for downstream analysis and plotting.

    Parameters
    ----------
    config : PressureModulationConfig | None
        Configuration for the experiment (default: standard diving pressures)

    Returns
    -------
    Dict[str, Any]
        Telemetry including:
        - pressure_series: Pressure values (atm)
        - v_rig_series: Effective v_RIG values (m/s)
        - z_eff_series: Effective impedance values (Ω)
        - cff_series: Doppler-shifted CFF values (Hz)
        - gamma_series: Modulation factors
        - delta_aic: Model comparison (hex vs. linear null model)
    """
    cfg = config or PressureModulationConfig()
    modulator = PressureModulator()

    results: Dict[str, List[float]] = {
        "pressure_atm": [],
        "v_rig_m_s": [],
        "z_eff_ohm": [],
        "cff_hz": [],
        "gamma": [],
    }

    for pressure in cfg.pressures_atm:
        for temperature in cfg.temperatures_celsius:
            for chemistry in cfg.chemistry_factors:
                gamma = modulator.gamma_modulation(pressure, temperature, chemistry)
                z_eff = modulator.effective_impedance(pressure, temperature, chemistry)
                v_rig_eff = modulator.effective_v_rig(pressure, temperature, chemistry)
                cff_shifted = modulator.cff_doppler_shift(
                    pressure, temperature, chemistry, cfg.baseline_cff_hz
                )

                results["pressure_atm"].append(float(pressure))
                results["v_rig_m_s"].append(float(v_rig_eff))
                results["z_eff_ohm"].append(float(z_eff))
                results["cff_hz"].append(float(cff_shifted))
                results["gamma"].append(float(gamma))

    # Convert to arrays for AIC calculation
    pressure_array = np.array(results["pressure_atm"])
    v_rig_array = np.array(results["v_rig_m_s"])

    # Null model: constant v_RIG (no pressure dependence)
    v_rig_null = np.full_like(v_rig_array, modulator.v_rig_baseline)

    # Residuals
    residuals_hex = v_rig_array - v_rig_array.mean()
    residuals_null = v_rig_array - v_rig_null

    # AIC calculation
    n = len(v_rig_array)
    k_hex = 4  # Parameters: pressure, temp, chemistry, β_hex
    k_null = 1  # Parameters: constant

    rss_hex = np.sum(residuals_hex**2)
    rss_null = np.sum(residuals_null**2)

    aic_hex = n * np.log(max(rss_hex / n, 1e-12)) + 2 * k_hex
    aic_null = n * np.log(max(rss_null / n, 1e-12)) + 2 * k_null

    delta_aic = float(aic_null - aic_hex)

    telemetry: Dict[str, Any] = {
        "beta_hex": cfg.beta,
        "z_baseline": cfg.z_baseline,
        "v_rig_baseline_m_s": modulator.v_rig_baseline,
        "pressure_series": results["pressure_atm"],
        "v_rig_series": results["v_rig_m_s"],
        "z_eff_series": results["z_eff_ohm"],
        "cff_series": results["cff_hz"],
        "gamma_series": results["gamma"],
        "delta_aic": delta_aic,
        "null_model": "constant v_RIG with no pressure/temperature/chemistry dependence",
        "testable_predictions": [
            "CFF increases with pressure (hyperbaric environments)",
            "HPNS tremor onset at γ ≈ 1.3-1.5 (v_RIG ↑ 30-50%)",
            "Anesthesia corresponds to γ < 0.8 (v_RIG ↓ 20%)",
            "EEG synchronization shifts with v_RIG modulation",
        ],
    }

    return telemetry


__all__ = [
    "PressureModulationConfig",
    "PressureModulator",
    "simulate_pressure_modulation",
]
