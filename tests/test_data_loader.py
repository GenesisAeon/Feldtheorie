import pandas as pd
import pytest

from utils.data_loader import (
    calculate_tau_star,
    load_all,
    load_dataset,
    load_metadata,
)


def test_load_metadata_reads_yaml(tmp_path):
    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()

    metadata_file = metadata_dir / "sample.yaml"
    metadata_file.write_text("dataset: sample_data\nbeta_estimate: 0.42\n")

    meta = load_metadata(metadata_file.name, metadata_dir=str(metadata_dir))

    assert meta["dataset"] == "sample_data"
    assert meta["beta_estimate"] == 0.42


def test_load_dataset_prefers_available_format(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset_name = "Example Dataset"
    csv_path = data_dir / "example_dataset.csv"
    pd.DataFrame({"value": [1, 2, 3]}).to_csv(csv_path, index=False)

    loaded = load_dataset({"dataset": dataset_name}, data_dir=str(data_dir))

    assert list(loaded["value"]) == [1, 2, 3]


def test_load_dataset_requires_dataset_field():
    with pytest.raises(ValueError):
        load_dataset({}, data_dir="unused")


def test_load_dataset_supports_compressed_csv(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset_name = "Compressed Data"
    gzip_path = data_dir / "compressed_data.csv.gz"
    pd.DataFrame({"value": [10, 20]}).to_csv(gzip_path, index=False, compression="gzip")

    loaded = load_dataset({"dataset": dataset_name}, data_dir=str(data_dir))

    assert list(loaded["value"]) == [10, 20]


def test_load_all_collects_metadata_and_optional_data(tmp_path):
    metadata_dir = tmp_path / "metadata"
    data_dir = tmp_path / "data"
    metadata_dir.mkdir()
    data_dir.mkdir()

    # Entry with data
    (metadata_dir / "with_data.yaml").write_text("dataset: alpha\n")
    pd.DataFrame({"x": [0]}).to_csv(data_dir / "alpha.csv", index=False)

    # Entry without data
    (metadata_dir / "metadata_only.yaml").write_text("dataset: beta\n")

    loaded = load_all(metadata_dir=str(metadata_dir), data_dir=str(data_dir))

    assert set(loaded.keys()) == {"alpha", "beta"}
    assert list(loaded["alpha"]["data"]["x"]) == [0]
    assert loaded["beta"]["data"] is None


def test_calculate_tau_star_handles_threshold_crossing():
    assert calculate_tau_star(beta=2.0, theta=5.0, R=1.0) > 0
    assert calculate_tau_star(beta=1.0, theta=1.0, R=2.0) == 0.0
