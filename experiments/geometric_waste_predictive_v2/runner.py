"""Staged execution of GW-PRED-002; development never generates test states.

python runner.py development --output runs/development_001 --code-commit FULL_SHA
python runner.py prepare --output runs/confirmatory_001 --code-commit FULL_SHA
python runner.py evaluate --output runs/confirmatory_001 --code-commit FULL_SHA --reviews reviews.json

Prepare freezes all 20 training/validation fits. Evaluate requires review
evidence and the immutable completion record from prepare. Resume a stopped
stage with --resume; completed units and earlier runs are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import resource
import signal
import time
import uuid
from pathlib import Path

# Limit numerical worker threads before importing numerical libraries.
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np

from model import (COMPARATORS, OBSERVERS, block_fractions, choose_comparator,
                   features, fit_ridge, generate_split, mae, predict,
                   repeat_bootstrap, step)

SUPPORTED_PROTOCOL_SHA256 = "38de6c3ec0574f4abd712beda000255058821be66f23b12185301af39d78a578"
HERE = Path(__file__).resolve().parent
ACTIVE_BUDGET = None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config():
    path = HERE / "protocol.json"
    if digest(path) != SUPPORTED_PROTOCOL_SHA256:
        raise ValueError("This runner has not been verified against the modified protocol")
    return json.loads(path.read_text())


def content_digest(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path, checkpoint=True):
    data = json.loads(Path(path).read_text())
    checksum = data.pop("_content_sha256", None)
    if checkpoint or checksum is not None:
        if checksum != content_digest(data):
            raise ValueError("Checkpoint content checksum mismatch: " + str(path))
    return data


def write_once(path, data):
    """Publish complete JSON atomically without replacing an existing file."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    data = dict(data, _content_sha256=content_digest(data))
    raw = (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if ACTIVE_BUDGET is not None:
        ACTIVE_BUDGET.reserve(len(raw))
    temporary = path.parent / (path.name + ".partial-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()  # Only this writer's unpublished temporary file.


class Budget:
    def __init__(self, config, output):
        self.output = output
        self.start = time.monotonic()
        self.last_disk_check = 0.0
        self.seconds = config["batch_active_seconds_max"]
        self.disk_limit = int(config["output_gib_max"] * 1024**3)
        memory_limit = int(config["runner_memory_gib_max"] * 1024**3)
        self.previous_memory = resource.getrlimit(resource.RLIMIT_AS)
        soft, hard = self.previous_memory
        if soft != resource.RLIM_INFINITY:
            memory_limit = min(memory_limit, soft)
        if hard != resource.RLIM_INFINITY:
            memory_limit = min(memory_limit, hard)
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, hard))
        self.previous_alarm = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, self._expired)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    @staticmethod
    def _expired(signum, frame):
        raise TimeoutError("Active batch time limit reached; resume the same stage")

    def check(self):
        now = time.monotonic()
        if now - self.start > self.seconds:
            raise TimeoutError("Active batch time limit reached")
        if now - self.last_disk_check >= 0.5:
            size = sum(p.stat().st_size for p in self.output.rglob("*") if p.is_file())
            if size >= self.disk_limit:
                raise RuntimeError("Output storage limit reached")
            self.last_disk_check = now

    def reserve(self, additional_bytes, log=False):
        # One writer/process; reserve 64 KiB so an incomplete batch can log its cause.
        size = sum(p.stat().st_size for p in self.output.rglob("*") if p.is_file())
        if size + additional_bytes + (0 if log else 65536) > self.disk_limit:
            raise RuntimeError("Output storage limit would be exceeded")

    def close(self):
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self.previous_alarm)
        resource.setrlimit(resource.RLIMIT_AS, self.previous_memory)


def signature(mode, code_commit):
    if re.fullmatch(r"[0-9a-f]{40}", code_commit or "") is None:
        raise ValueError("Record the full implementation commit SHA with --code-commit")
    return {"mode": mode, "protocol_id": "GW-PRED-002",
            "code_commit": code_commit,
            "protocol_sha256": digest(HERE / "protocol.json"),
            "protocol_md_sha256": digest(HERE / "PROTOCOL.md"),
            "runner_sha256": digest(HERE / "runner.py"),
            "model_sha256": digest(HERE / "model.py"),
            "python": platform.python_version(), "numpy": np.__version__,
            "platform": platform.platform(), "machine": platform.machine()}


