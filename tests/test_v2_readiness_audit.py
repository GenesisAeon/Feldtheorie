from analysis.v2_readiness_audit import parse_dataset_status


def test_parse_dataset_status_marks_manifest_components_as_declared() -> None:
    manifest = {
        "datasets": [
            {
                "id": "ds-001",
                "domain": "climate",
                "path": "data/climate/urban_heat_intensity.csv",
                "expected_outputs": ["analysis/results/urban_heat_global_fit.json"],
                "resonance_status": "active",
                "threshold_Theta_estimate": 3.2,
                "steepness_beta_target": 14.5,
            }
        ]
    }

    datasets = parse_dataset_status(manifest)

    assert len(datasets) == 1
    component_names_to_declared = {
        component.name: component.declared_exists for component in datasets[0].components
    }
    assert component_names_to_declared["data"] is True
    assert component_names_to_declared["metadata"] is True
    assert component_names_to_declared["urban_heat_global_fit.json"] is True
