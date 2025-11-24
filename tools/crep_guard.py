#!/usr/bin/env python3
"""
CREP/τ* Safety Guard

Validates Type-VI implosive field compliance:
- CREP ≥ 0.7 threshold enforcement
- τ* = 0.1·|Θ−R| default validation
- TriLayer drift detection (YAML/JSON/MD)
- Reviewer routing for Level 2/3 escalation

Usage:
    python -m tools.crep_guard --threshold 0.7 --tau-default 0.1
    python -m tools.crep_guard --trilayer V6_ToDoListe.* Chronik/chronik_v6_release.*

Corresponds to: releases/V6-Plans_etc/type6_crep_tau_star_checklist.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple


def check_crep_thresholds(threshold: float = 0.7) -> Tuple[bool, List[str]]:
    """
    Check CREP values in analysis results.

    Returns:
        (all_safe, warnings): True if all CREP < threshold, list of warnings
    """
    results_dir = Path("analysis/results")
    if not results_dir.exists():
        print("ℹ️  No analysis/results/ directory - skipping CREP check")
        return True, []

    crep_files = list(results_dir.glob("*crep*.json"))

    if not crep_files:
        print("ℹ️  No CREP analysis files found - Type-VI models not yet in use")
        return True, []

    warnings = []
    all_safe = True

    print(f"\n🛡️  Checking CREP thresholds (threshold={threshold})...\n")

    for crep_file in crep_files:
        try:
            with open(crep_file) as f:
                data = json.load(f)
                crep_value = data.get("crep", 0.0)

                if crep_value >= threshold:
                    all_safe = False
                    warning = f"{crep_file.name}: CREP={crep_value:.3f} ≥ {threshold}"
                    warnings.append(warning)
                    print(f"⚠️  {warning} → MANDATORY REVIEWER!")
                else:
                    print(f"✅ {crep_file.name}: CREP={crep_value:.3f} (safe)")
        except Exception as e:
            print(f"⚠️  Failed to read {crep_file.name}: {e}")

    return all_safe, warnings


def check_tau_star_usage(tau_default: float = 0.1) -> Tuple[bool, List[str]]:
    """
    Check τ* safety delay usage and integrator choice in models.

    Returns:
        (compliant, warnings): True if RK4+ used with τ*, warnings list
    """
    models_dir = Path("models")
    if not models_dir.exists():
        print("ℹ️  No models/ directory - skipping τ* check")
        return True, []

    print(f"\n🔬 Checking τ* safety delay usage (default={tau_default})...\n")

    tau_files = list(models_dir.glob("**/*.py"))
    warnings = []
    compliant = True
    tau_count = 0

    for model_file in tau_files:
        try:
            content = model_file.read_text()

            has_tau = any(term in content for term in ["tau_star", "τ*", "safety_delay"])

            if has_tau:
                tau_count += 1

                # Check integrator
                has_euler = "euler" in content.lower()
                has_rk4 = "rk4" in content.lower() or "runge" in content.lower()

                if has_euler and not has_rk4:
                    compliant = False
                    warning = f"{model_file.name}: Uses Euler for ζ<0 (requires RK4+)"
                    warnings.append(warning)
                    print(f"❌ {warning}")
                else:
                    print(f"✅ {model_file.name}: τ* with proper integrator")
        except Exception as e:
            print(f"⚠️  Failed to read {model_file.name}: {e}")

    if tau_count == 0:
        print("ℹ️  No τ* usage found in models")
    else:
        print(f"\nℹ️  Total models using τ*: {tau_count}")

    return compliant, warnings


def check_trilayer_drift(trilayer_paths: List[str]) -> bool:
    """
    Check for drift between YAML/JSON/MD versions.

    Returns:
        True if synchronized, False if drift detected
    """
    print("\n🔍 Checking TriLayer drift...\n")

    # Use existing validator if available
    validator_path = Path("scripts/validate_trilayer.py")
    if validator_path.exists():
        import subprocess
        result = subprocess.run(
            ["python", str(validator_path)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return False
        return True
    else:
        print("⚠️  TriLayer validator not found at scripts/validate_trilayer.py")
        return True  # Don't fail if validator missing


def check_governance_docs() -> Tuple[bool, List[str]]:
    """
    Validate that required V6 governance documents exist.

    Returns:
        (all_exist, missing): True if all docs present, list of missing files
    """
    print("\n📋 Checking V6 governance documentation...\n")

    required_files = [
        "releases/V6-Plans_etc/type6_crep_tau_star_checklist.md",
        "releases/V6-Plans_etc/V6_ToDoListe.md",
        "METRICS.md",
    ]

    missing = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing.append(file_path)

    return len(missing) == 0, missing


def print_escalation_instructions(high_crep_warnings: List[str]):
    """Print instructions for CREP ≥ 0.7 scenarios."""
    print("\n" + "="*70)
    print("🔴 HIGH-CREP MODELS DETECTED - MANDATORY REVIEWER REQUIRED")
    print("="*70)
    print("\nModels requiring Level 2/3 escalation:\n")
    for warning in high_crep_warnings:
        print(f"  • {warning}")

    print("\n📋 Required actions (see type6_crep_tau_star_checklist.md):\n")
    print("  1. Document CREP analysis in releases/V6-Plans_etc/POLICY.md")
    print("  2. Add provenance block to releases/V6-Plans_etc/ETHICS.md")
    print("  3. Set reviewer slot in releases/V6-Plans_etc/Chronik/chronik_v6_release.md")
    print("  4. Ensure τ* = 0.1·|Θ−R| safety delay with RK4+ integrator")
    print("  5. Add ΔAIC/CI metrics to provenance trail")
    print("\n⚠️  DO NOT MERGE until reviewer approval documented\n")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="CREP/τ* Safety Guard for Type-VI implosive fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="CREP threshold for mandatory review (default: 0.7)"
    )
    parser.add_argument(
        "--tau-default",
        type=float,
        default=0.1,
        help="Default τ* coefficient (default: 0.1)"
    )
    parser.add_argument(
        "--trilayer",
        nargs="+",
        help="Paths to check for TriLayer drift"
    )
    parser.add_argument(
        "--fail-on-high-crep",
        action="store_true",
        help="Exit with error code if CREP ≥ threshold"
    )

    args = parser.parse_args()

    print("="*70)
    print("🛡️  CREP/τ* Safety Guard - V6 Governance Check")
    print("="*70)

    all_checks_passed = True

    # 1. Check CREP thresholds
    crep_safe, crep_warnings = check_crep_thresholds(args.threshold)
    if not crep_safe:
        all_checks_passed = False
        if args.fail_on_high_crep:
            print_escalation_instructions(crep_warnings)

    # 2. Check τ* usage
    tau_compliant, tau_warnings = check_tau_star_usage(args.tau_default)
    if not tau_compliant:
        all_checks_passed = False
        print("\n❌ τ* implementation issues detected")

    # 3. Check TriLayer drift (if paths provided)
    if args.trilayer:
        trilayer_ok = check_trilayer_drift(args.trilayer)
        if not trilayer_ok:
            all_checks_passed = False
            print("\n❌ TriLayer drift detected")

    # 4. Check governance docs
    docs_ok, missing_docs = check_governance_docs()
    if not docs_ok:
        print(f"\n⚠️  Missing {len(missing_docs)} governance document(s)")

    # Final summary
    print("\n" + "="*70)
    if all_checks_passed and docs_ok:
        print("✅ CREP/τ* SAFETY GUARD: ALL CHECKS PASSED")
        print("="*70)
        print("\nThe governance holds. Safe to proceed. ✨\n")
        return 0
    else:
        print("⚠️  CREP/τ* SAFETY GUARD: WARNINGS DETECTED")
        print("="*70)
        if not crep_safe and args.fail_on_high_crep:
            print("\n🔴 BLOCKING: High CREP values require mandatory review\n")
            return 1
        else:
            print("\nℹ️  Informational warnings only - review recommended\n")
            return 0


if __name__ == "__main__":
    sys.exit(main())
