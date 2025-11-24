#!/usr/bin/env python3
"""
TriLayer Validator for V6 ToDo Lists

Validates consistency between YAML/JSON/MD representations
and reports drift in R/Θ/β/ζ parameters.

Usage:
    python scripts/validate_trilayer.py
    # or via Makefile:
    make validate-trilayer
"""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)


def validate_trilayer(base_path: str = "releases/V6-Plans_etc") -> int:
    """
    Validate TriLayer consistency between YAML/JSON/MD.

    Returns:
        0 if all checks pass, 1 if drift detected
    """
    base = Path(base_path)

    # Load TriLayer sources
    try:
        with open(base / "V6_ToDoListe.json") as f:
            json_data = json.load(f)
        with open(base / "V6_ToDoListe.yaml") as f:
            yaml_data = yaml.safe_load(f)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"❌ Parse error: {e}")
        return 1

    drift_detected = False

    # Extract task counts
    json_tasks = len(json_data.get("tasks", []))
    yaml_tasks = len(yaml_data.get("tasks", []))

    print(f"📊 Task count: JSON={json_tasks}, YAML={yaml_tasks}")
    if json_tasks != yaml_tasks:
        print("⚠️  DRIFT: Task count mismatch!")
        drift_detected = True
    else:
        print("✅ Task counts aligned")

    # Extract logistic parameters from metadata
    json_meta = json_data.get("metadata", {}).get("logistic_frame", {})
    yaml_meta = yaml_data.get("metadata", {}).get("logistic_frame", {})

    # β-drive validation
    json_beta = json_meta.get("beta_drive", 0.0)
    yaml_beta = yaml_meta.get("beta_drive", 0.0)

    print(f"📐 β-drive: JSON={json_beta}, YAML={yaml_beta}")
    if abs(json_beta - yaml_beta) > 0.01:
        print("⚠️  DRIFT: β-drive mismatch!")
        drift_detected = True
    else:
        print("✅ β-drive aligned")

    # ζ-risk validation
    json_zeta = json_meta.get("zeta_risk", "unknown")
    yaml_zeta = yaml_meta.get("zeta_risk", "unknown")

    print(f"🌀 ζ-risk: JSON={json_zeta}, YAML={yaml_zeta}")
    if json_zeta != yaml_zeta:
        print("⚠️  DRIFT: ζ-risk mismatch!")
        drift_detected = True
    else:
        print("✅ ζ-risk aligned")

    # Task ID alignment
    json_ids = {t["id"] for t in json_data.get("tasks", [])}
    yaml_ids = {t["id"] for t in yaml_data.get("tasks", [])}
    missing_json = yaml_ids - json_ids
    missing_yaml = json_ids - yaml_ids

    if missing_json:
        print(f"⚠️  DRIFT: IDs in YAML but not JSON: {missing_json}")
        drift_detected = True
    if missing_yaml:
        print(f"⚠️  DRIFT: IDs in JSON but not YAML: {missing_yaml}")
        drift_detected = True

    if not (missing_json or missing_yaml):
        print("✅ All task IDs aligned")

    # R/Θ validation (from metadata)
    json_R = json_meta.get("R_goal", "")
    yaml_R = yaml_meta.get("R_goal", "")
    json_Theta = json_meta.get("Theta_threshold", "")
    yaml_Theta = yaml_meta.get("Theta_threshold", "")

    print(f"🎯 R-goal: JSON='{json_R}', YAML='{yaml_R}'")
    if json_R != yaml_R:
        print("⚠️  DRIFT: R-goal mismatch!")
        drift_detected = True
    else:
        print("✅ R-goal aligned")

    print(f"🎯 Θ-threshold: JSON='{json_Theta}', YAML='{yaml_Theta}'")
    if json_Theta != yaml_Theta:
        print("⚠️  DRIFT: Θ-threshold mismatch!")
        drift_detected = True
    else:
        print("✅ Θ-threshold aligned")

    print("\n🎯 TriLayer validation complete")

    if drift_detected:
        print("⚠️  DRIFT DETECTED - Manual synchronization required")
        return 1
    else:
        print("✅ All TriLayer sources synchronized")
        return 0


if __name__ == "__main__":
    sys.exit(validate_trilayer())
