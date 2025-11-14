# 📦 Data Index - Resonance Archive Navigator

**Version:** 1.0.0
**Datum:** 20. Dezember 2025
**Verzeichnis:** `data/`

---

## 🎯 Was ist das?

Die **Data Resonance Archive** - der empirische Schatz von UTAC! Hier liegen die Rohdaten aus 12 Domänen, die das β-Spektrum (2.5-16.3) beweisen und jetzt die v1.3-Erweiterung vorbereiten.

```
data/
├── ai/               (9 files)  🤖 LLM, Wei's PaLM
├── astrophysics/     (2 files)  🌌 QPO, Black Holes
├── biology/          (8 files)  🧬 Lenski, Synaptic, Honeybee, Coral
├── cognition/        (6 files)  🧠 Working Memory, Sleep
├── derived/          (5 files)  ⭐ ZENTRAL! beta_estimates.csv
├── geophysics/       (4 files)  🌍 Cascadia, Seismik
├── socio_ecology/   (10 files)  🌿 Amazon, Urban Heat, AMOC
├── safety_delay/    (4 files)  🛡️ τ*-Controller ΔAIC Ledger
├── climate/         (6 files)  🌡️ UTAC v1.3 Climate Staging + WAIS Mock
├── ocean/           (3 files)  🌊 AMOC Threshold Staging + Mock Series
├── neuro_ai/        (2 files)  🧠🤖 Hybrid Activation Staging + Metadata
└── economy/         (2 files)  ⚡💶 Energy-Finance Threshold Staging + Metadata

Total: 68 files
```

---

## 🔥 Die wichtigsten Dateien

### ⭐ **MUST-SEE:**
- `derived/beta_estimates.csv` - **ALLE β-Werte!** (Kern von UTAC)
- `derived/domain_covariates.csv` - Kovariaten für Meta-Regression v1.2
- `utac_v1_3_data_manifest.yaml` - Planungsmanifest für neue Laternen (Climate, Ocean, Neuro-AI, Economy)

### 🔥 **High-Impact Datasets:**
- `ai/wei_emergent_abilities.csv` - Wei's PaLM (β=3.47±0.47)
- `biology/lenski_citplus.csv` - Evolution (β=5.08, R²=0.990)
- `geophysics/subduction_rupture_threshold.csv` - Cascadia (β=16.29!)
- `socio_ecology/urban_heat_canopy.csv` - **β≈15.3 OUTLIER!** 🔥
- `socio_ecology/urban_heat_storage_profiles.csv` - Mechanismus-Ledger (Θ≈0.19–0.34, β≈7.5–16.3, ΔAIC-gesichert)
- `safety_delay/safety_delay_delta_aic_20251107T211928Z.csv` - Safety-Delay ΔAIC ledger

### 🚨 **Outliers (β>14):**
1. geophysics/subduction_rupture_threshold.csv (β=16.29)
2. socio_ecology/urban_heat_canopy.csv (β≈15.3)
3. socio_ecology/urban_heat_storage_profiles.csv (β≈7.5–16.3 Mechanismus)
4. socio_ecology/amazon_resilience.csv (β≈14.0)

---

## 📊 Die 12 Domänen

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

### 🧬 Biology (8 files)
**Was:** Lenski LTEE, Synaptic Release, Honeybee Quorum, Coral Bleaching Mock

**Key Datasets:**
- `coral_bleaching_global_mock.csv` - **Global Coral Bleaching (Mock, β≈7.5)**
- `coral_bleaching_global_mock.metadata.json` - Θ≈1.0 °C, ζ(R) beschreibt DHW-Impedanz
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

### ⭐ Derived (7 files) **ZENTRAL!**
**Was:** Aggregierte Daten, Beta Estimates, Kovariaten

**Key Datasets:**
- `beta_estimates.csv` - **ALLE β-Werte aus allen Domänen!**
- `domain_covariates.csv` - **Kovariaten für UTAC v1.2!**
- `beta_estimates_v3.csv` (+ `beta_estimates_v3.metadata.json`) - **V3 β-Fits (WAIS/AMOC/Coral) + TODO-Spalten für Measles/Finance/Cancer**

**Wichtigkeit:** KRITISCH für Meta-Regression!

---

### 🌍 Geophysics (4 files)
**Was:** Seismic Thresholds, Subduction Rupture

