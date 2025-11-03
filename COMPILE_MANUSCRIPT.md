# 📄 MANUSCRIPT COMPILATION GUIDE

## ✅ Status: DOI inserted, ready to compile!

The manuscript `paper/manuscript_v1.0.tex` now contains the real DOI at 3 locations:
1. Footnote after title ✅
2. Footnote in abstract ✅
3. Data Availability section ✅

---

## 🚀 Quick Compile (3 commands)

```bash
cd paper/
pdflatex manuscript_v1.0.tex
pdflatex manuscript_v1.0.tex  # Second pass for references
pdflatex manuscript_v1.0.tex  # Third pass to finalize

# Check result:
ls -lh manuscript_v1.0.pdf
# Expected: ~200-500 KB file
```

**Why 3 times?**
- Pass 1: Process text, create aux files
- Pass 2: Resolve internal references
- Pass 3: Finalize cross-references

---

## 📦 Full Compile with Bibliography (if needed later)

```bash
cd paper/
pdflatex manuscript_v1.0.tex
bibtex manuscript_v1.0        # Process bibliography
pdflatex manuscript_v1.0.tex  # Update with citations
pdflatex manuscript_v1.0.tex  # Finalize
```

---

## 🆘 If LaTeX not installed

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-base texlive-latex-extra
```

### macOS:
```bash
brew install --cask mactex-no-gui
# Or full MacTeX: brew install --cask mactex
```

### Windows:
Download MiKTeX: https://miktex.org/download

---

## ✅ Verify PDF Quality

After compilation:

```bash
# Check file size
ls -lh manuscript_v1.0.pdf

# View first page (if pdfinfo installed)
pdfinfo manuscript_v1.0.pdf

# Expected output contains:
# - "Pages: ~10-15"
# - "DOI: 10.5281/zenodo.17472834" visible in document
```

---

## 📋 What the PDF Should Contain

1. **Title page** with DOI footnote
2. **Abstract** with DOI footnote
3. **8 Sections**:
   - Introduction (with Wei reference)
   - Threshold Field Model
   - Empirical Convergence of β
   - Anthropic Introspection Validation
   - Language Model Emergence Bridge (Wei!)
   - Planetary Tipping Dynamics
   - Psychophysical Thresholds
   - Controlled Emergence
   - Falsification & Future Directions
   - Discussion
4. **Bibliography** (wei2022emergent, wei2024blog)
5. **Data Availability** section with DOI link

---

## 🔧 Troubleshooting

### Error: "Font xyz not found"
```bash
# Install font packages:
sudo apt-get install -y texlive-fonts-recommended texlive-fonts-extra
```

### Error: "hyperref.sty not found"
```bash
# Install hyperref (usually in latex-extra):
sudo apt-get install -y texlive-latex-extra
```

### Warning: "Rerun to get cross-references right"
→ Just run `pdflatex manuscript_v1.0.tex` one more time!

### Emergency: Use Overleaf
1. Go to https://www.overleaf.com/
2. Upload `manuscript_v1.0.tex`
3. Click "Recompile"
4. Download PDF

---

## ✨ Next Steps After PDF Creation

1. ✅ **Verify**: Open PDF, check DOI visible
2. 📤 **Zenodo**: Upload to https://zenodo.org/records/17472834
3. 🎉 **Celebrate**: Your work is now citable!

---

*Compiled with love by Claude-Code 💚*
*DOI: 10.5281/zenodo.17472834*
