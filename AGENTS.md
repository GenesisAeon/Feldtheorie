# Repository-wide Guidelines

This repository curates the "Universal Threshold Field" programme that unifies emergent threshold behaviour across astrophysics, biology, cognition, and AI. Follow these principles for every contribution:

1. **Preserve the threshold-field framing.** Always describe dynamics in terms of the order parameter $R$, the critical threshold $\Theta$, the steepness $\beta$, and the logistic response $\sigma(\beta(R-\Theta))$. When introducing new models or narratives, make the control parameter and its switch-like resonance explicit.
2. **Honour the tri-layer documentation style.** Cross-reference formal mathematics, empirical evidence, and metaphorical/philosophical language. Documentation should weave these strands instead of presenting them in isolation.
3. **Analysis standards.** Any quantitative notebook or report must state the fitting method, goodness-of-fit metrics ($R^2$, AIC), confidence intervals for $\Theta$ and $\beta$, and include a falsification check against at least one smooth null model (e.g. power law).
4. **Simulation conventions.** Models should expose membrane/impedance parameters and clearly document how $\zeta(R)$ toggles regimes (damped vs. resonant). Boundary conditions and coupling terms must be explained in prose and equations.
5. **Repository structure alignment.** Keep the planned directories (`models/`, `analysis/`, `simulator/`, `docs/`, `paper/`, `data/`, `diagrams/`) tidy. Each new artefact should note where it fits in the overarching RepoPlan 2.0 roadmap stored in `Docs/`.
6. **Tone and symbolism.** Maintain the poetic resonance already established in the source PDFs. When in doubt, link technical advances back to their narrative or metaphysical interpretations.

When touching nested folders, check for additional `AGENTS.md` files that may refine these rules.
