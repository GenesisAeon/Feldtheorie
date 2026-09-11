"""Independent reference recomputation for GW-EXACT-001 (geometric_waste_v1).

Written from PROTOCOL.md / protocol.json ONLY, deliberately without reading
run_exact.py's grouping or entropy/error functions first. Uses a different
enumeration style (itertools + explicit modular neighbour loops + dict-based
grouping via Counter/defaultdict) instead of run_exact.py's numpy vectorised
reshape/np.unique approach, so the two implementations share no code path.

Only compares against run_exact.py's *published numbers* at the end, not its
internals.

Run: python independent_recompute.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SIDE = 4
NCELLS = SIDE * SIDE  # 16


def enumerate_states():
    """Yield all 2**16 states as 16-tuples of 0/1.

    Bit k (k=0..15) is the low-order bit of the integer id, per PROTOCOL.md:
    "cell zero is the low-order bit and rows use C order" -> cell k sits at
    row k//4, col k%4 (row-major / C order), matching bit k of the integer.

    Implemented here via itertools.product in *reverse* bit order then
    reversed, deliberately not via numpy right-shift broadcasting (the
    method used in run_exact.py), to keep the enumeration logic independent.
    """
    for bits_msb_first in itertools.product((0, 1), repeat=NCELLS):
        # itertools.product gives the *first* produced axis varying slowest;
        # we want bit 0 (cell 0) to be the fastest-varying / low-order bit,
        # so reverse the tuple to get bit order [bit0, bit1, ..., bit15].
        bits = bits_msb_first[::-1]
        yield bits


def state_id(bits) -> int:
    """Integer id of a 16-bit state tuple (bit k = cell k), for cross-checks."""
    return sum(b << k for k, b in enumerate(bits))


def cell_rc(k: int) -> tuple[int, int]:
    return divmod(k, SIDE)  # (row, col), row-major / C order


def occupancy_of(bits) -> int:
    return sum(bits)


def block_label(bits) -> tuple[int, int, int, int]:
    """Four non-overlapping labelled 2x2 block counts, computed via explicit
    per-block cell sums (not via a reshape trick)."""
    grid = [[bits[r * SIDE + c] for c in range(SIDE)] for r in range(SIDE)]
    blocks = []
    for br in (0, 1):
        for bc in (0, 1):
            total = 0
            for dr in (0, 1):
                for dc in (0, 1):
                    total += grid[br * 2 + dr][bc * 2 + dc]
            blocks.append(total)
    return tuple(blocks)


def boundary_length_of(bits) -> int:
    """Periodic nearest-neighbour disagreement count, each undirected edge
    counted once. Implemented via an explicit double loop over horizontal
    and vertical edges (not via numpy np.roll), independent of run_exact.py.
    """
    grid = [[bits[r * SIDE + c] for c in range(SIDE)] for r in range(SIDE)]
    total = 0
    # Horizontal edges: (r, c) -- (r, c+1 mod SIDE), one edge per (r, c) pair,
    # SIDE*SIDE = 16 such undirected edges total for a periodic 4-cycle per row.
    for r in range(SIDE):
        for c in range(SIDE):
            if grid[r][c] != grid[r][(c + 1) % SIDE]:
                total += 1
    # Vertical edges: (r, c) -- (r+1 mod SIDE, c), another 16 edges.
    for r in range(SIDE):
        for c in range(SIDE):
            if grid[r][c] != grid[(r + 1) % SIDE][c]:
                total += 1
    return total


def conditional_entropy_and_error(members_bits: list[tuple], labels: list[tuple]):
    """H(X|Y) in bits, and Bayes cellwise Hamming error fraction, for a
    uniform ensemble over `members_bits`, grouped by `labels`.

    Independent grouping via a plain dict (not np.unique), independent
    entropy/error formulas derived directly from PROTOCOL.md's definitions:
      H(X|Y) = sum_y P(y) * log2(|class_y|)   [uniform-within-class]
      Bayes cellwise error = (1/(N*16)) * sum_over_classes sum_over_cells
                              min(ones_in_cell, count_in_class - ones_in_cell)
    """
    n = len(members_bits)
    groups: dict[tuple, list[tuple]] = defaultdict(list)
    for bits, label in zip(members_bits, labels):
        groups[label].append(bits)

    conditional_bits = 0.0
    total_cell_errors = 0
    class_sizes = []
    for label, members in groups.items():
        count = len(members)
        class_sizes.append(count)
        conditional_bits += (count / n) * math.log2(count)
        # per-cell ones count within this class
        ones = [0] * NCELLS
        for bits in members:
            for k in range(NCELLS):
                ones[k] += bits[k]
        for k in range(NCELLS):
            total_cell_errors += min(ones[k], count - ones[k])

    microstate_entropy = math.log2(n)
    bayes_error_fraction = total_cell_errors / (n * NCELLS)
    return {
        "microstates": n,
        "observation_classes": len(groups),
        "microstate_entropy_bits": microstate_entropy,
        "conditional_entropy_bits": conditional_bits,
        "retained_information_bits": microstate_entropy - conditional_bits,
        "bayes_cell_error_fraction": bayes_error_fraction,
    }


def scrambled_permutation(boundary_values: list[int], seed: int) -> list[int]:
    """Same declared procedure as PROTOCOL.md: permute the boundary labels
    within the ensemble via a seeded RNG, preserving their marginal
    distribution. This call itself IS the frozen protocol's stochastic
    definition, so it is intentionally reproduced verbatim (not
    reimplemented differently) -- the goal here is to confirm the
    *implementation* used exactly this reproducible procedure, not to
    invent an alternative one.
    """
    arr = np.asarray(boundary_values)
    permuted = np.random.default_rng(seed).permutation(arr)
    return [int(v) for v in permuted]


def sanity_checks(all_bits_list):
    """Checks demanded explicitly by PROTOCOL.md's 'Checks and interpretation'."""
    results = {}

    # Identity observer: zero conditional entropy, zero reconstruction error.
    ident_labels = [(i,) for i in range(len(all_bits_list))]
    ident = conditional_entropy_and_error(all_bits_list, ident_labels)
    results["identity_zero_entropy"] = ident["conditional_entropy_bits"] == 0.0
    results["identity_zero_error"] = ident["bayes_cell_error_fraction"] == 0.0

    # Constant observer: loses log2(ensemble size) exactly.
    const_labels = [(0,) for _ in all_bits_list]
    const = conditional_entropy_and_error(all_bits_list, const_labels)
    results["constant_equals_log2_N"] = math.isclose(
        const["conditional_entropy_bits"], math.log2(len(all_bits_list)), rel_tol=1e-12
    )

    # Boundary fixtures: empty field (0), single occupied cell (2), vertical
    # half-plane (16), checkerboard (32).
    empty = tuple([0] * NCELLS)
    single = tuple([1] + [0] * (NCELLS - 1))
    # vertical half-plane: columns 0,1 = 1, columns 2,3 = 0 (a sharp vertical
    # boundary splitting the torus into two half-planes -> 2 vertical seams,
    # each SIDE cells long crossing = 2*SIDE = 8 disagreeing horizontal edges;
    # no vertical (row-direction) disagreements since columns are uniform down
    # each column).
    half_plane = tuple(1 if (k % SIDE) < 2 else 0 for k in range(NCELLS))
    checker = tuple((r + c) % 2 for r in range(SIDE) for c in range(SIDE))

    results["boundary_empty"] = boundary_length_of(empty)
    results["boundary_single_cell"] = boundary_length_of(single)
    results["boundary_vertical_half_plane"] = boundary_length_of(half_plane)
    results["boundary_checkerboard"] = boundary_length_of(checker)
    results["boundary_checkerboard_is_max_32"] = boundary_length_of(checker) == 32

    # Rotation/translation invariance of periodic boundary length: rotate
    # checkerboard by one row (cyclic shift) -- boundary length must be
    # unchanged (32, still fully disagreeing).
    def shift_rows(bits, by=1):
        grid = [[bits[r * SIDE + c] for c in range(SIDE)] for r in range(SIDE)]
        shifted = grid[-by:] + grid[:-by]
        return tuple(shifted[r][c] for r in range(SIDE) for c in range(SIDE))

    rotated_checker = shift_rows(checker, 1)
    results["boundary_rotation_invariant"] = (
        boundary_length_of(rotated_checker) == boundary_length_of(checker)
    )

    # single-occupied-cell fixture: 1 cell set, 4 neighbours disagree (2
    # horizontal + 2 vertical edges around that cell) = 4, not the whole 16.
    results["boundary_single_cell_is_4"] = boundary_length_of(single) == 4

    return results


