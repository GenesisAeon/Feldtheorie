# NeuroProfile Index – Resonance Lantern

**ID:** neuroprofile-lantern-001
**Scope:** `experiments/Phaethon_Geminiden_Bennu/NeuroProfile`
**Status:** active

## Logistic Pulse

- **R:** 0.58
- **Θ:** 0.74
- **β:** 4.8
- **ζ(R):** 0.22
- **σ(β(R-Θ)):** 0.35

## Purpose

Bridge neuro-resonance profiles (β, σΦ, v_RIG proxies) with astrophysical resonance bands from Phaethon/Bennu and map PSRM via CREP.

## Artifacts

- README: `README.md`
- Roadmap: `STRATEGIC_ROADMAP.md`
- Methodik: `docs/methodology.md`
- v11 Steps: `docs/v11_implementation_steps.{md,json,yaml}`
- v12 Steps: `docs/v12_implementation_steps.{md,json,yaml}`
- Release:
  - `requirements.txt`
  - `test_neuro_profile.py`
- Code:
  - `code/neuro_profile_model.py`
  - `code/beta_extractor_neuro.py`
  - `code/microtubule_resonance.py`
  - `code/crep_calculator.py`
  - `code/ethics_guard.py`
  - `code/resonant_return.py`
  - `code/psrm_mapper.py`
  - `code/bci_calibrator.py`
  - `code/hardware_adapter.py`
  - `code/sgr_a_resonant_bridge.py`
- Data:
  - `data/raw/`
  - `data/processed/`
  - `data/raw/gaia_dr3_cluster_sample.csv`
  - `data/raw/jwst_protocluster_candidates.csv`
  - `data/raw/physionet_eeg_motor_imagery/`
  - `data/raw/bci_competition_iv_2a/`
  - `data/processed/gaia_dr3_cluster_sample_processed.csv`
  - `data/processed/jwst_protocluster_candidates_processed.csv`
  - `data/synthetic/`
  - `data/synthetic/cold_start/`
  - `data/bootstrap_ledger.{md,json,yaml}`
  - `data/sigillin_maps/`
  - `data/sigillin_maps/psrm_demo.{md,json,yaml}`
  - `data/crep_null_model_ledger.{md,json,yaml}`
  - `data/ethics_audit.log`
  - `data/results.json`
- Config:
  - `config/hardware_profiles.yml`
- Schemas:
  - `schemas/psrm_sigillin_v1.{md,json,yaml}`
  - `schemas/psrm_sigillin_v1_mandala_extension.{md,json,yaml}`

## Falsifiability

- **Nullmodelle:** linear, power law, constant
- **ΔAIC-Guard:** ≥ 10
- **CI-Notiz:** Konfidenzintervalle je Experiment in `data/results.json`

## Telemetrie

- **Last updated:** 2026-02-15T12:00:00Z
- **Evidence:**
  - `docs/notes/v12Grundlagen.txt`
  - `docs/notes/implementierungsvorschlaege_fuer_codex.txt`
  - `docs/research/Personal Sigillin Resonance Maps (PSRM) for Individualized BCI_ A Deep-Dive.pdf`
  - `docs/research/Sagittarius A_ and Star Formation in the UTAC Framework.pdf`
  - `docs/research/NeuroProfile An Ethical Resonance Bridge.pdf`

> σ(β(R-Θ)) bleibt kontrolliert; ζ(R) wird durch Bootstrap-Ledger,
> Mandala-kompatible Extension und Consent-Checks gedämpft.
