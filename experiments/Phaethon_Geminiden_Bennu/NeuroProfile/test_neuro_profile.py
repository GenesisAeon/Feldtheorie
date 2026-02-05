"""
Comprehensive unit tests for NeuroProfile release readiness.

Tests cover:
- Consent enforcement
- β-estimation accuracy
- σΦ-proxy range checking
- Correct ΔAIC selection
- Null model generation
- Bootstrap CI calculations
- CREP aggregation
- Resonance proxy
- PSRM mapper output
- Hardware profile loading
- Ethics audit logging
- BCI calibrator
- Sgr A* bridge
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys
import tempfile

import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.neuro_profile_model import (  # noqa: E402
    NeuroProfileModel,
    NeuroProfileConfig,
    NeuroProfile,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.beta_extractor_neuro import (  # noqa: E402
    estimate_beta_from_series,
    BetaEstimate,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.crep_calculator import (  # noqa: E402
    compute_crep,
    CrepResult,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.microtubule_resonance import (  # noqa: E402
    estimate_resonance_proxy,
    ResonanceProxyResult,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.resonant_return import (  # noqa: E402
    analyze_resonant_return,
    ResonantReturnConfig,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.ethics_guard import (  # noqa: E402
    EthicsGuard,
    EthicsViolation,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.bci_calibrator import (  # noqa: E402
    BCICalibrator,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.sgr_a_resonant_bridge import (  # noqa: E402
    estimate_sgr_a_bridge,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.hardware_adapter import (  # noqa: E402
    load_hardware_profiles,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.psrm_mapper import (  # noqa: E402
    PSRMMapper,
    build_psrm_map,
)


class TestNeuroProfileModel(unittest.TestCase):
    """Tests for the main NeuroProfileModel class."""

    def setUp(self) -> None:
        self.model = NeuroProfileModel()
        rng = np.random.default_rng(7)
        self.series = rng.normal(0.0, 1.0, 512)

    def test_requires_consent(self) -> None:
        """Consent must be granted with a valid token."""
        with self.assertRaises(PermissionError):
            self.model.analyze(self.series, consent_granted=False, consent_token="token")

        with self.assertRaises(PermissionError):
            self.model.analyze(self.series, consent_granted=True, consent_token=None)

    def test_analyze_outputs(self) -> None:
        """Analysis produces valid bounded outputs."""
        result = self.model.analyze(
            self.series,
            consent_granted=True,
            consent_token="demo-token",
            subject_id="demo",
        )
        self.assertTrue(0.0 <= result.sigma_phi_proxy <= 1.0)
        self.assertIsNotNone(result.beta_estimate)
        self.assertTrue(result.consent.granted)
        self.assertIsNotNone(result.consent.anonymized_subject)
        self.assertIsNotNone(result.consent.consent_token_hash)
        self.assertTrue(0.0 <= result.crep.aggregate <= 1.0)
        self.assertEqual(result.ethics_report.action, "proceed")
        self.assertIsNotNone(result.resonant_return)
        self.assertTrue(0.0 <= result.resonant_return.v_rig_alignment <= 1.0)
        self.assertGreaterEqual(len(result.null_model_bootstrap), 1)

    def test_mandala_schema_extension_hook(self) -> None:
        """Mandala schema extension file exists and is valid."""
        schema_path = (
            ROOT_DIR
            / "experiments"
            / "Phaethon_Geminiden_Bennu"
            / "NeuroProfile"
            / "schemas"
            / "psrm_sigillin_v1_mandala_extension.json"
        )
        self.assertTrue(schema_path.exists())
        payload = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertIn("mandala", payload.get("title", "").lower())

    def test_preprocessing_normalizes_data(self) -> None:
        """Preprocessing should normalize data to zero mean and unit variance."""
        prepared = self.model.preprocess(self.series)
        self.assertAlmostEqual(float(np.mean(prepared)), 0.0, places=5)
        self.assertAlmostEqual(float(np.std(prepared)), 1.0, places=5)

    def test_empty_series_handling(self) -> None:
        """Empty series should be handled gracefully."""
        prepared = self.model.preprocess([])
        self.assertEqual(prepared.size, 0)
        sigma_phi = self.model.estimate_sigma_phi_proxy(prepared)
        self.assertEqual(sigma_phi, 0.0)


class TestLanternNetLedgerLogging(unittest.TestCase):
    """Tests for LanternNet ledger logging integration."""

    def test_lanternnet_logging_writes_trilayer(self) -> None:
        """Logging should append entries and write JSON/YAML/MD files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            bootstrap_path = tmp_path / "bootstrap_ledger.json"
            crep_path = tmp_path / "crep_null_model_ledger.json"

            bootstrap_path.write_text(
                json.dumps(
                    {
                        "meta": {
                            "document": "Bootstrap Ledger – LanternNet",
                            "version": "v13.0.0",
                            "consent_protocol": "Sigillin consent gating + anonymization required",
                        },
                        "entries": [],
                    }
                ),
                encoding="utf-8",
            )
            crep_path.write_text(
                json.dumps(
                    {
                        "meta": {
                            "document": "CREP Null-Model Ledger – LanternNet",
                            "version": "v13.0.0",
                            "consent_protocol": "Sigillin consent gating + anonymization required",
                        },
                        "entries": [],
                    }
                ),
                encoding="utf-8",
            )

            config = NeuroProfileConfig(
                enable_lanternnet_logging=True,
                lanternnet_bootstrap_ledger_path=bootstrap_path,
                lanternnet_crep_ledger_path=crep_path,
            )
            model = NeuroProfileModel(config=config)
            rng = np.random.default_rng(9)
            series = rng.normal(0.0, 1.0, 256)

            result = model.analyze(
                series,
                consent_granted=True,
                consent_token="ledger-token",
                subject_id="ledger-subject",
                log_to_lanternnet=True,
                source_id="synthetic-ledger-test",
            )

            self.assertTrue(bootstrap_path.exists())
            self.assertTrue(crep_path.exists())
            self.assertTrue(bootstrap_path.with_suffix(".yaml").exists())
            self.assertTrue(bootstrap_path.with_suffix(".md").exists())
            self.assertTrue(crep_path.with_suffix(".yaml").exists())
            self.assertTrue(crep_path.with_suffix(".md").exists())

            bootstrap_payload = json.loads(bootstrap_path.read_text(encoding="utf-8"))
            crep_payload = json.loads(crep_path.read_text(encoding="utf-8"))
            self.assertEqual(len(bootstrap_payload["entries"]), 1)
            self.assertEqual(len(crep_payload["entries"]), 1)
            self.assertIn("consent_prompt", bootstrap_payload["meta"])
            self.assertIn("consent_prompt", crep_payload["meta"])
            self.assertEqual(
                bootstrap_payload["entries"][0]["consent_token_hash"],
                result.consent.consent_token_hash,
            )


