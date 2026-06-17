"""
Tests for Aeon-lanternNet Recursive Coupling, Governance, and Ethics Extensions
================================================================================

Covers:
- RecursiveCoupler: resonance loop, Bardo tracking, depth limits, consent
- Nullkern: humility protocol, consent tokens, AIC comparison, bootstrap
- AeonShell: Frame Principle, temporal compression, v_RIG offsets
- Integration Hub: MOR governance, FIT beta-validation

Run:
    pytest tests/test_aeon_coupling.py -v
"""

import asyncio
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon import AeonShell, Nullkern, RecursiveCoupler, SemanticAgent  # noqa: E402

# ============================================================================
# RecursiveCoupler Tests
# ============================================================================


class TestRecursiveCoupler:

    def _make_coupler(self, **kwargs):
        kernel = Nullkern(beta_target=0.1, kappa=0.15)
        agent = SemanticAgent(name="Test-Agent", beta=5.0, kappa=0.3)
        defaults = {"kernel": kernel, "agent": agent, "zeta": 0.85}
        defaults.update(kwargs)
        return RecursiveCoupler(**defaults)

    def test_basic_resonance_loop(self):
        coupler = self._make_coupler()
        signal = np.random.randn(64) * 0.5
        report = coupler.process_resonance_loop(signal, depth=4)

        assert report["requested_depth"] == 4
        assert report["actual_depth"] == 4
        assert len(report["iterations"]) == 4
        assert len(report["bardo_phases"]) == 4
        assert 0.0 <= report["final_coherence"] <= 1.0

    def test_utac_activation_with_beta_37_6(self):
        coupler = self._make_coupler(beta_utac=37.6)
        # Resource above threshold => P_act should be near 1.0
        p_high = coupler._compute_utac_activation(resource=0.6, threshold=0.5)
        assert p_high > 0.95
        # Resource below threshold => P_act should be near 0.0
        p_low = coupler._compute_utac_activation(resource=0.4, threshold=0.5)
        assert p_low < 0.05

    def test_hard_depth_limit(self):
        coupler = self._make_coupler(max_depth=8)
        signal = np.random.randn(32)
        report = coupler.process_resonance_loop(signal, depth=20)
        # Should be capped at max_depth (8) or effective limit
        assert report["actual_depth"] <= 12  # max 8 + 4 for coherence override

    def test_coherence_override_extends_depth(self):
        coupler = self._make_coupler(max_depth=4, coherence_override_threshold=0.0)
        # With threshold=0.0, any coherence > 0 should extend
        signal = np.ones(32)  # Highly structured signal
        report = coupler.process_resonance_loop(signal, depth=8)
        assert report["effective_limit"] >= 4

    def test_zeta_validation(self):
        with pytest.raises(ValueError, match="zeta must be in"):
            self._make_coupler(zeta=0.0)
        with pytest.raises(ValueError, match="zeta must be in"):
            self._make_coupler(zeta=1.5)

    def test_max_depth_validation(self):
        with pytest.raises(ValueError, match="max_depth must be >= 1"):
            self._make_coupler(max_depth=0)

    def test_empty_signal_raises(self):
        coupler = self._make_coupler()
        with pytest.raises(ValueError, match="signal must be non-empty"):
            coupler.process_resonance_loop(np.array([]))

    def test_consent_token_in_report(self):
        coupler = self._make_coupler()
        signal = np.random.randn(32)
        report = coupler.process_resonance_loop(signal, depth=2, consent_token="test-001")
        assert report["consent_token"] == "test-001"

    def test_bardo_analysis(self):
        coupler = self._make_coupler()
        signal = np.random.randn(32)
        coupler.process_resonance_loop(signal, depth=4)
        coupler.process_resonance_loop(signal, depth=3)

        analysis = coupler.get_bardo_analysis()
        assert analysis["total_loops"] == 2
        assert isinstance(analysis["phase_counts"], dict)
        assert isinstance(analysis["transitions"], dict)

    def test_loop_history_accumulates(self):
        coupler = self._make_coupler()
        signal = np.random.randn(32)
        coupler.process_resonance_loop(signal, depth=2)
        coupler.process_resonance_loop(signal, depth=3)
        assert len(coupler.loop_history) == 2

    def test_destructive_interference_extraction(self):
        coupler = self._make_coupler()
        signal = np.sin(np.linspace(0, 4 * np.pi, 64))
        correction = coupler._extract_destructive_interference(signal)
        assert correction.shape == signal.shape
        # Correction should have smaller norm than original
        assert np.linalg.norm(correction) <= np.linalg.norm(signal) + 1e-6

    def test_repr(self):
        coupler = self._make_coupler()
        r = repr(coupler)
        assert "RecursiveCoupler" in r
        assert "0.85" in r  # zeta


