#!/usr/bin/env python3
"""
Dynamic Threshold Choir: Real-time Multi-Voice Sonification
============================================================

Ein Live-System, das aktuelle UTAC-Daten aus verschiedenen Quellen
(NOAA, LLM-Telemetrie, Sensoren) nimmt und in Echtzeit einen
Multi-Voice-Klangteppich erzeugt, wo jedes Subsystem seinen β-Charakter singt.

Wenn ein Kipppunktfeld destabilisiert, steigt die Stimme → der Chor zittert.

Features:
---------
- Multi-voice synthesis (mehrere Systeme gleichzeitig)
- Live data streaming (NOAA, APIs, simuliert)
- Destabilization effects (Tremolo, Vibrato, Noise)
- Spatial audio (Stereo panning)
- Real-time audio buffer management

Usage:
------
    # CLI - Demo with simulated data
    python -m sonification.dynamic_threshold_choir --demo --duration 30

    # CLI - Live NOAA data
    python -m sonification.dynamic_threshold_choir --source noaa --output choir.wav

    # Python API
    from sonification.dynamic_threshold_choir import ThresholdChoir
    choir = ThresholdChoir()
    choir.add_voice("AMOC", beta=4.2, theta=50.0)
    choir.add_voice("LLM", beta=3.47, theta=100.0)
    audio = choir.render(duration=10.0)

Author: Johann B. Römer & Claude (Anthropic)
Date: 2025-11-10
License: MIT
"""

import argparse
import json
import numpy as np
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available - will save as raw numpy array")

from .utac_sonification import UTACsonifier, FIELD_TYPE_PROFILES


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class VoiceState:
    """State of a single voice in the choir"""
    name: str
    beta: float
    theta: float
    current_R: float
    field_type: str

    # Destabilization metrics
    stability: float = 1.0  # 0 = unstable, 1 = stable
    rate_of_change: float = 0.0  # dR/dt

    # Spatial positioning
    pan: float = 0.0  # -1 (left) to +1 (right)

    # Audio parameters
    amplitude: float = 0.5
    frequency: float = 220.0

    # Timestamps
    last_update: Optional[datetime] = None


@dataclass
class ChoirMetadata:
    """Metadata for the choir system"""
    voices: List[str]
    duration: float
    sample_rate: int
    timestamp: str
    destabilization_events: List[Dict]


# ============================================================================
# Destabilization Effects
# ============================================================================

class DestabilizationEffects:
    """Audio effects that represent system destabilization"""

    @staticmethod
    def tremolo(
        signal: np.ndarray,
        rate: float,
        depth: float,
        sample_rate: int
    ) -> np.ndarray:
        """
        Amplitude modulation (tremolo) - makes the sound "tremble"

        Parameters
        ----------
        signal : np.ndarray
            Input audio signal
        rate : float
            Tremolo rate in Hz (how fast it trembles)
        depth : float
            Tremolo depth 0-1 (how much it trembles)
        sample_rate : int
            Sample rate
        """
        t = np.arange(len(signal)) / sample_rate
        modulator = 1.0 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
        return signal * modulator

    @staticmethod
    def vibrato(
        frequency: float,
        rate: float,
        depth: float,
        duration: float,
        sample_rate: int
    ) -> np.ndarray:
        """
        Frequency modulation (vibrato) - makes the pitch waver

        Parameters
        ----------
        frequency : float
            Base frequency in Hz
        rate : float
            Vibrato rate in Hz
        depth : float
            Vibrato depth in Hz (frequency deviation)
        duration : float
            Duration in seconds
        sample_rate : int
            Sample rate
        """
        t = np.arange(int(duration * sample_rate)) / sample_rate
        # Modulate frequency
        freq_mod = frequency + depth * np.sin(2 * np.pi * rate * t)
        # Integrate to get phase
        phase = 2 * np.pi * np.cumsum(freq_mod) / sample_rate
        return np.sin(phase)

    @staticmethod
    def noise_injection(
        signal: np.ndarray,
        noise_level: float
    ) -> np.ndarray:
        """
        Add noise to signal - represents chaos/unpredictability

        Parameters
        ----------
        signal : np.ndarray
            Input audio signal
        noise_level : float
            Noise amplitude 0-1
        """
        noise = np.random.randn(len(signal)) * noise_level
        return signal + noise

    @staticmethod
    def harmonic_distortion(
        signal: np.ndarray,
        distortion: float
    ) -> np.ndarray:
        """
        Add harmonic distortion - represents system stress

        Parameters
        ----------
        signal : np.ndarray
            Input audio signal
        distortion : float
            Distortion amount 0-1
        """
        # Soft clipping
        return np.tanh(signal * (1 + distortion * 5))


