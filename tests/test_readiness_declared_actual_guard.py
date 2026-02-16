from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path("scripts/validation/check_readiness_declared_actual.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("readiness_guard", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collect_mismatches_detects_dataset_component_drift() -> None:
    module = _load_module()
    report = {
        "datasets": [
            {
                "id": "urban_heat",
                "domain": "climate",
                "components": [
                    {
                        "name": "data",
                        "path": "data/socio_ecology/urban_heat/urban_heat_global.csv",
                        "declared_exists": False,
                        "actual_exists": True,
                    },
                    {
                        "name": "metadata",
                        "path": "data/socio_ecology/urban_heat/urban_heat_global.metadata.json",
                        "declared_exists": True,
                        "actual_exists": True,
                    },
                ],
            }
        ]
    }

    mismatches = module._collect_mismatches(report)

    assert len(mismatches) == 1
    mismatch = mismatches[0]
    assert mismatch["dataset"] == "urban_heat"
    assert mismatch["domain"] == "climate"
    assert mismatch["component"] == "data"
    assert mismatch["declared_exists"] is False
    assert mismatch["actual_exists"] is True


def test_collect_mismatches_keeps_legacy_domain_shape_compatible() -> None:
    module = _load_module()
    report = {
        "domains": [
            {
                "name": "legacy-domain",
                "components": [
                    {
                        "name": "legacy-component",
                        "path": "legacy/path",
                        "declared_exists": True,
                        "actual_exists": False,
                    }
                ],
            }
        ]
    }

    mismatches = module._collect_mismatches(report)

    assert len(mismatches) == 1
    assert mismatches[0]["dataset"] == "legacy-domain"
    assert mismatches[0]["domain"] == "legacy-domain"