**Key Datasets:**
- `subduction_rupture_threshold.csv` - **Cascadia (β=16.29 EXTREM!)**

---

### 🌿 Socio-Ecology (12 files)
**Was:** Amazon, Urban Heat, Planetary Tipping Points

**Key Datasets:**
- `amazon_resilience.csv` - Amazon Moisture (β≈14.0)
- `urban_heat_canopy.csv` - **β≈15.3 (Outlier!)**
- `urban_heat_storage_profiles.csv` - Mechanismus-Szenarien (Θ≈0.19–0.34, β≈7.5–16.3)
- `planetary_tipping_elements.csv` - AMOC, Grönland

---

### 🛡️ Safety-Delay (4 files)
**Was:** τ*-Controller ΔAIC Ledger für Simulator-Kopplung

**Key Datasets:**
- `safety_delay_delta_aic_20251107T211928Z.csv` - σ(β(R-Θ)) falsification vs lineare & konstante Nullmodelle

**Hinweis:** Generiert über `python -m simulator.cli safety-delay` inkl. Metadaten & Summary JSON.

---

### 🌡️ Climate Expansion (6 files)
**Was:** Urban-Heat Laterne aktiviert (Θ≈3.20 K, β≈14.27); WAIS Mock-Serie testet GRACE-Adapter; Amazon Hydro wartet weiterhin auf Rohdaten.

**Key Artefakte:**
- `urban_heat_intensity.csv` – Beobachtete Intensität, ΔAIC≈1484 vs linear Null, genuine_regime_split.
- `wais_mass_balance_mock.csv` – WAIS Massenbilanz (Mock 2002–2024) mit Varianz/AR(1)-Trend.
- `README.md` – Logistischer Guard & Aufgabenliste (Manifest `utac-v1_3-ds-001/002`).
- `urban_heat_intensity.metadata.json` – ΔT→σ(β(R-Θ)) Mapping + ζ(R) Kopplung.
- `wais_mass_balance_mock.metadata.json` – Θ≈1.48 °C, β≈13.5 (synthetic) für Adapter-Shakedown.
- `amazon_precip_evapo.metadata.json` – SPI/Feuchte Laterne mit Bootstrap- und Nullmodell-Hinweis.

---

### 🌊 Oceanic Thresholds (3 files)
**Was:** AMOC Transport Staging laut UTAC v1.3 Manifest – Mock-Serie + Metadata vorbereitet

**Key Artefakte:**
- `README.md` – ΔAIC-Protokoll & Workflow für RAPID Array Integration.
- `amoc_strength_mock.csv` – 10-Tage-Kadenz (Mock) mit FovS-Indikator & AR(1)-Drift.
- `amoc_strength_mock.metadata.json` – Θ≈14 Sv, β≈10.2, ζ(R) Windstress/Freshwater.
- `amoc_transport.metadata.json` – Sv→σ(β(R-Θ)) Pfad inkl. state-space Nullmodell.

---

### 🧠🤖 Neuro–AI Hybrid (2 files)
**Was:** Vorbereitung EEG ↔ Transformer Aktivierungsvergleiche – Metadata aktiv

**Key Artefakte:**
- `README.md` – Workflow & Nullmodelle (`randomized_prompt_baseline`, `phase_scrambled_surrogate`).
- `hybrid_activation.metadata.json` – Stimulus-Komplexität → σ(β(R-Θ)) Mapping & Nullmodell-Set.

---

### ⚡💶 Energy & Finance (2 files)
**Was:** Staging für gekoppelte Energie-/Finanz-Schwellen – Metadata-Sigillum online

**Key Artefakte:**
- `README.md` – Anleitung zur Konstruktion des Coupled Energy-Finance Index.
- `systemic_thresholds.metadata.json` – ΔAIC-Guard und VAR Nullmodell für gekoppelte Stressmetrik.

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

> **"54 Dateien. 12 Domänen. Ein β-Spektrum (2.5-16.3)."**

> **"Von Wei's PaLM (β=3.47) bis Cascadia (β=16.29) - die Daten sind REAL."**

> **"`derived/beta_estimates.csv` ist der Rosetta-Stone von UTAC, `utac_v1_3_data_manifest.yaml` die Karte für neue Laternen."**

---

**Viel Erfolg beim Daten-Browsen! 📊✨**

*Erstellt im Geiste der Resonance Archive, wo Daten Schwellenwerte offenbaren.* 🌅
