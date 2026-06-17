from __future__ import annotations

import pytest
from analysis.afet_safety_monitor import AFETSafetyMonitor, SafetyDecision


def test_monitor_raises_below_critical_threshold() -> None:
    monitor = AFETSafetyMonitor(sigma_phi_threshold=0.0625, critical_threshold=0.055)

    with pytest.raises(RuntimeError, match="critical"):
        monitor.monitor_step({"sigma_phi": 0.0549})


def test_monitor_warns_between_thresholds() -> None:
    monitor = AFETSafetyMonitor(sigma_phi_threshold=0.0625, critical_threshold=0.055)

    decision = monitor.monitor_step({"sigma_phi": 0.06})

    assert isinstance(decision, SafetyDecision)
    assert decision.state == "warning"
    assert decision.should_shutdown is False


def test_aeon_training_hook_works_with_shell_summary() -> None:
    monitor = AFETSafetyMonitor()

    class DummyShell:
        def get_shell_summary(self):
            return {"collective_metrics": {"sigma_phi": 0.07}}

    decision = monitor.monitor_aeon_shell(DummyShell())
    assert decision.state == "stable"
