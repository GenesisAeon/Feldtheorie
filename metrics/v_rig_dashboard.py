"""v_RIG Consciousness Framework - Live Validation Dashboard

V8.0 Telemetry Module for tracking empirical validations across:
- Cosmic dipole alignment (1.3% deviation target)
- Kleiber's Law metabolic scaling (β=7.4 → b=0.75)
- Neural integration frequency (13.5 MHz resonance)
- Specious present (100-300 ms integration window)

This dashboard complements the existing β-drift telemetry by providing
v_RIG-specific validation monitoring and alerting.

Lantern: #3 (Dashboard integration, β=5.4)
Version: v8.0.0
Authors: Johann Benjamin Römer, Claude Code Agent
Date: 2025-12-16
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY_PANDAS = True
except ImportError:
    HAS_NUMPY_PANDAS = False
    print("⚠️  numpy/pandas not available - some features will be limited")

try:
    from models.consciousness_integration import (
        calculate_impedance,
        calculate_integration_velocity,
        run_full_validation_suite,
        validate_cosmic_dipole,
        validate_kleiber_scaling,
        validate_neural_frequency,
        validate_specious_present,
    )
    from models.unified_constants import V_RIG_DEFAULT
    HAS_MODELS = True
except ImportError:
    # Fallback constants if models not available
    V_RIG_DEFAULT = 1351.7868
    HAS_MODELS = False
    print("⚠️  models.consciousness_integration not available - using fallback constants")


TELEMETRY_CSV = Path(__file__).parent / "v_rig_validation_log.csv"


# ============================================================================
# Telemetry Logging
# ============================================================================

def log_validation_snapshot(
    domain: str = "general",
    v_rig_km_s: Optional[float] = None,
    impedance_z: Optional[float] = None,
    cosmic_dipole_deviation_pct: Optional[float] = None,
    kleiber_beta: Optional[float] = None,
    neural_frequency_mhz: Optional[float] = None,
    specious_present_ms: Optional[float] = None,
    notes: str = "",
) -> None:
    """Log a v_RIG validation snapshot to telemetry.

    Args:
        domain: Application domain (e.g., "neuroscience", "cosmology")
        v_rig_km_s: Integration velocity (if None, use default)
        impedance_z: Dimensional impedance
        cosmic_dipole_deviation_pct: Cosmic dipole % deviation from v_RIG
        kleiber_beta: Biological β-parameter
        neural_frequency_mhz: Predicted neural frequency in MHz
        specious_present_ms: Typical integration window in ms
        notes: Additional context
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Use defaults if not provided
    if v_rig_km_s is None:
        v_rig_km_s = V_RIG_DEFAULT
    if impedance_z is None:
        impedance_z = calculate_impedance() if 'calculate_impedance' in globals() else 221.74

    row = {
        "timestamp": timestamp,
        "domain": domain,
        "v_rig_km_s": f"{v_rig_km_s:.6f}",
        "impedance_z": f"{impedance_z:.6f}",
        "cosmic_dipole_deviation_pct": f"{cosmic_dipole_deviation_pct:.6f}" if cosmic_dipole_deviation_pct is not None else "",
        "kleiber_beta": f"{kleiber_beta:.6f}" if kleiber_beta is not None else "",
        "neural_frequency_mhz": f"{neural_frequency_mhz:.6f}" if neural_frequency_mhz is not None else "",
        "specious_present_ms": f"{specious_present_ms:.6f}" if specious_present_ms is not None else "",
        "notes": notes,
    }

    # Append to CSV
    file_exists = TELEMETRY_CSV.exists()
    with open(TELEMETRY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists or TELEMETRY_CSV.stat().st_size < 200:
            writer.writeheader()
        writer.writerow(row)


def log_full_validation_suite(domain: str = "general", notes: str = "") -> dict:
    """Run full v8.0 validation suite and log results to telemetry.

    Returns:
        dict: Validation results from run_full_validation_suite()
    """
    if not HAS_MODELS:
        print("⚠️  Models not available - cannot run validation suite")
        return {}

    try:
        results = run_full_validation_suite()

        log_validation_snapshot(
            domain=domain,
            v_rig_km_s=results['v_rig'],
            impedance_z=results['impedance'],
            cosmic_dipole_deviation_pct=results['cosmic_dipole'].deviation_percent,
            kleiber_beta=results['kleiber'].beta_biological,
            neural_frequency_mhz=results['neural_frequency'].predicted_frequency_mhz,
            specious_present_ms=results['specious_present'].integration_window_typical_ms,
            notes=notes,
        )

        return results

    except Exception as e:
        print(f"⚠️  Validation suite failed: {e}")
        import traceback
        traceback.print_exc()
        return {}


# ============================================================================
# Telemetry Loading & Analysis
# ============================================================================

def load_validation_log():
    """Load v_RIG validation telemetry from CSV.

    Returns:
        DataFrame with validation snapshots (empty if no data)
    """
    if not HAS_NUMPY_PANDAS:
        print("⚠️  pandas not available - cannot load telemetry log")
        return None

    if not TELEMETRY_CSV.exists():
        import pandas as pd
        return pd.DataFrame()

    import pandas as pd
    df = pd.read_csv(TELEMETRY_CSV, comment="#")
    if df.empty:
        return df

    # Parse timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Convert numeric columns
    numeric_cols = [
        "v_rig_km_s",
        "impedance_z",
        "cosmic_dipole_deviation_pct",
        "kleiber_beta",
        "neural_frequency_mhz",
        "specious_present_ms",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def generate_validation_report() -> dict:
    """Generate v_RIG validation summary statistics.

    Returns:
        Dictionary with summary metrics and alert flags
    """
    df = load_validation_log()
    if df is None or (hasattr(df, 'empty') and df.empty):
        return {"status": "no_data"}

    # Alert thresholds (from v8.0 falsification criteria)
    COSMIC_DIPOLE_MAX_DEVIATION = 10.0  # %
    NEURAL_FREQ_TARGET = 13.5  # MHz
    NEURAL_FREQ_TOLERANCE = 1.0  # MHz
    IMPEDANCE_TARGET = 221.74
    IMPEDANCE_TOLERANCE = 10.0

    # Compute alerts
    alerts = []

    if "cosmic_dipole_deviation_pct" in df.columns:
        recent_dipole_dev = df["cosmic_dipole_deviation_pct"].dropna().iloc[-1] if len(df["cosmic_dipole_deviation_pct"].dropna()) > 0 else None
        if recent_dipole_dev is not None and recent_dipole_dev > COSMIC_DIPOLE_MAX_DEVIATION:
            alerts.append(f"⚠️  Cosmic dipole deviation {recent_dipole_dev:.2f}% > {COSMIC_DIPOLE_MAX_DEVIATION}% threshold")

    if "neural_frequency_mhz" in df.columns:
        recent_neural_freq = df["neural_frequency_mhz"].dropna().iloc[-1] if len(df["neural_frequency_mhz"].dropna()) > 0 else None
        if recent_neural_freq is not None and abs(recent_neural_freq - NEURAL_FREQ_TARGET) > NEURAL_FREQ_TOLERANCE:
            alerts.append(f"⚠️  Neural frequency {recent_neural_freq:.2f} MHz deviates from {NEURAL_FREQ_TARGET} MHz target")

    if "impedance_z" in df.columns:
        recent_impedance = df["impedance_z"].dropna().iloc[-1] if len(df["impedance_z"].dropna()) > 0 else None
        if recent_impedance is not None and abs(recent_impedance - IMPEDANCE_TARGET) > IMPEDANCE_TOLERANCE:
            alerts.append(f"⚠️  Impedance Z {recent_impedance:.2f} deviates from {IMPEDANCE_TARGET:.2f} target")

    summary = {
        "total_snapshots": len(df),
        "domains": df["domain"].unique().tolist(),
        "v_rig_mean_km_s": float(df["v_rig_km_s"].mean()) if "v_rig_km_s" in df.columns else None,
        "v_rig_std_km_s": float(df["v_rig_km_s"].std()) if "v_rig_km_s" in df.columns else None,
        "impedance_mean": float(df["impedance_z"].mean()) if "impedance_z" in df.columns else None,
        "cosmic_dipole_deviation_mean_pct": float(df["cosmic_dipole_deviation_pct"].mean()) if "cosmic_dipole_deviation_pct" in df.columns else None,
        "kleiber_beta_mean": float(df["kleiber_beta"].mean()) if "kleiber_beta" in df.columns else None,
        "neural_frequency_mean_mhz": float(df["neural_frequency_mhz"].mean()) if "neural_frequency_mhz" in df.columns else None,
        "time_range": {
            "start": df["timestamp"].min().isoformat() if not df.empty else None,
            "end": df["timestamp"].max().isoformat() if not df.empty else None,
        },
        "alerts": alerts,
        "status": "healthy" if len(alerts) == 0 else "alert",
    }

    return summary


# ============================================================================
# Visualization Dashboard
# ============================================================================

def plot_v_rig_dashboard(
    output_dir: str | Path = "analysis/results/v_rig_telemetry",
    show: bool = False,
) -> None:
    """Generate v_RIG validation visualization dashboard.

    Creates:
    - v_RIG evolution over time (color by domain)
    - Impedance Z tracking
    - Cosmic dipole deviation timeline
    - Neural frequency vs. 13.5 MHz target
    - Kleiber β distribution
    - Validation status heatmap

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

    df = load_validation_log()
    if df.empty:
        print("⚠️  No v_RIG telemetry data available")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. v_RIG Evolution Over Time
    ax1 = fig.add_subplot(gs[0, :2])
    for domain in df["domain"].unique():
        domain_df = df[df["domain"] == domain]
        ax1.plot(
            domain_df["timestamp"],
            domain_df["v_rig_km_s"],
            marker="o",
            label=domain,
            alpha=0.7,
        )
    ax1.axhline(V_RIG_DEFAULT, color="red", linestyle="--", alpha=0.5, label=f"v_RIG canonical ({V_RIG_DEFAULT:.2f} km/s)")
    ax1.set_xlabel("Time (UTC)")
    ax1.set_ylabel("v_RIG (km/s)")
    ax1.set_title("v_RIG Integration Velocity Over Time")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 2. Impedance Z Tracking
    ax2 = fig.add_subplot(gs[0, 2])
    if "impedance_z" in df.columns and df["impedance_z"].notna().any():
        ax2.hist(df["impedance_z"].dropna(), bins=20, alpha=0.7, color="steelblue", edgecolor="black")
        ax2.axvline(221.74, color="red", linestyle="--", label="Z canonical (221.74)")
        ax2.set_xlabel("Impedance Z")
        ax2.set_ylabel("Count")
        ax2.set_title("Impedance Z Distribution")
        ax2.legend()
        ax2.grid(alpha=0.3)

    # 3. Cosmic Dipole Deviation Timeline
    ax3 = fig.add_subplot(gs[1, 0])
    if "cosmic_dipole_deviation_pct" in df.columns and df["cosmic_dipole_deviation_pct"].notna().any():
        valid_data = df[df["cosmic_dipole_deviation_pct"].notna()]
        ax3.plot(valid_data["timestamp"], valid_data["cosmic_dipole_deviation_pct"], marker="o", color="purple", alpha=0.7)
        ax3.axhline(1.3, color="green", linestyle="--", alpha=0.5, label="v8.0 validation (1.3%)")
        ax3.axhline(10.0, color="red", linestyle="--", alpha=0.5, label="Falsification threshold (10%)")
        ax3.set_xlabel("Time (UTC)")
        ax3.set_ylabel("Deviation (%)")
        ax3.set_title("Cosmic Dipole Deviation")
        ax3.legend()
        ax3.grid(alpha=0.3)

    # 4. Neural Frequency vs. Target
    ax4 = fig.add_subplot(gs[1, 1])
    if "neural_frequency_mhz" in df.columns and df["neural_frequency_mhz"].notna().any():
        valid_data = df[df["neural_frequency_mhz"].notna()]
        ax4.plot(valid_data["timestamp"], valid_data["neural_frequency_mhz"], marker="o", color="orange", alpha=0.7)
        ax4.axhline(13.5, color="red", linestyle="--", alpha=0.5, label="13.5 MHz target (Sahu et al., 2013)")
        ax4.fill_between(valid_data["timestamp"], 12.5, 14.5, alpha=0.2, color="green", label="±1 MHz tolerance")
        ax4.set_xlabel("Time (UTC)")
        ax4.set_ylabel("Frequency (MHz)")
        ax4.set_title("Neural Integration Frequency")
        ax4.legend()
        ax4.grid(alpha=0.3)

    # 5. Kleiber β Distribution
    ax5 = fig.add_subplot(gs[1, 2])
    if "kleiber_beta" in df.columns and df["kleiber_beta"].notna().any():
        ax5.hist(df["kleiber_beta"].dropna(), bins=15, alpha=0.7, color="green", edgecolor="black")
        ax5.axvline(7.4, color="red", linestyle="--", label="β = 7.4 (biological)")
        ax5.set_xlabel("Kleiber β")
        ax5.set_ylabel("Count")
        ax5.set_title("Biological β Distribution")
        ax5.legend()
        ax5.grid(alpha=0.3)

    # 6. Validation Status Summary
    ax6 = fig.add_subplot(gs[2, :])
    summary = generate_validation_report()

    summary_text = f"""
V8.0 Validation Dashboard Summary
═══════════════════════════════════════════════════════════════

📊 Telemetry Stats:
   • Total snapshots: {summary.get('total_snapshots', 0)}
   • Domains tracked: {', '.join(summary.get('domains', []))}
   • Time range: {summary.get('time_range', {}).get('start', 'N/A')} → {summary.get('time_range', {}).get('end', 'N/A')}

📈 Mean Values:
   • v_RIG: {summary.get('v_rig_mean_km_s', 0):.4f} ± {summary.get('v_rig_std_km_s', 0):.4f} km/s
   • Impedance Z: {summary.get('impedance_mean', 0):.4f}
   • Cosmic dipole deviation: {summary.get('cosmic_dipole_deviation_mean_pct', 0):.4f}%
   • Kleiber β: {summary.get('kleiber_beta_mean', 0):.2f}
   • Neural frequency: {summary.get('neural_frequency_mean_mhz', 0):.2f} MHz

🚨 Alert Status: {summary.get('status', 'unknown').upper()}
   {chr(10).join(['   ' + alert for alert in summary.get('alerts', [])])}

✅ Falsification Criteria:
   • Cosmic dipole deviation < 10%: {'PASS' if summary.get('cosmic_dipole_deviation_mean_pct', 0) < 10 else 'FAIL'}
   • Neural frequency ≈ 13.5 MHz: {'PASS' if abs(summary.get('neural_frequency_mean_mhz', 13.5) - 13.5) < 1.0 else 'FAIL'}
   • Impedance Z ≈ 221.74: {'PASS' if abs(summary.get('impedance_mean', 221.74) - 221.74) < 10 else 'FAIL'}

📚 Framework Status: v8.0 Consciousness Integration
    """

    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
             fontfamily='monospace', fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    ax6.axis('off')

    plt.suptitle("🌀 v_RIG Consciousness Framework - Live Validation Dashboard (V8.0)",
                 fontsize=16, fontweight='bold', y=0.98)

    plot_path = (
        output_path
        / f"v_rig_dashboard_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.png"
    )
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"✅ v_RIG Dashboard saved: {plot_path}")

    if show:
        plt.show()
    else:
        plt.close()


# ============================================================================
# Export to JSON for Web Dashboard Integration
# ============================================================================

def export_validation_json(
    output_path: str | Path = "analysis/results/v_rig_telemetry/validation_feed.json"
) -> None:
    """Export current validation state as JSON for dashboard ingestion.

    Creates a JSON feed suitable for web dashboard consumption with:
    - Latest validation snapshot
    - Validation summary statistics
    - Alert status
    - Time-series data for sparklines
    """
    df = load_validation_log()
    summary = generate_validation_report()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Latest snapshot
    latest = {}
    if not df.empty:
        latest_row = df.iloc[-1]
        latest = {
            "timestamp": latest_row["timestamp"].isoformat(),
            "domain": latest_row["domain"],
            "v_rig_km_s": float(latest_row["v_rig_km_s"]) if pd.notna(latest_row["v_rig_km_s"]) else None,
            "impedance_z": float(latest_row["impedance_z"]) if pd.notna(latest_row["impedance_z"]) else None,
            "cosmic_dipole_deviation_pct": float(latest_row["cosmic_dipole_deviation_pct"]) if pd.notna(latest_row["cosmic_dipole_deviation_pct"]) else None,
            "neural_frequency_mhz": float(latest_row["neural_frequency_mhz"]) if pd.notna(latest_row["neural_frequency_mhz"]) else None,
        }

    # Time-series for sparklines (last 50 points)
    time_series = {}
    if not df.empty:
        recent_df = df.tail(50)
        time_series = {
            "timestamps": recent_df["timestamp"].dt.isoformat().tolist(),
            "v_rig_km_s": recent_df["v_rig_km_s"].fillna(-1).tolist(),
            "cosmic_dipole_deviation_pct": recent_df["cosmic_dipole_deviation_pct"].fillna(-1).tolist(),
            "neural_frequency_mhz": recent_df["neural_frequency_mhz"].fillna(-1).tolist(),
        }

    feed = {
        "meta": {
            "framework": "v_RIG Consciousness Integration",
            "version": "v8.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "latest_snapshot": latest,
        "summary": summary,
        "time_series": time_series,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2)

    print(f"✅ Validation JSON feed exported: {output_file}")


# ============================================================================
# CLI Interface
# ============================================================================

__all__ = [
    "log_validation_snapshot",
    "log_full_validation_suite",
    "load_validation_log",
    "generate_validation_report",
    "plot_v_rig_dashboard",
    "export_validation_json",
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="v_RIG Validation Telemetry Dashboard")
    parser.add_argument("--log", action="store_true", help="Run validation suite and log results")
    parser.add_argument("--plot", action="store_true", help="Generate dashboard plots")
    parser.add_argument("--report", action="store_true", help="Print validation report")
    parser.add_argument("--export-json", action="store_true", help="Export validation JSON feed")
    parser.add_argument("--domain", default="general", help="Domain identifier for logging")
    parser.add_argument("--notes", default="", help="Notes for logging")
    parser.add_argument(
        "--output-dir", default="analysis/results/v_rig_telemetry", help="Output directory"
    )

    args = parser.parse_args()

    if args.log:
        print("🌀 Running v8.0 validation suite...")
        results = log_full_validation_suite(domain=args.domain, notes=args.notes)
        if results:
            print("✅ Validation suite logged successfully")
            print(f"   v_RIG: {results.get('v_rig', 0):.4f} km/s")
            print(f"   Impedance Z: {results.get('impedance', 0):.4f}")
            print(f"   Cosmic dipole deviation: {results.get('cosmic_dipole', {}).deviation_percent:.2f}%")

    if args.report:
        print("\n" + "=" * 80)
        print("v_RIG VALIDATION REPORT")
        print("=" * 80)
        summary = generate_validation_report()
        print(json.dumps(summary, indent=2))

    if args.export_json:
        export_validation_json(output_path=Path(args.output_dir) / "validation_feed.json")

    if args.plot:
        plot_v_rig_dashboard(output_dir=args.output_dir, show=False)
        print("✅ v_RIG dashboard generated")
