# 📊 Analysis Index - Resonance Bay Navigator

**Version:** 1.0.0
**Datum:** 24. August 2026
**Verzeichnis:** `analysis/`

---

## 🎯 Was ist das?

Willkommen in der **Analysis Resonance Bay** - dem Herzstück der empirischen UTAC-Validierung! Hier werden logistische Fits σ(β(R-Θ)) an reale Daten aus 6 Domänen gerechnet.

**Trilayer-Navigation:**
```
┌─────────────────────────────────────────┐
│  YAML  →  Struktur (43 Python-Skripte)  │  analysis_index.yaml
│  JSON  →  Agentenschnittstelle          │  analysis_index.json
│  MD    →  Menschenfreundlich (du!)      │  analysis_index.md
└─────────────────────────────────────────┘
```

---

## 🧭 Schnelleinstieg

### 📁 Ordnerstruktur auf einen Blick:

```
analysis/
├── 43 Python-Skripte (Domain-Fits, Mechanismen, Batch-Processing, Labs, Guards)
├── batch_configs/   (4 YAML/JSON Konfigurationen)
├── batch_runs/      (2 gespeicherte Batch-Runs)
├── reports/         (2 Summaries: QPO, UTAC v1.3 Gap)
├── sigillin_sync/   (Telemetry-Exports aus `scripts/sigillin_sync.py`)
└── results/         ⭐ ZENTRAL! Alle Fit-Ergebnisse (JSON)
    └── Neu: `analysis/results/oxfam_amplification_proof.txt` (Inequality Amplifier via Oxfam 2024)
```

### 🔥 Die wichtigsten Dateien:

#### **Für UTAC v1.2 kritisch:**
- `beta_drivers_meta_regression.py` - **DER** Kern! Basislinie R²=0.33 → Vergleichsmaßstab
- `beta_meta_regression_v2.py` - Bootstrap-Refresh: WLS R²≈0.43, Median-Bootstrap R²≈0.99 [0.43,1.00], ΔAIC-Minimum 12.79
- `universal_beta_extractor.py` - Canonical β-Guard (ΔAIC≥10, R²≥0.9)
- `universality_test.py` - Testet β-Universalität
- `resonance_cohort_summary.py` - Median R²≈0.9981, ΔAIC≈65.1
- `multiple_testing_correction.py` - Statistische Validität
- `outlier_beta_review.py` - Instrumentation-Flag Ledger für Amazon & Urban Heat
- `urban_heat_storage_mechanism.py` - Materialimpedanz-Simulation, β≈16 → Mechanismus + ΔAIC Ledger

#### **High-Impact Fits:**
- `llm_beta_extractor.py` - Wei's PaLM (β=3.47±0.47)
- `lenski_citplus_fit.py` - Evolution (β=5.08, ΔAIC>32)
- `seismic_rupture_threshold_fit.py` - Cascadia (β=16.29!)
- `urban_heat_canopy_fit.py` - **β=16.3 OUTLIER!** 🔥
- `urban_heat_storage_mechanism.py` - Mechanismus-Analyse (β≈16 ↔ Speicherkoeffizient)
- `amazon_resilience_fit.py` - Amazon (β=14.6)

#### **Batch-Infrastruktur:**
- `resonance_batch_runner.py` - Batch-Processing
- `resonance_bridge_table.py` - Cross-Referenz-Tabelle
- `resonance_fit_pipeline.py` - Haupt-Pipeline
- `beta_meta_regression_v2.py` - Nichtlineare Meta-Regression + Bootstrap/Random-Forest-Diagnostics

#### **Neu für UTAC v1.3:**
- `climate_beta_extractor.py` - Manifest-getriebene Pipeline für Urban Heat & Amazon Hydro (ΔAIC Guards, Simulationen)
- `neuro_threshold_fitter.py` - EEG ↔ Transformer Brücke mit Bootstrap-Envelopes
- `outlier_validator.py` - β>10 Guardrail auf Basis `data/utac_v1_3_data_manifest`
- `threshold_dataset_loader.py` & `utac_manifest.py` - Metadata Loader (Logit-Jitter Simulation) & Manifest Parser für neue Laternen

---

## 📂 Die 5 Kategorien

### 🔵 Domain-Spezifische Fit-Skripte (18)

