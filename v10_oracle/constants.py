"""GenesisAeon v10.0 constants (Zenodo record 17969457).

These anchors express the hexadecimal signature (1/16) and the minimal
entropy-verschnitt tolerances the Crystal Answer pursues.
"""

HEX_SIG_PHI: float = 1 / 16  # 0.0625 — the target volatility edge
ENTROPY_OFFSET_TOLERANCE: float = 0.005  # breathing room around the edge
DIMENSIONAL_WASTE_FACTOR: float = 0.137  # thermodynamic inefficiency constant

__all__ = [
    "HEX_SIG_PHI",
    "ENTROPY_OFFSET_TOLERANCE",
    "DIMENSIONAL_WASTE_FACTOR",
]
