#!/usr/bin/env python3
"""
Repository Self-Similarity Analysis (Prediction 6)
===================================================

Tests whether the Feldtheorie repository itself follows UTAC scaling laws,
demonstrating the framework's universal applicability.

Prediction: File sizes, commit frequencies, and inter-event times should show
β ≈ 4.2 universality, demonstrating fractal self-reference.

Author: Johann Benjamin Römer (with Claude-Sonnet-4)
Date: 2025-12-16
Version: v9.0.0-alpha
"""

import numpy as np
import json
from pathlib import Path
from datetime import datetime
from scipy import stats
from scipy.optimize import curve_fit
import warnings

warnings.filterwarnings('ignore')


def logistic_function(x, beta, theta, L=1.0):
    """
    Standard logistic function: σ(β(x - Θ))

    Args:
        x: Input variable
        beta: Steepness parameter (UTAC universality ≈ 4.2)
        theta: Threshold/midpoint
        L: Maximum value (default 1.0 for CDF)
    """
    return L / (1 + np.exp(-beta * (x - theta)))


def compute_inter_event_times(timestamps):
    """
    Compute inter-event times between commits.

    Args:
        timestamps: Unix timestamps (sorted newest first from git log)

    Returns:
        Inter-event times in hours
    """
    timestamps = np.array(timestamps)
    # Reverse to get chronological order
    timestamps = timestamps[::-1]

    # Compute differences (in seconds)
    diffs = np.diff(timestamps)

    # Convert to hours
    inter_event_hours = diffs / 3600.0

    return inter_event_hours


