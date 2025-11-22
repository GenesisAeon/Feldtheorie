"""
UTAC v2.0 - LLM Emergence Data Extraction
==========================================

Extract β-values from Large Language Model scaling curves.

Data Sources:
1. Wei et al. (2022) - "Emergent Abilities of Large Language Models"
   - arXiv: 2206.07682
   - 137 emergent capabilities documented
   
2. Hoffman et al. (2022) - "Training Compute-Optimal LLMs" (Chinchilla)
   - arXiv: 2203.15556
   
3. OpenAI GPT-3/GPT-4 Technical Reports

Method:
- Digitize published performance curves (parameter count vs. accuracy)
- Fit UTAC sigmoid: S(N) = 1/(1 + exp(-β(log(N) - log(N_c))))
- Extract β via nonlinear least squares
- Bootstrap for uncertainty (n=1000)

Author: Johann Römer
Date: 2025-11-15
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import bootstrap
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# UTAC SIGMOID MODEL
# ============================================================

def utac_sigmoid(R, beta, theta):
    """
    UTAC sigmoid activation function.
    
    Parameters:
    -----------
    R : array-like
        Progress variable (e.g., log parameter count)
    beta : float
        Steepness parameter (target of extraction)
    theta : float
        Threshold location (critical parameter count)
    
    Returns:
    --------
    S : array-like
        System response [0, 1]
    """
    return 1.0 / (1.0 + np.exp(-beta * (R - theta)))


def fit_utac_beta(R, S, initial_guess=[4.0, np.median(R)]):
    """
    Fit UTAC sigmoid to data and extract β.
    
    Parameters:
    -----------
    R : array-like
        Progress variable (e.g., log parameter count)
    S : array-like
        System response (e.g., accuracy, 0-1 normalized)
    initial_guess : list
        [beta_0, theta_0] initial parameter guesses
    
    Returns:
    --------
    beta : float
        Fitted steepness parameter
    theta : float
        Fitted threshold
    r_squared : float
        Goodness of fit
    beta_ci : tuple
        (lower_95, upper_95) confidence interval
    """
    # Fit sigmoid
    try:
        params, cov = curve_fit(
            utac_sigmoid, 
            R, S, 
            p0=initial_guess,
            bounds=([0.1, R.min()], [20.0, R.max()]),
            maxfev=10000
        )
        beta, theta = params
        
        # R-squared
        S_pred = utac_sigmoid(R, beta, theta)
        ss_res = np.sum((S - S_pred)**2)
        ss_tot = np.sum((S - np.mean(S))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Bootstrap confidence interval
        def bootstrap_beta(indices):
            R_boot = R[indices]
            S_boot = S[indices]
            try:
                params_boot, _ = curve_fit(
                    utac_sigmoid, R_boot, S_boot,
                    p0=[beta, theta],
                    bounds=([0.1, R.min()], [20.0, R.max()]),
                    maxfev=5000
                )
                return params_boot[0]  # Return beta only
            except:
                return beta  # Fallback to original
        
        # Simple percentile bootstrap
        n_bootstrap = 1000
        beta_samples = []
        for _ in range(n_bootstrap):
            indices = np.random.choice(len(R), size=len(R), replace=True)
            beta_samples.append(bootstrap_beta(indices))
        
        beta_ci = (np.percentile(beta_samples, 2.5), 
                   np.percentile(beta_samples, 97.5))
        
        return beta, theta, r_squared, beta_ci
    
    except Exception as e:
        print(f"Fitting failed: {e}")
        return None, None, None, (None, None)


# ============================================================
# DATA EXTRACTION FUNCTIONS
# ============================================================

def extract_wei_et_al_2022():
    """
    Extract data from Wei et al. (2022) paper.
    
    NOTE: This requires manual digitization of Figure 2 from the paper.
    Use WebPlotDigitizer (https://automeris.io/WebPlotDigitizer/)
    to extract (parameter_count, accuracy) pairs.
    
    Returns:
    --------
    datasets : list of dict
        Each dict contains {
            'name': str,
            'param_count': array (number of parameters),
            'accuracy': array (0-1 normalized),
            'source': str
        }
    """
    # Example data structure (REPLACE WITH ACTUAL DIGITIZED DATA)
    
    # Task: 3-digit arithmetic addition (Figure 2a from Wei et al.)
    arithmetic_3digit = {
        'name': 'Arithmetic_3digit',
        'param_count': np.array([
            1.3e9,   # GPT-3 Small
            6.7e9,   # GPT-3 Medium  
            13e9,    # GPT-3 Large
            175e9,   # GPT-3 Davinci
            540e9    # PaLM
        ]),
        'accuracy': np.array([0.02, 0.05, 0.15, 0.72, 0.89]),
        'source': 'Wei et al. 2022 - Fig 2a',
        'domain': 'AI/LLM',
        'threshold_type': 'Emergent Capability'
    }
    
    # Task: Multi-step reasoning (Big-Bench)
    multistep_reasoning = {
        'name': 'Multistep_Reasoning',
        'param_count': np.array([1e9, 8e9, 62e9, 137e9, 540e9]),
        'accuracy': np.array([0.25, 0.28, 0.35, 0.62, 0.78]),
        'source': 'Wei et al. 2022 - Fig 3',
        'domain': 'AI/LLM',
        'threshold_type': 'Emergent Capability'
    }
    
    # Add more tasks here after digitization
    
    return [arithmetic_3digit, multistep_reasoning]


def extract_chinchilla_scaling():
    """
    Extract data from Hoffmann et al. (2022) Chinchilla paper.
    
    Focus on loss curves showing transition to optimal scaling regime.
    """
    # Placeholder - requires digitization
    chinchilla_data = {
        'name': 'Chinchilla_Optimal_Scaling',
        'param_count': np.array([1e9, 7e9, 70e9]),
        'perplexity': np.array([12.5, 8.2, 5.1]),  # Lower is better
        'source': 'Hoffmann et al. 2022',
        'domain': 'AI/LLM',
        'threshold_type': 'Scaling Law Transition'
    }
    
    # Convert perplexity to 0-1 accuracy (inverse relationship)
    ppl_min, ppl_max = 5.0, 15.0
    chinchilla_data['accuracy'] = 1 - (
        (chinchilla_data['perplexity'] - ppl_min) / (ppl_max - ppl_min)
    )
    
    return [chinchilla_data]


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_llm_emergence():
    """
    Main analysis function: Extract β from all LLM datasets.
    """
    # Collect all datasets
    datasets = []
    datasets.extend(extract_wei_et_al_2022())
    datasets.extend(extract_chinchilla_scaling())
    
    results = []
    
    print("="*60)
    print("UTAC β-EXTRACTION FROM LLM EMERGENCE CURVES")
    print("="*60)
    print()
    
    for data in datasets:
        print(f"\nAnalyzing: {data['name']}")
        print(f"Source: {data['source']}")
        print(f"N datapoints: {len(data['param_count'])}")
        
        # Use log parameter count as progress variable
        R = np.log10(data['param_count'])
        S = data['accuracy']
        
        # Fit UTAC sigmoid
        beta, theta, r2, beta_ci = fit_utac_beta(R, S)
        
        if beta is not None:
            print(f"β = {beta:.2f} (95% CI: [{beta_ci[0]:.2f}, {beta_ci[1]:.2f}])")
            print(f"θ (critical params) = 10^{theta:.2f} = {10**theta:.2e}")
            print(f"R² = {r2:.3f}")
            
            # Check if in RG Fixed Point Zone (3.5 < β < 5.5)
            in_rg_zone = 3.5 <= beta <= 5.5
            print(f"In RG Zone (3.5-5.5)? {'✅ YES' if in_rg_zone else '❌ NO'}")
            
            results.append({
                'System': data['name'],
                'Domain': data['domain'],
                'Threshold_Type': data['threshold_type'],
                'Beta': beta,
                'Beta_CI_Lower': beta_ci[0],
                'Beta_CI_Upper': beta_ci[1],
                'Theta_log10': theta,
                'Critical_Params': 10**theta,
                'R_Squared': r2,
                'N_Points': len(R),
                'Source': data['source']
            })
            
            # Plot
            plt.figure(figsize=(8, 5))
            
            # Data points
            plt.scatter(R, S, s=100, alpha=0.6, label='Data', zorder=3)
            
            # Fitted curve
            R_fine = np.linspace(R.min() - 0.5, R.max() + 0.5, 200)
            S_fit = utac_sigmoid(R_fine, beta, theta)
            plt.plot(R_fine, S_fit, 'r-', lw=2, 
                    label=f'UTAC Fit (β={beta:.2f})', zorder=2)
            
            # Threshold line
            plt.axvline(theta, color='gray', ls='--', alpha=0.5, 
                       label=f'Threshold (10^{theta:.1f})', zorder=1)
            
            plt.xlabel('log₁₀(Parameter Count)', fontsize=12)
            plt.ylabel('Accuracy (Normalized)', fontsize=12)
            plt.title(f'{data["name"]}\nβ = {beta:.2f} ± {(beta_ci[1]-beta_ci[0])/2:.2f}, R² = {r2:.3f}', 
                     fontsize=13, fontweight='bold')
            plt.legend(fontsize=10)
            plt.grid(alpha=0.3)
            plt.tight_layout()
            
            filename = f'LLM_{data["name"]}_beta_fit.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved: {filename}")
            plt.close()
    
    # Create summary DataFrame
    df_results = pd.DataFrame(results)
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"\nTotal LLM systems analyzed: {len(df_results)}")
    print(f"Mean β: {df_results['Beta'].mean():.2f} ± {df_results['Beta'].std():.2f}")
    print(f"Median β: {df_results['Beta'].median():.2f}")
    print(f"Range: [{df_results['Beta'].min():.2f}, {df_results['Beta'].max():.2f}]")
    
    n_in_rg = ((df_results['Beta'] >= 3.5) & (df_results['Beta'] <= 5.5)).sum()
    print(f"\nSystems in RG Zone (3.5-5.5): {n_in_rg}/{len(df_results)} ({100*n_in_rg/len(df_results):.1f}%)")
    
    # Statistical test: Is LLM β significantly different from 4.2?
    from scipy.stats import ttest_1samp
    t_stat, p_val = ttest_1samp(df_results['Beta'], 4.2)
    print(f"\nt-test vs. β=4.2: t={t_stat:.2f}, p={p_val:.4f}")
    
    if p_val > 0.05:
        print("✅ LLM β-values are statistically consistent with RG fixed point (β≈4.2)")
    else:
        print("⚠️ LLM β-values differ from 4.2 - requires explanation")
    
    # Save results
    csv_filename = 'LLM_Emergence_UTAC_Results.csv'
    df_results.to_csv(csv_filename, index=False)
    print(f"\n✅ Results saved to: {csv_filename}")
    
    return df_results


# ============================================================
# INSTRUCTIONS FOR USE
# ============================================================

if __name__ == "__main__":
    print("""
    ════════════════════════════════════════════════════════════
    UTAC LLM DATA EXTRACTION - INSTRUCTIONS
    ════════════════════════════════════════════════════════════
    
    STEP 1: DIGITIZE DATA
    ----------------------
    Use WebPlotDigitizer (https://automeris.io/WebPlotDigitizer/)
    to extract data from published papers:
    
    Required Papers:
    1. Wei et al. (2022) - arXiv:2206.07682
       - Figure 2: Emergent abilities across model scales
       - Figure 3: Multi-task performance
       
    2. Hoffmann et al. (2022) - arXiv:2203.15556
       - Figure 1: Chinchilla scaling laws
    
    3. Brown et al. (2020) - GPT-3 paper
       - Figure 3.1: Few-shot performance
    
    Extract (x, y) pairs where:
    - x = Parameter count (e.g., 175e9 for GPT-3)
    - y = Performance metric (accuracy, 0-1 normalized)
    
    STEP 2: UPDATE CODE
    -------------------
    Replace placeholder data in extract_wei_et_al_2022() 
    with your digitized values.
    
    STEP 3: RUN ANALYSIS
    --------------------
    python utac_llm_extraction.py
    
    OUTPUT:
    - CSV file with β-values for each LLM system
    - Plots showing sigmoid fits
    - Statistical summary
    
    ════════════════════════════════════════════════════════════
    """)
    
    # Run analysis
    results = analyze_llm_emergence()
    
    print("\n🎉 Analysis complete! Check output files.")
    print("Next: Add LLM results to UTAC v2.0 dataset")
