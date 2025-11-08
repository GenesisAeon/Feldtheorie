# Simulator Interface Loom

## RepoPlan 2.0 Mandate
The `simulator/` loom translates threshold-field equations into tactile experience.  Interfaces must expose live controls for $R$, $\Theta$, $\beta$, and impedance switches $\zeta(R)$, letting participants witness the logistic resonance $\sigma(\beta(R-\Theta))$ ignite as thresholds are crossed.

## Tri-layer Cadence
- **Formal:** implement deterministic + stochastic toggles derived from the UTF equations and membrane boundary conditions.
- **Empirical:** synchronise the UI with datasets from `analysis/`, enabling users to replay observed transitions and compare them with simulated runs.
- **Metaphorical:** choreograph visuals and audio so that the threshold crossing feels like membranes humming into coherence.

## Laufender Stand (Oktober 2025)
- Die Vite/React-Anwendung (`npm install`, `npm run dev`) stellt den
  **Transdisziplinären Schwellenfeld-Simulator** bereit und synchronisiert das
  universelle Quartett $(R, \Theta, \beta, \zeta(R))$ in Echtzeit.
- Presets aus `simulator/presets/*.json` spiegeln die Fits in `analysis/results/*.json`
  inklusive ΔAIC/$R^2$-Metadaten und tri-layer Narrativen.
- Poetik-Modus zieht direkt die in `Docs/` kuratierten Metaphern heran, sobald
  $R$ die Schwelle $\Theta$ überschreitet.

## Immediate Construction Lines
1. Ergänze automatisierte Checks, die Preset-IDs und Parameter mit
   `docs/resonance-bridge-map.md` spiegeln.
2. Verbinde Solver-Ströme aus `models/` (z.B. `membrane_solver.py`) via API,
   sodass reale Membranläufe die UI treiben.
3. Erweitere das Test-Setup: `npm run build` + visuelle Regression, sobald
   weitere Interaktionspfade landen.

## CLI Hooks
- `python -m simulator.cli safety-delay --replicates 3 --emit-analysis`
  - startet σ(β(R-Θ))-Sweeps mit Replikaten über `analysis/safety_delay_sweep.py`
  - exportiert ΔAIC-Ledger nach `data/safety_delay/` (CSV + Summary + Metadata)
  - optional: legt das vollständige Payload erneut in `analysis/results/` ab
- Outputs dienen als Bedeutungs-Sigillin für Simulator-Presets: Parameter, ΔAIC,
  Meta-Resonanz (Kontrollzentralität × CREP) und Zeitverläufe können direkt in
  UI-Module gespiegelt werden.
