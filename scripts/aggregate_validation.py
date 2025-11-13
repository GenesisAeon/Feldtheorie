#!/usr/bin/env python
"""
Aggregate Validation Results

Reads validation CSV and creates aggregated statistics grouped by
(lattice, noise, J/T).

Input:
    analysis/results/rg_phase2_microscopic_validation.csv

Output:
    analysis/results/rg_phase2_microscopic_validation_agg.json
"""
from __future__ import annotations
import json, pathlib, pandas as pd

IN_DIR  = pathlib.Path("analysis/results")
OUT_JSON = IN_DIR/"rg_phase2_microscopic_validation_agg.json"

def main():
    """Aggregate validation results."""
    csv = IN_DIR/"rg_phase2_microscopic_validation.csv"
    if not csv.exists():
        raise FileNotFoundError(f"Validation CSV not found: {csv}")

    print(f"📊 Aggregating validation results from {csv}")

    df = pd.read_csv(csv)

    # Aggregation nach (lattice, noise, J/T)
    g = df.groupby(["lattice","noise","J_over_T"])
    agg = g.agg(beta_mean=("beta_hat","mean"),
                beta_std=("beta_hat","std"),
                beta_n=("beta_hat","count")).reset_index()

    payload = {
        "summary": {"n_records": int(len(df)), "n_groups": int(len(agg))},
        "records": df.to_dict(orient="records"),
        "groups":  agg.to_dict(orient="records"),
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2))
    print(f"✅ Wrote: {OUT_JSON}")
    print(f"\n📊 Summary:")
    print(f"  Total records: {len(df)}")
    print(f"  Unique groups: {len(agg)}")
    print(f"  β overall mean: {df['beta_hat'].mean():.3f} ± {df['beta_hat'].std():.3f}")

if __name__ == "__main__":
    main()
