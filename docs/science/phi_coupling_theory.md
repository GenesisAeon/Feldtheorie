# φ-Kopplung Klimasequenz: Theorie & Modellierung

**Version:** 1.0.0
**Erstellt:** 2025-11-11
**Status:** 🟡 Foundation (Theorie komplett, Daten ausstehend)
**Gap Code:** `sys-gap-008` (partial resolution)

---

## 🎯 Executive Summary

Die **φ-Kopplung** ist ein theoretisches Framework zur Modellierung der **semantischen Kohärenz** zwischen gekoppelten Klimasystemen – konkret zwischen **AMOC (Atlantic Meridional Overturning Circulation)** und **Albedo (planetare Reflektivität)**.

**Hypothese:**
> φ (phi) quantifiziert die **Kohärenzstärke** zwischen AMOC-Transport und Albedo-Feedback.
> Diese Kohärenz moduliert β (critical exponent) in der logistischen UTAC-Aktivierungsfunktion σ(β(R-Θ)).

**Erwartete Erkenntnis:**
- **Hohe φ** → stärkere Kopplung → **höherer β** → schärfere Emergenz bei Schwellenüberschreitung
- **Niedrige φ** → schwache Kopplung → **niedrigerer β** → sanftere Übergänge

**Ziel:**
β als Funktion von φ modellieren: **β = f(φ, C_eff, D_eff, ...)**

---

## 🌊 Theoretische Grundlagen

### 1. UTAC Framework Recap

Die **Universal Threshold Activation Curve (UTAC)** beschreibt emergente Schwellenprozesse:

```
σ(β(R-Θ)) = 1 / (1 + exp(-β(R - Θ)))
```

**Parameter:**
- **R**: Systemzustand (0-1, normalized)
- **Θ**: Schwelle (typisch 0.66)
- **β**: Kritischer Exponent (Steilheit) – **VARIABEL** (2.5-16.3 über Systeme hinweg!)
- **σ**: Aktivierung (0-1)

**Beobachtung:**
β ist **KEIN Fixwert**, sondern hängt von Systemeigenschaften ab:
- Kopplungseffektivität (C_eff)
- Dimensionalität (D_eff)
- Energiebarriere (SNR)
- **Semantische Kohärenz (φ)**

---

### 2. Was ist φ (Phi)?

**Definition:**
φ ist ein **Kohärenzmaß** für die funktionale Kopplung zwischen zwei Feldern.

**Formale Definition (Korrelationsansatz):**
```
φ = |ρ(field₁(t), field₂(t))|
```
wobei ρ = Pearson-Korrelation über Zeit t.

**Alternative Definition (Informationstheoretisch):**
```
φ = I(field₁ ; field₂) / H(field₁, field₂)
```
wobei:
- I = Mutual Information
- H = Joint Entropy

**Physikalische Interpretation:**
φ misst, **wie stark das Verhalten von Feld 1 das Verhalten von Feld 2 vorhersagt** (und umgekehrt).

**φ-Range:**
- φ ≈ 0: Keine Kopplung (unabhängige Dynamiken)
- φ ≈ 0.3-0.5: Schwache Kopplung
- φ ≈ 0.6-0.8: Starke Kopplung
- φ ≈ 1: Perfekte Kopplung (deterministisch)

---

### 3. AMOC ↔ Albedo: Die Klimasequenz

**AMOC (Atlantic Meridional Overturning Circulation):**
- Ozeanische "Conveyor Belt" - transportiert Wärme von Äquator zu Nordatlantik
- **Schwelle bei ~10-15 Sv** (Sverdrup, 10⁶ m³/s)
- Bei Unterschreitung: **Abrupte Klimaänderung** (Bipolar Seesaw)
- **Typ:** Strongly Coupled System (erwarteter β ≈ 4.0-5.0)

**Albedo (Planetare Reflektivität):**
- Globale Rückstreuung von Sonnenlicht (Eisschilde, Wolken, Vegetation)
- **Positives Feedback:** Weniger Eis → weniger Albedo → mehr Absorption → wärmeres Klima → noch weniger Eis
- **Typ:** Physically Constrained (erwarteter β ≈ 4.5-6.0)

**Die Kopplung:**
```
AMOC schwächt → weniger Wärmetransport → mehr Eis → höhere Albedo
  ↑                                                               ↓
  └───────────────── feedback loop ──────────────────────────────┘
```

