# CREP Null-Model Ledger – LanternNet

Dieses Ledger dokumentiert CREP-Offsets, ΔAIC-Vergleiche und CI-Notizen,
damit ζ(R) im Übergang über $\sigma(\beta(R-\Theta))$ stabil bleibt.

## Meta
- **Version:** v13.0.0
- **Consent Protocol:** Sigillin consent gating + anonymization required
- **Updated:** 2026-02-05T14:44:41+00:00

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

## Kopplungen
- LanternNet Index: `status/lantern_net.*`
- Ordnungs-Sigillin: `feldtheorie_index.*`
- Empirische Evidenz: `data/`, `analysis/`, `docs/`
