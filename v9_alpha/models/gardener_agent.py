"""
Type-Ω Gardener Agent - Cultivation over Governance

Paradigm Shift:
    v6-v8: Governance → Control → Boundary → Guard Agents
    v9+:   Cultivation → Resonance → Permeability → Gardener Agents

The Gardener Agent assesses lantern fertility and applies cultivation actions:
- Prune: low-fertility lanterns (reduce κ_EM)
- Fertilize: high-potential lanterns (increase κ_EM)
- Water: stable lanterns (maintain resonance)

Goal: Lanterns evolve through anschlussfähigkeit (connectability), not power.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CultivationAction(Enum):
    """Types of cultivation actions the gardener can perform"""
    PRUNE = "prune"        # Reduce coupling for low-fertility lanterns
    FERTILIZE = "fertilize"  # Increase coupling for high-potential lanterns
    WATER = "water"        # Maintain resonance for stable lanterns
    OBSERVE = "observe"    # No action needed, continue monitoring


@dataclass
class LanternHealth:
    """Health assessment of a lantern"""
    name: str
    efi: float  # Entropy Fertility Index
    h_freq: float  # Frequency entropy
    beta_coherence: float  # β-domain coherence
    kappa_total: float  # Total coupling strength
    kappa_deviation: float  # |κ_total - 1.0|
    recommended_action: CultivationAction
    action_strength: float  # How strongly to apply the action (0.0-1.0)

    def __repr__(self):
        return (f"LanternHealth({self.name}, EFI={self.efi:.3f}, "
                f"action={self.recommended_action.value}, "
                f"strength={self.action_strength:.2f})")


class GardenerAgent:
    """
    Type-Ω Gardener Agent for Lantern Network Cultivation

    The gardener assesses each lantern's Entropy Fertility Index (EFI)
    and applies cultivation actions to optimize network resonance.

    EFI = H_freq × β_coherence × (1 - |κ_total - 1.0|)

    where:
        H_freq: Frequency entropy (diversity of interactions)
        β_coherence: How well the lantern aligns with its β-domain
        κ_total: Total coupling strength (optimal ≈ 1.0)
    """

    def __init__(
        self,
        prune_threshold: float = 0.3,
        fertilize_threshold: float = 0.7,
        kappa_target: float = 1.0,
        action_learning_rate: float = 0.1,
    ):
        """
        Initialize Gardener Agent

        Args:
            prune_threshold: EFI below this triggers pruning
            fertilize_threshold: EFI above this triggers fertilization
            kappa_target: Optimal coupling strength (default: 1.0)
            action_learning_rate: How strongly to adjust κ values (0.0-1.0)
        """
        self.prune_threshold = prune_threshold
        self.fertilize_threshold = fertilize_threshold
        self.kappa_target = kappa_target
        self.action_learning_rate = action_learning_rate

        # Cultivation history
        self.cultivation_history: List[Dict] = []

    def calculate_efi(
        self,
        h_freq: float,
        beta_coherence: float,
        kappa_total: float,
    ) -> float:
        """
        Calculate Entropy Fertility Index (EFI)

        EFI = H_freq × β_coherence × (1 - |κ_total - 1.0|)

        High EFI indicates a fertile lantern that's:
        - Diverse in interactions (high H_freq)
        - Well-aligned with its domain (high β_coherence)
        - Near optimal coupling (κ_total ≈ 1.0)

        Args:
            h_freq: Frequency entropy (0.0-1.0)
            beta_coherence: β-domain coherence (0.0-1.0)
            kappa_total: Total coupling strength (typically 0.0-2.0)

        Returns:
            EFI value (0.0-1.0)
        """
        kappa_deviation = abs(kappa_total - self.kappa_target)
        kappa_factor = 1.0 - min(kappa_deviation, 1.0)

        efi = h_freq * beta_coherence * kappa_factor
        return float(np.clip(efi, 0.0, 1.0))

    def assess_lantern(
        self,
        name: str,
        h_freq: float,
        beta_coherence: float,
        kappa_total: float,
    ) -> LanternHealth:
        """
        Assess a lantern's health and recommend cultivation action

        Args:
            name: Lantern name
            h_freq: Frequency entropy
            beta_coherence: β-domain coherence
            kappa_total: Total coupling strength

        Returns:
            LanternHealth assessment with recommended action
        """
        efi = self.calculate_efi(h_freq, beta_coherence, kappa_total)
        kappa_deviation = abs(kappa_total - self.kappa_target)

        # Determine cultivation action based on EFI
        if efi < self.prune_threshold:
            # Low fertility - reduce coupling
            action = CultivationAction.PRUNE
            strength = (self.prune_threshold - efi) / self.prune_threshold
        elif efi > self.fertilize_threshold:
            # High fertility - increase coupling
            action = CultivationAction.FERTILIZE
            strength = (efi - self.fertilize_threshold) / (1.0 - self.fertilize_threshold)
        elif kappa_deviation < 0.2:
            # Stable and near optimal - maintain
            action = CultivationAction.WATER
            strength = 1.0 - kappa_deviation / 0.2
        else:
            # Observable but no action needed
            action = CultivationAction.OBSERVE
            strength = 0.0

        return LanternHealth(
            name=name,
            efi=efi,
            h_freq=h_freq,
            beta_coherence=beta_coherence,
            kappa_total=kappa_total,
            kappa_deviation=kappa_deviation,
            recommended_action=action,
            action_strength=strength,
        )

    def cultivate_network(
        self,
        lantern_stats: Dict[str, Dict[str, float]],
        coupling_matrix: np.ndarray,
        lantern_names: List[str],
    ) -> Tuple[np.ndarray, List[LanternHealth]]:
        """
        Assess entire lantern network and apply cultivation actions

        Args:
            lantern_stats: Dict mapping lantern names to stats
                          (h_freq, beta_coherence, kappa_total)
            coupling_matrix: Current NxN coupling matrix
            lantern_names: Ordered list of lantern names

        Returns:
            (adjusted_coupling_matrix, lantern_assessments)
        """
        assessments = []
        adjusted_matrix = coupling_matrix.copy()

        # Assess each lantern
        for i, name in enumerate(lantern_names):
            if name not in lantern_stats:
                continue

            stats = lantern_stats[name]
            assessment = self.assess_lantern(
                name=name,
                h_freq=stats.get('h_freq', 0.5),
                beta_coherence=stats.get('beta_coherence', 0.5),
                kappa_total=stats.get('kappa_total', 0.5),
            )
            assessments.append(assessment)

            # Apply cultivation action
            if assessment.recommended_action == CultivationAction.PRUNE:
                # Reduce coupling strength
                factor = 1.0 - (self.action_learning_rate * assessment.action_strength)
                adjusted_matrix[i, :] *= factor
                adjusted_matrix[:, i] *= factor

            elif assessment.recommended_action == CultivationAction.FERTILIZE:
                # Increase coupling strength
                factor = 1.0 + (self.action_learning_rate * assessment.action_strength)
                adjusted_matrix[i, :] *= factor
                adjusted_matrix[:, i] *= factor

            elif assessment.recommended_action == CultivationAction.WATER:
                # Maintain resonance - gentle normalization toward κ_target
                current_sum = np.sum(adjusted_matrix[i, :])
                if current_sum > 0:
                    target_sum = self.kappa_target * len(lantern_names)
                    gentle_factor = 1.0 + self.action_learning_rate * (target_sum / current_sum - 1.0)
                    adjusted_matrix[i, :] *= gentle_factor
                    adjusted_matrix[:, i] *= gentle_factor

        # Ensure matrix stays symmetric
        adjusted_matrix = (adjusted_matrix + adjusted_matrix.T) / 2

        # Record cultivation cycle
        self.cultivation_history.append({
            'cycle': len(self.cultivation_history),
            'assessments': assessments,
            'mean_efi': np.mean([a.efi for a in assessments]),
            'actions': {
                'prune': sum(1 for a in assessments if a.recommended_action == CultivationAction.PRUNE),
                'fertilize': sum(1 for a in assessments if a.recommended_action == CultivationAction.FERTILIZE),
                'water': sum(1 for a in assessments if a.recommended_action == CultivationAction.WATER),
                'observe': sum(1 for a in assessments if a.recommended_action == CultivationAction.OBSERVE),
            }
        })

        return adjusted_matrix, assessments

    def get_cultivation_summary(self) -> Dict:
        """
        Get summary statistics of cultivation history

        Returns:
            Dict with summary statistics
        """
        if not self.cultivation_history:
            return {'cycles': 0}

        mean_efis = [cycle['mean_efi'] for cycle in self.cultivation_history]
        total_actions = {action: 0 for action in ['prune', 'fertilize', 'water', 'observe']}

        for cycle in self.cultivation_history:
            for action, count in cycle['actions'].items():
                total_actions[action] += count

        return {
            'cycles': len(self.cultivation_history),
            'mean_efi_trend': mean_efis,
            'final_mean_efi': mean_efis[-1] if mean_efis else 0.0,
            'total_actions': total_actions,
            'cultivation_style': self._classify_style(total_actions),
        }

    def _classify_style(self, actions: Dict[str, int]) -> str:
        """Classify the gardener's cultivation style based on actions"""
        total = sum(actions.values())
        if total == 0:
            return "observer"

        prune_ratio = actions['prune'] / total
        fertilize_ratio = actions['fertilize'] / total

        if prune_ratio > 0.5:
            return "pruner"  # Focuses on removing weak connections
        elif fertilize_ratio > 0.5:
            return "cultivator"  # Focuses on strengthening strong connections
        elif actions['water'] / total > 0.5:
            return "maintainer"  # Focuses on stability
        else:
            return "balanced"  # Mixed strategy


def create_gardener(
    cultivation_style: str = "balanced",
) -> GardenerAgent:
    """
    Factory function to create a gardener with preset cultivation style

    Args:
        cultivation_style: One of "pruner", "cultivator", "maintainer", "balanced"

    Returns:
        Configured GardenerAgent
    """
    if cultivation_style == "pruner":
        return GardenerAgent(
            prune_threshold=0.4,
            fertilize_threshold=0.8,
            action_learning_rate=0.15,
        )
    elif cultivation_style == "cultivator":
        return GardenerAgent(
            prune_threshold=0.2,
            fertilize_threshold=0.6,
            action_learning_rate=0.15,
        )
    elif cultivation_style == "maintainer":
        return GardenerAgent(
            prune_threshold=0.3,
            fertilize_threshold=0.7,
            action_learning_rate=0.05,
        )
    else:  # balanced
        return GardenerAgent(
            prune_threshold=0.3,
            fertilize_threshold=0.7,
            action_learning_rate=0.1,
        )
