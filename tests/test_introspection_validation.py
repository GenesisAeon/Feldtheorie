import numpy as np
import pytest

from analysis.introspection_validation import compile_summary


def test_compile_summary_hits_expected_beta_and_probability() -> None:
    beta_values = np.linspace(3.5, 4.5, 21)
    phi_gradients = np.linspace(0.6, 1.4, 41)

    payload = compile_summary(beta_values, phi_gradients, target_probability=0.2)
    summary = payload["summary"]

    assert summary["beta_at_target"] == pytest.approx(4.2, abs=0.05)
    assert summary["phi_gradient_at_target"] == pytest.approx(1.0, abs=0.05)
    assert summary["achieved_probability"] == pytest.approx(0.2, abs=0.01)
    assert summary["logistic_advantage"] >= 0
    assert summary["temperature_advantage"] == pytest.approx(
        summary["achieved_probability"] - summary["temperature_null_probability"], abs=1e-9
    )
    assert 0.0 <= summary["temperature_null_probability"] <= 1.0
    assert not pytest.approx(summary["temperature_null_probability"]) == summary["null_model_probability"]
    assert summary["null_temperature"] == pytest.approx(2.5)
    assert "σ(β(∥∇φ∥ - Θ_detect))" in payload["tri_layer"]["formal"]

    falsification = payload["falsification"]["null_models"]
    assert "temperature_scaled" in falsification
    temp_model = falsification["temperature_scaled"]
    assert temp_model["temperature"] == pytest.approx(2.5)
    assert temp_model["probability_at_target"] == pytest.approx(summary["temperature_null_probability"])
