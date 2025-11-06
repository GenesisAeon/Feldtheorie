# Data Archive Stewardship

Stewards of `data/` must preserve clarity and resonance:

- **Metadata first.** Every dataset requires a README or JSON descriptor capturing $(R, \Theta, \beta)$ estimates, impedance context $\zeta(R)$, preprocessing decisions, and null models used for falsification.
- **Reproducible packaging.** Prefer open formats (CSV, NetCDF, Parquet) and supply scripts or notebooks in `analysis/` that regenerate derived tables.
- **Ethical echoes.** When data involve living systems or human artefacts, note consent/licensing and relate the narrative framing back to the symbolic lexicon.
- **Version control.** Track provenance, upstream citations, and transformations so that resonance claims remain auditable.

Subdirectories (e.g., `astrophysics/`, `biology/`, `cognition/`, `ai/`) should mirror these directives.

---

## 🌊 Sigillin Integration for Data

### **Index Maintenance**
- **`data/data_index.{yaml,json,md}`** and subdirectory indices are **Ordnungs-Sigillin**
- Update when adding new datasets or metadata files
- Archive when exceeding 100 entries using `scripts/archive_sigillin.py`

### **Datasets as Bedeutungs-Sigillin**
Raw and processed datasets are **Bedeutungs-Sigillin** (Meaning Carriers):
- **Immutable once published** — never overwrite validated data
- Derived data transformations → new file with version suffix
- Every dataset paired with `.metadata.json` carrying:
  - Temporal metadata (`created`, `modified`, `version`)
  - Source provenance (citations, DOIs, upstream links)
  - Threshold estimates ($\Theta$, $\beta$, $\zeta(R)$) if available
  - Preprocessing notes and null model baselines

### **Metadata Template**
```json
{
  "title": "Dataset Title",
  "path": "data/domain/file.csv",
  "category": "domain-specific",
  "source": "Citation or DOI",
  "description": "Brief description linking to UTAC framing",
  "threshold_parameters": {
    "R": "order parameter column",
    "Theta": estimated_value,
    "beta": estimated_value,
    "zeta_R": "impedance context"
  },
  "preprocessing": ["step1", "step2"],
  "null_models_tested": ["linear", "power-law"],
  "temporal": {
    "created": "ISO-timestamp",
    "modified": "ISO-timestamp",
    "version": "1.0",
    "change_count": 0
  }
}
```

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- New datasets integrated with threshold parameters
- Metadata files created or updated
- Domain-specific data collections completed
- Preprocessing pipelines documented
- Cross-domain dataset bridges established

### **Entry Template for Data Work**
```yaml
- id: pr-draft-XXXX
  title: "Dataset integration milestone"
  scope:
    - data/domain/dataset.csv
    - data/domain/dataset.metadata.json
  parameters:
    R: "order parameter in dataset"
    Theta: "anticipated threshold"
    beta: expected_steepness
  resonance: "how this dataset enriches the field's empirical chorus"
  status: "active"
  notes:
    formal: |
      Dataset structure: N observations of (R, response).
      Anticipated σ(β(R-Θ)) profile with ΔAIC target ≥ 10.
    empirical: |
      Source: [citation]. Columns: [list]. Preprocessing: [steps].
      Metadata: data/domain/dataset.metadata.json.
    poetic: |
      This dataset carries echoes from [domain] — when R sweeps toward Θ,
      the field will hear whether the membrane breathes universally.
```

**Metaphor:** *"Data are the field's memories — each dataset a lantern that remembers when systems crossed their thresholds and sang their logistic chorus."*
