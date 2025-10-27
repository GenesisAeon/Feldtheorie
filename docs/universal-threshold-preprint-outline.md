# Universal Threshold Field Preprint Outline

## Formal strata — framing the field equation
- **Order parameter ($R$):** repository of cross-domain intensities (token flux, dopamine gain, luminosity). Each section of the preprint anchors to a measurable $R$ stream so the logistic membrane has empirical footing.
- **Critical threshold ($\Theta$):** emphasise how observed tipping points are estimated through the fitting routines in `analysis/` (e.g. `analysis/resonance_fit_pipeline.py`). Document confidence intervals and AIC comparisons versus power-law nulls to foreground falsifiability.
- **Steepness ($\beta$):** explain how membrane sharpness is tuned in `models/membrane_solver.py` and the simulator controls. Include derivations showing how varying $\beta$ reshapes the sigmoid $\sigma(\beta(R-\Theta)) = 1/(1 + e^{-\beta(R-\Theta)})$.
- **Impedance ($\zeta(R)$):** outline the regimes encoded in `simulator/threshold_membrane.vue` (damped vs resonant). Specify how the Euler stride $R_{t+1} = R_t + \Delta t [J(t) - \zeta(R_t)(R_t - \sigma)]$ propagates through the numerical appendix.

## Empirical strata — weaving data into the manuscript
- **Astrophysics:** summarize quasi-periodic oscillation fits (`analysis/results/qpo_resonance_scan.json`) and the associated null comparisons. Highlight how $\Delta\mathrm{AIC} > 0$ validates the logistic membrane over smooth baselines.
- **Biology:** integrate the synaptic and waggle-dance ledgers (`docs/biology/synaptic_release_threshold.md`, `data/biology/waggle_dance.metadata.json`) to demonstrate $R$ surges crossing $\Theta$ in living systems.
- **Cognition:** use the working-memory gate diagnostics (`analysis/results/working_memory_gate.json`) to showcase how $\beta$ sharpens once rehearsal gain passes its membrane threshold.
- **AI:** connect `docs/ai/llm-threshold-training.md` with simulator sliders so readers can replicate emergent reasoning phases. Mention the logistic versus power-law score deltas stored in `analysis/results/llm_emergent_skill.json`.
- **Socio-ecology:** document resilience metrics (`data/socio_ecology/amazon_resilience.metadata.json`) and early-warning fits to evidence universal $\Theta$ signatures.

Each subsection should close with a "Falsification lens" paragraph describing the null scenario (linear drift, power-law slide, or exponential calm) that fails to match the recorded resonance.

## Metaphorical strata — sustaining the codex voice
- Narrate the preprint as a **membrane chronicle**: astrophysical pulses, bee choruses, and neural sparks walk the same dawn-lit bridge.
- Use the **codex lexicon** (luminous thresholds, membranes breathing, dawn choruses) to bind sections, echoing motifs in `utf-living-glossary.md`.
- Close with a call to steward the field: the logistic crest is both a scientific transition and a poetic invitation.

## Proposed manuscript structure
1. **Prelude:** contextualise the Universal Threshold Field with references to `Docs/Entwurf eines transdisziplinären Feldmodells.pdf` and the living glossary.
2. **Equation of the Field:** formal derivation of the solver, impedance regimes, and null comparisons.
3. **Empirical Resonance:** five-domain case studies (AI, cognition, biology, astrophysics, socio-ecology) with shared $R$, $\Theta$, $\beta$ tables.
4. **Simulator Interface:** describe how `simulator/` components let readers manipulate membranes and observe transitions.
5. **Symbolic Echo:** reflective prose aligning scientific claims with metaphorical insight.
6. **Falsifiability & Future Work:** enumerate replication hooks, dataset gaps, and codexfeedback follow-ups.

## Cross-references
- Link to `docs/resonance-bridge-map.md` for the canonical parameter ledger.
- Reference `analysis/AGENTS.md` directives for reporting standards in figures and tables.
- Annotate upcoming pull requests in `codexfeedback.*` so the manuscript remains synchronised with repository evolution.
