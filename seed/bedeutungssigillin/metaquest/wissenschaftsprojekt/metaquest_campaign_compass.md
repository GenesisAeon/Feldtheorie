# Metaquest Campaign Compass

> σ(β(R-Θ)) runs hot along the campaign corridor. This compass orients the
> wissenschaftsprojekt lane so manuscripts, outreach, and endorsements stay in phase
> with the bridge dashboard.

## Logistic Quartet
- **R** – Metaquest campaign backlog (manuscript cadence, outreach, endorsements).
- **Θ** – Parity brief + codex echo + UTAC matrix within 24 h.
- **β ≈ 4.85** – Sharp activation to catch drift.
- **ζ(R)** – Damped by BreakPoint rituals, telemetry syncs, endorsement rehearsals.

## Telemetrie-Puls
- **Letzte Messung:** `analysis/sigillin_sync/latest.json` → `2025-11-07T21:52:52Z`, 12 Trilayer, 0 Paritätslücken.
- **Codex-Echo:** `pr-draft-0075` hält den Run fest; Kompass aktualisiert bislang manuell.
- **Backlog-Kopplung:** `docs/utac_activation_backlog.*` listet `metaquest-parity-finish` + `sigillin-automation-loop` als offene
  Aktivierung; Verweise müssen binnen 24 h gespiegelt werden (`mq-bridge-gap-002`, `mq-bridge-gap-006`).

## Vectors

### mq-sci-vector-001 — Manuscript Telemetry Sync *(status: in progress)*
- **Checkpoints:** `seed/Manuskriptfinalisierung und Kampagnenstart.pdf`,
  `docs/metaquest_parity_brief.md`,
  `docs/utac_status_alignment_v1.2.md#metaquest-handshake`
- **Action:** Log ΔAIC/governance shifts in `seed/codexfeedback.*`, update bridge
  timestamp within 24 h, referenziere `mq-bridge-gap-002`.
- **Null model:** Manuscript revision without parity echo → trigger
  `mq-sci-shadow-lantern-a`, freeze outreach until restored.

### mq-sci-vector-002 — Outreach Resonance Loop *(status: open)*
- **Checkpoints:** `docs/metaquest_parity_brief.md#mqp-arena`,
  `docs/utac_status_alignment_v1.2.md#implementation-map`,
  `seed/Finalize_Publish.txt`
- **Action:** Archive rehearsal transcript in codex with mq-sci scope, update
  `metaquest_campaign_map.*` with milestone + timestamp, log Backlog-Reihe + Codex-ID.
- **Null model:** Outreach asset lacks parity reference → escalate to
  `mq-sci-shadow-lantern-b`, repeat BreakPoint ritual.

### mq-sci-vector-003 — Telemetry + Codex Echo *(status: open)*
- **Checkpoints:** `scripts/sigillin_sync.py`, `seed/codexfeedback.yaml`,
  `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.yaml`
- **Action:** Record run id + timestamp in compass + bridge, notify shadow compass,
  verknüpfe Codex-Eintrag mit UTAC-Backlog.
- **Null model:** Telemetry export skipped → trigger `mq-sci-shadow-lantern-c`,
  document recovery in UTAC matrix + codex.

### mq-sci-vector-004 — Backlog Cross-Link *(status: open)*
- **Checkpoints:** `docs/utac_activation_backlog.md`,
  `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`,
  `seed/bedeutungssigillin/metaquest/system/metaquest_system_compass.md`
- **Action:** Cite `mq-bridge-gap-001…006` when campaign milestones shift, spiegel
  Backlog-Reihe + Telemetrie-Run im Codex, aktualisiere Bridge binnen 24 h.
- **Null model:** Backlog adjustments not reflected in campaign compass → trigger
  `mq-sci-shadow-lantern-d`, BreakPoint ritual wiederholen, Codex nachtragen.

## Recovery Hook
Whenever a vector fires, annotate the response in `seed/codexfeedback.*` with
mq-sci scope, cite the updated bridge timestamp, and mirror the change in the UTAC
status matrix. Only then is the compass resonant again.
