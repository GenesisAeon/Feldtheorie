#!/usr/bin/env python3
"""
Master script to generate all figures for arXiv submission
"""

import sys
import subprocess

figures = [
    ('generate_figure1.py', 'Figure 1: UTAC Overview'),
    ('generate_figure3.py', 'Figure 3: ABM Results'),
    ('generate_figures_4_5.py', 'Figures 4 & 5: Meta-Regression and Phi-Scaling'),
]

print("=" * 60)
print("UTAC Paper - Figure Generation")
print("Emergent Steepness: Microscopic Derivation of β")
print("=" * 60)
print()

failed = []
for script, description in figures:
    print(f"Generating {description}...")
    print(f"  Running: python3 {script}")
    
    try:
        result = subprocess.run(['python3', script], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print(f"  ✓ Success!")
            if result.stdout:
                print(f"  {result.stdout.strip()}")
        else:
            print(f"  ✗ FAILED with exit code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            failed.append((script, description))
    except subprocess.TimeoutExpired:
        print(f"  ✗ TIMEOUT (>60s)")
        failed.append((script, description))
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        failed.append((script, description))
    
    print()

print("=" * 60)
if not failed:
    print("✓ ALL FIGURES GENERATED SUCCESSFULLY!")
    print()
    print("Generated files in /mnt/user-data/outputs/:")
    print("  - figure1_utac_overview.pdf/png")
    print("  - figure3_abm_results.pdf/png")
    print("  - figure4_meta_regression.pdf/png")
    print("  - figure5_phi_scaling.pdf/png")
    print()
    print("Next steps:")
    print("  1. Review figures visually")
    print("  2. Compile LaTeX: pdflatex emergent_steepness.tex")
    print("  3. Submit to arXiv!")
else:
    print(f"✗ {len(failed)} FIGURE(S) FAILED:")
    for script, desc in failed:
        print(f"  - {desc} ({script})")
    sys.exit(1)

print("=" * 60)
