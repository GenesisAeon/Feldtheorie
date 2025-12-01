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
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)


def _parse_md_metadata(md_content: str) -> dict:
    """Extract metadata fields from the Markdown TriLayer view."""

    def _search(pattern: str) -> str | None:
        match = re.search(pattern, md_content)
        return match.group(1).strip() if match else None

    md_meta: dict[str, object] = {}
    md_meta["version"] = _search(r"\*\*Version:\*\*\s*([^\n]+)")
    md_meta["scope"] = _search(r"\*\*Scope:\*\*\s*([^\n]+)")
    # Support both "Generated:" and "Generiert:"
    md_meta["generated_at"] = _search(r"\*\*(?:Generated|Generiert):\*\*\s*([^\n]+)")
    md_meta["updated_at"] = _search(r"\*\*Updated:\*\*\s*([^\n]+)")

    # Try old format first (Logistische Membran)
    logistic_match = re.search(
        r"Logistische Membran:\*\* R→\"(?P<R>.+?)\", Θ→\"(?P<Theta>.+?)\", β≈(?P<beta>[0-9.]+), ζ-Risiko: (?P<zeta>[^.]+)",
        md_content,
    )
    if logistic_match:
        md_meta["R_goal"] = logistic_match.group("R")
        md_meta["Theta_threshold"] = logistic_match.group("Theta")
        md_meta["beta_drive"] = float(logistic_match.group("beta"))
        md_meta["zeta_risk"] = logistic_match.group("zeta").strip()
    else:
        # Try new format (Logistic Frame section)
        md_meta["R_goal"] = _search(r"\*\*R_goal:\*\*\s*([^\n]+)")
        md_meta["Theta_threshold"] = _search(r"\*\*Theta_threshold:\*\*\s*([^\n]+)")
        beta_str = _search(r"\*\*beta_drive:\*\*\s*([0-9.]+)")
        if beta_str:
            md_meta["beta_drive"] = float(beta_str)
        md_meta["zeta_risk"] = _search(r"\*\*zeta_risk:\*\*\s*([^\n]+)")

    return md_meta


def _check_metadata_sync(json_data: dict, yaml_data: dict, md_meta: dict) -> bool:
    """Validate that version, timestamps, and scope align across the TriLayer."""

    drift_detected = False
    json_meta = json_data.get("metadata", {})
    yaml_meta = yaml_data.get("metadata", {})

    for label, j_val, y_val, m_val in [
        ("version", json_meta.get("version"), yaml_meta.get("version"), md_meta.get("version")),
        ("generated_at", json_meta.get("generated_at"), yaml_meta.get("generated_at"), md_meta.get("generated_at")),
        ("updated_at", json_meta.get("updated_at"), yaml_meta.get("updated_at"), md_meta.get("updated_at")),
        ("scope", json_meta.get("scope"), yaml_meta.get("scope"), md_meta.get("scope")),
    ]:
        print(f"🧭 {label}: JSON='{j_val}', YAML='{y_val}', MD='{m_val}'")
        if len({j_val, y_val, m_val}) > 1:
            print(f"⚠️  DRIFT: {label} mismatch across TriLayer")
            drift_detected = True
        else:
            print(f"✅ {label} aligned")

    return drift_detected


def _check_index_bridges() -> bool:
    """Ensure index files acknowledge the TriLayer validator hooks."""

    drift_detected = False
    index_targets = [
        (Path("feldtheorie_index.md"), ["validate-trilayer", "V6_ToDoListe"]),
        (Path("docs/docs_index.md"), ["validate-trilayer", "V6_ToDoListe"]),
    ]

    for path, tokens in index_targets:
        if not path.exists():
            print(f"⚠️  DRIFT: Index file missing → {path}")
            drift_detected = True
            continue

        text = path.read_text(encoding="utf-8").lower()
        missing_tokens = [t for t in tokens if t.lower() not in text]
        if missing_tokens:
            print(f"⚠️  DRIFT: {path} lacks references to {missing_tokens}")
            drift_detected = True
        else:
            print(f"✅ Index bridge OK: {path}")

    return drift_detected


