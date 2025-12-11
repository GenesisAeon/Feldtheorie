#!/usr/bin/env python3
"""
Basic Usage Examples for UTAC API

Demonstrates all 5 endpoints with simple examples.

Requirements:
    pip install requests

Usage:
    # Start the server first:
    uvicorn api.server:app --port 8000

    # Then run this script:
    python api/examples/01_basic_usage.py
"""

import base64
import json
from pathlib import Path

import requests

# API Base URL
BASE_URL = "http://localhost:8000"


def example_health_check():
    """Example: Check API health"""
    print("\n" + "=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/health")
    data = response.json()

    print(f"Status: {data['status']}")
    print(f"Version: {data['version']}")
    print(f"Phase: {data['phase']} ({data['progress']})")
    print("\nEndpoints:")
    for name, status in data["endpoints"].items():
        print(f"  - {name}: {status}")


def example_get_fieldtypes():
    """Example: Get all field types"""
    print("\n" + "=" * 60)
    print("Example 2: Get Field Types")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/fieldtypes")
    data = response.json()

    print(f"Found {len(data['field_types'])} field types:\n")
    for ft in data["field_types"]:
        print(f"📊 {ft['name'].upper()}")
        print(f"   β range: {ft['beta_range']}")
        print(f"   {ft['description']}")
        print(f"   Examples: {', '.join(ft['examples'][:2])}")
        print()


def example_sonify():
    """Example: Generate audio from threshold dynamics"""
    print("\n" + "=" * 60)
    print("Example 3: Sonification (Generate Audio)")
    print("=" * 60)

    # Parameters for a strongly coupled system (like AMOC)
    request_data = {
        "beta": 4.2,
        "theta": 50.0,
        "field_type": "strongly_coupled",
        "duration": 3.0,
        "sample_rate": 44100,
    }

    print("Generating audio with:")
    print(f"  β = {request_data['beta']}")
    print(f"  Θ = {request_data['theta']}")
    print(f"  Field type = {request_data['field_type']}")

    response = requests.post(f"{BASE_URL}/api/sonify", json=request_data)

    if response.status_code == 200:
        data = response.json()
        metadata = data["metadata"]

        print("\n✅ Audio generated successfully!")
        print(f"   Duration: {metadata['duration']}s")
        print(f"   Sample rate: {metadata['sample_rate']} Hz")
        print(f"   Field type: {metadata['field_type']}")
        print(f"   Base frequency: {metadata['base_frequency_hz']:.1f} Hz")

        # Decode and save audio
        audio_bytes = base64.b64decode(data["audio_base64"])
        output_path = Path("threshold_sound.wav")
        output_path.write_bytes(audio_bytes)
        print(f"\n🎵 Audio saved to: {output_path}")
    else:
        print(f"❌ Error: {response.json()}")


def example_analyze():
    """Example: Fit β and Θ to empirical data"""
    print("\n" + "=" * 60)
    print("Example 4: Analysis (β-Fitting)")
    print("=" * 60)

    # Generate synthetic logistic data
    # σ(R) = 1 / (1 + exp(-β(R-Θ)))
    # True parameters: β=4.5, Θ=0.5
    R = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sigma = [0.01, 0.02, 0.05, 0.12, 0.35, 0.68, 0.88, 0.95, 0.98, 0.99]

    request_data = {"R": R, "sigma": sigma, "bootstrap_iterations": 1000}

    print("Analyzing threshold data...")
    print(f"  Data points: {len(R)}")

    response = requests.post(f"{BASE_URL}/api/analyze", json=request_data)

    if response.status_code == 200:
        data = response.json()

        print("\n✅ Analysis complete!")
        print("\nFitted parameters:")
        print(
            f"  Θ (theta) = {data['theta']:.3f} [{data['theta_ci'][0]:.3f}, {data['theta_ci'][1]:.3f}]"
        )
        print(
            f"  β (beta)  = {data['beta']:.3f} [{data['beta_ci'][0]:.3f}, {data['beta_ci'][1]:.3f}]"
        )
        print(f"  R² = {data['r_squared']:.4f}")
        print(f"  AIC = {data['aic']:.2f}")
        print(f"\nField type: {data['field_type']}")

        print("\nNull model comparison:")
        for model, metrics in data["null_models"].items():
            print(f"  {model}:")
            print(f"    ΔAIC = {metrics['delta_aic']:.2f}")
            print(f"    ΔR² = {metrics['delta_r2']:.4f}")
    else:
        print(f"❌ Error: {response.json()}")


