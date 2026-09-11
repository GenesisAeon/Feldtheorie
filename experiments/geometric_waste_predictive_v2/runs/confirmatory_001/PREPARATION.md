# GW-PRED-002: pre-test preparation commitment

All 20 repetitions have completed training and validation. No test state has been generated. `prepared.json` commits to every frozen checkpoint and each checkpoint commits to the saved inputs, features, predictions and fitted coefficients. `manifest.json` records the exact source and environment. These records are published before test opening.

Code commit: `2da5414c8a58ffbcf8a963c9b1f9a96202e3300a`. Preparation SHA-256: `cef3776a1d1d70e5d4752b402eaa39c27c4d59482db3da3492f849b101510f24`.

The merged independent reviews and native Linux preflight were verified before preparation. The initial exec-server connection failed after ten complete repetitions; no runner remained active. An attempted fresh start refused the existing output directory. Explicit resume verified the existing checkpoints and completed all twenty. The terminated first segment has no final resource log, so later resource totals must not be presented as complete accounting. No protocol, source or scientific parameter was changed.

JSON/YAML receipts contain the same provenance and operational details. Full data will be archived with the result; the hashes here bind their pre-test contents. The RIG-EEG holdout is untouched.
