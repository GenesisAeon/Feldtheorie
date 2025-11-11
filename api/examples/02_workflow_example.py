#!/usr/bin/env python3
"""
Workflow Example for UTAC API

Demonstrates complete research workflows combining multiple endpoints:
1. Analyze empirical data → Sonify results → Simulate dynamics
2. Get system metadata → Simulate with parameters → Compare results

Requirements:
    pip install requests matplotlib numpy

Usage:
    # Start the server first:
    uvicorn api.server:app --port 8000

    # Then run this script:
    python api/examples/02_workflow_example.py
"""

import requests
import json
import base64
import numpy as np
from pathlib import Path

# API Base URL
BASE_URL = "http://localhost:8000"


# ============================================================================
# Workflow 1: Data → Analysis → Sonification → Simulation
# ============================================================================

def workflow_analyze_sonify_simulate():
    """
    Complete workflow: Analyze empirical data, sonify the fitted parameters,
    then simulate the dynamics to verify behavior.
    """
    print("\n" + "="*70)
    print("WORKFLOW 1: Analyze → Sonify → Simulate")
    print("="*70)

    # Step 1: Prepare empirical data (e.g., ecosystem collapse data)
    print("\n[1/4] Preparing empirical data...")
    print("      Simulating ecosystem collapse measurements")

    # Synthetic data: ecological stability vs. biodiversity loss
    R = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # True parameters: β≈4.2, Θ≈0.55 (strongly coupled system)
    sigma = [0.99, 0.98, 0.96, 0.92, 0.82, 0.55, 0.25, 0.08, 0.02, 0.01, 0.005]

    print(f"      Data points: {len(R)}")
    print(f"      R range: [{min(R)}, {max(R)}]")
    print(f"      σ range: [{min(sigma):.3f}, {max(sigma):.3f}]")

    # Step 2: Analyze data to fit β and Θ
    print("\n[2/4] Analyzing data (β-fitting)...")

    analyze_response = requests.post(
        f"{BASE_URL}/api/analyze",
        json={
            "R": R,
            "sigma": sigma,
            "bootstrap_iterations": 500
        }
    )

    if analyze_response.status_code != 200:
        print(f"❌ Analysis failed: {analyze_response.json()}")
        return

    analysis = analyze_response.json()

    print(f"✅ Analysis complete!")
    print(f"   Θ = {analysis['theta']:.3f} [{analysis['theta_ci'][0]:.3f}, {analysis['theta_ci'][1]:.3f}]")
    print(f"   β = {analysis['beta']:.3f} [{analysis['beta_ci'][0]:.3f}, {analysis['beta_ci'][1]:.3f}]")
    print(f"   R² = {analysis['r_squared']:.4f}")
    print(f"   Field type: {analysis['field_type']}")

    # Step 3: Sonify the fitted parameters
    print("\n[3/4] Generating audio from fitted parameters...")

    sonify_response = requests.post(
        f"{BASE_URL}/api/sonify",
        json={
            "beta": analysis['beta'],
            "theta": analysis['theta'] * 100,  # Scale to Hz range
            "field_type": analysis['field_type'],
            "duration": 4.0,
            "sample_rate": 44100
        }
    )

    if sonify_response.status_code != 200:
        print(f"❌ Sonification failed: {sonify_response.json()}")
        return

    sonify_data = sonify_response.json()

    # Save audio file
    audio_bytes = base64.b64decode(sonify_data['audio_base64'])
    audio_path = Path("workflow1_ecosystem_collapse.wav")
    audio_path.write_bytes(audio_bytes)

    print(f"✅ Audio generated!")
    print(f"   Duration: {sonify_data['metadata']['duration']}s")
    print(f"   Base frequency: {sonify_data['metadata']['base_frequency_hz']:.1f} Hz")
    print(f"   🎵 Saved to: {audio_path}")

    # Step 4: Simulate dynamics with fitted parameters
    print("\n[4/4] Running simulation with fitted parameters...")

    simulate_response = requests.post(
        f"{BASE_URL}/api/simulate",
        json={
            "theta": analysis['theta'],
            "beta": analysis['beta'],
            "initial_R": 0.9,  # Start near collapse
            "initial_psi": 0.05,
            "initial_phi": 0.02,
            "duration": 15.0,
            "dt": 0.05,
            "stimulus": {
                "base": 0.1,
                "amplitude": 0.15,
                "frequency": 0.2
            }
        }
    )

    if simulate_response.status_code != 200:
        print(f"❌ Simulation failed: {simulate_response.json()}")
        return

    simulation = simulate_response.json()

    print(f"✅ Simulation complete!")
    print(f"   Time steps: {len(simulation['time'])}")
    print(f"   Final R: {simulation['R'][-1]:.3f}")
    print(f"   Final σ: {simulation['sigma'][-1]:.3f}")

    # Save simulation results
    sim_path = Path("workflow1_simulation.json")
    sim_path.write_text(json.dumps(simulation, indent=2))
    print(f"   💾 Saved to: {sim_path}")

    print(f"\n{'='*70}")
    print("✅ WORKFLOW 1 COMPLETE!")
    print(f"{'='*70}")
    print(f"\nResults:")
    print(f"  1. Fitted parameters: β={analysis['beta']:.3f}, Θ={analysis['theta']:.3f}")
    print(f"  2. Audio representation: {audio_path}")
    print(f"  3. Dynamic simulation: {sim_path}")
    print(f"\nInterpretation:")
    print(f"  Field type '{analysis['field_type']}' indicates {get_field_type_description(analysis['field_type'])}")


