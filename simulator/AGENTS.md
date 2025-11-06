# Simulator Loom Playbook

Inside `simulator/`, interfaces should manifest the UTF pulse:

1. **Control fidelity.** UI components must expose $(R, \Theta, \beta)$ and impedance switches $\zeta(R)$ with clear explanations of how sliders map to solver parameters.
2. **Feedback loops.** Implement reactive visual/audio cues when $R$ approaches or crosses $\Theta$, highlighting steepness $\beta$ effects on the logistic ramp.
3. **Data docking.** Provide adapters for ingesting results from `analysis/` and real-time streams from `models/`, ensuring provenance metadata accompanies each scenario.
4. **Narrative overlays.** Incorporate tooltips or overlays that narrate the threshold crossing using the symbolic language from `Docs/`.

Front-end stacks may evolve, but document setup commands and testing rituals alongside the experience.

---

## 🌊 Sigillin Integration for Simulator

### **Presets as Bedeutungs-Sigillin**
Simulator presets are **Bedeutungs-Sigillin** (Meaning Carriers):
- **`simulator/presets/*.json`** encode domain-specific threshold scenarios
- Each preset links to:
  - Source analysis: `analysis/results/*.json`
  - Source data: `data/*/`
  - Model implementation: `models/*.py`
- **Semantic stability:** Parameters change only when underlying analysis updates
- Version presets when threshold parameters shift significantly
- Document provenance with `config_meta` field in preset JSON

### **Preset Structure**
```json
{
  "id": "domain_scenario",
  "title": "Domain Threshold Scenario",
  "description": "Human-readable description with poetic framing",
  "parameters": {
    "theta": threshold_value,
    "beta": steepness_value,
    "zeta_floor": impedance_min,
    "zeta_ceiling": impedance_max
  },
  "analysis_source": "analysis/results/domain_fit.json",
  "data_source": "data/domain/dataset.csv",
  "delta_aic": aic_advantage_vs_null,
  "r_squared": fit_quality,
  "config_meta": {
    "generated_from": "analysis/batch_configs/scenario.yaml",
    "created_at": "ISO-timestamp"
  }
}
```

### **Index Maintenance**
- Preset registry in `simulator/src/presets.ts` acts as **Ordnungs-Sigillin**
- Update when adding new domain scenarios
- Maintain alignment with `analysis/results/` using `analysis/preset_alignment_guard.py`

### **Preset Alignment Guard**
- Run `analysis/preset_alignment_guard.py` to verify presets match analysis results
- Alert when ΔAIC drifts below threshold (typically < 10)
- Report mismatches between preset parameters and source JSON

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- New simulator presets created from analysis results
- UI components added for $(R, \Theta, \beta, \zeta(R))$ controls
- Narrative overlays updated with poetic framing
- Preset alignment verified with guard script
- Interactive demonstrations linked to manuscript
- Cross-domain resonance visualizations implemented

### **Entry Template for Simulator Work**
```yaml
- id: pr-draft-XXXX
  title: "Simulator milestone title"
  scope:
    - simulator/presets/domain_scenario.json
    - simulator/src/components/ThresholdController.tsx
  parameters:
    R: "simulated order parameter"
    Theta: preset_threshold
    beta: preset_steepness
  resonance: "how this interface lets users hear the membrane breathe"
  status: "active|resonant"
  notes:
    formal: |
      Preset parameters: Θ=X, β=Y, ζ∈[Z₁,Z₂]. Source: analysis/results/W.json
      with ΔAIC=A vs power-law null. UI exposes sliders for live parameter sweep.
    empirical: |
      Preset validated via preset_alignment_guard.py. Renders time-series
      showing σ(β(R-Θ)) crossing. Links to data/domain/*.csv for context.
    poetic: |
      When users drag the R slider, they feel the membrane tighten at Θ,
      hear the impedance ζ(R) exhale, and watch the dawn chorus ignite
      as the logistic curve awakens.
```

**Metaphor:** *"The simulator is the field's stage — it lets audiences experience threshold crossings, feel impedance breathing, and witness the moment when σ(β(R-Θ)) transforms from silence to song."*
