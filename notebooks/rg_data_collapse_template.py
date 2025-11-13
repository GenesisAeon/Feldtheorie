# %% [markdown]
# # RG Data-Collapse Template (UTAC β from J/T)
# Ziel:
# - Finite-Size-Scaling & Data-Collapse
# - Seeds-Statistik & 95%-KI
# - Optional: Binder-Kumulant-Collapse falls M2/M4 vorhanden
#
# Voraussetzungen:
# - results JSON/CSV in analysis/results/* aus validate_phase2.py / aggregate_validation.py
# - matplotlib, numpy, pandas, scipy
#
# Nutzung:
# - Datei ist Jupytext-kompatibel. In Jupyter: "Open" -> wird als Notebook erkannt.
# - Oder via jupytext: jupytext --to ipynb notebooks/rg_data_collapse_template.py

# %%
import json, math, itertools, pathlib
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

RESULTS_DIR = pathlib.Path("analysis/results")
AGG_JSON   = RESULTS_DIR / "rg_phase2_microscopic_validation_agg.json"
RAW_JSON   = RESULTS_DIR / "rg_phase2_microscopic_validation.json"  # optional pro-run
CSV_FILE   = RESULTS_DIR / "rg_phase2_microscopic_validation.csv"   # optional

# %% [markdown]
# ## Daten laden

# %%
def _load_any():
    if AGG_JSON.exists():
        return pd.json_normalize(json.loads(AGG_JSON.read_text())["records"])
    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE)
    if RAW_JSON.exists():
        return pd.json_normalize(json.loads(RAW_JSON.read_text())["records"])
    raise FileNotFoundError("Keine Validation-Ergebnisse gefunden (agg.json/csv/json fehlt).")

df = _load_any()
print(df.head())
print("N =", len(df))

# %% [markdown]
# Erwartete Spalten (mindestens):
# - beta_hat, beta_ci_low, beta_ci_high
# - J_over_T, lattice, noise, seed
# - optional: R, response (für Collapse auf Rohkurven)
# Prüfe und säubere:

# %%
req = {"beta_hat","J_over_T","lattice","noise","seed"}
missing = req - set(df.columns)
if missing:
    raise ValueError(f"Fehlende Spalten: {missing}")

# %% [markdown]
# ## Finite-Size-Collapse auf Kurven (optional)
# Wenn Rohkurven (R,response) pro Kombination vorliegen, versuchen wir einen globalen Collapse.
# Wir optimieren zwei Exponenten (a,b), so dass reskalierte Kurven minimalen MSE haben:
#  R' = (R - R_c) * N^a,    y' = response * N^b
#  Minimierung über alle Datensätze

# %%
def try_data_collapse(df_curves: pd.DataFrame, max_samples=200_000):
    # df_curves erwartet Spalten: R, response, lattice, group_id (unique pro Kurve)
    # Wir definieren ein Loss: mittlere Quad.-Distanz zum globalen Mittel in Bins
    if not {"R","response","lattice","group_id"} <= set(df_curves.columns):
        print("Keine Rohkurven, skip Collapse.")
        return None

    if len(df_curves) > max_samples:
        df_curves = df_curves.sample(max_samples, random_state=1337)

    R_c = df_curves["R"].median()  # heuristischer Schätzer
    Ns  = df_curves["lattice"].astype(float).values

    X   = df_curves[["R","lattice"]].to_numpy()
    y   = df_curves["response"].to_numpy()

    def collapse_loss(theta):
        a, b = theta
        Rp = (X[:,0] - R_c) * (X[:,1] ** a)
        yp = y * (X[:,1] ** b)
        # Binning
        bins = np.linspace(Rp.min(), Rp.max(), 200)
        idx  = np.digitize(Rp, bins)
        dfb  = pd.DataFrame({"bin": idx, "y": yp})
        g    = dfb.groupby("bin")["y"]
        mu   = g.transform("mean")
        return float(np.nanmean((dfb["y"] - mu)**2))

    res = minimize(collapse_loss, x0=np.array([0.5,0.0]), method="Nelder-Mead")
    print("Best (a,b) =", res.x, "loss=", res.fun)
    return {"a": float(res.x[0]), "b": float(res.x[1]), "R_c": float(R_c), "loss": float(res.fun)}

# %% [markdown]
# ## β vs. J/T: Linearisierung & Fit
# Wir fitten eine einfache Beziehung β ~ c0 + c1*(J/T)^γ (log/lin je nach Skala) und reporten Fit-Qualität.

# %%
from scipy.stats import linregress

def fit_beta_vs_J_over_T(df):
    x = np.log(df["J_over_T"].astype(float).values)
    y = df["beta_hat"].astype(float).values
    lr = linregress(x, y)
    return {"r": lr.rvalue, "r2": lr.rvalue**2, "slope": lr.slope, "intercept": lr.intercept}

fit = fit_beta_vs_J_over_T(df)
print("Fit β ~ a*log(J/T) + b → R² =", round(fit["r2"], 3))

# %% [markdown]
# ## Plots

# %%
def plot_beta_hist(df):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.hist(df["beta_hat"], bins=40, edgecolor='black', alpha=0.7)
    ax.set_xlabel("β")
    ax.set_ylabel("Häufigkeit")
    ax.set_title("Verteilung β über Seeds/Noise/Lattice")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def plot_beta_vs_J_over_T(df):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.scatter(np.log(df["J_over_T"]), df["beta_hat"], s=12, alpha=0.75)
    ax.set_xlabel("log(J/T)")
    ax.set_ylabel("β")
    ax.set_title("β vs. log(J/T)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

_ = plot_beta_hist(df)
_ = plot_beta_vs_J_over_T(df)
plt.show()

# %% [markdown]
# ## Advanced: Finite-Size Scaling
#
# Für die Lattice-Größen N=64, 128, 256 können wir prüfen, ob β(N) konvergiert.
# Erwartung: β(N) → β_∞ mit Potenzgesetz-Korrektur β(N) = β_∞ + c*N^(-ω)

# %%
def plot_beta_by_lattice(df):
    """Plot β convergence vs. lattice size for each J/T ratio."""
    fig, ax = plt.subplots(figsize=(8,5))

    for jt, sub in df.groupby("J_over_T"):
        # Group by lattice and compute mean β
        lattice_stats = sub.groupby("lattice")["beta_hat"].agg(["mean", "std"]).reset_index()

        ax.errorbar(lattice_stats["lattice"], lattice_stats["mean"],
                   yerr=lattice_stats["std"],
                   marker='o', capsize=5, label=f"J/T={jt:.1f}")

    ax.set_xlabel("Lattice Size N")
    ax.set_ylabel("β")
    ax.set_title("Finite-Size Scaling: β(N)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

_ = plot_beta_by_lattice(df)
plt.show()

# %% [markdown]
# ## Export Results
#
# Save summary statistics to JSON for documentation.

# %%
summary = {
    "n_records": int(len(df)),
    "beta_mean": float(df["beta_hat"].mean()),
    "beta_std": float(df["beta_hat"].std()),
    "beta_min": float(df["beta_hat"].min()),
    "beta_max": float(df["beta_hat"].max()),
    "fit_r2": float(fit["r2"]),
    "fit_slope": float(fit["slope"]),
    "fit_intercept": float(fit["intercept"])
}

summary_path = RESULTS_DIR / "rg_data_collapse_summary.json"
summary_path.write_text(json.dumps(summary, indent=2))
print(f"\n✅ Summary saved to: {summary_path}")
print(json.dumps(summary, indent=2))
