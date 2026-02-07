from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class AFETConstants:
    """Central AFET constants shared across modules."""

    BETA_CRITICAL: float = 37.6
    SIGMA_PHI: float = 0.0625
    FREQ_RES: float = 13.5e6
    V_RIG: float = 1.352


class AFETFramework:
    """Reference implementation of AFET axioms and helpers."""

    def __init__(self, constants: AFETConstants = AFETConstants()) -> None:
        self.constants = constants

    _BETA_INFO_ANCHOR = 4.2
    _DIMENSION_EXPONENT = 2.13

    def predict_beta(self, dimension: float) -> float:
        """Predict β from dimension n using AFET n/3 scaling anchors.

        Anchors:
        - n=0 -> β≈4.2
        - n=1 -> β≈7.4
        - n=3 -> β=β_critical
        """
        n = max(0.0, float(dimension))
        scaled = (n / 3.0) ** self._DIMENSION_EXPONENT
        return self._BETA_INFO_ANCHOR + (
            self.constants.BETA_CRITICAL - self._BETA_INFO_ANCHOR
        ) * scaled

    def critical_entropy_density(self) -> float:
        """Return the AFET metastability boundary 1/σΦ."""
        return 1.0 / self.constants.SIGMA_PHI

    def check_metastability(self, entropy_density: float) -> dict[str, float | bool]:
        threshold = self.critical_entropy_density()
        value = float(entropy_density)
        return {
            "entropy_density": value,
            "critical_density": threshold,
            "margin": threshold - value,
            "is_metastable": value <= threshold,
        }

    def integration_rate(self, gradient: float) -> float:
        return self.constants.V_RIG * float(gradient)

    def consciousness_emergence_criterion(
        self,
        surface_entropy: float,
        volume_entropy: float,
    ) -> dict[str, float | bool]:
        delta = float(surface_entropy) - float(volume_entropy)
        return {
            "surface_entropy": float(surface_entropy),
            "volume_entropy": float(volume_entropy),
            "delta_entropy": delta,
            "threshold": self.constants.SIGMA_PHI,
            "emergent": delta >= self.constants.SIGMA_PHI,
        }

    def beta_to_peclet(self, beta: float) -> float:
        """Convert β to normalized Péclet ratio β/β_critical."""
        return float(beta) / self.constants.BETA_CRITICAL

    def peclet_to_beta(self, peclet: float) -> float:
        """Convert normalized Péclet ratio back to β value."""
        return float(peclet) * self.constants.BETA_CRITICAL

    def critical_peclet(self) -> float:
        """Critical Péclet number (equal to β_critical in AFET)."""
        return self.constants.BETA_CRITICAL

    def load_beta_dataset(self, csv_path: str | Path) -> list[dict[str, float | str | int]]:
        frame = pd.read_csv(csv_path)
        records: list[dict[str, float | str | int]] = []
        for row in frame.to_dict(orient="records"):
            domain = str(row.get("domain", "unknown"))
            observed_beta = float(row.get("beta", 0.0))
            if "dimension" in row and row.get("dimension") is not None:
                dimension = float(row["dimension"])
            elif "domain" in row and row.get("domain"):
                dimension = float(self._infer_dimension(domain))
            else:
                dimension = self._estimate_dimension_from_beta(observed_beta)
            records.append(
                {
                    "domain": domain,
                    "dimension": float(dimension),
                    "observed_beta": observed_beta,
                    "predicted_beta": self.predict_beta(dimension),
                }
            )
        return records

    def _estimate_dimension_from_beta(self, beta: float) -> float:
        """Infer an effective dimension from an observed β value."""
        b = float(beta)
        b0 = self._BETA_INFO_ANCHOR
        if b <= b0:
            return 0.0
        span = self.constants.BETA_CRITICAL - b0
        ratio = min(max((b - b0) / span, 0.0), 1.0)
        return 3.0 * (ratio ** (1.0 / self._DIMENSION_EXPONENT))

    @staticmethod
    def _infer_dimension(domain: str) -> int:
        domain_norm = domain.lower()
        if domain_norm.startswith(("llm", "ai")):
            return 0
        if domain_norm.startswith(("bio", "neuro")):
            return 1
        if domain_norm.startswith(("climate", "social", "econ")):
            return 2
        return 3