def open_run(output, mode, code_commit, resume=False):
    expected = signature(mode, code_commit)
    if output.exists():
        if not resume:
            raise FileExistsError("Use a new output directory or explicit --resume")
        if read(output / "manifest.json") != expected:
            raise ValueError("Resume requires the same protocol, source and environment")
    else:
        if resume:
            raise FileNotFoundError("Cannot resume a run that does not exist")
        output.mkdir(parents=True)
        write_once(output / "manifest.json", expected)
    return expected


def pack_states(states):
    return [np.packbits(x.reshape(-1), bitorder="big").tobytes().hex() for x in states]


def unpack_states(rows):
    if any(len(row) != 64 for row in rows):
        raise ValueError("Invalid 16x16 packed state")
    return np.asarray([np.unpackbits(np.frombuffer(bytes.fromhex(row), dtype=np.uint8),
                                    bitorder="big").reshape(16, 16) for row in rows])


def split_data(config, directory, repeat, split, registry, development, budget):
    path = directory / (split + ".json")
    if path.exists():
        data = read(path)
        keys = [bytes.fromhex(key) for key in data["canonical_keys"]]
        if len(set(keys)) != len(keys) or any(key in registry for key in keys):
            raise ValueError("Duplicate checkpoint states")
        registry.update(keys)
        return unpack_states(data["states_hex"]), data
    states, records, keys, rejects = generate_split(
        config, repeat, split, registry, development=development, check=budget.check)
    data = {"split": split, "repeat": repeat, "states_hex": pack_states(states),
            "metadata": records, "canonical_keys": keys, "rejections": rejects,
            "targets": block_fractions(step(states)).tolist()}
    write_once(path, data)
    budget.check()
    return states, data


def feature_set(config, repeat, split, states):
    split_id = config["sampling"]["splits"][split]["split_id"]
    seed = np.random.SeedSequence([config["sampling"]["shuffle_seed"], repeat, split_id])
    return features(states, np.random.Generator(np.random.PCG64(seed)))


def prepare_repeat(config, output, repeat, development, budget):
    directory = output / f"repeat-{repeat:02d}"
    directory.mkdir(exist_ok=True)
    done = directory / "frozen.json"
    if done.exists():
        frozen = read(done)
        for name, checksum in frozen["file_hashes"].items():
            if digest(directory / name) != checksum:
                raise ValueError("Frozen checkpoint was changed")
        return frozen
    registry = set()
    train, train_record = split_data(config, directory, repeat, "train", registry, development, budget)
    validation, validation_record = split_data(
        config, directory, repeat, "validation", registry, development, budget)
    train_features = feature_set(config, repeat, "train", train)
    validation_features = feature_set(config, repeat, "validation", validation)
    train_y = np.asarray(train_record["targets"])
    validation_y = np.asarray(validation_record["targets"])
    scores = {"PERSISTENCE": mae(validation_y, block_fractions(validation))}
    fits = {}
    for observer in OBSERVERS:
        budget.check()
        path = directory / (observer + ".json")
        if path.exists():
            fitted = read(path)
        else:
            fitted = fit_ridge(train_features[observer], train_y, validation_features[observer],
                               validation_y, config["learner"]["lambda_grid"])
            write_once(path, fitted)
        scores[observer] = fitted["validation_mae"]
        fits[observer] = fitted
    for split, observed, data in (("train", train_features, train_record),
                                   ("validation", validation_features, validation_record)):
        path = directory / (split + "-predictions.json")
        if path.exists():
            read(path)
        else:
            predictions = {name: predict(fits[name], observed[name]).tolist() for name in OBSERVERS}
            predictions["PERSISTENCE"] = observed["BASE"][:, :16].tolist()
            write_once(path, {"features": {k: v.tolist() for k, v in observed.items()},
                              "predictions": predictions,
                              "sample_ids": [v["sample_id"] for v in data["metadata"]]})
    frozen = {"repeat": repeat, "selected_comparator": choose_comparator(scores),
              "validation_mae": scores,
              "file_hashes": {p.name: digest(p) for p in directory.glob("*.json")}}
    write_once(done, frozen)
    return frozen


def verify_reviews(path, config):
    """Require traceable review reports; identity/independence needs human review.

    This validates an evidence record, not cryptographic reviewer identity.
    A boolean --approved flag is deliberately insufficient.
    """
    if path is None:
        raise ValueError("G01 and implementation review evidence is required before evaluation")
    reviews = read(path, checkpoint=False)
    if reviews.get("protocol_sha256") != digest(HERE / "protocol.json"):
        raise ValueError("Review concerns a different protocol")
    if reviews.get("runner_sha256") != digest(HERE / "runner.py") or reviews.get(
        "model_sha256") != digest(HERE / "model.py"):
        raise ValueError("Review concerns a different implementation")
    for key in ("G01", "implementation"):
        entry = reviews.get(key, {})
        if entry.get("verdict") != "approved" or not entry.get("reviewer"):
            raise ValueError("Missing approved review: " + key)
        report = Path(path).parent / entry.get("report_path", "")
        if not report.is_file() or report.stat().st_size == 0:
            raise ValueError("Missing review report: " + key)
        if digest(report) != entry.get("report_sha256"):
            raise ValueError("Review report checksum mismatch: " + key)
    return reviews


