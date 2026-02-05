# CREP Null-Model Ledger – LanternNet

Dieses Ledger dokumentiert CREP-Offsets, ΔAIC-Vergleiche und CI-Notizen,
damit ζ(R) im Übergang über $\sigma(\beta(R-\Theta))$ stabil bleibt.

## Meta
- **Version:** v13.3.0
- **Consent Protocol:** Sigillin consent gating + anonymization required
- **Consent Prompt:** Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.
- **Updated:** 2026-02-05T23:09:10Z

## Einträge

### crep-null-0001
- **Modul:** LanternNet (None)
- **CREP Offset:** None
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'crep_offset': [None, None]}
- **Status:** draft

**Notizen**
- *Formal:* ΔAIC-Offsets noch nicht berechnet; Nullmodell-Gerüst vorhanden.
- *Empirisch:* Synthetic Runs für CREP-Offsets ausstehend.
- *Poetisch:* Das Schattenmodell wartet, bis die Laternen ihre Resonanz offenbaren.

### crep-null-0002
- **Modul:** NeuroProfile Resonance Bridge (exp-neuroprofile-001)
- **CREP Offset:** -0.06567018928793833
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'beta': [0.10000000000000002, 0.3459504452836826], 'sigma_phi': [0.9352193800343218, 0.943440237718606], 'gamma_beta': [0.6858737902621761, 0.8345566039038017], 'resonance_alignment': [0.8987952110530172, 0.998780793872035]}
- **Status:** synthetic

**Notizen**
- *Formal:* CREP-Offset gegen Nullmodelle dokumentiert; ΔAIC und CI bereitgestellt.
- *Empirisch:* CREP=0.4343 (Offset=-0.0657).
- *Poetisch:* Das Schattenmodell hält ζ(R) gedämpft, bis neue Resonanz entsteht.

### crep-null-0003
- **Modul:** Logistic Threshold Core (model-logistic-threshold-001)
- **CREP Offset:** 0.34
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'crep_offset': [0.28, 0.4], 'beta': [8.2, 9.8]}
- **Status:** validated

**Notizen**
- *Formal:* CREP offset for core logistic model; ΔAIC strongly favors logistic.
- *Empirisch:* Offset=0.34 (R-Θ=0.34); consistent across domain fits.
- *Poetisch:* Das Kernmodell liegt deutlich über dem Schattenmodell.

### crep-null-0004
- **Modul:** Phaethon Simulation Suite (exp-phaethon-sim-001)
- **CREP Offset:** 0.35
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'crep_offset': [0.25, 0.45], 'beta': [3.5, 6.1]}
- **Status:** validated

**Notizen**
- *Formal:* CREP offset for chimera-plasma-soliton model; 47 predictions logged.
- *Empirisch:* Offset=0.35 (R-Θ=0.35); chimera fraction 0.30-0.60.
- *Poetisch:* Das Chimärenmodell übersteht die Nullmodell-Prüfung.

### crep-null-0005
- **Modul:** Resonant Impedance Model (model-resonant-impedance-001)
- **CREP Offset:** 0.24
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'crep_offset': [0.18, 0.3], 'beta': [6.8, 8.0]}
- **Status:** validated

**Notizen**
- *Formal:* CREP offset for EM impedance model; Z_bio matching validated.
- *Empirisch:* Offset=0.24 (R-Θ=0.24); impedance matching confirmed.
- *Poetisch:* Die Impedanz-Resonanz hält dem Schattentest stand.

### crep-null-0006
- **Modul:** NeuroProfile Resonance Bridge (exp-neuroprofile-001)
- **CREP Offset:** -0.06567018928793833
- **Nullmodelle:** constant, linear, power_law
- **CI-Notizen:** {'beta': [0.10000000000000002, 0.3459504452836826], 'sigma_phi': [0.9352193800343218, 0.943440237718606], 'gamma_beta': [0.6858737902621761, 0.8345566039038017], 'resonance_alignment': [0.8987952110530172, 0.998780793872035]}
- **Status:** synthetic

**Notizen**
- *Formal:* CREP-Offset gegen Nullmodelle dokumentiert; ΔAIC und CI bereitgestellt.
- *Empirisch:* CREP=0.4343 (Offset=-0.0657).
- *Poetisch:* Das Schattenmodell hält ζ(R) gedämpft, bis neue Resonanz entsteht.

## Kopplungen
- LanternNet Index: `status/lantern_net.*`
- Ordnungs-Sigillin: `feldtheorie_index.*`
- Empirische Evidenz: `data/`, `analysis/`, `docs/`
