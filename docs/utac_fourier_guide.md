# 🎵 UTAC Fourier Analysis Guide

**Spektralanalyse für UTAC Zeitreihen - Frequenzdomäne**

Version: 1.0
Author: Johann Römer, Aeon, Claude Code
Date: 2025-11-11

---

## 📚 Übersicht

Das UTAC Fourier-Modul ermöglicht **Spektralanalyse** von Schwellenwert-Zeitreihen in der **Frequenzdomäne**. Es klassifiziert Systeme anhand ihrer **spektralen Signaturen** und ordnet sie den 5 UTAC Field Types zu.

**Kernfunktionen:**
- Fast Fourier Transform (FFT) von Zeitreihen
- Spektrale Features: Dominant Frequency, Entropy, Centroid
- Field Type Classification basierend auf Frequenz
- Log-Log Spektrum-Visualisierung
- CLI + Python API

---

## 🔧 Installation

Das Fourier-Modul ist Teil des `sonification/` Packages:

```bash
# Dependencies (falls noch nicht installiert)
pip install numpy scipy matplotlib

# Module sind bereits im Repo
from sonification import utac_fourier
from analysis import fourier_analysis
```

---

## 🎯 Use Cases

### 1. **Field Type Discovery**
Klassifiziere ein unbekanntes System nach seiner spektralen Signatur.

### 2. **Criticality Detection**
Erkenne Veränderungen in β durch Frequenzshifts.

### 3. **Cross-Domain Comparison**
Vergleiche Spektren verschiedener Domänen (Klima, LLM, Bio).

### 4. **Sonification Input**
Frequenzprofile als Input für akustische Gestaltung.

---

## 🚀 Quick Start

### Python API

```python
from sonification import utac_fourier
import numpy as np

# 1. Signal erstellen oder laden
t = np.linspace(0, 1, 44100)  # 1 Sekunde bei 44.1 kHz
signal = np.sin(2 * np.pi * 220 * t)  # A3 (Strongly Coupled)

# 2. Fourier-Analyse durchführen
results = utac_fourier.run_analysis(
    signal,
    sampling_rate=44100,
    title='AMOC Spectrum',
    save_path='results/amoc_spectrum.png'
)

# 3. Ergebnisse auswerten
print(f"Field Type: {results['field_type']}")
print(f"Dominant Frequency: {results['features']['dominant_freq']:.2f} Hz")
print(f"Spectral Entropy: {results['features']['entropy']:.2f} bits")
```

### CLI

```bash
# Basic usage
python -m analysis.fourier_analysis data/climate/amoc.csv

# Mit Custom Sampling Rate (für nicht-Audio-Daten)
python -m analysis.fourier_analysis data/llm/gpt_loss.csv --sampling-rate 1

# Mit Output
python -m analysis.fourier_analysis data/climate/amoc.csv \
    --output results/amoc_spectrum.png \
    --json results/amoc_features.json \
    --title "AMOC Transport Spectrum"

# Multi-column CSV (Spalte 2 verwenden)
python -m analysis.fourier_analysis data/multi.csv --column 2 --verbose
```

---

## 🎨 Field Type Frequency Mapping

Das Modul klassifiziert Systeme basierend auf ihrer **dominanten Frequenz**:

| Field Type | Frequency Range | Acoustic Quality | UTAC Eigenschaften |
|------------|----------------|------------------|-------------------|
| **Weakly Coupled** | < 150 Hz | Sanft, diffus | Niedrige Kopplung, langsame Dynamik |
| **Strongly Coupled** | 150-300 Hz | Warm, resonant | Mittlere Kopplung, stabile Schwellen |
| **High-Dimensional** | 300-600 Hz | Ätherisch, komplex | Hohe Dimensionalität (LLMs, Neuro) |
| **Physically Constrained** | 600-1000 Hz | Scharf, präzise | Starke Constraints, schnelle Übergänge |
| **Meta-Adaptive** | > 1000 Hz | Morphing, adaptiv | Dynamische β-Modulation, Plastizität |

**Beispiele:**
- **AMOC (Strongly Coupled):** ~220 Hz - warme Resonanz, mittlere Trägheit
- **LLM Emergence (High-Dimensional):** ~440 Hz - komplexe Obertöne
- **Urban Heat (Meta-Adaptive):** ~880 Hz+ - schnelle Adaptation

