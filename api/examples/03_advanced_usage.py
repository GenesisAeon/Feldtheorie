#!/usr/bin/env python3
"""
Advanced Usage Examples for UTAC API

Demonstrates advanced patterns:
- Error handling and validation
- Batch processing
- Asynchronous requests
- Data export and visualization
- Parameter sweeps

Requirements:
    pip install requests matplotlib numpy pandas

Usage:
    # Start the server first:
    uvicorn api.server:app --port 8000

    # Then run this script:
    python api/examples/03_advanced_usage.py
"""

import requests
import json
import base64
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Base URL
BASE_URL = "http://localhost:8000"


# ============================================================================
# Error Handling
# ============================================================================

def example_robust_error_handling():
    """Demonstrate proper error handling for all error types"""
    print("\n" + "="*70)
    print("ADVANCED 1: Robust Error Handling")
    print("="*70)

    test_cases = [
        {
            "name": "Valid request",
            "endpoint": "/api/sonify",
            "method": "POST",
            "data": {"beta": 4.0, "theta": 50.0, "duration": 1.0},
            "expected": 200
        },
        {
            "name": "Invalid beta (too high)",
            "endpoint": "/api/sonify",
            "method": "POST",
            "data": {"beta": 25.0, "theta": 50.0},
            "expected": 422
        },
        {
            "name": "Invalid field type",
            "endpoint": "/api/sonify",
            "method": "POST",
            "data": {"beta": 4.0, "theta": 50.0, "field_type": "invalid_type"},
            "expected": 422
        },
        {
            "name": "Mismatched array lengths",
            "endpoint": "/api/analyze",
            "method": "POST",
            "data": {"R": [0.1, 0.2, 0.3], "sigma": [0.1, 0.2]},
            "expected": 422
        },
        {
            "name": "System not found",
            "endpoint": "/api/system/nonexistent",
            "method": "GET",
            "data": None,
            "expected": 404
        },
        {
            "name": "Duration too long",
            "endpoint": "/api/simulate",
            "method": "POST",
            "data": {"theta": 0.5, "beta": 4.0, "duration": 200.0},
            "expected": 422
        }
    ]

    print("\nTesting error handling across all endpoints:\n")

    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test['name']}")

        try:
            if test['method'] == 'GET':
                response = requests.get(f"{BASE_URL}{test['endpoint']}", timeout=5)
            else:
                response = requests.post(
                    f"{BASE_URL}{test['endpoint']}",
                    json=test['data'],
                    timeout=5
                )

            status_ok = response.status_code == test['expected']
            symbol = "✅" if status_ok else "❌"

            print(f"    {symbol} Status: {response.status_code} (expected {test['expected']})")

            if not status_ok or response.status_code >= 400:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"       Error: {error_data['detail']}")

        except requests.exceptions.Timeout:
            print(f"    ⏱️  Timeout (> 5s)")
        except requests.exceptions.ConnectionError:
            print(f"    🔌 Connection error - is server running?")
            break
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")

    print(f"\n{'='*70}")
    print("✅ Error handling test complete")


# ============================================================================
# Batch Processing
# ============================================================================

def example_batch_analysis():
    """Analyze multiple datasets in batch"""
    print("\n" + "="*70)
    print("ADVANCED 2: Batch Processing")
    print("="*70)

    # Generate synthetic datasets for different systems
    datasets = []

    # Dataset 1: Strongly coupled (β ≈ 4.5)
    R1 = np.linspace(0, 1, 15)
    sigma1 = 1 / (1 + np.exp(-4.5 * (R1 - 0.5)))
    datasets.append(("strongly_coupled_synthetic", R1.tolist(), sigma1.tolist()))

    # Dataset 2: Weakly coupled (β ≈ 2.5)
    R2 = np.linspace(0, 1, 15)
    sigma2 = 1 / (1 + np.exp(-2.5 * (R2 - 0.6)))
    datasets.append(("weakly_coupled_synthetic", R2.tolist(), sigma2.tolist()))

    # Dataset 3: Physically constrained (β ≈ 7.0)
    R3 = np.linspace(0, 1, 15)
    sigma3 = 1 / (1 + np.exp(-7.0 * (R3 - 0.4)))
    datasets.append(("physically_constrained_synthetic", R3.tolist(), sigma3.tolist()))

    print(f"\nAnalyzing {len(datasets)} datasets in batch...\n")

    results = []

    for i, (name, R, sigma) in enumerate(datasets, 1):
        print(f"[{i}/{len(datasets)}] {name}")

        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={
                "R": R,
                "sigma": sigma,
                "bootstrap_iterations": 200  # Reduced for speed
            }
        )

        if response.status_code == 200:
            data = response.json()
            results.append({
                "name": name,
                "beta": data['beta'],
                "beta_ci": data['beta_ci'],
                "theta": data['theta'],
                "theta_ci": data['theta_ci'],
                "field_type": data['field_type'],
                "r_squared": data['r_squared']
            })
            print(f"    ✅ β={data['beta']:.3f}, Θ={data['theta']:.3f}, R²={data['r_squared']:.4f}")
            print(f"       Field type: {data['field_type']}")
        else:
            print(f"    ❌ Failed: {response.json()}")

    # Save batch results
    output_path = Path("advanced_batch_results.json")
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\n💾 Batch results saved to: {output_path}")

    print(f"\n{'='*70}")
    print("✅ Batch processing complete")


