# G02 implementation review: GW-PRED-002 (geometric_waste_predictive_v2)

## Reviewer, date, scope

- **Reviewer:** Claude Sonnet 5 (Claude Code), acting on Johann Benjamin Römer's explicit review request (`ArbeitFeldtheorie_mandala/Promt.txt`, 2026-09-11).
- **Date:** 2026-09-11.
- **Reviewed protocol commit (frozen):** `065ee4d9207cc88d76f02a75a72c82ca3ad28e5d` ("research: specify G02 predictive geometric waste experiment before data generation").
- **Reviewed implementation commit (pre-development-run):** `584b79500e912dffc17e03832802ac6a94f7bb45` ("research: implement staged GW-PRED-002 runner with 25 reference and gate checks").
- **Development archive/handoff commit:** `4cdbaa6fb5d19600424ed60cb561d9f81b1c3989` ("research: archive verified development run and G02 review handoff").
- **PR #782 merge commit:** `753f8a1e8ec7a740412de9b09c9ff304ed582c7e`. Diffed clean against current `main` (`0e46ec8818`) for both experiment directories — nothing changed post-merge.
- **This is the "implementation" review gate required by `IMPLEMENTATION.md`/`reviews.json`, not a confirmatory scientific result** — no `prepare` or `evaluate` stage was run, and no `test_known`/`test_unseen`/`diagonal`/`tiles` states were generated, per Johann's explicit instruction. The `diagonal` and `tiles` generator branches and the real held-out evaluation path remain untested by this review, as `IMPLEMENTATION.md` itself already discloses.

## Reviewed files (canonical git-blob SHA-256 — see G01_REPORT.md's "hash caveat"; the same Windows-checkout CRLF artifact applies here and was resolved the same way, via `git cat-file -p`)

| File | SHA-256 |
|---|---|
| `PROTOCOL.md` | `7b58145b26d68413719294bf1c998ef430677d54943f8d75daed8952be6c37ba` |
| `protocol.json` | `38de6c3ec0574f4abd712beda000255058821be66f23b12185301af39d78a578` |
| `model.py` | `c1cecde52d656748bdfd6f71573368c575b97d4650c00b0f89445bf79049a878` |
| `runner.py` | `a2e485722c6c16541086f5b2b7f699815843125c652c59bc6a57015d02ff48a0` |
| `test_predictive.py` | `d8c4db86820e7d31ad8495fb7fb217ffb08892459a1b3be817c2d0b0b7d5b8d4` |
| `audit_development.py` | `e9f809214abac8b0a78a4be3356b1fbf979e1df8e60584599c7f650e1939c240` |

All six match `runs/development_001/manifest.json`'s recorded hashes (where applicable) exactly.

## Trilayer sync

`protocol.json` and `protocol.yaml` parse to identical Python dicts (`json.load(...) == yaml.safe_load(...)` → `True`). `PROTOCOL.md` matches both in every mathematical/structural detail checked below.

## Genuine platform limitation (disclosed, not worked around silently)

`runner.py` (and therefore `test_predictive.py` and `audit_development.py`, which both `import runner`) hard-depends on Linux/POSIX-only modules: `resource` (for `RLIMIT_AS`) and `signal.SIGALRM`/`setitimer` (for the 30-minute wall-clock abort). Neither exists in native Windows Python. This machine's WSL (Ubuntu) has Python 3.12 but **no `pip`, no `venv`, and no numpy pre-installed**; installing them requires `apt`/`sudo`, which I did not do unprompted (out of scope for a review task, and a system-modifying action on the user's machine).

