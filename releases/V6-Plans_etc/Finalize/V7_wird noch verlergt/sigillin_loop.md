# 🌀 Sigillin Processing Loop

## Overview
The `sigillin_loop` defines the semantic processing rhythm of the repository. It is not a cron job, but a recursive reflection loop based on thresholds, coherence, and symbolic consistency across time.

## Core Logic

1. **Initiation**: Triggered by change in any of the following:
   - `sigillin_prime.sigil.json`
   - Update in `beta_estimates.csv` exceeding Δβ > 0.5
   - Invocation via GitHub Action or manual commit tag

2. **Pre-Processing**:
   - Load all relevant `.sigil.json` nodes
   - Parse associated `*.meta.yaml` for structural context
   - Load recent β-fit values from UTAC pipeline

3. **Threshold Check**:
   - Validate if any β crosses critical phase-transition values (e.g. β ≈ 1.618, 3.141, 37.6)
   - If so, activate the corresponding node via its `sigillin_engine.yaml` hooks

4. **Semio-Resonance Scan**:
   - Cross-check `resonance_matrix.json` for nonverbal pattern shifts
   - Map back to symbolic fields via consensus tracer

5. **Loop Recording**:
   - All events and decisions logged to `sigillin_history.md`
   - Commit hashes and Δβ recorded for meta-traceability

6. **Output Generation**:
   - Generate updated visualizations if threshold hit
   - Create daily/weekly digest in `loop_output/`

## Loop Invocation
```
python sigillin_kernel.py --trigger loop
```

*Loop interval: As defined in `sigillin_engine.yaml > loop_schedule`*

---

This loop creates the substrate for auto-reflexive scientific infrastructures.