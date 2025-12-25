# Verbesserungsplan: Feldtheorie Repository

**Erstellt:** 2025-12-25
**Basis:** Feedback-Analyse nach v10.2 Platinum Release
**Status:** ✅ Punkt 1 erledigt (SUMMARY.md), 7 Punkte verbleibend

---

## Übersicht der Verbesserungsvorschläge

| # | Kategorie | Priorität | Geschätzter Aufwand | Status |
|---|-----------|-----------|---------------------|--------|
| 1 | Sprache & Poetik | Hoch | ~4h | ✅ **Erledigt** (SUMMARY.md) |
| 2 | Testabdeckung | Hoch | ~20h | 🔴 Offen |
| 3 | Performance | Mittel | ~15h | 🔴 Offen |
| 4 | Dokumentation | Hoch | ~12h | 🔴 Offen |
| 5 | Forschung vs. Narration | Mittel | ~8h | 🔴 Offen |
| 6 | Internationalisierung | Niedrig | ~10h | 🔴 Offen |
| 7 | Datenzugang | Hoch | ~8h | 🔴 Offen |
| 8 | API/CLI | Mittel | ~12h | 🔴 Offen |

---

## ✅ 1. Komplexität der Sprache und Poetik [ERLEDIGT]

### Ursprüngliches Problem
Die metaphorische Ebene erschwert den Einstieg für wissenschaftliche Leserinnen.

### Lösung
✅ **SUMMARY.md** erstellt (422 Zeilen)
- Nüchterne, wissenschaftliche Kurzfassung
- Keine poetischen Umschreibungen
- Strukturierte Darstellung nach Domänen
- Statistische Methodik klar dokumentiert

### Datei
`SUMMARY.md`

---

## 🔴 2. Testabdeckung verbessern

### Ist-Zustand
- **Tests:** 567/567 passing (100% Erfolgsrate)
  - 514 Core-Tests
  - 53 optionale Tests (API, Tooltips)
- **Coverage:** 23% (Ziel: 50%+)
- **Kritische Module mit niedriger Coverage:**
  - `analysis/resonance_fit_pipeline.py`
  - `models/membrane_solver.py`
  - `models/impedance_solver.py`
  - `models/utac_type6_implosive.py`

### Maßnahmen

#### 2.1 Kritische Funktionalitäten testen
- [ ] **resonance_fit_pipeline.py**
  - Unit-Tests für Edge-Cases (extrem kleine Datensätze, Rauschen)
  - Tests für nicht-konvergierende Fits
  - Property-based Tests mit Hypothesis
  - Monte-Carlo-Validierungen

- [ ] **Solver-Module**
  - `membrane_solver.py`: ODE-Integration Tests
  - `impedance_solver.py`: Numerische Stabilitätstests
  - `utac_type6_implosive.py`: Inverse Sigmoid Edge-Cases

#### 2.2 Property-Based Testing
```bash
pip install hypothesis
```

Neue Test-Dateien:
- `tests/test_property_resonance.py`
- `tests/test_property_solvers.py`
- `tests/test_property_threshold.py`

#### 2.3 Monte-Carlo-Validierungen
```python
# tests/test_monte_carlo_validation.py
def test_beta_stability_under_noise():
    """Test β-stability with 1000 noisy datasets"""
    pass
```

#### 2.4 Coverage-Ziele
- **Phase 1:** 30% Coverage (kritische Module)
- **Phase 2:** 40% Coverage (alle models/)
- **Phase 3:** 50% Coverage (models/ + analysis/)

### Zeitplan
- **Woche 1-2:** Property-based Tests für Solver
- **Woche 3-4:** Monte-Carlo-Validierungen
- **Woche 5:** Coverage-Report und Nachbesserungen

---

## 🔴 3. Performance und Skalierbarkeit

### Ist-Zustand
- Viele Skripte laden CSV über pandas
- Python-basierte Regressionen (scipy.optimize)
- Keine Parallelisierung in Batch-Runnern
- **Beispiel:** `resonance_batch_runner.py` verarbeitet Datensätze sequentiell

