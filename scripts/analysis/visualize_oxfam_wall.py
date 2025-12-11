"""
Visualize how inequality-driven rigidity compresses the logistic warning window.

This script compares two logistic curves:
- Universal Adaptive (beta=4.1)
- Oxfam Rigid (beta=37.6)

It computes the warning window width (distance between P=0.1 and P=0.9)
for each beta, reports the reduction percentage, and produces a plot
highlighting the difference. The plot is saved to
`analysis/results/figure_oxfam_wall.png` for local generation.
"""

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def logistic(r: np.ndarray, beta: float) -> np.ndarray:
    """Logistic function P(R) = 1 / (1 + exp(-beta * R))."""
    return 1.0 / (1.0 + np.exp(-beta * r))


def warning_window(beta: float) -> float:
    """Compute the warning window width for a given beta."""
    return (np.log(0.9 / 0.1) - np.log(0.1 / 0.9)) / beta


def compute_windows(beta_universal: float, beta_oxfam: float) -> tuple[float, float, float]:
    """Return the windows for both betas and the reduction percentage."""
    window_universal = warning_window(beta_universal)
    window_oxfam = warning_window(beta_oxfam)
    reduction_pct = 100.0 * (1.0 - (window_oxfam / window_universal))
    return window_universal, window_oxfam, reduction_pct


def plot_curves(beta_universal: float, beta_oxfam: float, window_reduction_pct: float) -> None:
    """Plot both logistic curves and annotate the reduction percentage."""
    r_values = np.linspace(-1, 1, 500)
    plt.figure(figsize=(8, 5))

    plt.plot(
        r_values,
        logistic(r_values, beta_universal),
        label=f"Universal Adaptive (β={beta_universal})",
        linewidth=2,
    )
    plt.plot(
        r_values,
        logistic(r_values, beta_oxfam),
        label=f"Oxfam Rigid (β={beta_oxfam})",
        linewidth=2,
        linestyle="--",
    )

    plt.title("Warning Window Compression under Inequality")
    plt.xlabel("Order Parameter R")
    plt.ylabel("Activation P(R)")
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.annotate(
        f"Warning Window reduced by {window_reduction_pct:.2f}%",
        xy=(0.02, 0.05),
        xycoords="axes fraction",
        fontsize=11,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    output_path = os.path.join("analysis", "results", "figure_oxfam_wall.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)


def main() -> None:
    beta_universal = 4.1
    beta_oxfam = 37.6

    window_universal, window_oxfam, reduction_pct = compute_windows(beta_universal, beta_oxfam)

    print(f"Warning Window (Universal): {window_universal:.12f}")
    print(f"Warning Window (Oxfam): {window_oxfam:.12f}")
    print(f"CRITICAL: Warning Window reduced by {reduction_pct:.6f}%")

    plot_curves(beta_universal, beta_oxfam, reduction_pct)


if __name__ == "__main__":
    main()
