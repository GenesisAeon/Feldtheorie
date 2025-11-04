# Contributing Guide

## Development environment
1. Fork and clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   pip install -e .[dev]
   ```
3. Run the reproducibility harness:
   ```bash
   make lint test
   ```

## Coding standards
- Format Python code with `black` and lint with `ruff` (executed via `make lint`).
- Cover new functionality with `pytest` tests.  Targeted fixtures should record
the logistic quartet \((R, \Theta, \beta, \zeta(R))\) relevant to the feature.
- Prefer pure functions that expose deterministic interfaces, seeded via the
  shared `RANDOM_SEED` constant when stochasticity is unavoidable.

## Documentation standards
- Maintain the tri-layer cadence: formal mathematics, empirical evidence, and
  interpretive narrative clearly distinguished.
- When editing `docs/` or `paper/`, cross-reference the analysis script and
  dataset that support each claim.
- Keep metaphors in appendices or labelled sections so reviewers can focus on
the quantitative argument.

## Data contributions
- Submit new datasets under `data/<domain>/` with a matching
  `<name>.metadata.json` that satisfies `schemas/metadata.schema.json`.
- Document provenance, licensing, measurement methods, and null-model
  comparisons.
- Provide an accompanying analysis script or notebook that reproduces the
  logistic fit and exports JSON results.

## Pull request checklist
- [ ] Tests pass locally (`make test`).
- [ ] Linting passes (`make lint`).
- [ ] Documentation updated for new or changed functionality.
- [ ] ΔAIC comparisons reported for any new analysis.
- [ ] Seeds and environment details noted when introducing stochastic components.

## Communication
Open an issue before large changes so we can align on how the addition supports
the UTF logistic framework.  Cite relevant data files, notebooks, or simulator
presets to keep the resonance braid traceable.
