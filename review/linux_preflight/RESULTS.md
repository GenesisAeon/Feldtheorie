# Linux follow-up to independent review PR #783

Author: Codex, 2026-09-11. Reviewed independent-review commit: `fae4a1c0713669bb19ca133387a658bf6d18bfc4`. Reviewed experiment source remains the implementation committed as `584b79500e912dffc17e03832802ac6a94f7bb45`, on main `0e46ec88181b430c41330016279a8bd1ea2c0d9b`.

**Outcome:** the outstanding native Linux resource checks pass. The original 25-test suite and unmodified development audit pass without a shim, changed tolerances or skipped signature checks. Both actual review-evidence gates accept the unchanged Claude reports. The independent numerical G01 results are reproduced. Two statements in the review narrative need the clarifications below; no experiment-source correction was necessary.

This is the implementer's operational follow-up and inspection of another reviewer's evidence. It does not replace Claude's independent authorship or constitute a third independent implementation. The original reports, review evidence, production sources, scientific configuration and previous outputs remain unchanged.

## Native Linux checks

Environment: Linux 6.18.35 x86_64 / glibc 2.39, Python 3.12.14, NumPy 2.3.5. The CPython `resource` module is genuinely built into this runtime. No Windows shim was imported. Tests run in child processes and restore the original memory limit and signal handler.

| Check | Observed result |
|---|---|
| Actual `RLIMIT_AS` | Soft ceiling is 4,294,967,296 bytes. A mapping requesting that much additional virtual address space fails with `ENOMEM`; physical pages are not allocated. |
| Actual `SIGALRM` | A 0.05-second timer invokes the real exception handler after about 0.05015 seconds, without calling `Budget.check()`. |
| Disk preflight | With an explicit 96 KiB operational fixture and the real 64 KiB log reserve, an oversized JSON write is refused before publication; prior bytes are preserved. |
| External disk consumption | Real files exceeding the fixture limit are detected by `Budget.check()`. |
| Interruption and resume | A 0.03-second development-only batch records `incomplete`. Explicit resume with the normal budget completes and preserves both existing files. The resulting 576-state audit passes. |
| Restoration | Memory limits and signal handlers are restored; timers are cancelled. |
| Review gate | The real Linux `verify_reviews()` accepts both canonical report hashes and both `approved` verdicts. |

The shortened time and disk budgets are declared operational fixtures in memory, not changes to protocol files or scientific parameters. Testing the actual timer mechanism does not require a 30-minute wait or generating held-out states. These checks do not certify every possible process-kill, filesystem-failure or concurrency scenario. The actual confirmatory `prepare`/`evaluate` execution remains outstanding.

The first local preflight attempt had an error in this new harness: it assumed every native `resource` module has a `.so` origin. This runtime statically links it as `built-in`. The check was corrected to accept a real built-in/extension module and require a built-in `setrlimit` function. The initial failure and its source hash are retained in the result record; no runner defect was involved.

## G01 numerical replay and stronger checks

`recheck_g01.py` executes Claude's reference functions without invoking the script's output-overwriting `main()`. It compares every numerical field in all 14 ensemble/observer results against both the published experiment and Claude's committed output. Maximum absolute difference: **4.529709940470639e-14**, below the declared absolute comparison tolerance of 1e-12.

All **401 exported observation-class records** are individually checked for class size, class entropy and posterior reconstruction loss. This goes beyond checking CSV row counts. The state enumeration contains exactly 65,536 distinct states in the specified integer order and 12,870 states at half density. The reference's sanity checks and analytic single-block calculation pass.

The original reference's check named `boundary_rotation_invariant` actually shifts checkerboard rows. This follow-up additionally checks a genuine quarter-turn and a row/column torus translation for **every one of the 65,536 states**; both preserve boundary length. This closes that limitation of the independently written sanity check.

## Clarification 1: G01 reconstruction comparison

The paragraph under “Explicitly not checked / interpretation limits” in [G01_REPORT.md](../g01_independent/G01_REPORT.md) describes the boundary observer as indistinguishable in Bayes reconstruction error from a scrambled control. The numbers establish a different comparison:

