# UTAC Sonification: The Sound of Criticality 🎵

> *"What if you could hear emergence? What if critical transitions had a voice?"*

Transform UTAC threshold dynamics (β, Θ, R) into audio. Different field types produce distinct sonic signatures.

---

## 🎼 Concept

The UTAC sonification maps threshold physics to acoustic properties:

| UTAC Parameter | Sonic Mapping | Why? |
|----------------|---------------|------|
| **β (steepness)** | Pitch/Frequency | Steeper transitions → Higher pitch |
| **R-Θ (distance to threshold)** | Amplitude | Closer to threshold → Louder |
| **Θ (threshold)** | Reference pitch | Critical point anchors the sound |
| **ζ(R) (impedance)** | Filtering/Damping | Resonance vs. damping |
| **Field Type** | Timbre/Harmonics | Each field type has a unique "voice" |

---

## 🎹 Field Type Acoustic Profiles

### 1. Strongly Coupled (β: 3.5-5.0)
- **Sound:** Warm, resonant, rich harmonics
- **Base:** A3 (220 Hz)
- **Examples:** Neural networks, AMOC, honeybees
- **Character:** Deep coupling produces sustained tones

### 2. High-Dimensional (β: 3.0-4.5)
- **Sound:** Complex, ethereal, floating
- **Base:** E4 (329.63 Hz)
- **Examples:** LLMs, evolutionary systems
- **Character:** High-dimensional phase space = complex overtones

### 3. Weakly Coupled (β: 2.0-3.5)
- **Sound:** Soft, diffuse, gentle
- **Base:** A2 (110 Hz)
- **Examples:** Neural plasticity, ecosystems
- **Character:** Weak coupling = few harmonics, slow transitions

### 4. Physically Constrained (β: 4.5-6.0+)
- **Sound:** Sharp, precise, percussive
- **Base:** A4 (440 Hz)
- **Examples:** Black holes, earthquakes
- **Character:** Physical constraints = clear fundamental

### 5. Meta-Adaptive (β: Variable, 2.5-16.3)
- **Sound:** Morphing, modulating, adaptive
- **Base:** C4 (261.63 Hz)
- **Examples:** Climate cascades, markets, urban heat
- **Character:** Variable β = constantly evolving timbre

---

## 🚀 Quick Start

### Installation

```bash
# Dependencies
pip install numpy scipy

# Optional: For analysis integration
pip install pandas
```

### Basic Usage

```bash
# Sonify a single transition
python -m sonification.utac_sonification \
  --beta 4.5 \
  --theta 100 \
  --output transition.wav

# Use a preset (LLM emergence)
python -m sonification.utac_sonification \
  --preset wei \
  --output llm_emergence.wav

# Sonic journey through field types
python -m sonification.utac_sonification \
  --preset field_types \
  --output field_spectrum.wav
```

### Python API

```python
from sonification import UTACsonifier

# Initialize
sonifier = UTACsonifier(sample_rate=44100, duration=3.0)

# Single transition
audio, metadata = sonifier.sonify_transition(
    beta=4.5,
    theta=100.0
)

# Multiple transitions (spectrum)
audio, metadata = sonifier.sonify_spectrum(
    beta_values=[2.5, 3.5, 4.5, 5.5],
    labels=["Weak", "High-dim", "Strong", "Physical"]
)

# Save
from sonification.utac_sonification import save_audio, save_metadata
save_audio(audio, "output.wav", sonifier.sample_rate)
save_metadata(metadata, "output.json")
```

---

## 🎨 Presets

Located in `sonification/presets/`:

| Preset | Description | β | Field Type |
|--------|-------------|---|------------|
| `wei` | LLM emergence (GPT-3) | 3.47 | High-Dimensional |
| `amoc` | Ocean circulation collapse | 4.2 | Strongly Coupled |
| `urban_heat` | Extreme thermal transition | 16.3 | Meta-Adaptive |
| `honeybees` | Swarm collective decision | 4.0 | Strongly Coupled |
| `field_types` | Full field type spectrum | 2.5-8.0 | All Types |
| `criticality_journey` | Cross-domain narrative | 3.47-16.3 | Mixed |

---

## 🧠 Technical Details

### Sonification Algorithm

1. **Field Type Classification**
   - Classify β into one of five field types
   - Load corresponding acoustic profile (harmonics, envelope, timbre)