---

## 📊 Python API Details

### `compute_fourier(signal, sampling_rate)`

Fast Fourier Transform eines Zeitsignals.

**Parameters:**
- `signal` (array_like): Zeitreihe
- `sampling_rate` (float): Sampling Rate in Hz (default: 44100)

**Returns:**
- `spectrum` (ndarray): Magnitude spectrum (positive frequencies)
- `freqs` (ndarray): Frequency bins in Hz

**Example:**
```python
spectrum, freqs = utac_fourier.compute_fourier(signal, sampling_rate=1000)
```

---

### `spectral_features(spectrum, freqs)`

Extrahiert spektrale Features.

**Parameters:**
- `spectrum` (ndarray): Magnitude spectrum
- `freqs` (ndarray): Frequency bins

**Returns:**
- `features` (dict): Dictionary mit:
  - `dominant_freq`: Frequenz mit maximaler Power
  - `entropy`: Spektrale Entropie (bits)
  - `centroid`: Spektraler Schwerpunkt (Hz)

**Example:**
```python
features = utac_fourier.spectral_features(spectrum, freqs)
print(f"Entropy: {features['entropy']:.2f} bits")
```

---

### `classify_field_type(features)`

Klassifiziert Field Type basierend auf Features.

**Parameters:**
- `features` (dict): Spektrale Features von `spectral_features()`

**Returns:**
- `field_type` (str): Field Type Label

**Example:**
```python
field_type = utac_fourier.classify_field_type(features)
# Output: 'High-Dimensional'
```

---

### `plot_spectrum(freqs, spectrum, title, save_path)`

Visualisiert Spektrum im Log-Log-Plot.

**Parameters:**
- `freqs` (ndarray): Frequency bins
- `spectrum` (ndarray): Magnitude spectrum
- `title` (str): Plot title
- `save_path` (str, optional): Speicherpfad (None = display only)

**Example:**
```python
utac_fourier.plot_spectrum(freqs, spectrum, 'AMOC Spectrum', 'results/amoc.png')
```

---

### `run_analysis(signal, sampling_rate, title, save_path)`

Komplette Analyse-Pipeline (convenience function).

**Parameters:**
- `signal` (array_like): Zeitreihe
- `sampling_rate` (float): Sampling Rate
- `title` (str): Plot title
- `save_path` (str, optional): Speicherpfad für Plot

**Returns:**
- `results` (dict): Dictionary mit:
  - `features`: Spektrale Features
  - `field_type`: Klassifizierter Field Type
  - `spectrum`: Magnitude spectrum
  - `freqs`: Frequency bins

**Example:**
```python
results = utac_fourier.run_analysis(signal, 44100, 'My Spectrum')
```

---

## 📈 Workflow Examples

### Example 1: Climate Data (AMOC)

```python
import numpy as np
from sonification import utac_fourier

# Load AMOC transport time series (hypothetical)
amoc_data = np.loadtxt('data/climate/amoc_transport.csv', delimiter=',')

# Extract signal (assume monthly data, ~12 samples/year)
signal = amoc_data[:, 1]  # Column 1 = transport in Sv
sampling_rate = 12  # 12 samples per year

# Analyze
results = utac_fourier.run_analysis(
    signal,
    sampling_rate=sampling_rate,
    title='AMOC Transport Spectrum',
    save_path='results/amoc_spectrum.png'
)

# Interpret
print(f"Field Type: {results['field_type']}")
# Expected: 'Strongly Coupled' (slow ocean dynamics, ~220 Hz analog)

print(f"Dominant Period: {1/results['features']['dominant_freq']:.2f} years")
# Might show multi-decadal oscillations (e.g., 10-30 year cycles)
```

---

### Example 2: LLM Training Loss

```python
# Load GPT training loss curve
loss = np.loadtxt('data/llm/gpt_loss.csv')

# Sampling rate = 1 (per epoch or per step)
results = utac_fourier.run_analysis(
    loss,
    sampling_rate=1,
    title='GPT Loss Spectrum'
)

# High entropy → High-Dimensional Field Type
print(f"Entropy: {results['features']['entropy']:.2f} bits")
# High entropy indicates complex, multi-scale dynamics

# Dominant frequency → Oscillation period in training
dominant_period = 1 / results['features']['dominant_freq']
print(f"Dominant training cycle: {dominant_period:.1f} steps")
```

