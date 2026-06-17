"""Unit tests for Phaethon/Bennu simulation modules.

Tests cover:
  - ChimeraStateModel (chimera_state_model.py)
  - PlasmaResonanceModel (plasma_resonance_model.py)
  - KdVSolver & DustySolitonModel (soliton_generator.py)
  - IntegratedAsteroidSimulation (integrated_asteroid_simulation.py)
  - Statistical analysis classes (statistical_analysis.py)

All tests use seeded randomness for reproducibility.

Framework: GenesisAeon / UTAC Case Study
"""

import sys
import unittest
from pathlib import Path

import numpy as np

# Ensure the experiment code directory is importable
_PHAETHON_CODE = Path(__file__).resolve().parent.parent / "experiments" / "Phaethon_Geminiden_Bennu" / "code"
if str(_PHAETHON_CODE) not in sys.path:
    sys.path.insert(0, str(_PHAETHON_CODE))


# ---------------------------------------------------------------------------
# Chimera State Model Tests
# ---------------------------------------------------------------------------

class TestBennuParameters(unittest.TestCase):
    """Tests for BennuParameters dataclass defaults."""

    def test_default_values(self) -> None:
        from chimera_state_model import BennuParameters

        params = BennuParameters()
        self.assertAlmostEqual(params.surface_gravity, 1e-5)
        self.assertAlmostEqual(params.escape_velocity, 0.20)
        self.assertEqual(params.max_temperature, 400)
        self.assertEqual(params.min_temperature, 100)
        self.assertAlmostEqual(params.rotation_period, 4.297)
        self.assertAlmostEqual(params.porosity, 0.50)
        self.assertAlmostEqual(params.photoemission_current, 1e-8)

    def test_ejection_time_window(self) -> None:
        from chimera_state_model import BennuParameters

        params = BennuParameters()
        self.assertEqual(params.ejection_time_window, (15.0, 18.0))


class TestChimeraStateModel(unittest.TestCase):
    """Tests for ChimeraStateModel core functionality."""

    def setUp(self) -> None:
        from chimera_state_model import BennuParameters, ChimeraStateModel

        np.random.seed(42)
        self.params = BennuParameters()
        self.model = ChimeraStateModel(self.params, n_patches=50)

    def test_initialization(self) -> None:
        self.assertEqual(self.model.n_patches, 50)
        self.assertEqual(len(self.model.phases), 50)
        self.assertEqual(len(self.model.omega_natural), 50)
        self.assertTrue(np.all(self.model.phases >= 0))
        self.assertTrue(np.all(self.model.phases <= 2 * np.pi))

    def test_thermal_forcing_range(self) -> None:
        """Thermal forcing should be in [0, 1] for all times."""
        for t in np.linspace(0, 20, 100):
            val = self.model.thermal_forcing(t)
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

    def test_thermal_forcing_periodicity(self) -> None:
        period = self.params.rotation_period
        for t in [0.0, 1.5, 3.0]:
            self.assertAlmostEqual(
                self.model.thermal_forcing(t),
                self.model.thermal_forcing(t + period),
                places=10,
            )

    def test_electrostatic_forcing_nonnegative(self) -> None:
        for t in np.linspace(0, 20, 100):
            val = self.model.electrostatic_forcing(t)
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

    def test_frustration_parameter_range(self) -> None:
        """Frustration should be in [0, 1]."""
        theta = np.random.uniform(0, 2 * np.pi, 50)
        F = self.model.frustration_parameter(theta)
        self.assertGreaterEqual(F, 0.0)
        self.assertLessEqual(F, 1.0)

    def test_frustration_coherent_state(self) -> None:
        """Fully coherent phases should have frustration near 0."""
        theta = np.zeros(50)  # all aligned
        F = self.model.frustration_parameter(theta)
        self.assertAlmostEqual(F, 0.0, places=5)

    def test_chimera_fraction_range(self) -> None:
        theta = np.random.uniform(0, 2 * np.pi, 50)
        frac = self.model.chimera_fraction(theta)
        self.assertGreaterEqual(frac, 0.0)
        self.assertLessEqual(frac, 1.0)

    def test_ejection_probability_range(self) -> None:
        prob = self.model.ejection_probability(0.5, 0.7, 0.3)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_ejection_probability_monotonic(self) -> None:
        """Higher stress should give higher ejection probability."""
        p_low = self.model.ejection_probability(0.1, 0.1, 0.1)
        p_high = self.model.ejection_probability(0.9, 0.9, 0.9)
        self.assertGreater(p_high, p_low)

    def test_kuramoto_dynamics_shape(self) -> None:
        theta = np.random.uniform(0, 2 * np.pi, 50)
        np.random.seed(42)
        dtheta = self.model.kuramoto_dynamics(theta, 1.0)
        self.assertEqual(len(dtheta), 50)

    def test_simulate_returns_expected_keys(self) -> None:
        np.random.seed(42)
        results = self.model.simulate(duration_hours=1.0, dt=0.5)
        expected_keys = {"times", "theta_history", "frustration",
                         "chimera_fraction", "ejection_probability", "events"}
        self.assertEqual(set(results.keys()), expected_keys)

    def test_simulate_time_array(self) -> None:
        np.random.seed(42)
        results = self.model.simulate(duration_hours=2.0, dt=0.5)
        self.assertEqual(len(results["times"]), 4)  # 0, 0.5, 1.0, 1.5
        self.assertAlmostEqual(results["times"][0], 0.0)