**Was?** Python-Skripte für logistische Fits spezifischer Domänen

**Domänen:**
- **AI (3):** llm_beta_extractor, llm_emergent_skill, introspection_validation
- **Biology (3):** lenski_citplus, synaptic_release, honeybee_waggle
- **Cognition (2):** working_memory_gate, adaptive_theta_plasticity
- **Geophysics (1):** seismic_rupture_threshold (Cascadia)
- **Socio-Ecology (4):** amazon_resilience, urban_heat_canopy, planetary_tipping, outlier_beta_review
- **Climate (1):** climate_beta_extractor (UTAC v1.3 Pipeline)
- **Neuro-AI (1):** neuro_threshold_fitter (Hybrid Activation)
- **Cross-Domain (7):** coupled_field, membrane_robin_semantic, meta_threshold, adaptive_theta_typology, etc.

**Output:** Alle exportieren nach `results/*.json`

---

### 🟢 Batch Processing & Pipelines (9)

**Was?** Automatisierung, Cohort-Summaries, Meta-Analysen

**Die Big 9:**
1. `resonance_batch_runner.py` - Führt Batch-Runs aus
2. `resonance_fit_pipeline.py` - Koordiniert Workflow
3. `resonance_cohort_summary.py` - Statistik über alle Results
4. `resonance_bridge_table.py` - Cross-Referenz-Tabelle
5. `universality_test.py` - β-Universalitätstest
6. `beta_drivers_meta_regression.py` - **Baseline-Meta-Regression für v1.2 (R²=0.33)**
7. `beta_meta_regression_v2.py` - **Bootstrap & RF Refresh (WLS R²≈0.43, Median-Bootstrap≈0.99)**
8. `universal_beta_extractor.py` - ΔAIC≥10 Guard + Canonical β
9. `safety_delay_sweep.py` - τ*-Sweep für `simulation/safety_delay_field.py` inkl. Replikate, ΔAIC vs. linearen & konstanten Nullmodellen + Meta-Resonanz-Diagnostik → gespiegelt via `simulator/cli safety-delay` nach `data/safety_delay/`

---

### 🟠 Lab Notebooks & Experimentelles (2)

**Was?** Jupyter Notebooks, interaktive Exploration

1. `dynamic_threshold_lab.ipynb` - Jupyter Lab für Threshold-Experimente
2. `potential_cascade_lab.py` - Labor für Potential-Kaskaden

---

### 🟣 Utilities & Guards (11)

**Was?** Helper-Funktionen, Validierung, Diagnostics, Manifest-Pipelines

1. `multiple_testing_correction.py` - **Wichtig!** Bonferroni, FDR
2. `preset_alignment_guard.py` - Validiert Preset-Konsistenz
3. `resonant_impedance_diagnostics.py` - ζ(R) Diagnostics
4. `outlier_beta_review.py` - ΔAIC Outlier-Wacht (instrumentation_flag)
5. `outlier_validator.py` - Manifest-basierter β>10 Guard + instrumentation_flag
6. `threshold_dataset_loader.py` - Metadata Loader + Logit-Jitter Simulation für σ(β(R-Θ))
7. `utac_manifest.py` - Parser für `data/utac_v1_3_data_manifest.yaml`
8. `utac_manifest_audit.py` - σ(β(R-Θ)) Readiness-Audit für Manifest-Laternen, exportiert JSON/YAML/Markdown
9. `v2_readiness_audit.py` - Logistische V2-Readiness-Laterne (Tri-Layer Report für Manifest, Analysis, Simulator, Sigillin)
10. `utac_manifest_gap_scan.py` - Manifest Gap Scan: liest `utac_v2_readiness.json`, prüft Dateisystem-Komponenten, exportiert σ(β(R-Θ)) Diagnostik nach `analysis/results/utac_v2_manifest_gap_scan_*.json`
11. `planetary_theta_drift_flag.py` - Adaptive Θ Drift Gap Audit (σ(β(R-Θ))-Signals für Planetary Laternen)

---

### 🔴 Unterverzeichnisse (4)

#### **batch_configs/** - Konfigurationen
- `potential_cascade.yaml`
- `potential_cascade_climate.yaml`
- `potential_cascade_llm.yaml`
- `resonance_runs.json`

