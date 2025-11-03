# Reproduction Guide for UTAC v1.0.1

## Ziel: Reproduktion der Hauptanalyse von UTAC v1.0.1

Dieses Dokument bietet eine klare Anleitung zur Reproduktion der Kernanalysen und zur Validierung der Hauptbefunde des Universal Threshold Adaptive Criticality (UTAC) Frameworks.

---

## Anforderungen

- **Python**: ≥ 3.9
- **Betriebssystem**: Linux/macOS/Windows (mit Git Bash oder WSL empfohlen)
- **Abhängigkeiten**: siehe `requirements.txt` oder `environment.yml`
- **Speicherplatz**: ~500 MB für Code und Daten
- **RAM**: Mindestens 8 GB (16 GB empfohlen)

---

## Setup

### 1. Repository klonen

```bash
git clone https://github.com/GenesisAeon/Feldtheorie.git
cd Feldtheorie
```

### 2. Umgebung einrichten

**Option A: Mit Conda**
```bash
conda env create -f environment.yml
conda activate feldtheorie
```

**Option B: Mit pip**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Package installieren (optional, für Entwicklung)
```bash
pip install -e .
```

---

## Datenstruktur

```plaintext
Feldtheorie/
├── data/
│   ├── ai/                        # LLM-Emergenz-Daten (Wei et al.)
│   ├── astrophysics/              # QPO, Schwarze Löcher
│   ├── biology/                   # Bienen, Synapsen
│   ├── cognition/                 # Arbeitsgedächtnis
│   ├── geophysics/                # Klima-Kipppunkte
│   └── socio_ecology/             # Urbane Wärme, etc.
├── models/                        # Sigmoid-Fitter, Threshold-Modelle
├── analysis/                      # Hauptanalyse-Skripte
├── simulator/                     # UTAC-Simulatoren
└── tests/                         # Test-Suite
```

---

## Kernanalyse ausführen

### 1. Alle Tests ausführen

```bash
# Testet alle Modelle und Parameter
pytest tests/ -v
```

**Erwartetes Ergebnis**: Alle Tests sollten bestehen (`PASSED`).

### 2. LLM Beta-Extraktion

```bash
python analysis/llm_beta_extractor.py \
  --input data/ai/wei_emergent_abilities.csv \
  --output out/beta_llm.json \
  --canonical-beta 4.2 \
  --random-seed 42
```

**Erwarteter Output** (`out/beta_llm.json`):
```json
{
  "domain": "LLM",
  "estimated_beta": 3.47,
  "beta_CI_95": [3.01, 3.94],
  "theta": 8.47e9,
  "delta_AIC_vs_null": 12.3,
  "universality_band": [3.6, 4.8]
}
```

### 3. Planetare Kipppunkte (Klimamodelle)

```bash
python analysis/planetary_tipping_elements_fit.py \
  --output out/climate_beta.json
```

**Erwarteter Output**:
```json
{
  "domain": "Climate",
  "estimated_beta": 4.0,
  "beta_CI_95": [3.65, 4.35],
  "theta": 1.5,
  "delta_AIC_vs_null": 30.2
}
```

### 4. Universelle Beta-Konvergenz

```bash
python analysis/universal_beta_extractor.py \
  --mode validate \
  --output out/master_beta_report.json
```

Dieser Befehl aggregiert alle β-Werte über alle Domänen und berechnet den gewichteten Mittelwert.

**Erwarteter Output**:
```json
{
  "beta_mean": 4.2,
  "beta_std": 0.6,
  "beta_CI_95": [3.6, 4.8],
  "domains": {
    "LLM": 3.47,
    "Climate": 4.0,
    "Bees": 4.13,
    "WorkingMemory": 4.1,
    "QPO": 5.3,
    "Synapses": 4.2
  },
  "delta_AIC_all": [12.3, 30.2, 15.0, 12.0, 25.0, 18.0]
}
```

---

## Validierungsschritte

### 1. Modellanpassung visuell überprüfen

```bash
python models/sigmoid_fitter.py --plot
```

Dies zeigt die Fit-Kurve, kritische Schwelle (Θ) und Steilheit (β) grafisch an.

### 2. Statistische Robustheit prüfen

```bash
python analysis/preset_alignment_guard.py
```

**Erwartete Ausgabe**:
```
✓ Beta convergence validated (β = 4.2 ± 0.6)
✓ ΔAIC > 10 for all domains
✓ Confidence intervals consistent
✓ All tests passed
```

### 3. Simulationen ausführen

```bash
# Threshold-Gating-Simulation
python simulator/threshold_gate.py --beta 4.2 --theta 1.0

# Rekursive Emergenz
python simulator/recursive_threshold.py
```