# ============================================================================
# Parallel Processing
# ============================================================================

def example_parallel_sonification():
    """Generate multiple audio files in parallel"""
    print("\n" + "="*70)
    print("ADVANCED 3: Parallel Sonification")
    print("="*70)

    # Define parameter sweep
    beta_values = [2.5, 3.5, 4.5, 6.0, 8.0]
    theta_values = [30.0, 50.0, 70.0]

    print(f"\nGenerating {len(beta_values) * len(theta_values)} audio files in parallel...")
    print(f"  β values: {beta_values}")
    print(f"  Θ values: {theta_values}")

    def sonify_params(beta: float, theta: float) -> Dict[str, Any]:
        """Sonify single parameter combination"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/sonify",
                json={
                    "beta": beta,
                    "theta": theta,
                    "duration": 2.0,
                    "sample_rate": 22050  # Lower for speed
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # Save audio file
                audio_bytes = base64.b64decode(data['audio_base64'])
                filename = f"advanced_parallel_beta{beta:.1f}_theta{theta:.0f}.wav"
                filepath = Path(filename)
                filepath.write_bytes(audio_bytes)

                return {
                    "beta": beta,
                    "theta": theta,
                    "success": True,
                    "file": str(filepath),
                    "field_type": data['metadata']['field_type']
                }
            else:
                return {
                    "beta": beta,
                    "theta": theta,
                    "success": False,
                    "error": response.json()
                }

        except Exception as e:
            return {
                "beta": beta,
                "theta": theta,
                "success": False,
                "error": str(e)
            }

    # Execute in parallel
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        for beta in beta_values:
            for theta in theta_values:
                future = executor.submit(sonify_params, beta, theta)
                futures.append(future)

        # Collect results
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            symbol = "✅" if result['success'] else "❌"
            if result['success']:
                print(f"  {symbol} β={result['beta']:.1f}, Θ={result['theta']:.0f} → {result['file']}")
            else:
                print(f"  {symbol} β={result['beta']:.1f}, Θ={result['theta']:.0f} → Error: {result.get('error', 'Unknown')}")

    elapsed = time.time() - start_time

    success_count = sum(1 for r in results if r['success'])

    print(f"\n⏱️  Completed in {elapsed:.2f}s")
    print(f"   Success rate: {success_count}/{len(results)} ({100*success_count/len(results):.0f}%)")

    print(f"\n{'='*70}")
    print("✅ Parallel sonification complete")


# ============================================================================
# Parameter Sweep
# ============================================================================

def example_parameter_sweep():
    """Systematic parameter sweep for simulation"""
    print("\n" + "="*70)
    print("ADVANCED 4: Parameter Sweep (Simulation)")
    print("="*70)

    beta_range = [3.0, 4.0, 5.0, 6.0]
    theta_range = [0.4, 0.5, 0.6, 0.7]

    print(f"\nRunning parameter sweep:")
    print(f"  β: {beta_range}")
    print(f"  Θ: {theta_range}")
    print(f"  Total: {len(beta_range) * len(theta_range)} simulations\n")

    sweep_results = []

    for i, beta in enumerate(beta_range):
        for j, theta in enumerate(theta_range):
            idx = i * len(theta_range) + j + 1
            total = len(beta_range) * len(theta_range)

            print(f"[{idx}/{total}] β={beta:.1f}, Θ={theta:.2f}", end=" ... ")

            response = requests.post(
                f"{BASE_URL}/api/simulate",
                json={
                    "beta": beta,
                    "theta": theta,
                    "initial_R": 0.5,
                    "initial_psi": 0.1,
                    "initial_phi": 0.05,
                    "duration": 5.0,
                    "dt": 0.05,
                    "stimulus": {
                        "base": 0.15,
                        "amplitude": 0.2,
                        "frequency": 0.3
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()

                # Calculate summary statistics
                R_final = data['R'][-1]
                sigma_final = data['sigma'][-1]
                R_mean = np.mean(data['R'])
                R_std = np.std(data['R'])

                sweep_results.append({
                    "beta": beta,
                    "theta": theta,
                    "R_final": R_final,
                    "sigma_final": sigma_final,
                    "R_mean": R_mean,
                    "R_std": R_std
                })

                print(f"✅ R_final={R_final:.3f}, σ_final={sigma_final:.3f}")
            else:
                print(f"❌ Failed")

    # Save sweep results
    output_path = Path("advanced_parameter_sweep.json")
    output_path.write_text(json.dumps(sweep_results, indent=2))
    print(f"\n💾 Sweep results saved to: {output_path}")

    # Summary
    print(f"\nSummary:")
    print(f"  Completed: {len(sweep_results)}/{len(beta_range) * len(theta_range)} simulations")

    if sweep_results:
        R_finals = [r['R_final'] for r in sweep_results]
        print(f"  R_final range: [{min(R_finals):.3f}, {max(R_finals):.3f}]")
        print(f"  Mean R_final: {np.mean(R_finals):.3f}")

    print(f"\n{'='*70}")
    print("✅ Parameter sweep complete")


# ============================================================================
# Data Export
# ============================================================================

def example_data_export():
    """Export analysis results in multiple formats"""
    print("\n" + "="*70)
    print("ADVANCED 5: Data Export (JSON, CSV)")
    print("="*70)

    # Run analysis
    print("\n[1/3] Running analysis...")

    R = [i * 0.1 for i in range(11)]
    sigma = [1 / (1 + np.exp(-4.2 * (r - 0.55))) for r in R]

    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json={"R": R, "sigma": sigma, "bootstrap_iterations": 500}
    )

    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.json()}")
        return

    analysis = response.json()
    print(f"✅ Analysis complete (β={analysis['beta']:.3f}, Θ={analysis['theta']:.3f})")

    # Export as JSON
    print("\n[2/3] Exporting as JSON...")
    json_path = Path("advanced_export.json")
    json_path.write_text(json.dumps({
        "input": {"R": R, "sigma": sigma},
        "results": analysis,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_version": "1.0.0"
        }
    }, indent=2))
    print(f"✅ Saved to: {json_path}")

    # Export as CSV
    print("\n[3/3] Exporting as CSV...")
    csv_path = Path("advanced_export.csv")
    csv_lines = [
        "parameter,value,lower_ci,upper_ci",
        f"theta,{analysis['theta']},{analysis['theta_ci'][0]},{analysis['theta_ci'][1]}",
        f"beta,{analysis['beta']},{analysis['beta_ci'][0]},{analysis['beta_ci'][1]}",
        f"r_squared,{analysis['r_squared']},,",
        f"aic,{analysis['aic']},,"
    ]
    csv_path.write_text("\n".join(csv_lines))
    print(f"✅ Saved to: {csv_path}")

    print(f"\n{'='*70}")
    print("✅ Data export complete")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all advanced examples"""
    print("\n" + "🚀 UTAC API - Advanced Usage Examples ".center(70, "="))

    try:
        # Check API health
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            raise ConnectionError("API not healthy")

        print("\n✅ API is healthy and ready")

        # Run examples
        example_robust_error_handling()
        example_batch_analysis()
        example_parallel_sonification()
        example_parameter_sweep()
        example_data_export()

        print("\n" + "="*70)
        print("✅ ALL ADVANCED EXAMPLES COMPLETED!")
        print("="*70)
        print("\nGenerated files:")
        print("  📊 advanced_batch_results.json")
        print("  📊 advanced_parameter_sweep.json")
        print("  📊 advanced_export.json")
        print("  📊 advanced_export.csv")
        print("  🎵 advanced_parallel_*.wav (multiple files)")
        print("\nThese examples demonstrate:")
        print("  1. Robust error handling for all error types")
        print("  2. Batch processing of multiple datasets")
        print("  3. Parallel requests for performance")
        print("  4. Systematic parameter sweeps")
        print("  5. Multi-format data export")
        print("="*70 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server!")
        print("Please start the server first:")
        print("  uvicorn api.server:app --port 8000\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
