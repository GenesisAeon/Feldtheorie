"""Regression tests for the shared data loader utilities."""

from __future__ import annotations

import pandas as pd
import pytest

from utils.data_loader import calculate_tau_star, load_all, load_dataset, load_metadata


def test_load_metadata_reads_yaml(tmp_path) -> None:
    """Metadata YAML should round-trip through the loader."""

    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()

    metadata_file = metadata_dir / "sample.yaml"
    metadata_file.write_text("dataset: sample_data\nbeta_estimate: 0.42\n")

    meta = load_metadata(metadata_file.name, metadata_dir=str(metadata_dir))

    assert meta["dataset"] == "sample_data"
    assert meta["beta_estimate"] == 0.42


def test_load_dataset_reads_csv_with_normalized_name(tmp_path) -> None:
    """CSV files should load after name normalization to σ(β(R-Θ)) paths."""

    meta = {"dataset": "Resonant Data"}
    df = pd.DataFrame({"value": [1, 2, 3]})
    csv_path = tmp_path / "resonant_data.csv"
    df.to_csv(csv_path, index=False)

    loaded = load_dataset(meta, data_dir=tmp_path)

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_prefers_available_format(tmp_path) -> None:
    """A plain CSV should be ingested when it is present."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset_name = "Example Dataset"
    csv_path = data_dir / "example_dataset.csv"
    df = pd.DataFrame({"value": [1, 2, 3]})
    df.to_csv(csv_path, index=False)

    loaded = load_dataset({"dataset": dataset_name}, data_dir=str(data_dir))

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_handles_gzipped_csv(tmp_path) -> None:
    """Gzipped CSV should load when it is the available τ-track."""

    meta = {"dataset": "Compressed Echo"}
    df = pd.DataFrame({"signal": [0.1, 0.2]})
    gz_path = tmp_path / "compressed_echo.csv.gz"
    df.to_csv(gz_path, index=False, compression="gzip")

    loaded = load_dataset(meta, data_dir=tmp_path)

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_uses_provided_extension_without_duplication(tmp_path) -> None:
    """Explicit extensions should be honored without duplicating suffixes."""

    meta = {"dataset": "Observations.csv.gz"}
    df = pd.DataFrame({"signal": [1, 2, 3]})
    gz_path = tmp_path / "observations.csv.gz"
    df.to_csv(gz_path, index=False, compression="gzip")

    loaded = load_dataset(meta, data_dir=tmp_path)

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_falls_back_to_other_known_formats(tmp_path) -> None:
    """When a specified format is absent the loader should try other known suffixes."""

    meta = {"dataset": "Signal.csv"}
    df = pd.DataFrame({"signal": [4, 5]})
    gz_path = tmp_path / "signal.csv.gz"
    df.to_csv(gz_path, index=False, compression="gzip")

    loaded = load_dataset(meta, data_dir=tmp_path)

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_reads_json(tmp_path) -> None:
    """JSON datasets should hydrate into DataFrames when present."""

    meta = {"dataset": "Json Resonance"}
    df = pd.DataFrame({"signal": [0.5, 0.9]})
    json_path = tmp_path / "json_resonance.json"
    df.to_json(json_path, orient="records")

    loaded = load_dataset(meta, data_dir=tmp_path)

    pd.testing.assert_frame_equal(loaded, df)


def test_load_dataset_requires_dataset_field() -> None:
    """Missing dataset metadata should surface as a clear validation error."""

    with pytest.raises(ValueError, match="non-empty 'dataset' field"):
        load_dataset({})


def test_load_dataset_rejects_none_dataset() -> None:
    """Explicit null dataset names should be treated as missing metadata."""

    with pytest.raises(ValueError, match="non-empty 'dataset' field"):
        load_dataset({"dataset": None})


def test_load_dataset_strict_reports_search_log(tmp_path) -> None:
    """Strict mode should expose the candidate search log when nothing is found."""

    meta = {"dataset": "Missing Signal"}

    with pytest.raises(FileNotFoundError) as excinfo:
        load_dataset(meta, data_dir=tmp_path, strict=True)

    message = str(excinfo.value)
    assert "missing_signal.csv" in message
    assert "missing_signal.csv.gz" in message
    assert "missing_signal.json" in message


def test_load_all_collects_metadata_and_optional_data(tmp_path) -> None:
    """load_all should collect metadata even when data files are absent."""

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


def test_load_all_requires_dataset_field(tmp_path) -> None:
    """Incomplete metadata should surface a clear σ(β(R-Θ)) validation error."""

    metadata_dir = tmp_path / "metadata"
    data_dir = tmp_path / "data"
    metadata_dir.mkdir()
    data_dir.mkdir()

    (metadata_dir / "broken.yaml").write_text("title: missing dataset\n")

    with pytest.raises(ValueError, match="missing the required 'dataset' field"):
        load_all(metadata_dir=str(metadata_dir), data_dir=str(data_dir))


def test_calculate_tau_star_requires_positive_beta() -> None:
    """β must be positive to keep the τ* curve physically meaningful."""

    for beta in (0.0, -1.2):
        with pytest.raises(ValueError, match="beta must be positive"):
            calculate_tau_star(beta=beta, theta=1.0, R=0.5)


def test_calculate_tau_star_zero_when_at_threshold() -> None:
    """If R ≥ Θ the τ* horizon collapses to zero."""

    assert calculate_tau_star(beta=3.3, theta=1.0, R=1.0) == 0.0


def test_calculate_tau_star_positive_when_below_threshold() -> None:
    """Below the threshold the τ* horizon should remain finite and positive."""

    tau_star = calculate_tau_star(beta=2.0, theta=5.0, R=1.0)
    assert tau_star > 0