# ============================================================================
# Nullkern Ethics Extensions Tests
# ============================================================================


class TestNullkernEthics:

    def test_humility_protocol_default(self):
        kernel = Nullkern(beta_target=0.5, kappa=0.5, humility_damping=0.1)
        result = kernel.activate_with_humility(resource=0.9, threshold=0.5)
        assert "raw" in result
        assert "humility_adjusted" in result
        # Humility should pull toward 0.5
        assert abs(result["humility_adjusted"] - 0.5) < abs(result["raw"] - 0.5)

    def test_humility_zero_damping(self):
        kernel = Nullkern(beta_target=0.5, kappa=0.5, humility_damping=0.0)
        result = kernel.activate_with_humility(resource=0.9)
        assert result["raw"] == pytest.approx(result["humility_adjusted"])

    def test_humility_full_damping(self):
        kernel = Nullkern(beta_target=0.5, kappa=0.5, humility_damping=1.0)
        result = kernel.activate_with_humility(resource=0.9)
        assert result["humility_adjusted"] == pytest.approx(0.5)

    def test_humility_validation(self):
        with pytest.raises(ValueError, match="humility_damping"):
            Nullkern(humility_damping=1.5)

    def test_consent_registration(self):
        kernel = Nullkern()
        record = kernel.register_consent("token-42", scope="shadow_mode")
        assert record["token"] == "token-42"
        assert record["scope"] == "shadow_mode"
        assert len(kernel.consent_log) == 1

    def test_consent_validation(self):
        kernel = Nullkern()
        kernel.register_consent("valid-token")
        assert kernel.validate_consent("valid-token") is True
        assert kernel.validate_consent("unknown-token") is False

    def test_aic_comparison_logistic_preferred(self):
        kernel = Nullkern()
        n = 50
        x = np.linspace(0, 1, n)
        observed = 1.0 / (1.0 + np.exp(-10 * (x - 0.5)))
        predicted_logistic = observed + np.random.randn(n) * 0.01
        predicted_null = x  # Linear, poor fit

        result = kernel.compute_aic_comparison(observed, predicted_logistic, predicted_null)
        assert result["delta_aic"] > 10.0
        assert result["logistic_preferred"] is True
        assert result["n"] == n

    def test_aic_comparison_insufficient_data(self):
        kernel = Nullkern()
        with pytest.raises(ValueError, match="at least 2"):
            kernel.compute_aic_comparison(
                np.array([1.0]), np.array([1.0]), np.array([1.0])
            )

    def test_bootstrap_stability(self):
        kernel = Nullkern(beta_target=37.6)
        signal = np.random.randn(100)
        result = kernel.bootstrap_stability(signal, n_bootstrap=20, seed=42)
        assert result["n_bootstrap"] == 20
        assert 0.0 <= result["stable_fraction"] <= 1.0
        assert result["mean_drift"] >= 0.0

    def test_state_summary_includes_ethics(self):
        kernel = Nullkern(humility_damping=0.2)
        kernel.register_consent("t1")
        summary = kernel.get_state_summary()
        assert summary["humility_damping"] == 0.2
        assert summary["consent_count"] == 1