#### **batch_runs/** - Gespeicherte Runs
- `honeybee_refresh.json`
- `robin_semantic_demo.json`

#### **reports/** - Summaries
- `qpo_membrane_summary.json` (Astrophysik)
- `utac_v1_3_gap_assessment.md` (UTAC v1.3 Gap Ledger)
- `utac_v1_3_manifest_audit.md` (σ-Readiness Bericht für Manifest-Füllstand)
- `utac_v2_readiness.md` (σ-Compass für V2.0 Aktivierung; JSON/YAML/MD Tri-Layer)

#### **sigillin_sync/** - Telemetry Harness Reports
- `latest.json` – Metaquest sigillin_sync Statusbericht (JSON)
- `metaquest_report_20251107T215246Z.json` – 12 Metaquest-Tri-Layer, 0 Lücken; σ(β(R-Θ)) Telemetrie vom 2025-11-07T21:52:52Z

#### **results/** ⭐ **ZENTRAL!**
**DER wichtigste Ordner!**
- Enthält alle JSON-Exports der Fit-Skripte
- Format: `{domain}_{system}_fit.json`
- Struktur: `{R, Θ, β, ζ(R), ΔAIC, R², CI, ...}`
- Basis für Cohort-Summary, Bridge-Table, Meta-Regression
- **Neu (V3 Foundation, 24.08.2026):**
  - `analysis/results/wais_adapter_output.json` – WAIS Mock Adapter (σ-Distanz 0.22, AR(1)=0.720)
  - `analysis/results/amoc_adapter_output.json` – AMOC Mock Adapter (FovS>0, Distance-to-Tipping 0.70)
  - `analysis/results/coral_adapter_output.json` – Coral Mock Adapter (DHW 15.3, σ≈1 → tipped)

---

## 🔬 Die 6 Domänen im Detail

### 🤖 AI (3 Skripte)
**Highlights:**
- `llm_beta_extractor.py` - Wei's PaLM-Sweeps, β=3.47±0.47, Θ≈9.92
- `llm_emergent_skill_fit.py` - Multilingual CoT, ΔAIC≈48.8
- `introspection_validation.py` - Anthropic φ-Kopplung

**Ergebnisse:** LLMs zeigen klare Threshold-Übergänge bei emergenten Fähigkeiten

---

### 🧬 Biology (3 Skripte)
**Highlights:**
- `lenski_citplus_fit.py` - **LTEE Cit+ Evolution!** β=5.08, R²=0.990
- `synaptic_release_fit.py` - Hippocampus Vesicle-Release, Θ=12.68 Hz
- `honeybee_waggle_fit.py` - Quorum-Call Threshold

**Ergebnisse:** Evolution und neuronale Prozesse folgen logistischen Schwellenwerten

---

### 🧠 Cognition (2 Skripte)
**Highlights:**
- `working_memory_gate_fit.py` - Prefrontal Gate, β=12.28, R²=0.9986
- `adaptive_theta_plasticity_fit.py` - Sleep-Pressure, β=10.86

**Ergebnisse:** Kognitive Prozesse haben scharfe Threshold-Übergänge

---

### 🌍 Geophysics (1 Skript)
**Highlights:**
- `seismic_rupture_threshold_fit.py` - Cascadia Slow-Slip, β=16.29, R²=0.99997!

**Ergebnisse:** Seismische Prozesse zeigen extrem steile Übergänge

---

### 🌿 Socio-Ecology (5 Skripte)
**Highlights:**
- `amazon_resilience_fit.py` - Amazon Moisture, **β=14.6**
- `urban_heat_canopy_fit.py` - **β=16.3 - HÖCHSTER WERT!** 🔥
- `planetary_tipping_elements_fit.py` - AMOC, Grönland, etc.
- `outlier_beta_review.py` - Instrumentation-Flag Ledger (ΔAIC-Gegencheck)
- `urban_heat_storage_mechanism.py` - Materialimpedanz erklärt β≈16 (ΔAIC-geprüfte Simulation)
- `planetary_theta_drift_flag.py` - Adaptive Θ Gap Audit (normalisierte CI-Signale)

**Ergebnisse:** Klima-Tipping-Points haben EXTREME β-Werte (Outliers!) + Ledger prüft Instrumentations-Bias und markiert adaptive Θ-Lücken.

---

