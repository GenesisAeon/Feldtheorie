#!/usr/bin/env python3
"""
UTAC Fourier Analysis CLI

Command-line interface for spectral analysis of UTAC time series.
Analyzes β-spectra, field type signatures, and criticality patterns.

Usage:
    python -m analysis.fourier_analysis <signal_file> [options]

Examples:
    # Analyze a CSV time series
    python -m analysis.fourier_analysis data/climate/amoc_transport.csv --sampling-rate 1 --title "AMOC Spectrum"

    # Analyze with custom output
    python -m analysis.fourier_analysis data/llm/gpt_loss.csv --output results/gpt_spectrum.png

Author: Johann Römer, Claude Code
Date: 2025-11-11
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# Import the core Fourier module
try:
    from sonification import utac_fourier
except ImportError:
    # Fallback for direct script execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from sonification import utac_fourier


def load_signal(filepath, column=0, delimiter=','):
    """
    Load time series signal from file.

    Supports:
    - CSV files (single or multi-column)
    - TXT files (whitespace-separated)
    - NPY files (numpy arrays)

    Parameters
    ----------
    filepath : str or Path
        Path to signal file
    column : int, optional
        Column index if multi-column CSV (default: 0)
    delimiter : str, optional
        CSV delimiter (default: ',')

    Returns
    -------
    signal : ndarray
        1D time series signal
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Signal file not found: {filepath}")

    # Load based on extension
    if filepath.suffix == '.npy':
        signal = np.load(filepath)
    elif filepath.suffix in ['.csv', '.txt', '.dat']:
        data = np.loadtxt(filepath, delimiter=delimiter)

        # Handle multi-column data
        if data.ndim > 1:
            signal = data[:, column]
        else:
            signal = data
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")

    return signal


def save_results(results, output_path):
    """
    Save analysis results to JSON.

    Parameters
    ----------
    results : dict
        Analysis results from utac_fourier.run_analysis()
    output_path : str or Path
        Path to output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert numpy arrays to lists for JSON serialization
    serializable_results = {
        "features": results["features"],
        "field_type": results["field_type"],
        "spectrum": results["spectrum"].tolist()[:100],  # First 100 bins only
        "freqs": results["freqs"].tolist()[:100]
    }

    with open(output_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"✅ Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='UTAC Fourier Analysis - Spectral analysis for threshold field systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python -m analysis.fourier_analysis data/climate/amoc.csv

  # Custom sampling rate (for non-44.1kHz signals)
  python -m analysis.fourier_analysis data/llm/loss.csv --sampling-rate 1

  # Save figure and JSON results
  python -m analysis.fourier_analysis data/climate/amoc.csv \\
      --output results/amoc_spectrum.png \\
      --json results/amoc_spectrum.json

  # Multi-column CSV (use column 2)
  python -m analysis.fourier_analysis data/multi.csv --column 2

Field Type Classification:
  - Weakly Coupled:         < 150 Hz (sanft, diffus)
  - Strongly Coupled:    150-300 Hz (warm, resonant)
  - High-Dimensional:    300-600 Hz (ätherisch, komplex)
  - Physically Constrained: 600-1000 Hz (scharf, präzise)
  - Meta-Adaptive:       > 1000 Hz (morphing, adaptiv)
        """
    )

    # Required arguments
    parser.add_argument(
        'signal_file',
        type=str,
        help='Path to signal file (CSV, TXT, NPY)'
    )

    # Optional arguments
    parser.add_argument(
        '--sampling-rate', '-sr',
        type=float,
        default=44100,
        help='Sampling rate in Hz (default: 44100)'
    )

    parser.add_argument(
        '--column', '-c',
        type=int,
        default=0,
        help='Column index for multi-column files (default: 0)'
    )

    parser.add_argument(
        '--delimiter', '-d',
        type=str,
        default=',',
        help='CSV delimiter (default: ",")'
    )

    parser.add_argument(
        '--title', '-t',
        type=str,
        default='UTAC Fourier Spectrum',
        help='Plot title (default: "UTAC Fourier Spectrum")'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output path for spectrum plot (default: display only)'
    )

    parser.add_argument(
        '--json', '-j',
        type=str,
        default=None,
        help='Output path for JSON results (default: no JSON output)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed analysis results'
    )

    args = parser.parse_args()

    try:
        # Load signal
        print(f"📊 Loading signal from: {args.signal_file}")
        signal = load_signal(args.signal_file, column=args.column, delimiter=args.delimiter)
        print(f"✅ Signal loaded: {len(signal)} samples")

        # Run Fourier analysis
        print(f"🔬 Running Fourier analysis (sampling rate: {args.sampling_rate} Hz)")
        results = utac_fourier.run_analysis(
            signal,
            sampling_rate=args.sampling_rate,
            title=args.title,
            save_path=args.output
        )

        # Print results
        print("\n" + "="*60)
        print("🎵 UTAC FOURIER ANALYSIS RESULTS")
        print("="*60)
        print(f"Field Type:         {results['field_type']}")
        print(f"Dominant Frequency: {results['features']['dominant_freq']:.2f} Hz")
        print(f"Spectral Centroid:  {results['features']['centroid']:.2f} Hz")
        print(f"Spectral Entropy:   {results['features']['entropy']:.2f} bits")
        print("="*60)

        if args.verbose:
            print(f"\nSpectrum bins: {len(results['spectrum'])}")
            print(f"Frequency range: {results['freqs'][0]:.2f} - {results['freqs'][-1]:.2f} Hz")

        # Save JSON if requested
        if args.json:
            save_results(results, args.json)

        # Save plot confirmation
        if args.output:
            print(f"✅ Spectrum plot saved to: {args.output}")
        else:
            print("ℹ️  Plot displayed (close window to exit)")

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
