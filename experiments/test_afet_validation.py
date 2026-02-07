from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
from scipy.stats import pearsonr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from theory.afet import AFETFramework


def main() -> int:
    framework = AFETFramework()
    csv_path = Path("data/derived/beta_estimates.csv")
    frame = pd.read_csv(csv_path)

    dataset = framework.load_beta_dataset(csv_path)
    predicted = [row["predicted_beta"] for row in dataset]
    observed = [row["observed_beta"] for row in dataset]

    r, p = pearsonr(predicted, observed)

    print("AFET Validation")
    print(f"rows={len(frame)}")
    print(f"pearson_r={r:.4f}")
    print(f"p_value={p:.6g}")

    if r > 0.8 and p < 0.001:
        print("status=PASS")
        return 0

    print("status=FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
