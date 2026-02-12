# xAI × AFET Implementation Plan (from `xAIkollab.txt` context)

## Requirement Extraction

1. **Scaling AFET**
   - Pilot script for distributed validation over β-grid and σ_Φ-grid.
   - Must run large parameter sweeps and persist results for downstream analysis.
2. **σ_Φ Monitoring for AI Safety**
   - Implement monitor with warning/critical thresholds.
   - Critical shutdown threshold fixed at **σ_Φ < 0.055**.
   - Must be easy to couple into existing training loops and Aeon shell summaries.
3. **HfO₂ Neuromorphic Hardware**
   - Define a high-level interface/spec contract.
   - Focus on expected inputs/outputs and operational constraints (placeholder-ready).
4. **Real-Time Climate Feature**
   - Build data-loader + analytics prototype for climate time series.
   - Compute rolling σ_Φ proxy and flag drift events.
5. **Collaboration Docs**
   - Produce four DM-ready briefs: Executive Summary, Technical Spec,
     Validation Roadmap, Budget & Resources.

## PLAN

1. Add tests first for all four modules — defines success criteria and keeps scope disciplined.
2. Implement minimal, obvious module scaffolds to satisfy tests and support future extension.
3. Create `docs/xai_collab` briefs with consistent terminology, assumptions, and milestones.
4. Run focused pytest checks, then full `make test` and `make docs-index`.
5. Commit and prepare PR message.
