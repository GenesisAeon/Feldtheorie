#!/usr/bin/env python3
"""Parallel batch orchestration for UTF resonance fits with multiprocessing.

Formal layer:
    Extends the sequential resonance_batch_runner with multiprocessing support,
    distributing independent fit operations across CPU cores. Uses process pools
    to parallelize dataset loading, threshold fitting, and null model evaluation,
    reducing wall-clock time for large cohort analyses.

Empirical layer:
    Provides a CLI that accepts --workers N to control parallelism. Defaults to
    CPU count - 1, leaving one core for system responsiveness. Includes progress
    tracking with Rich progress bars for long-running batch operations.

Metaphorical layer:
    Where the serial runner lights lanterns one by one, the parallel runner
    orchestrates a dawn chorus—many resonances humming simultaneously, each
    finding its own threshold in parallel cadence.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.resonance_fit_pipeline import (  # noqa: E402
    fit_threshold_parameters,
)

try:
    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskID,
        TextColumn,
        TimeElapsedColumn,
    )

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore
    Progress = None  # type: ignore


@dataclass
class DatasetConfig:
    """Configuration for a single dataset to be processed."""

    name: str
    data_path: Path
    x_col: str
    y_col: str
    output_path: Path


@dataclass
class FitResult:
    """Result of fitting a single dataset."""

    name: str
    success: bool
    beta: float | None = None
    theta: float | None = None
    r_squared: float | None = None
    aic_delta: float | None = None
    error_message: str | None = None


def process_single_dataset(config: DatasetConfig) -> FitResult:
    """Process a single dataset with threshold fitting.

    This function is designed to be picklable for multiprocessing.

    Args:
        config: DatasetConfig with paths and column names

    Returns:
        FitResult with fit parameters or error information
    """
    try:
        import pandas as pd

        # Load data
        df = pd.read_csv(config.data_path)
        R = df[config.x_col].values
        zeta = df[config.y_col].values

        # Fit threshold model
        result = fit_threshold_parameters(R, zeta)

        # Extract key metrics
        return FitResult(
            name=config.name,
            success=True,
            beta=result.get("beta"),
            theta=result.get("theta"),
            r_squared=result.get("r_squared"),
            aic_delta=result.get("delta_aicc"),
        )

    except Exception as e:
        return FitResult(
            name=config.name,
            success=False,
            error_message=str(e),
        )


def process_datasets_parallel(
    datasets: Sequence[DatasetConfig],
    n_workers: int | None = None,
    verbose: bool = False,
) -> list[FitResult]:
    """Process multiple datasets in parallel using multiprocessing.

    Args:
        datasets: Sequence of DatasetConfig objects
        n_workers: Number of parallel workers (default: CPU count - 1)
        verbose: Enable verbose logging

    Returns:
        List of FitResult objects
    """
    if n_workers is None:
        n_workers = max(1, mp.cpu_count() - 1)

    if verbose:
        print(f"🚀 Processing {len(datasets)} datasets with {n_workers} workers")

    results = []

    if RICH_AVAILABLE and not verbose:
        # Use Rich progress bar
        console = Console()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Processing datasets...", total=len(datasets)
            )

            with mp.Pool(processes=n_workers) as pool:
                for result in pool.imap_unordered(process_single_dataset, datasets):
                    results.append(result)
                    progress.update(task, advance=1)

                    if result.success:
                        status = f"✓ {result.name}"
                    else:
                        status = f"✗ {result.name}: {result.error_message}"

                    progress.console.print(status)

    else:
        # Fallback: No progress bar
        with mp.Pool(processes=n_workers) as pool:
            results = pool.map(process_single_dataset, datasets)

        for result in results:
            if result.success:
                print(f"✓ {result.name}: β={result.beta:.4f}, Θ={result.theta:.4f}")
            else:
                print(f"✗ {result.name}: {result.error_message}")

    return results


def export_results(
    results: Sequence[FitResult],
    output_path: Path,
    format: str = "json",
) -> None:
    """Export fit results to file.

    Args:
        results: Sequence of FitResult objects
        output_path: Path to output file
        format: Output format ('json', 'csv', 'yaml')
    """
    import json

    if format == "json":
        data = [
            {
                "name": r.name,
                "success": r.success,
                "beta": r.beta,
                "theta": r.theta,
                "r_squared": r.r_squared,
                "aic_delta": r.aic_delta,
                "error": r.error_message,
            }
            for r in results
        ]

        with output_path.open("w") as f:
            json.dump(data, f, indent=2)

    elif format == "csv":
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "name": r.name,
                    "success": r.success,
                    "beta": r.beta,
                    "theta": r.theta,
                    "r_squared": r.r_squared,
                    "aic_delta": r.aic_delta,
                    "error": r.error_message,
                }
                for r in results
            ]
        )
        df.to_csv(output_path, index=False)

    elif format == "yaml":
        import yaml

        data = [
            {
                "name": r.name,
                "success": r.success,
                "beta": r.beta,
                "theta": r.theta,
                "r_squared": r.r_squared,
                "aic_delta": r.aic_delta,
                "error": r.error_message,
            }
            for r in results
        ]

        with output_path.open("w") as f:
            yaml.dump(data, f, default_flow_style=False)

    print(f"\n✅ Results exported to: {output_path}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parallel batch UTAC analysis with multiprocessing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: CPU count - 1)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("parallel_batch_results.json"),
        help="Output file path (default: parallel_batch_results.json)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Example dataset configurations
    # In production, these would be loaded from a config file
    datasets = [
        DatasetConfig(
            name="example_1",
            data_path=ROOT / "data" / "example.csv",
            x_col="x",
            y_col="y",
            output_path=ROOT / "results" / "example_1.json",
        ),
        # Add more dataset configurations here
    ]

    print("=" * 80)
    print("🔬 PARALLEL BATCH UTAC ANALYSIS")
    print("=" * 80)
    print(f"Datasets: {len(datasets)}")
    print(f"Workers: {args.workers or 'Auto (CPU count - 1)'}")
    print(f"Output: {args.output} (format: {args.format})")
    print("=" * 80 + "\n")

    # Process datasets in parallel
    results = process_datasets_parallel(
        datasets,
        n_workers=args.workers,
        verbose=args.verbose,
    )

    # Export results
    export_results(results, args.output, args.format)

    # Summary statistics
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total datasets: {len(results)}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")

    if successful > 0:
        avg_beta = sum(r.beta for r in results if r.success and r.beta) / successful
        avg_r2 = (
            sum(r.r_squared for r in results if r.success and r.r_squared) / successful
        )
        print(f"\nAverage β (steepness): {avg_beta:.4f}")
        print(f"Average R²: {avg_r2:.4f}")

    print("=" * 80)


if __name__ == "__main__":
    # Required for multiprocessing on Windows
    mp.freeze_support()
    main()
