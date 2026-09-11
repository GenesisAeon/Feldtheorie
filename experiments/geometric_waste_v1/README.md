# Geometric waste calibration

Exact finite-state pilot for Johann Benjamin Römer’s geometric-waste idea. Read [PROTOCOL.md](PROTOCOL.md) before interpreting results. The frozen design is mirrored in [protocol.json](protocol.json) and [protocol.yaml](protocol.yaml).

From this directory, with Python 3.10+ and NumPy installed:

```bash
python -m unittest -v test_exact
python run_exact.py --output runs/my_new_run
```

The output directory must be new. Runs never overwrite existing results. The pilot is standalone and does not import Feldtheorie packages or require the full repository environment. Recorded runtime versions describe the pilot, not compatibility certification of the entire repository.

The result is a calibration of conditional entropy and reconstruction error. It is not evidence for a thermodynamic identity or quantum gravity. Exhaustive counts have no sampling confidence interval. Scrambled boundary labels are diagnostic counter-observers with the same marginal distribution; three seeds do not constitute a statistical hypothesis test.

Conceptual origin: [geometric waste hypothesis](../../seed/theory/entropy_geometric_waste/entropy_geometric_waste.md). Order index: [seed index](../../seed/seed_index.md). Historical claims and existing evidence remain intact. An independent AI evaluation is still required before interpreting this implementation as independently checked.

<!-- CUSTOM_RULES -->
The experiment-level protocol and result records use Markdown, JSON and YAML. Python and CSV are executable and tabular artifacts referenced by those records, not duplicated into artificial formats. No logistic model is fit, so AIC and bootstrap confidence intervals are inapplicable to this exact enumeration.
<!-- /CUSTOM_RULES -->
