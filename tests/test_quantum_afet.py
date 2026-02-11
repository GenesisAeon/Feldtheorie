"""Tests for theory.quantum_afet and experiments.week2.quantum_decoherence."""

from __future__ import annotations

import math

import numpy as np
import pytest

from theory.quantum_afet import HBAR, K_BOLTZMANN, QuantumAFET, QuantumAFETResult


# ===========================================================================
# QuantumAFET — sigma_phi_quantum
# ===========================================================================


class TestSigmaPhiQuantum:
    def test_positive_result(self) -> None:
        q = QuantumAFET()
        result = q.sigma_phi_quantum(300.0, 1e-9)
        assert result > 0.0

    def test_higher_temp_lower_sigma(self) -> None:
        """Higher T → larger kT denominator → lower sigma_phi_q."""
        q = QuantumAFET()
        s_low = q.sigma_phi_quantum(100.0, 1e-9)
        s_high = q.sigma_phi_quantum(500.0, 1e-9)
        assert s_low > s_high

    def test_shorter_tau_higher_sigma(self) -> None:
        """Shorter decoherence time → higher sigma_phi_q."""
        q = QuantumAFET()
        s_short = q.sigma_phi_quantum(300.0, 1e-12)
        s_long = q.sigma_phi_quantum(300.0, 1e-6)
        assert s_short > s_long

    def test_formula_matches_manual(self) -> None:
        q = QuantumAFET()
        T, tau = 300.0, 1e-9
        expected = (HBAR / (K_BOLTZMANN * T)) / tau
        assert q.sigma_phi_quantum(T, tau) == pytest.approx(expected)

    def test_invalid_temperature(self) -> None:
        q = QuantumAFET()
        with pytest.raises(ValueError):
            q.sigma_phi_quantum(0.0, 1e-9)
        with pytest.raises(ValueError):
            q.sigma_phi_quantum(-10.0, 1e-9)

    def test_invalid_tau(self) -> None:
        q = QuantumAFET()
        with pytest.raises(ValueError):
            q.sigma_phi_quantum(300.0, 0.0)


# ===========================================================================
# QuantumAFET — decoherence_threshold
# ===========================================================================


class TestDecoherenceThreshold:
    def test_positive_result(self) -> None:
        q = QuantumAFET()
        tau_crit = q.decoherence_threshold(300.0)
        assert tau_crit > 0.0

    def test_at_threshold_sigma_equals_boundary(self) -> None:
        """At critical tau, sigma_phi_q should equal the AFET boundary."""
        q = QuantumAFET()
        T = 300.0
        tau_crit = q.decoherence_threshold(T)
        sigma = q.sigma_phi_quantum(T, tau_crit)
        assert sigma == pytest.approx(q.constants.SIGMA_PHI, rel=1e-10)

    def test_higher_temp_shorter_critical_tau(self) -> None:
        q = QuantumAFET()
        tau_300 = q.decoherence_threshold(300.0)
        tau_600 = q.decoherence_threshold(600.0)
        assert tau_600 < tau_300

    def test_invalid_temperature(self) -> None:
        q = QuantumAFET()
        with pytest.raises(ValueError):
            q.decoherence_threshold(0.0)


# ===========================================================================
# QuantumAFET — adaptive_switching
# ===========================================================================


class TestAdaptiveSwitching:
    def test_quantum_regime_when_lower(self) -> None:
        q = QuantumAFET()
        result = q.adaptive_switching(0.03, 0.06)
        assert result["regime"] == "quantum"
        assert result["use_quantum"] is True
        assert result["active_sigma_phi"] == 0.03

    def test_classical_regime_when_higher(self) -> None:
        q = QuantumAFET()
        result = q.adaptive_switching(0.10, 0.06)
        assert result["regime"] == "classical"
        assert result["use_quantum"] is False
        assert result["active_sigma_phi"] == 0.06

    def test_equal_uses_classical(self) -> None:
        q = QuantumAFET()
        result = q.adaptive_switching(0.05, 0.05)
        assert result["regime"] == "classical"

    def test_ratio_computed(self) -> None:
        q = QuantumAFET()
        result = q.adaptive_switching(0.03, 0.06)
        assert result["ratio"] == pytest.approx(0.5)


# ===========================================================================
# QuantumAFET — classical_probability
# ===========================================================================


class TestClassicalProbability:
    def test_zero_time_zero_probability(self) -> None:
        q = QuantumAFET()
        assert q.classical_probability(0.0, 1e-9) == pytest.approx(0.0)

    def test_long_time_approaches_one(self) -> None:
        q = QuantumAFET()
        p = q.classical_probability(1.0, 1e-9)
        assert p == pytest.approx(1.0, abs=1e-10)

    def test_at_tau_about_63_percent(self) -> None:
        q = QuantumAFET()
        p = q.classical_probability(1e-9, 1e-9)
        assert p == pytest.approx(1 - math.exp(-1), rel=1e-6)

    def test_negative_time_returns_zero(self) -> None:
        q = QuantumAFET()
        assert q.classical_probability(-1.0, 1e-9) == 0.0


# ===========================================================================
# QuantumAFET — critical_temperature
# ===========================================================================


class TestCriticalTemperature:
    def test_positive_result(self) -> None:
        q = QuantumAFET()
        T_crit = q.critical_temperature(2 * math.pi * 13.5e6)
        assert T_crit > 0.0

    def test_invalid_omega(self) -> None:
        q = QuantumAFET()
        with pytest.raises(ValueError):
            q.critical_temperature(0.0)


# ===========================================================================
# QuantumAFET — evaluate_quantum_system
# ===========================================================================


class TestEvaluateQuantumSystem:
    def test_returns_result(self) -> None:
        q = QuantumAFET()
        result = q.evaluate_quantum_system(300.0, 1e-9)
        assert isinstance(result, QuantumAFETResult)

    def test_with_classical_comparison(self) -> None:
        q = QuantumAFET()
        result = q.evaluate_quantum_system(300.0, 1e-9, sigma_classical=0.065)
        assert isinstance(result.is_quantum_regime, bool)


# ===========================================================================
# Quantum decoherence experiment
# ===========================================================================


class TestQuantumDecoherenceExperiment:
    def test_experiment_runs(self) -> None:
        from experiments.week2.quantum_decoherence import run_quantum_experiment

        points, report = run_quantum_experiment(force_classical=True, t_steps=5, tau_steps=5)
        assert len(points) == 25  # 5 * 5
        assert report.backend == "classical"

    def test_tau_crit_positive(self) -> None:
        from experiments.week2.quantum_decoherence import run_quantum_experiment

        _, report = run_quantum_experiment(force_classical=True, t_steps=3, tau_steps=3)
        assert report.tau_crit_at_87C > 0.0

    def test_experiment_writes_json(self, tmp_path) -> None:
        from experiments.week2.quantum_decoherence import run_quantum_decoherence_experiment

        payload = run_quantum_decoherence_experiment(
            output_dir=tmp_path,
            force_classical=True,
        )
        assert (tmp_path / "quantum_sim.json").exists()
        assert "report" in payload


# ===========================================================================
# Inheritance from AFETFramework
# ===========================================================================


class TestQuantumAFETInheritance:
    def test_inherits_predict_beta(self) -> None:
        q = QuantumAFET()
        beta = q.predict_beta(3.0)
        assert beta == pytest.approx(q.constants.BETA_CRITICAL, rel=1e-3)

    def test_inherits_check_metastability(self) -> None:
        q = QuantumAFET()
        result = q.check_metastability(10.0)
        assert "is_metastable" in result