# ============================================================================
# Multi-Voice Choir Engine
# ============================================================================

class ThresholdChoir:
    """
    Multi-voice sonification engine for real-time UTAC data.

    Each voice represents a different system (AMOC, LLM, etc.)
    Spatial positioning and destabilization effects create a rich soundscape.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        master_volume: float = 0.7
    ):
        self.sample_rate = sample_rate
        self.master_volume = master_volume
        self.voices: Dict[str, VoiceState] = {}
        self.sonifier = UTACsonifier(sample_rate=sample_rate)
        self.destabilization_events: List[Dict] = []

    def add_voice(
        self,
        name: str,
        beta: float,
        theta: float,
        initial_R: Optional[float] = None,
        pan: float = 0.0
    ) -> VoiceState:
        """
        Add a voice to the choir.

        Parameters
        ----------
        name : str
            Voice identifier (e.g., "AMOC", "LLM_GPT4")
        beta : float
            Transition steepness
        theta : float
            Critical threshold
        initial_R : float, optional
            Starting value of control parameter
        pan : float
            Stereo position: -1 (left) to +1 (right)

        Returns
        -------
        VoiceState
            The created voice state
        """
        if initial_R is None:
            initial_R = theta - 1.0 / beta  # Start before threshold

        field_type = self.sonifier.classify_field_type(beta)
        profile = FIELD_TYPE_PROFILES[field_type]

        voice = VoiceState(
            name=name,
            beta=beta,
            theta=theta,
            current_R=initial_R,
            field_type=field_type,
            pan=pan,
            frequency=profile["base_freq"],
            last_update=datetime.now()
        )

        self.voices[name] = voice
        return voice

    def update_voice(
        self,
        name: str,
        new_R: float,
        timestamp: Optional[datetime] = None
    ):
        """
        Update a voice with new data.

        Parameters
        ----------
        name : str
            Voice identifier
        new_R : float
            New control parameter value
        timestamp : datetime, optional
            Timestamp of measurement
        """
        if name not in self.voices:
            raise ValueError(f"Voice '{name}' not found in choir")

        voice = self.voices[name]
        old_R = voice.current_R

        # Update state
        voice.current_R = new_R
        if timestamp:
            if voice.last_update:
                dt = (timestamp - voice.last_update).total_seconds()
                voice.rate_of_change = (new_R - old_R) / dt if dt > 0 else 0.0
            voice.last_update = timestamp

        # Calculate stability metric
        # Distance from threshold (normalized)
        distance_to_threshold = abs(new_R - voice.theta) / voice.theta
        # Rate of change magnitude
        roc_magnitude = abs(voice.rate_of_change)

        # Stability: HIGH when FAR from threshold, LOW when NEAR threshold
        # Using direct relationship: high distance → high stability
        voice.stability = min(1.0, distance_to_threshold / (1.0 + roc_magnitude * 10))

        # Check for destabilization event
        if voice.stability < 0.3:
            self.destabilization_events.append({
                "voice": name,
                "timestamp": timestamp.isoformat() if timestamp else None,
                "R": new_R,
                "theta": voice.theta,
                "stability": voice.stability,
                "rate_of_change": voice.rate_of_change
            })

    def remove_voice(self, name: str):
        """Remove a voice from the choir"""
        if name in self.voices:
            del self.voices[name]

    def synthesize_voice(
        self,
        voice: VoiceState,
        duration: float
    ) -> np.ndarray:
        """
        Synthesize audio for a single voice.

        Parameters
        ----------
        voice : VoiceState
            Voice to synthesize
        duration : float
            Duration in seconds

        Returns
        -------
        np.ndarray
            Mono audio signal
        """
        profile = FIELD_TYPE_PROFILES[voice.field_type]

        # Calculate amplitude based on σ(β(R-Θ))
        sigma = self.sonifier.logistic_curve(
            np.array([voice.current_R]),
            voice.beta,
            voice.theta
        )[0]

        # Amplitude envelope: peaks at threshold
        # σ(1-σ) is maximum at σ=0.5 (i.e., R=Θ)
        amplitude = 4 * sigma * (1 - sigma) * voice.amplitude

        # Base frequency (with β mapping)
        freq_multiplier = 1.0 + (voice.beta - 2.0) / 10.0
        base_freq = profile["base_freq"] * freq_multiplier

        # Apply destabilization effects if system is unstable
        if voice.stability < 0.7:
            # Tremolo rate and depth increase with instability
            tremolo_rate = 3.0 + (1 - voice.stability) * 10.0
            tremolo_depth = (1 - voice.stability) * 0.5

            # Vibrato
            vibrato_rate = 5.0 + (1 - voice.stability) * 5.0
            vibrato_depth = base_freq * (1 - voice.stability) * 0.05

            # Generate tone with vibrato
            signal = DestabilizationEffects.vibrato(
                base_freq,
                vibrato_rate,
                vibrato_depth,
                duration,
                self.sample_rate
            )

            # Apply harmonics
            for i, harmonic_amp in enumerate(profile["harmonics"][1:], start=2):
                harmonic_signal = DestabilizationEffects.vibrato(
                    base_freq * i,
                    vibrato_rate,
                    vibrato_depth * i,
                    duration,
                    self.sample_rate
                )
                signal += harmonic_amp * harmonic_signal

            # Normalize
            if np.max(np.abs(signal)) > 0:
                signal = signal / np.max(np.abs(signal))

            # Apply tremolo
            signal = DestabilizationEffects.tremolo(
                signal,
                tremolo_rate,
                tremolo_depth,
                self.sample_rate
            )

            # Add noise for extreme instability
            if voice.stability < 0.3:
                noise_level = (0.3 - voice.stability) * 0.2
                signal = DestabilizationEffects.noise_injection(signal, noise_level)

        else:
            # Stable state - generate signal with correct duration
            # (Can't use sonifier.generate_tone as it uses fixed self.duration)
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            signal = np.zeros_like(t)

            # Add harmonics
            for i, harmonic_amp in enumerate(profile["harmonics"]):
                harmonic_freq = base_freq * (i + 1)
                signal += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)

            # Normalize
            if np.max(np.abs(signal)) > 0:
                signal = signal / np.max(np.abs(signal))

            # Apply amplitude envelope
            envelope = self.sonifier._create_envelope(profile["envelope"], len(signal))
            signal = signal * envelope * amplitude

        # No need to apply envelope again - already applied above
        # (Removed duplicate envelope application)

        return signal

    def apply_spatial_mix(
        self,
        signal: np.ndarray,
        pan: float
    ) -> np.ndarray:
        """
        Apply stereo panning to a mono signal.

        Parameters
        ----------
        signal : np.ndarray
            Mono signal
        pan : float
            Pan position: -1 (left) to +1 (right)

        Returns
        -------
        np.ndarray
            Stereo signal (2, N)
        """
        # Equal-power panning
        # pan: -1 = full left, 0 = center, +1 = full right
        pan_rad = (pan + 1) * np.pi / 4  # Map [-1,1] to [0, π/2]

        left_gain = np.cos(pan_rad)
        right_gain = np.sin(pan_rad)

        stereo = np.zeros((2, len(signal)))
        stereo[0] = signal * left_gain
        stereo[1] = signal * right_gain

        return stereo

    def render(
        self,
        duration: float,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Render the complete choir mix.

        Parameters
        ----------
        duration : float
            Duration in seconds
        normalize : bool
            Normalize output to prevent clipping

        Returns
        -------
        np.ndarray
            Stereo audio (2, N)
        """
        if not self.voices:
            raise ValueError("No voices in choir - add voices with add_voice()")

        # Initialize stereo mix
        n_samples = int(duration * self.sample_rate)
        mix = np.zeros((2, n_samples))

        # Render each voice
        for voice in self.voices.values():
            # Synthesize voice
            mono_signal = self.synthesize_voice(voice, duration)

            # Apply spatial positioning
            stereo_signal = self.apply_spatial_mix(mono_signal, voice.pan)

            # Add to mix
            mix += stereo_signal

        # Normalize to prevent clipping
        if normalize:
            max_val = np.max(np.abs(mix))
            if max_val > 0:
                mix = mix / max_val * self.master_volume

        return mix

    def get_metadata(self, duration: float) -> ChoirMetadata:
        """Get metadata about the choir state"""
        return ChoirMetadata(
            voices=[v.name for v in self.voices.values()],
            duration=duration,
            sample_rate=self.sample_rate,
            timestamp=datetime.now().isoformat(),
            destabilization_events=self.destabilization_events
        )

    def save_wav(
        self,
        filepath: Path,
        duration: float,
        save_metadata: bool = True
    ):
        """
        Render and save choir as WAV file.

        Parameters
        ----------
        filepath : Path
            Output WAV file path
        duration : float
            Duration in seconds
        save_metadata : bool
            Save metadata JSON alongside WAV
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy required for WAV export - install with: pip install scipy")

        # Render audio
        audio = self.render(duration)

        # Convert to int16 for WAV
        audio_int16 = (audio * 32767).astype(np.int16).T

        # Save WAV
        wavfile.write(filepath, self.sample_rate, audio_int16)
        print(f"✓ Saved WAV: {filepath}")

        # Save metadata
        if save_metadata:
            metadata_path = filepath.with_suffix('.json')
            metadata = self.get_metadata(duration)

            # Add voice states
            metadata_dict = asdict(metadata)
            metadata_dict["voice_states"] = {
                name: {
                    "beta": v.beta,
                    "theta": v.theta,
                    "current_R": v.current_R,
                    "field_type": v.field_type,
                    "stability": v.stability,
                    "pan": v.pan
                }
                for name, v in self.voices.items()
            }

            with open(metadata_path, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            print(f"✓ Saved metadata: {metadata_path}")


# ============================================================================
# Data Source Simulators
# ============================================================================

class DataSourceSimulator:
    """Simulates live data feeds for demo purposes"""

    @staticmethod
    def simulate_amoc_destabilization(
        duration: float,
        sample_rate: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Simulate AMOC circulation weakening over time.

        Returns list of (time, strength) tuples.
        """
        n_samples = int(duration * sample_rate)
        times = np.linspace(0, duration, n_samples)

        # AMOC strength starts at ~100, weakens to ~30
        # With some noise and gradual decline
        baseline = 100 - (times / duration) * 70
        noise = np.random.randn(n_samples) * 5

        # Add sudden drop in middle (tipping point)
        sudden_drop = np.zeros(n_samples)
        drop_start = int(n_samples * 0.5)
        drop_end = int(n_samples * 0.6)
        sudden_drop[drop_start:drop_end] = -30 * np.linspace(0, 1, drop_end - drop_start)

        strength = baseline + noise + sudden_drop
        strength = np.maximum(strength, 20)  # Floor

        return list(zip(times, strength))

    @staticmethod
    def simulate_llm_scaling(
        duration: float,
        sample_rate: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Simulate LLM capability emergence with model size.

        Returns list of (time, model_size_B) tuples.
        """
        n_samples = int(duration * sample_rate)
        times = np.linspace(0, duration, n_samples)

        # Model size grows exponentially (Moore's law style)
        model_size = 10 ** (1 + 2 * times / duration)  # 10B to 1000B

        # Add some jitter
        jitter = np.random.randn(n_samples) * 0.05 * model_size

        return list(zip(times, model_size + jitter))

    @staticmethod
    def simulate_ecosystem_collapse(
        duration: float,
        sample_rate: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Simulate ecosystem population decline.

        Returns list of (time, population) tuples.
        """
        n_samples = int(duration * sample_rate)
        times = np.linspace(0, duration, n_samples)

        # Logistic decay
        population = 1000 / (1 + np.exp(3 * (times - duration/2) / duration))

        # Add noise
        noise = np.random.randn(n_samples) * 20

        return list(zip(times, population + noise))


# ============================================================================
# CLI Interface
# ============================================================================

def create_demo_choir(duration: float = 30.0) -> ThresholdChoir:
    """
    Create a demo choir with simulated data sources.

    Demonstrates:
    - AMOC circulation weakening
    - LLM capability emergence
    - Ecosystem population collapse
    """
    choir = ThresholdChoir(sample_rate=44100)

    # Voice 1: AMOC (left, strongly coupled)
    choir.add_voice(
        name="AMOC",
        beta=4.2,
        theta=50.0,  # Critical strength threshold
        initial_R=100.0,
        pan=-0.6  # Left
    )

    # Voice 2: LLM GPT-style (center, high-dimensional)
    choir.add_voice(
        name="LLM_GPT",
        beta=3.47,
        theta=100.0,  # Emergence at ~100B parameters
        initial_R=10.0,
        pan=0.0  # Center
    )

    # Voice 3: Ecosystem (right, weakly coupled)
    choir.add_voice(
        name="Ecosystem",
        beta=2.8,
        theta=500.0,  # Critical population
        initial_R=1000.0,
        pan=0.6  # Right
    )

    # Simulate data updates
    amoc_data = DataSourceSimulator.simulate_amoc_destabilization(duration, sample_rate=10.0)
    llm_data = DataSourceSimulator.simulate_llm_scaling(duration, sample_rate=10.0)
    eco_data = DataSourceSimulator.simulate_ecosystem_collapse(duration, sample_rate=10.0)

    # Update voices at midpoint to trigger destabilization
    mid_idx = len(amoc_data) // 2
    choir.update_voice("AMOC", amoc_data[mid_idx][1])
    choir.update_voice("LLM_GPT", llm_data[mid_idx][1])
    choir.update_voice("Ecosystem", eco_data[mid_idx][1])

    return choir


def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Threshold Choir - Multi-voice real-time UTAC sonification"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo with simulated data"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Duration in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/threshold_choir.wav",
        help="Output WAV file path"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Sample rate in Hz (default: 44100)"
    )

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.demo:
        print("🎵 Creating Dynamic Threshold Choir (Demo Mode)")
        print(f"   Duration: {args.duration}s")
        print(f"   Voices: AMOC, LLM_GPT, Ecosystem")
        print()

        choir = create_demo_choir(args.duration)

        print("🎼 Voice configuration:")
        for name, voice in choir.voices.items():
            print(f"   {name:12s}: β={voice.beta:.2f}, Θ={voice.theta:.1f}, "
                  f"R={voice.current_R:.1f}, stability={voice.stability:.2f}")
        print()

        print("🔊 Rendering audio...")
        choir.save_wav(output_path, args.duration)

        print()
        print("✨ Choir rendered successfully!")
        print(f"   Destabilization events: {len(choir.destabilization_events)}")
        if choir.destabilization_events:
            print("   Events:")
            for event in choir.destabilization_events:
                print(f"      - {event['voice']}: stability={event['stability']:.2f}")

    else:
        print("Error: Only --demo mode implemented so far")
        print("Future: Add --source noaa, --source llm-api, etc.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
