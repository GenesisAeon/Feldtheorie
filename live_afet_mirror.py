"""AFET Living Mirror — Streamlit Entry Point.

Launch with:
    streamlit run live_afet_mirror.py

Displays a real-time, self-observing dashboard of the AFET field state,
including the Profiling-Tafel, consciousness score, and 13.5 MHz
resonance indicator.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from visuals.profiling.live_dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()
else:
    # Streamlit executes the module directly (not via __main__)
    run_dashboard()