To still actually **execute** (not just read) the code under review, I wrote `review/g02_independent/windows_posix_shim.py`: a small import-time shim that stubs `resource` (fake `RLIMIT_AS`/`getrlimit`/`setrlimit`/`getrusage`) and no-ops `signal.SIGALRM`/`setitimer`/`signal.signal` for that one signal, purely so `import runner` succeeds. **This does not test the real resource-limiting behaviour** (`Budget.__init__`/`.check()`/`.close()`'s actual virtual-memory cap and wall-timer abort) — that remains genuinely unverified by this review. Everything else in `runner.py` (checkpoint hashing, atomic writes, resume logic, review-evidence gating, aggregation/bootstrap) runs and is exercised for real through this shim.

**Recommendation:** before the confirmatory run, actually execute `runner.py prepare`/`evaluate` end-to-end on a real Linux machine (or a WSL environment with numpy installed) at least once specifically to exercise `Budget`'s real `RLIMIT_AS` and `SIGALRM` paths, which this review could not do. This is a gap in what could be tested here, not a known defect.

## Protocol-vs-implementation walkthrough (`model.py`)

Read in full against every numbered clause of `PROTOCOL.md`/`protocol.json`; no discrepancy found. Points specifically re-derived or independently spot-checked rather than only read:

- **`step()`:** periodic Moore-neighbourhood B3/S23, synchronous — matches `"alive_next": "neighbours == 3 or (alive_now and neighbours == 2)"` exactly (standard Conway life rule). Cross-checked against `test_predictive.py`'s independent `direct_step()` (explicit nested loop, no `np.roll`) via the executed test suite (see below) — bit-exact agreement on random development-family states.
- **`block_fractions()`:** reshape-based block extraction verified by hand-tracing the index algebra: reshape `(N,16,16)→(N,4,4,4,4)` splits each spatial axis into `(block_index, position_within_block)`, and `sum(axis=(2,4))` sums exactly the within-block positions — confirms row-major 16-block ordering as specified.
- **`quadrant_boundaries()`:** re-derived independently that `quadrants[:,:,:,1:] != quadrants[:,:,:,:-1]` (last-axis diff, no wraparound) plus the same for the row axis gives exactly `7×8 + 8×7 = 112` edges per quadrant with **no periodic wraparound and no cross-quadrant seam** — this exactly matches PROTOCOL.md's explicit requirement that quadrant boundaries and periodic connections across them "count for the sensor not at all." This is the single easiest place a naive re-implementation (e.g., copying the G01-style periodic `np.roll` boundary logic) would have silently gotten wrong, and it is correct here.
- **GEOMETRY quantization (`floor(4·L/113)`):** independently recomputed the full bucket map for `L = 0..112` (`(4*L)//113` in plain Python, not read from the code): buckets are exactly `{0,1,2,3}`, exhaustive and disjoint, with boundaries at `L = 29, 57, 85` — matching `test_predictive.py`'s own hard-coded thresholds `(29, 57, 85)` exactly, confirmed independently rather than taken on faith.
- **MICRO windows:** rows/cols 3–4 (0-indexed) of each 8×8 quadrant, `min(k,3)/3` — matches spec, including the deliberate merging of counts 3 and 4.
- **COARSE:** mean of the 4 pairwise `|Δp|` terms across a quadrant's 2×2 block-fraction sub-grid, `min(3,floor(4D))/3` — matches spec exactly (4-term mean, not sum).
- **SHUFFLED:** whole-example GEOMETRY rows permuted together via a separate seeded stream — matches "packages stay together, permuted across examples."
- **`make_state()`:** verified the top-128 selection tie-break (`np.lexsort((arange(256), -score))`) resolves ties toward the smaller flat index, per spec. All five family score formulas (iid/smooth/axial/diagonal/tiles) checked term-by-term against `PROTOCOL.md`'s formulas, including the toroidal-distance convention for `smooth` and the `(-1)^n = 1-2(n mod 2)` reformulation for `tiles`. Symmetry order (rotate → reflect → shift) matches `protocol.json`'s `symmetry_order` list exactly.
- **`canonical_key()`:** this is the most intricate function in the file (bit-packed D4×translation search). Rather than trust a read-through alone, I relied on `test_predictive.py`'s own independent `brute_key()` (a genuinely different, unvectorized implementation: nested Python loops building explicit row-tuples, no bit-packing tricks) and its two dedicated tests — `test_canonical_key_matches_independent_small_grid_enumeration` (6 fixed 4×4 grids incl. `0x0000`/`0xFFFF`/`0xAAAA` checkerboard) and `test_canonical_key_symmetry_and_no_complement_identification` (all 8 D4 images × an arbitrary translation of a 3-point 16×16 mask must collide; the bitwise complement must **not** collide) — both passed under actual execution (see below), which is a stronger check than reading the bit-packing code by eye.
- **`fit_ridge()`:** re-derived by hand that the SVD-based closed form `coefficients = Vᵀ·diag(S/(S²+n·λ))·(Uᵀr)` (with `r = y - mean(y)`, features pre-centred/scaled so the intercept can be handled by mean-subtraction alone) is the correct minimizer of `(1/n)‖Xβ-r‖² + λ‖β‖²` — i.e. confirms the code's `factor = S/(S²+n·regularization)` uses the **mean**-squared-error convention (not sum-of-squares), matching `IMPLEMENTATION.md`'s explicit claim. Also confirmed `design_rank = rank(a) + 1` and `effective_degrees_of_freedom = 1 + Σ S²/(S²+nλ)` are correct because the intercept direction (constant vector) is exactly orthogonal to every column of the already mean-centred `a`, so it always contributes exactly one full, unpenalized additional degree of freedom — this is not an ad hoc fudge. Independently cross-checked in the executed test suite via `test_ridge_matches_augmented_normal_equations`, which compares against literal augmented normal equations (`np.linalg.solve`) — passed.
- **Lambda tie-break (larger λ wins) and comparator tie-break (BASE > MICRO > COARSE > PERSISTENCE order):** both re-derived from the `min(..., key=...)` tuple constructions and confirmed to match `protocol.json`'s stated tie-break rules exactly.
- **`repeat_bootstrap()`:** matches the specified single fixed `PCG64(bootstrap_seed)` stream, 10,000 draws, linear-interpolated 0.025/0.975 quantiles.

No correctness bugs found anywhere in `model.py`.

## `runner.py` walkthrough

Read in full. Checkpointing (`write_once`, atomic hardlink-publish, content-checksum via `_content_sha256`), resume logic (`open_run`, per-unit `frozen.json`/`evaluated.json` hash re-verification), the review-evidence gate (`verify_reviews`: requires `protocol_sha256`/`runner_sha256`/`model_sha256` to match the *current* files, both `G01` and `implementation` verdicts to literally equal `"approved"`, and each linked report to exist, be non-empty, and hash-match) and the aggregation/decision logic in `aggregate()` (paired deltas, family guard at `-0.005`, `support_all_conditions` requiring all four listed conditions) were all read against `PROTOCOL.md`/`protocol.json` clause-by-clause; no discrepancy found. `SUPPORTED_PROTOCOL_SHA256` correctly pins the runner to the exact frozen `protocol.json` blob (confirmed via `git cat-file -p`, see hash caveat).

## Actual execution (not just static review)

**`test_predictive.py`, all 25 declared checks, run for real** via `windows_posix_shim.py` plus one additional, disclosed workaround: this Windows checkout's CRLF conversion (see G01_REPORT.md) made `runner.load_config()`'s pinned-hash check fail for 6 of the 25 tests on the first attempt; re-run from a temp copy with `protocol.json`/`runner.py`/`model.py`/`PROTOCOL.md` restored to their canonical git-blob (LF) bytes via `git cat-file -p` — **all 25/25 pass.** Full output: `review/g02_independent/test_predictive_output.txt`.

**`audit_development.py`, run for real against the actual archived `runs/development_001.tar.gz`** (576 states: 384 train + 192 validation across iid/smooth/axial). Archive SHA-256 independently recomputed and matches `DEVELOPMENT.md`'s declared `3ee95971ac92ade16071a6ca74a283fae6db5657aa65b68de1d00d11a9bfad58` exactly (binary file, unaffected by the line-ending issue). Ran via `review/g02_independent/audit_development_patched.py`, which differs from the original in exactly three disclosed, justified ways (documented in that file's own docstring and reproduced here):

