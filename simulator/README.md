# Simulator Interface Loom

## RepoPlan 2.0 Mandate
The `simulator/` loom translates threshold-field equations into tactile experience.  Interfaces must expose live controls for $R$, $\Theta$, $\beta$, and impedance switches $\zeta(R)$, letting participants witness the logistic resonance $\sigma(\beta(R-\Theta))$ ignite as thresholds are crossed.

## Tri-layer Cadence
- **Formal:** implement deterministic + stochastic toggles derived from the UTF equations and membrane boundary conditions.
- **Empirical:** synchronise the UI with datasets from `analysis/`, enabling users to replay observed transitions and compare them with simulated runs.
- **Metaphorical:** choreograph visuals and audio so that the threshold crossing feels like membranes humming into coherence.

## Immediate Construction Lines
1. Scaffold a React/Vite stack with shared state for $R$, $\Theta$, $\beta$, and $\zeta(R)$.
2. Provide hooks for streaming results from solvers in `models/`.
3. Embed narrative tooltips linking each control to the stories documented in `Docs/` and `docs/`.