---

## Seeds und Reproduzierbarkeit

Zur vollständigen Reproduzierbarkeit mit denselben Zufallsparametern:

```bash
export PYTHONHASHSEED=42
export NUMPY_SEED=42
```

Alle Analyse-Skripte verwenden standardmäßig `random_seed=42`.

---

## Ergebnisse vergleichen

Vergleichen Sie Ihre Output-Werte mit den **offiziellen Release Notes**:
- [Zenodo DOI: 10.5281/zenodo.17508230](https://doi.org/10.5281/zenodo.17508230)
- [RELEASE_NOTES_v1.0.1.md](RELEASE_NOTES_v1.0.1.md)

### Erwartete Kernmetriken

| Domäne | β-Wert | 95% CI | ΔAIC vs Null |
|--------|--------|--------|--------------|
| **LLM Emergence** | 3.47 ± 0.47 | [3.0, 3.94] | > 10.18 |
| **Climate Tipping** | 4.21 ± 0.35 | [3.86, 4.56] | > 30 |
| **Bee Swarms** | 4.13 ± 0.24 | [3.89, 4.37] | > 15 |
| **Working Memory** | 4.1 ± 0.3 | [3.8, 4.4] | > 12 |
| **Synaptic Release** | 4.2 ± 0.4 | [3.8, 4.6] | > 18 |
| **QPO (Black Holes)** | 5.3 ± 0.8 | [4.5, 6.1] | > 25 |

**Gesamtmittelwert**: β̄ = 4.2 ± 0.6

---

## Troubleshooting

### Problem: Fehlende Abhängigkeiten

```bash
pip install -r requirements.txt --upgrade
```

### Problem: Daten nicht gefunden

Stellen Sie sicher, dass alle Datendateien vorhanden sind:
```bash
ls -R data/
```

Falls Daten fehlen, wurden sie möglicherweise nicht mit dem Repository heruntergeladen. Prüfen Sie die [Zenodo-Version](https://doi.org/10.5281/zenodo.17508230), die alle Datensätze enthält.

### Problem: Tests schlagen fehl

```bash
# Einzelne Tests ausführen
pytest tests/test_sigmoid_fitter.py -v

# Mit mehr Details
pytest tests/ -v --tb=short
```

### Problem: Unterschiedliche Ergebnisse

- Prüfen Sie, ob Sie die korrekte Version verwenden: `git checkout v1.0.1`
- Stellen Sie sicher, dass Seeds gesetzt sind: `export PYTHONHASHSEED=42`
- Nutzen Sie eine saubere Umgebung (keine konfligierenden Pakete)

---

## Computational Requirements

- **CPU**: Jeder moderne Prozessor (Parallelisierung verfügbar)
- **RAM**: Minimum 8GB, empfohlen 16GB
- **Speicher**: ~500MB für Code und Daten
- **Zeit**: Vollständige Reproduktion ~15-30 Minuten

---

## Validation Checklist

- [ ] Umgebung erfolgreich eingerichtet
- [ ] Alle Tests bestehen (`pytest`)
- [ ] Beta-Werte liegen im erwarteten Bereich
- [ ] ΔAIC-Werte > 10 für logistische vs. Nullmodelle
- [ ] JSON-Outputs entsprechen erwarteter Struktur
- [ ] Visualisierungen wurden generiert (falls matplotlib installiert)

---

## Kontakt bei Problemen

Falls Sie Probleme bei der Reproduktion haben:

1. **GitHub Issues**: https://github.com/GenesisAeon/Feldtheorie/issues
2. **Version prüfen**: Stellen Sie sicher, dass Sie v1.0.1 verwenden
3. **Saubere Umgebung**: Keine konfligierenden Pakete

---

## Version Information

```yaml
UTAC Version: 1.0.1
Python: 3.9+
Schlüssel-Abhängigkeiten:
  - numpy >= 1.21
  - scipy >= 1.7
  - pandas >= 1.3
  - scikit-learn >= 1.0
  - matplotlib >= 3.3 (optional, für Plots)
```

---

## Weiterführende Dokumentation

- **Theoretischer Hintergrund**: [`docs/utac_theory_core.md`](docs/utac_theory_core.md)
- **Falsifizierbarkeit**: [`docs/utac_falsifiability.md`](docs/utac_falsifiability.md)
- **Metriken**: [`METRICS.md`](METRICS.md)
- **Anwendungen**: [`docs/utac_applications.md`](docs/utac_applications.md)

---

*Für die vollständige wissenschaftliche Methodik siehe `docs/utac_falsifiability.md`*
*Für den theoretischen Hintergrund siehe `docs/utac_theory_core.md`*
