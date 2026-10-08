"""LR1 legacy probe: the FULL original loader, once, in a separate process (plan sections 11/12, LR1).

Worker (`python -s legacy_probe.py --repo R --config C --out-dir D`):
- installs a sys.addaudithook BEFORE any project import and records the OBSERVED events per
  phase (imports, file opens incl. write modes, network/subprocess/ctypes events). This is an
  observation log, NOT a sandbox: nothing is blocked, no isolation is claimed or enforced;
- records the global NumPy RNG state before the import, after the import and after the
  construction (the original loader reseeds the global RNG via Python hash() of strings);
- builds `LanternNetwork(config)` with the unchanged original code and exports, in YAML
  insertion order, the IDs, the coupling matrix and the per-node parameters (theta is
  exported as `theta_threshold`, never as a phase);
- lists every loaded module with its file and the raw SHA-256 of files inside the repo;
- writes probe_raw.json + probe_raw.npz exclusively.

Parent (`run_probe`): starts the worker with a fixed PYTHONHASHSEED, PYTHONDONTWRITEBYTECODE=1,
no PYTHONPATH, no user site (-s), TMP/TEMP and the working directory on D:, and a timeout.
The research path later loads only the verified snapshot (registry_adapter) -- never this module.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

WORKER_SCHEMA = "lantern-legacy-probe-v1"
NODE_KEYS = ("beta", "theta_threshold", "frequency_hz", "impedance_z", "kappa_photonic", "kappa_em", "kappa_metabolic", "wavelength_cm")
WATCHED = ("open", "os.remove", "os.rename", "os.replace", "os.mkdir", "os.rmdir", "os.chmod", "shutil.copyfile", "shutil.rmtree",
           "socket.connect", "socket.bind", "socket.getaddrinfo", "urllib.Request", "http.client.connect", "subprocess.Popen",
           "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.startfile", "ctypes.dlopen", "import", "compile", "exec")
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


def _worker(repo: str, config: str, out_dir: str) -> int:
    import hashlib
    import json

    events: Dict[str, dict] = {}
    phase = ["pre"]

    def hook(name, args):
        if name not in WATCHED:
            return
        ph = events.setdefault(phase[0], {"counts": {}, "writes": [], "network_or_process": [], "imports": 0})
        ph["counts"][name] = ph["counts"].get(name, 0) + 1
        if name == "import":
            ph["imports"] += 1
        elif name == "open" and len(args) >= 3:
            path, mode, flags = args[0], args[1], args[2]
            is_write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (isinstance(flags, int) and flags & WRITE_FLAGS)
            if is_write:
                ph["writes"].append({"path": str(path), "mode": str(mode)})
        elif name.startswith(("socket", "urllib", "http", "subprocess", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.startfile")):
            import traceback
            frames = [f"{Path(fr.filename).parent.name}/{Path(fr.filename).name}:{fr.lineno} {fr.name}" for fr in traceback.extract_stack()[:-1]][-14:]
            ph["network_or_process"].append({"event": name, "args": [str(a)[:200] for a in args], "caller_frames": frames})

    sys.addaudithook(hook)
    import numpy as np                                            # noqa: E402  (after the hook on purpose)

    def rng_digest():
        st = np.random.get_state()
        return hashlib.sha256(st[1].tobytes() + str(st[2:]).encode()).hexdigest()

    rng = {"before_import": rng_digest()}
    phase[0] = "import"
    sys.path.insert(0, repo)
    from v9_alpha.api.lantern_bridge import LanternNetwork       # noqa: E402
    rng["after_import"] = rng_digest()
    phase[0] = "construct"
    net = LanternNetwork(config)
    rng["after_construct"] = rng_digest()
    phase[0] = "extract"
    ids = list(net.lanterns)
    nodes = list(net.lanterns.values())
    C = np.array(net.coupling_matrix, dtype=np.float64, copy=True)
    arrays = {"C_yaml_order": C}
    for k in NODE_KEYS:
        if k == "theta_threshold":
            arrays[k] = np.array([float(n.theta) for n in nodes], dtype=np.float64)
        elif k == "beta":
            arrays[k] = np.array([float(n.beta) for n in nodes], dtype=np.float64)
        else:
            arrays[k] = np.array([float(getattr(n.em_properties, k)) for n in nodes], dtype=np.float64)
    meta = {"name": [n.name for n in nodes], "type": [n.type for n in nodes], "domain": [n.domain for n in nodes],
            "status": [n.status for n in nodes], "readiness": [str(n.readiness) for n in nodes],
            "coupling_targets_loaded": [len(n.coupling_targets) for n in nodes]}
    repo_p = Path(repo).resolve()
    modules = []
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            modules.append({"module": name, "file": None, "inside_repo": False, "origin": "builtin_or_namespace"})
            continue
        p = Path(f).resolve()
        inside = repo_p in p.parents
        row = {"module": name, "file": p.relative_to(repo_p).as_posix() if inside else str(p), "inside_repo": inside}
        if p.is_file():
            row["raw_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
        modules.append(row)
    import importlib.metadata as md
    dist_of = md.packages_distributions()
    versions = {}
    for top in sorted({m["module"].split(".")[0] for m in modules if not m["inside_repo"]}):
        for dist in dist_of.get(top, []):
            try:
                versions[dist] = md.version(dist)
            except md.PackageNotFoundError:
                pass
    phase[0] = "export"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    import io
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    fd = os.open(str(out / "probe_raw.npz"), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(buf.getvalue())
    payload = {
        "schema": WORKER_SCHEMA, "python": sys.version.split()[0], "numpy": np.__version__,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"), "dont_write_bytecode": bool(sys.dont_write_bytecode),
        "no_user_site": bool(sys.flags.no_user_site), "cwd": os.getcwd(), "config": str(Path(config).resolve()),
        "ids_yaml_order": ids, "node_meta_yaml_order": meta, "array_keys": sorted(arrays),
        "global_rng": {**rng, "consumed_by_import": rng["after_import"] != rng["before_import"],
                       "consumed_by_construct": rng["after_construct"] != rng["after_import"]},
        "audit": {"kind": "observation (sys.addaudithook); nothing blocked, no isolation enforced or claimed",
                  "phases": {k: v for k, v in events.items() if k != "export"}},
        "modules": {"count": len(modules), "all": modules, "inside_repo": [m for m in modules if m["inside_repo"]],
                    "distribution_versions": versions, "python_executable": sys.executable,
                    "note": "complete module list at the end of the extraction: module, origin file and raw SHA-256 of every file-backed module"},
    }
    fd = os.open(str(out / "probe_raw.json"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    return 0


def _kernel_worker(repo: str, cases: str, out: str) -> int:
    """Run the ORIGINAL PhaseEvolver.evolve_phases (full import, noise_level=0) on stored cases.
    Records the states after the steps listed per case; the global RNG is consumed by the original
    even at zero noise -- this is reported, the research core never uses it."""
    import hashlib
    import io
    import json

    import numpy as np

    sys.path.insert(0, repo)
    src = Path(repo) / "v9_alpha" / "models" / "phase_dynamics.py"
    try:                                                   # regular package import first (records the outcome)
        from v9_alpha.models.phase_dynamics import PhaseEvolver
        load_mode, package_import_error = "package import v9_alpha.models.phase_dynamics", None
    except ImportError as e:                               # e.g. the package __init__ needs pandas
        import importlib.util
        package_import_error = f"{type(e).__name__}: {e}"
        spec = importlib.util.spec_from_file_location("lantern_original_phase_dynamics", src)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)                       # the UNCHANGED original file, executed completely
        PhaseEvolver = mod.PhaseEvolver
        load_mode = "original file executed by path (package __init__ bypassed after the failed package import)"

    with np.load(cases, allow_pickle=False) as f:
        data = {k: np.array(f[k]) for k in f.files}
    n_cases = int(data["n_cases"])
    results, rng_moved = {}, []
    for k in range(n_cases):
        theta, C, omega = data[f"theta_{k}"], data[f"C_{k}"], data[f"omega_{k}"]
        g, dt, steps = float(data[f"g_{k}"]), float(data[f"dt_{k}"]), [int(s) for s in data[f"record_{k}"]]
        ev = PhaseEvolver(dt=dt, noise_level=0.0, coupling_strength_scale=g)
        before = np.random.get_state()[1].copy()
        x, rec = theta.copy(), []
        for step in range(1, max(steps) + 1):
            x = ev.evolve_phases(x, C, omega)
            if step in steps:
                rec.append(x.copy())
        rng_moved.append(not np.array_equal(before, np.random.get_state()[1]))
        results[f"states_{k}"] = np.stack(rec)
    buf = io.BytesIO()
    np.savez(buf, **results)
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(buf.getvalue())
    meta = {"schema": "lantern-original-kernel-run-v1", "python": sys.version.split()[0], "numpy": np.__version__,
            "pythonhashseed": os.environ.get("PYTHONHASHSEED"), "n_cases": n_cases,
            "kernel": "PhaseEvolver.evolve_phases from v9_alpha/models/phase_dynamics.py (noise_level=0.0)",
            "load_mode": load_mode, "package_import_error": package_import_error,
            "kernel_file_raw_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "global_rng_consumed_in_every_case": all(rng_moved)}
    fd = os.open(out + ".json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(meta, indent=1) + "\n")
    return 0


def run_original_kernel(repo: Path, cases_npz: Path, out_npz: Path, *, python: Optional[str] = None, timeout_s: float = 1800.0) -> Path:
    """Separate process with the same environment rules as run_probe."""
    repo, cases_npz, out_npz = Path(repo).resolve(), Path(cases_npz).resolve(), Path(out_npz).resolve()
    if out_npz.exists():
        raise FileExistsError(f"{out_npz} exists already (never overwritten)")
    work = out_npz.parent / (out_npz.name + ".cwd")
    work.mkdir(parents=True, exist_ok=False)
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "TMP": str(out_npz.parent),
                "TEMP": str(out_npz.parent), "MPLCONFIGDIR": str(work), "OPENBLAS_NUM_THREADS": "1"})
    cmd = [python or sys.executable, "-s", str(Path(__file__).resolve()), "--repo", str(repo), "--kernel-cases", str(cases_npz),
           "--kernel-out", str(out_npz)]
    r = subprocess.run(cmd, env=env, cwd=str(work), capture_output=True, text=True, timeout=timeout_s)
    if r.returncode != 0:
        raise RuntimeError(f"original kernel run failed ({r.returncode}): {r.stderr[-2000:]}")
    return out_npz


def run_probe(repo: Path, out_dir: Path, *, config: Optional[Path] = None, hashseed: str = "0", python: Optional[str] = None,
              timeout_s: float = 300.0) -> Path:
    """Start the worker in a separate process; return out_dir. Raises on failure or timeout."""
    repo, out_dir = Path(repo).resolve(), Path(out_dir).resolve()
    if out_dir.exists():
        raise FileExistsError(f"probe output {out_dir} exists already (never overwritten)")
    if str(out_dir).upper().startswith("C:"):
        raise ValueError("refusing to write on C:")
    config = Path(config) if config is not None else repo / "v9_alpha" / "config" / "lantern_hub.yaml"
    if not config.is_file():
        raise FileNotFoundError(f"registry source missing: {config}")
    work = out_dir.parent / (out_dir.name + ".cwd")
    work.mkdir(parents=True, exist_ok=False)
    tmp = str(out_dir.parent)
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONHASHSEED": str(hashseed), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
                "TMP": tmp, "TEMP": tmp, "MPLCONFIGDIR": str(work), "OPENBLAS_NUM_THREADS": "1"})
    cmd = [python or sys.executable, "-s", str(Path(__file__).resolve()), "--repo", str(repo), "--config", str(config), "--out-dir", str(out_dir)]
    r = subprocess.run(cmd, env=env, cwd=str(work), capture_output=True, text=True, timeout=timeout_s)
    if r.returncode != 0:
        raise RuntimeError(f"legacy probe failed ({r.returncode}): {r.stderr[-2000:]}")
    return out_dir


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--config")
    ap.add_argument("--out-dir")
    ap.add_argument("--kernel-cases")
    ap.add_argument("--kernel-out")
    a = ap.parse_args()
    if a.kernel_cases:
        raise SystemExit(_kernel_worker(a.repo, a.kernel_cases, a.kernel_out))
    raise SystemExit(_worker(a.repo, a.config, a.out_dir))
