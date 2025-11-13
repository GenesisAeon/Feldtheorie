# arXiv Submission Package - "Emergent Steepness"

**Paper Title:** Emergent Steepness: Microscopic Derivation of UTAC β from J/T

**Authors:** [To be filled]

**Date:** 2025-11-13

---

## 📦 Package Contents

### Main Paper
- `emergent_steepness.tex` - Main LaTeX source
- `references.bib` - Bibliography (BibTeX)

### Figures (PDF, 300 DPI)
- `figures/figure1_utac_overview.pdf` - UTAC Overview (4 panels)
- `figures/figure3_abm_results.pdf` - ABM Results (3 panels)
- `figures/figure4_meta_regression.pdf` - Meta-Regression (2 panels)
- `figures/figure5_phi_scaling.pdf` - Φ^(1/3) Scaling (2 panels)
- `figures/figureS1_noise_robustness.pdf` - Noise Robustness (Supplementary)

### Supplementary Material
- `supplementary/supplementary_information.md` - Full supplementary information
  - Theoretical derivations (RG, Information Theory)
  - Complete 36-system dataset table
  - ABM pseudocode
  - Meta-regression diagnostics

---

## 🚀 Compilation Instructions

### Option 1: Overleaf (Recommended)
1. Upload all files to Overleaf
2. Set compiler to `pdflatex`
3. Compile: Main document → Bibliography → Main document (2x)

### Option 2: Local LaTeX
```bash
pdflatex emergent_steepness.tex
bibtex emergent_steepness
pdflatex emergent_steepness.tex
pdflatex emergent_steepness.tex
```

### Required LaTeX Packages
- `amsmath, amssymb` - Mathematics
- `graphicx` - Figures
- `natbib` - Bibliography
- `hyperref` - Links
- `caption, subcaption` - Figure captions
- `xcolor` - Colors
- `geometry` - Page layout

---

## 📊 Key Results

**Meta-Regression v4:**
- n = 36 systems across 11 domains
- Adjusted R² = 0.665
- p-value = 0.0005
- β range: 1.22 - 18.47

**RG Microscopic Derivation:**
- β emerges from J/T (coupling-to-noise ratio)
- ABM validation: 21/21 tests passed
- Proof-of-concept: β = 3.25 (Theory: 4.21, 23% deviation)

**Φ^(1/3) Scaling:**
- Universal fixpoint at Φ³ = 4.2361
- Convergence accuracy: 0.31%

---

## 🔬 Reproducibility

All code, data, and validation scripts available at:
- GitHub: [Repository URL]
- Zenodo: [DOI when published]

**Validation Pipeline:**
- `scripts/validate_phase2.py` - RG Phase 2 validation
- `scripts/generate_all_figures.py` - Figure regeneration
- `.github/workflows/validation.yml` - CI/CD pipeline
- `Dockerfile` - 1-click reproduction environment

**Run validation:**
```bash
make reproduce
```

---

## 📝 Submission Checklist

- [x] Main LaTeX source (`emergent_steepness.tex`)
- [x] Bibliography (`references.bib`)
- [x] All figures (5 main + 1 supplementary) as PDF
- [x] Supplementary information
- [ ] Author information & affiliations (to be added)
- [ ] Acknowledgments section (to be completed)
- [ ] Funding information (if applicable)
- [ ] Conflict of interest statement
- [ ] Data availability statement
- [ ] Code availability statement

---

## 🎯 Target Journals

**Primary:**
- Physical Review E (Statistical Physics)
- Chaos (AIP)
- Frontiers in Physics (Complex Systems)

**Alternative:**
- PLOS ONE (Interdisciplinary)
- Scientific Reports (Nature)

---

## 📧 Contact

[Author contact information to be added]

---

**Generated:** 2025-11-13
**Version:** V2.0
**Status:** Ready for author review & submission
