# PDF Compilation Guide - manuscript_v1.1.tex

## 🎯 Quick Start (Recommended)

### Method 1: pdfLaTeX (Standard)
```bash
cd paper/
pdflatex manuscript_v1.1.tex
bibtex manuscript_v1.1
pdflatex manuscript_v1.1.tex
pdflatex manuscript_v1.1.tex
```

### Method 2: XeLaTeX (Better Unicode Support)
```bash
cd paper/
xelatex manuscript_v1.1.tex
bibtex manuscript_v1.1
xelatex manuscript_v1.1.tex
xelatex manuscript_v1.1.tex
```

### Method 3: LuaLaTeX (Modern, Fast)
```bash
cd paper/
lualatex manuscript_v1.1.tex
bibtex manuscript_v1.1
lualatex manuscript_v1.1.tex
lualatex manuscript_v1.1.tex
```

---

## ✅ Pre-Compilation Checklist

### Required Files
- [x] `manuscript_v1.1.tex` (main LaTeX file)
- [x] `references.bib` (247 bibliography entries)
- [x] `beta_by_field_type.png` (Figure 1)
- [x] `meta_regression_grid.png` (Figure 2)
- [x] `correlation_heatmap.png` (Figure 3)
- [x] `beta_outlier_analysis.png` (Supplementary)

**Status**: ✅ All files present and validated!

### LaTeX Document Validation
- [x] All `\begin{...}` and `\end{...}` environments matched
- [x] All figure references point to existing files
- [x] No syntax errors detected
- [x] All appendices completed (A, B, C, D)

---

## 📦 Dependencies

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install texlive-full
# or minimal:
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

### macOS
```bash
brew install --cask mactex
# or minimal:
brew install basictex
```

### Windows
Download and install:
- **MiKTeX**: https://miktex.org/download
- **TeX Live**: https://www.tug.org/texlive/

### Docker (Cross-Platform)
```bash
docker run --rm -v $(pwd):/workspace -w /workspace \
  texlive/texlive:latest \
  pdflatex manuscript_v1.1.tex
```

---

## 🔧 Compilation Process Explained

### Pass 1: pdflatex (First Run)
```bash
pdflatex manuscript_v1.1.tex
```
- Processes LaTeX source
- Generates `.aux` file with references
- Creates initial PDF (without bibliography)
- **Expected warnings**: "Citation ... undefined" (normal!)

### Pass 2: bibtex (Bibliography Processing)
```bash
bibtex manuscript_v1.1
```
- Reads `references.bib`
- Processes citations from `.aux` file
- Generates `.bbl` file with formatted references
- **Output**: Should show "247 entries" processed

### Pass 3: pdflatex (Second Run)
```bash
pdflatex manuscript_v1.1.tex
```
- Includes bibliography from `.bbl` file
- Updates cross-references
- **Expected warnings**: "Label(s) may have changed" (normal!)

### Pass 4: pdflatex (Final Run)
```bash
pdflatex manuscript_v1.1.tex
```
- Finalizes all cross-references
- Resolves page numbers
- Generates final PDF
- **Expected**: No warnings!

---

## 📊 Expected Output

### File: `manuscript_v1.1.pdf`
- **Pages**: ~25 pages (including appendices)
- **Size**: ~1.5-2 MB (with embedded figures)
- **Sections**:
  1. Title & Abstract
  2. Introduction
  3. Methods
  4. Results (with 3 figures)
  5. Discussion
  6. Conclusions
  7. References (~247 entries)
  8. **Appendix A**: Complete Dataset Table
  9. **Appendix B**: Covariate Justifications
  10. **Appendix C**: Simulation Details
  11. **Appendix D**: Statistical Analysis Code

---

## 🐛 Troubleshooting

### Error: "File not found: beta_by_field_type.png"
**Solution**: Ensure all PNG files are in the same directory as manuscript_v1.1.tex
```bash
ls *.png  # Should show 4 PNG files
```

### Error: "Undefined control sequence"
**Solution**: Check if all required LaTeX packages are installed
```bash
# Install missing packages (Ubuntu/Debian)
sudo apt-get install texlive-latex-extra texlive-fonts-extra
```

### Error: "Bibliography not found"
**Solution**: Run bibtex BEFORE the final pdflatex passes
```bash
pdflatex manuscript_v1.1.tex  # First pass
bibtex manuscript_v1.1         # Process bibliography
pdflatex manuscript_v1.1.tex  # Second pass
pdflatex manuscript_v1.1.tex  # Final pass
```

### Warning: "Font shape ... not available"
**Solution**: Install additional fonts
```bash
sudo apt-get install texlive-fonts-recommended texlive-fonts-extra
```

### Error: "! LaTeX Error: Too many unprocessed floats"
**Solution**: This shouldn't happen in our manuscript, but if it does:
- Add `\clearpage` before problematic sections
- Or use `\usepackage{morefloats}` in preamble

---

## 🎨 Output Validation

### After successful compilation, check:
```bash
# PDF should exist and be reasonable size
ls -lh manuscript_v1.1.pdf
# Expected: ~1.5-2 MB

# Verify PDF has correct number of pages
pdfinfo manuscript_v1.1.pdf | grep Pages
# Expected: Pages: ~25

# Check if figures are embedded
pdfimages -list manuscript_v1.1.pdf
# Expected: 3-4 images listed
```

### Visual Inspection Checklist:
- [ ] Title page displays correctly
- [ ] Abstract is complete
- [ ] All 3 main figures render properly
- [ ] Tables in appendices are formatted correctly
- [ ] Bibliography has 247 entries
- [ ] Cross-references work (click on citations)
- [ ] Page numbers are sequential
- [ ] No missing symbols or garbled text

---

## 🚀 Clean Build (If Something Goes Wrong)

```bash
# Remove all auxiliary files
rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot

# Start fresh
pdflatex manuscript_v1.1.tex
bibtex manuscript_v1.1
pdflatex manuscript_v1.1.tex
pdflatex manuscript_v1.1.tex
```

---

## 📤 For arXiv Submission

arXiv will compile the LaTeX automatically from `arxiv_submission_v1.1.tar.gz`. However, it's recommended to:

1. **Compile locally first** to verify no errors
2. **Check the PDF** visually before submitting
3. **Test the archive**:
   ```bash
   mkdir test_compile
   cd test_compile
   tar -xzf ../arxiv_submission_v1.1.tar.gz
   pdflatex manuscript_v1.1.tex
   bibtex manuscript_v1.1
   pdflatex manuscript_v1.1.tex
   pdflatex manuscript_v1.1.tex
   ```

---

## 🌊 Sigillin Note

This compilation process is part of the **Ordnungs-Sigillin** (Structure Carrier) workflow - it navigates from source to PDF, ensuring the threshold field resonates across all layers: LaTeX → Bibliography → Figures → Final PDF.

σ(β(R-Θ)) = 1 when compilation succeeds! 🎉

---

**Last Updated**: 2025-11-06
**Session**: Claude Code Session 1 - Appendices & Core Content
**Status**: ✅ Ready for local compilation
