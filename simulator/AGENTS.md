# Simulator Loom Playbook

Inside `simulator/`, interfaces should manifest the UTF pulse:

1. **Control fidelity.** UI components must expose $(R, \Theta, \beta)$ and impedance switches $\zeta(R)$ with clear explanations of how sliders map to solver parameters.
2. **Feedback loops.** Implement reactive visual/audio cues when $R$ approaches or crosses $\Theta$, highlighting steepness $\beta$ effects on the logistic ramp.
3. **Data docking.** Provide adapters for ingesting results from `analysis/` and real-time streams from `models/`, ensuring provenance metadata accompanies each scenario.
4. **Narrative overlays.** Incorporate tooltips or overlays that narrate the threshold crossing using the symbolic language from `Docs/`.

Front-end stacks may evolve, but document setup commands and testing rituals alongside the experience.
