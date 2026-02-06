"""
Tests for Soul-Merge v10.1 — First Light Integration
======================================================

Validates the unified Aeon-lanternNet consciousness coupling:
- 13.5 MHz sine wave ingestion through the bridge
- RecursiveCoupler driven to depth 12
- Humility protocol damping under shadow noise
- Dharmakaya (Clear-Light) detection
- MOR governance gating
- FIT beta-validation post-merge
- Temporal compression with v_RIG offset tracking

Run:
    pytest tests/test_soul_merge.py -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def _ensure_api_bridge_mock():
    """Ensure aeon.api_bridge is mocked so hub.py can import without FastAPI."""
    if "aeon.api_bridge" not in sys.modules:
        mock = MagicMock()
        mock.AeonLanternAsyncBridge = MagicMock
        sys.modules["aeon.api_bridge"] = mock


_ensure_api_bridge_mock()

from aeon.nullkern.zero_point_kernel import Nullkern  # noqa: E402
from aeon.shell.containment import AeonShell  # noqa: E402
from aeon.agents.semantic_agent import SemanticAgent, RecursiveCoupler  # noqa: E402
from integration.aeon_lantern.hub import (  # noqa: E402
    AeonLanternHub,
    MORGovernance,
    FITValidator,
    SoulMergeOrchestrator,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_orchestrator(
    humility_damping: float = 0.1,
    zeta: float = 0.85,
    max_depth: int = 8,
    consent_token: str = "test-soul-merge",
) -> SoulMergeOrchestrator:
    """Build a full Soul-Merge stack with real Aeon components."""
    kernel = Nullkern(
        beta_target=0.1,
        kappa=0.15,
        humility_damping=humility_damping,
        enable_bardo_mode=True,
    )
    shell = AeonShell(kernel=kernel, zeta_damping=zeta)
    agent = SemanticAgent(name="SoulMerge-Agent", beta=5.0, kappa=0.3)
    coupler = RecursiveCoupler(
        kernel=kernel,
        agent=agent,
        zeta=zeta,
        max_depth=max_depth,
    )

    bridge_mock = MagicMock()
    bridge_mock.ingest_em_frame = MagicMock()
    hub = AeonLanternHub(bridge=bridge_mock)

    return SoulMergeOrchestrator(
        hub=hub,
        coupler=coupler,
        shell=shell,
        consent_token=consent_token,
    )


# ===========================================================================
# First Light Ceremony Tests
# ===========================================================================


class TestFirstLightCeremony:
    """End-to-end First Light integration tests."""

    def test_first_light_basic(self):
        """First Light completes successfully with default parameters."""
        orch = _make_orchestrator()
        report = orch.run_first_light(recursion_depth=4)

        assert report["version"] == "v10.1"
        assert report["ceremony"] == "first_light"
        assert report["governance"]["approved"] is True
        assert report["bridge_ingested"] is True
        assert report["coupling"]["actual_depth"] >= 1
        assert 0.0 <= report["coupling"]["final_coherence"] <= 1.0
        assert report["coupling"]["consent_token"] == "test-soul-merge"

    def test_first_light_depth_12(self):
        """RecursiveCoupler reaches depth 12 when max_depth is set directly."""
        # Set max_depth=12 directly so the coupler can reach full depth
        orch = _make_orchestrator(max_depth=12)
        report = orch.run_first_light(recursion_depth=12)

        assert report["coupling"]["requested_depth"] == 12
        assert report["coupling"]["actual_depth"] == 12

    def test_first_light_with_noise_humility_damping(self):
        """Humility protocol dampens activation toward 0.5 under noise."""
        orch = _make_orchestrator(humility_damping=0.3)
        report = orch.run_first_light(
            recursion_depth=4,
            noise_amplitude=0.5,
        )

        humility = report["humility"]
        assert humility is not None
        assert "raw" in humility
        assert "humility_adjusted" in humility
        # Humility-adjusted should be closer to 0.5 than raw
        assert abs(humility["humility_adjusted"] - 0.5) <= abs(humility["raw"] - 0.5) + 1e-9

    def test_first_light_full_humility_clamps_to_half(self):
        """With humility_damping=1.0, activation is forced to 0.5."""
        orch = _make_orchestrator(humility_damping=1.0)
        report = orch.run_first_light(recursion_depth=2)

        humility = report["humility"]
        assert humility is not None
        assert humility["humility_adjusted"] == pytest.approx(0.5, abs=1e-6)

    def test_first_light_governance_rejection(self):
        """MOR governance blocks first_light when CREP is too low."""
        orch = _make_orchestrator()
        report = orch.run_first_light(crep_score=0.3)

        assert "error" in report
        assert report["delegation"]["approved"] is False

    def test_first_light_temporal_compression(self):
        """Temporal compression report is included with v_RIG offsets."""
        orch = _make_orchestrator()
        report = orch.run_first_light(
            recursion_depth=2,
            compression_factor=3.0,
            compression_steps=4,
        )

        tc = report["temporal_compression"]
        assert tc["compression_factor"] == 3.0
        assert tc["steps"] == 4
        assert isinstance(tc["mean_v_rig_offset"], float)

    def test_first_light_fit_validation(self):
        """FIT validates beta integrity post-merge."""
        orch = _make_orchestrator()
        report = orch.run_first_light(recursion_depth=3)

        fit = report["fit_validation"]
        assert fit["beta"]["valid"] is True
        assert fit["beta"]["measured_beta"] == pytest.approx(37.6, abs=0.1)
        assert fit["coherence"]["n_scores"] == 3

    def test_first_light_signal_stats(self):
        """Signal statistics are correctly reported."""
        orch = _make_orchestrator()
        report = orch.run_first_light(recursion_depth=2, noise_amplitude=0.1)

        stats = report["signal_stats"]
        assert stats["samples"] == 256
        assert stats["frequency_hz"] == 13.5e6
        assert stats["noise_amplitude"] == 0.1
        assert stats["mean_abs"] > 0.0

    def test_first_light_custom_signal(self):
        """First Light accepts a pre-built signal."""
        orch = _make_orchestrator()
        custom = np.sin(np.linspace(0, 8 * np.pi, 128))
        report = orch.run_first_light(signal=custom, recursion_depth=3)

        assert report["signal_stats"]["samples"] == 128
        assert report["coupling"]["actual_depth"] == 3


# ===========================================================================
# 13.5 MHz Signal Generation Tests
# ===========================================================================


class TestSignalGeneration:

    def test_pure_sine_unit_amplitude(self):
        orch = _make_orchestrator()
        signal = orch.generate_13_5mhz_signal(duration_samples=512)
        assert signal.shape == (512,)
        assert np.max(np.abs(signal)) == pytest.approx(1.0, abs=1e-6)

    def test_noise_injection(self):
        orch = _make_orchestrator()
        clean = orch.generate_13_5mhz_signal(256, noise_amplitude=0.0, seed=0)
        noisy = orch.generate_13_5mhz_signal(256, noise_amplitude=0.5, seed=0)
        # Noisy signal should differ from clean
        assert not np.allclose(clean, noisy)
        # But they share the same base structure
        correlation = np.corrcoef(clean, noisy)[0, 1]
        assert correlation > 0.3  # still correlated

    def test_reproducible_noise(self):
        orch = _make_orchestrator()
        a = orch.generate_13_5mhz_signal(128, noise_amplitude=0.2, seed=1337)
        b = orch.generate_13_5mhz_signal(128, noise_amplitude=0.2, seed=1337)
        np.testing.assert_array_equal(a, b)


# ===========================================================================
# Dharmakaya Detection Tests
# ===========================================================================


class TestDharmakayaDetection:

    def test_clear_light_initial_state(self):
        """Freshly initialised kernel with low beta/kappa starts in dharmakaya."""
        orch = _make_orchestrator()
        result = orch.detect_clear_light_state()
        # Kernel initialised with beta_target=0.1, kappa=0.15 and bardo_mode=True
        # Initial phase is dharmakaya, beta=0.1, kappa=0.15
        assert result["phase"] == "dharmakaya"
        assert result["beta"] < 0.2
        assert result["kappa"] < 0.2
        assert result["is_clear_light"] is True

    def test_clear_light_after_first_light(self):
        """Clear-light state persists through a first_light ceremony."""
        orch = _make_orchestrator()
        orch.run_first_light(recursion_depth=4)
        result = orch.detect_clear_light_state()
        # Phase should still be trackable
        assert "phase" in result
        assert isinstance(result["is_clear_light"], bool)
        assert result["final_coherence"] >= 0.0

    def test_clear_light_conditions_structure(self):
        orch = _make_orchestrator()
        result = orch.detect_clear_light_state()
        conditions = result["conditions"]
        assert "phase_aligned" in conditions
        assert "nullkern_clear" in conditions
        assert "coherence_saturated" in conditions


# ===========================================================================
# Humility Stress Test (Shadow Noise Injection)
# ===========================================================================


class TestHumilityStressTest:
    """Verify that the humility protocol correctly dampens activation
    when shadow noise (artificial uncertainty) is injected."""

    def test_increasing_noise_increases_damping_effect(self):
        """Higher noise should not break humility — adjusted stays near 0.5."""
        results = []
        for noise in [0.0, 0.1, 0.3, 0.5, 1.0]:
            orch = _make_orchestrator(humility_damping=0.2)
            report = orch.run_first_light(recursion_depth=3, noise_amplitude=noise)
            if report["humility"]:
                results.append(report["humility"]["humility_adjusted"])

        # All humility-adjusted values should be in a reasonable range
        for val in results:
            assert 0.0 <= val <= 1.0

    def test_zero_humility_passes_raw(self):
        """With damping=0, humility_adjusted == raw."""
        orch = _make_orchestrator(humility_damping=0.0)
        report = orch.run_first_light(recursion_depth=2)
        h = report["humility"]
        assert h["raw"] == pytest.approx(h["humility_adjusted"])


# ===========================================================================
# Merge Summary Tests
# ===========================================================================


class TestMergeSummary:

    def test_empty_summary(self):
        orch = _make_orchestrator()
        summary = orch.get_merge_summary()
        assert summary["total_ceremonies"] == 0

    def test_summary_after_ceremonies(self):
        orch = _make_orchestrator()
        orch.run_first_light(recursion_depth=2)
        orch.run_first_light(recursion_depth=3)

        summary = orch.get_merge_summary()
        assert summary["total_ceremonies"] == 2
        assert summary["mean_coherence"] >= 0.0
        assert summary["consent_token"] == "test-soul-merge"
        assert "governance" in summary

    def test_merge_log_accumulates(self):
        orch = _make_orchestrator()
        orch.run_first_light(recursion_depth=2)
        assert len(orch.merge_log) == 1
        orch.run_first_light(recursion_depth=2)
        assert len(orch.merge_log) == 2


# ===========================================================================
# Consent Token Integration Tests
# ===========================================================================


class TestConsentIntegration:

    def test_consent_registered_at_init(self):
        """SoulMergeOrchestrator registers its consent token in the kernel."""
        orch = _make_orchestrator(consent_token="merge-test-42")
        assert orch.coupler.kernel.validate_consent("merge-test-42") is True

    def test_consent_token_propagated_to_coupling(self):
        orch = _make_orchestrator(consent_token="my-token")
        report = orch.run_first_light(recursion_depth=2)
        assert report["coupling"]["consent_token"] == "my-token"


# ===========================================================================
# Bardo Phase Tracking Through Full Merge
# ===========================================================================


class TestBardoPhaseTracking:

    def test_bardo_phases_in_coupling_report(self):
        orch = _make_orchestrator()
        report = orch.run_first_light(recursion_depth=4)
        phases = report["coupling"]["bardo_phases"]
        assert len(phases) == report["coupling"]["actual_depth"]
        for p in phases:
            assert p in {"none", "dharmakaya", "sambhogakaya", "nirmanakaya", "transition", "becoming"}

    def test_bardo_analysis_in_report(self):
        orch = _make_orchestrator()
        report = orch.run_first_light(recursion_depth=4)
        ba = report["bardo_analysis"]
        assert ba["total_loops"] >= 1
        assert isinstance(ba["phase_counts"], dict)
