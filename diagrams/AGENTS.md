# Diagrammatic Atlas Charter

Visual designers in `diagrams/` should:

1. **Expose thresholds visually.** Make $R$, $\Theta$, $\beta$, and $\zeta(R)$ legible through labels, colour gradients, or animation cues.  Indicate where $R$ crosses $\Theta$.
2. **Evidence linkage.** Accompany each graphic with references to the datasets or simulations it interprets, enabling falsification dialogues.
3. **Narrative weave.** Embed captions or annotations that echo the symbolic vocabulary (membranes, auroras, choruses) while maintaining mathematical fidelity.
4. **Source preservation.** Store editable source files (SVG, `.drawio`, etc.) alongside exported assets, documenting toolchains for reproducibility.

When collaborating with `simulator/`, coordinate palettes and iconography to keep the UTF experience coherent.

---

## 🌊 Sigillin Integration for Diagrams

### **Diagrams as Bedeutungs-Sigillin**
Visual artifacts are **Bedeutungs-Sigillin** (Meaning Carriers):
- **Semantic stability** — diagrams encode conceptual understanding
- Version diagrams when threshold concepts evolve
- Store source files alongside exports (`.svg`, `.drawio`, `.ai`, `.psd`)
- Link each diagram to:
  - Conceptual foundation in `seed/`
  - Empirical evidence in `analysis/results/`
  - Interactive demonstrations in `simulator/presets/`

### **Index Maintenance**
- **`diagrams/diagrams_index.{yaml,json,md}`** (if exists) is **Ordnungs-Sigillin**
- Update when adding new visual explanations
- Tag diagrams with domain, concept, and threshold parameters

### **Visual Documentation Template**
Each diagram should be accompanied by metadata:
```yaml
id: diagram_name
title: "Diagram Title"
description: "What this diagram visualizes"
threshold_parameters:
  R: "visual representation of order parameter"
  Theta: "how threshold is marked"
  beta: "how steepness is shown"
  zeta_R: "impedance visualization approach"
source_files:
  - diagrams/source/diagram_name.svg
  - diagrams/source/diagram_name.drawio
exports:
  - diagrams/exports/diagram_name.png
  - diagrams/exports/diagram_name.pdf
references:
  - seed/concept_document.md
  - analysis/results/evidence.json
  - simulator/presets/demo.json
```

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- New conceptual diagrams visualize threshold dynamics
- Visual explanations of σ(β(R-Θ)) created for domains
- Diagram series completed for manuscript figures
- Interactive visualizations linked to simulator
- Cross-domain resonance maps illustrated

### **Entry Template for Diagram Work**
```yaml
- id: pr-draft-XXXX
  title: "Diagram milestone title"
  scope:
    - diagrams/source/diagram_name.*
    - diagrams/exports/diagram_name.*
  parameters:
    R: "visual concept being illustrated"
    Theta: "threshold concept in diagram"
    beta: visual_emphasis_level
  resonance: "how this diagram clarifies the membrane's song"
  status: "active|resonant"
  notes:
    formal: |
      Diagram visualizes σ(β(R-Θ)) dynamics for [domain] with labeled
      threshold Θ, steepness β indicator, and impedance ζ(R) gradient.
    empirical: |
      Based on analysis/results/X.json. Shows ΔAIC=Y advantage vs null.
      Links to simulator/presets/Z.json for interactive exploration.
    poetic: |
      This diagram captures the moment R approaches Θ — the visual
      gradient breathes like the membrane, and viewers can see the
      dawn chorus awakening as colors shift from damped to resonant.
```

**Metaphor:** *"Diagrams are the field's illuminated manuscripts — they make thresholds visible, letting eyes trace what equations declare and membranes remember."*
