"""Tests for the Aeon FastAPI bridge."""

import importlib

import numpy as np
import pytest


def test_aeon_bridge_requires_fastapi(monkeypatch):
    """AeonBridge should refuse to initialize when FastAPI is unavailable."""

    api_bridge = importlib.import_module("aeon.api_bridge")

    # Force the FastAPI availability flag off to simulate missing dependency
    monkeypatch.setattr(api_bridge, "FASTAPI_AVAILABLE", False)

    with pytest.raises(ImportError, match="FastAPI not available"):
        api_bridge.AeonBridge(shell=object())


@pytest.mark.skipif(
    not importlib.util.find_spec("fastapi"),
    reason="fastapi not installed",
)
def test_aeon_lantern_async_bridge_telemetry_snapshot():
    api_bridge = importlib.import_module("aeon.api_bridge")

    class _Shell:
        def get_shell_summary(self):
            return {
                "kernel_state": {
                    "beta": 0.4,
                    "kappa": 0.3,
                    "resonance": 0.8,
                    "phase": "none",
                    "information_density": 0.6,
                    "v_rig_effective": 12.0,
                },
                "num_agents": 0,
                "trajectory_length": 0,
                "safeguards_active": True,
                "violations": 0,
                "age_seconds": 1.0,
                "collective_metrics": {},
                "auto_exit_triggered": False,
            }

    bridge = api_bridge.AeonLanternAsyncBridge(shell=_Shell(), frame_capacity=8)
    bridge.ingest_em_frame(np.array([0.8, 0.9, 0.85]))
    telemetry = bridge.get_emergence_telemetry()
    bridge.close()

    assert telemetry["system_impedance"] == pytest.approx(221.7)
    assert telemetry["metastability_offset"] == pytest.approx(0.0625)
    assert telemetry["frame_counter"] >= 1
    assert telemetry["kappa_metric"] == pytest.approx(0.3)
    assert 0.0 <= telemetry["sigma_metric"] <= 1.0
    assert telemetry["aleph_metric"] == pytest.approx(0.6)
