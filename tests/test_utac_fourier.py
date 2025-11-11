"""
Tests for UTAC Fourier Analysis Module
=======================================

Tests spectral analysis functions for UTAC threshold field systems.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sonification import utac_fourier


class TestComputeFourier:
    """Test suite for Fourier transform computation"""

    def test_basic_fourier(self):
        """Test basic FFT computation"""
        # Create simple sine wave: 440 Hz (A4)
        sampling_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sampling_rate * duration))
        signal = np.sin(2 * np.pi * 440 * t)

        # Compute Fourier
        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)

        # Check shapes
        assert len(spectrum) == len(freqs)
        assert len(spectrum) == len(signal) // 2

        # Check frequency range
        assert freqs[0] == pytest.approx(0.0, abs=1e-3)
        assert freqs[-1] < sampling_rate / 2  # Nyquist limit

        # Check peak at 440 Hz
        peak_idx = np.argmax(spectrum)
        peak_freq = freqs[peak_idx]
        assert peak_freq == pytest.approx(440.0, abs=2.0)  # Within 2 Hz

    def test_composite_signal(self):
        """Test FFT on composite signal (multiple frequencies)"""
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)

        # Composite: 220 Hz + 440 Hz + 880 Hz
        signal = (np.sin(2 * np.pi * 220 * t) +
                  np.sin(2 * np.pi * 440 * t) +
                  np.sin(2 * np.pi * 880 * t))

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)

        # Find peaks (should be at 220, 440, 880 Hz)
        peaks = []
        for i in range(1, len(spectrum) - 1):
            if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1]:
                if spectrum[i] > 1000:  # Significant peak
                    peaks.append(freqs[i])

        # Check we found 3 major peaks
        assert len(peaks) >= 3

        # Check peaks are near expected frequencies
        expected = [220, 440, 880]
        for exp_freq in expected:
            assert any(abs(peak - exp_freq) < 5 for peak in peaks)

    def test_custom_sampling_rate(self):
        """Test FFT with custom sampling rate"""
        # Climate data: 1 Hz sampling (1 sample per day)
        sampling_rate = 1.0
        duration = 365  # 1 year
        t = np.linspace(0, duration, int(sampling_rate * duration))

        # Annual cycle: period = 365 days → freq = 1/365 Hz
        signal = np.sin(2 * np.pi * (1/365) * t)

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)

        # Check Nyquist is at 0.5 Hz (half of sampling rate)
        assert freqs[-1] == pytest.approx(0.5, abs=0.01)

        # Check peak near 1/365 Hz
        peak_idx = np.argmax(spectrum)
        peak_freq = freqs[peak_idx]
        assert peak_freq == pytest.approx(1/365, abs=0.01)


class TestSpectralFeatures:
    """Test suite for spectral feature extraction"""

    def test_dominant_frequency(self):
        """Test dominant frequency detection"""
        # Create signal with clear dominant freq at 440 Hz
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)
        signal = np.sin(2 * np.pi * 440 * t)

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)
        features = utac_fourier.spectral_features(spectrum, freqs)

        assert features['dominant_freq'] == pytest.approx(440.0, abs=2.0)

    def test_spectral_centroid(self):
        """Test spectral centroid computation"""
        # Low frequency signal → low centroid
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)
        signal_low = np.sin(2 * np.pi * 100 * t)

        spectrum_low, freqs = utac_fourier.compute_fourier(signal_low, sampling_rate)
        features_low = utac_fourier.spectral_features(spectrum_low, freqs)

        # High frequency signal → high centroid
        signal_high = np.sin(2 * np.pi * 1000 * t)
        spectrum_high, freqs = utac_fourier.compute_fourier(signal_high, sampling_rate)
        features_high = utac_fourier.spectral_features(spectrum_high, freqs)

        assert features_low['centroid'] < features_high['centroid']

    def test_spectral_entropy(self):
        """Test spectral entropy computation"""
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)

        # Pure tone → low entropy (concentrated)
        pure_tone = np.sin(2 * np.pi * 440 * t)
        spectrum_pure, freqs = utac_fourier.compute_fourier(pure_tone, sampling_rate)
        features_pure = utac_fourier.spectral_features(spectrum_pure, freqs)

        # White noise → high entropy (distributed)
        np.random.seed(42)
        noise = np.random.randn(sampling_rate)
        spectrum_noise, freqs = utac_fourier.compute_fourier(noise, sampling_rate)
        features_noise = utac_fourier.spectral_features(spectrum_noise, freqs)

        # Entropy should be higher for noise than pure tone
        assert features_noise['entropy'] > features_pure['entropy']

    def test_feature_keys(self):
        """Test that all expected features are present"""
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)
        signal = np.sin(2 * np.pi * 440 * t)

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)
        features = utac_fourier.spectral_features(spectrum, freqs)

        # Check all required keys exist
        assert 'dominant_freq' in features
        assert 'entropy' in features
        assert 'centroid' in features

        # Check values are numeric
        assert isinstance(features['dominant_freq'], (int, float, np.number))
        assert isinstance(features['entropy'], (int, float, np.number))
        assert isinstance(features['centroid'], (int, float, np.number))


class TestClassifyFieldType:
    """Test suite for UTAC field type classification"""

    def test_weakly_coupled(self):
        """Test Weakly Coupled classification (< 150 Hz)"""
        features = {'dominant_freq': 110}
        field_type = utac_fourier.classify_field_type(features)
        assert field_type == 'Weakly Coupled'

    def test_strongly_coupled(self):
        """Test Strongly Coupled classification (150-300 Hz)"""
        features = {'dominant_freq': 220}
        field_type = utac_fourier.classify_field_type(features)
        assert field_type == 'Strongly Coupled'

    def test_high_dimensional(self):
        """Test High-Dimensional classification (300-600 Hz)"""
        features = {'dominant_freq': 440}
        field_type = utac_fourier.classify_field_type(features)
        assert field_type == 'High-Dimensional'

    def test_physically_constrained(self):
        """Test Physically Constrained classification (600-1000 Hz)"""
        features = {'dominant_freq': 800}
        field_type = utac_fourier.classify_field_type(features)
        assert field_type == 'Physically Constrained'

    def test_meta_adaptive(self):
        """Test Meta-Adaptive classification (> 1000 Hz)"""
        features = {'dominant_freq': 1500}
        field_type = utac_fourier.classify_field_type(features)
        assert field_type == 'Meta-Adaptive'

    def test_boundary_conditions(self):
        """Test classification at boundary frequencies"""
        # Exactly at 150 Hz → Strongly Coupled (>= 150)
        features_150 = {'dominant_freq': 150}
        assert utac_fourier.classify_field_type(features_150) == 'Strongly Coupled'

        # Just below 150 Hz → Weakly Coupled
        features_149 = {'dominant_freq': 149}
        assert utac_fourier.classify_field_type(features_149) == 'Weakly Coupled'

        # Exactly at 1000 Hz → Meta-Adaptive (>= 1000 per classification logic)
        features_1000 = {'dominant_freq': 1000}
        assert utac_fourier.classify_field_type(features_1000) == 'Meta-Adaptive'

        # Just below 1000 Hz → Physically Constrained
        features_999 = {'dominant_freq': 999}
        assert utac_fourier.classify_field_type(features_999) == 'Physically Constrained'


class TestRunAnalysis:
    """Test suite for complete analysis pipeline"""

    def test_complete_pipeline(self):
        """Test full analysis pipeline"""
        # Create test signal: 220 Hz (Strongly Coupled)
        sampling_rate = 44100
        t = np.linspace(0, 1, sampling_rate)
        signal = np.sin(2 * np.pi * 220 * t)

        # Run analysis (without plot to avoid display issues)
        results = utac_fourier.run_analysis(signal, sampling_rate, title='Test', save_path=None)

        # Check all keys exist
        assert 'features' in results
        assert 'field_type' in results
        assert 'spectrum' in results
        assert 'freqs' in results

        # Check types
        assert isinstance(results['features'], dict)
        assert isinstance(results['field_type'], str)
        assert isinstance(results['spectrum'], np.ndarray)
        assert isinstance(results['freqs'], np.ndarray)

        # Check field type is correct
        assert results['field_type'] == 'Strongly Coupled'

        # Check dominant frequency is correct
        assert results['features']['dominant_freq'] == pytest.approx(220.0, abs=2.0)

    def test_utac_field_type_spectrum(self):
        """Test analysis across different UTAC field types"""
        sampling_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sampling_rate * duration))

        # Test each field type
        test_cases = [
            (110, 'Weakly Coupled'),
            (220, 'Strongly Coupled'),
            (440, 'High-Dimensional'),
            (800, 'Physically Constrained'),
            (1500, 'Meta-Adaptive'),
        ]

        for freq, expected_type in test_cases:
            signal = np.sin(2 * np.pi * freq * t)
            results = utac_fourier.run_analysis(signal, sampling_rate, save_path=None)

            assert results['field_type'] == expected_type
            assert results['features']['dominant_freq'] == pytest.approx(freq, abs=5.0)


class TestEdgeCases:
    """Test suite for edge cases and robustness"""

    def test_empty_signal(self):
        """Test handling of empty signal"""
        with pytest.raises((IndexError, ValueError)):
            signal = np.array([])
            utac_fourier.compute_fourier(signal)

    def test_single_sample(self):
        """Test handling of single sample"""
        # Single sample should work but give trivial spectrum
        signal = np.array([1.0])
        spectrum, freqs = utac_fourier.compute_fourier(signal)

        # Should have 0 frequency bins (N//2 = 1//2 = 0)
        assert len(spectrum) == 0
        assert len(freqs) == 0

    def test_zero_signal(self):
        """Test handling of zero signal (DC only)"""
        sampling_rate = 44100
        signal = np.zeros(sampling_rate)

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)

        # Zero signal should have near-zero spectrum
        assert np.sum(spectrum) == pytest.approx(0.0, abs=1e-6)

    def test_dc_signal(self):
        """Test handling of DC signal (constant)"""
        sampling_rate = 44100
        signal = np.ones(sampling_rate) * 5.0  # DC = 5.0

        spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate)

        # Peak should be at 0 Hz (DC)
        assert np.argmax(spectrum) == 0
        assert freqs[0] == 0.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, '-v'])
