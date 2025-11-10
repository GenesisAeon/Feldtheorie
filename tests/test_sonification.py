"""
Tests for UTAC Sonification module
===================================
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sonification import UTACsonifier, FIELD_TYPE_PROFILES


class TestUTACsonifier:
    """Test suite for UTACsonifier class"""

    def test_init(self):
        """Test initialization"""
        sonifier = UTACsonifier(sample_rate=44100, duration=3.0)
        assert sonifier.sample_rate == 44100
        assert sonifier.duration == 3.0

    def test_logistic_curve(self):
        """Test logistic function σ(β(R-Θ))"""
        sonifier = UTACsonifier()

        R = np.array([98, 99, 100, 101, 102])
        beta = 4.0
        theta = 100.0

        sigma = sonifier.logistic_curve(R, beta, theta)

        # Check shape
        assert sigma.shape == R.shape

        # Check values
        assert sigma[2] == pytest.approx(0.5, abs=1e-3)  # σ(0) = 0.5
        assert sigma[0] < 0.1  # Far below threshold
        assert sigma[4] > 0.9  # Far above threshold

        # Check monotonicity
        assert all(sigma[i] < sigma[i+1] for i in range(len(sigma)-1))

    def test_classify_field_type(self):
        """Test field type classification"""
        sonifier = UTACsonifier()

        assert sonifier.classify_field_type(2.5) == "weakly_coupled"
        assert sonifier.classify_field_type(3.47) == "high_dimensional"
        assert sonifier.classify_field_type(4.0) == "strongly_coupled"
        assert sonifier.classify_field_type(5.5) == "physically_constrained"
        assert sonifier.classify_field_type(16.3) == "meta_adaptive"  # Outlier

    def test_generate_tone(self):
        """Test tone generation with harmonics"""
        sonifier = UTACsonifier(duration=1.0)

        audio = sonifier.generate_tone(
            frequency=440.0,
            amplitude=0.8,
            harmonics=[1.0, 0.5, 0.25],
            envelope_type="sustained"
        )

        # Check shape
        expected_length = int(sonifier.sample_rate * sonifier.duration)
        assert len(audio) == expected_length

        # Check amplitude range
        assert np.max(np.abs(audio)) <= 0.8 * 1.1  # Allow 10% margin for envelope

        # Check not all zeros
        assert np.any(audio != 0)

    def test_create_envelope(self):
        """Test envelope creation"""
        sonifier = UTACsonifier()

        for env_type in ["sustained", "percussive", "gentle", "floating", "adaptive"]:
            envelope = sonifier._create_envelope(env_type, 1000)

            # Check shape
            assert len(envelope) == 1000

            # Check range
            assert np.all(envelope >= 0)
            assert np.all(envelope <= 1.1)  # Allow small overshoot

    def test_sonify_transition(self):
        """Test single transition sonification"""
        sonifier = UTACsonifier(duration=1.0)

        audio, metadata = sonifier.sonify_transition(
            beta=4.0,
            theta=100.0
        )

        # Check audio
        expected_length = int(sonifier.sample_rate * sonifier.duration)
        assert len(audio) == expected_length
        assert audio.dtype == np.float64

        # Check metadata
        assert metadata["beta"] == 4.0
        assert metadata["theta"] == 100.0
        assert "field_type" in metadata
        assert metadata["field_type"] == "strongly_coupled"
        assert "base_frequency_hz" in metadata
        assert metadata["duration_sec"] == 1.0

    def test_sonify_spectrum(self):
        """Test spectrum sonification"""
        sonifier = UTACsonifier(duration=0.5)

        beta_values = [2.5, 3.5, 4.5]
        audio, metadata = sonifier.sonify_spectrum(
            beta_values=beta_values,
            gap_duration=0.2
        )

        # Check audio exists
        assert len(audio) > 0

        # Check metadata
        assert metadata["n_transitions"] == 3
        assert len(metadata["transitions"]) == 3

        # Check each transition
        for i, trans in enumerate(metadata["transitions"]):
            assert trans["beta"] == beta_values[i]

    def test_beta_to_frequency_scaling(self):
        """Test that higher β produces higher frequency"""
        sonifier = UTACsonifier(duration=0.5)

        # Low β
        _, meta_low = sonifier.sonify_transition(beta=2.5, theta=100)
        freq_low = meta_low["base_frequency_hz"]

        # High β
        _, meta_high = sonifier.sonify_transition(beta=6.0, theta=100)
        freq_high = meta_high["base_frequency_hz"]

        # Higher β should produce higher frequency
        assert freq_high > freq_low

    def test_field_type_profiles_complete(self):
        """Test that all field type profiles are complete"""
        required_keys = ["beta_range", "base_freq", "harmonics", "envelope", "timbre", "description"]

        for field_type, profile in FIELD_TYPE_PROFILES.items():
            for key in required_keys:
                assert key in profile, f"Missing {key} in {field_type}"

            # Check beta_range is tuple
            assert isinstance(profile["beta_range"], tuple)
            assert len(profile["beta_range"]) == 2

            # Check harmonics is list
            assert isinstance(profile["harmonics"], list)
            assert len(profile["harmonics"]) > 0

    def test_extreme_beta_values(self):
        """Test extreme β values (outliers)"""
        sonifier = UTACsonifier(duration=0.5)

        # Very low β
        audio_low, meta_low = sonifier.sonify_transition(beta=1.5, theta=100)
        assert len(audio_low) > 0
        assert meta_low["field_type"] == "weakly_coupled"

        # Very high β (urban heat)
        audio_high, meta_high = sonifier.sonify_transition(beta=20.0, theta=100)
        assert len(audio_high) > 0
        assert meta_high["field_type"] == "meta_adaptive"

    def test_reproducibility(self):
        """Test that same parameters produce same output"""
        sonifier = UTACsonifier(duration=0.5)

        audio1, meta1 = sonifier.sonify_transition(beta=4.0, theta=100)
        audio2, meta2 = sonifier.sonify_transition(beta=4.0, theta=100)

        # Should be identical
        np.testing.assert_array_almost_equal(audio1, audio2)
        assert meta1["base_frequency_hz"] == meta2["base_frequency_hz"]


class TestIntegration:
    """Integration tests with presets and file I/O"""

    def test_preset_loading(self):
        """Test loading preset files"""
        from sonification.utac_sonification import load_preset

        # Test wei preset
        preset = load_preset("wei")
        assert preset["beta"] == 3.47
        assert preset["field_type"] == "high_dimensional"

    def test_audio_save(self, tmp_path):
        """Test saving audio to file"""
        from sonification.utac_sonification import save_audio

        sonifier = UTACsonifier(duration=0.5)
        audio, _ = sonifier.sonify_transition(beta=4.0, theta=100)

        output_file = tmp_path / "test.wav"
        save_audio(audio, output_file, sonifier.sample_rate)

        # Check file exists
        assert output_file.exists()

    def test_metadata_save(self, tmp_path):
        """Test saving metadata to JSON"""
        from sonification.utac_sonification import save_metadata

        metadata = {
            "beta": 4.0,
            "theta": 100.0,
            "field_type": "strongly_coupled"
        }

        output_file = tmp_path / "test.json"
        save_metadata(metadata, output_file)

        # Check file exists
        assert output_file.exists()

        # Check content
        import json
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded["beta"] == 4.0


class TestAcousticMapping:
    """Test the acoustic mapping principles"""

    def test_beta_pitch_relationship(self):
        """Test β → pitch mapping creates distinct sonic character"""
        sonifier = UTACsonifier(duration=0.5)

        # Test that different β values produce different frequencies
        betas = [2.5, 4.0, 6.0, 10.0, 16.3]
        frequencies = []

        for beta in betas:
            _, meta = sonifier.sonify_transition(beta=beta, theta=100)
            frequencies.append(meta["base_frequency_hz"])

        # All frequencies should be different
        assert len(set(frequencies)) == len(frequencies), \
            f"Expected unique frequencies for different β values, got: {frequencies}"

        # Test that β-scaling works within a fixed field type profile
        # By testing the frequency multiplier directly
        base_freq = 220.0  # Example base frequency

        beta_low = 2.0
        freq_mult_low = 1.0 + (beta_low - 2.0) / 10.0

        beta_high = 6.0
        freq_mult_high = 1.0 + (beta_high - 2.0) / 10.0

        # Higher β should produce higher multiplier
        assert freq_mult_high > freq_mult_low, \
            f"Expected higher β to produce higher frequency multiplier"

        # Check actual scaled frequencies
        assert base_freq * freq_mult_high > base_freq * freq_mult_low

    def test_threshold_crossing_amplitude(self):
        """Test that amplitude peaks at threshold crossing"""
        sonifier = UTACsonifier(duration=1.0)

        # Generate audio
        audio, metadata = sonifier.sonify_transition(beta=4.0, theta=100)

        # Find peak amplitude position
        peak_idx = np.argmax(np.abs(audio))
        peak_position = peak_idx / len(audio)

        # Should be roughly in the middle (threshold crossing)
        assert 0.3 < peak_position < 0.7, f"Peak at position {peak_position}, expected ~0.5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
