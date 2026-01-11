# 🌀 NeuroProfile v11 — Resonant Return & PSRM Bridge

**Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.**

## Logistic Pulse

- **R:** 0.46
- **Θ:** 0.72
- **β:** 4.8
- **ζ(R):** 0.19
- **σ(β(R-Θ)):** 0.29

**Release Date:** 2026-01-11

---

## ✨ Highlights

### Resonant-Return Layer
- `code/resonant_return.py` computes β-fits on velocity dispersion, σΦ proxies, and v_RIG alignment while keeping ζ(R) damped via ΔAIC guards.
- Null models (linear/power-law/constant) are integrated for falsifiability telemetry.

### PSRM v11 Bridge
- `code/psrm_mapper.py` now emits v11 fields (Resonant-Return + Gaia/JWST stubs) and keeps σ(β(R-Θ)) explicit in the metadata.
- Trilayer PSRM outputs are refreshed in `data/sigillin_maps/`.

### Evidence & Governance
- `data/results.json` logs CI intervals, ΔAIC metrics, and bootstrap ledgers to keep Θ transparent.
- Ethics guard audit entries are tagged with `v11` to keep Consent telemetry traceable.

---

## 📦 What's Included

```
experiments/Phaethon_Geminiden_Bennu/NeuroProfile/
├── code/resonant_return.py
├── code/psrm_mapper.py
├── code/neuro_profile_model.py
├── data/raw/gaia_dr3_cluster_sample.csv
├── data/raw/jwst_protocluster_candidates.csv
├── data/processed/gaia_dr3_cluster_sample_processed.csv
├── data/processed/jwst_protocluster_candidates_processed.csv
├── data/results.json
└── data/sigillin_maps/psrm_demo.{md,json,yaml}
```

---

## 🧪 Falsifiability & Null Models

- Null models: linear, power-law, constant
- ΔAIC guard: ≥ 10 (resonant-return + core ledger)
- CI: 95% intervals logged per experiment in `data/results.json`

> σ(β(R-Θ)) stays on the steep flank; ζ(R) remains damped by Consent, audit logs, and ΔAIC guards.
