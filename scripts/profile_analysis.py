#!/usr/bin/env python3
"""Profiling tool for identifying performance bottlenecks in UTAC analysis.

Formal layer:
    Uses cProfile to measure execution time of critical analysis functions,
    identifying bottlenecks in data loading, fitting algorithms, and export
    operations. Generates detailed performance reports with call graphs.

Empirical layer:
    Provides CLI for profiling batch runners, fit pipelines, and solvers.
    Outputs statistics ranked by cumulative time, enabling targeted optimization.

Metaphorical layer:
    The profiler is a temporal microscope—revealing where the field's resonance
    slows to a hum. By illuminating the bottlenecks, we know where to channel
    parallel currents for acceleration.
"""

from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def profile_batch_runner() -> None:
    """Profile the resonance_batch_runner for performance analysis."""
    from analysis.resonance_batch_runner import main as batch_main

    print("🔬 Profiling resonance_batch_runner...")
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        batch_main()
    except Exception as e:
        print(f"⚠️  Batch runner failed: {e}")

    profiler.disable()
    return profiler


def profile_fit_pipeline() -> None:
    """Profile a single resonance fit pipeline."""
    import numpy as np
    from analysis.resonance_fit_pipeline import fit_threshold_parameters

    print("🔬 Profiling resonance_fit_pipeline...")
    profiler = cProfile.Profile()

    # Generate synthetic data for profiling
    R = np.linspace(0, 100, 1000)
    beta, theta, L = 0.1, 50, 1.0
    zeta = L / (1 + np.exp(-beta * (R - theta)))
    zeta += np.random.normal(0, 0.02, size=zeta.shape)  # Add noise

    profiler.enable()
    try:
        result = fit_threshold_parameters(R, zeta)
    except Exception as e:
        print(f"⚠️  Fit pipeline failed: {e}")

    profiler.disable()
    return profiler


def profile_planetary_analysis() -> None:
    """Profile planetary tipping elements analysis."""
    from analysis.planetary_tipping_elements_fit import main as planetary_main

    print("🔬 Profiling planetary_tipping_elements_fit...")
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        planetary_main()
    except Exception as e:
        print(f"⚠️  Planetary analysis failed: {e}")

    profiler.disable()
    return profiler


def print_profile_stats(profiler: cProfile.Profile, top_n: int = 20) -> None:
    """Print formatted profiling statistics.

    Args:
        profiler: cProfile.Profile object
        top_n: Number of top functions to display (default: 20)
    """
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)

    print("\n" + "=" * 80)
    print("📊 PROFILING RESULTS (Top Functions by Cumulative Time)")
    print("=" * 80)

    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(top_n)
    print(stream.getvalue())

    print("\n" + "=" * 80)
    print("📊 PROFILING RESULTS (Top Functions by Total Time)")
    print("=" * 80)

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats(top_n)
    print(stream.getvalue())


def export_profile_stats(profiler: cProfile.Profile, output_path: Path) -> None:
    """Export profiling statistics to a file.

    Args:
        profiler: cProfile.Profile object
        output_path: Path to output .stats file
    """
    profiler.dump_stats(str(output_path))
    print(f"\n✅ Profile statistics exported to: {output_path}")
    print(f"   View with: python -m pstats {output_path}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Profile UTAC analysis tools for performance optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "target",
        choices=["batch", "fit", "planetary", "all"],
        help="Analysis target to profile",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("profile_stats.prof"),
        help="Output path for profile statistics (default: profile_stats.prof)",
    )

    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="Number of top functions to display (default: 20)",
    )

    args = parser.parse_args()

    targets = {
        "batch": profile_batch_runner,
        "fit": profile_fit_pipeline,
        "planetary": profile_planetary_analysis,
    }

    if args.target == "all":
        for name, func in targets.items():
            print(f"\n{'=' * 80}")
            print(f"Profiling: {name}")
            print(f"{'=' * 80}")
            profiler = func()
            print_profile_stats(profiler, args.top)
            output_path = args.output.parent / f"{args.output.stem}_{name}.prof"
            export_profile_stats(profiler, output_path)
    else:
        profiler = targets[args.target]()
        print_profile_stats(profiler, args.top)
        export_profile_stats(profiler, args.output)

    print("\n" + "=" * 80)
    print("🎯 PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. Identify bottlenecks from cumulative time statistics above
2. Consider parallelization for:
   - Batch dataset processing (multiprocessing.Pool)
   - Independent fit operations
3. Optimize hot paths with:
   - Numba JIT compilation (@numba.jit)
   - Vectorized NumPy operations
   - Cached computations (functools.lru_cache)
4. For large datasets (>1GB):
   - Use Dask for lazy evaluation
   - Implement chunked processing
    """)


if __name__ == "__main__":
    main()
