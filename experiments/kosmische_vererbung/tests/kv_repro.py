"""Comparison contract for re-simulated V5/V5c runs against committed raw series.

Two levels (Astra review ASTRA-2026-10-12-03, C5):

1. Bit identity, only in the environment recorded in raw.json["provenance"]
   (python, numpy, scipy). Elsewhere the bit test is skipped visibly with the reason.
2. A narrow per-quantity comparison that runs everywhere.

Exact everywhere: the set of series keys, all lengths (also nested), the time axis
``t`` and the discrete count ``event_splits``. Every value must be finite.

Tolerances. Astra measured under Python 3.12.14 / NumPy 2.2.6 / SciPy 1.15.3 at most
(each deviation divided by the largest absolute value of its series):
mean_Z 3.1e-17 abs on max 0.017 (1.8e-15), gas_mass 2.1e-9 Msun on 2e6 (1.0e-15),
f_primordial_origin 6.1e-16 abs on 0.5 (1.2e-15), budget_rel_error 1.2e-16 abs (V5c).
Emulating the compensated float ``sum()`` of Python 3.12 under 3.11 (``neumaier_sum``)
reproduces exactly Astra's V5 deviations and additionally gives zone_Z 2.6e-15 scaled and
budget_rel_error 8.2e-16 abs. Scaled quantities therefore get 1e-13 times the largest
absolute value of the committed series (about 40-100x the largest observed deviation),
budget_rel_error gets 1e-13 absolute (about 100x; it is itself a rounding residue and stays
four orders of magnitude below the balance tolerance 1e-9 of both protocols). 1e-13 relative on
mean_Z moves r = (Z_A - Z_B)/Z_B by at most about 2e-13, below the strictest protocol
criterion (L: |r| <= 1e-12) and nine orders of magnitude below atol_r = 1e-4 of V5c.
The scientific convergence criteria of the protocols are not touched here.
"""
from __future__ import annotations

import math
import platform

import numpy
import scipy

SCALED_RTOL = 1e-13
SCALED = ("mean_Z", "zone_Z", "gas_mass", "f0", "f_primordial_origin", "pop3_mass_formed", "synthesized_O")
ABSOLUTE = {"budget_rel_error": 1e-13}
EXACT = ("t", "event_splits")


def environment() -> dict:
    return {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__}


def environment_mismatch(provenance: dict) -> str | None:
    """None if this is the environment recorded with the run, otherwise the reason."""
    here = environment()
    diff = [f"{k} {provenance.get(k)} (Lauf) != {here[k]} (hier)" for k in ("python", "numpy", "scipy") if provenance.get(k) != here[k]]
    if not diff:
        return None
    return "Bitgleichheit nur in der Originalumgebung des Laufs zugesagt: " + "; ".join(diff)


def _flatten(x, path):
    if isinstance(x, list):
        for i, v in enumerate(x):
            yield from _flatten(v, path + (i,))
    else:
        yield path, x


def _shape(x):
    return [_shape(v) for v in x] if isinstance(x, list) else None


def compare_series(new: dict, committed: dict) -> list[str]:
    """Return the list of violations (empty means the re-simulation matches)."""
    problems = []
    known = set(SCALED) | set(ABSOLUTE) | set(EXACT)
    if set(new) != set(committed):
        problems.append(f"keys differ: {sorted(set(new) ^ set(committed))}")
    for key in sorted(set(new) & set(committed)):
        if key not in known:
            problems.append(f"{key}: no comparison rule declared")
            continue
        a, b = new[key], committed[key]
        if _shape(a) != _shape(b):
            problems.append(f"{key}: shape differs")
            continue
        flat_a, flat_b = list(_flatten(a, ())), list(_flatten(b, ()))
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for _, v in flat_a + flat_b):
            problems.append(f"{key}: non-finite or non-numeric value")
            continue
        if key in EXACT:
            if a != b:
                problems.append(f"{key}: must match exactly")
            continue
        if key in ABSOLUTE:
            tol = ABSOLUTE[key]
        else:
            tol = SCALED_RTOL * max((abs(v) for _, v in flat_b), default=0.0)
        worst = max((abs(va - vb) for (_, va), (_, vb) in zip(flat_a, flat_b)), default=0.0)
        if worst > tol:
            problems.append(f"{key}: max deviation {worst:.3e} > tolerance {tol:.3e}")
    return problems


def neumaier_sum(iterable, start=0):
    """Emulation of the compensated float sum() of CPython 3.12 (Neumaier), for tests only.

    Compensates while the running sum and the items are exact Python floats; other types
    (ints, NumPy scalars) are added plainly, as in CPython's generic path.
    """
    s, c, comp = start, 0.0, False
    for x in iterable:
        if type(x) is float and (type(s) is float or (type(s) is int and not comp)):
            s, comp = float(s), True
            t = s + x
            c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
            s = t
        else:
            if comp:
                s, c, comp = s + c, 0.0, False
            s = s + x
    return s + c if comp else s
