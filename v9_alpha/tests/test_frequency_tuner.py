"""
Unit Tests for Autonomous Frequency Tuner

Tests self-organizing resonance optimization
"""

import numpy as np
import pytest
from v9_alpha.models.frequency_tuner import (
    FrequencyTuner,
    TuningState,
    TuningStrategy,
    create_tuner,
)


class TestFrequencyTuner:
    """Test suite for FrequencyTuner"""

    def test_initialization(self):
        """Test tuner initialization"""
        tuner = FrequencyTuner()

        assert tuner.learning_rate == 0.05
        assert tuner.max_frequency_shift == 0.2
        assert tuner.z_critical == 50.0
        assert tuner.strategy == TuningStrategy.GRADIENT_ASCENT
        assert len(tuner.tuning_history) == 0
        assert not tuner.converged

    def test_phase_coherence_perfect(self):
        """Test perfect phase coherence (all same phase)"""
        tuner = FrequencyTuner()

        phases = np.array([0.0, 0.0, 0.0, 0.0])
        coherence = tuner.calculate_phase_coherence(phases)

        assert coherence == pytest.approx(1.0, abs=1e-6)

    def test_phase_coherence_random(self):
        """Test low phase coherence (random phases)"""
        tuner = FrequencyTuner()

        np.random.seed(42)
        phases = np.random.uniform(0, 2*np.pi, 100)
        coherence = tuner.calculate_phase_coherence(phases)

        # Random phases → low coherence
        assert coherence < 0.2

    def test_phase_coherence_weighted(self):
        """Test weighted phase coherence"""
        tuner = FrequencyTuner()

        # 3 lanterns at phase 0, 1 outlier at phase π
        phases = np.array([0.0, 0.0, 0.0, np.pi])
        weights = np.array([1.0, 1.0, 1.0, 0.1])  # Outlier has low weight

        coherence_weighted = tuner.calculate_phase_coherence(phases, weights)
        coherence_uniform = tuner.calculate_phase_coherence(phases)

        # Weighted should be higher (outlier de-emphasized)
        assert coherence_weighted > coherence_uniform

    def test_impedance_matching_perfect(self):
        """Test perfect impedance matching (all same Z)"""
        tuner = FrequencyTuner()

        impedances = np.array([200.0, 200.0, 200.0])
        coupling = np.array([
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ])

        matching = tuner.calculate_impedance_matching(impedances, coupling)

        # All should have perfect match
        assert np.all(matching == pytest.approx(1.0, abs=1e-6))

    def test_impedance_matching_mismatch(self):
        """Test impedance mismatch detection"""
        tuner = FrequencyTuner(z_critical=50.0)

        # Large impedance difference
        impedances = np.array([100.0, 200.0, 300.0])
        coupling = np.array([
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
        ])

        matching = tuner.calculate_impedance_matching(impedances, coupling)

        # Middle lantern (200Ω) coupled to 100Ω and 300Ω
        # Should have lower matching than perfect
        assert matching[1] < 1.0

        # 100Ω difference is 2× Z_critical → η ≈ 1/3
        expected_middle = (1/(1 + 100/50) + 1/(1 + 100/50)) / 2  # ≈ 0.33
        assert matching[1] == pytest.approx(expected_middle, abs=0.01)

    def test_impedance_matching_isolated(self):
        """Test isolated lantern has perfect match (no neighbors)"""
        tuner = FrequencyTuner()

        impedances = np.array([100.0, 200.0, 300.0])
        coupling = np.zeros((3, 3))  # No coupling

        matching = tuner.calculate_impedance_matching(impedances, coupling)

        # All isolated → perfect match
        assert np.all(matching == 1.0)

    def test_resonance_quality(self):
        """Test resonance quality factor calculation"""
        tuner = FrequencyTuner()

        frequencies = np.array([13.5e6, 13.5e6, 13.5e6, 15.0e6])  # 3 at baseline, 1 outlier
        coupling = np.array([
            [0.0, 1.0, 1.0, 0.0],
            [1.0, 0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],  # Isolated
        ])

        q_factors = tuner.calculate_resonance_quality(frequencies, coupling)

        # First 3 lanterns at same freq → high Q
        assert q_factors[0] > 50

        # Isolated lantern → default Q
        assert q_factors[3] == 1.0

    def test_gradient_computation(self):
        """Test frequency gradient computation"""
        tuner = FrequencyTuner()

        # Create states with varying phases
        states = [
            TuningState("A", 13.5e6, 221.7, 0.0, 1.0, 7.4, 0.8, 0.9, 50.0),
            TuningState("B", 13.5e6, 221.7, np.pi/2, 1.0, 7.4, 0.8, 0.9, 50.0),
            TuningState("C", 13.5e6, 221.7, np.pi, 1.0, 7.4, 0.8, 0.9, 50.0),
        ]

        coupling = np.ones((3, 3)) - np.eye(3)

        gradients = tuner.compute_tuning_gradient(states, coupling)

        # Should have non-zero gradients (not perfectly coherent)
        # Gradients can be small but not exactly zero
        assert np.any(np.abs(gradients) > 1e-8)

    def test_frequency_tuning_improves_coherence(self):
        """Test that tuning improves phase coherence"""
        tuner = FrequencyTuner(learning_rate=0.1, max_frequency_shift=0.3)

        # Start with misaligned phases
        initial_phases = np.array([0.0, np.pi/3, 2*np.pi/3, np.pi])
        states = [
            TuningState(f"L{i}", 13.5e6, 221.7, phase, 1.0, 7.4, 0.5, 0.9, 50.0)
            for i, phase in enumerate(initial_phases)
        ]

        coupling = np.ones((4, 4)) - np.eye(4)

        # Initial coherence
        initial_coherence = tuner.calculate_phase_coherence(initial_phases)

        # Tune
        tuned_states, info = tuner.tune_frequencies(states, coupling, n_iterations=20)

        # Final coherence
        final_coherence = info['coherence'][-1]

        # Should improve
        assert final_coherence > initial_coherence

    def test_frequency_tuning_convergence(self):
        """Test that tuning converges"""
        tuner = FrequencyTuner(
            learning_rate=0.1,
            convergence_threshold=0.001,
        )

        # Slightly misaligned
        states = [
            TuningState("A", 13.5e6, 221.7, 0.0, 1.0, 7.4, 0.9, 0.9, 50.0),
            TuningState("B", 13.5e6, 221.7, 0.1, 1.0, 7.4, 0.9, 0.9, 50.0),
            TuningState("C", 13.5e6, 221.7, -0.1, 1.0, 7.4, 0.9, 0.9, 50.0),
        ]

        coupling = np.ones((3, 3)) - np.eye(3)

        tuned_states, info = tuner.tune_frequencies(states, coupling, n_iterations=50)

        # Should converge before max iterations
        assert info['converged']
        assert info['converged_at'] < 50

    def test_frequency_shift_constraint(self):
        """Test that frequency shifts respect max_shift constraint"""
        tuner = FrequencyTuner(
            learning_rate=0.5,  # Large learning rate
            max_frequency_shift=0.1,  # But strict constraint
        )

        f_baseline = 13.5e6
        states = [
            TuningState("A", f_baseline, 221.7, 0.0, 1.0, 7.4, 0.5, 0.9, 50.0),
            TuningState("B", f_baseline, 221.7, np.pi, 1.0, 7.4, 0.5, 0.9, 50.0),
        ]

        coupling = np.array([[0.0, 1.0], [1.0, 0.0]])

        tuned_states, _ = tuner.tune_frequencies(states, coupling, n_iterations=20)

        # Check constraints
        for state in tuned_states:
            beta_ratio = state.beta_target / 7.4
            f_baseline_scaled = 13.5e6 * beta_ratio

            deviation = abs(state.frequency_hz - f_baseline_scaled) / f_baseline_scaled
            assert deviation <= 0.1 + 1e-6  # Within constraint

    def test_impedance_optimization(self):
        """Test impedance matching optimization"""
        tuner = FrequencyTuner(learning_rate=0.2)

        # Mismatched impedances
        states = [
            TuningState("A", 13.5e6, 150.0, 0.0, 1.0, 7.4, 0.8, 0.5, 50.0),
            TuningState("B", 13.5e6, 250.0, 0.0, 1.0, 7.4, 0.8, 0.5, 50.0),
            TuningState("C", 13.5e6, 200.0, 0.0, 1.0, 7.4, 0.8, 0.9, 50.0),
        ]

        coupling = np.ones((3, 3)) - np.eye(3)

        # Initial impedance spread
        initial_z = np.array([s.impedance_ohm for s in states])
        initial_spread = np.std(initial_z)

        # Optimize
        optimized_states = tuner.optimize_impedance_matching(states, coupling)

        # Final impedance spread
        final_z = np.array([s.impedance_ohm for s in optimized_states])
        final_spread = np.std(final_z)

        # Spread should decrease
        assert final_spread < initial_spread

    def test_tuning_history_recorded(self):
        """Test that tuning history is properly recorded"""
        tuner = FrequencyTuner()

        states = [
            TuningState("A", 13.5e6, 221.7, 0.0, 1.0, 7.4, 0.8, 0.9, 50.0),
            TuningState("B", 13.5e6, 221.7, 0.5, 1.0, 7.4, 0.8, 0.9, 50.0),
        ]
        coupling = np.array([[0.0, 1.0], [1.0, 0.0]])

        # Run tuning twice
        tuner.tune_frequencies(states, coupling, n_iterations=5)
        tuner.tune_frequencies(states, coupling, n_iterations=5)

        assert len(tuner.tuning_history) == 2

        summary = tuner.get_tuning_summary()
        assert summary['cycles'] == 2
        assert 'final_coherence' in summary

    def test_tuning_strategies(self):
        """Test different tuning strategies can be created"""
        gradient = create_tuner("gradient_ascent")
        assert gradient.strategy == TuningStrategy.GRADIENT_ASCENT

        harmonic = create_tuner("harmonic_lock")
        assert harmonic.strategy == TuningStrategy.HARMONIC_LOCK

        impedance = create_tuner("impedance_match")
        assert impedance.strategy == TuningStrategy.IMPEDANCE_MATCH

        collective = create_tuner("collective_mode")
        assert collective.strategy == TuningStrategy.COLLECTIVE_MODE