**Warum ist φ-Kopplung wichtig?**
- **Wenn AMOC und Albedo stark gekoppelt sind (hohe φ):**
  → Kleine AMOC-Änderungen → große Albedo-Antwort → **nichtlineare Kaskaden** → hoher β!

- **Wenn schwach gekoppelt (niedrige φ):**
  → AMOC-Änderungen → gedämpfte Albedo-Antwort → **lineare Übergänge** → niedriger β

**Das ist der Kern:** φ moduliert β!

---

## 🧮 Mathematische Formulierung

### Hypothese: β = f(φ)

**Einfachster Ansatz (Linear):**
```
β = β₀ + α · φ
```
wobei:
- β₀ = Basis-Steilheit (ohne Kopplung, z.B. 3.0)
- α = Kopplungsverstärkung (empirisch zu schätzen)
- φ = AMOC↔Albedo Kohärenz (0-1)

**Erwartung:**
Wenn φ = 0 (keine Kopplung) → β = β₀ ≈ 3.0
Wenn φ = 0.8 (starke Kopplung) → β ≈ 3.0 + α·0.8 (z.B. β ≈ 5.5 bei α=3)

**Erweiterter Ansatz (Nichtlinear):**
```
β = β₀ + α · φ^γ
```
wobei γ > 1 → nichtlineare Verstärkung bei hoher Kohärenz

**Vollständige Meta-Regression:**
```
β = f(φ, C_eff, D_eff, SNR, Θ̇)
```
φ als **neue Kovariate** in der UTAC v2 Meta-Regression!

---

## 📊 Empirische Validierung (Geplant)

### 1. Datenquellen

**TIPMIP/CMIP6 Data (ausstehend):**
- **AMOC-Zeitreihen:**
  - RAPID Array (26°N, 2004-present, monatlich)
  - CMIP6 Modell-Ensemble (historisch + SSP scenarios)