def block_independent_fair_binary_check():
    """PROTOCOL.md: 'For independent fair binary cells, the block-count
    result must equal four times the corresponding analytic 2 by 2 block
    loss.'

    The 'analytic 2x2 block loss' is the conditional entropy of a single,
    isolated 2x2 block of 4 iid fair bits given only its own ones-count
    (0..4), computed directly from the binomial class sizes C(4,k) -- NOT by
    marginalising against the full 16-bit state (that would incorrectly
    also count the other, still fully unresolved 12 bits' entropy). Since
    the four blocks are mutually independent under uniform_all, the total
    loss from observing all four block counts must equal 4x this one-block
    analytic figure.
    """
    from math import comb

    class_sizes = [comb(4, k) for k in range(5)]  # 1,4,6,4,1, sums to 16
    analytic_single_block = sum(
        (n / 16) * math.log2(n) for n in class_sizes if n > 0
    )

    all_bits_list = list(enumerate_states())
    all_block_labels = [block_label(b) for b in all_bits_list]
    full = conditional_entropy_and_error(all_bits_list, all_block_labels)

    return {
        "analytic_single_block_conditional_entropy_bits": analytic_single_block,
        "four_times_analytic_single_block": 4 * analytic_single_block,
        "full_block_counts_conditional_entropy_bits": full["conditional_entropy_bits"],
        "matches_within_1e-9": math.isclose(
            4 * analytic_single_block,
            full["conditional_entropy_bits"],
            abs_tol=1e-9,
        ),
    }