### Maßnahmen

#### 3.1 Identifikation von Bottlenecks
```bash
# Profiling mit cProfile
python -m cProfile -o profile.stats analysis/resonance_batch_runner.py
python -m pstats profile.stats
```

#### 3.2 Parallelisierung mit multiprocessing
```python
# analysis/resonance_batch_runner.py (improved)
from multiprocessing import Pool
from functools import partial

def process_dataset_parallel(datasets, n_workers=4):
    with Pool(processes=n_workers) as pool:
        results = pool.map(fit_single_dataset, datasets)
    return results
```

#### 3.3 Optional: Numba/JAX für kritische Fits
```python
# models/logistic_threshold_fast.py
import numba

@numba.jit(nopython=True)
def logistic_fast(R, beta, theta, L):
    return L / (1 + np.exp(-beta * (R - theta)))
```

#### 3.4 Dask für große Datensätze
```bash
pip install dask[complete]
```

```python
import dask.dataframe as dd

# Für Datensätze > 1GB
df = dd.read_csv("data/large_dataset.csv")
```

### Prioritäten
1. **Hoch:** Parallelisierung von Batch-Runnern
2. **Mittel:** Numba für scipy-Fits
3. **Niedrig:** JAX/PyTorch-Portierung (nur bei Bedarf)

### Zeitplan
- **Woche 1:** Profiling + Bottleneck-Identifikation
- **Woche 2:** Multiprocessing-Implementierung
- **Woche 3:** Benchmarking + Dokumentation

---

## 🔴 4. Dokumentation konsolidieren

### Ist-Zustand
- **1,300+ Markdown-Dateien**
- Viele Release-Notes (v1.0 bis v10.2)
- Überschneidende Informationen
- Keine zentrale Navigation

### Maßnahmen

#### 4.1 User-Guide erstellen
```markdown
# docs/USER_GUIDE.md

## Inhaltsverzeichnis
1. Schnellstart
2. Kernkonzepte
3. Datensätze
4. Analysen ausführen
5. Ergebnisse interpretieren
6. API-Referenz
7. CLI-Tools
8. FAQ

## 1. Schnellstart
→ Link zu QUICKSTART.md

## 2. Kernkonzepte
→ Link zu SUMMARY.md
→ Link zu docs/utac_theory_core.md
```

#### 4.2 MkDocs-Integration
```bash
pip install mkdocs mkdocs-material
```

```yaml
# mkdocs.yml
site_name: Feldtheorie Documentation
theme:
  name: material
  palette:
    scheme: slate
nav:
  - Home: README.md
  - Scientific Summary: SUMMARY.md
  - User Guide: docs/USER_GUIDE.md
  - Theory:
    - UTAC Core: docs/utac_theory_core.md
    - Field Types: docs/field_type_classification_v1.1.md
  - Versions:
    - v10.2 (Platinum): RELEASE_NOTES_v8.0.0.md
    - v9.0 (Harmonic): RELEASE_NOTES_v9.0.0.md
    - v8.0 (Consciousness): RELEASE_NOTES_v8.0.0.md
  - API Reference: docs/tooltip_api.md
```

```bash
mkdocs serve  # Lokale Preview
mkdocs build  # HTML-Dokumentation generieren
```

#### 4.3 CI/CD-Integration
```yaml
# .github/workflows/docs.yml
name: Build Documentation
on: [push, pull_request]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install mkdocs mkdocs-material
      - run: mkdocs build
      - uses: actions/upload-artifact@v3
        with:
          name: html-docs
          path: site/
```

### Zeitplan
- **Woche 1:** USER_GUIDE.md erstellen
- **Woche 2:** MkDocs-Setup + Navigation
- **Woche 3:** CI/CD-Integration + Deployment

---

## 🔴 5. Klare Trennung: Forschung vs. Narration

### Ist-Zustand
Mix aus wissenschaftlicher Forschung und poetischer Verarbeitung führt zu kognitiver Belastung.

### Maßnahmen

