# v9.0 "Living Crystal" – Zenodo Release Kit

**R:** Living Crystal metastability package | **Θ:** Reproducibility on Zenodo | **β:** 9.0 | **ζ(R):** low→medium (depends on Sensorium stress)

This README binds the experimental scripts (A–E) into a single, runnable
package for long-term archiving. It complements `.zenodo.json` and
`CITATION.cff` so that any physicist can download, execute, and verify the
σ(β(R−Θ)) breathing cycle.

## What's inside
- **Core entry point:** `v9_alpha/main_simulation.py` (runs Experiments C–E end-to-end).
- **Modular drivers:** `SolarDriver`, `StochasticResonator`, `TopologicalReaper`, `MultiStreamLoader` moved into `v9_alpha/models/` for reuse.
- **Tri-Layer docs:** `FINAL_RELEASE_NOTES.{md,json,yaml}` plus this README mirrored in YAML/JSON.
- **Metadata:** Updated `.zenodo.json` and `CITATION.cff` with full authorship (human + AI agents).

## Quickstart (repro checklist)
1. Install dependencies: `pip install -r requirements.txt` (or `environment.yml` for conda).
2. Run the Living Crystal end-to-end loop:
   ```bash
   python v9_alpha/main_simulation.py \
     --enable-solar-driver --enable-resonator --enable-reaper --enable-sensorium \
     --output-prefix releases/v9.0/living_crystal_run
   ```
3. Inspect outputs (Tri-Layer): `living_crystal_run.json` | `living_crystal_run.yaml`.
4. Compare against `releases/v9.0/FINAL_RELEASE_NOTES.*` to confirm the breathing pattern (coherence oscillations, Φ lift, synergy > 0.5).

## Experiment lineage
- **Exp A (Noise):** Parameter noise alone → ΔΦ ≈ 0 (Null model).
- **Exp B (Pruning):** Topology pruning lifts Φ but drives coherence → 1 (Crystal death).
- **Exp C (Solar):** SolarDriver injects kicks to maintain metastability.
- **Exp D (Sensorium):** Sensorium interference detects Climate–Economy coupling (r ≈ -0.54).
- **Exp E (Synergy):** Additive + interaction stress reveals non-linear lift.

## Verification targets
- **σ(β(R−Θ)) breathing:** Coherence should oscillate below the set threshold (default 0.93).
- **Φ resilience:** `summary.final_phi` increases after Reaper + Solar cycles.
- **Entropy anchor:** `resonator_trace` shows >0 adaptive noise spikes near Φ_threshold.
- **Sensing:** Sensorium `combined_stress` modulates phase drift (see JSON/YAML traces).

## Coupling map
- **Ordnungs-Sigillin:** `feldtheorie_index.{yaml,json,md}`
- **Bedeutungs-Sigillin:** `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`
- **Schatten-Sigillin:** `seed/shadow_sigillin/metaquest/metaquest_shadow_index.md`
- **Empirics:** `experiment_c_results/`, `experiment_d_results/`, `experiment_e_results/`