def example_get_system():
    """Example: Get system metadata"""
    print("\n" + "=" * 60)
    print("Example 5: Get System Metadata")
    print("=" * 60)

    system_id = "amazon"
    print(f"Fetching metadata for system: {system_id}")

    response = requests.get(f"{BASE_URL}/api/system/{system_id}")

    if response.status_code == 200:
        data = response.json()

        print(f"\n✅ System: {data['name']}")
        print(f"   Domain: {data['domain']}")
        print(f"   Field type: {data['field_type']}")

        params = data["parameters"]
        print("\nParameters:")
        print(
            f"  β = {params['beta']:.3f} [{params['beta_ci'][0]:.3f}, {params['beta_ci'][1]:.3f}]"
        )
        print(
            f"  Θ = {params['theta']:.3f} [{params['theta_ci'][0]:.3f}, {params['theta_ci'][1]:.3f}]"
        )
        print(f"  R² = {params['r_squared']:.4f}")

        print("\nReferences:")
        for ref in data["references"]:
            print(f"  - {ref}")
    else:
        print(f"❌ Error: {response.json()}")


def example_simulate():
    """Example: Run coupled threshold field simulation"""
    print("\n" + "=" * 60)
    print("Example 6: Simulation (Coupled Dynamics)")
    print("=" * 60)

    request_data = {
        "theta": 0.66,
        "beta": 4.8,
        "initial_R": 0.5,
        "initial_psi": 0.1,
        "initial_phi": 0.05,
        "duration": 10.0,
        "dt": 0.05,
        "stimulus": {"base": 0.15, "amplitude": 0.25, "frequency": 0.3},
    }

    print("Running simulation with:")
    print(f"  Θ = {request_data['theta']}")
    print(f"  β = {request_data['beta']}")
    print(f"  Duration = {request_data['duration']}")

    response = requests.post(f"{BASE_URL}/api/simulate", json=request_data)

    if response.status_code == 200:
        data = response.json()

        print("\n✅ Simulation complete!")
        print(f"   Time steps: {len(data['time'])}")
        print(f"   Final R: {data['R'][-1]:.3f}")
        print(f"   Final σ: {data['sigma'][-1]:.3f}")

        # Show some stats
        import statistics

        print("\nStatistics:")
        print(f"  R:   mean={statistics.mean(data['R']):.3f}, max={max(data['R']):.3f}")
        print(f"  Ψ:   mean={statistics.mean(data['psi']):.3f}, max={max(data['psi']):.3f}")
        print(f"  φ:   mean={statistics.mean(data['phi']):.3f}, max={max(data['phi']):.3f}")
        print(f"  σ:   mean={statistics.mean(data['sigma']):.3f}, max={max(data['sigma']):.3f}")

        # Optionally save to JSON
        output_path = Path("simulation_results.json")
        output_path.write_text(json.dumps(data, indent=2))
        print(f"\n💾 Results saved to: {output_path}")
    else:
        print(f"❌ Error: {response.json()}")


# ============================================================================
# Main
# ============================================================================


def main():
    """Run all examples"""
    print("\n" + "🌐 UTAC API - Basic Usage Examples ".center(60, "="))

    try:
        example_health_check()
        example_get_fieldtypes()
        example_analyze()
        example_get_system()
        example_simulate()
        example_sonify()  # Last because it generates file

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server!")
        print("Please start the server first:")
        print("  uvicorn api.server:app --port 8000\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