class TestBetaEstimator(unittest.TestCase):
    """Tests for β-curve fitting accuracy."""

    def test_beta_estimate_bounds(self) -> None:
        """β estimate should be within reasonable bounds."""
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 1024)
        estimate = estimate_beta_from_series(series)
        self.assertIsInstance(estimate, BetaEstimate)
        self.assertGreaterEqual(estimate.beta, 0.0)
        self.assertLessEqual(estimate.beta, 20.0)
        self.assertTrue(0.0 <= estimate.threshold <= 1.0)

    def test_beta_r_value_range(self) -> None:
        """R-value (fit quality) should be between 0 and 1."""
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 1024)
        estimate = estimate_beta_from_series(series)
        self.assertTrue(-1.0 <= estimate.r_value <= 1.0)

    def test_short_series_fallback(self) -> None:
        """Series shorter than 10 samples should return zero estimates."""
        short_series = [1.0, 2.0, 3.0]
        estimate = estimate_beta_from_series(short_series)
        self.assertEqual(estimate.beta, 0.0)
        self.assertEqual(estimate.threshold, 0.0)
        self.assertEqual(estimate.r_value, 0.0)

    def test_logistic_curve_fitting(self) -> None:
        """Logistic curve should fit synthetic sigmoidal data well."""
        x = np.linspace(0, 1, 100)
        # Create sigmoidal data with known β
        true_beta = 10.0
        true_threshold = 0.5
        y = 1.0 / (1.0 + np.exp(-true_beta * (x - true_threshold)))
        y = y + np.random.default_rng(42).normal(0, 0.05, len(y))
        estimate = estimate_beta_from_series(y)
        # The estimate should capture the general trend
        self.assertGreater(estimate.beta, 1.0)