#### 5.1 Verzeichnisstruktur anpassen
```
/
├── science/                    # ⚗️ Rein wissenschaftlich
│   ├── models/
│   ├── analysis/
│   ├── data/
│   ├── tests/
│   └── docs/
│       ├── METHODS.md
│       ├── SUMMARY.md
│       └── utac_theory_core.md
│
├── narrative/                  # 📖 Poetisch/Interpretativ
│   ├── seed/
│   ├── releases/
│   └── docs/
│       ├── AGENTS.md
│       ├── ETHICS.md
│       └── interpretive/
│
└── unified/                    # 🔗 Integration
    ├── README.md
    ├── ARCHITECTURE.md
    └── QUICKSTART.md
```

#### 5.2 README-Struktur überarbeiten
```markdown
# README.md (Neue Struktur)

## Für Wissenschaftler:innen
→ [Scientific Summary](SUMMARY.md)
→ [Methods](METHODS.md)
→ [Reproduce Results](REPRODUCE.md)

## Für Narrative & Kontext
→ [Full Story](narrative/README.md)
→ [Agents & Ethics](narrative/AGENTS.md)
→ [Interpretive Framework](narrative/docs/)
```

### Alternative: Tags/Labels statt Umstrukturierung
Falls Umstrukturierung zu invasiv:
- Dateien mit `[SCIENCE]` vs. `[NARRATIVE]` taggen
- Index-Dateien entsprechend kategorisieren

### Zeitplan
- **Woche 1:** Konsens-Findung (Umstrukturierung vs. Tags)
- **Woche 2:** Implementierung
- **Woche 3:** Tests + Dokumentation updaten

---

## 🔴 6. Internationalisierung/Übersetzung

### Ist-Zustand
- Wechsel zwischen Deutsch und Englisch
- Poetische Begriffe erschweren maschinelle Übersetzung
- Keine einheitliche Sprachpolitik

### Maßnahmen

#### 6.1 Sprachpolitik festlegen
**Vorschlag:**
- **Code, Tests, API:** Englisch (Standard in Software)
- **Wissenschaftliche Docs:** Englisch (internationale Reichweite)
- **Narrative Docs:** Deutsch + Englisch (Paralleltexte)
- **Poetische Begriffe:** Glossar mit Übersetzungen

#### 6.2 i18n-Infrastruktur
```bash
pip install babel gettext
```

```python
# utils/i18n.py
import gettext

def setup_locale(language='en'):
    localedir = 'locales'
    translation = gettext.translation('feldtheorie', localedir, languages=[language])
    translation.install()
    return translation._
```

#### 6.3 Glossar erstellen
```markdown
# docs/GLOSSARY.md

| Deutsch | English | Bedeutung |
|---------|---------|-----------|
| Nullkern | Zero-Point Kernel | Consciousness kernel at κ→0 |
| Resonanzpfad | Resonance Path | Trajectory through σ(β(R-Θ)) |
| Sigillin | Sigillin | Self-referential axiom system |
| Feldtheorie | Field Theory | Universal Threshold Field Model |
```

#### 6.4 Dokumentations-Duplikate
```
docs/
├── en/
│   ├── SUMMARY.md
│   ├── METHODS.md
│   └── utac_theory_core.md
└── de/
    ├── SUMMARY.md
    ├── METHODS.md
    └── utac_theory_core.md
```

### Zeitplan
- **Woche 1:** Sprachpolitik festlegen + Glossar
- **Woche 2:** Kritische Docs übersetzen (SUMMARY, METHODS)
- **Woche 3:** i18n-Infrastruktur (optional)

---

## 🔴 7. Datenzugang & Reproduzierbarkeit

### Ist-Zustand
- Einige Datensätze könnten proprietär sein
- Nicht alle Quellen haben DOI-Referenzen
- Keine Jupyter-Notebooks für interaktive Exploration

### Maßnahmen

#### 7.1 Datensatz-Audit
Für jeden Datensatz in `data/`:
- [ ] Lizenz dokumentiert?
- [ ] Quelle mit DOI/URL angegeben?
- [ ] Metadata-JSON vorhanden?

