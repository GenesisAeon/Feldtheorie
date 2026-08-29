"""H1 collapse test: Train A (Ising) + Train B (NSIDC sea ice) only.

Hold-out (data/holdout_sealed/) is never imported, opened, or referenced
by this script. Per RIG_v0_SCOPING.md section 5, this must run to
completion and be recorded BEFORE the hold-out may be opened for H2.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline

from estimators import role_vector

BASE = Path(__file__).resolve().parents[1]


def load_train_a() -> tuple[np.ndarray, np.ndarray]:
    data = np.load(BASE / "data" / "train_a" / "ising_run.npz")
    x = np.abs(data["magnetization"])  # standard: |M| as the order parameter (sign is arbitrary)
    d_star = data["d_star"]
    return x, d_star


def load_train_b() -> tuple[np.ndarray, np.ndarray]:
    """Daily NSIDC sea ice extent, 1988-01-01 onward (first fully continuous
    daily stretch -- verified 2026-08-29, no gaps > 1 day, no Missing flags).
    x = seasonal-anomaly (raw extent minus day-of-year climatological mean),
    the standard cryosphere analysis object -- required because the raw
    series' autocorrelation is dominated by the trivial ~365-day annual
    cycle, which would swamp tau/V estimation with the known seasonal
    period rather than any real dynamics. This is standard deseasonalization,
    not a post-hoc metric change; RIG_v0_SCOPING.md section 1 already
    specifies "the (detrended, per domain) series" for V.
    d_star = |anomaly - linear_trend| / std(anomaly), per section 3's
    literal specification ("normalized rolling deviation from the 40-year
    linear trend").
    """
    df = pd.read_csv(BASE / "data" / "train_b" / "N_seaice_extent_daily_v4.0.csv", skiprows=[1])
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]].rename(columns={"Year": "year", "Month": "month", "Day": "day"}))
    df = df[df["date"] >= "1988-01-01"].reset_index(drop=True)
    assert (df["date"].diff().dt.days.dropna() == 1.0).all(), "expected fully continuous daily record"

    df["doy"] = df["date"].dt.dayofyear.clip(upper=365)  # fold leap-day into day 365
    climatology = df.groupby("doy")["Extent"].transform("mean")
    anomaly = (df["Extent"] - climatology).to_numpy()

    t_idx = np.arange(len(anomaly))
    trend_coef = np.polyfit(t_idx, anomaly, 1)
    trend = np.polyval(trend_coef, t_idx)
    d_star = np.abs(anomaly - trend) / anomaly.std()

    return anomaly, d_star


def normalize_time(d_star: np.ndarray, tau: float) -> np.ndarray:
    tau = max(tau, 1.0)
    return np.arange(len(d_star)) / tau


def pooled_goodness(t_prime_list: list[np.ndarray], d_star_list: list[np.ndarray], n_grid: int = 200) -> dict[str, float]:
    """Interpolate each domain's d*(t') onto a common grid spanning the
    overlap of both domains' t' ranges, compute the pointwise mean curve,
    then score each domain's deviation from it."""
    lo = max(t.min() for t in t_prime_list)
    hi = min(t.max() for t in t_prime_list)
    if hi <= lo:
        return {"mean_abs_dev": float("nan"), "one_minus_r2": float("nan"), "overlap": 0.0}

    grid = np.linspace(lo, hi, n_grid)
    interpolated = []
    for t_prime, d_star in zip(t_prime_list, d_star_list):
        order = np.argsort(t_prime)
        interpolated.append(np.interp(grid, t_prime[order], d_star[order]))

    interpolated = np.array(interpolated)
    mean_curve = interpolated.mean(axis=0)

    abs_dev = np.abs(interpolated - mean_curve).mean()

    ss_res = ((interpolated - mean_curve) ** 2).sum()
    ss_tot = ((interpolated - interpolated.mean()) ** 2).sum()
    one_minus_r2 = ss_res / ss_tot if ss_tot > 0 else float("nan")

    return {"mean_abs_dev": float(abs_dev), "one_minus_r2": float(one_minus_r2), "overlap": float(hi - lo)}


def null_model_goodness(d_star_list: list[np.ndarray], n_knots: int = 1, n_grid: int = 200) -> dict[str, float]:
    """Same pooled-goodness test, but WITHOUT tau-normalization: each
    domain's raw (unnormalized) d*(t) index is smoothed by a spline with
    `n_knots` interior knots (matching the single-scalar tau's degrees of
    freedom), then pooled on a common [0,1]-rescaled-index grid. Tests
    whether generic curve flexibility alone -- without the physically
    motivated t/tau rescaling -- already collapses the domains."""
    smoothed = []
    for d_star in d_star_list:
        x = np.linspace(0, 1, len(d_star))
        spline = UnivariateSpline(x, d_star, k=3, s=len(d_star) * np.var(d_star) * 0.1)
        smoothed.append(spline(x))

    grid_index = [np.linspace(0, 1, len(s)) for s in smoothed]
    return pooled_goodness(grid_index, smoothed, n_grid=n_grid)


def main() -> None:
    x_a, d_star_a = load_train_a()
    x_b, d_star_b = load_train_b()

    role_a = role_vector(x_a)
    role_b = role_vector(x_b)

    t_prime_a = normalize_time(d_star_a, role_a["tau"])
    t_prime_b = normalize_time(d_star_b, role_b["tau"])

    h1_result = pooled_goodness([t_prime_a, t_prime_b], [d_star_a, d_star_b])
    null_result = null_model_goodness([d_star_a, d_star_b])

    tau_normalization_beats_null = h1_result["mean_abs_dev"] < null_result["mean_abs_dev"]

    report = {
        "role_vector_train_a": role_a,
        "role_vector_train_b": role_b,
        "h1_pooled_goodness_tau_normalized": h1_result,
        "null_model_goodness_raw_index": null_result,
        "tau_normalization_beats_null": bool(tau_normalization_beats_null),
        "note": (
            "Fail-threshold check against hold-out cannot run yet -- "
            "hold-out is sealed per RIG_v0_SCOPING.md section 5. This "
            "report only establishes the Train A+B baseline goodness "
            "values that any future hold-out result will be compared "
            "against (hold-out must be <= 2x this mean_abs_dev, or H1 is "
            "rejected)."
        ),
    }

    out_path = BASE / "results" / "h1_train_ab_result.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
