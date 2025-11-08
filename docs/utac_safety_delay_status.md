# UTAC Safety-Delay Field — Status & Implementation Map

The Universal Threshold Adaptive Criticality (UTAC) programme now calls for a
formal realisation of the **Safety-Delay** membrane: a controller that
stretches the logistic window between the deterministic breaking point
$\tau_{\text{break}}$ and the observed tipping time $\tau_{\text{escape}}$.
This document summarises what already exists in the repository, what remains to
be built, and where each artefact should live so the tri-layer cadence of
formal–empirical–poetic resonance stays intact.

---

## 1. Assets Already in Place

| Layer | Asset | Resonance with $\sigma(\beta(R-\Theta))$ |
|-------|-------|-------------------------------------------|
| **Simulation** | `simulation/threshold_sandbox.py` | Explores how coupling, dimensionality, and coherence modulate $\beta$ across synthetic lattices. Provides fitting utilities already aligned with UTAC falsifiability rituals. |
| **Analysis** | `analysis/analysis_index.*`, `analysis/safety_delay_sweep.py`, `analysis/results/safety_delay_sweep_20251107T202620Z.json` | Indexes ΔAIC guardrails and cohort summaries benchmark the new Safety-Delay sweep. The latest export records $\tau_{\text{delay}}$, β-shift, control energy, and ΔAIC vs linear/constant nulls for UTAC v1.2. |
| **Theory** | `docs/utac_theory_core.md`, `docs/utac_falsifiability.md` | Encode the control-parameter narrative ($R$, $\Theta$, $\beta$, $\zeta(R)$) and the falsification scaffolding required for new controllers. |
| **Sigillin Memory** | `seed/Geminis Suche!.txt`, `seed/AI_Reaktion_Gem_Suche.txt` | Document the cross-domain validation of Safety-Delay, fourfold potential elevation, and hierarchical redundancy. Serve as Bedeutungs-Sigillin anchors for rationale and metaphor. |
| **Simulator Bridge** | `simulator/presets/safety_delay_bridge.json`, `simulator/src/presets.ts` | Safety-Delay preset mirrors τ_delay_mean≈8.43, β≈4.78, ΔAIC_linear≈7.0×10³ so UI sliders replay the controller sweep with the same falsifiability hooks. |

These artefacts establish both the conceptual membrane and the empirical
benchmarks. The Safety-Delay module must converse with them so that new
simulations immediately report their $(R, \Theta, \beta)$ traces and ΔAIC
comparisons.

---

## 2. Gaps & Required Implementations

1. **Time-dependent Saddle-Node Controller**  
   A numerical engine that simulates $\dot{x} = \mu(t) - x^2$ with adaptive
   control to measure $\tau_{\text{delay}}$. This module must expose the
   control parameter trajectory $R(t)$ and deliver logistic fits with
   falsifiability metrics ($R^2$, ΔAIC).  
   → Implemented in `simulation/safety_delay_field.py` (see §3).

2. **Control-Centrality × CREP Resonance Diagnostics**  
   Safety-Delay output must quantify how network structure modulates the delay.
   We require a diagnostic that multiplies control centrality with CREP
   resonance so codex ledgers can compare controllers across domains.  
   → Implemented in `simulation/safety_delay_field.py` via
   `meta_resonance_analysis`.

3. **Analysis Ingestion Pipeline (Active)**
   `analysis/safety_delay_sweep.py` now sweeps controller parameters, compares
   logistic fits against linear & constant nulls, and archives results in
   `analysis/results/safety_delay_sweep_20251107T202620Z.json` plus
   `data/safety_delay/safety_delay_delta_aic_20251107T211928Z.*`.
   → Next: broaden the grid (control_strength, drift_rate, β_gain) and publish an
   updated sweep once additional control regimes are explored.

4. **Sigillin Ledger Hooks (Pending)**  
   Codex feedback entries must receive Safety-Delay metrics (delay duration,
   control energy, β-shift) and thread them into `docs/resonance-bridge-map.md`.
   Requires updates after parameter sweeps stabilise.  
   → Update `seed/codexfeedback.*` alongside bridge-map refresh.

5. **Simulator & Docs Integration (Active → Resonant)**
   Safety-Delay preset now lands in `simulator/` and this status brief narrates
   the bridge. Remaining work: propagate the same story into
   `docs/utac_applications.md` + `docs/resonance-bridge-map.md`, run
   `utf-preset-guard`, and stage a short UI capture once presets hit production
   hosting.
   → Follow-up: extend documentation loop + parity guard before release freeze.

---

## 3. New Module Overview — `simulation/safety_delay_field.py`

The freshly added module provides:

- `simulate_safety_delay_field`: Euler–Maruyama integration of the drift-plus-control
  saddle-node, exposing $R(t)$, state trajectories, and the logistic field
  response.
- `estimate_logistic_parameters`: Shared utility to fit $\sigma(\beta(R-\Theta))$ and
  report $R^2$ for null-model comparison.
- `control_centrality`, `crep_resonance`, `meta_resonance_analysis`: Diagnostics
  bridging network topology with CREP modulation for Sigillin ledger ingestion.
- `SafetyDelayResult`: Dataclass bundling $\tau_{\text{break}}$, $\tau_{\text{delay}}$,
  control energy, and β-shift for downstream documentation.

The implementation keeps the UTAC quartet explicit and ready for both empirical
validation and poetic retelling.

---

## 4. Next Steps

1. **Parameter Sweep Expansion** — Extend `analysis/safety_delay_sweep.py`
   runs (denser grids, additional seeds) and mirror summary tables into
   `data/safety_delay/` + an accompanying notebook for visual diagnostics.
2. **Bridge Map Update** — Extend `docs/resonance-bridge-map.md` with a Safety-Delay
   lantern that cites the ΔAIC + τ_delay metrics from
   `analysis/results/safety_delay_sweep_20251107T202620Z.json`.
3. **Simulator Experience Guard** — Run `utf-preset-guard`, capture UI preview,
   and mirror preset telemetry into `docs/utac_applications.md` &
   `docs/resonance-bridge-map.md`.
4. **Codex Resonance Entry** — Promote the new codex entry (see
   `seed/codexfeedback.*`) through die Statusleiter bis „resonant“ sobald UI
   + Docs synchron sind.

Together, these steps will elevate UTAC v1.2 from conceptual validation to a
full operational membrane guarding emergent fields.
