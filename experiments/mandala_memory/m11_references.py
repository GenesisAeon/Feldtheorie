"""M11 model-based reference phase (plan Fassung 2, sections 2.2/2.3 and 5).

For each case: the M10 Bayes value (file + SHA + SE), the population accuracies of the
learning criteria NM(inf), LDA(inf), and the numerical linear reference L_found with
all optimiser starts. Order (M11-R4): procedures and decisions are VERSIONED first; the
research references are then computed ONCE and frozen. This module refuses the research
case set unless the M11 files are committed and unchanged (git), and it never
overwrites an existing reference artifact.

    python -m experiments.mandala_memory.m11_references --cases dev --out D:/mandala/mandala-memory-results/m11/dev/references-dev.json
    python -m experiments.mandala_memory.m11_references --cases research     # writes protocol/m11_references.json (reference phase)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict

import numpy as np

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory.core import MemoryLabError, is_drive_c

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol" / "m11_protokoll.json"
RESEARCH_REFERENCES = HERE / "protocol" / "m11_references.json"
VERSIONED = ("m11_readout.py", "m11_references.py", "m11_run.py", "m11_evaluate.py", "protocol/m11_protokoll.json")


def load_protocol() -> Dict:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def case_states(case: Dict, m10proto: Dict, conditions: Dict, pats, delay: int) -> np.ndarray:
    """States from the FROZEN M10 functions (the Mandala is not changed)."""
    cond = None if case["condition"] == "K0" else conditions[case["condition"]]
    return mt.readout_states(mt.network(m10proto, case["network"], "tanh", cond), delay, pats)


def bayes_reference(case: Dict, source: Dict) -> Dict:
    f = Path(source["file"])
    if sha(f) != source["sha256"] and hashlib.sha256(f.read_bytes()).hexdigest() != source["sha256"]:
        raise MemoryLabError(f"Bayes source {f.name} does not match its recorded SHA-256")
    res = json.loads(f.read_text(encoding="utf-8"))
    row = next(r for r in res["level_B"] if r["network"] == case["network"] and r["nonlinearity"] == "tanh"
               and r["condition"] == case["condition"] and r["delay"] == source["delay"])
    return {"B": row["preserve"]["estimate"], "B_se": row["preserve"]["se"], "n_mc": row["preserve"]["n"],
            "file": str(f), "sha256": source["sha256"]}


def git_clean(paths) -> bool:
    out = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", *paths], capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() == ""


def compute(case_set: str) -> Dict:
    proto = load_protocol()
    m10proto = mt.load_protocol()
    pats = mt.patterns()
    probs = np.array([float(p) for _, p in pats])
    sigma, d = m10proto["observation"]["sigma"], proto["delay"]
    if case_set == "research":
        cases, conditions, source = proto["cases"], m10proto["conditions"], proto["bayes_source"]["research"]
    elif case_set == "dev":
        cases, conditions, source = proto["development"]["cases"], m10proto["development"]["conditions"], proto["bayes_source"]["dev"]
    else:
        raise MemoryLabError("case set must be dev or research")
    lr = proto["linear_reference"]
    out = {"schema": "mandala-memory-m11-references-v1", "case_set": case_set, "created_unix": time.time(),
           "protocol_sha256": sha(PROTOCOL), "code_sha256": {f: sha(HERE / f) for f in VERSIONED if f.endswith(".py")},
           "git_head": subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "cases": {}}
    for case in cases:
        z = case_states(case, m10proto, conditions, pats, d)
        rules = mr.population_rules(z, probs, sigma)
        rng = mr.stream(proto["modes"][case_set], lr["seed"], "linref", case["name"])[0]
        ref = mr.linear_reference(z, probs, sigma, rng, n_random=lr["n_random"], gtol=lr["gtol"], maxiter=lr["maxiter"])
        out["cases"][case["name"]] = {
            **bayes_reference(case, source),
            "acc_nm_inf": mr.exact_accuracy(*rules["nm"], z, probs, sigma),
            "acc_lda_inf": mr.exact_accuracy(*rules["lda"], z, probs, sigma),
            "L_found": ref["L_found"], "linear_reference": ref,
            "rules": {k: {"w": v[0].tolist(), "b": v[1]} for k, v in rules.items()}}
    return out


def write_exclusive(path: Path, payload: Dict) -> None:
    if is_drive_c(path):
        raise MemoryLabError("refusing to write on C:")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, indent=1, ensure_ascii=False, allow_nan=False) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", choices=("dev", "research"), required=True)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    if a.cases == "research":
        if a.out is not None:
            raise SystemExit("research references are always written to protocol/m11_references.json")
        if not git_clean(VERSIONED):
            raise SystemExit("reference phase refused: M11 procedures/protocol are not committed (M11-R4)")
        out = RESEARCH_REFERENCES
    else:
        if a.out is None:
            raise SystemExit("--out is required for dev references")
        out = a.out
    payload = compute(a.cases)
    write_exclusive(out, payload)
    print(json.dumps({"written": str(out), "cases": {k: {x: v[x] for x in ("B", "acc_nm_inf", "acc_lda_inf", "L_found")}
                                                     for k, v in payload["cases"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