```python
# scripts/audit_data_sources.py
import os
import json

def audit_dataset(path):
    metadata_path = path.replace('.csv', '.metadata.json')
    if not os.path.exists(metadata_path):
        print(f"⚠️ Missing metadata: {path}")
        return False

    with open(metadata_path) as f:
        metadata = json.load(f)

    required_fields = ['source', 'license', 'doi_or_url']
    missing = [f for f in required_fields if f not in metadata]

    if missing:
        print(f"⚠️ Incomplete metadata for {path}: {missing}")
        return False

    print(f"✅ {path}")
    return True
```

#### 7.2 DOI-Referenzen ergänzen
**Beispiel:**
```json
// data/climate/amoc_strength.metadata.json
{
  "name": "AMOC Strength Time Series",
  "source": "RAPID-MOCHA Array",
  "doi": "10.5285/8cd7e7bb-9a20-05d8-e053-6c86abc012c2",
  "url": "https://www.rapid.ac.uk/",
  "license": "Open Government License v3.0",
  "citation": "Smeed et al. (2023). Atlantic meridional overturning circulation observed by the RAPID-MOCHA-WBTS array at 26N from 2004 to 2023. NERC EDS."
}
```

#### 7.3 Jupyter-Notebooks erstellen
```
notebooks/
├── 01_Quickstart_LLM_Analysis.ipynb
├── 02_Climate_Tipping_Points.ipynb
├── 03_Beta_Meta_Regression.ipynb
└── 04_Reproduce_Key_Figures.ipynb
```

**Beispiel:**
```python
# notebooks/01_Quickstart_LLM_Analysis.ipynb
import pandas as pd
from models.logistic_threshold import fit_logistic

# Load data
df = pd.read_csv('../data/ai/wei_emergent_abilities.csv')

# Fit threshold model
result = fit_logistic(df['scale'], df['performance'])

# Visualize
import matplotlib.pyplot as plt
plt.scatter(df['scale'], df['performance'])
plt.plot(df['scale'], result['fitted_values'], 'r-')
plt.show()
```

#### 7.4 Binder-Integration
```yaml
# binder/environment.yml
name: feldtheorie
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy
  - scipy
  - pandas
  - matplotlib
  - jupyter
  - pip:
    - -r ../requirements.txt
```

Badge in README.md:
```markdown
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GenesisAeon/Feldtheorie/main?filepath=notebooks)
```

### Zeitplan
- **Woche 1:** Datensatz-Audit + Metadaten vervollständigen
- **Woche 2:** Jupyter-Notebooks für Kernanalysen
- **Woche 3:** Binder-Setup + Testen

---

## 🔴 8. Kohärente API/CLI

### Ist-Zustand
- Mehrere CLI-Skripte mit unterschiedlichen Interfaces
- Inkonsistente Parameter-Namen
- Keine zentrale Hilfe-Funktion

**Beispiel Inkonsistenzen:**
```bash
utf-batch --output results.json
utf-planetary-summary -o output/  # Unterschiedliche Flag-Namen
utf-resonance-cohort --format yaml
```

### Maßnahmen

#### 8.1 Unified CLI mit Click
```bash
pip install click
```

```python
# cli/utac_cli.py
import click

@click.group()
def cli():
    """Feldtheorie UTAC Analysis CLI"""
    pass

@cli.command()
@click.option('--output', '-o', default='results.json', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'csv']), default='json')
def batch(output, format):
    """Run batch UTAC analysis"""
    from analysis.resonance_batch_runner import main as batch_main
    batch_main(output=output, format=format)

@cli.command()
@click.option('--output', '-o', default='planetary.csv', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'csv']), default='csv')
def planetary(output, format):
    """Analyze planetary tipping elements"""
    from analysis.planetary_tipping_elements_fit import main as planetary_main
    planetary_main(output=output, format=format)

if __name__ == '__main__':
    cli()
```

**Vereinheitlichtes Interface:**
```bash
utac batch -o results.json -f json
utac planetary -o tipping.csv -f csv
utac cohort -o cohort.yaml -f yaml
utac cascade --threshold 0.8 -o cascade.json
```