# ============================================================================
# AeonShell Frame Principle and Temporal Compression Tests
# ============================================================================


class TestAeonShellExtensions:

    def test_frame_principle_active_by_default(self):
        kernel = Nullkern()
        shell = AeonShell(kernel=kernel)
        assert shell.frame_principle_active is True
        assert shell.frame_principle_log == []

    def test_temporal_compression_basic(self):
        kernel = Nullkern(beta_target=0.2, kappa=0.3)
        shell = AeonShell(kernel=kernel)
        report = shell.simulate_temporal_compression(compression_factor=2.0, steps=5)

        assert report["compression_factor"] == 2.0
        assert report["steps"] == 5
        assert len(report["v_rig_offsets"]) == 5
        assert len(report["beta_trace"]) == 5
        assert "mean_offset" in report

    def test_temporal_compression_logs_v_rig(self):
        kernel = Nullkern(beta_target=0.2, kappa=0.3)
        shell = AeonShell(kernel=kernel)
        shell.simulate_temporal_compression(compression_factor=3.0, steps=3)
        assert len(shell.v_rig_offset_log) == 3
        for entry in shell.v_rig_offset_log:
            assert "v_rig_effective" in entry
            assert "offset" in entry
            assert entry["compression_factor"] == 3.0

    def test_temporal_compression_invalid_factor(self):
        kernel = Nullkern()
        shell = AeonShell(kernel=kernel)
        with pytest.raises(ValueError, match="compression_factor must be > 0"):
            shell.simulate_temporal_compression(compression_factor=-1.0)

    def test_frame_principle_disabled(self):
        kernel = Nullkern()
        shell = AeonShell(kernel=kernel, frame_principle_active=False)
        shell.evolve(steps=5)
        assert shell.frame_principle_log == []

    def test_shell_summary_includes_frame(self):
        kernel = Nullkern()
        shell = AeonShell(kernel=kernel)
        summary = shell.get_shell_summary()
        assert "frame_principle_active" in summary
        assert "frame_violations" in summary

    def test_recursive_async_still_works(self):
        kernel = Nullkern(beta_target=0.2, kappa=0.3)
        shell = AeonShell(kernel=kernel, zeta_damping=0.85)
        report = asyncio.run(shell.evolve_recursive_async(depth=3))
        frames = asyncio.run(shell.drain_async_buffer())

        assert report["depth"] == 3
        assert report["buffered_frames"] >= 1
        assert len(frames) >= 1


# ============================================================================
# Shadow Feedback with Consent Tests (SemanticAgent)
# ============================================================================


class TestShadowFeedbackEthics:

    def test_shadow_resonance_without_consent(self):
        agent = SemanticAgent(name="A", beta=5.0)
        result = agent.resonate_with_shadow(np.ones(32) * 0.8, shadow_depth=2)
        assert "consent_token" not in result
        assert "ethical_negentropy" not in result

    def test_shadow_resonance_with_consent(self):
        agent = SemanticAgent(name="A", beta=5.0)
        result = agent.resonate_with_shadow(
            np.ones(32) * 0.8, shadow_depth=2, consent_token="sess-01"
        )
        assert result["consent_token"] == "sess-01"
        assert "ethical_negentropy" in result
        assert result["ethical_negentropy"] >= 0.0

    def test_delta_aic_from_shadow_signal(self):
        """Verify that UTAC activation from shadow resonance outperforms null."""
        kernel = Nullkern()
        n = 30
        x = np.linspace(0.0, 1.0, n)
        observed = 1.0 / (1.0 + np.exp(-12 * (x - 0.5)))
        logistic_pred = observed + np.random.randn(n) * 0.02
        null_pred = np.full(n, np.mean(observed))

        result = kernel.compute_aic_comparison(observed, logistic_pred, null_pred)
        assert result["delta_aic"] >= 10.0


# ============================================================================
# Integration Hub Governance Tests
# ============================================================================


