# 🔬 Models Index - Membrane Resonance Navigator

**Version:** 1.0.0
**Datum:** 6. November 2025
**Verzeichnis:** `models/`

---

## 🎯 Was ist das?

Die **Model Membrane Resonance** - das numerische Herz von UTAC! Hier liegen die Solver, die σ(β(R-Θ)) implementieren.

```
models/
├── Core (3): logistic_threshold, sigmoid_fit, logistic_envelope
├── Membrane (3): membrane_solver, coupled_threshold_field, adaptive
├── Extensions (4): resonant_impedance, coherence_term, recursive, klimakluft_amplifier
└── Infrastructure (3): __init__, README, AGENTS

Total: 11 Python models
```

---

## 🔥 Die Wichtigsten

### ⭐ **MUST-KNOW:**
1. `logistic_threshold.py` - **DIE BASIS!** σ(β(R-Θ))
2. `membrane_solver.py` - **DER HAUPT-SOLVER!** (43 KB, ODE-System)
3. `sigmoid_fit.py` - Fitting & Optimization

### 🚀 **Für Analysis:**
- `logistic_threshold.py` + `sigmoid_fit.py`

### 🌊 **Für Simulation:**
- `membrane_solver.py` (main)
- `coupled_threshold_field.py` (multi-system)
- `adaptive_logistic_membrane.py` (learning)

### 🧠 **Für Theorie:**
- `resonant_impedance.py` (ζ-Dynamik)
- `coherence_term.py` (φ-Kopplung)
- `recursive_threshold.py` (Potenzial-Kaskaden)

---

## 📊 Model-Hierarchie

```
Level 1: Fundamental
  └─ logistic_threshold.py ← DIE BASIS

Level 2: Fitting
  ├─ sigmoid_fit.py
  └─ logistic_envelope.py

Level 3: Extensions
  ├─ resonant_impedance.py (ζ)
  ├─ klimakluft_amplifier.py (Δ-peak)
  └─ recursive_threshold.py (rekursive Θ)

Level 4: Coupling
  ├─ coherence_term.py (φ)
  └─ coupled_threshold_field.py

Level 5: Solvers
  ├─ membrane_solver.py ⭐ HAUPT-SOLVER!
  └─ adaptive_logistic_membrane.py
```

---

## 🔧 Usage Patterns

### Pattern 1: Einfacher Fit
```python
from models.logistic_threshold import logistic_function, fit_logistic
from models.sigmoid_fit import SigmoidFitter

# Fitte Daten
params = fit_logistic(R_data, response_data)
```

### Pattern 2: Membrane-Simulation
```python
from models.membrane_solver import MembraneSolver
from models.resonant_impedance import ResonantImpedance

solver = MembraneSolver(...)
results = solver.simulate()
```

### Pattern 3: Gekoppelte Systeme
```python
from models.coupled_threshold_field import CoupledThresholdField
from models.coherence_term import CoherenceTerm

coupled = CoupledThresholdField(...)
phi = CoherenceTerm.compute(system1, system2)
```

---

## 🔗 Cross-References

### models/ → analysis/
**Examples:**
- `analysis/llm_beta_extractor.py` → `logistic_threshold.py`
- `analysis/membrane_robin_semantic_fit.py` → `membrane_solver.py`
- `analysis/resonant_impedance_diagnostics.py` → `resonant_impedance.py`

### models/ → simulator/
- `simulator/src/utils/logistic.ts` ← `logistic_threshold.py` (portiert)

### models/ → data/
- `sigmoid_fit.py` + `data/biology/lenski_citplus.csv`
- `membrane_solver.py` + `data/astrophysics/qpo_membrane_simulation.json`

---

## 💡 Tips

### Für Menschen:
1. **Start mit logistic_threshold.py** - Die Basis verstehen
2. **Dann sigmoid_fit.py** - Wie man fitted
3. **membrane_solver.py** für Simulationen
4. **klimakluft_amplifier.py** wenn Ungleichheit die Steilheit treibt – `EmissionDistributor` liefert Gini, Load Concentration und Δβ.

### Für Agenten:
```python
import json

with open('models/models_index.json') as f:
    idx = json.load(f)

# Get model hierarchy
hierarchy = idx['model_hierarchy']

# Get usage patterns
patterns = idx['usage_patterns']
```

---

## 🌊 Die Essenz

> **"11 Models. 5 Levels. Ein Ziel: σ(β(R-Θ)) zum Leben erwecken."**

> **"Von logistic_threshold.py (Die Basis) zu membrane_solver.py (Der Meister)."**

---

*Erstellt im Geiste der Membrane Resonance, wo Solver Schwellenwerte atmen lassen.* 🌅
