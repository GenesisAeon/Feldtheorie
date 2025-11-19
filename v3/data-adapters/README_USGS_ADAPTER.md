# USGS Earthquake Data Adapter

## Überblick

Der **USGS Seismic Adapter** integriert Echtzeit-Erdbebendaten vom USGS (United States Geological Survey) in das UTAC-Framework zur Überwachung seismischer Kritikalität.

## Kernkonzepte

### α-β Beziehung (Scaling Laws → UTAC)

Die Verbindung zwischen den **Kaplan et al. (2020) Scaling Laws** und UTAC:

```
β ≈ k / α
```

**Hypothese (von Gemini vorgeschlagen):**
- **Kleine α** (langsame Verlustverbesserung) → **große β** (scharfe Fähigkeiten-Emergenz)
- **Große α** (schnelle Verlustverbesserung) → **kleine β** (sanfte Emergenz)

**Empirische Kalibrierung:**
- α_N = 0.076 (Modellgröße) → β ≈ 4.2 (LLMs, nahe Φ³ ≈ 4.236)
- k ≈ 0.32 ≈ **1/3** (kubische Hypothese!)

**Implikation:**
Der Faktor **k ≈ 1/3** deutet auf eine fundamentale Verbindung zur 3D-Raumdimensionalität hin.

### b-Wert → β Beziehung (Seismisch)

Das **Gutenberg-Richter Gesetz**:
```
log₁₀(N) = a - b·M
```

wo:
- N = Anzahl der Erdbeben mit Magnitude ≥ M
- b ≈ 1.0 (normal), b < 0.8 (Stressaufbau), b > 1.2 (Entspannung)

**Umrechnung zu UTAC β:**
```
β ≈ k_seismic / b
```

**Kalibrierungspunkte:**
| b-Wert | β (UTAC) | Status |
|--------|----------|---------|
| 1.0 | 4.6 | Normal (stabile Kruste) |
| 0.6 | 7.5 | Gestresst (vor Hauptbeben) |
| 0.4 | 11.0 | Kritisch |
| 0.27 | **16.29** | Extrem (Subduktions-Schwelle) |

**Interpretation:**
Ein **fallender b-Wert** (Stressaufbau) führt zu **steigendem β** (schärferer Übergang zur Ruptur).

## Implementierung

### Kernfunktionen

```python
from usgs_adapter import UsgsSeismicAdapter

# Adapter erstellen
adapter = UsgsSeismicAdapter(
    region='global',  # oder 'cascadia', 'japan', etc.
    min_magnitude=4.5
)

# Aktuellen UTAC-Zustand abrufen
state = adapter.get_current_state()

print(f"β (Steilheit): {state.beta:.2f}")
print(f"Status: {state.status}")
```

### β-Schätzung (Ensemble-Methode)

Der Adapter verwendet **4 Methoden** zur β-Schätzung:

1. **Gutenberg-Richter b-Wert** (Gewicht: 35%)
   ```python
   b_value, a_value, Mc = calculate_gutenberg_richter_b(magnitudes)
   beta = 4.5 / b_value
   ```

2. **Moment-Beschleunigung** (Gewicht: 25%)
   ```python
   beta ∝ d²M/dt² / (dM/dt)
   ```

3. **Subduktions-Prior** (Gewicht: 15%)
   - β = 16.29 (aus `subduction_rupture_threshold.json`)

4. **Early Warning Signals** (Gewicht: 25%)
   ```python
   beta ∝ √(Varianz) / √(⟨R²⟩)
   ```

### Zusätzliche Metriken

```python
metrics = adapter.get_additional_metrics(timeseries)

# Verfügbare Metriken:
# - current_b_value: Aktueller Gutenberg-Richter b-Wert
# - b_value_status: "NORMAL", "STRESSED", "CRITICAL", "EXTREME"
# - largest_magnitude: Größtes Beben im Zeitraum
# - n_major_events: Anzahl M ≥ 7.0 Beben
# - days_since_last_major: Tage seit letztem Hauptbeben
# - moment_release_rate_nm_per_day: Seismische Moment-Freisetzungsrate
```