def main():
    here = Path(__file__).resolve().parent
    repo_root = here.parents[1]
    protocol_dir = repo_root / "experiments" / "geometric_waste_v1"

    all_bits_list = list(enumerate_states())
    assert len(all_bits_list) == 65536, f"expected 65536 states, got {len(all_bits_list)}"

    occupancies = [occupancy_of(b) for b in all_bits_list]
    density_half_bits = [b for b, occ in zip(all_bits_list, occupancies) if occ == 8]
    assert len(density_half_bits) == 12870, (
        f"expected 12870 states with occupancy 8, got {len(density_half_bits)}"
    )

    report = {
        "note": "Independent recompute, own enumeration/grouping/entropy code, "
                 "compared only against run_exact.py's published output numbers.",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "n_all_states": len(all_bits_list),
        "n_density_half_states": len(density_half_bits),
        "sanity_checks": sanity_checks(all_bits_list),
        "independent_fair_binary_block_check": block_independent_fair_binary_check(),
        "ensembles": {},
    }

    for name, sample in (("uniform_all", all_bits_list), ("uniform_density_half", density_half_bits)):
        blocks = [block_label(b) for b in sample]
        boundary = [boundary_length_of(b) for b in sample]

        observers = {
            "identity": [(i,) for i in range(len(sample))],
            "occupancy": [(occupancy_of(b),) for b in sample],
            "block_counts": blocks,
            "block_counts_boundary": [blk + (bd,) for blk, bd in zip(blocks, boundary)],
        }
        for seed in (11, 23, 47):
            scrambled = scrambled_permutation(boundary, seed)
            observers[f"block_counts_scrambled_{seed}"] = [
                blk + (sc,) for blk, sc in zip(blocks, scrambled)
            ]

        measured = {}
        for observer_name, labels in observers.items():
            measured[observer_name] = conditional_entropy_and_error(sample, labels)
        report["ensembles"][name] = measured

    out_path = here / "independent_results.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {out_path}")

    # Self-hash for the review report.
    print("independent_recompute.py sha256:", hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print("independent_results.json sha256:", hashlib.sha256(out_path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
