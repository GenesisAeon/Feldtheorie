"""Utilities to parse UTAC data manifest entries into structured records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ManifestDataset:
    """Structured view over a manifest dataset entry."""

    identifier: str
    path: Path
    domain: str
    expected_outputs: List[Path]
    theta_estimate: Optional[float]
    beta_target: Optional[float]
    resonance_status: str

    @property
    def metadata_path(self) -> Path:
        return (ROOT / self.path).with_suffix(".metadata.json")


def load_manifest(manifest_path: Path) -> List[ManifestDataset]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    datasets: List[ManifestDataset] = []
    for entry in payload.get("datasets", []):
        expected = [ROOT / Path(item) for item in entry.get("expected_outputs", [])]
        datasets.append(
            ManifestDataset(
                identifier=entry["id"],
                path=Path(entry["path"]),
                domain=entry.get("domain", ""),
                expected_outputs=expected,
                theta_estimate=entry.get("threshold_Theta_estimate"),
                beta_target=entry.get("steepness_beta_target"),
                resonance_status=entry.get("resonance_status", "draft"),
            )
        )
    return datasets


def filter_datasets(
    datasets: Sequence[ManifestDataset],
    domains: Optional[Iterable[str]] = None,
    identifiers: Optional[Iterable[str]] = None,
) -> List[ManifestDataset]:
    domains_norm = {domain.lower() for domain in domains} if domains else None
    identifiers_norm = {item.lower() for item in identifiers} if identifiers else None

    filtered: List[ManifestDataset] = []
    for dataset in datasets:
        if domains_norm and dataset.domain.lower() not in domains_norm:
            continue
        if identifiers_norm and dataset.identifier.lower() not in identifiers_norm:
            continue
        filtered.append(dataset)
    return filtered


def resolve_output_path(dataset: ManifestDataset, default_name: str) -> Path:
    for candidate in dataset.expected_outputs:
        if candidate.suffix.lower() == ".json":
            return candidate
    return ROOT / "analysis" / "results" / default_name


__all__ = [
    "ManifestDataset",
    "filter_datasets",
    "load_manifest",
    "resolve_output_path",
]