class TestSigmaPhiProxy(unittest.TestCase):
    """Tests for σΦ spectral entropy proxy."""

    def test_sigma_phi_range(self) -> None:
        """σΦ proxy should be normalized between 0 and 1."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 1024)
        prepared = model.preprocess(series)
        sigma_phi = model.estimate_sigma_phi_proxy(prepared)
        self.assertTrue(0.0 <= sigma_phi <= 1.0)

    def test_white_noise_high_entropy(self) -> None:
        """White noise should have high spectral entropy."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        white_noise = rng.normal(0.0, 1.0, 2048)
        sigma_phi = model.estimate_sigma_phi_proxy(white_noise)
        self.assertGreater(sigma_phi, 0.8)

    def test_sinusoid_low_entropy(self) -> None:
        """Pure sinusoid should have low spectral entropy."""
        model = NeuroProfileModel()
        t = np.linspace(0, 10, 2048)
        sinusoid = np.sin(2 * np.pi * 10 * t)
        sigma_phi = model.estimate_sigma_phi_proxy(sinusoid)
        self.assertLess(sigma_phi, 0.5)


class TestNullModels(unittest.TestCase):
    """Tests for null model generation and ΔAIC computation."""

    def test_null_model_types(self) -> None:
        """Null model summary should include constant, linear, and power_law."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        prepared = model.preprocess(series)
        null_summary = model._fit_null_models(prepared)
        self.assertIn("constant", null_summary.aic)
        self.assertIn("linear", null_summary.aic)
        self.assertIn("power_law", null_summary.aic)

    def test_delta_aic_best_model_is_zero(self) -> None:
        """Best model should have ΔAIC = 0."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        prepared = model.preprocess(series)
        null_summary = model._fit_null_models(prepared)
        best_model = null_summary.best_model
        self.assertEqual(null_summary.delta_aic[best_model], 0.0)

    def test_null_model_parameters_present(self) -> None:
        """Null model parameters should be recorded."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        prepared = model.preprocess(series)
        null_summary = model._fit_null_models(prepared)
        self.assertIn("mean", null_summary.parameters["constant"])
        self.assertIn("slope", null_summary.parameters["linear"])
        self.assertIn("a", null_summary.parameters["power_law"])
        self.assertIn("b", null_summary.parameters["power_law"])

    def test_empty_series_null_models(self) -> None:
        """Empty series should return default null model summary."""
        model = NeuroProfileModel()
        null_summary = model._fit_null_models(np.array([]))
        self.assertEqual(null_summary.best_model, "constant")


class TestBootstrapCI(unittest.TestCase):
    """Tests for bootstrap confidence interval calculations."""

    def test_ci_bounds_ordering(self) -> None:
        """CI lower bound should be <= upper bound."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        prepared = model.preprocess(series)
        low, high = model._bootstrap_ci(prepared, model.estimate_sigma_phi_proxy)
        self.assertLessEqual(low, high)

    def test_bootstrap_reproducibility(self) -> None:
        """Bootstrap with same seed should produce same results."""
        config = NeuroProfileConfig(bootstrap_seed=42, bootstrap_samples=50)
        model1 = NeuroProfileModel(config=config)
        model2 = NeuroProfileModel(config=config)
        rng = np.random.default_rng(7)
        series = rng.normal(0.0, 1.0, 512)
        prepared = model1.preprocess(series)
        ci1 = model1._bootstrap_ci(prepared, model1.estimate_sigma_phi_proxy)
        ci2 = model2._bootstrap_ci(prepared, model2.estimate_sigma_phi_proxy)
        self.assertEqual(ci1, ci2)

    def test_null_model_bootstrap_ledger(self) -> None:
        """Null model bootstrap should produce a ledger of entries."""
        model = NeuroProfileModel()
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 256)
        prepared = model.preprocess(series)
        ledger = model._bootstrap_null_models(prepared)
        self.assertEqual(len(ledger), model.config.bootstrap_samples)
        for entry in ledger:
            self.assertIn(entry.best_model, ["constant", "linear", "power_law"])


