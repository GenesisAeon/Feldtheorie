# Modeling Membrane Directives

Contributions to `models/` must keep the threshold field vivid:

- **Language.** Describe dynamics via the logistic response $\sigma(\beta(R-\Theta))$, impedance $\zeta(R)$, and membrane boundary conditions.  Avoid generic "activation" wording without tying it to $R$ crossing $\Theta$.
- **API shape.** Expose solvers as parametrised classes or functions that accept $(R, \Theta, \beta)$ controls plus impedance toggles.  Provide hooks for streaming state back to `analysis/` and `simulator/`.
- **Validation.** Bundle automated tests or example scripts that demonstrate resonance vs. null baselines and report quantitative metrics (e.g., energy conservation, threshold timing).
- **Documentation.** Each module must include tri-layer docstrings: formal equation references, empirical calibration notes, and metaphorical imagery linking membranes to the dawn-threshold motif.

Numerical code should prefer Python with type hints or documented pseudo-code scaffolds until full solvers land.