1. Skipped the manifest environment-signature equality check — the archive's `manifest.json` records `Linux-6.18.35-x86_64/Python 3.12.14/numpy 2.3.5`; this review ran `Windows-10/Python 3.11.9/numpy 2.2.6`. A genuine, expected cross-platform difference, not a defect — this is exactly the kind of check the original script is *right* to enforce for a real resume, and I do not consider it satisfied here.
2. & 3. Relaxed two `assert_array_equal` floating-point comparisons (sensor feature values; observer predictions) to `assert_allclose(atol=1e-9, rtol=1e-9)`. Confirmed first, before relaxing, that the actual observed differences were at the ~1e-16 absolute / ~1e-13 relative level (visible in the raw `AssertionError` diff before patching) — consistent with ordinary cross-NumPy-version floating-point summation-order noise, not a real numerical divergence.

**Result: full pass.** All 576 states reconstruct byte-exact from their recorded RNG pre-states; all canonical keys re-verified with zero duplicates; the independently-formulated cell-wise reference (`direct_step`, not the vectorised `step`) reproduces every stored target with **exactly zero** MAE; every family/split count matches the frozen protocol; the frozen comparator selection (`COARSE`) is independently re-derived from the validation MAE table and matches. Full output: `review/g02_independent/audit_development_output.json`.

