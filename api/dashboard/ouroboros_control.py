"""
OUROBOROS MISSION CONTROL
==========================

Streamlit dashboard for real-time control and visualization of the Ouroboros Engine.

This is the "Holodeck" - a visual interface to observe and interact with the
8-level cosmology simulation in real-time.

Usage:
    streamlit run api/dashboard/ouroboros_control.py

Features:
    - Live status monitoring
    - Real-time timeline visualization (🟢⚫ Garden of Worlds)
    - Interactive parameter controls
    - God-mode interventions
    - ECM score charts over generations
    - WebSocket streaming of events
"""

import asyncio
import json
import time
from datetime import datetime

import requests
import streamlit as st

# API Configuration
API_BASE = "http://localhost:8000"
API_OUROBOROS = f"{API_BASE}/api/ouroboros"


def get_status():
    """Fetch current status from API."""
    try:
        response = requests.get(f"{API_OUROBOROS}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        return None


def start_simulation(config=None):
    """Start the simulation."""
    try:
        response = requests.post(f"{API_OUROBOROS}/start", json=config, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to start: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error starting simulation: {e}")
        return None


def pause_simulation():
    """Pause the simulation."""
    try:
        response = requests.post(f"{API_OUROBOROS}/pause", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error pausing: {e}")
        return None


def resume_simulation():
    """Resume the simulation."""
    try:
        response = requests.post(f"{API_OUROBOROS}/resume", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error resuming: {e}")
        return None


def stop_simulation():
    """Stop the simulation."""
    try:
        response = requests.post(f"{API_OUROBOROS}/stop", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error stopping: {e}")
        return None


def reset_simulation():
    """Reset the simulation."""
    try:
        response = requests.post(f"{API_OUROBOROS}/reset", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error resetting: {e}")
        return None


def intervene(intervention_type, params):
    """Perform god-mode intervention."""
    try:
        payload = {
            "intervention_type": intervention_type,
            "params": params
        }
        response = requests.post(f"{API_OUROBOROS}/intervene", json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Intervention failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error during intervention: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Streamlit App
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Ouroboros Mission Control",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐍♾️ OUROBOROS MISSION CONTROL")
st.markdown("*The 8-Level Cosmology Simulation Dashboard*")

# Sidebar: Controls
with st.sidebar:
    st.header("⚙️ Control Panel")

    # Configuration
    with st.expander("🔧 Configuration", expanded=False):
        base_ecm = st.slider("Base ECM", 0.0, 1.0, 0.1, 0.01)
        mutation_rate = st.slider("Mutation Rate", 0.0, 1.0, 0.15, 0.01)
        gravity = st.slider("Gravity Constant", 0.1, 10.0, 1.0, 0.1)
        max_cycles = st.number_input("Max Cycles (0 = infinite)", 0, 1000, 0)
        pause_duration = st.slider("Pause Between Cycles (s)", 0.0, 10.0, 2.0, 0.5)

    # Start/Stop Controls
    st.subheader("🎮 Simulation Control")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start", use_container_width=True):
            config = {
                "base_ecm": base_ecm,
                "mutation_rate": mutation_rate,
                "gravity": gravity,
                "max_cycles": max_cycles if max_cycles > 0 else None,
                "pause_between_cycles": pause_duration
            }
            result = start_simulation(config)
            if result:
                st.success(result.get("message", "Started!"))

        if st.button("⏸️ Pause", use_container_width=True):
            result = pause_simulation()
            if result:
                st.info(result.get("message", "Paused"))

    with col2:
        if st.button("⏯️ Resume", use_container_width=True):
            result = resume_simulation()
            if result:
                st.success(result.get("message", "Resumed"))

        if st.button("⏹️ Stop", use_container_width=True):
            result = stop_simulation()
            if result:
                st.warning(result.get("message", "Stopped"))

    if st.button("🔄 Reset", use_container_width=True):
        result = reset_simulation()
        if result:
            st.info(result.get("message", "Reset complete"))

    # God Mode Interventions
    st.subheader("⚡ God Mode")

    intervention_type = st.selectbox(
        "Intervention Type",
        ["gravity_change", "mutation_boost", "energy_injection"]
    )

    if intervention_type == "gravity_change":
        new_gravity = st.slider("New Gravity", 0.1, 10.0, 1.5, 0.1)
        if st.button("🌌 Change Gravity"):
            result = intervene(intervention_type, {"new_gravity": new_gravity})
            if result and result.get("success"):
                st.success(f"Gravity changed! {result['effects']}")

    elif intervention_type == "mutation_boost":
        new_rate = st.slider("New Mutation Rate", 0.0, 1.0, 0.2, 0.01)
        if st.button("🧬 Boost Mutation"):
            result = intervene(intervention_type, {"new_rate": new_rate})
            if result and result.get("success"):
                st.success(f"Mutation rate changed! {result['effects']}")

    elif intervention_type == "energy_injection":
        energy = st.number_input("Energy Amount", 0.0, 1000.0, 100.0)
        if st.button("⚡ Inject Energy"):
            result = intervene(intervention_type, {"energy": energy})
            if result and result.get("success"):
                st.success(f"Energy injected! {result['effects']}")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (2s)", value=True)

# ═══════════════════════════════════════════════════════════════════════════
# Main Dashboard
# ═══════════════════════════════════════════════════════════════════════════

# Fetch status
status = get_status()

if status is None:
    st.error("⚠️ Cannot connect to Ouroboros API. Is the server running?")
    st.code("uvicorn api.server:app --reload --port 8000", language="bash")
    st.stop()

# State indicator
state = status.get("state", "unknown")
state_colors = {
    "idle": "🔵",
    "running": "🟢",
    "paused": "🟡",
    "completed": "⚪",
    "failed": "🔴"
}

state_emoji = state_colors.get(state, "❓")

st.header(f"{state_emoji} Status: {state.upper()}")

# Current Metrics
metrics = status.get("current_metrics", {})
history = status.get("history", {})

# Top-level metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Generation", metrics.get("generation", 0))

with col2:
    st.metric("Cycle", metrics.get("cycle", 0))

with col3:
    st.metric("Current Level", metrics.get("level", 0))

with col4:
    st.metric("ECM Score", f"{metrics.get('ecm_score', 0):.4f}")

with col5:
    alive_emoji = "✅" if metrics.get("is_alive", False) else "💀"
    st.metric("Alive", alive_emoji)

# Detailed metrics
st.subheader("📊 Universe Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Particle Count", metrics.get("particle_count", 0))

with col2:
    st.metric("Energy Level", f"{metrics.get('energy', 0):.2f}")

with col3:
    st.metric("Complexity Score", f"{metrics.get('complexity', 0):.4f}")

# History statistics
st.subheader("📈 Historical Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Cycles", history.get("total_cycles", 0))

with col2:
    st.metric("Successful", history.get("successful", 0))

with col3:
    st.metric("Failed", history.get("failed", 0))

with col4:
    success_rate = history.get("success_rate", 0.0)
    st.metric("Success Rate", f"{success_rate:.1f}%")

# Garden of Worlds (Timeline)
st.subheader("🌌 Garden of Worlds")

timeline = history.get("timeline_recent", [])
if timeline:
    # Visual representation
    symbols = []
    for entry in timeline:
        if entry == "SUCCESS":
            symbols.append("🟢")
        else:
            symbols.append("⚫")

    st.markdown(" ".join(symbols))
    st.caption(f"Last {len(timeline)} attempts (🟢 = Success, ⚫ = Failure)")
else:
    st.info("No attempts yet. Start the simulation to see the garden grow.")

# ECM Score chart (if there are successful universes)
st.subheader("📊 ECM Evolution")

if history.get("successful", 0) > 0:
    # In a real implementation, we'd plot the ECM scores over generations
    # For now, show key metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Highest Generation", history.get("current_generation", 1))

    with col2:
        st.metric("Highest ECM Score", f"{history.get('highest_ecm', 0):.4f}")

    st.info("📊 Full ECM chart coming soon! (Requires historical data storage)")
else:
    st.info("No successful universes yet. Keep running the simulation!")

# Configuration display
with st.expander("🔧 Current Configuration"):
    config = status.get("config", {})
    st.json(config)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    time.sleep(2)
    st.rerun()
