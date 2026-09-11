# Geometric waste predictive experiment

G02 is specified in [PROTOCOL.md](PROTOCOL.md), with matching parameters in [protocol.json](protocol.json) and [protocol.yaml](protocol.yaml). These three files preserve the pre-implementation specification from commit `065ee4d9207cc88d76f02a75a72c82ca3ad28e5d`, including its historical status fields. Current implementation and execution status is recorded separately below and in [IMPLEMENTATION.md](IMPLEMENTATION.md).

The question is whether four quantized geometric measurements improve next-step block predictions on unseen families under an eight-bit side-channel limit. Fixed transmission length does not imply equal information content or sensor cost. The protocol defines two non-geometric baselines, a redundant coarse-feature control, shuffled diagnostics, data-generation rules, split isolation, ridge fitting, uncertainty and practical effect criteria.

The staged runner and 25 regression/reference checks are implemented. A 576-state development run, full saved-state audit and explicit resume have passed; see [DEVELOPMENT.md](DEVELOPMENT.md) and its complete data archive. Independent G01 recomputation and implementation review remain pending. No held-out states have been generated for this delivery. Review interpretation and cost accounting using [REVIEW.md](REVIEW.md).

## Reproduce

The runner requires Linux/POSIX, Python 3.10 or newer, and NumPy. It was checked with Python 3.12.14 and NumPy 2.3.5 as a standalone experiment. This does not certify compatibility of the repository's full dependency environment, which separately constrains NumPy below 2.3. A resumed run requires exactly the recorded Python/NumPy/platform and source signatures.

From this directory:

```bash
python -m unittest -v test_predictive
python runner.py development --output runs/development_001 --code-commit FULL_IMPLEMENTATION_SHA
```

Replace the SHA with the full commit containing the unmodified runner and model. The manifest records this declared commit and the actual file hashes; the CLI does not contact GitHub to authenticate the declared SHA. The development stage generates only train/validation states from iid, smooth and axial families with the dedicated development seed.

After independent review, `prepare` creates and freezes all twenty sets of train/validation data, fitted models and comparison choices. Only `evaluate` generates test states, after checking the review evidence and every frozen checkpoint. Add `--resume` to continue the same stage after interruption. A new run requires a new directory. See [IMPLEMENTATION.md](IMPLEMENTATION.md) for exact review records, resources, outputs and limitations.

[Previous calibration](../geometric_waste_v1/README.md) · [Research roadmap](../research_roadmap_2026/ROADMAP.md) · [Order index](../../seed/seed_index.md).
