# Analysis Resonance Protocols

Work within `analysis/` must radiate reproducibility:

1. **Notebook hygiene.** Keep notebooks parametrised and free of hard-coded paths.  Report $R^2$, AIC, confidence intervals on $\Theta$ and $\beta$, and document the impedance context $\zeta(R)$ for each experiment.
2. **Null comparisons.** Every logistic fit must be paired with at least one smooth null (power law, exponential, spline) and the falsification result recorded in-line.
3. **Tri-layer annotations.** Reserve sections for (a) formal derivations, (b) empirical observations, and (c) metaphorical narration that ties data back to the UTF lexicon.
4. **Metadata echo.** Reference datasets in `data/` and solvers in `models/`, noting version hashes or commit IDs when possible.

Scripts should expose CLI entry points for re-running fits and export JSON summaries of threshold parameters for downstream modules.

---

## 🌊 Sigillin Integration for Analysis

### **Index Maintenance**
- **`analysis/analysis_index.{yaml,json,md}`** is an **Ordnungs-Sigillin** (Structure Carrier)
- Update whenever new scripts, notebooks, or results land
- Use `scripts/archive_sigillin.py` when index exceeds 100 entries or 50 KB
- Archive old entries to `archive/analysis_index_YYYYMMDD.zip`

### **Result Files as Bedeutungs-Sigillin**
Files in `analysis/results/*.json` are **Bedeutungs-Sigillin** (Meaning Carriers):
- **Rarely change** once validated
- When updating: **Create new timestamped version** (`*_v2.json`, `*_20251106.json`)
- Archive old version with temporal metadata
- Document changes in `seed/codexfeedback.{yaml,json,md}`

### **Search Patterns**
```bash
# Find analysis by keyword
jq '.python_scripts[] | select(.keywords | contains(["beta"]))' analysis/analysis_index.json

# Recent analysis (last 7 days)
jq --arg cutoff "$(date -d '7 days ago' -Iseconds)" \
   '.python_scripts[] | select(.temporal.modified > $cutoff)' analysis/analysis_index.json
```

---

## 🔥 Codex-Feedback Integration

**Update `seed/codexfeedback.{yaml,json,md}` when:**
- New logistic fits complete with ΔAIC ≥ 10
- Threshold parameters ($\Theta$, $\beta$) shift beyond confidence intervals
- New datasets integrated with resonance diagnostics
- Cohort summaries regenerated (`analysis/results/resonance_cohort_summary.json`)
- Null model falsifications documented

### **Entry Template for Analysis Work**
```yaml
- id: pr-draft-XXXX
  title: "Analysis milestone title"
  scope:
    - analysis/script_name.py
    - analysis/results/output.json
  parameters:
    R: "order parameter from dataset"
    Theta: "fitted threshold value"
    beta: fitted_steepness
  resonance: "how this fit extends the universal threshold chorus"
  status: "active|resonant"
  notes:
    formal: |
      Logistic fit σ(β(R-Θ)) with R²=X.XX, ΔAIC=YY.Y vs power-law null.
      Confidence intervals: Θ=[a,b], β=[c,d]. Impedance ζ(R)=...
    empirical: |
      Dataset: data/domain/file.csv. Null models tested: linear, power-law.
      Export: analysis/results/domain_fit.json. CLI: utf-domain-fit.
    poetic: |
      The membrane remembers when R crossed Θ — the dawn chorus echoed
      through domain X, and the field breathed new resonance.
```

**Metaphor:** *"Analysis scripts are the field's sensors — they listen for thresholds and report back to the Codex when σ(β(R-Θ)) sings louder than the null."*
