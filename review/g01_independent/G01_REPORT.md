# G01 independent review: GW-EXACT-001 (geometric_waste_v1)

## Reviewer, date, scope

- **Reviewer:** Claude Sonnet 5 (Claude Code), acting on Johann Benjamin Römer's explicit review request (`ArbeitFeldtheorie_mandala/Promt.txt`, 2026-09-11).
- **Date:** 2026-09-11.
- **Reviewed protocol commit:** `620a5ce3425f9da741c6444e12ce5b26c029771e` ("research: freeze geometric waste exact calibration protocol and runner"). Confirmed via `git merge-base --is-ancestor` to be an ancestor of the results commit `a02def2ef7` ("research: add experimental roadmap and exact geometric waste calibration results") — the frozen protocol predates its own results, as REVIEW_PACKET.md requires.
- **Base repository commit at review time:** `0e46ec88181b430c41330016279a8bd1ea2c0d9b` (current `main`, pulled fresh; diffed clean against the PR #782 merge commit `753f8a1e8e` for the reviewed experiment directories — no relevant changes since merge).
- **Reviewed files (canonical git-blob SHA-256, see "hash caveat" below):**
  - `PROTOCOL.md`: `6c93fe30f5dd6f37b1b67e89be4c6699b0fe18ffeb40031a19a8cdbf2c5ff8d3`
  - `protocol.json`: `d906d72e9053dac1eaf6d24601fcb513d862987eb9fc902a084c31191cd3eabf`
  - `run_exact.py`: `f21ea5703f84c8244c1e68fee636dd334462b58a444f66b2b945d5465d4cb8ac`
  - `test_exact.py`: `53fa0f6e4b041c75e91f3d34e6b82f963f1111050a3a2d96b9d7f95d45c7f910`
  - All three match the hashes recorded inside `runs/calibration_v1/results.json` exactly (see hash caveat).
- **Environment:** Windows 10 (10.0.19045), Python 3.11.9, NumPy 2.2.6, git worktree `review/g01-g02-independent-verification` at `.claude/worktrees/review-g01-g02-independent`. Published results were computed with Python 3.12.14 / NumPy 2.3.5 on Linux (per `results.json`); this review's independent recomputation used a different Python/NumPy version and platform deliberately, since exact combinatorial enumeration and rational-valued entropy/error formulas are expected to be platform- and version-independent (unlike the floating-point-heavy G02 fits — see the G02 report for where that distinction actually matters).

## Hash caveat (applies to this whole review, both G01 and G02)

**Finding, not a defect:** this Windows checkout has `core.autocrlf=true`, so git rewrites the repo's native LF line endings to CRLF on checkout. A SHA-256 computed directly against the checked-out files on this machine therefore does **not** match the hashes recorded by the original (Linux) run, even though the content is byte-identical modulo line endings. Confirmed directly: hashing `PROTOCOL.md`/`protocol.json`/`run_exact.py` after `.replace(b"\r\n", b"\n")`, or reading the content via `git cat-file -p <rev>:<path>` (which returns the canonical git-blob bytes, unaffected by checkout-time line-ending conversion), reproduces every hash recorded in `results.json` exactly. All hashes in this report and in `reviews.json` were computed the second way (via `git cat-file -p`), not from the raw Windows working-tree file. This is a systemic gotcha for anyone reviewing this repository on Windows and is worth a `.gitattributes` entry (`* -text` or explicit `text eol=lf` for the tracked source/protocol files) if this comes up again — but it is **not** a flaw in GW-EXACT-001 or its runner.

## Independently reproduced quantities

Own implementation: `review/g01_independent/independent_recompute.py`, ~230 lines, written directly from `PROTOCOL.md`/`protocol.json` only. Deliberately does **not** reuse `run_exact.py`'s grouping (`np.unique`/reshape-based) or entropy/error functions:

- Enumeration: `itertools.product` over reversed bit tuples (vs. `run_exact.py`'s vectorised right-shift broadcast).
- Block counts: explicit nested-loop 2×2 sums per block (vs. reshape/sum trick).
- Boundary length: explicit double loop over modular row/column neighbours (vs. `np.roll`-based comparison).
- Grouping/entropy/error: plain Python `dict`/`Counter`-based grouping and manually derived `H(X|Y) = Σ_y P(y)·log2(|class_y|)` and Bayes cellwise-error formulas (vs. `np.unique(..., return_inverse=True)` + `np.add.at`).

**Result:** every one of the 14 ensemble/observer combinations (`uniform_all` and `uniform_density_half`, 7 observers each: identity, occupancy, block_counts, block_counts_boundary, block_counts_scrambled_{11,23,47}) matches the published `results.json` to within **4.5×10⁻¹⁴** absolute difference on every numeric field (conditional entropy, retained information, Bayes cellwise error, observation-class counts, microstate counts) — consistent with ordinary floating-point summation-order noise between two independently-written implementations on different NumPy versions, not a discrepancy. Full numeric output: `review/g01_independent/independent_results.json`.

Class-record cross-check: `observation_classes.csv`'s row counts (85 `block_counts` + 316 `block_counts_boundary` = 401 total for `uniform_density_half`) match the class counts in `results.json` exactly. `observations.jsonl` has the expected 14 rows (2 ensembles × 7 observers).

Scrambled-diagnostic reproducibility: `np.random.default_rng(seed).permutation(boundary)` for seeds 11/23/47, applied to my independently-computed boundary arrays, reproduced `run_exact.py`'s published `block_counts_scrambled_*` entropy/error values bit-for-bit up to float noise — confirming the seeded RNG procedure is exactly reproducible as PROTOCOL.md requires ("Seeds 11, 23 and 47 are fixed before execution").

## PROTOCOL.md-mandated checks, all independently re-verified

| Check (from PROTOCOL.md "Checks and interpretation") | Result |
|---|---|
| Identity observer: zero conditional entropy, zero reconstruction error | ✅ confirmed |
| Constant observer: loses exactly log2(ensemble size) | ✅ confirmed |
| Boundary fixtures: empty field | 0 (max is 32) — ✅ |
| Boundary fixtures: single occupied cell | 4 (its 4 periodic neighbours) — ✅ |
| Boundary fixtures: vertical half-plane | 8 (two seams × 4 rows) — ✅ |
| Boundary fixtures: checkerboard | 32 (the stated maximum) — ✅ |
| Rotation/translation preserve periodic boundary length | ✅ confirmed (cyclic row shift of checkerboard still 32) |
| Independent fair binary cells: block-count loss = 4× the analytic single-block loss | ✅ confirmed to 1e-9 **after I fixed my own first attempt** — see below |

**Self-correction during this review:** my first version of the "4× fair block" check computed the wrong quantity (conditional entropy of the *full* 16-bit state given only one block's count, which spuriously also carries the other 12 unresolved bits' entropy) and reported a false failure (`13.97` vs. `55.88` bits). The correct analytic quantity is the conditional entropy of a single isolated 2×2 block of 4 iid fair bits given only its own ones-count, computed directly from the binomial class sizes C(4,k): `Σ_k (C(4,k)/16)·log2(C(4,k)) = 1.969360...` bits; four independent blocks under `uniform_all` give exactly `4 × 1.969360... = 7.877443751...`, matching the published `block_counts` conditional entropy (`7.877443751081733`) to 1e-9. Fixed in the committed script; flagging this here per the standing "verify, don't trust — including your own first draft" discipline this repository already applies elsewhere.

## Existing unit tests

`python -m unittest test_exact` (native Windows, no platform issues since this file has no POSIX dependency): **7/7 pass.**

## Explicitly not checked / interpretation limits

- Did not re-verify NumPy's own `np.unique`/floating-point summation internals — only the published *output* was cross-checked against an independently-coded implementation, which is the correct scope for this kind of exact-combinatorial calibration.
- This calibration is, as PROTOCOL.md itself states, **not** evidence of a geometry-specific law, a thermodynamic/gravitational/quantum/spacetime claim, or a universal entropy principle — it establishes only that (a) the declared exact computation is correctly implemented and (b) revealing boundary-length information does reduce conditional entropy in this specific finite ensemble by an amount comparable to (in this instance, indistinguishable in Bayes cellwise error from) a same-budget scrambled/nonlocal-lookup control. No claim beyond that is endorsed by this review.
- No new counterexamples were found; no discrepancies remain outstanding.

## Verdict

**`approved`**

The independent recomputation matches the published exact calibration to floating-point precision across all 14 ensemble/observer combinations, every protocol-mandated sanity check passes, the frozen-protocol-predates-results ordering is confirmed, and the existing unit tests pass. The only irregularity found (SHA-256 mismatches) was tracked down to a benign, disclosed Windows checkout artifact (`core.autocrlf`), not a defect in the frozen protocol, the runner, or its published results.

## Follow-up experiment note

Per PROTOCOL.md's own "Next experiment" section, GW-EXACT-001's result is explicitly not held-out evidence for GW-PRED-002 (G02) — it only informs G02's design. This review treats G01 and G02 as two independent gates accordingly (see `G02_REPORT.md`).