class TestCREP(unittest.TestCase):
    """Tests for CREP (Coherence, Resonance, Emergence, Potential) calculation."""

    def test_crep_components_bounded(self) -> None:
        """All CREP components should be in [0, 1]."""
        rng = np.random.default_rng(42)
        eeg_data = rng.normal(0.0, 1.0, 512)
        crep = compute_crep(
            beta=4.8,
            sigma_phi=0.0625,
            eeg_data=eeg_data,
            fs=256.0,
        )
        self.assertTrue(0.0 <= crep.coherence <= 1.0)
        self.assertTrue(0.0 <= crep.resonance <= 1.0)
        self.assertTrue(0.0 <= crep.emergence <= 1.0)
        self.assertTrue(0.0 <= crep.potential <= 1.0)
        self.assertTrue(0.0 <= crep.aggregate <= 1.0)

    def test_crep_aggregate_is_mean(self) -> None:
        """Aggregate should be mean of four components."""
        rng = np.random.default_rng(42)
        eeg_data = rng.normal(0.0, 1.0, 512)
        crep = compute_crep(
            beta=4.8,
            sigma_phi=0.0625,
            eeg_data=eeg_data,
            fs=256.0,
        )
        expected = (crep.coherence + crep.resonance + crep.emergence + crep.potential) / 4.0
        self.assertAlmostEqual(crep.aggregate, expected, places=6)

    def test_crep_potential_near_target(self) -> None:
        """Potential should be high when σΦ is near target."""
        rng = np.random.default_rng(42)
        eeg_data = rng.normal(0.0, 1.0, 512)
        crep = compute_crep(
            beta=4.8,
            sigma_phi=0.0625,  # Exact target
            eeg_data=eeg_data,
            fs=256.0,
            sigma_phi_target=0.0625,
        )
        self.assertGreater(crep.potential, 0.9)


class TestResonanceProxy(unittest.TestCase):
    """Tests for microtubule resonance proxy."""

    def test_resonance_proxy_bounds(self) -> None:
        """Resonance proxy values should be bounded."""
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 1024)
        result = estimate_resonance_proxy(series, fs=256.0)
        self.assertIsInstance(result, ResonanceProxyResult)
        self.assertTrue(0.0 <= result.gamma_beta_coupling <= 1.0)
        self.assertTrue(0.0 <= result.proxy_alignment <= 1.0)

    def test_short_series_resonance(self) -> None:
        """Short series should return zero resonance."""
        short_series = [1.0, 2.0, 3.0]
        result = estimate_resonance_proxy(short_series, fs=256.0)
        self.assertEqual(result.gamma_beta_coupling, 0.0)
        self.assertEqual(result.proxy_alignment, 0.0)


class TestResonantReturn(unittest.TestCase):
    """Tests for resonant return (v_RIG alignment) analysis."""

    def test_resonant_return_output_structure(self) -> None:
        """Resonant return should produce complete output structure."""
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        result = analyze_resonant_return(series)
        self.assertIsNotNone(result.beta_velocity_fit)
        self.assertIsNotNone(result.null_models)
        self.assertTrue(0.0 <= result.v_rig_alignment <= 1.0)

    def test_resonant_return_null_models(self) -> None:
        """Resonant return should include null model comparison."""
        rng = np.random.default_rng(42)
        series = rng.normal(0.0, 1.0, 512)
        result = analyze_resonant_return(series)
        self.assertIn(result.null_models.best_model, ["constant", "linear", "power_law"])


