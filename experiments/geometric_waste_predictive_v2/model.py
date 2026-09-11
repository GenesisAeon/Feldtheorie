"""Pure simulation, observation and fitting functions for GW-PRED-002."""

from __future__ import annotations

import hashlib
import math

import numpy as np


FAMILIES = ("iid", "smooth", "axial", "diagonal", "tiles")
DEVELOPMENT_FAMILIES = FAMILIES[:3]
OBSERVERS = ("BASE", "GEOMETRY", "MICRO", "COARSE", "SHUFFLED")
COMPARATORS = ("BASE", "MICRO", "COARSE", "PERSISTENCE")


def step(states):
    x = np.asarray(states, dtype=np.uint8)
    neighbours = np.zeros_like(x)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                neighbours += np.roll(x, (dr, dc), axis=(-2, -1))
    return ((neighbours == 3) | ((x == 1) & (neighbours == 2))).astype(np.uint8)


def block_fractions(states):
    x = np.asarray(states).reshape(-1, 16, 16)
    return x.reshape(-1, 4, 4, 4, 4).sum(axis=(2, 4)).reshape(-1, 16) / 16.0


def quadrant_boundaries(states):
    x = np.asarray(states).reshape(-1, 16, 16)
    quadrants = x.reshape(-1, 2, 8, 2, 8).transpose(0, 1, 3, 2, 4).reshape(-1, 4, 8, 8)
    horizontal = (quadrants[:, :, :, 1:] != quadrants[:, :, :, :-1]).sum(axis=(2, 3))
    vertical = (quadrants[:, :, 1:, :] != quadrants[:, :, :-1, :]).sum(axis=(2, 3))
    return horizontal + vertical


def features(states, shuffle_rng=None):
    x = np.asarray(states).reshape(-1, 16, 16)
    base = block_fractions(x)
    geometry = (4 * quadrant_boundaries(x) // 113) / 3.0
    micro = np.column_stack([
        np.minimum(x[:, r + 3:r + 5, c + 3:c + 5].sum(axis=(1, 2)), 3) / 3.0
        for r in (0, 8) for c in (0, 8)
    ])
    grid = base.reshape(-1, 4, 4)
    coarse = []
    for r in (0, 2):
        for c in (0, 2):
            p = grid[:, r:r + 2, c:c + 2]
            difference = (
                abs(p[:, 0, 0] - p[:, 0, 1]) + abs(p[:, 1, 0] - p[:, 1, 1])
                + abs(p[:, 0, 0] - p[:, 1, 0]) + abs(p[:, 0, 1] - p[:, 1, 1])
            ) / 4.0
            coarse.append(np.minimum(3, np.floor(4 * difference)) / 3.0)
    extras = {"BASE": np.zeros_like(geometry), "GEOMETRY": geometry,
              "MICRO": micro, "COARSE": np.column_stack(coarse)}
    if shuffle_rng is not None:
        extras["SHUFFLED"] = geometry[shuffle_rng.permutation(len(x))]
    return {name: np.column_stack((base, values)) for name, values in extras.items()}


def canonical_key(mask):
    """Exact lexicographic representative under D4 and torus translations.

    Big-endian row integers preserve lexicographic binary-cell ordering.
    All translations are compared; hashes are not used as the equality test.
    """
    x = np.asarray(mask, dtype=np.uint8)
    side = x.shape[0]
    if x.shape != (side, side) or not 1 <= side <= 16:
        raise ValueError("Expected square binary lattice of side 1..16")
    if not np.all((x == 0) | (x == 1)):
        raise ValueError("Expected binary cells")
    shifts = np.arange(side, dtype=np.uint32)
    row_indices = (np.arange(side)[:, None] + np.arange(side)[None, :]) % side
    weights = 1 << np.arange(side - 1, -1, -1, dtype=np.uint32)
    best = None
    for rotation in range(4):
        rotated = np.rot90(x, rotation)
        for oriented in (rotated, rotated[:, ::-1]):
            rows = oriented @ weights
            columns = ((rows[None, :] >> shifts[:, None])
                       | (rows[None, :] << (side - shifts[:, None]))) & ((1 << side) - 1)
            candidates = columns[:, row_indices].reshape(side * side, side).astype(">u2")
            raw = candidates.tobytes()
            stride = 2 * side
            value = min(raw[i:i + stride] for i in range(0, len(raw), stride))
            best = value if best is None else min(best, value)
    return best


def make_state(family, rng):
    if family not in FAMILIES:
        raise ValueError("Unknown family")
    r, c = np.indices((16, 16))
    parameters = {"family": family}
    if family == "iid":
        score = rng.uniform(size=(16, 16))
    elif family == "smooth":
        centres = rng.uniform(0, 16, size=(4, 2))
        amplitudes = rng.uniform(-1, 1, size=4)
        width = float(rng.choice([1.5, 2.5, 3.5]))
        score = np.zeros((16, 16), dtype=float)
        for (row, col), amplitude in zip(centres, amplitudes):
            dr = np.minimum(abs(r - row), 16 - abs(r - row))
            dc = np.minimum(abs(c - col), 16 - abs(c - col))
            score += amplitude * np.exp(-(dr * dr + dc * dc) / (2 * width * width))
        score += 0.25 * rng.standard_normal((16, 16))
        parameters.update(centres=centres.tolist(), amplitudes=amplitudes.tolist(), width=width)
    elif family in ("axial", "diagonal"):
        frequency = int(rng.choice([1, 2, 3, 4]))
        directions = [(1, 0), (0, 1)] if family == "axial" else [(1, 1), (1, -1)]
        direction = directions[int(rng.integers(2))]
        phase = float(rng.uniform(0, 2 * math.pi))
        a, b = direction
        score = np.cos(2 * math.pi * frequency * (a * r + b * c) / 16 + phase)
        score += 0.35 * rng.standard_normal((16, 16))
        parameters.update(frequency=frequency, direction=list(direction), phase=phase)
    else:
        width = int(rng.choice([2, 4, 8]))
        u, v = [int(value) for value in rng.integers(0, 16, size=2)]
        parity = (((r + u) % 16) // width + ((c + v) % 16) // width) % 2
        score = 1.0 - 2.0 * parity + 0.5 * rng.standard_normal((16, 16))
        parameters.update(width=width, offsets=[u, v])
    selected = np.lexsort((np.arange(256), -score.ravel()))[:128]
    mask = np.zeros(256, dtype=np.uint8)
    mask[selected] = 1
    rotation = int(rng.integers(4))
    reflection = bool(rng.integers(2))
    shifts = [int(value) for value in rng.integers(0, 16, size=2)]
    mask = np.rot90(mask.reshape(16, 16), rotation)
    if reflection:
        mask = mask[:, ::-1]
    mask = np.roll(mask, shifts, axis=(0, 1)).copy()
    parameters.update(rotation=rotation, reflection=reflection, shifts=shifts)
    return mask, parameters


def generate_split(config, repeat, split, registry, development=False, check=lambda: None):
    if development and repeat != 0:
        raise ValueError("The development stream is fixed to repeat zero")
    if development and split not in ("train", "validation"):
        raise ValueError("Development cannot generate any test split")
    sampling = config["sampling"]
    counts = sampling["splits"][split]["counts"]
    if development and not set(counts) <= set(DEVELOPMENT_FAMILIES):
        raise ValueError("Development cannot generate held-out families")
    seed = sampling["development_seed" if development else "master_seed"]
    split_id = sampling["splits"][split]["split_id"]
    states, metadata, keys = [], [], []
    rejections = {}
    for family in sampling["family_order"]:
        if family not in counts:
            continue
        family_id = config["generators"][family]["family_id"]
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
            [seed, repeat, split_id, family_id])))
        rejected = 0
        for index in range(counts[family]):
            for attempt in range(10001):
                check()
                if attempt == 10000:
                    raise RuntimeError("Duplicate rejection limit reached")
                rng_before = rng.bit_generator.state
                mask, record = make_state(family, rng)
                key = canonical_key(mask)
                if key in registry:
                    rejected += 1
                    continue
                registry.add(key)
                states.append(mask)
                keys.append(key.hex())
                record.update(sample_id=f"{repeat}:{split}:{family}:{index}",
                              repeat=repeat, split=split, index=index,
                              rng_state_before=rng_before,
                              canonical_sha256=hashlib.sha256(key).hexdigest())
                metadata.append(record)
                break
        rejections[family] = rejected
    return np.asarray(states, dtype=np.uint8), metadata, keys, rejections


