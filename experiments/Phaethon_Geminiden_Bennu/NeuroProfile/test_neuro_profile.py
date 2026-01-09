"""Minimal unit tests for NeuroProfile release readiness."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

import numpy as np


CODE_DIR = Path(__file__).resolve().parent / "code"
sys.path.insert(0, str(CODE_DIR))

from neuro_profile_model import NeuroProfileModel  # noqa: E402


class TestNeuroProfileModel(unittest.TestCase):
    def setUp(self) -> None:
        self.model = NeuroProfileModel()
        rng = np.random.default_rng(7)
        self.series = rng.normal(0.0, 1.0, 512)

    def test_requires_consent(self) -> None:
        with self.assertRaises(PermissionError):
            self.model.analyze(self.series, consent_granted=False)

    def test_analyze_outputs(self) -> None:
        result = self.model.analyze(self.series, consent_granted=True, subject_id="demo")
        self.assertTrue(0.0 <= result.sigma_phi_proxy <= 1.0)
        self.assertIsNotNone(result.beta_estimate)
        self.assertTrue(result.consent.granted)
        self.assertIsNotNone(result.consent.anonymized_subject)


if __name__ == "__main__":
    unittest.main()
