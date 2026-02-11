# AFET/Feldtheorie Roadmap Q1 2026

## Week 2: CLIP Validation + Quantum Exploration (Feb 10-16)

### Must-Have
- **CLIP validation** (`experiments/week2/clip_validation.py`) — replace numpy fallback with real CLIP, generate sigma_Phi distributions
- **Multimodal stress test** (`experiments/week2/multimodal_stress_test.py`) — 5 adversarial scenarios, detection accuracy metrics
- **Grok bridge** (`integration/grok_bridge/`) — per-layer sigma_Phi monitoring, safety hooks, metrics collection

### Should-Have
- **Quantum decoherence** (`experiments/week2/quantum_decoherence.py`) — Qiskit/classical simulation, tau_dec to sigma_Phi mapping
- **Quantum AFET theory** (`theory/quantum_afet.py`) — sigma_Phi_q = (hbar/kT) * (1/tau_dec)

## Week 3: Federated Learning + Hardware Specs (Feb 17-23)

### Should-Have
- **Federated simulation** (`experiments/week3/federated_simulation.py`) — 5-client federation, weighted median consensus
- **HfO2 spec** (`hardware/neuromorphic/hfo2_detailed_spec.py`) — manufacturing-ready design docs, BOM, protocol

## Week 4-5: Production Integration (Feb 24 - Mar 9)

### Nice-to-Have
- **Aeon-Lantern production coupler** — Phase 2 (recursive engine) + Phase 3 (shadow integration)
- **Climate dashboard v2** (`analysis/climate_dashboard_v2.py`) — per-system sigma_Phi tracking
- **Integration kits** (`partnerships/integration_kits/`) — PyTorch Lightning, HuggingFace callbacks

## Month 2: Publications + Partnerships (Mar-Apr)

- **AFET validation paper** (`papers/afet_validation_nature.md`) — Nature/Science submission
- **Quantum AFET paper** (`papers/quantum_afet_prl.md`) — PRL short communication
- **CI/CD pipelines** — automated testing, docs, releases