# ---------------------------------------------------------------------------
# Plasma Resonance Model Tests
# ---------------------------------------------------------------------------

class TestPhaethonParameters(unittest.TestCase):
    """Tests for PhaethonParameters dataclass."""

    def test_perihelion_distance(self) -> None:
        from plasma_resonance_model import PhaethonParameters

        p = PhaethonParameters()
        self.assertAlmostEqual(p.perihelion_distance, 0.14)
        self.assertEqual(p.max_temperature, 750)

    def test_regolith_properties(self) -> None:
        from plasma_resonance_model import PhaethonParameters

        p = PhaethonParameters()
        self.assertAlmostEqual(p.porosity, 0.60)
        self.assertEqual(p.sound_speed, 100)


class TestPlasmaResonanceModel(unittest.TestCase):
    """Tests for PlasmaResonanceModel calculations."""

    def setUp(self) -> None:
        from plasma_resonance_model import (
            PhaethonParameters,
            PlasmaResonanceModel,
            SolarWindParameters,
        )

        self.phaethon = PhaethonParameters()
        self.sw = SolarWindParameters()
        self.model = PlasmaResonanceModel(self.phaethon, self.sw)

    def test_alfven_velocity_positive(self) -> None:
        v_A = self.model.alfven_velocity()
        self.assertGreater(v_A, 0)
        # Should be in the range of hundreds of km/s
        self.assertGreater(v_A, 1e4)

    def test_plasma_beta_positive(self) -> None:
        beta = self.model.plasma_beta()
        self.assertGreater(beta, 0)

    def test_regolith_resonance_frequencies(self) -> None:
        freqs = self.model.regolith_resonance_frequencies(n_modes=5)
        self.assertEqual(len(freqs), 5)
        # Should be monotonically increasing (harmonics)
        for i in range(1, len(freqs)):
            self.assertGreater(freqs[i], freqs[i - 1])
        # Fundamental should be positive
        self.assertGreater(freqs[0], 0)

    def test_alfven_frequency_spectrum_shape(self) -> None:
        frequencies = np.logspace(-1, 2, 100)
        power = self.model.alfven_frequency_spectrum(frequencies)
        self.assertEqual(len(power), 100)
        # Power should be non-negative
        self.assertTrue(np.all(power >= 0))

    def test_coupling_efficiency_peak(self) -> None:
        """Coupling should peak when frequencies match."""
        eff_match = self.model.coupling_efficiency(5.0, 5.0)
        eff_mismatch = self.model.coupling_efficiency(5.0, 50.0)
        self.assertAlmostEqual(eff_match, 1.0)
        self.assertLess(eff_mismatch, 0.01)

    def test_coupling_efficiency_range(self) -> None:
        eff = self.model.coupling_efficiency(1.0, 2.0)
        self.assertGreaterEqual(eff, 0.0)
        self.assertLessEqual(eff, 1.0)

    def test_dust_emission_rate_nonnegative(self) -> None:
        rate = self.model.dust_emission_rate(0.5, 600)
        self.assertGreaterEqual(rate, 0.0)

    def test_dust_emission_rate_threshold(self) -> None:
        """Low coupling should give low emission."""
        rate_low = self.model.dust_emission_rate(0.01, 400)
        rate_high = self.model.dust_emission_rate(0.99, 750)
        self.assertGreater(rate_high, rate_low)

    def test_resonance_map_keys(self) -> None:
        result = self.model.resonance_map(freq_range=(1, 50), n_points=100)
        expected_keys = {"frequencies", "alfven_power", "coupling",
                         "emission_rate", "resonances"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_resonance_map_dimensions(self) -> None:
        result = self.model.resonance_map(freq_range=(1, 50), n_points=100)
        self.assertEqual(len(result["frequencies"]), 100)
        self.assertEqual(len(result["coupling"]), 100)
        self.assertEqual(len(result["emission_rate"]), 100)

    def test_generate_report_nonempty(self) -> None:
        report = self.model.generate_report()
        self.assertIn("PHAETHON", report)
        self.assertIn("Alfvén", report)


# ---------------------------------------------------------------------------
# Soliton Generator Tests
# ---------------------------------------------------------------------------

class TestKdVSolver(unittest.TestCase):
    """Tests for the KdV spectral solver."""

    def setUp(self) -> None:
        from soliton_generator import KdVSolver

        self.solver = KdVSolver(alpha=6.0, beta=1.0, L=100, N=128)

    def test_spatial_grid(self) -> None:
        self.assertEqual(len(self.solver.x), 128)
        self.assertAlmostEqual(self.solver.x[0], -50.0)

    def test_soliton_initial_condition_peak(self) -> None:
        u0 = self.solver.soliton_initial_condition(amplitude=2.0, width=3.0, x0=0)
        # Peak should be near the center
        peak_idx = np.argmax(u0)
        self.assertAlmostEqual(self.solver.x[peak_idx], 0.0, delta=2.0)
        self.assertAlmostEqual(np.max(u0), 2.0, places=1)

    def test_soliton_sech_squared_profile(self) -> None:
        """Soliton profile should be sech^2."""
        u0 = self.solver.soliton_initial_condition(amplitude=1.0, width=2.0, x0=0)
        expected = 1.0 / np.cosh(self.solver.x / 2.0) ** 2
        np.testing.assert_allclose(u0, expected, atol=1e-10)

    def test_multi_soliton_superposition(self) -> None:
        u0 = self.solver.multi_soliton(
            amplitudes=[1.0, 2.0],
            widths=[2.0, 3.0],
            positions=[-20, 20],
        )
        self.assertEqual(len(u0), 128)
        # Should have two bumps
        self.assertGreater(np.max(u0), 1.5)

    def test_rhs_spectral_shape(self) -> None:
        from scipy.fft import fft

        u0 = self.solver.soliton_initial_condition()
        u0_hat = fft(u0)
        rhs = self.solver.rhs_spectral(0.0, u0_hat)
        self.assertEqual(len(rhs), 128)

    def test_solve_returns_expected_keys(self) -> None:
        u0 = self.solver.soliton_initial_condition()
        result = self.solver.solve(u0, t_span=(0, 1), n_frames=5)
        expected_keys = {"x", "t", "u", "n_frames"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_solve_time_points(self) -> None:
        u0 = self.solver.soliton_initial_condition()
        result = self.solver.solve(u0, t_span=(0, 1), n_frames=10)
        self.assertGreater(len(result["t"]), 0)


class TestDustySolitonModel(unittest.TestCase):
    """Tests for DustySolitonModel physics calculations."""

    def setUp(self) -> None:
        from soliton_generator import DustyPlasmaParameters, DustySolitonModel

        self.params = DustyPlasmaParameters()
        self.model = DustySolitonModel(self.params)

    def test_dust_acoustic_speed(self) -> None:
        c_d = self.model.dust_acoustic_speed()
        self.assertEqual(c_d, self.params.acoustic_speed)
        self.assertGreater(c_d, 0)

    def test_debye_length_positive(self) -> None:
        lam = self.model.debye_length()
        self.assertGreater(lam, 0)
        # Debye length should be in the meter to sub-meter range
        self.assertGreater(lam, 1e-3)
        self.assertLess(lam, 100)

    def test_dust_plasma_frequency_positive(self) -> None:
        omega = self.model.dust_plasma_frequency()
        self.assertGreater(omega, 0)

    def test_soliton_amplitude_to_velocity(self) -> None:
        v = self.model.soliton_amplitude_to_velocity(1.0)
        c_d = self.model.dust_acoustic_speed()
        # Should be slightly above acoustic speed
        self.assertGreater(v, c_d)

    def test_charge_distribution_shape(self) -> None:
        x = np.linspace(-50, 50, 100)
        profile = 1.0 / np.cosh(x / 2) ** 2
        density = self.model.charge_distribution(x, profile)
        self.assertEqual(len(density), 100)

    def test_energy_density_positive(self) -> None:
        u = np.sin(np.linspace(0, 2 * np.pi, 100))
        E = self.model.energy_density(u, 0.1)
        self.assertGreater(E, 0)


# ---------------------------------------------------------------------------
# Integrated Asteroid Simulation Tests
# ---------------------------------------------------------------------------

class TestPhysicalConstants(unittest.TestCase):
    """Tests for the PhysicalConstants dataclass."""

    def test_speed_of_light(self) -> None:
        from integrated_asteroid_simulation import CONSTANTS

        self.assertAlmostEqual(CONSTANTS.c, 2.998e8, places=0)

    def test_hex_resonance_beta(self) -> None:
        from integrated_asteroid_simulation import CONSTANTS

        self.assertAlmostEqual(CONSTANTS.HEX_RESONANCE_BETA, 4.8)


class TestPhaethonSystem(unittest.TestCase):
    """Tests for the PhaethonSystem parameter set."""

    def test_computed_properties(self) -> None:
        from integrated_asteroid_simulation import CONSTANTS, PhaethonSystem

        p = PhaethonSystem()
        self.assertAlmostEqual(p.perihelion_m, 0.14 * CONSTANTS.AU)
        self.assertGreater(p.rotation_freq_Hz, 0)
        self.assertGreater(p.omega_rotation, 0)


class TestSolarWindAtPhaethon(unittest.TestCase):
    """Tests for solar wind parameter properties."""

    def test_alfven_velocity(self) -> None:
        from integrated_asteroid_simulation import SolarWindAtPhaethon

        sw = SolarWindAtPhaethon()
        self.assertGreater(sw.v_alfven, 1e4)  # > 10 km/s

    def test_plasma_beta(self) -> None:
        from integrated_asteroid_simulation import SolarWindAtPhaethon

        sw = SolarWindAtPhaethon()
        self.assertGreater(sw.plasma_beta, 0)

    def test_debye_length(self) -> None:
        from integrated_asteroid_simulation import SolarWindAtPhaethon

        sw = SolarWindAtPhaethon()
        self.assertGreater(sw.debye_length, 0)


class TestEnhancedChimeraModel(unittest.TestCase):
    """Tests for the enhanced chimera state model."""

    def setUp(self) -> None:
        from integrated_asteroid_simulation import EnhancedChimeraModel, PhaethonSystem

        self.phaethon = PhaethonSystem()
        self.model = EnhancedChimeraModel(self.phaethon, n_patches=30, seed=42)

    def test_initialization(self) -> None:
        self.assertEqual(self.model.n_patches, 30)
        self.assertEqual(len(self.model.phases), 30)

    def test_temperature_profile_range(self) -> None:
        offsets = np.linspace(0, self.phaethon.rotation_period_h, 30, endpoint=False)
        T = self.model.temperature_profile(1.0, offsets)
        self.assertTrue(np.all(T >= self.phaethon.T_min_K))
        self.assertTrue(np.all(T <= self.phaethon.T_max_K))

    def test_electrostatic_force_nonneg(self) -> None:
        T = np.array([200.0, 500.0, 1050.0])
        F = self.model.electrostatic_force(T)
        self.assertTrue(np.all(F >= 0))

    def test_compute_frustration_range(self) -> None:
        phases = np.random.uniform(0, 2 * np.pi, 30)
        F = self.model.compute_frustration(phases)
        self.assertGreaterEqual(F, 0.0)
        self.assertLessEqual(F, 1.0)

    def test_compute_chimera_fraction_returns_tuple(self) -> None:
        phases = np.random.uniform(0, 2 * np.pi, 30)
        frac, local_order = self.model.compute_chimera_fraction(phases)
        self.assertGreaterEqual(frac, 0.0)
        self.assertLessEqual(frac, 1.0)
        self.assertEqual(len(local_order), 30)

    def test_ejection_probability_shape(self) -> None:
        T = np.full(30, 600.0)
        E = np.full(30, 10.0)
        local_order = np.full(30, 0.5)
        prob = self.model.ejection_probability(0.4, T, E, local_order)
        self.assertEqual(len(prob), 30)
        self.assertTrue(np.all(prob >= 0))
        self.assertTrue(np.all(prob <= 1))

    def test_simulate_short_run(self) -> None:
        results = self.model.simulate(duration_hours=0.5, dt=0.1)
        expected_keys = {"times", "LST_offsets", "phases", "frustration",
                         "chimera_fraction", "ejection_probability",
                         "temperature", "events", "activation_history"}
        self.assertEqual(set(results.keys()), expected_keys)
        self.assertEqual(len(results["times"]), 5)  # 0, 0.1, 0.2, 0.3, 0.4


class TestIntegratedPlasmaSolitonModel(unittest.TestCase):
    """Tests for the integrated plasma-soliton model."""

    def setUp(self) -> None:
        from integrated_asteroid_simulation import (
            IntegratedPlasmaSolitonModel,
            PhaethonSystem,
            SolarWindAtPhaethon,
        )

        self.model = IntegratedPlasmaSolitonModel(
            PhaethonSystem(), SolarWindAtPhaethon()
        )

    def test_alfven_wave_spectrum_shape(self) -> None:
        freqs = np.logspace(-2, 2, 50)
        power = self.model.alfven_wave_spectrum(freqs)
        self.assertEqual(len(power), 50)
        self.assertTrue(np.all(power >= 0))

    def test_regolith_response_normalized(self) -> None:
        freqs = np.logspace(-1, 2, 200)
        response = self.model.regolith_response(freqs)
        self.assertAlmostEqual(np.max(response), 1.0, places=5)
        self.assertTrue(np.all(response >= 0))

    def test_soliton_velocity_distribution(self) -> None:
        np.random.seed(42)
        v = self.model.soliton_velocity_distribution(n_particles=1000)
        self.assertEqual(len(v), 1300)  # 1000 * (0.5+0.3+0.2) + 0.3*1000 thermal
        self.assertGreater(np.mean(v), 50)  # should include fast particles

    def test_dust_charge_distribution(self) -> None:
        np.random.seed(42)
        charges = self.model.dust_charge_distribution(n_particles=1000)
        self.assertEqual(len(charges), 1000)
        self.assertTrue(np.all(charges >= 0))

    def test_compute_resonance_coupling_keys(self) -> None:
        result = self.model.compute_resonance_coupling()
        expected_keys = {"frequencies", "alfven_power", "regolith_response",
                         "coupling", "peak_frequencies"}
        self.assertEqual(set(result.keys()), expected_keys)


class TestDestinyPredictionsCalculator(unittest.TestCase):
    """Tests for DESTINY+ predictions calculator."""

    def test_predictions_count(self) -> None:
        from integrated_asteroid_simulation import (
            DestinyPredictionsCalculator,
            PhaethonSystem,
            SolarWindAtPhaethon,
        )

        calc = DestinyPredictionsCalculator(PhaethonSystem(), SolarWindAtPhaethon())

        # Create minimal chimera results
        chimera_results = {
            "chimera_fraction": np.array([0.4, 0.5, 0.45]),
            "events": [
                {"LST": 2.5, "time": 1.0},
                {"LST": 2.8, "time": 2.0},
            ],
        }
        plasma_results = {"peak_frequencies": np.array([5, 10, 15])}

        predictions = calc.calculate_all_predictions(chimera_results, plasma_results)
        # Should have at least 30 prediction keys
        self.assertGreater(len(predictions), 30)
        self.assertIn("beta_threshold", predictions)
        self.assertIn("alfven_velocity_kms", predictions)

    def test_predictions_table_generation(self) -> None:
        from integrated_asteroid_simulation import (
            DestinyPredictionsCalculator,
            PhaethonSystem,
            SolarWindAtPhaethon,
        )

        calc = DestinyPredictionsCalculator(PhaethonSystem(), SolarWindAtPhaethon())
        chimera_results = {
            "chimera_fraction": np.array([0.45]),
            "events": [{"LST": 2.5, "time": 1.0}],
        }
        plasma_results = {"peak_frequencies": np.array([5])}
        calc.calculate_all_predictions(chimera_results, plasma_results)

        table = calc.generate_predictions_table()
        self.assertIn("DESTINY+", table)
        self.assertIn("FALSIFICATION", table)


# ---------------------------------------------------------------------------
# Statistical Analysis Tests
# ---------------------------------------------------------------------------

class TestStatisticalResult(unittest.TestCase):
    """Tests for StatisticalResult dataclass."""

    def test_str_representation(self) -> None:
        from statistical_analysis import StatisticalResult

        r = StatisticalResult(
            test_name="Test",
            statistic=1.5,
            p_value=0.03,
            hypothesis_supported="CHIMERA",
            confidence="HIGH",
            details="test details",
        )
        s = str(r)
        self.assertIn("Test", s)
        self.assertIn("1.5", s)
        self.assertIn("CHIMERA", s)


class TestLSTAnalyzer(unittest.TestCase):
    """Tests for LST distribution analysis."""

    def setUp(self) -> None:
        from statistical_analysis import LSTAnalyzer

        np.random.seed(42)
        # Generate clustered LST data around 2.5 hours (late afternoon equivalent)
        self.LSTs = np.random.normal(2.5, 0.3, 200) % 3.604
        self.analyzer = LSTAnalyzer(self.LSTs, period_h=3.604)

    def test_circular_mean_range(self) -> None:
        mean = self.analyzer.compute_circular_mean()
        self.assertGreaterEqual(mean, 0)
        self.assertLessEqual(mean, self.analyzer.period)

    def test_circular_variance_range(self) -> None:
        var = self.analyzer.compute_circular_variance()
        self.assertGreaterEqual(var, 0.0)
        self.assertLessEqual(var, 1.0)

    def test_uniformity_test_result_type(self) -> None:
        from statistical_analysis import StatisticalResult

        result = self.analyzer.test_uniformity()
        self.assertIsInstance(result, StatisticalResult)
        self.assertIn("Rayleigh", result.test_name)

    def test_chimera_vs_thermal_result(self) -> None:
        from statistical_analysis import StatisticalResult

        result = self.analyzer.test_chimera_vs_thermal()
        self.assertIsInstance(result, StatisticalResult)
        self.assertIn(result.hypothesis_supported, ["CHIMERA", "THERMAL"])

    def test_peak_lst(self) -> None:
        peak_lst, peak_density = self.analyzer.compute_peak_LST()
        self.assertGreaterEqual(peak_lst, 0)
        self.assertLessEqual(peak_lst, self.analyzer.period)
        self.assertGreater(peak_density, 0)

    def test_generate_report(self) -> None:
        report = self.analyzer.generate_report()
        self.assertIn("LST DISTRIBUTION", report)
        self.assertIn("FALSIFICATION", report)


class TestVelocityAnalyzer(unittest.TestCase):
    """Tests for velocity distribution analysis."""

    def setUp(self) -> None:
        from statistical_analysis import VelocityAnalyzer

        np.random.seed(42)
        # Multi-modal velocity distribution
        v1 = np.random.normal(120, 15, 500)
        v2 = np.random.normal(250, 25, 300)
        v3 = np.random.normal(380, 35, 200)
        self.velocities = np.concatenate([v1, v2, v3])
        self.analyzer = VelocityAnalyzer(self.velocities)

    def test_n_particles(self) -> None:
        self.assertEqual(self.analyzer.n_particles, 1000)

    def test_fit_gaussian_mixture(self) -> None:
        result = self.analyzer.fit_gaussian_mixture(n_components=2)
        self.assertIn("weights", result)
        self.assertIn("means", result)
        self.assertIn("bic", result)
        self.assertEqual(result["n_components"], 2)
        # Weights should sum to 1
        self.assertAlmostEqual(np.sum(result["weights"]), 1.0, places=5)

    def test_multimodality_test(self) -> None:
        from statistical_analysis import StatisticalResult

        result = self.analyzer.test_multimodality()
        self.assertIsInstance(result, StatisticalResult)

    def test_high_velocity_excess(self) -> None:
        from statistical_analysis import StatisticalResult

        result = self.analyzer.test_high_velocity_excess(threshold=200)
        self.assertIsInstance(result, StatisticalResult)
        # With our multi-modal data, there should be excess
        self.assertIn("SOLITON", result.hypothesis_supported)

    def test_identify_velocity_peaks(self) -> None:
        peaks = self.analyzer.identify_velocity_peaks()
        self.assertIsInstance(peaks, list)
        self.assertGreater(len(peaks), 0)

    def test_generate_report(self) -> None:
        report = self.analyzer.generate_report()
        self.assertIn("VELOCITY", report)


class TestRepeatabilityAnalyzer(unittest.TestCase):
    """Tests for spatial repeatability analysis."""

    def setUp(self) -> None:
        from statistical_analysis import RepeatabilityAnalyzer

        # Activation with some patches active multiple times
        self.activation = np.array([0, 0, 3, 1, 5, 0, 2, 1, 0, 4])
        self.analyzer = RepeatabilityAnalyzer(self.activation, n_orbits=3)

    def test_repeatability_index(self) -> None:
        R = self.analyzer.compute_repeatability_index()
        self.assertGreaterEqual(R, 0.0)
        self.assertLessEqual(R, 1.0)

    def test_repeatability_all_zero(self) -> None:
        from statistical_analysis import RepeatabilityAnalyzer

        analyzer = RepeatabilityAnalyzer(np.zeros(10), n_orbits=1)
        R = analyzer.compute_repeatability_index()
        self.assertAlmostEqual(R, 0.0)

    def test_repeatability_test_result(self) -> None:
        from statistical_analysis import StatisticalResult

        result = self.analyzer.test_repeatability()
        self.assertIsInstance(result, StatisticalResult)
        self.assertIn("Repeatability", result.test_name)

    def test_generate_report(self) -> None:
        report = self.analyzer.generate_report()
        self.assertIn("REPEATABILITY", report)


class TestComprehensiveStatisticalAnalysis(unittest.TestCase):
    """Tests for the unified statistical analysis suite."""

    def test_run_all_analyses(self) -> None:
        from statistical_analysis import ComprehensiveStatisticalAnalysis

        np.random.seed(42)
        sim_results = {
            "events": [{"LST": np.random.uniform(0, 3.604)} for _ in range(100)],
            "velocities": np.concatenate([
                np.random.normal(120, 20, 300),
                np.random.normal(250, 30, 200),
            ]),
            "activation_history": np.random.poisson(2, 50),
        }
        analyzer = ComprehensiveStatisticalAnalysis(sim_results)
        analyses = analyzer.run_all_analyses()

        self.assertIn("LST", analyses)
        self.assertIn("velocity", analyses)
        self.assertIn("repeatability", analyses)

    def test_unified_report(self) -> None:
        from statistical_analysis import ComprehensiveStatisticalAnalysis

        np.random.seed(42)
        sim_results = {
            "events": [{"LST": np.random.uniform(0, 3.604)} for _ in range(50)],
            "velocities": np.random.normal(150, 50, 200),
            "activation_history": np.random.poisson(2, 30),
        }
        analyzer = ComprehensiveStatisticalAnalysis(sim_results)
        report = analyzer.generate_unified_report()
        self.assertIn("COMPREHENSIVE", report)
        self.assertIn("SUMMARY", report)


if __name__ == "__main__":
    unittest.main()
