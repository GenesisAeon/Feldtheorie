"""
Ouroboros Control Dashboard
============================

Streamlit-based interactive dashboard for controlling and visualizing
the eternal cosmic loop simulation.

Features:
---------
- Real-time status monitoring
- Visual timeline (Garden of Worlds)
- Control panel (start/pause/resume/stop/reset)
- God-mode interventions
- ECM score tracking
- Success rate visualization

Usage:
------
streamlit run src/interface/dashboard.py

Make sure the API server is running first:
python -m src.interface.api_server
"""

import time
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════

API_URL = "http://localhost:8000"
REFRESH_INTERVAL = 2  # seconds

# Page configuration
st.set_page_config(
    page_title="Ouroboros Control",
    layout="wide",
    page_icon="♾️",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-badge {
        color: #28a745;
        font-weight: bold;
    }
    .fail-badge {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════

def check_api_connection() -> bool:
    """Check if API server is reachable."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_simulation_state() -> dict[str, Any]:
    """Fetch current simulation state from API."""
    try:
        response = requests.get(f"{API_URL}/api/ouroboros/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Failed to fetch state: {e}")
        return {}


def get_history() -> list[dict[str, Any]]:
    """Fetch complete history from API."""
    try:
        response = requests.get(f"{API_URL}/api/ouroboros/history", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def send_command(endpoint: str, data: dict = None) -> dict[str, Any]:
    """Send command to API."""
    try:
        if data:
            response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        else:
            response = requests.post(f"{API_URL}{endpoint}", timeout=5)

        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def format_state_emoji(state: str) -> str:
    """Get emoji for simulation state."""
    emoji_map = {
        "idle": "⏹️",
        "running": "▶️",
        "paused": "⏸️",
        "completed": "✅",
        "failed": "❌"
    }
    return emoji_map.get(state, "❓")


def format_result_emoji(result: str) -> str:
    """Get emoji for generation result."""
    return "🟢" if result == "SUCCESS" else "⚫"


# ═══════════════════════════════════════════════════════════
# Main Dashboard
# ═══════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown('<h1 class="main-header">♾️ OUROBOROS CONTROL CENTER</h1>', unsafe_allow_html=True)
    st.markdown("### *The God-Mode Dashboard for the Eternal Cosmic Loop*")
    st.markdown("---")

    # Check API connection
    if not check_api_connection():
        st.error("🔴 **Cannot connect to Ouroboros API Server**")
        st.info("Please start the API server first:")
        st.code("python -m src.interface.api_server", language="bash")
        st.stop()

    # ═══════════════════════════════════════════════════════════
    # Sidebar - Control Panel
    # ═══════════════════════════════════════════════════════════

    with st.sidebar:
        st.header("🎛️ Control Panel")
        st.markdown("---")

        # Main controls
        st.subheader("Simulation Control")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("▶️ START", use_container_width=True):
                result = send_command("/api/ouroboros/start")
                if result.get("status") == "started":
                    st.success("Simulation started!")
                else:
                    st.info(result.get("message", "Already running"))

            if st.button("⏸️ PAUSE", use_container_width=True):
                result = send_command("/api/ouroboros/pause")
                st.info(result.get("message", "Paused"))

        with col2:
            if st.button("⏯️ RESUME", use_container_width=True):
                result = send_command("/api/ouroboros/resume")
                st.info(result.get("message", "Resumed"))

            if st.button("🛑 STOP", use_container_width=True):
                result = send_command("/api/ouroboros/stop")
                st.warning(result.get("message", "Stopped"))

        if st.button("🔄 RESET TO GEN 1", use_container_width=True, type="primary"):
            result = send_command("/api/ouroboros/reset")
            st.success(result.get("message", "Reset"))

        st.markdown("---")

        # God-Mode Interventions
        st.subheader("⚡ God-Mode Interventions")

        intervention_type = st.selectbox(
            "Intervention Type",
            ["mutation_rate", "energy_injection", "mutation_boost"],
            format_func=lambda x: {
                "mutation_rate": "🧬 Set Mutation Rate",
                "energy_injection": "⚡ Energy Injection",
                "mutation_boost": "🚀 Mutation Boost"
            }[x]
        )

        if intervention_type == "mutation_rate":
            value = st.slider("Mutation Rate", 0.0, 1.0, 0.1, 0.01)
        elif intervention_type == "energy_injection":
            value = st.slider("Energy Boost", 0.0, 0.5, 0.1, 0.01)
        else:  # mutation_boost
            value = st.slider("Boost Percentage", 0.0, 1.0, 0.2, 0.05)

        if st.button("⚡ APPLY INTERVENTION", use_container_width=True):
            result = send_command(
                "/api/ouroboros/intervene",
                {"type": intervention_type, "value": value}
            )
            if result.get("status") == "success":
                st.success(result.get("message", "Applied!"))
            else:
                st.error(result.get("message", "Failed"))

        st.markdown("---")
        st.caption("Dashboard updates every 2 seconds")

    # ═══════════════════════════════════════════════════════════
    # Main Content - Status Display
    # ═══════════════════════════════════════════════════════════

    # Create placeholders for auto-refresh
    status_placeholder = st.empty()
    metrics_placeholder = st.empty()
    charts_placeholder = st.empty()
    history_placeholder = st.empty()

    # Auto-refresh loop
    while True:
        # Fetch current state
        state = get_simulation_state()

        if not state:
            st.error("Failed to fetch simulation state")
            time.sleep(REFRESH_INTERVAL)
            continue

        # ═══════════════════════════════════════════════════════════
        # Status Section
        # ═══════════════════════════════════════════════════════════

        with status_placeholder.container():
            st.markdown("### 📊 Current Status")

            state_emoji = format_state_emoji(state.get("state", "idle"))
            st.info(f"{state_emoji} **{state.get('status_message', 'Unknown')}**")

        # ═══════════════════════════════════════════════════════════
        # Metrics Section
        # ═══════════════════════════════════════════════════════════

        with metrics_placeholder.container():
            st.markdown("### 🔢 Universe Metrics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Generation",
                    f"#{state.get('generation', 0)}",
                    delta=f"Cycle {state.get('current_cycle', 0)}"
                )

            with col2:
                ecm = state.get('ancestor_ecm', 0.0)
                st.metric(
                    "Ancestor ECM",
                    f"{ecm:.4f}",
                    delta=f"Peak: {state.get('highest_ecm', 0.0):.4f}"
                )

            with col3:
                success_rate = state.get('success_rate', 0.0)
                st.metric(
                    "Success Rate",
                    f"{success_rate:.1%}",
                    delta=f"{state.get('successful_generations', 0)}/{state.get('total_generations', 0)}"
                )

            with col4:
                mutation = state.get('mutation_rate', 0.0)
                failures = state.get('consecutive_failures', 0)
                st.metric(
                    "Mutation Rate",
                    f"{mutation:.4f}",
                    delta=f"{failures} failures" if failures > 0 else "Stable",
                    delta_color="inverse" if failures > 2 else "normal"
                )

        # ═══════════════════════════════════════════════════════════
        # Charts Section
        # ═══════════════════════════════════════════════════════════

        with charts_placeholder.container():
            st.markdown("### 📈 Evolution Tracking")

            history = get_history()

            if history and len(history) > 1:
                # Prepare data
                df = pd.DataFrame(history)

                col1, col2 = st.columns(2)

                with col1:
                    # ECM Score over time
                    fig_ecm = go.Figure()

                    # Separate successful and failed generations
                    df_success = df[df['result'] == 'SUCCESS']
                    df_fail = df[df['result'] == 'FAILED']

                    if not df_success.empty:
                        fig_ecm.add_trace(go.Scatter(
                            x=df_success['generation'],
                            y=df_success['ecm_score'],
                            mode='lines+markers',
                            name='Successful',
                            line=dict(color='green', width=2),
                            marker=dict(size=8)
                        ))

                    if not df_fail.empty:
                        fig_ecm.add_trace(go.Scatter(
                            x=df_fail['generation'],
                            y=df_fail['ecm_score'],
                            mode='markers',
                            name='Failed',
                            marker=dict(color='red', size=6, symbol='x')
                        ))

                    fig_ecm.update_layout(
                        title="ECM Score Evolution",
                        xaxis_title="Generation",
                        yaxis_title="ECM Score",
                        height=300,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig_ecm, use_container_width=True)

                with col2:
                    # Success/Failure distribution
                    result_counts = df['result'].value_counts()

                    fig_pie = go.Figure(data=[go.Pie(
                        labels=result_counts.index,
                        values=result_counts.values,
                        marker=dict(colors=['green', 'red'])
                    )])

                    fig_pie.update_layout(
                        title="Universe Outcomes",
                        height=300
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)

        # ═══════════════════════════════════════════════════════════
        # History Section - Garden of Worlds
        # ═══════════════════════════════════════════════════════════

        with history_placeholder.container():
            st.markdown("### 🌳 Garden of Worlds")
            st.caption("Timeline of all universe generations")

            history = get_history()

            if history:
                # Display recent history as timeline
                recent = history[-20:]  # Last 20 generations

                timeline_str = ""
                for entry in recent:
                    gen = entry['generation']
                    result = entry['result']
                    ecm = entry.get('ecm_score', 0.0)
                    emoji = format_result_emoji(result)

                    if result == "SUCCESS":
                        timeline_str += f"{emoji} **Gen {gen}** (ECM: {ecm:.3f}) • "
                    else:
                        timeline_str += f"{emoji} Gen {gen} • "

                st.markdown(timeline_str)

                # Detailed history table (expandable)
                with st.expander("📜 Full History Table"):
                    df_history = pd.DataFrame(history)

                    # Format timestamp
                    if 'timestamp' in df_history.columns:
                        df_history['time'] = pd.to_datetime(
                            df_history['timestamp'], unit='s'
                        ).dt.strftime('%H:%M:%S')

                    # Select and rename columns
                    display_cols = ['generation', 'result', 'ecm_score']
                    if 'time' in df_history.columns:
                        display_cols.append('time')

                    st.dataframe(
                        df_history[display_cols],
                        use_container_width=True,
                        hide_index=True
                    )

            else:
                st.info("No generations yet. Start the simulation to begin!")

        # Sleep before next refresh
        time.sleep(REFRESH_INTERVAL)


# ═══════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