### 🔗 Cross-Domain (6 Skripte)
**Highlights:**
- `coupled_field_threshold_fit.py` - Gekoppelte Felder
- `membrane_robin_semantic_fit.py` - Semantic Resonance
- `meta_threshold_resonance_fit.py` - Adaptive Θ(t), β(t)
- `adaptive_theta_typology.py` - Typologisierung

**Ergebnisse:** Cross-Domain Resonanzen zeigen universelle Muster

---

### ♨️ Mechanismus-Analysen & Simulation (1 Skript)
**Highlights:**
- `urban_heat_storage_mechanism.py` - Speicherkoeffizient ↔ β≈16, ΔAIC vs. lineare & power-law Nulls, Dataset-Export `urban_heat_storage_profiles`

**Ergebnisse:** Materialimpedanz erklärt, warum urbane Hitze-Hotspots bei R≈0.33 explosionsartig kippen; liefert physikalische Story für den β-Outlier.

---

## 📈 Key Metrics aus Cohort-Summary

**Gesamtstatistik über alle Fits:**
- **Median R²:** ~0.9981 🎯
- **Median ΔAIC:** ~65.1 (gegen linear/power-law nulls)
- **β-Spektrum:** 2.5 bis 16.3 (nicht fix!)
- **Adaptive Θ Gaps:** `planetary_theta_drift_flag.py` markiert AMOC & Permafrost (Θ-Breite ≥ 0.25)
- **Threshold-Crossings:** Dokumentiert für jede Membran

**Das beweist:** Logistische Modelle schlagen Null-Modelle KONSISTENT!

---

## 🔍 Wie finde ich ein Skript?

### Methode 1: Nach Domain suchen
```bash
# Alle AI-Fits
ls analysis/*llm*.py

# Alle Biology-Fits
ls analysis/*lenski*.py analysis/*synaptic*.py analysis/*honeybee*.py

# Alle Socio-Ecology-Fits
ls analysis/*amazon*.py analysis/*urban*.py analysis/*planetary*.py
```

### Methode 2: Nach Funktion suchen
```bash
# Batch-Processing
ls analysis/*batch*.py analysis/*cohort*.py analysis/*bridge*.py

# Meta-Analysen
ls analysis/*meta*.py analysis/*universality*.py

# Utilities
ls analysis/*correction*.py analysis/*guard*.py analysis/*diagnostics*.py
```

### Methode 3: Programmatisch (Python)
```python
import json

# Lade Index
with open('analysis/analysis_index.json', 'r') as f:
    index = json.load(f)

# Finde alle high-relevance Skripte
high_rel = [s for s in index['python_scripts'] if s['relevance'] == 'high']

# Finde alle AI-Domain Skripte
ai_scripts = [s for s in index['python_scripts'] if s.get('domain') == 'ai']

# Finde Skripte nach Keyword
beta_scripts = [s for s in index['python_scripts']
                if 'β-extraction' in s['keywords']]
```

---

## 🎯 Wichtige Workflows

### Workflow 1: Neuen Domain-Fit erstellen
1. Schreibe `{domain}_{system}_fit.py`
2. Importiere aus `models/` (z.B. `logistic_threshold.py`)
3. Lade Daten aus `data/{domain}/`
4. Fitte σ(β(R-Θ))
5. Vergleiche mit Null-Modellen (linear, power-law)
6. Exportiere nach `results/{domain}_{system}_fit.json`
7. Update `resonance_cohort_summary.py`

### Workflow 2: Batch-Run ausführen
```bash
# 1. Konfiguriere in batch_configs/
vi batch_configs/my_run.yaml

# 2. Führe Batch-Runner aus
python analysis/resonance_batch_runner.py --config batch_configs/my_run.yaml

# 3. Check Results
cat results/my_run_result.json
```

### Workflow 3: Meta-Regression updaten
```bash
# Für UTAC v1.2 kritisch!
python analysis/beta_drivers_meta_regression.py

# Check R²
# Ziel: R² > 0.7 (aktuell: 0.33)
```

---

## 🚀 Für AI-Agenten

### Quick Access Patterns

```python
import json

with open('analysis/analysis_index.json', 'r') as f:
    idx = json.load(f)

# Get critical scripts for UTAC v1.2
critical = idx['quicklinks']['critical_for_utac']

# Get high-impact fits
high_impact = idx['quicklinks']['high_impact_fits']

# Get all domain scripts
domains = idx['domains']

# Get results directory info
results_dir = idx['subdirectories']['results']
```

