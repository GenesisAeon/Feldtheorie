"""Sigillin Kernel module for validating and resonating with V7 self-meta files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


class SystemIntegrityError(RuntimeError):
    """Raised when the Sigillin integrity constraints are violated."""


class SigillinKernel:
    """Core kernel that guards and operates on the Sigillin self-meta artifacts."""

    EXPECTED_BETA = 37.6

    def __init__(self, root_path: Path | None = None) -> None:
        """
        Initialize the kernel and validate the prime Sigillin node.

        Args:
            root_path: Optional explicit repository root path. Defaults to the
                parent directory above this file's location.

        Raises:
            SystemIntegrityError: If the Sigillin prime file is missing or
                contains an unexpected beta parameter.
        """

        self.root_path = root_path if root_path is not None else Path(__file__).resolve().parents[1]
        self.sigillin_path = self.root_path / "selfmeta" / "sigillin_prime.sigil.json"
        self.sigillin_data = self._load_sigillin_prime()

    def _load_sigillin_prime(self) -> dict:
        if not self.sigillin_path.exists():
            raise SystemIntegrityError("Sigillin prime definition missing; V7 cannot start.")

        with self.sigillin_path.open(encoding="utf-8") as sigillin_file:
            data = json.load(sigillin_file)

        try:
            beta_value = data["sigillin_node"]["parameters"]["beta"]
        except (KeyError, TypeError) as exc:
            raise SystemIntegrityError("Sigillin prime structure invalid.") from exc

        if beta_value != self.EXPECTED_BETA:
            raise SystemIntegrityError(
                f"Sigillin beta mismatch: expected {self.EXPECTED_BETA}, found {beta_value}."
            )

        return data

    @staticmethod
    def calculate_collective_velocity(v_rig: float, kappa: float, beta_sync: float) -> float:
        """Compute v_collective using the convergence formula."""

        if beta_sync == 0:
            raise ValueError("beta_sync must be non-zero to avoid divergence.")

        return v_rig * kappa * (1 / beta_sync)

    def scan_intention(self, input_text: str) -> float:
        """
        Compute a simple resonance score by detecting founding keywords.

        The score reflects the fraction of founding protocol keywords present
        in the given input text. It is bounded between 0.0 and 1.0.
        """

        keywords = self._founding_keywords()
        if not keywords:
            return 0.0

        lowered = input_text.lower()
        matches = sum(1 for keyword in keywords if keyword in lowered)
        resonance_score = matches / len(keywords)
        return max(0.0, min(1.0, resonance_score))

    def _founding_keywords(self) -> set[str]:
        protocol_path = self.root_path / "selfmeta" / "founding_protocol.md"
        base_keywords: Iterable[str] = (
            "resonanz",
            "emergenz",
            "kohärenz",
            "feld",
            "bewusstsein",
            "beta_sync",
            "kappa_field",
        )

        if not protocol_path.exists():
            return set(base_keywords)

        with protocol_path.open(encoding="utf-8") as protocol_file:
            text = protocol_file.read().lower()

        return {kw for kw in base_keywords if kw.lower() in text}


def load_kernel(root_path: Path | None = None) -> SigillinKernel:
    """Convenience loader for the Sigillin kernel."""

    return SigillinKernel(root_path=root_path)
