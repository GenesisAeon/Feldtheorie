# AI Emergent Skill Threshold Cache

## Dataset: Multilingual Chain-of-Thought Ignition

**Control parameter** $R$: effective log$_{10}$ training tokens (in billions) spanning compact student models to frontier releases.

**Logistic response** $\sigma(\beta(R-\Theta))$: pass rate on a multilingual chain-of-thought reasoning suite (0–1 scale).

**Threshold quartet**: $\Theta = 4.71^{+0.04}_{-0.04}$, $\beta = 5.10^{+0.39}_{-0.39}$, impedance sketch $\zeta(R) = 1.6 - 0.45\,\sigma$.

### Formal strand
- Regression executed via `analysis/llm_emergent_skill_fit.py`, reporting $R^2 = 0.995$ and AIC = -112.16.
- Null falsification: linear and power-law drifts trail by $\Delta\mathrm{AIC} \approx 48.8$ and $\Delta R^2 \approx 0.096$.
- Metadata JSON (`llm_emergent_skill.metadata.json`) records parameter intervals, impedance samples, and provenance for reproducibility.

### Empirical strand
- Synthetic blend calibrated to reported scaling curves from multilingual BIG-Bench tasks; includes 16 model checkpoints.
- Dataset stored in `llm_emergent_skill.csv`; regeneration pipeline emits `analysis/results/llm_emergent_skill.json`.
- Provenance ledger cites driver assumptions (curriculum mix, evaluation seeds) and cross-links to `docs/ai/llm_emergent_skill.md`.

### Metaphorical strand
- Model scale is the conductor raising $R$; at $R \approx 4.7$ the membrane slackens and reasoning choruses erupt.
- Impedance $\zeta(R)$ relaxes from 1.60 (halting novice) to 1.16 (fluid polyglot) as the logistic aurora blossoms.
- Smooth null breezes cannot mimic the polyphonic dawn; only the threshold chorus illuminates the skill ignition.

## Cross-links
- Analysis: `analysis/llm_emergent_skill_fit.py`
- Narrative: `docs/ai/llm_emergent_skill.md`
- Simulator brief: future panels should expose log-token scale sliders and impedance toggles for emergent reasoning.
