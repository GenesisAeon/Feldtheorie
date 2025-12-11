"""β-Drift & τ* Telemetry Dashboard

FIT-Microstep for v6-activation-gaps (Priority 2).

Tracks UTAC Type-6 implosive field dynamics in real-time:
- β evolution and φ^(n/3) ladder alignment
- τ* safety delays
- ζ-risk flags (ζ<0 implosive regime detection)
- CREP threshold violations

Usage:
    from metrics.telemetry_dashboard import log_telemetry, plot_beta_drift

    # Log simulation step
    log_telemetry(
        domain="urban_heat",
        beta=16.3,
        R=0.307,
        Theta=0.5,
        tau_star=0.0193,
        zeta_risk=-0.42,
        crep_flag=True,
        notes="Implosive regime detected"
    )

    # Generate dashboard plots
    plot_beta_drift(output_dir="analysis/results/telemetry")
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from models.utac_type6_implosive import BETA_FIXPOINT_PHI3, PHI, PHI_CBRT
except ImportError:
    PHI = 1.618034
    PHI_CBRT = 1.174070
    BETA_FIXPOINT_PHI3 = 4.236

TELEMETRY_CSV = Path(__file__).parent / "beta_evolution.csv"


def log_telemetry(
    domain: str,
    beta: float,
    R: float,
    Theta: float,
    tau_star: float | None = None,
    zeta_risk: float | None = None,
    crep_flag: bool = False,
    notes: str = "",
) -> None:
    """Append telemetry entry to beta_evolution.csv.

    Args:
        domain: Field domain identifier
        beta: Current β value
        R: Resource/Reality coordinate
        Theta: Activation threshold
        tau_star: τ* safety delay (optional)
        zeta_risk: ζ-risk value (optional)
        crep_flag: True if CREP ≥ 0.7
        notes: Additional context
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Compute φ^(n/3) alignment
    phi_cbrt_step = np.round(np.log(beta) / np.log(PHI_CBRT))
    beta_phi_theoretical = PHI ** (phi_cbrt_step / 3.0)
    beta_phi_deviation = (beta - beta_phi_theoretical) / beta_phi_theoretical

    row = {
        "timestamp": timestamp,
        "domain": domain,
        "beta": f"{beta:.6f}",
        "beta_phi_theoretical": f"{beta_phi_theoretical:.6f}",
        "beta_phi_deviation": f"{beta_phi_deviation:.6f}",
        "phi_cbrt_step": int(phi_cbrt_step),
        "tau_star": f"{tau_star:.6f}" if tau_star is not None else "",
        "zeta_risk": f"{zeta_risk:.6f}" if zeta_risk is not None else "",
        "R": f"{R:.6f}",
        "Theta": f"{Theta:.6f}",
        "crep_flag": "TRUE" if crep_flag else "FALSE",
        "notes": notes,
    }

    # Append to CSV
    file_exists = TELEMETRY_CSV.exists()
    with open(TELEMETRY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists or TELEMETRY_CSV.stat().st_size < 200:
            writer.writeheader()
        writer.writerow(row)


def load_telemetry() -> pd.DataFrame:
    """Load telemetry log from beta_evolution.csv.

    Returns:
        DataFrame with telemetry entries (empty if no data)
    """
    if not TELEMETRY_CSV.exists():
        return pd.DataFrame()

    df = pd.read_csv(TELEMETRY_CSV, comment="#")
    if df.empty:
        return df

    # Parse timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Convert numeric columns
    numeric_cols = [
        "beta",
        "beta_phi_theoretical",
        "beta_phi_deviation",
        "tau_star",
        "zeta_risk",
        "R",
        "Theta",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def plot_beta_drift(
    output_dir: str | Path = "analysis/results/telemetry",
    show: bool = False,
) -> None:
    """Generate β-drift visualization dashboard.

    Creates:
    - β evolution over time (color by domain)
    - φ^(n/3) ladder alignment histogram
    - τ* vs ζ-risk scatter plot
    - CREP flag timeline

    Args:
        output_dir: Directory for output plots
        show: If True, display plots interactively
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("⚠️  matplotlib/seaborn not available - skipping visualization")
        return

    df = load_telemetry()
    if df.empty:
        print("⚠️  No telemetry data available")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. β Evolution Over Time
    ax = axes[0, 0]
    for domain in df["domain"].unique():
        domain_df = df[df["domain"] == domain]
        ax.plot(
            domain_df["timestamp"],
            domain_df["beta"],
            marker="o",
            label=domain,
            alpha=0.7,
        )
    ax.axhline(BETA_FIXPOINT_PHI3, color="red", linestyle="--", alpha=0.5, label="Φ³ (canonical)")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("β (Steepness)")
    ax.set_title("β Evolution Over Time")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(alpha=0.3)

    # 2. φ^(n/3) Ladder Alignment
    ax = axes[0, 1]
    ax.hist(
        df["beta_phi_deviation"].dropna(),
        bins=30,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
    )
    ax.axvline(0, color="red", linestyle="--", label="Perfect alignment")
    ax.set_xlabel("β Deviation from φ^(n/3) Ladder")
    ax.set_ylabel("Count")
    ax.set_title("φ^(n/3) Alignment Distribution")
    ax.legend()
    ax.grid(alpha=0.3)

    # 3. τ* vs ζ-Risk Scatter
    ax = axes[1, 0]
    valid_data = df[df["tau_star"].notna() & df["zeta_risk"].notna()]
    if not valid_data.empty:
        scatter = ax.scatter(
            valid_data["zeta_risk"],
            valid_data["tau_star"],
            c=valid_data["beta"],
            cmap="viridis",
            alpha=0.6,
            s=100,
        )
        plt.colorbar(scatter, ax=ax, label="β")
        ax.axvline(0, color="red", linestyle="--", alpha=0.5, label="ζ=0 (criticality)")
        ax.set_xlabel("ζ-Risk (ζ<0 = implosive)")
        ax.set_ylabel("τ* (Safety Delay)")
        ax.set_title("τ* vs ζ-Risk Phase Space")
        ax.legend()
        ax.grid(alpha=0.3)
    else:
        ax.text(0.5, 0.5, "No τ*/ζ data", ha="center", va="center", transform=ax.transAxes)

    # 4. CREP Flag Timeline
    ax = axes[1, 1]
    df_crep = df[df["crep_flag"] == True]
    if not df_crep.empty:
        ax.scatter(
            df_crep["timestamp"],
            df_crep["beta"],
            color="red",
            marker="x",
            s=100,
            label="CREP ≥ 0.7",
        )
        ax.scatter(df["timestamp"], df["beta"], color="lightgray", alpha=0.3, s=30, label="Normal")
        ax.axhline(BETA_FIXPOINT_PHI3, color="blue", linestyle="--", alpha=0.5)
        ax.set_xlabel("Time (UTC)")
        ax.set_ylabel("β")
        ax.set_title("CREP Flag Timeline")
        ax.legend()
        ax.grid(alpha=0.3)
    else:
        ax.text(0.5, 0.5, "No CREP flags", ha="center", va="center", transform=ax.transAxes)

    plt.tight_layout()
    plot_path = (
        output_path
        / f"beta_drift_dashboard_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.png"
    )
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"✅ Dashboard saved: {plot_path}")

    if show:
        plt.show()
    else:
        plt.close()


def generate_summary_report() -> dict:
    """Generate telemetry summary statistics.

    Returns:
        Dictionary with summary metrics
    """
    df = load_telemetry()
    if df.empty:
        return {"status": "no_data"}

    summary = {
        "total_entries": len(df),
        "domains": df["domain"].unique().tolist(),
        "beta_mean": float(df["beta"].mean()),
        "beta_std": float(df["beta"].std()),
        "beta_min": float(df["beta"].min()),
        "beta_max": float(df["beta"].max()),
        "phi_alignment_mean_deviation": float(df["beta_phi_deviation"].mean()),
        "crep_violations": int(df["crep_flag"].sum()),
        "implosive_regime_count": int((df["zeta_risk"] < 0).sum()),
        "time_range": {
            "start": df["timestamp"].min().isoformat() if not df.empty else None,
            "end": df["timestamp"].max().isoformat() if not df.empty else None,
        },
    }

    return summary


__all__ = [
    "log_telemetry",
    "load_telemetry",
    "plot_beta_drift",
    "generate_summary_report",
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="β-Drift Telemetry Dashboard")
    parser.add_argument("--plot", action="store_true", help="Generate dashboard plots")
    parser.add_argument("--summary", action="store_true", help="Print summary report")
    parser.add_argument(
        "--output-dir", default="analysis/results/telemetry", help="Output directory"
    )

    args = parser.parse_args()

    if args.summary:
        import json

        summary = generate_summary_report()
        print(json.dumps(summary, indent=2))

    if args.plot:
        plot_beta_drift(output_dir=args.output_dir, show=False)
        print("✅ Telemetry dashboard generated")
