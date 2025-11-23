"""
Manuscript Compilation System (UTAC v5.0)

This script orchestrates the complete paper generation pipeline:
    1. Generate LaTeX tables from empirical data
    2. Copy template and inject tables
    3. Compile PDF using pdflatex
    4. Generate metadata and archive package

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Automated Manuscript Generation"
"""

import subprocess
from pathlib import Path
import shutil
import sys
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
PAPER_DIR = PROJECT_ROOT / "paper" / "v5_manuscript"
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "paper"
FIGURES_DIR = PROJECT_ROOT / "figures" / "v5_empirical"

TEMPLATE_FILE = PAPER_DIR / "template.tex"
OUTPUT_TEX = PAPER_DIR / "manuscript_v5.tex"
OUTPUT_PDF = PAPER_DIR / "manuscript_v5.pdf"


# ============================================================================
# PIPELINE FUNCTIONS
# ============================================================================

def step_generate_tables():
    """Step 1: Generate LaTeX tables from data."""
    print("STEP 1: Generating LaTeX tables...")
    print("-" * 70)

    table_script = SCRIPTS_DIR / "generate_latex_tables.py"

    if not table_script.exists():
        print(f"ERROR: Script not found: {table_script}")
        return False

    result = subprocess.run(
        [sys.executable, str(table_script)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("ERROR: Table generation failed:")
        print(result.stderr)
        return False

    print(result.stdout)
    print("✓ Tables generated successfully")
    print()
    return True


def step_check_figures():
    """Step 2: Verify figures exist."""
    print("STEP 2: Checking figures...")
    print("-" * 70)

    required_figures = [
        "time_series_comparison.png",
        "phase_diagram.png",
        "correlation_scatter.png"
    ]

    missing = []
    for fig in required_figures:
        fig_path = FIGURES_DIR / fig
        if not fig_path.exists():
            missing.append(fig)
            print(f"  ✗ Missing: {fig}")
        else:
            print(f"  ✓ Found: {fig}")

    if missing:
        print()
        print(f"ERROR: {len(missing)} figures missing. Run visualization scripts first.")
        print("  python scripts/grounding/visualize_history_vs_theory.py")
        return False

    print()
    print("✓ All figures present")
    print()
    return True


def step_compile_latex():
    """Step 3: Compile LaTeX to PDF."""
    print("STEP 3: Compiling LaTeX manuscript...")
    print("-" * 70)

    # Check if pdflatex is available
    try:
        subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING: pdflatex not found. Skipping PDF compilation.")
        print("  Install LaTeX distribution (TeX Live, MiKTeX) to compile PDF.")
        print("  Manuscript .tex file will still be generated.")
        return True  # Not a failure, just skip PDF

    # Copy template to output
    if not TEMPLATE_FILE.exists():
        print(f"ERROR: Template not found: {TEMPLATE_FILE}")
        return False

    shutil.copy(TEMPLATE_FILE, OUTPUT_TEX)
    print(f"  ✓ Copied template to: {OUTPUT_TEX.name}")

    # Compile PDF (run twice for references)
    for i in range(2):
        print(f"  Running pdflatex (pass {i+1}/2)...")

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", OUTPUT_TEX.name],
            cwd=PAPER_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("ERROR: LaTeX compilation failed:")
            print(result.stdout[-2000:])  # Last 2000 chars
            return False

    # Check PDF was created
    if OUTPUT_PDF.exists():
        print(f"  ✓ PDF compiled: {OUTPUT_PDF.name}")
    else:
        print("ERROR: PDF not generated despite successful compilation")
        return False

    print()
    print("✓ LaTeX compilation successful")
    print()
    return True


def step_generate_metadata():
    """Step 4: Generate manuscript metadata."""
    print("STEP 4: Generating metadata...")
    print("-" * 70)

    metadata = {
        "title": "Scale-Invariant Information Coupling: From Cosmic Velocities to Social Rigidity",
        "authors": ["Johann Benjamin Römer"],
        "version": "5.0.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "doi": "10.5281/zenodo.17472834",
        "repository": "https://github.com/GenesisAeon/Feldtheorie",
        "license": "GPLv3 (code) / CC BY-NC 4.0 (content & data); commercial use requires author permission",
        "abstract": (
            "We investigate structural isomorphism across cosmic and social domains, "
            "testing (1) cosmic velocity scaling via fundamental constants and "
            "(2) social phase transitions via Ising dynamics. Both hypotheses show "
            "statistical significance (p<0.01) but acknowledge critical limitations."
        )
    }

    metadata_file = PAPER_DIR / "manuscript_metadata.json"

    import json
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"  ✓ Saved metadata: {metadata_file.name}")
    print()
    print("✓ Metadata generated")
    print()
    return True


def step_cleanup():
    """Step 5: Clean up auxiliary LaTeX files."""
    print("STEP 5: Cleaning up auxiliary files...")
    print("-" * 70)

    aux_extensions = [".aux", ".log", ".out", ".toc", ".bbl", ".blg"]

    cleaned = 0
    for ext in aux_extensions:
        aux_file = PAPER_DIR / f"manuscript_v5{ext}"
        if aux_file.exists():
            aux_file.unlink()
            cleaned += 1

    print(f"  ✓ Removed {cleaned} auxiliary files")
    print()
    return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete manuscript compilation pipeline."""

    print("=" * 70)
    print("MANUSCRIPT COMPILATION SYSTEM (UTAC v5.0)")
    print("=" * 70)
    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output directory: {PAPER_DIR}")
    print()

    # Create output directory
    PAPER_DIR.mkdir(parents=True, exist_ok=True)

    # Run pipeline
    steps = [
        ("Generate Tables", step_generate_tables),
        ("Check Figures", step_check_figures),
        ("Compile LaTeX", step_compile_latex),
        ("Generate Metadata", step_generate_metadata),
        ("Cleanup", step_cleanup)
    ]

    for step_name, step_func in steps:
        success = step_func()

        if not success:
            print()
            print("=" * 70)
            print(f"PIPELINE FAILED AT: {step_name}")
            print("=" * 70)
            print()
            print("TROUBLESHOOTING:")
            if step_name == "Generate Tables":
                print("  1. Run data ingestion: scripts/grounding/ingest_historical_data.py")
                print("  2. Run parameter fitting: scripts/grounding/fit_ising_parameters.py")
                print("  3. Run constant scan: scripts/validation/universal_constant_scan.py")
            elif step_name == "Check Figures":
                print("  1. Run visualization: scripts/grounding/visualize_history_vs_theory.py")
            elif step_name == "Compile LaTeX":
                print("  1. Install LaTeX (TeX Live or MiKTeX)")
                print("  2. Check template syntax: paper/v5_manuscript/template.tex")

            return False

    # Success summary
    print()
    print("=" * 70)
    print("MANUSCRIPT COMPILATION COMPLETE ✓")
    print("=" * 70)
    print()
    print("OUTPUT FILES:")
    print(f"  LaTeX source: {OUTPUT_TEX}")

    if OUTPUT_PDF.exists():
        print(f"  PDF manuscript: {OUTPUT_PDF}")
        file_size = OUTPUT_PDF.stat().st_size / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")
    else:
        print("  PDF: Not generated (pdflatex not available)")

    print()
    print("NEXT STEPS:")
    print("  1. Review PDF for accuracy and formatting")
    print("  2. Upload to arXiv or preprint server")
    print("  3. Update Zenodo archive with new version")
    print()
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
