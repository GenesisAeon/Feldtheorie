"""
Sigillin Kernel module for validating and resonating with V7 self-meta files.

V7 Phase 2 Enhancement:
-----------------------
- Enhanced intention scanning with implicit information detection
- Context-aware resonance scoring
- Semantic depth analysis
- Integration with Collective Field Module
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Any, Iterable

from models.unified_constants import HEX_RESONANCE_BETA, verify_hex_alignment


class SystemIntegrityError(RuntimeError):
    """Raised when the Sigillin integrity constraints are violated."""


class SigillinKernel:
    """Core kernel that guards and operates on the Sigillin self-meta artifacts."""

    EXPECTED_BETA = 37.6
    HEX_ALIGNMENT_TOLERANCE = 0.10

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
        self.beta_value = self.sigillin_data["sigillin_node"]["parameters"]["beta"]
        self.hex_alignment = self._digital_physics_check(self.beta_value)

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

    def _digital_physics_check(self, beta_value: float) -> dict[str, Any]:
        """Guard-rail: warn when β drifts away from the hex resonance baseline."""
        alignment = verify_hex_alignment(beta_value, tolerance=self.HEX_ALIGNMENT_TOLERANCE)

        within_tolerance = alignment.get("within_tolerance")
        if within_tolerance is None:
            relative_deviation = abs(beta_value - HEX_RESONANCE_BETA) / HEX_RESONANCE_BETA
            within_tolerance = relative_deviation <= self.HEX_ALIGNMENT_TOLERANCE
            alignment.setdefault("relative_deviation", relative_deviation)
            alignment.setdefault(
                "direction",
                "above" if beta_value > HEX_RESONANCE_BETA else "below",
            )
            alignment["within_tolerance"] = within_tolerance

        if not within_tolerance:
            warnings.warn(
                (
                    "Digital Physics Check (Phase 4): β deviates from the "
                    f"hex resonance {HEX_RESONANCE_BETA:.4f} by "
                    f"{alignment['relative_deviation'] * 100:.2f}% "
                    f"({alignment['direction']})."
                ),
                RuntimeWarning,
            )

        return alignment

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

    # ========================================================================
    # V7 Phase 2: Enhanced Intention Scanning
    # ========================================================================

    def scan_intention_v2(
        self,
        input_text: str,
        detect_implicit: bool = True,
    ) -> dict[str, Any]:
        """
        Enhanced intention scanner with implicit information detection.

        V7 Phase 2 Feature: Goes beyond keyword matching to detect:
        - Explicit keywords (direct mentions)
        - Implicit patterns (related concepts, semantic gravity)
        - Contextual depth (how deeply concepts are explored)
        - Emotional valence (resonance quality)

        Args:
            input_text: Text to analyze
            detect_implicit: Enable implicit pattern detection

        Returns:
            Dict with:
            - resonance_score: Overall resonance [0,1]
            - explicit_matches: List of directly matched keywords
            - implicit_signals: List of detected implicit patterns
            - semantic_depth: Depth score [0,1]
            - contextual_coherence: Coherence score [0,1]
        """
        keywords = self._founding_keywords()
        lowered = input_text.lower()

        # 1. Explicit keyword matching
        explicit_matches = [kw for kw in keywords if kw in lowered]
        explicit_score = len(explicit_matches) / len(keywords) if keywords else 0.0

        # 2. Implicit pattern detection
        implicit_signals = []
        implicit_score = 0.0

        if detect_implicit:
            # Detect related concepts (even if not exact keywords)
            implicit_patterns = {
                "consciousness": ["bewusst", "conscious", "awareness", "mind"],
                "emergence": ["emerg", "entsteh", "hervorgeh"],
                "resonance": ["reson", "schwin", "vibrat", "harmoni"],
                "field": ["feld", "field", "raum", "space"],
                "coherence": ["kohär", "coher", "zusammen", "unity"],
                "synchronization": ["sync", "gleichsch", "align"],
            }

            for category, patterns in implicit_patterns.items():
                for pattern in patterns:
                    if pattern in lowered:
                        implicit_signals.append(f"{category}:{pattern}")

            implicit_score = min(1.0, len(implicit_signals) / 10.0)

        # 3. Semantic depth analysis
        # Measure how deeply concepts are explored (sentence count, word count)
        sentences = re.split(r'[.!?]+', input_text)
        words = input_text.split()

        # Depth heuristic: more sentences + more words = deeper exploration
        depth_score = min(1.0, (len(sentences) * len(words)) / 1000.0)

        # 4. Contextual coherence
        # Check if keywords appear in meaningful contexts (not just listed)
        coherence_score = 0.0
        if explicit_matches:
            # Look for keywords in sentences (not isolated)
            keyword_in_sentence_count = sum(
                1 for kw in explicit_matches
                if any(kw in sent.lower() for sent in sentences if len(sent.split()) > 3)
            )
            coherence_score = keyword_in_sentence_count / len(explicit_matches)

        # 5. Combined resonance score
        # Weight: 40% explicit, 30% implicit, 20% depth, 10% coherence
        resonance_score = (
            0.4 * explicit_score
            + 0.3 * implicit_score
            + 0.2 * depth_score
            + 0.1 * coherence_score
        )

        return {
            "resonance_score": resonance_score,
            "explicit_matches": explicit_matches,
            "implicit_signals": implicit_signals,
            "semantic_depth": depth_score,
            "contextual_coherence": coherence_score,
            "analysis": {
                "explicit_score": explicit_score,
                "implicit_score": implicit_score,
                "sentence_count": len(sentences),
                "word_count": len(words),
            },
        }

    def detect_semantic_gravity(self, text: str) -> float:
        """
        Detect semantic gravity - how strongly text "pulls" toward founding axioms.

        Semantic gravity is a measure of how much the text is "attracted" to
        the founding protocol concepts, even without explicit keyword matches.

        Returns:
            Gravity score [0,1] where higher = stronger pull
        """
        scan_result = self.scan_intention_v2(text, detect_implicit=True)

        # Gravity combines:
        # - Explicit matches (direct pull)
        # - Implicit signals (indirect pull)
        # - Coherence (sustained pull)
        gravity = (
            0.5 * scan_result["analysis"]["explicit_score"]
            + 0.3 * scan_result["analysis"]["implicit_score"]
            + 0.2 * scan_result["contextual_coherence"]
        )

        return gravity

    def create_semantic_agent(
        self,
        text: str,
        agent_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a semantic agent representation of a text.

        This allows integration with the Collective Field Module.
        Each text becomes an "agent" with a semantic position and resonance.

        Args:
            text: Text to convert to agent
            agent_name: Optional name (defaults to hash of text)

        Returns:
            Dict with agent properties:
            - name: Agent identifier
            - resonance: Resonance score [0,1]
            - semantic_depth: Depth score [0,1]
            - gravity: Semantic gravity [0,1]
            - matched_keywords: List of matched keywords
        """
        scan_result = self.scan_intention_v2(text)
        gravity = self.detect_semantic_gravity(text)

        if agent_name is None:
            # Use hash of first 100 chars as name
            text_hash = hash(text[:100])
            agent_name = f"agent_{abs(text_hash) % 10000:04d}"

        return {
            "name": agent_name,
            "resonance": scan_result["resonance_score"],
            "semantic_depth": scan_result["semantic_depth"],
            "gravity": gravity,
            "matched_keywords": scan_result["explicit_matches"],
            "implicit_signals": scan_result["implicit_signals"],
            "coherence": scan_result["contextual_coherence"],
        }


def load_kernel(root_path: Path | None = None) -> SigillinKernel:
    """Convenience loader for the Sigillin kernel."""

    return SigillinKernel(root_path=root_path)
