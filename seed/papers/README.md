# 📄 UTAC Papers

This directory contains scientific papers and publications related to the UTAC framework.

## 📑 Contents

### Main Paper: Emergent Steepness
**File:** `emergent_steepness.tex`
**Status:** 🟢 Draft Complete, Ready for arXiv Submission
**Topic:** Microscopic derivation of UTAC β from coupling-to-noise ratio (J/T)

**Key Results:**
- **Meta-Regression v4**: n=36 systems, R²=0.665, p=0.0005
- **RG Microscopic Derivation**: β = 2(J/T) validated via ABM
- **Φ^(1/3) Scaling**: Universal scaling with 0.31% accuracy

### Figures
**Directory:** `figures/`
**Status:** 🟡 Specified, ready for generation

**Main Figures:**
1. **Figure 1**: UTAC Overview (4 panels)
2. **Figure 3**: ABM Results (3 panels)
3. **Figure 4**: Meta-Regression (2 panels)
4. **Figure 5**: Φ^(1/3) Scaling (2 panels)

**Supplementary Figures:**
- S1-S4: Additional validations

### Supplementary Information
**Directory:** `supplementary/`
**File:** `supplementary_information.md`
**Status:** 🟢 Complete

**Contents:**
- Theoretical derivations
- Complete dataset (36 systems table)
- ABM source code with comments
- Additional statistical analyses

## 🚀 Submission Workflow

### For arXiv Submission:

1. **Generate all figures:**
   ```bash
   python scripts/generate_all_figures.py
   ```

2. **Compile LaTeX:**
   ```bash
   cd papers/
   pdflatex emergent_steepness.tex
   bibtex emergent_steepness
   pdflatex emergent_steepness.tex
   pdflatex emergent_steepness.tex
   ```

3. **Create submission package:**
   ```bash
   tar -czf emergent_steepness_arxiv.tar.gz \
     emergent_steepness.tex \
     figures/*.pdf \
     emergent_steepness.bbl
   ```

4. **Upload to arXiv:**
   - Category: physics.data-an (primary)
   - Secondary: cond-mat.stat-mech, cs.AI
   - Title: "Emergent Steepness: Microscopic Derivation of UTAC β from J/T"

## 📊 Citation

If you use this work, please cite:

```bibtex
@article{roemer2025emergent,
  author = {Römer, Johann Benjamin},
  title = {Emergent Steepness: Microscopic Derivation of UTAC β from J/T},
  year = {2025},
  note = {In preparation},
  archivePrefix = {arXiv},
  primaryClass = {physics.data-an}
}
```

## 📝 Version History

| Version | Date | Status |
|---------|------|--------|
| 0.1 | 2025-11-13 | Initial draft from documented sessions |
| 1.0 | TBD | arXiv submission |

## 🔗 Links

- **Main Repository**: https://github.com/GenesisAeon/Feldtheorie
- **Zenodo DOI**: [To be added]
- **arXiv ID**: [To be added after submission]

---

**Maintained by:** Johann Benjamin Römer
**Contact:** See CITATION.cff in main repository
**Last Updated:** 2025-11-13
