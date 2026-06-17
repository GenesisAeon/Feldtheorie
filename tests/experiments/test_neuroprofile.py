"""Unit tests for NeuroProfile consent, beta fitting, σΦ proxy, and ΔAIC selection."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.beta_extractor_neuro import (  # noqa: E402
    estimate_beta_from_series,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.neuro_profile_model import (  # noqa: E402
    NeuroProfileModel,
)


def _logistic(x: np.ndarray, beta: float, threshold: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-beta * (x - threshold)))


def test_requires_consent_token() -> None:
    model = NeuroProfileModel()
    rng = np.random.default_rng(10)
    series = rng.normal(0.0, 1.0, 128)
    with np.testing.assert_raises(PermissionError):
        model.analyze(series, consent_granted=True, consent_token=None)


def test_beta_estimate_accuracy() -> None:
    rng = np.random.default_rng(5)
    x = np.linspace(0.0, 1.0, 512)
    target_beta = 5.0
    threshold = 0.55
    y = _logistic(x, target_beta, threshold) + rng.normal(0.0, 0.01, x.size)
    estimate = estimate_beta_from_series(y)
    assert math.isfinite(estimate.beta)
    assert abs(estimate.beta - target_beta) < 2.0


def test_sigma_phi_proxy_range() -> None:
    model = NeuroProfileModel()
    rng = np.random.default_rng(2)
    series = rng.normal(0.0, 1.0, 256)
    sigma_phi = model.estimate_sigma_phi_proxy(series)
    assert 0.0 <= sigma_phi <= 1.0


def test_delta_aic_prefers_linear() -> None:
    model = NeuroProfileModel()
    x = np.linspace(0.0, 1.0, 256)
    series = 0.1 + 0.8 * x
    summary = model._fit_null_models(series)  # noqa: SLF001 - testing internal utility
    assert summary.best_model == "linear"