class TestEthicsGuard(unittest.TestCase):
    """Tests for ethics guard and consent enforcement."""

    def test_ethics_violation_without_consent(self) -> None:
        """Analysis without consent should raise EthicsViolation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = Path(tmpdir) / "audit.log"
            guard = EthicsGuard(audit_path)
            with self.assertRaises(EthicsViolation):
                guard.check_before_analysis(
                    location="lab",
                    crep=0.8,
                    consent_granted=False,
                    subject_hash="test",
                )

    def test_public_mode_warning(self) -> None:
        """Public location should trigger PUBLIC_MODE_RISK warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = Path(tmpdir) / "audit.log"
            guard = EthicsGuard(audit_path)
            report = guard.check_before_analysis(
                location="public",
                crep=0.8,
                consent_granted=True,
                subject_hash="test",
            )
            warning_codes = [w.code for w in report.warnings]
            self.assertIn("PUBLIC_MODE_RISK", warning_codes)

    def test_low_crep_warning(self) -> None:
        """Low CREP should trigger FRAME_DRIFT warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = Path(tmpdir) / "audit.log"
            guard = EthicsGuard(audit_path)
            report = guard.check_before_analysis(
                location="lab",
                crep=0.5,  # Below default threshold of 0.70
                consent_granted=True,
                subject_hash="test",
            )
            warning_codes = [w.code for w in report.warnings]
            self.assertIn("FRAME_DRIFT", warning_codes)

    def test_audit_log_creation(self) -> None:
        """Warnings should be logged to audit file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = Path(tmpdir) / "audit.log"
            guard = EthicsGuard(audit_path)
            guard.check_before_analysis(
                location="public",
                crep=0.5,
                consent_granted=True,
                subject_hash="test-subject",
            )
            self.assertTrue(audit_path.exists())
            content = audit_path.read_text()
            self.assertIn("test-subject", content)
            self.assertIn("PUBLIC_MODE_RISK", content)


class TestBCICalibrator(unittest.TestCase):
    """Tests for BCI calibrator."""

    def test_calibration_quality_calculation(self) -> None:
        """Calibration quality should scale with channel count."""
        calibrator = BCICalibrator(target_channels=16)
        # 16 channels should give quality = 1.0
        data_16ch = np.random.default_rng(42).normal(0, 1, (16, 100))
        result = calibrator.calibrate(data_16ch)
        self.assertEqual(result.quality, 1.0)
        self.assertEqual(result.calibration_status, "calibrated")

    def test_degraded_calibration(self) -> None:
        """Few channels should result in degraded status."""
        calibrator = BCICalibrator(target_channels=16)
        data_4ch = np.random.default_rng(42).normal(0, 1, (4, 100))
        result = calibrator.calibrate(data_4ch)
        self.assertLess(result.quality, 0.7)
        self.assertEqual(result.calibration_status, "degraded")

    def test_single_channel_data(self) -> None:
        """1D array should be treated as single channel."""
        calibrator = BCICalibrator(target_channels=16)
        data_1d = np.random.default_rng(42).normal(0, 1, 100)
        result = calibrator.calibrate(data_1d)
        self.assertEqual(result.detected_channels, 1)


class TestSgrABridge(unittest.TestCase):
    """Tests for Sagittarius A* resonant bridge."""

    def test_bridge_normalization(self) -> None:
        """Bridge should normalize values to valid ranges."""
        result = estimate_sgr_a_bridge(
            sigma_phi_proxy=1.5,  # Should be clamped to 1.0
            beta_fit=-1.0,  # Should be clamped to 0.0
            dipole_alignment=2.0,  # Should be clamped to 1.0
            evidence_hooks=["test_hook"],
        )
        self.assertEqual(result.sigma_phi_proxy, 1.0)
        self.assertEqual(result.beta_fit, 0.0)
        self.assertEqual(result.dipole_alignment, 1.0)

    def test_bridge_preserves_valid_values(self) -> None:
        """Bridge should preserve valid values."""
        result = estimate_sgr_a_bridge(
            sigma_phi_proxy=0.5,
            beta_fit=4.8,
            dipole_alignment=0.7,
            evidence_hooks=["hook1", "hook2"],
        )
        self.assertEqual(result.sigma_phi_proxy, 0.5)
        self.assertEqual(result.beta_fit, 4.8)
        self.assertEqual(result.dipole_alignment, 0.7)
        self.assertEqual(len(result.evidence_hooks), 2)