def evaluate_repeat(config, output, repeat, budget):
    directory = output / f"repeat-{repeat:02d}"
    path = directory / "evaluated.json"
    if path.exists():
        cached = read(path)
        for name, checksum in cached["file_hashes"].items():
            if digest(directory / name) != checksum:
                raise ValueError("Evaluated checkpoint changed")
        return cached
    registry = set()
    for split in ("train", "validation"):
        registry.update(bytes.fromhex(key) for key in read(directory / (split + ".json"))["canonical_keys"])
    frozen = read(directory / "frozen.json")
    records = {"repeat": repeat, "selected_comparator": frozen["selected_comparator"], "splits": {}}
    for split in ("test_known", "test_unseen"):
        budget.check()
        states, data = split_data(config, directory, repeat, split, registry, False, budget)
        observed = feature_set(config, repeat, split, states)
        target = np.asarray(data["targets"])
        predictions = {name: predict(read(directory / (name + ".json")), observed[name])
                       for name in OBSERVERS}
        predictions["PERSISTENCE"] = block_fractions(states)
        families = np.asarray([record["family"] for record in data["metadata"]])
        family_scores = {family: {name: mae(target[families == family], value[families == family])
                                 for name, value in predictions.items()}
                         for family in config["sampling"]["splits"][split]["counts"]}
        prediction_path = directory / (split + "-predictions.json")
        if not prediction_path.exists():
            write_once(prediction_path, {"features": {k: v.tolist() for k, v in observed.items()},
                                         "predictions": {k: v.tolist() for k, v in predictions.items()},
                                         "sample_ids": [v["sample_id"] for v in data["metadata"]]})
        else:
            read(prediction_path)
        records["splits"][split] = family_scores
    records["file_hashes"] = {p.name: digest(p) for p in directory.glob("test*.json")}
    write_once(path, records)
    return records


def aggregate(config, evaluated):
    if (len(evaluated) != config["sampling"]["repeats"]
            or [row["repeat"] for row in evaluated] != config["sampling"]["repeat_indices"]):
        raise ValueError("All complete repetitions are required")
    deltas, base_deltas = [], []
    by_family = {name: [] for name in ("diagonal", "tiles")}
    for row in evaluated:
        scores = row["splits"]["test_unseen"]
        comparator = row["selected_comparator"]
        delta = []
        for family in by_family:
            value = scores[family][comparator] - scores[family]["GEOMETRY"]
            by_family[family].append(value)
            delta.append(value)
        deltas.append(float(np.mean(delta)))
        base_deltas.append(float(np.mean([scores[f]["BASE"] - scores[f]["GEOMETRY"] for f in by_family])))
    interval = repeat_bootstrap(deltas, config["evaluation"]["primary_ci"]["draws"],
                                config["sampling"]["bootstrap_seed"])
    mean = float(np.mean(deltas))
    family_means = {k: float(np.mean(v)) for k, v in by_family.items()}
    threshold = config["evaluation"]["practical_delta"]
    guard = all(v >= -config["evaluation"]["maximum_family_degradation"] for v in family_means.values())
    supported = mean >= threshold and interval[0] > 0 and np.mean(base_deltas) >= threshold and guard
    secondary = {}
    for split in ("test_known", "test_unseen"):
        secondary[split] = {}
        for reference in (*COMPARATORS, "SHUFFLED"):
            contrasts, relative = [], []
            family_losses = {f: {o: [] for o in (*OBSERVERS, "PERSISTENCE")}
                             for f in config["sampling"]["splits"][split]["counts"]}
            for row in evaluated:
                scores = row["splits"][split]
                for f, observers in family_losses.items():
                    for o in observers:
                        observers[o].append(scores[f][o])
                baseline = float(np.mean([v[reference] for v in scores.values()]))
                geometric = float(np.mean([v["GEOMETRY"] for v in scores.values()]))
                contrasts.append(baseline - geometric)
                relative.append(None if baseline == 0 else (baseline - geometric) / baseline)
            secondary[split][reference] = {
                "mean_delta": float(np.mean(contrasts)),
                "paired_repeat_deltas": contrasts,
                "descriptive_ci95": repeat_bootstrap(contrasts,
                    config["evaluation"]["primary_ci"]["draws"], config["sampling"]["bootstrap_seed"]),
                "relative_improvement_by_repeat": relative,
                "family_mean_mae": {f: {o: float(np.mean(v)) for o, v in obs.items()}
                                    for f, obs in family_losses.items()}}
    return {"paired_repeat_deltas": deltas, "mean_delta": mean, "primary_ci95": interval,
            "mean_BASE_delta": float(np.mean(base_deltas)), "family_mean_deltas": family_means,
            "support_all_conditions": bool(supported), "family_guard_passed": guard,
            "against_practical_advantage": interval[1] < threshold,
            "evidence_of_disadvantage": interval[1] < 0,
            "secondary_descriptive_only": secondary,
            "interpretation_scope": config["evaluation"]["interpretation"]}


