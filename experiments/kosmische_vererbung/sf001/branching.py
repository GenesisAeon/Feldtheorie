"""Multi-type branching populations for SF-001 (package V2, roadmap S00/S01).

Explicitly artificial reproduction rule (plan §7): an individual of type i has
Poisson(b_i) offspring; each offspring independently gets type j with
probability M[j, i]. M is column-stochastic (columns = parent type).

Two layers:

* exact expected operator  n_{g+1} = M diag(b) n_g  and the deterministic
  frequency recursion (pure Python, works with ``fractions.Fraction``);
* a stochastic, count-based simulator with a population cap, an explicit
  extinction rule and founder lineages.

Nothing here is astrophysics. Types are abstract labels; a "universe" is an
individual of the model population.
"""
from __future__ import annotations

import math
from fractions import Fraction
from numbers import Real

import numpy as np

EXTINCTION_RULE = (
    "Eine Population mit 0 Individuen ist ausgestorben. Sie bleibt ausgestorben; "
    "Neustarts sind nicht erlaubt (restarts = 0)."
)


def validate_model(M, b, tol: float = 1e-12) -> int:
    """Check that M is square and column-stochastic and b is finite, >= 0."""

    K = len(M)
    if K == 0 or any(len(row) != K for row in M):
        raise ValueError("M must be a non-empty square matrix")
    if len(b) != K:
        raise ValueError("b must have one entry per type")
    exact = all(isinstance(x, (int, Fraction)) for row in M for x in row)
    for value in [x for row in M for x in row]:
        if not isinstance(value, Real) or not math.isfinite(value) or value < 0:
            raise ValueError("M entries must be finite and >= 0")
    for i in range(K):
        col = sum(M[j][i] for j in range(K))
        if (col != 1) if exact else abs(col - 1) > tol:
            raise ValueError(f"column {i} of M sums to {col}, not 1")
    for value in b:
        if not isinstance(value, Real) or not math.isfinite(value) or value < 0:
            raise ValueError("b entries must be finite and >= 0")
    return K


def expected_step(M, b, n):
    """Expected type counts of the next generation: M diag(b) n."""

    K = validate_model(M, b)
    if len(n) != K:
        raise ValueError("n must have one entry per type")
    return [sum(M[j][i] * b[i] * n[i] for i in range(K)) for j in range(K)]


def frequency_step(M, b, p):
    """Deterministic frequency recursion; ``None`` if the population dies out.

    No normalisation by zero and no apparent stationary state after extinction.
    """

    numerator = expected_step(M, b, p)
    denominator = sum(numerator)
    if denominator == 0:
        return None
    return [x / denominator for x in numerator]


def mutation_matrix(K: int, mu: float) -> np.ndarray:
    """Nearest-neighbour mutation with probability mu (reflecting ends)."""

    if not 0 <= mu <= 1:
        raise ValueError("mu must lie in [0, 1]")
    M = np.zeros((K, K))
    for i in range(K):
        M[i, i] = 1 - mu
        neighbours = [j for j in (i - 1, i + 1) if 0 <= j < K]
        for j in neighbours:
            M[j, i] += mu / len(neighbours)
    return M


def erasure_matrix(pi) -> np.ndarray:
    """M = pi 1^T: the offspring type ignores the parent type."""

    pi = np.asarray(pi, dtype=float)
    return np.outer(pi, np.ones(len(pi)))


def simulate(M, b, founders, generations: int, cap: int | None, seed) -> dict:
    """Run one stochastic population.

    founders: number of founders per type. Every founder starts its own
    lineage; lineages are laid out canonically by type, so the result depends
    only on the counts, never on a list order.

    cap: if the offspring generation exceeds ``cap`` individuals, ``cap`` of
    them survive, drawn uniformly without replacement (multivariate
    hypergeometric over lineage x type counts). ``None`` = no cap.

    seed: anything accepted by ``numpy.random.default_rng``.
    """

    M = np.asarray(M, dtype=float)
    b = np.asarray(b, dtype=float)
    validate_model(M.tolist(), b.tolist())
    founders = [int(x) for x in founders]
    if len(founders) != len(b) or min(founders) < 0:
        raise ValueError("founders must be one non-negative count per type")
    if generations < 0 or (cap is not None and cap < 1):
        raise ValueError("generations >= 0 and cap >= 1 (or None)")

    K = len(b)
    lineage_type = [t for t in range(K) for _ in range(founders[t])]
    F = len(lineage_type)
    state = np.zeros((F, K), dtype=np.int64)
    state[np.arange(F), lineage_type] = 1

    rng = np.random.default_rng(seed)
    type_counts = [state.sum(axis=0).tolist()]
    lineages_alive = [int((state.sum(axis=1) > 0).sum())]
    individual_generations = 0
    extinct_generation = 0 if F == 0 else None
    cap_events = 0

    for g in range(1, generations + 1):
        if extinct_generation is not None:
            type_counts.append([0] * K)
            lineages_alive.append(0)
            continue
        individual_generations += int(state.sum())
        offspring = rng.poisson(state * b[None, :])
        new = np.zeros_like(state)
        for f, i in np.argwhere(offspring):  # row-major, i.e. canonical order
            new[f] += rng.multinomial(int(offspring[f, i]), M[:, i])
        total = int(new.sum())
        if cap is not None and total > cap:
            new = rng.multivariate_hypergeometric(new.ravel(), cap).reshape(F, K)
            cap_events += 1
        state = new
        type_counts.append(state.sum(axis=0).tolist())
        lineages_alive.append(int((state.sum(axis=1) > 0).sum()))
        if state.sum() == 0:
            extinct_generation = g

    return {
        "type_counts": type_counts,
        "lineages_alive": lineages_alive,
        "extinct_generation": extinct_generation,
        "restarts": 0,
        "individual_generations": individual_generations,
        "cap_events": cap_events,
    }
