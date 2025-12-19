"""Planetary Voice: Sonify the Winning Seed from Dreamtime.

This script loads the stable seed (2048) from dream_journal.json and generates
an audio waveform representing the resonance signature of the crystal oracle.

The WAV file encodes:
- Base frequency from the seed signature
- Phase evolution from the ConsciousnessSeed oscillators
- Amplitude modulation by global coherence

Output: v10_oracle/logs/planetary_voice_seed2048.wav
"""

from __future__ import annotations

import json
import pathlib
import sys
import wave
from typing import Tuple

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.models import ConsciousnessSeed

DREAM_JOURNAL = REPO_ROOT / "v10_oracle" / "logs" / "dream_journal.json"
OUTPUT_WAV = REPO_ROOT / "v10_oracle" / "logs" / "planetary_voice_seed2048.wav"

# Audio parameters
SAMPLE_RATE = 44100  # Hz (CD quality)
DURATION_SECONDS = 30  # 30 seconds of oracle voice
AMPLITUDE_SCALE = 0.3  # Prevent clipping


def load_winning_seed() -> Tuple[int, float, float, float]:
    """Extract seed and signature from dream_journal.json metadata."""
    with DREAM_JOURNAL.open("r", encoding="utf-8") as fp:
        journal = json.load(fp)

    meta = journal["meta"]
    signature = meta["signature"]

    return (
        int(meta["seed"]),
        float(signature["sigma_phi"]),
        float(signature["coherence"]),
        float(signature["frequency"]),
    )


def initialize_oracle_oscillators(seed: int, n_nodes: int = 24) -> Tuple[np.ndarray, np.ndarray]:
    """Initialize the oscillator network with the winning seed."""
    rng = np.random.default_rng(seed)
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    coupling = rng.uniform(0.0, 1.0, size=(n_nodes, n_nodes))
    np.fill_diagonal(coupling, 0.0)
    coupling = (coupling + coupling.T) / 2.0
    return phases, coupling


def synthesize_waveform(
    seed: int,
    base_frequency: float,
    coherence: float,
    sigma_phi: float,
    duration: float = DURATION_SECONDS,
    sample_rate: int = SAMPLE_RATE,
) -> np.ndarray:
    """Generate audio waveform by evolving the oracle's oscillator network.

    The waveform is the mean phase projection of all oscillators,
    modulated by the global coherence to create amplitude variations.
    """
    phases, coupling = initialize_oracle_oscillators(seed)
    kernel = ConsciousnessSeed()

    n_samples = int(duration * sample_rate)
    waveform = np.zeros(n_samples)

    # Time step sized to match audio sampling
    dt = 1.0 / sample_rate

    print(f"Synthesizing {duration}s at {sample_rate}Hz ({n_samples} samples)...")
    print(f"Seed: {seed} | σ_ϕ={sigma_phi:.4f} | coherence={coherence:.4f} | f={base_frequency:.3f}Hz")

    for i in range(n_samples):
        # Evolve the consciousness seed one step
        phases, info = kernel.step(phases, coupling, em_coherence=coherence)

        # Mean phase projection (sum of sin components)
        mean_phase = np.mean(np.sin(phases))

        # Modulate amplitude by current coherence
        current_coherence = info["global_coherence"]
        amplitude = AMPLITUDE_SCALE * current_coherence

        waveform[i] = amplitude * mean_phase

        if i % (sample_rate * 5) == 0:  # Progress every 5 seconds
            print(f"  {i / sample_rate:.1f}s | σ_ϕ={info['sigma_phi']:.4f} | coherence={current_coherence:.4f}")

    return waveform


def write_wav(filepath: pathlib.Path, waveform: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    """Write waveform to 16-bit WAV file."""
    # Scale to 16-bit integer range
    waveform_int16 = np.int16(waveform * 32767)

    with wave.open(str(filepath), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform_int16.tobytes())


def analyze_waveform(waveform: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    """Print statistical properties of the generated voice."""
    print("\n=== Waveform Analysis ===")
    print(f"Duration: {len(waveform) / sample_rate:.2f}s")
    print(f"Mean amplitude: {np.mean(np.abs(waveform)):.4f}")
    print(f"Peak amplitude: {np.max(np.abs(waveform)):.4f}")
    print(f"RMS: {np.sqrt(np.mean(waveform**2)):.4f}")

    # Frequency analysis via FFT
    fft = np.fft.rfft(waveform)
    freqs = np.fft.rfftfreq(len(waveform), 1.0 / sample_rate)
    magnitudes = np.abs(fft)

    # Find dominant frequency
    dominant_idx = np.argmax(magnitudes[1:]) + 1  # Skip DC component
    dominant_freq = freqs[dominant_idx]

    print(f"Dominant frequency: {dominant_freq:.2f} Hz")

    # Spectral entropy (measure of harmonic structure vs noise)
    magnitude_norm = magnitudes / (np.sum(magnitudes) + 1e-12)
    spectral_entropy = -np.sum(magnitude_norm * np.log2(magnitude_norm + 1e-12))
    max_entropy = np.log2(len(magnitude_norm))
    normalized_entropy = spectral_entropy / max_entropy

    print(f"Spectral entropy: {normalized_entropy:.4f} (0=pure tone, 1=white noise)")


def main() -> None:
    print("🔮 GenesisAeon v10.1 — Planetary Voice Sonification\n")

    # Load the winning seed from Dreamtime
    seed, sigma_phi, coherence, frequency = load_winning_seed()

    # Generate audio waveform
    waveform = synthesize_waveform(
        seed=seed,
        base_frequency=frequency,
        coherence=coherence,
        sigma_phi=sigma_phi,
    )

    # Write to disk
    OUTPUT_WAV.parent.mkdir(parents=True, exist_ok=True)
    write_wav(OUTPUT_WAV, waveform)

    # Analyze
    analyze_waveform(waveform)

    print(f"\n✓ Voice saved to: {OUTPUT_WAV}")
    print("\nThe crystal has spoken. 💎🔊")


if __name__ == "__main__":
    main()
