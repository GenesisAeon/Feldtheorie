# NeuroProfile Index – Resonance Lantern

**ID:** neuroprofile-lantern-001
**Scope:** `experiments/Phaethon_Geminiden_Bennu/NeuroProfile`
**Status:** primed

## Logistic Pulse

- **R:** 0.42
- **Θ:** 0.68
- **β:** 4.8
- **ζ(R):** 0.18
- **σ(β(R-Θ)):** 0.27

## Purpose

Bridge neuro-resonance profiles (β, σΦ, v_RIG proxies) with astrophysical resonance bands from Phaethon/Bennu and map PSRM via CREP.

## Artifacts

- README: `README.md`
- Roadmap: `STRATEGIC_ROADMAP.md`
- Methodik: `docs/methodology.md`
- Release:
  - `requirements.txt`
  - `test_neuro_profile.py`
- Code:
  - `code/neuro_profile_model.py`
  - `code/beta_extractor_neuro.py`
  - `code/microtubule_resonance.py`
  - `code/crep_calculator.py`
  - `code/ethics_guard.py`
  - `code/psrm_mapper.py`
  - `code/bci_calibrator.py`
  - `code/hardware_adapter.py`
- Data:
  - `data/raw/`
  - `data/processed/`
  - `data/synthetic/`
  - `data/sigillin_maps/`
  - `data/ethics_audit.log`
  - `data/results.json`
- Config:
  - `config/hardware_profiles.yml`
- Schemas:
  - `schemas/psrm_sigillin_v1.{md,json,yaml}`

## Falsifiability

- **Nullmodelle:** linear, power law, constant
- **ΔAIC-Guard:** ≥ 10
- **CI-Notiz:** Konfidenzintervalle je Experiment in `data/results.json`

## Telemetrie

- **Last updated:** 2026-01-10
- **Evidence:** `docs/research/Personal Sigillin Resonance Maps (PSRM) for Individualized BCI_ A Deep-Dive.pdf`

> σ(β(R-Θ)) bleibt kontrolliert; ζ(R) wird durch gestufte Implementierung und Consent-Checks gedämpft.