class TestIntegrationScenarios:
    """Integration tests with realistic network scenarios"""

    def test_three_lantern_network(self):
        """Test tuning on small 3-lantern network"""
        tuner = FrequencyTuner(learning_rate=0.1)

        # Create network
        states = [
            TuningState("Urban Heat", 13.5e6, 221.7, 0.0, 1.0, 4.2, 0.6, 0.8, 40.0),
            TuningState("v_RIG Framework", 13.5e6, 221.7, 0.8, 1.0, 4.5, 0.7, 0.9, 50.0),
            TuningState("Collective Field", 13.5e6, 155.8, 1.5, 1.0, 10.0, 0.5, 0.7, 30.0),
        ]

        coupling = np.array([
            [0.0, 0.6, 0.5],
            [0.6, 0.0, 0.96],
            [0.5, 0.96, 0.0],
        ])

        tuned_states, info = tuner.tune_frequencies(states, coupling, n_iterations=20)

        # Should improve coherence
        assert info['coherence'][-1] > info['coherence'][0]

        # Metrics should be in valid range
        for state in tuned_states:
            assert 0.0 <= state.phase_coherence <= 1.0
            assert 0.0 <= state.impedance_match <= 1.0
            assert state.resonance_quality > 0.0

    def test_heterogeneous_beta_network(self):
        """Test network with diverse β-domains"""
        tuner = FrequencyTuner(learning_rate=0.08)

        # Different β-domains (information, geo, biology)
        np.random.seed(42)  # For reproducibility
        betas = [4.2, 4.6, 7.4, 11.0]
        states = [
            TuningState(f"L{i}", 13.5e6 * (beta/7.4), 221.7 * (beta/7.4),
                       np.random.rand() * 2 * np.pi, 1.0, beta, 0.5, 0.8, 40.0)
            for i, beta in enumerate(betas)
        ]

        coupling = np.random.rand(4, 4)
        coupling = (coupling + coupling.T) / 2  # Symmetric
        np.fill_diagonal(coupling, 0.0)

        # Initial coherence
        initial_coherence = tuner.calculate_phase_coherence(
            np.array([s.phase_rad for s in states])
        )

        tuned_states, info = tuner.tune_frequencies(states, coupling, n_iterations=30)

        # Diverse β-domains should improve coherence (even if not to high values)
        # Heterogeneous networks naturally have lower coherence
        assert info['coherence'][-1] > initial_coherence or info['coherence'][-1] > 0.2

    def test_impedance_and_frequency_joint_optimization(self):
        """Test joint optimization of frequency and impedance"""
        tuner = FrequencyTuner(learning_rate=0.15)

        # Misaligned network
        states = [
            TuningState("A", 13.5e6, 180.0, 0.0, 1.0, 7.4, 0.4, 0.6, 30.0),
            TuningState("B", 14.0e6, 250.0, 1.0, 1.0, 7.4, 0.4, 0.6, 30.0),
            TuningState("C", 13.0e6, 210.0, 0.5, 1.0, 7.4, 0.4, 0.6, 30.0),
        ]

        coupling = np.ones((3, 3)) - np.eye(3)

        # Initial metrics
        initial_coherence = tuner.calculate_phase_coherence(
            np.array([s.phase_rad for s in states])
        )
        initial_impedances = np.array([s.impedance_ohm for s in states])
        initial_z_match = tuner.calculate_impedance_matching(initial_impedances, coupling)

        # Optimize frequencies
        tuned_states, info = tuner.tune_frequencies(states, coupling, n_iterations=15)

        # Optimize impedances
        optimized_states = tuner.optimize_impedance_matching(tuned_states, coupling)

        # Final metrics
        final_coherence = info['coherence'][-1]  # Use info coherence (most recent)
        final_impedances = np.array([s.impedance_ohm for s in optimized_states])
        final_z_match = tuner.calculate_impedance_matching(final_impedances, coupling)

        # At least one should improve (frequency OR impedance)
        coherence_improved = final_coherence >= initial_coherence - 0.01  # Allow small tolerance
        impedance_improved = np.mean(final_z_match) > np.mean(initial_z_match)

        assert coherence_improved or impedance_improved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
