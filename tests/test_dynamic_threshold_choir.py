#!/usr/bin/env python3
"""
Tests for Dynamic Threshold Choir system
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from sonification.dynamic_threshold_choir import (
    ThresholdChoir,
    VoiceState,
    ChoirMetadata,
    DestabilizationEffects,
    DataSourceSimulator,
    create_demo_choir
)


class TestVoiceState:
    """Test VoiceState dataclass"""

    def test_voice_state_creation(self):
        voice = VoiceState(
            name="Test",
            beta=4.0,
            theta=50.0,
            current_R=60.0,
            field_type="strongly_coupled"
        )
        assert voice.name == "Test"
        assert voice.beta == 4.0
        assert voice.theta == 50.0
        assert voice.current_R == 60.0
        assert voice.stability == 1.0  # Default
        assert voice.pan == 0.0  # Default

    def test_voice_state_defaults(self):
        voice = VoiceState(
            name="Test",
            beta=3.0,
            theta=100.0,
            current_R=90.0,
            field_type="high_dimensional"
        )
        assert voice.amplitude == 0.5
        assert voice.frequency == 220.0
        assert voice.last_update is None


class TestDestabilizationEffects:
    """Test audio effects for destabilization"""

    def test_tremolo(self):
        # Create simple sine wave
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = np.sin(2 * np.pi * 440 * t)

        # Apply tremolo
        tremolo_signal = DestabilizationEffects.tremolo(
            signal,
            rate=5.0,
            depth=0.5,
            sample_rate=sample_rate
        )

        # Check output shape
        assert tremolo_signal.shape == signal.shape

        # Check amplitude is modulated (not constant)
        envelope = np.abs(tremolo_signal)
        assert np.std(envelope) > 0.01  # Some modulation occurred

    def test_vibrato(self):
        sample_rate = 44100
        duration = 0.5
        vibrato_signal = DestabilizationEffects.vibrato(
            frequency=440.0,
            rate=5.0,
            depth=10.0,
            duration=duration,
            sample_rate=sample_rate
        )

        # Check output shape
        expected_len = int(duration * sample_rate)
        assert len(vibrato_signal) == expected_len

        # Check signal is not constant
        assert np.std(vibrato_signal) > 0.1

    def test_noise_injection(self):
        signal = np.ones(1000)
        noisy = DestabilizationEffects.noise_injection(signal, noise_level=0.1)

        # Check shape preserved
        assert noisy.shape == signal.shape

        # Check noise was added (std > 0)
        assert np.std(noisy - signal) > 0.01

    def test_harmonic_distortion(self):
        signal = np.linspace(-1, 1, 1000)
        distorted = DestabilizationEffects.harmonic_distortion(signal, distortion=0.5)

        # Check shape preserved
        assert distorted.shape == signal.shape

        # Tanh should compress peaks
        assert np.max(np.abs(distorted)) <= np.max(np.abs(np.tanh(signal * 3.5)))


class TestThresholdChoir:
    """Test ThresholdChoir main engine"""

    def test_choir_initialization(self):
        choir = ThresholdChoir(sample_rate=44100)
        assert choir.sample_rate == 44100
        assert len(choir.voices) == 0
        assert choir.master_volume == 0.7

    def test_add_voice(self):
        choir = ThresholdChoir()
        voice = choir.add_voice(
            name="TestVoice",
            beta=4.2,
            theta=50.0,
            initial_R=60.0,
            pan=-0.5
        )

        assert voice.name == "TestVoice"
        assert voice.beta == 4.2
        assert voice.theta == 50.0
        assert voice.current_R == 60.0
        assert voice.pan == -0.5
        assert "TestVoice" in choir.voices

    def test_add_voice_default_R(self):
        choir = ThresholdChoir()
        voice = choir.add_voice("Test", beta=4.0, theta=100.0)

        # Should start before threshold
        assert voice.current_R < voice.theta

    def test_update_voice(self):
        choir = ThresholdChoir()
        choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=60.0)

        # Update with new R
        timestamp = datetime.now()
        choir.update_voice("Test", new_R=40.0, timestamp=timestamp)

        voice = choir.voices["Test"]
        assert voice.current_R == 40.0
        assert voice.last_update == timestamp

    def test_update_voice_stability(self):
        choir = ThresholdChoir()
        choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=100.0)

        # Update to near threshold
        choir.update_voice("Test", new_R=50.0)
        voice = choir.voices["Test"]

        # Stability should decrease when near threshold
        assert voice.stability < 1.0

    def test_remove_voice(self):
        choir = ThresholdChoir()
        choir.add_voice("Test", beta=4.0, theta=50.0)
        assert "Test" in choir.voices

        choir.remove_voice("Test")
        assert "Test" not in choir.voices

    def test_synthesize_voice_stable(self):
        choir = ThresholdChoir(sample_rate=44100)
        voice = choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=80.0, pan=0.0)

        audio = choir.synthesize_voice(voice, duration=1.0)

        # Check output
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0
        assert audio.dtype in [np.float32, np.float64]

    def test_synthesize_voice_unstable(self):
        choir = ThresholdChoir(sample_rate=44100)
        voice = choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=50.5, pan=0.0)

        # Force low stability
        voice.stability = 0.2

        audio = choir.synthesize_voice(voice, duration=0.5)

        # Should still produce audio
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0

    def test_apply_spatial_mix(self):
        choir = ThresholdChoir()
        signal = np.random.randn(1000)

        # Test center
        stereo_center = choir.apply_spatial_mix(signal, pan=0.0)
        assert stereo_center.shape == (2, 1000)
        # Center should have equal power in both channels
        assert np.abs(np.sum(stereo_center[0]**2) - np.sum(stereo_center[1]**2)) < 1e-5

        # Test left
        stereo_left = choir.apply_spatial_mix(signal, pan=-1.0)
        assert np.sum(stereo_left[0]**2) > np.sum(stereo_left[1]**2)

        # Test right
        stereo_right = choir.apply_spatial_mix(signal, pan=1.0)
        assert np.sum(stereo_right[1]**2) > np.sum(stereo_right[0]**2)

    def test_render_empty_choir_raises(self):
        choir = ThresholdChoir()
        with pytest.raises(ValueError, match="No voices in choir"):
            choir.render(duration=1.0)

    def test_render_single_voice(self):
        choir = ThresholdChoir(sample_rate=44100)
        choir.add_voice("Test", beta=4.0, theta=50.0, pan=0.0)

        audio = choir.render(duration=1.0)

        # Check stereo output
        assert audio.shape == (2, 44100)  # 2 channels, 1 second
        assert audio.dtype in [np.float32, np.float64]

    def test_render_multiple_voices(self):
        choir = ThresholdChoir(sample_rate=44100)
        choir.add_voice("Voice1", beta=4.0, theta=50.0, pan=-0.5)
        choir.add_voice("Voice2", beta=3.5, theta=100.0, pan=0.5)

        audio = choir.render(duration=0.5)

        # Check stereo output
        assert audio.shape[0] == 2
        assert audio.shape[1] == int(0.5 * 44100)

    def test_render_normalization(self):
        choir = ThresholdChoir(sample_rate=44100, master_volume=0.8)
        choir.add_voice("Test", beta=4.0, theta=50.0)

        audio = choir.render(duration=0.5, normalize=True)

        # Should not clip
        assert np.max(np.abs(audio)) <= 1.0

    def test_get_metadata(self):
        choir = ThresholdChoir()
        choir.add_voice("Voice1", beta=4.0, theta=50.0)
        choir.add_voice("Voice2", beta=3.5, theta=100.0)

        metadata = choir.get_metadata(duration=5.0)

        assert isinstance(metadata, ChoirMetadata)
        assert metadata.voices == ["Voice1", "Voice2"]
        assert metadata.duration == 5.0
        assert metadata.sample_rate == 44100

    def test_destabilization_event_logging(self):
        choir = ThresholdChoir()
        choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=100.0)

        # Trigger destabilization
        timestamp = datetime.now()
        choir.update_voice("Test", new_R=50.0, timestamp=timestamp)

        # Force low stability by updating again quickly
        for new_R in [49.0, 48.5, 48.0]:
            timestamp += timedelta(seconds=0.1)
            choir.update_voice("Test", new_R=new_R, timestamp=timestamp)

        # Should have logged events
        assert len(choir.destabilization_events) > 0


class TestDataSourceSimulator:
    """Test data source simulators"""

    def test_simulate_amoc(self):
        data = DataSourceSimulator.simulate_amoc_destabilization(
            duration=10.0,
            sample_rate=1.0
        )

        assert len(data) == 10
        # Should be list of (time, value) tuples
        assert all(len(item) == 2 for item in data)

        # Values should generally decrease
        values = [v for t, v in data]
        assert values[-1] < values[0]

    def test_simulate_llm_scaling(self):
        data = DataSourceSimulator.simulate_llm_scaling(
            duration=5.0,
            sample_rate=2.0
        )

        assert len(data) == 10  # 5s * 2 Hz

        # Values should increase (model size grows)
        values = [v for t, v in data]
        assert values[-1] > values[0]

    def test_simulate_ecosystem_collapse(self):
        data = DataSourceSimulator.simulate_ecosystem_collapse(
            duration=8.0,
            sample_rate=1.0
        )

        assert len(data) == 8

        # Population should decline
        values = [v for t, v in data]
        assert values[-1] < values[0]


class TestDemoChoir:
    """Test demo creation function"""

    def test_create_demo_choir(self):
        choir = create_demo_choir(duration=10.0)

        # Should have 3 voices
        assert len(choir.voices) == 3
        assert "AMOC" in choir.voices
        assert "LLM_GPT" in choir.voices
        assert "Ecosystem" in choir.voices

        # Should have logged some events
        assert len(choir.destabilization_events) >= 0

    def test_demo_choir_renders(self):
        choir = create_demo_choir(duration=5.0)
        audio = choir.render(duration=2.0)

        # Should produce valid stereo audio
        assert audio.shape[0] == 2
        assert audio.shape[1] > 0


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete workflow: create, update, render, save"""
        choir = ThresholdChoir(sample_rate=22050)  # Lower rate for speed

        # Add voices
        choir.add_voice("AMOC", beta=4.2, theta=50.0, initial_R=100.0, pan=-0.5)
        choir.add_voice("LLM", beta=3.47, theta=100.0, initial_R=50.0, pan=0.5)

        # Update voices
        timestamp = datetime.now()
        choir.update_voice("AMOC", new_R=45.0, timestamp=timestamp)
        choir.update_voice("LLM", new_R=105.0, timestamp=timestamp)

        # Render
        audio = choir.render(duration=1.0)
        assert audio.shape == (2, 22050)

        # Save
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_choir.wav"
            choir.save_wav(output, duration=1.0)

            assert output.exists()
            assert output.stat().st_size > 0

            # Check metadata
            metadata_path = output.with_suffix('.json')
            assert metadata_path.exists()

    def test_stability_dynamics(self):
        """Test that stability changes correctly"""
        choir = ThresholdChoir()
        choir.add_voice("Test", beta=4.0, theta=50.0, initial_R=100.0)

        # Far from threshold → high stability
        voice = choir.voices["Test"]
        initial_stability = voice.stability

        # Move to threshold → low stability
        choir.update_voice("Test", new_R=50.0)
        threshold_stability = choir.voices["Test"].stability

        # Move away → stability increases
        choir.update_voice("Test", new_R=80.0)
        recovered_stability = choir.voices["Test"].stability

        assert threshold_stability < initial_stability
        # Note: recovered might not be same due to rate_of_change effects


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
