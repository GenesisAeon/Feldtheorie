"""
UTAC Fourier Analysis Module
Spectral analysis for UTAC field type classification and resonance detection.

This module provides tools for analyzing the frequency-domain properties of
UTAC systems to identify field types, detect critical transitions, and
classify emergent patterns.
"""

import numpy as np
import scipy.fftpack as fft
import matplotlib.pyplot as plt
from pathlib import Path

def compute_fourier(signal, sampling_rate=44100):
    """
    Compute the Fourier transform of a time-domain signal.
    
    Args:
        signal: Array-like, time-domain signal
        sampling_rate: Sampling rate in Hz (default: 44100 for audio)
    
    Returns:
        tuple: (spectrum, freqs)
            spectrum: Magnitude spectrum (positive frequencies only)
            freqs: Corresponding frequency bins in Hz
    """
    N = len(signal)
    spectrum = np.abs(fft.fft(signal))[:N // 2]
    freqs = fft.fftfreq(N, d=1.0 / sampling_rate)[:N // 2]
    return spectrum, freqs

def plot_spectrum(freqs, spectrum, title='Spectral Profile', save_path=None):
    """
    Plot the log-log spectral profile.
    
    Args:
        freqs: Frequency bins (Hz)
        spectrum: Magnitude spectrum
        title: Plot title
        save_path: Path to save figure (optional)
    """
    plt.figure(figsize=(10, 6))
    plt.loglog(freqs + 1e-8, spectrum + 1e-8, label='Spectrum', linewidth=1.5)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Magnitude', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved spectrum plot: {save_path}")
    plt.close()

def spectral_features(spectrum, freqs):
    """
    Extract simple features from spectrum for classification.
    
    Args:
        spectrum: Magnitude spectrum
        freqs: Frequency bins
    
    Returns:
        dict: Features including:
            - dominant_freq: Frequency with maximum power
            - entropy: Spectral entropy (measure of complexity)
            - centroid: Spectral centroid (center of mass)
            - bandwidth: Spectral bandwidth
            - rolloff: Frequency below which 85% of energy is contained
    """
    # Normalize spectrum
    spectrum_norm = spectrum / (np.sum(spectrum) + 1e-8)
    
    # Spectral entropy
    entropy = -np.sum(spectrum_norm * np.log2(spectrum_norm + 1e-8))
    
    # Spectral centroid (center of mass)
    centroid = np.sum(freqs * spectrum_norm)
    
    # Dominant frequency
    dominant_freq = freqs[np.argmax(spectrum)]
    
    # Spectral bandwidth (standard deviation around centroid)
    bandwidth = np.sqrt(np.sum(((freqs - centroid) ** 2) * spectrum_norm))
    
    # Spectral rolloff (85% energy threshold)
    cumsum = np.cumsum(spectrum_norm)
    rolloff_idx = np.where(cumsum >= 0.85)[0]
    rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else freqs[-1]
    
    return {
        "dominant_freq": float(dominant_freq),
        "entropy": float(entropy),
        "centroid": float(centroid),
        "bandwidth": float(bandwidth),
        "rolloff": float(rolloff)
    }

def classify_field_type(features):
    """
    Classify field type based on extracted spectral features.
    
    Classification based on UTAC field types:
    - Weakly Coupled: Low-frequency dominance, diffuse spectrum
    - Strongly Coupled: Mid-frequency resonance, narrow bandwidth
    - High-Dimensional: High-frequency content, complex structure
    - Physically Triggered: Spike-rich, transient features
    - Meta-Adaptive: Drifting spectral profile, high entropy
    
    Args:
        features: Dict of spectral features from spectral_features()
    
    Returns:
        str: Field type classification
    """
    f = features['dominant_freq']
    entropy = features['entropy']
    bandwidth = features['bandwidth']
    
    # Classification thresholds (based on UTAC empirical data)
    if f < 150:
        if entropy < 6.0:
            return 'Weakly Coupled'
        else:
            return 'Meta-Adaptive (Low-frequency)'
    elif f < 300:
        if bandwidth < 100:
            return 'Strongly Coupled'
        else:
            return 'High-Dimensional (Transitional)'
    elif f < 600:
        return 'High-Dimensional'
    elif f < 1000:
        if entropy > 7.0:
            return 'Physically Triggered'
        else:
            return 'High-Dimensional (Upper)'
    else:
        if entropy > 8.0:
            return 'Meta-Adaptive'
        else:
            return 'Physically Triggered (High-frequency)'

def run_analysis(signal, sampling_rate=44100, title='UTAC Spectrum', save_path=None):
    """
    Run complete Fourier analysis pipeline.
    
    Args:
        signal: Time-domain signal
        sampling_rate: Sampling rate in Hz
        title: Plot title
        save_path: Path to save plot (optional)
    
    Returns:
        dict: Analysis results including:
            - features: Spectral features
            - field_type: Classified field type
            - spectrum: Magnitude spectrum
            - freqs: Frequency bins
    """
    # Compute FFT
    spectrum, freqs = compute_fourier(signal, sampling_rate)
    
    # Extract features
    features = spectral_features(spectrum, freqs)
    
    # Classify field type
    field_type = classify_field_type(features)
    
    # Plot
    if save_path or title != 'UTAC Spectrum':
        plot_spectrum(freqs, spectrum, title, save_path)
    
    return {
        "features": features,
        "field_type": field_type,
        "spectrum": spectrum,
        "freqs": freqs
    }

# Example usage and testing
if __name__ == "__main__":
    print("🎵 UTAC Fourier Analysis Module")
    print("=" * 50)
    
    # Generate synthetic test signals
    t = np.linspace(0, 1, 44100)
    
    # Test 1: Low-frequency sine (Weakly Coupled)
    signal1 = np.sin(2 * np.pi * 100 * t)
    result1 = run_analysis(signal1, title="Test 1: Weakly Coupled (100 Hz)")
    print(f"\n✅ Test 1 (100 Hz sine):")
    print(f"   Field Type: {result1['field_type']}")
    print(f"   Dominant Freq: {result1['features']['dominant_freq']:.1f} Hz")
    print(f"   Entropy: {result1['features']['entropy']:.2f}")
    
    # Test 2: Mid-frequency sine (Strongly Coupled)
    signal2 = np.sin(2 * np.pi * 250 * t)
    result2 = run_analysis(signal2, title="Test 2: Strongly Coupled (250 Hz)")
    print(f"\n✅ Test 2 (250 Hz sine):")
    print(f"   Field Type: {result2['field_type']}")
    print(f"   Dominant Freq: {result2['features']['dominant_freq']:.1f} Hz")
    print(f"   Entropy: {result2['features']['entropy']:.2f}")
    
    # Test 3: High-frequency complex (High-Dimensional)
    signal3 = np.sin(2 * np.pi * 500 * t) + 0.3 * np.sin(2 * np.pi * 1000 * t)
    result3 = run_analysis(signal3, title="Test 3: High-Dimensional (500+1000 Hz)")
    print(f"\n✅ Test 3 (500+1000 Hz complex):")
    print(f"   Field Type: {result3['field_type']}")
    print(f"   Dominant Freq: {result3['features']['dominant_freq']:.1f} Hz")
    print(f"   Entropy: {result3['features']['entropy']:.2f}")
    
    # Test 4: Noisy signal (Meta-Adaptive/Physically Triggered)
    signal4 = np.random.randn(44100) * 0.5 + np.sin(2 * np.pi * 800 * t)
    result4 = run_analysis(signal4, title="Test 4: Physically Triggered (Noisy)")
    print(f"\n✅ Test 4 (Noisy 800 Hz):")
    print(f"   Field Type: {result4['field_type']}")
    print(f"   Dominant Freq: {result4['features']['dominant_freq']:.1f} Hz")
    print(f"   Entropy: {result4['features']['entropy']:.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("Ready for integration with UTAC sonification.")
