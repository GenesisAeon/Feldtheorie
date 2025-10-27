# Analysis Resonance Protocols

Work within `analysis/` must radiate reproducibility:

1. **Notebook hygiene.** Keep notebooks parametrised and free of hard-coded paths.  Report $R^2$, AIC, confidence intervals on $\Theta$ and $\beta$, and document the impedance context $\zeta(R)$ for each experiment.
2. **Null comparisons.** Every logistic fit must be paired with at least one smooth null (power law, exponential, spline) and the falsification result recorded in-line.
3. **Tri-layer annotations.** Reserve sections for (a) formal derivations, (b) empirical observations, and (c) metaphorical narration that ties data back to the UTF lexicon.
4. **Metadata echo.** Reference datasets in `data/` and solvers in `models/`, noting version hashes or commit IDs when possible.

Scripts should expose CLI entry points for re-running fits and export JSON summaries of threshold parameters for downstream modules.
