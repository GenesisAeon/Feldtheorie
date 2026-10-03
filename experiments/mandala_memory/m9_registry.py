"""M9: register of what has already been SEEN and the held-out grid.

No kernel import (only plain data). 'Seen' = a combination whose memory curve
or duration has been looked at before the freeze:

- the benchmark (M3/M4) and its M6 comparison networks (same knobs);
- the throw-away knob scan before M8 (ROADMAP "Explorative Vorerfahrung");
- the development combinations of tests/test_m9_predict.py;
- every 'lab' entry in explore/protocol.jsonl (read at freeze time).

The held-out grid uses for c, gamma, ell, amplitude and sigma ONLY values that
occur in none of the seen combinations, so every held-out combination differs
from every seen one in all five continuous knobs (checked in m9_freeze)."""
from __future__ import annotations

BENCHMARK = {"N": 12, "M": 3, "c": 0.25, "gamma": 0.8, "ell": 0.5, "amplitude": 0.6, "sigma": 0.02, "inputs": [0, 4],
             "readout": "full", "readout_node": 0, "nonlinearity": "tanh"}
B = BENCHMARK

SEEN_PRE_M8 = [
    B, {**B, "gamma": 0.95}, {**B, "gamma": 0.5}, {**B, "ell": 0.25}, {**B, "ell": 0.9}, {**B, "c": 0.05},
    {**B, "c": 0.5}, {**B, "amplitude": 1.2}, {**B, "inputs": [0, 1]}, {**B, "M": 1, "c": None},
]

DEV_COMBOS = SEEN_PRE_M8 + [
    {**B, "readout": "module_means"}, {**B, "readout": "sum"}, {**B, "readout": "node", "readout_node": 0},
    {**B, "readout": "node", "readout_node": 5}, {**B, "amplitude": 3.0, "ell": 1.0, "gamma": 0.95, "c": 0.0},
    {**B, "N": 24, "M": 12, "c": 0.05, "inputs": [3, 10], "readout": "module_means"},
    {**B, "N": 6, "M": 3, "c": 1.0, "inputs": [1, 4], "sigma": 0.05},
    {**B, "N": 18, "M": 2, "c": 0.5, "gamma": 0.95, "inputs": [2, 15], "readout": "node", "readout_node": 15, "amplitude": 3.0},
    {**B, "N": 18, "M": 9, "ell": 1.0, "inputs": [4, 5], "amplitude": 1.2},
    {**B, "nonlinearity": "identity", "amplitude": 3.0},
]

CONTINUOUS = ("c", "gamma", "ell", "amplitude", "sigma")

HELD_OUT_GRID = {
    "N": [12, 18, 24],
    "c": [0.1, 0.15, 0.35, 0.6, 0.8],
    "gamma": [0.6, 0.7, 0.85, 0.9],
    "ell": [0.3, 0.4, 0.6, 0.75],
    "amplitude": [0.3, 0.9, 1.6, 2.4],
    "sigma": [0.01, 0.015, 0.03],
}
HELD_OUT_PER_READOUT = 6
HELD_OUT_READOUTS = ("full", "module_means", "node", "sum")
DRAW_SEED = 202610039

__all__ = ["BENCHMARK", "SEEN_PRE_M8", "DEV_COMBOS", "CONTINUOUS", "HELD_OUT_GRID", "HELD_OUT_PER_READOUT",
           "HELD_OUT_READOUTS", "DRAW_SEED"]
