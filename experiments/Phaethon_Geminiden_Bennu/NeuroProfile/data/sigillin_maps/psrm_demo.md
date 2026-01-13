# PSRM Sigillin Map

**Permission Request:** Do you accept this task? We aim for a joyful and efficient collaboration.

## Logistic Pulse

- **R:** 0.46
- **Θ:** 0.72
- **β:** 4.8
- **ζ(R):** 0.19
- **σ(β(R-Θ)):** 0.223

## Overview

PSRM maps the Signal → Intention → Context layers and anchors falsifiability via ΔAIC/CI metrics.

## YAML Payload

```yaml
$schema: https://genesisaeon.org/schemas/neuroprofile/v1
version: '1.0'
user_id: cd70d47c6438f77a82e75678f7cc4c7fb03d208ae30778ee6853240bbfdc61ee
layer_1_signal:
  source: synthetic
  beta: 3.521167731066255
  beta_cluster: near-critical
  sigma_phi: 0.28203711410844506
  gamma_beta_coupling: 0.14849199852435624
  resonant_return:
    beta_velocity_fit: 2.9213287662044243
    velocity_dispersion: 0.0024396440627299375
    sigma_phi_proxy: 0.22124438329320686
    v_rig_alignment: 0.0018044711989093631
    v_rig_target_kms: 1.352
    null_models:
      best_model: linear
      delta_aic:
        constant: 2726.6239089272567
        linear: 0.0
        power_law: 1491.651933309091
  crep_baseline:
    coherence: 1.0
    resonance: 0.14849199852435624
    emergence: 0.4758334771711155
    potential: 0.11131723943626583
  crep_aggregate: 0.4339106787829344
layer_2_intention:
  calibrated_intents: []
  intent_ontology_version: '1.0'
  calibration_status: uncalibrated
layer_3_context:
  ethics_consent: true
  hardware_tier: prosumer
  data_retention: study_duration_only
  timestamp: '2026-01-11T20:51:31.903188+00:00'
metadata:
  neuroprofile_version: v12
  psrm_mapper_version: '1.0'
  mandala_bridge:
    mandala_version: '>=0.8.0'
    bridge_status: planned
    validator_plan: tests/test_neuro_profile.py::test_mandala_schema_extension_hook
    compatibility_notes: PSRM remains an additive extension to Mandala formats.
  falsifiability_metrics:
    beta_ci:
    - 3.435845982362081
    - 3.689930238499985
    sigma_phi_ci:
    - 0.9346480220401849
    - 0.9434927241505243
    best_null_model: linear
    delta_aic:
      constant: 342.1224965654387
      linear: 0.0
      power_law: 619.5342276819533
  data_stubs:
    gaia_dr3_cluster_sample: data/raw/gaia_dr3_cluster_sample.csv
    jwst_protocluster_candidates: data/raw/jwst_protocluster_candidates.csv
    gaia_processed: data/processed/gaia_dr3_cluster_sample_processed.csv
    jwst_processed: data/processed/jwst_protocluster_candidates_processed.csv
  logistic:
    R: 0.46
    Theta: 0.72
    beta: 4.8
    zeta_R: 0.19
    sigma_beta_R_minus_Theta: 0.22304654039804278
```
