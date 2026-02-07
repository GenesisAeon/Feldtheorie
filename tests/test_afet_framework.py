from __future__ import annotations

import pytest

from theory.afet import AFETConstants, AFETFramework


def test_predict_beta_anchor_points() -> None:
    framework = AFETFramework()
    assert framework.predict_beta(0) == pytest.approx(4.2, abs=0.2)
    assert framework.predict_beta(1) == pytest.approx(7.4, abs=0.3)
    assert framework.predict_beta(3) == pytest.approx(AFETConstants.BETA_CRITICAL, abs=0.2)


def test_metastability_threshold_behavior() -> None:
    framework = AFETFramework()
    threshold = 1.0 / AFETConstants.SIGMA_PHI

    stable = framework.check_metastability(threshold - 0.01)
    boundary = framework.check_metastability(threshold)
    unstable = framework.check_metastability(threshold + 0.01)

    assert stable["is_metastable"] is True
    assert boundary["is_metastable"] is True
    assert unstable["is_metastable"] is False


def test_integration_rate_scales_with_gradient() -> None:
    framework = AFETFramework()
    assert framework.integration_rate(0.0) == pytest.approx(0.0)
    assert framework.integration_rate(2.0) == pytest.approx(AFETConstants.V_RIG * 2.0)


def test_consciousness_emergence_criterion() -> None:
    framework = AFETFramework()

    emergent = framework.consciousness_emergence_criterion(surface_entropy=1.0, volume_entropy=0.8)
    suppressed = framework.consciousness_emergence_criterion(
        surface_entropy=0.7, volume_entropy=0.8
    )

    assert emergent["emergent"] is True
    assert suppressed["emergent"] is False


def test_beta_helpers_and_dataset_loader() -> None:
    framework = AFETFramework()
    assert framework.beta_to_peclet(AFETConstants.BETA_CRITICAL) == pytest.approx(1.0)
    assert framework.peclet_to_beta(1.0) == pytest.approx(AFETConstants.BETA_CRITICAL)
    assert framework.critical_peclet() == pytest.approx(AFETConstants.BETA_CRITICAL)
    assert framework.critical_entropy_density() == pytest.approx(16.0)

    dataset = framework.load_beta_dataset("data/derived/beta_estimates.csv")
    assert dataset
    assert {"domain", "observed_beta", "predicted_beta", "dimension"}.issubset(dataset[0].keys())


def test_load_beta_dataset_infers_dimension_from_domain(tmp_path) -> None:
    framework = AFETFramework()
    dataset_path = tmp_path / "beta.csv"
    dataset_path.write_text("domain,beta\nbiological,7.4\nllm,4.2\n", encoding="utf-8")

    rows = framework.load_beta_dataset(dataset_path)

    assert rows[0]["dimension"] == pytest.approx(1.0)
    assert rows[1]["dimension"] == pytest.approx(0.0)
