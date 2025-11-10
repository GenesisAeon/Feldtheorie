#!/usr/bin/env python3
"""
UTAC Sonification: The Sound of Criticality
============================================

Transforms β-spectra and threshold dynamics into audio.
Different Field Types → Different sonic characteristics.

Usage:
    python -m sonification.utac_sonification --preset wei --output sound.wav
    python -m sonification.utac_sonification --beta 4.5 --theta 100 --output transition.wav

Author: Johann B. Römer & Claude (Anthropic)
Date: 2025-11-10
License: MIT
"""

import argparse
import json
import numpy as np
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available - will save as raw numpy array")


# ============================================================================
# Field Type Acoustic Profiles
# ============================================================================

FIELD_TYPE_PROFILES = {
    "strongly_coupled": {
        "beta_range": (3.5, 5.0),
        "base_freq": 220.0,  # A3 - warm, resonant
        "harmonics": [1.0, 0.5, 0.25, 0.125],  # Rich harmonics
        "envelope": "sustained",
        "timbre": "warm",
        "description": "Neural networks, AMOC, honeybees"
    },
    "high_dimensional": {
        "beta_range": (3.0, 4.5),
        "base_freq": 329.63,  # E4 - complex, ethereal
        "harmonics": [1.0, 0.7, 0.4, 0.3, 0.2, 0.15],  # Complex overtones
        "envelope": "floating",
        "timbre": "ethereal",
        "description": "LLMs, evolutionary systems"
    },
    "weakly_coupled": {
        "beta_range": (2.0, 3.5),
        "base_freq": 110.0,  # A2 - soft, diffuse
        "harmonics": [1.0, 0.3, 0.1],  # Few harmonics
        "envelope": "gentle",
        "timbre": "soft",
        "description": "Neural plasticity, ecosystems"
    },
    "physically_constrained": {
        "beta_range": (4.5, 6.0),
        "base_freq": 440.0,  # A4 - sharp, precise
        "harmonics": [1.0, 0.2, 0.05],  # Clear fundamental
        "envelope": "percussive",
        "timbre": "sharp",
        "description": "Black holes, earthquakes"
    },
    "meta_adaptive": {
        "beta_range": (2.5, 16.3),  # Variable!
        "base_freq": 261.63,  # C4 - modulating, adaptive
        "harmonics": [1.0, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1],  # Rich modulation
        "envelope": "adaptive",
        "timbre": "morphing",
        "description": "Climate cascades, markets, urban heat"
    }
}


# ============================================================================
# Core Sonification Engine
# ============================================================================

