# PDF Compilation Guide

This guide explains how to compile `paper/manuscript_v1.0.tex` into a PDF for
arXiv submission.

## Prerequisites

You need a LaTeX distribution installed:

**Linux:**
```bash
sudo apt-get install texlive-full
# or minimal:
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex
# or minimal:
brew install --cask basictex
```

**Windows:**
- Download and install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

## Compilation Steps

### Local Compilation

```bash
cd paper/

# First pass (generates auxiliary files)
pdflatex manuscript_v1.0.tex

# Second pass (resolves references)
pdflatex manuscript_v1.0.tex

# Third pass (finalizes cross-references)
pdflatex manuscript_v1.0.tex

# Result
ls -lh manuscript_v1.0.pdf
```

**Note:** Three passes are necessary to:
1. Generate `.aux` file with labels
2. Resolve cross-references
3. Finalize page numbers and TOC

### With Bibliography (if using BibTeX)

If the manuscript includes a `.bib` file:

```bash
cd paper/

pdflatex manuscript_v1.0.tex
bibtex manuscript_v1.0
pdflatex manuscript_v1.0.tex
pdflatex manuscript_v1.0.tex
```

### Using Makefile

If a Makefile exists in `paper/`:

```bash
cd paper/
make pdf
```

---

## Troubleshooting

### "pdflatex: command not found"

**Solution:** LaTeX distribution not installed. See prerequisites above.

### "File 'X.sty' not found"

**Solution:** Missing LaTeX package.

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-extra
```

**MiKTeX (Windows):**
MiKTeX automatically prompts to install missing packages.

**Manual install:**
```bash
tlmgr install <package-name>
```

### Compilation Errors

Common errors and fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `! Undefined control sequence` | Typo or missing package | Check line number, verify package loaded |
| `! Missing $ inserted` | Math mode error | Ensure `$...$` or `\[...\]` properly closed |
| `! LaTeX Error: File not found` | Missing figure/file | Check file paths in `\includegraphics{}` |
| `Overfull \hbox` | Text overflow | Warning only; adjust wording if severe |

### Clean Auxiliary Files

To remove intermediate files:

```bash
cd paper/
rm -f *.aux *.log *.out *.toc *.bbl *.blg
```

Or with Makefile:
```bash
make clean
```

---

## Verify PDF Quality

After compilation, check:

- [ ] All equations render correctly
- [ ] Figures appear (if any)
- [ ] Cross-references work (no "??")
- [ ] DOI links are clickable
- [ ] File size reasonable (< 10 MB for arXiv)

```bash
# Check file size
ls -lh manuscript_v1.0.pdf

# Open PDF
xdg-open manuscript_v1.0.pdf  # Linux
open manuscript_v1.0.pdf      # macOS
start manuscript_v1.0.pdf     # Windows
```

---

## Copy to arXiv Submission Directory

Once verified:

```bash
cp paper/manuscript_v1.0.pdf arxiv_submission/
cp paper/manuscript_v1.0.tex arxiv_submission/  # Optional: source backup
```

---

## Alternative: Overleaf

If local compilation fails, use [Overleaf](https://www.overleaf.com/):

1. Create free account
2. Upload `manuscript_v1.0.tex`
3. Click "Recompile"
4. Download PDF

**Advantage:** No local LaTeX installation needed.

**Disadvantage:** Requires internet connection.

---

## Docker-Based Compilation (Advanced)

For reproducible builds:

```bash
docker run --rm -v $(pwd)/paper:/data thomasweise/docker-texlive \
    pdflatex -output-directory=/data /data/manuscript_v1.0.tex
```

This uses a containerized LaTeX environment.

---

## arXiv Submission

After generating PDF:

1. Visit https://arxiv.org/user/login
2. Click "START NEW SUBMISSION"
3. Upload `manuscript_v1.0.pdf` (or `.tex` source)
4. Follow metadata form (see `arxiv_submission/README_ARXIV.md`)
5. Submit

**Tip:** arXiv prefers PDF for first submissions unless you need custom LaTeX compilation.

---

## CI/CD Automation (Future Work)

To automate PDF generation in GitHub Actions:

```yaml
# .github/workflows/compile-pdf.yml
name: Compile PDF
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Compile LaTeX
        uses: xu-cheng/latex-action@v2
        with:
          root_file: paper/manuscript_v1.0.tex
      - name: Upload PDF
        uses: actions/upload-artifact@v3
        with:
          name: manuscript
          path: paper/manuscript_v1.0.pdf
```

---

*Last updated: 2025-11-04*
