import os

# CONFIGURATION V4.0 - DATA DRIVEN
BETA_BASE_MEAN = 4.1  # Universal Cluster (Honeybee, Wei, etc.)
LOAD_FACTOR_OXFAM = 9.6  # Top 1% vs Global Avg (Oxfam 2024)
GINI_GLOBAL_WEALTH = 0.85  # Global Wealth Inequality


def run_analysis():
    print("--- UTAC V4.0: Inequality Amplifier Proof (Oxfam 2024) ---")

    # Formula: beta_eff = beta_base * (1 + Gini * Load)
    amplification = 1 + (GINI_GLOBAL_WEALTH * LOAD_FACTOR_OXFAM)
    beta_eff = BETA_BASE_MEAN * amplification

    print(f"Base Beta: {BETA_BASE_MEAN}")
    print(f"Inequality Load: {GINI_GLOBAL_WEALTH} * {LOAD_FACTOR_OXFAM}")
    print(f"Effective Beta: {beta_eff:.2f}")

    output_path = "analysis/results/oxfam_amplification_proof.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("Source: Carbon Inequality Kills (Oxfam 2024)\n")
        f.write(f"Beta_Base: {BETA_BASE_MEAN}\n")
        f.write(f"Beta_Eff: {beta_eff:.2f}\n")
        status = "BROKEN RAM (Collapse)" if beta_eff > 20 else "STABLE"
        f.write(f"System Status: {status}\n")


if __name__ == "__main__":
    run_analysis()
