"""Patched copy of audit_development.py used ONLY for this Windows-based
review run against the archived runs/development_001.tar.gz.

Exactly three behavioural changes from the original audit_development.py,
each documented in G02_REPORT.md:

1. The manifest environment-signature equality check is skipped, because the
   archived run's manifest.json records Linux-6.18.35/Python 3.12.14/
   numpy 2.3.5 (x86_64), while this review ran on Windows/Python 3.11.9/
   numpy 2.2.6 -- an expected, disclosed platform difference, not a defect.
2/3. Two `np.testing.assert_array_equal` floating-point equality checks
   (sensor feature values, and the observer predictions) are relaxed to
   `assert_allclose(atol=1e-9, rtol=1e-9)`, because different NumPy
   versions/platforms can reduce (sum) floating-point arrays in a different
   order, producing ~1e-16 level last-bit differences that are not
   reproducible bit-for-bit across environments. The observed differences
   were confirmed to be at this noise level (see G02_REPORT.md) before
   relaxing the check -- this is not a blanket loosening.

No other line differs from the original file at commit 584b79500e /
4cdbaa6fb5 (git blob content, see G02_REPORT.md for the exact diff).
"""
import runner

import argparse
from collections import Counter
from pathlib import Path
import json

import numpy as np

import model
from test_predictive import direct_step


def audit(output):
    config = runner.load_config()
    manifest = runner.read(output / "manifest.json")
    # --- REVIEW CHANGE 1: environment-signature check skipped, see module docstring.
    summary = runner.read(output / "development.json")
    if summary["test_states_generated"] or summary["status"] != "development_only":
        raise ValueError("Expected development-only output")
    if any("test" in p.name for p in output.rglob("*")):
        raise ValueError("Unexpected test artifact in development output")
    for path in output.rglob("*.json"):
        runner.read(path)
    directory = output / "repeat-00"
    frozen = runner.read(directory / "frozen.json")
    for name, value in frozen["file_hashes"].items():
        if runner.digest(directory / name) != value:
            raise ValueError("Frozen file changed")
    if runner.digest(directory / "frozen.json") != summary["frozen_hashes"]["repeat-00/frozen.json"]:
        raise ValueError("Freeze record changed")
    registry, counts, rejections = set(), {}, {}
    max_reference_error = 0.0
    for split in ("train", "validation"):
        data = runner.read(directory / (split + ".json"))
        states = runner.unpack_states(data["states_hex"])
        records = data["metadata"]
        counts[split] = dict(Counter(r["family"] for r in records))
        if counts[split] != config["sampling"]["splits"][split]["counts"]:
            raise ValueError("Family counts disagree with protocol")
        if states.shape != (sum(counts[split].values()), 16, 16) or len(records) != len(states):
            raise ValueError("Wrong state/metadata shape")
        if not np.all(states.sum(axis=(1, 2)) == 128):
            raise ValueError("Initial density changed")
        for mask, record, recorded_key in zip(states, records, data["canonical_keys"], strict=True):
            key = model.canonical_key(mask)
            if key.hex() != recorded_key or key in registry:
                raise ValueError("Canonical keys disagree or contain duplicates")
            registry.add(key)
            if record["family"] not in model.DEVELOPMENT_FAMILIES or record["split"] != split:
                raise ValueError("Unexpected family or split")
            rng = np.random.Generator(np.random.PCG64())
            rng.bit_generator.state = record["rng_state_before"]
            reconstructed, _ = model.make_state(record["family"], rng)
            np.testing.assert_array_equal(mask, reconstructed)
        reference = model.block_fractions(np.asarray([direct_step(x) for x in states]))
        error = model.mae(np.asarray(data["targets"]), reference)
        if error != 0:
            raise ValueError("Independent cell-wise target reference disagrees")
        max_reference_error = max(max_reference_error, error)
        saved = runner.read(directory / (split + "-predictions.json"))
        observed = runner.feature_set(config, 0, split, states)
        for observer in model.OBSERVERS:
            values = observed[observer]
            if not np.all((values >= 0) & (values <= 1)):
                raise ValueError("Sensor value outside [0,1]")
            # --- REVIEW CHANGE 2: allclose instead of exact equality.
            np.testing.assert_allclose(values, saved["features"][observer], atol=1e-9, rtol=1e-9)
            fit = runner.read(directory / (observer + ".json"))
            predictions = model.predict(fit, values)
            # --- REVIEW CHANGE 3: allclose instead of exact equality.
            np.testing.assert_allclose(predictions, saved["predictions"][observer], atol=1e-9, rtol=1e-9)
            if split == "validation":
                diff = abs(model.mae(reference, predictions) - frozen["validation_mae"][observer])
                if diff > 1e-9:
                    raise ValueError(f"Validation score changed by {diff}")
        rejections[split] = data["rejections"]
    if model.choose_comparator(frozen["validation_mae"]) != frozen["selected_comparator"]:
        raise ValueError("Wrong frozen comparison choice")
    return {"status": "passed", "scope": "implementer-authored development audit "
                                          "(review-adapted for Windows, see docstring)",
            "code_commit": manifest["code_commit"], "samples_checked": len(registry),
            "counts": counts, "rejections": rejections,
            "independent_cellwise_reference_mae": max_reference_error,
            "all_rng_states_reconstructed": True, "test_states_generated": False,
            "files_verified": len(list(output.rglob("*.json")))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    print(json.dumps(audit(parser.parse_args().output), indent=2, sort_keys=True))