def execute(args):
    global ACTIVE_BUDGET
    config = load_config()
    mode = "development" if args.stage == "development" else "confirmatory"
    if args.stage == "evaluate":
        reviews = verify_reviews(args.reviews, config)
        if not (args.output / "prepared.json").is_file():
            raise ValueError("All training fits must be frozen before evaluation")
        expected = signature(mode, args.code_commit)
        if read(args.output / "manifest.json") != expected:
            raise ValueError("Frozen run signature mismatch")
        prepared = read(args.output / "prepared.json")
        paths = {f"repeat-{r:02d}/frozen.json" for r in config["sampling"]["repeat_indices"]}
        if set(prepared["frozen_hashes"]) != paths:
            raise ValueError("Incomplete preparation")
        for relative, checksum in prepared["frozen_hashes"].items():
            if digest(args.output / relative) != checksum:
                raise ValueError("Preparation checksum mismatch")
            frozen = read(args.output / relative)
            for name, value in frozen["file_hashes"].items():
                if digest((args.output / relative).parent / name) != value:
                    raise ValueError("Frozen data or model changed")
        if (args.output / "reviews.json").exists():
            if not args.resume:
                raise FileExistsError("Evaluation already started; use explicit --resume")
            if read(args.output / "reviews.json") != reviews:
                raise ValueError("Review evidence changed after evaluation started")
    else:
        open_run(args.output, mode, args.code_commit, args.resume)
    budget = Budget(config["execution"], args.output)
    ACTIVE_BUDGET = budget
    stage_id = uuid.uuid4().hex
    start = time.monotonic()
    status = "incomplete"
    failure = None
    try:
        if args.stage == "evaluate" and not (args.output / "reviews.json").exists():
            write_once(args.output / "reviews.json", reviews)
        if args.stage in ("development", "prepare"):
            repeats = 1 if mode == "development" else config["sampling"]["repeats"]
            frozen = [prepare_repeat(config, args.output, repeat, mode == "development", budget)
                      for repeat in range(repeats)]
            final_name = "development.json" if mode == "development" else "prepared.json"
            summary = {"status": "development_only" if mode == "development" else "fits_frozen",
                       "test_states_generated": False,
                       "repeats": repeats, "validation": frozen,
                       "frozen_hashes": {f"repeat-{r:02d}/frozen.json": digest(
                           args.output / f"repeat-{r:02d}/frozen.json") for r in range(repeats)}}
        else:
            evaluated = [evaluate_repeat(config, args.output, repeat, budget)
                         for repeat in range(config["sampling"]["repeats"])]
            summary = aggregate(config, evaluated)
            summary.update(status="completed", test_states_generated=True)
            final_name = "results.json"
        budget.check()
        if not (args.output / final_name).exists():
            write_once(args.output / final_name, summary)
        elif read(args.output / final_name) != summary:
            raise ValueError("Completed summary disagrees with resumed checkpoints")
        status = "completed"
        print(json.dumps({"stage": args.stage, "status": status, "summary": str(args.output / final_name)}))
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        budget.close()
        ACTIVE_BUDGET = None
        budget.reserve(8192, log=True)
        write_once(args.output / ("batch-" + stage_id + ".json"), {
            "stage": args.stage, "status": status,
            "failure": failure,
            "active_seconds": time.monotonic() - start,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "size_bytes": sum(p.stat().st_size for p in args.output.rglob("*") if p.is_file()),
            "memory_enforcement": "RLIMIT_AS <= 4 GiB virtual address space (stricter than RSS)",
            "numerical_threads": 1, "worker_processes": 1})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["development", "prepare", "evaluate"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--code-commit", required=True,
                        help="Full SHA of the commit containing this runner and model")
    execute(parser.parse_args())