| Ensemble | Block counts | Block counts + boundary | Scrambled controls, seeds 11/23/47 |
|---|---:|---:|---:|
| Uniform over all states | 0.312500000 | 0.312500000 | 0.288621902 / 0.288372040 / 0.288765907 |
| Uniform at half density | 0.338461538 | 0.338461538 | 0.318230381 / 0.318803419 / 0.318186674 |

**Equality holds between the block and block-plus-boundary observers.** All three scrambled controls have lower Bayes error in both enumerated ensembles. They also have lower residual entropy than the boundary observer in these results. This does not establish physical superiority of those controls: their arbitrary nonlocal lookup and acquisition costs remain unmatched. The correction concerns the review's interpretation, not its reproduced numerical output or the original experiment report.

## Clarification 2: G02 audit adaptations

[G02_REPORT.md](../g02_independent/G02_REPORT.md) and the patched audit docstring count three behavioural changes. The committed [audit_development_patched.py](../g02_independent/audit_development_patched.py) has **four** relevant adaptations:

1. Removal of the whole manifest-signature equality check. That comparison covers source/protocol signatures as well as the environment; the report separately checks canonical source hashes.
2. Feature arrays compared with `allclose(atol=1e-9, rtol=1e-9)` instead of exact equality.
3. Prediction arrays compared with the same tolerance instead of exact equality.
4. Validation MAE compared with absolute tolerance 1e-9 instead of exact equality.

The fourth change is visible in the code but missing from the three-item explanation. The cross-platform reasoning is plausible, but this follow-up does not independently certify the maximum Windows discrepancies stated by Claude. On the original Linux environment, the unmodified audit passes every check, including all exact comparisons and the complete manifest signature. Original production checks were never weakened.

## Evidence, reproduction and decision

[RESULTS.json](RESULTS.json) and [RESULTS.yaml](RESULTS.yaml) contain identical status and evidence records. [native_results.json](native_results.json) preserves the native probe output, source hashes, interruption/resume logs and final checkpoint hashes. [g01_linux_replay.json](g01_linux_replay.json) contains every recomputed metric and the detailed check counts.

From a Linux checkout with the reviewed source and NumPy available, use fresh output paths:

```bash
python review/linux_preflight/native_preflight.py --output /tmp/genesis-linux-preflight-new
python review/linux_preflight/recheck_g01.py --output /tmp/genesis-g01-replay-new.json
```

The native interrupted-development audit records its own environment, so it does not require the original archive's platform signature. The original archive audit, when run separately, deliberately requires that original signature. No native test invokes `run_tests_windows.py` or `windows_posix_shim.py`.

With this supplement attached, **PR #783 is suitable to merge as review evidence**. The Linux resource gap is resolved for the tested mechanisms, and the numerical conclusions of G01 are verified. The two narrative clarifications above accompany the preserved original reports. A merged review is still not a positive outcome of GW-PRED-002: its confirmatory effect remains unknown.

No confirmatory fits, either scientific test split or diagonal/tiles samples were generated. The RIG-EEG holdout was not accessed. The next scientific step remains the separately initiated twenty-repeat preparation, followed by evaluation only after all fits and choices are frozen.

Meaning: [original geometric-waste hypothesis](../../seed/theory/entropy_geometric_waste/entropy_geometric_waste.md). Order: [seed index](../../seed/seed_index.md). Primary evidence: [G01 protocol](../../experiments/geometric_waste_v1/PROTOCOL.md), [G01 results](../../experiments/geometric_waste_v1/runs/calibration_v1/results.json), [G02 protocol](../../experiments/geometric_waste_predictive_v2/PROTOCOL.md), and [runner](../../experiments/geometric_waste_predictive_v2/runner.py).

<!-- CUSTOM_RULES -->
This operational review is represented in Markdown, JSON and YAML. It fits no resource-driven logistic transition in (R, Theta, beta, zeta(R)); neither sigma(beta(R-Theta)) nor AIC is an appropriate output for these exact checks. The later scientific experiment retains its prespecified paired confidence interval. Historical reports and their review hashes are preserved.
<!-- /CUSTOM_RULES -->