def polynomial(x):
    if x.shape[1] != 20:
        raise ValueError("Expected 20 sensor values")
    i, j = np.triu_indices(20)
    return np.column_stack((x, x[:, i] * x[:, j]))


def predict(model, x):
    expanded = polynomial(x)
    normalized = (expanded - np.asarray(model["mean"])) / np.asarray(model["scale"])
    normalized[:, model["constant_columns"]] = 0.0
    return np.clip(normalized @ np.asarray(model["coefficients"]) + model["intercept"], 0, 1)


def mae(target, predicted):
    return float(np.mean(np.abs(target - predicted)))


def fit_ridge(train_x, train_y, validation_x, validation_y, lambdas):
    expanded = polynomial(train_x)
    mean = expanded.mean(axis=0)
    scale = expanded.std(axis=0, ddof=0)
    # Repeated fractions such as 1/3 can have a nonzero floating-point std.
    constant = np.flatnonzero(np.ptp(expanded, axis=0) == 0)
    scale[constant] = 1.0
    a = (expanded - mean) / scale
    a[:, constant] = 0.0
    target_mean = train_y.mean(axis=0)
    u, singular, vt = np.linalg.svd(a, full_matrices=False)
    rhs = u.T @ (train_y - target_mean)
    tolerance = singular.max() * max(a.shape) * np.finfo(a.dtype).eps
    rank = int(np.sum(singular > tolerance)) + 1
    candidates = []
    for regularization in lambdas:
        factor = singular / (singular * singular + len(a) * regularization)
        coefficients = vt.T @ (factor[:, None] * rhs)
        model = {"mean": mean.tolist(), "scale": scale.tolist(),
                 "constant_columns": constant.tolist(),
                 "coefficients": coefficients.tolist(), "intercept": target_mean.tolist(),
                 "lambda": regularization,
                 "design_rank": rank,
                 "effective_degrees_of_freedom": float(
                     1 + np.sum(singular * singular / (singular * singular + len(a) * regularization)))}
        score = mae(validation_y, predict(model, validation_x))
        candidates.append((score, -regularization, model))
    winner = min(candidates, key=lambda value: value[:2])
    winner[2]["validation_mae"] = winner[0]
    winner[2]["lambda_validation_mae"] = {str(-negative_lambda): score
                                         for score, negative_lambda, _ in candidates}
    return winner[2]


def choose_comparator(validation_maes):
    return min(COMPARATORS, key=lambda name: (validation_maes[name], COMPARATORS.index(name)))


def repeat_bootstrap(deltas, draws, seed):
    values = np.asarray(deltas, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Expected finite repeat-level paired differences")
    rng = np.random.Generator(np.random.PCG64(seed))
    means = values[rng.integers(0, len(values), size=(draws, len(values)))].mean(axis=1)
    return np.quantile(means, [0.025, 0.975], method="linear").tolist()