# ============================================================================
# Workflow 2: System Comparison
# ============================================================================

def workflow_system_comparison():
    """
    Compare multiple systems by retrieving metadata and running simulations.
    """
    print("\n" + "="*70)
    print("WORKFLOW 2: System Comparison (AMOC vs Amazon)")
    print("="*70)

    systems = ["amoc", "amazon"]
    results = {}

    for system_id in systems:
        print(f"\n[{system_id.upper()}] Fetching system metadata...")

        # Get system metadata
        system_response = requests.get(f"{BASE_URL}/api/system/{system_id}")

        if system_response.status_code != 200:
            print(f"❌ System '{system_id}' not found")
            continue

        system = system_response.json()
        params = system['parameters']

        print(f"✅ {system['name']}")
        print(f"   Domain: {system['domain']}")
        print(f"   β = {params['beta']:.3f} [{params['beta_ci'][0]:.3f}, {params['beta_ci'][1]:.3f}]")
        print(f"   Θ = {params['theta']:.3f} [{params['theta_ci'][0]:.3f}, {params['theta_ci'][1]:.3f}]")
        print(f"   Field type: {system['field_type']}")

        # Run simulation with system parameters
        print(f"   Running simulation...")

        simulate_response = requests.post(
            f"{BASE_URL}/api/simulate",
            json={
                "theta": params['theta'],
                "beta": params['beta'],
                "initial_R": 0.6,
                "initial_psi": 0.1,
                "initial_phi": 0.05,
                "duration": 10.0,
                "dt": 0.05,
                "stimulus": {
                    "base": 0.15,
                    "amplitude": 0.2,
                    "frequency": 0.3
                }
            }
        )

        if simulate_response.status_code != 200:
            print(f"   ❌ Simulation failed")
            continue

        simulation = simulate_response.json()

        # Calculate statistics
        import statistics
        R_mean = statistics.mean(simulation['R'])
        R_std = statistics.stdev(simulation['R'])
        sigma_final = simulation['sigma'][-1]

        print(f"   ✅ Simulation complete")
        print(f"      R: mean={R_mean:.3f}, std={R_std:.3f}")
        print(f"      Final σ: {sigma_final:.3f}")

        results[system_id] = {
            'system': system,
            'simulation': simulation,
            'stats': {
                'R_mean': R_mean,
                'R_std': R_std,
                'sigma_final': sigma_final
            }
        }

    # Compare results
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")

    for system_id, data in results.items():
        system = data['system']
        stats = data['stats']

        print(f"\n{system['name'].upper()}")
        print(f"  β: {system['parameters']['beta']:.3f}")
        print(f"  R variability: {stats['R_std']:.3f}")
        print(f"  Final stability: {stats['sigma_final']:.3f}")
        print(f"  Field type: {system['field_type']}")

    # Save comparison
    comparison_path = Path("workflow2_comparison.json")
    comparison_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n💾 Full comparison saved to: {comparison_path}")

    print(f"\n{'='*70}")
    print("✅ WORKFLOW 2 COMPLETE!")
    print(f"{'='*70}")


