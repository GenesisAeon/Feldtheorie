"""M12 references per test condition (plan Fassung 2, section 5) and the protocol freeze check.

For each of the 9 conditions c: the Bayes accuracy B(c) of the class-conditional pattern
mixtures (FROZEN m10_bayes estimator, own independent stream per condition; B(c0) is
estimated exactly once) and the bedingungsspezifische population LDA LDA_pop(c) with its
exact accuracy. Diagnostic D1 source: the frozen M10 value of the base condition.

Order (plan section 7): protocol freeze BEFORE the reference phase; the research
references are computed ONCE (exclusive claim, failure record, never overwritten) and
get their own hash, which is bound in the model freeze and in the evaluation gate.

    python -m experiments.mandala_memory.m12_references --cases dev --out D:/mandala/mandala-memory-results/m12/dev/references-dev.json
    python -m experiments.mandala_memory.m12_references --cases research     # reference phase -> protocol/m12_references.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np

from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m12_common as mc
from experiments.mandala_memory.core import MemoryLabError

FROZEN_PROTOCOL_SHA256: Optional[str] = None            # set in the M12 protocol freeze commit
FREEZE_RECORD = mc.HERE / "protocol" / "m12_freeze.json"
RESEARCH_REFERENCES = mc.HERE / "protocol" / "m12_references.json"
RESEARCH_CLAIM = mc.HERE / "protocol" / "m12_references.claim.json"
RESEARCH_FAILURE = mc.HERE / "protocol" / "m12_references.failed.json"
VERSIONED = tuple(f for f in mc.CODE_FILES if f.startswith("m12_")) + ("protocol/m12_protokoll.json",)
SCHEMA = "mandala-memory-m12-references-v1"
clock: Callable[[], float] = time.monotonic


class RunTimeout(MemoryLabError):
    pass


def git_head() -> str:
    return subprocess.run(["git", "-C", str(mc.HERE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def git_clean(paths) -> bool:
    out = subprocess.run(["git", "-C", str(mc.HERE), "status", "--porcelain", "--", *paths], capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() == ""


def require_protocol_frozen(what: str) -> Dict:
    """Protocol constant + protocol file + freeze record (reviewed commit, code hashes)."""
    if FROZEN_PROTOCOL_SHA256 is None:
        raise MemoryLabError(f"{what} blocked: the M12 protocol is not frozen yet")
    if mc.sha(mc.PROTOCOL) != FROZEN_PROTOCOL_SHA256:
        raise MemoryLabError(f"{what} blocked: protocol differs from the frozen protocol")
    if not FREEZE_RECORD.is_file():
        raise MemoryLabError(f"{what} blocked: freeze record missing")
    rec = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    if rec.get("protocol_sha256") != FROZEN_PROTOCOL_SHA256 or not rec.get("reviewed_code_commit"):
        raise MemoryLabError(f"{what} blocked: freeze record does not match the protocol")
    if rec.get("code_sha256") != mc.code_sha256():
        raise MemoryLabError(f"{what} blocked: code differs from the frozen code")
    return rec


def d1_source(case_set: str) -> Dict:
    """Frozen M10 Bayes value of the base condition (SHA-checked via the M11 bayes_source)."""
    from experiments.mandala_memory import m11_references as mref

    proto = mc.load_protocol()
    key = "research" if case_set in ("research", "smoke") else "dev"
    src = json.loads(mc.M11_PROTOCOL.read_text(encoding="utf-8"))["bayes_source"][key]
    base = mc.base_of(proto, case_set)
    return mref.bayes_reference({"network": proto["mandala"]["network"], "condition": base["m10_condition"]}, src)


def compute(case_set: str, *, n_mc: Optional[int] = None, time_limit_s: Optional[float] = None, _claimed: bool = False) -> Dict:
    if case_set == "research" and not _claimed:
        raise MemoryLabError("research references only via research_reference_phase() (frozen protocol, claim)")
    if case_set not in ("research", "dev"):
        raise MemoryLabError("case set must be dev or research")
    if case_set == "research" and (n_mc is not None or time_limit_s is not None):
        raise MemoryLabError("no overrides for the research references")
    binding = mc.require_predecessors_frozen()              # M10/M11 frozen, before any state
    proto = mc.load_protocol()
    ref = proto["references"]["bayes"]
    n = n_mc or ref["n_mc"]
    limit = time_limit_s if time_limit_s is not None else proto["resources"]["time_limits_s"]["references"]
    start = clock()

    def deadline():
        if clock() - start > limit:
            raise RunTimeout(f"time limit of {limit} s exceeded")

    t0 = time.perf_counter()
    pats = mt.patterns()
    probs = mc.probabilities(pats)
    conds = mc.conditions(proto, case_set)
    zs: Dict[float, np.ndarray] = {}
    out = {"schema": SCHEMA, "case_set": case_set, "created_unix": time.time(), "protocol_sha256": mc.sha(mc.PROTOCOL),
           "code_sha256": mc.code_sha256(), "git_head": git_head(), "binding": binding, "n_mc": n, "block": ref["block"],
           "conditions": {}}
    for c in conds:
        deadline()
        a = round(c["amplitude"], 10)
        if a not in zs:
            zs[a] = mc.states(proto, case_set, c["amplitude"], pats)
        z = zs[a]
        rng, key = mc.stream("m12bayes", ref["base_seed"][case_set], case_set, c["name"])
        B = mb.bayes_accuracy_mc(mb.preserve_mixtures(z, pats), c["sigma"], n, rng, block=ref["block"], deadline=deadline)
        w, b = mr.population_rules(z, probs, c["sigma"])["lda"]
        out["conditions"][c["name"]] = {"amplitude": c["amplitude"], "sigma": c["sigma"], "B": B["estimate"], "B_se": B["se"],
                                        "n_mc": B["n"], "stream": list(key),
                                        "lda_pop": {"w": w.tolist(), "b": float(b),
                                                    "acc": mr.exact_accuracy(w, b, z, probs, c["sigma"])}}
    out["d1_source"] = d1_source(case_set)
    deadline()
    out["timing_s"] = time.perf_counter() - t0
    return out


def research_reference_phase() -> Dict:
    """One-time reference phase: preconditions BEFORE any computation (no artifact, claim
    or failure record; M12 files committed; protocol frozen), then an exclusive claim."""
    if RESEARCH_REFERENCES.exists():
        raise MemoryLabError("reference phase already completed: artifact exists")
    if RESEARCH_CLAIM.exists() or RESEARCH_FAILURE.exists():
        raise MemoryLabError("reference phase already started or failed: claim/failure record exists (no silent retry)")
    if not git_clean(VERSIONED):
        raise MemoryLabError("reference phase refused: M12 code/protocol are not committed")
    require_protocol_frozen("reference phase")
    mc.write_json_exclusive(RESEARCH_CLAIM, {"started_unix": time.time(), "git_head": git_head(), "protocol_sha256": mc.sha(mc.PROTOCOL)})
    try:
        payload = compute("research", _claimed=True)
    except Exception as e:
        mc.write_json_exclusive(RESEARCH_FAILURE, {"failed_unix": time.time(), "error": f"{type(e).__name__}: {e}"})
        raise
    mc.write_json_exclusive(RESEARCH_REFERENCES, payload)
    return payload


def require_references(case_set: str, path: Optional[Path] = None) -> Dict:
    """Research/smoke: the committed reference artifact computed against the frozen protocol."""
    if case_set in ("research", "smoke"):
        rec = require_protocol_frozen(f"{case_set} references")
        path = RESEARCH_REFERENCES
        refs = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if refs is None:
            raise MemoryLabError("reference artifact missing (reference phase not done)")
        if refs.get("protocol_sha256") != rec["protocol_sha256"] or refs.get("case_set") != "research":
            raise MemoryLabError("reference artifact was not computed against the frozen protocol")
        return {"refs": refs, "sha256": mc.sha(path)}
    if path is None:
        raise MemoryLabError("dev references need an explicit file")
    refs = json.loads(Path(path).read_text(encoding="utf-8"))
    if refs.get("case_set") != "dev":
        raise MemoryLabError("dev mode needs dev references")
    return {"refs": refs, "sha256": mc.sha(path)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", choices=("dev", "research"), required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--n-mc", type=int, help="dev only")
    a = ap.parse_args(argv)
    try:
        if a.cases == "research":
            if a.out is not None or a.n_mc is not None:
                raise SystemExit("research references: no --out/--n-mc (written to protocol/m12_references.json)")
            payload, out = research_reference_phase(), RESEARCH_REFERENCES
        else:
            if a.out is None:
                raise SystemExit("--out is required for dev references")
            payload, out = compute("dev", n_mc=a.n_mc), a.out
            mc.write_json_exclusive(out, payload)
    except MemoryLabError as e:
        raise SystemExit(str(e))
    print(json.dumps({"written": str(out), "timing_s": round(payload["timing_s"], 1),
                      "conditions": {k: {"B": round(v["B"], 4), "B_se": v["B_se"], "lda_pop": round(v["lda_pop"]["acc"], 4)}
                                     for k, v in payload["conditions"].items()},
                      "d1_source": {k: payload["d1_source"][k] for k in ("B", "B_se")}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
