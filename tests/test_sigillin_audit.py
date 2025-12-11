import math

import pytest
from scripts.sigillin_audit import ALETHEIA_ALERT, V_RIG_IDEAL, audit_integrity


def test_audit_integrity_passes_with_stable_parameters():
    report = audit_integrity(seed=7, mock_entropy=0.42, mock_velocity=V_RIG_IDEAL)

    assert report.passed
    assert report.entropy_ok
    assert report.velocity_ok
    assert ALETHEIA_ALERT not in "\n".join(report.alerts)


@pytest.mark.parametrize(
    "entropy_value, velocity_value",
    [
        (0.0, V_RIG_IDEAL * 1.05),
        (0.0, V_RIG_IDEAL * 0.9),
    ],
)
def test_audit_integrity_triggers_alert_on_failures(entropy_value, velocity_value):
    report = audit_integrity(
        seed=3,
        overrides={"photon_coupling": 0.05, "expansion_rate": 1.05},
        mock_entropy=entropy_value,
        mock_velocity=velocity_value,
    )

    assert not report.passed
    assert not report.entropy_ok
    assert not report.velocity_ok
    assert any(alert.startswith("CRITICAL_WARNING") for alert in report.alerts)
    assert ALETHEIA_ALERT in report.alerts
    assert math.isclose(report.simulated_v_rig, velocity_value, rel_tol=1e-12)