**Cross-check against `DEVELOPMENT.md`'s published table:** the audited `frozen.json` validation MAEs (BASE 0.10776174689928253, GEOMETRY 0.10502214586663994, MICRO 0.10887386159783163, COARSE 0.10769868900705677, SHUFFLED 0.10916063379331925, PERSISTENCE 0.3099161783854167) match `DEVELOPMENT.md`'s table to the displayed precision, and `0.10769868900705677 − 0.10502214586663994 = 0.0026765...` matches the claimed "GEOMETRY beats COARSE by 0.002677" delta.

## Explicitly not checked / interpretation limits

- **The real POSIX `Budget` resource enforcement** (actual `RLIMIT_AS` virtual-memory capping, actual `SIGALRM`-based 30-minute wall timer, actual disk-quota preflight under real I/O) — untestable on this machine without a working Linux/numpy environment; genuinely open, not merely "assumed fine." Recommend one real Linux execution of `prepare`/`evaluate` before relying on these limits operationally.
- **The `diagonal` and `tiles` generator branches** (the two held-out families) — never exercised, by design (test data must stay closed). `PROTOCOL.md`'s formulas for these families were read and checked for internal consistency with the `axial` formula they mirror, but no state was ever generated from them, consistent with the instruction not to touch held-out generation in this review.
- **The real `prepare`/`evaluate` CLI paths and the confirmatory 20-repeat run** — not executed, by explicit instruction.
- A successful implementation-fidelity review is **not** a confirmation of the GEOMETRY hypothesis itself — per `PROTOCOL.md`'s own repeated caveats, the development-run MAE gap (0.0027) is explicitly not an unbiased test-set estimate (it was also used to pick λ and the comparator) and carries no confirmatory weight.
- No additional regression tests were added: the existing 25-test suite, once actually executable, already covers every item Johann's review prompt asked to check (hand fixtures for the CA rule, block/MICRO/GEOMETRY ordering and quantizer boundaries incl. L=0/L=112, COARSE redundancy, SHUFFLED row-permutation-only property, canonical-key symmetry/non-complement via independent brute-force enumeration, ridge-vs-normal-equations, train-only scaling and constant-column handling, lambda/comparator ties, external-target-isolation, bootstrap determinism, aggregation/heterogeneity/zero-denominator handling, atomic-write/corruption/resume, and both review-gate failure modes) and, once run for real, revealed no gap that a new test would need to close.

## Verdict

**`implementation`: `approved`**

Both the static protocol-vs-code walkthrough and actual execution (25/25 tests, full development-archive re-audit against an independently-formulated cellular-automaton reference) found zero correctness discrepancies against the frozen `GW-PRED-002` protocol. The one residual gap — real POSIX resource-limit enforcement, untestable on this Windows machine — is a testing-coverage gap in *this review*, not a known defect in `runner.py`, and does not bear on scientific validity; it is flagged above as a recommended pre-confirmatory-run action rather than a blocking finding.

This verdict, together with `G01_REPORT.md`'s `approved` verdict, is recorded in `../reviews.json` per `IMPLEMENTATION.md`'s required schema. Per `PROTOCOL.md`, satisfying both gates is a precondition for `held_out_test_opening`, but does **not** itself authorize running `prepare`/`evaluate`: that remains Johann's decision, and the real Linux resource-limit gap above should be resolved first.
