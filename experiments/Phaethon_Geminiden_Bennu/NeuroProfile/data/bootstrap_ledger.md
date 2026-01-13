# NeuroProfile v12 Bootstrap Data Ledger

**Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.**

## Logistic Pulse

- **R:** 0.58
- **Θ:** 0.74
- **β:** 4.8
- **ζ(R):** 0.22
- **σ(β(R-Θ)):** 0.35

## Dataset Ledger

| ID | Source | Modality | Access Path | Use Case |
| --- | --- | --- | --- | --- |
| physionet-eeg-motor-imagery | PhysioNet EEG Motor Imagery | EEG | `data/raw/physionet_eeg_motor_imagery/` | Bootstrap baseline for PSRM |
| bci-competition-iv-2a | BCI Competition IV Dataset 2a | EEG | `data/raw/bci_competition_iv_2a/` | Cross-check hardware tiers |
| synthetic-cold-start | Synthetic cold-start generator | EEG (synthetic) | `data/synthetic/cold_start/` | Null-model calibration |

## Null-Model Guard

- **Models:** linear, power-law, constant
- **ΔAIC target:** ≥ 10
- **Bootstrap samples:** 200
- **CI requirement:** Log CI + bootstrap intervals in `data/results.json`

## Telemetry Storage

- Results: `data/results.json`
- CREP ledger: `data/crep_null_model_ledger.{md,json,yaml}`

## Evidence Hooks

- `docs/notes/v12Grundlagen.txt`
- `docs/notes/implementierungsvorschlaege_fuer_codex.txt`
- `docs/research/Personal Sigillin Resonance Maps (PSRM) for Individualized BCI_ A Deep-Dive.pdf`

> σ(β(R-Θ)) bleibt auf der Steilflanke, weil der Bootstrap-Ledger die Nullmodelle
> bindet und ζ(R) über klare Provenance gedämpft wird.
