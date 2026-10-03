"""M9b: draw the held-out combinations and FREEZE the closed-form predictions.

Runs before any kernel computation on these combinations and imports no
kernel (only predict.py and m9_registry.py). Writes, exclusively (never
overwrites):

    protocol/m9_frozen_predictions.json

containing the draw (seed, grid), the seen register (with the SHA-256 of
explore/protocol.jsonl at freeze time), the hashes of predict.py and of the
derivation, the decision rules of docs/M9_HERLEITUNG.md section 7 and, for
each of the 24 held-out combinations, the complete predicted band.

    python -m experiments.mandala_memory.m9_freeze [--out FILE] [--explore-protocol FILE]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

from experiments.mandala_memory import m9_registry as reg
from experiments.mandala_memory import predict

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "protocol" / "m9_frozen_predictions.json"
EXPLORE_PROTOCOL = Path(r"D:/mandala/mandala-memory-results/explore/protocol.jsonl")
SCHEMA = "mandala-memory-m9-frozen-v1"
RULES = {
    "p_star": 0.75,
    "primary": "for every held-out combination and every d in 0..64: kernel ||H dx(d)|| within "
               "s_lin(d) +- (H_norm2 * E(d) + tol), tol = 1e-12 * max(1, s_lin) + 1e-15; and kernel D in [D_lo, D_hi] "
               "(None counts as -1). A single violation falsifies the derivation or its implementation.",
    "secondary": {"decoder": "nearest mean, no standardisation, tie -> 0", "n_train_per_class": 1000,
                  "n_test_per_class": 4000, "mode": "m9", "delays": "D_linear and D_linear + 1 where 0 <= D_linear <= 63",
                  "band": "[lo(d) - 0.01 - 4 SE, hi(d) + 4 SE], SE = sqrt(p (1 - p) / 8000), p = (lo + hi) / 2",
                  "seeds": "one seed per combination: 9000 + index"},
    "informative": ["number of point predictions (D_lo == D_hi) and band widths",
                    "number of combinations where the naive q rule misses the kernel D",
                    "Z1 (not proven): full readout, different modules: kernel separation <= linear separation for all d"],
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _same(a: Dict, b: Dict) -> bool:
    ka = {**a, "c": None if a["M"] == 1 else a["c"]}
    kb = {**b, "c": None if b["M"] == 1 else b["c"]}
    return all(ka.get(k) == kb.get(k) for k in predict.COMBO_KEYS)


def seen_combinations(explore_protocol: Path) -> List[Dict]:
    seen = [dict(c) for c in reg.DEV_COMBOS]          # includes the benchmark and the pre-M8 scan
    if explore_protocol.is_file():
        for line in explore_protocol.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("kind") == "lab":
                k = e["knobs"]
                seen.append({key: k.get(key) for key in predict.COMBO_KEYS})
            # comparison runs (M6) use the benchmark knobs; the benchmark is already in the register
    return seen


def check_unseen(held: List[Dict], seen: List[Dict]) -> Dict:
    seen_values = {k: {s[k] for s in seen if s.get(k) is not None} for k in reg.CONTINUOUS}
    for k in reg.CONTINUOUS:
        overlap = set(reg.HELD_OUT_GRID[k]) & seen_values[k]
        if overlap:
            raise RuntimeError(f"held-out grid value(s) {sorted(overlap)} for {k} were already seen")
    for h in held:
        for s in seen:
            if _same(h, s):
                raise RuntimeError(f"held-out combination equals a seen one: {h}")
            differing = [k for k in reg.CONTINUOUS if h[k] != s.get(k) and not (k == "c" and h["M"] == 1)]
            if not differing:
                raise RuntimeError(f"held-out combination does not differ from a seen one in any continuous knob: {h}")
    return {"n_seen": len(seen), "seen_continuous_values": {k: sorted(v) for k, v in seen_values.items()}}


def draw_held_out() -> List[Dict]:
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(reg.DRAW_SEED)))
    G = reg.HELD_OUT_GRID
    held, keys = [], set()
    for readout in reg.HELD_OUT_READOUTS:
        k = 0
        while k < reg.HELD_OUT_PER_READOUT:
            N = int(rng.choice(G["N"]))
            Ms = [m for m in range(1, N // 2 + 1) if N % m == 0]
            M = int(rng.choice(Ms))
            n = N // M
            want_same = (k % 3 == 2) or M == 1
            mi = int(rng.integers(0, M))
            i = mi * n + int(rng.integers(0, n))
            if want_same:
                j = mi * n + int(rng.choice([t for t in range(n) if mi * n + t != i]))
            else:
                mj = int(rng.choice([m for m in range(M) if m != mi]))
                j = mj * n + int(rng.integers(0, n))
            node_choice = [i, j, int(rng.integers(0, N))][int(rng.integers(0, 3))]
            combo = {"N": N, "M": M, "c": None if M == 1 else float(rng.choice(G["c"])),
                     "gamma": float(rng.choice(G["gamma"])), "ell": float(rng.choice(G["ell"])),
                     "amplitude": float(rng.choice(G["amplitude"])), "sigma": float(rng.choice(G["sigma"])),
                     "inputs": [i, j], "readout": readout, "readout_node": node_choice if readout == "node" else 0,
                     "nonlinearity": "tanh"}
            key = json.dumps(combo, sort_keys=True)
            if key in keys:
                continue
            predict.check_family(combo)
            keys.add(key)
            held.append(combo)
            k += 1
    return held


def git_head() -> str:
    r = subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def build(explore_protocol: Path = EXPLORE_PROTOCOL) -> Dict:
    held = draw_held_out()
    seen = seen_combinations(explore_protocol)
    seen_info = check_unseen(held, seen)
    items = []
    for idx, h in enumerate(held):
        pr = predict.predict(h, RULES["p_star"])
        items.append({"id": f"h{idx:02d}", "index": idx, "prediction": pr})
    return {
        "schema": SCHEMA, "created_unix": time.time(), "git_head_at_freeze": git_head(),
        "predict_py_sha256": sha256_file(HERE / "predict.py"),
        "derivation_sha256": sha256_file(HERE / "docs" / "M9_HERLEITUNG.md"),
        "registry_sha256": sha256_file(HERE / "m9_registry.py"),
        "draw": {"seed": reg.DRAW_SEED, "grid": reg.HELD_OUT_GRID, "per_readout": reg.HELD_OUT_PER_READOUT,
                 "readouts": list(reg.HELD_OUT_READOUTS)},
        "seen_register": {**seen_info, "explore_protocol": str(explore_protocol),
                          "explore_protocol_sha256": sha256_file(explore_protocol) if explore_protocol.is_file() else None},
        "rules": RULES, "kernel_evaluated_before_freeze": False, "held_out": items,
    }


def write_exclusive(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=FROZEN)
    ap.add_argument("--explore-protocol", type=Path, default=EXPLORE_PROTOCOL)
    a = ap.parse_args(argv)
    frozen = build(a.explore_protocol)
    text = json.dumps(frozen, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    write_exclusive(a.out, text)
    print(json.dumps({"written": str(a.out), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                      "n_held_out": len(frozen["held_out"]), "n_seen": frozen["seen_register"]["n_seen"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
