"""β-Drift & CREP Telemetry Logger for Type-VI Governance.

This tool appends β-evolution and CREP detection entries to metrics/beta_evolution.csv
for tracking Type-VI implosive dynamics and triggering governance escalation when needed.

Usage:
    python -m tools.log_beta_telemetry \\
        --domain climate \\
        --beta 4.5 \\
        --theta 0.8 \\
        --R 0.75 \\
        --zeta -0.02 \\
        --crep 0.65 \\
        --notes "Arctic ice feedback simulation"

Escalation Rules:
    - β-Drift > 10% → Warning banner in logs
    - CREP ≥ 0.7 → Level 2 escalation, reviewer required
    - CREP ≥ 0.8 → Level 3 escalation, automatic block

Reference: releases/V6-Plans_etc/type6_crep_tau_star_checklist.md
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "metrics" / "beta_evolution.csv"
REFERENCE_BETA = 4.2  # Global baseline for drift calculation


def calculate_tau_star(R: float, Theta: float, multiplier: float = 0.1) -> float:
    """Calculate safety delay τ* = multiplier * |Θ - R|."""
    return multiplier * abs(Theta - R)


def calculate_beta_drift(beta: float, reference: float = REFERENCE_BETA) -> float:
    """Calculate β-drift percentage relative to reference."""
    return abs(beta - reference) / reference


def determine_crep_level(crep: float) -> int:
    """Map CREP to escalation level."""
    if crep >= 0.8:
        return 3
    if crep >= 0.7:
        return 2
    if crep >= 0.6:
        return 1
    return 0


def append_telemetry_entry(
    *,
    domain: str,
    beta: float,
    theta: float,
    R: float,
    zeta: float,
    crep: float,
    notes: str = "",
) -> None:
    """Append a telemetry entry to metrics/beta_evolution.csv."""
    timestamp = datetime.now(timezone.utc).isoformat()
    tau_star = calculate_tau_star(R, theta)
    beta_drift = calculate_beta_drift(beta)
    drift_flag = "HIGH_DRIFT" if beta_drift > 0.1 else ""
    crep_level = determine_crep_level(crep)
    type6_tag = "[TYPE-VI-RISK]" if crep >= 0.6 else ""

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists and has header
    file_exists = CSV_PATH.exists()

    with CSV_PATH.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)

        # Write header if file is new
        if not file_exists or CSV_PATH.stat().st_size == 0:
            writer.writerow(
                [
                    "timestamp",
                    "domain",
                    "beta",
                    "beta_drift_pct",
                    "drift_flag",
                    "R",
                    "Theta",
                    "zeta",
                    "tau_star",
                    "crep_value",
                    "crep_level",
                    "type6_tag",
                    "notes",
                ]
            )

        # Write data row
        writer.writerow(
            [
                timestamp,
                domain,
                f"{beta:.4f}",
                f"{beta_drift:.4f}",
                drift_flag,
                f"{R:.4f}",
                f"{theta:.4f}",
                f"{zeta:.4f}",
                f"{tau_star:.4f}",
                f"{crep:.4f}",
                crep_level,
                type6_tag,
                notes,
            ]
        )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="β-Drift & CREP Telemetry Logger for Type-VI Governance"
    )
    parser.add_argument("--domain", required=True, help="Domain (climate, bio, ai, etc.)")
    parser.add_argument("--beta", type=float, required=True, help="β value")
    parser.add_argument("--theta", type=float, required=True, help="Θ threshold")
    parser.add_argument("--R", type=float, required=True, help="R regime value")
    parser.add_argument("--zeta", type=float, required=True, help="ζ damping coefficient")
    parser.add_argument("--crep", type=float, required=True, help="CREP index (0-1)")
    parser.add_argument("--notes", default="", help="Additional notes")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        append_telemetry_entry(
            domain=args.domain,
            beta=args.beta,
            theta=args.theta,
            R=args.R,
            zeta=args.zeta,
            crep=args.crep,
            notes=args.notes,
        )

        # Print warnings if needed
        drift_pct = calculate_beta_drift(args.beta)
        crep_level = determine_crep_level(args.crep)

        print(
            f"[beta_telemetry] Logged: domain={args.domain} β={args.beta:.3f} CREP={args.crep:.3f}"
        )

        if drift_pct > 0.1:
            print(f"⚠️  [HIGH_DRIFT] β-drift {drift_pct*100:.1f}% > 10% threshold")

        if crep_level >= 2:
            print(
                f"⚠️  [CREP-ESCALATION] Level {crep_level} - Reviewer required (CREP={args.crep:.3f})"
            )

        if crep_level >= 3:
            print("🛑 [TYPE-VI-BLOCK] CREP ≥ 0.8 - Automatic escalation to Level 3")

    except Exception as exc:
        print(f"[beta_telemetry] ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
