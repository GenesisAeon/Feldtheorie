"""LR2 development reference data (plan section 10, integration proofs 1 and 2). Written exclusively.

- kernel_cases.npz       100 deterministic development states (sizes 2..34, Lantern C at g and 5g,
                         zero matrices, random dense/sparse/uniform matrices), 500 Euler steps of dt=0.02;
- kernel_original.npz    the ORIGINAL PhaseEvolver.evolve_phases on these cases (separate legacy process);
- ode_cases.npz          32 synthetic cases (sizes up to 34) with a high-accuracy solve_ivp reference
                         (DOP853, rtol 1e-11, atol 1e-12) at t = 0, 0.5, 1, 2, 3, 5, 10;
- manifest.json          generator stream, settings and SHA-256 of every file.

All randomness from an own named development stream (never the global RNG):
SeedSequence([2026100802, 120, case_index]) for the kernel cases, [2026100802, 220, case_index] for the ODE cases.

    python experiments/lantern_reconstruction/tools/lr2_make_reference.py --out experiments/lantern_reconstruction/artifacts/lr2_reference
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.lantern_reconstruction import dynamics as dyn  # noqa: E402
from experiments.lantern_reconstruction import legacy_probe, registry_adapter  # noqa: E402
from experiments.lantern_reconstruction.linear_diagnostics import pair_write_matrix  # noqa: E402

MASTER = 2026100802
TIMES = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
DT = 0.02
KERNEL_STEPS = 500
KERNEL_RECORD = [1, 250, 500]


def rng(role: int, k: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([MASTER, role, k])))


def random_coupling(r, n, kind):
    if kind == "zero":
        return np.zeros((n, n))
    if kind == "uniform":
        C = np.ones((n, n))
    else:
        C = r.uniform(0.0, 1.0, size=(n, n))
        if kind == "sparse":
            C *= r.uniform(size=(n, n)) < 0.3
    C = np.triu(C, 1)
    return C + C.T


def kernel_cases(C_lantern, g_lantern):
    plan = ([("lantern", 34, g_lantern)] * 10 + [("lantern", 34, 5 * g_lantern)] * 10 + [("zero", 34, 1.0)] * 10 +
            [("zero", 5, 1.0)] * 10 + [("dense", n, s) for n in (2, 3, 5, 8, 12) for s in (0.1, 1.0, 5.0, 0.5)] +
            [("dense", 34, s) for s in (0.03, 0.3)] * 10 + [("uniform", n, 0.5) for n in (4, 6, 8, 10, 12)] * 2 +
            [("sparse", 20, s) for s in (0.2, 1.0)] * 5)
    assert len(plan) == 100, len(plan)
    out = {"n_cases": np.array(len(plan))}
    for k, (kind, n, g) in enumerate(plan):
        r = rng(120, k)
        C = C_lantern if kind == "lantern" else random_coupling(r, n, kind)
        omega = r.normal(0.0, 0.1, n)
        omega -= omega.mean()
        out.update({f"theta_{k}": r.uniform(-np.pi, np.pi, n), f"C_{k}": np.ascontiguousarray(C), f"omega_{k}": omega,
                    f"g_{k}": np.array(float(g)), f"dt_{k}": np.array(DT), f"record_{k}": np.array(KERNEL_RECORD)})
    return out, [f"{kind}:{n}:g={g:.6g}" for kind, n, g in plan]


def ode_cases(C_lantern, g_lantern):
    plan = ([("lantern", 34, g_lantern, "study")] * 6 + [("lantern", 34, 5 * g_lantern, "study")] * 4 +
            [("dense", n, 0.5, "random") for n in (2, 4, 8, 16)] + [("dense", 34, 0.03, "study")] * 4 +
            [("sparse", 16, 1.0, "random")] * 4 + [("uniform", 8, 0.3, "study")] * 4 + [("zero", 34, 1.0, "study")] * 2 +
            [("dense", 2, 2.0, "random")] * 4)
    assert len(plan) == 32, len(plan)
    out = {"n_cases": np.array(len(plan)), "times": np.array(TIMES)}
    for k, (kind, n, g, init) in enumerate(plan):
        r = rng(220, k)
        C = C_lantern if kind == "lantern" else random_coupling(r, n, kind)
        omega = r.normal(0.0, 0.1, n)
        omega -= omega.mean()
        if init == "study" and n >= 8:                     # theta(0) = phi 1 + a E u, four disjoint pairs, a = 0.35
            pairs = r.permutation(n)[:8].reshape(4, 2)
            theta0 = r.uniform(-np.pi, np.pi) + 0.35 * pair_write_matrix(n, pairs) @ r.uniform(-1, 1, 4)
        else:
            theta0 = r.uniform(-np.pi, np.pi, n)
        sol = solve_ivp(dyn.ode_rhs(C, omega, g), (0.0, TIMES[-1]), theta0, method="DOP853", t_eval=TIMES, rtol=1e-11, atol=1e-12)
        if not sol.success:
            raise RuntimeError(f"solve_ivp failed for case {k}")
        out.update({f"theta_{k}": theta0, f"C_{k}": np.ascontiguousarray(C), f"omega_{k}": omega, f"g_{k}": np.array(float(g)),
                    f"reference_{k}": dyn.wrap(sol.y.T)})
    return out, [f"{kind}:{n}:g={g:.6g}:{init}" for kind, n, g, init in plan]


def write_npz(path: Path, arrays: dict) -> str:
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(buf.getvalue())
    return hashlib.sha256(buf.getvalue()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True, help="directory on D: for the legacy process output")
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"{a.out} exists already (never overwritten)")
    snap = registry_adapter.load_verified_snapshot()
    C, g = np.array(snap.C), float(snap.structure["g"])
    t0 = time.perf_counter()
    kc, kdesc = kernel_cases(C, g)
    oc, odesc = ode_cases(C, g)
    a.out.mkdir(parents=True)
    hashes = {"kernel_cases.npz": write_npz(a.out / "kernel_cases.npz", kc), "ode_cases.npz": write_npz(a.out / "ode_cases.npz", oc)}
    t1 = time.perf_counter()
    raw = legacy_probe.run_original_kernel(registry_adapter.REPO, a.out / "kernel_cases.npz", a.scratch / "kernel_original.npz")
    t2 = time.perf_counter()
    orig_bytes = raw.read_bytes()
    fd = os.open(str(a.out / "kernel_original.npz"), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(orig_bytes)
    hashes["kernel_original.npz"] = hashlib.sha256(orig_bytes).hexdigest()
    run_meta = json.loads(Path(str(raw) + ".json").read_text(encoding="utf-8"))
    manifest = {"schema": "lantern-lr2-reference-v1", "generator": "tools/lr2_make_reference.py", "master_seed": MASTER,
                "streams": {"kernel_cases": "SeedSequence([master, 120, k])", "ode_cases": "SeedSequence([master, 220, k])"},
                "snapshot_canonical_sha256": snap.canonical_sha256, "dt": DT, "kernel_steps": KERNEL_STEPS, "kernel_record_steps": KERNEL_RECORD,
                "ode_times": TIMES, "ode_reference": {"method": "DOP853", "rtol": 1e-11, "atol": 1e-12},
                "kernel_case_kinds": kdesc, "ode_case_kinds": odesc, "original_kernel_run": run_meta, "file_sha256": hashes,
                "timing_s": {"cases_and_ode_reference": t1 - t0, "original_kernel_process": t2 - t1}}
    fd = os.open(str(a.out / "manifest.json"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({k: manifest[k] for k in ("file_sha256", "timing_s")} | {"rng": run_meta["global_rng_consumed_in_every_case"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
