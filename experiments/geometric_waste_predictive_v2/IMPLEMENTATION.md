# Implementation and review handoff

Protocol: GW-PRED-002, frozen in `065ee4d9207cc88d76f02a75a72c82ca3ad28e5d`.
Status: runner implemented; 25 regression/reference checks passed; the 576-state development run, saved-state audit and explicit resume are complete. See [DEVELOPMENT.md](DEVELOPMENT.md), its matching JSON/YAML records and full archive. No confirmatory fit or test generation has been run. Independent G01 and implementation review are pending.

## What is implemented

`model.py` contains the periodic B3/S23 rule, all specified generators, exact full-string deduplication under rotations/reflections/translations, the five 20-component observers, quadratic ridge fitting and repeat-level bootstrap. Zero-variance columns are explicitly suppressed even for constant fractions whose floating-point standard deviation is not exactly zero. Coefficients use the mean-squared-error convention, an unpenalized intercept, train-only scaling and validation-only lambda selection. Secondary intervals reuse the fixed bootstrap seed so the complete-repeat resampling is paired across contrasts; they remain descriptive.

`runner.py` separates development, preparation and evaluation. Preparation saves every training/validation state, generator RNG state, feature, prediction, scaler, coefficient, lambda and comparison choice. Evaluation first verifies all twenty frozen units and their data/model hashes. It then stores test states and predictions, family losses, complete-repeat deltas, primary bootstrap and individual reference contrasts, including null relative ratios when a reference has zero error.

JSON checkpoints carry a canonical content checksum. Atomic publication refuses to replace an existing file. Finished units additionally freeze hashes of their dependencies; resume checks the source/environment signature and checkpoint hashes. These detect changed files and accidental corruption, not a malicious actor who rewrites every checksum. Files created by this run are preserved; only the current writer's unpublished temporary file is removed on failure. A killed process may leave a partial file, which remains preserved and counts toward the size limit.

One process and one numerical thread are used. A 30-minute wall timer bounds each active batch, Linux `RLIMIT_AS` caps virtual address space at at most 4 GiB (stricter than a resident-memory cap), and writes reserve capacity before crossing the 2 GiB output limit. A 64 KiB reserve supports incomplete-batch logs. Resume retains completed split/model units; an interrupted unfinished unit is regenerated deterministically. Run only one invocation per output directory. OS termination or hardware failure can prevent the final resource log, but cannot turn an incomplete run into a complete result.

## What the checks establish

Run `python -m unittest -v test_predictive`. The 25 checks cover hand-computable rule cases, periodic transitions and a cell-wise reference; block/MICRO ordering; boundary seams and every quantizer integer; coarse redundancy and whole-row shuffling; exact small-grid symmetry enumeration; density and development-stream reconstruction; duplicate rejection; ridge versus normal equations; train-only/constant-column scaling; clipping and selection ties; external target isolation; repeat bootstrap and support/family guards; data packing; atomic preservation and corruption detection; explicit resume; review gates; and output-cap preflight.

The fixtures invoke only the three development generators. Hand-made grids and invented loss arrays test algorithms without opening a scientific held-out split. The diagonal and tiles generator branches, real review-approved evaluation path, confirmatory runtime, and final effect size still require the protocol review and staged run. Checks written and run by the implementer are not an independent G01 recomputation or independent scientific review. The full repository suite has not been run for this isolated additive experiment.

## Review evidence required for evaluation

The reviewer should inspect the protocol, implementation, checks and the previous experiment at `experiments/geometric_waste_v1`. G01 concerns the exact pilot's independent recomputation; implementation concerns this runner's fidelity to GW-PRED-002. Retain review reports and any requested amendments. Changes to the scientific design require a new protocol version and a fresh held-out plan.

Pass a plain UTF-8 JSON evidence file to `--reviews`. It must contain:

| Field | Required content |
|---|---|
| `protocol_sha256` | SHA-256 of the frozen protocol.json |
| `runner_sha256`, `model_sha256` | SHA-256 of the reviewed source files |
| `G01` | Object with `reviewer`, `verdict`, `report_path`, `report_sha256` |
| `implementation` | Object with the same four fields for implementation review |

Each verdict must be `approved`; each report must exist, be nonempty and match its hash. Report paths resolve relative to the evidence file. These are checks for documented evidence, not authentication of the reviewer's identity or independence. No approved review record is included in this delivery, because the reviews have not occurred.

Once those actual reports exist and their findings have been handled:

```bash
python runner.py prepare --output runs/confirmatory_001 --code-commit FULL_IMPLEMENTATION_SHA
python runner.py evaluate --output runs/confirmatory_001 --code-commit FULL_IMPLEMENTATION_SHA --reviews path/to/reviews.json
```

Use the same source and full commit in both commands. All twenty fits are fixed before the first test state is generated. Do not interpret a development score as evidence for the primary hypothesis. Sensor budgets still compare maximum transmitted length, with unequal acquisition cost and potentially unequal information content. The existing RIG-EEG holdout is not accessed.
