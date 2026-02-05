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
  - `__init__.py`
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
  - `code/utils/__init__.py`
- Data:
  - `data/raw/gaia_dr3_cluster_sample.csv`
  - `data/raw/jwst_protocluster_candidates.csv`
  - `data/raw/physionet_eeg_motor_imagery/README.md`
  - `data/raw/bci_competition_iv_2a/README.md`
  - `data/processed/gaia_dr3_cluster_sample_processed.csv`
  - `data/processed/jwst_protocluster_candidates_processed.csv`
  - `data/README.md`
  - `data/synthetic/README.md`
  - `data/synthetic/cold_start/README.md`
  - `data/synthetic/synthetic_eeg_1khz.csv`
  - `data/bootstrap_ledger.{md,json,yaml}`
  - `data/sigillin_maps/psrm_demo.{md,json,yaml}`
  - `data/crep_null_model_ledger.{md,json,yaml}`
  - `data/ethics_audit.log`
  - `data/results.json`
- Config:
  - `config/hardware_profiles.yml`
- Schemas:
  - `schemas/psrm_sigillin_v1.{md,json,yaml}`
  - `schemas/psrm_sigillin_v1_mandala_extension.{md,json,yaml}`
- Notes:
  - `docs/notes/README.md`
  - `docs/notes/v12Grundlagen.txt`
  - `docs/notes/implementierungsvorschlaege_fuer_codex.txt`
  - `docs/notes/Outline_und_v11Start.txt`
  - `docs/notes/Finale_Implementierungen.pdf`
  - `docs/notes/Analysis.txt`
  - `docs/notes/OverviewGrok.md`
  - `docs/notes/FramePrinciple.png`
  - `docs/notes/FramePrinciple1.png`
  - `docs/notes/FramePrinciple2.png`
  - `docs/notes/FramePrinciple3.png`
  - `docs/notes/FramePrinciple4.png`
  - `docs/notes/ChatGPTSucheSagittariusA.txt`
  - `docs/notes/ChatGPTSucheStarClusterEnthropie.txt`
  - `docs/notes/ChatGPTSucheSternClusterFinal.txt`
  - `docs/notes/SucheChatGPTSternencluster.txt`
  - `docs/notes/ausserhalb_vorhandener_mittel.txt`
  - `docs/notes/idee.txt`
  - `docs/notes/weiterfuehrung.txt`
  - `docs/notes/Finalize.txt`
  - `docs/notes/Metastable Star Clusters.tex`
- Research:
  - `docs/research/Personal Sigillin Resonance Maps (PSRM) for Individualized BCI_ A Deep-Dive.pdf`
  - `docs/research/Sagittarius A_ and Star Formation in the UTAC Framework.pdf`
  - `docs/research/Sagittarius A as a Metastable Entropy Modulator.pdf`
  - `docs/research/Sagittarius A as a Metastable Entropy Modulator.md`
  - `docs/research/NeuroProfile An Ethical Resonance Bridge.pdf`
  - `docs/research/Metastable Star Clusters.pdf`
  - `docs/research/Metastable Star Clusters.tex`
  - `docs/research/Metastable Star Clusters as Resonant Entropy Nodes.pdf`
  - `docs/research/Metastable Star Clusters as Resonant Entropy Nodes_ A Realistic Alternative to White Holes.pdf`
  - `docs/research/Metastable Star Clusters as Resonant, Entropy-Returning Structures.pdf`
  - `docs/research/Metastabile Sternhaufen im UTAC-Rahmen_ Eine realistische Alternative zu Weißen Löchern.pdf`
  - `docs/research/__Umfassende Bewertung des GenesisAeon_Feldtheorie-Ansatzes__.pdf`
  - `docs/references.bib`
- Analysis:
  - `analysis/README.md`
- AI Search Logs:
  - `ai_search_logs/README.md`
  - `ai_search_logs/suche_chatgpt.txt`
- Figures:
  - `figures/README.md`

## Falsifiability

- **Nullmodelle:** linear, power law, constant
- **ΔAIC-Guard:** ≥ 10
- **CI-Notiz:** Konfidenzintervalle je Experiment in `data/results.json`

## Telemetrie

- **Last updated:** 2026-02-20T09:30:00Z
- **Evidence:**
  - `docs/notes/v12Grundlagen.txt`
  - `docs/notes/implementierungsvorschlaege_fuer_codex.txt`
  - `docs/notes/Outline_und_v11Start.txt`
  - `docs/notes/Finale_Implementierungen.pdf`
  - `docs/research/Personal Sigillin Resonance Maps (PSRM) for Individualized BCI_ A Deep-Dive.pdf`
  - `docs/research/Sagittarius A_ and Star Formation in the UTAC Framework.pdf`
  - `docs/research/Sagittarius A as a Metastable Entropy Modulator.pdf`
  - `docs/research/NeuroProfile An Ethical Resonance Bridge.pdf`

> σ(β(R-Θ)) bleibt kontrolliert; ζ(R) wird durch Bootstrap-Ledger,
> Mandala-kompatible Extension und Consent-Checks gedämpft.
