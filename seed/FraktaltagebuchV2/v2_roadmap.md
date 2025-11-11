# 🗺️ UTAC v2.0 Roadmap

**Version:** 1.0.0
**Erstellt:** 2025-11-10
**Status:** R̄=0.50, Θ=0.66, σ(β(R-Θ))≈0.317 (partial activation)

---

## 📊 Übersicht

**Gesamtfortschritt:** 50% der Manifest-Laternen aktiv

```
V2.0 Readiness: ████████░░░░░░░░░░ 40%

Kern-Features:  ███░░░░░░░░░░░░░░░ 18% (1/6)
Erweiterungen:  ░░░░░░░░░░░░░░░░░░  0% (0/3)
Automation:     ██░░░░░░░░░░░░░░░░ 12% (0.25/2)
Tests:          █░░░░░░░░░░░░░░░░░  4% (12/290)
```

**Release Criteria:** R̄ ≥ 0.66 über alle Kern-Features

---

## 📂 Kategorien

1. [✅ Fertig / In Progress](#-fertig--in-progress)
2. [🔴 Kern-Features](#-kern-features-critical-path)
3. [🔵 Erweiterungen](#-erweiterungen-nice-to-have)
4. [⚙️ Automation](#️-automation--cicd)
5. [🧪 Tests](#-tests--stabilität)
6. [🚀 Release Criteria](#-release-criteria)

---

## ✅ Fertig / In Progress

### ✅ v2-feat-done-001: UTAC Sonifikation

**Status:** ✅ COMPLETED (2025-11-09)
**Scope:** `sonification/`
**R=1.00, β=4.8**

**Beschreibung:**
Audio-Tool das β-Spektren in Klang verwandelt - "The Sound of Criticality"

**Deliverables:**
- ✅ `sonification/utac_sonification.py`
- ✅ `sonification/output/demo/*.wav` (5 Field Type Demos)
- ✅ `sonification/README.md`
- ✅ 16 Tests passing

**Features:**
- 5 Field Type Acoustic Profiles (Weakly → Meta-Adaptive)
- 6 Presets: LLM-Emergence, AMOC, Urban Heat, Honeybees, etc.
- CLI + Python API
- Ready für Museen, Planetarien, Galerien

**PR:** #172 (bereits gemerged)

---

### ✅ v2-feat-done-002: Outreach Essays DE/EN

**Status:** ✅ COMPLETED (2025-11-10)
**Scope:** `docs/outreach/`
**R=1.00, β=4.2**

**Beschreibung:**
Essays über epistemischen Kontrollverlust in KI-Forschung

**Deliverables:**
- ✅ `docs/outreach/ai_semantic_maps_de.md`
- ✅ `docs/outreach/ai_semantic_maps_en.md`

**Thema:** "Wenn Maschinen denken, aber Menschen nicht mehr folgen - Warum wir semantische Landkarten brauchen"

**Ready für:** Medium, t3n, Towards Data Science

---

### 🟡 v2-feat-progress-001: Fourier-Analyse Modul

**Status:** 🟡 IN PROGRESS (seit 2025-11-08)
**Scope:** `analysis/`
**R=0.60, β=4.5**

**Beschreibung:**
Spektralanalyse für UTAC Zeitreihen (Frequenzdomäne)

**Deliverables:**
- ✅ `sonification/utac_fourier.py` (Kernmodul fertig!)
- ⏳ `analysis/fourier_analysis.py` (CLI)
- ⏳ `docs/utac_fourier_guide.md`
- ⏳ `analysis/results/frequency_profiles/`

**Next Steps:**
1. CLI-Wrapper schreiben
2. Dokumentation vervollständigen
3. Spektrogramm-Visualisierung

---

## 🔴 Kern-Features (Critical Path)

### 🔴 v2-feat-core-001: UTAC v2 Data Lanterns

**Status:** ❌ PENDING
**Priority:** P0 (CRITICAL)
**Scope:** `data/`
**R=0.20, Θ=0.66, β=4.8**

**Problem:** 4 von 5 Manifest-Datasets fehlen!

**Fehlende Datasets:**
1. ❌ `data/climate/amazon_precip_evapo.nc` + metadata
2. ❌ `data/ocean/amoc_transport.csv` + metadata
3. ❌ `data/neuro_ai/hybrid_activation.csv` + metadata
4. ❌ `data/economy/systemic_thresholds.csv` + metadata

**Aktuell:** Nur Urban Heat fertig (1/5 = 20%)

**Estimated Effort:** 2-4 Wochen

**Blockers:**
- Daten-Akquisition (TIPMIP, RAPID Array, Paper-Extraktion)

**Next Steps:**
1. **AMOC:** RAPID Array Data anfragen ([rapid.ac.uk](https://www.rapid.ac.uk/))
2. **Amazon:** TIPMIP/CMIP6 Request schreiben
3. **Neuro-AI:** Wei et al. (2022) Daten + eigene EEG-Daten
4. **Economy:** Systemic Risk Centre kontaktieren

**Gap Code:** `utac-v2-data-lanterns`

---

### 🔴 v2-feat-core-002: UTAC v2 Analysis Exports

**Status:** ❌ PENDING
**Priority:** P0 (CRITICAL)
**Scope:** `analysis/results/`
**R=0.17, Θ=0.66, β=4.8**

**Problem:** 6 Analysis JSON Exports fehlen!

**Fehlende Exports:**
1. ❌ `analysis/results/amazon_hydro_fit.json`
2. ❌ `analysis/results/amoc_transport_fit.json`
3. ❌ `analysis/results/neuro_ai_beta.json`
4. ❌ `analysis/results/neuro_ai_bootstrap.json`
5. ❌ `analysis/results/economy_threshold_fit.json`
6. ❌ `analysis/results/beta_meta_regression_v2_latest.json`

**Aktuell:** Nur `urban_heat_global_fit.json` fertig (1/6 = 17%)

**Estimated Effort:** 1-2 Wochen (nach Daten)

**Dependencies:** v2-feat-core-001 (braucht Rohdaten zuerst!)

**Next Steps:**
1. Sobald Datasets da sind: `analysis/*_extractor.py` laufen lassen
2. Bootstrap CIs berechnen (1000 iterations)
3. ΔAIC ≥ 10 gegen Nullmodelle validieren
4. JSON Exports in `analysis/results/` speichern

---

### 🔴 v2-feat-core-003: Meta-Regression v2

**Status:** ❌ PENDING
**Priority:** P0 (CRITICAL)
**Scope:** `analysis/`
**R=0.50, Θ=0.70, β=4.2**

**Problem:** Kontinuierliche Kovariaten erklären nur R²≈0.43

**Aktuell:**
- WLS R² ≈ 0.43 (nicht signifikant, p=0.53)
- Bootstrap Median R² ≈ 0.99 (aber within [0.43, 1.00])
- Field Type ANOVA: η²=0.68 (p=0.0025) ✅

**Ziel:** R² ≥ 0.7 (adjusted)

**Estimated Effort:** 1 Woche

**Dependencies:** v2-feat-core-002 (braucht alle β-estimates)

**Approach:**
1. Field Types als Dummies in Regression (One-hot encoding)
2. Hierarchical Model (mixed effects mit field_type als random effect)
3. Random Forest feature importance für Kovariaten-Selektion

**Deliverables:**
- Enhanced `analysis/beta_meta_regression_v2.py`
- `analysis/results/beta_meta_regression_v2_latest.json`
- `docs/meta_regression_v2_report.md`

---

### 🔴 v2-feat-core-004: Neuro-Kosmos Bridge

**Status:** ❌ PENDING
**Priority:** P1
**Scope:** `seed/sigillin/`
**R=0.00, Θ=0.66, β=4.88**

**Beschreibung:**
EEG↔QPO β-coupling Bridge - zeigt UTAC als domain-übergreifendes Prinzip

**Deliverables:**
- `seed/sigillin/neuro_kosmos_bridge.yaml`
- `seed/sigillin/neuro_kosmos_bridge.json`
- `seed/sigillin/neuro_kosmos_bridge.md`
- `simulator/presets/neuro_kosmos_bridge.json`
- (optional) `models/neuro_kosmos_coupling.py`

**Estimated Effort:** 3-5 Tage

**Gap Code:** `mq-sci-gap-008`

**Notes:** Konzeptuell skizziert in `seed/Sigillin_Neuro_Membran_Modell_Plan.txt`

**Next Steps:**
1. Trilayer erstellen (siehe Template in meinem Feedback)
2. Simulator-Preset mit β-coupling Slider
3. Shadow-Sigillin erstellen

---

### 🔴 v2-feat-core-005: φ-Kopplung Klimasequenz

**Status:** ❌ PENDING
**Priority:** P1
**Scope:** `models/`, `data/climate/`
**R=0.00, Θ=0.66, β=4.75**

**Beschreibung:**
AMOC↔Albedo φ-Kopplungs-Modell

**Deliverables:**
- `models/climate_utac_phi_coupling.py`
- `data/climate/phi_coupling/` (TIPMIP/CMIP6 Daten)
- `analysis/results/phi_coupling_beta_gradients.json`
- `docs/phi_coupling_theory.md`

**Estimated Effort:** 2-3 Wochen

**Blockers:**
- TIPMIP Data Request (Email ausstehend)

**Gap Code:** `sys-gap-008`

**Next Steps:**
1. TIPMIP Email senden (Template vorhanden in meinem Feedback)
2. Codex-Eintrag erstellen (pr-draft-0120)
3. Datenstrukturen vorbereiten
4. Theorie-Dokument schreiben

---

### 🔴 v2-feat-core-006: Urban Heat Mechanism

**Status:** ❌ PENDING
**Priority:** P2
**Scope:** `analysis/`, `docs/`
**R=0.00, Θ=0.66, β=16.3 (!)**

**Beschreibung:**
Physikalische Erklärung für extremen β=16.3 Wert bei Urban Heat

**Deliverables:**
- `analysis/urban_heat_storage_mechanism.py`
- `analysis/results/urban_heat_storage_mechanism.json`
- `data/socio_ecology/urban_heat/urban_heat_storage_profiles.csv`
- `data/socio_ecology/urban_heat/urban_heat_storage_profiles.metadata.json`
- `docs/urban_heat_mechanism.md`

**Estimated Effort:** 1-2 Wochen

**Gap Code:** `socio-gap-004`

**Hypothese:** Material-Speicherkoeffizient moduliert β≈16→β≈7.5

**Next Steps:**
1. Literatur zu Urban Heat Island Storage Coefficient
2. Mechanismus formalisieren
3. ΔAIC>20 gegen Nullmodelle validieren

---

## 🔵 Erweiterungen (Nice-to-have)

### 🔵 v2-feat-ext-001: Tooltip-System

**Status:** ❌ PENDING
**Priority:** P2
**R=0.00, β=3.8**

**Beschreibung:**
Interaktive Hover-Tooltipps über Plots (β, Θ, R, CREP, ΔAIC)

**Tech Stack:** D3.js/Plotly + Flask/Node Backend

**Estimated Effort:** 1 Woche

**Deliverables:**
- `simulator/src/components/TooltipOverlay.tsx`
- `docs/tooltip_api.md`
- `examples/tooltip_demo.html`

**Notes:** Aus `seed/NextVersionPlan/Letzte_Zusätze_bis_V2.txt`

---

### 🔵 v2-feat-ext-002: VR Emergenz Hub

**Status:** ❌ PENDING
**Priority:** P3
**R=0.00, β=3.2**

**Beschreibung:**
VR-Kollaborationsraum für Mensch-AI mit UTAC

**Tech Stack:** Unity/Unreal + OpenXR + Python WebSocket Bridge

**Estimated Effort:** 4-6 Wochen (GROSS!)

**Deliverables:**
- `vr/unity_project/`
- `vr/websocket_bridge.py`
- `vr/README.md`

**Notes:** Optional für V2.0, kann auch in v2.1 folgen

---

### 🔵 v2-feat-ext-003: UTAC Modular API

**Status:** ❌ PENDING
**Priority:** P2
**R=0.00, β=4.0**

**Beschreibung:**
REST API für UTAC Module (OpenAPI 3.0)

**Tech Stack:** FastAPI/Flask + OpenAPI + Docker

**Estimated Effort:** 2-3 Wochen

**Endpoints:**
- `POST /api/sonify` → Audio generieren
- `POST /api/analyze` → β-Fit durchführen
- `GET /api/system/:id` → System-Metadaten
- `GET /api/fieldtypes` → Field Type Übersicht
- `POST /api/simulate` → Schwellen-Simulation

**Deliverables:**
- `api/openapi.yaml`
- `api/server.py`
- `api/README.md`

---

## ⚙️ Automation & CI/CD

### ⚙️ v2-feat-auto-001: Guards in CI

**Status:** ❌ PENDING
**Priority:** P1
**R=0.25, β=4.5**

**Problem:** Nur 1 von 4 Guards in CI integriert!

**Guards:**
- ✅ `scripts/sigillin_sync.py` (bereits in `sigillin-health.yml`)
- ❌ `scripts/archive_sigillin.py --recount`
- ❌ `analysis/preset_alignment_guard.py`
- ❌ `analysis/utac_manifest_gap_scan.py`

**Estimated Effort:** 2-3 Tage

**Deliverables:**
- `.github/workflows/guards.yml`

**Next Steps:**
1. YAML für neue Guards schreiben
2. Exit codes richtig setzen
3. Tests schreiben
4. Fail if Δindex > 0 oder gaps > 0

---

### ⚙️ v2-feat-auto-002: Parser → Codex Automation

**Status:** ❌ PENDING
**Priority:** P2
**R=0.00, β=4.2**

**Beschreibung:**
CREP Parser schreibt automatisch in Codex

**Estimated Effort:** 2-3 Tage

**Deliverables:**
- Enhanced `scripts/crep_parser.py` mit `--write-codex` Flag
- `tests/test_crep_parser_codex.py`

**Warum:** Verhindert Codex-Verletzungen (sys-shadow-002)

---

## 🧪 Tests & Stabilität

### 🧪 v2-feat-test-001: Test-Suite Stabilität

**Status:** ❌ PENDING
**Priority:** P0 (CRITICAL!)
**R=0.04, β=5.2**

**Problem:** Tests können nicht collected werden!

**Aktuell:**
```
collected 12 items / 20 errors
```

**Ziel:** 290 tests passing (wie in README angegeben)

**Estimated Effort:** 1 Tag

**Next Steps:**
1. `pytest tests/ -v --tb=short` diagnostics
2. Import errors beheben
3. Relative → absolute imports
4. Testdaten-Fixtures prüfen

**Warum kritisch:** Tests sind σ(β(R-Θ))-Wächter!

---

## 🚀 Release Criteria

### ✅ Required (MUSS)

- [ ] **R̄ ≥ 0.66** über alle `core_features`
- [ ] **Alle P0 features completed**
- [ ] **Tests passing ≥ 80%** (232/290)
- [ ] **ΔAIC ≥ 10** für alle neuen Datasets
- [ ] **Meta-Regression R² ≥ 0.7**
- [ ] **Dokumentation vollständig** (README, CHANGELOG, CITATION)

### 🔵 Optional (Nice-to-have)

- [ ] P2/P3 features (können in v2.1 folgen)
- [ ] Extensions (VR Hub, API)

### 📋 Release Process

1. **Review** aller `v2_codex.*` Einträge
2. **Merge** wichtiger Einträge in `seed/codexfeedback.*`
3. **Update:**
   - `README.md` (v2.0 features)
   - `CITATION.cff` → v2.0
   - `NEWS.md` → Changelog
4. **Zenodo v2.0** Upload + DOI
5. **arXiv v2** Submission
6. **FraktaltagebuchV2/** archivieren oder als Doku behalten

---

## 📊 Current Status Summary

| Kategorie | Fertig | In Progress | Pending | Total | %     |
|:----------|:-------|:------------|:--------|:------|:------|
| Completed | 2      | 1           | 0       | 3     | 100%  |
| Core      | 0      | 0           | 6       | 6     | 0%    |
| Extensions| 0      | 0           | 3       | 3     | 0%    |
| Automation| 0      | 0           | 2       | 2     | 12.5% |
| Tests     | 0      | 0           | 1       | 1     | 4%    |
| **TOTAL** | **2**  | **1**       | **12**  | **15**| **20%**|

**Overall Progress:** 20% (3/15 features done/in-progress)

---

**Version:** 1.0.0
**Letztes Update:** 2025-11-10T23:30:00Z
**Maintained by:** Claude Code + Johann Römer

*"R tastet die Schwelle - lass uns gemeinsam über Θ steigen!"* 🚀
