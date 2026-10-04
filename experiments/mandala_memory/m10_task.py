"""M10: memory under distraction -- task definition (docs/M10_PLAN_ABLENKUNG.md, Fassung 2).

Episode (delay d, window W = 3 directly before the readout):
    x_0 = 0; step 0: target pulse e_s (s = A at node 0, B at node 4, amplitude a);
    steps 1 .. d-3: zero; steps d-2 .. d: window, each step independently with
    p = 1/2 a pulse on distractor channel X or Y (1/4 each), otherwise zero;
    readout x_(d+1); observation y = x_(d+1) + eps, eps ~ N(0, sigma^2 I).

There are 27 window patterns pi in {0 (none), 1 (X), 2 (Y)}^3 with known
probabilities. For a fixed network the readout state z(s, pi) is deterministic,
so every class-conditional distribution is EXACTLY a finite Gaussian mixture
(level B, m10_bayes.py). All states come from the tested kernel
(core.EpisodeOperator); no second dynamics implementation.
"""
from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from experiments.mandala_memory.core import EpisodeOperator, MemoryLabError, NetworkSpec, build_network

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol" / "m10_protokoll.json"
W = 3
NONE, X, Y = 0, 1, 2


def load_protocol(path: Path = PROTOCOL) -> Dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --- window patterns ----------------------------------------------------------
def patterns(p_pulse: Fraction = Fraction(1, 2)) -> List[Tuple[Tuple[int, ...], Fraction]]:
    """All 27 patterns with exact probabilities; slot order = time order."""
    q = {NONE: 1 - p_pulse, X: p_pulse / 2, Y: p_pulse / 2}
    out = []
    for pat in itertools.product((NONE, X, Y), repeat=W):
        pr = Fraction(1)
        for v in pat:
            pr *= q[v]
        out.append((pat, pr))
    assert sum(pr for _, pr in out) == 1
    return out


def last_channel(pat) -> Optional[int]:
    for v in reversed(pat):
        if v != NONE:
            return v
    return None


# --- networks -----------------------------------------------------------------
def network(proto: Dict, name: str, nonlinearity: str, condition: Optional[Dict]) -> NetworkSpec:
    """Fixed network (no Hebb) with 4 input columns: target A, target B, X, Y.
    'modular' and 'uniform' share N, gamma (row sums), ell, inputs and amplitudes."""
    base = proto["network"]
    shape = proto["networks"][name]
    spec = build_network(N=base["N"], M=shape["M"], c=shape.get("c", 0.25), gamma=base["gamma"], ell=base["ell"],
                         inputs=tuple(base["inputs"]), amplitude=base["amplitude"], nonlinearity=nonlinearity,
                         name=f"m10_{name}_{nonlinearity}")
    B = np.zeros((base["N"], 4))
    B[:, :2] = spec.B
    if condition is not None:
        B[condition["X"], 2] = condition["amplitude"]
        B[condition["Y"], 3] = condition["amplitude"]
    return NetworkSpec(spec.A, B, spec.ell, nonlinearity, spec.name, spec.module_of, spec.mask,
                       {**spec.meta, "distractor": condition})


def input_sequence(s: int, pat, d: int) -> List[np.ndarray]:
    """u_0 .. u_d for target class s (0 = A, 1 = B) and window pattern pat."""
    if d < W:
        raise MemoryLabError(f"delay d must be >= W = {W}")
    seq = [np.eye(4)[s]]
    for k in range(1, d + 1):
        u = np.zeros(4)
        slot = k - (d - W + 1)
        if 0 <= slot < W and pat[slot] != NONE:
            u[1 + pat[slot]] = 1.0          # X -> column 2, Y -> column 3
        seq.append(u)
    return seq


def trajectory(spec: NetworkSpec, s: int, pat, d: int) -> np.ndarray:
    op = EpisodeOperator(spec)
    op.reset()
    return op.run(input_sequence(s, pat, d))          # (d + 2, N): x_0 .. x_(d+1)


def readout_states(spec: NetworkSpec, d: int, pats) -> np.ndarray:
    """z[s, i] = x_(d+1) for class s and pattern pats[i]; shape (2, len(pats), N)."""
    return np.array([[trajectory(spec, s, pat, d)[-1] for pat, _ in pats] for s in (0, 1)])


# --- symmetry (A1, A2) --------------------------------------------------------
def swap_permutation(N: int, M: int, i: int = 0, j: int = 4) -> List[int]:
    """Involution exchanging the two target inputs (M9 derivation, section 5)."""
    from experiments.mandala_memory.predict import symmetry_permutation

    return symmetry_permutation(N, M, i, j)


def condition_is_p_fixed(perm: List[int], condition: Optional[Dict]) -> bool:
    return condition is None or (perm[condition["X"]] == condition["X"] and perm[condition["Y"]] == condition["Y"])


def check_a1(spec: NetworkSpec, perm: List[int], d: int, pats, tol_rel: float) -> Dict:
    """A1: x_B(k) = P x_A(k) for every k and every pattern (same pattern for both)."""
    worst = 0.0
    for pat, _ in pats:
        xa, xb = trajectory(spec, 0, pat, d), trajectory(spec, 1, pat, d)
        scale = max(float(np.max(np.abs(xa))), 1e-300)
        worst = max(worst, float(np.max(np.abs(xb - xa[:, perm]))) / scale)
    return {"max_rel_deviation": float(worst), "holds": bool(worst <= tol_rel), "tol_rel": tol_rel}


def check_a2_structural(z: np.ndarray, pats, perm: List[int], tol: float) -> Dict:
    """A2 (linear twin): r(pi) = z(s, pi) - z(s, none) lies in V+ (P-symmetric), i.e.
    ||P_- r|| <= tol with P_- = (I - P)/2, for both classes."""
    none = next(i for i, (p, _) in enumerate(pats) if all(v == NONE for v in p))
    worst = 0.0
    for s in (0, 1):
        for i in range(len(pats)):
            r = z[s, i] - z[s, none]
            worst = max(worst, float(np.linalg.norm((r - r[perm]) / 2)))
    return {"max_norm_antisymmetric_part": float(worst), "holds": bool(worst <= tol), "tol": tol}


__all__ = ["load_protocol", "patterns", "last_channel", "network", "input_sequence", "trajectory",
           "readout_states", "swap_permutation", "condition_is_p_fixed", "check_a1", "check_a2_structural", "W"]