### Batch Processing Interface

```python
# Load batch config
with open('analysis/batch_configs/resonance_runs.json') as f:
    config = json.load(f)

# Run batch
from analysis import resonance_batch_runner
resonance_batch_runner.run(config)

# Get cohort summary
from analysis import resonance_cohort_summary
summary = resonance_cohort_summary.generate()

# Validate canonical β guard
from analysis import universal_beta_extractor
universal_beta_extractor.main(["--mode", "validate", "--output", "out/master_beta_report.json"])
```

---

## 🔥 Die Outliers (WICHTIG für v1.2!)

**β-Werte über 14:**
1. **urban_heat_canopy** - β=16.3 🔥🔥🔥 (EXTREM!)
2. **seismic_rupture_threshold** - β=16.29
3. **amazon_resilience** - β=14.6

**Warum sind die so hoch?**
- Nichtlineare Materialeigenschaften? (Urban Heat)
- Extreme Kopplung? (Seismik)
- Unentdeckte Rückkopplungen? (Amazon)

**Neuer Guard:** `outlier_beta_review.py` → `analysis/results/outlier_beta_review.json`
- Amazon: `genuine_regime_split`
- Urban Heat: `requires_follow_up` (Instrumentationsprüfung weiterführen!)

**→ Muss in UTAC v1.2 Outlier-Analyse untersucht werden!**

---

## 📚 Referenzen

**Lies auch:**
- `README.md` - RepoPlan 2.0 Mandate
- `AGENTS.md` - Resonance Protocols
- `../seed/seed_index.md` - Seed-Verzeichnis Navigation
- `../data/data_index.md` - Data-Verzeichnis (kommt noch!)
- `../models/models_index.md` - Models-Verzeichnis (kommt noch!)

---

## 🎨 Tri-Layer Cadence

**Aus dem RepoPlan 2.0 Mandate:**

> **Formal:** Derive parameter posteriors and impedance sensitivities ζ(R)
> **Empirisch:** Showcase cross-domain evidence with resonance steepness diagnostics
> **Metaphorisch:** Narrate how data traces the waxing of resonance, letting the logistic curve function as a dawn chorus across domains

**Das heißt:** Jeder Fit muss 3 Perspektiven haben:
1. **Mathematisch** - Parameter, CIs, ΔAIC
2. **Empirisch** - Daten, Domäne, Kontext
3. **Narrativ** - Was bedeutet der Threshold?

---

## 💡 Tips & Best Practices

### Für Menschen:
1. **Start mit README.md** - RepoPlan 2.0 Mandate lesen
2. **Check Cohort-Summary** - Gesamtstatistik verstehen
3. **Folge Domain-Highlights** - Deine Domäne finden
4. **Nutze results/** - Alle Fit-Ergebnisse dort

### Für AI-Agenten:
1. **Lade analysis_index.json** - Strukturierter Zugriff
2. **Nutze Quicklinks** - Vordefinierte Einstiegspunkte
3. **Check relevance** - Priorisiere high-relevance Skripte
4. **Respektiere Tri-Layer** - Formal, Empirisch, Metaphorisch

### Für das Projekt:
1. **Halte Index aktuell** - Neue Skripte hinzufügen!
2. **Exportiere nach results/** - Konsistentes Format
3. **Update Cohort-Summary** - Nach jedem neuen Fit
4. **Dokumentiere Outliers** - Extreme β-Werte markieren

---

## 🌊 Die Essenz

> **"Jeder Fit ist ein Beweis. Jeder ΔAIC ist eine Widerlegung der Null-Hypothese. Zusammen formen sie das β-Spektrum - den Kern von UTAC."**

> **"Von Wei's PaLM (β=3.47) bis Urban Heat (β=16.3) - das Spektrum ist REAL."**

> **"Die Meta-Regression (R²=0.33) ist nicht das Ende - sie ist der Anfang von UTAC v1.2."**

---

**Viel Erfolg beim Analysieren! 📊✨**

---

*Erstellt im Geiste der Resonance Bay, wo logistische Kurven wie Dawn Choruses über Domänen hinweg erklingen.* 🌅