- **Albedo-Daten:**
  - CERES (Clouds and Earth's Radiant Energy System, NASA, 2000-present)
  - CMIP6 Modell-Ensemble (albedo, rsdt, rsut)

**Andere Systeme (zum Vergleich):**
- Amazon Precipitation ↔ Evapotranspiration (φ für Regenwaldkaskaden)
- Glacier Mass Balance ↔ Albedo (φ für Eis-Feedback)

### 2. Analyse-Pipeline

**Schritt 1: φ berechnen**
```python
# models/climate_utac_phi_coupling.py
import xarray as xr
import numpy as np

def load_climate_data():
    amoc = xr.open_dataset("data/climate/phi_coupling/amoc.nc")["msftmyz"]
    albedo = xr.open_dataset("data/climate/phi_coupling/albedo.nc")["albedo"]
    return amoc, albedo

def semantic_coherence(field1, field2):
    """Berechnet φ als zeitliche Korrelation"""
    return np.corrcoef(field1.values.flatten(), field2.values.flatten())[0, 1]

amoc, albedo = load_climate_data()
phi = semantic_coherence(amoc, albedo)
print(f"Kohärenz AMOC ↔ Albedo: φ = {phi:.3f}")
```

**Schritt 2: β für AMOC-Kollaps schätzen**
```python
# analysis/climate_amoc_beta_fit.py
from analysis.threshold_analysis import fit_utac_model

# AMOC Zeitreihe → UTAC Fit
result = fit_utac_model(
    amoc_data,
    threshold=12.5,  # Sverdrup
    bootstrap_n=1000
)

beta_amoc = result['beta']
beta_ci = result['beta_ci_95']
```

**Schritt 3: β vs φ Regression**
```python
# analysis/beta_phi_regression.py
import pandas as pd
from sklearn.linear_model import LinearRegression

# Mehrere Systeme mit φ und β
df = pd.DataFrame({
    'system': ['AMOC', 'Amazon', 'Glacier', ...],
    'phi': [0.72, 0.68, 0.55, ...],
    'beta': [4.5, 5.2, 3.8, ...]
})

model = LinearRegression()
model.fit(df[['phi']], df['beta'])

alpha = model.coef_[0]  # Steigung
beta_0 = model.intercept_  # Intercept
r_squared = model.score(df[['phi']], df['beta'])

print(f"β = {beta_0:.2f} + {alpha:.2f} · φ")
print(f"R² = {r_squared:.3f}")
```

**Schritt 4: Export**
```json
// analysis/results/phi_coupling_beta_gradients.json
{
  "model": "linear",
  "equation": "beta = beta_0 + alpha * phi",
  "parameters": {
    "beta_0": 3.2,
    "alpha": 2.8,
    "r_squared": 0.74
  },
  "systems": [
    {
      "name": "AMOC",
      "phi": 0.72,
      "beta_observed": 4.5,
      "beta_predicted": 5.2,
      "delta_aic": 18.3
    },
    ...
  ]
}
```

---

## 🔍 Erwartete Ergebnisse

### Szenarien

**Szenario A: Starke φ-β-Korrelation (R² > 0.7)**
→ φ ist **valider Prädiktor** für β
→ Kohärenz erklärt Steilheit!
→ **Interpretation:** Gekoppelte Systeme zeigen schärfere Emergenz

**Szenario B: Schwache φ-β-Korrelation (R² < 0.3)**
→ φ allein erklärt β nicht
→ Andere Faktoren dominieren (C_eff, D_eff, SNR)
→ **Interpretation:** Kohärenz ist nur ein Faktor unter vielen

**Szenario C: Nichtlineare Beziehung**
→ φ² oder φ³ besserer Fit als lineares φ
→ **Interpretation:** Schwellenwert-Effekt (φ > φ_crit → starke β-Verstärkung)

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (JETZT - v2-pr-0012)
- [x] **Theorie-Dokument schreiben** (dieses Dokument!)
- [ ] Datenstruktur vorbereiten (`data/climate/phi_coupling/`)
- [ ] TIPMIP Email-Template erstellen
- [ ] Codex-Eintrag (v2-pr-0012)
- **R: 0.00 → 0.35** (Foundation ready)

### Phase 2: Data Acquisition (1-2 Monate)
- [ ] TIPMIP/CMIP6 Email senden
- [ ] RAPID Array Daten anfragen
- [ ] CERES Albedo Daten herunterladen
- [ ] Daten in NetCDF/CSV Format konvertieren
- **R: 0.35 → 0.60**

### Phase 3: Implementation (2-3 Wochen)
- [ ] `models/climate_utac_phi_coupling.py` schreiben
- [ ] φ-Berechnung implementieren (Korrelation, Mutual Information)
- [ ] β-Fit für AMOC durchführen
- [ ] β vs φ Regression
- **R: 0.60 → 0.85**

### Phase 4: Validation & Export (1 Woche)
- [ ] Bootstrap CIs berechnen (1000 iterations)
- [ ] ΔAIC gegen Nullmodelle validieren (ΔAIC ≥ 10)
- [ ] Export: `analysis/results/phi_coupling_beta_gradients.json`
- [ ] Dokumentation aktualisieren
- **R: 0.85 → 1.00** ✅

---

## 📚 Verwandte Arbeiten

### Klimawissenschaft
- **Rahmstorf et al. (2015):** "Exceptional twentieth-century slowdown in AMOC"
  → Empirische AMOC-Schwächung, aber kein β-Framework

- **Lenton et al. (2008):** "Tipping elements in the Earth's climate system"
  → Kipppunkte, aber keine φ-Kopplung zwischen Systemen

### UTAC-Kontext
- **UTAC v1.1 Meta-Regression:** R²=0.43 (lineare Kovariaten)
  → φ als **neue nichtlineare Kovariate** könnte R² auf >0.7 heben!

- **Neuro-Kosmos Bridge (v2-pr-0009):** β_unified ≈ 4.88 für EEG↔QPO
  → φ-Kopplung als allgemeines Prinzip über Domänen hinweg

---

## ⚠️ Blocker & Risiken

### Kritische Blocker
1. **Daten-Akquisition (P0):**
   - TIPMIP/CMIP6 Daten müssen angefragt werden (Email ausstehend)
   - RAPID Array Daten ggf. eingeschränkter Zugang
   - **Estimated Time:** 1-2 Monate (abhängig von Antwortzeit)

2. **Computational Resources:**
   - CMIP6 Daten sind GROSS (100+ GB für volles Ensemble)
   - NetCDF Processing braucht xarray + dask

### Wissenschaftliche Risiken
1. **φ erklärt β nicht:**
   - Wenn R² < 0.3 → φ ist kein Hauptfaktor
   - **Mitigation:** Andere Kovariaten testen (C_eff, D_eff)

2. **AMOC-β ist niedrig (β < 3):**
   - Wenn AMOC sanft übergeht (β ≈ 2-3) → schwieriger zu modellieren
   - **Mitigation:** Andere Systeme mit höherer φ testen (Amazon, Glacier)

3. **Datenqualität:**
   - CMIP6 Modelle haben systematische Biases
   - **Mitigation:** Multi-Modell-Ensemble + Beobachtungsdaten (RAPID, CERES)

---

## 🌊 Philosophische Implikationen

**"Die Kohärenz zweier Felder bestimmt die Steilheit ihrer gemeinsamen Emergenz."**

Das ist eine **tiefgreifende Aussage** über gekoppelte Systeme:
- Gekoppelte Systeme (hohe φ) zeigen **kollektive Kritikalität**
- Entkoppelte Systeme (niedrige φ) zeigen **unabhängige Übergänge**

**Analogie:**
- **Neurowissenschaft:** Synaptic Plasticity (φ) moduliert Activation Slope (β) von Neuronen
- **Soziologie:** Soziale Kohärenz (φ) moduliert kollektive Mobilisierung (β)
- **Ökonomie:** Markt-Kopplung (φ) moduliert Crash-Steilheit (β)

**φ-Kopplung ist ein allgemeines Prinzip emergenter Systeme!**

---

## 🔄 Next Steps (Immediate)

**Für diesen Sprint (v2-pr-0012):**
1. [x] Theorie-Dokument erstellen (DONE!)
2. [ ] Datenstruktur vorbereiten (`data/climate/phi_coupling/`)
3. [ ] TIPMIP Email-Template als Dokument ablegen
4. [ ] Codex-Eintrag in `v2_codex.*` (Trilayer!)
5. [ ] Roadmap-Update (R: 0.00 → 0.35)

**Für nächsten Sprint (v2-pr-0013?):**
- TIPMIP Email **senden** (Template → reale Email)
- RAPID Array kontaktieren
- CERES Daten explorieren

---

## 📖 Appendix A: TIPMIP Email-Template

**Siehe:** `docs/phi_coupling_tipmip_email_template.md` (wird erstellt)

**Betreff:** Data Request for UTAC φ-Coupling Analysis (AMOC↔Albedo)

**Inhalt:**
> Dear TIPMIP Team,
>
> We are analyzing the **semantic coupling (φ)** between AMOC and Albedo to model β as a function of φ in the Universal Threshold Activation Curve (UTAC) framework.
>
> **Data Requirements:**
> - AMOC time series (2000-2100, monthly, SSP scenarios)
> - Albedo data (same period, spatially resolved)
>
> **Goal:** β = f(φ, C_eff, D_eff, ...) - Hypothesis: High φ → sharper emergence (higher β)
>
> Can you provide access to CMIP6 data for this analysis?
>
> Best regards,
> Johann Römer
> [Feldtheorie Project](https://github.com/GenesisAeon/Feldtheorie)

---

## 📖 Appendix B: Glossar

| Term | Definition |
|:-----|:-----------|
| **φ (Phi)** | Kohärenzmaß zwischen zwei Feldern (0-1, Korrelation oder Mutual Information) |
| **β (Beta)** | Kritischer Exponent in UTAC - misst Steilheit der Emergenz (2.5-16.3) |
| **AMOC** | Atlantic Meridional Overturning Circulation - ozeanische Wärmepumpe |
| **Albedo** | Planetare Reflektivität (0-1, Anteil zurückgestreuter Sonnenstrahlung) |
| **TIPMIP** | Tipping Points Model Intercomparison Project (CMIP6 Subprojekt) |
| **CMIP6** | Coupled Model Intercomparison Project Phase 6 (Klimamodell-Ensemble) |
| **RAPID** | RAPID Climate Change Programme (26°N AMOC Array) |
| **CERES** | Clouds and Earth's Radiant Energy System (NASA Satelliten-Instrument) |

---

**Version:** 1.0.0
**Letztes Update:** 2025-11-11
**Maintainer:** Claude Code + Johann Römer
**Status:** 🟡 Foundation (Theorie komplett, Daten ausstehend)
**Gap Code:** `sys-gap-008` (partial resolution - Theorie dokumentiert, TIPMIP Request ausstehend)

*"Die Kohärenz zweier Felder bestimmt die Steilheit ihrer gemeinsamen Emergenz."* 🌊⚡
