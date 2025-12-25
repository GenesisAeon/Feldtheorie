# UTAC Fourier Analysis Guide

**Spectrotemporal Depth Mapping of Emergent Fields**

Version: 1.0  
Author: Johann Römer & Aeon  
Date: December 2024

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Theory](#theory)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [API Reference](#api-reference)
6. [Use Cases](#use-cases)
7. [Field Type Classification](#field-type-classification)
8. [Examples](#examples)

---

## Overview

The UTAC Fourier Analysis module provides spectral decomposition tools for emergent field dynamics. It enables:

- **System Classification**: Identify field types by spectral signatures
- **Criticality Prediction**: Detect approaching transitions via frequency shifts
- **Sonification Integration**: Map spectral features to audio parameters
- **Agent Control**: Spectral features as input for CREP modules

### Why Fourier Analysis for UTAC?

Emergent field dynamics are often frequency-encoded:
- β-oscillations in neural systems
- Climate feedback loops with characteristic timescales
- Resonance patterns in coupled systems
- Critical slowing down → spectral reddening

---

## Theory

### Mathematical Foundation

For a time-domain signal $f(t)$ representing UTAC dynamics (e.g., $\beta(t)$, $R(t)$, or $\sigma(\beta(R-\Theta))(t)$), the Fourier transform is:

$$
\mathcal{F}[f(t)](\omega) = \int_{-\infty}^{\infty} f(t)e^{-i\omega t}dt
$$

The **magnitude spectrum** $|F(\omega)|$ reveals:
- **Dominant frequencies**: Peak locations
- **Spectral complexity**: Entropy and spread
- **Power-law scaling**: $1/f^\alpha$ noise (pink/red)
- **Harmonic structure**: Resonance peaks

### Critical Phenomena in Frequency Space

Near critical transitions:
- **Critical slowing down** → Energy shifts to low frequencies
- **Variance increase** → Broader spectrum
- **Loss of resilience** → Spectral reddening ($1/f^2$)

---

## Installation

### Requirements

```bash
pip install numpy scipy matplotlib
```

Optional (for enhanced features):
```bash
pip install pandas seaborn
```

### Import Module

```python
from sonification import utac_fourier
```

---

## Quick Start

### Basic Analysis

```python
import numpy as np
from sonification import utac_fourier

# Generate synthetic UTAC signal
t = np.linspace(0, 1, 44100)  # 1 second at 44.1 kHz
beta = 4.2
theta = 0.5
R = t
signal = 1 / (1 + np.exp(-beta * (R - theta)))

# Run analysis
results = utac_fourier.run_analysis(
    signal,
    sampling_rate=44100,
    title="UTAC Demo",
    save_path="output/spectrum.png"
)

# Access results
print(f"Field Type: {results['field_type']}")
print(f"Dominant Frequency: {results['features']['dominant_freq']:.2f} Hz")
print(f"Spectral Entropy: {results['features']['entropy']:.2f}")
```

---

## API Reference

### Core Functions

#### `compute_fourier(signal, sampling_rate=44100)`

Compute FFT of time-domain signal.

**Parameters:**
- `signal` (array-like): Time-domain signal
- `sampling_rate` (int): Sampling frequency in Hz

**Returns:**
- `spectrum` (ndarray): Magnitude spectrum
- `freqs` (ndarray): Frequency bins

---

#### `spectral_features(spectrum, freqs)`

Extract features for classification.

**Returns dict with:**
- `dominant_freq`: Peak frequency (Hz)
- `entropy`: Spectral entropy (bits)
- `centroid`: Spectral centroid (Hz)
- `bandwidth`: Standard deviation around centroid
- `rolloff`: 85% energy threshold frequency

---

#### `classify_field_type(features)`

Classify UTAC field type from spectral features.

**Returns:**
- String: Field type label (see below)

---

#### `run_analysis(signal, sampling_rate, title, save_path)`

End-to-end analysis pipeline.

**Returns dict with:**
- `features`: Spectral features dict
- `field_type`: Classification label
- `spectrum`: Full spectrum array
- `freqs`: Frequency bins array

---

## Field Type Classification

### Classification Scheme

| Field Type | Frequency Range | Spectral Characteristics |
|------------|----------------|--------------------------|
| **Weakly Coupled** | < 150 Hz | Diffuse, low-pass, high entropy |
| **Strongly Coupled** | 150-300 Hz | Resonant peaks, narrow bandwidth |
| **High-Dimensional** | 300-600 Hz | Multimodal, complex structure |
| **Physically Triggered** | 600-1000 Hz | Spike-rich, transient features |
| **Meta-Adaptive** | > 1000 Hz | Drifting, high entropy, modulating |

### Physical Interpretation

**Weakly Coupled (< 150 Hz):**
- Slow dynamics, diffusive processes
- Examples: Ecosystem succession, gradual climate shifts
- Intervention: Possible with long lead times

**Strongly Coupled (150-300 Hz):**
- Resonant feedback loops
- Examples: AMOC circulation, neural oscillations
- Intervention: Target specific resonances

**High-Dimensional (300-600 Hz):**
- Complex multi-scale interactions
- Examples: LLM activations, cognitive processes
- Intervention: Multi-level approaches needed

**Physically Triggered (600-1000 Hz):**
- Fast transients, threshold crossings
- Examples: Urban heat cascades, flash floods
- Intervention: Rapid response required

**Meta-Adaptive (> 1000 Hz):**
- Self-modifying dynamics
- Examples: AI meta-learning, evolutionary adaptation
- Intervention: Co-evolutionary strategies

---

## Use Cases

### 1. Climate System Analysis

```python
# Load climate time series
temperature = load_temperature_data("arctic_temp.csv")

# Analyze spectral evolution
results = utac_fourier.run_analysis(temperature)

if results['field_type'] == 'Physically Triggered':
    print("⚠️ Warning: Approaching rapid transition!")
```

### 2. Neural Field Classification

```python
# EEG data from meditation vs. stress
eeg_data = load_eeg_channel("Fz")

results = utac_fourier.run_analysis(eeg_data, sampling_rate=256)

# α-band (8-13 Hz) = meditative (Weakly Coupled)
# β-band (13-30 Hz) = alert (Strongly Coupled)
# γ-band (30-100 Hz) = cognitive load (High-Dimensional)
```

### 3. LLM Activation Monitoring

```python
# Track LLM layer activations
activations = model.get_layer_activations(layer=12)

spectrum, freqs = utac_fourier.compute_fourier(activations)
features = utac_fourier.spectral_features(spectrum, freqs)

if features['entropy'] > 8.0:
    print("High entropy → Model uncertainty")
```

### 4. Sonification Integration

```python
# Generate audio from field dynamics
signal = generate_field_signal(beta=6.2, theta=100)

results = utac_fourier.run_analysis(signal)

# Map spectral features to audio
pitch = features['centroid'] / 10  # Scale to audible range
volume = features['dominant_freq'] / 1000
timbre = features['entropy'] / 10  # Brightness
```

---

## Examples

### Example 1: Synthetic Sigmoid

```python
import numpy as np
from sonification import utac_fourier

# UTAC sigmoid transition
t = np.linspace(0, 1, 44100)
beta = 4.2
theta = 0.5
signal = 1 / (1 + np.exp(-beta * (t - theta)))

results = utac_fourier.run_analysis(signal, title="Sigmoid Transition")
```

### Example 2: Multi-Component Signal

```python
# Composite signal: base + harmonics
t = np.linspace(0, 1, 44100)
base = np.sin(2 * np.pi * 220 * t)  # A3
harm1 = 0.5 * np.sin(2 * np.pi * 440 * t)  # A4
harm2 = 0.25 * np.sin(2 * np.pi * 880 * t)  # A5

signal = base + harm1 + harm2

results = utac_fourier.run_analysis(signal, title="Harmonic Structure")
print(f"Centroid: {results['features']['centroid']:.1f} Hz")  # ~370 Hz
```

### Example 3: Noise Analysis

```python
# Pink noise (1/f) vs. White noise
white_noise = np.random.randn(44100)
pink_noise = generate_pink_noise(44100)  # Custom function

results_white = utac_fourier.run_analysis(white_noise, title="White Noise")
results_pink = utac_fourier.run_analysis(pink_noise, title="Pink Noise")

print(f"White entropy: {results_white['features']['entropy']:.2f}")
print(f"Pink entropy: {results_pink['features']['entropy']:.2f}")
# Pink should have lower entropy (more structure)
```

---

## Advanced Topics

### Custom Feature Extraction

Extend `spectral_features()` with domain-specific features:

```python
def custom_features(spectrum, freqs):
    features = utac_fourier.spectral_features(spectrum, freqs)
    
    # Add power-law exponent
    log_freq = np.log(freqs[1:])
    log_spec = np.log(spectrum[1:] + 1e-8)
    slope, _ = np.polyfit(log_freq, log_spec, 1)
    features['power_law_exponent'] = -slope
    
    # Add specific band power (e.g., 8-13 Hz for alpha)
    alpha_mask = (freqs >= 8) & (freqs <= 13)
    features['alpha_power'] = np.sum(spectrum[alpha_mask])
    
    return features
```

### Time-Frequency Analysis

For non-stationary signals, use STFT:

```python
from scipy import signal as sig

# Short-Time Fourier Transform
f, t, Zxx = sig.stft(signal, fs=44100, nperseg=1024)

# Spectrogram
plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.title('STFT Magnitude')
```

---

## Integration with UTAC Pipeline

### Complete Workflow

```python
from models import logistic_threshold
from sonification import utac_fourier, utac_sonification

# 1. Generate field dynamics
R = np.linspace(0, 200, 10000)
beta = 5.2
theta = 100
response = logistic_threshold.sigmoid(R, beta, theta)

# 2. Spectral analysis
fourier_results = utac_fourier.run_analysis(response)

# 3. Classification
field_type = fourier_results['field_type']
print(f"Detected: {field_type}")

# 4. Sonification
audio = utac_sonification.generate_field_sound(
    response,
    field_type=field_type,
    duration=5.0
)

# 5. Save outputs
utac_sonification.save_audio(audio, "output/field_sound.wav")
```

---

## Troubleshooting

### Issue: Noisy spectrum

**Solution:** Apply windowing before FFT

```python
from scipy.signal import hann

window = hann(len(signal))
windowed_signal = signal * window
spectrum, freqs = utac_fourier.compute_fourier(windowed_signal)
```

### Issue: Low-frequency dominance

**Problem:** DC offset or trend

**Solution:** Detrend signal

```python
from scipy.signal import detrend

signal_detrended = detrend(signal)
```

### Issue: Classification unstable

**Problem:** Short signals or low sampling rate

**Solution:** Ensure minimum duration (0.5+ seconds) and adequate sampling (> 1 kHz for interesting dynamics)

---

## References

1. Lenton, T.M. et al. (2012). "Early warning signals of tipping points." *Nature* 461:53-59
2. Scheffer, M. (2009). *Critical Transitions in Nature and Society*. Princeton University Press
3. Wilson, K.G. (1975). "The renormalization group." *Reviews of Modern Physics* 47:773
4. Van der Maas, H.L.J. et al. (2003). "Sudden transitions in attitudes." *Sociological Methods & Research* 32:125-152

---

## License

CC-BY-4.0

---

**Last Updated:** December 15, 2024  
**Module Version:** utac_fourier.py v1.0  
**Status:** ✅ Production Ready