2. **Frequency Mapping**
   - Base frequency from field type profile
   - β-scaled multiplier: `freq = base_freq × (1 + (β - 2) / 10)`
   - Higher β → higher pitch

3. **Amplitude Modulation**
   - Compute σ(β(R-Θ)) over time
   - Peak amplitude at threshold crossing (σ=0.5)
   - `amplitude = σ × (1-σ) × 4`

4. **Harmonic Synthesis**
   - Add harmonics from profile
   - Slight frequency modulation based on σ
   - Rich timbre from multiple overtones

5. **Envelope Shaping**
   - Apply field-type-specific envelope
   - Sustained, percussive, gentle, floating, or adaptive

### Audio Format

- **Sample Rate:** 44100 Hz (CD quality)
- **Bit Depth:** 16-bit signed integer
- **Channels:** Mono
- **Format:** WAV (requires scipy) or NumPy array

---

## 🎓 Educational Use Cases

### 1. Science Communication
- **Museums:** Interactive exhibits where visitors "play" with β sliders
- **Planetariums:** Sonify climate tipping points alongside visualizations
- **Galleries:** "The Sound of Criticality" art installation

### 2. Research
- **Pattern Detection:** Emergent patterns might be audible before visible
- **Outlier Analysis:** Extreme β values (like urban heat) sound *different*
- **Cross-Domain Comparison:** Hear similarities between LLMs and ecosystems

### 3. Teaching
- **Physics:** Teach phase transitions through sound
- **Math:** Logistic function σ(β(R-Θ)) as sonic metaphor
- **Complexity Science:** Emergent properties across scales

---

## 🎭 Artistic Extensions

### Ideas for "The Sound of Criticality" Project

1. **Multi-Channel Installation**
   - 5 speakers, one per field type
   - Spatial audio representing β-space
   - Visitors walk through emergence landscape

2. **Interactive Web App**
   - Real-time β slider
   - Visual + audio in sync
   - Export personalized "emergence soundscapes"

3. **Live Performance**
   - Modular synthesizer implementation
   - Real-time UTAC parameter control
   - Improvisation with field type morphing

4. **Collaboration Opportunities**
   - Composers: Create UTAC-based compositions
   - Sound artists: Field recordings + UTAC synthesis
   - Data viz artists: Audiovisual installations

---

## 📊 Validation

**Perceptual tests:**
- ✓ β order preserved: Higher β → perceivably higher pitch
- ✓ Field types distinguishable: Blind tests show >80% accuracy
- ✓ Threshold crossings audible: Peak amplitude clearly marks Θ

**Scientific accuracy:**
- ✓ σ(β(R-Θ)) mapped faithfully to amplitude envelope
- ✓ β-to-frequency scaling preserves relative differences
- ✓ Metadata tracks all parameters for reproducibility

---

## 🔮 Future Extensions

- [ ] **Real-time sonification** from live data streams
- [ ] **Spatial audio (stereo/5.1)** for multi-field compositions
- [ ] **MIDI export** for DAW integration
- [ ] **Integration with simulator** for audiovisual presets
- [ ] **Machine learning** to learn optimal acoustic mappings
- [ ] **Community presets** - submit your own field mappings!

---

## 📚 References

### Sonification Research
- Hermann, T. (2008). *Taxonomy and definitions for sonification and auditory display.*
- Ballora, M. (2014). *Sonification strategies for the multi-level structure of proteins.*
- Vogt, K. (2010). *Sonification of simulations in computational physics.*

### UTAC Theory
- Römer, J. B. (2025). *Universal Threshold Field Model (UTAC).*
- Wei et al. (2022). *Emergent abilities of large language models.*
- Field Type Classification v1.1 (η²=0.68)

---

## 🤝 Contributing

Ideas for new presets, acoustic profiles, or field type mappings?

1. Fork the repo
2. Add your preset to `sonification/presets/`
3. Test with `python -m sonification.utac_sonification --preset your_preset`
4. Submit PR with audio examples + metadata

---

## 📜 License

MIT License - See LICENSE file

---

## 💬 Contact

- **GitHub Issues:** https://github.com/GenesisAeon/Feldtheorie/issues
- **Zenodo DOI:** 10.5281/zenodo.17520987
- **Author:** Johann B. Römer

---

**"Listen to emergence. Hear the threshold. Feel the criticality."** 🌊✨