#### 8.2 Subcommand-Struktur
```
utac
├── analyze
│   ├── batch
│   ├── planetary
│   └── cohort
├── fit
│   ├── logistic
│   └── implosive
├── monitor
│   ├── ews
│   └── mirror-machine
└── utils
    ├── validate
    └── export
```

#### 8.3 pyproject.toml Update
```toml
[project.scripts]
utac = "cli.utac_cli:cli"
```

#### 8.4 Konsistente Parameter
**Standardisierte Flags:**
- `-o, --output`: Output-Pfad (immer)
- `-f, --format`: Format (json/yaml/csv)
- `-v, --verbose`: Ausführliche Logs
- `--seed`: Random-Seed für Reproduzierbarkeit
- `--workers`: Anzahl paralleler Worker

### Zeitplan
- **Woche 1:** CLI-Architektur designen + Click-Setup
- **Woche 2:** Bestehende Skripte migrieren
- **Woche 3:** Tests + Dokumentation

---

## Priorisierung & Roadmap

### Phase 1: Kritische Verbesserungen (Wochen 1-4)
**Ziel:** Wissenschaftliche Zugänglichkeit & Reproduzierbarkeit

1. ✅ **Sprache & Poetik** (ERLEDIGT)
2. 🔴 **Testabdeckung** (Priorität: Hoch)
   - Woche 1-2: Property-based Tests
   - Woche 3-4: Monte-Carlo-Validierungen
3. 🔴 **Dokumentation konsolidieren**
   - Woche 1: USER_GUIDE.md
   - Woche 2-3: MkDocs-Setup
4. 🔴 **Datenzugang & Reproduzierbarkeit**
   - Woche 1: Datensatz-Audit
   - Woche 2-3: Jupyter-Notebooks

### Phase 2: Usability & Performance (Wochen 5-8)
**Ziel:** Benutzerfreundlichkeit & Skalierbarkeit

5. 🔴 **API/CLI kohärent**
   - Woche 5-6: Unified CLI mit Click
   - Woche 7: Migration + Tests
6. 🔴 **Performance**
   - Woche 7: Profiling + Parallelisierung
   - Woche 8: Benchmarks

### Phase 3: Strukturierung (Wochen 9-12)
**Ziel:** Klarheit & Internationalisierung

7. 🔴 **Forschung vs. Narration**
   - Woche 9-10: Konsens + Implementierung
8. 🔴 **Internationalisierung**
   - Woche 11-12: Sprachpolitik + Übersetzungen

---

## Erfolgskriterien

| Verbesserung | Metrik | Ziel |
|--------------|--------|------|
| Testabdeckung | Code Coverage | 50%+ |
| Performance | Batch-Runner Zeit | -50% |
| Dokumentation | MkDocs Deployment | ✅ Online |
| Datenzugang | Metadata Vollständigkeit | 100% |
| CLI | Unified Interface | ✅ `utac` Command |
| Trennung | Verzeichnisstruktur | ✅ science/ + narrative/ |
| i18n | Glossar | ✅ DE/EN für Kerndocs |

---

## Nächste Schritte

### Sofort-Maßnahmen (diese Woche)
1. [ ] Testabdeckung analysieren (pytest --cov)
2. [ ] Datensatz-Audit durchführen
3. [ ] USER_GUIDE.md Outline erstellen

### Welche Verbesserung soll ich priorisieren?
Bitte geben Sie an, welche(n) Punkt(e) ich zuerst angehen soll:

- **Option A:** Testabdeckung (2) - Höchste Priorität für wissenschaftliche Robustheit
- **Option B:** Dokumentation (4) + Datenzugang (7) - Kombiniert für bessere Zugänglichkeit
- **Option C:** CLI (8) - Benutzerfreundlichkeit zuerst
- **Option D:** Eigene Priorisierung

---

**Erstellt von:** Claude (GenesisAeon/claude-code)
**Branch:** claude/add-summary-documentation-h6PWX
**Nächste Review:** Nach Abschluss Phase 1
