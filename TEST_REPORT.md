# Test Suite Report - V6

**Datum:** 2025-11-27
**Branch:** claude/testing-docs-review-01KcWVr6QpZq8FDzgNzwev2n

## Zusammenfassung

- ✅ **530 Tests bestanden** (96.9%)
- ❌ **17 Tests fehlgeschlagen** (3.1%)
- ⚠️ **117 Warnungen**
- 🚫 **1 Test-Datei übersprungen** (test_sonification.py - ImportError)

**Gesamtdauer:** 2 Minuten 8 Sekunden

## Fehlgeschlagene Tests (nach Modul)

### 1. API Tests (1 Fehler)
- `tests/test_api.py::test_health_check` - Tooltip-Assertion fehlgeschlagen

### 2. RG Flow Tests (4 Fehler)
- `test_linear_phi_attractor_converges` - Konvergenz-Problem
- `test_polynomial_flow_symmetry` - Symmetrie-Verletzung
- `test_simulate_convergence` - Simulator konvergiert nicht
- `test_variant_converges[FlowVariant.POLYNOMIAL_FLOW]` - Variant konvergiert nicht

### 3. UTAC Fourier Tests (8 Fehler)
- `test_weakly_coupled` - Klassifikation fehlgeschlagen
- `test_strongly_coupled` - Klassifikation fehlgeschlagen
- `test_high_dimensional` - Klassifikation fehlgeschlagen
- `test_physically_constrained` - Klassifikation fehlgeschlagen
- `test_meta_adaptive` - Klassifikation fehlgeschlagen
- `test_boundary_conditions` - Klassifikation fehlgeschlagen
- `test_complete_pipeline` - Pipeline fehlgeschlagen
- `test_utac_field_type_spectrum` - Spektrum-Analyse fehlgeschlagen

### 4. UTAC Microscopic ABM Tests (1 Fehler)
- `test_full_pipeline_quantum` - Quantum Pipeline fehlgeschlagen

### 5. Wavefunction V6 Tests (3 Fehler)
- `test_wavefunction_normalization` - Normalisierung fehlgeschlagen
- `test_tetrahedral_harmonics_symmetry` - Symmetrie-Problem
- `test_crep_classification_thresholds` - CREP-Index Klassifikation fehlgeschlagen

## Wichtige Warnungen

### Deprecated NumPy Functions
- `np.trapz` ist deprecated → sollte durch `np.trapezoid` ersetzt werden
- Betrifft: `logistic_threshold.py`, `resonant_impedance.py`, `adaptive_membrane_phase_scan.py`

### Pydantic V1 → V2 Migration
- `@validator` → `@field_validator`
- `min_items/max_items` → `min_length/max_length`
- Betrifft: `api/server.py` (mehrere Validatoren)

### NumPy Array Conversion
- Scalar conversion von mehrdimensionalen Arrays ist deprecated
- Betrifft: `models/coherence_term.py:115`

## Bekannte Probleme

1. **Sonification Module:** Import-Fehler verhindert Test-Ausführung
   - `UTACsonifier` kann nicht importiert werden

2. **Test-Markierungen:** `@pytest.mark.slow` ist nicht registriert
   - Betrifft: `test_utac_microscopic_abm.py`

## Empfehlungen

1. **Priorisiert:** Wavefunction V6 Tests fixen (Core-Funktionalität)
2. **Wichtig:** UTAC Fourier Klassifikation überprüfen
3. **Wartung:** NumPy/Pydantic Deprecation Warnings beheben
4. **Optional:** Sonification Module Import reparieren

## Erfolgreiche Test-Bereiche

- ✅ Adaptive Logistic Membrane (alle Tests bestanden)
- ✅ Adaptive Membrane Phase Scan (alle Tests bestanden)
- ✅ Archive Sigillin (alle Tests bestanden)
- ✅ Climate Beta Pipeline (alle Tests bestanden)
- ✅ Coherence Term (alle Tests bestanden)
- ✅ Coupled Threshold Field (alle Tests bestanden)
- ✅ Dynamic Threshold Choir (alle Tests bestanden)
- ✅ Genesis Loader (alle Tests bestanden)
- ✅ Genesis Ψ-Field Integration (alle Tests bestanden)
- ✅ Introspection Validation (alle Tests bestanden)
- ✅ LLM Beta Extractor (alle Tests bestanden)
- ✅ Logistic Envelope (alle Tests bestanden)
- ✅ Logistic Threshold (alle Tests bestanden)
- ✅ Membrane Solver (alle Tests bestanden)
- ✅ Planetary Tipping Summary (alle Tests bestanden)
- ✅ Potential Cascade Lab (alle Tests bestanden)
- ✅ Preset Alignment Guard (alle Tests bestanden)
- ✅ Ψ-Field (alle Tests bestanden)
- ✅ Recursive Threshold (alle Tests bestanden)
- ✅ Resonance Cohort Summary (alle Tests bestanden)
- ✅ Resonance Fit Pipeline (alle Tests bestanden)
- ✅ Resonant Impedance (alle Tests bestanden)
- ✅ Sigmoid Fit (alle Tests bestanden)
- ✅ Sigillin Sync (alle Tests bestanden)
- ✅ Tau Star Delay (alle Tests bestanden)
- ✅ Threshold Dataset Loader (alle Tests bestanden)
- ✅ Tooltip API (alle Tests bestanden)

---

**Generiert von:** Claude Code Test Suite Runner
**Test Framework:** pytest 9.0.1