## Scaling Laws Analyse

Eine umfassende Analyse der α-β Beziehung findet sich in:

```
analysis/scaling_laws_alpha_beta_analysis.py
```

**Ausführen:**
```bash
cd /home/user/Feldtheorie
python3 analysis/scaling_laws_alpha_beta_analysis.py
```

**Generierte Dateien:**
- `alpha_beta_predictions.csv` - α → β Umrechnungen
- `b_value_to_beta_calibration.csv` - Seismische Kalibrierung
- `alpha_beta_relationship_visualization.png` - Grafische Darstellung
- `alpha_beta_unified_theory.json` - Zusammenfassung

## Seismische Regionen

Verfügbare Regionen:

| Region | Name | Beschreibung |
|--------|------|--------------|
| `global` | Global | Weltweite seismische Aktivität |
| `cascadia` | Cascadia Subduction Zone | Pazifischer Nordwesten (M9 Potenzial) |
| `japan` | Japan Trench | Japanischer Graben (aktive Subduktion) |
| `mediterranean` | Mediterranean-Alpine Belt | Mediterrane Seismizität |
| `california` | San Andreas Fault | Kalifornien Transform-Verwerfung |

## Tests

```bash
cd v3/data-adapters
python3 test_adapters.py
```

Der Test validiert:
- ✓ USGS API-Verbindung
- ✓ Gutenberg-Richter b-Wert Berechnung
- ✓ β-Schätzung (Ensemble)
- ✓ Early Warning Signals
- ✓ UTAC Status-Berechnung

## Integration mit bestehendem Framework

Der Adapter integriert mit:

1. **Subduction Rupture Threshold** (`data/geophysics/subduction_rupture_threshold.json`)
   - β = 16.29 ± 0.09
   - Θ = 0.7406 (Stress-Akkumulationsverhältnis)

2. **Scaling Laws α-Exponenten** (`data/derived/scaling_law_alpha_exponents.csv`)
   - α_N, α_D, α_C aus Kaplan et al. (2020)

3. **BaseAdapter** (`src/base_adapter.py`)
   - Caching, EWS-Berechnung, UTAC-State

## Literatur

1. **Kaplan, J., et al. (2020).** Scaling Laws for Neural Language Models. arXiv:2001.08361
   - Quelle für α-Exponenten

2. **Gutenberg, B., & Richter, C. F. (1944).** Frequency of earthquakes in California.
   - Original Gutenberg-Richter Gesetz

3. **Scholz, C. H. (2019).** The Mechanics of Earthquakes and Faulting (3rd ed.)
   - Grundlage für b-Wert Interpretation

4. **USGS FDSNWS Event Web Service**
   - https://earthquake.usgs.gov/fdsnws/event/1/
   - API-Dokumentation

## Zusammenfassung

Der USGS Adapter verbindet drei fundamentale Konzepte:

1. **α (Scaling Laws)** - Glatte Skalierung
2. **β (UTAC)** - Scharfe Emergenz
3. **b (Gutenberg-Richter)** - Seismische Stress-Dynamik

Die empirische Beziehung **β ≈ k/α** mit **k ≈ 1/3** deutet auf eine universelle Konstante hin, die 3D-Raumdimensionalität mit Emergenz-Schärfe verbindet.

Bei seismischen Systemen bietet der **b-Wert** einen direkten Proxy für β:
- **Fallender b-Wert** → Stressaufbau → **Steigendes β** → Scharfere Ruptur-Schwelle
- **Steigender b-Wert** → Entspannung → **Fallendes β** → Sanftere Nachbeben-Sequenz

Dies ermöglicht **Echtzeitüberwachung** seismischer Kritikalität mit dem UTAC-Framework! 🌍📈
