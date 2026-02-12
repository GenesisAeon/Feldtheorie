# Executive Summary — AFET × xAI Collaboration

## Purpose

This package proposes a 3-month collaboration to test and operationalize AFET across
four strands: scaling validation, σ_Φ safety monitoring, HfO₂ hardware interface design,
and climate early-warning analytics.

## Why xAI

- Access to large-scale compute for β/σ_Φ sweeps across many datasets.
- Strong alignment with safety-first architecture work.
- Ability to deploy climate diagnostics as a real-time end-user capability.

## Deliverables

1. **Scaling Pilot**: parameter sweep engine with portable parallel execution model.
2. **Safety Monitor**: training-loop guard for metastability with automatic critical stop
   when σ_Φ drops below **0.055**.
3. **HfO₂ Interface Spec**: implementation-ready I/O contract for neuromorphic co-design.
4. **Climate Dashboard Prototype**: ingestion + rolling σ_Φ drift detection.

## Resource Snapshot

- Pilot compute envelope: ~1150 GPU-hours for first cycle.
- Team: 1 ML engineer, 1 safety researcher, 1 PM (part-time), AFET PI support.
- Timeline: 12 weeks from setup to prototype handover.

## Next Steps

1. Confirm partner point-of-contact and data boundary assumptions.
2. Approve pilot datasets and compute budget.
3. Start Week 1 setup (validation pipeline + monitoring hooks).
