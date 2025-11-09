from pathlib import Path

from analysis.climate_beta_extractor import process_dataset
from analysis.utac_manifest import filter_datasets, load_manifest


def test_process_dataset_simulation(tmp_path):
    manifest = load_manifest(Path("data/utac_v1_3_data_manifest.yaml"))
    dataset = filter_datasets(manifest, identifiers=["utac-v1_3-ds-001"])[0]

    payload = process_dataset(dataset, simulate_missing=True, seed=123)

    assert payload["dataset_id"] == "utac-v1_3-ds-001"
    assert payload["data_origin"] == "simulated"
    assert payload["delta_aic_guard_passed"] is True
    assert payload["beta_manifest_target"] == dataset.beta_target
    assert payload["theta_manifest_estimate"] == dataset.theta_estimate
    assert payload["resonance_status"] == dataset.resonance_status

