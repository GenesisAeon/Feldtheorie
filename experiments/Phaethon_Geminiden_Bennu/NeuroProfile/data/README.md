# NeuroProfile Data

- `raw/`: Rohdaten (EEG/MEG/Proxy-Streams, Gaia/JWST-Stubs)
- `processed/`: Vorverarbeitete Signale + v11-Proxys
- `synthetic/`: Synthetische Testdaten (z. B. 1 kHz EEG-Slices)
- `bootstrap_ledger.{md,json,yaml}`: v12-Datenledger (PhysioNet, BCI IV 2a, Cold-Start)
- `crep_null_model_ledger.{md,json,yaml}`: CREP-Nullmodell-Telemetrie
- `sigillin_maps/`: PSRM-Sigillin (YAML/JSON/MD) für Signal → Intention → Kontext
- `ethics_audit.log`: Audit-Trail für Ethics-Guard-Warnungen
- `results.json`: β/σΦ/Resonanz-Proxies mit ΔAIC/CI-Notizen + CREP

## v11-Provenance (R, Θ, β, ζ(R))

- **Gaia Stub:** `raw/gaia_dr3_cluster_sample.csv` → `processed/gaia_dr3_cluster_sample_processed.csv`
- **JWST Stub:** `raw/jwst_protocluster_candidates.csv` → `processed/jwst_protocluster_candidates_processed.csv`
- **Bootstrap-Stubs:** `raw/physionet_eeg_motor_imagery/`, `raw/bci_competition_iv_2a/`, `synthetic/cold_start/`
- **Logistik:** R≈0.46, Θ≈0.72, β≈4.8 halten σ(β(R-Θ)) auf der Steilflanke, ζ(R) bleibt über Audit-Logs und ΔAIC-Guards gedämpft.
