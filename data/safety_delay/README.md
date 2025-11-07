# Safety-Delay ΔAIC Ledger

The `data/safety_delay/` ledger records σ(β(R-Θ)) sweeps for the UTAC
safety-delay controller.  Each export is generated via
`python -m simulator.cli safety-delay` and contains:

- **CSV dataset** with parameter combinations, τ-delay measurements,
  ΔAIC values against linear/constant nulls, and resonance diagnostics.
- **Summary JSON** capturing aggregate τ-delay and ΔAIC statistics plus the
  sweep configuration.
- **Metadata JSON** describing the threshold parameters, impedance context
  ζ(R), preprocessing steps, and provenance hooks.

Use these artefacts to keep simulator presets, manuscripts, and codex
entries aligned on the same control membrane.  New exports must be
referenced in `seed/codexfeedback.*` and linked from the UTAC status matrix.
