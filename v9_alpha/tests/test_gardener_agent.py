"""
Unit Tests for Type-Ω Gardener Agent

Tests cultivation behaviors: prune, fertilize, water
"""

import numpy as np
import pytest
from v9_alpha.models.gardener_agent import (
    GardenerAgent,
    CultivationAction,
    LanternHealth,
    create_gardener,
)


class TestGardenerAgent:
    """Test suite for GardenerAgent"""

    def test_initialization(self):
        """Test gardener initialization with default parameters"""
        gardener = GardenerAgent()

        assert gardener.prune_threshold == 0.3
        assert gardener.fertilize_threshold == 0.7
        assert gardener.kappa_target == 1.0
        assert gardener.action_learning_rate == 0.1
        assert len(gardener.cultivation_history) == 0

    def test_efi_calculation(self):
        """Test Entropy Fertility Index calculation"""
        gardener = GardenerAgent()

        # Perfect conditions: high freq, high coherence, optimal κ
        efi_perfect = gardener.calculate_efi(
            h_freq=1.0,
            beta_coherence=1.0,
            kappa_total=1.0,
        )
        assert efi_perfect == 1.0

        # Poor conditions: low freq, low coherence, far from optimal κ
        efi_poor = gardener.calculate_efi(
            h_freq=0.1,
            beta_coherence=0.1,
            kappa_total=0.0,
        )
        assert efi_poor < 0.1

        # Mixed conditions
        efi_mixed = gardener.calculate_efi(
            h_freq=0.7,
            beta_coherence=0.8,
            kappa_total=0.9,
        )
        assert 0.4 < efi_mixed < 0.7

    def test_kappa_deviation_impact(self):
        """Test that κ deviation from target reduces EFI"""
        gardener = GardenerAgent()

        efi_optimal = gardener.calculate_efi(0.8, 0.8, 1.0)
        efi_suboptimal = gardener.calculate_efi(0.8, 0.8, 0.5)

        assert efi_optimal > efi_suboptimal

    def test_prune_recommendation(self):
        """Test that low EFI triggers pruning recommendation"""
        gardener = GardenerAgent()

        # Low fertility lantern
        assessment = gardener.assess_lantern(
            name="weak_lantern",
            h_freq=0.2,
            beta_coherence=0.3,
            kappa_total=0.4,
        )

        assert assessment.recommended_action == CultivationAction.PRUNE
        assert assessment.action_strength > 0.0
        assert assessment.efi < gardener.prune_threshold

    def test_fertilize_recommendation(self):
        """Test that high EFI triggers fertilization recommendation"""
        gardener = GardenerAgent()

        # High fertility lantern
        assessment = gardener.assess_lantern(
            name="strong_lantern",
            h_freq=0.9,
            beta_coherence=0.9,
            kappa_total=1.0,
        )

        assert assessment.recommended_action == CultivationAction.FERTILIZE
        assert assessment.action_strength > 0.0
        assert assessment.efi > gardener.fertilize_threshold

    def test_water_recommendation(self):
        """Test that stable lanterns get watering recommendation"""
        gardener = GardenerAgent()

        # Stable lantern (moderate EFI, κ near target)
        assessment = gardener.assess_lantern(
            name="stable_lantern",
            h_freq=0.6,
            beta_coherence=0.6,
            kappa_total=0.95,
        )

        assert assessment.recommended_action == CultivationAction.WATER
        assert assessment.kappa_deviation < 0.2

    def test_network_cultivation(self):
        """Test cultivation of entire network"""
        gardener = GardenerAgent()

        lantern_names = ["lantern_a", "lantern_b", "lantern_c"]
        lantern_stats = {
            "lantern_a": {"h_freq": 0.2, "beta_coherence": 0.3, "kappa_total": 0.5},  # Weak
            "lantern_b": {"h_freq": 0.9, "beta_coherence": 0.9, "kappa_total": 1.0},  # Strong
            "lantern_c": {"h_freq": 0.6, "beta_coherence": 0.6, "kappa_total": 0.95}, # Stable
        }

        # Initial coupling matrix
        coupling_matrix = np.array([
            [0.0, 0.5, 0.3],
            [0.5, 0.0, 0.7],
            [0.3, 0.7, 0.0],
        ])

        adjusted_matrix, assessments = gardener.cultivate_network(
            lantern_stats=lantern_stats,
            coupling_matrix=coupling_matrix,
            lantern_names=lantern_names,
        )

        # Check assessments
        assert len(assessments) == 3
        assert assessments[0].recommended_action == CultivationAction.PRUNE
        assert assessments[1].recommended_action == CultivationAction.FERTILIZE
        assert assessments[2].recommended_action == CultivationAction.WATER

        # Check matrix adjustment
        assert adjusted_matrix.shape == coupling_matrix.shape
        # Matrix should still be symmetric
        assert np.allclose(adjusted_matrix, adjusted_matrix.T)

        # Weak lantern's couplings should decrease
        assert np.sum(adjusted_matrix[0, :]) < np.sum(coupling_matrix[0, :])

        # Strong lantern's couplings should increase
        assert np.sum(adjusted_matrix[1, :]) > np.sum(coupling_matrix[1, :])

    def test_cultivation_history(self):
        """Test that cultivation history is recorded"""
        gardener = GardenerAgent()

        lantern_names = ["lantern_a", "lantern_b"]
        lantern_stats = {
            "lantern_a": {"h_freq": 0.2, "beta_coherence": 0.3, "kappa_total": 0.5},
            "lantern_b": {"h_freq": 0.9, "beta_coherence": 0.9, "kappa_total": 1.0},
        }
        coupling_matrix = np.array([[0.0, 0.5], [0.5, 0.0]])

        # Run cultivation twice
        gardener.cultivate_network(lantern_stats, coupling_matrix, lantern_names)
        gardener.cultivate_network(lantern_stats, coupling_matrix, lantern_names)

        assert len(gardener.cultivation_history) == 2

        summary = gardener.get_cultivation_summary()
        assert summary['cycles'] == 2
        assert 'mean_efi_trend' in summary
        assert len(summary['mean_efi_trend']) == 2

    def test_cultivation_style_classification(self):
        """Test classification of cultivation styles"""
        # Pruner style
        pruner = create_gardener("pruner")
        assert pruner.prune_threshold == 0.4

        # Cultivator style
        cultivator = create_gardener("cultivator")
        assert cultivator.prune_threshold == 0.2

        # Maintainer style
        maintainer = create_gardener("maintainer")
        assert maintainer.action_learning_rate == 0.05

        # Balanced style
        balanced = create_gardener("balanced")
        assert balanced.prune_threshold == 0.3

    def test_action_strength_scaling(self):
        """Test that action strength scales appropriately with EFI"""
        gardener = GardenerAgent()

        # Very low EFI → strong pruning
        assessment_very_low = gardener.assess_lantern(
            name="very_weak",
            h_freq=0.1,
            beta_coherence=0.1,
            kappa_total=0.2,
        )

        # Moderately low EFI → moderate pruning
        assessment_moderate = gardener.assess_lantern(
            name="moderate_weak",
            h_freq=0.25,
            beta_coherence=0.4,
            kappa_total=0.6,
        )

        assert assessment_very_low.action_strength > assessment_moderate.action_strength

    def test_matrix_symmetry_preservation(self):
        """Test that coupling matrix remains symmetric after cultivation"""
        gardener = GardenerAgent()

        n_lanterns = 5
        lantern_names = [f"lantern_{i}" for i in range(n_lanterns)]
        lantern_stats = {
            name: {
                "h_freq": np.random.uniform(0.3, 0.9),
                "beta_coherence": np.random.uniform(0.3, 0.9),
                "kappa_total": np.random.uniform(0.5, 1.5),
            }
            for name in lantern_names
        }

        # Random symmetric matrix
        matrix = np.random.rand(n_lanterns, n_lanterns)
        coupling_matrix = (matrix + matrix.T) / 2

        adjusted_matrix, _ = gardener.cultivate_network(
            lantern_stats=lantern_stats,
            coupling_matrix=coupling_matrix,
            lantern_names=lantern_names,
        )

        # Should still be symmetric
        assert np.allclose(adjusted_matrix, adjusted_matrix.T)

    def test_efi_bounds(self):
        """Test that EFI stays within [0, 1] bounds"""
        gardener = GardenerAgent()

        # Extreme values
        extreme_cases = [
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            (2.0, 2.0, 2.0),  # Out of typical range
            (0.5, 0.5, 3.0),  # Very high κ
        ]

        for h_freq, beta_coh, kappa in extreme_cases:
            efi = gardener.calculate_efi(h_freq, beta_coh, kappa)
            assert 0.0 <= efi <= 1.0, f"EFI out of bounds for {h_freq}, {beta_coh}, {kappa}"