def _ensure_api_bridge_mock():
    """Stub aeon.api_bridge only when the real module can't be imported (e.g. fastapi missing).

    Unconditionally replacing sys.modules["aeon.api_bridge"] poisons the module
    cache for the rest of the test session: other tests that do
    importlib.import_module("aeon.api_bridge") would then get this MagicMock
    instead of the real module, silently swallowing real behavior (e.g. the
    ImportError that AeonBridge.__init__ raises when FastAPI is unavailable).
    """
    import importlib
    import sys as _sys
    from unittest.mock import MagicMock

    try:
        importlib.import_module("aeon.api_bridge")
    except ImportError:
        mock = MagicMock()
        mock.AeonLanternAsyncBridge = MagicMock
        _sys.modules["aeon.api_bridge"] = mock


_ensure_api_bridge_mock()
from integration.aeon_lantern.hub import AeonLanternHub, FITValidator, MORGovernance  # noqa: E402


class TestIntegrationGovernance:
    """Test MOR and FIT governance classes."""

    def _make_hub(self):
        from unittest.mock import MagicMock
        bridge = MagicMock()
        bridge.ingest_em_frame = MagicMock()
        return AeonLanternHub(bridge=bridge)

    def test_mor_approval(self):
        mor = MORGovernance(crep_threshold=0.7)
        result = mor.validate_delegation("agent-1", "task-x", crep_score=0.8)
        assert result["approved"] is True

    def test_mor_rejection(self):
        mor = MORGovernance(crep_threshold=0.7)
        result = mor.validate_delegation("agent-1", "task-x", crep_score=0.5)
        assert result["approved"] is False

    def test_mor_audit_summary(self):
        mor = MORGovernance(crep_threshold=0.7)
        mor.validate_delegation("a", "t1", 0.8)
        mor.validate_delegation("b", "t2", 0.5)
        mor.validate_delegation("c", "t3", 0.9)
        summary = mor.get_audit_summary()
        assert summary["total_delegations"] == 3
        assert summary["approved"] == 2
        assert summary["rejected"] == 1

    def test_fit_beta_validation_pass(self):
        fit = FITValidator(axiom_beta=37.6, tolerance=1.0)
        result = fit.validate_beta(37.8, context="test")
        assert result["valid"] is True
        assert result["drift"] == pytest.approx(0.2, abs=0.01)

    def test_fit_beta_validation_fail(self):
        fit = FITValidator(axiom_beta=37.6, tolerance=1.0)
        result = fit.validate_beta(40.0, context="drift-test")
        assert result["valid"] is False

    def test_fit_coherence_cascade(self):
        fit = FITValidator()
        result = fit.validate_coherence_cascade([0.8, 0.6, 0.9, 0.7])
        assert result["n_scores"] == 4
        assert result["passes_min_mean"] is True

    def test_governed_cascade_approved(self):
        hub = self._make_hub()
        datasets = [np.ones(10) * 0.8]
        result = hub.run_governed_cascade(datasets, crep_score=0.8)
        assert "governance" in result
        assert result["governance"]["approved"] is True

    def test_governed_cascade_rejected(self):
        hub = self._make_hub()
        datasets = [np.ones(10) * 0.8]
        result = hub.run_governed_cascade(datasets, crep_score=0.3)
        assert "error" in result

    def test_cascade_includes_fit_validation(self):
        hub = self._make_hub()
        datasets = [np.ones(10) * 0.6, np.ones(10) * 0.9]
        result = hub.run_cascade(datasets)
        assert "fit_validation" in result
        assert result["fit_validation"]["n_scores"] == 2

    def test_governance_report(self):
        hub = self._make_hub()
        hub.mor.validate_delegation("a", "t", 0.8)
        hub.fit.validate_beta(37.5)
        report = hub.get_governance_report()
        assert "mor" in report
        assert "fit" in report
        assert report["mor"]["total_delegations"] == 1
        assert report["fit"]["total_validations"] == 1