class UTACsonifier:
    """
    Transforms UTAC parameters (β, Θ, R) into audio.

    The sonic metaphor:
    - β (steepness) → Pitch/Frequency (steeper = higher)
    - R-Θ (distance to threshold) → Amplitude (closer = louder)
    - Θ (threshold) → Reference pitch
    - ζ(R) (impedance) → Filtering/Damping
    - Field Type → Timbre/Harmonic profile
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        duration: float = 3.0,
        beta_to_freq_scale: float = 100.0
    ):
        self.sample_rate = sample_rate
        self.duration = duration
        self.beta_to_freq_scale = beta_to_freq_scale

    def logistic_curve(
        self,
        R: np.ndarray,
        beta: float,
        theta: float,
        L: float = 1.0
    ) -> np.ndarray:
        """Compute σ(β(R-Θ))"""
        return L / (1.0 + np.exp(-beta * (R - theta)))

    def classify_field_type(self, beta: float) -> str:
        """Classify field type based on β value"""
        for field_type, profile in FIELD_TYPE_PROFILES.items():
            beta_min, beta_max = profile["beta_range"]
            if beta_min <= beta <= beta_max:
                return field_type

        # Fallback for outliers
        if beta > 6.0:
            return "meta_adaptive"  # Like urban heat
        return "weakly_coupled"

    def generate_tone(
        self,
        frequency: float,
        amplitude: float,
        harmonics: List[float],
        envelope_type: str = "sustained"
    ) -> np.ndarray:
        """
        Generate a complex tone with harmonics and envelope.

        Parameters
        ----------
        frequency : float
            Base frequency in Hz
        amplitude : float
            Amplitude (0-1)
        harmonics : List[float]
            Harmonic amplitudes [fundamental, 2nd, 3rd, ...]
        envelope_type : str
            Type of amplitude envelope
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = np.zeros_like(t)

        # Add harmonics
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            signal += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)

        # Normalize
        signal = signal / np.max(np.abs(signal)) if np.max(np.abs(signal)) > 0 else signal

        # Apply envelope
        envelope = self._create_envelope(envelope_type, len(t))
        signal = signal * envelope * amplitude

        return signal

    def _create_envelope(self, envelope_type: str, length: int) -> np.ndarray:
        """Create amplitude envelope"""
        t_norm = np.linspace(0, 1, length)

        if envelope_type == "sustained":
            # ADSR: Attack-Decay-Sustain-Release
            attack = 0.1
            decay = 0.1
            sustain_level = 0.7
            release = 0.2

            envelope = np.ones(length) * sustain_level
            attack_len = int(attack * length)
            decay_len = int(decay * length)
            release_len = int(release * length)

            # Attack
            envelope[:attack_len] = np.linspace(0, 1, attack_len)
            # Decay
            envelope[attack_len:attack_len+decay_len] = np.linspace(1, sustain_level, decay_len)
            # Release
            envelope[-release_len:] = np.linspace(sustain_level, 0, release_len)

        elif envelope_type == "percussive":
            # Sharp attack, exponential decay
            envelope = np.exp(-5 * t_norm)

        elif envelope_type == "gentle":
            # Slow fade in and out
            envelope = np.sin(np.pi * t_norm) ** 2

        elif envelope_type == "floating":
            # Gentle oscillation
            envelope = 0.7 + 0.3 * np.sin(2 * np.pi * t_norm)

        elif envelope_type == "adaptive":
            # Complex modulation
            envelope = 0.5 + 0.3 * np.sin(2 * np.pi * t_norm) + 0.2 * np.sin(5 * np.pi * t_norm)

        else:
            envelope = np.ones(length)

        return envelope

    def sonify_transition(
        self,
        beta: float,
        theta: float,
        R_range: Optional[Tuple[float, float]] = None,
        L: float = 1.0
    ) -> Tuple[np.ndarray, Dict]:
        """
        Sonify a single threshold transition.

        Parameters
        ----------
        beta : float
            Transition steepness
        theta : float
            Critical threshold
        R_range : Tuple[float, float], optional
            Range of control parameter R
        L : float
            Logistic amplitude

        Returns
        -------
        audio : np.ndarray
            Audio signal
        metadata : Dict
            Sonification metadata
        """
        if R_range is None:
            R_range = (theta - 2/beta, theta + 2/beta)

        # Classify field type
        field_type = self.classify_field_type(beta)
        profile = FIELD_TYPE_PROFILES[field_type]

        # β → Frequency mapping
        # Higher β = steeper transition = higher pitch
        freq_multiplier = 1.0 + (beta - 2.0) / 10.0  # Scale β to ~0.8-2.4x
        base_freq = profile["base_freq"] * freq_multiplier

        # R → Time evolution
        R = np.linspace(R_range[0], R_range[1], int(self.sample_rate * self.duration))
        sigma = self.logistic_curve(R, beta, theta, L)

        # σ(β(R-Θ)) → Amplitude modulation
        # As we cross threshold, amplitude peaks
        amplitude = sigma * (1 - sigma) * 4  # Peak at σ=0.5
        amplitude = amplitude / np.max(amplitude)  # Normalize

        # Generate time-varying tone
        t = np.linspace(0, self.duration, len(R))
        signal = np.zeros_like(t)

        # Use harmonics from field type
        for i, harmonic_amp in enumerate(profile["harmonics"]):
            harmonic_freq = base_freq * (i + 1)
            # Frequency modulation based on σ
            freq_mod = harmonic_freq * (1.0 + 0.1 * sigma)  # Slight FM
            phase = 2 * np.pi * np.cumsum(freq_mod) / self.sample_rate
            signal += harmonic_amp * np.sin(phase)

        # Normalize
        signal = signal / np.max(np.abs(signal)) if np.max(np.abs(signal)) > 0 else signal

        # Apply amplitude modulation
        signal = signal * amplitude

        # Apply envelope
        envelope = self._create_envelope(profile["envelope"], len(signal))
        signal = signal * envelope

        # Metadata
        metadata = {
            "beta": beta,
            "theta": theta,
            "R_range": R_range,
            "L": L,
            "field_type": field_type,
            "base_frequency_hz": base_freq,
            "profile": profile["description"],
            "duration_sec": self.duration,
            "sample_rate_hz": self.sample_rate
        }

        return signal, metadata

    def sonify_spectrum(
        self,
        beta_values: List[float],
        theta_values: Optional[List[float]] = None,
        labels: Optional[List[str]] = None,
        gap_duration: float = 0.5
    ) -> Tuple[np.ndarray, Dict]:
        """
        Sonify multiple β values as a sequence.

        Parameters
        ----------
        beta_values : List[float]
            List of β values to sonify
        theta_values : List[float], optional
            Corresponding thresholds
        labels : List[str], optional
            Labels for each transition
        gap_duration : float
            Silence between transitions (seconds)

        Returns
        -------
        audio : np.ndarray
            Combined audio signal
        metadata : Dict
            Sonification metadata
        """
        if theta_values is None:
            theta_values = [100.0] * len(beta_values)

        if labels is None:
            labels = [f"Transition {i+1}" for i in range(len(beta_values))]

        signals = []
        transition_metadata = []

        gap_samples = int(gap_duration * self.sample_rate)
        gap_signal = np.zeros(gap_samples)

        for beta, theta, label in zip(beta_values, theta_values, labels):
            signal, meta = self.sonify_transition(beta, theta)
            meta["label"] = label
            signals.append(signal)
            signals.append(gap_signal)
            transition_metadata.append(meta)

        # Concatenate
        combined = np.concatenate(signals)

        metadata = {
            "n_transitions": len(beta_values),
            "total_duration_sec": len(combined) / self.sample_rate,
            "gap_duration_sec": gap_duration,
            "transitions": transition_metadata
        }

        return combined, metadata


