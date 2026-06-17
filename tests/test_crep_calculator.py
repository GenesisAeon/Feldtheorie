"""Tests for CREP calculator (PSRM readiness)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.crep_calculator import (  # noqa: E402
    compute_crep,
)


def test_crep_bounds() -> None:
    rng = np.random.default_rng(123)
    signal = rng.normal(0.0, 1.0, 512)
    result = compute_crep(beta=1.2, sigma_phi=0.06, eeg_data=signal, fs=256.0)
    assert 0.0 <= result.aggregate <= 1.0
    assert 0.0 <= result.coherence <= 1.0


def test_crep_multichannel_coherence() -> None:
    rng = np.random.default_rng(99)
    channel_a = rng.normal(0.0, 1.0, 256)
    channel_b = channel_a + rng.normal(0.0, 0.01, 256)
    signal = np.vstack([channel_a, channel_b])
    result = compute_crep(beta=2.4, sigma_phi=0.08, eeg_data=signal, fs=256.0)
    assert result.coherence >= 0.8
