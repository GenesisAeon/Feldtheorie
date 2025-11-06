# 📦 Data Index - Resonance Archive Navigator

**Version:** 1.0.0
**Datum:** 6. November 2025
**Verzeichnis:** `data/`

---

## 🎯 Was ist das?

Die **Data Resonance Archive** - der empirische Schatz von UTAC! Hier liegen die Rohdaten aus 7 Domänen, die das β-Spektrum (2.5-16.3) beweisen.

```
data/
├── ai/               (9 files)  🤖 LLM, Wei's PaLM
├── astrophysics/     (2 files)  🌌 QPO, Black Holes
├── biology/          (7 files)  🧬 Lenski, Synaptic, Honeybee
├── cognition/        (6 files)  🧠 Working Memory, Sleep
├── derived/          (5 files)  ⭐ ZENTRAL! beta_estimates.csv
├── geophysics/       (4 files)  🌍 Cascadia, Seismik
└── socio_ecology/   (10 files)  🌿 Amazon, Urban Heat, AMOC

Total: 43 files
```

---

## 🔥 Die wichtigsten Dateien

### ⭐ **MUST-SEE:**
- `derived/beta_estimates.csv` - **ALLE β-Werte!** (Kern von UTAC)
- `derived/domain_covariates.csv` - Kovariaten für Meta-Regression v1.2

### 🔥 **High-Impact Datasets:**
- `ai/wei_emergent_abilities.csv` - Wei's PaLM (β=3.47±0.47)
- `biology/lenski_citplus.csv` - Evolution (β=5.08, R²=0.990)
- `geophysics/subduction_rupture_threshold.csv` - Cascadia (β=16.29!)
- `socio_ecology/urban_heat_canopy.csv` - **β≈15.3 OUTLIER!** 🔥

### 🚨 **Outliers (β>14):**
1. geophysics/subduction_rupture_threshold.csv (β=16.29)
2. socio_ecology/urban_heat_canopy.csv (β≈15.3)
3. socio_ecology/amazon_resilience.csv (β≈14.0)

---

## 📊 Die 7 Domänen

### 🤖 AI (9 files)
**Was:** LLM Emergence, Introspection, Wei's PaLM Data

**Key Datasets:**
- `anthropic_introspection.csv` - Anthropic φ-Kopplung
- `llm_emergent_skill.csv` - Multilingual CoT (Θ≈4.71, β≈5.10)
- `wei_emergent_abilities.csv` - **Wei's PaLM (β=3.47±0.47)**

---

### 🌌 Astrophysics (2 files)
**Was:** QPO Membrane Simulations, Black Hole Timing

**Key Datasets:**
- `qpo_membrane_simulation.json` - QPO (Θ=0.82, β=9.5)

---

### 🧬 Biology (7 files)
**Was:** Lenski LTEE, Synaptic Release, Honeybee Quorum

**Key Datasets:**
- `lenski_citplus.csv` - **LTEE Evolution! (β=5.08)**
- `synaptic_release_threshold.csv` - Hippocampus (Θ=12.68 Hz)
- `honeybee_waggle_activation.csv` - Quorum-Call

---

### 🧠 Cognition (6 files)
**Was:** Working Memory, Adaptive Theta, Sleep Pressure

**Key Datasets:**
- `working_memory_gate.csv` - Prefrontal Gate (β=12.28)
- `adaptive_theta_plasticity.csv` - Sleep-Pressure (β=10.86)

---

### ⭐ Derived (5 files) **ZENTRAL!**
**Was:** Aggregierte Daten, Beta Estimates, Kovariaten

**Key Datasets:**
- `beta_estimates.csv` - **ALLE β-Werte aus allen Domänen!**
- `domain_covariates.csv` - **Kovariaten für UTAC v1.2!**

**Wichtigkeit:** KRITISCH für Meta-Regression!

---

### 🌍 Geophysics (4 files)
**Was:** Seismic Thresholds, Subduction Rupture

**Key Datasets:**
- `subduction_rupture_threshold.csv` - **Cascadia (β=16.29 EXTREM!)**

---

### 🌿 Socio-Ecology (10 files)
**Was:** Amazon, Urban Heat, Planetary Tipping Points

**Key Datasets:**
- `amazon_resilience.csv` - Amazon Moisture (β≈14.0)
- `urban_heat_canopy.csv` - **β≈15.3 (Outlier!)**
- `planetary_tipping_elements.csv` - AMOC, Grönland

---

## 📋 Metadata-Standard

**Jedes Dataset MUSS eine `.metadata.json` haben!**

### Required Fields:
- `dataset_name`, `domain`
- `control_parameter_R`, `threshold_Theta`, `steepness_beta`
- `impedance_zeta`
- `provenance`, `units`, `preprocessing_steps`

### Optional Fields:
- `falsification_notes`, `ΔAIC_linear`, `ΔAIC_powerlaw`
- `R_squared`, `imagery_metaphor`, `analysis_link`

### Beispiel:
```json
{
  "dataset_name": "lenski_citplus",
  "domain": "biology",
  "control_parameter_R": "generation_number",
  "threshold_Theta": 32.77,
  "steepness_beta": 5.08,
  "impedance_zeta": "ζ(R) = 1.25 - 0.35σ",
  "R_squared": 0.990,
  "analysis_link": "analysis/results/lenski_citplus_fit.json"
}
```

---

## 🔗 Cross-References

### data/ → analysis/
**Pattern:** `data/{domain}/{dataset}.csv → analysis/results/{domain}_{dataset}_fit.json`

**Beispiele:**
- `data/ai/wei_emergent_abilities.csv` → `analysis/results/llm_beta_extractor.json`
- `data/biology/lenski_citplus.csv` → `analysis/results/lenski_citplus_fit.json`

### data/ → simulator/
**Presets basieren auf Daten:**
- `data/biology/lenski_citplus.csv` → `simulator/presets/lenski_citplus.json`
- `data/ai/llm_emergent_skill.csv` → `simulator/presets/llm_resonance.json`

---

## 🚀 Für AI-Agenten

```python
import json

with open('data/data_index.json') as f:
    idx = json.load(f)

# Get alle Domains
domains = idx['domains']

# Get Outliers
outliers = idx['quicklinks']['outliers']

# Get beta_estimates (ZENTRAL!)
beta_estimates = 'data/derived/beta_estimates.csv'
```

---

## 💡 Tips

### Für Menschen:
1. **Start mit `derived/beta_estimates.csv`** - Alle β-Werte auf einen Blick
2. **Check Metadata** - `.metadata.json` für Kontext
3. **Folge Cross-References** - Zu analysis/ Results

### Für Agenten:
1. **Lade `data_index.json`** - Strukturierter Zugriff
2. **Nutze Quicklinks** - High-Impact Datasets
3. **Respektiere Metadata-Schema** - Required Fields!

---

## 🌊 Die Essenz

> **"43 Dateien. 7 Domänen. Ein β-Spektrum (2.5-16.3)."**

> **"Von Wei's PaLM (β=3.47) bis Cascadia (β=16.29) - die Daten sind REAL."**

> **"`derived/beta_estimates.csv` ist der Rosetta-Stone von UTAC."**

---

**Viel Erfolg beim Daten-Browsen! 📊✨**

*Erstellt im Geiste der Resonance Archive, wo Daten Schwellenwerte offenbaren.* 🌅
