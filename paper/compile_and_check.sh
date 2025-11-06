#!/bin/bash
# arXiv Manuscript Compilation & Validation Script
# Usage: ./compile_and_check.sh

set -e  # Exit on error

echo "🌊 Universal Threshold Field - arXiv Compilation Script"
echo "=========================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manuscript_v1.1.tex" ]; then
    echo "❌ Error: manuscript_v1.1.tex not found"
    echo "   Please run this script from the paper/ directory"
    exit 1
fi

echo "✅ Found manuscript_v1.1.tex"
echo ""

# Check for required files
echo "📋 Checking required files..."
REQUIRED_FILES=("manuscript_v1.1.tex" "references.bib" "beta_by_field_type.png" "meta_regression_grid.png" "correlation_heatmap.png")
MISSING=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "❌ $MISSING required file(s) missing. Cannot proceed."
    exit 1
fi

echo ""
echo "✅ All required files present"
echo ""

# Check for LaTeX installation
echo "🔧 Checking LaTeX installation..."
if command -v pdflatex &> /dev/null; then
    LATEX_CMD="pdflatex"
    echo "  ✓ Found pdflatex"
elif command -v xelatex &> /dev/null; then
    LATEX_CMD="xelatex"
    echo "  ✓ Found xelatex"
elif command -v lualatex &> /dev/null; then
    LATEX_CMD="lualatex"
    echo "  ✓ Found lualatex"
else
    echo ""
    echo "❌ No LaTeX compiler found (pdflatex, xelatex, or lualatex)"
    echo ""
    echo "Install LaTeX:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-full"
    echo "  macOS: brew install --cask mactex"
    echo "  Windows: Download from https://miktex.org"
    echo ""
    echo "Or use Overleaf (online): https://www.overleaf.com"
    exit 1
fi

# Check for bibtex
if ! command -v bibtex &> /dev/null; then
    echo "  ⚠️  Warning: bibtex not found. Bibliography may not compile."
fi

echo ""

# Clean previous compilation
echo "🧹 Cleaning previous compilation artifacts..."
rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot
echo "  ✓ Cleaned"
echo ""

# Compilation
echo "📝 Starting compilation (this may take 1-2 minutes)..."
echo ""

echo "  Pass 1/4: ${LATEX_CMD} (first run)..."
$LATEX_CMD -interaction=nonstopmode manuscript_v1.1.tex > compile_pass1.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Pass 1 complete"
else
    echo "  ✗ Pass 1 failed. Check compile_pass1.log"
    exit 1
fi

echo "  Pass 2/4: bibtex (processing bibliography)..."
if command -v bibtex &> /dev/null; then
    bibtex manuscript_v1.1 > compile_bibtex.log 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Pass 2 complete ($(grep -c "^\\\\bibitem" manuscript_v1.1.bbl 2>/dev/null || echo 0) entries)"
    else
        echo "  ⚠️  Pass 2 had warnings. Check compile_bibtex.log"
    fi
else
    echo "  ⚠️  Skipping bibtex (not installed)"
fi

echo "  Pass 3/4: ${LATEX_CMD} (second run)..."
$LATEX_CMD -interaction=nonstopmode manuscript_v1.1.tex > compile_pass3.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Pass 3 complete"
else
    echo "  ✗ Pass 3 failed. Check compile_pass3.log"
    exit 1
fi

echo "  Pass 4/4: ${LATEX_CMD} (final run)..."
$LATEX_CMD -interaction=nonstopmode manuscript_v1.1.tex > compile_pass4.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Pass 4 complete"
else
    echo "  ✗ Pass 4 failed. Check compile_pass4.log"
    exit 1
fi

echo ""
echo "✅ Compilation successful!"
echo ""

# Validation
if [ -f "manuscript_v1.1.pdf" ]; then
    PDF_SIZE=$(du -h manuscript_v1.1.pdf | cut -f1)
    echo "📄 PDF generated: manuscript_v1.1.pdf ($PDF_SIZE)"
    echo ""

    # Check PDF properties if pdfinfo is available
    if command -v pdfinfo &> /dev/null; then
        PAGES=$(pdfinfo manuscript_v1.1.pdf | grep "Pages:" | awk '{print $2}')
        echo "📊 PDF Statistics:"
        echo "  - Pages: $PAGES"
        echo "  - Size: $PDF_SIZE"
        echo ""
    fi

    # Check for images in PDF
    if command -v pdfimages &> /dev/null; then
        IMAGE_COUNT=$(pdfimages -list manuscript_v1.1.pdf 2>/dev/null | tail -n +3 | wc -l)
        echo "  - Embedded images: $IMAGE_COUNT"
        echo ""
    fi

    echo "🎯 Next Steps:"
    echo "  1. Open and review: manuscript_v1.1.pdf"
    echo "  2. Check all figures display correctly"
    echo "  3. Verify bibliography is complete"
    echo "  4. If good: Upload arxiv_submission_v1.1.tar.gz to arXiv!"
    echo ""
    echo "📚 Documentation:"
    echo "  - Detailed guide: QUICKSTART_ARXIV.md"
    echo "  - Full checklist: PRE_SUBMISSION_CHECKLIST.md"
    echo "  - Troubleshooting: COMPILE_PDF.md"
    echo ""
    echo "🌊 σ(β(R-Θ)) = 1 — Compilation threshold crossed! ✨"
else
    echo "❌ PDF not generated. Check compilation logs."
    exit 1
fi
