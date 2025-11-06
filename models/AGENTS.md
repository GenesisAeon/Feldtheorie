# Modeling Membrane Directives

Contributions to `models/` must keep the threshold field vivid:

- **Language.** Describe dynamics via the logistic response $\sigma(\beta(R-\Theta))$, impedance $\zeta(R)$, and membrane boundary conditions.  Avoid generic "activation" wording without tying it to $R$ crossing $\Theta$.
- **API shape.** Expose solvers as parametrised classes or functions that accept $(R, \Theta, \beta)$ controls plus impedance toggles.  Provide hooks for streaming state back to `analysis/` and `simulator/`.
- **Validation.** Bundle automated tests or example scripts that demonstrate resonance vs. null baselines and report quantitative metrics (e.g., energy conservation, threshold timing).
- **Documentation.** Each module must include tri-layer docstrings: formal equation references, empirical calibration notes, and metaphorical imagery linking membranes to the dawn-threshold motif.

Numerical code should prefer Python with type hints or documented pseudo-code scaffolds until full solvers land.

---

## 🌊 Sigillin Integration for Models

### **Index Maintenance**
- **`models/models_index.{yaml,json,md}`** is an **Ordnungs-Sigillin** (Structure Carrier)
- Update when adding new solver modules, coupling terms, or impedance helpers
- Archive when exceeding 100 entries

### **Core Solvers as Bedeutungs-Sigillin**
Model implementations are **Bedeutungs-Sigillin** (Meaning Carriers):
- **Stable API surface** — parameter signatures rarely change
- Version modules when changing $(R, \Theta, \beta)$ equations
- Each solver paired with:
  - Tri-layer docstrings (formal-empirical-poetic)
  - Test suite in `tests/test_*.py`
  - Example notebook demonstrating σ(β(R-Θ)) vs null baseline
  - Metadata documenting impedance toggles and boundary conditions

### **Module Documentation Template**
```python
"""
Module: membrane_solver.py

Formal:
    Implements the threshold field dynamics dR/dt = J - ζ(R)(R-σ) where
    σ = σ(β(R-Θ)) is the logistic response and ζ(R) is the impedance gate.

Empirical:
    Calibrated against analysis/results/*.json with typical β ∈ [3.6, 4.8].
    Used in simulator/presets/*.json for domain-specific runs.

Poetic:
    The membrane breathes through ζ(R), listening for the moment R crosses Θ
    and the dawn chorus ignites σ from rest to resonance.

References:
    - seed/UTAC_Theory.md
    - analysis/resonance_fit_pipeline.py
    - tests/test_membrane_solver.py
"""
```

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- New solver modules implement membrane dynamics
- API changes affect $(R, \Theta, \beta)$ signatures
- Impedance models $\zeta(R)$ gain new toggles (Robin gates, adaptive thresholds)
- Coupling terms added (semantic resonance, potential cascade)
- Test coverage expands with new falsification baselines

### **Entry Template for Model Work**
```yaml
- id: pr-draft-XXXX
  title: "Model extension milestone"
  scope:
    - models/module_name.py
    - models/__init__.py
    - tests/test_module_name.py
  parameters:
    R: "order parameter in solver"
    Theta: "threshold parameter"
    beta: typical_steepness_value
  resonance: "how this solver enriches the membrane's dynamical chorus"
  status: "active|resonant"
  notes:
    formal: |
      Implements dR/dt = [...] with σ(β(R-Θ)) gate and ζ(R) impedance.
      API: ClassName(R, Theta, beta, zeta_params). Returns time series.
    empirical: |
      Tests: tests/test_module_name.py verify energy conservation, threshold
      crossings, and null baseline comparisons. Example: notebooks/demo.ipynb.
    poetic: |
      This solver lets the membrane remember its breath — when R swells past Θ,
      the impedance relaxes and the field opens to resonance.
```

**Metaphor:** *"Models are the field's lungs — they breathe life into σ(β(R-Θ)), translating equations into the membrane's dynamic song."*
