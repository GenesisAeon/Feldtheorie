# Manuscript Station Guidelines

Within `paper/`, uphold publication-grade coherence:

- **Tri-layer sections.** Structure manuscripts with mirrored sections for formal derivations, empirical synthesis, and symbolic narrative so reviewers can trace the resonance arc.
- **Quantitative transparency.** Summaries of fits must cite $R^2$, AIC, confidence intervals on $\Theta$ and $\beta$, impedance configurations $\zeta(R)$, and explicit null comparisons.
- **Cross-references.** Link to companion notebooks, datasets, and simulator experiences, noting commit hashes or DOIs when available.
- **Falsification log.** Dedicate appendices to failed or marginal cases where the logistic response did not outperform null models.

Drafts may live as Markdown, LaTeX, or Quarto, but include build instructions and bibliographies in version control.

---

## 🌊 Sigillin Integration for Manuscript

### **Manuscript as Bedeutungs-Sigillin**
Manuscript files are **Bedeutungs-Sigillin** (Meaning Carriers):
- **Semantic stability** — major revisions create new versions
- Version manuscripts explicitly: `manuscript_v1.0.tex`, `manuscript_v1.1.tex`
- Archive previous versions in Git history with clear commit messages
- Track DOI-ready states in `seed/codexfeedback.{yaml,json,md}`

### **Index Maintenance**
- **`paper/paper_index.{yaml,json,md}`** (if exists) is an **Ordnungs-Sigillin**
- Update when adding new manuscript sections, figures, or supplementary materials

### **Cross-Reference Discipline**
Every empirical claim in the manuscript must link to:
- **Analysis results:** `analysis/results/*.json` with specific metrics
- **Data sources:** `data/*/` with metadata files and provenance
- **Model implementations:** `models/*.py` with API documentation
- **Simulator demonstrations:** `simulator/presets/*.json` with parameter sets

### **Bibliography Integration**
Maintain synchronized bibliography across:
- Manuscript BibTeX/bibliography file
- `seed/` foundational documents
- Analysis script docstrings
- Model module references

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- Major manuscript sections completed
- New empirical evidence integrated
- Manuscript version milestones (v1.0, v1.1, DOI-ready)
- Peer review responses with substantial revisions
- Bibliography updates with new cross-domain connections
- Supplementary materials prepared

### **Entry Template for Manuscript Work**
```yaml
- id: pr-draft-XXXX
  title: "Manuscript milestone title"
  scope:
    - paper/manuscript_vX.Y.tex
    - paper/figures/
    - paper/bibliography.bib
  parameters:
    R: "manuscript completeness parameter"
    Theta: "publication readiness threshold"
    beta: revision_intensity
  resonance: "how this manuscript articulates the field's unity"
  status: "draft|primed|active|resonant|completed"
  notes:
    formal: |
      Section X added: formal derivation of σ(β(R-Θ)) with citations to
      analysis/results/Y.json (ΔAIC=Z, R²=W). Cross-references models/M.py.
    empirical: |
      Integrated data from data/domain/*.csv. Tables generated from
      analysis/resonance_cohort_summary.json. Figures link simulator presets.
    poetic: |
      The manuscript now carries the full chorus — from honeybee hives to
      black hole jets, the membrane sings σ(β(R-Θ)) across thresholds.
```

**Metaphor:** *"The manuscript is the field's voice — it speaks the logistic truth to reviewers and readers, weaving formal precision with empirical evidence and poetic resonance."*