def validate_trilayer(base_path: str = "releases/V6-Plans_etc", todo_name: str = "V6ToDorefresh") -> int:
    """
    Validate TriLayer consistency between YAML/JSON/MD.

    Args:
        base_path: Base directory containing trilayer files
        todo_name: Name prefix for trilayer files (V6_ToDoListe or V6ToDorefresh)

    Returns:
        0 if all checks pass, 1 if drift detected
    """
    base = Path(base_path)

    # Load TriLayer sources
    try:
        with open(base / f"{todo_name}.json") as f:
            json_data = json.load(f)
        with open(base / f"{todo_name}.yaml") as f:
            yaml_data = yaml.safe_load(f)
        md_path = base / f"{todo_name}.md"
        md_content = md_path.read_text(encoding="utf-8")
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
    md_meta = _parse_md_metadata(md_content)

    # β-drive validation
    json_beta = json_meta.get("beta_drive", 0.0)
    yaml_beta = yaml_meta.get("beta_drive", 0.0)
    md_beta = md_meta.get("beta_drive")

    print(f"📐 β-drive: JSON={json_beta}, YAML={yaml_beta}, MD={md_beta}")
    if abs(json_beta - yaml_beta) > 0.01 or (md_beta is not None and abs(json_beta - md_beta) > 0.01):
        print("⚠️  DRIFT: β-drive mismatch!")
        drift_detected = True
    else:
        print("✅ β-drive aligned")

    # ζ-risk validation
    json_zeta = json_meta.get("zeta_risk", "unknown")
    yaml_zeta = yaml_meta.get("zeta_risk", "unknown")
    md_zeta = md_meta.get("zeta_risk")

    print(f"🌀 ζ-risk: JSON={json_zeta}, YAML={yaml_zeta}, MD={md_zeta}")
    if len({json_zeta, yaml_zeta, md_zeta}) > 1:
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
    md_R = md_meta.get("R_goal", "")
    json_Theta = json_meta.get("Theta_threshold", "")
    yaml_Theta = yaml_meta.get("Theta_threshold", "")
    md_Theta = md_meta.get("Theta_threshold", "")

    print(f"🎯 R-goal: JSON='{json_R}', YAML='{yaml_R}', MD='{md_R}'")
    if len({json_R, yaml_R, md_R}) > 1:
        print("⚠️  DRIFT: R-goal mismatch!")
        drift_detected = True
    else:
        print("✅ R-goal aligned")

    print(f"🎯 Θ-threshold: JSON='{json_Theta}', YAML='{yaml_Theta}', MD='{md_Theta}'")
    if len({json_Theta, yaml_Theta, md_Theta}) > 1:
        print("⚠️  DRIFT: Θ-threshold mismatch!")
        drift_detected = True
    else:
        print("✅ Θ-threshold aligned")

    drift_detected |= _check_metadata_sync(json_data, yaml_data, md_meta)
    drift_detected |= _check_index_bridges()

    print("\n🎯 TriLayer validation complete")

    if drift_detected:
        print("⚠️  DRIFT DETECTED - Manual synchronization required")
        return 1
    else:
        print("✅ All TriLayer sources synchronized")
        return 0


if __name__ == "__main__":
    # Support both V6_ToDoListe and V6ToDorefresh trilayers
    import argparse
    parser = argparse.ArgumentParser(description="Validate TriLayer consistency")
    parser.add_argument("--name", default="V6ToDorefresh",
                        help="Trilayer name prefix (default: V6ToDorefresh)")
    parser.add_argument("--path", default="releases/V6-Plans_etc",
                        help="Base path (default: releases/V6-Plans_etc)")
    args = parser.parse_args()

    sys.exit(validate_trilayer(base_path=args.path, todo_name=args.name))
