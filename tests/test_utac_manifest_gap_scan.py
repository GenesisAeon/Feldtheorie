import json
from pathlib import Path

from analysis.utac_manifest_gap_scan import scan_manifest


def test_scan_manifest_reports_declared_actual_drift(tmp_path: Path) -> None:
    existing_file = tmp_path / "existing.json"
    existing_file.write_text("{}", encoding="utf-8")

    missing_file = tmp_path / "missing.json"

    manifest = {
        "meta": {"logistic": {"beta": 4.8, "theta": 0.66, "mean_readiness": 0.9}},
        "datasets": [
            {
                "id": "drift-dataset",
                "domain": "test",
                "actual_readiness_ratio": 0.5,
                "components": [
                    {
                        "name": "declared-missing-but-present",
                        "path": str(existing_file),
                        "kind": "data",
                        "declared_exists": False,
                    },
                    {
                        "name": "declared-present-but-missing",
                        "path": str(missing_file),
                        "kind": "metadata",
                        "declared_exists": True,
                    },
                ],
            }
        ],
        "analysis_targets": [],
        "doc_targets": [],
        "sigillin_targets": [],
        "simulator_targets": [],
    }

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = scan_manifest(manifest_path)

    assert result["summary"]["declared_actual_drift_count"] == 2

    drift_entries = result["gaps"]["declared_actual_drift"]
    assert len(drift_entries) == 2
    assert all(entry["dataset_id"] == "drift-dataset" for entry in drift_entries)


def test_scan_manifest_ignores_components_without_declared_flag(tmp_path: Path) -> None:
    existing_file = tmp_path / "existing.json"
    existing_file.write_text("{}", encoding="utf-8")

    manifest = {
        "meta": {"logistic": {"beta": 4.8, "theta": 0.66, "mean_readiness": 0.5}},
        "datasets": [
            {
                "id": "legacy-dataset",
                "domain": "test",
                "actual_readiness_ratio": 1.0,
                "components": [
                    {
                        "name": "legacy-component",
                        "path": str(existing_file),
                        "kind": "data",
                    }
                ],
            }
        ],
        "analysis_targets": [],
        "doc_targets": [],
        "sigillin_targets": [],
        "simulator_targets": [],
    }

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = scan_manifest(manifest_path)

    assert result["summary"]["declared_actual_drift_count"] == 0
    assert result["gaps"]["declared_actual_drift"] == []