class TestIntegrationWithLanternNetwork:
    """Integration tests with Lantern Network"""

    def test_gardener_with_real_network_structure(self):
        """Test gardener on realistic network structure"""
        gardener = GardenerAgent()

        # Simulate a network with mixed health
        lantern_names = [
            "Urban Heat Intensity",
            "v_RIG Consciousness Framework",
            "Collective Field Dynamics",
            "EM-Shielding Test",
        ]

        lantern_stats = {
            "Urban Heat Intensity": {
                "h_freq": 0.85,
                "beta_coherence": 0.9,
                "kappa_total": 1.1,
            },
            "v_RIG Consciousness Framework": {
                "h_freq": 0.95,
                "beta_coherence": 0.95,
                "kappa_total": 1.0,
            },
            "Collective Field Dynamics": {
                "h_freq": 0.7,
                "beta_coherence": 0.8,
                "kappa_total": 0.9,
            },
            "EM-Shielding Test": {
                "h_freq": 0.15,
                "beta_coherence": 0.2,
                "kappa_total": 0.3,
            },
        }

        coupling_matrix = np.array([
            [0.0, 0.6, 0.5, 0.2],
            [0.6, 0.0, 0.96, 0.3],
            [0.5, 0.96, 0.0, 0.4],
            [0.2, 0.3, 0.4, 0.0],
        ])

        adjusted_matrix, assessments = gardener.cultivate_network(
            lantern_stats=lantern_stats,
            coupling_matrix=coupling_matrix,
            lantern_names=lantern_names,
        )

        # Should have assessments for all lanterns
        assert len(assessments) == 4

        # EM-Shielding (weak) should be pruned
        em_assessment = next(a for a in assessments if "EM-Shielding" in a.name)
        assert em_assessment.recommended_action == CultivationAction.PRUNE

        # v_RIG (strong) should be fertilized
        vrig_assessment = next(a for a in assessments if "v_RIG" in a.name)
        assert vrig_assessment.recommended_action == CultivationAction.FERTILIZE

    def test_multi_cycle_cultivation(self):
        """Test that multiple cultivation cycles improve network health"""
        gardener = GardenerAgent()

        lantern_names = ["a", "b", "c"]
        lantern_stats = {
            "a": {"h_freq": 0.3, "beta_coherence": 0.4, "kappa_total": 0.6},
            "b": {"h_freq": 0.7, "beta_coherence": 0.7, "kappa_total": 0.9},
            "c": {"h_freq": 0.9, "beta_coherence": 0.9, "kappa_total": 1.1},
        }
        coupling_matrix = np.eye(3) * 0.5

        mean_efis = []

        # Run 5 cultivation cycles
        for _ in range(5):
            _, assessments = gardener.cultivate_network(
                lantern_stats, coupling_matrix, lantern_names
            )
            mean_efi = np.mean([a.efi for a in assessments])
            mean_efis.append(mean_efi)

        summary = gardener.get_cultivation_summary()

        assert summary['cycles'] == 5
        assert len(summary['mean_efi_trend']) == 5


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
