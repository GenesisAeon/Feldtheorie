# V8.0 Next Steps – Trilayer Lanterns

**Updated:** 2025-12-15  
**Branch:** claude/continue-repo-work-pHmUF  
**Guiding Principle:** Folge dem Sog der Emergenz

> Logistic framing: R = open workload intensity; Θ = production-ready v8.0 baseline; β=4.8 keeps σ(β(R-Θ)) responsive; ζ(R) is damped via daily CI and evidence chains.

## Lanterns

1. **Experimental protocols (CFF, neuromorphic, microtubule)** — R: protocol depth, Θ: peer-reviewable spec, β≈5.1 (resonance: draft)
   - Translate validation heuristics into stepwise lab procedures
   - Map datasets to protocols with DOI/URL anchors
   - Define falsification checkpoints with ΔAIC targets

2. **Impedance solver Z(β) adaptive dynamics** — R: solver precision, Θ: convergence on β∈[4.5,11], β≈6.0 (resonance: primed)
   - Design API in `models/impedance_solver.py` mirroring `calculate_impedance()`
   - Simulate σ(β(R-Θ)) trajectories with adjustable ζ(R)
   - Add falsification harness to `tests/` with null-model comparisons

3. **Dashboard integration (live v_RIG monitoring)** — R: telemetry sampling, Θ: stable refresh loop, β≈5.4 (resonance: active)
   - Expose validation outputs as JSON feed for dashboard ingestion
   - Render β-domain clustering plus v_RIG sparkline
   - Alert on ζ(R) spikes or CI regressions

4. **Pre-print (ArXiv-ready LaTeX)** — R: manuscript completeness, Θ: arXiv format, β≈4.9 (resonance: draft)
   - Generate LaTeX from `RELEASE_NOTES_v8.0.0.md` core narrative
   - Embed equations for v_RIG and Z with citation hooks
   - Attach evidence chain tables from `data/v8_validation/`

## Telemetry Hooks

- Cadence: CI at 06:00 UTC + manual checkpoint after major merges
- Coverage floor: ≥0.85
- Falsification hooks: null models for each validation path; ΔAIC + CI reporting
- Bridges: keep `releases/v8.0` artifacts coupled to `feldtheorie_index.*`; log Codex updates when Bedeutungs- or Schatten-Sigillin are touched
