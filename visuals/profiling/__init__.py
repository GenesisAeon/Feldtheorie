"""AFET Visual Profiling Hub — Quad-Layer Component 4.

Generates spatial/topological snapshots of the AFET field state.
"""

from .profiling_generator import FieldMetrics, ProfilingGenerator, load_symbols

__all__ = [
    "FieldMetrics",
    "ProfilingGenerator",
    "compute_consciousness_score",
    "load_symbols",
    "run_dashboard",
]


def __getattr__(name: str):
    """Lazy-import streamlit-dependent symbols to avoid hard dependency."""
    if name in ("compute_consciousness_score", "run_dashboard"):
        from .live_dashboard import compute_consciousness_score, run_dashboard

        globals()["compute_consciousness_score"] = compute_consciousness_score
        globals()["run_dashboard"] = run_dashboard
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
