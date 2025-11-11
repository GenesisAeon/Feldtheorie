"""
UTAC Fourier Analysis Module

Spektralanalyse für UTAC Zeitreihen - Frequenzdomäne
Analysiert β-Spektren, Field Type Signaturen und Kritikalitätsmuster

Author: Aeon (konzeptionell), Johann Römer
Source: seed/NextVersionPlan/Letzte_Zusätze_bis_V2.txt (Lines 269-352)
Date: 2025-11-11
"""

import numpy as np
import scipy.fftpack as fft
import matplotlib.pyplot as plt


def compute_fourier(signal, sampling_rate=44100):
    """
    Compute the Fourier transform of a time-domain signal.
    Returns magnitude spectrum and corresponding frequency bins.

    Parameters
    ----------
    signal : array_like
        Time-domain signal
    sampling_rate : float, optional
        Sampling rate in Hz (default: 44100)

    Returns
    -------
    spectrum : ndarray
        Magnitude spectrum (positive frequencies only)
    freqs : ndarray
        Frequency bins in Hz
    """
    N = len(signal)
    spectrum = np.abs(fft.fft(signal))[:N // 2]
    freqs = fft.fftfreq(N, d=1.0 / sampling_rate)[:N // 2]
    return spectrum, freqs


def plot_spectrum(freqs, spectrum, title='Spectral Profile', save_path=None):
    """
    Plot the log-log spectral profile.

    Parameters
    ----------
    freqs : ndarray
        Frequency bins in Hz
    spectrum : ndarray
        Magnitude spectrum
    title : str, optional
        Plot title
    save_path : str, optional
        Path to save the figure (if None, display only)
    """
    plt.figure(figsize=(10, 6))
    plt.loglog(freqs + 1e-8, spectrum + 1e-8, label='Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title(title)
    plt.grid(True, which='both', linestyle='--')
    plt.legend()

    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def spectral_features(spectrum, freqs):
    """
    Extract simple features from spectrum.
    Returns dominant frequency, spectral entropy, and spectral centroid.

    Parameters
    ----------
    spectrum : ndarray
        Magnitude spectrum
    freqs : ndarray
        Frequency bins in Hz

    Returns
    -------
    features : dict
        Dictionary with keys:
        - dominant_freq: Frequency with maximum power
        - entropy: Spectral entropy (bits)
        - centroid: Spectral centroid (Hz)
    """
    spectrum_norm = spectrum / (np.sum(spectrum) + 1e-8)

    # Spectral entropy
    entropy = -np.sum(spectrum_norm * np.log2(spectrum_norm + 1e-8))

    # Spectral centroid
    centroid = np.sum(freqs * spectrum_norm)

    # Dominant frequency
    dominant_freq = freqs[np.argmax(spectrum)]

    return {
        "dominant_freq": dominant_freq,
        "entropy": entropy,
        "centroid": centroid
    }


def classify_field_type(features):
    """
    Classify field type based on extracted spectral features.
    Returns a simple string label.

    UTAC Field Type Frequency Mapping:
    - Weakly Coupled: < 150 Hz (sanft, diffus)
    - Strongly Coupled: 150-300 Hz (warm, resonant)
    - High-Dimensional: 300-600 Hz (ätherisch, komplex)
    - Physically Constrained: 600-1000 Hz (scharf, präzise)
    - Meta-Adaptive: > 1000 Hz (morphing, adaptiv)

    Parameters
    ----------
    features : dict
        Spectral features from spectral_features()

    Returns
    -------
    field_type : str
        Field type classification
    """
    f = features['dominant_freq']

    if f < 150:
        return 'Weakly Coupled'
    elif f < 300:
        return 'Strongly Coupled'
    elif f < 600:
        return 'High-Dimensional'
    elif f < 1000:
        return 'Physically Constrained'
    else:
        return 'Meta-Adaptive'


def run_analysis(signal, sampling_rate=44100, title='UTAC Spectrum', save_path=None):
    """
    Run complete Fourier analysis on a signal.

    Parameters
    ----------
    signal : array_like
        Time-domain signal
    sampling_rate : float, optional
        Sampling rate in Hz
    title : str, optional
        Plot title
    save_path : str, optional
        Path to save the figure

    Returns
    -------
    results : dict
        Dictionary containing:
        - features: Spectral features (dict)
        - field_type: Classified field type (str)
        - spectrum: Magnitude spectrum (ndarray)
        - freqs: Frequency bins (ndarray)
    """
    # Compute spectrum
    spectrum, freqs = compute_fourier(signal, sampling_rate)

    # Extract features
    features = spectral_features(spectrum, freqs)

    # Classify field type
    field_type = classify_field_type(features)

    # Plot
    plot_spectrum(freqs, spectrum, title, save_path)

    return {
        "features": features,
        "field_type": field_type,
        "spectrum": spectrum,
        "freqs": freqs
    }


# Example usage
if __name__ == "__main__":
    # Generate example signal: Composite of multiple frequencies
    t = np.linspace(0, 1, 44100)  # 1 second at 44.1 kHz
    signal = (np.sin(2 * np.pi * 220 * t) +  # A3 (Strongly Coupled)
              0.5 * np.sin(2 * np.pi * 440 * t) +  # A4 (Physically Constrained)
              0.3 * np.sin(2 * np.pi * 880 * t))   # A5 (Meta-Adaptive)

    # Run analysis
    results = run_analysis(signal, title='Example UTAC Spectrum')

    print("\n=== UTAC Fourier Analysis Results ===")
    print(f"Field Type: {results['field_type']}")
    print(f"Dominant Frequency: {results['features']['dominant_freq']:.2f} Hz")
    print(f"Spectral Centroid: {results['features']['centroid']:.2f} Hz")
    print(f"Spectral Entropy: {results['features']['entropy']:.2f} bits")
