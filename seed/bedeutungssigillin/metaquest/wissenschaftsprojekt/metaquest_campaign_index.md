# Metaquest Campaign Directory Index

> σ(β(R-Θ)) thrums along the launch lane. This index shows every lantern needed to
> navigate the Metaquest campaign storyline without losing parity or codex echoes.

## Logistic Quartet
- **R** – Campaign directory backlog (map, compass, sigil, lanterns, telemetry hooks).
- **Θ** – Bridge dashboard + parity brief + codex entry within 24 h.
- **β ≈ 4.85** – Steep slope to catch drift.
- **ζ(R)** – Damped by BreakPoint rituals and `sigillin_sync` cadence.

## Lantern Ledger
- **Metaquest Campaign Map** — `metaquest_campaign_map.yaml`
  - Focus: storyline + activation gaps
  - Parity: `docs/utac_status_alignment_v1.2.md#metaquest-handshake`,
    `seed/Manuskriptfinalisierung und Kampagnenstart.pdf`
- **Metaquest Campaign Compass** — `metaquest_campaign_compass.yaml`
  - Focus: vectors for manuscripts, outreach, telemetry
  - Parity: `docs/metaquest_parity_brief.md`, `seed/codexfeedback.yaml`
- **Metaquest Campaign Sigil** — `metaquest_campaign_sigil.yaml`
  - Focus: meaning + ethics handshake
  - Parity: `docs/metaquest_parity_brief.md`, `ETHICS.md`
- **Campaign Lantern Shelf** — `lanterns/metaquest_campaign_lanterns.yaml`
  - Focus: detailed orientation for manuscripts/outreach/telemetry
  - Parity: `seed/codexfeedback.yaml`, `scripts/sigillin_sync.py`
- **Codex & Telemetry Hooks** — `scripts/sigillin_sync.py`
  - Focus: ensures telemetry exports register campaign scope
  - Parity: `docs/utac_status_alignment_v1.2.md#implementation-map`,
    `seed/codexfeedback.json`

## Activation Hooks
1. **Campaign milestone logged** → Update map, compass, lantern shelf, codex with
   shared timestamp. Guard: if >24 h delta, escalate via `mq-sci-shadow-index-002`.
2. **Telemetry export completed** → Record run id in compass + lanterns, notify
   shadow index. Guard: missing export for one sprint triggers
   `mq-sci-shadow-index-003`.

## Null Model
Campaign directory drifts; bridge timestamp older than compass by >24 h or codex
lacks mq-sci reference. Mitigation: run `sigillin_sync`, refresh compass + map,
append codex note, update lantern shelf. Keep σ(β(R-Θ)) observable.