class TestHardwareAdapter(unittest.TestCase):
    """Tests for hardware profile loading."""

    def test_load_hardware_profiles(self) -> None:
        """Hardware profiles should load from YAML config."""
        config_path = (
            ROOT_DIR
            / "experiments"
            / "Phaethon_Geminiden_Bennu"
            / "NeuroProfile"
            / "config"
            / "hardware_profiles.yml"
        )
        if config_path.exists():
            profiles = load_hardware_profiles(config_path)
            self.assertIsInstance(profiles, dict)
            # Check that profiles have expected fields
            for tier, profile in profiles.items():
                self.assertIsNotNone(profile.channels)
                self.assertIsNotNone(profile.sampling_rate_hz)


class TestPSRMMapper(unittest.TestCase):
    """Tests for PSRM (Personal Sigillin Resonance Map) generation."""

    def test_psrm_map_structure(self) -> None:
        """PSRM map should have proper trilayer structure."""
        profile = NeuroProfile(subject_id="test-subject")
        profile.load_synthetic_data(size=512, seed=42)
        profile.analyze(consent_granted=True, consent_token="test-token")

        mapper = PSRMMapper(profile, source="synthetic")
        psrm_map = mapper.generate_sigillin_map()

        # Check trilayer structure
        payload = psrm_map.payload
        self.assertIn("layer_1_signal", payload)
        self.assertIn("layer_2_intention", payload)
        self.assertIn("layer_3_context", payload)
        self.assertIn("metadata", payload)

    def test_psrm_falsifiability_metrics(self) -> None:
        """PSRM map should include falsifiability metrics."""
        profile = NeuroProfile(subject_id="test-subject")
        profile.load_synthetic_data(size=512, seed=42)
        profile.analyze(consent_granted=True, consent_token="test-token")

        mapper = PSRMMapper(profile, source="synthetic")
        psrm_map = mapper.generate_sigillin_map()

        metadata = psrm_map.payload["metadata"]
        self.assertIn("falsifiability_metrics", metadata)
        self.assertIn("beta_ci", metadata["falsifiability_metrics"])
        self.assertIn("sigma_phi_ci", metadata["falsifiability_metrics"])
        self.assertIn("delta_aic", metadata["falsifiability_metrics"])

    def test_psrm_mandala_bridge(self) -> None:
        """PSRM map should include Mandala bridge fields."""
        profile = NeuroProfile(subject_id="test-subject")
        profile.load_synthetic_data(size=512, seed=42)
        profile.analyze(consent_granted=True, consent_token="test-token")

        mapper = PSRMMapper(profile, source="synthetic")
        psrm_map = mapper.generate_sigillin_map()

        mandala_bridge = psrm_map.payload["metadata"]["mandala_bridge"]
        self.assertIn("mandala_version", mandala_bridge)
        self.assertIn("bridge_status", mandala_bridge)


class TestNeuroProfileClass(unittest.TestCase):
    """Tests for the high-level NeuroProfile class."""

    def test_load_synthetic_data(self) -> None:
        """Synthetic data loading should be reproducible."""
        profile1 = NeuroProfile()
        profile2 = NeuroProfile()
        data1 = profile1.load_synthetic_data(size=100, seed=42)
        data2 = profile2.load_synthetic_data(size=100, seed=42)
        np.testing.assert_array_equal(data1, data2)

    def test_analyze_without_data_raises(self) -> None:
        """Analysis without loaded data should raise ValueError."""
        profile = NeuroProfile()
        with self.assertRaises(ValueError):
            profile.analyze(consent_granted=True, consent_token="token")

    def test_full_pipeline(self) -> None:
        """Full pipeline should work end-to-end."""
        profile = NeuroProfile(subject_id="test-subject")
        profile.load_synthetic_data(size=512, seed=42)
        result = profile.analyze(consent_granted=True, consent_token="test-token")

        self.assertIsNotNone(result)
        self.assertEqual(profile.result, result)
        self.assertTrue(result.consent.granted)


if __name__ == "__main__":
    unittest.main()
