#!/usr/bin/env python
"""
RG Phase 2 Validation Runner

Runs validation across:
- Multiple random seeds (reproducibility)
- Multiple lattice sizes N (finite-size scaling)
- Multiple noise models (robustness)
- Multiple J/T ratios (emergent β relationship)

Usage:
    python scripts/validate_phase2.py --seeds 0 1 2 --lattice 64 128 --noise gaussian laplace

Environment variables:
    RG_SIM_ENTRYPOINT: Module:function for ABM simulator (default: scripts.stubs.rg_sim_stub:simulate)

Output:
    analysis/results/rg_phase2_microscopic_validation.csv
    analysis/results/rg_phase2_microscopic_validation.json
"""
from __future__ import annotations
import os, json, time, pathlib, importlib
import numpy as np, pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple
from scipy.optimize import curve_fit
from numpy.random import default_rng

OUT_DIR = pathlib.Path("analysis/results")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Erwartete Entry-Point-API:
#   simulate(J_over_T: float, lattice: int, noise: str, seed: int) -> Dict[str, Any]
#   Muss mindestens liefern: {"R": array, "response": array}
ENTRY_ENV = os.environ.get("RG_SIM_ENTRYPOINT", "scripts.stubs.rg_sim_stub:simulate")

def load_entrypoint():
    """Load the ABM simulator entry point from environment variable."""
    mod_name, fn_name = ENTRY_ENV.split(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)

def logistic(R, beta, theta):
    """
    UTAC sigmoid: σ(β(R-Θ)) = 1/(1+exp(-β(R-Θ)))

    Numerically stabilized to avoid overflow.
    """
    z = np.clip(beta*(R-theta), -60, 60)
    return 1.0/(1.0+np.exp(-z))

def fit_beta_theta(R, y):
    """
    Fit β and Θ from response curve using curve_fit.

    Parameters
    ----------
    R : array
        Resource/activation values
    y : array
        System response (sigmoid)

    Returns
    -------
    beta : float
        Fitted steepness parameter
    theta : float
        Fitted threshold
    """
    # Robuster Fit mit Bounds
    p0 = [4.0, np.median(R)]
    bounds = ([0.1, np.min(R)], [50.0, np.max(R)])
    beta, theta = curve_fit(logistic, R, y, p0=p0, bounds=bounds, maxfev=20000)[0]
    return float(beta), float(theta)

def bootstrap_ci(R, y, n_boot=200, seed=1337):
    """
    Bootstrap 95% confidence interval for β.

    Parameters
    ----------
    R : array
        Resource values
    y : array
        Response values
    n_boot : int
        Number of bootstrap samples
    seed : int
        Random seed

    Returns
    -------
    ci_low : float
        2.5th percentile
    ci_high : float
        97.5th percentile
    """
    rng = default_rng(seed)
    betas = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(R), len(R))
        b, _ = fit_beta_theta(R[idx], y[idx])
        betas.append(b)
    arr = np.array(betas)
    return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))

@dataclass
class Record:
    """Single validation run record."""
    seed: int
    lattice: int
    noise: str
    J_over_T: float
    beta_hat: float
    beta_ci_low: float
    beta_ci_high: float
    theta_hat: float

def run_once(sim_fn, J_over_T: float, lattice: int, noise: str, seed: int) -> Record:
    """
    Run a single validation: simulate + fit β.

    Parameters
    ----------
    sim_fn : callable
        Simulator function
    J_over_T : float
        Coupling-to-noise ratio
    lattice : int
        Lattice size
    noise : str
        Noise model
    seed : int
        Random seed

    Returns
    -------
    Record
        Validation results with β estimate and CI
    """
    out = sim_fn(J_over_T=J_over_T, lattice=lattice, noise=noise, seed=seed)
    R = np.asarray(out["R"]); y = np.asarray(out["response"])

    # sort by R
    idx = np.argsort(R); R = R[idx]; y = y[idx]

    beta, theta = fit_beta_theta(R, y)
    lo, hi = bootstrap_ci(R, y, n_boot=120, seed=seed+17)

    return Record(seed, lattice, noise, J_over_T, beta, lo, hi, theta)

def main():
    """Main validation runner."""
    import argparse
    ap = argparse.ArgumentParser(description="RG Phase 2 Validation Runner")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0,1,2,3,4,5,6,7,8,9],
                    help="Random seeds for reproducibility")
    ap.add_argument("--lattice", type=int, nargs="+", default=[64,128,256],
                    help="Lattice sizes for finite-size scaling")
    ap.add_argument("--noise", type=str, nargs="+", default=["gaussian","laplace","poisson"],
                    help="Noise models for robustness testing")
    ap.add_argument("--J_over_T", type=float, nargs="+", default=[0.5, 1.0, 1.5, 2.0],
                    help="Coupling-to-noise ratios")
    ap.add_argument("--tag", type=str, default=time.strftime("run_%Y%m%d_%H%M%S"),
                    help="Run tag for identification")
    args = ap.parse_args()

    print(f"🔬 RG Phase 2 Validation")
    print(f"Entry point: {ENTRY_ENV}")
    print(f"Seeds: {args.seeds}")
    print(f"Lattices: {args.lattice}")
    print(f"Noise models: {args.noise}")
    print(f"J/T ratios: {args.J_over_T}")

    sim_fn = load_entrypoint()
    recs: List[Record] = []

    total = len(args.seeds) * len(args.lattice) * len(args.noise) * len(args.J_over_T)
    count = 0

    for seed in args.seeds:
        for N in args.lattice:
            for nm in args.noise:
                for jt in args.J_over_T:
                    count += 1
                    print(f"  [{count}/{total}] seed={seed}, N={N}, noise={nm}, J/T={jt:.1f}...", end=" ")
                    rec = run_once(sim_fn, jt, N, nm, seed)
                    print(f"β={rec.beta_hat:.3f} [{rec.beta_ci_low:.3f}, {rec.beta_ci_high:.3f}]")
                    recs.append(rec)

    df = pd.DataFrame([asdict(r) for r in recs])

    # Save CSV
    csv_path = OUT_DIR/"rg_phase2_microscopic_validation.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Wrote: {csv_path}")

    # Save JSON
    payload = {"tag": args.tag, "records": df.to_dict(orient="records")}
    json_path = OUT_DIR/"rg_phase2_microscopic_validation.json"
    json_path.write_text(json.dumps(payload, indent=2))
    print(f"✅ Wrote: {json_path}")

    # Summary stats
    print(f"\n📊 Summary:")
    print(f"  Total runs: {len(df)}")
    print(f"  β mean: {df['beta_hat'].mean():.3f} ± {df['beta_hat'].std():.3f}")
    print(f"  β range: [{df['beta_hat'].min():.3f}, {df['beta_hat'].max():.3f}]")

if __name__ == "__main__":
    main()
