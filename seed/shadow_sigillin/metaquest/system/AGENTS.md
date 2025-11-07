# Metaquest System Shadow Compass Protocol

This recess tracks system-side Metaquest failure modes and recovery
rituals.

- **Logistic guard.** $R$ = unattended automation drift, index lag, or
  telemetry silence; $\Theta$ = parity brief + codex echo + status matrix
  entries refreshed within 24h; $\beta \approx 5.2$ keeps alerts sharp;
  $\zeta(R)$ spikes when BreakPoint rituals lapse.
- **Tri-layer parity.** Always update YAML/JSON/MD together. Mirror the
  light-side compass under
  `../../../bedeutungssigillin/metaquest/system/`.
- **Actionability.** Every risk must specify signals, remediation steps,
  and escalation hooks (e.g. `scripts/sigillin_sync.py`, Makefile,
  CI/nox runs).
- **Codex discipline.** Log every alert or mitigation in
  `seed/codexfeedback.{yaml,json,md}` with mq-sys-shadow ids, and ensure
  indices surface the shadow artefact.