def fit_logistic_to_distribution(data, data_type="commits"):
    """
    Fit logistic CDF to empirical distribution.

    Args:
        data: Array of values (inter-event times or file sizes)
        data_type: Description for reporting

    Returns:
        Dictionary with fit parameters and statistics
    """
    # Sort data
    sorted_data = np.sort(data)
    n = len(sorted_data)

    # Empirical CDF
    ecdf = np.arange(1, n + 1) / n

    # Initial parameter guesses
    theta_init = np.median(sorted_data)
    beta_init = 4.2  # UTAC universality guess

    try:
        # Fit logistic CDF
        params, covariance = curve_fit(
            logistic_function,
            sorted_data,
            ecdf,
            p0=[beta_init, theta_init],
            maxfev=10000
        )

        beta_fit, theta_fit = params

        # Compute R²
        ecdf_pred = logistic_function(sorted_data, beta_fit, theta_fit)
        ss_res = np.sum((ecdf - ecdf_pred) ** 2)
        ss_tot = np.sum((ecdf - np.mean(ecdf)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Standard errors
        perr = np.sqrt(np.diag(covariance))

        return {
            'beta': beta_fit,
            'beta_stderr': perr[0],
            'theta': theta_fit,
            'theta_stderr': perr[1],
            'r_squared': r_squared,
            'n_samples': n,
            'data_type': data_type
        }

    except Exception as e:
        print(f"Warning: Logistic fit failed for {data_type}: {e}")
        return None


def fit_power_law(data, data_type="file_sizes"):
    """
    Fit power-law distribution: P(x) ∝ x^(-α)

    Args:
        data: Array of values (file sizes)
        data_type: Description

    Returns:
        Dictionary with power-law exponent and statistics
    """
    # Remove zeros
    data = data[data > 0]

    if len(data) < 10:
        return None

    # Log-log linear fit
    sorted_data = np.sort(data)
    # Rank (reverse: largest = rank 1)
    ranks = np.arange(len(sorted_data), 0, -1)

    # Log-log
    log_sizes = np.log10(sorted_data)
    log_ranks = np.log10(ranks)

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        log_sizes, log_ranks
    )

    # Power-law exponent α (slope of log-log plot)
    alpha = -slope

    return {
        'alpha': alpha,
        'alpha_stderr': std_err,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'n_samples': len(data),
        'data_type': data_type
    }


def analyze_repository_self_similarity(commit_times_file, file_sizes_file):
    """
    Main analysis function.

    Args:
        commit_times_file: Path to file with Unix timestamps
        file_sizes_file: Path to file with file sizes in bytes

    Returns:
        Dictionary with all analysis results
    """
    print("=" * 70)
    print("REPOSITORY SELF-SIMILARITY ANALYSIS (Prediction 6)")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Framework: UTAC v9.0.0-alpha (Dimensional Emergence)")
    print()

    results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'framework_version': 'v9.0.0-alpha',
            'prediction': 'Repository follows UTAC scaling laws (β ≈ 4.2)'
        }
    }

    # ===== PART 1: COMMIT INTER-EVENT TIMES =====
    print("[1/3] Analyzing Commit Inter-Event Times...")
    print("-" * 70)

    timestamps = np.loadtxt(commit_times_file)
    inter_event_hours = compute_inter_event_times(timestamps)

    print(f"Total commits: {len(timestamps)}")
    print(f"Inter-event samples: {len(inter_event_hours)}")
    print(f"Time span: {(timestamps.max() - timestamps.min()) / 86400:.1f} days")
    print()

    # Statistics
    print("Descriptive Statistics (hours between commits):")
    print(f"  Mean:   {np.mean(inter_event_hours):.2f} hours")
    print(f"  Median: {np.median(inter_event_hours):.2f} hours")
    print(f"  Std:    {np.std(inter_event_hours):.2f} hours")
    print(f"  Min:    {np.min(inter_event_hours):.4f} hours ({np.min(inter_event_hours)*60:.1f} min)")
    print(f"  Max:    {np.max(inter_event_hours):.2f} hours ({np.max(inter_event_hours)/24:.1f} days)")
    print()

    # Logistic fit
    commit_fit = fit_logistic_to_distribution(inter_event_hours, "commit_inter_events")

    if commit_fit:
        print("Logistic Model Fit: σ(β(Δt - Θ))")
        print(f"  β (steepness):  {commit_fit['beta']:.3f} ± {commit_fit['beta_stderr']:.3f}")
        print(f"  Θ (threshold):  {commit_fit['theta']:.2f} ± {commit_fit['theta_stderr']:.2f} hours")
        print(f"  R²:             {commit_fit['r_squared']:.4f}")
        print()

        # Check UTAC prediction
        beta_predicted = 4.2
        beta_error = abs(commit_fit['beta'] - beta_predicted)
        z_score = beta_error / commit_fit['beta_stderr'] if commit_fit['beta_stderr'] > 0 else np.inf

        print(f"UTAC Prediction Check:")
        print(f"  Predicted β:    {beta_predicted:.1f}")
        print(f"  Observed β:     {commit_fit['beta']:.3f}")
        print(f"  Deviation:      {beta_error:.3f} ({beta_error/beta_predicted*100:.1f}%)")
        print(f"  Z-score:        {z_score:.2f}")

        if z_score < 2:
            print(f"  Result:         ✅ CONSISTENT with UTAC (Z < 2)")
        else:
            print(f"  Result:         ⚠️  Deviation from UTAC (Z ≥ 2)")

        results['commit_analysis'] = commit_fit
        results['commit_analysis']['utac_check'] = {
            'predicted_beta': beta_predicted,
            'deviation': beta_error,
            'deviation_percent': beta_error / beta_predicted * 100,
            'z_score': z_score,
            'consistent': z_score < 2
        }

    print()

    # ===== PART 2: FILE SIZE DISTRIBUTION =====
    print("[2/3] Analyzing File Size Distribution...")
    print("-" * 70)

    file_sizes = np.loadtxt(file_sizes_file)

    print(f"Total files: {len(file_sizes)}")
    print(f"Total size: {np.sum(file_sizes) / 1e6:.2f} MB")
    print()

    print("Descriptive Statistics (file sizes):")
    print(f"  Mean:   {np.mean(file_sizes):.0f} bytes ({np.mean(file_sizes)/1024:.1f} KB)")
    print(f"  Median: {np.median(file_sizes):.0f} bytes ({np.median(file_sizes)/1024:.1f} KB)")
    print(f"  Std:    {np.std(file_sizes):.0f} bytes")
    print(f"  Min:    {np.min(file_sizes):.0f} bytes")
    print(f"  Max:    {np.max(file_sizes):.0f} bytes ({np.max(file_sizes)/1e6:.2f} MB)")
    print()

    # Power-law fit
    powerlaw_fit = fit_power_law(file_sizes, "file_sizes")

    if powerlaw_fit:
        print("Power-Law Fit: P(size) ∝ size^(-α)")
        print(f"  α (exponent):   {powerlaw_fit['alpha']:.3f} ± {powerlaw_fit['alpha_stderr']:.3f}")
        print(f"  R²:             {powerlaw_fit['r_squared']:.4f}")
        print(f"  p-value:        {powerlaw_fit['p_value']:.2e}")
        print()

        # Zipf's law check (α ≈ 1)
        if 0.8 < powerlaw_fit['alpha'] < 1.5:
            print(f"  Observation:    ✅ Zipf-like distribution (α ≈ 1)")
        else:
            print(f"  Observation:    Power-law present, but not Zipf (α ≠ 1)")

        results['file_size_analysis'] = powerlaw_fit

    # Also try logistic fit on file sizes
    filesize_logistic = fit_logistic_to_distribution(file_sizes / 1024, "file_sizes_kb")

    if filesize_logistic:
        print()
        print("Logistic Model Fit (alternative view):")
        print(f"  β (steepness):  {filesize_logistic['beta']:.3f} ± {filesize_logistic['beta_stderr']:.3f}")
        print(f"  Θ (threshold):  {filesize_logistic['theta']:.2f} KB")
        print(f"  R²:             {filesize_logistic['r_squared']:.4f}")

        results['file_size_logistic'] = filesize_logistic

    print()

    # ===== PART 3: ACTIVITY BURSTS =====
    print("[3/3] Analyzing Activity Burst Patterns...")
    print("-" * 70)

    # Define "burst" as inter-event time < 1 hour
    burst_threshold = 1.0  # hours
    bursts = inter_event_hours < burst_threshold
    burst_ratio = np.sum(bursts) / len(bursts)

    print(f"Burst threshold: {burst_threshold} hour")
    print(f"Burst commits:   {np.sum(bursts)} / {len(bursts)} ({burst_ratio*100:.1f}%)")
    print()

    # Clustering: consecutive bursts = work session
    burst_sessions = []
    current_session = 0
    for is_burst in bursts:
        if is_burst:
            current_session += 1
        else:
            if current_session > 0:
                burst_sessions.append(current_session)
            current_session = 0
    if current_session > 0:
        burst_sessions.append(current_session)

    burst_sessions = np.array(burst_sessions)

    if len(burst_sessions) > 0:
        print(f"Work sessions detected: {len(burst_sessions)}")
        print(f"  Mean session length:  {np.mean(burst_sessions):.1f} commits")
        print(f"  Median session:       {np.median(burst_sessions):.0f} commits")
        print(f"  Longest session:      {np.max(burst_sessions)} commits")
        print()

        results['activity_bursts'] = {
            'burst_threshold_hours': burst_threshold,
            'burst_count': int(np.sum(bursts)),
            'burst_ratio': float(burst_ratio),
            'work_sessions': int(len(burst_sessions)),
            'mean_session_length': float(np.mean(burst_sessions)),
            'median_session_length': float(np.median(burst_sessions)),
            'max_session_length': int(np.max(burst_sessions))
        }

    # ===== SUMMARY =====
    print()
    print("=" * 70)
    print("SUMMARY: Repository Self-Similarity")
    print("=" * 70)

    if commit_fit:
        print(f"✨ Commit Inter-Event β: {commit_fit['beta']:.3f} ± {commit_fit['beta_stderr']:.3f}")

        if commit_fit['beta_stderr'] > 0:
            z = abs(commit_fit['beta'] - 4.2) / commit_fit['beta_stderr']
            if z < 2:
                print(f"   → CONSISTENT with UTAC prediction (β ≈ 4.2)")
            else:
                print(f"   → Deviates from UTAC prediction (Z = {z:.2f})")

    if powerlaw_fit:
        print(f"📊 File Size Power-Law α: {powerlaw_fit['alpha']:.3f}")
        if 0.8 < powerlaw_fit['alpha'] < 1.5:
            print(f"   → Zipf-like distribution (scale-free)")

    print()
    print("🌀 Conclusion:")

    if commit_fit and commit_fit.get('utac_check', {}).get('consistent', False):
        print("   The repository DOES follow UTAC scaling laws!")
        print("   This demonstrates FRACTAL SELF-REFERENCE:")
        print("   The tool (code) follows the rules of the theory. ✅")
    else:
        print("   The repository shows emergent patterns, but β deviates from 4.2.")
        print("   This suggests domain-specific scaling dynamics.")

    print()
    print("=" * 70)

    return results


def save_results(results, output_path):
    """Save results as JSON."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    # File paths
    commit_times_file = "/tmp/commit_times.txt"
    file_sizes_file = "/tmp/file_sizes.txt"
    output_json = "analysis/repository_self_similarity_v9.json"

    # Run analysis
    results = analyze_repository_self_similarity(commit_times_file, file_sizes_file)

    # Save results
    Path("analysis").mkdir(exist_ok=True)
    save_results(results, output_json)

    print("\n🎯 Prediction 6 Analysis Complete!")
    print(f"   See: {output_json}")
