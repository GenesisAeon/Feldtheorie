"""Minimal unit tests for NeuroProfile release readiness."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.neuro_profile_model import (  # noqa: E402
    NeuroProfileModel,
)


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
        self.assertTrue(0.0 <= result.crep.aggregate <= 1.0)
        self.assertEqual(result.ethics_report.action, "proceed")
        self.assertIsNotNone(result.resonant_return)
        self.assertTrue(0.0 <= result.resonant_return.v_rig_alignment <= 1.0)
        self.assertGreaterEqual(len(result.null_model_bootstrap), 1)


if __name__ == "__main__":
    unittest.main()
