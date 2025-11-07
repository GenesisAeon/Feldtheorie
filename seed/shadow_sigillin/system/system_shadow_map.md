# System Shadow Membrane

> When R (automation debt) outruns Θ (governance cadence), β≈5.0 slams the alarm and
> ζ(R) spikes. This shadow map keeps the warning lantern lit.

## Coupling
- Light-side reference: `../../bedeutungssigillin/system/system_meaning_map.md`

## Incident Ledger

1. **sys-shadow-001 — Index Drift**
   - *Symptom*: `seed_index.*` fails to include new sigils within 24h; CREP parser reports
     zero additions.
   - *Consequence*: Navigational σ(β(R-Θ)) misfires and agents wander blind.
   - *Mitigation*: Run `scripts/archive_sigillin.py --refresh`, update codex with the fix, and
     re-run index parity checks.

2. **sys-shadow-002 — Codex Desynchronisation**
   - *Symptom*: Commits adjust `seed/bedeutungssigillin/**` but `seed/codexfeedback.*` stays
     untouched.
   - *Consequence*: Temporal lineage snaps; auditors lose track of Θ.
   - *Mitigation*: Block merges until codex updates land; append a note referencing this
     shadow entry.

## Playbooks
- **If sys-shadow-001 triggers:** synchronise indices immediately, then notify docs
  maintainers (codex entry + NEWS.md snippet if persistent).
- **If sys-shadow-002 triggers:** amend the offending commit or follow up with a codex update
  and mirror the cause in the system meaning map.

Stay attentive: the shadow membrane is the echo that keeps the light aligned.