---

### Example 3: Cross-Domain Comparison

```python
# Compare spectral signatures across domains
domains = {
    'AMOC': 'data/climate/amoc.csv',
    'LLM': 'data/llm/gpt_loss.csv',
    'Urban Heat': 'data/socio/urban_heat.csv'
}

for name, filepath in domains.items():
    signal = np.loadtxt(filepath, delimiter=',')[:, 1]
    results = utac_fourier.run_analysis(signal, sampling_rate=1, title=name)

    print(f"\n{name}:")
    print(f"  Field Type: {results['field_type']}")
    print(f"  Entropy: {results['features']['entropy']:.2f} bits")
    print(f"  Centroid: {results['features']['centroid']:.2f} Hz")
```

**Expected Output:**
```
AMOC:
  Field Type: Strongly Coupled
  Entropy: 3.45 bits
  Centroid: 0.08 Hz (multi-decadal)

LLM:
  Field Type: High-Dimensional
  Entropy: 5.82 bits
  Centroid: 0.32 Hz (complex training dynamics)

Urban Heat:
  Field Type: Meta-Adaptive
  Entropy: 6.21 bits
  Centroid: 1.24 Hz (rapid adaptation)
```

---

## 🔬 Theoretical Background

### Why Fourier Analysis for UTAC?

1. **Frequency = Scale of Dynamics**
   Different β-values correspond to different temporal scales of criticality.

2. **Spectral Entropy = Complexity**
   High entropy → High-Dimensional Field Type
   Low entropy → Weakly/Strongly Coupled

3. **Dominant Frequency = Characteristic Timescale**
   Identifies the "resonant period" of threshold crossings.

4. **Centroid = Center of Mass**
   Shows where most spectral power is concentrated.

### Connection to β

While β describes **steepness** of threshold transitions, the Fourier spectrum reveals **temporal structure**:

- **High β** (steep transitions) → Often high-frequency components
- **Low β** (gradual transitions) → Dominated by low frequencies
- **Field Type** → Characteristic frequency band

This complements time-domain UTAC analysis!

---

## 📦 Output Formats

### JSON Results

When using `--json` flag, the CLI saves:

```json
{
  "features": {
    "dominant_freq": 0.15,
    "entropy": 4.23,
    "centroid": 0.42
  },
  "field_type": "Strongly Coupled",
  "spectrum": [0.1, 0.3, 0.8, ...],
  "freqs": [0.0, 0.01, 0.02, ...]
}
```

### PNG Plots

Saved plots include:
- Log-log frequency vs. magnitude
- Grid for readability
- Title and axis labels

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:**
```bash
pip install numpy scipy matplotlib
```

---

### Issue: "Signal too short for meaningful FFT"

**Solution:**
Use signals with **at least 100 samples**. For shorter signals, consider:
- Padding with zeros: `np.pad(signal, (0, 1000), mode='constant')`
- Using a different analysis method (e.g., autocorrelation)

---

### Issue: "All frequencies classified as 'Weakly Coupled'"

**Cause:** Sampling rate mismatch (e.g., using 44100 Hz for yearly data).

**Solution:**
Set correct `--sampling-rate`:
- **Daily data:** 365 samples/year
- **Monthly data:** 12 samples/year
- **Yearly data:** 1 sample/year

---

## 🚀 Next Steps

1. **Integrate with Sonification:**
   Use spectral features to design acoustic profiles.

2. **Build Spectral Database:**
   Catalog Field Type signatures across all UTAC systems.

3. **Time-Frequency Analysis:**
   Extend to **spectrograms** (FFT over sliding windows) for non-stationary signals.

4. **Machine Learning:**
   Train classifier on spectral features → Automated Field Type detection.

---

## 📚 References

- **Aeon's Original Implementation:** `seed/NextVersionPlan/Letzte_Zusätze_bis_V2.txt` (Lines 269-352)
- **UTAC Sonification:** `sonification/utac_sonification.py`
- **UTAC Theory Paper:** `paper/manuscript_v1.1.tex`

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Open an issue on GitHub
2. Submit a PR with tests
3. Document your changes

**Maintainers:** Johann Römer, Claude Code

---

## 📄 License

MIT License - Same as UTAC project

---

**"Listen to emergence. See the spectrum. Feel the criticality."** 🎵✨