# ============================================================================
# I/O Functions
# ============================================================================

def save_audio(
    audio: np.ndarray,
    filepath: Path,
    sample_rate: int = 44100,
    normalize: bool = True
):
    """Save audio to WAV file"""
    if normalize:
        audio = audio / np.max(np.abs(audio))

    # Convert to int16
    audio_int = (audio * 32767).astype(np.int16)

    if SCIPY_AVAILABLE:
        wavfile.write(str(filepath), sample_rate, audio_int)
        print(f"✓ Audio saved: {filepath}")
    else:
        # Fallback: save as numpy
        np.save(filepath.with_suffix('.npy'), audio)
        print(f"✓ Audio saved as numpy: {filepath.with_suffix('.npy')}")
        print("  Install scipy to save as WAV: pip install scipy")


def save_metadata(metadata: Dict, filepath: Path):
    """Save sonification metadata as JSON"""
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {filepath}")


def load_preset(preset_name: str) -> Dict:
    """Load sonification preset"""
    preset_path = Path(__file__).parent / "presets" / f"{preset_name}.json"

    if not preset_path.exists():
        raise FileNotFoundError(f"Preset not found: {preset_path}")

    with open(preset_path) as f:
        return json.load(f)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="UTAC Sonification: Transform threshold dynamics into audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sonify a single transition
  python -m sonification.utac_sonification --beta 4.5 --theta 100 --output transition.wav

  # Use a preset (e.g., LLM emergence)
  python -m sonification.utac_sonification --preset wei --output llm_emergence.wav

  # Sonify full field type spectrum
  python -m sonification.utac_sonification --preset field_types --output field_spectrum.wav
"""
    )

    parser.add_argument("--preset", help="Load preset configuration")
    parser.add_argument("--beta", type=float, help="β (transition steepness)")
    parser.add_argument("--theta", type=float, default=100.0, help="Θ (threshold)")
    parser.add_argument("--duration", type=float, default=3.0, help="Duration per transition (seconds)")
    parser.add_argument("--output", "-o", required=True, help="Output audio file (.wav)")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Sample rate (Hz)")

    args = parser.parse_args()

    # Initialize sonifier
    sonifier = UTACsonifier(
        sample_rate=args.sample_rate,
        duration=args.duration
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.preset:
        # Load preset
        print(f"🎵 Loading preset: {args.preset}")
        preset = load_preset(args.preset)

        if "beta_values" in preset:
            # Multiple transitions
            audio, metadata = sonifier.sonify_spectrum(
                beta_values=preset["beta_values"],
                theta_values=preset.get("theta_values"),
                labels=preset.get("labels")
            )
        else:
            # Single transition
            audio, metadata = sonifier.sonify_transition(
                beta=preset["beta"],
                theta=preset.get("theta", 100.0)
            )

    elif args.beta is not None:
        # Single transition from CLI args
        print(f"🎵 Sonifying β={args.beta}, Θ={args.theta}")
        audio, metadata = sonifier.sonify_transition(
            beta=args.beta,
            theta=args.theta
        )

    else:
        parser.error("Either --preset or --beta must be specified")

    # Save
    save_audio(audio, output_path, args.sample_rate)
    save_metadata(metadata, output_path.with_suffix('.json'))

    print(f"\n✨ Sonification complete!")
    print(f"   Duration: {len(audio)/args.sample_rate:.2f} seconds")
    if "field_type" in metadata:
        print(f"   Field Type: {metadata['field_type']}")
        print(f"   Profile: {FIELD_TYPE_PROFILES[metadata['field_type']]['description']}")


if __name__ == "__main__":
    main()