# ============================================================================
# Workflow 3: Field Type Survey
# ============================================================================

def workflow_field_type_survey():
    """
    Survey all field types and sonify each one.
    """
    print("\n" + "="*70)
    print("WORKFLOW 3: Field Type Acoustic Survey")
    print("="*70)

    # Get all field types
    print("\n[1/2] Fetching field type catalog...")

    fieldtypes_response = requests.get(f"{BASE_URL}/api/fieldtypes")

    if fieldtypes_response.status_code != 200:
        print(f"❌ Failed to get field types")
        return

    field_types = fieldtypes_response.json()['field_types']

    print(f"✅ Found {len(field_types)} field types")

    # Sonify each field type
    print(f"\n[2/2] Generating audio for each field type...")

    audio_files = []

    for i, ft in enumerate(field_types, 1):
        print(f"\n[{i}/{len(field_types)}] {ft['name'].upper()}")
        print(f"      β range: {ft['beta_range']}")
        print(f"      {ft['description']}")

        # Use middle of beta range
        beta_mid = sum(ft['beta_range']) / 2
        theta_hz = ft['acoustic_profile']['base_frequency']

        sonify_response = requests.post(
            f"{BASE_URL}/api/sonify",
            json={
                "beta": beta_mid,
                "theta": theta_hz,
                "field_type": ft['name'],
                "duration": 3.0,
                "sample_rate": 44100
            }
        )

        if sonify_response.status_code != 200:
            print(f"      ❌ Sonification failed")
            continue

        sonify_data = sonify_response.json()

        # Save audio
        audio_bytes = base64.b64decode(sonify_data['audio_base64'])
        audio_path = Path(f"workflow3_{ft['name']}.wav")
        audio_path.write_bytes(audio_bytes)
        audio_files.append(audio_path)

        print(f"      ✅ Audio saved: {audio_path}")
        print(f"         β={beta_mid:.1f}, Θ={theta_hz:.1f} Hz")
        print(f"         Timbre: {ft['acoustic_profile']['timbre']}")

    print(f"\n{'='*70}")
    print("✅ WORKFLOW 3 COMPLETE!")
    print(f"{'='*70}")
    print(f"\nGenerated {len(audio_files)} audio files:")
    for path in audio_files:
        print(f"  🎵 {path}")
    print(f"\nListen to each file to hear the acoustic signature of different")
    print(f"threshold field types (weakly coupled → meta-adaptive).")


# ============================================================================
# Helper Functions
# ============================================================================

def get_field_type_description(field_type: str) -> str:
    """Get human-readable description of field type"""
    descriptions = {
        "weakly_coupled": "gradual, diffuse transitions with weak feedback",
        "high_dimensional": "complex, multi-scale dynamics",
        "strongly_coupled": "sharp, critical transitions with strong feedback",
        "physically_constrained": "hard physical limits and constraints",
        "meta_adaptive": "extreme sensitivity and meta-stable dynamics"
    }
    return descriptions.get(field_type, "unknown dynamics")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all workflow examples"""
    print("\n" + "🔬 UTAC API - Workflow Examples ".center(70, "="))

    try:
        # Check API health
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            raise ConnectionError("API not healthy")

        print("\n✅ API is healthy and ready")
        print(f"   Version: {health_response.json()['version']}")

        # Run workflows
        workflow_analyze_sonify_simulate()
        workflow_system_comparison()
        workflow_field_type_survey()

        print("\n" + "="*70)
        print("✅ ALL WORKFLOWS COMPLETED!")
        print("="*70)
        print("\nGenerated files:")
        print("  📊 workflow1_ecosystem_collapse.wav")
        print("  📊 workflow1_simulation.json")
        print("  📊 workflow2_comparison.json")
        print("  📊 workflow3_*.wav (5 files)")
        print("\nThese workflows demonstrate:")
        print("  1. Complete research pipeline (data → analysis → sonification)")
        print("  2. Cross-system comparison and simulation")
        print("  3. Systematic field type characterization")
        print("="*70 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server!")
        print("Please start the server first:")
        print("  uvicorn api.server:app --port 8000\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
