"""Exact conditional entropy and posterior reconstruction on binary lattices.

Run from this directory: python run_exact.py --output runs/calibration_v1
Only NumPy is required. Existing output directories are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


def all_states(side: int = 4) -> np.ndarray:
    """Enumerate small binary arrays in ascending integer order."""
    if side not in (2, 4):
        raise ValueError("Exact enumeration supports only side 2 or 4")
    ids = np.arange(1 << (side * side), dtype=np.uint32)
    bits = ((ids[:, None] >> np.arange(side * side)) & 1).astype(np.uint8)
    return bits.reshape(-1, side, side)


def block_counts(states: np.ndarray) -> np.ndarray:
    count, side, _ = states.shape
    return states.reshape(count, side // 2, 2, side // 2, 2).sum(axis=(2, 4)).reshape(count, -1)


def boundary_length(states: np.ndarray) -> np.ndarray:
    """Count periodic horizontal/vertical disagreements on a 4x4 lattice."""
    if states.shape[1:] != (4, 4):
        raise ValueError("The boundary convention is defined only for 4x4")
    return np.count_nonzero(states != np.roll(states, 1, axis=1), axis=(1, 2)) + np.count_nonzero(
        states != np.roll(states, 1, axis=2), axis=(1, 2)
    )


def exact_metrics(states: np.ndarray, labels: np.ndarray) -> tuple[dict, list[dict]]:
    """Return ensemble-averaged loss and exact observation-class records."""
    x = states.reshape(len(states), -1)
    labels = np.asarray(labels).reshape(len(states), -1)
    unique, inverse, counts = np.unique(labels, axis=0, return_inverse=True, return_counts=True)
    ones = np.zeros((len(counts), x.shape[1]), dtype=np.int64)
    np.add.at(ones, inverse, x)
    errors = np.minimum(ones, counts[:, None] - ones).sum(axis=1)
    weights = counts / len(x)
    conditional = float(np.dot(weights, np.log2(counts)))
    entropy = math.log2(len(x))
    metrics = {
        "microstates": len(x),
        "observation_classes": len(counts),
        "microstate_entropy_bits": entropy,
        "conditional_entropy_bits": conditional,
        "retained_information_bits": entropy - conditional,
        "bayes_cell_error_fraction": float(errors.sum() / x.size),
    }
    classes = [
        {
            "label": ":".join(str(int(v)) for v in label),
            "microstates": int(n),
            "conditional_entropy_bits": math.log2(int(n)),
            "bayes_cell_error_fraction": float(err / (n * x.shape[1])),
        }
        for label, n, err in zip(unique, counts, errors)
    ]
    return metrics, classes


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    states = all_states()
    occupancy = states.sum(axis=(1, 2))
    config = json.loads((here / "protocol.json").read_text())
    results = {
        "protocol_id": config["protocol_id"],
        "status": "exact_calibration_not_hypothesis_confirmation",
        "base_commit": config["base_commit"],
        "protocol_sha256": sha256(here / "PROTOCOL.md"),
        "protocol_json_sha256": sha256(here / "protocol.json"),
        "runner_sha256": sha256(Path(__file__)),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "diagnostic_seeds": config["diagnostic_seeds"],
        "independent_review": "pending",
        "ensembles": {},
    }
    class_records = []
    for name, sample in (
        ("uniform_all", states),
        ("uniform_density_half", states[occupancy == 8]),
    ):
        block = block_counts(sample)
        boundary = boundary_length(sample)
        observers = {
            "identity": np.arange(len(sample))[:, None],
            "occupancy": sample.sum(axis=(1, 2))[:, None],
            "block_counts": block,
            "block_counts_boundary": np.column_stack((block, boundary)),
        }
        for seed in config["diagnostic_seeds"]:
            scrambled = np.random.default_rng(seed).permutation(boundary)
            observers[f"block_counts_scrambled_{seed}"] = np.column_stack((block, scrambled))
        measured = {}
        for observer, labels in observers.items():
            metrics, classes = exact_metrics(sample, labels)
            measured[observer] = metrics
            if name == "uniform_density_half" and observer in (
                "block_counts", "block_counts_boundary"
            ):
                class_records.extend({"observer": observer, **row} for row in classes)
        results["ensembles"][name] = measured
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    with (output / "observation_classes.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(class_records[0]))
        writer.writeheader()
        writer.writerows(class_records)
    rows = []
    for ensemble, measured in results["ensembles"].items():
        for observer, metrics in measured.items():
            rows.append({"ensemble": ensemble, "observer": observer, **metrics})
    (output / "observations.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output)
    for ensemble, measured in report["ensembles"].items():
        print(ensemble)
        for observer, row in measured.items():
            print(f"  {observer}: H={row['conditional_entropy_bits']:.6f} bits, "
                  f"cell_error={row['bayes_cell_error_fraction']:.6f}")
