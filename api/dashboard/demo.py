#!/usr/bin/env python3
"""
Demo script for Collective Field Dashboard

Creates a demo field and simulates dynamics for dashboard visualization.

Usage:
    python api/dashboard/demo.py
"""

import asyncio
import time

import requests

BASE_URL = "http://localhost:8000"


def create_demo_field():
    """Create a demo field with sample agents."""
    print("🧬 Creating demo field...")

    response = requests.post(
        f"{BASE_URL}/api/collective/field/create",
        json={
            "field_id": "demo_field",
            "texts": [
                "Die Resonanz zwischen Bewusstsein und Feld zeigt eine tiefe Emergenz und Kohärenz",
                "Consciousness emerges from the coupling of individual agents in semantic space",
                "Synchronization enables collective understanding and shared emergence patterns",
                "The field develops through iterative feedback and harmonic vibrations",
            ],
            "v_rig": 1.0,
        },
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Field created: {data['field_id']}")
        print(f"   Agents: {data['n_agents']}")
        print(f"   Message: {data['message']}")
        return True
    elif response.status_code == 409:
        print("ℹ️  Field already exists (using existing)")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.json()}")
        return False


def get_field_state():
    """Get current field state."""
    response = requests.get(f"{BASE_URL}/api/collective/field/demo_field")

    if response.status_code == 200:
        state = response.json()
        print(f"\n📊 Current Field State:")
        print(f"   κ_field (pairwise): {state['kappa_field_pairwise']:.3f}")
        print(f"   κ_field (centroid): {state['kappa_field_centroid']:.3f}")
        print(f"   κ_field (weighted): {state['kappa_field_weighted']:.3f}")
        print(f"   β_sync: {state['beta_sync']:.2f}")
        print(f"   v_collective: {state['v_collective']:.3f}")
        print(f"   Agents: {state['n_agents']}")
        return state
    else:
        print(f"❌ Error getting state: {response.status_code}")
        return None


def delete_demo_field():
    """Delete the demo field."""
    print("\n🗑️  Deleting demo field...")

    response = requests.delete(f"{BASE_URL}/api/collective/field/demo_field")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False


def run_demo():
    """Run the complete demo."""
    print("=" * 60)
    print("🎨 Collective Field Dashboard - Demo")
    print("=" * 60)

    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API server not responding!")
            print("   Start it with: uvicorn api.server:app --reload --port 8000")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Start it with: uvicorn api.server:app --reload --port 8000")
        return

    print("✅ API server is running\n")

    # Create demo field
    if not create_demo_field():
        return

    # Get initial state
    get_field_state()

    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("=" * 60)
    print()
    print("1. Open the dashboard:")
    print("   → Open api/dashboard/index.html in your browser")
    print("   → Or run: python -m http.server 8080 (in api/dashboard/)")
    print()
    print("2. Connect to field:")
    print("   → Enter field ID: demo_field")
    print("   → Click 'Connect to Field'")
    print()
    print("3. Watch the magic! ✨")
    print("   → Real-time metrics updating")
    print("   → Live charts showing evolution")
    print("   → Agent list with resonances")
    print()
    print("4. To clean up:")
    print("   → Run this script again with --clean")
    print()


def cleanup():
    """Clean up demo field."""
    print("=" * 60)
    print("🧹 Cleaning up demo field")
    print("=" * 60)
    delete_demo_field()


if __name__ == "__main__":
    import sys

    if "--clean" in sys.argv:
        cleanup()
    else:
        run_demo()
